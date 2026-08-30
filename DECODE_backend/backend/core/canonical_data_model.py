from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import math


@dataclass
class DataPoint:
    """
    Represents one extracted numerical value.
    """

    category: str
    value: Optional[float]

    series: str = "Value"

    confidence: float = 1.0

    source: str = "unknown"

    bbox: Optional[List[float]] = None

    label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "value": self.value,
            "series": self.series,
            "confidence": self.confidence,
            "source": self.source,
            "bbox": self.bbox,
            "label": self.label,
        }


@dataclass
class DataSeries:
    """
    Represents one logical data series.
    """

    name: str

    points: List[DataPoint] = field(
        default_factory=list
    )

    color: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:

        return {
            "name": self.name,

            "points": [
                point.to_dict()
                for point in self.points
            ],

            "color": self.color,
        }


@dataclass
class CanonicalDataset:
    """
    Universal data representation used
    throughout DECODE.

    Extraction produces this object.

    Reconstruction consumes this object.

    Frontend editing operates on this object.

    Compliance analysis can compare the
    rendering generated from this object.
    """

    title: str = ""

    x_axis_label: str = ""

    y_axis_label: str = ""

    unit: str = ""

    categories: List[str] = field(
        default_factory=list
    )

    series: List[DataSeries] = field(
        default_factory=list
    )

    numeric_values: List[float] = field(
        default_factory=list
    )

    detected_type: str = "unknown"

    extraction_method: str = "unknown"

    overall_confidence: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_series(
        self,
        series: DataSeries,
    ) -> None:

        self.series.append(series)

        self.ensure_categories()

        self.rebuild_numeric_values()

    def add_numeric_value(
        self,
        value: Any,
    ) -> None:

        try:

            number = float(value)

            if math.isfinite(number):

                self.numeric_values.append(
                    number
                )

        except (
            TypeError,
            ValueError,
        ):

            return

    def ensure_categories(self) -> None:

        categories: List[str] = []

        for series in self.series:

            for point in series.points:

                category = str(
                    point.category
                )

                if (
                    category
                    and category not in categories
                ):

                    categories.append(
                        category
                    )

        self.categories = categories

    def rebuild_numeric_values(self) -> None:

        self.numeric_values = []

        confidences: List[float] = []

        for series in self.series:

            for point in series.points:

                if point.value is not None:

                    self.add_numeric_value(
                        point.value
                    )

                confidences.append(
                    max(
                        0.0,
                        min(
                            1.0,
                            float(
                                point.confidence
                            ),
                        ),
                    )
                )

        if confidences:

            if self.metadata.get("confidence_source") != "extractor":

                self.overall_confidence = (
                    sum(confidences)
                    / len(confidences)
                )

    def get_series_names(
        self,
    ) -> List[str]:

        return [
            series.name
            for series in self.series
        ]

    def get_row_count(
        self,
    ) -> int:

        return len(
            self.categories
        )

    def get_series_count(
        self,
    ) -> int:

        return len(
            self.series
        )

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        self.ensure_categories()

        self.rebuild_numeric_values()

        return {

            "title": self.title,

            "x_axis_label": (
                self.x_axis_label
            ),

            "y_axis_label": (
                self.y_axis_label
            ),

            "unit": self.unit,

            "categories": (
                self.categories
            ),

            "series": [
                series.to_dict()
                for series in self.series
            ],

            "numeric_values": (
                self.numeric_values
            ),

            "detected_type": (
                self.detected_type
            ),

            "extraction_method": (
                self.extraction_method
            ),

            "overall_confidence": (
                self.overall_confidence
            ),

            "metadata": (
                self.metadata
            ),
        }

    @classmethod
    def from_dict(
        cls,
        payload: Dict[str, Any],
    ) -> "CanonicalDataset":

        dataset = cls(

            title=str(
                payload.get(
                    "title",
                    "",
                )
            ),

            x_axis_label=str(
                payload.get(
                    "x_axis_label",
                    "",
                )
            ),

            y_axis_label=str(
                payload.get(
                    "y_axis_label",
                    "",
                )
            ),

            unit=str(
                payload.get(
                    "unit",
                    "",
                )
            ),

            detected_type=str(
                payload.get(
                    "detected_type",
                    "unknown",
                )
            ),

            extraction_method=str(
                payload.get(
                    "extraction_method",
                    "unknown",
                )
            ),

            overall_confidence=float(
                payload.get(
                    "overall_confidence",
                    0.0,
                )
                or 0.0
            ),

            metadata=dict(
                payload.get(
                    "metadata",
                    {},
                )
                or {}
            ),
        )

        raw_series = payload.get(
            "series",
            [],
        )

        if not isinstance(
            raw_series,
            list,
        ):

            raw_series = []

        for raw_series_item in raw_series:

            if not isinstance(
                raw_series_item,
                dict,
            ):

                continue

            series = DataSeries(

                name=str(
                    raw_series_item.get(
                        "name",
                        "Value",
                    )
                ),

                color=raw_series_item.get(
                    "color"
                ),
            )

            raw_points = (
                raw_series_item.get(
                    "points",
                    [],
                )
            )

            if not isinstance(
                raw_points,
                list,
            ):

                raw_points = []

            for raw_point in raw_points:

                if not isinstance(
                    raw_point,
                    dict,
                ):

                    continue

                raw_value = (
                    raw_point.get(
                        "value"
                    )
                )

                value: Optional[
                    float
                ] = None

                if raw_value is not None:

                    try:

                        value = float(
                            raw_value
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        value = None

                try:

                    confidence = float(
                        raw_point.get(
                            "confidence",
                            1.0,
                        )
                        or 0.0
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    confidence = 0.0

                point = DataPoint(

                    category=str(
                        raw_point.get(
                            "category",
                            "",
                        )
                    ),

                    value=value,

                    series=str(
                        raw_point.get(
                            "series",
                            series.name,
                        )
                    ),

                    confidence=confidence,

                    source=str(
                        raw_point.get(
                            "source",
                            "unknown",
                        )
                    ),

                    bbox=raw_point.get(
                        "bbox"
                    ),

                    label=(
                        raw_point.get(
                            "label"
                        )
                    ),
                )

                series.points.append(
                    point
                )

            dataset.series.append(
                series
            )

        dataset.ensure_categories()

        dataset.rebuild_numeric_values()

        return dataset


def canonical_to_table(
    dataset: CanonicalDataset,
) -> List[Dict[str, Any]]:
    """
    Convert canonical series data into
    frontend-friendly table rows.

    Example:

    [
        {
            "category": "2024",
            "values": {
                "Revenue": 120,
                "Profit": 45
            }
        }
    ]
    """

    dataset.ensure_categories()

    rows: Dict[
        str,
        Dict[str, Any],
    ] = {}

    for category in dataset.categories:

        rows[category] = {

            "category": category,

            "values": {},
        }

    for series in dataset.series:

        for point in series.points:

            category = str(
                point.category
            )

            if category not in rows:

                rows[category] = {

                    "category": category,

                    "values": {},
                }

            rows[category][
                "values"
            ][series.name] = point.value

    return list(
        rows.values()
    )


def table_to_canonical(
    rows: List[Dict[str, Any]],
    *,
    title: str = "",
    detected_type: str = "table",
) -> CanonicalDataset:
    """
    Convert frontend table data back into
    the universal canonical representation.

    This is what enables:

        table → chart

    without performing extraction again.
    """

    dataset = CanonicalDataset(

        title=title,

        detected_type=detected_type,

        extraction_method=(
            "table_edit"
        ),
    )

    if not rows:

        return dataset

    series_names: List[str] = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        values = row.get(
            "values",
            {},
        )

        if not isinstance(
            values,
            dict,
        ):

            continue

        for name in values:

            name = str(name)

            if name not in series_names:

                series_names.append(
                    name
                )

    series_map: Dict[
        str,
        DataSeries,
    ] = {}

    for name in series_names:

        series_map[name] = DataSeries(
            name=name
        )

    for row_index, row in enumerate(
        rows
    ):

        if not isinstance(
            row,
            dict,
        ):

            continue

        category = str(
            row.get(
                "category",
                row_index + 1,
            )
        )

        values = row.get(
            "values",
            {},
        )

        if not isinstance(
            values,
            dict,
        ):

            values = {}

        for name in series_names:

            raw_value = values.get(
                name
            )

            value = None

            if raw_value is not None:

                try:

                    value = float(
                        raw_value
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    value = None

            series_map[
                name
            ].points.append(

                DataPoint(

                    category=category,

                    value=value,

                    series=name,

                    confidence=1.0,

                    source="table_edit",
                )
            )

    for series in series_map.values():

        dataset.add_series(
            series
        )

    dataset.metadata[
        "source"
    ] = "editable_table"

    return dataset
