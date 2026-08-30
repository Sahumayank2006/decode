import os
import re

file_path = 'Decode_backend/backend/core/chart_extractor.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Part B: Add normalize_region_type
part_b = """
def normalize_region_type(region_type):
    value = str(region_type or "").strip().lower()
    aliases = {
        "chart": "chart", "graph": "chart", "plot": "chart",
        "bar": "bar_chart", "bar chart": "bar_chart", "bar_chart": "bar_chart",
        "line": "line_chart", "line chart": "line_chart", "line_chart": "line_chart",
        "area": "area_chart", "area chart": "area_chart", "area_chart": "area_chart",
        "pie": "pie_chart", "pie chart": "pie_chart", "pie_chart": "pie_chart",
        "donut": "donut_chart", "donut chart": "donut_chart", "donut_chart": "donut_chart",
        "radar": "radar_chart", "radar chart": "radar_chart", "radar_chart": "radar_chart",
        "scatter": "scatter_plot", "scatter plot": "scatter_plot", "scatter_plot": "scatter_plot",
        "table": "table", "data table": "table",
    }
    return aliases.get(value, value)

NORMALIZED_DATA_REGION_TYPES = {
    "chart", "bar_chart", "line_chart", "area_chart", "pie_chart",
    "donut_chart", "radar_chart", "scatter_plot", "table",
}

def is_data_region(region_type):
    normalized = normalize_region_type(region_type)
    return normalized in NORMALIZED_DATA_REGION_TYPES

def _clean_number(value):
    if value is None: return None
    import re, math
    text = str(value).strip().replace(",", "").replace("−", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"[^\\d.\\-+eE%]", "", text)
    if not text: return None
    try:
        number = float(text)
        if math.isfinite(number): return number
    except (TypeError, ValueError):
        pass
    return None

def extract_numeric_ocr_values(ocr_items):
    values = []
    for item in ocr_items or []:
        if not isinstance(item, dict): continue
        text = item.get("text")
        number = _clean_number(text)
        if number is None: continue
        values.append({"value": number, "text": str(text), "bbox": item.get("bbox")})
    return values

def extract_chart_data_safe(image, ocr_items=None, region_type="chart", existing_extractor=None):
    normalized_type = normalize_region_type(region_type)
    logger.info("[chart-extraction] region_type=%s normalized=%s", region_type, normalized_type)

    if normalized_type not in {
        "chart", "bar_chart", "line_chart", "area_chart",
        "pie_chart", "donut_chart", "radar_chart", "scatter_plot",
    }:
        logger.info("[chart-extraction] Not a chart region: %s", normalized_type)
        return {"series": [], "categories": [], "confidence": 0.0}

    if existing_extractor is not None:
        try:
            result = existing_extractor(image, ocr_items, normalized_type)
            if result:
                series = result.get("series") or []
                categories = result.get("categories") or []
                if series and categories:
                    logger.info("[chart-extraction] existing extractor succeeded: %d series / %d categories", len(series), len(categories))
                    return result
        except Exception:
            logger.exception("[chart-extraction] Existing extractor failed")

    logger.warning("[chart-extraction] No structured chart data recovered for %s. Returning empty result rather than fabricated values.", normalized_type)
    return {"series": [], "categories": [], "confidence": 0.0}
"""

if 'def normalize_region_type' not in text:
    text = text.replace('import math\n', 'import math\nimport re\n' + part_b + '\n')

# Now patch extract_chart_data to use extract_chart_data_safe
# We need to find extract_chart_data(cropped_image, chart_type="bar_chart", language="en")
# and rewrite it to use extract_chart_data_safe.

old_func_def = """def extract_chart_data(cropped_image, chart_type="bar_chart", language="en") -> dict:
    \"\"\"
    Main entry point for chart data extraction.
    ...
    \"\"\"
"""
# Since I can't easily regex replace the whole function, I will do it intelligently by replacing the skip logic.
# Wait, the prompt says: "Wherever you currently have the logic that decides whether extraction should happen, replace it with:"
# Let's replace the skip logic in `extract_chart_data`.

skip_logic_old = """    extractor = _EXTRACTORS.get(chart_type)
    if extractor:
        extraction = extractor(cropped_image, axis_info)
    else:
        logger.info("Skipping data extraction for non-data region type: %s", chart_type)
        extraction = {"series": [], "extraction_confidence": 0.0}"""

skip_logic_new = """    logger.info("[DECODE DEBUG] region_type=%r normalized=%r", chart_type, normalize_region_type(chart_type))
    
    def _existing_extractor_wrapper(img, ocr_it, n_type):
        ex = _EXTRACTORS.get(n_type) or _EXTRACTORS.get(chart_type)
        if ex: return ex(img, axis_info)
        return {"series": [], "extraction_confidence": 0.0}
        
    extraction = extract_chart_data_safe(cropped_image, ocr_items, chart_type, _existing_extractor_wrapper)
    
    logger.info(
        "[DECODE DEBUG] chart extraction result: categories=%d series=%d points=%d confidence=%.3f",
        len(extraction.get("categories", [])),
        len(extraction.get("series", [])),
        sum(len(s.get("values", []) or s.get("points", [])) for s in extraction.get("series", [])),
        float(extraction.get("confidence", extraction.get("extraction_confidence", 0.0))),
    )"""

text = text.replace(skip_logic_old, skip_logic_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated backend chart_extractor.py")
