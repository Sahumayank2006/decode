import urllib.request
import shutil
import ssl
from pathlib import Path

TARGET_DIR = Path("tests/real_pdf_source")

# A diverse, publicly accessible collection of real PDFs for reproducible testing
PDFS = [
    # Research Papers (arXiv)
    ("https://arxiv.org/pdf/1706.03762.pdf", "research_attention_1706.03762.pdf"),
    ("https://arxiv.org/pdf/1512.03385.pdf", "research_resnet_1512.03385.pdf"),
    
    # Github hosted samples (highly reliable)
    ("https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/tracemonkey.pdf", "research_tracemonkey.pdf"),
    ("https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/160F-2019.pdf", "annual_160F_2019.pdf"),
    ("https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/bug1468166.pdf", "scanned_bug1468166.pdf"),
    ("https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/table.pdf", "government_table_sample.pdf"),
    
    # Government/Policy Reports
    ("https://files.eric.ed.gov/fulltext/ED536736.pdf", "government_education_report.pdf"),
    
    # Miscellaneous / Mixed
    ("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf", "mixed_dummy_test.pdf"),
]

def download():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("DECODE REAL PDF CORPUS DOWNLOADER")
    print("=" * 60)
    
    success = 0
    
    for url, filename in PDFS:
        dest = TARGET_DIR / filename
        if dest.exists():
            print(f"[SKIP] {filename} already exists.")
            success += 1
            continue
            
        print(f"[DOWNLOAD] {filename}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response, open(dest, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            success += 1
        except Exception as e:
            print(f"  [ERROR] Failed to download {filename}: {e}")
            
    print("-" * 60)
    print(f"Successfully secured {success}/{len(PDFS)} real PDFs.")
    print("=" * 60)

if __name__ == "__main__":
    download()
