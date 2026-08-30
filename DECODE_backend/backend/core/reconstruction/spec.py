from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VisualizationSpec:
    """
    Rendering instructions for a CanonicalDataset.

    CanonicalDataset contains WHAT the data is.

    VisualizationSpec contains HOW the data should
    be displayed.
    """

    chart_type: str = "bar"

    width: int = 1200
    height: int = 700

    title: str = ""

    x_axis_label: str = ""
    y_axis_label: str = ""

    show_legend: bool = True
    show_grid: bool = True

    palette_name: str = "default"

    background: str = "#FFFFFF"

    text_color: str = "#1F2937"

    grid_color: str = "#E5E7EB"

    axis_color: str = "#64748B"

    font_family: str = (
        "Inter, Arial, sans-serif"
    )

    font_size: int = 14

    title_font_size: int = 28

    series_colors: Dict[
        str,
        str
    ] = field(
        default_factory=dict
    )

    margin_left: int = 90
    margin_right: int = 50
    margin_top: int = 90
    margin_bottom: int = 90

    extra: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "chart_type": self.chart_type,
            "width": self.width,
            "height": self.height,
            "title": self.title,
            "x_axis_label": self.x_axis_label,
            "y_axis_label": self.y_axis_label,
            "show_legend": self.show_legend,
            "show_grid": self.show_grid,
            "palette_name": self.palette_name,
            "background": self.background,
            "text_color": self.text_color,
            "grid_color": self.grid_color,
            "axis_color": self.axis_color,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "title_font_size": self.title_font_size,
            "series_colors": dict(
                self.series_colors
            ),
            "margin_left": self.margin_left,
            "margin_right": self.margin_right,
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
            "extra": dict(
                self.extra
            ),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "VisualizationSpec":

        return cls(

            chart_type=data.get(
                "chart_type",
                "bar",
            ),

            width=int(
                data.get(
                    "width",
                    1200,
                )
            ),

            height=int(
                data.get(
                    "height",
                    700,
                )
            ),

            title=str(
                data.get(
                    "title",
                    "",
                )
            ),

            x_axis_label=str(
                data.get(
                    "x_axis_label",
                    "",
                )
            ),

            y_axis_label=str(
                data.get(
                    "y_axis_label",
                    "",
                )
            ),

            show_legend=bool(
                data.get(
                    "show_legend",
                    True,
                )
            ),

            show_grid=bool(
                data.get(
                    "show_grid",
                    True,
                )
            ),

            palette_name=str(
                data.get(
                    "palette_name",
                    "default",
                )
            ),

            background=str(
                data.get(
                    "background",
                    "#FFFFFF",
                )
            ),

            text_color=str(
                data.get(
                    "text_color",
                    "#1F2937",
                )
            ),

            grid_color=str(
                data.get(
                    "grid_color",
                    "#E5E7EB",
                )
            ),

            axis_color=str(
                data.get(
                    "axis_color",
                    "#64748B",
                )
            ),

            font_family=str(
                data.get(
                    "font_family",
                    "Inter, Arial, sans-serif",
                )
            ),

            font_size=int(
                data.get(
                    "font_size",
                    14,
                )
            ),

            title_font_size=int(
                data.get(
                    "title_font_size",
                    28,
                )
            ),

            series_colors=dict(
                data.get(
                    "series_colors",
                    {},
                )
            ),

            margin_left=int(
                data.get(
                    "margin_left",
                    90,
                )
            ),

            margin_right=int(
                data.get(
                    "margin_right",
                    50,
                )
            ),

            margin_top=int(
                data.get(
                    "margin_top",
                    90,
                )
            ),

            margin_bottom=int(
                data.get(
                    "margin_bottom",
                    90,
                )
            ),

            extra=dict(
                data.get(
                    "extra",
                    {},
                )
            ),
        )
