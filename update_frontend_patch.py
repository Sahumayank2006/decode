import re
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
chart_selector = """
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
text = text.replace(
    '<div className="mt-6 flex flex-col items-start lg:flex-row lg:space-x-8">',
    chart_selector + '\n\n<div className="mt-6 flex flex-col items-start lg:flex-row lg:space-x-8">'
)

with open("decode-frontend/src/components/demo/DemoWorkspace.tsx", "w", encoding="utf-8") as f:
    f.write(text)
