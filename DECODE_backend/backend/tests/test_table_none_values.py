import math
from core.visualization.table_normalizer import safe_float, format_table_value

def test_none_values():
    assert safe_float(None) is None
    assert safe_float(float('nan')) is None
    assert safe_float(float('inf')) is None
    assert safe_float(float('-inf')) is None
    assert safe_float("") is None
    assert safe_float("N/A") is None
    assert safe_float("—") is None
    
    assert format_table_value(None) == "—"
    assert format_table_value(float('nan')) == "—"
    assert format_table_value(float('inf')) == "—"

if __name__ == "__main__":
    test_none_values()
    print("test_table_none_values passed")
