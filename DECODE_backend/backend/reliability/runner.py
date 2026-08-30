from __future__ import annotations

import json
import time
import traceback
from pathlib import Path
from typing import Any, Callable

from .models import DocumentResult, ArtifactResult


class ReliabilityRunner:
    """
    Runs the DECODE pipeline against a PDF and records every stage.

    The actual DECODE pipeline is supplied through `processor`.
    This avoids coupling the reliability lab to a particular
    run_chart_pipeline signature.
    """

    def __init__(
        self,
        processor: Callable[[Path, Path], dict[str, Any]],
        output_dir: str | Path = "reliability_output",
    ):
        self.processor = processor
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_file(self, pdf_path: str | Path) -> DocumentResult:
        pdf_path = Path(pdf_path)

        result = DocumentResult(
            document=str(pdf_path),
            success=False,
        )

        start = time.perf_counter()

        if not pdf_path.exists():
            result.errors.append("PDF does not exist")
            result.total_duration_seconds = time.perf_counter() - start
            return result

        if pdf_path.suffix.lower() != ".pdf":
            result.errors.append("File is not a PDF")
            result.total_duration_seconds = time.perf_counter() - start
            return result

        file_output = (
            self.output_dir /
            pdf_path.stem
        )

        file_output.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            pipeline_result = self.processor(
                pdf_path,
                file_output,
            )

            self._consume_pipeline_result(
                result,
                pipeline_result,
                file_output,
            )

            result.success = not bool(result.errors)

        except Exception as exc:
            result.errors.append(
                f"{type(exc).__name__}: {exc}"
            )

            result.warnings.append(
                traceback.format_exc()
            )

        result.total_duration_seconds = (
            time.perf_counter() - start
        )

        self._write_result(result, file_output)

        return result

    def _consume_pipeline_result(
        self,
        result: DocumentResult,
        data: dict[str, Any] | None,
        output_dir: Path,
    ):
        if not isinstance(data, dict):
            result.errors.append(
                "Pipeline did not return a dictionary"
            )
            return

        result.pages = int(
            data.get("pages", 0) or 0
        )

        result.charts_detected = int(
            data.get("charts_detected", 0) or 0
        )

        result.tables_detected = int(
            data.get("tables_detected", 0) or 0
        )

        artifacts = data.get("artifacts", [])

        if not isinstance(artifacts, list):
            result.errors.append(
                "Pipeline artifacts must be a list"
            )
            return

        for index, item in enumerate(artifacts):
            artifact = self._inspect_artifact(
                index,
                item,
            )

            result.artifacts.append(artifact)

    def _inspect_artifact(
        self,
        index: int,
        item: Any,
    ) -> ArtifactResult:

        if not isinstance(item, dict):
            return ArtifactResult(
                artifact_id=str(index),
                artifact_type="unknown",
                success=False,
                errors=[
                    "Artifact is not a dictionary"
                ],
            )

        artifact_id = str(
            item.get("id", index)
        )

        artifact_type = str(
            item.get(
                "artifact_type",
                item.get("type", "unknown"),
            )
        )

        artifact = ArtifactResult(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            success=False,
        )

        artifact.extraction_success = bool(
            item.get(
                "extraction_success",
                item.get("extraction"),
            )
        )

        artifact.canonical_success = bool(
            item.get(
                "canonical_success",
                item.get("canonical_data"),
            )
        )

        artifact.visualization_success = bool(
            item.get(
                "visualization_success",
                item.get("visualization"),
            )
        )

        artifact.svg_success = bool(
            item.get("svg_success")
            or item.get("svg_path")
        )

        artifact.png_success = bool(
            item.get("png_success")
            or item.get("png_path")
        )

        artifact.detected_type = str(
            item.get("detected_type", "")
        )

        artifact.recommended_type = str(
            item.get("recommended_type", "")
        )

        try:
            artifact.confidence = float(
                item.get("confidence", 0.0) or 0.0
            )
        except (TypeError, ValueError):
            artifact.confidence = 0.0

        artifact.warnings.extend(
            item.get("warnings", []) or []
        )

        artifact.errors.extend(
            item.get("errors", []) or []
        )

        artifact.success = (
            artifact.extraction_success
            and artifact.canonical_success
            and artifact.visualization_success
            and artifact.svg_success
        )

        return artifact

    def _write_result(
        self,
        result: DocumentResult,
        output_dir: Path,
    ):
        path = output_dir / "result.json"

        path.write_text(
            json.dumps(
                result.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
