"""
DECODE – Data Models / Schemas
Pydantic-based validation models for API request/response objects.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime


@dataclass
class DocumentRecord:
    """Firestore document record."""
    id: str = ""
    filename: str = ""
    file_path: str = ""
    file_size: int = 0
    mime_type: str = ""
    file_hash: str = ""
    ocr_language: str = "eng"
    word_count: int = 0
    char_count: int = 0
    confidence: float = 0.0
    total_pages: int = 1
    status: str = "pending"
    created_at: str = ""


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
class EntityResult:
    entities: dict = field(default_factory=dict)
    noun_phrases: list = field(default_factory=list)
    entity_count: int = 0


@dataclass
class KeywordResult:
    keyword: str = ""
    score: float = 0.0


@dataclass
class SummaryResult:
    summary: str = ""
    sentences: list = field(default_factory=list)
    total_sentences: int = 0
    ratio: float = 0.0
    scored_sentences: list = field(default_factory=list)


@dataclass
class ClassificationResult:
    predicted_category: str = ""
    confidence: float = 0.0
    all_scores: dict = field(default_factory=dict)


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
class GraphNode:
    id: str = ""
    label: str = ""
    freq: int = 1
    degree: int = 0


@dataclass
class GraphEdge:
    source: str = ""
    target: str = ""
    weight: int = 1


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
    top_nodes_by_betweenness: list = field(default_factory=list)
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


@dataclass
class SearchResult:
    document_id: str = ""
    filename: str = ""
    similarity: float = 0.0
    summary: str = ""
    matched_entity: str = ""
    entity_type: str = ""
    category: str = ""
    confidence: float = 0.0


@dataclass
class Statistics:
    total_documents: int = 0
    total_words: int = 0
    total_pages: int = 0
    category_distribution: dict = field(default_factory=dict)
    entity_type_distribution: dict = field(default_factory=dict)
