"""
DECODE – LLM Service
Provides chart type classification, legend disambiguation, and alternative
chart type recommendations.

Architecture:
  • If GEMINI_API_KEY is set in .env → uses the real Gemini API
  • Otherwise → falls back to smart rule-based logic
  • The switch is automatic — no code changes needed

Usage:
    from services.llm_service import get_llm
    llm = get_llm()
    result = llm.classify_chart(image_description, features)
    result = llm.recommend_chart_type(series_data, current_type)
    result = llm.disambiguate_legend(ocr_texts, colors)
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger("decode.llm")


# ─────────────────────────────────────────────────────────────────────────────
# Abstract LLM interface
# ─────────────────────────────────────────────────────────────────────────────

class BaseLLM(ABC):
    """Common interface for LLM providers."""

    @abstractmethod
    def classify_chart(
        self, image_description: str, features: dict
    ) -> dict:
        """
        Classify a chart type from visual features.
        Returns: {"chart_type": str, "confidence": float, "reasoning": str}
        """
        ...

    @abstractmethod
    def recommend_chart_type(
        self, series: list[dict], current_type: str
    ) -> dict:
        """
        Recommend the best alternative chart type.
        Returns: {"recommended_type": str, "reason": str}
        """
        ...

    @abstractmethod
    def disambiguate_legend(
        self, ocr_texts: list[str], colors: list[str]
    ) -> list[dict]:
        """
        Match legend text entries to colors / series.
        Returns: [{"name": str, "color": str}]
        """
        ...

    @abstractmethod
    def generate_chart_description(
        self, series: list[dict], chart_type: str, title: str
    ) -> str:
        """Generate a human-readable description of the chart data."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Rule-based fallback  (no API key required)
# ─────────────────────────────────────────────────────────────────────────────

class RuleBasedLLM(BaseLLM):
    """
    Smart rule-based fallback when no LLM API key is available.
    Uses heuristics and pattern matching for chart intelligence.
    """

    def classify_chart(self, image_description: str, features: dict) -> dict:
        # Use the features from chart_detector
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
            "chart_type": "other",
            "confidence": 0.40,
            "reasoning": "Could not confidently classify chart type from visual features.",
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

        if current_type == "bar":
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
        elif current_type == "line":
            if total_points <= 4:
                return {
                    "recommended_type": "bar",
                    "reason": "With few data points, a bar chart provides clearer comparison between categories.",
                }
        elif current_type == "pie":
            if total_points > 6:
                return {
                    "recommended_type": "bar",
                    "reason": "With many segments, a bar chart is easier to read and compare values accurately.",
                }

        if n_series >= 3 and current_type != "heatmap":
            return {
                "recommended_type": "heatmap",
                "reason": "Multiple data series can be compared more effectively in a heatmap format.",
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
# Gemini LLM provider
# ─────────────────────────────────────────────────────────────────────────────

class GeminiLLM(BaseLLM):
    """
    Real Gemini API integration.
    Activated automatically when GEMINI_API_KEY is set in environment.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._model = None
        self._init_client()

    def _init_client(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Gemini LLM initialised successfully")
        except ImportError:
            logger.warning(
                "google-generativeai package not installed. "
                "Install via: pip install google-generativeai"
            )
            self._model = None
        except Exception as e:
            logger.error("Failed to initialise Gemini: %s", e)
            self._model = None

    def _generate(self, prompt: str) -> str:
        if self._model is None:
            raise RuntimeError("Gemini model not initialised")
        response = self._model.generate_content(prompt)
        return response.text

    def classify_chart(self, image_description: str, features: dict) -> dict:
        if self._model is None:
            return RuleBasedLLM().classify_chart(image_description, features)

        prompt = f"""You are a chart analysis expert. Based on the following visual features of a detected chart region, classify the chart type.

Visual features:
{json.dumps(features, indent=2)}

Additional description: {image_description}

Respond in JSON format ONLY:
{{"chart_type": "bar|line|pie|scatter|other", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

        try:
            text = self._generate(prompt)
            # Extract JSON from response
            text = text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            logger.warning("Gemini classify_chart failed, falling back: %s", e)
            return RuleBasedLLM().classify_chart(image_description, features)

    def recommend_chart_type(self, series: list[dict], current_type: str) -> dict:
        if self._model is None:
            return RuleBasedLLM().recommend_chart_type(series, current_type)

        # Summarise data for the prompt (avoid sending too much)
        data_summary = []
        for s in series:
            pts = s.get("points", [])
            data_summary.append({
                "name": s["name"],
                "n_points": len(pts),
                "labels": [p["label"] for p in pts[:10]],
                "values": [p["value"] for p in pts[:10]],
            })

        prompt = f"""You are a data visualisation expert. Given this data, recommend the best alternative chart type.

Current chart type: {current_type}
Data series:
{json.dumps(data_summary, indent=2)}

Respond in JSON format ONLY:
{{"recommended_type": "bar|line|pie|heatmap|scatter", "reason": "brief explanation"}}"""

        try:
            text = self._generate(prompt)
            text = text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            logger.warning("Gemini recommend failed, falling back: %s", e)
            return RuleBasedLLM().recommend_chart_type(series, current_type)

    def disambiguate_legend(self, ocr_texts: list[str], colors: list[str]) -> list[dict]:
        if self._model is None:
            return RuleBasedLLM().disambiguate_legend(ocr_texts, colors)

        prompt = f"""Match these legend text labels to their corresponding colors:

Texts: {json.dumps(ocr_texts)}
Colors (hex): {json.dumps(colors)}

Respond in JSON format ONLY — an array:
[{{"name": "label text", "color": "#hex"}}]"""

        try:
            text = self._generate(prompt)
            text = text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            logger.warning("Gemini disambiguate failed, falling back: %s", e)
            return RuleBasedLLM().disambiguate_legend(ocr_texts, colors)

    def generate_chart_description(
        self, series: list[dict], chart_type: str, title: str
    ) -> str:
        if self._model is None:
            return RuleBasedLLM().generate_chart_description(series, chart_type, title)

        data_summary = []
        for s in series:
            pts = s.get("points", [])
            data_summary.append({
                "name": s["name"],
                "points": pts[:10],
            })

        prompt = f"""Write a concise 2-3 sentence description of this chart for accessibility.

Chart type: {chart_type}
Title: {title}
Data: {json.dumps(data_summary, indent=2)}

Respond with plain text only."""

        try:
            return self._generate(prompt)
        except Exception as e:
            logger.warning("Gemini description failed, falling back: %s", e)
            return RuleBasedLLM().generate_chart_description(series, chart_type, title)


# ─────────────────────────────────────────────────────────────────────────────
# Factory — auto-detects API key and returns the right provider
# ─────────────────────────────────────────────────────────────────────────────

_llm_instance: Optional[BaseLLM] = None


def get_llm() -> BaseLLM:
    """
    Get the LLM instance.  Automatically selects Gemini if GEMINI_API_KEY
    is set, otherwise falls back to rule-based logic.

    The switch is entirely automatic — just add GEMINI_API_KEY to .env
    and restart the server.
    """
    global _llm_instance

    # Check on every call so hot-reload picks up new env vars
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if api_key:
        if not isinstance(_llm_instance, GeminiLLM):
            logger.info("GEMINI_API_KEY detected — switching to Gemini LLM")
            _llm_instance = GeminiLLM(api_key)
    else:
        if not isinstance(_llm_instance, RuleBasedLLM):
            logger.info("No LLM API key found — using rule-based fallback")
            _llm_instance = RuleBasedLLM()

    return _llm_instance
