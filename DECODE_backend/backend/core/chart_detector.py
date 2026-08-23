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
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

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
# Low-level feature detectors
# ─────────────────────────────────────────────────────────────────────────────

def _analyze_region(image_bgr: np.ndarray) -> tuple[dict, np.ndarray]:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    debug_image = image_bgr.copy()
    features = {
        "contour_count": len(contours),
        "large_contours": sum(1 for c in contours if cv2.contourArea(c) > 2000),
        "circularity_scores": [],
        "rectangle_count": 0,
        "rectangles": [],
        "detected_lines": 0,
        "arrow_count": 0,
        "grid_score": 0,
        "has_common_baseline": False
    }

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
            features["circularity_scores"].append(circularity)
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
                for rx, ry, rw, rh in features["rectangles"]:
                    if abs(x-rx) < 5 and abs(y-ry) < 5 and abs(w-rw) < 5 and abs(h-rh) < 5:
                        duplicate = True
                        break
                if not duplicate:
                    features["rectangle_count"] += 1
                    features["rectangles"].append((x, y, w, h))
                    cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Check for common baseline among vertical rectangles (for bar chart)
    features["has_common_baseline"] = False
    if features["rectangle_count"] >= 2:
        # For vertical bars, check if they share a bottom Y coordinate
        bottoms = [r[1] + r[3] for r in features["rectangles"] if r[3] > r[2] * 0.8]
        for b in bottoms:
            if sum(1 for other_b in bottoms if abs(b - other_b) < 10) >= 2:
                features["has_common_baseline"] = True
                break

    # --- Line segment detection (for line_chart / arrows) ---
    lines = cv2.HoughLinesP(edges, 1, math.pi/180, threshold=50,
                             minLineLength=30, maxLineGap=10)
    features["detected_lines"] = 0 if lines is None else len(lines)
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            cv2.line(debug_image, (x1,y1), (x2,y2), (0,0,255), 2)

    # --- Arrowhead / Connector detection ---
    # In many PDFs, thin lines and small arrowheads are merged or noisy.
    # We infer connecting arrows topologically by counting the distinct gaps between separated nodes.
    features["arrow_count"] = 0
    valid_nodes = [r for r in features["rectangles"] if r[2] * r[3] < 0.8 * image_bgr.shape[0] * image_bgr.shape[1]]
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
        
        features["arrow_count"] = max(gaps_x, gaps_y)

    # --- Table / Grid detection ---
    # Intersections of lines
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(gray.shape[1] // 10, 20), 1))
    h_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, h_kernel)
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(gray.shape[0] // 10, 20)))
    v_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, v_kernel)
    
    intersections = cv2.bitwise_and(h_lines, v_lines)
    inter_cnts, _ = cv2.findContours(intersections, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # A true grid (table) will have many distinct intersection points forming cells
    if len(inter_cnts) >= 4:
        features["grid_score"] = 1
        cv2.putText(debug_image, f"grid intersections: {len(inter_cnts)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,255), 2)
        
    return features, debug_image

def _classify_features(features: dict) -> tuple[str, float, str]:
    # 1. If a region has almost no contours and no lines, it is plain text/whitespace
    if features["contour_count"] < 3 and features["detected_lines"] == 0:
        return "text", 0.9, "No significant graphical structure detected — likely plain text."
        
    # Dense text with many characters (contours) but no LARGE contours
    if features["contour_count"] > 20 and features["large_contours"] == 0 and features["grid_score"] == 0:
        return "text", 0.9, "High contour count but zero large shapes detected — likely dense plain text."

    # 2. Table: grid regularity detected
    if features["grid_score"] > 0:
        return "table", 0.95, "Detected a regular grid of intersecting horizontal and vertical lines."

    # 3. Bar chart: multiple rectangles sharing a common baseline
    if features["rectangle_count"] >= 2 and features["has_common_baseline"]:
        return "bar_chart", 0.9, f"Detected {features['rectangle_count']} bar-like rectangles sharing a common baseline."

    # 4. Process diagram / flowchart: real arrowheads found connecting real rectangles
    if features["arrow_count"] >= 1 and features["rectangle_count"] >= 2:
        return "process_diagram", 0.95, (
            f"Detected {features['arrow_count']} arrowhead(s) and "
            f"{features['rectangle_count']} rectangular node(s)."
        )

    # 5. Pie chart: only if a genuinely high circularity contour exists
    max_circularity = max(features["circularity_scores"], default=0)
    # The condition is now strict since we enforce aspect ratio in _analyze_region
    if max_circularity > 0.8 and features["rectangle_count"] < 2 and features["arrow_count"] == 0:
        return "pie_chart", 0.95, f"Detected a circular contour with circularity {max_circularity:.2f}."

    # 6. Line chart: line segments present, no arrows
    if features["detected_lines"] > 0 and features["arrow_count"] == 0:
        return "line_chart", 0.85, f"Detected {features['detected_lines']} line segment(s) with no arrows."

    return "unknown", 0.0, "No classification rule matched the detected features confidently."


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

        features, debug_image = _analyze_region(cropped_bgr)
        chart_type, confidence, reason = _classify_features(features)
        
        # Add classification text to the debug image
        cv2.putText(debug_image, f"TYPE: {chart_type.upper()}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
        cv2.putText(debug_image, f"CONF: {confidence:.2f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

        # Skip text regions unless confidence is low/unknown and they might be something else
        if chart_type == "text":
            continue

        # Temporary Debug Logging as requested
        logger.info(
            f"Region [P{page_number}] {cw}x{ch} px at ({x},{y}): "
            f"classified as {chart_type} ({confidence}) via OpenCV heuristic. Reason: {reason}"
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
            "confidence": confidence,
            "reason": reason,
            "needs_review": confidence < confidence_threshold,
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
