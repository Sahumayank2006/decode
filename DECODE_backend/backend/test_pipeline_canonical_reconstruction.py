from pathlib import Path

from core.canonical_data_model import (
    CanonicalDataset,
    DataSeries,
    DataPoint,
)

from core.reconstruction import (
    CanonicalReconstructionService,
    VisualizationSpec,
)


def build_dataset():

    revenue = DataSeries(
        name="Revenue",
        color="#2563EB",
    )

    revenue.points = [
        DataPoint(
            category="2023",
            value=100.0,
            series="Revenue",
            confidence=1.0,
            source="integration_test",
        ),
        DataPoint(
            category="2024",
            value=140.0,
            series="Revenue",
            confidence=1.0,
            source="integration_test",
        ),
        DataPoint(
            category="2025",
            value=180.0,
            series="Revenue",
            confidence=1.0,
            source="integration_test",
        ),
    ]

    dataset = CanonicalDataset(

        title="Integration Test",

        x_axis_label="Year",

        y_axis_label="Revenue",

        categories=[
            "2023",
            "2024",
            "2025",
        ],

        series=[
            revenue,
        ],

        detected_type="bar",

        extraction_method="integration_test",

        overall_confidence=1.0,
    )

    dataset.rebuild_numeric_values()

    return dataset


def main():

    dataset = build_dataset()

    payload = dataset.to_dict()

    restored = (
        CanonicalDataset.from_dict(
            payload
        )
    )

    assert isinstance(
        restored,
        CanonicalDataset,
    )

    assert (
        restored.title
        == "Integration Test"
    )

    assert (
        len(restored.series)
        == 1
    )

    assert (
        len(
            restored.series[0].points
        )
        == 3
    )

    output_dir = Path(
        "test_exports"
        / Path("pipeline_canonical")
    )

    service = (
        CanonicalReconstructionService()
    )

    result = service.reconstruct(

        dataset=restored,

        spec=VisualizationSpec(
            chart_type="bar",
            title="Integration Test",
            x_axis_label="Year",
            y_axis_label="Revenue",
        ),

        export_dir=str(
            output_dir
        ),

        export_prefix="pipeline",
    )

    assert "<svg" in result["svg"]

    assert Path(
        result["svg_path"]
    ).exists()

    assert Path(
        result["png_path"]
    ).exists()

    print(
        "PIPELINE CANONICAL "
        "RECONSTRUCTION TEST PASSED"
    )


if __name__ == "__main__":
    main()
