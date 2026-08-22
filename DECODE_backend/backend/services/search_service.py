"""
DECODE – Search Service
Full-text and keyword search across stored documents in Firestore.
Includes semantic similarity search using sentence-transformers.
"""

import logging
import re
from datetime import datetime
from typing import Optional

from config.firebase_config import get_db

logger = logging.getLogger("decode.search")

_embedder = None


def _get_embedder():
    """Lazy-load sentence transformer for semantic search."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Sentence transformer loaded")
        except Exception as e:
            logger.warning("Could not load sentence transformer: %s", e)
    return _embedder


# ─────────────────────────────────────────────────────────────────────────────
# Keyword search
# ─────────────────────────────────────────────────────────────────────────────

def keyword_search(query: str,
                   collection: str = "documents",
                   field: str = "filename",
                   limit: int = 20) -> list[dict]:
    """
    Simple keyword search over Firestore collection.
    Searches filename field by default; for full-text needs Algolia/ElasticSearch.
    """
    db = get_db()
    query_lower = query.lower()
    results = []

    for snap in db.collection(collection).stream():
        data = snap.to_dict()
        data["id"] = snap.id

        # Check filename match
        if query_lower in data.get("filename", "").lower():
            results.append(data)
            continue

        # Check if query appears in any text field
        for key in ("filename", "status"):
            if query_lower in str(data.get(key, "")).lower():
                results.append(data)
                break

    return results[:limit]


def search_by_category(category: str, limit: int = 20) -> list[dict]:
    """Search analysis results by predicted document category."""
    db = get_db()
    results = []

    for snap in db.collection("analysis").stream():
        data = snap.to_dict()
        nlp = data.get("nlp_result", {})
        cls = nlp.get("classification", {})
        if cls.get("predicted_category", "").lower() == category.lower():
            doc_id = data.get("document_id")
            results.append({
                "document_id": doc_id,
                "filename": data.get("filename"),
                "category": cls.get("predicted_category"),
                "confidence": cls.get("confidence"),
                "id": snap.id,
            })

    return results[:limit]


def search_by_entity(entity_text: str, limit: int = 20) -> list[dict]:
    """Find documents that contain a specific named entity."""
    db = get_db()
    entity_lower = entity_text.lower()
    results = []

    for snap in db.collection("analysis").stream():
        data = snap.to_dict()
        nlp = data.get("nlp_result", {})
        entities = nlp.get("entities", {}).get("entities", {})

        for label, ents in entities.items():
            if any(entity_lower in e.lower() for e in ents):
                results.append({
                    "document_id": data.get("document_id"),
                    "filename": data.get("filename"),
                    "matched_entity": entity_text,
                    "entity_type": label,
                    "id": snap.id,
                })
                break

    return results[:limit]


# ─────────────────────────────────────────────────────────────────────────────
# Semantic similarity search
# ─────────────────────────────────────────────────────────────────────────────

def semantic_search(query: str,
                    top_k: int = 5,
                    threshold: float = 0.3) -> list[dict]:
    """
    Find documents semantically similar to a query using sentence embeddings.
    Runs over stored summaries in Firestore.
    """
    embedder = _get_embedder()
    if embedder is None:
        return keyword_search(query)

    import numpy as np

    db = get_db()
    query_emb = embedder.encode([query])[0]

    results = []
    for snap in db.collection("analysis").stream():
        data = snap.to_dict()
        nlp = data.get("nlp_result", {})
        summary = nlp.get("summary", {}).get("summary", "")
        keywords = [k["keyword"] for k in nlp.get("keywords", [])[:10]]
        doc_text = summary + " " + " ".join(keywords)

        if not doc_text.strip():
            continue

        doc_emb = embedder.encode([doc_text])[0]
        similarity = float(np.dot(query_emb, doc_emb) /
                           (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb) + 1e-9))

        if similarity >= threshold:
            results.append({
                "document_id": data.get("document_id"),
                "filename": data.get("filename"),
                "similarity": round(similarity, 4),
                "summary": summary[:200],
                "id": snap.id,
            })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


# ─────────────────────────────────────────────────────────────────────────────
# Stats / dashboard
# ─────────────────────────────────────────────────────────────────────────────

def get_statistics() -> dict:
    """Aggregate stats across all documents."""
    db = get_db()

    doc_count = 0
    total_words = 0
    total_pages = 0
    categories: dict[str, int] = {}
    entity_types: dict[str, int] = {}

    for snap in db.collection("documents").stream():
        d = snap.to_dict()
        doc_count += 1
        total_words += d.get("word_count", 0)
        total_pages += d.get("total_pages", 1)

    for snap in db.collection("analysis").stream():
        d = snap.to_dict()
        nlp = d.get("nlp_result", {})
        cat = nlp.get("classification", {}).get("predicted_category")
        if cat:
            categories[cat] = categories.get(cat, 0) + 1

        ents = nlp.get("entities", {}).get("entities", {})
        for label, items in ents.items():
            entity_types[label] = entity_types.get(label, 0) + len(items)

    return {
        "total_documents": doc_count,
        "total_words": total_words,
        "total_pages": total_pages,
        "category_distribution": categories,
        "entity_type_distribution": entity_types,
    }
