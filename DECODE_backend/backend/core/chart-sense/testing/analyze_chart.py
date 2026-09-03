#!/usr/bin/env python3
"""
Chart Sense CLI Testing Tool

Test chart property extraction from PNG images.
Perfect for validating chart rendering or analyzing unknown charts.
"""

import argparse
import json
import sys
from pathlib import Path
import logging
from PIL import Image
import numpy as np
import joblib
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Configuration constants
@dataclass
class Config:
    """Configuration for chart analysis."""
    IMAGE_SIZE: Tuple[int, int] = (64, 64)
    WHITE_THRESHOLD: int = 240
    MAX_COLORS: int = 5
    CHART_TYPES: Tuple[str, ...] = ('bar', 'line', 'pie', 'doughnut')
    
    # Model paths (relative to this file)
    MODEL_DIR: Path = Path(__file__).parent.parent / "trainer_1"
    CHART_TYPE_MODEL: str = "chart_classifier_rf.pkl"

config = Config()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ChartAnalyzer:
    """Analyze chart images and extract properties."""

    def __init__(self):
        self.chart_type_model = None
        self.load_models()

    def load_models(self):
        """Load trained models."""
        model_path = Path(__file__).parent.parent / \
            "trainer_1" / "chart_classifier_rf.pkl"

        if model_path.exists():
            self.chart_type_model = joblib.load(model_path)
            logging.info("Loaded chart type classifier: %s", model_path)
        else:
            logging.warning("Chart type model not found: %s", model_path)
            logging.warning(
                "Run 'cd ../trainer_1 && python sklearn_train.py' first")

    def extract_chart_type(self, image_path: str) -> Dict[str, Any]:
        """Extract chart type from image."""
        if not self.chart_type_model:
            return {"error": "Chart type model not loaded"}

        try:
            # Preprocess image (same as training)
            img = Image.open(image_path).convert('RGB')
            img = img.resize((64, 64))
            img_array = np.array(img).flatten() / 255.0

            # Predict
            prediction = self.chart_type_model.predict([img_array])[0]
            probabilities = self.chart_type_model.predict_proba([img_array])[0]
            confidence = float(max(probabilities))

            # Map prediction back to label
            chart_types = ['bar', 'line', 'pie', 'doughnut']
            prediction_map = {i: chart_type for i,
                              chart_type in enumerate(chart_types)}

            return {
                "chart_type": prediction_map.get(prediction, "unknown"),
                "confidence": round(confidence, 3),
                "probabilities": {
                    chart_types[i]: round(float(prob), 3)
                    for i, prob in enumerate(probabilities)
                }
            }

        except Exception as e:
            logging.error("Error extracting chart type: %s", e)
            return {"error": str(e)}

    def extract_colors(self, image_path: str) -> Dict[str, Any]:
        """Extract dominant colors from chart image."""
        try:
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)

            # Reshape to get all pixels
            pixels = img_array.reshape(-1, 3)

            # Remove white background (assuming white is common)
            non_white_pixels = pixels[~np.all(pixels > 240, axis=1)]

            if len(non_white_pixels) == 0:
                return {"colors": [], "note": "Only white/light pixels found"}

            # Simple dominant color extraction (could use k-means for better results)
            unique_colors, counts = np.unique(
                non_white_pixels, axis=0, return_counts=True)

            # Get top 5 most common colors
            top_indices = np.argsort(counts)[-5:][::-1]
            dominant_colors = unique_colors[top_indices]

            # Convert to hex
            hex_colors = [
                f"#{r:02x}{g:02x}{b:02x}"
                for r, g, b in dominant_colors
            ]

            return {
                "colors": hex_colors,
                "color_counts": [int(counts[i]) for i in top_indices],
                "total_non_white_pixels": len(non_white_pixels)
            }

        except Exception as e:
            logging.error("Error extracting colors: %s", e)
            return {"error": str(e)}

    def analyze_chart(self, image_path: str) -> Dict[str, Any]:
        """Complete chart analysis."""
        logging.info("Analyzing chart: %s", image_path)

        if not Path(image_path).exists():
            return {"error": f"Image not found: {image_path}"}

        result = {
            "image_path": str(image_path),
            "image_size": None,
            "extracted_properties": {}
        }

        # Get image info
        try:
            img = Image.open(image_path)
            result["image_size"] = list(img.size)
            result["image_format"] = img.format
        except Exception as e:
            result["image_info_error"] = str(e)

        # Extract chart type
        chart_type_result = self.extract_chart_type(image_path)
        result["extracted_properties"]["chart_type_analysis"] = chart_type_result

        # Extract colors
        color_result = self.extract_colors(image_path)
        result["extracted_properties"]["color_analysis"] = color_result

        # TODO: Add more extractors here
        # result["extracted_properties"]["text_analysis"] = self.extract_text(image_path)
        # result["extracted_properties"]["value_analysis"] = self.extract_values(image_path)

        return result


def print_results(results: Dict[str, Any], format_type: str = "pretty"):
    """Print analysis results in specified format."""

    if format_type == "json":
        print(json.dumps(results, indent=2))
        return

    # Pretty format
    print("\n" + "="*60)
    print("📊 CHART SENSE ANALYSIS RESULTS")
    print("="*60)

    print(f"\n📁 Image: {results.get('image_path', 'Unknown')}")
    if 'image_size' in results:
        print(
            f"📐 Size: {results['image_size'][0]}×{results['image_size'][1]} px")

    props = results.get('extracted_properties', {})

    # Chart Type Analysis
    if 'chart_type_analysis' in props:
        chart_analysis = props['chart_type_analysis']
        if 'error' not in chart_analysis:
            print(
                f"\n🎯 Chart Type: {chart_analysis.get('chart_type', 'unknown').upper()}")
            print(
                f"🎲 Confidence: {chart_analysis.get('confidence', 0)*100:.1f}%")

            print(f"\n📊 All Probabilities:")
            probs = chart_analysis.get('probabilities', {})
            for chart_type, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                bar_length = int(prob * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                print(f"  {chart_type:8} {bar} {prob*100:5.1f}%")
        else:
            print(f"\n❌ Chart Type Error: {chart_analysis['error']}")

    # Color Analysis
    if 'color_analysis' in props:
        color_analysis = props['color_analysis']
        if 'error' not in color_analysis:
            colors = color_analysis.get('colors', [])
            if colors:
                print(f"\n🎨 Dominant Colors:")
                for i, color in enumerate(colors[:5], 1):
                    print(f"  {i}. {color}")
        else:
            print(f"\n❌ Color Analysis Error: {color_analysis['error']}")

    print(f"\n{'='*60}")
    print("🚀 Analysis complete! Add more extractors to get additional properties.")
    print("="*60)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze chart images and extract properties",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_chart.py chart.png
  python analyze_chart.py chart.png --format json
  python analyze_chart.py chart.png --output result.json
        """
    )

    parser.add_argument(
        "image",
        help="Path to chart image (PNG, JPG)"
    )

    parser.add_argument(
        "--format",
        choices=["pretty", "json"],
        default="pretty",
        help="Output format (default: pretty)"
    )

    parser.add_argument(
        "--output",
        help="Save results to file (JSON format)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create analyzer
    analyzer = ChartAnalyzer()

    # Analyze chart
    results = analyzer.analyze_chart(args.image)

    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logging.info("Results saved to %s", args.output)

    print_results(results, args.format)

    # Exit code based on success
    if any('error' in str(v) for v in results.get('extracted_properties', {}).values()):
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
