import math
from core.visualization.table_normalizer import safe_float, align_values, normalize_table_series, format_table_value

def test_safe_float():
    assert safe_float(None) is None
    assert safe_float("N/A") is None
    assert safe_float("—") is None
    assert safe_float("") is None
    assert safe_float(float('nan')) is None
    assert safe_float(float('inf')) is None
    assert safe_float(float('-inf')) is None
    assert safe_float("42") == 42.0

def test_align_values():
    assert align_values([1, 2, 3], 5) == [1, 2, 3, None, None]
    assert align_values([1, 2, 3, 4, 5], 3) == [1, 2, 3]

def test_normalize_table_series():
    raw_series = [
        {"name": "Revenue", "values": [1, None, "N/A"]},
        {"name": "Revenue", "values": ["2", float('nan'), 3]}
    ]
    norm = normalize_table_series(raw_series, 4)
    assert norm[0]["name"] == "Revenue"
    assert norm[0]["values"] == [1.0, None, None, None]
    assert norm[1]["name"] == "Revenue (2)"
    assert norm[1]["values"] == [2.0, None, 3.0, None]

def test_format_table_value():
    assert format_table_value(None) == "—"
    assert format_table_value(float('nan')) == "—"
    assert format_table_value(float('inf')) == "—"
    assert format_table_value(42) == "42"

if __name__ == "__main__":
    test_safe_float()
    test_align_values()
    test_normalize_table_series()
    test_format_table_value()
    print("All table normalization tests passed!")
