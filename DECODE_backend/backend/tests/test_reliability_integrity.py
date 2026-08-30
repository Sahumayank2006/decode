from __future__ import annotations

import sys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def flatten_dataset_values(dataset):
    values = []

    for series in getattr(dataset, "series", []):

        for point in getattr(series, "points", []):

            value = getattr(
                point,
                "value",
                None,
            )

            if value is None:
                continue

            value = float(value)

            if math.isfinite(value):
                values.append(value)

    return values


def test_numeric_integrity():
    """
    Canonical values must survive visualization conversion
    without modification.
    """

    from core.canonical_data_model import (
        CanonicalDataset,
    )

    payload = {
        "title": "Integrity Test",
        "categories": [
            "India",
            "USA",
            "Germany",
        ],
        "series": [
            {
                "name": "Value",
                "points": [
                    {
                        "category": "India",
                        "value": 72.4,
                    },
                    {
                        "category": "USA",
                        "value": 68.1,
                    },
                    {
                        "category": "Germany",
                        "value": 64.7,
                    },
                ],
            }
        ],
    }

    dataset = CanonicalDataset.from_dict(
        payload
    )

    values_before = flatten_dataset_values(
        dataset
    )

    assert values_before == [
        72.4,
        68.1,
        64.7,
    ]

    # Rebuild numeric representation.
    dataset.rebuild_numeric_values()

    values_after = flatten_dataset_values(
        dataset
    )

    assert values_before == values_after

    assert dataset.numeric_values == [
        72.4,
        68.1,
        64.7,
    ]

    print(
        "NUMERICAL INTEGRITY TEST PASSED"
    )


if __name__ == "__main__":
    test_numeric_integrity()
