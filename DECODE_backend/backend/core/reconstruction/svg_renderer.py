from __future__ import annotations

import math
from html import escape
from typing import List

from core.canonical_data_model import (
    CanonicalDataset,
    DataSeries,
)

from .spec import VisualizationSpec
from .palettes import color_for_series


def _safe_text(value, default: str = "") -> str:
    """
    Convert arbitrary extracted values into safe SVG text.

    This is intentionally defensive because chart/table text can originate
    from OCR or PDF extraction and may contain None, numbers, or unexpected
    objects.
    """
    if value is None:
        return default

    try:
        text = str(value)
    except Exception:
        return default

    return text.strip()


def _esc(value) -> str:
    """
    XML/SVG-safe text escaping.

    All extracted PDF/OCR text must pass through this before being
    inserted into SVG markup.
    """
    return escape(
        _safe_text(value),
        quote=True,
    )


def _safe_float(value, default=0.0) -> float:
    """
    Convert to a finite float or return the supplied default.
    """
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return default

    if not math.isfinite(number):
        return default

    return number


def _is_finite_number(value) -> bool:
    """
    Return True only for finite numeric values.

    Rejects:
      - None
      - NaN
      - +inf
      - -inf
      - non-numeric strings
    """
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return False

    return math.isfinite(number)


def _clean_numeric_value(value, default: float = 0.0) -> float:
    """
    Safely convert an arbitrary value to a finite float.

    Non-finite or invalid values fall back to `default`.
    """
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return default

    if not math.isfinite(number):
        return default

    return number


def _format_number(
    value,
    decimals: int = 2,
    trim_trailing_zeroes: bool = True,
) -> str:
    """
    Produce stable human-readable numeric text for SVG labels.

    Examples:
        100       -> "100"
        100.5     -> "100.5"
        100.5678  -> "100.57"
        1.0       -> "1"
    """
    number = _clean_numeric_value(value)

    decimals = max(0, min(int(decimals), 8))

    text = f"{number:.{decimals}f}"

    if trim_trailing_zeroes and "." in text:
        text = text.rstrip("0").rstrip(".")

    if text == "-0":
        text = "0"

    return text


def _truncate_text(
    value,
    max_chars: int = 32,
    suffix: str = "…",
) -> str:
    """
    Prevent extremely long extracted labels from destroying chart layout.
    """
    text = _safe_text(value)

    if max_chars <= 0:
        return ""

    if len(text) <= max_chars:
        return text

    if max_chars <= len(suffix):
        return text[:max_chars]

    return text[: max_chars - len(suffix)] + suffix


def _safe_dimension(value, minimum: int, maximum: int) -> int:
    """
    Clamp SVG dimensions/margins to safe integer ranges.
    """
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        number = minimum

    return max(minimum, min(number, maximum))


def _nice_number(
    value: float,
) -> float:

    if value <= 0:

        return 1.0

    exponent = math.floor(
        math.log10(value)
    )

    fraction = value / (
        10 ** exponent
    )

    if fraction <= 1:

        nice = 1

    elif fraction <= 2:

        nice = 2

    elif fraction <= 5:

        nice = 5

    else:

        nice = 10

    return nice * (
        10 ** exponent
    )


def _nice_max(
    value: float,
) -> float:

    if value <= 0:

        return 1.0

    step = _nice_number(
        value / 5
    )

    return math.ceil(
        value / step
    ) * step


class SVGChartRenderer:

    SUPPORTED_CHART_TYPES = frozenset({
        "bar",
        "line",
        "area",
        "scatter",
        "pie",
        "donut",
        "table",
    })

    @property
    def supported_chart_types(self):
        """
        Return the visualization types supported by
        the SVG renderer.
        """

        return self.SUPPORTED_CHART_TYPES

    def supports(
        self,
        chart_type: str,
    ) -> bool:
        """
        Check whether this renderer supports a
        visualization type.
        """

        normalized = str(
            chart_type or ""
        ).strip().lower()

        return (
            normalized
            in self.SUPPORTED_CHART_TYPES
        )

    def render(
        self,
        dataset,
        spec,
    ) -> str:
        """
        Render a CanonicalDataset according to a
        VisualizationSpec.

        The renderer uses explicit dispatch rather than
        dynamically evaluating method names. This keeps
        unsupported visualization types deterministic and
        safe.
        """

        chart_type = str(
            spec.chart_type or "bar"
        ).strip().lower()

        renderers = {
            "bar": self.render_bar,
            "line": self.render_line,
            "area": self.render_area,
            "scatter": getattr(self, "render_scatter", None),
            "pie": getattr(self, "render_pie", None),
            "donut": getattr(self, "render_donut", None),
            "table": getattr(self, "render_table", None),
        }

        renderer = renderers.get(chart_type)

        if renderer is None:
            supported = ", ".join(
                sorted(renderers.keys())
            )

            raise ValueError(
                f"Unsupported chart type: "
                f"{chart_type}. "
                f"Supported types: {supported}"
            )

        return renderer(
            dataset,
            spec,
        )

    # --------------------------------------------------
    # Common SVG
    # --------------------------------------------------

    def _svg_start(
        self,
        spec: VisualizationSpec,
    ) -> str:

        return (
            f'<svg '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'width="{spec.width}" '
            f'height="{spec.height}" '
            f'viewBox="0 0 '
            f'{spec.width} '
            f'{spec.height}">'
        )

    def _text(
        self,
        x,
        y,
        text,
        size,
        color,
        anchor="middle",
        weight="400",
    ) -> str:

        escaped_text = _esc(text)

        return (
            f'<text '
            f'x="{x}" '
            f'y="{y}" '
            f'font-family="{_esc(self._font)}" '
            f'font-size="{size}px" '
            f'font-weight="{weight}" '
            f'fill="{color}" '
            f'text-anchor="{anchor}">'
            f'{escaped_text}'
            f'</text>'
        )

    @property
    def _font(self):

        return getattr(
            self,
            "_current_font",
            "Inter, Arial, sans-serif",
        )

    def _setup(
        self,
        spec: VisualizationSpec,
    ):

        self._current_font = (
            spec.font_family
        )

    # --------------------------------------------------
    # Common geometry
    # --------------------------------------------------

    def _geometry(
        self,
        spec: VisualizationSpec,
    ):

        left = spec.margin_left

        right = (
            spec.width
            - spec.margin_right
        )

        top = spec.margin_top

        bottom = (
            spec.height
            - spec.margin_bottom
        )

        return (
            left,
            top,
            right,
            bottom,
        )

    def _value_range(self, dataset):
        """
        Calculate a safe numerical range for SVG rendering.

        Handles:
        - empty datasets
        - None values
        - NaN / Infinity
        - negative-only datasets
        - positive-only datasets
        - mixed positive/negative datasets
        - identical min/max values
        - extremely large values
        - very small ranges
        """

        import math

        values = []

        for series in getattr(dataset, "series", []) or []:
            for point in getattr(series, "points", []) or []:
                value = getattr(point, "value", None)

                if value is None:
                    continue

                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue

                if not math.isfinite(value):
                    continue

                values.append(value)

        # Completely empty / invalid dataset.
        if not values:
            return 0.0, 1.0

        minimum = min(values)
        maximum = max(values)

        # Single-value dataset.
        if minimum == maximum:
            if minimum == 0:
                return -1.0, 1.0

            magnitude = max(abs(minimum), 1.0)

            padding = magnitude * 0.10

            if padding == 0 or not math.isfinite(padding):
                padding = 1.0

            minimum -= padding
            maximum += padding

        else:
            span = maximum - minimum

            # Protect against pathological floating-point ranges.
            if not math.isfinite(span) or span <= 0:
                span = max(abs(minimum), abs(maximum), 1.0)

            padding = span * 0.08

            if not math.isfinite(padding) or padding <= 0:
                padding = 1.0

            minimum -= padding
            maximum += padding

        # Ensure zero is visible for mixed-sign data.
        if minimum < 0 < maximum:
            minimum = min(minimum, 0.0)
            maximum = max(maximum, 0.0)

        # Negative-only data should remain negative.
        # Positive-only data should remain positive unless
        # the range naturally crosses zero.

        # Final sanity check.
        if not math.isfinite(minimum):
            minimum = 0.0

        if not math.isfinite(maximum):
            maximum = 1.0

        if minimum == maximum:
            maximum = minimum + 1.0

        return minimum, maximum

    def _safe_ticks(self, minimum, maximum, count=6):
        """
        Generate stable, readable Y-axis tick values.
        """

        import math

        try:
            minimum = float(minimum)
            maximum = float(maximum)
        except (TypeError, ValueError):
            return [0.0, 1.0]

        if not math.isfinite(minimum) or not math.isfinite(maximum):
            return [0.0, 1.0]

        if maximum <= minimum:
            return [minimum, maximum]

        count = max(2, min(int(count), 12))

        span = maximum - minimum

        raw_step = span / (count - 1)

        if raw_step <= 0 or not math.isfinite(raw_step):
            return [minimum, maximum]

        magnitude = 10 ** math.floor(math.log10(raw_step))

        normalized = raw_step / magnitude

        if normalized <= 1:
            nice = 1
        elif normalized <= 2:
            nice = 2
        elif normalized <= 5:
            nice = 5
        else:
            nice = 10

        step = nice * magnitude

        if not math.isfinite(step) or step <= 0:
            step = raw_step

        start = math.floor(minimum / step) * step
        end = math.ceil(maximum / step) * step

        ticks = []

        value = start

        # Protection against pathological loops.
        max_iterations = 100

        for _ in range(max_iterations):
            if value > end + step * 0.001:
                break

            if math.isfinite(value):
                # Remove floating-point noise.
                rounded = round(value, 12)
                ticks.append(rounded)

            value += step

        if len(ticks) < 2:
            return [minimum, maximum]

        return ticks

    def _format_axis_value(self, value):
        """
        Format numerical axis labels without unnecessary
        floating-point noise.
        """

        import math

        try:
            value = float(value)
        except (TypeError, ValueError):
            return ""

        if not math.isfinite(value):
            return ""

        absolute = abs(value)

        if absolute == 0:
            return "0"

        if absolute >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f}B"

        if absolute >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"

        if absolute >= 1_000:
            return f"{value / 1_000:.1f}K"

        if absolute >= 1:
            if value.is_integer():
                return str(int(value))
            return f"{value:.2f}".rstrip("0").rstrip(".")

        if absolute >= 0.01:
            return f"{value:.3f}".rstrip("0").rstrip(".")

        return f"{value:.4f}".rstrip("0").rstrip(".")

    def _safe_categories(self, dataset):
        """
        Return a clean, deterministic category list.

        Categories may originate from OCR/PDF extraction and can therefore
        contain None, empty strings, non-string objects, or duplicates.
        """

        categories = getattr(dataset, "categories", None) or []

        result = []
        seen = set()

        for index, category in enumerate(categories):
            if category is None:
                category = ""

            category = str(category).strip()

            if not category:
                category = f"Category {index + 1}"

            # Preserve duplicate categories visually while keeping them
            # deterministic.
            candidate = category

            if candidate in seen:
                suffix = 2

                while f"{category} ({suffix})" in seen:
                    suffix += 1

                candidate = f"{category} ({suffix})"

            seen.add(candidate)
            result.append(candidate)

        return result

    def _point_value(self, point):
        """
        Safely retrieve a numerical point value.

        Invalid values are represented as None rather than causing
        renderer failures.
        """

        import math

        if point is None:
            return None

        value = getattr(point, "value", None)

        if value is None:
            return None

        try:
            value = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(value):
            return None

        return value

    def _truncate_label(self, value, max_length=24):
        """
        Prevent extremely long PDF/OCR labels from destroying chart layout.
        """

        if value is None:
            return ""

        value = str(value)

        if len(value) <= max_length:
            return value

        if max_length <= 3:
            return value[:max_length]

        return value[: max_length - 3] + "..."

    # --------------------------------------------------
    # Axes
    # --------------------------------------------------

    def _draw_axes(
        self,
        spec,
        x,
        y,
        right,
        bottom,
        minimum,
        maximum,
    ) -> str:

        output = []

        # Y axis

        output.append(
            f'<line '
            f'x1="{x}" '
            f'y1="{y}" '
            f'x2="{x}" '
            f'y2="{bottom}" '
            f'stroke="{spec.axis_color}" '
            f'stroke-width="1.5"/>'
        )

        # X axis

        output.append(
            f'<line '
            f'x1="{x}" '
            f'y1="{bottom}" '
            f'x2="{right}" '
            f'y2="{bottom}" '
            f'stroke="{spec.axis_color}" '
            f'stroke-width="1.5"/>'
        )

        ticks = self._safe_ticks(minimum, maximum)

        for value in ticks:

            span = maximum - minimum

            if span <= 0:
                span = 1.0

            ratio = (value - minimum) / span

            py = (
                bottom
                - ratio
                * (
                    bottom - y
                )
            )

            if spec.show_grid:

                output.append(
                    f'<line '
                    f'x1="{x}" '
                    f'y1="{py:.2f}" '
                    f'x2="{right}" '
                    f'y2="{py:.2f}" '
                    f'stroke="{spec.grid_color}" '
                    f'stroke-width="1"/>'
                )

            output.append(
                self._text(
                    x - 12,
                    py + 5,
                    self._format_axis_value(value),
                    spec.font_size,
                    spec.text_color,
                    "end",
                )
            )

        return "".join(
            output
        )

    def _draw_title(
        self,
        dataset,
        spec,
    ) -> str:

        title = (
            spec.title
            or dataset.title
        )

        if not title:

            return ""

        return self._text(
            spec.width / 2,
            45,
            title,
            spec.title_font_size,
            spec.text_color,
            "middle",
            "700",
        )

    def _draw_axis_labels(
        self,
        dataset,
        spec,
        x,
        bottom,
    ) -> str:

        output = []

        x_label = (
            spec.x_axis_label
            or dataset.x_axis_label
        )

        y_label = (
            spec.y_axis_label
            or dataset.y_axis_label
        )

        if x_label:

            output.append(
                self._text(
                    (
                        spec.margin_left
                        + (
                            spec.width
                            - spec.margin_left
                            - spec.margin_right
                        )
                        / 2
                    ),
                    spec.height - 25,
                    x_label,
                    spec.font_size,
                    spec.text_color,
                )
            )

        if y_label:

            output.append(
                f'<text '
                f'transform="rotate(-90)" '
                f'x="{-spec.height / 2}" '
                f'y="25" '
                f'font-family="{_esc(spec.font_family)}" '
                f'font-size="{spec.font_size}px" '
                f'fill="{spec.text_color}" '
                f'text-anchor="middle">'
                f'{_esc(y_label)}'
                f'</text>'
            )

        return "".join(
            output
        )

    # --------------------------------------------------
    # BAR
    # --------------------------------------------------

    def render_bar(
        self,
        dataset,
        spec,
    ) -> str:

        self._setup(
            spec
        )

        x, y, right, bottom = (
            self._geometry(
                spec
            )
        )

        minimum, maximum = (
            self._value_range(
                dataset
            )
        )

        width = (
            right - x
        )

        height = (
            bottom - y
        )

        categories = (
            dataset.categories
        )

        if not categories:

            categories = []

            for series in (
                dataset.series
            ):

                for point in (
                    series.points
                ):

                    if (
                        point.category
                        not in categories
                    ):

                        categories.append(
                            point.category
                        )

        if not categories:

            return (
                self._svg_start(
                    spec
                )
                + "</svg>"
            )

        category_width = (
            width
            / len(categories)
        )

        series_count = max(
            len(dataset.series),
            1,
        )

        bar_width = (
            category_width
            * 0.72
            / series_count
        )

        output = [
            self._svg_start(
                spec
            ),
            (
                f'<rect '
                f'x="0" y="0" '
                f'width="{spec.width}" '
                f'height="{spec.height}" '
                f'fill="{spec.background}"/>'
            ),
            self._draw_title(
                dataset,
                spec,
            ),
            self._draw_axes(
                spec,
                x,
                y,
                right,
                bottom,
                minimum,
                maximum,
            ),
        ]

        for category_index, category in (
            enumerate(categories)
        ):

            cx = (
                x
                + category_width
                * (
                    category_index
                    + 0.5
                )
            )

            output.append(
                self._text(
                    cx,
                    bottom + 25,
                    category,
                    spec.font_size,
                    spec.text_color,
                )
            )

        for series_index, series in (
            enumerate(
                dataset.series
            )
        ):

            color = (
                spec.series_colors.get(
                    series.name
                )
                or getattr(
                    series,
                    "color",
                    None,
                )
                or color_for_series(
                    series.name,
                    series_index,
                    spec.palette_name,
                )
            )

            lookup = {
                str(
                    point.category
                ): point.value
                for point
                in series.points
            }

            for category_index, category in (
                enumerate(categories)
            ):

                value = lookup.get(
                    str(category)
                )

                if value is None:

                    continue

                value = _safe_float(
                    value
                )

                ratio = (

                    value - minimum

                ) / (

                    maximum - minimum

                )

                bar_height = (
                    ratio * height
                )

                bx = (

                    x
                    + category_width
                    * category_index
                    + category_width
                    * 0.14
                    + bar_width
                    * series_index

                )

                by = (
                    bottom
                    - bar_height
                )

                output.append(
                    f'<rect '
                    f'x="{bx:.2f}" '
                    f'y="{by:.2f}" '
                    f'width="{bar_width * 0.9:.2f}" '
                    f'height="{bar_height:.2f}" '
                    f'rx="4" '
                    f'fill="{color}"/>'
                )

        output.append(
            self._draw_axis_labels(
                dataset,
                spec,
                x,
                bottom,
            )
        )

        output.append(
            "</svg>"
        )

        return "".join(
            output
        )

    # --------------------------------------------------
    # LINE
    # --------------------------------------------------

    def render_line(
        self,
        dataset,
        spec,
    ) -> str:

        self._setup(
            spec
        )

        x, y, right, bottom = (
            self._geometry(
                spec
            )
        )

        minimum, maximum = (
            self._value_range(
                dataset
            )
        )

        width = (
            right - x
        )

        height = (
            bottom - y
        )

        categories = (
            dataset.categories
        )

        if not categories:

            return (
                self._svg_start(
                    spec
                )
                + "</svg>"
            )

        step = (

            width
            / max(
                len(categories) - 1,
                1,
            )

        )

        output = [
            self._svg_start(
                spec
            ),
            (
                f'<rect '
                f'x="0" y="0" '
                f'width="{spec.width}" '
                f'height="{spec.height}" '
                f'fill="{spec.background}"/>'
            ),
            self._draw_title(
                dataset,
                spec,
            ),
            self._draw_axes(
                spec,
                x,
                y,
                right,
                bottom,
                minimum,
                maximum,
            ),
        ]

        for index, category in enumerate(
            categories
        ):

            px = (
                x
                + step
                * index
            )

            output.append(
                self._text(
                    px,
                    bottom + 25,
                    category,
                    spec.font_size,
                    spec.text_color,
                )
            )

        for series_index, series in (
            enumerate(
                dataset.series
            )
        ):

            color = (
                spec.series_colors.get(
                    series.name
                )
                or getattr(
                    series,
                    "color",
                    None,
                )
                or color_for_series(
                    series.name,
                    series_index,
                    spec.palette_name,
                )
            )

            lookup = {
                str(
                    point.category
                ): point.value
                for point
                in series.points
            }

            points = []

            for index, category in enumerate(
                categories
            ):

                value = lookup.get(
                    str(category)
                )

                if value is None:

                    continue

                ratio = (

                    _safe_float(
                        value
                    )
                    - minimum

                ) / (

                    maximum - minimum

                )

                px = (
                    x
                    + step * index
                )

                py = (
                    bottom
                    - ratio * height
                )

                points.append(
                    (
                        px,
                        py,
                    )
                )

            if len(points) >= 2:

                path = " ".join(

                    (
                        (
                            "M"
                            if i == 0
                            else "L"
                        )
                        + f" {px:.2f} {py:.2f}"
                    )

                    for i, (
                        px,
                        py,
                    ) in enumerate(
                        points
                    )
                )

                output.append(
                    f'<path '
                    f'd="{path}" '
                    f'fill="none" '
                    f'stroke="{color}" '
                    f'stroke-width="3" '
                    f'stroke-linecap="round" '
                    f'stroke-linejoin="round"/>'
                )

            for px, py in points:

                output.append(
                    f'<circle '
                    f'cx="{px:.2f}" '
                    f'cy="{py:.2f}" '
                    f'r="5" '
                    f'fill="{color}"/>'
                )

        output.append(
            self._draw_axis_labels(
                dataset,
                spec,
                x,
                bottom,
            )
        )

        output.append(
            "</svg>"
        )

        return "".join(
            output
        )

    # --------------------------------------------------
    # AREA
    # --------------------------------------------------

    def render_area(
        self,
        dataset,
        spec,
    ) -> str:

        self._setup(
            spec
        )

        # Start with line rendering geometry,
        # then add filled paths.

        x, y, right, bottom = (
            self._geometry(
                spec
            )
        )

        minimum, maximum = (
            self._value_range(
                dataset
            )
        )

        width = (
            right - x
        )

        height = (
            bottom - y
        )

        categories = (
            dataset.categories
        )

        if not categories:

            return (
                self._svg_start(
                    spec
                )
                + "</svg>"
            )

        step = (

            width
            / max(
                len(categories) - 1,
                1,
            )
        )

        output = [
            self._svg_start(
                spec
            ),
            (
                f'<rect '
                f'x="0" y="0" '
                f'width="{spec.width}" '
                f'height="{spec.height}" '
                f'fill="{spec.background}"/>'
            ),
            self._draw_title(
                dataset,
                spec,
            ),
            self._draw_axes(
                spec,
                x,
                y,
                right,
                bottom,
                minimum,
                maximum,
            ),
        ]

        for index, category in enumerate(
            categories
        ):

            px = (
                x
                + step * index
            )

            output.append(
                self._text(
                    px,
                    bottom + 25,
                    category,
                    spec.font_size,
                    spec.text_color,
                )
            )

        for series_index, series in (
            enumerate(
                dataset.series
            )
        ):

            color = (
                spec.series_colors.get(
                    series.name
                )
                or getattr(
                    series,
                    "color",
                    None,
                )
                or color_for_series(
                    series.name,
                    series_index,
                    spec.palette_name,
                )
            )

            lookup = {
                str(
                    point.category
                ): point.value
                for point
                in series.points
            }

            points = []

            for index, category in enumerate(
                categories
            ):

                value = lookup.get(
                    str(category)
                )

                if value is None:

                    continue

                ratio = (

                    _safe_float(
                        value
                    )
                    - minimum

                ) / (

                    maximum - minimum

                )

                px = (
                    x
                    + step * index
                )

                py = (
                    bottom
                    - ratio * height
                )

                points.append(
                    (
                        px,
                        py,
                    )
                )

            if len(points) < 2:

                continue

            line_path = " ".join(

                (
                    (
                        "M"
                        if i == 0
                        else "L"
                    )
                    + f" {px:.2f} {py:.2f}"
                )

                for i, (
                    px,
                    py,
                ) in enumerate(
                    points
                )
            )

            first_x = points[0][0]

            last_x = points[-1][0]

            area_path = (
                line_path
                + f" L {last_x:.2f} {bottom:.2f}"
                + f" L {first_x:.2f} {bottom:.2f}"
                + " Z"
            )

            output.append(
                f'<path '
                f'd="{area_path}" '
                f'fill="{color}" '
                f'fill-opacity="0.18" '
                f'stroke="none"/>'
            )

            output.append(
                f'<path '
                f'd="{line_path}" '
                f'fill="none" '
                f'stroke="{color}" '
                f'stroke-width="3"/>'
            )

        output.append(
            self._draw_axis_labels(
                dataset,
                spec,
                x,
                bottom,
            )
        )

        output.append(
            "</svg>"
        )

        return "".join(
            output
        )

    def _polar_point(
        self,
        cx: float,
        cy: float,
        radius: float,
        angle_degrees: float,
    ):
        """
        Convert polar coordinates into SVG coordinates.

        SVG angles increase clockwise because the Y axis points
        downward.
        """

        angle = math.radians(
            angle_degrees
        )

        x = (
            cx
            + radius
            * math.cos(angle)
        )

        y = (
            cy
            + radius
            * math.sin(angle)
        )

        return x, y

    def _arc_path(
        self,
        cx: float,
        cy: float,
        outer_radius: float,
        start_angle: float,
        end_angle: float,
        inner_radius: float = 0.0,
    ):
        """
        Build an SVG path for a pie or donut slice.
        """

        start_outer = self._polar_point(
            cx,
            cy,
            outer_radius,
            start_angle,
        )

        end_outer = self._polar_point(
            cx,
            cy,
            outer_radius,
            end_angle,
        )

        large_arc = (
            1
            if (
                end_angle
                - start_angle
            ) > 180
            else 0
        )

        if inner_radius <= 0:

            return (
                f"M {cx:.3f} {cy:.3f} "
                f"L {start_outer[0]:.3f} "
                f"{start_outer[1]:.3f} "
                f"A {outer_radius:.3f} "
                f"{outer_radius:.3f} "
                f"0 {large_arc} 1 "
                f"{end_outer[0]:.3f} "
                f"{end_outer[1]:.3f} Z"
            )

        start_inner = self._polar_point(
            cx,
            cy,
            inner_radius,
            start_angle,
        )

        end_inner = self._polar_point(
            cx,
            cy,
            inner_radius,
            end_angle,
        )

        return (
            f"M {start_outer[0]:.3f} "
            f"{start_outer[1]:.3f} "
            f"A {outer_radius:.3f} "
            f"{outer_radius:.3f} "
            f"0 {large_arc} 1 "
            f"{end_outer[0]:.3f} "
            f"{end_outer[1]:.3f} "
            f"L {end_inner[0]:.3f} "
            f"{end_inner[1]:.3f} "
            f"A {inner_radius:.3f} "
            f"{inner_radius:.3f} "
            f"0 {large_arc} 0 "
            f"{start_inner[0]:.3f} "
            f"{start_inner[1]:.3f} Z"
        )

    def _prepare_pie_data(
        self,
        dataset,
    ):
        """
        Prepare canonical series data for pie/donut rendering.

        Pie and donut charts represent parts of a whole, therefore
        negative values are mathematically invalid and are rejected.
        Missing and zero values are ignored.
        """

        items = []

        for series_index, series in enumerate(
            dataset.series
        ):

            for point in series.points:

                if point.value is None:
                    continue

                value = float(
                    point.value
                )

                if value < 0:

                    raise ValueError(
                        "Pie and donut charts "
                        "cannot represent negative "
                        f"values. Found {value} "
                        f"for '{series.name}'."
                    )

                if value == 0:
                    continue

                items.append({
                    "category": str(
                        point.category
                        if point.category is not None
                        else ""
                    ),
                    "value": value,
                    "series": str(
                        series.name
                    ),
                    "series_index": (
                        series_index
                    ),
                })

        numeric_values = [
            item["value"] for item in items
            if isinstance(item["value"], (int, float))
            and math.isfinite(float(item["value"]))
        ]
        total = sum(numeric_values)

        if total <= 0:

            return [], 0.0

        for item in items:

            item["percentage"] = (
                item["value"]
                / total
                * 100.0
            )

        return items, total

    def render_pie(
        self,
        dataset,
        spec,
    ) -> str:
        """
        Render a pie chart from canonical data.
        """

        return self._render_pie_or_donut(
            dataset,
            spec,
            donut=False,
        )

    def render_donut(
        self,
        dataset,
        spec,
    ) -> str:
        """
        Render a donut chart from canonical data.
        """

        return self._render_pie_or_donut(
            dataset,
            spec,
            donut=True,
        )

    def _render_pie_or_donut(
        self,
        dataset,
        spec,
        donut: bool = False,
    ) -> str:
        """
        Shared deterministic renderer for pie and donut charts.
        """

        self._setup(spec)

        svg = [self._svg_start(spec)]

        left, top, right, bottom = (
            self._geometry(spec)
        )

        # ---------------------------------------------------------
        # Background
        # ---------------------------------------------------------

        svg.append(
            f'<rect x="0" y="0" '
            f'width="{spec.width}" '
            f'height="{spec.height}" '
            f'fill="{_esc(spec.background)}"/>'
        )

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------

        svg.append(
            self._draw_title(
                dataset,
                spec,
            )
        )

        # ---------------------------------------------------------
        # Prepare data
        # ---------------------------------------------------------

        items, total = (
            self._prepare_pie_data(
                dataset
            )
        )

        # ---------------------------------------------------------
        # Empty data
        # ---------------------------------------------------------

        if not items or total <= 0:

            svg.append(
                self._text(
                    (left + right) / 2,
                    (top + bottom) / 2,
                    "No positive data available",
                    spec.font_size,
                    spec.text_color,
                    anchor="middle",
                )
            )

            svg.append("</svg>")

            return "".join(svg)

        # ---------------------------------------------------------
        # Geometry
        # ---------------------------------------------------------

        center_x = (
            left + right
        ) / 2

        center_y = (
            top + bottom
        ) / 2

        available_width = (
            right - left
        )

        available_height = (
            bottom - top
        )

        radius = (
            min(
                available_width,
                available_height,
            )
            * 0.34
        )

        inner_radius = (
            radius * 0.55
            if donut
            else 0.0
        )

        # ---------------------------------------------------------
        # Slices
        # ---------------------------------------------------------

        current_angle = -90.0

        for index, item in enumerate(
            items
        ):

            sweep = (
                item["percentage"]
                / 100.0
                * 360.0
            )

            # Prevent floating point accumulation
            # from creating a tiny gap at the end.
            if index == len(items) - 1:

                end_angle = 270.0

            else:

                end_angle = (
                    current_angle
                    + sweep
                )

            color = (
                spec.series_colors.get(
                    item["series"]
                )
                or color_for_series(
                    item["series"],
                    item["series_index"],
                    spec.palette_name,
                )
            )

            path = self._arc_path(
                center_x,
                center_y,
                radius,
                current_angle,
                end_angle,
                inner_radius,
            )

            svg.append(
                f'<path '
                f'd="{path}" '
                f'fill="{_esc(color)}" '
                f'stroke="{_esc(spec.background)}" '
                f'stroke-width="2" '
                f'data-series="{_esc(item["series"])}" '
                f'data-category="{_esc(item["category"])}" '
                f'data-value="{item["value"]:.6g}" '
                f'data-percentage="{item["percentage"]:.6f}"/>'
            )

            current_angle = end_angle

        # ---------------------------------------------------------
        # Center label for donut
        # ---------------------------------------------------------

        if donut:

            svg.append(
                self._text(
                    center_x,
                    center_y - 5,
                    f"{total:g}",
                    max(
                        18,
                        spec.title_font_size
                        - 4,
                    ),
                    spec.text_color,
                    anchor="middle",
                    weight="700",
                )
            )

            svg.append(
                self._text(
                    center_x,
                    center_y + 20,
                    "Total",
                    spec.font_size,
                    spec.axis_color,
                    anchor="middle",
                )
            )

        # ---------------------------------------------------------
        # Legend
        # ---------------------------------------------------------

        if spec.show_legend:

            legend_y = (
                bottom
                + 35
            )

            legend_x = left

            for index, item in enumerate(
                items
            ):

                color = (
                    spec.series_colors.get(
                        item["series"]
                    )
                    or color_for_series(
                        item["series"],
                        item["series_index"],
                        spec.palette_name,
                    )
                )

                svg.append(
                    f'<rect '
                    f'x="{legend_x:.3f}" '
                    f'y="{legend_y - 10:.3f}" '
                    f'width="12" '
                    f'height="12" '
                    f'rx="2" '
                    f'fill="{_esc(color)}"/>'
                )

                legend_text = (
                    f'{item["category"]} '
                    f'({item["percentage"]:.1f}%)'
                )

                svg.append(
                    self._text(
                        legend_x + 18,
                        legend_y,
                        legend_text,
                        spec.font_size,
                        spec.text_color,
                    )
                )

                legend_x += (
                    35
                    + len(legend_text)
                    * max(
                        6,
                        spec.font_size * 0.5,
                    )
                )

                # Wrap legend if necessary.
                if (
                    legend_x
                    > right - 100
                ):

                    legend_x = left
                    legend_y += (
                        spec.font_size
                        + 18
                    )

        svg.append("</svg>")

        return "".join(svg)


    # --------------------------------------------------
    # SCATTER
    # --------------------------------------------------

    def render_scatter(
        self,
        dataset,
        spec,
    ) -> str:
        """
        Render a scatter plot from CanonicalDataset.

        The canonical dataset remains the single source of truth.
        Each DataPoint becomes one SVG circle.

        X coordinates are derived from category order. This supports
        both categorical labels and numeric-looking categories while
        preserving the extracted values exactly.
        """

        self._setup(spec)

        svg = [self._svg_start(spec)]

        left, top, right, bottom = self._geometry(spec)

        minimum, maximum = self._value_range(dataset)

        # ---------------------------------------------------------
        # Background
        # ---------------------------------------------------------

        svg.append(
            f'<rect x="0" y="0" '
            f'width="{spec.width}" '
            f'height="{spec.height}" '
            f'fill="{_esc(spec.background)}"/>'
        )

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------

        svg.append(
            self._draw_title(
                dataset,
                spec,
            )
        )

        # ---------------------------------------------------------
        # Axes
        # ---------------------------------------------------------

        svg.append(
            self._draw_axes(
                spec,
                left,
                top,
                right,
                bottom,
                minimum,
                maximum,
            )
        )

        # ---------------------------------------------------------
        # Axis labels
        # ---------------------------------------------------------

        svg.append(
            self._draw_axis_labels(
                dataset,
                spec,
                left,
                bottom,
            )
        )

        categories = list(
            dataset.categories
        )

        # Recover categories if necessary.
        if not categories:

            seen = set()

            for series in dataset.series:

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

        # ---------------------------------------------------------
        # Empty dataset protection
        # ---------------------------------------------------------

        if not categories:

            svg.append(
                self._text(
                    (left + right) / 2,
                    (top + bottom) / 2,
                    "No data available",
                    spec.font_size,
                    spec.text_color,
                    anchor="middle",
                )
            )

            svg.append("</svg>")

            return "".join(svg)

        # ---------------------------------------------------------
        # X-axis geometry
        # ---------------------------------------------------------

        plot_width = max(
            1.0,
            right - left,
        )

        if len(categories) == 1:

            x_positions = {
                str(categories[0]): (
                    left + plot_width / 2
                )
            }

        else:

            step = (
                plot_width
                / (len(categories) - 1)
            )

            x_positions = {
                str(category): (
                    left + index * step
                )
                for index, category
                in enumerate(categories)
            }

        # ---------------------------------------------------------
        # Scatter points
        # ---------------------------------------------------------

        for series_index, series in enumerate(
            dataset.series
        ):

            color = (
                spec.series_colors.get(
                    series.name
                )
                or color_for_series(
                    series.name,
                    series_index,
                    spec.palette_name,
                )
            )

            for point in series.points:

                if point.value is None:
                    continue

                category = str(
                    point.category
                    if point.category is not None
                    else ""
                )

                x = x_positions.get(
                    category
                )

                if x is None:
                    continue

                # Protect against degenerate ranges.
                if maximum == minimum:

                    y = (
                        top
                        + (bottom - top) / 2
                    )

                else:

                    ratio = (
                        (
                            float(point.value)
                            - minimum
                        )
                        / (
                            maximum
                            - minimum
                        )
                    )

                    y = (
                        bottom
                        - ratio
                        * (bottom - top)
                    )

                svg.append(
                    f'<circle '
                    f'cx="{x:.3f}" '
                    f'cy="{y:.3f}" '
                    f'r="5" '
                    f'fill="{_esc(color)}" '
                    f'stroke="{_esc(spec.background)}" '
                    f'stroke-width="1.5" '
                    f'data-series="{_esc(series.name)}" '
                    f'data-category="{_esc(category)}" '
                    f'data-value="{_safe_float(point.value):.6g}"/>'
                )

        # ---------------------------------------------------------
        # X-axis tick labels
        # ---------------------------------------------------------

        label_y = (
            bottom
            + max(20, spec.font_size + 8)
        )

        for category in categories:

            category_text = str(
                category
            )

            x = x_positions[
                category_text
            ]

            svg.append(
                self._text(
                    x,
                    label_y,
                    category_text,
                    spec.font_size,
                    spec.text_color,
                    anchor="middle",
                )
            )

        # ---------------------------------------------------------
        # Legend
        # ---------------------------------------------------------

        if spec.show_legend and dataset.series:

            legend_y = max(
                22,
                top - 35,
            )

            legend_x = left

            for series_index, series in enumerate(
                dataset.series
            ):

                color = (
                    spec.series_colors.get(
                        series.name
                    )
                    or color_for_series(
                        series.name,
                        series_index,
                        spec.palette_name,
                    )
                )

                svg.append(
                    f'<rect '
                    f'x="{legend_x:.3f}" '
                    f'y="{legend_y - 10:.3f}" '
                    f'width="12" '
                    f'height="12" '
                    f'rx="2" '
                    f'fill="{_esc(color)}"/>'
                )

                svg.append(
                    self._text(
                        legend_x + 18,
                        legend_y,
                        series.name,
                        spec.font_size,
                        spec.text_color,
                    )
                )

                legend_x += (
                    25
                    + len(str(series.name))
                    * max(
                        7,
                        spec.font_size * 0.55,
                    )
                )

        svg.append("</svg>")

        return "".join(svg)


    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    def render_table(
        self,
        dataset: CanonicalDataset,
        spec: VisualizationSpec,
    ) -> str:
        """
        Render the canonical dataset as a structured SVG table.

        The table is generated directly from CanonicalDataset so numerical
        values are never re-extracted or recalculated.
        """

        self._setup(spec)

        width = max(int(spec.width), 600)
        height = max(int(spec.height), 400)

        margin_left = max(int(spec.margin_left), 20)
        margin_right = max(int(spec.margin_right), 20)
        margin_top = max(int(spec.margin_top), 30)
        margin_bottom = max(int(spec.margin_bottom), 30)

        title = dataset.title or spec.title or "Data Table"

        categories = list(dataset.categories or [])

        # If categories were not explicitly populated, recover them from
        # the canonical series without changing numerical values.
        if not categories:
            seen = set()

            for series in dataset.series:
                for point in series.points:
                    category = str(point.category)

                    if category not in seen:
                        seen.add(category)
                        categories.append(category)

        series_list = list(dataset.series or [])

        # ------------------------------------------------------------------
        # Empty dataset
        # ------------------------------------------------------------------

        if not categories and not series_list:
            svg = self._svg_start(spec)

            svg.append(
                self._text(
                    width / 2,
                    height / 2,
                    "No data available",
                    max(spec.font_size, 18),
                    spec.text_color,
                    anchor="middle",
                )
            )

            svg.append("</svg>")
            return "".join(svg)

        # ------------------------------------------------------------------
        # Geometry
        # ------------------------------------------------------------------

        table_x = margin_left
        table_y = margin_top + 60

        table_width = width - margin_left - margin_right

        if table_width < 300:
            table_width = 300

        # First column contains category names.
        category_column_width = min(
            max(table_width * 0.24, 140),
            260,
        )

        remaining_width = max(
            table_width - category_column_width,
            100,
        )

        series_count = max(len(series_list), 1)

        series_column_width = remaining_width / series_count

        header_height = 52
        row_height = 46

        table_height = header_height + row_height * len(categories)

        # ------------------------------------------------------------------
        # SVG
        # ------------------------------------------------------------------

        svg = [self._svg_start(spec)]

        # Background
        svg.append(
            f'<rect x="0" y="0" width="{width}" height="{height}" '
            f'fill="{_esc(spec.background)}"/>'
        )

        # ------------------------------------------------------------------
        # Title
        # ------------------------------------------------------------------

        if title:
            svg.append(
                self._text(
                    width / 2,
                    margin_top,
                    title,
                    spec.title_font_size,
                    spec.text_color,
                    anchor="middle",
                    weight="700",
                )
            )

        # ------------------------------------------------------------------
        # Axis / metadata subtitle
        # ------------------------------------------------------------------

        subtitle_parts = []

        if dataset.x_axis_label:
            subtitle_parts.append(str(dataset.x_axis_label))

        if dataset.y_axis_label:
            subtitle_parts.append(str(dataset.y_axis_label))

        if dataset.unit:
            subtitle_parts.append(f"Unit: {dataset.unit}")

        if subtitle_parts:
            subtitle = " • ".join(subtitle_parts)

            svg.append(
                self._text(
                    width / 2,
                    margin_top + 30,
                    subtitle,
                    max(spec.font_size - 1, 11),
                    spec.axis_color,
                    anchor="middle",
                )
            )

        # ------------------------------------------------------------------
        # Table container
        # ------------------------------------------------------------------

        svg.append(
            f'<rect x="{table_x}" y="{table_y}" '
            f'width="{table_width}" height="{table_height}" '
            f'fill="{_esc(spec.background)}" '
            f'stroke="{_esc(spec.axis_color)}" '
            f'stroke-width="1.5" rx="8"/>'
        )

        # ------------------------------------------------------------------
        # Header background
        # ------------------------------------------------------------------

        svg.append(
            f'<rect x="{table_x}" y="{table_y}" '
            f'width="{table_width}" height="{header_height}" '
            f'fill="{_esc(spec.grid_color)}" '
            f'opacity="0.65"/>'
        )

        # ------------------------------------------------------------------
        # Header: Category
        # ------------------------------------------------------------------

        category_header_x = table_x + category_column_width / 2

        svg.append(
            self._text(
                category_header_x,
                table_y + header_height / 2 + spec.font_size / 2 - 2,
                dataset.x_axis_label or "Category",
                spec.font_size,
                spec.text_color,
                anchor="middle",
                weight="700",
            )
        )

        # ------------------------------------------------------------------
        # Header: Series names
        # ------------------------------------------------------------------

        for series_index, series in enumerate(series_list):

            x = (
                table_x
                + category_column_width
                + series_column_width * series_index
            )

            center_x = x + series_column_width / 2

            series_name = str(series.name or f"Series {series_index + 1}")

            series_color = (
                spec.series_colors.get(series_name)
                or getattr(series, "color", None)
                or color_for_series(
                    series_name,
                    series_index,
                    spec.palette_name,
                )
            )

            # Small color indicator.
            indicator_size = 10

            svg.append(
                f'<rect x="{center_x - 40}" '
                f'y="{table_y + header_height / 2 - indicator_size / 2}" '
                f'width="{indicator_size}" '
                f'height="{indicator_size}" '
                f'rx="2" '
                f'fill="{_esc(series_color)}"/>'
            )

            svg.append(
                self._text(
                    center_x + 2,
                    table_y + header_height / 2 + spec.font_size / 2 - 2,
                    series_name,
                    spec.font_size,
                    spec.text_color,
                    anchor="middle",
                    weight="700",
                )
            )

        # ------------------------------------------------------------------
        # Build lookup maps.
        # ------------------------------------------------------------------

        value_maps = []

        for series in series_list:
            mapping = {}

            for point in series.points:
                category = str(point.category)

                # Preserve the first occurrence rather than silently
                # replacing duplicate canonical points.
                if category not in mapping:
                    mapping[category] = point

            value_maps.append(mapping)

        # ------------------------------------------------------------------
        # Rows
        # ------------------------------------------------------------------

        for row_index, category in enumerate(categories):

            row_y = table_y + header_height + row_index * row_height

            # Alternating row background.
            if row_index % 2 == 1:
                svg.append(
                    f'<rect x="{table_x}" y="{row_y}" '
                    f'width="{table_width}" height="{row_height}" '
                    f'fill="{_esc(spec.grid_color)}" opacity="0.20"/>'
                )

            # Category cell.
            category_text = str(category)

            svg.append(
                self._text(
                    table_x + 14,
                    row_y + row_height / 2 + spec.font_size / 2 - 2,
                    category_text,
                    spec.font_size,
                    spec.text_color,
                    anchor="start",
                    weight="600",
                )
            )

            # Series values.
            for series_index, series in enumerate(series_list):

                column_x = (
                    table_x
                    + category_column_width
                    + series_column_width * series_index
                )

                point = value_maps[series_index].get(category)

                if point is None or point.value is None:
                    value_text = "—"
                    raw_value = ""
                    confidence = ""
                else:
                    value = float(point.value)

                    # Preserve exact numeric value while presenting it
                    # cleanly to the user.
                    if not math.isfinite(value):
                        value_text = "—"
                    elif value.is_integer():
                        value_text = str(int(value))
                    else:
                        value_text = f"{value:g}"

                    raw_value = str(value)

                    confidence = str(
                        getattr(point, "confidence", 1.0)
                    )

                center_x = column_x + series_column_width / 2

                svg.append(
                    self._text(
                        center_x,
                        row_y + row_height / 2 + spec.font_size / 2 - 2,
                        value_text,
                        spec.font_size,
                        spec.text_color,
                        anchor="middle",
                    )
                )

                # Invisible metadata carrier.
                #
                # This allows the frontend to identify exactly which
                # canonical value produced the rendered table cell.
                svg.append(
                    f'<rect '
                    f'x="{column_x}" '
                    f'y="{row_y}" '
                    f'width="{series_column_width}" '
                    f'height="{row_height}" '
                    f'fill="transparent" '
                    f'pointer-events="all" '
                    f'data-series="{_esc(series.name)}" '
                    f'data-category="{_esc(category)}" '
                    f'data-value="{_esc(raw_value)}" '
                    f'data-confidence="{_esc(confidence)}"/>'
                )

        # ------------------------------------------------------------------
        # Grid lines
        # ------------------------------------------------------------------

        # Vertical separator after category column.
        separator_x = table_x + category_column_width

        svg.append(
            f'<line x1="{separator_x}" y1="{table_y}" '
            f'x2="{separator_x}" y2="{table_y + table_height}" '
            f'stroke="{_esc(spec.grid_color)}" stroke-width="1"/>'
        )

        # Remaining vertical separators.
        for series_index in range(series_count + 1):

            x = (
                table_x
                + category_column_width
                + series_column_width * series_index
            )

            svg.append(
                f'<line x1="{x}" y1="{table_y}" '
                f'x2="{x}" y2="{table_y + table_height}" '
                f'stroke="{_esc(spec.grid_color)}" '
                f'stroke-width="1"/>'
            )

        # Horizontal separators.
        for row_index in range(len(categories) + 1):

            y = table_y + header_height + row_index * row_height

            svg.append(
                f'<line x1="{table_x}" y1="{y}" '
                f'x2="{table_x + table_width}" y2="{y}" '
                f'stroke="{_esc(spec.grid_color)}" '
                f'stroke-width="1"/>'
            )

        svg.append("</svg>")

        return "".join(svg)
