import os
import logging
import fitz  # PyMuPDF
import re

logger = logging.getLogger("decode.visual_extractor")

class VisualExtractor:
    def __init__(self, dpi: int = 200):
        self.dpi = dpi
        self.zoom = dpi / 72.0

    def extract_from_pdf(self, pdf_path: str):
        """
        Extracts visual elements from a PDF.
        Returns a list of dicts:
        {
            "page_number": int (1-indexed),
            "bbox": [x0, y0, x1, y1] (Scaled to self.dpi),
            "type": str ("table", "figure", "chart", "diagram", etc.),
            "confidence": float
        }
        """
        doc = fitz.open(pdf_path)
        all_elements = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_elements = self._extract_page_elements(page, page_num)
            all_elements.extend(page_elements)
            
        doc.close()
        return all_elements

    def _extract_page_elements(self, page, page_num):
        elements = []
        page_rect = page.rect
        
        # 1. Extract Tables
        tables = page.find_tables()
        if tables and tables.tables:
            for tab in tables.tables:
                elements.append({
                    "bbox": list(tab.bbox),
                    "type": "table",
                    "page_number": page_num + 1,
                    "confidence": 0.95
                })
        
        # 2. Extract Images (Figures/Photos)
        image_list = page.get_images()
        for img_info in image_list:
            xref = img_info[0]
            try:
                rects = page.get_image_rects(xref)
                for rect in rects:
                    rect = fitz.Rect(rect)
                    # Ignore tiny images (often used as bullets/icons) or full page background images
                    area = rect.width * rect.height
                    page_area = page_rect.width * page_rect.height
                    if area < 400 or area > page_area * 0.95:
                        continue
                    elements.append({
                        "bbox": list(rect),
                        "type": "figure",
                        "page_number": page_num + 1,
                        "confidence": 0.90
                    })
            except Exception as e:
                logger.warning(f"Failed to get image rects for xref {xref}: {e}")

        # 3. Extract Vector Graphics (Charts/Diagrams)
        drawings = page.get_drawings()
        if drawings:
            text_blocks = page.get_text("blocks")
            vector_rects = self._group_drawings(drawings, page_rect, text_blocks)
            
            # Filter out purely textual/background clusters
            
            for rect in vector_rects:
                if not self._is_pure_text_or_background(rect, text_blocks, page_rect):
                    elements.append({
                        "bbox": list(rect),
                        "type": "chart", # General chart/diagram
                        "page_number": page_num + 1,
                        "confidence": 0.85
                    })
                
        # 4. Resolve overlaps
        resolved = self._resolve_overlaps(elements)
        
        # 5. Scale to Target DPI
        scaled_elements = []
        for elem in resolved:
            scaled_bbox = [
                int(elem["bbox"][0] * self.zoom),
                int(elem["bbox"][1] * self.zoom),
                int(elem["bbox"][2] * self.zoom),
                int(elem["bbox"][3] * self.zoom)
            ]
            
            # Ensure valid dimensions
            if scaled_bbox[2] > scaled_bbox[0] and scaled_bbox[3] > scaled_bbox[1]:
                elem["bbox"] = scaled_bbox
                scaled_elements.append(elem)
                
        return scaled_elements

    def _is_pure_text_or_background(self, rect, text_blocks, page_rect) -> bool:
        """
        Rejects full-page regions or regions that are purely text.
        """
        rect = fitz.Rect(rect)
        page_rect = fitz.Rect(page_rect)
        area = rect.width * rect.height
        page_area = page_rect.width * page_rect.height
        
        # Rule 1: Reject full page background graphics
        if area > page_area * 0.85:
            return True
            
        # Rule 2: Reject if the vector box perfectly encapsulates just a text block
        # (This happens when text has a drawn background or border)
        text_area_in_rect = 0
        for b in text_blocks:
            b_rect = fitz.Rect(b[:4])
            intersect = rect.intersect(b_rect)
            if not intersect.is_empty:
                text_area_in_rect += (intersect.width * intersect.height)
                
        # If the drawing box is more than 85% covered by text, it's just a text box
        if area > 0 and (text_area_in_rect / area) > 0.85:
            return True
            
        return False
        
    def _group_drawings(self, drawings, page_rect, text_blocks):
        """
        Group drawing commands into contiguous visual regions,
        incorporating nearby text (labels, legends, titles) and adding padding.
        """
        valid_rects = []
        page_area = page_rect.width * page_rect.height
        
        for d in drawings:
            r = fitz.Rect(d["rect"])
            area = r.width * r.height
            # Ignore background fills or tiny dots
            if area > page_area * 0.9 or area < 10:
                continue
            valid_rects.append(r)
            
        if not valid_rects:
            return []
            
        # 1. Aggressively merge nearby vector graphics
        merged = []
        # Use a larger threshold to ensure disconnected chart parts (like legends) merge
        THRESHOLD = 50.0 
        
        for r in valid_rects:
            r_expanded = r + (-THRESHOLD, -THRESHOLD, THRESHOLD, THRESHOLD)
            matched_idx = -1
            for i, m in enumerate(merged):
                if m.intersects(r_expanded):
                    matched_idx = i
                    break
            
            if matched_idx >= 0:
                merged[matched_idx] = merged[matched_idx] | r
            else:
                merged.append(r)
                
        # Second pass to merge any newly overlapping rects
        final_merged = []
        for r in merged:
            matched_idx = -1
            for i, m in enumerate(final_merged):
                if m.intersects(r + (-THRESHOLD, -THRESHOLD, THRESHOLD, THRESHOLD)):
                    matched_idx = i
                    break
            if matched_idx >= 0:
                final_merged[matched_idx] = final_merged[matched_idx] | r
            else:
                final_merged.append(r)
                
        # 2. Filter tiny/meaningless groups
        filtered = []
        for r in final_merged:
            area = r.width * r.height
            if area > page_area * 0.02: # At least 2% of page area for a meaningful chart/diagram
                filtered.append(r)
                
        # 3. Absorb adjacent text blocks (titles, legends, axes)
        TEXT_PROXIMITY = 30.0 # How close text must be to be considered part of the chart
        text_rects = [fitz.Rect(b[:4]) for b in text_blocks]
        
        expanded_charts = []
        for r in filtered:
            current_r = r
            changed = True
            while changed:
                changed = False
                search_area = current_r + (-TEXT_PROXIMITY, -TEXT_PROXIMITY, TEXT_PROXIMITY, TEXT_PROXIMITY)
                for tr in text_rects:
                    if search_area.intersects(tr) and not current_r.contains(tr):
                        current_r = current_r | tr
                        changed = True
            
            # 4. Add final adaptive padding to prevent tight cropping of borders
            pad_x = min(30, max(15, current_r.width * 0.05))
            pad_y = min(30, max(15, current_r.height * 0.05))
            padded_r = current_r + (-pad_x, -pad_y, pad_x, pad_y)
            
            # Clamp to page size
            clamped_r = padded_r.intersect(page_rect)
            if not clamped_r.is_empty:
                expanded_charts.append(clamped_r)
                
        return expanded_charts
        
    def _resolve_overlaps(self, elements):
        """
        If a table, image, and vector graphic overlap significantly, keep the most specific one.
        (e.g., Table > Figure > Chart)
        """
        # Sort so we process Table first, then Figure, then Chart
        priority = {"table": 1, "figure": 2, "chart": 3}
        elements.sort(key=lambda x: priority.get(x["type"], 99))
        
        resolved = []
        for elem in elements:
            r1 = fitz.Rect(elem["bbox"])
            is_redundant = False
            for existing in resolved:
                r2 = fitz.Rect(existing["bbox"])
                intersect = r1.intersect(r2)
                if intersect.is_empty:
                    continue
                intersect_area = intersect.width * intersect.height
                r1_area = r1.width * r1.height
                
                # If elem is highly contained in existing, ignore it
                if r1_area > 0 and intersect_area / r1_area > 0.8:
                    is_redundant = True
                    break
            if not is_redundant:
                resolved.append(elem)
                
        return resolved
