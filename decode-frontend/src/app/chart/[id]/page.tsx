/* eslint-disable */
// @ts-nocheck
"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  ArrowLeft, BarChart3, Download, RefreshCw, Loader2, ShieldCheck,
  Check, AlertTriangle, Eye, Sparkles, ScanLine
} from "lucide-react";
import { getChart, rescoreChart, getExportUrl } from "@/lib/api";
import { useChartStore } from "@/store/useChartStore";
import { reconstructChart as buildCanonicalChart } from "@/lib/chartUtils";
import { ChartRenderer } from "@/components/chart/ChartRenderer";

function ScoreGauge({ score, risk }: { score: number; risk: string }) {
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color =
    risk === "low" ? "#22c55e" : risk === "medium" ? "#f59e0b" : "#ef4444";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="130" height="130" className="score-ring">
        <circle
          cx="65" cy="65" r={radius}
          fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8"
        />
        <circle
          cx="65" cy="65" r={radius}
          fill="none" stroke={color} strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold" style={{ color }}>
          {score.toFixed(0)}
        </span>
        <span className="text-[10px] text-slate-400 uppercase tracking-wider">
          similarity
        </span>
      </div>
    </div>
  );
}

export default function ChartWorkspacePage() {
  const router = useRouter();
  const params = useParams();
  const chartId = params.id as string;

  const [chart, setChart] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [rescoring, setRescoring] = useState(false);
  
  const setStoreChart = useChartStore(state => state.setChart);
  const storeChart = useChartStore(state => state.charts[chartId]);

  const fetchChart = useCallback(async () => {
    try {
      const data = await getChart(chartId);
      setChart(data);
      
      // Transform into canonical chart format and save in Zustand store
      if (data.extraction) {
        const chartType = data.reconstruction?.chart_type || data.chart_type || 'bar';
        const canonical = buildCanonicalChart(data.extraction);
        canonical.id = chartId;
        setStoreChart(canonical);
      }
    } catch (e) {
      console.error("Failed to fetch chart:", e);
    } finally {
      setLoading(false);
    }
  }, [chartId, setStoreChart]);

  useEffect(() => { fetchChart(); }, [fetchChart]);

  const handleRescore = async () => {
    setRescoring(true);
    try {
      const result = await rescoreChart(chartId);
      setChart((prev: any) => ({ ...prev, compliance: result }));
    } catch (e) {
      console.error("Rescore failed:", e);
    } finally {
      setRescoring(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
      </div>
    );
  }

  const extraction = chart?.extraction;
  const compliance = chart?.compliance;

  return (
    <div className="min-h-screen gradient-bg flex flex-col">
      {/* ── Nav ──────────────────────────────────────────────────────── */}
      <nav className="glass-strong sticky top-0 z-50 px-4 py-3">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2 flex-1">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-white" />
            </div>
            <div>
              <span className="font-bold text-sm">Chart Workspace</span>
              <span className="text-xs text-slate-400 ml-2 capitalize">
                {chart?.chart_type} chart · Page {chart?.page_number}
              </span>
            </div>
          </div>

          {/* Export buttons */}
          <a
            href={getExportUrl(chartId, "png")}
            download
            className="px-3 py-1.5 rounded-lg glass text-xs font-medium text-slate-300 hover:text-white flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5" /> Original PNG
          </a>
        </div>
      </nav>

      {/* ── Main content ─────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col lg:flex-row gap-4 p-4 overflow-hidden">
        {/* ── Left: Original chart ───────────────────────────────────── */}
        <div className="lg:w-1/2 flex flex-col gap-4">
          <div className="glass rounded-2xl p-4 flex-1 flex flex-col">
            <div className="flex items-center gap-2 mb-3">
              <Eye className="w-4 h-4 text-slate-400" />
              <span className="text-sm font-semibold">Original Chart</span>
            </div>
            <div className="flex-1 bg-slate-900 rounded-xl overflow-hidden flex items-center justify-center min-h-[300px]">
              {chart?.original_image_base64 ? (
                <img
                  src={`data:image/png;base64,${chart.original_image_base64}`}
                  alt="Original chart"
                  className="max-w-full max-h-full object-contain p-4"
                />
              ) : (
                <ScanLine className="w-16 h-16 text-slate-700" />
              )}
            </div>
          </div>

          {/* Extraction data summary */}
          {extraction && (
            <div className="glass rounded-2xl p-4">
              <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                Extracted Data
              </h3>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-slate-400">Title:</span>
                  <p className="font-medium">{extraction.title || "Untitled"}</p>
                </div>
                <div>
                  <span className="text-slate-400">Series:</span>
                  <p className="font-medium">{extraction.series?.length || 0} found</p>
                </div>
                <div>
                  <span className="text-slate-400">X-Axis:</span>
                  <p className="font-medium">{extraction.axis_labels?.x_label || "—"}</p>
                </div>
                <div>
                  <span className="text-slate-400">Y-Axis:</span>
                  <p className="font-medium">{extraction.axis_labels?.y_label || "—"}</p>
                </div>
                <div className="col-span-2">
                  <span className="text-slate-400">Confidence:</span>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 h-2 rounded-full bg-slate-700 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500"
                        style={{ width: `${(extraction.extraction_confidence || 0) * 100}%` }}
                      />
                    </div>
                    <span className="font-medium">
                      {((extraction.extraction_confidence || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── Right: Reconstructed chart + controls ───────────────────── */}
        <div className="lg:w-1/2 flex flex-col gap-4 overflow-y-auto">
          {/* Universal Chart Renderer */}
          <div className="glass rounded-2xl p-4 flex-1 flex flex-col">
            {storeChart ? (
              <ChartRenderer chartId={chartId} />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-500">
                <span>Reconstruction not available</span>
              </div>
            )}
          </div>

          {/* Compliance panel */}
          <div className="glass rounded-2xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-green-400" />
                Copyright Compliance
              </span>
              <button
                onClick={handleRescore}
                disabled={rescoring}
                className="px-3 py-1 rounded-lg glass text-xs hover:bg-white/5 transition-colors flex items-center gap-1.5"
              >
                {rescoring ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <RefreshCw className="w-3 h-3" />
                )}
                Re-score
              </button>
            </div>

            {compliance ? (
              <div className="flex gap-6">
                <ScoreGauge score={compliance.similarity_score} risk={compliance.risk_level} />
                <div className="flex-1 space-y-3">
                  {/* Risk badge */}
                  <div className="flex items-center gap-2">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold badge-${compliance.risk_level}`}>
                      {compliance.risk_level.toUpperCase()} RISK
                    </span>
                  </div>

                  {/* Sub-scores */}
                  {[
                    { label: "Color", value: compliance.color_similarity },
                    { label: "Layout", value: compliance.layout_similarity },
                    { label: "Geometry", value: compliance.geometry_similarity },
                  ].map((sub) => (
                    <div key={sub.label} className="text-xs">
                      <div className="flex justify-between text-slate-400 mb-0.5">
                        <span>{sub.label}</span>
                        <span>{sub.value?.toFixed(0)}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-slate-700 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-green-500 via-amber-500 to-red-500"
                          style={{ width: `${sub.value || 0}%` }}
                        />
                      </div>
                    </div>
                  ))}

                  {/* Recommendations */}
                  {compliance.recommendations?.length > 0 && (
                    <div className="space-y-1.5 pt-1">
                      {compliance.recommendations.slice(0, 3).map((rec: any) => (
                        <div
                          key={rec.id}
                          className={`flex items-start gap-2 text-xs p-2 rounded-lg ${
                            rec.priority === "high"
                              ? "bg-red-500/10 border border-red-500/20"
                              : rec.priority === "info"
                              ? "bg-green-500/10 border border-green-500/20"
                              : "bg-amber-500/10 border border-amber-500/20"
                          }`}
                        >
                          {rec.priority === "high" ? (
                            <AlertTriangle className="w-3.5 h-3.5 text-red-400 mt-0.5 flex-shrink-0" />
                          ) : rec.priority === "info" ? (
                            <Check className="w-3.5 h-3.5 text-green-400 mt-0.5 flex-shrink-0" />
                          ) : (
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 mt-0.5 flex-shrink-0" />
                          )}
                          <span className="text-slate-300">{rec.text}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-6 text-sm text-slate-400">
                <ShieldCheck className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                Compliance data not yet available
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
