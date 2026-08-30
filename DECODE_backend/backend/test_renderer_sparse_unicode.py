from core.canonical_data_model import (
    CanonicalDataset,
    DataSeries,
    DataPoint,
)

from core.reconstruction.svg_renderer import SVGChartRenderer
from core.reconstruction.spec import VisualizationSpec


def build_dataset():
    return CanonicalDataset(
        title="भारत में बिक्री — Sales ₹",
        x_axis_label="महीना / Month",
        y_axis_label="राजस्व ₹",
        unit="₹",
        categories=[
            "जनवरी",
            "February",
            "मार्च & April",
            "Very Long Category Name That Should Be Truncated",
        ],
        series=[
            DataSeries(
                name="Revenue ₹",
                points=[
                    DataPoint(
                        category="जनवरी",
                        value=100000,
                        series="Revenue ₹",
                    ),
                    DataPoint(
                        category="February",
                        value=None,
                        series="Revenue ₹",
                    ),
                    DataPoint(
                        category="मार्च & April",
                        value=150000,
                        series="Revenue ₹",
                    ),
                    DataPoint(
                        category="Very Long Category Name That Should Be Truncated",
                        value=175000,
                        series="Revenue ₹",
                    ),
                ],
            ),
            DataSeries(
                name="Profit %",
                points=[
                    DataPoint(
                        category="जनवरी",
                        value=20000,
                        series="Profit %",
                    ),
                    DataPoint(
                        category="February",
                        value=25000,
                        series="Profit %",
                    ),
                    # Deliberately sparse.
                ],
            ),
        ],
        detected_type="chart",
        extraction_method="test",
        overall_confidence=1.0,
    )


def main():

    print("=== SPARSE + UNICODE RENDERER TEST ===")

    dataset = build_dataset()

    renderer = SVGChartRenderer()

    categories = renderer._safe_categories(dataset)

    assert len(categories) == 4

    assert categories[0] == "जनवरी"

    # Unicode should survive.
    assert "जनवरी" in categories

    # Missing values should not crash.
    assert renderer._point_value(
        dataset.series[0].points[1]
    ) is None

    # Valid value.
    assert renderer._point_value(
        dataset.series[0].points[0]
    ) == 100000.0

    # NaN.
    nan_point = DataPoint(
        category="NaN",
        value=float("nan"),
    )

    assert renderer._point_value(nan_point) is None

    # Infinity.
    inf_point = DataPoint(
        category="Inf",
        value=float("inf"),
    )

    assert renderer._point_value(inf_point) is None

    # Long labels.
    label = renderer._truncate_label(
        "This is an extremely long category label "
        "that came from OCR extraction"
    )

    assert len(label) <= 24
    assert label.endswith("...")

    # Short label must remain unchanged.
    assert renderer._truncate_label("January") == "January"

    # Render multiple visualization types.
    for chart_type in [
        "bar",
        "line",
        "area",
        "scatter",
        "table",
    ]:

        spec = VisualizationSpec(
            chart_type=chart_type,
            title=dataset.title,
            width=1200,
            height=700,
        )

        svg = renderer.render(dataset, spec)

        assert svg
        assert svg.startswith("<svg")
        assert "</svg>" in svg

        # XML-sensitive characters should be escaped.
        assert "&amp;" in svg or "&" not in svg

    print("SPARSE + UNICODE RENDERER TEST PASSED")


if __name__ == "__main__":
    main()
