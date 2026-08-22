#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# DECODE – Setup & Run Script
# ─────────────────────────────────────────────────────────────────

set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   DECODE – Document Intelligence Backend Setup       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 not found. Please install Python 3.9+"
  exit 1
fi

PYTHON=$(which python3)
echo "✅ Python: $($PYTHON --version)"

# Check tesseract
if ! command -v tesseract &> /dev/null; then
  echo "⚠️  Tesseract not found. Installing..."
  sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin 2>/dev/null || \
  brew install tesseract 2>/dev/null || \
  echo "⚠️  Please install Tesseract manually: https://tesseract-ocr.github.io/tessdoc/Installation.html"
else
  echo "✅ Tesseract: $(tesseract --version 2>&1 | head -1)"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet --break-system-packages 2>/dev/null || \
pip3 install -r requirements.txt --quiet

# Download spaCy model
echo "📥 Downloading spaCy model..."
python3 -m spacy download en_core_web_sm --quiet 2>/dev/null || true

# Download NLTK data
echo "📥 Downloading NLTK data..."
python3 -c "
import nltk
for pkg in ['punkt','stopwords','averaged_perceptron_tagger',
            'maxent_ne_chunker','words','punkt_tab','averaged_perceptron_tagger_eng']:
    nltk.download(pkg, quiet=True)
print('  NLTK data ready')
"

# Create required directories
mkdir -p static/uploads logs

# Firebase setup prompt
echo ""
echo "─────────────────────────────────────────────────────────"
echo "🔥 Firebase / Firestore Setup"
echo "─────────────────────────────────────────────────────────"
echo "The app works WITHOUT Firebase (uses in-memory mock)."
echo "To enable real Firestore, set one of:"
echo ""
echo "  Option A: File-based credentials"
echo "    export FIREBASE_CREDENTIALS_PATH=/path/to/serviceAccount.json"
echo ""
echo "  Option B: Inline JSON credentials"
echo "    export FIREBASE_CREDENTIALS_JSON='{\"type\":\"service_account\",...}'"
echo ""
echo "  Option C: (default) No credentials → uses local MockFirestore"
echo "─────────────────────────────────────────────────────────"
echo ""

# Run tests
echo "🧪 Running tests..."
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -30 || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "▶  Start the server:"
echo "   python3 app.py"
echo ""
echo "▶  Production mode:"
echo "   gunicorn app:app --workers 4 --bind 0.0.0.0:5000"
echo ""
echo "▶  API documentation:"
echo "   http://localhost:5000/api/v1/info"
echo ""
echo "▶  Web UI:"
echo "   http://localhost:5000"
echo ""
