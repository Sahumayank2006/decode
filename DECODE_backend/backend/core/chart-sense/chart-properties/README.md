# Chart Properties Extractor

Extracts normalized, AI-friendly features from ECharts JSON metadata for advanced chart analysis.

## Features

✅ **20+ Normalized Properties** from rich JSON metadata  
✅ **Statistical Analysis** of data distributions  
✅ **Visual Complexity Scoring** for UI/UX analysis  
✅ **Multiple Output Formats** (CSV, Parquet, NumPy)  
✅ **ML-Ready Feature Vectors** for advanced modeling

## Extracted Properties

### Data Characteristics

- `data_size` - Number of data points
- `value_range_min/max` - Data bounds
- `value_mean/std` - Statistical measures
- `value_skewness` - Distribution shape
- `data_density` - Points per value range

### Visual Properties

- `chart_type` - bar, line, pie, doughnut
- `color_scheme` - vibrant, pastel, dark, etc.
- `num_colors` - Color palette size
- `visual_complexity` - Composite complexity score
- `background_is_white` - Background color flag

### Chart Structure

- `has_title/legend` - UI element presence
- `title_length` - Text complexity
- `num_categories` - Category count
- `is_horizontal` - Orientation (bar charts)
- `has_animation` - Animation enabled

## Usage

### Extract Properties

```bash
cd chart-properties
python extract.py
```

### Use Extracted Data

```python
import pandas as pd
import numpy as np

# Load normalized properties
df = pd.read_csv('output/chart_properties.csv')

# Load ML-ready feature vectors
features = np.load('output/feature_vectors.npy')

# Analyze patterns
print(df.groupby('chart_type')['visual_complexity'].mean())
```

## Output Structure

```()
output/
├── chart_properties.csv        # Human-readable data
├── chart_properties.parquet    # Efficient binary format
├── feature_vectors.npy         # ML-ready numeric features
├── feature_names.txt           # Feature column names
└── categorical_mappings.json   # Categorical value mappings
```

## Advanced Use Cases

### 1. Chart Complexity Analysis

```python
# Find most complex charts
complex_charts = df.nlargest(10, 'visual_complexity')
```

### 2. Data Pattern Discovery

```python
# Analyze value distributions by chart type
df.groupby('chart_type')[['value_mean', 'value_std', 'value_skewness']].describe()
```

### 3. Design Pattern Mining

```python
# Common color schemes by chart type
df.groupby(['chart_type', 'color_scheme']).size().unstack(fill_value=0)
```

### 4. Quality Scoring

```python
# Charts with good data-to-ink ratio
efficient_charts = df[(df['data_size'] >= 5) & (df['visual_complexity'] <= 3)]
```

## Integration with ML Models

The extracted features enable advanced analysis beyond chart type classification:

- **Chart Quality Scoring** - Rate design effectiveness
- **Automatic Chart Recommendation** - Suggest best chart type for data
- **Style Transfer** - Apply design patterns across charts
- **Accessibility Analysis** - Evaluate color/contrast properties
