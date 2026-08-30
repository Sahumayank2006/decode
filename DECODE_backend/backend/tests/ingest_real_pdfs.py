from pathlib import Path
import shutil


SOURCE_DIR = Path("tests/real_pdf_source")

CORPUS = {
    "research_papers": [
        "paper",
        "research",
        "journal",
        "conference",
    ],
    "annual_reports": [
        "annual",
        "financial",
        "investor",
        "report",
    ],
    "government": [
        "government",
        "gov",
        "ministry",
        "india",
        "policy",
    ],
    "scanned": [
        "scan",
        "scanned",
    ],
}


def classify_pdf(pdf_path: Path) -> str:
    name = pdf_path.name.lower()

    for category, keywords in CORPUS.items():
        if any(keyword in name for keyword in keywords):
            return category

    return "mixed"


def ingest():
    if not SOURCE_DIR.exists():
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    corpus_root = Path("tests/corpus")

    for category in CORPUS:
        (corpus_root / category).mkdir(parents=True, exist_ok=True)

    (corpus_root / "mixed").mkdir(parents=True, exist_ok=True)

    pdfs = list(SOURCE_DIR.glob("*.pdf"))

    if not pdfs:
        print("No PDFs found.")
        print(f"Place real PDFs inside: {SOURCE_DIR.absolute()}")
        return

    for pdf in pdfs:
        category = classify_pdf(pdf)

        destination = corpus_root / category / pdf.name

        shutil.copy2(pdf, destination)

        print(
            f"[INGESTED] {pdf.name} -> {category}"
        )

    print()
    print(f"Total PDFs ingested: {len(pdfs)}")


if __name__ == "__main__":
    ingest()
