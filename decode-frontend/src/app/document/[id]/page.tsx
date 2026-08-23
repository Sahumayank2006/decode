"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft, BarChart3, FileText, Clock, CheckCircle2,
  Loader2, XCircle, ScanLine, PieChart, LineChart,
  Layers, ShieldCheck, Download, Eye, RefreshCw,
} from "lucide-react";
import { getDocument, getDocumentStatus, getDocumentCharts } from "@/lib/api";

const PIPELINE_STAGES = [
  { key: "uploaded",       icon: FileText,    label: "Uploaded" },
  { key: "ingesting",      icon: ScanLine,    label: "Ingesting" },
  { key: "detecting",      icon: Layers,      label: "Detecting" },
  { key: "extracting",     icon: BarChart3,   label: "Extracting" },
  { key: "reconstructing", icon: PieChart,    label: "Reconstructing" },
  { key: "scoring",        icon: ShieldCheck, label: "Scoring" },
  { key: "done",           icon: CheckCircle2,label: "Done" },
];

const CHART_TYPE_ICONS: Record<string, any> = {
  bar_chart: BarChart3,
  line_chart: LineChart,
  pie_chart: PieChart,
  scatter_plot: ScanLine,
  table: Layers,
  flowchart: Layers,
  process_diagram: Layers,
  unknown: ScanLine,
  // Fallbacks for older records
  bar: BarChart3,
  line: LineChart,
  pie: PieChart,
  scatter: ScanLine,
  diagram: ScanLine,
  other: Layers,
};

function getStageIndex(status: string): number {
  const idx = PIPELINE_STAGES.findIndex((s) => s.key === status);
  return idx >= 0 ? idx : 0;
}

export default function DocumentPage() {
  const router = useRouter();
  const params = useParams();
  const docId = params.id as string;

  const [doc, setDoc] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);
  const [charts, setCharts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const [docData, statusData, chartsData] = await Promise.all([
        getDocument(docId),
        getDocumentStatus(docId),
        getDocumentCharts(docId).catch(() => ({ charts: [] })),
      ]);
      setDoc(docData);
      setStatus(statusData);
      setCharts(chartsData.charts || []);
    } catch (e) {
      console.error("Failed to fetch document:", e);
    } finally {
      setLoading(false);
    }
  }, [docId]);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 3000);
    return () => clearInterval(interval);
  }, [refresh]);

  const currentStage = getStageIndex(doc?.status || "uploaded");
  const isDone = doc?.status === "done";
  const isFailed = doc?.status === "failed";
  const isProcessing = !isDone && !isFailed && doc?.status !== "uploaded";

  if (loading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-bg">
      {/* ── Nav ──────────────────────────────────────────────────────── */}
      <nav className="glass-strong sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <button
            onClick={() => router.push("/dashboard")}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div className="min-w-0">
              <div className="font-bold truncate">{doc?.filename || "Document"}</div>
              <div className="text-xs text-slate-400">Document Analysis</div>
            </div>
          </div>
          <button
            onClick={refresh}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors text-slate-400"
          >
            <RefreshCw className={`w-5 h-5 ${isProcessing ? "animate-spin" : ""}`} />
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* ── Pipeline stepper ─────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-6 mb-8"
        >
          <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-400" />
            Processing Pipeline
          </h2>

          <div className="flex items-center justify-between relative">
            {/* Progress bar background */}
            <div className="absolute top-5 left-0 right-0 h-0.5 bg-slate-700 mx-8" />
            <div
              className="absolute top-5 left-0 h-0.5 bg-gradient-to-r from-indigo-500 to-cyan-500 mx-8 transition-all duration-1000"
              style={{
                width: `${(currentStage / (PIPELINE_STAGES.length - 1)) * 100}%`,
              }}
            />

            {PIPELINE_STAGES.map((stage, i) => {
              const isActive = i === currentStage;
              const isCompleted = i < currentStage;
              const StageIcon = stage.icon;
              const isCurrent = isActive && isProcessing;

              return (
                <div
                  key={stage.key}
                  className="flex flex-col items-center relative z-10"
                >
                  <div
                    className={`
                      w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500
                      ${isCompleted
                        ? "bg-gradient-to-br from-indigo-500 to-cyan-500 text-white"
                        : isActive
                          ? isFailed
                            ? "bg-red-500/20 border-2 border-red-500 text-red-400"
                            : "bg-indigo-500/20 border-2 border-indigo-500 text-indigo-400"
                          : "bg-slate-800 border-2 border-slate-700 text-slate-500"
                      }
                    `}
                  >
                    {isCurrent ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : isCompleted ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : isFailed && isActive ? (
                      <XCircle className="w-5 h-5" />
                    ) : (
                      <StageIcon className="w-5 h-5" />
                    )}
                  </div>
                  <span
                    className={`text-xs mt-2 font-medium ${
                      isActive
                        ? isFailed ? "text-red-400" : "text-indigo-400"
                        : isCompleted ? "text-white" : "text-slate-500"
                    }`}
                  >
                    {stage.label}
                  </span>
                </div>
              );
            })}
          </div>

          {isFailed && doc?.error_message && (
            <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-sm text-red-400">
              <strong>Error:</strong> {doc.error_message}
            </div>
          )}
        </motion.div>

        {/* ── Processing events timeline ───────────────────────────────── */}
        {status?.events && status.events.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass rounded-2xl p-6 mb-8"
          >
            <h2 className="text-lg font-bold mb-4">Processing Log</h2>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {status.events.map((evt: any, i: number) => (
                <div key={i} className="flex items-start gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0" />
                  <div>
                    <span className="text-slate-400">[{evt.stage}]</span>{" "}
                    <span className="text-slate-300">{evt.message}</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── Detected charts grid ─────────────────────────────────────── */}
        {charts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-cyan-400" />
              Detected Charts
              <span className="text-sm font-normal text-slate-400">
                ({charts.length} found)
              </span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {charts.map((chart, i) => {
                const TypeIcon = CHART_TYPE_ICONS[chart.chart_type] || Layers;
                return (
                  <motion.div
                    key={chart.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.05 }}
                    className="glass rounded-2xl overflow-hidden card-hover cursor-pointer group"
                    onClick={() => router.push(`/chart/${chart.id}`)}
                  >
                    {/* Chart preview image */}
                    <div className="aspect-[4/3] bg-slate-800 relative overflow-hidden">
                      {chart.original_image_base64 ? (
                        <img
                          src={`data:image/png;base64,${chart.original_image_base64}`}
                          alt={`Chart from page ${chart.page_number}`}
                          className="w-full h-full object-contain p-2"
                        />
                      ) : chart.original_image_path ? (
                        <img
                          src={`http://localhost:5000${chart.original_image_path}`}
                          alt={`Chart from page ${chart.page_number}`}
                          className="w-full h-full object-contain p-2"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <TypeIcon className="w-16 h-16 text-slate-600" />
                        </div>
                      )}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-center pb-4">
                        <span className="text-sm font-medium text-white flex items-center gap-1">
                          <Eye className="w-4 h-4" /> Open Workspace
                        </span>
                      </div>
                    </div>

                    {/* Chart info */}
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <TypeIcon className="w-4 h-4 text-indigo-400" />
                          <span className="text-sm font-semibold capitalize">
                            {chart.chart_type.replace(/_/g, ' ')}
                          </span>
                        </div>
                        <span className="text-xs text-slate-400">
                          Page {chart.page_number}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 rounded-full bg-slate-700 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500"
                            style={{ width: `${(chart.detection_confidence || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-400">
                          {((chart.detection_confidence || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                      {chart.classification_reason && (
                        <p className="mt-2 text-xs text-slate-400 line-clamp-2" title={chart.classification_reason}>
                          {chart.classification_reason}
                        </p>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}

        {isDone && charts.length === 0 && (
          <div className="glass rounded-2xl p-12 text-center">
            <ScanLine className="w-12 h-12 text-slate-500 mx-auto mb-4" />
            <p className="text-lg font-medium mb-2">No Charts Detected</p>
            <p className="text-sm text-slate-400">
              The pipeline completed but no chart regions were found in this PDF.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
