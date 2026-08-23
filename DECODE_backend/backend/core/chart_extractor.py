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

def _extract_axis_info(ocr_items: list[dict], img_h: int, img_w: int) -> dict:
    """
    Partition OCR results into axis labels, tick values, title, and legend text.
    Uses spatial position heuristics.
    """
    x_ticks = []       # text along the bottom
    y_ticks = []       # numeric text along the left
    title_candidates = []
    x_label = ""
    y_label = ""
    legend_items = []

    bottom_zone = img_h * 0.75
    top_zone = img_h * 0.15
    left_zone = img_w * 0.15
    right_zone = img_w * 0.75

    for item in ocr_items:
        x1, y1, x2, y2 = item["bbox"]
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        text = item["text"]

        # Title: text in the top-centre
        if cy < top_zone and left_zone < cx < (img_w - left_zone):
            title_candidates.append(text)

        # Y-axis tick values: numeric text on the left side
        elif cx < left_zone and _is_numeric(text):
            val = _parse_number(text)
            if val is not None:
                y_ticks.append({"text": text, "value": val, "y": cy})

        # X-axis tick labels: text along the bottom
        elif cy > bottom_zone:
            if _is_numeric(text):
                val = _parse_number(text)
                if val is not None:
                    x_ticks.append({"text": text, "value": val, "x": cx})
            else:
                x_ticks.append({"text": text, "x": cx})

        # Y-axis label: rotated text far left
        elif cx < left_zone * 0.6 and not _is_numeric(text):
            y_label = text

        # Legend items: text in the right zone or bottom-right
        elif cx > right_zone and cy > bottom_zone * 0.5:
            legend_items.append(text)

    # Sort ticks by position
    x_ticks.sort(key=lambda t: t["x"])
    y_ticks.sort(key=lambda t: t["y"], reverse=True)

    # X-axis label: the text at the very bottom centre (below x-ticks)
    # If not found from spatial analysis, leave empty
    bottom_texts = [item for item in ocr_items
                    if item["bbox"][3] > img_h * 0.9]
    for bt in bottom_texts:
        if not _is_numeric(bt["text"]):
            x_label = bt["text"]
            break

    return {
        "title": " ".join(title_candidates) if title_candidates else "",
        "x_label": x_label,
        "y_label": y_label,
        "x_ticks": [t["text"] for t in x_ticks],
        "y_ticks": [t.get("value", 0) for t in y_ticks],
        "y_tick_positions": {t.get("value", 0): t["y"] for t in y_ticks},
        "legend_texts": legend_items,
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

    # If only one series and we have legend text, use it
    legend_texts = axis_info.get("legend_texts", [])
    for i, s in enumerate(series):
        if i < len(legend_texts):
            s["name"] = legend_texts[i]

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
    legend_texts = axis_info.get("legend_texts", [])
    for i, s in enumerate(series):
        if i < len(legend_texts):
            s["name"] = legend_texts[i]

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
    legend_texts = axis_info.get("legend_texts", [])

    # Build series (pie has a single series with multiple points)
    points = []
    for i, seg in enumerate(segments):
        label = legend_texts[i] if i < len(legend_texts) else f"Segment {i + 1}"
        points.append({
            "label": label,
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
# Public API
# ─────────────────────────────────────────────────────────────────────────────

# Map chart types to their extractors
_EXTRACTORS = {
    "bar_chart": _extract_bar_chart,
    "line_chart": _extract_line_chart,
    "pie_chart": _extract_pie_chart,
    "scatter_plot": _extract_scatter_chart,
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

    # Step 1: OCR all text in the chart
    ocr_items = _ocr_region(cropped_image)
    raw_text = "\n".join(item["text"] for item in ocr_items)

    # Step 2: Parse axis info from OCR results
    axis_info = _extract_axis_info(ocr_items, h, w)

    # Step 3: Run the chart-type-specific extractor, or skip if unsupported (like flowchart)
    extractor = _EXTRACTORS.get(chart_type)
    if extractor:
        extraction = extractor(cropped_image, axis_info)
    else:
        logger.info("Skipping data extraction for non-data region type: %s", chart_type)
        extraction = {"series": [], "extraction_confidence": 0.0}

    # Step 4: Compose the result
    series = extraction.get("series", [])
    legend = [{"name": s["name"], "color": s["color"]} for s in series]

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
        "extraction_confidence": extraction.get("extraction_confidence", 0.0),
    }

    logger.info(
        "Extracted %d series, %d total points, confidence %.2f",
        len(series),
        sum(len(s["points"]) for s in series),
        result["extraction_confidence"],
    )
    return result
