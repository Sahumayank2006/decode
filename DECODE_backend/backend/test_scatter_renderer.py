from core.canonical_data_model import (
    CanonicalDataset,
    DataSeries,
    DataPoint,
)

from core.reconstruction.spec import (
    VisualizationSpec,
)

from core.reconstruction.svg_renderer import (
    SVGChartRenderer,
)


def build_dataset():

    series_a = DataSeries(
        name="Revenue",
    )

    series_a.points = [
        DataPoint(
            category="2021",
            value=100.0,
            series="Revenue",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2022",
            value=140.0,
            series="Revenue",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2023",
            value=120.0,
            series="Revenue",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2024",
            value=190.0,
            series="Revenue",
            confidence=1.0,
            source="test",
        ),
    ]

    series_b = DataSeries(
        name="Profit",
    )

    series_b.points = [
        DataPoint(
            category="2021",
            value=40.0,
            series="Profit",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2022",
            value=65.0,
            series="Profit",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2023",
            value=55.0,
            series="Profit",
            confidence=1.0,
            source="test",
        ),
        DataPoint(
            category="2024",
            value=90.0,
            series="Profit",
            confidence=1.0,
            source="test",
        ),
    ]

    return CanonicalDataset(
        title="Revenue vs Profit",
        x_axis_label="Year",
        y_axis_label="Amount",
        categories=[
            "2021",
            "2022",
            "2023",
            "2024",
        ],
        series=[
            series_a,
            series_b,
        ],
        detected_type="scatter",
        extraction_method="test",
        overall_confidence=1.0,
    )


def main():

    dataset = build_dataset()

    spec = VisualizationSpec(
        chart_type="scatter",
        title=dataset.title,
        x_axis_label=dataset.x_axis_label,
        y_axis_label=dataset.y_axis_label,
        palette_name="professional",
        show_legend=True,
        show_grid=True,
    )

    renderer = SVGChartRenderer()

    svg = renderer.render(
        dataset,
        spec,
    )

    assert isinstance(
        svg,
        str,
    )

    assert len(svg) > 0

    assert "<svg" in svg

    assert "</svg>" in svg

    # We have 8 actual numerical points.
    assert svg.count(
        "<circle "
    ) == 8

    # Verify the exact values survived into
    # the generated SVG metadata.
    assert (
        'data-value="100"'
        in svg
    )

    assert (
        'data-value="190"'
        in svg
    )

    assert (
        'data-value="40"'
        in svg
    )

    assert (
        'data-value="90"'
        in svg
    )

    # Verify both series are present.
    assert (
        'data-series="Revenue"'
        in svg
    )

    assert (
        'data-series="Profit"'
        in svg
    )

    # Verify axis labels.
    assert "Year" in svg
    assert "Amount" in svg

    print(
        "SCATTER RENDERER TEST PASSED"
    )


if __name__ == "__main__":
    main()
