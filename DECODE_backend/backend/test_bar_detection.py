import fitz
import cv2
import numpy as np
from core.visual_extractor import VisualExtractor
from core.chart_extractor import _extract_bar_chart, _extract_axis_info, _ocr_region

doc = fitz.open('static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf')
page = doc[0]
pix = page.get_pixmap(dpi=200)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
if pix.n >= 3:
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

extractor = VisualExtractor(dpi=200)
elems = extractor.extract_from_pdf('static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf')
x0, y0, x1, y1 = elems[0]['bbox']
crop = img[y0:y1, x0:x1]

h, w = crop.shape[:2]
gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)

# Remove horizontal grid lines
h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(w * 0.08), 1))
h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel)
binary_no_grid = cv2.subtract(binary, h_lines)

contours, _ = cv2.findContours(binary_no_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Total contours found: {len(contours)}")

bars = []
for cnt in contours:
    x, y, bw, bh = cv2.boundingRect(cnt)
    if bw >= 12 and bh >= 30 and bw < w * 0.15 and bh > bw * 0.8:
        bars.append({"x": x, "y": y, "w": bw, "h": bh, "top_y": y})

bars.sort(key=lambda b: b["x"])
print(f"Detected Bars: {len(bars)}")
for b in bars:
    print(f"  Bar at x={b['x']}, y={b['y']}, w={b['w']}, h={b['h']}")
