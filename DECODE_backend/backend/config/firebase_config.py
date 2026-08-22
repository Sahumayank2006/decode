"""
Firebase Firestore initialization for DECODE
Handles both service-account JSON and environment-variable modes.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("decode.firebase")

_db = None
_app = None
_initialized = False


def init_firebase():
    """
    Initialize Firebase Admin SDK.
    Priority:
      1. FIREBASE_CREDENTIALS_PATH env var pointing to a JSON key file
      2. FIREBASE_CREDENTIALS_JSON env var containing the JSON directly
      3. Mock/local mode for development (no credentials file)
    Returns the Firestore client or a MockDB instance.
    """
    global _db, _app, _initialized

    if _initialized:
        return _db

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
        cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")

        if cred_path and Path(cred_path).exists():
            cred = credentials.Certificate(cred_path)
            _app = firebase_admin.initialize_app(cred, {
                "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", "decode-app.appspot.com")
            })
            _db = firestore.client()
            logger.info("Firebase initialized from credentials file: %s", cred_path)

        elif cred_json:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            _app = firebase_admin.initialize_app(cred, {
                "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", "decode-app.appspot.com")
            })
            _db = firestore.client()
            logger.info("Firebase initialized from environment JSON")

        else:
            logger.warning(
                "No Firebase credentials found – running in LOCAL MOCK mode. "
                "Set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON to use real Firestore."
            )
            _db = MockFirestore()

    except Exception as exc:
        logger.error("Firebase init error: %s – falling back to MockFirestore", exc)
        _db = MockFirestore()

    _initialized = True
    return _db


def get_db():
    """Return the Firestore client (or MockFirestore)."""
    global _db
    if not _initialized:
        init_firebase()
    return _db


# ─── Mock Firestore for local development ────────────────────────────────────

class MockDocument:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = True

    def to_dict(self):
        return self._data


class MockCollection:
    """In-memory Firestore-compatible collection."""

    def __init__(self, name):
        self.name = name
        self._docs: dict = {}

    # ── write ──────────────────────────────────────────────────────────────
    def add(self, data):
        import uuid
        from datetime import datetime
        doc_id = str(uuid.uuid4())
        data["created_at"] = datetime.utcnow().isoformat()
        self._docs[doc_id] = data
        ref = MockDocRef(self, doc_id)
        return ref, ref

    def document(self, doc_id=None):
        import uuid
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        return MockDocRef(self, doc_id)

    # ── read ───────────────────────────────────────────────────────────────
    def get(self):
        return [MockDocument(k, v) for k, v in self._docs.items()]

    def where(self, field, op, value):
        return MockQuery(self, field, op, value)

    def order_by(self, field, **kwargs):
        return self  # simplified

    def limit(self, n):
        return self  # simplified

    def stream(self):
        return iter([MockDocument(k, v) for k, v in self._docs.items()])


class MockDocRef:
    def __init__(self, collection, doc_id):
        self._col = collection
        self.id = doc_id

    def set(self, data, merge=False):
        self._col._docs[self.id] = data

    def update(self, data):
        if self.id in self._col._docs:
            self._col._docs[self.id].update(data)
        else:
            self._col._docs[self.id] = data

    def get(self):
        data = self._col._docs.get(self.id)
        return MockDocument(self.id, data) if data else MockDocument(self.id, None)

    def delete(self):
        self._col._docs.pop(self.id, None)


class MockQuery:
    def __init__(self, collection, field, op, value):
        self._col = collection
        self._field = field
        self._op = op
        self._value = value

    def stream(self):
        results = []
        for doc_id, data in self._col._docs.items():
            val = data.get(self._field)
            if self._op == "==" and val == self._value:
                results.append(MockDocument(doc_id, data))
            elif self._op == ">=" and val is not None and val >= self._value:
                results.append(MockDocument(doc_id, data))
            elif self._op == "<=" and val is not None and val <= self._value:
                results.append(MockDocument(doc_id, data))
        return iter(results)

    def get(self):
        return list(self.stream())


class MockFirestore:
    """Root mock Firestore client."""

    _collections: dict = {}

    def collection(self, name):
        if name not in self._collections:
            self._collections[name] = MockCollection(name)
        return self._collections[name]
