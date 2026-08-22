"""
DECODE – Main Flask Application
Document Extraction, Classification, OCR & Data Engine

Run:
  python app.py               # development
  gunicorn app:app            # production

Configure Firebase:
  export FIREBASE_CREDENTIALS_PATH=/path/to/serviceAccount.json
  OR
  export FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
"""

import logging
import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# ── Logging setup ────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "decode.log"),
    ],
)
logger = logging.getLogger("decode")


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static")
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "decode-dev-secret"),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,   # 50 MB upload limit
        JSON_SORT_KEYS=False,
    )

    # CORS – allow all origins in dev (restrict in production)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Firebase init ────────────────────────────────────────────────────────
    from config.firebase_config import init_firebase
    init_firebase()
    logger.info("Firebase initialised")

    # ── Register blueprints ──────────────────────────────────────────────────
    from api.routes import api_bp
    app.register_blueprint(api_bp)

    # ── Static files (frontend) ──────────────────────────────────────────────
    @app.route("/")
    def index():
        static_index = Path(__file__).parent / "static" / "index.html"
        if static_index.exists():
            return send_from_directory("static", "index.html")
        return jsonify({
            "message": "DECODE API is running",
            "docs": "/api/v1/info",
            "health": "/api/v1/health",
        })

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "path": str(e)}), 404

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "File too large (max 50 MB)"}), 413

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("500 error")
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

    logger.info("DECODE app created – blueprints registered")
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "true").lower() == "true"
    logger.info("Starting DECODE on port %d (debug=%s)", port, debug)
    app.run(host="0.0.0.0", port=port, debug=debug)
