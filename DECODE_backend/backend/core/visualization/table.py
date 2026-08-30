"""
CanonicalDataset -> editable table representation.

The table is deliberately derived directly from CanonicalDataset
so that numerical values remain lossless.
"""

from typing import Any, Dict, List

from core.canonical_data_model import CanonicalDataset


def dataset_to_table(
    dataset: CanonicalDataset,
) -> Dict[str, Any]:
    """
    Convert a CanonicalDataset into a normalized table.

    Returns:
        {
            "columns": [...],
            "rows": [...],
            "title": "...",
            "x_axis_label": "...",
            "y_axis_label": "...",
            "unit": "..."
        }
    """

    series_list = list(dataset.series)

    columns: List[str] = [
        "Category"
    ]

    for series in series_list:
        name = str(
            series.name or "Value"
        ).strip()

        if not name:
            name = "Value"

        # Avoid duplicate column names.
        original_name = name
        suffix = 2

        while name in columns:
            name = (
                f"{original_name}_{suffix}"
            )
            suffix += 1

        columns.append(name)

    categories = list(
        dataset.categories
    )

    # If categories were not explicitly populated,
    # recover them from the points.
    if not categories:

        seen = set()

        for series in series_list:

            for point in series.points:

                category = str(
                    point.category
                    if point.category is not None
                    else ""
                )

                if category not in seen:

                    seen.add(category)
                    categories.append(
                        category
                    )

    rows: List[Dict[str, Any]] = []

    for category in categories:

        row: Dict[str, Any] = {
            "Category": category
        }

        for series_index, series in enumerate(
            series_list
        ):

            column_name = columns[
                series_index + 1
            ]

            value = None

            for point in series.points:

                if str(
                    point.category
                    if point.category is not None
                    else ""
                ) == str(category):

                    value = point.value
                    break

            row[column_name] = value

        rows.append(row)

    return {
        "columns": columns,
        "rows": rows,
        "title": dataset.title,
        "x_axis_label": dataset.x_axis_label,
        "y_axis_label": dataset.y_axis_label,
        "unit": dataset.unit,
        "detected_type": dataset.detected_type,
        "extraction_method": dataset.extraction_method,
        "overall_confidence": dataset.overall_confidence,
    }
