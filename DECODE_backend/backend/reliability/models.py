from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ArtifactResult:
    artifact_id: str
    artifact_type: str

    extraction_success: bool = False
    canonical_success: bool = False
    visualization_success: bool = False
    svg_success: bool = False
    png_success: bool = False

    numerical_integrity: bool = False
    deterministic: bool = False

    success: bool = False

    detected_type: str = ""
    recommended_type: str = ""
    confidence: float = 0.0

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def finalize(self):
        self.success = all(
            [
                self.extraction_success,
                self.canonical_success,
                self.visualization_success,
                self.svg_success,
                self.png_success,
                self.numerical_integrity,
                self.deterministic,
            ]
        )

    def to_dict(self):
        import dataclasses
        return dataclasses.asdict(self)


@dataclass
class DocumentResult:
    document: str

    success: bool = False

    charts_detected: int = 0
    tables_detected: int = 0
    pages: int = 0
    total_duration_seconds: float = 0.0

    artifacts: List[ArtifactResult] = field(
        default_factory=list
    )

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def finalize(self):
        self.success = (
            len(self.errors) == 0
            and all(
                artifact.success
                for artifact in self.artifacts
            )
        )

    def to_dict(self):
        import dataclasses
        return dataclasses.asdict(self)


@dataclass
class ReliabilityReport:
    documents: List[DocumentResult] = field(
        default_factory=list
    )

    def summary(self) -> Dict[str, Any]:
        total_documents = len(self.documents)

        successful_documents = sum(
            1
            for d in self.documents
            if d.success
        )

        artifacts = [
            artifact
            for document in self.documents
            for artifact in document.artifacts
        ]

        successful_artifacts = sum(
            1
            for artifact in artifacts
            if artifact.success
        )

        return {
            "documents": total_documents,
            "successful_documents": successful_documents,
            "document_success_rate": (
                successful_documents / total_documents * 100
                if total_documents
                else 0
            ),
            "artifacts": len(artifacts),
            "successful_artifacts": successful_artifacts,
            "artifact_success_rate": (
                successful_artifacts / len(artifacts) * 100
                if artifacts
                else 0
            ),
        }
