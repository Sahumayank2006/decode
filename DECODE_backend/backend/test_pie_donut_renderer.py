from core.canonical_data_model import (
    CanonicalDataset,
    DataPoint,
    DataSeries,
)

from core.reconstruction.spec import (
    VisualizationSpec,
)

from core.reconstruction.svg_renderer import (
    SVGChartRenderer,
)


def build_dataset():

    series = DataSeries(
        name="Market Share",
    )

    series.points = [
        DataPoint(
            category="Product A",
            value=50.0,
            series="Market Share",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="Product B",
            value=30.0,
            series="Market Share",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="Product C",
            value=20.0,
            series="Market Share",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="Ignored Zero",
            value=0.0,
            series="Market Share",
            confidence=1.0,
            source="test",
        ),
    ]

    return CanonicalDataset(
        title="Market Share",
        categories=[
            "Product A",
            "Product B",
            "Product C",
            "Ignored Zero",
        ],
        series=[series],
        detected_type="pie",
        extraction_method="test",
        overall_confidence=1.0,
    )


def main():

    dataset = build_dataset()

    renderer = SVGChartRenderer()

    pie_spec = VisualizationSpec(
        chart_type="pie",
        title="Market Share",
        palette_name="professional",
        show_legend=True,
    )

    pie_svg = renderer.render(
        dataset,
        pie_spec,
    )

    assert "<svg" in pie_svg
    assert "</svg>" in pie_svg

    # Only 3 positive values become slices.
    assert (
        pie_svg.count("<path ")
        == 3
    )

    assert (
        'data-value="50"'
        in pie_svg
    )

    assert (
        'data-value="30"'
        in pie_svg
    )

    assert (
        'data-value="20"'
        in pie_svg
    )

    assert (
        'data-percentage="50.000000"'
        in pie_svg
    )

    assert (
        'data-percentage="30.000000"'
        in pie_svg
    )

    assert (
        'data-percentage="20.000000"'
        in pie_svg
    )

    # -------------------------------------------------
    # DONUT
    # -------------------------------------------------

    donut_spec = VisualizationSpec(
        chart_type="donut",
        title="Market Share",
        palette_name="professional",
        show_legend=True,
    )

    donut_svg = renderer.render(
        dataset,
        donut_spec,
    )

    assert "<svg" in donut_svg

    assert (
        donut_svg.count("<path ")
        == 3
    )

    assert "Total" in donut_svg

    assert "100" in donut_svg

    # -------------------------------------------------
    # NEGATIVE VALUE
    # -------------------------------------------------

    negative_series = DataSeries(
        name="Invalid",
        points=[
            DataPoint(
                category="A",
                value=100.0,
                series="Invalid",
            ),
            DataPoint(
                category="B",
                value=-20.0,
                series="Invalid",
            ),
        ],
    )

    negative_dataset = (
        CanonicalDataset(
            title="Invalid Pie",
            categories=["A", "B"],
            series=[
                negative_series
            ],
        )
    )

    try:

        renderer.render(
            negative_dataset,
            pie_spec,
        )

    except ValueError as exc:

        assert (
            "negative"
            in str(exc).lower()
        )

    else:

        raise AssertionError(
            "Negative pie values must "
            "raise ValueError."
        )

    # -------------------------------------------------
    # ALL ZERO
    # -------------------------------------------------

    zero_series = DataSeries(
        name="Zero",
        points=[
            DataPoint(
                category="A",
                value=0.0,
                series="Zero",
            ),
            DataPoint(
                category="B",
                value=0.0,
                series="Zero",
            ),
        ],
    )

    zero_dataset = (
        CanonicalDataset(
            title="Zero Data",
            categories=["A", "B"],
            series=[
                zero_series
            ],
        )
    )

    zero_svg = renderer.render(
        zero_dataset,
        pie_spec,
    )

    assert (
        "No positive data available"
        in zero_svg
    )

    print(
        "PIE DONUT RENDERER TEST PASSED"
    )


if __name__ == "__main__":
    main()
