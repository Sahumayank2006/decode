from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .canonical_data_model import (
    CanonicalDataset,
    DataPoint,
    DataSeries,
)


NUMBER_PATTERN = re.compile(
    r"""
    (?<![\w.])

    [-+]?

    (?:
        \d{1,3}(?:,\d{3})+
        |
        \d+
    )

    (?:\.\d+)?

    %?

    (?![\w.])
    """,
    re.VERBOSE,
)


def parse_number(
    value: Any,
) -> Optional[float]:

    if value is None:
        return None

    if isinstance(
        value,
        (int, float),
    ):

        return float(value)

    text = str(value).strip()

    if not text:
        return None

    text = text.replace(
        ",",
        "",
    )

    text = text.replace(
        "%",
        "",
    )

    try:

        return float(text)

    except (
        TypeError,
        ValueError,
    ):

        return None


def extract_numbers_from_text(
    text: str,
) -> List[float]:

    if not text:
        return []

    values: List[float] = []

    for match in NUMBER_PATTERN.finditer(
        text
    ):

        value = parse_number(
            match.group(0)
        )

        if value is not None:

            values.append(
                value
            )

    return values


def extract_numeric_tokens(
    ocr_items: List[
        Dict[str, Any]
    ],
) -> List[Dict[str, Any]]:
    """
    Extract numeric tokens from OCR.

    Expected OCR item:

    {
        "text": "42.5",
        "confidence": 0.96,
        "bbox": [x1, y1, x2, y2]
    }
    """

    results: List[
        Dict[str, Any]
    ] = []

    for item in ocr_items:

        if not isinstance(
            item,
            dict,
        ):

            continue

        text = str(
            item.get(
                "text",
                "",
            )
        ).strip()

        if not text:
            continue

        matches = NUMBER_PATTERN.findall(
            text
        )

        for match in matches:

            value = parse_number(
                match
            )

            if value is None:
                continue

            results.append({

                "value": value,

                "text": match,

                "confidence": float(
                    item.get(
                        "confidence",
                        0.0,
                    )
                    or 0.0
                ),

                "bbox": item.get(
                    "bbox"
                ),

                "source": "ocr",
            })

    return results


def build_fallback_dataset(
    *,
    detected_type: str = "figure",
    ocr_items: Optional[
        List[Dict[str, Any]]
    ] = None,
    raw_text: str = "",
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> CanonicalDataset:
    """
    Universal fallback.

    If specialised chart extraction fails,
    DECODE still preserves the numerical
    information discovered by OCR.
    """

    ocr_items = ocr_items or []

    metadata = metadata or {}

    numeric_tokens = (
        extract_numeric_tokens(
            ocr_items
        )
    )

    if not numeric_tokens:

        text_values = (
            extract_numbers_from_text(
                raw_text
            )
        )

        numeric_tokens = [

            {
                "value": value,
                "text": str(value),
                "confidence": 0.5,
                "bbox": None,
                "source": "text",
            }

            for value in text_values
        ]

    dataset = CanonicalDataset(

        title=str(
            metadata.get(
                "title",
                "",
            )
        ),

        detected_type=(
            detected_type
            or "figure"
        ),

        extraction_method=(
            "universal_numeric_fallback"
        ),

        metadata={
            **metadata,

            "fallback": True,

            "numeric_token_count": len(
                numeric_tokens
            ),
        },
    )

    series = DataSeries(
        name="Value"
    )

    for index, token in enumerate(
        numeric_tokens
    ):

        series.points.append(

            DataPoint(

                category=str(
                    index + 1
                ),

                value=float(
                    token["value"]
                ),

                series="Value",

                confidence=float(
                    token.get(
                        "confidence",
                        0.0,
                    )
                    or 0.0
                ),

                source=str(
                    token.get(
                        "source",
                        "unknown",
                    )
                ),

                bbox=token.get(
                    "bbox"
                ),
            )
        )

    if series.points:

        dataset.add_series(
            series
        )

    if numeric_tokens:

        confidence_values = [

            float(
                item.get(
                    "confidence",
                    0.0,
                )
                or 0.0
            )

            for item in numeric_tokens
        ]

        dataset.overall_confidence = (

            sum(confidence_values)

            / len(
                confidence_values
            )
        )

    return dataset


def merge_datasets(
    primary: CanonicalDataset,
    fallback: CanonicalDataset,
) -> CanonicalDataset:
    """
    Preserve specialised structured extraction
    while recording values discovered by the
    universal fallback.
    """

    primary.rebuild_numeric_values()

    fallback.rebuild_numeric_values()

    primary_values = {

        round(
            float(value),
            8,
        )

        for value
        in primary.numeric_values
    }

    fallback_values = [

        float(value)

        for value
        in fallback.numeric_values
    ]

    unmatched = [

        value

        for value
        in fallback_values

        if round(
            value,
            8,
        )
        not in primary_values
    ]

    primary.metadata.update({

        "universal_numeric_values":
            fallback_values,

        "unmatched_numeric_values":
            unmatched,

        "universal_numeric_count":
            len(
                fallback_values
            ),
    })

    return primary
