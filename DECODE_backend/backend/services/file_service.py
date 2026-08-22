"""
DECODE – File Service
Handles file validation, safe storage, format conversion,
and thumbnail generation via OpenCV.
"""

import os
import uuid
import logging
import shutil
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger("decode.file")

ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif',
    'docx', 'doc', 'txt', 'csv', 'xlsx'
}

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def allowed_file(filename: str) -> bool:
    ext = Path(filename).suffix.lower().lstrip(".")
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(filepath: str) -> bool:
    return os.path.getsize(filepath) <= MAX_FILE_SIZE


def secure_filename(filename: str) -> str:
    """Sanitise filename and add UUID prefix to avoid collisions."""
    name = Path(filename).stem
    ext = Path(filename).suffix
    safe_name = "".join(c for c in name if c.isalnum() or c in "-_ ").strip()
    safe_name = safe_name[:64] or "document"
    return f"{uuid.uuid4().hex[:8]}_{safe_name}{ext}"


def save_uploaded_file(file_obj, original_filename: str) -> dict:
    """
    Save an uploaded file object to disk.
    Returns metadata dict with path, size, etc.
    """
    if not allowed_file(original_filename):
        raise ValueError(f"File type not allowed: {original_filename}")

    safe_name = secure_filename(original_filename)
    dest_path = UPLOAD_DIR / safe_name

    # Save
    if hasattr(file_obj, "save"):
        file_obj.save(str(dest_path))
    elif hasattr(file_obj, "read"):
        with open(dest_path, "wb") as f:
            f.write(file_obj.read())
    else:
        shutil.copy2(file_obj, dest_path)

    size = os.path.getsize(dest_path)
    if size > MAX_FILE_SIZE:
        dest_path.unlink()
        raise ValueError(f"File too large: {size} bytes (max {MAX_FILE_SIZE})")

    ext = Path(original_filename).suffix.lower().lstrip(".")

    return {
        "original_filename": original_filename,
        "saved_filename": safe_name,
        "path": str(dest_path),
        "size": size,
        "extension": ext,
    }


def generate_thumbnail(image_path: str, size: tuple = (320, 240)) -> Optional[str]:
    """
    Generate a thumbnail for image files using OpenCV.
    Returns path of the thumbnail or None.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            # Try PIL for formats OpenCV doesn't handle
            pil_img = Image.open(image_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        thumb = cv2.resize(img, size, interpolation=cv2.INTER_LANCZOS4)
        thumb_path = str(Path(image_path).parent /
                         f"thumb_{Path(image_path).name}")
        cv2.imwrite(thumb_path, thumb)
        return thumb_path
    except Exception as e:
        logger.warning("Thumbnail generation failed: %s", e)
        return None


def convert_image_format(src_path: str, target_format: str = "png") -> str:
    """Convert an image to a different format using PIL."""
    src = Path(src_path)
    dst = src.parent / f"{src.stem}_converted.{target_format}"
    img = Image.open(src_path)
    img.save(str(dst), format=target_format.upper())
    return str(dst)


def get_image_metadata(image_path: str) -> dict:
    """Extract image metadata using OpenCV and PIL."""
    result = {}
    try:
        img = cv2.imread(image_path)
        if img is not None:
            h, w, c = img.shape if len(img.shape) == 3 else (*img.shape, 1)
            result["width"] = w
            result["height"] = h
            result["channels"] = c
            result["color_space"] = "BGR" if c == 3 else "GRAY"

            # Brightness and contrast
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if c == 3 else img
            result["mean_brightness"] = round(float(gray.mean()), 2)
            result["std_contrast"] = round(float(gray.std()), 2)

        pil_img = Image.open(image_path)
        result["format"] = pil_img.format
        result["mode"] = pil_img.mode
        exif = pil_img._getexif() if hasattr(pil_img, "_getexif") else None
        if exif:
            result["has_exif"] = True

    except Exception as e:
        logger.warning("Image metadata error: %s", e)

    return result


def list_uploaded_files() -> list[dict]:
    """List all files in the upload directory."""
    files = []
    for p in UPLOAD_DIR.iterdir():
        if p.is_file() and not p.name.startswith("thumb_"):
            files.append({
                "filename": p.name,
                "size": p.stat().st_size,
                "extension": p.suffix.lower().lstrip("."),
                "path": str(p),
            })
    return sorted(files, key=lambda x: x["filename"])


def delete_file(filename: str) -> bool:
    """Delete a file from the upload directory."""
    path = UPLOAD_DIR / filename
    if path.exists():
        path.unlink()
        # Also delete thumbnail if exists
        thumb = UPLOAD_DIR / f"thumb_{filename}"
        if thumb.exists():
            thumb.unlink()
        return True
    return False
