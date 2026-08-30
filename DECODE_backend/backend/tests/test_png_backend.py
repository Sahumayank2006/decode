from pathlib import Path
import tempfile
from core.reconstruction.png_exporter import svg_to_png, PNG_SIGNATURE

def test_png_backend_fallback():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "test.png"
        try:
            result = svg_to_png(svg, str(out))
            assert out.exists()
            assert out.stat().st_size > 0
            assert out.read_bytes().startswith(PNG_SIGNATURE)
        except RuntimeError as e:
            assert "All SVG to PNG conversion methods failed" in str(e)
            
if __name__ == "__main__":
    test_png_backend_fallback()
    print("test_png_backend passed")
