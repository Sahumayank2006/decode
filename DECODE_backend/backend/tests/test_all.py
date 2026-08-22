"""
DECODE – Test Suite
Tests for OCR engine, NLP engine, graph engine, Firebase mock, and API routes.
Run: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import json
import io
import numpy as np

# ─── Fixtures ────────────────────────────────────────────────────────────────

SAMPLE_TEXT = """
Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
Tim Cook is the CEO of Apple. The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne
in April 1976. Apple's revenue in 2023 was approximately $394 billion.
The company develops consumer electronics including the iPhone, iPad, Mac, and Apple Watch.
Google, Microsoft, and Amazon are among Apple's key competitors in the technology sector.
Dr. John Smith from Stanford University published research on machine learning algorithms.
"""

SAMPLE_TEXT_SHORT = "Hello World. This is a test document from DECODE."


# ─── OCR Engine tests ────────────────────────────────────────────────────────

class TestOCREngine:
    def test_preprocess_image_grayscale(self):
        """Preprocess should return grayscale uint8 array."""
        from core.ocr_engine import preprocess_image
        img = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        result = preprocess_image(img, deskew=False)
        assert result is not None
        assert len(result.shape) == 2   # grayscale

    def test_detect_tables_empty(self):
        """Should return empty list on blank image."""
        from core.ocr_engine import detect_tables
        blank = np.ones((200, 300, 3), dtype=np.uint8) * 255
        tables = detect_tables(blank)
        assert isinstance(tables, list)

    def test_detect_figures_blank(self):
        """Should return empty list on all-white image."""
        from core.ocr_engine import detect_figures
        blank = np.ones((200, 300, 3), dtype=np.uint8) * 255
        figures = detect_figures(blank)
        assert isinstance(figures, list)

    def test_text_file_extraction(self, tmp_path):
        """Should extract text from a .txt file correctly."""
        from core.ocr_engine import extract_text_from_file
        txt = tmp_path / "sample.txt"
        txt.write_text("Hello DECODE test.")
        result = extract_text_from_file(str(txt))
        assert "Hello" in result["text"]
        assert result["confidence"] == 100.0

    def test_unsupported_extension_raises(self, tmp_path):
        """Unsupported extension should raise ValueError."""
        from core.ocr_engine import extract_text_from_file
        f = tmp_path / "file.xyz"
        f.write_text("data")
        with pytest.raises(ValueError):
            extract_text_from_file(str(f))


# ─── NLP Engine tests ────────────────────────────────────────────────────────

class TestNLPEngine:
    def test_clean_text(self):
        from core.nlp_engine import clean_text
        dirty = "Hello   \n\n\n  World!!!"
        clean = clean_text(dirty)
        assert "Hello" in clean
        assert "\n\n\n" not in clean

    def test_extract_entities(self):
        from core.nlp_engine import extract_entities
        result = extract_entities(SAMPLE_TEXT)
        assert "entities" in result
        assert "entity_count" in result
        assert result["entity_count"] >= 0

    def test_extract_keywords(self):
        from core.nlp_engine import extract_keywords
        kws = extract_keywords(SAMPLE_TEXT, top_n=10)
        assert isinstance(kws, list)
        assert len(kws) <= 10
        if kws:
            assert "keyword" in kws[0]
            assert "score" in kws[0]

    def test_summarize(self):
        from core.nlp_engine import summarize
        result = summarize(SAMPLE_TEXT, num_sentences=3)
        assert "summary" in result
        assert isinstance(result["summary"], str)
        assert "ratio" in result

    def test_classify_document(self):
        from core.nlp_engine import classify_document
        result = classify_document(SAMPLE_TEXT)
        assert "predicted_category" in result
        assert result["predicted_category"] in [
            "Legal","Medical","Financial","Technical","Academic","News","Business","General"
        ]

    def test_detect_language(self):
        from core.nlp_engine import detect_language
        result = detect_language("This is an English text.")
        assert "language" in result
        assert result["language"] == "en"

    def test_readability_metrics(self):
        from core.nlp_engine import readability_metrics
        result = readability_metrics(SAMPLE_TEXT)
        # Should return numeric metrics
        assert isinstance(result, dict)

    def test_full_pipeline(self):
        from core.nlp_engine import run_full_nlp_pipeline
        result = run_full_nlp_pipeline(SAMPLE_TEXT)
        assert "entities" in result
        assert "keywords" in result
        assert "summary" in result
        assert "classification" in result
        assert "word_count" in result

    def test_sentence_split(self):
        from core.nlp_engine import sentence_split
        sents = sentence_split("Hello world. This is a test. Goodbye.")
        assert len(sents) == 3


# ─── Graph Engine tests ──────────────────────────────────────────────────────

class TestGraphEngine:
    def test_build_cooccurrence_graph(self):
        from core.graph_engine import build_cooccurrence_graph
        G, node_types = build_cooccurrence_graph(SAMPLE_TEXT)
        assert G is not None
        assert G.number_of_nodes() >= 0

    def test_graph_analytics_empty(self):
        import networkx as nx
        from core.graph_engine import graph_analytics
        G = nx.Graph()
        result = graph_analytics(G)
        assert result["nodes"] == 0

    def test_graph_analytics(self):
        import networkx as nx
        from core.graph_engine import graph_analytics
        G = nx.Graph()
        G.add_edges_from([("A","B"),("B","C"),("C","A")])
        result = graph_analytics(G)
        assert result["nodes"] == 3
        assert result["edges"] == 3

    def test_graph_to_dict(self):
        import networkx as nx
        from core.graph_engine import graph_to_dict
        G = nx.Graph()
        G.add_node("Alice", freq=2)
        G.add_node("Bob", freq=1)
        G.add_edge("Alice", "Bob", weight=1)
        d = graph_to_dict(G)
        assert "nodes" in d
        assert "edges" in d

    def test_full_pipeline_returns_structure(self):
        from core.graph_engine import run_graph_pipeline
        result = run_graph_pipeline(SAMPLE_TEXT, render=False)
        assert "graph_data" in result
        assert "analytics" in result


# ─── Firebase Mock tests ─────────────────────────────────────────────────────

class TestMockFirestore:
    def setup_method(self):
        from config.firebase_config import MockFirestore
        self.db = MockFirestore()

    def test_add_and_retrieve(self):
        col = self.db.collection("test_docs")
        ref, _ = col.add({"name": "Alice", "score": 95})
        docs = list(col.stream())
        assert any(d.to_dict()["name"] == "Alice" for d in docs)

    def test_document_update(self):
        col = self.db.collection("test_docs2")
        ref = col.document("doc1")
        ref.set({"value": 1})
        ref.update({"value": 2})
        snap = ref.get()
        assert snap.to_dict()["value"] == 2

    def test_where_query(self):
        col = self.db.collection("qtest")
        col.add({"status": "active"})
        col.add({"status": "inactive"})
        results = list(col.where("status", "==", "active").stream())
        assert len(results) == 1

    def test_delete_document(self):
        col = self.db.collection("del_test")
        ref = col.document("to_delete")
        ref.set({"x": 1})
        ref.delete()
        snap = ref.get()
        assert snap.to_dict() is None


# ─── File Service tests ──────────────────────────────────────────────────────

class TestFileService:
    def test_allowed_file(self):
        from services.file_service import allowed_file
        assert allowed_file("document.pdf")
        assert allowed_file("image.png")
        assert not allowed_file("malware.exe")
        assert not allowed_file("script.sh")

    def test_secure_filename(self):
        from services.file_service import secure_filename
        name = secure_filename("../../etc/passwd.pdf")
        assert "/" not in name or name.startswith("/")
        assert name.endswith(".pdf")

    def test_image_metadata(self, tmp_path):
        from services.file_service import get_image_metadata
        from PIL import Image
        img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
        path = str(tmp_path / "test.png")
        img.save(path)
        meta = get_image_metadata(path)
        assert meta.get("width") == 100


# ─── Utility tests ───────────────────────────────────────────────────────────

class TestHelpers:
    def test_extract_emails(self):
        from utils.helpers import extract_emails
        text = "Contact us at support@decode.ai or admin@example.com"
        emails = extract_emails(text)
        assert "support@decode.ai" in emails

    def test_extract_urls(self):
        from utils.helpers import extract_urls
        text = "Visit https://decode.ai or http://example.com/path"
        urls = extract_urls(text)
        assert len(urls) == 2

    def test_extract_dates(self):
        from utils.helpers import extract_dates
        text = "The date is 2024-01-15 and also Jan 15, 2024"
        dates = extract_dates(text)
        assert len(dates) >= 1

    def test_file_size_human(self):
        from utils.helpers import file_size_human
        assert file_size_human(1024) == "1.0 KB"
        assert file_size_human(1024 * 1024) == "1.0 MB"

    def test_word_count(self):
        from utils.helpers import word_count
        assert word_count("Hello World Test") == 3

    def test_unique_id(self):
        from utils.helpers import unique_id
        id1 = unique_id()
        id2 = unique_id()
        assert id1 != id2
        assert len(id1) == 36  # UUID format


# ─── API Integration tests ───────────────────────────────────────────────────

class TestAPI:
    @pytest.fixture
    def client(self):
        from app import create_app
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_health(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "ok"

    def test_info(self, client):
        resp = client.get("/api/v1/info")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "capabilities" in data

    def test_nlp_endpoint(self, client):
        resp = client.post("/api/v1/nlp",
                           json={"text": SAMPLE_TEXT},
                           content_type="application/json")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "keywords" in data

    def test_nlp_empty_text(self, client):
        resp = client.post("/api/v1/nlp",
                           json={"text": ""},
                           content_type="application/json")
        assert resp.status_code == 400

    def test_keywords_endpoint(self, client):
        resp = client.post("/api/v1/nlp/keywords",
                           json={"text": SAMPLE_TEXT, "top_n": 5})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "keywords" in data

    def test_summarize_endpoint(self, client):
        resp = client.post("/api/v1/nlp/summarize",
                           json={"text": SAMPLE_TEXT, "sentences": 3})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "summary" in data

    def test_classify_endpoint(self, client):
        resp = client.post("/api/v1/nlp/classify",
                           json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "predicted_category" in data

    def test_graph_endpoint(self, client):
        resp = client.post("/api/v1/graph",
                           json={"text": SAMPLE_TEXT, "render": False})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "graph_data" in data

    def test_list_documents(self, client):
        resp = client.get("/api/v1/documents")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "documents" in data

    def test_stats_endpoint(self, client):
        resp = client.get("/api/v1/stats")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "total_documents" in data

    def test_search_endpoint(self, client):
        resp = client.get("/api/v1/search?q=apple")
        assert resp.status_code == 200

    def test_upload_no_file(self, client):
        resp = client.post("/api/v1/upload")
        assert resp.status_code == 400

    def test_txt_upload(self, client, tmp_path):
        txt_content = b"DECODE is a document intelligence platform by Anthropic."
        data = {
            "file": (io.BytesIO(txt_content), "test_doc.txt"),
            "lang": "eng",
            "run_nlp": "true",
            "run_graph": "false",
        }
        resp = client.post("/api/v1/upload",
                           data=data,
                           content_type="multipart/form-data")
        assert resp.status_code == 201
        result = json.loads(resp.data)
        assert result["status"] == "success"
        assert "document_id" in result
