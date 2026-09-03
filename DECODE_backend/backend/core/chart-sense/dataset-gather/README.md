# Dataset Gather

Python-based dataset generation tool using Playwright to capture Apache ECharts visualizations.

## Setup

### Prerequisites

1. Activate the project conda environment (see root README)
2. Install Playwright browsers:

```bash
playwright install firefox
```

### Start Chart Generator Server

In a separate terminal:

```bash
cd ../dataset-generator
bun run dev
# Should be running at http://localhost:5173
```

## Usage

### Generate Dataset

Generate 100 samples with Firefox (default):

```bash
python generate_dataset.py
```

Generate with specific browser:

```bash
# Firefox (recommended)
python generate_dataset.py -b firefox

# Chromium
python generate_dataset.py -b chromium

# WebKit (Safari)
python generate_dataset.py -b webkit
```

Generate custom number of samples:

```bash
python generate_dataset.py -n 1000 -b firefox
```

Generate with headful browser (for debugging):

Edit `generate_dataset.py` and change `headless=True` to `headless=False`

### Verify Dataset

Check dataset integrity:

```bash
python generate_dataset.py --verify
```

## Output

Dataset files are saved in the `dataset/` directory:

- `000000.png` - Chart image (600x400px)
- `000000.json` - ECharts configuration (ground truth)
- `000001.png` / `000001.json`
- ... and so on

## File Structure

```()
dataset-gather/
├── generate_dataset.py    # Main generation script
├── README.md             # This file
└── dataset/              # Generated data (gitignored)
    ├── 000000.png
    ├── 000000.json
    └── ...
```
