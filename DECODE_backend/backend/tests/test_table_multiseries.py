from core.visualization.table_normalizer import normalize_table_series

def test_multiseries():
    raw_series = [
        {"name": "A", "values": [1, 2]},
        {"name": "A", "values": [3, 4]},
        {"name": None, "values": []},
        {"name": "B", "values": ["garbage"]},
        "invalid_series"
    ]
    norm = normalize_table_series(raw_series, 2)
    assert len(norm) == 4
    assert norm[0]["name"] == "A"
    assert norm[1]["name"] == "A (2)"
    assert norm[2]["name"] == "Series"
    assert norm[3]["name"] == "B"
    assert norm[2]["values"] == [None, None]
    assert norm[3]["values"] == [None, None]

if __name__ == "__main__":
    test_multiseries()
    print("test_table_multiseries passed")
