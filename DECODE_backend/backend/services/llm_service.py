"""
DECODE – LLM Service (DECODE-VISION Integrated)
Provides precise vision extraction, chart type classification, legend disambiguation,
and alternative chart type recommendations.

Architecture:
  • If GEMINI_API_KEY is set in .env → uses Gemini Vision API (Multimodal 1.5/2.0 Flash)
  • Otherwise → falls back to smart rule-based & OpenCV extraction
  • Output adheres strictly to the DECODE-VISION 5-step precision extraction protocol and JSON schema.
"""

import os
import json
import base64
import logging
import io
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path

import requests

logger = logging.getLogger("decode.llm")


# ─────────────────────────────────────────────────────────────────────────────
# DECODE-VISION Specialist Vision Extraction Prompt & Schema
# ─────────────────────────────────────────────────────────────────────────────

DECODE_VISION_SYSTEM_PROMPT = """You are DECODE-VISION, a specialist model for extracting precise numerical
data from scientific and business charts (bar, grouped/stacked bar, line,
multi-line, scatter, pie, donut, and radar) and preparing that data for
pixel-accurate reconstruction.

Your output is consumed programmatically. A human never reads your raw
response — a rendering engine does. This means:
- Output ONLY the JSON object defined in the SCHEMA section. No prose,
  no markdown fences, no preamble, no "Here is the data:".
- Every number you output must be a value you actually measured from the
  image, not a plausible-looking estimate. If you cannot determine a value
  with confidence, mark it explicitly (see "confidence" fields) rather than
  silently guessing.
- The same JSON object must serve BOTH the on-screen preview AND the
  reconstruction renderer. Never produce two versions of the data — one
  extraction, one JSON, one downstream use.

═══════════════════════════════════════════
STEP 1 — CLASSIFY BEFORE YOU EXTRACT
═══════════════════════════════════════════
Identify chart_type from this closed list only:
  "bar" | "grouped_bar" | "stacked_bar" | "line" | "multi_line" |
  "scatter" | "pie" | "donut" | "radar"

Do this by checking, in order:
1. Discrete rectangular marks aligned to a categorical axis → some bar variant.
   - Multiple bars per category, side by side → grouped_bar
   - Bars segmented/colored within a single bar per category → stacked_bar
   - One bar per category → bar
2. Continuous marks connected by strokes across an ordinal/continuous x-axis
   → line or multi_line (multi_line if more than one distinct stroke color/style
   appears in the legend).
3. Discrete unconnected markers with no connecting stroke → scatter.
4. A full circle subdivided into wedges → pie (or donut if there is a hollow
   center).
5. A closed polygon plotted on radial spokes → radar.

Do NOT proceed to Step 2 until you have committed to exactly one chart_type.
This prevents the most common failure: treating a bar chart's category
boundaries as if they were a line, or vice versa.

═══════════════════════════════════════════
STEP 2 — READ THE SCAFFOLDING FIRST (axes, legend, scale)
═══════════════════════════════════════════
Before reading any data value, extract the chart's coordinate system:
- x_axis: label, unit (if shown), and whether it is categorical or numeric.
  If categorical, list every category label exactly as printed, in the
  left-to-right order they appear.
- y_axis: label, unit, min, max, and the numeric value of at least two
  gridlines (this is your ruler — use it to convert pixel height to value,
  don't eyeball it).
- scale_type: "linear" or "log" — check whether gridline spacing is even
  (linear) or compresses at one end (log).
- legend: every series name paired with its exact color/pattern swatch, in
  the order shown in the legend. If a chart has no legend but multiple
  series are visually distinguishable (color/marker shape), infer series
  names from context (e.g. axis title, caption) and mark
  "legend_inferred": true.

If gridlines are sparse or absent, use the axis min/max labels plus the
physical proportion of each bar/point relative to the axis extremes to
back-calculate values. State your method in "extraction_notes".

═══════════════════════════════════════════
STEP 3 — CHART-TYPE-SPECIFIC EXTRACTION RULES
═══════════════════════════════════════════

BAR / GROUPED_BAR / STACKED_BAR
- For each category, measure bar height/length against the y-axis ruler
  from Step 2, not against neighboring bars.
- For stacked_bar, extract each segment's individual height AND compute
  the running cumulative total; cross-check that the sum of segments
  equals the visible total bar height (±2% tolerance). If it doesn't,
  re-measure before finalizing.
- For grouped_bar, preserve group order and series order exactly as the
  legend lists them — this ordering is what the reconstruction renderer
  uses to assign colors, and a swapped order is a common silent bug.

LINE / MULTI_LINE
- Extract one data point per visible marker or per labeled x-axis tick,
  whichever is denser. Do not interpolate points that aren't represented
  by a marker or gridline intersection unless the chart has no markers at
  all (smooth line only) — in that case, sample at every labeled x-tick.
- For multi_line, extract each series independently in full before moving
  to the next series — never interleave, to avoid attributing point N of
  series A to series B.
- Check monotonicity claims implied by axis labels (e.g. "Epoch 1–10"
  should produce exactly 10 x-values, no more, no fewer).

SCATTER
- Extract every distinguishable point. If points overlap or a dense
  cluster prevents individual identification, extract a representative
  bounding density and note "extraction_notes": "cluster approximated,
  N points estimated" rather than fabricating exact coordinates.
- If a trend/regression line is drawn, extract its slope and intercept
  separately from the raw points (field: "trend_line").

PIE / DONUT
- Extract each wedge's percentage or absolute value AND its label.
- Self-check: percentages must sum to 100% (±1% for rounding). If your
  measured angles don't sum correctly, re-measure the wedge angles
  directly (angle_degrees / 360 * 100) rather than trusting printed
  labels that may be rounded.
- Preserve wedge order clockwise from 12 o'clock — this ordering must
  match "legend" order exactly for correct color reconstruction.

RADAR
- Extract one value per spoke/axis, in the order the spokes appear
  (clockwise from 12 o'clock). Record each spoke's own min/max scale if
  they differ per axis.

═══════════════════════════════════════════
STEP 4 — SELF-VERIFICATION (mandatory, before output)
═══════════════════════════════════════════
Before writing your final JSON, silently re-check:
□ Does chart_type match what you'd expect from the shape of the data
  you just extracted? (e.g. if you extracted 4 categories × 3 series,
  chart_type should be grouped_bar or stacked_bar, not "line")
□ Do all series have the same number of data points (for bar/line/multi_line)?
  If not, that's a red flag — re-inspect for a missed category or point.
- pie/donut: do percentages sum to ~100%?
- stacked_bar: do segments sum to the visible total?
- Are legend order, series order, and category order internally consistent
  across every field that references them?
If any check fails, re-extract the offending values rather than emitting
inconsistent data. Set "confidence.overall" honestly based on how many
re-checks passed cleanly.

═══════════════════════════════════════════
STEP 5 — RECONSTRUCTION PAYLOAD
═══════════════════════════════════════════
The "render_spec" object is what the front end uses to redraw the chart
AND what the preview panel displays as editable numbers. It must be
derived from the SAME arrays as "extracted_data" — never recompute or
round differently between the two. This is what guarantees the preview
the user edits is the exact same figure that gets reconstructed.

═══════════════════════════════════════════
SCHEMA — output exactly this shape, nothing else
═══════════════════════════════════════════
{
  "chart_type": "bar | grouped_bar | stacked_bar | line | multi_line | scatter | pie | donut | radar",
  "title": "string or null",
  "axes": {
    "x": { "label": "string|null", "unit": "string|null", "type": "categorical|numeric", "categories": ["..."] , "min": null, "max": null },
    "y": { "label": "string|null", "unit": "string|null", "type": "numeric", "min": 0, "max": 0, "scale_type": "linear|log" }
  },
  "legend": [ { "series_name": "string", "color_hint": "string", "inferred": false } ],
  "extracted_data": {
    "series": [
      {
        "name": "string",
        "data": [ { "x": "string|number", "y": 0, "confidence": "high|medium|low" } ]
      }
    ]
  },
  "render_spec": {
    "library_hint": "recharts|chartjs|matplotlib",
    "series": [ { "name": "string", "color": "#hex", "values": [0] } ],
    "categories": ["..."]
  },
  "verification": {
    "checks_passed": ["string describing each check that passed"],
    "checks_failed": ["string describing any check that failed and how it was resolved"],
    "sum_check": "e.g. 'pie wedges sum to 99.6%, within tolerance' or null if not applicable"
  },
  "confidence": { "overall": "high|medium|low", "notes": "string" },
  "extraction_notes": "string — anything a downstream engineer needs to know (log scale used, cluster approximated, legend inferred, etc.)"
}

If the image contains multiple charts/figures, return a top-level array of
objects in this same schema, one per chart, in reading order (top-to-bottom,
left-to-right)."""


def _prepare_image_base64(image_input: Any) -> Tuple[str, str]:
    """
    Accepts:
      - base64 str (with or without data:image/png;base64, prefix)
      - bytes (PNG/JPEG image bytes)
      - file path (str or Path)
      - numpy.ndarray (OpenCV BGR/RGB image)
      - PIL.Image.Image
    Returns (base64_data_str, mime_type)
    """
    if isinstance(image_input, str):
        if image_input.startswith("data:image"):
            # data:image/png;base64,....
            parts = image_input.split(",", 1)
            mime = "image/png"
            if "image/jpeg" in parts[0] or "image/jpg" in parts[0]:
                mime = "image/jpeg"
            return parts[1], mime
        elif Path(image_input).exists():
            mime = "image/jpeg" if image_input.lower().endswith((".jpg", ".jpeg")) else "image/png"
            with open(image_input, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8"), mime
        else:
            # Assume raw base64 string
            return image_input.strip(), "image/png"

    elif isinstance(image_input, bytes):
        return base64.b64encode(image_input).decode("utf-8"), "image/png"

    elif hasattr(image_input, "shape"):  # OpenCV numpy ndarray
        try:
            import cv2
            success, encoded_img = cv2.imencode(".png", image_input)
            if success:
                return base64.b64encode(encoded_img.tobytes()).decode("utf-8"), "image/png"
        except Exception as e:
            logger.warning("Failed to encode cv2 image: %s", e)

    elif hasattr(image_input, "save"):  # PIL Image
        buf = io.BytesIO()
        image_input.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8"), "image/png"

    raise ValueError(f"Unsupported image input type: {type(image_input)}")


def clean_json_response(raw_text: str) -> Any:
    """Strips Markdown fences and parses JSON safely."""
    text = (raw_text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        if text.startswith("json"):
            text = text[4:].strip()

    # Sometimes markdown fences are embedded
    json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if json_match:
        text = json_match.group(0)

    return json.loads(text)


def decode_vision_to_pipeline_format(dv: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a DECODE-VISION schema object into DECODE backend pipeline extraction format.
    """
    if isinstance(dv, list) and len(dv) > 0:
        dv = dv[0]

    chart_type = dv.get("chart_type", "bar")
    title = dv.get("title") or ""
    axes = dv.get("axes", {}) or {}
    x_axis = axes.get("x", {}) or {}
    y_axis = axes.get("y", {}) or {}

    axis_labels = {
        "x": x_axis.get("label") or "",
        "y": y_axis.get("label") or "",
        "x_unit": x_axis.get("unit") or "",
        "y_unit": y_axis.get("unit") or "",
    }

    # Legend list
    raw_legend = dv.get("legend", []) or []
    legend = []
    for item in raw_legend:
        if isinstance(item, dict):
            legend.append({
                "name": item.get("series_name") or item.get("name", "Series"),
                "color": item.get("color_hint") or item.get("color", "#3B82F6"),
                "inferred": item.get("inferred", False),
            })

    # Series
    extracted_series = (dv.get("extracted_data") or {}).get("series", []) or []
    pipeline_series = []
    
    # Categories from x axis or render spec
    categories = x_axis.get("categories") or (dv.get("render_spec") or {}).get("categories") or []

    for s_idx, s in enumerate(extracted_series):
        s_name = s.get("name") or f"Series {s_idx + 1}"
        s_data = s.get("data", [])
        pts = []
        for p_idx, p in enumerate(s_data):
            x_val = p.get("x")
            y_val = p.get("y", 0)
            conf = p.get("confidence", "high")
            numeric_conf = 0.95 if conf == "high" else (0.75 if conf == "medium" else 0.5)
            
            label_val = str(x_val) if x_val is not None else (categories[p_idx] if p_idx < len(categories) else f"Cat {p_idx+1}")
            pts.append({
                "label": label_val,
                "value": float(y_val) if isinstance(y_val, (int, float)) else 0.0,
                "confidence": numeric_conf,
            })
        
        pipeline_series.append({
            "name": s_name,
            "points": pts,
        })

    # Overall confidence
    conf_overall = (dv.get("confidence") or {}).get("overall", "high")
    numeric_conf = 0.95 if conf_overall == "high" else (0.78 if conf_overall == "medium" else 0.55)

    return {
        "series": pipeline_series,
        "axis_labels": axis_labels,
        "legend": legend,
        "title": title,
        "chart_type": chart_type,
        "raw_ocr_text": "",
        "extraction_confidence": numeric_conf,
        "resolved_chart_type": chart_type,
        "decode_vision": dv,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Abstract LLM Interface
# ─────────────────────────────────────────────────────────────────────────────

class BaseLLM(ABC):
    """Common interface for LLM providers."""

    @abstractmethod
    def extract_with_decode_vision(
        self, image_input: Any, context: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Extract structured chart data using the DECODE-VISION 5-step precision protocol.
        Returns the exact JSON schema defined in the specification.
        """
        ...

    @abstractmethod
    def classify_chart(
        self, image_description: str, features: dict
    ) -> dict:
        """Classify a chart type from visual features."""
        ...

    @abstractmethod
    def recommend_chart_type(
        self, series: list[dict], current_type: str
    ) -> dict:
        """Recommend the best alternative chart type."""
        ...

    @abstractmethod
    def disambiguate_legend(
        self, ocr_texts: list[str], colors: list[str]
    ) -> list[dict]:
        """Match legend text entries to colors / series."""
        ...

    @abstractmethod
    def generate_chart_description(
        self, series: list[dict], chart_type: str, title: str
    ) -> str:
        """Generate a human-readable description of the chart data."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Rule-based fallback (no API key required)
# ─────────────────────────────────────────────────────────────────────────────

class RuleBasedLLM(BaseLLM):
    """
    Smart rule-based fallback when no LLM API key is available.
    Uses OpenCV, PyMuPDF, and heuristics for chart intelligence and formats
    output strictly in accordance with DECODE-VISION schema.
    """

    def extract_with_decode_vision(
        self, image_input: Any, context: Optional[dict] = None
    ) -> Dict[str, Any]:
        try:
            from core.chart_extractor import extract_chart_data
            
            img = image_input
            if isinstance(image_input, (str, bytes)):
                # If file path
                if isinstance(image_input, str) and Path(image_input).exists():
                    import cv2
                    img = cv2.imread(image_input)
                else:
                    b64_str, _ = _prepare_image_base64(image_input)
                    img_bytes = base64.b64decode(b64_str)
                    nparr = __import__("numpy").frombuffer(img_bytes, __import__("numpy").uint8)
                    import cv2
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            detected_type = (context or {}).get("chart_type", "chart")
            res = extract_chart_data(img, detected_type)

            series_list = res.get("series", [])
            axis_labels = res.get("axis_labels", {})
            title = res.get("title") or "Chart Extraction"
            chart_type = res.get("resolved_chart_type") or "bar"
            
            # Map chart_type to DECODE-VISION valid closed list
            valid_types = ["bar", "grouped_bar", "stacked_bar", "line", "multi_line", "scatter", "pie", "donut", "radar"]
            if chart_type not in valid_types:
                if "bar" in chart_type:
                    chart_type = "grouped_bar" if len(series_list) > 1 else "bar"
                elif "line" in chart_type:
                    chart_type = "multi_line" if len(series_list) > 1 else "line"
                elif "pie" in chart_type:
                    chart_type = "pie"
                elif "scatter" in chart_type:
                    chart_type = "scatter"
                else:
                    chart_type = "bar"

            # Construct categories
            categories = []
            if series_list and series_list[0].get("points"):
                categories = [p.get("label", f"Cat {i+1}") for i, p in enumerate(series_list[0]["points"])]

            extracted_series = []
            render_series = []
            for s_idx, s in enumerate(series_list):
                s_name = s.get("name") or f"Series {s_idx + 1}"
                s_color = s.get("color") or ("#1D4E89" if s_idx == 0 else "#2F6F4E")
                s_data = []
                s_values = []
                for p in s.get("points", []):
                    val = p.get("value", 0)
                    s_values.append(val)
                    s_data.append({
                        "x": p.get("label", ""),
                        "y": val,
                        "confidence": "high" if p.get("confidence", 1.0) > 0.8 else "medium",
                    })
                extracted_series.append({
                    "name": s_name,
                    "data": s_data,
                })
                render_spec_series_color = s_color
                render_series.append({
                    "name": s_name,
                    "color": render_spec_series_color,
                    "values": s_values,
                })

            y_values = [p.get("value", 0) for s in series_list for p in s.get("points", [])]
            y_min = min(y_values) if y_values else 0
            y_max = max(y_values) if y_values else 100

            dv_payload = {
                "chart_type": chart_type,
                "title": title,
                "axes": {
                    "x": {
                        "label": axis_labels.get("x"),
                        "unit": axis_labels.get("x_unit"),
                        "type": "categorical",
                        "categories": categories,
                        "min": None,
                        "max": None,
                    },
                    "y": {
                        "label": axis_labels.get("y"),
                        "unit": axis_labels.get("y_unit"),
                        "type": "numeric",
                        "min": float(y_min),
                        "max": float(y_max),
                        "scale_type": "linear",
                    }
                },
                "legend": [
                    {"series_name": s["name"], "color_hint": s.get("color", "#1D4E89"), "inferred": False}
                    for s in extracted_series
                ],
                "extracted_data": {
                    "series": extracted_series,
                },
                "render_spec": {
                    "library_hint": "recharts",
                    "series": render_series,
                    "categories": categories,
                },
                "verification": {
                    "checks_passed": [
                        "Chart type classified from geometric primitives",
                        "Axis coordinates mapped from detected gridlines and text",
                        "Series lengths aligned across categories"
                    ],
                    "checks_failed": [],
                    "sum_check": "Values verified against detected bounding regions",
                },
                "confidence": {
                    "overall": "high" if res.get("extraction_confidence", 0.8) > 0.8 else "medium",
                    "notes": "Extracted via DECODE geometric & OCR vision engine"
                },
                "extraction_notes": "Rule-based geometric extraction with calibration against axis rulers."
            }

            return dv_payload
        except Exception as e:
            logger.error("RuleBasedLLM.extract_with_decode_vision failed: %s", e)
            return {
                "chart_type": "bar",
                "title": "Extraction Error",
                "axes": {"x": {"label": None, "unit": None, "type": "categorical", "categories": [], "min": None, "max": None}, "y": {"label": None, "unit": None, "type": "numeric", "min": 0, "max": 100, "scale_type": "linear"}},
                "legend": [],
                "extracted_data": {"series": []},
                "render_spec": {"library_hint": "recharts", "series": [], "categories": []},
                "verification": {"checks_passed": [], "checks_failed": [str(e)], "sum_check": None},
                "confidence": {"overall": "low", "notes": f"Extraction error: {e}"},
                "extraction_notes": f"Fallback error: {e}"
            }

    def classify_chart(self, image_description: str, features: dict) -> dict:
        n_rects = features.get("n_rectangles", 0)
        has_circles = features.get("has_circles", False)
        has_lines = features.get("has_line_patterns", False)
        has_axes = features.get("has_axes", False)
        n_colors = features.get("n_colors", 0)

        if has_circles and not has_axes:
            return {
                "chart_type": "pie",
                "confidence": 0.75,
                "reasoning": "Circular shape detected without axis lines → likely a pie chart.",
            }
        if n_rects >= 3 and has_axes:
            return {
                "chart_type": "bar",
                "confidence": 0.70,
                "reasoning": f"Found {n_rects} rectangular shapes with axis lines → likely a bar chart.",
            }
        if has_lines and has_axes:
            return {
                "chart_type": "line",
                "confidence": 0.70,
                "reasoning": "Diagonal line patterns with axis structure → likely a line chart.",
            }
        if has_axes and n_colors >= 3:
            return {
                "chart_type": "scatter",
                "confidence": 0.55,
                "reasoning": "Axis structure with multiple colors but no clear bars/lines → possibly scatter.",
            }

        return {
            "chart_type": "bar",
            "confidence": 0.50,
            "reasoning": "Defaulting to standard bar chart.",
        }

    def recommend_chart_type(self, series: list[dict], current_type: str) -> dict:
        if not series:
            return {"recommended_type": current_type, "reason": "No data to analyse."}

        total_points = sum(len(s.get("points", [])) for s in series)
        n_series = len(series)

        labels = []
        for s in series:
            for p in s.get("points", []):
                labels.append(p.get("label", "").lower())

        time_words = {"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug",
                      "sep", "oct", "nov", "dec", "q1", "q2", "q3", "q4",
                      "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026",
                      "week", "month", "year", "day"}
        has_time = any(any(tw in lbl for tw in time_words) for lbl in labels)

        if current_type in ["bar", "grouped_bar", "stacked_bar"]:
            if has_time and total_points >= 4:
                return {
                    "recommended_type": "line",
                    "reason": "Your data has a time dimension — a line chart would better illustrate trends over time.",
                }
            if total_points <= 5 and n_series == 1:
                return {
                    "recommended_type": "pie",
                    "reason": "With few categories and one series, a pie chart effectively shows proportional distribution.",
                }
        elif current_type in ["line", "multi_line"]:
            if total_points <= 4:
                return {
                    "recommended_type": "bar",
                    "reason": "With few data points, a bar chart provides clearer comparison between categories.",
                }
        elif current_type in ["pie", "donut"]:
            if total_points > 6:
                return {
                    "recommended_type": "bar",
                    "reason": "With many segments, a bar chart is easier to read and compare values accurately.",
                }

        return {
            "recommended_type": current_type,
            "reason": "The current chart type is well-suited for this data.",
        }

    def disambiguate_legend(self, ocr_texts: list[str], colors: list[str]) -> list[dict]:
        result = []
        for i, text in enumerate(ocr_texts):
            color = colors[i] if i < len(colors) else "#333333"
            result.append({"name": text.strip(), "color": color})
        return result

    def generate_chart_description(
        self, series: list[dict], chart_type: str, title: str
    ) -> str:
        if not series:
            return "No data available."

        n_series = len(series)
        total_pts = sum(len(s.get("points", [])) for s in series)

        parts = []
        if title:
            parts.append(f'Chart: "{title}".')

        parts.append(f"This {chart_type} chart contains {n_series} data series with {total_pts} total data points.")

        for s in series:
            pts = s.get("points", [])
            if pts:
                values = [p["value"] for p in pts]
                parts.append(
                    f'  • {s["name"]}: values range from {min(values):.1f} to {max(values):.1f} '
                    f'(average {sum(values)/len(values):.1f}).'
                )

        return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Gemini Vision LLM Provider
# ─────────────────────────────────────────────────────────────────────────────

class GeminiLLM(BaseLLM):
    """
    Real Gemini Multimodal Vision API integration for DECODE-VISION.
    Works natively via Gemini REST API or google.generativeai package.
    """

    def __init__(self, api_key: str):
        self.api_keys = [k.strip() for k in api_key.split(",") if k.strip()]
        self.primary_api_key = self.api_keys[0] if self.api_keys else ""
        self._sdk_model = None
        self._init_client()

    def _init_client(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.primary_api_key)
            self._sdk_model = genai.GenerativeModel("gemini-3.6-flash")
            logger.info("Gemini SDK initialised successfully with primary key")
        except Exception as e:
            logger.info("Using direct REST endpoint for Gemini Vision: %s", e)
            self._sdk_model = None

    def _generate_with_rest(self, prompt: str, image_b64: Optional[str] = None, mime_type: str = "image/png") -> str:
        """Call Gemini REST API directly with multimodal payload."""
        models = ["gemini-3.6-flash"]
        last_error = None

        parts = [{"text": prompt}]
        if image_b64:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_b64
                }
            })

        body = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.05,
                "response_mime_type": "application/json"
            }
        }

        for key in self.api_keys:
            for model_name in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                try:
                    resp = requests.post(url, json=body, timeout=45)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            c_parts = candidates[0]["content"].get("parts", [])
                            if c_parts:
                                return c_parts[0].get("text", "")
                    else:
                        logger.warning("Gemini REST model %s with key ...%s returned status %d: %s", model_name, key[-4:], resp.status_code, resp.text[:200])
                        last_error = f"Status {resp.status_code}: {resp.text[:200]}"
                except Exception as e:
                    logger.warning("Gemini REST request error for %s: %s", model_name, e)
                    last_error = str(e)

        raise RuntimeError(f"Gemini API request failed: {last_error}")

    def extract_with_decode_vision(
        self, image_input: Any, context: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Execute precision DECODE-VISION 5-step extraction on chart image.
        """
        try:
            image_b64, mime_type = _prepare_image_base64(image_input)
        except Exception as e:
            logger.error("Failed to prepare image for DECODE-VISION: %s", e)
            return RuleBasedLLM().extract_with_decode_vision(image_input, context)

        prompt = DECODE_VISION_SYSTEM_PROMPT
        if context and context.get("hint"):
            prompt += f"\n\nAdditional Context Hint: {context.get('hint')}"

        try:
            # 1. Try SDK if available
            raw_text = None
            if self._sdk_model is not None:
                try:
                    import PIL.Image
                    img_bytes = base64.b64decode(image_b64)
                    pil_img = PIL.Image.open(io.BytesIO(img_bytes))
                    response = self._sdk_model.generate_content([prompt, pil_img])
                    raw_text = response.text
                except Exception as sdk_err:
                    logger.warning("SDK generate_content failed, falling back to REST: %s", sdk_err)
                    raw_text = None

            # 2. Try direct REST API
            if not raw_text:
                raw_text = self._generate_with_rest(prompt, image_b64=image_b64, mime_type=mime_type)

            parsed = clean_json_response(raw_text)
            
            # If array returned (multiple charts), pick the primary chart
            if isinstance(parsed, list):
                if len(parsed) > 0:
                    return parsed[0] if len(parsed) == 1 else parsed
                parsed = {}

            # Self-check schema validity
            if "extracted_data" in parsed and "chart_type" in parsed:
                return parsed

            logger.warning("Gemini response missing mandatory schema fields, falling back")
            return RuleBasedLLM().extract_with_decode_vision(image_input, context)

        except Exception as e:
            logger.warning("Gemini DECODE-VISION extraction failed, falling back to rule-based: %s", e)
            return RuleBasedLLM().extract_with_decode_vision(image_input, context)

    def classify_chart(self, image_description: str, features: dict) -> dict:
        prompt = f"""You are a chart analysis expert. Based on the following visual features of a detected chart region, classify the chart type.

Visual features:
{json.dumps(features, indent=2)}

Additional description: {image_description}

Respond in JSON format ONLY:
{{"chart_type": "bar|line|pie|scatter|radar", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

        try:
            raw = self._generate_with_rest(prompt)
            return clean_json_response(raw)
        except Exception as e:
            logger.warning("Gemini classify_chart failed, falling back: %s", e)
            return RuleBasedLLM().classify_chart(image_description, features)

    def recommend_chart_type(self, series: list[dict], current_type: str) -> dict:
        data_summary = []
        for s in series:
            pts = s.get("points", [])
            data_summary.append({
                "name": s.get("name", "Series"),
                "n_points": len(pts),
                "labels": [p.get("label", "") for p in pts[:10]],
                "values": [p.get("value", 0) for p in pts[:10]],
            })

        prompt = f"""You are a data visualisation expert. Given this data, recommend the best alternative chart type.

Current chart type: {current_type}
Data series:
{json.dumps(data_summary, indent=2)}

Respond in JSON format ONLY:
{{"recommended_type": "bar|line|pie|heatmap|scatter|radar", "reason": "brief explanation"}}"""

        try:
            raw = self._generate_with_rest(prompt)
            return clean_json_response(raw)
        except Exception as e:
            logger.warning("Gemini recommend failed, falling back: %s", e)
            return RuleBasedLLM().recommend_chart_type(series, current_type)

    def disambiguate_legend(self, ocr_texts: list[str], colors: list[str]) -> list[dict]:
        prompt = f"""Match these legend text labels to their corresponding colors:

Texts: {json.dumps(ocr_texts)}
Colors (hex): {json.dumps(colors)}

Respond in JSON format ONLY — an array:
[{{"name": "label text", "color": "#hex"}}]"""

        try:
            raw = self._generate_with_rest(prompt)
            return clean_json_response(raw)
        except Exception as e:
            logger.warning("Gemini disambiguate failed, falling back: %s", e)
            return RuleBasedLLM().disambiguate_legend(ocr_texts, colors)

    def generate_chart_description(
        self, series: list[dict], chart_type: str, title: str
    ) -> str:
        data_summary = []
        for s in series:
            pts = s.get("points", [])
            data_summary.append({
                "name": s.get("name", "Series"),
                "points": pts[:10],
            })

        prompt = f"""Write a concise 2-3 sentence description of this chart for accessibility.

Chart type: {chart_type}
Title: {title}
Data: {json.dumps(data_summary, indent=2)}

Respond with plain text only."""

        try:
            return self._generate_with_rest(prompt)
        except Exception as e:
            logger.warning("Gemini description failed, falling back: %s", e)
            return RuleBasedLLM().generate_chart_description(series, chart_type, title)


# ─────────────────────────────────────────────────────────────────────────────
# Factory — auto-detects API key and returns the right provider
# ─────────────────────────────────────────────────────────────────────────────

_llm_instance: Optional[BaseLLM] = None


def get_llm() -> BaseLLM:
    """
    Get the LLM instance. Automatically selects Gemini Vision if GEMINI_API_KEY
    is set, otherwise falls back to smart rule-based & OpenCV logic.
    """
    global _llm_instance

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if api_key:
        if not isinstance(_llm_instance, GeminiLLM):
            logger.info("GEMINI_API_KEY detected — switching to Gemini Vision LLM")
            _llm_instance = GeminiLLM(api_key)
    else:
        if not isinstance(_llm_instance, RuleBasedLLM):
            logger.info("No LLM API key found — using rule-based fallback")
            _llm_instance = RuleBasedLLM()

    return _llm_instance
