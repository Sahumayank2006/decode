import sys
import os
from pathlib import Path
import logging

logger = logging.getLogger("decode.chart_sense_service")

# Dynamically add chart-sense/testing to sys.path to allow importing despite hyphens
CHART_SENSE_DIR = Path(__file__).parent.parent / "core" / "chart-sense"
TESTING_DIR = CHART_SENSE_DIR / "testing"

if str(TESTING_DIR) not in sys.path:
    sys.path.insert(0, str(TESTING_DIR))

try:
    from analyze_chart import ChartAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError as e:
    logger.error("Failed to import ChartAnalyzer from chart-sense: %s", e)
    ANALYZER_AVAILABLE = False


class ChartSenseService:
    def __init__(self):
        self.analyzer = None
        if ANALYZER_AVAILABLE:
            try:
                self.analyzer = ChartAnalyzer()
            except Exception as e:
                logger.error("Failed to initialize ChartAnalyzer: %s", e)

    def analyze(self, image_path: str) -> dict:
        """
        Analyze the chart PNG and return its properties.
        """
        if not self.analyzer:
            logger.warning("ChartAnalyzer not available. Returning default properties.")
            return {
                "chart_type": "other_chart",
                "properties": {}
            }

        try:
            results = self.analyzer.analyze_chart(image_path)
            
            # Extract useful properties
            chart_type_info = results.get("extracted_properties", {}).get("chart_type_analysis", {})
            color_info = results.get("extracted_properties", {}).get("color_analysis", {})
            
            # Ensure it falls back gracefully if the model isn't trained
            final_type = chart_type_info.get("chart_type", "other_chart")
            if final_type == "unknown" or "error" in chart_type_info:
                final_type = "other_chart"
                
            return {
                "chart_type": final_type,
                "properties": {
                    "colors": color_info.get("colors", []),
                    "color_counts": color_info.get("color_counts", []),
                }
            }
        except Exception as e:
            logger.error("Error during chart-sense analysis: %s", e)
            return {
                "chart_type": "other_chart",
                "properties": {}
            }

# Singleton instance
chart_sense_service = ChartSenseService()

def analyze_chart_with_sense(image_path: str) -> dict:
    return chart_sense_service.analyze(image_path)
