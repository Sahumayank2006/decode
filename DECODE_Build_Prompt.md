# DECODE — Full Build Prompt (Frontend + Backend + Supabase)

> Paste this entire document into your AI coding tool (Antigravity, Cursor, etc.) as the master build instruction. It is written so the tool can implement the whole project — frontend, backend, and database — as one coherent, production-quality system.

---

## 1. Project Summary

Build **DECODE**, a full-stack web application that lets a user upload a research paper or scientific PDF and automatically:

1. Detects charts, graphs, tables, and diagrams inside the PDF.
2. Extracts their underlying numeric data, axis labels, legends, and titles using OCR + computer vision.
3. Regenerates each chart as an **editable, interactive** chart (not a static image) — user can switch chart type (bar ↔ line ↔ pie ↔ heatmap), edit values, restyle colors/fonts, and export as SVG/PNG.
4. Runs a **Copyright Compliance Module** that scores structural/visual similarity between the original chart and the regenerated one, returns a risk rating (Low/Medium/High), and gives actionable fixes (change color palette, adjust layout, add citation).
5. Stores every project, document, extracted chart, and compliance result per-user, so users can come back to past work.

This must be a **real, working, deployable product** — not a mockup. Every button must work. Every page must load real data from Supabase. No dummy/placeholder data anywhere in the final build.

Build it with genuine care for code quality, UX polish, and correctness — this is going in front of a mentor/evaluator, so it needs to look and feel like a finished product, not a student prototype.

---

## 2. Tech Stack (use exactly this — do not substitute without asking)

### Frontend
- **Next.js 14+ (App Router)** with **React** and **TypeScript**
- **Tailwind CSS** for styling
- **shadcn/ui** for base components (buttons, dialogs, tables, forms, toasts)
- **Recharts** for interactive/editable in-app charts
- **Zustand or React Context** for lightweight client state (only where server state via Supabase isn't enough)
- **react-hook-form + zod** for all forms and validation
- **Lucide-react** for icons

### Backend
- **Node.js + Express** (or **FastAPI** if the extraction pipeline is Python-heavy — pick ONE and be consistent; recommend FastAPI since OCR/CV libraries are Python-native)
- **Python** processing pipeline for the AI stages:
  - **PyMuPDF (fitz)** — PDF parsing, page rendering, image extraction, bounding boxes
  - **OpenCV** — contour/edge detection for locating chart regions, geometric analysis of bars/lines/pie segments
  - **Tesseract OCR (pytesseract)** — text/label/legend extraction
  - **Matplotlib / Plotly** — server-side regeneration of charts for export (PNG/SVG)
  - An **LLM API call** (configurable provider) for: chart-type classification assistance, legend/series labeling disambiguation, and generating the "alternative chart type" recommendation
- Background job handling for long-running PDF processing (use a simple queue — e.g. Supabase's `pg_cron`/a jobs table with polling, or a lightweight worker — do NOT block HTTP requests on multi-second OCR jobs)

### Database, Auth & Storage — Supabase (all of it)
- **Supabase Postgres** — all relational data
- **Supabase Auth** — email/password + optional Google OAuth
- **Supabase Storage** — buckets for uploaded PDFs, extracted page images, and generated chart exports
- **Row Level Security (RLS)** on every table — a user must only ever see their own projects/documents/charts
- **Supabase Realtime** (optional but nice) — live-update the UI as a document moves through processing stages (Uploaded → Detecting → Extracting → Reconstructing → Scoring → Done)

Do not introduce MongoDB, Firebase, or any other database — everything lives in Supabase.

---

## 3. Supabase Schema

Design and create these tables (adjust field names as needed, but keep this structure and relationships):

```sql
-- Users are handled by Supabase Auth (auth.users). Extend with a profile table:
profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  avatar_url text,
  created_at timestamptz default now()
)

projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id) on delete cascade not null,
  name text not null,
  description text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
)

documents (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade not null,
  user_id uuid references profiles(id) on delete cascade not null,
  original_filename text not null,
  storage_path text not null,          -- Supabase Storage path to the uploaded PDF
  page_count int,
  status text not null default 'uploaded',
    -- 'uploaded' | 'detecting' | 'extracting' | 'reconstructing' | 'scoring' | 'done' | 'failed'
  error_message text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
)

charts (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade not null,
  page_number int not null,
  bounding_box jsonb not null,          -- {x, y, width, height}
  chart_type text not null,             -- 'bar' | 'line' | 'pie' | 'scatter' | 'other'
  detection_confidence numeric,
  original_image_path text,             -- Supabase Storage path to cropped original chart image
  title text,
  created_at timestamptz default now()
)

extractions (
  id uuid primary key default gen_random_uuid(),
  chart_id uuid references charts(id) on delete cascade not null,
  series jsonb not null,                -- structured: [{ name, color, points: [{label, value, confidence}] }]
  axis_labels jsonb,                    -- {x_label, y_label, x_ticks, y_ticks}
  legend jsonb,
  raw_ocr_text text,
  extraction_confidence numeric,
  created_at timestamptz default now()
)

reconstructions (
  id uuid primary key default gen_random_uuid(),
  chart_id uuid references charts(id) on delete cascade not null,
  chart_type text not null,             -- may differ from original if user/LLM changed it
  chart_config jsonb not null,          -- fully describes how to render it (Recharts-compatible)
  export_svg_path text,
  export_png_path text,
  recommended_alt_type text,            -- LLM suggestion, nullable
  recommendation_reason text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
)

compliance_scores (
  id uuid primary key default gen_random_uuid(),
  chart_id uuid references charts(id) on delete cascade not null,
  reconstruction_id uuid references reconstructions(id) on delete cascade not null,
  similarity_score numeric not null,     -- 0-100
  risk_level text not null,              -- 'low' | 'medium' | 'high'
  color_similarity numeric,
  layout_similarity numeric,
  geometry_similarity numeric,
  recommendations jsonb,                 -- array of suggested actions
  created_at timestamptz default now()
)

processing_events (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade not null,
  stage text not null,
  message text,
  created_at timestamptz default now()
)
```

**RLS policy pattern for every table**: a row is visible/editable only if `user_id` (directly, or via joining up to `documents.user_id` / `projects.user_id`) equals `auth.uid()`. Write explicit `select`, `insert`, `update`, `delete` policies — do not rely on a single blanket policy.

**Storage buckets**:
- `documents` — original uploaded PDFs (private)
- `chart-images` — cropped original chart images + generated exports (private)

Every bucket must have storage policies mirroring the RLS logic (a user can only read/write objects under their own `user_id/` prefix).

---

## 4. Backend Requirements

Build a proper API layer, not ad-hoc scripts. Structure:

```
/api
  /projects        CRUD for projects
  /documents       upload, list, get status, delete
  /documents/:id/process   kicks off the 6-stage pipeline
  /charts          list charts for a document, get single chart with extraction + reconstruction + score
  /charts/:id/reconstruct  regenerate with a new chart_type or edited data
  /charts/:id/rescore      re-run compliance scoring after user edits
  /exports/:reconstructionId  download SVG/PNG
```

For each stage of the pipeline, implement it as a **discrete, testable function/service**, not one giant script:

1. **Ingestion** — `ingestDocument(pdfPath)` → parses pages with PyMuPDF, stores page images, returns page metadata.
2. **Detection** — `detectCharts(pageImages)` → OpenCV contour/edge pass + confidence scoring, returns bounding boxes + predicted chart type per region. Anything below a confidence threshold (make this configurable, e.g. 0.55) gets flagged `needs_review: true` instead of being dropped.
3. **Extraction** — `extractChartData(croppedImage, chartType)` → runs Tesseract for text, OpenCV geometry analysis for bar/line/pie measurements, calibrates values against the OCR'd axis scale, returns the structured `series`/`axis_labels`/`legend` object with a confidence value per data point.
4. **Reconstruction** — `reconstructChart(extraction, chartType)` → produces a Recharts-compatible config for the frontend, and a Matplotlib/Plotly render for SVG/PNG export.
5. **Compliance scoring** — `scoreCompliance(originalImage, reconstructedImage)` → structural similarity (e.g. SSIM), color histogram comparison, and layout/proportion comparison; combine into one 0–100 score + risk band + specific recommendations.
6. **Evaluation/logging** — write every stage transition into `processing_events` so the frontend can show real-time progress, and so extraction accuracy / processing time can be reported back to the user per document.

**Non-negotiable backend quality bar:**
- Real error handling at every stage — a failed OCR call must mark the document `failed` with a clear `error_message`, never crash silently or return fake success.
- Idempotent processing — re-running a stage should not duplicate rows.
- Long-running work must not block HTTP responses — return immediately with a `processing` status and let the frontend poll or subscribe via Supabase Realtime.
- Environment variables for all secrets (Supabase service key, LLM API key) — never hardcoded.
- Input validation on every endpoint (file type/size limits on upload, etc.).

---

## 5. Frontend Requirements

### Pages
- **Landing / Marketing page** — clean explanation of what DECODE does, with a "Get Started" CTA. Should look professional, not like a default template — real hierarchy, real hero section, one credible visual.
- **Auth pages** — sign up, log in, forgot password (Supabase Auth UI or custom forms styled to match the rest of the app).
- **Dashboard** — list of the user's projects, "New Project" action, quick stats (documents processed, charts extracted).
- **Project view** — list of documents inside a project, upload button (drag-and-drop PDF), per-document status badge (Uploaded/Processing/Done/Failed) that updates live.
- **Document detail / processing view** — shows the pipeline stage progress (a stepper: Ingest → Detect → Extract → Reconstruct → Score → Done), and once complete, a grid of detected charts as thumbnails.
- **Chart workspace** (the core screen) — split view:
  - Left: original chart image (as detected/cropped from the PDF).
  - Right: the regenerated, **editable** interactive chart (Recharts), with controls to:
    - Switch chart type (bar/line/pie/heatmap/table)
    - Edit individual data points inline
    - Change color palette / theme
    - See the LLM's "alternative format" suggestion with one-click apply
  - Below/beside: the **Compliance Panel** — similarity score (visual gauge/progress ring), risk badge (Low/Medium/High, color-coded), and a checklist of recommended actions, each with an "Apply" button where feasible (e.g. auto-apply a suggested palette) and a live-updating score as the user makes changes.
  - Export buttons: Download SVG, Download PNG, Copy chart config.
- **Settings** — profile, account, danger zone (delete account/data).

### UX & design bar
- Consult the frontend-design skill guidance for spacing, type scale, and avoiding "generic AI template" look — this must feel like a considered, branded product, not defaults.
- Every async action needs a loading state (skeletons, not blank screens) and a clear error state (toast + retry, not a silent failure).
- Empty states must be designed, not blank ("No projects yet — create your first one" with an illustration/CTA).
- Fully responsive — must work cleanly on a laptop screen for a demo, and reasonably on mobile.
- Use a consistent, considered color system with a couple of accent colors (e.g. one primary brand color + semantic colors for risk levels: green/amber/red) — define this once in Tailwind config, use everywhere.

### Data flow
- All reads/writes go through the Supabase client (with RLS enforced) for simple CRUD (projects, documents, listing charts).
- Heavy processing (the actual AI pipeline) goes through your backend API, which itself writes results into Supabase.
- Use Supabase Realtime subscriptions (or polling as a fallback) so the processing view updates without manual refresh.

---

## 6. Non-Functional Requirements

- **Security**: RLS on every table, storage policies matching, no service-role key ever exposed to the frontend, all secrets server-side only.
- **No dummy data**: every screen must reflect real Supabase state. If a feature isn't finished, show an honest "coming soon" — never fake data.
- **Configurability**: similarity-score thresholds, detection-confidence thresholds, and the LLM provider/key must be environment-configurable, not hardcoded magic numbers scattered in code.
- **Logging**: meaningful server logs for each pipeline stage (useful for demoing/debugging in front of a mentor).
- **Documentation**: a `README.md` explaining setup (Supabase project creation, env vars, running frontend + backend locally, running the Python pipeline dependencies).

---

## 7. Definition of Done

Treat the build as incomplete until ALL of the following are true:

- [ ] A user can sign up, log in, and see an empty dashboard.
- [ ] A user can create a project and upload a real PDF.
- [ ] The document visibly moves through every pipeline stage with real status updates.
- [ ] At least bar, line, and pie charts are correctly detected and extracted from a real sample PDF with reasonable numeric accuracy.
- [ ] The Chart Workspace shows the original next to a genuinely editable, re-renderable chart.
- [ ] Switching chart type in the UI actually re-renders the chart with the same underlying data.
- [ ] The Compliance Panel shows a real computed similarity score and risk level, not a static/mock number.
- [ ] Applying a recommendation (e.g. changing the color palette) visibly changes the chart and the score recalculates.
- [ ] SVG and PNG export both produce a real downloadable file matching what's on screen.
- [ ] All data is scoped per-user via RLS — verify by testing with two separate accounts.
- [ ] The app has no console errors, no broken links, and no placeholder "Lorem ipsum" text anywhere in the shipped build.

---

## 8. Build Order (recommended)

1. Supabase project setup: schema, RLS policies, storage buckets, auth config.
2. Backend skeleton: API routes + Supabase service-role client, stubbed pipeline functions returning realistic shapes.
3. Frontend skeleton: auth flow, dashboard, project/document CRUD wired to Supabase directly.
4. Wire real PDF upload → storage → `documents` row → trigger backend processing.
5. Implement pipeline stage 1 (ingestion) and 2 (detection) end-to-end, visible in the UI as real progress.
6. Implement extraction (stage 3) with at least one chart type working accurately before generalizing to all types.
7. Implement reconstruction (stage 4) in the Chart Workspace with live editing.
8. Implement compliance scoring (stage 5) with the panel and recommendation actions.
9. Polish: loading/empty/error states, responsive pass, final design pass, README.
10. End-to-end test with 2-3 real sample research-paper PDFs before considering it done.
