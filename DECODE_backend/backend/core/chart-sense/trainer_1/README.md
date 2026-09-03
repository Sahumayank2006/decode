# Chart Sense - Machine Learning Model

sklearn-based chart type classification using Random Forest for production-ready chart recognition.

## Results

✅ **Production Model**: Random Forest achieving **100% accuracy** on test data

- **Training**: 232 samples  
- **Test**: 58 samples
- **Chart Types**: bar, line, pie, doughnut
- **Model Size**: ~500KB (chart_classifier_rf.pkl)

## Setup

Activate the project conda environment (see root README).

## Usage

### Train Random Forest Model

```bash
python sklearn_train.py
```

This will:

1. Load dataset from `../dataset-gather/dataset`
2. Preprocess images (64x64 grayscale, flatten to 12,288 features)
3. Train Random Forest classifier
4. Save model as `chart_classifier_rf.pkl`
5. Display classification report

### Use Trained Model

```python
import pickle
import numpy as np
from PIL import Image

# Load model
with open('chart_classifier_rf.pkl', 'rb') as f:
    model = pickle.load(f)

# Preprocess image
def preprocess_image(image_path):
    img = Image.open(image_path).convert('L')  # Grayscale
    img = img.resize((64, 64))                 # Resize
    return np.array(img).flatten() / 255.0     # Flatten & normalize

# Predict
features = preprocess_image('chart.png')
prediction = model.predict([features])[0]
confidence = max(model.predict_proba([features])[0])

print(f"Chart type: {prediction} (confidence: {confidence:.2f})")
```

## Model Details

- **Algorithm**: Random Forest (100 trees)
- **Features**: 12,288 (64x64 grayscale pixels)
- **Input**: PNG/JPG chart images
- **Output**: Chart type classification
- **Preprocessing**: Resize → Grayscale → Flatten → Normalize

## Deployment Options

### Browser/Client-Side

- **Model size**: ~500KB (small enough for browser)
- **Runtime**: Pyodide/WASM for Python in browser
- **Use case**: Browser extensions, client-side analysis
- **Performance**: Fast inference (no API calls)

### Server-Side API

- **Runtime**: Standard Python/FastAPI
- **Use case**: Web services, batch processing
- **Benefits**: Easier model updates, centralized logic

## Future Scaling Paths

### When to Consider Deep Learning

**Current**: Random Forest (perfect for 290 samples, 4 chart types)

**Deep Learning Threshold:**

- **Dataset size**: 10,000+ samples (vs current 290)
- **Chart types**: 15+ types (ECharts supports 20+)
- **Visual complexity**: Styled charts, annotations, overlays
- **Performance**: GPU-accelerated real-time inference

**Recommended transition:**

1. **1,000-5,000 samples**: Stick with Random Forest
2. **5,000-10,000 samples**: Consider Gradient Boosting (XGBoost)
3. **10,000+ samples**: Neural networks (CNN, Vision Transformer)

### ECharts Chart Types for Future Expansion

- Current: bar, line, pie, doughnut
- Available: scatter, radar, candlestick, heatmap, treemap, sunburst, parallel, sankey, graph, gauge, funnel, theme river, calendar

## Files

- `sklearn_train.py` - Training script for Random Forest model
- `chart_classifier_rf.pkl` - Trained model (ready for production)
