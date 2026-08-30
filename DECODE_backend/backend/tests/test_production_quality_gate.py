import json
from pathlib import Path


OUTPUT = Path("reliability_output/summary.json")


MIN_DOCUMENT_SUCCESS = 95.0
MIN_ARTIFACT_SUCCESS = 95.0


def main():
    if not OUTPUT.exists():
        raise AssertionError(
            "Reliability report does not exist."
        )

    summary = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    document_rate = float(
        summary.get("document_success_rate", 0)
    ) * 100.0

    artifact_rate = float(
        summary.get("artifact_success_rate", 0)
    ) * 100.0

    print()
    print("=" * 60)
    print("DECODE PRODUCTION QUALITY GATE")
    print("=" * 60)

    print(
        f"Document success: {document_rate:.2f}%"
    )

    print(
        f"Artifact success: {artifact_rate:.2f}%"
    )

    if document_rate < MIN_DOCUMENT_SUCCESS:
        raise AssertionError(
            "Document success rate below production threshold."
        )

    if artifact_rate < MIN_ARTIFACT_SUCCESS:
        raise AssertionError(
            "Artifact success rate below production threshold."
        )

    print()
    print("PRODUCTION QUALITY GATE PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
