"""
DECODE – Chart Detection Engine
Detects charts, graphs, tables, and diagrams inside PDF pages using
OpenCV contour/edge analysis.  Classifies detected regions as bar, line,
pie, scatter, table, or other.

Each detected region is returned with:
  • bounding box   {x, y, width, height}
  • chart_type     bar | line | pie | scatter | table | other
  • confidence     0.0 – 1.0
  • page_number
"""

import logging
import math
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

import cv2
import numpy as np

try:
    from backend.core.ocr_engine import ocr_reader
except ImportError:
    ocr_reader = None

logger = logging.getLogger("decode.chart_detector")

# Configurable via env / settings
DEFAULT_CONFIDENCE_THRESHOLD = 0.55
MIN_CHART_AREA_RATIO = 0.02          # chart must be ≥ 2 % of page area
MAX_CHART_AREA_RATIO = 0.90          # chart must be ≤ 90 % of page area


# ─────────────────────────────────────────────────────────────────────────────
# PDF → page images  (PyMuPDF)
# ─────────────────────────────────────────────────────────────────────────────

def pdf_to_page_images(pdf_path: str, dpi: int = 200) -> list[np.ndarray]:
    """Render each page of *pdf_path* as a BGR numpy array."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError(
            "PyMuPDF (fitz) is required for PDF parsing. "
            "Install via: pip install PyMuPDF"
        )

    doc = fitz.open(pdf_path)
    images: list[np.ndarray] = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, 3
        )
        # fitz returns RGB – convert to BGR for OpenCV
        images.append(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    doc.close()
    logger.info("Rendered %d pages from %s at %d DPI", len(images), pdf_path, dpi)
    return images

# ─────────────────────────────────────────────────────────────────────────────
# Evidence Model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EvidenceContext:
    contour_count: int = 0
    large_contours: int = 0
    circularity_scores: List[float] = field(default_factory=list)
    rectangle_count: int = 0
    rectangles: List[Tuple[int, int, int, int]] = field(default_factory=list)
    detected_lines: int = 0
    arrow_count: int = 0
    grid_score: int = 0
    has_common_baseline: bool = False
    
    # New OCR and Validation Signals
    ocr_tokens: List[Dict[str, Any]] = field(default_factory=list)
    numeric_axis_score: float = 0.0
    icon_illustration_score: float = 0.0
    paragraph_text_score: float = 0.0
    boxes_have_internal_text_labels_score: float = 0.0
    grid_line_regularity_score: float = 0.0
    text_column_alignment_score: float = 0.0
    small_uniform_contour_density: float = 0.0
    consistent_row_height_and_left_margin_score: float = 0.0
    contour_size_and_shape_variance: float = 0.0
    
    # For reasoning logs
    evidence_log: List[str] = field(default_factory=list)
    negative_evidence_log: List[str] = field(default_factory=list)

def _run_ocr(img_bgr: np.ndarray) -> List[Dict[str, Any]]:
    """Run OCR and return bounding boxes and text."""
    if not ocr_reader:
        return []
    
    # EasyOCR takes BGR or RGB, but grayscale is usually better for charts
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    try:
        results = ocr_reader.readtext(gray)
        tokens = []
        for (bbox, text, prob) in results:
            if not text.strip(): continue
            # bbox is [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            tokens.append({
                "x": int(min(x_coords)),
                "y": int(min(y_coords)),
                "w": int(max(x_coords) - min(x_coords)),
                "h": int(max(y_coords) - min(y_coords)),
                "text": text.strip(),
                "prob": prob
            })
        return tokens
    except Exception as e:
        logger.warning(f"OCR failed in chart detector: {e}")
        return []

def _numeric_axis_score(tokens: List[Dict[str, Any]], img_h: int, img_w: int, image_bgr: np.ndarray) -> float:
    """
    Returns a 0.0-1.0 score for the likelihood of a numeric axis.
    Never hard-fails. Checks multiple edges and accepts relaxed regex.
    """
    score = 0.0
    if not tokens: 
        pass
    else:
        # Relaxed pattern: integers, decimals, percentages, commas, negative, k/m, currency
        numeric_pattern = re.compile(r'^-?\$?\d{1,3}(,\d{3})*(\.\d+)?%?[kKmM]?$')
        
        # Check bottom edge and left edge
        for edge in ["bottom", "left"]:
            edge_tokens = []
            for t in tokens:
                # Replace common OCR errors on the fly
                txt = t["text"].replace("O", "0").replace("o", "0").replace("l", "1").replace("I", "1").replace("S", "5")
                txt = txt.strip()
                
                is_left = t["x"] < img_w * 0.3
                is_bottom = (t["y"] + t["h"]) > img_h * 0.7
                
                if (edge == "left" and is_left) or (edge == "bottom" and is_bottom):
                    edge_tokens.append(txt)
            
            if len(edge_tokens) > 0:
                hits = sum(1 for txt in edge_tokens if numeric_pattern.match(txt))
                edge_score = hits / len(edge_tokens) if hits > 0 else 0.0
                score = max(score, edge_score)

    # Partial credit for geometric tick marks (small perpendicular dashes)
    # Detect small vertical lines near the bottom or horizontal lines near the left
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, math.pi/180, threshold=20, minLineLength=5, maxLineGap=2)
    if lines is not None:
        tick_count = 0
        for l in lines:
            x1, y1, x2, y2 = l[0]
            # vertical tick (x diff small, y diff small but > 5) near bottom
            if abs(x1 - x2) < 3 and 5 <= abs(y1 - y2) <= 20 and max(y1, y2) > img_h * 0.7:
                tick_count += 1
            # horizontal tick near left
            if abs(y1 - y2) < 3 and 5 <= abs(x1 - x2) <= 20 and min(x1, x2) < img_w * 0.3:
                tick_count += 1
        if tick_count >= 3:
            score = max(score, 0.5)

    return score

def _analyze_text_metrics(tokens: List[Dict[str, Any]], rectangles: List[Tuple[int, int, int, int]]) -> Tuple[float, float, float]:
    """
    Returns:
    - boxes_have_internal_text_labels_score
    - short_scattered_text_labels_score
    - consistent_row_height_and_left_margin_score
    """
    if not tokens:
        return 0.0, 0.0, 0.0
        
    # 1. Boxes with text labels
    boxes_with_text = 0
    if rectangles:
        for (rx, ry, rw, rh) in rectangles:
            for t in tokens:
                cx, cy = t["x"] + t["w"]/2, t["y"] + t["h"]/2
                if rx < cx < rx+rw and ry < cy < ry+rh:
                    if re.search(r'[a-zA-Z]{3,}', t["text"]):
                        boxes_with_text += 1
                        break
    box_score = min(boxes_with_text / max(len(rectangles), 1), 1.0)
    
    # 2. Short scattered text labels (infographic style)
    # Typically 1-3 words, not purely numeric
    short_labels = [t for t in tokens if len(t["text"].split()) <= 3 and not re.match(r'^\d+$', t["text"])]
    scatter_score = min(len(short_labels) / max(len(tokens), 1), 1.0)
    
    # 3. Paragraph alignment
    # Check if multiple tokens share the same left margin (within 10px)
    left_margins = [t["x"] for t in tokens]
    margin_score = 0.0
    if len(tokens) > 5:
        margin_bins = {}
        for m in left_margins:
            b = m // 10
            margin_bins[b] = margin_bins.get(b, 0) + 1
        max_aligned = max(margin_bins.values()) if margin_bins else 0
        # If at least 30% of tokens align to the same left margin, strong signal
        margin_score = min(max_aligned / (len(tokens) * 0.3), 1.0)
        
    return box_score, scatter_score, margin_score



# ─────────────────────────────────────────────────────────────────────────────
# Low-level feature detectors
# ─────────────────────────────────────────────────────────────────────────────

def _analyze_region(image_bgr: np.ndarray) -> tuple[EvidenceContext, np.ndarray]:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    debug_image = image_bgr.copy()
    ctx = EvidenceContext()
    ctx.contour_count = len(contours)
    ctx.large_contours = sum(1 for c in contours if cv2.contourArea(c) > 2000)

    # Compute contour variance and density for text/infographic scoring
    if len(contours) > 5:
        areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 10]
        if areas:
            mean_area = np.mean(areas)
            std_area = np.std(areas)
            cv_area = std_area / (mean_area + 1e-5)
            ctx.contour_size_and_shape_variance = min(cv_area / 2.0, 1.0)
            
            small_areas = [a for a in areas if a < 500]
            if len(small_areas) > 20:
                ctx.small_uniform_contour_density = min(len(small_areas) / 100.0, 1.0)

    # --- Circularity check (for pie_chart candidacy) ---
    for c in contours:
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        circularity = (4 * math.pi * area) / (perimeter ** 2)
        approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / float(h) if h > 0 else 0
        # Real circle has many vertices, square aspect ratio, and is large enough
        if circularity > 0.8 and area > 0.05 * image_bgr.shape[0] * image_bgr.shape[1] and len(approx) > 5 and 0.8 < aspect < 1.2:
            ctx.circularity_scores.append(circularity)
            cv2.drawContours(debug_image, [c], -1, (0, 255, 0), 3)
            cv2.putText(debug_image, f"circularity={circularity:.2f}",
                        tuple(c[0][0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # --- Rectangle / bar detection (use edges to separate touching bars) ---
    edges = cv2.Canny(gray, 50, 150)
    edge_contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for c in edge_contours:
        x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        # Allow thin but long rectangles (bars) and larger boxes
        if (min(w, h) >= 10 and max(w, h) >= 30) and area > 200:
            approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
            solidity = area / (w * h) if w * h > 0 else 0
            if (len(approx) == 4 and solidity > 0.5) or solidity > 0.8:
                # Prevent double counting inner/outer edge contours
                duplicate = False
                for rx, ry, rw, rh in ctx.rectangles:
                    if abs(x-rx) < 5 and abs(y-ry) < 5 and abs(w-rw) < 5 and abs(h-rh) < 5:
                        duplicate = True
                        break
                if not duplicate:
                    ctx.rectangle_count += 1
                    ctx.rectangles.append((x, y, w, h))
                    cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Check for common baseline among vertical rectangles (for bar chart)
    ctx.has_common_baseline = False
    if ctx.rectangle_count >= 2:
        # For vertical bars, check if they share a bottom Y coordinate
        bottoms = [r[1] + r[3] for r in ctx.rectangles if r[3] > r[2] * 0.8]
        for b in bottoms:
            if sum(1 for other_b in bottoms if abs(b - other_b) < 10) >= 2:
                ctx.has_common_baseline = True
                break

    # --- Line segment detection (for line_chart / arrows) ---
    lines = cv2.HoughLinesP(edges, 1, math.pi/180, threshold=50,
                             minLineLength=30, maxLineGap=10)
    ctx.detected_lines = 0 if lines is None else len(lines)
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            cv2.line(debug_image, (x1,y1), (x2,y2), (0,0,255), 2)

    # --- Arrowhead / Connector detection ---
    # In many PDFs, thin lines and small arrowheads are merged or noisy.
    # We infer connecting arrows topologically by counting the distinct gaps between separated nodes.
    ctx.arrow_count = 0
    valid_nodes = [r for r in ctx.rectangles if r[2] * r[3] < 0.8 * image_bgr.shape[0] * image_bgr.shape[1]]
    if len(valid_nodes) >= 2:
        # Check horizontal topology
        nodes_sorted_x = sorted(valid_nodes, key=lambda r: r[0])
        gaps_x = 0
        for i in range(1, len(nodes_sorted_x)):
            if nodes_sorted_x[i][0] > nodes_sorted_x[i-1][0] + nodes_sorted_x[i-1][2]:
                gaps_x += 1
                cx = (nodes_sorted_x[i-1][0] + nodes_sorted_x[i-1][2] + nodes_sorted_x[i][0]) // 2
                cy = nodes_sorted_x[i-1][1] + (nodes_sorted_x[i-1][3] // 2)
                cv2.circle(debug_image, (cx, cy), 5, (0, 255, 255), -1)
        
        # Check vertical topology if horizontal yields 0
        gaps_y = 0
        if gaps_x == 0:
            nodes_sorted_y = sorted(valid_nodes, key=lambda r: r[1])
            for i in range(1, len(nodes_sorted_y)):
                if nodes_sorted_y[i][1] > nodes_sorted_y[i-1][1] + nodes_sorted_y[i-1][3]:
                    gaps_y += 1
                    cx = nodes_sorted_y[i-1][0] + (nodes_sorted_y[i-1][2] // 2)
                    cy = (nodes_sorted_y[i-1][1] + nodes_sorted_y[i-1][3] + nodes_sorted_y[i][1]) // 2
                    cv2.circle(debug_image, (cx, cy), 5, (0, 255, 255), -1)
        
        ctx.arrow_count = max(gaps_x, gaps_y)
        
    # If they share a baseline, it's highly unlikely they are flowchart nodes
    if ctx.has_common_baseline:
        ctx.arrow_count = 0

    # --- Table / Grid detection ---
    # Intersections of lines
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(gray.shape[1] // 10, 20), 1))
    h_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, h_kernel)
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(gray.shape[0] // 10, 20)))
    v_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, v_kernel)
    
    intersections = cv2.bitwise_and(h_lines, v_lines)
    inter_cnts, _ = cv2.findContours(intersections, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # A true grid (table) will have many distinct intersection points forming cells
    # A simple bar chart might have a few intersections (bars crossing baseline). 
    # A real table usually has at least a 3x3 grid (9+ intersections).
    if len(inter_cnts) >= 12:
        ctx.grid_score = 1
        cv2.putText(debug_image, f"grid intersections: {len(inter_cnts)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,255), 2)
                    
    # --- OCR Validation for Axes and Diagrams ---
    ctx.ocr_tokens = _run_ocr(image_bgr)
    ctx.numeric_axis_score = _numeric_axis_score(ctx.ocr_tokens, image_bgr.shape[0], image_bgr.shape[1], image_bgr)
    
    box_score, scatter_score, margin_score = _analyze_text_metrics(ctx.ocr_tokens, ctx.rectangles)
    ctx.boxes_have_internal_text_labels_score = box_score
    ctx.short_scattered_text_labels_score = scatter_score
    ctx.consistent_row_height_and_left_margin_score = margin_score
    
    # Borderless table score (OCR alignment checking)
    if len(ctx.ocr_tokens) > 10:
        x_starts = [t["x"] for t in ctx.ocr_tokens]
        unique_x = []
        for x in sorted(x_starts):
            if not unique_x or x - unique_x[-1] > 20:
                unique_x.append(x)
        if 2 <= len(unique_x) <= len(ctx.ocr_tokens) / 3:
            ctx.text_column_alignment_score = 1.0
        
    return ctx, debug_image

def _classify_features(ctx: EvidenceContext) -> dict:
    scores = {}

    # 1. FLOWCHART / PROCESS DIAGRAM
    scores["FLOWCHART"] = (
        0.5 * min(ctx.arrow_count, 1)
        + 0.3 * min(ctx.rectangle_count / 3, 1)
        + 0.2 * ctx.boxes_have_internal_text_labels_score
    )

    # 2. TABLE (check both bordered-grid and borderless-text-alignment signals)
    scores["TABLE"] = max(ctx.grid_score, ctx.text_column_alignment_score)

    # 3. CHART Candidates
    bar_score = (
        0.4 * min(ctx.rectangle_count / 3, 1)
        + 0.4 * ctx.numeric_axis_score
        + 0.2 * (1 if ctx.arrow_count == 0 else 0)
    )

    line_score = (
        0.4 * min(ctx.detected_lines / 2, 1)
        + 0.4 * ctx.numeric_axis_score
        + 0.2 * (1 if ctx.rectangle_count == 0 else 0)
    )

    pie_score = 0.0
    max_circularity = max(ctx.circularity_scores, default=0)
    if max_circularity > 0.6:
        pie_score = 0.6 * max_circularity + 0.4 * (1 if ctx.rectangle_count == 0 else 0)

    best_chart = max([(bar_score, "bar_chart"), (line_score, "line_chart"), (pie_score, "pie_chart")], key=lambda x: x[0])
    scores["CHART"] = best_chart[0]

    # 4. DIAGRAM / INFOGRAPHIC (icon-heavy illustrations)
    variety_score = ctx.contour_size_and_shape_variance
    label_score = ctx.short_scattered_text_labels_score
    no_axis_bonus = 1.0 - ctx.numeric_axis_score
    no_grid_bonus = 1.0 - ctx.grid_score
    scores["DIAGRAM"] = 0.35 * variety_score + 0.3 * label_score + 0.2 * no_axis_bonus + 0.15 * no_grid_bonus

    # 5. TEXT / OTHER (paragraph pages)
    scores["OTHER"] = (
        0.4 * ctx.small_uniform_contour_density +
        0.35 * ctx.consistent_row_height_and_left_margin_score +
        0.25 * (1.0 - ctx.contour_size_and_shape_variance)
    )

    # Pick the best-scoring category overall
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    # Only fall back to OTHER with low confidence if nothing scored meaningfully
    if best_score < 0.25:
        return {
            "type": "OTHER",
            "sub_type": None,
            "confidence": 0.3,
            "reason": "Low confidence across all categories; needs manual review.",
            "evidence": ctx.evidence_log,
            "negative_evidence": ctx.negative_evidence_log,
            "needs_review": True
        }

    sub_type = None
    if best_type == "CHART":
        sub_type = best_chart[1]
    elif best_type == "DIAGRAM":
        if label_score > 0.5:
            sub_type = "infographic"
        else:
            sub_type = "diagram"

    return {
        "type": best_type,
        "sub_type": sub_type,
        "confidence": best_score,
        "reason": f"Classified as {best_type}{' ('+sub_type+')' if sub_type else ''} via weighted scoring.",
        "evidence": ctx.evidence_log,
        "negative_evidence": ctx.negative_evidence_log,
        "needs_review": best_score < 0.5
    }


# ─────────────────────────────────────────────────────────────────────────────
# Candidate region detection
# ─────────────────────────────────────────────────────────────────────────────

def _find_candidate_regions(
    img_bgr: np.ndarray,
    min_area_ratio: float = MIN_CHART_AREA_RATIO,
    max_area_ratio: float = MAX_CHART_AREA_RATIO,
) -> list[dict]:
    """
    Find candidate chart/figure regions on a single page image.
    Uses connected component grouping so visually distinct elements 
    (like a chart and a table separated by whitespace) are correctly split.
    """
    h, w = img_bgr.shape[:2]
    page_area = h * w
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Get strong edges (for shapes/charts) and dark pixels (for text/lines)
    edges = cv2.Canny(gray, 50, 150)
    _, dark = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    combined = cv2.bitwise_or(edges, dark)

    # 2. Modest dilation to connect letters into words and nearby chart elements.
    # Keep this small (10x10) to avoid bridging large whitespace gaps between separate charts.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    dilated = cv2.dilate(combined, kernel, iterations=1)

    # 3. Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 4. Filter and collect bounding boxes
    boxes = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        boxes.append([x, y, x + cw, y + ch])
        
    if not boxes:
        return []

    # 5. Group overlapping/nearby boxes
    def merge_boxes(b1, b2, margin=15):
        # margin allows merging boxes that are within `margin` pixels of each other
        x1 = max(0, min(b1[0], b2[0]) - margin)
        y1 = max(0, min(b1[1], b2[1]) - margin)
        x2 = min(w, max(b1[2], b2[2]) + margin)
        y2 = min(h, max(b1[3], b2[3]) + margin)
        
        # Check intersection with margin
        ix = max(0, min(b1[2]+margin, b2[2]+margin) - max(b1[0]-margin, b2[0]-margin))
        iy = max(0, min(b1[3]+margin, b2[3]+margin) - max(b1[1]-margin, b2[1]-margin))
        return ix > 0 and iy > 0

    merged = True
    while merged:
        merged = False
        new_boxes = []
        while boxes:
            box = boxes.pop(0)
            merged_with_existing = False
            for i, other in enumerate(new_boxes):
                if merge_boxes(box, other, margin=15):
                    new_boxes[i] = [
                        min(box[0], other[0]),
                        min(box[1], other[1]),
                        max(box[2], other[2]),
                        max(box[3], other[3])
                    ]
                    merged_with_existing = True
                    merged = True
                    break
            if not merged_with_existing:
                new_boxes.append(box)
        boxes = new_boxes

    # 6. Final filter by area and aspect ratio
    candidates = []
    for (x1, y1, x2, y2) in boxes:
        cw, ch = x2 - x1, y2 - y1
        area = cw * ch
        ratio = area / page_area
        if ratio < min_area_ratio or ratio > max_area_ratio:
            continue
            
        aspect = cw / max(ch, 1)
        if aspect < 0.15 or aspect > 8.0:
            continue
            
        # Add a tiny padding to the crop
        pad = 5
        cx1 = max(0, x1 - pad)
        cy1 = max(0, y1 - pad)
        cx2 = min(w, x2 + pad)
        cy2 = min(h, y2 + pad)
            
        candidates.append({
            "x": int(cx1), "y": int(cy1),
            "width": int(cx2 - cx1), "height": int(cy2 - cy1),
        })

    return candidates


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def detect_charts_in_image(
    img_bgr: np.ndarray,
    page_number: int = 1,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> list[dict]:
    """
    Detect and classify chart regions in a single page image.

    Returns a list of dicts:
        {
            "page_number": int,
            "bounding_box": {"x": int, "y": int, "width": int, "height": int},
            "chart_type": str,
            "confidence": float,
            "needs_review": bool,
        }
    """
    candidates = _find_candidate_regions(img_bgr)
    results = []

    for cand in candidates:
        x, y, cw, ch = cand["x"], cand["y"], cand["width"], cand["height"]
        cropped_bgr = img_bgr[y:y + ch, x:x + cw]

        ctx, debug_image = _analyze_region(cropped_bgr)
        classification = _classify_features(ctx)
        
        chart_type = classification["type"]
        sub_type = classification.get("sub_type")
        confidence = classification["confidence"]
        reason = classification["reason"]
        
        # Add classification text to the debug image
        cv2.putText(debug_image, f"TYPE: {chart_type.upper()}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
        cv2.putText(debug_image, f"CONF: {confidence:.2f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

        # Skip text regions unless confidence is low/unknown and they might be something else
        if chart_type == "text" or chart_type == "OTHER":
            # For logging only
            pass

        # Temporary Debug Logging as requested
        logger.info(
            f"Region [P{page_number}] {cw}x{ch} px at ({x},{y}): "
            f"classified as {chart_type}{' ('+str(sub_type)+')' if sub_type else ''} ({confidence:.2f}). Reason: {reason}"
        )

        # Save debug crops to a temp directory so developer can verify
        debug_dir = Path("debug_crops")
        debug_dir.mkdir(exist_ok=True)
        cv2.imwrite(str(debug_dir / f"p{page_number}_{x}_{y}_{chart_type}_annotated.png"), debug_image)
        cv2.imwrite(str(debug_dir / f"p{page_number}_{x}_{y}_{chart_type}_crop.png"), cropped_bgr)

        results.append({
            "page_number": page_number,
            "bounding_box": {
                "x": x, "y": y, "width": cw, "height": ch,
            },
            "chart_type": chart_type,
            "sub_type": sub_type,
            "confidence": confidence,
            "reason": reason,
            "evidence": classification.get("evidence", []),
            "negative_evidence": classification.get("negative_evidence", []),
            "needs_review": classification["needs_review"],
        })

    # Sort by confidence descending
    results.sort(key=lambda r: r["confidence"], reverse=True)
    logger.info(
        "Page %d: detected %d chart candidates (%d above threshold)",
        page_number,
        len(results),
        sum(1 for r in results if not r["needs_review"]),
    )
    return results


def detect_charts_in_pdf(
    pdf_path: str,
    dpi: int = 200,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict:
    """
    Full chart detection pipeline for a PDF document.

    Returns:
        {
            "page_count": int,
            "charts": [... list of chart detections across all pages ...],
            "page_images": [... numpy arrays for each page ...],
        }
    """
    page_images = pdf_to_page_images(pdf_path, dpi=dpi)
    all_charts = []

    for i, page_img in enumerate(page_images):
        charts = detect_charts_in_image(
            page_img,
            page_number=i + 1,
            confidence_threshold=confidence_threshold,
        )
        all_charts.extend(charts)

    logger.info(
        "PDF %s: %d pages, %d total chart detections",
        pdf_path, len(page_images), len(all_charts),
    )
    return {
        "page_count": len(page_images),
        "charts": all_charts,
        "page_images": page_images,
    }


def crop_chart_image(
    page_image: np.ndarray,
    bounding_box: dict,
    padding: int = 10,
) -> np.ndarray:
    """Crop a chart region from a page image with optional padding."""
    h, w = page_image.shape[:2]
    x = max(0, bounding_box["x"] - padding)
    y = max(0, bounding_box["y"] - padding)
    x2 = min(w, bounding_box["x"] + bounding_box["width"] + padding)
    y2 = min(h, bounding_box["y"] + bounding_box["height"] + padding)
    return page_image[y:y2, x:x2].copy()
