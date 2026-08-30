from core.canonical_data_model import (
    CanonicalDataset,
    DataPoint,
    DataSeries,
)

from core.visualization import (
    dataset_to_table,
    convert_dataset,
    convert_table_to_visualization,
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
            source="test",
        ),
        DataPoint(
            category="2024",
            value=140.0,
            series="Revenue",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2025",
            value=180.0,
            series="Revenue",
            confidence=1.0,
            source="test",
        ),
    ]

    profit = DataSeries(
        name="Profit",
        color="#16A34A",
    )

    profit.points = [
        DataPoint(
            category="2023",
            value=40.0,
            series="Profit",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2024",
            value=65.0,
            series="Profit",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2025",
            value=90.0,
            series="Profit",
            confidence=1.0,
            source="test",
        ),
    ]

    return CanonicalDataset(

        title="Financial Performance",

        x_axis_label="Year",

        y_axis_label="Amount",

        categories=[
            "2023",
            "2024",
            "2025",
        ],

        series=[
            revenue,
            profit,
        ],

        numeric_values=[
            100.0,
            140.0,
            180.0,
            40.0,
            65.0,
            90.0,
        ],

        detected_type="table",

        extraction_method="test",

        overall_confidence=1.0,
    )


def main():

    dataset = build_dataset()

    # -------------------------------------------------
    # DATASET -> TABLE
    # -------------------------------------------------

    table = dataset_to_table(
        dataset
    )

    assert table["columns"] == [
        "Category",
        "Revenue",
        "Profit",
    ]

    assert len(
        table["rows"]
    ) == 3

    assert (
        table["rows"][0]["Revenue"]
        == 100.0
    )

    assert (
        table["rows"][2]["Profit"]
        == 90.0
    )

    # -------------------------------------------------
    # DATASET -> BAR
    # -------------------------------------------------

    bar = convert_dataset(
        dataset,
        "bar",
    )

    assert bar["type"] == "bar"

    assert (
        bar["spec"]["chart_type"]
        == "bar"
    )

    # -------------------------------------------------
    # DATASET -> LINE
    # -------------------------------------------------

    line = convert_dataset(
        dataset,
        "line",
    )

    assert line["type"] == "line"

    assert (
        line["spec"]["chart_type"]
        == "line"
    )

    # -------------------------------------------------
    # TABLE -> LINE
    # -------------------------------------------------

    converted = (
        convert_table_to_visualization(
            table,
            "line",
        )
    )

    assert (
        converted["type"]
        == "line"
    )

    assert (
        converted["dataset"]["categories"]
        == [
            "2023",
            "2024",
            "2025",
        ]
    )

    # -------------------------------------------------
    # NUMERICAL INTEGRITY
    # -------------------------------------------------

    converted_series = (
        converted["dataset"]["series"]
    )

    assert (
        converted_series[0]["points"][0][
            "value"
        ]
        == 100.0
    )

    assert (
        converted_series[0]["points"][2][
            "value"
        ]
        == 180.0
    )

    assert (
        converted_series[1]["points"][0][
            "value"
        ]
        == 40.0
    )

    assert (
        converted_series[1]["points"][2][
            "value"
        ]
        == 90.0
    )

    print(
        "VISUALIZATION CONVERSION TEST PASSED"
    )


if __name__ == "__main__":
    main()
