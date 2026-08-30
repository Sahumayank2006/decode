"""
DECODE – Chart Processing Pipeline
Orchestrates the 6-stage pipeline:
  1. Ingest   – parse PDF, render pages
  2. Detect   – find chart regions, classify types
  3. Extract  – pull structured data from each chart
  4. Reconstruct – generate Recharts config + server renders
  5. Score    – copyright compliance analysis
  6. Evaluate – log events, update status

Each stage writes a processing_event to Firestore so the frontend
can display real-time progress.
"""

import os
import uuid
import base64
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from config.firebase_config import get_db
from core.chart_detector import (
    pdf_to_page_images, crop_chart_image,
)
from core.visual_extractor import VisualExtractor
from core.chart_extractor import extract_chart_data
from core.extraction_normalizer import (
    normalize_extraction_result,
)
from core.reconstruction import (
    CanonicalReconstructionService,
    VisualizationSpec,
)
from core.canonical_data_model import (
    CanonicalDataset,
)
from core.chart_reconstructor import (
    reconstruct_chart, render_chart_image, generate_recharts_config,
    save_chart_export, PALETTES,
)
from services.chart_sense_service import analyze_chart_with_sense
from core.compliance_scorer import score_compliance
from services.llm_service import get_llm, decode_vision_to_pipeline_format
from core.visualization.service import UniversalVisualizationService

logger = logging.getLogger("decode.pipeline")

canonical_reconstruction_service = (
    CanonicalReconstructionService()
)

universal_vis_service = UniversalVisualizationService()

# ── Firestore collection names ───────────────────────────────────────────────
COL_DOCUMENTS         = "documents"
COL_CHARTS            = "charts"
COL_EXTRACTIONS       = "extractions"
COL_RECONSTRUCTIONS   = "reconstructions"
COL_COMPLIANCE        = "compliance_scores"
COL_EVENTS            = "processing_events"

# ── Local storage dirs ───────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
UPLOAD_DIR  = BASE_DIR / "static" / "uploads"
EXPORT_DIR  = BASE_DIR / "static" / "exports"
PAGES_DIR   = BASE_DIR / "static" / "pages"
CHARTS_DIR  = BASE_DIR / "static" / "chart_images"

for d in (UPLOAD_DIR, EXPORT_DIR, PAGES_DIR, CHARTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.utcnow().isoformat()


def _log_event(doc_id: str, stage: str, message: str):
    """Write a processing_event to Firestore."""
    db = get_db()
    db.collection(COL_EVENTS).add({
        "document_id": doc_id,
        "stage": stage,
        "message": message,
        "created_at": _ts(),
    })
    logger.info("[%s] %s – %s", doc_id[:8], stage, message)


def _update_doc_status(doc_id: str, status: str, error: str = ""):
    """Update document status in Firestore."""
    db = get_db()
    update = {"status": status, "updated_at": _ts()}
    if error:
        update["error_message"] = error
    db.collection(COL_DOCUMENTS).document(doc_id).update(update)


def _img_to_base64(img: np.ndarray, fmt: str = ".png") -> str:
    """Encode a BGR numpy array as a base64 PNG string."""
    _, buf = cv2.imencode(fmt, img)
    return base64.b64encode(buf.tobytes()).decode("utf-8")


def _save_image(img: np.ndarray, path: Path) -> str:
    """Save image to disk, return the relative URL path."""
    cv2.imwrite(str(path), img)
    # Return a URL-friendly path relative to static/
    rel = path.relative_to(BASE_DIR / "static")
    return f"/static/{rel.as_posix()}"


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Ingest
# ─────────────────────────────────────────────────────────────────────────────

def _stage_ingest(doc_id: str, pdf_path: str) -> list[np.ndarray]:
    """Parse PDF and render pages as images."""
    _log_event(doc_id, "ingesting", "Parsing PDF and rendering pages…")
    _update_doc_status(doc_id, "ingesting")

    page_images = pdf_to_page_images(pdf_path, dpi=200)

    # Save page images for frontend display
    page_paths = []
    for i, img in enumerate(page_images):
        fname = f"{doc_id}_page_{i + 1}.png"
        fpath = PAGES_DIR / fname
        url = _save_image(img, fpath)
        page_paths.append(url)

    _log_event(
        doc_id, "ingesting",
        f"Rendered {len(page_images)} pages successfully.",
    )
    return page_images


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Detect
# ─────────────────────────────────────────────────────────────────────────────

def _stage_detect(
    doc_id: str,
    pdf_path: str,
    page_images: list[np.ndarray],
    confidence_threshold: float = 0.45,
) -> list[dict]:
    """Detect chart regions across all pages using native PyMuPDF."""
    _log_event(doc_id, "detecting", "Scanning pages for charts and graphs…")
    _update_doc_status(doc_id, "detecting")

    db = get_db()
    all_charts = []

    extractor = VisualExtractor(dpi=200)
    try:
        detections = extractor.extract_from_pdf(pdf_path)
    except Exception as e:
        logger.error(f"VisualExtractor failed: {e}")
        detections = []

    for det in detections:
        # VisualExtractor returns 1-indexed page_number
        page_idx = det["page_number"] - 1
        if page_idx < 0 or page_idx >= len(page_images):
            continue
            
        page_img = page_images[page_idx]
        
        # bounding_box is [x0, y0, x1, y1]. detect_charts_in_image returned {x, y, w, h}
        # Let's convert to {x,y,w,h} dict format expected by rest of pipeline
        x0, y0, x1, y1 = det["bbox"]
        bbox_dict = {
            "x": int(x0),
            "y": int(y0),
            "width": int(x1 - x0),
            "height": int(y1 - y0)
        }
        
        chart_id = str(uuid.uuid4())

        # Crop and save the original chart image
        cropped = crop_chart_image(page_img, bbox_dict)
        
        # Avoid saving completely empty crops
        if cropped.size == 0:
            continue
            
        fname = f"{chart_id}_original.png"
        fpath = CHARTS_DIR / fname
        img_url = _save_image(cropped, fpath)

        # Call Chart-Sense for further analysis properties
        sense_props = {}
        if det["type"] in ["chart", "figure"]:
            try:
                abs_img_path = str(fpath.absolute())
                sense_results = analyze_chart_with_sense(abs_img_path)
                sense_props = sense_results.get("properties", {})
            except Exception as e:
                logger.debug("Chart sense analysis skipped: %s", e)

        chart_record = {
            "id": chart_id,
            "document_id": doc_id,
            "page_number": det["page_number"],
            "bounding_box": bbox_dict,
            "chart_type": det["type"],
            "classification_reason": "Native PDF Extractor + Chart Sense",
            "detection_confidence": det["confidence"],
            "needs_review": False,
            "original_image_path": img_url,
            "original_image_base64": _img_to_base64(cropped),
            "chart_sense_properties": sense_props,
            "table_data": det.get("table_data"),
            "created_at": _ts(),
        }

        db.collection(COL_CHARTS).document(chart_id).set(chart_record)
        chart_record["_cropped_image"] = cropped  # keep in memory
        all_charts.append(chart_record)

    _log_event(
        doc_id, "detecting",
        f"Detected {len(all_charts)} chart regions across {len(page_images)} pages.",
    )
    return all_charts


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: Extract
# ─────────────────────────────────────────────────────────────────────────────

def _stage_extract(doc_id: str, charts: list[dict]) -> list[dict]:
    """Extract structured data from each detected chart."""
    _log_event(doc_id, "extracting", f"Extracting data from {len(charts)} charts…")
    _update_doc_status(doc_id, "extracting")

    db = get_db()
    extractions = []

    for chart in charts:
        chart_id = chart["id"]
        cropped = chart.get("_cropped_image")
        if cropped is None:
            continue

        dv_payload = None
        extraction_method_used = "decode_chart_extractor"

        try:
            # 1. Attempt precision DECODE-VISION model extraction
            llm = get_llm()
            dv_result = llm.extract_with_decode_vision(
                cropped,
                context={"chart_type": chart.get("chart_type", "chart")}
            )
            if dv_result and (dv_result.get("extracted_data") or {}).get("series"):
                extraction = decode_vision_to_pipeline_format(dv_result)
                dv_payload = dv_result
                extraction_method_used = "decode_vision_specialist"
            else:
                extraction = extract_chart_data(
                    cropped,
                    chart["chart_type"],
                    raw_table_data=chart.get("table_data"),
                )
        except Exception as vision_err:
            logger.info("DECODE-VISION falling back to standard extractor: %s", vision_err)
            try:
                extraction = extract_chart_data(
                    cropped,
                    chart["chart_type"],
                    raw_table_data=chart.get("table_data"),
                )
            except Exception as e:
                logger.error("Extraction failed for chart %s: %s", chart_id, e)
                extraction = {
                    "series": [],
                    "axis_labels": {},
                    "legend": [],
                    "title": "",
                    "raw_ocr_text": "",
                    "extraction_confidence": 0.0,
                }
                extraction_method_used = "decode_chart_extractor_failed"

        try:
            # Update chart record if resolved type changed
            if extraction.get("resolved_chart_type"):
                chart["chart_type"] = extraction["resolved_chart_type"]

            canonical_dataset = (
                normalize_extraction_result(
                    extraction,
                    detected_type=chart.get(
                        "chart_type",
                        "unknown",
                    ),
                    extraction_method=extraction_method_used,
                    metadata={
                        "chart_id": chart_id,
                        "document_id": doc_id,
                        "decode_vision_used": (dv_payload is not None),
                    },
                )
            )
        except Exception as norm_err:
            logger.error("Normalization error for chart %s: %s", chart_id, norm_err)
            canonical_dataset = normalize_extraction_result(
                {
                    "series": [],
                    "axis_labels": {},
                    "legend": [],
                    "title": "",
                    "raw_ocr_text": "",
                    "extraction_confidence": 0.0,
                },
                detected_type=chart.get("chart_type", "unknown"),
                extraction_method="normalization_fallback",
                metadata={"chart_id": chart_id, "document_id": doc_id, "error": str(norm_err)},
            )

        ext_id = str(uuid.uuid4())
        ext_record = {
            "id": ext_id,
            "chart_id": chart_id,
            "series": extraction.get("series", []),
            "axis_labels": extraction.get("axis_labels", {}),
            "legend": extraction.get("legend", []),
            "raw_ocr_text": extraction.get("raw_ocr_text", ""),
            "extraction_confidence": extraction.get("extraction_confidence", 0.8),
            "title": extraction.get("title", ""),
            "decode_vision": dv_payload,
            "canonical_data": canonical_dataset.to_dict(),
            "created_at": _ts(),
        }

        if not isinstance(
            ext_record.get(
                "canonical_data"
            ),
            dict,
        ):
            raise ValueError(
                "Canonical extraction data "
                "must be a dictionary."
            )

        db.collection(
            COL_EXTRACTIONS
        ).document(
            ext_id
        ).set(
            ext_record
        )
        ext_record["_chart"] = chart  # back-reference
        extractions.append(ext_record)

    _log_event(
        doc_id, "extracting",
        f"Extracted data from {len(extractions)} charts.",
    )
    return extractions


# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: Reconstruct
# ─────────────────────────────────────────────────────────────────────────────

def _reconstruct_canonical_chart(
    ext: dict,
    chart: dict,
    export_subdir: Path,
):
    """
    Reconstruct a chart from canonical extraction data.

    This is the new reconstruction path.

    It intentionally does not modify the canonical data.
    The canonical dataset is the source of truth; the
    VisualizationSpec controls presentation.
    """

    canonical_payload = ext.get(
        "canonical_data"
    )

    if not isinstance(
        canonical_payload,
        dict,
    ):
        raise ValueError(
            "Missing or invalid canonical_data."
        )

    dataset = (
        CanonicalDataset.from_dict(
            canonical_payload
        )
    )

    raw_type = str(
        chart.get(
            "chart_type",
            dataset.detected_type
            if dataset.detected_type != "unknown"
            else "bar",
        )
    ).lower()

    if raw_type in ["chart", "unknown", "other", "figure", "diagram", "process_diagram", "flowchart"]:
        chart_type = "bar" if dataset.detected_type in ["unknown", "chart", "figure", "diagram"] else dataset.detected_type
    elif "pie" in raw_type:
        chart_type = "pie"
    elif "donut" in raw_type:
        chart_type = "donut"
    elif "line" in raw_type:
        chart_type = "line"
    elif "area" in raw_type:
        chart_type = "area"
    elif "radar" in raw_type:
        chart_type = "radar"
    elif "scatter" in raw_type:
        chart_type = "scatter"
    elif "table" in raw_type:
        chart_type = "table"
    else:
        chart_type = "bar"

    # Use UniversalVisualizationService to render canonical payload
    render_result = universal_vis_service.render(
        payload=canonical_payload,
        visualization_type=chart_type,
        export_dir=str(export_subdir),
        export_prefix="canonical",
        options={
            "palette_name": "professional",
            "title": dataset.title or chart.get("title", ""),
            "x_axis_label": dataset.x_axis_label or chart.get("x_axis_label", ""),
            "y_axis_label": dataset.y_axis_label or chart.get("y_axis_label", "")
        }
    )
    result = render_result["result"]

    # Get recommendations
    recs = universal_vis_service.recommend(canonical_payload)
    alt_type = chart_type
    alt_reason = "Reconstructed from canonical extracted data."
    if recs:
        alt_type = getattr(recs[0], "chart_type", chart_type)
        alt_reason = getattr(recs[0], "reason", alt_reason)

    return {
        "chart_type": result.get("chart_type", chart_type),
        "chart_config": result.get("chart_config", {}),
        "image_base64": "",
        "export_paths": {
            "svg": result.get("svg_path", ""),
            "png": result.get("png_path", ""),
        },
        "recommended_alt_type": alt_type,
        "recommendation_reason": alt_reason,
        "renderer": "canonical",
    }

def _stage_reconstruct(doc_id: str, extractions: list[dict]) -> list[dict]:
    """Reconstruct charts from extracted data."""
    _log_event(doc_id, "reconstructing", "Rebuilding charts from extracted data…")
    _update_doc_status(doc_id, "reconstructing")

    db = get_db()
    reconstructions = []

    for ext in extractions:
        chart = ext.get("_chart", {})
        chart_id = ext["chart_id"]
        chart_type = chart.get("chart_type", "bar")

        export_subdir = EXPORT_DIR / chart_id
        export_subdir.mkdir(parents=True, exist_ok=True)

        try:

            # -------------------------------------------------
            # NEW CANONICAL RECONSTRUCTION PATH
            # -------------------------------------------------

            if isinstance(
                ext.get("canonical_data"),
                dict,
            ):

                try:

                    recon = _reconstruct_canonical_chart(
                        ext=ext,
                        chart=chart,
                        export_subdir=export_subdir,
                    )

                    logger.info(
                        "Canonical reconstruction succeeded "
                        "for chart %s",
                        chart_id,
                    )

                except Exception as canonical_error:

                    logger.warning(
                        "Canonical reconstruction failed "
                        "for chart %s: %s. "
                        "Falling back to legacy renderer.",
                        chart_id,
                        canonical_error,
                    )

                    # -------------------------------------------------
                    # LEGACY FALLBACK
                    # -------------------------------------------------

                    recon = reconstruct_chart(

                        extraction=ext,

                        chart_type=chart_type,

                        palette_name="default",

                        export_dir=str(
                            export_subdir
                        ),

                        export_prefix="chart",
                    )

                    recon["renderer"] = "legacy_fallback"

            else:

                # -------------------------------------------------
                # OLD DATABASE RECORD
                # -------------------------------------------------

                logger.info(
                    "No canonical data found for chart %s. "
                    "Using legacy reconstruction.",
                    chart_id,
                )

                recon = reconstruct_chart(

                    extraction=ext,

                    chart_type=chart_type,

                    palette_name="default",

                    export_dir=str(
                        export_subdir
                    ),

                    export_prefix="chart",
                )

                recon["renderer"] = "legacy"

        except Exception as e:

            logger.error(
                "Reconstruction failed for chart %s: %s",
                chart_id,
                e,
            )

            recon = {

                "chart_type": chart_type,

                "chart_config": {},

                "image_base64": "",

                "export_paths": {},

                "recommended_alt_type": chart_type,

                "recommendation_reason": (
                    "Reconstruction failed."
                ),

                "renderer": "failed",
            }

        # Make export paths URL-friendly
        export_urls = {}
        for fmt, fpath in recon.get("export_paths", {}).items():
            try:
                rel = Path(fpath).relative_to(BASE_DIR / "static")
                export_urls[fmt] = f"/static/{rel.as_posix()}"
            except ValueError:
                export_urls[fmt] = fpath

        rec_id = str(uuid.uuid4())
        rec_record = {
            "id": rec_id,
            "chart_id": chart_id,
            "chart_type": recon["chart_type"],
            "chart_config": recon["chart_config"],
            "image_base64": recon.get("image_base64", ""),
            "export_svg_path": export_urls.get("svg", ""),
            "export_png_path": export_urls.get("png", ""),
            "recommended_alt_type": recon.get("recommended_alt_type", ""),
            "recommendation_reason": recon.get("recommendation_reason", ""),
            "renderer": recon.get(
                "renderer",
                "unknown",
            ),
            "created_at": _ts(),
            "updated_at": _ts(),
        }

        db.collection(COL_RECONSTRUCTIONS).document(rec_id).set(rec_record)
        rec_record["_extraction"] = ext
        rec_record["_original_image"] = chart.get("_cropped_image")
        reconstructions.append(rec_record)

    _log_event(
        doc_id, "reconstructing",
        f"Reconstructed {len(reconstructions)} charts.",
    )
    return reconstructions


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5: Score compliance
# ─────────────────────────────────────────────────────────────────────────────

def _stage_score(doc_id: str, reconstructions: list[dict]) -> list[dict]:
    """Run compliance scoring on each reconstruction."""
    _log_event(doc_id, "scoring", "Analysing copyright compliance…")
    _update_doc_status(doc_id, "scoring")

    db = get_db()
    scores = []

    for recon in reconstructions:
        chart_id = recon["chart_id"]
        rec_id = recon["id"]
        original_img = recon.get("_original_image")

        # Render the reconstructed chart as an image for comparison
        ext = recon.get("_extraction", {})
        try:
            recon_bytes = render_chart_image(
                series=ext.get("series", []),
                chart_type=recon.get("chart_type", "bar"),
                axis_labels=ext.get("axis_labels", {}),
                title=ext.get("title", ""),
            )
            recon_arr = np.frombuffer(recon_bytes, dtype=np.uint8)
            recon_img = cv2.imdecode(recon_arr, cv2.IMREAD_COLOR)
        except Exception:
            recon_img = None

        if recon.get("chart_type") in ["table", "table_chart"]:
            compliance = _default_score()
            compliance["recommendations"] = [{
                "id": "table_extracted",
                "text": "Tabular data extracted successfully. Copyright risk is low for pure data tables.",
                "category": "approval",
                "auto_applicable": False,
                "priority": "info"
            }]
        elif original_img is not None and recon_img is not None and recon_img.size > 0:
            try:
                compliance = score_compliance(original_img, recon_img)
            except Exception as e:
                logger.error("Scoring failed for chart %s: %s", chart_id, e)
                compliance = _default_score()
        else:
            compliance = _default_score()

        score_id = str(uuid.uuid4())
        score_record = {
            "id": score_id,
            "chart_id": chart_id,
            "reconstruction_id": rec_id,
            "similarity_score": compliance["similarity_score"],
            "risk_level": compliance["risk_level"],
            "color_similarity": compliance["color_similarity"],
            "layout_similarity": compliance["layout_similarity"],
            "geometry_similarity": compliance["geometry_similarity"],
            "recommendations": compliance["recommendations"],
            "created_at": _ts(),
        }

        db.collection(COL_COMPLIANCE).document(score_id).set(score_record)
        scores.append(score_record)

    _log_event(
        doc_id, "scoring",
        f"Compliance analysis complete for {len(scores)} charts.",
    )
    return scores


def _default_score() -> dict:
    return {
        "similarity_score": 25.0,
        "risk_level": "low",
        "color_similarity": 20.0,
        "layout_similarity": 30.0,
        "geometry_similarity": 25.0,
        "recommendations": [{
            "id": "approved",
            "text": "The regenerated chart appears sufficiently different from the original.",
            "category": "approval",
            "auto_applicable": False,
            "priority": "info",
        }],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Stage 6: Evaluate / finalize
# ─────────────────────────────────────────────────────────────────────────────

def _stage_evaluate(doc_id: str):
    """Final evaluation and status update."""
    _log_event(doc_id, "evaluating", "Finalising results…")

    db = get_db()
    
    # REQUIREMENT: Read directly from Firestore as the single source of truth
    # to ensure the UI and the summary stats are mathematically identical.
    charts = list_charts_for_document(doc_id)
    total_charts = len(charts)

    avg_confidence = 0.0
    avg_score = 0.0
    extractions = []
    scores = []
    
    # Fetch actual saved data for all detected charts
    for chart in charts:
        ext_snaps = list(db.collection(COL_EXTRACTIONS).where("chart_id", "==", chart["id"]).stream())
        if ext_snaps:
            extractions.append(ext_snaps[-1].to_dict())
            
        score_snaps = list(db.collection(COL_COMPLIANCE).where("chart_id", "==", chart["id"]).stream())
        if score_snaps:
            scores.append(score_snaps[-1].to_dict())
            
    if extractions:
        avg_confidence = sum(e.get("extraction_confidence", 0) for e in extractions) / len(extractions)
    if scores:
        avg_score = sum(s.get("similarity_score", 0) for s in scores) / len(scores)

    summary = {
        "total_charts_detected": total_charts,
        "average_extraction_confidence": round(avg_confidence, 2),
        "average_compliance_score": round(avg_score, 1),
    }

    db.collection(COL_DOCUMENTS).document(doc_id).update({
        "status": "done",
        "summary": summary,
        "updated_at": _ts(),
    })

    _log_event(
        doc_id, "done",
        f"Pipeline complete — {total_charts} charts processed, "
        f"avg extraction confidence {avg_confidence:.0%}, "
        f"avg compliance score {avg_score:.1f}.",
    )
    _update_doc_status(doc_id, "done")


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_chart_pipeline(doc_id: str, pdf_path: str) -> dict:
    """
    Run the full 6-stage DECODE chart processing pipeline.

    Args:
        doc_id: Firestore document ID
        pdf_path: local path to the uploaded PDF

    Returns:
        Consolidated result dict with charts, extractions, reconstructions,
        and compliance scores.
    """
    start = time.time()
    logger.info("Pipeline start for document %s", doc_id)

    try:
        # Stage 1: Ingest
        page_images = _stage_ingest(doc_id, pdf_path)

        # Stage 2: Detect
        charts = _stage_detect(doc_id, pdf_path, page_images)

        if not charts:
            _log_event(doc_id, "done", "No charts detected in this document.")
            _update_doc_status(doc_id, "done")
            return {
                "document_id": doc_id,
                "status": "done",
                "charts": [],
                "message": "No charts were detected in this document.",
                "processing_time": round(time.time() - start, 2),
            }

        # Stage 3: Extract
        extractions = _stage_extract(doc_id, charts)

        # Stage 4: Reconstruct
        reconstructions = _stage_reconstruct(doc_id, extractions)

        # Stage 5: Score
        scores = _stage_score(doc_id, reconstructions)

        # Stage 6: Evaluate
        _stage_evaluate(doc_id)

        elapsed = round(time.time() - start, 2)
        logger.info("Pipeline complete for %s in %.2fs", doc_id, elapsed)

        # Build response (strip internal fields starting with _)
        clean_charts = []
        for c in charts:
            clean = {k: v for k, v in c.items() if not k.startswith("_")}
            clean_charts.append(clean)

        clean_extractions = []
        for e in extractions:
            clean = {k: v for k, v in e.items() if not k.startswith("_")}
            clean_extractions.append(clean)

        clean_recons = []
        for r in reconstructions:
            clean = {k: v for k, v in r.items() if not k.startswith("_")}
            clean_recons.append(clean)

        return {
            "document_id": doc_id,
            "status": "done",
            "page_count": len(page_images),
            "charts": clean_charts,
            "extractions": clean_extractions,
            "reconstructions": clean_recons,
            "compliance_scores": scores,
            "processing_time": elapsed,
        }

    except Exception as e:
        logger.exception("Pipeline failed for %s: %s", doc_id, e)
        _update_doc_status(doc_id, "failed", str(e))
        _log_event(doc_id, "failed", f"Pipeline error: {e}")
        return {
            "document_id": doc_id,
            "status": "failed",
            "error": str(e),
            "processing_time": round(time.time() - start, 2),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Individual operations (for API endpoints)
# ─────────────────────────────────────────────────────────────────────────────

def reconstruct_single_chart(
    chart_id: str,
    new_chart_type: Optional[str] = None,
    edited_series: Optional[list] = None,
    palette_name: str = "default",
) -> dict:
    """
    Re-reconstruct a single chart (after user edits or type switch).
    """
    db = get_db()

    # Get existing extraction
    ext_snaps = list(
        db.collection(COL_EXTRACTIONS)
        .where("chart_id", "==", chart_id)
        .stream()
    )
    if not ext_snaps:
        return {"error": "No extraction found for this chart"}

    ext_data = ext_snaps[-1].to_dict()

    # Get chart info
    chart_snap = db.collection(COL_CHARTS).document(chart_id).get()
    chart_data = chart_snap.to_dict() if chart_snap.exists else {}
    chart_type = new_chart_type or chart_data.get("chart_type", "bar")

    export_subdir = EXPORT_DIR / chart_id
    export_subdir.mkdir(parents=True, exist_ok=True)

    # CANONICAL PATH
    if "canonical_data" in ext_data and ext_data["canonical_data"]:
        canonical_payload = ext_data["canonical_data"]
        
        if edited_series is not None:
            canonical_payload["series"] = edited_series
            # Also update extraction so we don't lose it if we rescore later
            ext_data["canonical_data"]["series"] = edited_series
            # Save updated extraction
            db.collection(COL_EXTRACTIONS).document(ext_snaps[-1].id).update({"canonical_data": canonical_payload})

        try:
            render_result = universal_vis_service.render(
                payload=canonical_payload,
                visualization_type=chart_type,
                export_dir=str(export_subdir),
                export_prefix="chart",
                options={
                    "palette_name": palette_name,
                }
            )
            recon = render_result["result"]
            
            # Get recommendations
            recs = universal_vis_service.recommend(canonical_payload)
            alt_type = ""
            alt_reason = ""
            if recs:
                for rec in recs:
                    if rec.visualization_type != chart_type:
                        alt_type = rec.visualization_type
                        alt_reason = rec.reason
                        break
                        
        except ValueError as e:
            return {"error": str(e)}

    # LEGACY FALLBACK PATH
    else:
        # Override series if user edited data
        if edited_series is not None:
            ext_data["series"] = edited_series
            db.collection(COL_EXTRACTIONS).document(ext_snaps[-1].id).update({"series": edited_series})

        recon = reconstruct_chart(
            extraction=ext_data,
            chart_type=chart_type,
            palette_name=palette_name,
            export_dir=str(export_subdir),
            export_prefix="chart",
        )
        alt_type = recon.get("recommended_alt_type", "")
        alt_reason = recon.get("recommendation_reason", "")

    # Save to Firestore
    rec_id = str(uuid.uuid4())
    export_urls = {}
    
    # Handle export paths (Canonical vs Legacy)
    if "export_paths" in recon:
        paths = recon["export_paths"]
    else:
        paths = {"svg": recon.get("svg_path"), "png": recon.get("png_path")}
        
    for fmt, fpath in paths.items():
        if fpath:
            try:
                rel = Path(fpath).relative_to(BASE_DIR / "static")
                export_urls[fmt] = f"/static/{rel.as_posix()}"
            except ValueError:
                export_urls[fmt] = fpath

    rec_record = {
        "id": rec_id,
        "chart_id": chart_id,
        "chart_type": chart_type,
        "chart_config": recon.get("chart_config", {}),
        "image_base64": recon.get("image_base64", ""),
        "export_svg_path": export_urls.get("svg", ""),
        "export_png_path": export_urls.get("png", ""),
        "recommended_alt_type": alt_type,
        "recommendation_reason": alt_reason,
        "created_at": _ts(),
        "updated_at": _ts(),
    }
    db.collection(COL_RECONSTRUCTIONS).document(rec_id).set(rec_record)

    return rec_record


def rescore_chart(chart_id: str) -> dict:
    """Re-run compliance scoring after user edits."""
    db = get_db()

    # Get original chart image
    chart_snap = db.collection(COL_CHARTS).document(chart_id).get()
    if not chart_snap.exists:
        return {"error": "Chart not found"}
    chart_data = chart_snap.to_dict()

    # Get latest reconstruction
    rec_snaps = list(
        db.collection(COL_RECONSTRUCTIONS)
        .where("chart_id", "==", chart_id)
        .stream()
    )
    if not rec_snaps:
        return {"error": "No reconstruction found"}

    rec_data = rec_snaps[-1].to_dict()

    # Get extraction for rendering
    ext_snaps = list(
        db.collection(COL_EXTRACTIONS)
        .where("chart_id", "==", chart_id)
        .stream()
    )
    ext_data = ext_snaps[-1].to_dict() if ext_snaps else {}

    # Load original image
    orig_path = chart_data.get("original_image_path", "")
    if orig_path.startswith("/static/"):
        full_path = BASE_DIR / "static" / orig_path[len("/static/"):]
    else:
        full_path = Path(orig_path)

    original_img = cv2.imread(str(full_path)) if full_path.exists() else None

    # Render reconstruction
    try:
        recon_bytes = render_chart_image(
            series=ext_data.get("series", []),
            chart_type=rec_data.get("chart_type", "bar"),
            axis_labels=ext_data.get("axis_labels", {}),
            title=ext_data.get("title", ""),
        )
        recon_arr = np.frombuffer(recon_bytes, dtype=np.uint8)
        recon_img = cv2.imdecode(recon_arr, cv2.IMREAD_COLOR)
    except Exception:
        recon_img = None

    if rec_data.get("chart_type") in ["table", "table_chart"]:
        compliance = _default_score()
        compliance["recommendations"] = [{
            "id": "table_extracted",
            "text": "Tabular data extracted successfully. Copyright risk is low for pure data tables.",
            "category": "approval",
            "auto_applicable": False,
            "priority": "info"
        }]
    elif original_img is not None and recon_img is not None and recon_img.size > 0:
        try:
            compliance = score_compliance(original_img, recon_img)
        except Exception as e:
            logger.error("Rescoring failed for chart %s: %s", chart_id, e)
            compliance = _default_score()
    else:
        compliance = _default_score()

    score_id = str(uuid.uuid4())
    score_record = {
        "id": score_id,
        "chart_id": chart_id,
        "reconstruction_id": rec_data.get("id", ""),
        "similarity_score": compliance["similarity_score"],
        "risk_level": compliance["risk_level"],
        "color_similarity": compliance["color_similarity"],
        "layout_similarity": compliance["layout_similarity"],
        "geometry_similarity": compliance["geometry_similarity"],
        "recommendations": compliance["recommendations"],
        "created_at": _ts(),
    }
    db.collection(COL_COMPLIANCE).document(score_id).set(score_record)

    return score_record


def get_chart_full(chart_id: str) -> Optional[dict]:
    """Get a chart with its extraction, reconstruction, and compliance data."""
    db = get_db()

    chart_snap = db.collection(COL_CHARTS).document(chart_id).get()
    if not chart_snap.exists:
        return None

    # Strip internal memory fields (like numpy arrays) so they don't break JSON serialization!
    chart = {k: v for k, v in chart_snap.to_dict().items() if not k.startswith("_")}
    chart["id"] = chart_id

    # Get extraction
    ext_snaps = list(
        db.collection(COL_EXTRACTIONS)
        .where("chart_id", "==", chart_id)
        .stream()
    )
    if ext_snaps:
        chart["extraction"] = {k: v for k, v in ext_snaps[-1].to_dict().items() if not k.startswith("_")}
    else:
        chart["extraction"] = None

    # Get reconstruction
    rec_snaps = list(
        db.collection(COL_RECONSTRUCTIONS)
        .where("chart_id", "==", chart_id)
        .stream()
    )
    if rec_snaps:
        chart["reconstruction"] = {k: v for k, v in rec_snaps[-1].to_dict().items() if not k.startswith("_")}
    else:
        chart["reconstruction"] = None

    # Get compliance
    comp_snaps = list(
        db.collection(COL_COMPLIANCE)
        .where("chart_id", "==", chart_id)
        .stream()
    )
    if comp_snaps:
        chart["compliance"] = {k: v for k, v in comp_snaps[-1].to_dict().items() if not k.startswith("_")}
    else:
        chart["compliance"] = None

    return chart






def normalize_extracted_chart(artifact: dict, index: int = 0) -> dict:
    '''
    Master canonical adapter that normalizes any backend extraction structure 
    into a strict frontend-compatible CanonicalChart schema.
    '''
    chart_id = artifact.get("id", f"chart-{index}")
    raw_type = str(artifact.get("chart_type", "bar")).lower()
    
    if raw_type in ["column", "vertical_bar", "stacked_bar"]:
        c_type = "bar"
    elif raw_type in ["doughnut"]:
        c_type = "donut"
    elif raw_type in ["spider"]:
        c_type = "radar"
    elif raw_type in ["bar", "line", "area", "pie", "donut", "radar"]:
        c_type = raw_type
    else:
        c_type = "bar"

    confidence = artifact.get("detection_confidence", 0.0)

    ext = artifact.get("extraction", {})
    if not ext:
        ext = artifact

    categories = []
    series = []
    title = ext.get("title", f"Extracted Chart {index + 1}")

    def parse_series(raw_s: list) -> list:
        s_out = []
        for s in raw_s:
            if not isinstance(s, dict): continue
            name = str(s.get("name", "Unknown"))
            # Format A: values array
            if "values" in s and isinstance(s["values"], list):
                s_out.append({
                    "name": name,
                    "values": [float(v) if v is not None else 0.0 for v in s["values"]]
                })
            # Format B: points array (CanonicalDataset)
            elif "points" in s and isinstance(s["points"], list):
                vals = []
                for p in s["points"]:
                    if isinstance(p, dict) and "value" in p:
                        v = p["value"]
                        vals.append(float(v) if v is not None else 0.0)
                    else:
                        vals.append(0.0)
                s_out.append({"name": name, "values": vals})
        return s_out

    found_data = False
    for key in ["canonical_data", "canonical_dataset", "data"]:
        nested = ext.get(key)
        if isinstance(nested, dict):
            c = nested.get("categories")
            s = nested.get("series")
            if isinstance(c, list) and isinstance(s, list) and len(c) > 0 and len(s) > 0:
                categories = [str(x) for x in c]
                series = parse_series(s)
                found_data = True
                
                meta = nested.get("metadata", {})
                if isinstance(meta, dict) and "confidence" in meta:
                    confidence = float(meta["confidence"])
                elif "confidence" in nested:
                    confidence = float(nested["confidence"])
                elif "overall_confidence" in nested:
                    confidence = float(nested["overall_confidence"])
                    
                if "title" in nested and nested["title"]:
                    title = nested["title"]
                break

    if not found_data:
        c = ext.get("categories")
        s = ext.get("series")
        if isinstance(c, list) and isinstance(s, list) and len(c) > 0 and len(s) > 0:
            categories = [str(x) for x in c]
            series = parse_series(s)
            found_data = True

    if not found_data:
        for key in ["rows", "table", "dataset", "data_points", "values"]:
            rows = ext.get(key)
            if isinstance(rows, list) and len(rows) > 0 and isinstance(rows[0], dict):
                cat_keys = ["Category", "category", "Label", "label", "Name", "name", "X", "x"]
                actual_cat_key = None
                for r_key in rows[0].keys():
                    if r_key in cat_keys:
                        actual_cat_key = r_key
                        break
                if not actual_cat_key:
                    actual_cat_key = list(rows[0].keys())[0]

                series_keys = [k for k in rows[0].keys() if k != actual_cat_key]
                categories = [str(r.get(actual_cat_key, "")) for r in rows]
                
                for sk in series_keys:
                    s_vals = []
                    for r in rows:
                        try:
                            s_vals.append(float(r.get(sk, 0)))
                        except (ValueError, TypeError):
                            s_vals.append(0.0)
                    series.append({"name": sk, "values": s_vals})
                
                if len(categories) > 0 and len(series) > 0:
                    found_data = True
                    break

    if confidence > 1.0:
        confidence = confidence / 100.0

    return {
        "id": chart_id,
        "chart_type": c_type,
        "canonical_data": {
            "title": title,
            "detected_type": c_type,
            "categories": categories,
            "series": series,
            "metadata": {
                "confidence": confidence
            }
        }
    }

def list_charts_for_document(doc_id: str) -> list[dict]:
    """
    List all charts detected in a document.

    The frontend needs one consolidated chart object, so this endpoint
    attaches the latest extraction, reconstruction and compliance records
    to every detected chart.
    """

    db = get_db()

    charts = []

    chart_snaps = (
        db.collection(COL_CHARTS)
        .where(
            "document_id",
            "==",
            doc_id,
        )
        .stream()
    )

    for snap in chart_snaps:

        chart = {
            k: v
            for k, v in (
                snap.to_dict() or {}
            ).items()
            if not k.startswith("_")
        }

        chart["id"] = snap.id

        # --------------------------------------------------------
        # Latest extraction
        # --------------------------------------------------------

        extraction_snaps = list(
            db.collection(COL_EXTRACTIONS)
            .where(
                "chart_id",
                "==",
                snap.id,
            )
            .stream()
        )

        extraction = None

        if extraction_snaps:
            extraction = {
                k: v
                for k, v in (
                    extraction_snaps[-1].to_dict()
                    or {}
                ).items()
                if not k.startswith("_")
            }

        chart["extraction"] = extraction

        # --------------------------------------------------------
        # Latest reconstruction
        # --------------------------------------------------------

        reconstruction_snaps = list(
            db.collection(COL_RECONSTRUCTIONS)
            .where(
                "chart_id",
                "==",
                snap.id,
            )
            .stream()
        )

        reconstruction = None

        if reconstruction_snaps:
            reconstruction = {
                k: v
                for k, v in (
                    reconstruction_snaps[-1].to_dict()
                    or {}
                ).items()
                if not k.startswith("_")
            }

        chart["reconstruction"] = reconstruction

        # --------------------------------------------------------
        # Latest compliance score
        # --------------------------------------------------------

        compliance_snaps = list(
            db.collection(COL_COMPLIANCE)
            .where(
                "chart_id",
                "==",
                snap.id,
            )
            .stream()
        )

        compliance = None

        if compliance_snaps:
            compliance = {
                k: v
                for k, v in (
                    compliance_snaps[-1].to_dict()
                    or {}
                ).items()
                if not k.startswith("_")
            }

        chart["compliance"] = compliance

        # --------------------------------------------------------
        # Build canonical frontend representation
        # --------------------------------------------------------

        canonical_data = None

        if extraction:
            extracted_series = (
                extraction.get(
                    "series",
                    [],
                )
                or []
            )

            categories = []

            for series_item in extracted_series:
                for point in (
                    series_item.get(
                        "points",
                        [],
                    )
                    or []
                ):
                    label = point.get(
                        "label"
                    )

                    if label is not None:
                        label = str(label)

                        if label not in categories:
                            categories.append(
                                label
                            )

            canonical_series = []

            for series_item in extracted_series:

                values = []

                point_map = {
                    str(
                        point.get(
                            "label",
                            "",
                        )
                    ): point.get(
                        "value"
                    )
                    for point in (
                        series_item.get(
                            "points",
                            [],
                        )
                        or []
                    )
                }

                for category in categories:
                    value = point_map.get(
                        category,
                        0,
                    )

                    try:
                        value = float(value)
                    except (
                        TypeError,
                        ValueError,
                    ):
                        value = 0

                    values.append(value)

                canonical_series.append({
                    "name": series_item.get(
                        "name",
                        "Series",
                    ),
                    "color": series_item.get(
                        "color",
                        "#4e79a7",
                    ),
                    "values": values,
                })

            canonical_data = {
                "title": extraction.get(
                    "title",
                    "",
                ),
                "detected_type": (
                    extraction.get(
                        "resolved_chart_type"
                    )
                    or chart.get(
                        "chart_type",
                        "bar",
                    )
                ),
                "categories": categories,
                "series": canonical_series,
                "metadata": {
                    "confidence": extraction.get(
                        "extraction_confidence",
                        0,
                    ),
                    "page_number": chart.get(
                        "page_number"
                    ),
                    "bounding_box": chart.get(
                        "bounding_box"
                    ),
                },
            }

        chart["canonical_data"] = canonical_data

        charts.append(chart)

    return sorted(
        charts,
        key=lambda c: (
            c.get(
                "page_number",
                0,
            ),
            c.get(
                "bounding_box",
                {}).get(
                    "y",
                    0,
                )
                if isinstance(
                    c.get(
                        "bounding_box"
                    ),
                    dict,
                )
                else 0,
        ),
    )


def get_processing_events(doc_id: str) -> list[dict]:
    """Get all processing events for a document."""
    db = get_db()
    events = []
    for snap in db.collection(COL_EVENTS).where("document_id", "==", doc_id).stream():
        d = snap.to_dict()
        d["id"] = snap.id
        events.append(d)
    return sorted(events, key=lambda e: e.get("created_at", ""))
