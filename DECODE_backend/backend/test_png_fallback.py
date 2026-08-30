import os
import sys
from pathlib import Path
from core.reconstruction.png_exporter import svg_to_png

def test_fallback():
    # Artificially hide cairosvg to force fallback
    if 'cairosvg' in sys.modules:
        del sys.modules['cairosvg']
    
    class CairoBlocker:
        def find_spec(self, fullname, path, target=None):
            if fullname == 'cairosvg':
                raise ImportError("CairoSVG blocked for testing")
            return None
            
    blocker = CairoBlocker()
    sys.meta_path.insert(0, blocker)
    
    try:
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect x="0" y="0" width="100" height="100" fill="red"/></svg>'
        out_path = Path("test_exports/fallback_test.png")
        if out_path.exists():
            out_path.unlink()
            
        result_path = svg_to_png(svg, str(out_path))
        
        assert out_path.exists()
        print(f"Fallback PNG created at: {result_path}")
        print("FALLBACK PNG EXPORT TEST PASSED")
    finally:
        sys.meta_path.remove(blocker)

if __name__ == "__main__":
    test_fallback()
