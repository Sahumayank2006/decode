"""
Visualization conversion layer.

This module converts the canonical dataset into visualization
specifications without modifying the underlying numerical data.
"""

from dataclasses import replace
from typing import Any, Dict, Optional

from core.canonical_data_model import (
    CanonicalDataset,
)

from core.reconstruction.spec import (
    VisualizationSpec,
)

from .registry import (
    get_visualization_type,
)

from .validators import (
    validate_for_visualization,
)

from .table import (
    dataset_to_table,
)


def _default_spec(
    dataset: CanonicalDataset,
    visualization_type: str,
    palette_name: str = "default",
) -> VisualizationSpec:

    return VisualizationSpec(

        chart_type=visualization_type,

        title=dataset.title,

        x_axis_label=dataset.x_axis_label,

        y_axis_label=dataset.y_axis_label,

        palette_name=palette_name,

        show_legend=len(
            dataset.series
        ) > 1,

        show_grid=(
            visualization_type
            not in {"pie", "donut"}
        ),
    )


def dataset_to_visualization(
    dataset: CanonicalDataset,
    visualization_type: str,
    palette_name: str = "default",
) -> Dict[str, Any]:
    """
    Convert a CanonicalDataset into a visualization
    representation.

    For table visualization the returned payload contains
    table data.

    For chart visualizations the returned payload contains
    a VisualizationSpec plus the original canonical dataset.
    """

    visualization_type = str(
        visualization_type or ""
    ).strip().lower()

    # Ensure the visualization type exists.
    get_visualization_type(
        visualization_type
    )

    problems = validate_for_visualization(
        dataset,
        visualization_type,
    )

    if problems:

        raise ValueError(
            "Cannot convert dataset to "
            f"{visualization_type}: "
            + "; ".join(problems)
        )

    if visualization_type == "table":

        table = dataset_to_table(
            dataset
        )

        return {
            "type": "table",
            "dataset": dataset.to_dict(),
            "table": table,
        }

    spec = _default_spec(
        dataset=dataset,
        visualization_type=(
            visualization_type
        ),
        palette_name=palette_name,
    )

    return {
        "type": visualization_type,
        "dataset": dataset.to_dict(),
        "spec": spec.to_dict(),
    }


def convert_dataset(
    dataset: CanonicalDataset,
    visualization_type: str,
    palette_name: str = "default",
) -> Dict[str, Any]:
    """
    Public alias for dataset_to_visualization().
    """

    return dataset_to_visualization(
        dataset=dataset,
        visualization_type=visualization_type,
        palette_name=palette_name,
    )


def convert_table_to_visualization(
    table: Dict[str, Any],
    visualization_type: str,
    title: str = "",
    x_axis_label: str = "",
    y_axis_label: str = "",
    unit: str = "",
    palette_name: str = "default",
) -> Dict[str, Any]:
    """
    Convert a normalized table representation back into
    a CanonicalDataset and then into a visualization.

    This is the key table -> chart bridge.
    """

    if not isinstance(table, dict):

        raise TypeError(
            "table must be a dictionary"
        )

    columns = list(
        table.get("columns", [])
    )

    rows = list(
        table.get("rows", [])
    )

    if not columns:

        raise ValueError(
            "Table must contain columns."
        )

    if not rows:

        raise ValueError(
            "Table must contain at least one row."
        )

    if columns[0] != "Category":

        raise ValueError(
            "The first table column must "
            "be 'Category'."
        )

    dataset_payload = {
        "title": title
        or table.get("title", ""),

        "x_axis_label": (
            x_axis_label
            or table.get(
                "x_axis_label",
                "",
            )
        ),

        "y_axis_label": (
            y_axis_label
            or table.get(
                "y_axis_label",
                "",
            )
        ),

        "unit": (
            unit
            or table.get(
                "unit",
                "",
            )
        ),

        "categories": [],

        "series": [],

        "numeric_values": [],

        "detected_type": "table",

        "extraction_method": (
            table.get(
                "extraction_method",
                "table",
            )
        ),

        "overall_confidence": float(
            table.get(
                "overall_confidence",
                1.0,
            )
            or 1.0
        ),

        "metadata": {
            "source": "table_conversion"
        },
    }

    # Build categories.
    for row in rows:

        category = row.get(
            "Category"
        )

        if category is None:

            category = ""

        dataset_payload[
            "categories"
        ].append(
            str(category)
        )

    # Build series.
    for column in columns[1:]:

        points = []

        for row_index, row in enumerate(
            rows
        ):

            category = (
                dataset_payload[
                    "categories"
                ][row_index]
            )

            raw_value = row.get(
                column
            )

            value: Optional[float]

            if (
                raw_value is None
                or raw_value == ""
            ):

                value = None

            else:

                try:

                    value = float(
                        raw_value
                    )

                except (
                    TypeError,
                    ValueError,
                ) as exc:

                    raise ValueError(
                        f"Invalid numeric value "
                        f"'{raw_value}' in "
                        f"column '{column}'."
                    ) from exc

            points.append({
                "category": category,
                "value": value,
                "series": column,
                "confidence": 1.0,
                "source": "table_conversion",
            })

            if value is not None:

                dataset_payload[
                    "numeric_values"
                ].append(value)

        dataset_payload[
            "series"
        ].append({
            "name": str(column),
            "points": points,
            "color": None,
        })

    reconstructed_dataset = (
        CanonicalDataset.from_dict(
            dataset_payload
        )
    )

    return dataset_to_visualization(
        dataset=(
            reconstructed_dataset
        ),
        visualization_type=(
            visualization_type
        ),
        palette_name=palette_name,
    )
