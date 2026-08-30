import tempfile
from pathlib import Path
from reliability.validators import validate_svg

def test_svg_validation():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "test.svg"
        assert validate_svg(p)[0] is False
        
        p.write_text("")
        assert validate_svg(p)[0] is False
        
        p.write_text("<svg></svg>")
        assert validate_svg(p)[0] is True
        
        p.write_text("<svg>NaN</svg>")
        assert validate_svg(p)[0] is False
        
        p.write_text("<svg>Infinity</svg>")
        assert validate_svg(p)[0] is False
        
        p.write_text("<svg>undefined</svg>")
        assert validate_svg(p)[0] is False
        
        p.write_text("<not-svg></not-svg>")
        assert validate_svg(p)[0] is False

if __name__ == "__main__":
    test_svg_validation()
    print("test_svg_validation passed")
