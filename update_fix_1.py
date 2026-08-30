import os

file_path = 'Decode_backend/backend/core/chart_extractor.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('# Public API')
if idx == -1:
    print('Error: # Public API not found in chart_extractor.py')
else:
    # We want to replace from `# Public API` to the end of the file.
    # We need to find the start of the comment block `# ───` above `# Public API`.
    block_start = text.rfind('# ───', 0, idx)
    if block_start == -1:
        block_start = idx
    
    prefix = text[:block_start]
    
    new_public_api = """# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

_EXTRACTORS = {
    "bar_chart": _extract_bar_chart,
    "line_chart": _extract_line_chart,
    "pie_chart": _extract_pie_chart,
    "scatter_plot": _extract_scatter_chart,
    "table": _extract_table,
    "table_chart": _extract_table,

    # backwards compatibility
    "bar": _extract_bar_chart,
    "line": _extract_line_chart,
    "pie": _extract_pie_chart,
    "scatter": _extract_scatter_chart,
}


def _safe_point_count(series: list[dict]) -> int:
    total = 0

    for s in series or []:
        points = s.get("points", [])

        if isinstance(points, list):
            total += len(points)

    return total


def _looks_like_pie_chart(img_bgr) -> bool:
    \"\"\"
    Conservative visual check for circular/pie charts.

    This is deliberately independent of OCR.
    \"\"\"
    try:
        import cv2
        import numpy as np
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=max(30, min(img_bgr.shape[:2]) // 5),
            param1=100,
            param2=35,
            minRadius=max(20, min(img_bgr.shape[:2]) // 8),
            maxRadius=max(30, min(img_bgr.shape[:2]) // 2),
        )

        if circles is None:
            return False

        h, w = img_bgr.shape[:2]
        image_area = h * w

        for circle in np.round(circles[0]).astype(int):
            _, _, radius = circle
            area = math.pi * radius * radius

            if image_area > 0 and area / image_area >= 0.08:
                return True

    except Exception as exc:
        logger.debug("Pie detection failed: %s", exc)

    return False


def _bar_visual_score(img_bgr) -> float:
    \"\"\"
    Detect filled vertical/horizontal bar-like regions.

    Returns a score in [0, 1].
    \"\"\"
    try:
        import cv2
        import numpy as np
        h, w = img_bgr.shape[:2]

        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # Colored / non-gray pixels.
        mask = cv2.inRange(
            hsv,
            np.array([0, 45, 45]),
            np.array([180, 255, 255]),
        )

        # Remove tiny noise.
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (5, 5),
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel,
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        bar_count = 0

        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            if area < h * w * 0.003:
                continue

            if bh < h * 0.08:
                continue

            if bw > w * 0.30:
                continue

            aspect = bh / max(bw, 1)

            # Typical vertical bar.
            if aspect >= 0.8:
                bar_count += 1

        return min(1.0, bar_count / 4.0)

    except Exception as exc:
        logger.debug("Bar visual analysis failed: %s", exc)
        return 0.0


def _line_visual_score(img_bgr) -> float:
    \"\"\"
    Detect evidence of colored/continuous line traces.
    \"\"\"
    try:
        import cv2
        import numpy as np
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(
            hsv,
            np.array([0, 60, 50]),
            np.array([180, 255, 255]),
        )

        h, w = img_bgr.shape[:2]

        # Thin morphology keeps line-like structures.
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 3),
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel,
        )

        edges = cv2.Canny(mask, 50, 150)

        lines = cv2.HoughLinesP(
            edges,
            1,
            np.pi / 180,
            threshold=max(20, w // 20),
            minLineLength=max(25, w // 10),
            maxLineGap=20,
        )

        if lines is None:
            return 0.0

        meaningful = 0

        for line in lines[:, 0]:
            x1, y1, x2, y2 = line

            length = math.sqrt(
                (x2 - x1) ** 2 +
                (y2 - y1) ** 2
            )

            if length > w * 0.08:
                meaningful += 1

        return min(1.0, meaningful / 8.0)

    except Exception as exc:
        logger.debug("Line visual analysis failed: %s", exc)
        return 0.0


def _infer_generic_chart_type(
    cropped_image,
    axis_info: dict,
) -> str:
    \"\"\"
    Infer a useful chart type when PDF/vector detection only says "chart".

    Priority:
      1. Pie/circular evidence
      2. Bar evidence
      3. Line evidence
      4. OCR axis evidence
      5. Safe bar fallback

    This does not fabricate data. It only selects which existing
    computer-vision extractor should be attempted.
    \"\"\"

    if _looks_like_pie_chart(cropped_image):
        logger.info(
            "[generic-chart] visual classifier selected pie_chart"
        )
        return "pie_chart"

    bar_score = _bar_visual_score(cropped_image)
    line_score = _line_visual_score(cropped_image)

    logger.info(
        "[generic-chart] visual scores bar=%.3f line=%.3f",
        bar_score,
        line_score,
    )

    x_ticks = axis_info.get("x_ticks", [])
    y_ticks = axis_info.get("y_ticks", [])

    if bar_score >= 0.35:
        return "bar_chart"

    if line_score >= 0.25 and len(x_ticks) >= 2:
        return "line_chart"

    # Strong numeric Y-axis + categorical X-axis is usually a bar/column
    # chart in the current DECODE test corpus.
    if len(y_ticks) >= 2 and len(x_ticks) >= 2:
        return "bar_chart"

    # Safe final attempt.
    return "bar_chart"


def _normalise_chart_type(value: object) -> str:
    \"\"\"
    Normalise detector/Chart-Sense names into our extractor names.
    \"\"\"
    value = str(value or "").strip().lower()

    aliases = {
        "chart": "chart",
        "figure": "chart",
        "other": "chart",
        "other_chart": "chart",
        "unknown": "chart",

        "bar": "bar_chart",
        "bar_chart": "bar_chart",
        "column": "bar_chart",
        "column_chart": "bar_chart",

        "line": "line_chart",
        "line_chart": "line_chart",
        "line_plot": "line_chart",

        "pie": "pie_chart",
        "pie_chart": "pie_chart",

        "scatter": "scatter_plot",
        "scatter_plot": "scatter_plot",

        "table": "table",
        "table_chart": "table",
    }

    return aliases.get(value, value)


def _compose_extraction_result(
    extraction: dict,
    axis_info: dict,
    raw_text: str,
) -> dict:

    series = extraction.get("series", []) or []

    confidence = 0.0

    if series:
        has_x = bool(
            axis_info.get("x_ticks")
            or axis_info.get("x_label")
        )

        has_y = bool(
            axis_info.get("y_ticks")
            or axis_info.get("y_label")
        )

        base_conf = float(
            extraction.get(
                "extraction_confidence",
                0.5,
            ) or 0.5
        )

        bonus = 0.0

        if has_x:
            bonus += 0.10

        if has_y:
            bonus += 0.10

        if axis_info.get("legend_pairs"):
            bonus += 0.10

        if axis_info.get("title"):
            bonus += 0.05

        confidence = min(
            0.95,
            base_conf + bonus,
        )

    legend = []

    for s in series:
        legend.append({
            "name": s.get("name", "Series"),
            "color": s.get("color", "#333333"),
        })

    if not legend:
        for lp in axis_info.get("legend_pairs", []):
            legend.append({
                "name": lp.get("name", "Series"),
                "color": lp.get("color", "#333333"),
            })

    return {
        "series": series,
        "axis_labels": {
            "x_label": axis_info.get(
                "x_label",
                "",
            ),
            "y_label": axis_info.get(
                "y_label",
                "",
            ),
            "x_ticks": axis_info.get(
                "x_ticks",
                [],
            ),
            "y_ticks": axis_info.get(
                "y_ticks",
                [],
            ),
        },
        "legend": legend,
        "title": axis_info.get(
            "title",
            "",
        ),
        "raw_ocr_text": raw_text,
        "extraction_confidence": confidence,
    }


def extract_chart_data(
    cropped_image,
    chart_type: str = "bar",
) -> dict:
    \"\"\"
    Extract structured data from a chart.

    Important:
    Generic detector output "chart" is now handled by real
    visual inference instead of being silently discarded.
    \"\"\"

    if cropped_image is None or cropped_image.size == 0:
        return {
            "series": [],
            "axis_labels": {},
            "legend": [],
            "title": "",
            "raw_ocr_text": "",
            "extraction_confidence": 0.0,
        }

    h, w = cropped_image.shape[:2]

    normalized_type = _normalise_chart_type(chart_type)

    logger.info(
        "Extracting %s chart data from %dx%d image",
        normalized_type,
        w,
        h,
    )

    # ------------------------------------------------------------
    # OCR
    # ------------------------------------------------------------

    ocr_items = _ocr_region(cropped_image)

    raw_text = "\\n".join(
        item["text"]
        for item in ocr_items
    )

    logger.info(
        "Raw OCR items for chart extraction: %s",
        [
            {
                "text": item["text"],
                "bbox": item["bbox"],
            }
            for item in ocr_items
        ],
    )

    axis_info = _extract_axis_info(
        ocr_items,
        cropped_image,
    )

    # ------------------------------------------------------------
    # Generic chart classification
    # ------------------------------------------------------------

    if normalized_type == "chart":
        normalized_type = _infer_generic_chart_type(
            cropped_image,
            axis_info,
        )

        logger.info(
            "[generic-chart] resolved chart type = %s",
            normalized_type,
        )

    extractor = _EXTRACTORS.get(
        normalized_type
    )

    if extractor is None:
        logger.warning(
            "No extractor available for chart type '%s'",
            normalized_type,
        )

        return _compose_extraction_result(
            {
                "series": [],
                "extraction_confidence": 0.0,
            },
            axis_info,
            raw_text,
        )

    # ------------------------------------------------------------
    # First extraction attempt
    # ------------------------------------------------------------

    try:
        extraction = extractor(
            cropped_image,
            axis_info,
        )
    except Exception as exc:
        logger.exception(
            "Primary chart extraction failed: %s",
            exc,
        )

        extraction = {
            "series": [],
            "extraction_confidence": 0.0,
        }

    # ------------------------------------------------------------
    # Generic fallback:
    # If our inferred extractor produced nothing, try all
    # data extractors. Pick the result with the most real points.
    # ------------------------------------------------------------

    if normalized_type != "table" and _safe_point_count(
        extraction.get("series", [])
    ) == 0:

        candidates = []

        for candidate_type in (
            "bar_chart",
            "line_chart",
            "pie_chart",
        ):
            candidate_extractor = _EXTRACTORS[
                candidate_type
            ]

            try:
                candidate_result = candidate_extractor(
                    cropped_image,
                    axis_info,
                )

                candidate_series = (
                    candidate_result.get(
                        "series",
                        [],
                    )
                    or []
                )

                point_count = _safe_point_count(
                    candidate_series
                )

                candidate_conf = float(
                    candidate_result.get(
                        "extraction_confidence",
                        0.0,
                    )
                    or 0.0
                )

                if point_count > 0:
                    candidates.append(
                        (
                            point_count,
                            candidate_conf,
                            candidate_type,
                            candidate_result,
                        )
                    )

            except Exception as exc:
                logger.debug(
                    "Fallback extractor %s failed: %s",
                    candidate_type,
                    exc,
                )

        if candidates:
            # Prefer real point count first, then confidence.
            candidates.sort(
                key=lambda item: (
                    item[0],
                    item[1],
                ),
                reverse=True,
            )

            best = candidates[0]

            logger.info(
                "[generic-chart] fallback selected %s "
                "with %d points and confidence %.3f",
                best[2],
                best[0],
                best[1],
            )

            normalized_type = best[2]
            extraction = best[3]

    result = _compose_extraction_result(
        extraction,
        axis_info,
        raw_text,
    )

    # Expose the resolved type for the pipeline.
    result["resolved_chart_type"] = normalized_type

    logger.info(
        "Extracted %d series, %d total points, confidence %.2f",
        len(result["series"]),
        _safe_point_count(result["series"]),
        result["extraction_confidence"],
    )

    return result
"""
    
    final_text = prefix + new_public_api
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
    print('Updated chart_extractor.py successfully')
