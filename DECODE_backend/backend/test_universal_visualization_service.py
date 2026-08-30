from pathlib import Path
import tempfile

from core.canonical_data_model import (
    CanonicalDataset,
    DataSeries,
    DataPoint,
)

from core.visualization.service import (
    UniversalVisualizationService,
)


def build_dataset():

    return CanonicalDataset(
        title="Revenue Performance",
        x_axis_label="Year",
        y_axis_label="Revenue",
        unit="₹",
        categories=[
            "2023",
            "2024",
            "2025",
        ],
        series=[
            DataSeries(
                name="Revenue",
                points=[
                    DataPoint(
                        category="2023",
                        value=100,
                        series="Revenue",
                        confidence=1.0,
                        source="test",
                    ),
                    DataPoint(
                        category="2024",
                        value=140,
                        series="Revenue",
                        confidence=1.0,
                        source="test",
                    ),
                    DataPoint(
                        category="2025",
                        value=180,
                        series="Revenue",
                        confidence=1.0,
                        source="test",
                    ),
                ],
            )
        ],
        detected_type="chart",
        extraction_method="test",
        overall_confidence=1.0,
    )


def main():

    print("=== UNIVERSAL VISUALIZATION SERVICE TEST ===")

    dataset = build_dataset()

    service = UniversalVisualizationService()

    payload = dataset.to_dict()

    # Rehydration.
    restored = service.load_dataset(payload)

    assert restored.categories == dataset.categories

    assert (
        restored.series[0].points[1].value
        == 140
    )

    # Validation.
    validation = service.validate(
        payload,
        "bar",
    )

    assert validation["valid"] is True

    # Render.
    with tempfile.TemporaryDirectory() as tmp:

        result = service.render(
            payload=payload,
            visualization_type="bar",
            export_dir=tmp,
            export_prefix="universal_test",
        )

        assert result["visualization_type"] == "bar"

        assert result["dataset"]["categories"] == [
            "2023",
            "2024",
            "2025",
        ]

        assert result["result"]["svg"]

        svg_path = Path(
            result["result"]["svg_path"]
        )

        assert svg_path.exists()

    print(
        "UNIVERSAL VISUALIZATION SERVICE TEST PASSED"
    )


if __name__ == "__main__":
    main()
