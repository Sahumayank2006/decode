from core.canonical_data_model import (
    CanonicalDataset,
    DataSeries,
    DataPoint,
)

from core.reconstruction.svg_renderer import SVGChartRenderer
from core.reconstruction.spec import VisualizationSpec


def dataset_from_values(values):
    points = []

    for index, value in enumerate(values):
        points.append(
            DataPoint(
                category=str(index),
                value=value,
                series="Series A",
                confidence=1.0,
                source="test",
            )
        )

    return CanonicalDataset(
        title="Numeric Hardening Test",
        categories=[str(i) for i in range(len(values))],
        series=[
            DataSeries(
                name="Series A",
                points=points,
            )
        ],
        detected_type="chart",
        extraction_method="test",
        overall_confidence=1.0,
    )


def render(values, chart_type="line"):
    dataset = dataset_from_values(values)

    renderer = SVGChartRenderer()

    spec = VisualizationSpec(
        chart_type=chart_type,
        title="Numeric Test",
        width=1000,
        height=600,
    )

    svg = renderer.render(dataset, spec)

    assert svg
    assert svg.startswith("<svg")
    assert "</svg>" in svg

    return svg


def main():

    print("=== NUMERICAL RANGE HARDENING TEST ===")

    # Empty dataset
    empty = CanonicalDataset()
    renderer = SVGChartRenderer()

    minimum, maximum = renderer._value_range(empty)

    assert minimum < maximum

    # Positive values
    minimum, maximum = renderer._value_range(
        dataset_from_values([10, 20, 30])
    )

    assert minimum < 10
    assert maximum > 30

    # Negative values
    minimum, maximum = renderer._value_range(
        dataset_from_values([-10, -20, -30])
    )

    assert minimum < -30
    assert maximum > -10

    # Mixed values
    minimum, maximum = renderer._value_range(
        dataset_from_values([-100, -20, 0, 50, 100])
    )

    assert minimum < 0
    assert maximum > 0

    # Single value
    minimum, maximum = renderer._value_range(
        dataset_from_values([100])
    )

    assert minimum < 100
    assert maximum > 100

    # Zero only
    minimum, maximum = renderer._value_range(
        dataset_from_values([0, 0, 0])
    )

    assert minimum < maximum

    # Tiny range
    minimum, maximum = renderer._value_range(
        dataset_from_values([
            99.999,
            100.000,
            100.001,
        ])
    )

    assert minimum < maximum

    # Huge values
    minimum, maximum = renderer._value_range(
        dataset_from_values([
            1_000_000_000,
            2_000_000_000,
            5_000_000_000,
        ])
    )

    assert minimum < maximum

    # NaN / Infinity
    minimum, maximum = renderer._value_range(
        dataset_from_values([
            float("nan"),
            float("inf"),
            10,
            20,
        ])
    )

    assert minimum < maximum

    # Actual render tests
    render([10, 20, 30], "bar")
    render([-10, -20, -30], "bar")
    render([-20, 0, 30], "line")
    render([-20, 0, 30], "area")
    render([-100, 0, 100], "scatter")
    render([100], "line")
    render([0, 0, 0], "line")
    render([99.999, 100.000, 100.001], "line")
    render([1_000_000, 2_000_000, 5_000_000], "bar")

    # Tick generation
    ticks = renderer._safe_ticks(-100, 100)

    assert len(ticks) >= 2
    assert all(ticks[i] <= ticks[i + 1] for i in range(len(ticks) - 1))

    # Number formatting
    assert renderer._format_axis_value(100) == "100"
    assert renderer._format_axis_value(1_000_000) == "1.0M"
    assert renderer._format_axis_value(1_000_000_000) == "1.0B"

    print("NUMERICAL RANGE HARDENING TEST PASSED")


if __name__ == "__main__":
    main()
