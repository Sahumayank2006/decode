from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from core.canonical_data_model import (
    CanonicalDataset,
)

from .renderer import CanonicalRenderer
from .spec import VisualizationSpec
from .png_exporter import svg_to_png


class CanonicalReconstructionService:

    def __init__(self):

        self.renderer = (
            CanonicalRenderer()
        )

    def reconstruct(
        self,
        dataset: CanonicalDataset,
        spec: VisualizationSpec,
        export_dir: str,
        export_prefix: str = "chart",
    ) -> Dict[str, Any]:

        export_directory = Path(
            export_dir
        )

        export_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        svg = self.renderer.render_svg(
            dataset,
            spec,
        )

        svg_path = (
            export_directory
            / f"{export_prefix}.svg"
        )

        png_path = (
            export_directory
            / f"{export_prefix}.png"
        )

        svg_path.write_text(
            svg,
            encoding="utf-8",
        )

        import logging
        try:
            svg_to_png(
                svg,
                str(png_path),
            )
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to generate PNG from SVG: {e}")

        return {

            "chart_type": (
                spec.chart_type
            ),

            "chart_config": (
                spec.to_dict()
            ),

            "svg": svg,

            "svg_path": str(
                svg_path
            ),

            "png_path": str(
                png_path
            ),
        }
