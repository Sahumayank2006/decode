"""
DECODE – Copyright Compliance Scoring Engine
Evaluates structural and visual similarity between the original chart
image and the regenerated chart, producing:
  • composite similarity score  (0–100)
  • risk level                  (low / medium / high)
  • sub-scores                  (color, layout, geometry)
  • actionable recommendations

The scoring uses:
  1. SSIM  (Structural Similarity Index) — overall pixel-level resemblance
  2. Color histogram comparison           — palette similarity
  3. Layout / proportion analysis         — bar widths, spacing, ratios
"""

import logging
import math
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger("decode.compliance")

# ── Configurable thresholds ──────────────────────────────────────────────────
# These can be overridden via environment variables

RISK_THRESHOLDS = {
    "low_max": 40,      # 0-40  → low risk (substantially different)
    "medium_max": 70,   # 40-70 → medium risk (review recommended)
    # 70-100 → high risk (too similar, modifications needed)
}

WEIGHTS = {
    "ssim": 0.40,
    "color": 0.30,
    "layout": 0.30,
}


# ─────────────────────────────────────────────────────────────────────────────
# SSIM  (Structural Similarity Index)
# ─────────────────────────────────────────────────────────────────────────────

def _compute_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    Compute SSIM between two images.
    Handles different sizes by resizing to a common dimension.
    Returns a value between 0.0 (completely different) and 1.0 (identical).
    """
    # Resize to common dimensions
    target_h, target_w = 256, 256
    a = cv2.resize(img1, (target_w, target_h))
    b = cv2.resize(img2, (target_w, target_h))

    # Convert to grayscale if needed
    if len(a.shape) == 3:
        a = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    if len(b.shape) == 3:
        b = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)

    a = a.astype(np.float64)
    b = b.astype(np.float64)

    # SSIM constants
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    mu_a = cv2.GaussianBlur(a, (11, 11), 1.5)
    mu_b = cv2.GaussianBlur(b, (11, 11), 1.5)

    mu_a_sq = mu_a ** 2
    mu_b_sq = mu_b ** 2
    mu_ab = mu_a * mu_b

    sigma_a_sq = cv2.GaussianBlur(a ** 2, (11, 11), 1.5) - mu_a_sq
    sigma_b_sq = cv2.GaussianBlur(b ** 2, (11, 11), 1.5) - mu_b_sq
    sigma_ab = cv2.GaussianBlur(a * b, (11, 11), 1.5) - mu_ab

    numerator = (2 * mu_ab + C1) * (2 * sigma_ab + C2)
    denominator = (mu_a_sq + mu_b_sq + C1) * (sigma_a_sq + sigma_b_sq + C2)

    ssim_map = numerator / denominator
    return float(np.mean(ssim_map))


# ─────────────────────────────────────────────────────────────────────────────
# Color histogram comparison
# ─────────────────────────────────────────────────────────────────────────────

def _compare_color_histograms(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    Compare color distributions using histogram correlation.
    Returns similarity from 0.0 (different) to 1.0 (identical).
    """
    # Resize to common dimensions
    a = cv2.resize(img1, (256, 256))
    b = cv2.resize(img2, (256, 256))

    # Convert to HSV for better color comparison
    if len(a.shape) == 3:
        a_hsv = cv2.cvtColor(a, cv2.COLOR_BGR2HSV)
    else:
        a_hsv = cv2.cvtColor(cv2.cvtColor(a, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2HSV)
    if len(b.shape) == 3:
        b_hsv = cv2.cvtColor(b, cv2.COLOR_BGR2HSV)
    else:
        b_hsv = cv2.cvtColor(cv2.cvtColor(b, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2HSV)

    # Calculate histograms for H and S channels
    h_bins, s_bins = 50, 60
    h_ranges = [0, 180, 0, 256]

    hist_a = cv2.calcHist(
        [a_hsv], [0, 1], None, [h_bins, s_bins], h_ranges
    )
    hist_b = cv2.calcHist(
        [b_hsv], [0, 1], None, [h_bins, s_bins], h_ranges
    )

    cv2.normalize(hist_a, hist_a, 0, 1, cv2.NORM_MINMAX)
    cv2.normalize(hist_b, hist_b, 0, 1, cv2.NORM_MINMAX)

    # Correlation method gives -1 to 1; normalise to 0-1
    correlation = cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_CORREL)
    return max(0.0, float(correlation))


# ─────────────────────────────────────────────────────────────────────────────
# Layout / geometry comparison
# ─────────────────────────────────────────────────────────────────────────────

def _compare_layout(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    Compare structural layout using edge maps and contour analysis.
    Returns similarity from 0.0 to 1.0.
    """
    # Resize
    a = cv2.resize(img1, (256, 256))
    b = cv2.resize(img2, (256, 256))

    # Convert to grayscale
    if len(a.shape) == 3:
        a_gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    else:
        a_gray = a
    if len(b.shape) == 3:
        b_gray = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    else:
        b_gray = b

    # Edge detection
    edges_a = cv2.Canny(a_gray, 50, 150)
    edges_b = cv2.Canny(b_gray, 50, 150)

    # Compare edge maps using pixel overlap
    intersection = np.sum((edges_a > 0) & (edges_b > 0))
    union = np.sum((edges_a > 0) | (edges_b > 0))

    if union == 0:
        return 0.0

    iou = intersection / union

    # Also compare contour shapes using Hu moments
    contours_a, _ = cv2.findContours(
        edges_a, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    contours_b, _ = cv2.findContours(
        edges_b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    hu_similarity = 0.0
    if contours_a and contours_b:
        # Compare the largest contours
        cnt_a = max(contours_a, key=cv2.contourArea)
        cnt_b = max(contours_b, key=cv2.contourArea)

        moments_a = cv2.HuMoments(cv2.moments(cnt_a)).flatten()
        moments_b = cv2.HuMoments(cv2.moments(cnt_b)).flatten()

        # Log-transform and compare
        for i in range(7):
            if moments_a[i] != 0:
                moments_a[i] = -math.copysign(1, moments_a[i]) * math.log10(abs(moments_a[i]) + 1e-10)
            if moments_b[i] != 0:
                moments_b[i] = -math.copysign(1, moments_b[i]) * math.log10(abs(moments_b[i]) + 1e-10)

        diff = np.linalg.norm(moments_a - moments_b)
        hu_similarity = max(0.0, 1.0 - diff / 20.0)

    # Combined layout score
    return 0.6 * iou + 0.4 * hu_similarity


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation generator
# ─────────────────────────────────────────────────────────────────────────────

def _generate_recommendations(
    similarity_score: float,
    color_similarity: float,
    layout_similarity: float,
    geometry_similarity: float,
) -> list[dict]:
    """
    Generate actionable recommendations based on sub-scores.
    Each recommendation has:
      {"id": str, "text": str, "category": str, "auto_applicable": bool, "priority": str}
    """
    recs = []

    if color_similarity > 0.6:
        recs.append({
            "id": "change_palette",
            "text": "Change the color palette to reduce visual similarity with the original chart.",
            "category": "color",
            "auto_applicable": True,
            "priority": "high" if color_similarity > 0.8 else "medium",
        })

    if layout_similarity > 0.6:
        recs.append({
            "id": "adjust_layout",
            "text": "Adjust chart layout, spacing, or proportions to differentiate from the original.",
            "category": "layout",
            "auto_applicable": False,
            "priority": "high" if layout_similarity > 0.8 else "medium",
        })

    if geometry_similarity > 0.7:
        recs.append({
            "id": "switch_chart_type",
            "text": "Consider switching to an alternative chart type to present the data differently.",
            "category": "geometry",
            "auto_applicable": True,
            "priority": "medium",
        })

    if similarity_score > 50:
        recs.append({
            "id": "add_citation",
            "text": "Add a source citation referencing the original publication.",
            "category": "legal",
            "auto_applicable": False,
            "priority": "high",
        })

    if similarity_score > 70:
        recs.append({
            "id": "modify_styling",
            "text": "Apply significant visual modifications — different fonts, grid style, and annotations.",
            "category": "style",
            "auto_applicable": True,
            "priority": "high",
        })

    if not recs:
        recs.append({
            "id": "approved",
            "text": "The regenerated chart is sufficiently different from the original. Low copyright risk.",
            "category": "approval",
            "auto_applicable": False,
            "priority": "info",
        })

    return recs


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def score_compliance(
    original_image: np.ndarray,
    reconstructed_image: np.ndarray,
    weights: Optional[dict] = None,
) -> dict:
    """
    Run the full compliance scoring pipeline.

    Args:
        original_image: BGR numpy array of the original chart (cropped from PDF)
        reconstructed_image: BGR numpy array of the reconstructed chart

    Returns:
        {
            "similarity_score": float,   # 0-100
            "risk_level": str,           # "low" | "medium" | "high"
            "color_similarity": float,   # 0-100
            "layout_similarity": float,  # 0-100
            "geometry_similarity": float, # 0-100 (SSIM-based)
            "recommendations": [...],
        }
    """
    w = weights or WEIGHTS

    # Compute sub-scores (0.0 – 1.0)
    ssim_raw = _compute_ssim(original_image, reconstructed_image)
    color_raw = _compare_color_histograms(original_image, reconstructed_image)
    layout_raw = _compare_layout(original_image, reconstructed_image)

    # Weighted composite (0.0 – 1.0 → 0 – 100)
    composite = (
        w.get("ssim", 0.4) * ssim_raw +
        w.get("color", 0.3) * color_raw +
        w.get("layout", 0.3) * layout_raw
    )
    similarity_score = round(composite * 100, 1)

    # Sub-scores as 0-100
    color_similarity = round(color_raw * 100, 1)
    layout_similarity = round(layout_raw * 100, 1)
    geometry_similarity = round(ssim_raw * 100, 1)

    # Risk level
    if similarity_score <= RISK_THRESHOLDS["low_max"]:
        risk_level = "low"
    elif similarity_score <= RISK_THRESHOLDS["medium_max"]:
        risk_level = "medium"
    else:
        risk_level = "high"

    # Generate recommendations
    recommendations = _generate_recommendations(
        similarity_score, color_raw, layout_raw, ssim_raw,
    )

    result = {
        "similarity_score": similarity_score,
        "risk_level": risk_level,
        "color_similarity": color_similarity,
        "layout_similarity": layout_similarity,
        "geometry_similarity": geometry_similarity,
        "recommendations": recommendations,
    }

    logger.info(
        "Compliance score: %.1f (%s risk) — SSIM=%.1f, Color=%.1f, Layout=%.1f",
        similarity_score, risk_level,
        geometry_similarity, color_similarity, layout_similarity,
    )
    return result


def score_compliance_from_bytes(
    original_bytes: bytes,
    reconstructed_bytes: bytes,
) -> dict:
    """Convenience wrapper that accepts PNG/JPEG bytes."""
    arr1 = np.frombuffer(original_bytes, dtype=np.uint8)
    img1 = cv2.imdecode(arr1, cv2.IMREAD_COLOR)
    arr2 = np.frombuffer(reconstructed_bytes, dtype=np.uint8)
    img2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)

    if img1 is None or img2 is None:
        raise ValueError("Could not decode one or both images.")

    return score_compliance(img1, img2)
