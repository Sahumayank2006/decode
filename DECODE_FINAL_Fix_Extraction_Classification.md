# DECODE — FINAL Fix Required: Extraction/Classification Is Still Fabricating Results

## This is the third failed attempt. New evidence proves the numbers themselves are fake, not just the labels.

Testing `DECODE_Test_Scientific_Charts.pdf` again produced this:

| Region (actual content) | Labeled | Confidence | Reason given |
|---|---|---|---|
| **Plain title page** — just the heading "DECODE Scientific Visualization Test Document" and one sentence of description text. NO shapes, boxes, or arrows exist anywhere on this page. | "Process Diagram" | 95% | "Detected 38 arrows connecting 5 rectangular nodes." |
| **Bar chart** (Accuracy %, 3 datasets, clear rectilinear axes) | "Pie Chart" | 70% | "Detected a dominant circular contour (circularity: 0.02) divided into sectors, with no grid or rectilinear axes present." |
| Line chart + data table | "Process Diagram" | 95% | "Detected 33 arrows connecting 3 rectangular nodes." |
| Pie chart + 2 flowcharts (still merged into one crop — segmentation still broken) | "Process Diagram" | 95% | "Detected 45 arrows connecting 3 rectangular nodes." |

### Why this proves fabrication at the numeric level, not just the label level

1. **A circularity score of 0.02 was used as evidence FOR a pie chart.** Circularity
   is measured on a 0–1 scale where 1.0 = a perfect circle. A score of 0.02 means
   "almost the opposite of circular." If any real circularity computation had run,
   this score should have been treated as strong evidence AGAINST `pie_chart`,
   not for it. This proves the decision logic connecting the computed number to
   the final label is broken or absent — a number is being computed (or invented)
   but not actually being used correctly, or not used at all.

2. **A page containing ONLY text was labeled a process diagram with a specific
   arrow/node count.** There are no arrows, boxes, or any graphical shapes on
   that page whatsoever. A count of "38 arrows connecting 5 rectangular nodes"
   cannot come from any real analysis of that image. This value is invented.

3. **Arrow counts of 38, 33, and 45 are all wrong by an order of magnitude.**
   Each actual flowchart in this test PDF has exactly 2 arrows connecting 3
   boxes. Real detection — even an imperfect one — would not produce numbers
   10-20x too high, and would not produce a *different* wrong number every
   single time on similar-looking diagrams. This pattern (specific-looking
   but wildly incorrect and inconsistent numbers) is the signature of a
   **random number generator or placeholder formula** standing in for real
   detection — e.g. something like `Math.floor(Math.random() * 50)` or a
   count derived from irrelevant data (like total pixel count or file size)
   rather than actual detected arrow shapes.

**Conclusion: no real OpenCV (or equivalent) analysis is running.** Numbers
are being generated that merely *look* like real measurements. This must be
replaced with a literal, verifiable implementation — not adjusted, not
tuned, replaced.

---

## Mandatory New Requirement: Visual Proof, Not Just Numbers

Because text/number claims have now been proven fabricated three times in a
row, going forward **every region's classification must be accompanied by a
saved annotated debug image** that visually proves what was detected. This
is non-negotiable and must ship as part of the fix:

For every processed region, save an additional image (alongside the normal
crop) with the following drawn directly onto a copy of it:
- Every contour that was actually found, outlined in a bright color
- If a circle/pie candidate was checked: the detected circular contour
  outlined distinctly, with its computed circularity value printed as text
  on the image itself
- If bars were checked: each detected bar's bounding rectangle outlined,
  with a count printed on the image
- If lines were checked: each detected line segment drawn in a distinct
  color
- If arrows were checked: each detected arrowhead marked with a dot/marker,
  and a line drawn between any two shapes considered "connected"
- If a grid/table was checked: detected row and column lines drawn

This annotated image must be saved to disk (or returned to the frontend for
display) for every region, every time. This is the only way to confirm going
forward whether real detection is happening, because claimed numbers alone
have proven unreliable. If your coding tool cannot produce this annotated
image, that itself proves no real detection is occurring yet.

---

## Exact Implementation Required (do not deviate — implement literally)

Use Python + OpenCV (`cv2`) for this. For each cropped region image:

```python
import cv2
import numpy as np

def analyze_region(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    debug_image = image_bgr.copy()
    features = {
        "contour_count": len(contours),
        "circularity_scores": [],
        "rectangle_count": 0,
        "rectangles": [],
        "detected_lines": 0,
        "arrow_count": 0,
    }

    # --- Circularity check (for pie_chart candidacy) ---
    for c in contours:
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        features["circularity_scores"].append(circularity)
        if circularity > 0.8 and area > 0.15 * image_bgr.shape[0] * image_bgr.shape[1]:
            cv2.drawContours(debug_image, [c], -1, (0, 255, 0), 3)
            cv2.putText(debug_image, f"circularity={circularity:.2f}",
                        tuple(c[0][0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # --- Rectangle / bar detection ---
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / float(h) if h > 0 else 0
        approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
        if len(approx) == 4 and w > 10 and h > 10:
            features["rectangle_count"] += 1
            features["rectangles"].append((x, y, w, h))
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # --- Line segment detection (for line_chart / arrows) ---
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50,
                             minLineLength=30, maxLineGap=10)
    features["detected_lines"] = 0 if lines is None else len(lines)
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            cv2.line(debug_image, (x1,y1), (x2,y2), (0,0,255), 2)

    # --- Arrowhead detection: small triangular contours near a line endpoint ---
    arrow_heads = 0
    for c in contours:
        approx = cv2.approxPolyDP(c, 0.04 * cv2.arcLength(c, True), True)
        area = cv2.contourArea(c)
        if len(approx) == 3 and 20 < area < 400:  # small triangle = likely arrowhead
            arrow_heads += 1
            cv2.drawContours(debug_image, [c], -1, (0, 255, 255), 2)
    features["arrow_count"] = arrow_heads

    return features, debug_image
```

**Then apply this exact decision logic — do not skip steps or reorder them:**

```python
def classify_region(features):
    # 1. Process diagram / flowchart: real arrowheads found connecting real rectangles
    if features["arrow_count"] >= 1 and features["rectangle_count"] >= 2:
        return "process_diagram", (
            f"Detected {features['arrow_count']} arrowhead(s) and "
            f"{features['rectangle_count']} rectangular node(s)."
        )

    # 2. Table: many small rectangles arranged in a grid (rows AND columns
    #    of similar-sized boxes) -- check separately, do not reuse rectangle_count blindly
    # (implement grid regularity check here)

    # 3. Pie chart: only if a genuinely high circularity contour exists
    max_circularity = max(features["circularity_scores"], default=0)
    if max_circularity > 0.8 and features["rectangle_count"] == 0:
        return "pie_chart", f"Detected a circular contour with circularity {max_circularity:.2f}."

    # 4. Bar chart: multiple rectangles sharing a common baseline + no arrows
    if features["rectangle_count"] >= 2 and features["arrow_count"] == 0:
        return "bar_chart", f"Detected {features['rectangle_count']} bar-like rectangles with no connecting arrows."

    # 5. Line chart: line segments present, no rectangles, no arrows
    if features["detected_lines"] > 0 and features["rectangle_count"] == 0 and features["arrow_count"] == 0:
        return "line_chart", f"Detected {features['detected_lines']} line segment(s) with no boxes or arrows."

    # 6. If a region has almost no contours and no lines, it is plain text/whitespace
    if features["contour_count"] < 3 and features["detected_lines"] == 0:
        return "text", "No significant graphical structure detected — likely plain text."

    return "unknown", "No classification rule matched the detected features confidently."
```

**This is a starting reference implementation, not a black box to copy blindly
— tune thresholds against the real test images, but the STRUCTURE (compute
real features → save proof image → apply ordered rules using ONLY those real
features) must be followed exactly. No random numbers. No canned strings. No
guessing.**

---

## Also Fix: Plain Text Regions Should Never Reach Classification As A Chart

The title-page region (heading + one sentence, no graphics at all) should
have been filtered out at the detection stage entirely, or classified as
`text` immediately (see rule 6 above) — it should never be scored as a
"process diagram" with a fabricated arrow count. Add an early check: if a
detected region has near-zero non-text pixel density (very few contours,
mostly font-shaped small dark blobs in dense lines resembling paragraphs),
classify it as `text` before running any of the shape/arrow analysis above.

---

## Also Still Required From Before (not yet fixed): Region Splitting

Page 2 must produce 2 separate regions (line chart, AND the data table below
it) — not 1 merged region. Page 3 must produce 3 separate regions (pie
chart, AND 2 separate process diagrams) — not 1 merged region. Use connected
component / contour-cluster separation with a whitespace-gap threshold to
split these before running classification on each piece independently.

---

## Verification Checklist — Do Not Report This Fixed Until Every Item Is True

- [ ] For every region, an annotated debug image is produced showing the
      actual contours/lines/rectangles/arrowheads detected — and these
      images have been manually opened and visually confirmed to show real,
      correct detections (not blank, not random noise)
- [ ] The plain title/text page is classified `text`, not `process_diagram`,
      and has zero fabricated arrow/rectangle counts
- [ ] The bar chart page is classified `bar_chart`, with a rectangle count
      that visually matches the real number of bars in the debug image
- [ ] Page 2 produces 2 separate regions: `line_chart` and `table`
- [ ] Page 3 produces 3 separate regions: `pie_chart` and 2 ×
      `process_diagram`
- [ ] The pie chart's reported circularity score is above 0.8 (a real
      circular shape), and this number visually matches a circle actually
      outlined in its debug image
- [ ] Each process diagram's reported arrow count is exactly 2 (matching the
      real diagrams in this test file), not double-digit fabricated numbers
- [ ] No two regions produce an identical `reason` string
- [ ] Grep confirms there is no random-number generation, no hardcoded
      per-type template dictionary, and no placeholder function anywhere in
      the classification code path
- [ ] Full end-to-end re-run on `DECODE_Test_Scientific_Charts.pdf` produces
      all of the above simultaneously in one pass
