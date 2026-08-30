"""
Validation utilities for converting CanonicalDataset
objects into visualizations.
"""

from typing import List

from core.canonical_data_model import (
    CanonicalDataset,
)

from .registry import (
    get_visualization_type,
)


def _has_numeric_data(
    dataset: CanonicalDataset,
) -> bool:

    if dataset.numeric_values:
        return any(
            value is not None
            for value in dataset.numeric_values
        )

    for series in dataset.series:
        for point in series.points:
            if point.value is not None:
                return True

    return False


def _has_categories(
    dataset: CanonicalDataset,
) -> bool:

    if dataset.categories:
        return True

    for series in dataset.series:
        for point in series.points:
            if point.category:
                return True

    return False


def validate_for_visualization(
    dataset: CanonicalDataset,
    visualization_type: str,
) -> List[str]:
    """
    Validate whether a dataset can reasonably be represented
    using a particular visualization.

    Returns a list of human-readable problems.

    An empty list means the dataset is valid.
    """

    problems: List[str] = []

    spec = get_visualization_type(
        visualization_type
    )

    if (
        spec.requires_categories
        and not _has_categories(dataset)
    ):
        problems.append(
            "The dataset does not contain "
            "usable categories."
        )

    if (
        spec.requires_numeric_values
        and not _has_numeric_data(dataset)
    ):
        problems.append(
            "The dataset does not contain "
            "usable numerical values."
        )

    if (
        not spec.supports_multiple_series
        and len(dataset.series) > 1
    ):
        problems.append(
            f"{spec.label} supports only "
            "one data series."
        )

    if not spec.supports_negative_values:

        has_negative = any(
            value < 0
            for value in dataset.numeric_values
            if value is not None
        )

        if has_negative:
            problems.append(
                f"{spec.label} does not support "
                "negative values."
            )

    return problems


def can_convert_to_visualization(
    dataset: CanonicalDataset,
    visualization_type: str,
) -> bool:
    """
    Return True if the dataset can be represented
    using the requested visualization.
    """

    return not validate_for_visualization(
        dataset,
        visualization_type,
    )
