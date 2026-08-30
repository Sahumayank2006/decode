from core.canonical_data_model import (
    CanonicalDataset,
    DataPoint,
    DataSeries,
)

from core.visualization import (
    list_visualization_types,
    can_convert_to_visualization,
    recommend_best_visualization,
    recommend_visualizations,
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
        ),
        DataPoint(
            category="2024",
            value=140.0,
            series="Revenue",
            confidence=1.0,
        ),
        DataPoint(
            category="2025",
            value=180.0,
            series="Revenue",
            confidence=1.0,
        ),
    ]

    dataset = CanonicalDataset(

        title="Revenue",

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

        numeric_values=[
            100.0,
            140.0,
            180.0,
        ],

        detected_type="bar",

        extraction_method="test",

        overall_confidence=1.0,
    )

    return dataset


def main():

    dataset = build_dataset()

    types = (
        list_visualization_types()
    )

    assert "bar" in types
    assert "line" in types
    assert "area" in types
    assert "table" in types

    assert can_convert_to_visualization(
        dataset,
        "bar",
    )

    assert can_convert_to_visualization(
        dataset,
        "line",
    )

    assert can_convert_to_visualization(
        dataset,
        "area",
    )

    recommendations = (
        recommend_visualizations(
            dataset
        )
    )

    assert recommendations

    best = (
        recommend_best_visualization(
            dataset
        )
    )

    assert best.visualization_type in {
        "bar",
        "line",
        "area",
    }

    assert 0.0 <= best.score <= 1.0

    print(
        "VISUALIZATION REGISTRY TEST PASSED"
    )


if __name__ == "__main__":
    main()
