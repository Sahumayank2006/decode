"""
Visualization recommendation engine.

This module analyzes a CanonicalDataset and recommends
appropriate visualization types.

It does not render charts.
"""

from dataclasses import dataclass
from typing import List

from core.canonical_data_model import (
    CanonicalDataset,
)

from .registry import (
    list_visualization_types,
)

from .validators import (
    validate_for_visualization,
)


@dataclass
class VisualizationRecommendation:

    visualization_type: str

    score: float

    reason: str

    alternatives: List[str]


def _category_looks_temporal(
    category: str,
) -> bool:

    value = str(
        category or ""
    ).strip().lower()

    if not value:
        return False

    temporal_tokens = (
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
        "q1",
        "q2",
        "q3",
        "q4",
    )

    if any(
        token in value
        for token in temporal_tokens
    ):
        return True

    # Simple year detection.
    if (
        len(value) == 4
        and value.isdigit()
        and 1900 <= int(value) <= 2200
    ):
        return True

    return False


def _looks_like_time_series(
    dataset: CanonicalDataset,
) -> bool:

    categories = dataset.categories

    if not categories:
        return False

    temporal_count = sum(
        1
        for category in categories
        if _category_looks_temporal(
            category
        )
    )

    return (
        temporal_count
        >= max(
            2,
            len(categories) // 2
        )
    )


def recommend_visualizations(
    dataset: CanonicalDataset,
) -> List[
    VisualizationRecommendation
]:
    """
    Generate ranked visualization recommendations.

    The result is ordered from strongest recommendation
    to weakest.
    """

    candidates = []

    temporal = _looks_like_time_series(
        dataset
    )

    series_count = len(
        dataset.series
    )

    category_count = len(
        dataset.categories
    )

    for visualization_type in (
        list_visualization_types()
    ):

        problems = (
            validate_for_visualization(
                dataset,
                visualization_type,
            )
        )

        if problems:
            continue

        score = 0.0
        reason = (
            "Suitable for the structure "
            "of the extracted dataset."
        )

        if visualization_type == "line":

            if temporal:

                score += 0.40

                reason = (
                    "The categories appear to "
                    "represent an ordered time "
                    "sequence, making a line chart "
                    "well suited for showing trends."
                )

            elif category_count >= 3:

                score += 0.15

        elif visualization_type == "area":

            if temporal:

                score += 0.30

                reason = (
                    "The dataset appears to contain "
                    "an ordered sequence where an "
                    "area chart can emphasize magnitude."
                )

        elif visualization_type == "bar":

            score += 0.30

            if (
                category_count > 0
                and category_count <= 20
            ):
                score += 0.25

                reason = (
                    "The dataset contains a manageable "
                    "number of categories, making direct "
                    "comparison effective with bars."
                )

            if series_count > 1:

                score += 0.10

        elif visualization_type == "table":

            score += 0.20

            reason = (
                "A table provides a direct editable "
                "representation of the extracted values."
            )

        elif visualization_type in (
            "pie",
            "donut",
        ):

            if (
                series_count == 1
                and 2 <= category_count <= 8
            ):

                score += 0.25

                reason = (
                    "The dataset contains a single "
                    "series with a small number of "
                    "categories, making part-to-whole "
                    "visualization practical."
                )

        elif visualization_type == "scatter":

            if category_count == 0:

                score += 0.20

                reason = (
                    "The dataset is numerical without "
                    "categorical labels, making a "
                    "scatter representation potentially "
                    "appropriate."
                )

        candidates.append(
            VisualizationRecommendation(
                visualization_type=(
                    visualization_type
                ),
                score=min(
                    1.0,
                    score,
                ),
                reason=reason,
                alternatives=[],
            )
        )

    candidates.sort(
        key=lambda item: item.score,
        reverse=True,
    )

    if candidates:

        alternatives = [
            item.visualization_type
            for item in candidates[1:]
        ]

        candidates[0].alternatives = (
            alternatives
        )

    return candidates


def recommend_best_visualization(
    dataset: CanonicalDataset,
) -> VisualizationRecommendation:

    recommendations = (
        recommend_visualizations(
            dataset
        )
    )

    if not recommendations:
        raise ValueError(
            "No compatible visualization "
            "type was found for the dataset."
        )

    return recommendations[0]
