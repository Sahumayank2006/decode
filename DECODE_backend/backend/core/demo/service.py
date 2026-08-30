from __future__ import annotations

import base64
import io
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.visualization.service import UniversalVisualizationService


class DemoService:
    """
    Thin product-facing orchestration layer.

    This service intentionally does NOT perform:
        - OCR
        - extraction
        - canonicalization
        - chart detection
        - chart reconstruction

    Those responsibilities remain in the existing pipeline.

    DemoService exists to provide a stable frontend-facing contract.
    """

    VERSION = "5.1.0"

    def __init__(self, db=None):
        self.db = db
        self.visualization = UniversalVisualizationService()

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clean_chart_type(chart_type: Optional[str]) -> str:
        if not chart_type:
            return "bar"

        value = str(chart_type).strip().lower()

        aliases = {
            "column": "bar",
            "columns": "bar",
            "bar_chart": "bar",
            "line_chart": "line",
            "area_chart": "area",
            "scatter_plot": "scatter",
            "pie_chart": "pie",
            "donut_chart": "donut",
            "table_chart": "table",
        }

        return aliases.get(value, value)

    @staticmethod
    def _encode_svg(svg: str) -> str:
        if not svg:
            return ""

        return base64.b64encode(
            svg.encode("utf-8")
        ).decode("ascii")

    @staticmethod
    def _response(
        *,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:

        result = {
            "success": bool(success),
            "version": DemoService.VERSION,
            "timestamp": DemoService._now(),
        }

        if data:
            result["data"] = data

        if error:
            result["error"] = error

        return result

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        return self._response(
            success=True,
            data={
                "service": "DECODE",
                "status": "healthy",
                "version": self.VERSION,
                "visualization_types": [
                    "bar",
                    "line",
                    "area",
                    "scatter",
                    "pie",
                    "donut",
                    "table",
                ],
            },
        )

    # ------------------------------------------------------------------
    # Visualization capabilities
    # ------------------------------------------------------------------

    def capabilities(self) -> Dict[str, Any]:
        chart_types = [
            "bar",
            "line",
            "area",
            "scatter",
            "pie",
            "donut",
            "table",
        ]

        supported = []

        for chart_type in chart_types:
            try:
                supported.append(
                    {
                        "chart_type": chart_type,
                        "supported": bool(
                            self.visualization.supports(chart_type)
                        ),
                    }
                )
            except Exception:
                supported.append(
                    {
                        "chart_type": chart_type,
                        "supported": False,
                    }
                )

        return self._response(
            success=True,
            data={
                "chart_types": supported,
                "count": len(supported),
            },
        )

    # ------------------------------------------------------------------
    # Render canonical visualization
    # ------------------------------------------------------------------

    def render(
        self,
        dataset,
        chart_type: str = "bar",
        palette: str = "default",
        export_png: bool = True,
        export_svg: bool = True,
    ) -> Dict[str, Any]:

        chart_type = self._clean_chart_type(chart_type)

        try:
            result = self.visualization.render(
                dataset=dataset,
                chart_type=chart_type,
                palette_name=palette,
            )

            svg = ""

            if isinstance(result, dict):
                svg = result.get("svg", "") or ""

            elif isinstance(result, str):
                svg = result

            response_data = {
                "chart_type": chart_type,
                "palette": palette,
                "svg": svg if export_svg else "",
                "svg_base64": self._encode_svg(svg)
                if export_svg
                else "",
                "png_base64": "",
            }

            # PNG generation is intentionally best-effort.
            #
            # SVG remains the canonical visual representation.
            # PNG is an export convenience.
            if export_png:
                try:
                    png = self._extract_png(result)

                    if png:
                        response_data["png_base64"] = (
                            base64.b64encode(png).decode("ascii")
                        )

                except Exception:
                    response_data["png_base64"] = ""

            return self._response(
                success=True,
                data=response_data,
            )

        except ValueError as exc:
            return self._response(
                success=False,
                error=str(exc),
            )

        except Exception as exc:
            return self._response(
                success=False,
                error=f"Visualization rendering failed: {exc}",
            )

    # ------------------------------------------------------------------
    # Result normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_png(result) -> bytes:
        if result is None:
            return b""

        if isinstance(result, dict):

            value = (
                result.get("png")
                or result.get("png_bytes")
                or result.get("image")
            )

            if isinstance(value, bytes):
                return value

            if isinstance(value, str):
                try:
                    return base64.b64decode(value)
                except Exception:
                    return b""

        return b""

    # ------------------------------------------------------------------
    # Demo metadata
    # ------------------------------------------------------------------

    def product_info(self) -> Dict[str, Any]:
        return self._response(
            success=True,
            data={
                "name": "DECODE",
                "tagline": (
                    "Intelligent PDF chart extraction, "
                    "reconstruction and visualization"
                ),
                "version": self.VERSION,
                "architecture": {
                    "extraction": "PDF/OCR",
                    "normalization": "CanonicalDataset",
                    "visualization": "UniversalVisualizationService",
                    "rendering": "SVGChartRenderer",
                    "exports": [
                        "SVG",
                        "PNG",
                    ],
                },
                "visualizations": [
                    {
                        "type": "bar",
                        "label": "Bar Chart",
                    },
                    {
                        "type": "line",
                        "label": "Line Chart",
                    },
                    {
                        "type": "area",
                        "label": "Area Chart",
                    },
                    {
                        "type": "scatter",
                        "label": "Scatter Plot",
                    },
                    {
                        "type": "pie",
                        "label": "Pie Chart",
                    },
                    {
                        "type": "donut",
                        "label": "Donut Chart",
                    },
                    {
                        "type": "table",
                        "label": "Data Table",
                    },
                ],
            },
        )
