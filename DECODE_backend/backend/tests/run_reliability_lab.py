from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from reliability import (
    ReliabilityRunner,
    load_results,
    write_summary,
    print_summary,
)
from reliability.validators import validate_png

from services.chart_pipeline import run_chart_pipeline


CORPUS = ROOT / "tests" / "corpus"

OUTPUT = ROOT / "reliability_output"


def process_pdf(pdf_path: Path, output_dir: Path):
    doc_id = pdf_path.stem
    result = run_chart_pipeline(doc_id, str(pdf_path))
    
    pages = result.get("page_count", 0)
    charts = result.get("charts", [])
    extractions = {e.get("chart_id"): e for e in result.get("extractions", [])}
    reconstructions = {r.get("chart_id"): r for r in result.get("reconstructions", [])}
    
    charts_detected = 0
    tables_detected = 0
    artifacts = []
    
    for chart in charts:
        cid = chart.get("id")
        detected_type = chart.get("chart_type", "unknown")
        
        if detected_type == "table":
            tables_detected += 1
        else:
            charts_detected += 1
            
        ext = extractions.get(cid, {})
        rec = reconstructions.get(cid, {})
        
        extraction_success = bool(ext)
        canonical_success = bool(ext.get("canonical_data"))
        visualization_success = bool(rec)
        svg_success = bool(rec.get("export_svg_path"))
        
        png_path_str = rec.get("export_png_path")
        png_success = False
        if png_path_str:
            # Re-resolve the correct path based on how export_png_path is stored (e.g., /static/...)
            if png_path_str.startswith("/static/"):
                png_full_path = ROOT / "static" / png_path_str.replace("/static/", "")
            else:
                png_full_path = Path(png_path_str)
            png_ok, _ = validate_png(png_full_path)
            png_success = png_ok

        artifacts.append({
            "id": cid,
            "artifact_type": "table" if detected_type == "table" else "chart",
            "extraction_success": extraction_success,
            "canonical_success": canonical_success,
            "visualization_success": visualization_success,
            "svg_success": svg_success,
            "png_success": png_success,
            "detected_type": detected_type,
            "recommended_type": rec.get("recommended_alt_type", ""),
            "confidence": ext.get("extraction_confidence", 0.0),
            "warnings": [],
            "errors": []
        })
        
    return {
        "pages": pages,
        "charts_detected": charts_detected,
        "tables_detected": tables_detected,
        "artifacts": artifacts
    }

def main():
    if not CORPUS.exists():
        print(
            f"Corpus directory missing: {CORPUS}"
        )
        return 1

    pdfs = sorted(
        CORPUS.rglob("*.pdf")
    )

    if not pdfs:
        print(
            "No PDFs found in corpus."
        )
        print(
            f"Put PDFs inside: {CORPUS}"
        )
        return 1

    runner = ReliabilityRunner(
        processor=process_pdf,
        output_dir=OUTPUT,
    )

    for pdf in pdfs:
        print()
        print(
            f"Testing: {pdf.name}"
        )

        result = runner.run_file(pdf)

        status = (
            "PASS"
            if result.success
            else "FAIL"
        )

        print(
            f"[{status}] "
            f"{pdf.name} "
            f"({result.total_duration_seconds:.2f}s)"
        )

    results = load_results(OUTPUT)

    summary = write_summary(
        results,
        OUTPUT / "summary.json",
    )

    print_summary(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
