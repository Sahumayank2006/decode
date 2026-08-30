import tempfile
from pathlib import Path
from reliability.validators import validate_png, PNG_SIGNATURE

def test_png_validation():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "test.png"
        assert validate_png(p)[0] is False
        
        p.write_bytes(b"")
        assert validate_png(p)[0] is False
        
        p.write_bytes(b"Not a PNG")
        assert validate_png(p)[0] is False
        
        p.write_bytes(PNG_SIGNATURE + b"data")
        assert validate_png(p)[0] is True

if __name__ == "__main__":
    test_png_validation()
    print("test_png_validation passed")
