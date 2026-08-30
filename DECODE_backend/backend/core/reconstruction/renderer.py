from __future__ import annotations

from core.canonical_data_model import (
    CanonicalDataset,
)

from .spec import VisualizationSpec
from .svg_renderer import SVGChartRenderer


class CanonicalRenderer:

    def __init__(self):

        self.svg_renderer = (
            SVGChartRenderer()
        )

    def render_svg(
        self,
        dataset: CanonicalDataset,
        spec: VisualizationSpec,
    ) -> str:

        return self.svg_renderer.render(
            dataset,
            spec,
        )
