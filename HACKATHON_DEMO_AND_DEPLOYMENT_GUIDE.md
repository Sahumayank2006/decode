# 🚀 DECODE – Hackathon Mentor Showcase & Free Deployment Guide

> **Autonomous PDF Visual Extraction, Copyright Compliance & Reactive Reconstruction Engine**  
> *100% Free & Open-Source Stack · Zero External API Key Dependencies · Production-Ready Local & Cloud Deployment*

---

## 📌 1. Project Overview & Pitch for Mentors

### **What is DECODE?**
Scientific research papers, financial prospectuses, and academic reports trap millions of critical data visualizations inside static, rasterized PDF pages. 

**DECODE** solves this problem through an end-to-end autonomous pipeline:
1. **Multi-Page Visual Detection**: Scans multi-page PDFs at high resolution (200 DPI) using computer vision (`PyMuPDF` + `OpenCV`) to detect bar charts, line plots, data tables, and architectural diagrams.
2. **Precision Extraction & OCR**: Disconnects gridlines, extracts contours, groups multi-series clusters, calibrates pixel positions against Y-axis ticks, and runs deep-learning text recognition (`EasyOCR`).
3. **Canonical Reconstruction & Normalization**: Transforms raw pixel coordinates into standard canonical JSON data structures.
4. **Copyright Compliance & Similarity Scoring**: Computes visual Structural Similarity Index (`SSIM`), color histogram correlation, and spatial bounding box similarity to assess IP reuse risk.
5. **Interactive Live Workspace**: Provides a bidirectional spreadsheet/table editor with instant live chart re-rendering across **9 visualization types** (Grouped Bar, Stacked Bar, Line, Area, Pie, Donut, Radar, Table, and Original visual crop) plus one-click vector **SVG** and high-res **PNG** downloads.

---

## 🎬 2. Step-by-Step 2-Minute Demo Script for Judges & Mentors

Follow this flow when presenting to mentors to deliver maximum impact:

```
+--------------------+      +--------------------+      +--------------------+
| 1. Upload PDF      | ---> | 2. Pipeline Stages | ---> | 3. Artifact Gallery|
| Drag sample paper  |      | Watch live progress|      | Select Chart/Table |
+--------------------+      +--------------------+      +--------------------+
                                                                  |
                                                                  v
+--------------------+      +--------------------+      +--------------------+
| 6. Export SVG/PNG  | <--- | 5. Edit Live Data  | <--- | 4. Inspect & Gauge |
| Instant vector DL  |      | Change cell values |      | Review Compliance  |
+--------------------+      +--------------------+      +--------------------+
```

### **Step 1: Upload the Test PDF**
1. Open the frontend at `http://localhost:3000` (or your deployed URL).
2. Drag and drop the included sample PDF: `DECODE_backend/backend/static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf` (or any scientific PDF).
3. **Showcase to Mentor**: Point out the live pipeline progression stages (`Ingesting` → `Detecting` → `Extracting` → `Reconstructing` → `Scoring` → `Done`).

### **Step 2: Explore Detected Artifacts**
1. Once completed, notice the **Detected Visual Artifacts Gallery**:
   * **Page 1**: Grouped Bar Chart (*Figure 1. Model Performance Across Experimental Conditions*)
   * **Page 2**: Data Table (*Table 1: Training and Validation Metrics Progression*)
   * **Page 2**: Convergence Line Plot (*Training & Validation Loss Dynamics*)
   * **Page 3**: System Pipeline Diagram (*DECODE Architecture Pipeline*)
2. Highlight the **96%+ average extraction confidence** badge on each item.

### **Step 3: Interactive Visual Switching**
1. Click on the **Figure 1** chart card.
2. Demonstrate instant zero-recomputation switching using the mode toolbar:
   * Click **Bar** → Displays multi-series grouped bars (Baseline, Enhanced, Hybrid, DECODE).
   * Click **Stacked** → Stacks the series with smooth corner radii.
   * Click **Line** → Renders comparative multi-series line curves.
   * Click **Area** → Renders translucent gradient area envelopes.
   * Click **Radar** → Plots multi-dimensional categorical radar points.
   * Click **Table View** → Renders the high-precision tabular matrix with styled headers, alternating rows, and summary metrics.
   * Click **Original** → Compares side-by-side with the exact high-res PDF visual crop.

### **Step 4: Live Bidirectional Table Editing & Custom Data Import**
1. Scroll down to the **Interactive Table & Data Series Editor**.
2. Change a cell value (e.g., change `Baseline` from `76.39` to `95.00`).
3. **Watch the live chart update instantaneously** with zero latency.
4. Click **Import Data (CSV/JSON)** in the header → Upload any `.csv` or `.json` file to instantly replace or extend the workspace data.
5. Click **Add Row** or **Add Series** to demonstrate full dynamic matrix capabilities.
6. Use **Undo** / **Redo** buttons to demonstrate history stack rollback.

### **Step 5: Copyright Compliance Gauge & Multi-Format Exports**
1. Point to the **Copyright Compliance Analysis** card showing **Overall Similarity (47%)**, **Structural SSIM**, and **Color Distribution**.
2. Click **SVG** → Instantly downloads crisp vector graphic (`.svg`).
3. Click **PNG** → Instantly downloads high-res raster graphic (`.png`) on dark canvas.
4. Click **CSV** → Downloads clean tabular data for Excel/Google Sheets.
5. Click **Export All Artifacts** in the top header → Downloads the complete `DECODE_Complete_Document_Package.json` with all 4 detected charts, compliance reports, and full metadata!

---

## 💻 3. Running Locally (Quickstart in 2 Commands)

### **Prerequisites**
* Python 3.10+
* Node.js 18+

### **Terminal 1: Backend Server**
```bash
# Navigate to backend directory
cd DECODE_backend/backend

# Install dependencies (all open-source, PyMuPDF, OpenCV, EasyOCR, Flask)
pip install -r requirements.txt

# Start the Flask API on port 5000
python app.py
```
> Backend runs at: `http://localhost:5000` (Mock database mode active by default, 0 config needed).

### **Terminal 2: Frontend Client**
```bash
# Navigate to frontend directory
cd decode-frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
> Frontend opens at: `http://localhost:3000`

---

## ☁️ 4. 100% Free Cloud Deployment Options

You can deploy the complete stack online for **free** without providing any credit card.

---

### **Option A: Instant Local Tunneling (Easiest for Live Mentor Demos)**

If you want mentors to immediately test on their phones or laptops without cloud setup:

1. Install [ngrok](https://ngrok.com/) or [Cloudflare Tunnel (cloudflared)](https://developers.cloudflare.com/pages/how-to/preview-with-cloudflare-tunnel/).
2. Run tunnel for backend:
   ```bash
   ngrok http 5000
   ```
   *Copy your generated URL (e.g., `https://backend-xyz.ngrok-free.app`).*
3. Update `decode-frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=https://backend-xyz.ngrok-free.app/api/v1
   ```
4. Run tunnel for frontend:
   ```bash
   ngrok http 3000
   ```
   *Share the frontend URL with your mentors!*

---

### **Option B: Vercel (Frontend) + Render / Railway / Hugging Face (Backend)**

#### **1. Deploy Frontend on Vercel (Free)**
1. Push your repository to GitHub.
2. Go to [Vercel](https://vercel.com) and click **Add New Project**.
3. Select your repository and set the **Root Directory** to `decode-frontend`.
4. Add the Environment Variable:
   * `NEXT_PUBLIC_API_URL`: `https://<your-backend-url>/api/v1`
5. Click **Deploy**.

#### **2. Deploy Backend on Render (Free Web Service)**
1. Go to [Render](https://render.com) and create a **New Web Service**.
2. Connect your GitHub repository.
3. Configure settings:
   * **Root Directory**: `DECODE_backend/backend`
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
4. Add Environment Variables:
   * `PORT`: `5000`
   * `DEBUG`: `false`
5. Click **Create Web Service**.

#### **3. Alternative: Deploy Backend on Hugging Face Spaces (Free CPU & PyTorch)**
Because Hugging Face Spaces provides free high-performance CPU instances with pre-configured PyTorch and OpenCV:
1. Create a new **Space** on [Hugging Face](https://huggingface.co/spaces) with SDK set to **Docker** or **Gradio/Flask**.
2. Upload the `DECODE_backend/backend` folder.
3. It exposes a free HTTPS endpoint ready for Next.js!

---

## 🛠️ 5. Technology Stack & Key Highlights

| Layer | Technologies Used | Key Benefits |
| :--- | :--- | :--- |
| **Frontend UI** | Next.js 16 (App Router), React 19, TailwindCSS, Framer Motion, Lucide Icons | Smooth glassmorphic aesthetics, ultra-responsive dark mode |
| **Interactive Visuals** | Recharts, Native SVG DOM Serialization, Canvas Pixmap Engine | 9 chart modes, sub-millisecond live updates, instant downloads |
| **PDF Extraction** | PyMuPDF (`fitz`), OpenCV (`cv2`) | 200 DPI multi-page rendering, contour clustering, gridline removal |
| **OCR & Calibration** | EasyOCR (PyTorch) | Deep learning text recognition with zero third-party API costs |
| **Compliance Engine** | Structural Similarity (`SSIM`), Color Histograms | Automated copyright IP transformation analysis |
| **Backend API** | Flask, Flask-CORS, In-Memory Mock Store | Zero setup friction, robust fallback strategies |

---

## 🏆 6. Mentor Q&A Cheat Sheet

* **Q: Does DECODE require any paid API keys (OpenAI, Gemini, AWS)?**  
  * **A**: *No. DECODE runs a 100% self-contained computer vision, OCR, and reconstruction pipeline locally using open-source deep learning and geometry algorithms.*

* **Q: How does DECODE ensure extracted data accuracy?**  
  * **A**: *We use a 3-layer verification system: (1) native PDF structural text extraction, (2) morphological gridline separation and contour clustering, and (3) pixel-to-Y-axis tick calibration with fallback inference.*

* **Q: What if the chart type detection is ambiguous?**  
  * **A**: *Our canonical data representation is visualization-agnostic. The user can switch between Bar, Stacked, Line, Area, Radar, Table, and Pie views instantly without re-processing.*

* **Q: How does copyright compliance work?**  
  * **A**: *DECODE computes pixel-level SSIM, chromatic histograms, and layout matrices between the original raster crop and the regenerated vector visualization, giving content creators a clear IP risk assessment score.*
