"""
DECODE – Chart Data Extraction Engine
Extracts structured numeric data, axis labels, legends, and titles from
cropped chart images using a combination of:
  • EasyOCR / Tesseract for text recovery
  • OpenCV geometric analysis for bar heights, line traces, pie angles

Output is a structured intermediate representation:
  {
    "series": [{"name": str, "color": str, "points": [{"label": str, "value": float, "confidence": float}]}],
    "axis_labels": {"x_label": str, "y_label": str, "x_ticks": [...], "y_ticks": [...]},
    "legend": [{"name": str, "color": str}],
    "title": str,
    "raw_ocr_text": str,
    "extraction_confidence": float,
  }
"""

import logging
import math
import re
from typing import Optional

import cv2
import numpy as np

from services.llm_service import get_llm, GeminiLLM

logger = logging.getLogger("decode.chart_extractor")


# ─────────────────────────────────────────────────────────────────────────────
# OCR helpers  (use the project's existing EasyOCR reader)
# ─────────────────────────────────────────────────────────────────────────────

def _get_ocr_reader():
    """Lazy-import the EasyOCR reader initialised in ocr_engine."""
    try:
        from core.ocr_engine import ocr_reader
        if ocr_reader is not None:
            return ocr_reader
    except ImportError:
        pass
    # Fallback: create a new reader
    try:
        import easyocr
        return easyocr.Reader(["en"], gpu=False)
    except Exception as e:
        logger.error("Cannot initialise OCR reader: %s", e)
        return None


def _ocr_region(img: np.ndarray) -> list[dict]:
    """
    Run OCR on an image region.
    Returns list of {"text": str, "confidence": float, "bbox": [x1,y1,x2,y2]}.
    """
    reader = _get_ocr_reader()
    if reader is None:
        return []

    try:
        results = reader.readtext(img)
        items = []
        for bbox, text, prob in results:
            text = text.strip()
            if not text:
                continue
            # Flatten bbox to [x1, y1, x2, y2]
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            items.append({
                "text": text,
                "confidence": round(prob, 3),
                "bbox": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))],
            })
        return items
    except Exception as e:
        logger.error("OCR failed: %s", e)
        return []


def _is_numeric(text: str) -> bool:
    """Check if text represents a number (with optional %, $, commas)."""
    cleaned = re.sub(r'[,$%\s]', '', text)
    try:
        float(cleaned)
        return True
    except ValueError:
        return False


def _parse_number(text: str) -> Optional[float]:
    """Parse a number from OCR'd text, handling $, %, commas."""
    cleaned = re.sub(r'[,$%\s]', '', text)
    cleaned = cleaned.replace('O', '0').replace('o', '0')
    cleaned = cleaned.replace('l', '1').replace('I', '1')
    try:
        return float(cleaned)
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Axis / label extraction
# ─────────────────────────────────────────────────────────────────────────────

def _color_distance(hex1: str, hex2: str) -> float:
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

def _find_x_axis_y(img_bgr: np.ndarray) -> int:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(img_bgr.shape[1] * 0.1), 1))
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    y_candidates = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > img_bgr.shape[1] * 0.3 and y < img_bgr.shape[0] * 0.95:
            y_candidates.append(y)
            
    if y_candidates:
        return max(y_candidates)
    return int(img_bgr.shape[0] * 0.75)

def _find_legend_pairs(img_bgr: np.ndarray, ocr_items: list[dict]) -> tuple[list[dict], set]:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    swatches = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 50 < area < 2000:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = w / float(max(h, 1))
            if 0.5 < aspect < 2.0:
                roi = img_bgr[y:y+h, x:x+w]
                median_color = np.median(roi.reshape(-1, 3), axis=0)
                b, g, r = [int(v) for v in median_color]
                if not (r > 240 and g > 240 and b > 240) and not (r < 30 and g < 30 and b < 30):
                    color_hex = f"#{r:02x}{g:02x}{b:02x}"
                    swatches.append({
                        "x": x, "y": y, "w": w, "h": h,
                        "cx": x + w//2, "cy": y + h//2,
                        "color": color_hex
                    })
                    
    legend_pairs = []
    assigned_texts = set()
    
    for swatch in swatches:
        best_text = None
        best_dist = 9999
        best_idx = -1
        
        for i, item in enumerate(ocr_items):
            if i in assigned_texts:
                continue
            x1, y1, x2, y2 = item["bbox"]
            tcx, tcy = (x1+x2)/2, (y1+y2)/2
            
            if abs(tcy - swatch["cy"]) < max(swatch["h"], 20):
                if x1 > swatch["x"] and (x1 - (swatch["x"] + swatch["w"])) < 150:
                    dist = x1 - (swatch["x"] + swatch["w"])
                    if dist < best_dist:
                        best_dist = dist
                        best_text = item["text"]
                        best_idx = i
                        
        if best_text:
            legend_pairs.append({
                "name": best_text,
                "color": swatch["color"],
                "text_idx": best_idx
            })
            assigned_texts.add(best_idx)
            
    return legend_pairs, assigned_texts

def _extract_axis_info(ocr_items: list[dict], img_bgr: np.ndarray) -> dict:
    """
    Partition OCR results into axis labels, tick values, title, and legend text.
    Uses spatial position heuristics combined with visual swatch detection.
    """
    h, w = img_bgr.shape[:2]
    legend_pairs, legend_text_indices = _find_legend_pairs(img_bgr, ocr_items)
    x_axis_y = _find_x_axis_y(img_bgr)
    
    x_ticks = []
    y_ticks = []
    title_candidates = []
    x_label = ""
    y_label = ""
    
    top_zone = h * 0.15
    left_zone = w * 0.15
    
    for i, item in enumerate(ocr_items):
        if i in legend_text_indices:
            continue
            
        x1, y1, x2, y2 = item["bbox"]
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        text = item["text"]
        
        if cy < top_zone and left_zone < cx < (w - left_zone):
            title_candidates.append(text)
        elif cx < left_zone and _is_numeric(text):
            val = _parse_number(text)
            if val is not None:
                y_ticks.append({"text": text, "value": val, "y": cy})
        elif cx < left_zone * 0.6 and not _is_numeric(text):
            y_label = text
        elif cy > x_axis_y - 20 and cy < x_axis_y + 50:
            if _is_numeric(text):
                val = _parse_number(text)
                if val is not None:
                    x_ticks.append({"text": text, "value": val, "x": cx})
            else:
                x_ticks.append({"text": text, "x": cx})

    x_ticks.sort(key=lambda t: t["x"])
    y_ticks.sort(key=lambda t: t["y"], reverse=True)

    # X-axis label: lowest text that is NOT a tick, legend, or title
    bottom_texts = [
        item for i, item in enumerate(ocr_items)
        if i not in legend_text_indices
        and item["bbox"][1] > x_axis_y + 30
        and not _is_numeric(item["text"])
    ]
    if bottom_texts:
        bottom_texts.sort(key=lambda item: item["bbox"][3], reverse=True)
        x_label = bottom_texts[0]["text"]

    return {
        "title": " ".join(title_candidates) if title_candidates else "",
        "x_label": x_label,
        "y_label": y_label,
        "x_ticks": [t["text"] for t in x_ticks],
        "y_ticks": [t.get("value", 0) for t in y_ticks],
        "y_tick_positions": {t.get("value", 0): t["y"] for t in y_ticks},
        "legend_pairs": legend_pairs,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Color extraction helpers
# ─────────────────────────────────────────────────────────────────────────────

def _extract_dominant_colors(img_bgr: np.ndarray, n_colors: int = 8) -> list[str]:
    """
    Extract dominant non-background colors using k-means.
    Returns hex color strings.
    """
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    # Mask out near-white and near-black
    mask = cv2.inRange(hsv, (0, 25, 25), (180, 255, 240))
    pixels = img_bgr[mask > 0].reshape(-1, 3).astype(np.float32)

    if len(pixels) < 50:
        return ["#333333"]

    k = min(n_colors, len(pixels) // 10, 8)
    if k < 1:
        k = 1

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(
        pixels, k, None, criteria, 5, cv2.KMEANS_PP_CENTERS
    )

    # Sort by frequency
    counts = np.bincount(labels.flatten())
    sorted_idx = np.argsort(-counts)

    colors = []
    for idx in sorted_idx:
        b, g, r = centers[idx].astype(int)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append(hex_color)

    return colors


# ─────────────────────────────────────────────────────────────────────────────
# Bar chart extractor
# ─────────────────────────────────────────────────────────────────────────────

def _extract_bar_chart(img_bgr: np.ndarray, axis_info: dict) -> dict:
    """Extract data series from a bar chart image."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Detect bar regions via contour analysis
    _, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(
        cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    bars = []
    chart_area = h * w
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < chart_area * 0.005:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
        if len(approx) >= 4:
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect = bw / max(bh, 1)
            # Filter: bars are typically taller than wide or wider than tall
            if (aspect < 2.0 and bh > h * 0.05) or (aspect > 0.5 and bw > w * 0.03):
                # Get dominant color of bar
                bar_region = img_bgr[y:y + bh, x:x + bw]
                colors = _extract_dominant_colors(bar_region, 2)
                bars.append({
                    "x": int(x), "y": int(y),
                    "w": int(bw), "h": int(bh),
                    "cx": int(x + bw // 2),
                    "top_y": int(y),
                    "bottom_y": int(y + bh),
                    "color": colors[0] if colors else "#333333",
                    "area": int(area),
                })

    if not bars:
        return {"series": [], "extraction_confidence": 0.0}

    # Sort bars left-to-right
    bars.sort(key=lambda b: b["cx"])

    # Map bar heights to values using y-axis scale
    y_ticks = axis_info.get("y_ticks", [])
    y_positions = axis_info.get("y_tick_positions", {})

    def _pixel_to_value(pixel_y: int) -> float:
        """Convert a pixel Y coordinate to a data value using axis calibration."""
        if len(y_ticks) >= 2 and len(y_positions) >= 2:
            sorted_ticks = sorted(y_positions.items(), key=lambda kv: kv[1])
            # In image coords, higher pixel_y = lower data value
            top_val, top_py = sorted_ticks[0]
            bot_val, bot_py = sorted_ticks[-1]
            if abs(bot_py - top_py) > 1:
                ratio = (pixel_y - top_py) / (bot_py - top_py)
                return top_val + ratio * (bot_val - top_val)
        # Fallback: use pixel proportion
        return round((1.0 - pixel_y / h) * 100, 1)

    # Match bars to x-axis labels
    x_ticks = axis_info.get("x_ticks", [])

    # Group bars by color for multi-series
    color_groups: dict[str, list] = {}
    for bar in bars:
        c = bar["color"]
        color_groups.setdefault(c, []).append(bar)

    series = []
    for color, group_bars in color_groups.items():
        points = []
        for i, bar in enumerate(group_bars):
            value = _pixel_to_value(bar["top_y"])
            label = x_ticks[i] if i < len(x_ticks) else f"Bar {i + 1}"
            points.append({
                "label": str(label),
                "value": round(abs(value), 2),
                "confidence": 0.75,
            })
        series.append({
            "name": f"Series {len(series) + 1}",
            "color": color,
            "points": points,
        })

    # Map to legend pairs based on color
    legend_pairs = axis_info.get("legend_pairs", [])
    for i, s in enumerate(series):
        best_name = s["name"]
        best_dist = 100
        for lp in legend_pairs:
            dist = _color_distance(s["color"], lp["color"])
            if dist < best_dist:
                best_dist = dist
                best_name = lp["name"]
        if best_dist >= 100 and i < len(legend_pairs):
            best_name = legend_pairs[i]["name"]
        s["name"] = best_name

    avg_conf = 0.75 if y_ticks else 0.5
    return {"series": series, "extraction_confidence": avg_conf}


# ─────────────────────────────────────────────────────────────────────────────
# Line chart extractor
# ─────────────────────────────────────────────────────────────────────────────

def _extract_line_chart(img_bgr: np.ndarray, axis_info: dict) -> dict:
    """Extract data series from a line chart image."""
    h, w = img_bgr.shape[:2]
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Detect colored lines by isolating non-background hues
    colors = _extract_dominant_colors(img_bgr, 6)
    y_ticks = axis_info.get("y_ticks", [])
    x_ticks = axis_info.get("x_ticks", [])

    series = []

    for color_hex in colors[:4]:
        # Convert hex to BGR
        r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
        target_bgr = np.uint8([[[b, g, r]]])
        target_hsv = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2HSV)[0][0]

        # Create mask for this color
        hue_range = 15
        lower = np.array([max(0, target_hsv[0] - hue_range), 40, 40])
        upper = np.array([min(180, target_hsv[0] + hue_range), 255, 255])
        mask = cv2.inRange(hsv, lower, upper)

        # Find non-zero pixels of this color
        points_y, points_x = np.where(mask > 0)
        if len(points_x) < 20:
            continue

        # Sample values at evenly spaced x positions
        n_samples = len(x_ticks) if x_ticks else 10
        chart_left = int(w * 0.15)
        chart_right = int(w * 0.90)
        sample_xs = np.linspace(chart_left, chart_right, n_samples).astype(int)

        data_points = []
        for i, sx in enumerate(sample_xs):
            # Get the y-values of the line near this x position
            nearby_mask = (points_x >= sx - 5) & (points_x <= sx + 5)
            nearby_ys = points_y[nearby_mask]
            if len(nearby_ys) == 0:
                continue
            median_y = np.median(nearby_ys)

            # Convert pixel to value
            if len(y_ticks) >= 2:
                val = y_ticks[0] + (1.0 - median_y / h) * (y_ticks[-1] - y_ticks[0])
            else:
                val = round((1.0 - median_y / h) * 100, 1)

            label = x_ticks[i] if i < len(x_ticks) else f"Point {i + 1}"
            data_points.append({
                "label": str(label),
                "value": round(abs(val), 2),
                "confidence": 0.70,
            })

        if data_points:
            series.append({
                "name": f"Series {len(series) + 1}",
                "color": color_hex,
                "points": data_points,
            })

    # Apply legend names
    legend_pairs = axis_info.get("legend_pairs", [])
    for i, s in enumerate(series):
        best_name = s["name"]
        best_dist = 100
        for lp in legend_pairs:
            dist = _color_distance(s["color"], lp["color"])
            if dist < best_dist:
                best_dist = dist
                best_name = lp["name"]
        if best_dist >= 100 and i < len(legend_pairs):
            best_name = legend_pairs[i]["name"]
        s["name"] = best_name

    return {"series": series, "extraction_confidence": 0.65 if series else 0.0}


# ─────────────────────────────────────────────────────────────────────────────
# Pie chart extractor
# ─────────────────────────────────────────────────────────────────────────────

def _extract_pie_chart(img_bgr: np.ndarray, axis_info: dict) -> dict:
    """Extract data series from a pie chart image."""
    h, w = img_bgr.shape[:2]
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Mask out background (white/near-white)
    mask = cv2.inRange(hsv, (0, 25, 25), (180, 255, 240))

    # Get distinct color segments
    colors = _extract_dominant_colors(img_bgr, 10)

    segments = []
    total_pixels = np.sum(mask > 0)
    if total_pixels == 0:
        return {"series": [], "extraction_confidence": 0.0}

    for color_hex in colors:
        r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
        target_bgr = np.uint8([[[b, g, r]]])
        target_hsv = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2HSV)[0][0]

        hue_range = 12
        lower = np.array([max(0, target_hsv[0] - hue_range), 30, 30])
        upper = np.array([min(180, target_hsv[0] + hue_range), 255, 255])
        color_mask = cv2.inRange(hsv, lower, upper)

        pixel_count = np.sum(color_mask > 0)
        if pixel_count < total_pixels * 0.02:
            continue

        percentage = round(pixel_count / total_pixels * 100, 1)
        segments.append({
            "color": color_hex,
            "percentage": percentage,
            "pixel_count": int(pixel_count),
        })

    if not segments:
        return {"series": [], "extraction_confidence": 0.0}

    # Normalise percentages to sum to 100
    total_pct = sum(s["percentage"] for s in segments)
    if total_pct > 0:
        for s in segments:
            s["percentage"] = round(s["percentage"] / total_pct * 100, 1)

    # Sort by size descending
    segments.sort(key=lambda s: s["percentage"], reverse=True)

    # OCR'd labels near the pie
    legend_pairs = axis_info.get("legend_pairs", [])

    # Build series (pie has a single series with multiple points)
    points = []
    for i, seg in enumerate(segments):
        best_label = f"Segment {i + 1}"
        best_dist = 100
        for lp in legend_pairs:
            dist = _color_distance(seg["color"], lp["color"])
            if dist < best_dist:
                best_dist = dist
                best_label = lp["name"]
        if best_dist >= 100 and i < len(legend_pairs):
            best_label = legend_pairs[i]["name"]
            
        points.append({
            "label": best_label,
            "value": seg["percentage"],
            "confidence": 0.65,
        })

    series = [{
        "name": "Distribution",
        "color": segments[0]["color"],
        "points": points,
    }]

    return {"series": series, "extraction_confidence": 0.60}


# ─────────────────────────────────────────────────────────────────────────────
# Generic / scatter extractor (fallback)
# ─────────────────────────────────────────────────────────────────────────────

def _extract_scatter_chart(img_bgr: np.ndarray, axis_info: dict) -> dict:
    """Extract data points from a scatter plot."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 1)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, 1.5, 8,
        param1=100, param2=15, minRadius=2, maxRadius=20,
    )

    y_ticks = axis_info.get("y_ticks", [])
    x_ticks = axis_info.get("x_ticks", [])

    if circles is None:
        return {"series": [], "extraction_confidence": 0.0}

    points = []
    for c in circles[0]:
        cx, cy = float(c[0]), float(c[1])
        x_val = round(cx / w * 100, 1)
        if len(y_ticks) >= 2:
            y_val = y_ticks[0] + (1.0 - cy / h) * (y_ticks[-1] - y_ticks[0])
        else:
            y_val = round((1.0 - cy / h) * 100, 1)
        points.append({
            "label": f"({round(x_val, 1)}, {round(y_val, 1)})",
            "value": round(abs(y_val), 2),
            "confidence": 0.55,
        })

    series = [{
        "name": "Data Points",
        "color": "#4e79a7",
        "points": points,
    }]

    return {"series": series, "extraction_confidence": 0.50}


# ─────────────────────────────────────────────────────────────────────────────
# Table extractor (img2table)
# ─────────────────────────────────────────────────────────────────────────────

def _extract_table(img_bgr: np.ndarray, axis_info: dict) -> dict:
    """Extract table data using img2table."""
    try:
        from img2table.document import Image
        from img2table.ocr import EasyOCR
    except ImportError:
        logger.error("img2table is not installed.")
        return {"series": [], "extraction_confidence": 0.0}
        
    success, buffer = cv2.imencode('.png', img_bgr)
    if not success:
        return {"series": [], "extraction_confidence": 0.0}
        
    img = Image(src=buffer.tobytes())
    ocr = EasyOCR(lang=["en"])
    
    extracted_tables = img.extract_tables(
        ocr=ocr, 
        implicit_rows=True, 
        borderless_tables=True, 
        min_confidence=50
    )
    
    if not extracted_tables:
        return {"series": [], "extraction_confidence": 0.0}
        
    # Take the largest table by area
    table = max(extracted_tables, key=lambda t: t.bbox.y2 - t.bbox.y1)
    df = table.df
    
    if df.empty or len(df.columns) < 2:
        return {"series": [], "extraction_confidence": 0.0}
        
    # If columns are just integers, promote the first row to header
    if list(df.columns) == list(range(len(df.columns))):
        df.columns = df.iloc[0].astype(str)
        df = df[1:].reset_index(drop=True)
        
    categories = df.iloc[:, 0].fillna("").astype(str).tolist()
    
    series = []
    # Distinct colors for series
    colors = ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#59a14f", "#edc949", "#af7aa1", "#ff9da7", "#9c755f", "#bab0ab"]
    
    for i, col in enumerate(df.columns[1:]):
        col_name = str(col)
        if not col_name.strip() or col_name == "nan":
            col_name = f"Column {i+1}"
            
        points = []
        for j, val in enumerate(df[col]):
            clean_val = str(val).replace(',', '').replace(' ', '').strip() if val else None
            try:
                num_val = float(clean_val)
            except (ValueError, TypeError):
                num_val = None
                
            label = categories[j] if j < len(categories) else f"Row {j+1}"
            points.append({
                "label": str(label),
                "value": num_val,
                "confidence": 0.85
            })
            
        series.append({
            "name": col_name,
            "color": colors[i % len(colors)],
            "points": points
        })
        
    return {"series": series, "extraction_confidence": 0.90}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

# Map chart types to their extractors
_EXTRACTORS = {
    "bar_chart": _extract_bar_chart,
    "line_chart": _extract_line_chart,
    "pie_chart": _extract_pie_chart,
    "scatter_plot": _extract_scatter_chart,
    "table": _extract_table,
    "table_chart": _extract_table,
    "bar": _extract_bar_chart,  # backwards compatibility
    "line": _extract_line_chart,
    "pie": _extract_pie_chart,
    "scatter": _extract_scatter_chart,
}

def extract_chart_data(
    cropped_image: np.ndarray,
    chart_type: str = "bar",
) -> dict:
    """
    Extract structured data from a cropped chart image.

    Args:
        cropped_image: BGR numpy array of the chart region
        chart_type: detected chart type (bar/line/pie/scatter/other)

    Returns:
        {
            "series": [...],
            "axis_labels": {"x_label", "y_label", "x_ticks", "y_ticks"},
            "legend": [{"name", "color"}],
            "title": str,
            "raw_ocr_text": str,
            "extraction_confidence": float,
        }
    """
    h, w = cropped_image.shape[:2]
    logger.info("Extracting %s chart data from %dx%d image", chart_type, w, h)
    
    llm = get_llm()
    if isinstance(llm, GeminiLLM):
        logger.info("[extraction] path=llm")
    else:
        logger.info("[extraction] path=fallback")

    # Step 1: OCR all text in the chart
    ocr_items = _ocr_region(cropped_image)
    raw_text = "\n".join(item["text"] for item in ocr_items)
    
    # Debug logging for OCR as requested in Step 2
    logger.info("Raw OCR items for chart extraction: %s", 
                [{"text": item["text"], "bbox": item["bbox"]} for item in ocr_items])

    # Step 2: Parse axis info from OCR results (now using BGR image for swatches/axis detection)
    axis_info = _extract_axis_info(ocr_items, cropped_image)

    # Step 3: Run the chart-type-specific extractor, or skip if unsupported (like flowchart)
    extractor = _EXTRACTORS.get(chart_type)
    if extractor:
        extraction = extractor(cropped_image, axis_info)
    else:
        logger.info("Skipping data extraction for non-data region type: %s", chart_type)
        extraction = {"series": [], "extraction_confidence": 0.0}

    # Step 4: Compose the result
    series = extraction.get("series", [])
    
    # Calculate a real confidence score (Step 4)
    confidence = 0.0
    if series:
        has_x = bool(axis_info.get("x_ticks") or axis_info.get("x_label"))
        has_y = bool(axis_info.get("y_ticks") or axis_info.get("y_label"))
        # Base confidence from extractor (usually 0.5 - 0.75)
        base_conf = extraction.get("extraction_confidence", 0.5)
        # Bonus for having axis and legend
        bonus = 0.0
        if has_x: bonus += 0.1
        if has_y: bonus += 0.1
        if axis_info.get("legend_pairs"): bonus += 0.1
        if axis_info.get("title"): bonus += 0.05
        confidence = min(0.95, base_conf + bonus)
        
    legend = []
    for s in series:
        legend.append({"name": s["name"], "color": s["color"]})
    if not legend and axis_info.get("legend_pairs"):
        legend = [{"name": lp["name"], "color": lp["color"]} for lp in axis_info.get("legend_pairs")]

    result = {
        "series": series,
        "axis_labels": {
            "x_label": axis_info.get("x_label", ""),
            "y_label": axis_info.get("y_label", ""),
            "x_ticks": axis_info.get("x_ticks", []),
            "y_ticks": axis_info.get("y_ticks", []),
        },
        "legend": legend,
        "title": axis_info.get("title", ""),
        "raw_ocr_text": raw_text,
        "extraction_confidence": confidence,
    }

    logger.info(
        "Extracted %d series, %d total points, confidence %.2f",
        len(series),
        sum(len(s["points"]) for s in series),
        result["extraction_confidence"],
    )
    return result
