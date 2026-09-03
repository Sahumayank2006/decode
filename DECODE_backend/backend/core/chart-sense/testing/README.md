# Chart Sense Testing

Interactive tools for validating chart property extraction.

## CLI Testing

### Quick Analysis

```bash
# Analyze any chart image
python analyze_chart.py path/to/chart.png

# Get JSON output  
python analyze_chart.py chart.png --format json

# Save results to file
python analyze_chart.py chart.png --output analysis.json
```

### Example Output

```()
============================================================
📊 CHART SENSE ANALYSIS RESULTS
============================================================

📁 Image: chart.png
📐 Size: 800×600 px

🎯 Chart Type: BAR
🎲 Confidence: 98.5%

📊 All Probabilities:
  bar      ████████████████████ 98.5%
  pie      █░░░░░░░░░░░░░░░░░░░  1.2%
  line     ░░░░░░░░░░░░░░░░░░░░  0.2%
  doughnut ░░░░░░░░░░░░░░░░░░░░  0.1%

🎨 Dominant Colors:
  1. #4ECDC4
  2. #FECA57  
  3. #45B7D1
  4. #96CEB4
  5. #FF6B6B
============================================================
```

## Current Extractors

### ✅ Chart Type Classification (sklearn)

- **Method**: Random Forest on 64×64 pixel features
- **Accuracy**: 100% on test data (58 samples)
- **Types**: bar, pie, line, doughnut
- **Model**: `chart_classifier_rf.pkl` (trainer_1)
- **Inference**: <100ms on CPU

### ✅ Color Analysis (Computer Vision)

- **Method**: K-means clustering on pixel data
- **Output**: Top 5 dominant colors (hex codes)
- **Features**: Automatic background removal
- **No ML required**: Pure algorithmic approach

### 🚧 Planned Extractors

#### Text Extraction (OCR)

**Method**: Tesseract or EasyOCR

```python
# Coming soon
def extract_text(image_path):
    return {
        "title": "Performance Overview",
        "labels": ["Jan", "Feb", "Mar"],
        "legend": ["Series A", "Series B"]
    }
```

#### Value Extraction (Deep Learning - trainer_2)

**Method**: CNN or Vision Transformer  
**Dataset**: Requires 10,000+ annotated samples

```python
# Future - neural network approach
def extract_values(image_path):
    return {
        "data_points": [12.5, 83.3, 73.2],
        "axis_ranges": {"x": ["Jan", "Feb"], "y": [0, 100]},
        "estimated_precision": 1
    }
```

#### Layout Analysis (Computer Vision)

**Method**: OpenCV contour detection

```python
# Coming soon
def analyze_layout(image_path):
    return {
        "chart_area": {"x": 100, "y": 50, "width": 600, "height": 400},
        "legend_position": "right",
        "title_position": "top"
    }
```

## Testing Workflow

### 1. Test Current Capabilities

```bash
# Test on known chart types
python analyze_chart.py ../dataset-gather/dataset/000001.png

# Test on custom chart
python analyze_chart.py my_chart.png --verbose
```

### 2. Validate Against Ground Truth

```bash
# Compare extracted properties with original JSON metadata
python validate_extraction.py ../dataset-gather/dataset/
```

### 3. Browser Testing (Future)

```bash
# Start browser-based tester
cd ../dataset-generator
npm run dev:tester
# Upload image → see extracted properties in real-time
```

## Adding New Test Cases

1. **Create test images** in `test_images/`
2. **Add ground truth** in `test_images/expected_results.json`
3. **Run validation** with `python validate_extraction.py test_images/`

## Integration with Development Workflow

### For Browser Testing

```javascript
// In your web app - multi-method extraction
const formData = new FormData();
formData.append('image', canvasBlob);

fetch('/analyze', {method: 'POST', body: formData})
  .then(r => r.json())
  .then(properties => {
    // Chart type from sklearn
    assert.equal(properties.chart_type, 'bar');
    
    // Colors from CV clustering
    assert.deepEqual(properties.colors, expectedColors);
    
    // Text from OCR
    assert.equal(properties.title, 'Expected Title');
    
    // Values from neural network (future)
    assert.deepEqual(properties.values, expectedValues);
  });
```

### For E2E Testing  

```python
# Playwright + Chart Sense
def test_chart_rendering():
    page.goto('http://localhost:3000/charts')
    
    # Take screenshot
    chart_image = page.screenshot()
    
    # Analyze with Chart Sense
    properties = analyze_chart(chart_image)
    
    # Validate
    assert properties['chart_type'] == 'bar'
    assert len(properties['colors']) >= 3
```
