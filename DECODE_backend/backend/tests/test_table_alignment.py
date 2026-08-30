from core.visualization.table_normalizer import align_values

def test_alignment():
    assert align_values([1, 2, 3], 5) == [1, 2, 3, None, None]
    assert align_values([1, 2, 3, 4, 5, 6, 7], 3) == [1, 2, 3]
    assert align_values([], 4) == [None, None, None, None]
    assert align_values(None, 2) == [None, None]

if __name__ == "__main__":
    test_alignment()
    print("test_table_alignment passed")
