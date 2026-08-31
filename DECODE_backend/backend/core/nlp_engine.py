"""
DECODE – NLP Engine
Provides: NER, keyword extraction, text summarization,
          classification, language detection, readability metrics,
          sentence similarity, topic modelling.
"""

import re
import logging
import math
from collections import Counter
from typing import Optional

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

logger = logging.getLogger("decode.nlp")

# ── lazy singletons ──────────────────────────────────────────────────────────
_nlp = None
_stop_words = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_stop_words():
    global _stop_words
    if _stop_words is None:
        try:
            _stop_words = set(stopwords.words("english"))
        except LookupError:
            nltk.download("stopwords", quiet=True)
            _stop_words = set(stopwords.words("english"))
    return _stop_words


# ─────────────────────────────────────────────────────────────────────────────
# Text cleaning
# ─────────────────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Remove noise while preserving meaningful content."""
    text = re.sub(r'\s+', ' ', text)          # normalise whitespace
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ASCII
    text = re.sub(r'(\n\s*){3,}', '\n\n', text)  # collapse blank lines
    text = text.strip()
    return text


def tokenize(text: str) -> list[str]:
    """Word-level tokenisation using NLTK."""
    try:
        return word_tokenize(text)
    except LookupError:
        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)
        return word_tokenize(text)


def sentence_split(text: str) -> list[str]:
    """Sentence tokenisation."""
    try:
        return sent_tokenize(text)
    except LookupError:
        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)
        return sent_tokenize(text)


# ─────────────────────────────────────────────────────────────────────────────
# Named Entity Recognition (spaCy)
# ─────────────────────────────────────────────────────────────────────────────

def extract_entities(text: str) -> dict:
    """
    Run spaCy NER on text.
    Returns dict grouped by entity label.
    """
    nlp = _get_nlp()
    # spaCy max length guard
    text_chunk = text[:1_000_000]
    doc = nlp(text_chunk)

    entities: dict[str, list] = {}
    for ent in doc.ents:
        label = ent.label_
        entities.setdefault(label, [])
        val = ent.text.strip()
        if val and val not in entities[label]:
            entities[label].append(val)

    # Collect noun phrases too
    noun_phrases = list({chunk.text.strip() for chunk in doc.noun_chunks
                         if len(chunk.text.strip()) > 2})

    return {
        "entities": entities,
        "noun_phrases": noun_phrases[:50],
        "entity_count": sum(len(v) for v in entities.values()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Keyword Extraction (TF-IDF + frequency)
# ─────────────────────────────────────────────────────────────────────────────

def extract_keywords(text: str, top_n: int = 20) -> list[dict]:
    """
    Extract top keywords using TF-IDF on sentences.
    Returns list of {keyword, score} dicts.
    """
    stop = _get_stop_words()
    sentences = sentence_split(text)
    if not sentences:
        return []

    # Term frequency in full text
    words = [w.lower() for w in tokenize(text)
             if w.isalpha() and len(w) > 2 and w.lower() not in stop]
    tf = Counter(words)

    # Inverse document frequency across sentences
    N = len(sentences)
    df: dict[str, int] = {}
    for sent in sentences:
        sent_words = set(
            w.lower() for w in tokenize(sent)
            if w.isalpha() and w.lower() not in stop
        )
        for w in sent_words:
            df[w] = df.get(w, 0) + 1

    tfidf = {}
    for word, freq in tf.items():
        idf = math.log((N + 1) / (df.get(word, 0) + 1)) + 1
        tfidf[word] = round(freq * idf, 4)

    sorted_kw = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
    return [{"keyword": kw, "score": sc} for kw, sc in sorted_kw[:top_n]]


# ─────────────────────────────────────────────────────────────────────────────
# Text Summarisation (extractive – TextRank-lite)
# ─────────────────────────────────────────────────────────────────────────────

def _sentence_vector(sentence: str, word_weights: dict) -> float:
    """Score a sentence by average word weight."""
    words = [w.lower() for w in tokenize(sentence) if w.isalpha()]
    if not words:
        return 0.0
    return sum(word_weights.get(w, 0) for w in words) / len(words)


def summarize(text: str, num_sentences: int = 5) -> dict:
    """
    Extractive summarisation using word frequency scoring.
    Returns summary text and individual scored sentences.
    """
    sentences = sentence_split(text)
    if len(sentences) <= num_sentences:
        return {"summary": text, "sentences": sentences, "ratio": 1.0}

    stop = _get_stop_words()
    words = [w.lower() for w in tokenize(text)
             if w.isalpha() and w.lower() not in stop]
    freq = Counter(words)
    max_freq = max(freq.values()) if freq else 1
    norm_freq = {w: f / max_freq for w, f in freq.items()}

    scored = [(sent, _sentence_vector(sent, norm_freq)) for sent in sentences]
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:num_sentences]

    # Restore original order
    top_set = {s for s, _ in top}
    ordered_summary = [s for s in sentences if s in top_set]

    return {
        "summary": " ".join(ordered_summary),
        "sentences": ordered_summary,
        "total_sentences": len(sentences),
        "ratio": round(len(ordered_summary) / len(sentences), 3),
        "scored_sentences": [
            {"sentence": s, "score": round(sc, 4)}
            for s, sc in sorted(scored, key=lambda x: x[1], reverse=True)[:10]
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Document Classification (rule-based + TF-IDF)
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "Legal": ["contract", "agreement", "clause", "liability", "jurisdiction",
              "plaintiff", "defendant", "court", "statute", "attorney"],
    "Medical": ["patient", "diagnosis", "treatment", "prescription", "clinical",
                "disease", "symptom", "hospital", "physician", "medication"],
    "Financial": ["revenue", "profit", "loss", "balance sheet", "invoice",
                  "tax", "audit", "equity", "dividend", "fiscal"],
    "Technical": ["algorithm", "software", "hardware", "system", "network",
                  "database", "API", "framework", "module", "deployment"],
    "Academic": ["abstract", "methodology", "hypothesis", "experiment",
                 "literature", "citation", "peer-review", "journal", "thesis"],
    "News": ["reported", "announced", "government", "official", "statement",
             "minister", "election", "parliament", "spokesperson", "crisis"],
    "Business": ["market", "strategy", "sales", "customer", "product",
                 "service", "management", "stakeholder", "ROI", "KPI"],
    "General": [],
}


def classify_document(text: str) -> dict:
    """
    Rule-based document classification.
    Returns predicted category and confidence scores.
    """
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        if not keywords:
            scores[category] = 0.01
            continue
        count = sum(1 for kw in keywords if kw.lower() in text_lower)
        scores[category] = round(count / len(keywords), 4)

    total = sum(scores.values()) or 1
    normalised = {k: round(v / total, 4) for k, v in scores.items()}
    predicted = max(normalised, key=normalised.get)

    return {
        "predicted_category": predicted,
        "confidence": normalised[predicted],
        "all_scores": normalised,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Language Detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_language(text: str) -> dict:
    """Detect document language using langdetect."""
    try:
        from langdetect import detect, detect_langs
        lang = detect(text[:3000])
        probs = detect_langs(text[:3000])
        return {
            "language": lang,
            "probabilities": [{"lang": p.lang, "prob": round(p.prob, 4)} for p in probs[:5]],
        }
    except Exception as e:
        logger.warning("Language detection failed: %s", e)
        return {"language": "en", "probabilities": []}


# ─────────────────────────────────────────────────────────────────────────────
# Readability metrics
# ─────────────────────────────────────────────────────────────────────────────

def readability_metrics(text: str) -> dict:
    """Flesch, Gunning-Fog, and other readability scores via textstat."""
    try:
        import textstat
        return {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "gunning_fog": textstat.gunning_fog(text),
            "smog_index": textstat.smog_index(text),
            "automated_readability_index": textstat.automated_readability_index(text),
            "dale_chall_readability": textstat.dale_chall_readability_score(text),
            "reading_time_minutes": textstat.reading_time(text, ms_per_char=14.69),
        }
    except Exception as e:
        logger.warning("Readability metrics error: %s", e)
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Part-of-speech tagging
# ─────────────────────────────────────────────────────────────────────────────

def pos_tags(text: str) -> list[dict]:
    """Return POS tags for tokens in the text (first 512 tokens)."""
    nlp = _get_nlp()
    doc = nlp(text[:5000])
    return [
        {"token": token.text, "pos": token.pos_, "tag": token.tag_, "dep": token.dep_}
        for token in doc
        if not token.is_space and not token.is_punct
    ][:200]


# ─────────────────────────────────────────────────────────────────────────────
# Full NLP pipeline
# ─────────────────────────────────────────────────────────────────────────────

def run_full_nlp_pipeline(text: str) -> dict:
    """
    Run all NLP modules and return a consolidated result dict.
    """
    cleaned = clean_text(text)
    logger.info("NLP pipeline: %d chars", len(cleaned))

    result = {}

    result["language"] = detect_language(cleaned)
    result["entities"] = extract_entities(cleaned)
    result["keywords"] = extract_keywords(cleaned, top_n=20)
    result["summary"] = summarize(cleaned, num_sentences=5)
    result["classification"] = classify_document(cleaned)
    result["readability"] = readability_metrics(cleaned)
    result["word_count"] = len(cleaned.split())
    result["char_count"] = len(cleaned)
    result["sentence_count"] = len(sentence_split(cleaned))

    return result
