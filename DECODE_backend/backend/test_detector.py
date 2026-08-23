import sys
import logging
logging.basicConfig(level=logging.INFO)
from core.chart_detector import detect_charts_in_pdf

pdf_path = r'c:\Users\licsa\Downloads\decode-main\decode-main\DECODE_backend\backend\static\uploads\17fa8048_DECODE_Test_Scientific_Charts.pdf'
import os
print(os.path.abspath(pdf_path))
try:
    result = detect_charts_in_pdf(pdf_path)
    for chart in result['charts']:
        print(f"Page {chart['page_number']}: {chart['chart_type']} ({chart['confidence']}) - {chart['reason']}")
except Exception as e:
    import traceback
    traceback.print_exc()
