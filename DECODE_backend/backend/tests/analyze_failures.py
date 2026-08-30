import json
from collections import Counter
from pathlib import Path


ROOT = Path("reliability_output")


def classify_failure(error_msg):
    error_msg = str(error_msg).lower()
    
    if "unsupported operand type" in error_msg and "nonetype" in error_msg:
        return "TABLE_NONE_VALUE"
    
    if "'str' object has no attribute 'append'" in error_msg:
        return "TABLE_MULTI_SERIES"
        
    if "canonical" in error_msg or "mapping" in error_msg:
        return "CANONICAL_MAPPING"
        
    if "svg" in error_msg or "render" in error_msg and "png" not in error_msg:
        return "SVG_RENDER"
        
    if "png" in error_msg or "cairo" in error_msg or "reportlab" in error_msg:
        return "PNG_RENDER"
        
    return "UNKNOWN"


def main():
    failures = []

    for result_file in ROOT.rglob("result.json"):
        try:
            data = json.loads(
                result_file.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            continue

        pdf_name = result_file.parent.name
        
        for artifact in data.get("artifacts", []):
            if not artifact.get("success", False):
                failures.append(
                    (
                        pdf_name,
                        artifact,
                    )
                )

    print()
    print("=" * 70)
    print("DECODE FAILURE ANALYSIS")
    print("=" * 70)

    if not failures:
        print("No artifact failures found.")
        return

    error_counter = Counter()
    class_counter = Counter()

    for document, artifact in failures:
        print()
        print(f"DOCUMENT: {document}")
        print(f"ID: {artifact.get('artifact_id')}")
        print(f"TYPE: {artifact.get('artifact_type')}")
        print(f"  Extraction: {artifact.get('extraction_success')}")
        print(f"  Canonical:  {artifact.get('canonical_success')}")
        print(f"  Visualiz.:  {artifact.get('visualization_success')}")
        print(f"  SVG:        {artifact.get('svg_success')}")
        print(f"  PNG:        {artifact.get('png_success')}")

        errors = artifact.get("errors", [])
        if not errors:
            # Infer from false flags
            if not artifact.get("png_success"):
                errors.append("PNG generation failed or timed out")
            elif not artifact.get("svg_success"):
                errors.append("SVG generation failed")
                
        for error in errors:
            cls = classify_failure(error)
            print(f"  ERROR [{cls}]: {error}")
            error_counter[error] += 1
            class_counter[cls] += 1

    print()
    print("=" * 70)
    print("MOST COMMON ERRORS")
    print("=" * 70)

    for error, count in error_counter.most_common():
        print(f"{count}x  {error}")
        
    print()
    print("=" * 70)
    print("FAILURE CLASSIFICATIONS")
    print("=" * 70)

    for cls, count in class_counter.most_common():
        print(f"{count}x  {cls}")


if __name__ == "__main__":
    main()
