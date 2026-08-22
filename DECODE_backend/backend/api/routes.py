"""
DECODE – API Routes
RESTful endpoints for document upload, processing, search, and analytics.
"""

import os
import logging
from pathlib import Path
from flask import Blueprint, request, jsonify, send_from_directory

from services.document_processor import (
    process_document, get_document, list_documents,
    get_analysis, get_graph, delete_document, reanalyze_document
)
from services.file_service import (
    save_uploaded_file, generate_thumbnail, get_image_metadata,
    list_uploaded_files, delete_file, allowed_file
)
from services.search_service import (
    keyword_search, search_by_category, search_by_entity,
    semantic_search, get_statistics
)
from core.ocr_engine import ocr_image, preprocess_image, detect_tables, detect_figures
from core.nlp_engine import (
    run_full_nlp_pipeline, extract_entities, extract_keywords,
    summarize, classify_document, readability_metrics
)
from core.graph_engine import run_graph_pipeline

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger("decode.api")

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"


# ─────────────────────────────────────────────────────────────────────────────
# Health & info
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "DECODE – Document Intelligence API",
        "version": "1.0.0",
    })


@api_bp.route("/info", methods=["GET"])
def info():
    return jsonify({
        "name": "DECODE",
        "description": "Document Extraction, Classification, OCR & Data Engine",
        "capabilities": [
            "OCR (Tesseract + OpenCV preprocessing)",
            "Named Entity Recognition (spaCy)",
            "Keyword Extraction (TF-IDF)",
            "Extractive Summarisation",
            "Document Classification",
            "Knowledge Graph Extraction",
            "Readability Metrics",
            "Semantic Search (sentence-transformers)",
            "Table & Figure Detection",
            "Multi-format support (PDF, DOCX, images)",
        ],
        "endpoints": [
            "POST /api/v1/upload          – Upload & fully process a document",
            "POST /api/v1/ocr             – OCR only (image/PDF)",
            "POST /api/v1/nlp             – NLP only (raw text input)",
            "POST /api/v1/graph           – Knowledge graph from text",
            "GET  /api/v1/documents       – List all documents",
            "GET  /api/v1/documents/<id>  – Get document by ID",
            "GET  /api/v1/analysis/<id>   – Get NLP analysis for document",
            "GET  /api/v1/graph/<id>      – Get graph data for document",
            "DELETE /api/v1/documents/<id> – Delete document",
            "POST /api/v1/reanalyze/<id> – Re-run NLP/Graph",
            "GET  /api/v1/search          – Keyword search",
            "GET  /api/v1/search/semantic – Semantic search",
            "GET  /api/v1/search/entity   – Entity-based search",
            "GET  /api/v1/search/category – Category-based search",
            "GET  /api/v1/stats           – Dashboard statistics",
        ],
    })


# ─────────────────────────────────────────────────────────────────────────────
# Upload & full pipeline
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/upload", methods=["POST"])
def upload_document():
    """
    Upload a document and run the full DECODE pipeline.
    Form fields:
      - file       (required)
      - lang       (optional, default=eng)
      - run_nlp    (optional, default=true)
      - run_graph  (optional, default=true)
      - layout     (optional, spring|kamada_kawai|circular, default=spring)
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed: {file.filename}"}), 400

    lang = request.form.get("lang", "eng")
    run_nlp = request.form.get("run_nlp", "true").lower() == "true"
    run_graph = request.form.get("run_graph", "true").lower() == "true"
    layout = request.form.get("layout", "spring")

    try:
        file_meta = save_uploaded_file(file, file.filename)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Generate thumbnail for image files
    ext = file_meta["extension"]
    if ext in ("png", "jpg", "jpeg", "bmp", "tiff", "gif"):
        generate_thumbnail(file_meta["path"])

    try:
        result = process_document(
            file_path=file_meta["path"],
            original_filename=file.filename,
            ocr_lang=lang,
            run_nlp=run_nlp,
            run_graph=run_graph,
            graph_layout=layout,
        )
    except Exception as e:
        logger.exception("Processing failed")
        return jsonify({"error": str(e)}), 500

    return jsonify(result), 201


# ─────────────────────────────────────────────────────────────────────────────
# OCR only
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/ocr", methods=["POST"])
def ocr_endpoint():
    """
    Run OCR on an uploaded image or PDF.
    Returns extracted text + confidence + tables/figures detected.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    lang = request.form.get("lang", "eng")
    preprocess_flag = request.form.get("preprocess", "true").lower() == "true"

    try:
        file_meta = save_uploaded_file(file, file.filename)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        from core.ocr_engine import extract_text_from_file
        result = extract_text_from_file(file_meta["path"], lang=lang)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# NLP only (accepts raw text)
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/nlp", methods=["POST"])
def nlp_endpoint():
    """
    Run full NLP pipeline on provided text.
    JSON body: {"text": "..."}
    or form field: text=...
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text") or request.form.get("text", "")

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    try:
        result = run_full_nlp_pipeline(text)
        return jsonify(result)
    except Exception as e:
        logger.exception("NLP error")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Individual NLP modules
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/nlp/entities", methods=["POST"])
def entities_endpoint():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or request.form.get("text", "")
    if not text:
        return jsonify({"error": "No text"}), 400
    return jsonify(extract_entities(text))


@api_bp.route("/nlp/keywords", methods=["POST"])
def keywords_endpoint():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or request.form.get("text", "")
    top_n = int(data.get("top_n", 20))
    return jsonify({"keywords": extract_keywords(text, top_n=top_n)})


@api_bp.route("/nlp/summarize", methods=["POST"])
def summarize_endpoint():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or request.form.get("text", "")
    n = int(data.get("sentences", 5))
    return jsonify(summarize(text, num_sentences=n))


@api_bp.route("/nlp/classify", methods=["POST"])
def classify_endpoint():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or request.form.get("text", "")
    return jsonify(classify_document(text))


@api_bp.route("/nlp/readability", methods=["POST"])
def readability_endpoint():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or request.form.get("text", "")
    return jsonify(readability_metrics(text))


# ─────────────────────────────────────────────────────────────────────────────
# Graph only (accepts raw text)
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/graph", methods=["POST"])
def graph_endpoint():
    """
    Extract knowledge graph from text.
    JSON body: {"text": "...", "layout": "spring", "render": true}
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text") or request.form.get("text", "")
    layout = data.get("layout", "spring")
    render = str(data.get("render", "true")).lower() == "true"

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    try:
        result = run_graph_pipeline(text, render=render, layout=layout)
        return jsonify(result)
    except Exception as e:
        logger.exception("Graph error")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Document CRUD
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/documents", methods=["GET"])
def list_docs():
    limit = int(request.args.get("limit", 50))
    docs = list_documents(limit=limit)
    return jsonify({"documents": docs, "count": len(docs)})


@api_bp.route("/documents/<doc_id>", methods=["GET"])
def get_doc(doc_id):
    doc = get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(doc)


@api_bp.route("/documents/<doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    result = delete_document(doc_id)
    return jsonify({"deleted": result, "document_id": doc_id})


@api_bp.route("/analysis/<doc_id>", methods=["GET"])
def get_analysis_route(doc_id):
    data = get_analysis(doc_id)
    if not data:
        return jsonify({"error": "Analysis not found"}), 404
    return jsonify(data)


@api_bp.route("/graph/<doc_id>", methods=["GET"])
def get_graph_route(doc_id):
    data = get_graph(doc_id)
    if not data:
        return jsonify({"error": "Graph not found"}), 404
    return jsonify(data)


@api_bp.route("/reanalyze/<doc_id>", methods=["POST"])
def reanalyze_route(doc_id):
    data = request.get_json(silent=True) or {}
    run_nlp = data.get("run_nlp", True)
    run_graph = data.get("run_graph", True)
    result = reanalyze_document(doc_id, run_nlp=run_nlp, run_graph=run_graph)
    return jsonify(result)


# ─────────────────────────────────────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/search", methods=["GET"])
def search_route():
    q = request.args.get("q", "")
    limit = int(request.args.get("limit", 20))
    if not q:
        return jsonify({"error": "Query parameter 'q' required"}), 400
    results = keyword_search(q, limit=limit)
    return jsonify({"query": q, "results": results, "count": len(results)})


@api_bp.route("/search/semantic", methods=["GET"])
def semantic_search_route():
    q = request.args.get("q", "")
    top_k = int(request.args.get("top_k", 5))
    threshold = float(request.args.get("threshold", 0.3))
    if not q:
        return jsonify({"error": "Query 'q' required"}), 400
    results = semantic_search(q, top_k=top_k, threshold=threshold)
    return jsonify({"query": q, "results": results, "count": len(results)})


@api_bp.route("/search/entity", methods=["GET"])
def entity_search_route():
    entity = request.args.get("entity", "")
    if not entity:
        return jsonify({"error": "Query 'entity' required"}), 400
    results = search_by_entity(entity)
    return jsonify({"entity": entity, "results": results})


@api_bp.route("/search/category", methods=["GET"])
def category_search_route():
    cat = request.args.get("category", "")
    if not cat:
        return jsonify({"error": "Query 'category' required"}), 400
    results = search_by_category(cat)
    return jsonify({"category": cat, "results": results})


# ─────────────────────────────────────────────────────────────────────────────
# Stats & uploaded files
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/stats", methods=["GET"])
def stats_route():
    return jsonify(get_statistics())


@api_bp.route("/files", methods=["GET"])
def list_files_route():
    return jsonify({"files": list_uploaded_files()})


@api_bp.route("/files/<filename>", methods=["DELETE"])
def delete_file_route(filename):
    result = delete_file(filename)
    return jsonify({"deleted": result, "filename": filename})


# ─────────────────────────────────────────────────────────────────────────────
# Image tools (OpenCV)
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/image/preprocess", methods=["POST"])
def preprocess_route():
    """Upload an image and get back the preprocessed version (base64 PNG)."""
    import base64, io
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["file"]
    img_bytes = file.read()
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({"error": "Could not decode image"}), 400

    processed = preprocess_image(img)
    _, buf = cv2.imencode(".png", processed)
    b64 = base64.b64encode(buf.tobytes()).decode()

    return jsonify({"image_base64": b64, "format": "png"})


@api_bp.route("/image/detect-tables", methods=["POST"])
def detect_tables_route():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    img_bytes = file.read()
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    tables = detect_tables(img)
    return jsonify({"tables": tables, "count": len(tables)})


@api_bp.route("/image/detect-figures", methods=["POST"])
def detect_figures_route():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    img_bytes = file.read()
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    figures = detect_figures(img)
    return jsonify({"figures": figures, "count": len(figures)})
