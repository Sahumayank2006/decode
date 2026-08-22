"""
DECODE – Utility Helpers
Common utility functions used across the codebase.
"""

import os
import re
import json
import uuid
import hashlib
import logging
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("decode.utils")


# ─── Text utils ──────────────────────────────────────────────────────────────

def truncate(text: str, max_chars: int = 5000) -> str:
    """Truncate text to max_chars, appending ellipsis if cut."""
    return text if len(text) <= max_chars else text[:max_chars] + "…"


def word_count(text: str) -> int:
    return len(text.split()) if text else 0


def char_count(text: str) -> int:
    return len(text)


def clean_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def remove_special_chars(text: str, keep_punct: bool = True) -> str:
    if keep_punct:
        return re.sub(r'[^\w\s.,!?;:\'"()-]', '', text)
    return re.sub(r'[^\w\s]', '', text)


def extract_emails(text: str) -> list[str]:
    return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)


def extract_urls(text: str) -> list[str]:
    pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(pattern, text)


def extract_phone_numbers(text: str) -> list[str]:
    pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
    return re.findall(pattern, text)


def extract_dates(text: str) -> list[str]:
    patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b',
    ]
    found = []
    for p in patterns:
        found.extend(re.findall(p, text, re.IGNORECASE))
    return list(set(found))


# ─── File utils ──────────────────────────────────────────────────────────────

def file_size_human(size_bytes: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def get_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_id() -> str:
    return str(uuid.uuid4())


def timestamp() -> str:
    return datetime.utcnow().isoformat()


# ─── JSON utils ──────────────────────────────────────────────────────────────

def safe_json_dumps(obj: Any) -> str:
    """JSON serialise with fallback for non-serialisable types."""
    def default(o):
        if hasattr(o, "isoformat"):
            return o.isoformat()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    return json.dumps(obj, default=default, ensure_ascii=False)


def safe_json_loads(s: str) -> Any:
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {}


# ─── Validation ──────────────────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


def is_valid_url(url: str) -> bool:
    return bool(re.match(r'^https?://', url))


# ─── Logging ─────────────────────────────────────────────────────────────────

def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    lg = logging.getLogger(name)
    lg.setLevel(getattr(logging, level.upper(), logging.INFO))
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s – %(message)s")

    if not lg.handlers:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        lg.addHandler(sh)

        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(fmt)
            lg.addHandler(fh)

    return lg
