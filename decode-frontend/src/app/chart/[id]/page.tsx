"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft, BarChart3, PieChart, LineChart, Grid3X3,
  Download, RefreshCw, Loader2, ShieldCheck, Palette,
  Check, AlertTriangle, XCircle, ChevronDown,
  Pencil, Eye, Sparkles, ArrowRight, ScanLine,
} from "lucide-react";
import {
  BarChart, Bar, LineChart as RLineChart, Line, PieChart as RPieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell,
} from "recharts";
import { getChart, reconstructChart, rescoreChart, getExportUrl } from "@/lib/api";

const CHART_TYPES = [
  { key: "bar",     icon: BarChart3, label: "Bar" },
  { key: "line",    icon: LineChart, label: "Line" },
  { key: "pie",     icon: PieChart,  label: "Pie" },
  { key: "heatmap", icon: Grid3X3,   label: "Heatmap" },
];

const PALETTE_NAMES = ["default", "vibrant", "pastel", "dark", "academic"];

const PALETTE_PREVIEWS: Record<string, string[]> = {
  default:  ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f"],
  vibrant:  ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"],
  pastel:   ["#b3e2cd", "#fdcdac", "#cbd5e8", "#f4cae4", "#e6f5c9"],
  dark:     ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e"],
  academic: ["#2c3e50", "#e74c3c", "#3498db", "#2ecc71", "#f39c12"],
};

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

function RechartsRender({
  config,
  chartType,
}: {
  config: any;
  chartType: string;
}) {
  if (!config || !config.data || config.data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500">
        <span>No chart data available</span>
      </div>
    );
  }

  const series = config.series || [];

  if (chartType === "pie") {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <RPieChart>
          <Pie
            data={config.data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius="75%"
            label={({ name, percent }: any) =>
              `${name}: ${(percent * 100).toFixed(0)}%`
            }
            labelLine
          >
            {config.data.map((entry: any, i: number) => (
              <Cell key={i} fill={entry.fill || PALETTE_PREVIEWS.default[i % 5]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#1a1d2e", border: "1px solid #2e3348",
              borderRadius: "12px", color: "#e2e8f0",
            }}
          />
          <Legend />
        </RPieChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "line") {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <RLineChart data={config.data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2e3348" />
          <XAxis
            dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={{ stroke: "#2e3348" }}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={{ stroke: "#2e3348" }}
          />
          <Tooltip
            contentStyle={{
              background: "#1a1d2e", border: "1px solid #2e3348",
              borderRadius: "12px", color: "#e2e8f0",
            }}
          />
          <Legend />
          {series.map((s: any) => (
            <Line
              key={s.dataKey}
              type="monotone"
              dataKey={s.dataKey}
              stroke={s.color}
              strokeWidth={2.5}
              dot={{ fill: s.color, r: 4 }}
              name={s.name}
            />
          ))}
        </RLineChart>
      </ResponsiveContainer>
    );
  }

  // Default: bar
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={config.data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2e3348" />
        <XAxis
          dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }}
          axisLine={{ stroke: "#2e3348" }}
        />
        <YAxis
          tick={{ fill: "#94a3b8", fontSize: 12 }}
          axisLine={{ stroke: "#2e3348" }}
        />
        <Tooltip
          contentStyle={{
            background: "#1a1d2e", border: "1px solid #2e3348",
            borderRadius: "12px", color: "#e2e8f0",
          }}
        />
        <Legend />
        {series.map((s: any) => (
          <Bar
            key={s.dataKey}
            dataKey={s.dataKey}
            fill={s.color}
            name={s.name}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function ChartWorkspacePage() {
  const router = useRouter();
  const params = useParams();
  const chartId = params.id as string;

  const [chart, setChart] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [reconstructing, setReconstructing] = useState(false);
  const [rescoring, setRescoring] = useState(false);
  const [activeType, setActiveType] = useState("bar");
  const [activePalette, setActivePalette] = useState("default");
  const [showPalettes, setShowPalettes] = useState(false);
  const [tab, setTab] = useState<"preview" | "data" | "compliance">("preview");

  const fetchChart = useCallback(async () => {
    try {
      const data = await getChart(chartId);
      setChart(data);
      if (data.reconstruction?.chart_type) {
        setActiveType(data.reconstruction.chart_type);
      } else if (data.chart_type) {
        setActiveType(data.chart_type);
      }
    } catch (e) {
      console.error("Failed to fetch chart:", e);
    } finally {
      setLoading(false);
    }
  }, [chartId]);

  useEffect(() => { fetchChart(); }, [fetchChart]);

  const handleTypeSwitch = async (type: string) => {
    setActiveType(type);
    setReconstructing(true);
    try {
      const result = await reconstructChart(chartId, {
        chart_type: type,
        palette: activePalette,
      });
      setChart((prev: any) => ({ ...prev, reconstruction: result }));
    } catch (e) {
      console.error("Reconstruction failed:", e);
    } finally {
      setReconstructing(false);
    }
  };

  const handlePaletteChange = async (palette: string) => {
    setActivePalette(palette);
    setShowPalettes(false);
    setReconstructing(true);
    try {
      const result = await reconstructChart(chartId, {
        chart_type: activeType,
        palette,
      });
      setChart((prev: any) => ({ ...prev, reconstruction: result }));
    } catch (e) {
      console.error("Palette change failed:", e);
    } finally {
      setReconstructing(false);
    }
  };

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
  const reconstruction = chart?.reconstruction;
  const compliance = chart?.compliance;
  const config = reconstruction?.chart_config;

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
            <Download className="w-3.5 h-3.5" /> PNG
          </a>
          <a
            href={getExportUrl(chartId, "svg")}
            download
            className="px-3 py-1.5 rounded-lg glass text-xs font-medium text-slate-300 hover:text-white flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5" /> SVG
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
        <div className="lg:w-1/2 flex flex-col gap-4">
          {/* Chart type switcher + palette */}
          <div className="glass rounded-2xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold flex items-center gap-2">
                <Pencil className="w-4 h-4 text-indigo-400" />
                Chart Controls
              </span>

              {/* Palette picker */}
              <div className="relative">
                <button
                  onClick={() => setShowPalettes(!showPalettes)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass text-xs hover:bg-white/5 transition-colors"
                >
                  <Palette className="w-3.5 h-3.5" />
                  <div className="flex gap-0.5">
                    {(PALETTE_PREVIEWS[activePalette] || PALETTE_PREVIEWS.default).slice(0, 4).map((c, i) => (
                      <div key={i} className="w-3 h-3 rounded-sm" style={{ background: c }} />
                    ))}
                  </div>
                  <ChevronDown className="w-3 h-3" />
                </button>

                <AnimatePresence>
                  {showPalettes && (
                    <motion.div
                      initial={{ opacity: 0, y: -5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -5 }}
                      className="absolute right-0 top-full mt-1 glass-strong rounded-xl p-3 w-52 z-50"
                    >
                      {PALETTE_NAMES.map((name) => (
                        <button
                          key={name}
                          onClick={() => handlePaletteChange(name)}
                          className={`w-full flex items-center gap-2 p-2 rounded-lg text-xs capitalize transition-colors ${
                            activePalette === name ? "bg-indigo-500/20 text-white" : "hover:bg-white/5 text-slate-300"
                          }`}
                        >
                          <div className="flex gap-0.5">
                            {PALETTE_PREVIEWS[name]?.map((c, i) => (
                              <div key={i} className="w-3.5 h-3.5 rounded-sm" style={{ background: c }} />
                            ))}
                          </div>
                          <span>{name}</span>
                          {activePalette === name && <Check className="w-3 h-3 ml-auto text-indigo-400" />}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Type buttons */}
            <div className="flex gap-2">
              {CHART_TYPES.map(({ key, icon: Icon, label }) => (
                <button
                  key={key}
                  onClick={() => handleTypeSwitch(key)}
                  disabled={reconstructing}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-medium transition-all duration-200 ${
                    activeType === key
                      ? "bg-gradient-to-r from-indigo-600 to-indigo-500 text-white"
                      : "glass text-slate-400 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Reconstructed chart */}
          <div className="glass rounded-2xl p-4 flex-1 flex flex-col">
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-semibold">Reconstructed Chart</span>
              {reconstructing && <Loader2 className="w-4 h-4 animate-spin text-indigo-400 ml-auto" />}
            </div>

            <div className="flex-1 min-h-[300px]">
              {config ? (
                <RechartsRender config={config} chartType={activeType} />
              ) : reconstruction?.image_base64 ? (
                <div className="w-full h-full flex items-center justify-center">
                  <img
                    src={`data:image/png;base64,${reconstruction.image_base64}`}
                    alt="Reconstructed chart"
                    className="max-w-full max-h-full object-contain"
                  />
                </div>
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-500">
                  <span>Reconstruction not available</span>
                </div>
              )}
            </div>

            {/* Recommendation */}
            {reconstruction?.recommended_alt_type &&
             reconstruction.recommended_alt_type !== activeType && (
              <div className="mt-3 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs">
                <div className="flex items-start gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-medium text-indigo-300">AI Recommendation: </span>
                    <span className="text-slate-300">{reconstruction.recommendation_reason}</span>
                    <button
                      onClick={() => handleTypeSwitch(reconstruction.recommended_alt_type)}
                      className="ml-2 text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center gap-1"
                    >
                      Try {reconstruction.recommended_alt_type} <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
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
                          {rec.auto_applicable && rec.id === "change_palette" && (
                            <button
                              onClick={() => handlePaletteChange(
                                activePalette === "default" ? "academic" : "default"
                              )}
                              className="ml-auto text-indigo-400 hover:text-indigo-300 font-medium whitespace-nowrap"
                            >
                              Apply
                            </button>
                          )}
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
