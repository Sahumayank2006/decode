# Chart Sense

**Reverse-engineer chart properties from PNG images using machine learning.**

Perfect for automated testing of chart rendering engines, browser canvas validation, or analyzing charts from any source.

## 🎯 Project Vision

Transform any chart image back into its structured properties using the best extraction method for each property:

```()
PNG Chart Image  →  Multi-Method Pipeline  →  Complete Chart Properties
    ↓                        ↓                              ↓
[chart.png] → [Chart Sense] → {
                  ↓               chart_type: 'bar',        (sklearn RF)
              ┌───┴────┐          colors: ['#4ECDC4', ...],  (CV clustering)
          sklearn  Neural         labels: ['May', 'Dec'],   (OCR)
            CV     Network         values: [12.51, 83.31],  (Deep Learning)
           OCR      Vision         title: 'Overview',       (OCR)
                                   background: '#ffffff',   (CV)
                                   // ... all extractable properties
                                }
```

**Multi-Method Approach**: Each chart property uses the most effective extraction technique—computer vision for colors, sklearn for chart type classification, OCR for text, neural networks for complex visual patterns.

### Use Cases

- **🧪 Automated Testing**: Verify chart rendering in browsers/canvas
- **📊 Chart Analysis**: Extract data from any chart image  
- **🔍 QA Validation**: Compare rendered charts against specifications
- **🤖 E2E Testing**: Playwright + Chart Sense for visual validation

## 🏗️ Current Capabilities

### Implemented (trainer_1)

- **Chart Type Classification**: bar, pie, line, doughnut
  - Method: sklearn Random Forest (100% accuracy on 290 samples)
  - Model: 64×64 grayscale features → 4 chart types
  - Status: Production-ready (~500KB model)

### 🚧 In Development

- **Color Extraction**: Dominant colors and palettes (Computer Vision)
- **Text Extraction**: Titles, labels, values (OCR - Tesseract/EasyOCR)
- **Layout Analysis**: Chart structure and positioning (CV)

### 🎯 Planned (trainer_2 - Deep Learning)

- **Value Extraction**: Precise data point extraction (CNN/Vision Transformer)
- **Complex Visual Patterns**: Multi-series detection, overlapping elements
- **Style Recognition**: Themes, fonts, animation states
- **Multi-Chart Support**: Dashboards, subplots, combined charts

**Philosophy**: Use the simplest effective method for each property. sklearn for basic classification, CV for colors/layout, OCR for text, neural networks only when visual complexity demands it.

### Roadmap

- More properties
- Browser Integration (Extension)
- Playwright Plugin
- Other libraries ?

## 🚀 Quick Start

```bash
# 1. Setup common environment (from project root)
conda env create -f environment.yml
conda activate chart-sense

# 2. Install Playwright browsers
playwright install firefox

# 3. Generate training data
cd dataset-gather
python generate_dataset.py -n 500

# 4. Extract chart properties from dataset
cd ../chart-properties
python extract.py

# 5. Train chart type classifier (sklearn)
cd ../trainer_1
python sklearn_train.py

# 6. Test on new images
cd ../testing
python analyze_chart.py chart.png
```

## Evaluation/Testing Interface

### CLI Testing

```bash
cd testing
python analyze_chart.py --image chart.png --output json
```

### Browser Testing (Planned)

```bash
cd dataset-generator
npm run dev:tester  # Starts testing mode
# Upload image → See extracted properties
```

### API Testing (Planned)

```bash
curl -X POST "http://localhost:8000/analyze" \
     -F "image=@chart.png" | jq .
```

## Architecture

```()
chart-sense/
├── dataset-generator/   # 🎨 ECharts chart generator (ViteJS)
├── dataset-gather/      # 🤖 Training data automation (Python + Playwright)  
├── chart-properties/    # 📊 Property extraction pipeline
├── trainer_1/           # 🧠 ML models (sklearn + future neural nets)
└── testing/             # 🧪 CLI and browser testing tools
```

### Component Details

#### **Dataset Generator**

- **Purpose**: Generate diverse chart images with known properties
- **Tech**: ViteJS + TypeScript + Apache ECharts
- **Output**: PNG + JSON metadata pairs for training

#### **Dataset Gather**

- **Purpose**: Automate screenshot capture and metadata extraction
- **Tech**: Python + Playwright + Firefox
- **Features**: Batch generation, edge cases, reproducible seeds

#### **Chart Properties**

- **Purpose**: Normalize rich JSON metadata into ML-friendly features  
- **Tech**: Python + pandas + feature engineering
- **Output**: 21 normalized properties per chart

#### **ML Models** (In Progress)

- **trainer_1** (sklearn): Chart type classification
  - Random Forest: 100% accuracy, ~500KB model
  - Status: Production-ready
- **trainer_2** (Deep Learning): Planned for complex properties
  - Value extraction, style recognition
  - Tech: TensorFlow/PyTorch for CNNs, Vision Transformers
  - Status: Planned (requires 10,000+ samples)

## Other Notes

`conda env update -f environment.yml --prune`
