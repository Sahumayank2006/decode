import fitz
import cv2
import numpy as np
from core.visual_extractor import VisualExtractor
from core.chart_extractor import extract_chart_data, _infer_generic_chart_type, _extract_axis_info, _ocr_region

extractor = VisualExtractor(dpi=200)
pdf_path = 'static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf'
elements = extractor.extract_from_pdf(pdf_path)
print(f"Total elements detected: {len(elements)}")

doc = fitz.open(pdf_path)
for i, elem in enumerate(elements):
    page = doc[elem['page_number'] - 1]
    pix = page.get_pixmap(dpi=200)
    page_img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    if pix.n == 4:
        page_img = cv2.cvtColor(page_img, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3:
        page_img = cv2.cvtColor(page_img, cv2.COLOR_RGB2BGR)

    x0, y0, x1, y1 = elem['bbox']
    crop = page_img[max(0, y0):min(pix.h, y1), max(0, x0):min(pix.w, x1)]

    res = extract_chart_data(crop, elem['type'], raw_table_data=elem.get('table_data'))
    print(f"\n--- ELEMENT {i} (Page {elem['page_number']}, Type: {elem['type']} -> {res.get('resolved_chart_type')}) ---")
    print(f"Title: {res.get('title')}")
    print(f"Confidence: {res.get('extraction_confidence')}")
    print(f"Categories: {res.get('categories')}")
    print(f"Series count: {len(res.get('series', []))}")
    for s in res.get('series', []):
        vals = [p.get('value') for p in s.get('points', [])]
        print(f"  Series '{s.get('name')}': {vals}")
