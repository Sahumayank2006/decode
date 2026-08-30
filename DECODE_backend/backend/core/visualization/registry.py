"""
Visualization type registry.

This module defines the visualization types that DECODE can
reason about. It intentionally does not render anything.

Rendering remains the responsibility of core.reconstruction.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class VisualizationType:
    """
    Metadata describing one visualization type.
    """

    name: str

    label: str

    description: str

    supports_multiple_series: bool = True

    supports_negative_values: bool = True

    requires_categories: bool = True

    requires_numeric_values: bool = True

    suitable_for_time_series: bool = False

    suitable_for_comparison: bool = False

    suitable_for_part_to_whole: bool = False


VISUALIZATION_TYPES = {

    "bar": VisualizationType(
        name="bar",
        label="Bar Chart",
        description=(
            "Compares numerical values across categories."
        ),
        supports_multiple_series=True,
        supports_negative_values=True,
        requires_categories=True,
        requires_numeric_values=True,
        suitable_for_time_series=False,
        suitable_for_comparison=True,
        suitable_for_part_to_whole=False,
    ),

    "line": VisualizationType(
        name="line",
        label="Line Chart",
        description=(
            "Shows trends and changes across an ordered "
            "sequence of categories."
        ),
        supports_multiple_series=True,
        supports_negative_values=True,
        requires_categories=True,
        requires_numeric_values=True,
        suitable_for_time_series=True,
        suitable_for_comparison=True,
        suitable_for_part_to_whole=False,
    ),

    "area": VisualizationType(
        name="area",
        label="Area Chart",
        description=(
            "Shows trends while emphasizing magnitude "
            "over an ordered sequence."
        ),
        supports_multiple_series=True,
        supports_negative_values=True,
        requires_categories=True,
        requires_numeric_values=True,
        suitable_for_time_series=True,
        suitable_for_comparison=True,
        suitable_for_part_to_whole=False,
    ),

    "scatter": VisualizationType(
        name="scatter",
        label="Scatter Plot",
        description=(
            "Shows relationships between numerical "
            "observations."
        ),
        supports_multiple_series=True,
        supports_negative_values=True,
        requires_categories=False,
        requires_numeric_values=True,
        suitable_for_time_series=False,
        suitable_for_comparison=True,
        suitable_for_part_to_whole=False,
    ),

    "pie": VisualizationType(
        name="pie",
        label="Pie Chart",
        description=(
            "Shows part-to-whole proportions."
        ),
        supports_multiple_series=False,
        supports_negative_values=False,
        requires_categories=True,
        requires_numeric_values=True,
        suitable_for_time_series=False,
        suitable_for_comparison=False,
        suitable_for_part_to_whole=True,
    ),

    "donut": VisualizationType(
        name="donut",
        label="Donut Chart",
        description=(
            "Shows part-to-whole proportions using "
            "a ring-based layout."
        ),
        supports_multiple_series=False,
        supports_negative_values=False,
        requires_categories=True,
        requires_numeric_values=True,
        suitable_for_time_series=False,
        suitable_for_comparison=False,
        suitable_for_part_to_whole=True,
    ),

    "table": VisualizationType(
        name="table",
        label="Data Table",
        description=(
            "Displays the canonical numerical data "
            "in an editable tabular form."
        ),
        supports_multiple_series=True,
        supports_negative_values=True,
        requires_categories=False,
        requires_numeric_values=False,
        suitable_for_time_series=True,
        suitable_for_comparison=True,
        suitable_for_part_to_whole=True,
    ),
}


def get_visualization_type(
    name: str,
) -> VisualizationType:
    """
    Return metadata for a visualization type.

    Raises:
        ValueError: if the type is unknown.
    """

    normalized = str(
        name or ""
    ).strip().lower()

    try:
        return VISUALIZATION_TYPES[
            normalized
        ]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported visualization type: "
            f"{name}"
        ) from exc


def list_visualization_types() -> Tuple[str, ...]:
    """
    Return all registered visualization types.
    """

    return tuple(
        VISUALIZATION_TYPES.keys()
    )


def is_supported_visualization_type(
    name: str,
) -> bool:
    """
    Check whether a visualization type is registered.
    """

    normalized = str(
        name or ""
    ).strip().lower()

    return normalized in VISUALIZATION_TYPES
