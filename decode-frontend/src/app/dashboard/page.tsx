"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, FileText, BarChart3, Clock, Trash2, Eye,
  Loader2, CheckCircle2, AlertCircle, XCircle,
  Plus, ArrowRight, ChevronRight, RefreshCw,
  PieChart, LineChart, ScanLine,
} from "lucide-react";
import { uploadDocument, listDocuments, deleteDocument } from "@/lib/api";

type Doc = {
  id: string;
  filename: string;
  status: string;
  file_size?: number;
  created_at?: string;
  summary?: { total_charts_detected?: number };
};

const STATUS_CONFIG: Record<string, { icon: any; color: string; label: string }> = {
  uploaded:       { icon: Clock,        color: "text-slate-400",  label: "Uploaded" },
  ingesting:      { icon: Loader2,      color: "text-blue-400",   label: "Ingesting" },
  detecting:      { icon: ScanLine,     color: "text-cyan-400",   label: "Detecting Charts" },
  extracting:     { icon: BarChart3,    color: "text-purple-400", label: "Extracting Data" },
  reconstructing: { icon: PieChart,     color: "text-amber-400",  label: "Reconstructing" },
  scoring:        { icon: LineChart,    color: "text-green-400",  label: "Scoring Compliance" },
  processing:     { icon: Loader2,      color: "text-indigo-400", label: "Processing" },
  done:           { icon: CheckCircle2, color: "text-green-400",  label: "Complete" },
  failed:         { icon: XCircle,      color: "text-red-400",    label: "Failed" },
};

function formatFileSize(bytes?: number): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso?: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

export default function DashboardPage() {
  const router = useRouter();
  const [docs, setDocs] = useState<Doc[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchDocs = useCallback(async () => {
    try {
      const data = await listDocuments();
      setDocs(data.documents || []);
    } catch {
      setError("Could not connect to DECODE backend. Is it running on port 5000?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocs();
    const interval = setInterval(fetchDocs, 5000);
    return () => clearInterval(interval);
  }, [fetchDocs]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    const file = acceptedFiles[0];
    setUploading(true);
    setError("");
    try {
      const result = await uploadDocument(file);
      await fetchDocs();
      if (result.document_id) {
        router.push(`/document/${result.document_id}`);
      }
    } catch (e: any) {
      setError(e?.response?.data?.error || "Upload failed. Check backend connection.");
    } finally {
      setUploading(false);
    }
  }, [fetchDocs, router]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
    disabled: uploading,
  });

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } catch {
      setError("Delete failed");
    }
  };

  const processingDocs = docs.filter((d) =>
    !["done", "failed", "uploaded"].includes(d.status)
  );
  const completedDocs = docs.filter((d) => d.status === "done");
  const totalCharts = docs.reduce(
    (sum, d) => sum + (d.summary?.total_charts_detected || 0), 0
  );

  return (
    <div className="min-h-screen gradient-bg">
      {/* ── Top bar ──────────────────────────────────────────────────── */}
      <nav className="glass-strong sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <button onClick={() => router.push("/")} className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">DECODE</span>
          </button>
          <button
            onClick={fetchDocs}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors text-slate-400 hover:text-white"
            title="Refresh"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* ── Stats ────────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Documents", value: docs.length, icon: FileText, color: "from-indigo-500 to-indigo-600" },
            { label: "Charts Found", value: totalCharts, icon: BarChart3, color: "from-cyan-500 to-cyan-600" },
            { label: "Processing", value: processingDocs.length, icon: Loader2, color: "from-amber-500 to-amber-600" },
            { label: "Completed", value: completedDocs.length, icon: CheckCircle2, color: "from-green-500 to-green-600" },
          ].map((stat) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-5"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">{stat.label}</span>
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center`}>
                  <stat.icon className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold">{stat.value}</div>
            </motion.div>
          ))}
        </div>

        {/* ── Upload zone ──────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div
            {...getRootProps()}
            className={`
              glass rounded-2xl p-10 text-center cursor-pointer transition-all duration-300
              border-2 border-dashed
              ${isDragActive
                ? "border-indigo-400 bg-indigo-500/10"
                : "border-slate-700 hover:border-indigo-500/50 hover:bg-indigo-500/5"
              }
              ${uploading ? "opacity-60 pointer-events-none" : ""}
            `}
          >
            <input {...getInputProps()} />
            {uploading ? (
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="w-12 h-12 text-indigo-400 animate-spin" />
                <p className="text-lg font-medium">Uploading & starting pipeline…</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 flex items-center justify-center">
                  <Upload className="w-8 h-8 text-indigo-400" />
                </div>
                <p className="text-lg font-medium">
                  {isDragActive ? "Drop your PDF here" : "Upload a Research Paper PDF"}
                </p>
                <p className="text-sm text-slate-400">
                  Drag and drop or click to browse · PDF up to 50 MB
                </p>
              </div>
            )}
          </div>
        </motion.div>

        {/* ── Error toast ──────────────────────────────────────────────── */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">{error}</span>
              <button onClick={() => setError("")} className="ml-auto">
                <XCircle className="w-4 h-4" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Documents list ───────────────────────────────────────────── */}
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            Your Documents
          </h2>

          {loading ? (
            <div className="glass rounded-2xl p-12 text-center">
              <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mx-auto mb-3" />
              <p className="text-slate-400">Loading documents…</p>
            </div>
          ) : docs.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center">
              <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mx-auto mb-4">
                <Plus className="w-8 h-8 text-slate-500" />
              </div>
              <p className="text-lg font-medium mb-2">No documents yet</p>
              <p className="text-sm text-slate-400">Upload your first research paper PDF to get started.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {docs.map((doc, i) => {
                const sc = STATUS_CONFIG[doc.status] || STATUS_CONFIG.uploaded;
                const StatusIcon = sc.icon;
                const isSpinning = ["ingesting", "detecting", "extracting", "reconstructing", "scoring", "processing"].includes(doc.status);
                return (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="glass rounded-xl p-4 flex items-center gap-4 group card-hover"
                  >
                    <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{doc.filename}</div>
                      <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                        <span>{formatFileSize(doc.file_size)}</span>
                        <span>·</span>
                        <span>{formatDate(doc.created_at)}</span>
                        {doc.summary?.total_charts_detected !== undefined && (
                          <>
                            <span>·</span>
                            <span className="text-cyan-400">
                              {doc.summary.total_charts_detected} charts
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className={`flex items-center gap-1.5 text-sm ${sc.color}`}>
                      <StatusIcon className={`w-4 h-4 ${isSpinning ? "animate-spin" : ""}`} />
                      <span className="hidden sm:inline">{sc.label}</span>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => router.push(`/document/${doc.id}`)}
                        className="p-2 rounded-lg hover:bg-white/10 transition-colors text-slate-400 hover:text-white"
                        title="View"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-2 rounded-lg hover:bg-red-500/20 transition-colors text-slate-400 hover:text-red-400"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <button
                      onClick={() => router.push(`/document/${doc.id}`)}
                      className="p-2 text-slate-500 hover:text-white transition-colors"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
