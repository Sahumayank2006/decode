"""
DECODE – Data Models / Schemas
Dataclass-based validation models for all API request/response objects.
Covers both the DECODE chart pipeline and legacy OCR/NLP/Graph modules.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime


# ═════════════════════════════════════════════════════════════════════════════
# DECODE Chart Pipeline Models
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class BoundingBox:
    """Bounding box for a detected chart region."""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


@dataclass
class DataPoint:
    """A single data point in a chart series."""
    label: str = ""
    value: float = 0.0
    confidence: float = 0.0


@dataclass
class ChartSeries:
    """A data series in a chart (e.g. one line, one set of bars)."""
    name: str = ""
    color: str = "#333333"
    points: list = field(default_factory=list)  # list of DataPoint dicts


@dataclass
class AxisLabels:
    """Axis label metadata extracted from a chart."""
    x_label: str = ""
    y_label: str = ""
    x_ticks: list = field(default_factory=list)
    y_ticks: list = field(default_factory=list)


@dataclass
class LegendEntry:
    """A legend entry mapping name to color."""
    name: str = ""
    color: str = ""


@dataclass
class ChartDetection:
    """A detected chart region in a document page."""
    id: str = ""
    document_id: str = ""
    page_number: int = 1
    bounding_box: dict = field(default_factory=dict)
    chart_type: str = "other"       # bar | line | pie | scatter | table | other
    detection_confidence: float = 0.0
    needs_review: bool = False
    original_image_path: str = ""
    original_image_base64: str = ""
    created_at: str = ""


@dataclass
class ChartExtraction:
    """Structured data extracted from a chart."""
    id: str = ""
    chart_id: str = ""
    series: list = field(default_factory=list)       # list of ChartSeries dicts
    axis_labels: dict = field(default_factory=dict)   # AxisLabels dict
    legend: list = field(default_factory=list)         # list of LegendEntry dicts
    title: str = ""
    raw_ocr_text: str = ""
    extraction_confidence: float = 0.0
    created_at: str = ""


@dataclass
class ChartReconstruction:
    """A reconstructed chart (Recharts config + export paths)."""
    id: str = ""
    chart_id: str = ""
    chart_type: str = "bar"
    chart_config: dict = field(default_factory=dict)   # Recharts-compatible JSON
    image_base64: str = ""
    export_svg_path: str = ""
    export_png_path: str = ""
    recommended_alt_type: str = ""
    recommendation_reason: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class ComplianceRecommendation:
    """A single actionable recommendation from compliance analysis."""
    id: str = ""
    text: str = ""
    category: str = ""          # color | layout | geometry | legal | style | approval
    auto_applicable: bool = False
    priority: str = "medium"    # info | medium | high


@dataclass
class ComplianceScore:
    """Copyright compliance analysis result."""
    id: str = ""
    chart_id: str = ""
    reconstruction_id: str = ""
    similarity_score: float = 0.0       # 0-100
    risk_level: str = "low"             # low | medium | high
    color_similarity: float = 0.0       # 0-100
    layout_similarity: float = 0.0      # 0-100
    geometry_similarity: float = 0.0    # 0-100
    recommendations: list = field(default_factory=list)  # list of ComplianceRecommendation dicts
    created_at: str = ""


@dataclass
class ProcessingEvent:
    """A pipeline stage transition event."""
    id: str = ""
    document_id: str = ""
    stage: str = ""             # ingesting | detecting | extracting | reconstructing | scoring | done | failed
    message: str = ""
    created_at: str = ""


@dataclass
class DocumentRecord:
    """Document record stored in Firestore."""
    id: str = ""
    filename: str = ""
    file_path: str = ""
    file_size: int = 0
    extension: str = ""
    status: str = "uploaded"    # uploaded | ingesting | detecting | extracting | reconstructing | scoring | done | failed
    error_message: str = ""
    page_count: int = 0
    summary: dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


# ═════════════════════════════════════════════════════════════════════════════
# Legacy OCR / NLP / Graph Models (kept for backward compatibility)
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class OCRResult:
    text: str = ""
    lines: list = field(default_factory=list)
    word_count: int = 0
    char_count: int = 0
    confidence: float = 0.0
    tables_detected: list = field(default_factory=list)
    figures_detected: list = field(default_factory=list)
    language: str = "eng"
    total_pages: int = 1
    pages: list = field(default_factory=list)


@dataclass
class NLPResult:
    language: dict = field(default_factory=dict)
    entities: dict = field(default_factory=dict)
    keywords: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    classification: dict = field(default_factory=dict)
    readability: dict = field(default_factory=dict)
    word_count: int = 0
    char_count: int = 0
    sentence_count: int = 0


@dataclass
class GraphData:
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)


@dataclass
class GraphAnalytics:
    nodes: int = 0
    edges: int = 0
    density: float = 0.0
    is_connected: bool = False
    average_clustering: float = 0.0
    top_nodes_by_degree: list = field(default_factory=list)
    communities: list = field(default_factory=list)
    community_count: int = 0


@dataclass
class ProcessingResponse:
    document_id: str = ""
    filename: str = ""
    file_size: int = 0
    ocr: dict = field(default_factory=dict)
    nlp: dict = field(default_factory=dict)
    graph: dict = field(default_factory=dict)
    status: str = "success"
    processed_at: str = ""
