from core.canonical_data_model import (
    CanonicalDataset,
    DataPoint,
    DataSeries,
    canonical_to_table,
    table_to_canonical,
)


def main():

    dataset = CanonicalDataset(
        title="Test Revenue",
        detected_type="bar",
        extraction_method="test",
        overall_confidence=0.98,
    )

    revenue = DataSeries(
        name="Revenue"
    )

    revenue.points = [

        DataPoint(
            category="2023",
            value=100,
            series="Revenue",
            confidence=0.99,
            source="test",
        ),

        DataPoint(
            category="2024",
            value=140,
            series="Revenue",
            confidence=0.98,
            source="test",
        ),

        DataPoint(
            category="2025",
            value=180,
            series="Revenue",
            confidence=0.97,
            source="test",
        ),
    ]

    profit = DataSeries(
        name="Profit"
    )

    profit.points = [

        DataPoint(
            category="2023",
            value=40,
            series="Profit",
            confidence=0.99,
            source="test",
        ),

        DataPoint(
            category="2024",
            value=65,
            series="Profit",
            confidence=0.98,
            source="test",
        ),

        DataPoint(
            category="2025",
            value=90,
            series="Profit",
            confidence=0.97,
            source="test",
        ),
    ]

    dataset.add_series(
        revenue
    )

    dataset.add_series(
        profit
    )

    print(
        "\n=== CANONICAL DATASET ==="
    )

    print(
        dataset.to_dict()
    )

    table = canonical_to_table(
        dataset
    )

    print(
        "\n=== TABLE ==="
    )

    print(table)

    rebuilt = table_to_canonical(
        table,
        title="Rebuilt Dataset",
    )

    print(
        "\n=== REBUILT DATASET ==="
    )

    print(
        rebuilt.to_dict()
    )

    assert (
        len(
            rebuilt.series
        ) == 2
    )

    assert (
        len(
            rebuilt.categories
        ) == 3
    )

    assert (
        rebuilt.numeric_values
    )

    print(
        "\nCANONICAL MODEL TEST PASSED"
    )


if __name__ == "__main__":

    main()
