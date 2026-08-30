import sys
import re

file_path = 'decode-frontend/src/components/demo/DemoWorkspace.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 4: Add state variables
state_vars = """
  const [backendCharts, setBackendCharts] = useState<any[]>([]);
  const [selectedBackendChart, setSelectedBackendChart] = useState<any | null>(null);
  const [selectedChartImage, setSelectedChartImage] = useState<string | null>(null);
"""
if 'const [backendCharts, setBackendCharts]' not in text:
    idx = text.find('const [documentId, setDocumentId] =')
    if idx != -1:
        end_idx = text.find(';', idx) + 1
        text = text[:end_idx] + state_vars + text[end_idx:]

# We need to replace the processPdf chart-fetch section.
# We will replace from `const chartsPayload = await getDocumentCharts(newDocumentId);`
# up to `window.setTimeout(() => setSuccess(null), 5000);`

# Since I rewrote processPdf recently, let's find the `setProcessingStage("Reading extracted chart data");`
start_idx = text.find('setProcessingStage("Reading extracted chart data");')
if start_idx != -1:
    end_idx = text.find('} catch (error) {', start_idx)
    if end_idx != -1:
        # We need to keep setProcessingStage and setUploadProgress(84);
        # Let's replace the content between `setUploadProgress(84);` and `setUploadProgress(100);`
        u84_idx = text.find('setUploadProgress(84);', start_idx)
        u100_idx = text.find('setUploadProgress(100);', start_idx)
        
        if u84_idx != -1 and u100_idx != -1:
            part_to_replace = text[u84_idx+len('setUploadProgress(84);'):u100_idx]
            
            new_part = """
      let chartsPayload: any = null;
      for (let attempt = 0; attempt < 12; attempt++) {
        chartsPayload = await getDocumentCharts(newDocumentId);
        const charts: any[] = Array.isArray(chartsPayload)
            ? chartsPayload
            : Array.isArray(chartsPayload?.charts)
            ? chartsPayload.charts
            : Array.isArray(chartsPayload?.data?.charts)
            ? chartsPayload.data.charts
            : [];
        if (charts.length > 0) break;
        await new Promise((resolve) => setTimeout(resolve, 800));
      }

      const charts: any[] = Array.isArray(chartsPayload)
        ? chartsPayload
        : Array.isArray(chartsPayload?.charts)
        ? chartsPayload.charts
        : Array.isArray(chartsPayload?.data?.charts)
        ? chartsPayload.data.charts
        : [];

      setBackendCharts(charts);

      const firstChart = charts[0] ?? null;
      setSelectedBackendChart(firstChart);

      if (firstChart) {
        const imageBase64 = firstChart.original_image_base64;
        const imagePath = firstChart.original_image_path;

        if (imageBase64) {
          setSelectedChartImage(`data:image/png;base64,${imageBase64}`);
        } else if (imagePath) {
          const apiOrigin = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api/v1").replace(/\/api\/v1\/?$/, "");
          setSelectedChartImage(`${apiOrigin}${imagePath}`);
        }

        const canonical = firstChart.canonical_data ?? firstChart.extraction?.canonical_data ?? null;
        let extractedRows: any[] | null = null;

        if (canonical && Array.isArray(canonical.categories) && Array.isArray(canonical.series)) {
          const categories = canonical.categories;
          const series = canonical.series;

          const revenueSeries = series.find((item: any) => String(item?.name ?? "").toLowerCase().includes("revenue")) ?? series[0];
          const profitSeries = series.find((item: any) => String(item?.name ?? "").toLowerCase().includes("profit")) ?? series[1];

          if (revenueSeries) {
            const revenueValues = Array.isArray(revenueSeries.values) ? revenueSeries.values : [];
            const profitValues = Array.isArray(profitSeries?.values) ? profitSeries.values : [];

            extractedRows = categories.map((category: any, index: number) => ({
              category: String(category ?? `Row ${index + 1}`),
              revenue: safeNumber(revenueValues[index]),
              profit: safeNumber(profitValues[index]),
              // Support arbitrary series for flexible extraction
              "series-0": safeNumber(revenueValues[index]),
              "series-1": safeNumber(profitValues[index])
            }));
          }
        }

        if (extractedRows && extractedRows.length > 0) {
          setRows(extractedRows);
          setHistory([]);
          setFuture([]);
        }

        const extractedType = canonical?.detected_type ?? firstChart?.extraction?.resolved_chart_type ?? firstChart?.chart_type ?? "bar";
        setChartMode((extractedType === "bar" || extractedType === "line" || extractedType === "pie" || extractedType === "donut" || extractedType === "area" || extractedType === "radar") ? extractedType as any : "bar");
      }
      """
            text = text[:u84_idx+len('setUploadProgress(84);')] + new_part + text[u100_idx:]

# Fix 5: Replace the chart area with the original crop fallback
# It's inside a div <div className="h-[390px] px-5 pb-5"> (Wait, my h-[390px] wasn't found. Let's find "renderChart()"
render_idx = text.find('{rows.length > 0 ? (')
if render_idx == -1:
    render_idx = text.find('{rows.length > 0 ?')
if render_idx == -1:
    render_idx = text.find('{rows.length > 0')

if render_idx != -1:
    # let's replace the whole {rows.length > 0 ...} block up to the enclosing </div>
    # My UI has {rows.length > 0 && <div className="..."> {renderChart()} </div>} or similar.
    # Actually, we can just find where `renderChart()` is called.
    r_idx = text.find('renderChart()')
    
    # We can inject this fallback UI using regex
    fallback_ui = """
    {rows.length > 0 ? (
      renderChart()
    ) : selectedChartImage ? (
      <div className="relative flex h-full items-center justify-center overflow-hidden rounded-xl border border-white/[0.06] bg-black/20 p-4 min-h-[350px]">
        <div className="absolute left-3 top-3 z-10 rounded-full border border-emerald-300/20 bg-[#07150f]/90 px-3 py-1 text-[9px] uppercase tracking-[0.16em] text-emerald-300 backdrop-blur">
          Real extracted artifact
        </div>
        <img
          src={selectedChartImage}
          alt="Extracted chart from uploaded PDF"
          className="max-h-[300px] max-w-full rounded-lg object-contain shadow-2xl"
        />
      </div>
    ) : (
      <div className="flex h-[350px] flex-col items-center justify-center text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-white/[0.06] bg-white/[0.02]">
          <BarChart3 size={20} className="text-white/20" />
        </div>
        <div className="mt-4 text-sm font-medium text-white/50">
          No extracted chart available
        </div>
        <div className="mt-2 max-w-sm text-[10px] leading-5 text-white/25">
          Upload a PDF containing a chart. DECODE will detect the visual artifact, extract its data and reconstruct it here.
        </div>
      </div>
    )}
"""
    # Let's replace whatever is doing `{rows.length > 0 && ... }` or similar in my code
    # We will search for where renderChart() is in the render tree.
    # It is usually:
    # <div className="...">
    #   {renderChart()}
    # </div>
    # Let's just find `renderChart()` in the return statement.
    match = re.search(r'\{(?:rows\.length > 0 \? )?renderChart\(\).*?\}', text, re.DOTALL)
    if match:
        pass
    else:
        # maybe it's {renderChart()}
        pass

# Fix 6: Add the Chart selector
# "Put this above your chart panel, after the upload-status section:"
# The upload-status section has `setSuccess` or something? No, it's the `Extracted artifacts` UI.
chart_selector_ui = """
{backendCharts.length > 0 && (
  <section className="mt-4 rounded-2xl border border-white/[0.07] bg-[#091810] p-4">
    <div className="mb-3 flex items-center justify-between">
      <div>
        <div className="text-xs font-semibold text-white/80">
          Extracted artifacts
        </div>
        <div className="mt-1 text-[9px] text-white/30">
          {backendCharts.length} visual artifacts detected from the PDF
        </div>
      </div>
      <div className="text-[9px] uppercase tracking-[0.16em] text-emerald-300">
        Live backend data
      </div>
    </div>
    <div className="flex flex-wrap gap-2">
      {backendCharts.map((chart: any, index: number) => {
        const active = selectedBackendChart?.id === chart.id;
        const chartType = chart?.canonical_data?.detected_type ?? chart?.extraction?.resolved_chart_type ?? chart?.chart_type ?? "chart";
        return (
          <button
            key={chart.id ?? `chart-${index}`}
            type="button"
            onClick={() => {
              setSelectedBackendChart(chart);
              const canonical = chart.canonical_data;
              if (canonical && Array.isArray(canonical.categories) && Array.isArray(canonical.series)) {
                const revenueSeries = canonical.series.find((item: any) => String(item?.name ?? "").toLowerCase().includes("revenue")) ?? canonical.series[0];
                const profitSeries = canonical.series.find((item: any) => String(item?.name ?? "").toLowerCase().includes("profit")) ?? canonical.series[1];
                if (revenueSeries) {
                  const revenueValues = revenueSeries.values ?? [];
                  const profitValues = profitSeries?.values ?? [];
                  const nextRows = canonical.categories.map((category: any, rowIndex: number) => ({
                    category: String(category),
                    revenue: safeNumber(revenueValues[rowIndex]),
                    profit: safeNumber(profitValues[rowIndex]),
                    "series-0": safeNumber(revenueValues[rowIndex]),
                    "series-1": safeNumber(profitValues[rowIndex])
                  }));
                  if (nextRows.length > 0) setRows(nextRows);
                  else setRows([]);
                }
              } else {
                setRows([]);
              }
              
              setChartMode((chartType === "bar" || chartType === "line" || chartType === "pie" || chartType === "donut" || chartType === "area" || chartType === "radar") ? chartType as any : "bar");
              
              const imageBase64 = chart.original_image_base64;
              const imagePath = chart.original_image_path;
              if (imageBase64) setSelectedChartImage(`data:image/png;base64,${imageBase64}`);
              else if (imagePath) {
                const apiOrigin = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api/v1").replace(/\/api\/v1\/?$/, "");
                setSelectedChartImage(`${apiOrigin}${imagePath}`);
              }
            }}
            className={`rounded-xl border px-4 py-3 text-left transition ${active ? "border-emerald-300/30 bg-emerald-300/[0.08]" : "border-white/[0.06] bg-white/[0.015] hover:border-white/[0.12]"}`}
          >
            <div className="text-[10px] font-medium text-white/75">
              Extracted Chart {index + 1}
            </div>
            <div className="mt-1 text-[9px] uppercase tracking-[0.12em] text-emerald-300/60">
              {chartType}
            </div>
            <div className="mt-1 text-[9px] text-white/25">
              {chart?.canonical_data?.categories?.length ?? 0} categories
            </div>
          </button>
        );
      })}
    </div>
  </section>
)}
"""

with open('update_frontend_patch.py', 'w') as out_script:
    out_script.write('''import re
with open("decode-frontend/src/components/demo/DemoWorkspace.tsx", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
"""          <div className="h-full flex items-center justify-center">
            {renderChart()}
          </div>""", 
"""          <div className="h-full w-full">
            {rows.length > 0 ? (
              renderChart()
            ) : selectedChartImage ? (
              <div className="relative flex h-[350px] items-center justify-center overflow-hidden rounded-xl border border-white/[0.06] bg-black/20 p-4">
                <div className="absolute left-3 top-3 z-10 rounded-full border border-emerald-300/20 bg-[#07150f]/90 px-3 py-1 text-[9px] uppercase tracking-[0.16em] text-emerald-300 backdrop-blur">
                  Real extracted artifact
                </div>
                <img
                  src={selectedChartImage}
                  alt="Extracted chart from uploaded PDF"
                  className="max-h-full max-w-full rounded-lg object-contain shadow-2xl"
                />
              </div>
            ) : (
              <div className="flex h-[350px] flex-col items-center justify-center text-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-white/[0.06] bg-white/[0.02]">
                  <BarChart3 size={20} className="text-white/20" />
                </div>
                <div className="mt-4 text-sm font-medium text-white/50">
                  No extracted chart available
                </div>
              </div>
            )}
          </div>"""
)

# Insert the chart selector before <div className="mt-6 flex flex-col items-start lg:flex-row lg:space-x-8">
chart_selector = """''' + chart_selector_ui + '''"""
text = text.replace(
    '<div className="mt-6 flex flex-col items-start lg:flex-row lg:space-x-8">',
    chart_selector + '\\n\\n<div className="mt-6 flex flex-col items-start lg:flex-row lg:space-x-8">'
)

with open("decode-frontend/src/components/demo/DemoWorkspace.tsx", "w", encoding="utf-8") as f:
    f.write(text)
''')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated DemoWorkspace.tsx processing logic.")
