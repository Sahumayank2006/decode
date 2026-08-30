from __future__ import annotations

from typing import Any, Dict, List, Optional

from .canonical_data_model import (
    CanonicalDataset,
    DataPoint,
    DataSeries,
)
from .visualization.table_normalizer import normalize_table_series


def _safe_float(
    value: Any,
) -> Optional[float]:
    """
    Safely convert a value to float.

    Returns None when conversion is impossible.
    """

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return None

    try:

        return float(
            str(value)
            .replace(",", "")
            .replace("%", "")
            .strip()
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


def _safe_confidence(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Normalize confidence into [0, 1].
    """

    try:

        confidence = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default

    # Handle percentages such as 95.
    if confidence > 1:

        confidence = confidence / 100.0

    return max(
        0.0,
        min(
            1.0,
            confidence,
        ),
    )


def _first_value(
    payload: Dict[str, Any],
    keys: List[str],
    default: Any = None,
) -> Any:
    """
    Return the first existing key.
    """

    for key in keys:

        if key in payload:

            value = payload[key]

            if value is not None:

                return value

    return default


def _normalise_point(
    point: Any,
    series_name: str,
    index: int,
) -> Optional[DataPoint]:
    """
    Convert many common point formats into
    a DataPoint.

    Supported examples:

        {"category": "2024", "value": 100}

        {"label": "2024", "y": 100}

        {"x": "2024", "y": 100}

        ["2024", 100]

        100
    """

    category: Any = None
    value: Any = None
    confidence: Any = 1.0
    bbox = None
    label = None
    source = "existing_extractor"

    if isinstance(
        point,
        dict,
    ):

        category = _first_value(
            point,
            [
                "category",
                "label",
                "x",
                "name",
                "key",
            ],
            str(index + 1),
        )

        value = _first_value(
            point,
            [
                "value",
                "y",
                "numeric_value",
                "number",
                "data",
            ],
        )

        confidence = _first_value(
            point,
            [
                "confidence",
                "score",
                "probability",
            ],
            1.0,
        )

        bbox = _first_value(
            point,
            [
                "bbox",
                "bounding_box",
                "box",
            ],
        )

        label = point.get(
            "label"
        )

        source = str(
            point.get(
                "source",
                source,
            )
        )

    elif isinstance(
        point,
        (list, tuple),
    ):

        if len(point) >= 2:

            category = point[0]

            value = point[1]

        elif len(point) == 1:

            category = str(
                index + 1
            )

            value = point[0]

    else:

        category = str(
            index + 1
        )

        value = point

    parsed_value = _safe_float(
        value
    )

    if parsed_value is None:

        return None

    return DataPoint(

        category=str(
            category
            if category is not None
            else index + 1
        ),

        value=parsed_value,

        series=series_name,

        confidence=_safe_confidence(
            confidence,
            1.0,
        ),

        source=source,

        bbox=bbox,

        label=label,
    )


def _normalise_series(
    raw_series: Any,
    default_name: str = "Value",
) -> List[DataSeries]:
    """
    Convert common series representations
    into DataSeries objects.
    """

    result: List[
        DataSeries
    ] = []

    if raw_series is None:

        return result

    # -----------------------------------------
    # Dictionary representation
    # -----------------------------------------

    if isinstance(
        raw_series,
        dict,
    ):

        # Case:
        #
        # {
        #   "Revenue": [
        #       {"category": "2024", "value": 100}
        #   ],
        #   "Profit": [...]
        # }

        if all(
            isinstance(
                value,
                (list, tuple),
            )
            for value
            in raw_series.values()
        ):

            for name, points in (
                raw_series.items()
            ):

                series = DataSeries(
                    name=str(name)
                )

                for index, point in enumerate(
                    points
                ):

                    normalised = (
                        _normalise_point(
                            point,
                            str(name),
                            index,
                        )
                    )

                    if normalised:

                        series.points.append(
                            normalised
                        )

                if series.points:

                    result.append(
                        series
                    )

            return result

        # Case:
        #
        # {
        #   "name": "Revenue",
        #   "data": [...]
        # }

        name = str(
            _first_value(
                raw_series,
                [
                    "name",
                    "series",
                    "label",
                ],
                default_name,
            )
        )

        color = raw_series.get(
            "color"
        )

        points = _first_value(
            raw_series,
            [
                "points",
                "data",
                "values",
            ],
            [],
        )

        if isinstance(
            points,
            (list, tuple),
        ):

            series = DataSeries(
                name=name,
                color=color,
            )

            for index, point in enumerate(
                points
            ):

                normalised = (
                    _normalise_point(
                        point,
                        name,
                        index,
                    )
                )

                if normalised:

                    series.points.append(
                        normalised
                    )

            if series.points:

                result.append(
                    series
                )

        return result

    # -----------------------------------------
    # List representation
    # -----------------------------------------

    if isinstance(
        raw_series,
        (list, tuple),
    ):

        if raw_series and isinstance(raw_series[0], dict) and any(k in raw_series[0] for k in ["name", "points", "data", "values"]):
            for item in raw_series:
                result.extend(
                    _normalise_series(
                        item,
                        default_name=item.get("name", default_name),
                    )
                )
            return result

        series = DataSeries(
            name=default_name
        )

        for index, point in enumerate(
            raw_series
        ):

            normalised = (
                _normalise_point(
                    point,
                    default_name,
                    index,
                )
            )

            if normalised:

                series.points.append(
                    normalised
                )

        if series.points:

            result.append(
                series
            )

    return result


def normalize_extraction_result(
    raw_result: Any,
    *,
    detected_type: str = "unknown",
    extraction_method: str = "existing_extractor",
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> CanonicalDataset:
    """
    Main adapter between the existing DECODE
    extraction system and the new canonical
    representation.

    IMPORTANT:

    This function does NOT perform extraction.

    It only converts an existing extraction
    result into CanonicalDataset.
    """

    metadata = dict(
        metadata or {}
    )

    if isinstance(
        raw_result,
        CanonicalDataset,
    ):

        dataset = raw_result

        dataset.detected_type = (
            detected_type
            or dataset.detected_type
        )

        dataset.extraction_method = (
            extraction_method
            or dataset.extraction_method
        )

        dataset.metadata.update(
            metadata
        )

        return dataset

    if raw_result is None:

        dataset = CanonicalDataset(

            detected_type=detected_type,

            extraction_method=(
                extraction_method
            ),

            metadata=metadata,
        )

        return dataset

    # -----------------------------------------
    # Convert non-dict result into a simple
    # single-series dataset.
    # -----------------------------------------

    if not isinstance(
        raw_result,
        dict,
    ):

        series_list = (
            _normalise_series(
                raw_result
            )
        )

        dataset = CanonicalDataset(

            detected_type=detected_type,

            extraction_method=(
                extraction_method
            ),

            metadata=metadata,
        )

        for series in series_list:

            dataset.add_series(
                series
            )

        return dataset

    # -----------------------------------------
    # Metadata
    # -----------------------------------------

    title = _first_value(
        raw_result,
        [
            "title",
            "chart_title",
            "figure_title",
        ],
        "",
    )

    # -----------------------------------------
    # Axis labels
    # -----------------------------------------

    axis_labels = raw_result.get(
        "axis_labels",
        {},
    )

    if not isinstance(
        axis_labels,
        dict,
    ):

        axis_labels = {}

    x_axis_label = _first_value(
        raw_result,
        [
            "x_axis_label",
            "x_label",
            "xlabel",
            "x_axis",
        ],
        axis_labels.get(
            "x_label",
            "",
        ),
    )

    y_axis_label = _first_value(
        raw_result,
        [
            "y_axis_label",
            "y_label",
            "ylabel",
            "y_axis",
        ],
        axis_labels.get(
            "y_label",
            "",
        ),
    )

    unit = _first_value(
        raw_result,
        [
            "unit",
            "units",
            "value_unit",
        ],
        "",
    )

    chart_type = _first_value(
        raw_result,
        [
            "chart_type",
            "type",
            "visualization_type",
            "detected_type",
        ],
        detected_type,
    )

    dataset = CanonicalDataset(

        title=str(
            title or ""
        ),

        x_axis_label=str(
            x_axis_label or ""
        ),

        y_axis_label=str(
            y_axis_label or ""
        ),

        unit=str(
            unit or ""
        ),

        detected_type=str(
            chart_type
            or detected_type
            or "unknown"
        ),

        extraction_method=(
            extraction_method
        ),

        metadata=metadata,
    )

    # -----------------------------------------
    # Preserve axis information from the
    # original extractor.
    # -----------------------------------------

    dataset.metadata[
        "axis_labels"
    ] = {
        "x_label": str(
            axis_labels.get(
                "x_label",
                x_axis_label or "",
            )
        ),
        "y_label": str(
            axis_labels.get(
                "y_label",
                y_axis_label or "",
            )
        ),
        "x_ticks": axis_labels.get(
            "x_ticks",
            [],
        ),
        "y_ticks": axis_labels.get(
            "y_ticks",
            [],
        ),
    }

    # -----------------------------------------
    # Preserve legend information.
    # -----------------------------------------

    legend = raw_result.get(
        "legend",
        [],
    )

    if isinstance(
        legend,
        list,
    ):

        dataset.metadata[
            "legend"
        ] = legend

    else:

        dataset.metadata[
            "legend"
        ] = []

    # -----------------------------------------
    # Preserve raw OCR text.
    # -----------------------------------------

    raw_ocr_text = raw_result.get(
        "raw_ocr_text",
        "",
    )

    if raw_ocr_text:

        dataset.metadata[
            "raw_ocr_text"
        ] = str(
            raw_ocr_text
        )

    # -----------------------------------------
    # Look for common series containers.
    # -----------------------------------------

    raw_series = _first_value(
        raw_result,
        [
            "series",
            "data_series",
            "datasets",
        ],
    )

    if raw_series is not None:
        
        if dataset.detected_type == "table":
            cat_count = len(dataset.categories) if dataset.categories else 0
            if not cat_count and "categories" in raw_result and isinstance(raw_result["categories"], list):
                dataset.categories = [str(c) for c in raw_result["categories"]]
                cat_count = len(dataset.categories)
            
            normalized_tables = normalize_table_series(raw_series, cat_count)
            for s_dict in normalized_tables:
                s = DataSeries(name=s_dict["name"])
                for i, v in enumerate(s_dict["values"]):
                    cat = dataset.categories[i] if i < len(dataset.categories) else str(i+1)
                    s.points.append(
                        DataPoint(
                            category=cat,
                            value=v,
                            series=s.name
                        )
                    )
                dataset.add_series(s)
        else:
            for series in _normalise_series(
                raw_series
            ):
                dataset.add_series(
                    series
                )

    # -----------------------------------------
    # Direct categories + values
    # -----------------------------------------

    if not dataset.series:

        categories = _first_value(
            raw_result,
            [
                "categories",
                "labels",
                "x_values",
                "x",
            ],
            [],
        )

        values = _first_value(
            raw_result,
            [
                "values",
                "y_values",
                "data",
                "numbers",
                "numeric_values",
            ],
            [],
        )

        if isinstance(
            categories,
            (list, tuple),
        ) and isinstance(
            values,
            (list, tuple),
        ):

            series = DataSeries(
                name="Value"
            )

            for index, value in enumerate(
                values
            ):

                category = (

                    categories[index]

                    if index
                    < len(categories)

                    else index + 1
                )

                normalised = (
                    _normalise_point(
                        {
                            "category": category,
                            "value": value,
                        },
                        "Value",
                        index,
                    )
                )

                if normalised:

                    series.points.append(
                        normalised
                    )

            if series.points:

                dataset.add_series(
                    series
                )

    # -----------------------------------------
    # Table-like rows
    # -----------------------------------------

    if not dataset.series:

        rows = _first_value(
            raw_result,
            [
                "rows",
                "table",
                "table_data",
            ],
        )

        if isinstance(
            rows,
            list,
        ):

            series_names: List[
                str
            ] = []

            for row in rows:

                if not isinstance(
                    row,
                    dict,
                ):

                    continue

                values = row.get(
                    "values",
                    row,
                )

                if not isinstance(
                    values,
                    dict,
                ):

                    continue

                for key in values:

                    if key not in series_names:

                        series_names.append(
                            str(key)
                        )

            for series_name in (
                series_names
            ):

                series = DataSeries(
                    name=series_name
                )

                for index, row in enumerate(
                    rows
                ):

                    if not isinstance(
                        row,
                        dict,
                    ):

                        continue

                    values = row.get(
                        "values",
                        row,
                    )

                    if not isinstance(
                        values,
                        dict,
                    ):

                        continue

                    value = values.get(
                        series_name
                    )

                    normalised = (
                        _normalise_point(
                            {
                                "category": row.get(
                                    "category",
                                    row.get(
                                        "label",
                                        index + 1,
                                    ),
                                ),
                                "value": value,
                            },
                            series_name,
                            index,
                        )
                    )

                    if normalised:

                        series.points.append(
                            normalised
                        )

                if series.points:

                    dataset.add_series(
                        series
                    )

    dataset.metadata.update(
        metadata
    )

    dataset.metadata[
        "normalizer"
    ] = "decode_extraction_normalizer"

    dataset.ensure_categories()

    dataset.rebuild_numeric_values()

    # -----------------------------------------
    # Confidence
    # -----------------------------------------
    #
    # Priority:
    #
    # 1. Explicit confidence supplied by the
    #    extraction engine.
    #
    # 2. Otherwise calculate confidence from
    #    individual extracted points.
    #
    # This is important because the existing
    # DECODE extractor already provides:
    #
    #     extraction_confidence
    #
    # and that value must not be accidentally
    # replaced by default point confidence.
    # -----------------------------------------

    explicit_confidence = _first_value(
        raw_result,
        [
            "extraction_confidence",
            "overall_confidence",
            "confidence",
            "score",
        ],
    )

    if explicit_confidence is not None:

        dataset.overall_confidence = (
            _safe_confidence(
                explicit_confidence
            )
        )

        dataset.metadata[
            "confidence_source"
        ] = "extractor"

    elif dataset.series:

        all_confidences = [

            point.confidence

            for series
            in dataset.series

            for point
            in series.points
        ]

        if all_confidences:

            dataset.overall_confidence = (

                sum(
                    all_confidences
                )

                / len(
                    all_confidences
                )
            )

            dataset.metadata[
                "confidence_source"
            ] = "point_average"

        else:

            dataset.overall_confidence = 0.0

            dataset.metadata[
                "confidence_source"
            ] = "none"

    else:

        dataset.overall_confidence = 0.0

        dataset.metadata[
            "confidence_source"
        ] = "none"

    return dataset
