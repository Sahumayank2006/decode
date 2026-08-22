"""
DECODE – Document Processor Service
Orchestrates: file upload → OCR → NLP → Graph → Firestore storage
"""

import os
import uuid
import logging
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.firebase_config import get_db
from core.ocr_engine import extract_text_from_file
from core.nlp_engine import run_full_nlp_pipeline
from core.graph_engine import run_graph_pipeline

logger = logging.getLogger("decode.processor")

COLLECTION_DOCUMENTS = "documents"
COLLECTION_ANALYSIS   = "analysis"
COLLECTION_GRAPHS     = "graphs"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _file_hash(path: str) -> str:
    """SHA-256 of file contents (used for deduplication)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


def _timestamp() -> str:
    return datetime.utcnow().isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Save / retrieve from Firestore
# ─────────────────────────────────────────────────────────────────────────────

def _save_document(doc_data: dict) -> str:
    """Persist document record to Firestore. Returns document ID."""
    db = get_db()
    ref, snap = db.collection(COLLECTION_DOCUMENTS).add(doc_data)
    return ref.id


def _save_analysis(analysis_data: dict) -> str:
    """Persist analysis results. Returns document ID."""
    db = get_db()
    ref, snap = db.collection(COLLECTION_ANALYSIS).add(analysis_data)
    return ref.id


def _save_graph(graph_data: dict) -> str:
    """Persist graph data. Returns document ID."""
    db = get_db()
    ref, snap = db.collection(COLLECTION_GRAPHS).add(graph_data)
    return ref.id


def get_document(doc_id: str) -> Optional[dict]:
    db = get_db()
    snap = db.collection(COLLECTION_DOCUMENTS).document(doc_id).get()
    if snap.exists:
        d = snap.to_dict()
        d["id"] = doc_id
        return d
    return None


def list_documents(limit: int = 50) -> list[dict]:
    db = get_db()
    docs = []
    for snap in db.collection(COLLECTION_DOCUMENTS).stream():
        d = snap.to_dict()
        d["id"] = snap.id
        docs.append(d)
    return docs[:limit]


def get_analysis(doc_id: str) -> Optional[dict]:
    db = get_db()
    results = list(
        db.collection(COLLECTION_ANALYSIS)
          .where("document_id", "==", doc_id)
          .stream()
    )
    if results:
        d = results[-1].to_dict()
        d["id"] = results[-1].id
        return d
    return None


def get_graph(doc_id: str) -> Optional[dict]:
    db = get_db()
    results = list(
        db.collection(COLLECTION_GRAPHS)
          .where("document_id", "==", doc_id)
          .stream()
    )
    if results:
        d = results[-1].to_dict()
        d["id"] = results[-1].id
        return d
    return None


def delete_document(doc_id: str) -> bool:
    db = get_db()
    db.collection(COLLECTION_DOCUMENTS).document(doc_id).delete()
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Core pipeline
# ─────────────────────────────────────────────────────────────────────────────

def process_document(file_path: str,
                     original_filename: str,
                     ocr_lang: str = "eng",
                     run_nlp: bool = True,
                     run_graph: bool = True,
                     graph_layout: str = "spring") -> dict:
    """
    Full DECODE pipeline:
      1. OCR / text extraction
      2. NLP analysis (entities, keywords, summary, classification, readability)
      3. Knowledge graph extraction
      4. Persist to Firestore
      5. Return consolidated result
    """
    doc_id = str(uuid.uuid4())
    logger.info("Processing document %s → id=%s", original_filename, doc_id)

    # ── Step 1: OCR ──────────────────────────────────────────────────────────
    try:
        ocr_result = extract_text_from_file(file_path, lang=ocr_lang)
    except Exception as exc:
        logger.error("OCR failed: %s", exc)
        ocr_result = {"text": "", "error": str(exc)}

    extracted_text = ocr_result.get("text", "")

    # ── Step 2: Store document metadata ──────────────────────────────────────
    file_size = os.path.getsize(file_path)
    doc_record = {
        "id": doc_id,
        "filename": original_filename,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": _mime(file_path),
        "file_hash": _file_hash(file_path),
        "ocr_language": ocr_lang,
        "word_count": ocr_result.get("word_count", 0),
        "char_count": ocr_result.get("char_count", 0),
        "confidence": ocr_result.get("confidence", 0),
        "total_pages": ocr_result.get("total_pages", 1),
        "status": "processed",
        "created_at": _timestamp(),
    }
    _save_document(doc_record)

    # ── Step 3: NLP ───────────────────────────────────────────────────────────
    nlp_result = {}
    if run_nlp and extracted_text.strip():
        try:
            nlp_result = run_full_nlp_pipeline(extracted_text)
        except Exception as exc:
            logger.error("NLP failed: %s", exc)
            nlp_result = {"error": str(exc)}

        analysis_record = {
            "document_id": doc_id,
            "filename": original_filename,
            "nlp_result": nlp_result,
            "created_at": _timestamp(),
        }
        _save_analysis(analysis_record)

    # ── Step 4: Graph ─────────────────────────────────────────────────────────
    graph_result = {}
    if run_graph and extracted_text.strip():
        try:
            graph_result = run_graph_pipeline(extracted_text, render=True, layout=graph_layout)
        except Exception as exc:
            logger.error("Graph extraction failed: %s", exc)
            graph_result = {"error": str(exc)}

        graph_record = {
            "document_id": doc_id,
            "filename": original_filename,
            "graph_data": graph_result.get("graph_data", {}),
            "analytics": graph_result.get("analytics", {}),
            # Don't store the large base64 in Firestore – keep it in response only
            "created_at": _timestamp(),
        }
        _save_graph(graph_record)

    # ── Final consolidated response ───────────────────────────────────────────
    return {
        "document_id": doc_id,
        "filename": original_filename,
        "file_size": file_size,
        "ocr": ocr_result,
        "nlp": nlp_result,
        "graph": graph_result,
        "status": "success",
        "processed_at": _timestamp(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Re-analysis endpoints
# ─────────────────────────────────────────────────────────────────────────────

def reanalyze_document(doc_id: str,
                       run_nlp: bool = True,
                       run_graph: bool = True) -> dict:
    """Re-run NLP and/or graph on an already-stored document."""
    doc = get_document(doc_id)
    if not doc:
        return {"error": f"Document {doc_id} not found"}

    file_path = doc.get("file_path")
    if not file_path or not Path(file_path).exists():
        return {"error": "Original file no longer available for re-analysis"}

    ocr_result = extract_text_from_file(file_path)
    text = ocr_result.get("text", "")

    result = {"document_id": doc_id}
    if run_nlp:
        result["nlp"] = run_full_nlp_pipeline(text)
    if run_graph:
        result["graph"] = run_graph_pipeline(text)

    return result
