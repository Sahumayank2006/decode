#!/usr/bin/env python3
"""
Chart Properties Extractor

Extracts normalized, AI-friendly features from ECharts JSON metadata.
Converts rich JSON configurations into structured feature vectors.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class ChartProperties:
    """Normalized chart properties for ML analysis."""
    
    # Basic identification
    chart_type: str
    seed: str
    
    # Data characteristics
    data_size: int
    value_range_min: float
    value_range_max: float
    value_spread: float  # max - min
    value_mean: float
    value_std: float
    value_skewness: float  # distribution shape
    
    # Visual properties
    color_scheme: str
    num_colors: int
    has_title: bool
    title_length: int
    has_legend: bool
    
    # Chart-specific properties
    has_axis_labels: bool
    num_categories: int
    is_horizontal: bool
    has_animation: bool
    background_is_white: bool
    
    # Advanced features
    data_density: float  # data_size / value_spread
    visual_complexity: float  # composite score
    

class ChartPropertyExtractor:
    """Extract standardized properties from ECharts JSON metadata."""
    
    # Known color schemes for normalization
    COLOR_SCHEMES = ['default', 'vibrant', 'pastel', 'dark', 'monochrome']
    
    def __init__(self):
        self.stats = {
            'processed': 0,
            'errors': 0,
            'chart_types': {},
            'color_schemes': {}
        }
    
    def extract_properties(self, json_path: str) -> Optional[ChartProperties]:
        """Extract properties from a single JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            generated_option = data.get('generatedOption', {})
            
            # Basic identification
            chart_type = metadata.get('chartType', 'unknown')
            seed = str(metadata.get('seed', ''))
            
            # Data analysis
            values = metadata.get('values', [])
            if not values:
                logging.warning(f"No values found in {json_path}")
                return None
            
            values_array = np.array(values, dtype=float)
            
            # Data characteristics
            data_size = len(values)
            value_range = metadata.get('valueRange', [0, 100])
            value_range_min, value_range_max = float(value_range[0]), float(value_range[1])
            value_spread = value_range_max - value_range_min
            value_mean = float(np.mean(values_array))
            value_std = float(np.std(values_array))
            value_skewness = float(self._calculate_skewness(values_array))
            
            # Visual properties
            color_scheme = metadata.get('colorScheme', 'default')
            colors = metadata.get('colors', [])
            num_colors = len(colors)
            
            # Title analysis
            title = generated_option.get('title', {})
            has_title = bool(title.get('text'))
            title_length = len(title.get('text', '')) if has_title else 0
            
            # Chart structure
            has_legend = 'legend' in generated_option
            has_axis_labels = bool(generated_option.get('xAxis', {}).get('data'))
            labels = metadata.get('labels', [])
            num_categories = len(labels)
            
            # Chart orientation (for bar charts)
            is_horizontal = self._is_horizontal_chart(generated_option, chart_type)
            
            # Visual settings
            has_animation = generated_option.get('animation', True)
            background_color = generated_option.get('backgroundColor', '#ffffff')
            background_is_white = background_color.lower() in ['#ffffff', '#fff', 'white']
            
            # Advanced calculations
            data_density = data_size / max(value_spread, 1)
            visual_complexity = self._calculate_visual_complexity(
                num_colors, has_title, has_legend, data_size, title_length
            )
            
            properties = ChartProperties(
                chart_type=chart_type,
                seed=seed,
                data_size=data_size,
                value_range_min=value_range_min,
                value_range_max=value_range_max,
                value_spread=value_spread,
                value_mean=value_mean,
                value_std=value_std,
                value_skewness=value_skewness,
                color_scheme=color_scheme,
                num_colors=num_colors,
                has_title=has_title,
                title_length=title_length,
                has_legend=has_legend,
                has_axis_labels=has_axis_labels,
                num_categories=num_categories,
                is_horizontal=is_horizontal,
                has_animation=has_animation,
                background_is_white=background_is_white,
                data_density=data_density,
                visual_complexity=visual_complexity
            )
            
            self._update_stats(chart_type, color_scheme)
            return properties
            
        except Exception as e:
            logging.error(f"Error processing {json_path}: {e}")
            self.stats['errors'] += 1
            return None
    
    def _calculate_skewness(self, values: np.ndarray) -> float:
        """Calculate distribution skewness."""
        if len(values) < 3:
            return 0.0
        
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return 0.0
        
        return float(np.mean(((values - mean) / std) ** 3))
    
    def _is_horizontal_chart(self, option: Dict, chart_type: str) -> bool:
        """Determine if chart is horizontally oriented."""
        if chart_type != 'bar':
            return False
        
        # Check if xAxis is value type (horizontal bars)
        x_axis = option.get('xAxis', {})
        return x_axis.get('type') == 'value'
    
    def _calculate_visual_complexity(self, num_colors: int, has_title: bool, 
                                   has_legend: bool, data_size: int, title_length: int) -> float:
        """Calculate composite visual complexity score."""
        score = 0.0
        
        # Color complexity
        score += min(num_colors / 10, 1.0) * 2
        
        # Text complexity
        if has_title:
            score += 1.0 + min(title_length / 50, 1.0)
        if has_legend:
            score += 1.0
        
        # Data complexity
        score += min(data_size / 20, 1.0) * 2
        
        return round(score, 2)
    
    def _update_stats(self, chart_type: str, color_scheme: str) -> None:
        """Update processing statistics."""
        self.stats['processed'] += 1
        self.stats['chart_types'][chart_type] = self.stats['chart_types'].get(chart_type, 0) + 1
        self.stats['color_schemes'][color_scheme] = self.stats['color_schemes'].get(color_scheme, 0) + 1
    
    def process_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Process entire dataset and return normalized properties."""
        dataset_dir = Path(dataset_path)
        json_files = list(dataset_dir.glob("*.json"))
        
        logging.info(f"Processing {len(json_files)} JSON files...")
        
        properties_list = []
        for json_file in json_files:
            props = self.extract_properties(str(json_file))
            if props:
                properties_list.append(asdict(props))
        
        df = pd.DataFrame(properties_list)
        
        logging.info(f"Extraction complete. Processed: {self.stats['processed']}, "
                    f"Errors: {self.stats['errors']}")
        logging.info(f"Chart types: {self.stats['chart_types']}")
        logging.info(f"Color schemes: {self.stats['color_schemes']}")
        
        return df
    
    def save_properties(self, df: pd.DataFrame, output_dir: str) -> None:
        """Save extracted properties in multiple formats."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save as CSV (human readable)
        csv_path = output_path / "chart_properties.csv"
        df.to_csv(csv_path, index=False)
        logging.info(f"Saved CSV: {csv_path}")
        
        # Save feature vectors as numpy (ML ready)
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        feature_vectors = df[numeric_columns].values
        np.save(output_path / "feature_vectors.npy", feature_vectors)
        
        # Save feature names
        with open(output_path / "feature_names.txt", 'w') as f:
            f.write('\n'.join(numeric_columns))
        
        logging.info(f"Saved {len(numeric_columns)} numeric features")
        
        # Save categorical mappings
        categorical_data = {}
        for col in df.select_dtypes(include=['object']).columns:
            categorical_data[col] = df[col].unique().tolist()
        
        with open(output_path / "categorical_mappings.json", 'w') as f:
            json.dump(categorical_data, f, indent=2)


def main():
    """Main extraction pipeline."""
    dataset_path = "../dataset-gather/dataset"
    output_dir = "./output"
    
    extractor = ChartPropertyExtractor()
    
    # Extract properties
    df = extractor.process_dataset(dataset_path)
    
    if df.empty:
        logging.error("No properties extracted")
        return 1
    
    # Display summary
    print("\n📊 Dataset Summary:")
    print(f"Total charts processed: {len(df)}")
    print(f"\nChart types:")
    for chart_type, count in df['chart_type'].value_counts().items():
        print(f"  {chart_type}: {count}")
    
    print(f"\nNumeric feature summary:")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    print(df[numeric_cols].describe())
    
    # Save outputs
    extractor.save_properties(df, output_dir)
    
    print(f"\n✅ Properties extracted and saved to {output_dir}/")
    print("Available formats: CSV, Parquet, NumPy arrays")
    
    return 0


if __name__ == "__main__":
    exit(main())