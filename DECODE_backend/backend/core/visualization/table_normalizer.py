import math


def safe_float(value):
    if value is None:
        return None

    if isinstance(value, bool):
        return float(value)

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(result):
        return None

    return result


def align_values(values, count):
    values = list(values or [])

    if len(values) < count:
        values.extend([None] * (count - len(values)))
    elif len(values) > count:
        values = values[:count]

    return values


def unique_name(name, used):
    base = str(name or "Series")

    if base not in used:
        used.add(base)
        return base

    index = 2
    while f"{base} ({index})" in used:
        index += 1

    result = f"{base} ({index})"
    used.add(result)
    return result


def normalize_table_series(series, category_count):
    if not isinstance(series, list):
        return []

    normalized = []
    used_names = set()

    for item in series:
        if not isinstance(item, dict):
            continue

        raw_name = item.get("name", "Series")
        name = unique_name(raw_name, used_names)

        raw_values = item.get("values", [])
        if not isinstance(raw_values, list):
            raw_values = []

        values = [
            safe_float(value)
            for value in raw_values
        ]
        
        values = align_values(values, category_count)

        normalized.append(
            {
                "name": name,
                "values": values,
            }
        )

    return normalized


def format_table_value(value):
    if value is None:
        return "—"

    if isinstance(value, float):
        if not math.isfinite(value):
            return "—"

    return str(value)
