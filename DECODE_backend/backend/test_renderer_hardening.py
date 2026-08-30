import math

from core.reconstruction.svg_renderer import (
    _clean_numeric_value,
    _esc,
    _format_number,
    _is_finite_number,
    _safe_dimension,
    _safe_float,
    _safe_text,
    _truncate_text,
)


def main():
    print("=== RENDERER HARDENING TEST ===")

    # ---------------------------------------------------------
    # Text handling
    # ---------------------------------------------------------

    assert _safe_text(None) == ""
    assert _safe_text("  Revenue  ") == "Revenue"
    assert _safe_text(123) == "123"

    # ---------------------------------------------------------
    # SVG/XML escaping
    # ---------------------------------------------------------

    escaped = _esc("<Revenue & Profit>")

    assert "&lt;" in escaped
    assert "&amp;" in escaped
    assert "<Revenue" not in escaped

    # ---------------------------------------------------------
    # Numeric validation
    # ---------------------------------------------------------

    assert _is_finite_number(10)
    assert _is_finite_number(10.5)

    assert not _is_finite_number(None)
    assert not _is_finite_number("abc")
    assert not _is_finite_number(float("nan"))
    assert not _is_finite_number(float("inf"))
    assert not _is_finite_number(float("-inf"))

    # ---------------------------------------------------------
    # Safe float
    # ---------------------------------------------------------

    assert _safe_float("10.5") == 10.5
    assert _safe_float(None, 7.0) == 7.0
    assert _safe_float("abc", 3.0) == 3.0

    assert _safe_float(float("nan"), 5.0) == 5.0
    assert _safe_float(float("inf"), 6.0) == 6.0

    # ---------------------------------------------------------
    # Numeric cleaning
    # ---------------------------------------------------------

    assert _clean_numeric_value("42") == 42.0
    assert _clean_numeric_value(None, 9.0) == 9.0
    assert _clean_numeric_value(float("nan"), 8.0) == 8.0

    # ---------------------------------------------------------
    # Number formatting
    # ---------------------------------------------------------

    assert _format_number(100) == "100"
    assert _format_number(100.5) == "100.5"
    assert _format_number(100.5678) == "100.57"
    assert _format_number(1.0) == "1"
    assert _format_number(-0.0) == "0"

    # ---------------------------------------------------------
    # Text truncation
    # ---------------------------------------------------------

    assert _truncate_text("Revenue") == "Revenue"

    truncated = _truncate_text(
        "This is an extremely long category label",
        max_chars=15,
    )

    assert len(truncated) <= 15
    assert truncated.endswith("…")

    # ---------------------------------------------------------
    # Dimensions
    # ---------------------------------------------------------

    assert _safe_dimension(500, 100, 2000) == 500
    assert _safe_dimension(20, 100, 2000) == 100
    assert _safe_dimension(5000, 100, 2000) == 2000

    print("RENDERER HARDENING TEST PASSED")


if __name__ == "__main__":
    main()
