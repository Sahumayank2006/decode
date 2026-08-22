"""
DECODE - Document Extraction, Classification, OCR & Data Engine
Configuration Settings
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Upload settings
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif',
    'docx', 'doc', 'txt', 'csv', 'xlsx'
}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

# Firebase settings
FIREBASE_CREDENTIALS_PATH = os.environ.get(
    "FIREBASE_CREDENTIALS_PATH",
    str(BASE_DIR / "config" / "firebase_credentials.json")
)
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "decode-app")
FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "decode-app.appspot.com")

# OCR settings
TESSERACT_CMD = os.environ.get("TESSERACT_CMD", "tesseract")
OCR_LANGUAGES = "eng"           # e.g. "eng+hin" for bilingual
OCR_DPI = 300
OCR_PSM = 3                     # Page Segmentation Mode (3=auto)
OCR_OEM = 3                     # OCR Engine Mode (3=LSTM)

# NLP settings
SPACY_MODEL = "en_core_web_sm"
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.75
MAX_SUMMARY_SENTENCES = 5

# Image processing
IMAGE_RESIZE_WIDTH = 1200       # pixels for pre-processing
DENOISE_STRENGTH = 10
ADAPTIVE_THRESH_BLOCK = 11
ADAPTIVE_THRESH_C = 2

# Graph extraction
GRAPH_LAYOUT = "spring"         # spring | kamada_kawai | circular
MIN_ENTITY_FREQ = 1
MAX_GRAPH_NODES = 100

# API settings
API_PREFIX = "/api/v1"
SECRET_KEY = os.environ.get("SECRET_KEY", "decode-secret-key-change-in-production")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

# Logging
LOG_DIR = BASE_DIR / "logs"
LOG_LEVEL = "INFO"
LOG_FILE = LOG_DIR / "decode.log"

# Ensure directories exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
