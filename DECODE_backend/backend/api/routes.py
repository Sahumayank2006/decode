"""
DECODE – API Routes
RESTful endpoints for:
  • Document upload & DECODE chart pipeline
  • Chart CRUD, reconstruction, compliance scoring
  • Legacy OCR / NLP / Graph endpoints (kept as bonus)
  • Search & stats
"""

import os
import uuid
import logging
import threading
from pathlib import Path
from flask import Blueprint, request, jsonify, send_from_directory, send_file

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
from services.chart_pipeline import (
    run_chart_pipeline, reconstruct_single_chart, rescore_chart,
    get_chart_full, list_charts_for_document, get_processing_events,
    PALETTES,
)
from core.ocr_engine import ocr_image, preprocess_image, detect_tables, detect_figures
from core.nlp_engine import (
    run_full_nlp_pipeline, extract_entities, extract_keywords,
    summarize, classify_document, readability_metrics
)
from core.graph_engine import run_graph_pipeline
from core.chart_reconstructor import render_chart_image, PALETTES as PALETTE_COLORS
from config.firebase_config import get_db

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger("decode.api")

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

BASE_DIR   = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
EXPORT_DIR = BASE_DIR / "static" / "exports"


# ─────────────────────────────────────────────────────────────────────────────
# Health & info
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "DECODE – Chart Intelligence API",
        "version": "2.0.0",
    })


@api_bp.route("/info", methods=["GET"])
def info():
    return jsonify({
        "name": "DECODE",
        "description": "Detection, Extraction, Compliance-verification, Output-generation, Diagram-reconstruction, and Evaluation",
        "capabilities": [
            "PDF chart/graph/table detection (OpenCV)",
            "Chart data extraction (OCR + geometric analysis)",
            "Interactive chart reconstruction (Recharts-compatible)",
            "Copyright compliance scoring (SSIM + color + layout)",
            "Chart type switching (bar/line/pie/heatmap)",
            "SVG/PNG export",
            "LLM-powered recommendations (Gemini / rule-based fallback)",
            "OCR (EasyOCR + OpenCV preprocessing)",
            "NLP analysis (NER, keywords, summary, classification)",
            "Knowledge graph extraction",
        ],
        "endpoints": {
            "documents": [
                "POST   /api/v1/documents/upload         – Upload PDF & start pipeline",
                "GET    /api/v1/documents                 – List all documents",
                "GET    /api/v1/documents/<id>            – Get document details",
                "GET    /api/v1/documents/<id>/status     – Get processing status",
                "GET    /api/v1/documents/<id>/charts     – List charts in document",
                "GET    /api/v1/documents/<id>/events     – Get processing events",
                "DELETE /api/v1/documents/<id>            – Delete document",
            ],
            "charts": [
                "GET    /api/v1/charts/<id>               – Get chart with full data",
                "POST   /api/v1/charts/<id>/reconstruct   – Reconstruct with new type/data",
                "POST   /api/v1/charts/<id>/rescore       – Re-run compliance scoring",
            ],
            "exports": [
                "GET    /api/v1/exports/<chart_id>/png    – Download chart as PNG",
                "GET    /api/v1/exports/<chart_id>/svg    – Download chart as SVG",
            ],
            "palettes": [
                "GET    /api/v1/palettes                  – List available color palettes",
            ],
            "legacy": [
                "POST   /api/v1/ocr        – OCR only",
                "POST   /api/v1/nlp        – NLP pipeline",
                "POST   /api/v1/graph      – Knowledge graph",
            ],
        },
    })


# ═════════════════════════════════════════════════════════════════════════════
# DECODE CHART PIPELINE ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

# ─── Document upload & pipeline ──────────────────────────────────────────────

@api_bp.route("/documents/upload", methods=["POST"])
def upload_and_process():
    """
    Upload a PDF and run the full 6-stage DECODE chart pipeline.
    The pipeline runs in a background thread so this returns immediately.

    Form fields:
      - file (required): PDF file
      - run_pipeline (optional, default=true): whether to auto-run pipeline
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed: {file.filename}"}), 400

    try:
        file_meta = save_uploaded_file(file, file.filename)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Create document record
    doc_id = str(uuid.uuid4())
    db = get_db()
    doc_record = {
        "id": doc_id,
        "filename": file.filename,
        "file_path": file_meta["path"],
        "file_size": file_meta["size"],
        "extension": file_meta["extension"],
        "status": "uploaded",
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
        "updated_at": __import__("datetime").datetime.utcnow().isoformat(),
    }
    db.collection("documents").document(doc_id).set(doc_record)

    run_pipeline = request.form.get("run_pipeline", "true").lower() == "true"

    if run_pipeline and file_meta["extension"] == "pdf":
        # Run pipeline in background thread
        def _run():
            try:
                run_chart_pipeline(doc_id, file_meta["path"])
            except Exception as e:
                logger.exception("Background pipeline failed: %s", e)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

        return jsonify({
            "document_id": doc_id,
            "filename": file.filename,
            "status": "processing",
            "message": "PDF uploaded. Chart pipeline is running in the background.",
        }), 202
    else:
        # Non-PDF or pipeline disabled
        return jsonify({
            "document_id": doc_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "File uploaded. Use POST /documents/<id>/process to start the pipeline.",
        }), 201


@api_bp.route("/documents/<doc_id>/process", methods=["POST"])
def process_doc(doc_id):
    """Manually trigger the chart pipeline for an uploaded document."""
    db = get_db()
    snap = db.collection("documents").document(doc_id).get()
    if not snap.exists:
        return jsonify({"error": "Document not found"}), 404

    doc = snap.to_dict()
    pdf_path = doc.get("file_path")
    if not pdf_path or not Path(pdf_path).exists():
        return jsonify({"error": "PDF file not found on server"}), 404

    def _run():
        try:
            run_chart_pipeline(doc_id, pdf_path)
        except Exception as e:
            logger.exception("Pipeline failed: %s", e)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return jsonify({
        "document_id": doc_id,
        "status": "processing",
        "message": "Pipeline started.",
    }), 202


# ─── Document CRUD ───────────────────────────────────────────────────────────

@api_bp.route("/documents", methods=["GET"])
def list_docs():
    limit = int(request.args.get("limit", 50))
    db = get_db()
    docs = []
    for snap in db.collection("documents").stream():
        d = snap.to_dict()
        d["id"] = snap.id
        docs.append(d)
    docs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jsonify({"documents": docs[:limit], "count": len(docs[:limit])})


@api_bp.route("/documents/<doc_id>", methods=["GET"])
def get_doc(doc_id):
    db = get_db()
    snap = db.collection("documents").document(doc_id).get()
    if not snap.exists:
        return jsonify({"error": "Document not found"}), 404
    d = snap.to_dict() or {}
    d["id"] = doc_id
    return jsonify(d)


@api_bp.route("/documents/<doc_id>/status", methods=["GET"])
def get_doc_status(doc_id):
    """Get document processing status and events."""
    db = get_db()
    snap = db.collection("documents").document(doc_id).get()
    if not snap.exists:
        return jsonify({"error": "Document not found"}), 404

    d = snap.to_dict() or {}
    events = get_processing_events(doc_id)

    return jsonify({
        "document_id": doc_id,
        "status": d.get("status", "unknown"),
        "error_message": d.get("error_message", ""),
        "summary": d.get("summary", {}),
        "events": events,
    })


@api_bp.route("/documents/<doc_id>/charts", methods=["GET"])
def list_doc_charts(doc_id):
    """List all charts detected in a document."""
    charts = list_charts_for_document(doc_id)
    return jsonify({"document_id": doc_id, "charts": charts, "count": len(charts)})


@api_bp.route("/documents/<doc_id>/events", methods=["GET"])
def list_doc_events(doc_id):
    """Get processing timeline events."""
    events = get_processing_events(doc_id)
    return jsonify({"document_id": doc_id, "events": events})


@api_bp.route("/documents/<doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    db = get_db()
    db.collection("documents").document(doc_id).delete()
    # Also clean up related collections
    for col in ["charts", "extractions", "reconstructions", "compliance_scores", "processing_events"]:
        for snap in db.collection(col).where("document_id", "==", doc_id).stream():
            db.collection(col).document(snap.id).delete()
        for snap in db.collection(col).where("chart_id", "==", doc_id).stream():
            db.collection(col).document(snap.id).delete()
    return jsonify({"deleted": True, "document_id": doc_id})


# ─── Chart endpoints ─────────────────────────────────────────────────────────

@api_bp.route("/charts/<chart_id>", methods=["GET"])
def get_chart(chart_id):
    """Get a chart with its extraction, reconstruction, and compliance data."""
    chart = get_chart_full(chart_id)
    if not chart:
        return jsonify({"error": "Chart not found"}), 404
    return jsonify(chart)


@api_bp.route("/charts/<chart_id>/reconstruct", methods=["POST"])
def reconstruct_chart_endpoint(chart_id):
    """
    Reconstruct a chart with a new type or edited data.
    JSON body:
      - chart_type (optional): "bar" | "line" | "pie" | "heatmap"
      - series (optional): edited series data
      - palette (optional): palette name
    """
    data = request.get_json(silent=True) or {}
    new_type = data.get("chart_type")
    edited_series = data.get("series")
    palette = data.get("palette", "default")

    result = reconstruct_single_chart(
        chart_id,
        new_chart_type=new_type,
        edited_series=edited_series,
        palette_name=palette,
    )

    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@api_bp.route("/charts/<chart_id>/rescore", methods=["POST"])
def rescore_chart_endpoint(chart_id):
    """Re-run compliance scoring after user edits."""
    result = rescore_chart(chart_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


# ─── DECODE-VISION Specialist Endpoints ─────────────────────────────────────

@api_bp.route("/charts/<chart_id>/decode-vision", methods=["POST"])
def chart_decode_vision(chart_id):
    """
    Run DECODE-VISION specialist extraction on a specific chart.
    Returns the exact JSON schema defined in the DECODE-VISION specification.
    """
    chart = get_chart_full(chart_id)
    if not chart:
        return jsonify({"error": "Chart not found"}), 404

    # Determine image source
    img_data = None
    if chart.get("original_image_path"):
        local_path = BASE_DIR / chart["original_image_path"].lstrip("/")
        if local_path.exists():
            img_data = str(local_path)
    if not img_data and chart.get("original_image_base64"):
        img_data = chart["original_image_base64"]

    if not img_data:
        return jsonify({"error": "No image data available for this chart."}), 400

    from services.llm_service import get_llm, decode_vision_to_pipeline_format
    llm = get_llm()
    dv_result = llm.extract_with_decode_vision(
        img_data,
        context={"chart_type": chart.get("chart_type", "chart")}
    )

    # Update extraction record in Firestore
    db = get_db()
    extractions = list(db.collection("extractions").where("chart_id", "==", chart_id).stream())
    if extractions:
        ext_doc = extractions[0]
        pipe_format = decode_vision_to_pipeline_format(dv_result)
        db.collection("extractions").document(ext_doc.id).update({
            "decode_vision": dv_result,
            "series": pipe_format["series"],
            "axis_labels": pipe_format["axis_labels"],
            "legend": pipe_format["legend"],
            "title": pipe_format["title"],
        })

    return jsonify({
        "status": "ok",
        "chart_id": chart_id,
        "decode_vision": dv_result
    })


@api_bp.route("/extract/decode-vision", methods=["POST"])
def standalone_decode_vision():
    """
    Direct standalone endpoint for DECODE-VISION chart extraction.
    Accepts:
      - Multipart file upload: 'file' or 'image'
      - JSON body: {"image_base64": "...", "hint": "..."}
    Returns strictly the DECODE-VISION JSON schema object.
    """
    from services.llm_service import get_llm
    llm = get_llm()

    image_data = None
    context = {}

    if "file" in request.files:
        file = request.files["file"]
        image_data = file.read()
    elif "image" in request.files:
        file = request.files["image"]
        image_data = file.read()
    elif request.is_json:
        data = request.get_json(silent=True) or {}
        image_data = data.get("image_base64") or data.get("image")
        if data.get("hint"):
            context["hint"] = data["hint"]

    if not image_data:
        return jsonify({"error": "No image provided. Pass a file or 'image_base64' in JSON."}), 400

    try:
        dv_result = llm.extract_with_decode_vision(image_data, context=context)
        return jsonify(dv_result)
    except Exception as e:
        logger.error("standalone_decode_vision failed: %s", e)
        return jsonify({"error": str(e)}), 500


# ─── Export endpoints ─────────────────────────────────────────────────────────

@api_bp.route("/exports/<chart_id>/png", methods=["GET"])
def export_png(chart_id):
    """Download a chart as PNG."""
    export_path = EXPORT_DIR / chart_id / "chart.png"
    if not export_path.exists():
        # Try to generate on-the-fly
        chart = get_chart_full(chart_id)
        if not chart or not chart.get("extraction"):
            return jsonify({"error": "Chart not found"}), 404
        ext = chart["extraction"]
        rec = chart.get("reconstruction", {})
        img_bytes = render_chart_image(
            series=ext.get("series", []),
            chart_type=rec.get("chart_type", "bar"),
            axis_labels=ext.get("axis_labels", {}),
            title=ext.get("title", ""),
            output_format="png",
        )
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "wb") as f:
            f.write(img_bytes)

    return send_file(
        str(export_path),
        mimetype="image/png",
        as_attachment=True,
        download_name=f"decode_chart_{chart_id[:8]}.png",
    )


@api_bp.route("/exports/<chart_id>/svg", methods=["GET"])
def export_svg(chart_id):
    """Download a chart as SVG."""
    export_path = EXPORT_DIR / chart_id / "chart.svg"
    if not export_path.exists():
        chart = get_chart_full(chart_id)
        if not chart or not chart.get("extraction"):
            return jsonify({"error": "Chart not found"}), 404
        ext = chart["extraction"]
        rec = chart.get("reconstruction", {})
        img_bytes = render_chart_image(
            series=ext.get("series", []),
            chart_type=rec.get("chart_type", "bar"),
            axis_labels=ext.get("axis_labels", {}),
            title=ext.get("title", ""),
            output_format="svg",
        )
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "wb") as f:
            f.write(img_bytes)

    return send_file(
        str(export_path),
        mimetype="image/svg+xml",
        as_attachment=True,
        download_name=f"decode_chart_{chart_id[:8]}.svg",
    )


# ─── Palettes ────────────────────────────────────────────────────────────────

@api_bp.route("/palettes", methods=["GET"])
def list_palettes():
    """Return available color palettes."""
    return jsonify({"palettes": PALETTE_COLORS})


# ═════════════════════════════════════════════════════════════════════════════
# LEGACY ENDPOINTS (kept for backward compatibility + bonus features)
# ═════════════════════════════════════════════════════════════════════════════

# ─── Upload (legacy full pipeline) ───────────────────────────────────────────

@api_bp.route("/upload", methods=["POST"])
def upload_document():
    """Legacy upload endpoint — runs OCR + NLP + Graph pipeline."""
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


# ─── OCR only ────────────────────────────────────────────────────────────────

@api_bp.route("/ocr", methods=["POST"])
def ocr_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    try:
        file_meta = save_uploaded_file(file, file.filename)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    try:
        from core.ocr_engine import extract_text_from_file
        result = extract_text_from_file(file_meta["path"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── NLP endpoints ───────────────────────────────────────────────────────────

@api_bp.route("/nlp", methods=["POST"])
def nlp_endpoint():
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


# ─── Graph ───────────────────────────────────────────────────────────────────

@api_bp.route("/graph", methods=["POST"])
def graph_endpoint():
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


# ─── Search ──────────────────────────────────────────────────────────────────

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


# ─── Stats ───────────────────────────────────────────────────────────────────

@api_bp.route("/stats", methods=["GET"])
def stats_route():
    return jsonify(get_statistics())


# ─── Image tools ─────────────────────────────────────────────────────────────

@api_bp.route("/image/preprocess", methods=["POST"])
def preprocess_route():
    import base64
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


# ============================================================================
# DECODE DEMO / PRODUCT API
# ============================================================================

from core.demo.service import DemoService


_demo_service = DemoService()


@api_bp.route("/demo/health", methods=["GET"])
def demo_health():
    """
    Public frontend health endpoint.
    """
    return jsonify(
        _demo_service.health()
    )


@api_bp.route("/demo/capabilities", methods=["GET"])
def demo_capabilities():
    """
    Returns all visualization capabilities.
    """
    return jsonify(
        _demo_service.capabilities()
    )


@api_bp.route("/demo/product", methods=["GET"])
def demo_product():
    """
    Returns product metadata used by the frontend.
    """
    return jsonify(
        _demo_service.product_info()
    )
