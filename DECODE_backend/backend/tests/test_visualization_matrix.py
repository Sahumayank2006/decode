import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canonical_data_model import (
    CanonicalDataset,
)

from core.reconstruction.spec import (
    VisualizationSpec,
)

from core.reconstruction.renderer import (
    CanonicalRenderer,
)


CHART_TYPES = [
    "bar",
    "line",
    "area",
    "scatter",
    "pie",
    "donut",
    "table",
]


def make_dataset():
    return CanonicalDataset.from_dict(
        {
            "title": "Matrix Test",
            "x_axis_label": "Category",
            "y_axis_label": "Value",

            "categories": [
                "A",
                "B",
                "C",
            ],

            "series": [
                {
                    "name": "Series 1",
                    "points": [
                        {
                            "category": "A",
                            "value": 10,
                        },
                        {
                            "category": "B",
                            "value": 20,
                        },
                        {
                            "category": "C",
                            "value": 30,
                        },
                    ],
                }
            ],
        }
    )


def test_visualization_matrix():

    dataset = make_dataset()
    renderer = CanonicalRenderer()

    for chart_type in CHART_TYPES:

        spec = VisualizationSpec(
            chart_type=chart_type,
            title=f"Matrix {chart_type}",
        )

        svg = renderer.render_svg(
            dataset,
            spec,
        )

        assert isinstance(svg, str)
        assert len(svg) > 100

        assert "<svg" in svg
        assert "</svg>" in svg

        assert "NaN" not in svg
        assert "Infinity" not in svg

        print(
            f"{chart_type.upper()} RENDER TEST PASSED"
        )

    print(
        "VISUALIZATION MATRIX TEST PASSED"
    )


if __name__ == "__main__":
    test_visualization_matrix()
