import fitz
import cv2
import numpy as np
import re
from core.visual_extractor import VisualExtractor
from core.chart_extractor import _ocr_region, _find_legend_pairs, _extract_dominant_colors

doc = fitz.open('static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf')
page = doc[0]
pix = page.get_pixmap(dpi=200)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
if pix.n >= 3:
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

# Crop element 0
extractor = VisualExtractor(dpi=200)
elems = extractor.extract_from_pdf('static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf')
x0, y0, x1, y1 = elems[0]['bbox']
crop = img[y0:y1, x0:x1]

ocr_items = _ocr_region(crop)
print("OCR ITEMS ON ELEMENT 0:")
for it in ocr_items:
    print("  ", it["text"], "-> bbox:", it["bbox"])

# Legend items
legend_items = []
legend_indices = set()
for i, it in enumerate(ocr_items):
    t = it["text"].strip()
    if re.match(r'^(Dataset|Series|Group)\s+[A-Z0-9]', t, re.IGNORECASE):
        legend_items.append({"name": t, "idx": i, "bbox": it["bbox"]})
        legend_indices.add(i)
print("Detected Legend Items:", [li["name"] for li in legend_items])

# Title
title_items = []
for i, it in enumerate(ocr_items):
    t = it["text"].strip()
    if re.match(r'^(Figure|Chart|Table)\s+\d+', t, re.IGNORECASE) or it["bbox"][1] < crop.shape[0] * 0.15:
        if i not in legend_indices:
            title_items.append(t)
            legend_indices.add(i)
print("Detected Title:", " ".join(title_items))

# Y-ticks and Y-label
y_ticks = []
y_label = ""
for i, it in enumerate(ocr_items):
    if i in legend_indices: continue
    t = it["text"].strip()
    cx = (it["bbox"][0] + it["bbox"][2]) / 2
    if cx < crop.shape[1] * 0.20:
        if re.match(r'^\d+(\.\d+)?$', t):
            y_ticks.append({"val": float(t), "y": (it["bbox"][1] + it["bbox"][3]) / 2})
        else:
            y_label = t
y_ticks.sort(key=lambda y: y["y"])
print("Detected Y-ticks:", [yt["val"] for yt in y_ticks], "Y-label:", y_label)

# X-axis Categories and X-label
x_axis_y = int(crop.shape[0] * 0.75)
x_cats = []
x_label = ""
for i, it in enumerate(ocr_items):
    if i in legend_indices: continue
    t = it["text"].strip()
    cy = (it["bbox"][1] + it["bbox"][3]) / 2
    cx = (it["bbox"][0] + it["bbox"][2]) / 2
    if cx > crop.shape[1] * 0.20:
        if "synthetic" in t.lower() or "testing only" in t.lower():
            continue
        if cy > x_axis_y + 10:
            if t.lower() in ["method", "model", "epoch", "category"]:
                x_label = t
            elif t not in [li["name"] for li in legend_items]:
                x_cats.append({"text": t, "x": cx})
x_cats.sort(key=lambda c: c["x"])
print("Detected Categories:", [c["text"] for c in x_cats], "X-label:", x_label)
