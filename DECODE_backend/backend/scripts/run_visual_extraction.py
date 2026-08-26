import os
import argparse
from pathlib import Path
import logging

from core.visual_extractor import VisualExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("run_visual_extraction")

def main():
    parser = argparse.ArgumentParser(description="Extract visual elements from PDF")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    parser.add_argument("--output_dir", type=str, default="output", help="Directory to save extracted elements")
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        logger.error(f"File not found: {pdf_path}")
        return
        
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting extraction for {pdf_path}")
    extractor = VisualExtractor(output_dir=str(output_dir))
    
    elements = extractor.extract_from_pdf(str(pdf_path))
    
    logger.info(f"Extraction complete! Extracted {len(elements)} elements.")
    logger.info(f"Check the {output_dir} directory for results.")

if __name__ == "__main__":
    main()
