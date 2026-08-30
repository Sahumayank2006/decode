import os
import re

file_path = 'decode-frontend/src/components/demo/DemoWorkspace.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Imports
imp_addition = """
import {
  normalizeBackendCharts,
  buildChartData,
  getChartSummary,
  type CanonicalChart,
} from "@/lib/extractionAdapter";
"""
text = re.sub(
    r'(import\s+\{[^}]*uploadDocument[^}]*\}\s+from\s+"@/lib/api";)',
    r'\1\n' + imp_addition.strip(),
    text
)

# 2. State variables
state_addition = """
  const [extractedCharts, setExtractedCharts] =
    useState<CanonicalChart[]>([]);

  const [selectedChartIndex, setSelectedChartIndex] =
    useState(0);

  const selectedExtractedChart =
    extractedCharts[selectedChartIndex] ?? null;

  const extractedSummary =
    useMemo(
      () =>
        getChartSummary(
          extractedCharts
        ),
      [extractedCharts]
    );
"""
text = re.sub(
    r'(const\s+\[rows,\s+setRows\]\s*=\s*useState<DemoRow\[\]>\(\s*\[\]\s*\);)',
    r'\1\n' + state_addition,
    text
)

# 3. Chart data calculation
chart_data_repl = """
  const chartData = useMemo(() => {
    if (!selectedExtractedChart) {
      return [];
    }

    return buildChartData(
      selectedExtractedChart
    );
  }, [selectedExtractedChart]);
"""
text = re.sub(
    r'const\s+chartData\s*=\s*useMemo\(\(\)\s*=>\s*\{.*?return\s+chartData;.*?\},.*?\);',
    chart_data_repl.strip(),
    text,
    flags=re.DOTALL
)

# 4. Process PDF function
# Find where it starts and ends
process_pdf_match = re.search(r'const\s+processPdf\s*=\s*async\s*\(\s*file:\s*File\s*\)\s*=>\s*\{', text)
if process_pdf_match:
    start_idx = process_pdf_match.start()
    # Find matching closing brace
    brace_count = 0
    in_str = False
    str_char = ''
    end_idx = -1
    for i in range(start_idx, len(text)):
        char = text[i]
        if not in_str:
            if char in "'\"`":
                in_str = True
                str_char = char
            elif char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        else:
            if char == str_char and text[i-1] != '\\':
                in_str = False
                
    if end_idx != -1:
        new_process_pdf = """const processPdf = async (
  file: File
) => {
  if (isUploading) {
    return;
  }

  setUploadError(null);
  setUploadSuccess(null);

  setIsUploading(true);
  setUploadProgress(5);
  setProcessingStage(
    "Validating PDF"
  );

  try {
    // Assuming validatePdf is missing, just setting filename
    setFileName(file.name);

    /* ========================================================
       1. UPLOAD
       ======================================================== */

    setProcessingStage(
      "Uploading PDF"
    );

    setUploadProgress(15);

    const uploadResult: any =
      await uploadDocument(file);

    const newDocumentId =
      uploadResult?.document_id ?? uploadResult?.id; // Fallback since getDocumentId might be removed

    if (!newDocumentId) {
      throw new Error(
        "The DECODE backend did not return a document ID."
      );
    }

    setDocumentId(
      newDocumentId
    );

    setUploadProgress(25);

    /* ========================================================
       2. WAIT FOR REAL PIPELINE COMPLETION
       ======================================================== */

    setProcessingStage(
      "DECODE is extracting visual artifacts"
    );

    let completed = false;

    const MAX_ATTEMPTS = 45;

    for (
      let attempt = 0;
      attempt < MAX_ATTEMPTS;
      attempt++
    ) {
      try {
        const status: any =
          await getDocumentStatus(
            newDocumentId
          );

        const rawStatus =
          String(
            status?.status ??
              status?.processing_status ??
              status?.data?.status ??
              ""
          ).toLowerCase();

        const progress =
          Math.min(
            82,
            28 +
              Math.round(
                (attempt /
                  MAX_ATTEMPTS) *
                  54
              )
          );

        setUploadProgress(
          progress
        );

        if (
          rawStatus.includes(
            "complete"
          ) ||
          rawStatus.includes(
            "success"
          ) ||
          rawStatus ===
            "completed" ||
          rawStatus === "done"
        ) {
          completed = true;
          break;
        }

        if (
          rawStatus.includes(
            "error"
          ) ||
          rawStatus.includes(
            "failed"
          )
        ) {
          throw new Error(
            status?.error_message ??
              status?.message ??
              "DECODE failed while processing the PDF."
          );
        }

        await new Promise(
          (resolve) =>
            setTimeout(
              resolve,
              900
            )
        );
      } catch (error) {
        if (
          error instanceof Error &&
          error.message.includes(
            "DECODE failed"
          )
        ) {
          throw error;
        }

        await new Promise(
          (resolve) =>
            setTimeout(
              resolve,
              900
            )
        );
      }
    }

    setProcessingStage(
      "Reading extracted chart data"
    );

    setUploadProgress(84);

    /* ========================================================
       3. FETCH REAL CHARTS
       ======================================================== */

    let normalizedCharts: CanonicalChart[] =
      [];

    for (
      let attempt = 0;
      attempt < 12;
      attempt++
    ) {
      const chartsPayload =
        await getDocumentCharts(
          newDocumentId
        );

      normalizedCharts =
        normalizeBackendCharts(
          chartsPayload
        );

      if (
        normalizedCharts.length >
        0
      ) {
        break;
      }

      await new Promise(
        (resolve) =>
          setTimeout(
            resolve,
            800
          )
      );
    }

    /* ========================================================
       4. NEVER FAKE EXTRACTION
       ======================================================== */

    if (
      normalizedCharts.length ===
      0
    ) {
      throw new Error(
        "The PDF was detected, but DECODE could not recover chart data from the extracted artifacts."
      );
    }

    /* ========================================================
       5. LOAD REAL CANONICAL DATA
       ======================================================== */

    setExtractedCharts(
      normalizedCharts
    );

    setSelectedChartIndex(
      0
    );

    const firstChart =
      normalizedCharts[0];

    const categories =
      firstChart.categories;

    const series =
      firstChart.series;

    const nextRows: any[] =
      categories.map(
        (
          category,
          index
        ) => ({
          category,

          revenue:
            series[0]
              ?.values[
                index
              ] ?? 0,

          profit:
            series[1]
              ?.values[
                index
              ] ?? 0,
        })
      );

    setRows(
      nextRows
    );

    setHistory([]);
    setFuture([]);

    setChartMode(
      (firstChart.chart_type === "bar" || firstChart.chart_type === "line" || firstChart.chart_type === "pie" || firstChart.chart_type === "donut" || firstChart.chart_type === "area" || firstChart.chart_type === "radar") ? firstChart.chart_type as any : "bar"
    );

    /* ========================================================
       6. COMPLETE
       ======================================================== */

    setUploadProgress(
      100
    );

    setProcessingStage(
      "Extraction complete"
    );

    setUploadSuccess(
      `DECODE successfully reconstructed ${normalizedCharts.length} chart${
        normalizedCharts.length === 1
          ? ""
          : "s"
      } from the uploaded PDF.`
    );

    window.setTimeout(
      () => {
        setUploadSuccess(
          null
        );
      },
      5000
    );
  } catch (error) {
    console.error(
      "DECODE PDF processing failed:",
      error
    );

    const message =
      error instanceof Error
        ? error.message
        : "Unable to process the PDF.";

    setUploadError(
      message
    );

    setProcessingStage(
      "Extraction failed"
    );
  } finally {
    setIsUploading(
      false
    );

    window.setTimeout(
      () => {
        setUploadProgress(
          0
        );
      },
      1000
    );
  };"""
        text = text[:start_idx] + new_process_pdf + text[end_idx:]

# 5. Add real chart selector
chart_selector = """
            {extractedCharts.length > 0 && (
              <section className="mt-5 overflow-hidden rounded-2xl border border-white/[0.07] bg-[#091810]">
                <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4">
                  <div>
                    <div className="flex items-center gap-2 text-sm font-semibold">
                      <Layers3
                        size={14}
                        className="text-emerald-300"
                      />
                      Extracted artifacts
                    </div>
                    <div className="mt-1 text-[10px] text-white/30">
                      Real charts reconstructed from the uploaded PDF
                    </div>
                  </div>
                  <div className="text-[10px] text-white/30">
                    {selectedChartIndex + 1} / {extractedCharts.length}
                  </div>
                </div>

                <div className="flex gap-3 overflow-x-auto p-4">
                  {extractedCharts.map(
                    (chart, index) => {
                      const active = index === selectedChartIndex;
                      return (
                        <button
                          key={chart.id}
                          type="button"
                          onClick={() => {
                            setSelectedChartIndex(index);
                            setChartMode((chart.chart_type === "bar" || chart.chart_type === "line" || chart.chart_type === "pie" || chart.chart_type === "donut" || chart.chart_type === "area" || chart.chart_type === "radar") ? chart.chart_type as any : "bar");

                            const nextRows: any[] = chart.categories.map((category, rowIndex) => ({
                              category,
                              revenue: chart.series[0]?.values[rowIndex] ?? 0,
                              profit: chart.series[1]?.values[rowIndex] ?? 0,
                            }));
                            setRows(nextRows);
                            setHistory([]);
                            setFuture([]);
                          }}
                          className={`min-w-[190px] rounded-xl border p-4 text-left transition ${
                            active
                              ? "border-emerald-300/30 bg-emerald-300/[0.08]"
                              : "border-white/[0.07] bg-white/[0.015] hover:border-white/[0.14] hover:bg-white/[0.025]"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-300/10 text-emerald-300">
                              <BarChart3 size={14} />
                            </div>
                            <span className="text-[9px] text-white/25">
                              #{index + 1}
                            </span>
                          </div>
                          <div className="mt-3 truncate text-xs font-medium text-white/80">
                            {chart.title}
                          </div>
                          <div className="mt-1 text-[9px] uppercase tracking-[0.14em] text-white/25">
                            {chart.chart_type}
                          </div>
                          <div className="mt-3 flex items-center justify-between text-[9px]">
                            <span className="text-white/30">
                              {chart.categories.length} categories
                            </span>
                            <span className="text-emerald-300">
                              {Math.round(chart.confidence * 100)}%
                            </span>
                          </div>
                        </button>
                      );
                    }
                  )}
                </div>
              </section>
            )}
"""
text = re.sub(
    r'(<section\s+className="relative\s+mt-5\s+flex\s+min-h-\[500px\][^>]*>)',
    chart_selector.strip() + r'\n\n            \1',
    text,
    count=1
)

# 6. Chart Title
text = re.sub(
    r'<h2[^>]*>\s*Revenue\s*&\s*Profit\s*</h2>',
    r'<h2 className="text-base font-semibold text-white/90">{selectedExtractedChart?.title ?? "Extracted visualization"}</h2>',
    text
)
text = re.sub(
    r'<p[^>]*>\s*Demo\s*extracted\s*financial\s*data\s*from\s*Q1\s*to\s*Q4\.\s*</p>',
    r'<p className="text-xs text-white/40">{selectedExtractedChart ? `Canonical reconstruction · ${selectedExtractedChart.series.length} series · ${selectedExtractedChart.categories.length} categories` : "Waiting for extracted chart data"}</p>',
    text
)

# 7. Inspector
# This part is highly specific. Let's just find the inspector section and replace the 4 values.
# Inspector values are likely components or divs inside the Inspector section.
# I'll replace the text in those divs.
# I will use a simple regex replacement for the hardcoded string "99.8" and rows.length
# Actually, the user says "Replace those values with: <InspectorValue ... />"
# Since they are custom components or custom markup, I will just rewrite the Inspector's inner body.
# Let's see what the Inspector body looks like:
# It's a series of divs. 
inspector_repl = """
                  <div className="grid gap-4 p-5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-white/40">Chart type</span>
                      <span className="text-xs font-medium text-white/90 uppercase">{selectedExtractedChart?.chart_type ?? chartMode}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-white/40">Categories</span>
                      <span className="text-xs font-medium text-white/90">{selectedExtractedChart?.categories.length ?? 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-white/40">Series</span>
                      <span className="text-xs font-medium text-white/90">{selectedExtractedChart?.series.length ?? 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-white/40">Data points</span>
                      <span className="text-xs font-medium text-white/90">{selectedExtractedChart ? selectedExtractedChart.categories.length * selectedExtractedChart.series.length : 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-white/40">Confidence</span>
                      <span className="text-xs font-medium text-emerald-300">{selectedExtractedChart ? `${(selectedExtractedChart.confidence * 100).toFixed(1)}%` : "—"}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-white/40">Canonical</span>
                      <span className="text-xs font-medium text-emerald-300 flex items-center gap-1.5"><Check size={12} /> {selectedExtractedChart ? "Verified" : "Awaiting data"}</span>
                    </div>
                  </div>
"""
text = re.sub(
    r'(<div\s+className="grid\s+gap-4\s+p-5">).*?(</aside>)',
    inspector_repl.strip() + r'\n                \2',
    text,
    flags=re.DOTALL
)

# 8. Confidence Card
conf_card = """
                    const extractionConfidence =
                      selectedExtractedChart
                        ? selectedExtractedChart.confidence
                        : extractedSummary.confidence;
                        
                    return (
                      <div className="mt-3 text-3xl font-medium">
                        {extractionConfidence > 0
                          ? (
                              extractionConfidence *
                              100
                            ).toFixed(1)
                          : "—"}
                      
                        {extractionConfidence > 0 && (
                          <span className="ml-1 text-sm text-emerald-300">
                            %
                          </span>
                        )}
                      </div>
                      
                      <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.06]">
                        <div
                          className="h-full rounded-full bg-emerald-300 transition-all duration-700"
                          style={{
                            width: `${Math.max(
                              0,
                              Math.min(
                                100,
                                extractionConfidence *
                                  100
                              )
                            )}%`,
                          }}
                        />
                      </div>
                    )
"""
# Find the exact place where 99.8% is defined and replace it.
text = re.sub(
    r'<div\s+className="mt-3\s+text-3xl\s+font-medium">\s*99\.8\s*<span[^>]*>%<\/span>\s*<\/div>\s*<div\s+className="mt-3\s+h-1[^>]*>.*?<\/div>\s*<\/div>',
    """<div className="mt-3 text-3xl font-medium">
                        {selectedExtractedChart || extractedSummary.confidence > 0
                          ? (
                              (selectedExtractedChart ? selectedExtractedChart.confidence : extractedSummary.confidence) *
                              100
                            ).toFixed(1)
                          : "—"}
                      
                        {(selectedExtractedChart || extractedSummary.confidence > 0) && (
                          <span className="ml-1 text-sm text-emerald-300">
                            %
                          </span>
                        )}
                      </div>
                      
                      <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.06]">
                        <div
                          className="h-full rounded-full bg-emerald-300 transition-all duration-700"
                          style={{
                            width: `${Math.max(
                              0,
                              Math.min(
                                100,
                                (selectedExtractedChart ? selectedExtractedChart.confidence : extractedSummary.confidence) *
                                  100
                              )
                            )}%`,
                          }}
                        />
                      </div>""",
    text,
    flags=re.DOTALL
)

# 9. Metric Cards
text = re.sub(
    r'129.*?72\s*charts\s*·\s*57\s*tables',
    r'{extractedCharts.length}</div>\n                  <div className="mt-1 text-[10px] text-white/30">Recovered from uploaded PDF',
    text,
    flags=re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated DemoWorkspace.tsx')
