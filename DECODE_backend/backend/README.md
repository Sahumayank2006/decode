# DECODE – Document Extraction, Classification, OCR & Data Engine

> Full-stack document intelligence backend with OCR, NLP, Knowledge Graph extraction, and Firebase Firestore storage.

---

## Architecture

```
backend/
├── app.py                        ← Flask application entry point
├── requirements.txt              ← Python dependencies
├── setup.sh                      ← One-shot setup & test runner
│
├── api/
│   ├── __init__.py
│   └── routes.py                 ← All REST API endpoints
│
├── core/
│   ├── __init__.py
│   ├── ocr_engine.py             ← OpenCV preprocessing + Tesseract OCR
│   ├── nlp_engine.py             ← spaCy NER, TF-IDF keywords, summarisation, classification
│   └── graph_engine.py           ← Knowledge graph extraction & visualisation
│
├── services/
│   ├── __init__.py
│   ├── document_processor.py     ← Orchestrates OCR → NLP → Graph → Firestore
│   ├── file_service.py           ← File upload, validation, thumbnail generation
│   └── search_service.py         ← Keyword, semantic & entity-based search
│
├── config/
│   ├── __init__.py
│   ├── settings.py               ← All configuration variables
│   └── firebase_config.py        ← Firebase init + MockFirestore fallback
│
├── models/
│   ├── __init__.py
│   └── schemas.py                ← Dataclass schemas for all entities
│
├── utils/
│   ├── __init__.py
│   └── helpers.py                ← Text utils, file utils, logging helpers
│
├── tests/
│   ├── __init__.py
│   └── test_all.py               ← Full pytest test suite
│
├── static/
│   ├── index.html                ← Simple web UI
│   └── uploads/                  ← Uploaded files stored here
│
└── logs/
    └── decode.log                ← Application logs
```

---

## Quick Start

```bash
# 1. Install dependencies & run tests
bash setup.sh

# 2. Start the server (dev mode)
python3 app.py

# 3. Open browser
open http://localhost:5000
```

---

## Firebase / Firestore Setup

The app runs in **local mock mode** by default (no credentials needed).

To connect real Firebase Firestore:

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a project → Project Settings → Service Accounts → Generate new private key
3. Download `serviceAccount.json`
4. Set the environment variable:

```bash
export FIREBASE_CREDENTIALS_PATH=/path/to/serviceAccount.json
python3 app.py
```

Or inline:

```bash
export FIREBASE_CREDENTIALS_JSON=$(cat serviceAccount.json)
python3 app.py
```

---

## API Reference

### Upload & Full Pipeline

```http
POST /api/v1/upload
Content-Type: multipart/form-data

Fields:
  file          – The document (PDF, DOCX, PNG, JPG, TIFF, TXT)
  lang          – OCR language (default: eng | eng+hin | hin)
  run_nlp       – true/false (default: true)
  run_graph     – true/false (default: true)
  layout        – spring | kamada_kawai | circular | spectral
```

**Response:**
```json
{
  "document_id": "uuid",
  "filename": "report.pdf",
  "ocr": {
    "text": "...",
    "confidence": 87.4,
    "word_count": 1250,
    "tables_detected": [...],
    "figures_detected": [...]
  },
  "nlp": {
    "entities": {"PERSON": ["Tim Cook"], "ORG": ["Apple"]},
    "keywords": [{"keyword": "revenue", "score": 4.2}],
    "summary": {"summary": "..."},
    "classification": {"predicted_category": "Business"},
    "readability": {"flesch_reading_ease": 62.3}
  },
  "graph": {
    "graph_data": {"nodes": [...], "edges": [...]},
    "analytics": {"nodes": 24, "edges": 41, "density": 0.14},
    "image_base64": "<PNG as base64>"
  }
}
```

---

### NLP Endpoints (raw text)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/nlp` | Full NLP pipeline |
| POST | `/api/v1/nlp/entities` | Named entity recognition |
| POST | `/api/v1/nlp/keywords` | Keyword extraction (TF-IDF) |
| POST | `/api/v1/nlp/summarize` | Extractive summarisation |
| POST | `/api/v1/nlp/classify` | Document classification |
| POST | `/api/v1/nlp/readability` | Readability metrics |

**Body:** `{"text": "your text here"}`

---

### OCR Endpoint

```http
POST /api/v1/ocr
Content-Type: multipart/form-data

Fields:
  file    – Image or PDF
  lang    – OCR language (default: eng)
```

---

### Knowledge Graph

```http
POST /api/v1/graph
Content-Type: application/json

{
  "text": "...",
  "layout": "spring",
  "render": true
}
```

---

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/documents` | List all documents |
| GET | `/api/v1/documents/<id>` | Get document by ID |
| DELETE | `/api/v1/documents/<id>` | Delete document |
| GET | `/api/v1/analysis/<id>` | Get NLP analysis |
| GET | `/api/v1/graph/<id>` | Get stored graph data |
| POST | `/api/v1/reanalyze/<id>` | Re-run NLP/Graph |

---

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search?q=apple` | Keyword search |
| GET | `/api/v1/search/semantic?q=machine learning` | Semantic search |
| GET | `/api/v1/search/entity?entity=Tim+Cook` | Entity-based search |
| GET | `/api/v1/search/category?category=Business` | Category-based search |

---

### Image Processing (OpenCV)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/image/preprocess` | Returns preprocessed image (base64) |
| POST | `/api/v1/image/detect-tables` | Detect table regions |
| POST | `/api/v1/image/detect-figures` | Detect figure regions |

---

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/info` | API info & capabilities |
| GET | `/api/v1/stats` | Dashboard statistics |
| GET | `/api/v1/files` | List uploaded files |
| DELETE | `/api/v1/files/<filename>` | Delete uploaded file |

---

## OCR Pipeline

```
Input File
    │
    ▼
┌─────────────────────────────────┐
│ OpenCV Image Pre-processing     │
│  • Resize (if < 800px wide)     │
│  • Grayscale conversion         │
│  • FastNlMeansDenoising         │
│  • CLAHE contrast enhancement   │
│  • Adaptive threshold binarise  │
│  • Deskew (Hough transform)     │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Tesseract OCR                   │
│  • PSM 3 (auto segmentation)    │
│  • OEM 3 (LSTM engine)          │
│  • Per-word confidence scores   │
│  • Multi-page PDF support       │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Structure Detection             │
│  • Table regions (Hough lines)  │
│  • Figure bounding boxes        │
└─────────────────────────────────┘
```

## NLP Pipeline

```
Extracted Text
    │
    ▼
Language Detection (langdetect)
    │
    ▼
Named Entity Recognition (spaCy en_core_web_sm)
  → PERSON, ORG, GPE, DATE, MONEY, PRODUCT, …
    │
    ▼
Keyword Extraction (TF-IDF across sentences)
    │
    ▼
Extractive Summarisation (word frequency scoring)
    │
    ▼
Document Classification (rule-based + keyword matching)
  → Legal, Medical, Financial, Technical, Academic, News, Business
    │
    ▼
Readability Metrics (textstat)
  → Flesch, Gunning-Fog, SMOG, ARI, Dale-Chall
```

## Knowledge Graph Pipeline

```
Text
  │
  ▼
Entity Co-occurrence Extraction (spaCy + sliding window)
  │
  ▼
Edge Weight Computation (co-occurrence frequency)
  │
  ▼
NetworkX Graph Construction
  │
  ├── Centrality Analysis (degree, betweenness)
  ├── Community Detection (greedy modularity)
  └── Matplotlib Visualisation (dark theme, entity-coloured nodes)
  │
  ▼
JSON Export + base64 PNG
```

---

## Running Tests

```bash
python3 -m pytest tests/test_all.py -v
```

Tests cover:
- OCR engine (preprocessing, detection, extraction)
- NLP engine (entities, keywords, summary, classification, language)
- Graph engine (construction, analytics, serialisation)
- Firebase MockFirestore (CRUD, queries)
- File service (validation, metadata)
- Utility helpers (regex extractors, file utils)
- Full API integration (all endpoints)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FIREBASE_CREDENTIALS_PATH` | – | Path to Firebase service account JSON |
| `FIREBASE_CREDENTIALS_JSON` | – | Firebase credentials as JSON string |
| `FIREBASE_PROJECT_ID` | `decode-app` | Firebase project ID |
| `FIREBASE_STORAGE_BUCKET` | `decode-app.appspot.com` | Storage bucket |
| `SECRET_KEY` | `decode-dev-secret` | Flask secret key |
| `PORT` | `5000` | Server port |
| `DEBUG` | `true` | Flask debug mode |

---

## Supported File Types

| Type | Extensions | Method |
|------|-----------|--------|
| Images | PNG, JPG, JPEG, TIFF, BMP, GIF | OpenCV + Tesseract |
| PDF | PDF | pdf2image + Tesseract (per-page) |
| Word | DOCX, DOC | python-docx (native extraction) |
| Plain text | TXT | Direct read |
| Spreadsheet | XLSX, CSV | Text extraction |

---

## Production Deployment

```bash
# With gunicorn
gunicorn app:app \
  --workers 4 \
  --threads 2 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

---

## Tech Stack

| Component | Library |
|-----------|---------|
| Web framework | Flask + Flask-CORS |
| OCR | Tesseract + pytesseract |
| Image processing | OpenCV (cv2) |
| NLP | spaCy (en_core_web_sm) |
| Tokenisation | NLTK |
| Semantic search | sentence-transformers (all-MiniLM-L6-v2) |
| Knowledge graph | NetworkX |
| Graph visualisation | Matplotlib |
| Readability | textstat |
| Language detection | langdetect |
| PDF processing | pdf2image + pdfplumber |
| DOCX processing | python-docx |
| Database | Firebase Firestore (or MockFirestore) |
| Deep learning | PyTorch + HuggingFace Transformers |
