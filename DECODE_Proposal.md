# DECODE: An AI-Assisted Framework for Copyright-Safe Recreation of Scientific Charts and Diagrams

**DECODE** — *Detection, Extraction, Compliance-verification, Output-generation, Diagram-reconstruction, and Evaluation*

**Author:** Vaibhav
**Department:** Computer Science and Engineering

---

## Abstract

Scientific and medical communication teams routinely need to reproduce charts, graphs, and diagrams from research papers for use in presentations, reports, and educational material. This task is presently performed manually — a process that is slow, prone to numerical error, and carries a real risk of copyright infringement when recreated visuals closely resemble their source.

This paper presents **DECODE**, an artificial-intelligence-assisted platform that automates the extraction and regeneration of scientific visualizations from PDF documents. The system combines optical character recognition, computer-vision-based chart detection, and large-language-model reasoning to:

- Identify visual elements within a document
- Extract their underlying numerical and textual content
- Reconstruct them as editable, style-flexible charts

A dedicated **compliance module** evaluates structural similarity between the original and regenerated visual and issues a quantitative copyright-risk score together with actionable recommendations.

Unlike existing digitization tools that focus purely on value extraction, DECODE is designed as an **end-to-end pipeline** spanning detection, extraction, regeneration, and legal-safety assessment — requiring no custom model training. The proposed methodology is organized into six stages covering ingestion, detection, extraction, reconstruction, compliance analysis, and evaluation.

The system is expected to reduce chart-recreation time substantially while preserving numerical accuracy and reducing copyright exposure, offering measurable value to researchers, communication teams, and students who routinely repurpose figures from published literature.

**Index Terms** — chart digitization, copyright compliance, data extraction, optical character recognition, scientific visualization.

---

## I. Introduction

### A. Problem Statement

Charts, graphs, and diagrams are central to how scientific and medical findings are communicated, yet reusing them beyond their original publication remains a largely manual exercise. Communication teams, medical educators, and students routinely need to reproduce a published figure inside a new presentation, report, or manuscript, and current practice requires an individual to manually redraw the visual using general-purpose tools such as PowerPoint, Illustrator, or Canva, reading data points directly off the original image.

This workflow introduces several compounding problems:

1. **Time-consuming** — a single complex figure can take hours to faithfully recreate.
2. **Error-prone** — manual transcription of data points is error-prone, and small numerical mistakes can materially affect scientific interpretation.
3. **Legally risky** — visuals redrawn too closely to the original risk violating copyright restrictions held by publishers, exposing organizations to legal and reputational harm.
4. **Inflexible** — once a manually recreated chart exists as a static image, it is difficult to edit, update, or restyle when requirements change.
5. **Siloed** — this process typically happens in isolation, with limited collaboration between the researchers who understand the data and the communication or design staff who produce the final visual.

Collectively, these issues make chart reproduction one of the most persistent and under-addressed bottlenecks in scientific and medical communication pipelines.

### B. Proposed Solution

To address these limitations, this paper proposes **DECODE**, an AI-assisted platform that converts scientific visuals embedded in PDF documents into editable, numerically faithful, and copyright-aware outputs. Rather than treating chart reproduction as a purely manual design task, DECODE treats it as a structured information-extraction and regeneration problem.

The workflow operates as follows:

- A user uploads a research paper, manuscript, or scientific image.
- The system automatically locates charts, graphs, tables, and diagrams within the document using computer-vision techniques.
- Once a visual element is located, the platform extracts its constituent numerical values, axis labels, legends, and accompanying text using OCR and layout analysis.
- These extracted values are used to regenerate the visualization as an **editable object** rather than a flat image, supporting export formats such as SVG, PNG, and presentation-compatible charts.
- Users can switch between alternative chart types — for example, converting a bar chart into a line chart or heatmap when that better communicates the underlying data.

A distinguishing capability of the platform is its **compliance layer**, which evaluates the structural and visual similarity between the regenerated chart and the original, returning a quantitative copyright-safety score along with concrete recommendations such as altering colour schemes, layout, or adding a source citation.

Because the pipeline relies on existing OCR engines, computer-vision libraries, and large-language-model APIs rather than custom-trained models, it is feasible to implement within a short development cycle while remaining extensible to more advanced detection models in future iterations. The result is a workflow that compresses a multi-hour manual task into a matter of minutes without sacrificing data fidelity or legal safety.

---

## II. Literature Review

Existing approaches to chart reproduction fall into three broad categories, each addressing part of the problem this work targets.

**1. Manual digitization tools** — such as WebPlotDigitizer and PlotDigitizer, which allow a user to calibrate axes and click on data points to recover approximate numerical values from a static chart image. While effective for simple extraction tasks, these tools require substantial manual interaction for every figure, do not regenerate an editable, restylable chart automatically, and provide no assessment of copyright risk, leaving the legal-safety question entirely to the user.

**2. Automated chart-mining research systems** — including deep-learning-based chart-question-answering models and figure-extraction pipelines developed for scientific literature mining, which can classify chart type and, in some cases, recover approximate data series from bar and line charts. These systems demonstrate the technical feasibility of automated visual understanding but are typically evaluated as research prototypes focused narrowly on data-value recovery, rather than as end-to-end, user-facing tools for producing publication-ready, editable output suitable for presentations or reports.

**3. General OCR and document-analysis frameworks** — such as Tesseract and layout-parsing libraries built on OpenCV, which are widely used for text and structural extraction from PDFs but are not purpose-built for chart semantics such as axis calibration or legend interpretation.

Separately, image-similarity and plagiarism-detection techniques used in academic-integrity tools offer established methods for quantifying visual resemblance between two images — a capability that has not, to date, been applied specifically to scientific chart regeneration or paired with an actionable remediation workflow.

**Taken together, no existing system integrates automated detection, faithful data extraction, editable multi-format regeneration, and quantitative copyright-risk scoring into a single, cohesive pipeline** — which is precisely the gap this work sets out to address.

---

## III. Methodology

### A. Document Ingestion and Preprocessing

The pipeline begins with document ingestion, where the user supplies a research paper PDF, manuscript, or scientific image or screenshot. The system uses **PyMuPDF** to parse the document structure, separating textual content from embedded raster and vector images while preserving page-level positional metadata such as bounding boxes and page numbers.

Each page is rendered at a resolution sufficient to support downstream visual analysis, and embedded images are extracted individually along with their coordinates within the source layout. Basic preprocessing steps — including noise reduction, contrast normalization, and skew correction — are applied to scanned or low-quality inputs, improving the reliability of the detection and extraction stages that follow and reducing false negatives on older or poorly digitized publications.

Where a document contains multiple candidate figures on a single page, the preprocessing stage also separates overlapping regions using whitespace and layout-boundary heuristics before handing each isolated candidate onward.

### B. AI-Based Visual Element Detection

Once the document has been preprocessed, the system identifies candidate visual regions corresponding to charts, graphs, tables, diagrams, and flowcharts embedded within the page. For a college-level implementation, this stage relies on **OpenCV-based contour and edge analysis** combined with existing AI vision APIs, deliberately avoiding the need for custom model training while still supporting reasonably accurate classification of common visualization types such as bar charts, line charts, pie charts, and scatter plots.

Detected regions are cropped from the page image and passed forward along with a predicted chart-type label and an associated confidence score, which downstream stages use to select the most appropriate extraction strategy for that particular visualization type. Regions falling below a minimum confidence threshold are flagged for optional manual confirmation rather than being silently discarded, preserving recall on unusual or hybrid visualization styles.

### C. Data and Text Extraction

Each detected visual is then subjected to fine-grained extraction:

- **Tesseract OCR** recovers textual elements including titles, axis labels, tick values, and legend entries.
- **OpenCV-based line and shape analysis** recovers the geometric structure of the chart, such as bar heights, line trajectories, or pie-segment angles.

These geometric measurements are mapped back to numerical data values using the calibrated axis scale recovered from the OCR output, and legend text is cross-referenced against detected colour or pattern groupings to correctly label each data series.

The extracted values, labels, and structural metadata are stored as a **structured intermediate representation** that fully describes the chart independently of its visual rendering, forming the numerical foundation for accurate downstream regeneration. Confidence scores are attached to every extracted value so that low-certainty points can later be surfaced to the user for quick manual verification rather than silently propagating an error.

### D. Visualization Reconstruction

Using the structured intermediate representation, the platform regenerates the chart as an editable object rather than a static image:

- **Frontend:** Recharts and Chart.js render interactive, user-editable visualizations.
- **Backend:** Matplotlib and Plotly produce export-ready SVG, PNG, and presentation-compatible outputs.

Because reconstruction operates on the extracted data rather than the original pixels, the system can offer alternative visualization formats for the same underlying data — for instance, regenerating a bar chart as a line chart, heatmap, or comparison table whenever a large-language-model-driven recommendation module determines that an alternative representation would communicate the underlying data more clearly to the intended audience, such as a simplified format for a non-technical reader.

Users retain full manual control to override any suggested format, edit individual data points, or restyle colours and fonts before export.

### E. Copyright Compliance Analysis

In parallel with reconstruction, a compliance module quantifies the structural and stylistic similarity between the regenerated chart and the original source image, considering factors such as colour palette, layout arrangement, and proportional geometry between the two versions.

This produces a numerical copyright-safety score together with a qualitative originality and risk rating — for example, labelling a result as "high originality and low risk." When similarity exceeds a defined threshold, the system issues concrete, actionable recommendations, such as modifying the colour scheme, adjusting the layout, or adding an explicit citation to the original source, allowing the user to reduce legal exposure before the regenerated output is finalized and shared externally. The scoring thresholds are configurable, allowing an organization to apply stricter or more lenient standards depending on internal legal policy.

![Compliance decision flow: regenerated charts are scored for similarity, then either approved as low-risk/high-originality or flagged with recommended actions (modify colour palette, adjust layout/structure, add source citation) before a re-score and final output.](media/image1.png)

*Figure 1: Copyright compliance decision workflow — similarity scoring, flagging, remediation, and re-scoring before finalization.*

### F. System Integration and Evaluation

The complete pipeline is integrated behind a **React-based frontend** and a **Node.js or FastAPI backend**, with **MongoDB** used to persist user accounts, projects, extracted data, and processing history, and **Cloudinary or AWS S3** used for storing uploaded PDFs and generated chart assets.

![System architecture: a Frontend Layer (React.js, Tailwind CSS, Recharts) feeds into a Backend API Layer (Node.js/Express or FastAPI), which connects to AI Components (OCR, OpenCV, LLM API), a Database (MongoDB), and Storage (AWS S3/Cloudinary) — all driving the Processing Pipeline: PDF Parsing → Chart Detection → OCR Extraction → Chart Regeneration → Compliance Scoring.](media/image2.png)

*Figure 2: End-to-end system architecture, from frontend layer through backend, AI components, and the processing pipeline.*

Evaluation is conducted along three axes:

1. **Extraction accuracy** — measured by comparing extracted numerical values against manually verified ground truth drawn from a benchmark set of published figures.
2. **Processing time** — measured end-to-end from document upload to final regenerated output.
3. **Compliance-score reliability** — assessed by comparing the system's automated similarity ratings against independent human reviewer judgments on a held-out sample of regenerated charts.

Results from each evaluation round feed back into threshold tuning for both the detection and compliance stages.

---

## IV. Resource Requirements

Implementation requires:

- A small **development team** with frontend, backend, and applied-AI expertise
- Standard **cloud compute** for hosting the processing pipeline
- Access to **third-party APIs**, including an OCR engine, computer-vision libraries, and a large-language-model provider such as Gemini or OpenAI
- **Cloud object storage** for uploaded documents and generated charts
- A **managed MongoDB database** instance
- **Version control and CI tooling**
- A modest **evaluation dataset** of research-paper figures with manually verified ground-truth values, to benchmark extraction accuracy and compliance-scoring reliability during development, testing, and iterative refinement

![Supporting concept illustration for DECODE's resource and data-processing needs.](media/image3.png)

*Figure 3: DECODE concept — transforming unstructured pixel data into polished visuals, refined trends, and structured insights.*

![Supporting illustration.](media/image4.png)

*Figure 4: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image5.png)

*Figure 5: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image6.png)

*Figure 6: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image7.png)

*Figure 7: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image8.png)

*Figure 8: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image9.png)

*Figure 9: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image10.png)

*Figure 10: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image11.png)

*Figure 11: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image12.png)

*Figure 12: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image13.png)

*Figure 13: Supporting illustration of platform capabilities.*

![Supporting illustration.](media/image14.png)

*Figure 14: Supporting illustration of platform capabilities.*

---

## V. Expected Results

DECODE is expected to deliver measurable improvements across the three dimensions identified during evaluation: extraction accuracy, processing speed, and compliance reliability.

**Extraction accuracy.** The structured intermediate representation approach — which anchors regenerated values directly to OCR-calibrated axis scales rather than free-hand approximation — is expected to yield close-to-exact numerical fidelity for clearly rendered bar and line charts, with validation reporting accuracy at or near 100% against manually verified source values for well-formed inputs, and gracefully degrading accuracy for low-resolution or heavily stylized figures where OCR confidence is lower.

**Processing speed.** Replacing a multi-hour manual redrawing workflow with an automated pipeline is expected to reduce end-to-end chart-recreation time by roughly an order of magnitude, with typical single-chart processing completing within seconds to low minutes depending on document complexity and page count — a substantial improvement that directly benefits time-constrained users such as students preparing seminar presentations or communication teams working against publication deadlines.

**Compliance reliability.** The similarity-scoring module is expected to reliably flag visuals that closely mirror their source in colour, layout, and proportion, providing consistent, actionable guidance that reduces the likelihood of inadvertent copyright violations reaching final publications or presentations. Agreement between automated risk scores and human reviewer judgment is expected to be high enough to make the tool trustworthy as a first-pass compliance check, while still recommending human review for high-stakes or externally published material.

Beyond these quantitative outcomes, the platform is expected to demonstrate clear qualitative value across three real-world contexts:

- **Pharmaceutical and medical communication** — teams will be able to generate compliant, presentation-ready charts directly from clinical trial publications without redrawing them from scratch.
- **Healthcare education** — doctors and educators will be able to generate simplified, audience-appropriate alternative visualizations, such as patient-friendly infographics, from complex research figures with a single conversion step.
- **Students and researchers** — the time burden of manually recreating figures for theses, literature reviews, and seminar presentations is expected to fall substantially, freeing effort for analysis and interpretation rather than artwork reproduction.

Collectively, these results are expected to establish DECODE as a practical, deployable solution rather than a purely theoretical prototype, with a credible and feasible path toward adoption across academic, healthcare, and pharmaceutical communication workflows where accurate, timely, and legally safe visual reproduction remains a recurring and largely unsolved operational need.

---

## VI. Conclusion

This paper has presented **DECODE**, an artificial-intelligence-assisted platform designed to automate the extraction, reconstruction, and copyright-compliance evaluation of scientific charts, graphs, and diagrams sourced from research papers and manuscripts.

The work is motivated by a persistent and under-addressed bottleneck in scientific and medical communication: the manual, time-consuming, and legally risky process by which researchers, designers, educators, and students currently reproduce published visuals for use in presentations, reports, and educational material.

By combining optical character recognition, computer-vision-based chart detection, and large-language-model-driven reasoning within a single **six-stage pipeline** — spanning ingestion, detection, extraction, reconstruction, compliance analysis, and evaluation — DECODE addresses a gap left by existing digitization and chart-mining tools, none of which integrate accurate data recovery, editable regeneration, and quantitative copyright-risk assessment into one cohesive workflow.

The system's reliance on existing OCR, computer-vision, and language-model APIs, rather than custom-trained models, makes it feasible to implement within a constrained development timeline while leaving considerable room for future enhancement through purpose-trained chart-detection models as the platform matures and usage data accumulates.

The expected outcomes — an order-of-magnitude reduction in chart-recreation time, near-complete numerical fidelity for well-formed inputs, and reliable, actionable copyright-risk guidance — together position DECODE as a solution with genuine operational value across pharmaceutical, healthcare, and academic settings rather than as a narrow academic exercise confined to a single demonstration.

**Future work** will focus on:

- Expanding detection coverage to more complex diagram types such as multi-panel figures, flowcharts, and composite statistical plots
- Incorporating purpose-trained vision models to improve extraction accuracy on low-quality or scanned inputs
- Extending the compliance module with publisher-specific licensing rules
- Conducting a formal user study with communication teams and student researchers to validate the platform's real-world time savings and compliance reliability under production conditions

In doing so, DECODE aims to shift scientific visual reproduction from a manual, error-prone, and legally uncertain task toward an automated, accurate, and compliant workflow that benefits the broader research, healthcare, and academic communication community as a whole.
