from pathlib import Path

from core.canonical_data_model import (
    CanonicalDataset,
    DataSeries,
    DataPoint,
)

from core.reconstruction import (
    VisualizationSpec,
    CanonicalReconstructionService,
)


def build_dataset():

    dataset = CanonicalDataset(

        title="Revenue & Profit",

        x_axis_label="Year",

        y_axis_label="Amount",

        detected_type="bar",

        extraction_method="test",

    )

    revenue = DataSeries(

        name="Revenue",

        color="#2563EB",
    )

    profit = DataSeries(

        name="Profit",

        color="#16A34A",
    )

    for category, revenue_value, profit_value in [

        ("2023", 100, 40),

        ("2024", 140, 65),

        ("2025", 180, 90),

    ]:

        revenue.points.append(
            DataPoint(
                category=category,
                value=revenue_value,
                series="Revenue",
                confidence=1.0,
                source="test",
            )
        )

        profit.points.append(
            DataPoint(
                category=category,
                value=profit_value,
                series="Profit",
                confidence=1.0,
                source="test",
            )
        )

    dataset.add_series(
        revenue
    )

    dataset.add_series(
        profit
    )

    dataset.ensure_categories()

    dataset.rebuild_numeric_values()

    return dataset


def main():

    dataset = build_dataset()

    service = (
        CanonicalReconstructionService()
    )

    output_dir = Path(
        "test_exports"
    )

    spec = VisualizationSpec(

        chart_type="bar",

        width=1200,

        height=700,

        title="Revenue & Profit",

        x_axis_label="Year",

        y_axis_label="Amount",

        palette_name="professional",
    )

    result = service.reconstruct(

        dataset=dataset,

        spec=spec,

        export_dir=str(
            output_dir
        ),

        export_prefix="canonical_test",
    )

    print(
        "\n=== RECONSTRUCTION RESULT ==="
    )

    print(
        result
    )

    assert (
        "<svg"
        in result["svg"]
    )

    assert (
        "</svg>"
        in result["svg"]
    )

    assert Path(
        result["svg_path"]
    ).exists()

    assert Path(
        result["png_path"]
    ).exists()

    print(
        "\nCANONICAL RECONSTRUCTION "
        "TEST PASSED"
    )


if __name__ == "__main__":

    main()
