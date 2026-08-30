from __future__ import annotations

import json
from pathlib import Path


def load_results(root: str | Path):
    root = Path(root)

    results = []

    for path in root.rglob("result.json"):
        try:
            results.append(
                json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )
            )
        except Exception:
            continue

    return results


def build_summary(results):
    total = len(results)

    successful = sum(
        bool(item.get("success"))
        for item in results
    )

    total_charts = sum(
        int(item.get("charts_detected", 0) or 0)
        for item in results
    )

    total_tables = sum(
        int(item.get("tables_detected", 0) or 0)
        for item in results
    )

    artifact_total = 0
    artifact_success = 0

    for document in results:
        artifacts = document.get(
            "artifacts",
            [],
        )

        artifact_total += len(artifacts)

        artifact_success += sum(
            bool(a.get("success"))
            for a in artifacts
        )

    return {
        "documents": total,
        "documents_successful": successful,
        "document_success_rate": (
            successful / total
            if total
            else 0.0
        ),
        "charts_detected": total_charts,
        "tables_detected": total_tables,
        "artifacts": artifact_total,
        "artifacts_successful": artifact_success,
        "artifact_success_rate": (
            artifact_success / artifact_total
            if artifact_total
            else 0.0
        ),
    }


def write_summary(
    results,
    output: str | Path,
):
    output = Path(output)

    summary = build_summary(results)

    output.write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )

    return summary


def print_summary(summary):
    print()
    print("=" * 60)
    print("DECODE RELIABILITY LAB")
    print("=" * 60)

    print(
        f"Documents: "
        f"{summary['documents']}"
    )

    print(
        f"Successful documents: "
        f"{summary['documents_successful']}"
    )

    print(
        f"Document success rate: "
        f"{summary['document_success_rate']:.1%}"
    )

    print(
        f"Charts detected: "
        f"{summary['charts_detected']}"
    )

    print(
        f"Tables detected: "
        f"{summary['tables_detected']}"
    )

    print(
        f"Artifacts: "
        f"{summary['artifacts']}"
    )

    print(
        f"Successful artifacts: "
        f"{summary['artifacts_successful']}"
    )

    print(
        f"Artifact success rate: "
        f"{summary['artifact_success_rate']:.1%}"
    )

    print("=" * 60)
