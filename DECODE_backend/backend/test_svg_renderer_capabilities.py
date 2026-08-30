from core.reconstruction.renderer import (
    CanonicalRenderer,
)


def test_table_renderer():
    from core.canonical_data_model import (
        CanonicalDataset,
        DataSeries,
        DataPoint,
    )
    from core.reconstruction.renderer import CanonicalRenderer
    from core.reconstruction.spec import VisualizationSpec

    dataset = CanonicalDataset(
        title="Revenue Overview",
        x_axis_label="Year",
        y_axis_label="Amount",
        unit="USD",
        categories=["2023", "2024", "2025"],
        series=[
            DataSeries(
                name="Revenue",
                points=[
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
                ],
            ),
            DataSeries(
                name="Profit",
                points=[
                    DataPoint(
                        category="2023",
                        value=40.0,
                        series="Profit",
                        confidence=1.0,
                    ),
                    DataPoint(
                        category="2024",
                        value=65.0,
                        series="Profit",
                        confidence=1.0,
                    ),
                    DataPoint(
                        category="2025",
                        value=90.0,
                        series="Profit",
                        confidence=1.0,
                    ),
                ],
            ),
        ],
        detected_type="table",
        extraction_method="test",
        overall_confidence=1.0,
    )

    spec = VisualizationSpec(
        chart_type="table",
        width=1200,
        height=700,
        title="Revenue Overview",
    )

    renderer = CanonicalRenderer()

    svg = renderer.render_svg(dataset, spec)

    assert isinstance(svg, str)
    assert svg.startswith("<svg")
    assert "</svg>" in svg

    # Header / categories.
    assert "2023" in svg
    assert "2024" in svg
    assert "2025" in svg

    # Series.
    assert "Revenue" in svg
    assert "Profit" in svg

    # Numerical integrity.
    assert 'data-value="100.0"' in svg
    assert 'data-value="140.0"' in svg
    assert 'data-value="180.0"' in svg
    assert 'data-value="40.0"' in svg
    assert 'data-value="65.0"' in svg
    assert 'data-value="90.0"' in svg

    # Interactive metadata.
    assert 'data-series="Revenue"' in svg
    assert 'data-series="Profit"' in svg
    assert 'data-category="2023"' in svg

    print("TABLE SVG RENDERER TEST PASSED")


def main():

    renderer = CanonicalRenderer()

    svg_renderer = renderer.svg_renderer

    expected = {
        "bar",
        "line",
        "area",
        "scatter",
        "pie",
        "donut",
        "table",
    }

    assert (
        expected
        == set(
            svg_renderer.supported_chart_types
        )
    )

    assert svg_renderer.supports(
        "bar"
    )

    assert svg_renderer.supports(
        "line"
    )

    assert svg_renderer.supports(
        "area"
    )

    assert svg_renderer.supports(
        "scatter"
    )

    assert svg_renderer.supports(
        "pie"
    )

    assert svg_renderer.supports(
        "donut"
    )

    assert svg_renderer.supports(
        "table"
    )

    assert not svg_renderer.supports(
        "unknown"
    )

    assert svg_renderer.supports(
        " BAR "
    )

    assert svg_renderer.supports(
        "Pie"
    )

    test_table_renderer()

    print(
        "SVG RENDERER CAPABILITY TEST PASSED"
    )


if __name__ == "__main__":
    main()
