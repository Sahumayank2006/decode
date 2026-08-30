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


def test_deterministic_rendering():

    dataset = CanonicalDataset.from_dict(
        {
            "title": "Deterministic Test",
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

    spec = VisualizationSpec(
        chart_type="bar",
        title="Deterministic Test",
    )

    renderer = CanonicalRenderer()

    svg1 = renderer.render_svg(
        dataset,
        spec,
    )

    svg2 = renderer.render_svg(
        dataset,
        spec,
    )

    assert svg1 == svg2

    assert "<svg" in svg1
    assert "</svg>" in svg1

    assert "NaN" not in svg1
    assert "Infinity" not in svg1

    print(
        "DETERMINISTIC RENDERING TEST PASSED"
    )


if __name__ == "__main__":
    test_deterministic_rendering()
