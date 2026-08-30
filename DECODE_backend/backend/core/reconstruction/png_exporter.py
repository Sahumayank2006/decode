import logging
import os
import tempfile
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

PNG_RENDER_TIMEOUT = int(os.getenv("PNG_RENDER_TIMEOUT", "5"))
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# Determine availability once at startup
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except Exception:
    CAIROSVG_AVAILABLE = False

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    # We must actually test import because renderPM might fail on rlPyCairo
    SVGLIB_AVAILABLE = True
except Exception:
    SVGLIB_AVAILABLE = False


def _render_cairosvg(svg_content: str, output: Path) -> bool:
    import cairosvg
    cairosvg.svg2png(
        bytestring=svg_content.encode("utf-8"),
        write_to=str(output)
    )
    return True


def _render_svglib(svg_content: str, output: Path) -> bool:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM

    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as f:
        f.write(svg_content.encode("utf-8"))
        temp_svg = f.name

    try:
        drawing = svg2rlg(temp_svg)
        if drawing is not None:
            renderPM.drawToFile(drawing, str(output), fmt="PNG")
            return True
    finally:
        if os.path.exists(temp_svg):
            os.remove(temp_svg)
    return False


def _run_with_timeout(func, *args, timeout: float):
    result = {"success": False, "error": None}

    def worker():
        try:
            result["success"] = func(*args)
        except Exception as e:
            result["error"] = e

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # It timed out, but we can't forcefully kill a thread easily.
        # We just return failure and let it hang in the background or crash later.
        raise TimeoutError(f"Renderer timed out after {timeout} seconds")
    
    if result["error"]:
        raise result["error"]
        
    return result["success"]


def _render_pymupdf(svg_content: str, output: Path) -> bool:
    import fitz
    doc = fitz.open(stream=svg_content.encode("utf-8"), filetype="svg")
    pix = doc[0].get_pixmap(dpi=150)
    pix.save(str(output))
    doc.close()
    return True


def svg_to_png(
    svg_content: str,
    output_path: str,
) -> str:

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    success = False

    # Strategy 1: PyMuPDF (Always available in DECODE, extremely fast and reliable)
    try:
        success = _render_pymupdf(svg_content, output)
    except Exception as e:
        logger.debug(f"PyMuPDF SVG render failed: {e}")
        success = False

    # Strategy 2: CairoSVG
    if not success and CAIROSVG_AVAILABLE:
        try:
            success = _run_with_timeout(_render_cairosvg, svg_content, output, timeout=PNG_RENDER_TIMEOUT)
        except Exception as e:
            logger.debug(f"CairoSVG failed: {e}")
            success = False

    # Strategy 3: svglib (Pure Python fallback)
    if not success and SVGLIB_AVAILABLE:
        try:
            success = _run_with_timeout(_render_svglib, svg_content, output, timeout=PNG_RENDER_TIMEOUT)
        except Exception as e:
            logger.debug(f"svglib failed: {e}")
            success = False

    if not success or not output.exists():
        raise RuntimeError("All SVG to PNG conversion methods failed.")

    png_bytes = output.read_bytes()
    
    if not png_bytes:
        raise RuntimeError("PNG renderer returned empty output")
        
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise RuntimeError("Invalid PNG output signature")
        
    return str(output)
