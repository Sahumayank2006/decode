# DECODE — Fix Required: Diagrams Misread as Bar Charts, Tables Misread as Line Charts

## Status: Detection is now CONSISTENT, which means the bug is now precisely findable — fix these two specific root causes.

Testing on a real 144-page document (cloud load balancing research) shows a
clear, repeatable pattern — not random fabrication this time, but a
systematic gap in the classification rules:

### Pattern 1 — Every box/illustration diagram is being labeled "Bar Chart"

Examples seen: "Figure 1.2: Cloud Models" (a SaaS/PaaS/IaaS layered stack
illustration), a "Hybrid Cloud" concept diagram (overlapping circles), a
cloud architecture diagram, and many similar illustrations — all labeled
`Bar Chart` with the same generic reason: *"Detected N line-like rectangles
sharing a common baseline."*

**Root cause:** the current `bar_chart` rule only checks for "multiple
rectangles + no arrows detected." It never checks for the one feature that
actually defines a bar chart: **a numeric axis with tick values next to the
bars.** An architecture diagram also has multiple rectangular boxes, so it
passes the same weak check. Also, arrow detection is clearly failing to
recognize the connectors used in many of these diagrams (they may use plain
lines, curved connectors, or thin arrows without a large filled triangular
head), so these diagrams fall through to the bar_chart rule by default
instead of being caught earlier as `process_diagram`/`diagram`.

### Pattern 2 — Real tables (e.g. "Table 1.4") are being labeled "Line Chart"

**Root cause:** the previous fix left table detection as a TODO placeholder
("implement grid regularity check here") — it was never actually built. A
table's row/column grid lines (or the aligned edges of bordered cells) are
straight lines, so they get picked up by the generic line-segment detector
and misclassified as a `line_chart`, since nothing is currently checking for
table structure specifically.

---

## Fix 1 — Bar Chart Must REQUIRE a Detected Numeric Axis (mandatory, non-negotiable)

A real bar chart always has: a baseline axis, tick marks or gridlines along
at least one axis, and OCR-readable numeric labels near that axis (e.g. "0,
20, 40, 60, 80, 100"). An architecture/illustration diagram never has this —
its "boxes" contain descriptive text labels INSIDE them (e.g. "SaaS",
"PaaS"), not numeric axis ticks BESIDE them.

**Required implementation change:**

```python
def has_numeric_axis(region_image, rectangles):
    """
    Look for a long straight line (the axis) running along one edge of the
    rectangle cluster, AND run OCR specifically in a narrow strip next to
    that line, checking whether the recognized text is predominantly
    numeric (e.g. matches patterns like r'^\d+(\.\d+)?%?$').
    Returns True only if BOTH a plausible axis line AND nearby numeric
    tick labels are found.
    """
    # 1. Find the longest near-horizontal or near-vertical line in the region
    #    (via cv2.HoughLinesP), that runs along the edge the rectangles share.
    # 2. Crop a thin strip of the image directly next to that line.
    # 3. Run OCR (pytesseract) on that strip only.
    # 4. Check: are at least 3 of the recognized text tokens purely numeric?
    # 5. Return True/False, plus the actual recognized tick values for logging.
    ...
```

**Updated bar_chart rule (replace the old one):**
```python
if (features["rectangle_count"] >= 2
    and features["arrow_count"] == 0
    and has_numeric_axis(region_image, features["rectangles"])):
    return "bar_chart", (
        f"Detected {features['rectangle_count']} bar-like rectangles "
        f"sharing a baseline, with a numeric axis showing tick values: "
        f"{detected_tick_values}."
    )
```

If `has_numeric_axis` returns False, the region must NOT be classified as
`bar_chart` even if it has multiple rectangles sharing a baseline — it must
fall through to the diagram check below instead.

---

## Fix 2 — Diagram/Illustration Detection Must Not Depend Only on Arrowhead Shape Matching

Right now, `process_diagram` is only detected when a triangular arrowhead
shape is found. Many real diagrams use thin-line connectors, curved
connectors, or simple lines without a clearly detectable filled triangle, so
this check is failing and letting these regions fall through to the (now
also broken) bar_chart rule.

**Add a second, independent signal for diagrams:** multiple separate
box-like contours (rectangles OR rounded rectangles) that each contain their
OWN internal text label (detected via OCR bounding boxes located INSIDE each
rectangle, not beside a shared axis), with NO numeric axis anywhere in the
region.

```python
def is_label_in_box_diagram(region_image, rectangles):
    """
    For each detected rectangle, run OCR restricted to inside that
    rectangle's bounding box. If most rectangles contain their own short
    text label (1-4 words, non-numeric), AND has_numeric_axis() is False
    for the region, this is strong evidence of a diagram/illustration
    rather than a chart.
    """
    ...
```

**Updated decision order (replace the previous ordering with this one):**

```python
def classify_region(region_image, features):
    # 1. Diagram/flowchart via arrows (existing check, keep it)
    if features["arrow_count"] >= 1 and features["rectangle_count"] >= 2:
        return "process_diagram", f"Detected {features['arrow_count']} arrow(s) connecting {features['rectangle_count']} labeled node(s)."

    # 2. NEW: Diagram/illustration via labeled boxes with NO numeric axis
    #    (catches diagrams whose connectors aren't detected as arrows)
    if (features["rectangle_count"] >= 2
        and is_label_in_box_diagram(region_image, features["rectangles"])
        and not has_numeric_axis(region_image, features["rectangles"])):
        return "diagram", f"Detected {features['rectangle_count']} labeled boxes with no numeric axis present — this is an illustration/diagram, not a chart."

    # 3. Table (see Fix 3 below — must run before line_chart)
    if is_table(region_image, features):
        return "table", table_reason

    # 4. Pie chart (only with genuinely high circularity, as already fixed)
    max_circularity = max(features["circularity_scores"], default=0)
    if max_circularity > 0.8 and features["rectangle_count"] == 0:
        return "pie_chart", f"Detected a circular contour with circularity {max_circularity:.2f}."

    # 5. Bar chart — NOW REQUIRES a numeric axis (Fix 1 above)
    if (features["rectangle_count"] >= 2
        and features["arrow_count"] == 0
        and has_numeric_axis(region_image, features["rectangles"])):
        return "bar_chart", f"Detected {features['rectangle_count']} bars with numeric axis ticks: {detected_ticks}."

    # 6. Line chart — must also require a detected axis, not just raw line segments
    if (features["detected_lines"] > 0
        and features["rectangle_count"] == 0
        and features["arrow_count"] == 0
        and has_numeric_axis(region_image, [])):
        return "line_chart", f"Detected {features['detected_lines']} line segment(s) with a numeric axis present."

    # 7. Plain text
    if features["contour_count"] < 3 and features["detected_lines"] == 0:
        return "text", "No significant graphical structure detected."

    return "unknown", "No classification rule matched confidently."
```

Note step 6 now also requires `has_numeric_axis` — this is exactly what
will stop a bordered table's grid lines from being misread as a line chart,
since a table's grid lines are not accompanied by numeric axis tick labels
positioned like a chart axis.

---

## Fix 3 — Implement Real Table Detection (this was never actually built — build it now)

Tables in real documents appear in two forms; detect both:

**Form A — Bordered tables (visible grid lines):**
```python
def detect_grid_lines(region_image):
    gray = cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 10)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))

    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)

    h_count = cv2.countNonZero(horizontal_lines)
    v_count = cv2.countNonZero(vertical_lines)

    # A real grid has BOTH a meaningful number of horizontal AND vertical
    # line pixels, roughly evenly spaced. Return counts + spacing regularity.
    return h_count, v_count
```

**Form B — Borderless tables (text aligned into rows/columns, no drawn lines):**
```python
def detect_text_grid(region_image):
    """
    Run OCR and get word-level bounding boxes (pytesseract image_to_data).
    Group words into rows by similar Y-coordinate.
    Within those rows, check whether word START X-coordinates repeat at
    consistent positions across multiple rows (i.e. column alignment).
    If at least 3 rows share at least 2 common column start-positions
    (within a small tolerance), this is a borderless table.
    """
    ...
```

**Combine into one check:**
```python
def is_table(region_image, features):
    h_count, v_count = detect_grid_lines(region_image)
    if h_count > 500 and v_count > 500:  # tune threshold against real samples
        return True, f"Detected a regular grid of horizontal and vertical lines (table borders)."
    if detect_text_grid(region_image):
        return True, f"Detected text aligned into a consistent row/column grid (borderless table)."
    return False, None
```

This must run as its own explicit step — not as a side effect of failing
other checks.

---

## Verification Checklist for This Round

- [ ] `has_numeric_axis()` is implemented and actually runs OCR on a strip
      next to the candidate axis line — verified by printing the actual
      recognized tick values (e.g. "0, 20, 40, 60, 80, 100") for real bar
      charts, and confirming it returns NOTHING for the diagram examples
      below
- [ ] "Figure 1.2: Cloud Models" and the "Hybrid Cloud" circles diagram are
      now classified `diagram` (or `process_diagram`), NOT `bar_chart`
- [ ] "Table 1.4" and other real tables are now classified `table`, NOT
      `line_chart`
- [ ] Real bar charts (e.g. the Accuracy % chart, any chart with genuine
      numeric Y-axis ticks) are STILL correctly classified `bar_chart` —
      confirm the axis requirement didn't break correctly-working cases
- [ ] Real line charts (with genuine numeric axes) are STILL correctly
      classified `line_chart`
- [ ] Annotated debug images (from the previous fix round) now also show:
      the detected axis line + OCR'd tick values overlaid as text, for every
      region classified as bar_chart or line_chart
- [ ] Annotated debug images show detected grid lines (or aligned text
      boxes) for every region classified as `table`
- [ ] Re-run across a sample of at least 15-20 regions from this same
      144-page document and manually spot-check that the diagram/bar-chart
      and table/line-chart confusions no longer occur anywhere in that
      sample
