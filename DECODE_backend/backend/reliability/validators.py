from __future__ import annotations

import math
from pathlib import Path
import xml.etree.ElementTree as ET


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def validate_svg(path: str | Path) -> tuple[bool, str]:
    path = Path(path)

    if not path.exists():
        return False, "SVG file does not exist"

    if path.stat().st_size == 0:
        return False, "SVG file is empty"

    try:
        text = path.read_text(encoding="utf-8")

        if "<svg" not in text:
            return False, "Missing <svg> element"

        if "</svg>" not in text:
            return False, "Missing closing </svg> element"

        for bad in ("NaN", "Infinity", "undefined"):
            if bad in text:
                return False, f"Invalid token found: {bad}"

        ET.fromstring(text)

    except Exception as exc:
        return False, f"Invalid SVG: {exc}"

    return True, "valid"


def validate_png(path: str | Path) -> tuple[bool, str]:
    path = Path(path)

    if not path.exists():
        return False, "PNG file does not exist"

    size = path.stat().st_size

    if size == 0:
        return False, "PNG file is empty"

    try:
        with path.open("rb") as fh:
            signature = fh.read(8)

        if signature != PNG_SIGNATURE:
            return False, "Invalid PNG signature"

    except Exception as exc:
        return False, f"PNG validation failed: {exc}"

    return True, "valid"


def validate_numeric_values(values) -> tuple[bool, str]:
    for value in values or []:
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        if not math.isfinite(value):
            return False, f"Non-finite numeric value: {value}"

    return True, "valid"


def validate_canonical_dataset(dataset) -> tuple[bool, str]:
    if dataset is None:
        return False, "Canonical dataset is None"

    values = getattr(dataset, "numeric_values", [])

    ok, reason = validate_numeric_values(values)

    if not ok:
        return False, reason

    if not hasattr(dataset, "series"):
        return False, "Canonical dataset has no series"

    return True, "valid"
