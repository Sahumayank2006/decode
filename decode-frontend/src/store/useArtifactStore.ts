"use client";

import { create } from "zustand";

export interface ArtifactSeries {
  name: string;
  values: number[];
  color?: string;
}

export interface ArtifactCompliance {
  overall_score: number;
  ssim_score: number;
  color_similarity: number;
  layout_similarity?: number;
  risk_level: "Low Risk" | "Medium Risk" | "High Risk";
  flags?: string[];
  recommendations?: string[];
}

export interface ArtifactExtraction {
  id: string;
  title: string;
  chart_type: string;
  page_number?: number;
  confidence?: number;
  categories: string[];
  series: ArtifactSeries[];
  original_image_path?: string;
  original_image_base64?: string;
  export_svg_path?: string;
  export_png_path?: string;
  compliance?: ArtifactCompliance;
  metadata?: Record<string, unknown>;
}

export type RenderMode =
  | "bar"
  | "stacked_bar"
  | "line"
  | "area"
  | "pie"
  | "donut"
  | "radar"
  | "table"
  | "original";

export const INITIAL_BENCHMARK_ARTIFACTS: ArtifactExtraction[] = [
  {
    id: "benchmark-resnet-accuracy",
    title: "Figure 1: Cross-Architecture Image Classification Benchmark",
    chart_type: "bar",
    page_number: 1,
    confidence: 0.99,
    categories: ["ResNet-50", "ViT-Base", "Swin-Transformer", "DECODE-Vision"],
    series: [
      {
        name: "Top-1 Accuracy (%)",
        values: [78.4, 84.5, 86.3, 89.1],
        color: "#3b82f6",
      },
      {
        name: "Top-5 Accuracy (%)",
        values: [92.1, 96.8, 97.4, 98.9],
        color: "#10b981",
      },
    ],
    compliance: {
      overall_score: 42,
      ssim_score: 38,
      color_similarity: 94,
      risk_level: "Medium Risk",
      flags: ["Direct layout mimicry from source PDF"],
      recommendations: ["Export in custom canonical palette for high-fidelity compliance"],
    },
    metadata: { source: "DECODE Benchmark Suite", model_eval: true },
  },
  {
    id: "benchmark-loss-progression",
    title: "Figure 2: Multi-Epoch Training & Validation Loss Curve",
    chart_type: "line",
    page_number: 2,
    confidence: 0.98,
    categories: ["Epoch 10", "Epoch 20", "Epoch 30", "Epoch 40", "Epoch 50", "Epoch 60"],
    series: [
      {
        name: "Training Loss",
        values: [0.82, 0.54, 0.35, 0.22, 0.15, 0.09],
        color: "#3b82f6",
      },
      {
        name: "Validation Loss",
        values: [0.89, 0.61, 0.41, 0.28, 0.23, 0.18],
        color: "#10b981",
      },
    ],
    compliance: {
      overall_score: 35,
      ssim_score: 31,
      color_similarity: 88,
      risk_level: "Low Risk",
      flags: [],
      recommendations: ["Canonical vector curves verify 100% numerical accuracy"],
    },
    metadata: { source: "DECODE Benchmark Suite", loss_eval: true },
  },
  {
    id: "benchmark-latency-breakdown",
    title: "Figure 3: Pipeline Inference Latency Breakdown",
    chart_type: "donut",
    page_number: 3,
    confidence: 0.97,
    categories: ["PDF Ingest", "Layout Detection", "Vision Extraction", "Reconstruct Engine", "SSIM Scoring"],
    series: [
      {
        name: "Latency (ms)",
        values: [45, 120, 310, 85, 60],
        color: "#f59e0b",
      },
    ],
    compliance: {
      overall_score: 28,
      ssim_score: 22,
      color_similarity: 85,
      risk_level: "Low Risk",
      flags: [],
      recommendations: ["Visual layout successfully refactored from raster scan"],
    },
    metadata: { source: "DECODE Benchmark Suite", latency_eval: true },
  },
  {
    id: "benchmark-table-matrix",
    title: "Table 1: Scientific Vision Extraction Benchmark Comparison",
    chart_type: "table",
    page_number: 4,
    confidence: 0.99,
    categories: ["ChartQA", "PlotQA", "DocVQA", "SciGraph", "DECODE Bench"],
    series: [
      {
        name: "Baseline OCR",
        values: [54.2, 61.0, 58.7, 49.3, 56.1],
        color: "#94a3b8",
      },
      {
        name: "Gemini 1.5",
        values: [78.9, 82.4, 86.1, 74.5, 80.2],
        color: "#818cf8",
      },
      {
        name: "DECODE Specialist",
        values: [91.4, 94.8, 96.2, 88.7, 95.3],
        color: "#10b981",
      },
    ],
    compliance: {
      overall_score: 18,
      ssim_score: 12,
      color_similarity: 90,
      risk_level: "Low Risk",
      flags: [],
      recommendations: ["Tabular data parsed directly into structured matrix"],
    },
    metadata: { source: "DECODE Benchmark Suite", table_eval: true },
  },
];

function getInitialRenderMode(chart?: ArtifactExtraction): RenderMode {
  if (!chart) return "bar";
  const type = chart.chart_type?.toLowerCase() || "";
  if (type === "table") return "table";
  if (type === "line" || type === "area_spline") return "line";
  if (type === "area") return "area";
  if (type === "pie") return "pie";
  if (type === "donut" || type === "doughnut") return "donut";
  if (type === "radar" || type === "spider") return "radar";
  if (type === "stacked_bar") return "stacked_bar";
  return "bar";
}

const initialMap = Object.fromEntries(INITIAL_BENCHMARK_ARTIFACTS.map((a) => [a.id, a]));
const initialHistory: Record<string, ArtifactExtraction[]> = Object.fromEntries(
  INITIAL_BENCHMARK_ARTIFACTS.map((a) => [a.id, [JSON.parse(JSON.stringify(a))]])
);
const initialHistoryIndex: Record<string, number> = Object.fromEntries(
  INITIAL_BENCHMARK_ARTIFACTS.map((a) => [a.id, 0])
);

export interface ArtifactStore {
  selectedArtifactId: string | null;
  artifacts: Record<string, ArtifactExtraction>;
  renderMode: RenderMode;
  history: Record<string, ArtifactExtraction[]>;
  historyIndex: Record<string, number>;

  // Actions
  setSelectedArtifact: (id: string) => void;
  setRenderMode: (mode: RenderMode) => void;
  loadArtifacts: (list: ArtifactExtraction[]) => void;
  updateArtifactData: (id: string, patch: Partial<ArtifactExtraction>) => void;
  updateCell: (id: string, seriesIndex: number, categoryIndex: number, value: number) => void;
  updateCategory: (id: string, categoryIndex: number, name: string) => void;
  updateSeriesName: (id: string, seriesIndex: number, name: string) => void;
  updateTitle: (id: string, title: string) => void;
  addRow: (id: string) => void;
  removeRow: (id: string, categoryIndex: number) => void;
  addSeries: (id: string) => void;
  removeSeries: (id: string, seriesIndex: number) => void;
  undo: (id: string) => void;
  redo: (id: string) => void;
  resetToBenchmarks: () => void;
}

export const useArtifactStore = create<ArtifactStore>((set, get) => ({
  selectedArtifactId: INITIAL_BENCHMARK_ARTIFACTS[0].id,
  artifacts: initialMap,
  renderMode: getInitialRenderMode(INITIAL_BENCHMARK_ARTIFACTS[0]),
  history: initialHistory,
  historyIndex: initialHistoryIndex,

  setSelectedArtifact: (id: string) => {
    const art = get().artifacts[id];
    if (art) {
      set({
        selectedArtifactId: id,
        renderMode: getInitialRenderMode(art),
      });
    }
  },

  setRenderMode: (mode: RenderMode) => {
    set({ renderMode: mode });
  },

  loadArtifacts: (list: ArtifactExtraction[]) => {
    if (!list || list.length === 0) return;
    const map = Object.fromEntries(list.map((a) => [a.id, a]));
    const firstId = list[0]?.id ?? null;
    const hist: Record<string, ArtifactExtraction[]> = Object.fromEntries(
      list.map((a) => [a.id, [JSON.parse(JSON.stringify(a))]])
    );
    const histIdx: Record<string, number> = Object.fromEntries(
      list.map((a) => [a.id, 0])
    );

    set({
      artifacts: map,
      selectedArtifactId: firstId,
      renderMode: getInitialRenderMode(list[0]),
      history: hist,
      historyIndex: histIdx,
    });
  },

  updateArtifactData: (id: string, patch: Partial<ArtifactExtraction>) => {
    const current = get().artifacts[id];
    if (!current) return;

    const updated: ArtifactExtraction = {
      ...current,
      ...patch,
    };

    const currentHist = get().history[id] || [current];
    const currentIdx = get().historyIndex[id] ?? 0;
    const newHist = currentHist.slice(0, currentIdx + 1);
    newHist.push(JSON.parse(JSON.stringify(updated)));
    if (newHist.length > 30) newHist.shift();

    set((state) => ({
      artifacts: {
        ...state.artifacts,
        [id]: updated,
      },
      history: {
        ...state.history,
        [id]: newHist,
      },
      historyIndex: {
        ...state.historyIndex,
        [id]: newHist.length - 1,
      },
    }));
  },

  updateCell: (id: string, seriesIndex: number, categoryIndex: number, value: number) => {
    const current = get().artifacts[id];
    if (!current) return;

    const cloned: ArtifactExtraction = JSON.parse(JSON.stringify(current));
    if (cloned.series[seriesIndex] && cloned.series[seriesIndex].values) {
      cloned.series[seriesIndex].values[categoryIndex] = isNaN(value) ? 0 : value;
      get().updateArtifactData(id, cloned);
    }
  },

  updateCategory: (id: string, categoryIndex: number, name: string) => {
    const current = get().artifacts[id];
    if (!current) return;

    const cloned: ArtifactExtraction = JSON.parse(JSON.stringify(current));
    if (cloned.categories) {
      cloned.categories[categoryIndex] = name;
      get().updateArtifactData(id, cloned);
    }
  },

  updateSeriesName: (id: string, seriesIndex: number, name: string) => {
    const current = get().artifacts[id];
    if (!current) return;

    const cloned: ArtifactExtraction = JSON.parse(JSON.stringify(current));
    if (cloned.series[seriesIndex]) {
      cloned.series[seriesIndex].name = name;
      get().updateArtifactData(id, cloned);
    }
  },

  updateTitle: (id: string, title: string) => {
    get().updateArtifactData(id, { title });
  },

  addRow: (id: string) => {
    const current = get().artifacts[id];
    if (!current) return;

    const cloned: ArtifactExtraction = JSON.parse(JSON.stringify(current));
    const newName = `Item ${cloned.categories.length + 1}`;
    cloned.categories.push(newName);
    cloned.series.forEach((s) => {
      if (!s.values) s.values = [];
      s.values.push(0);
    });
    get().updateArtifactData(id, cloned);
  },

  removeRow: (id: string, categoryIndex: number) => {
    const current = get().artifacts[id];
    if (!current || current.categories.length <= 1) return;

    const cloned: ArtifactExtraction = JSON.parse(JSON.stringify(current));
    cloned.categories.splice(categoryIndex, 1);
    cloned.series.forEach((s) => {
      if (s.values) s.values.splice(categoryIndex, 1);
    });
    get().updateArtifactData(id, cloned);
  },

  addSeries: (id: string) => {
    const current = get().artifacts[id];
    if (!current) return;

    const cloned: ArtifactExtraction = JSON.parse(JSON.stringify(current));
    const newName = `Series ${cloned.series.length + 1}`;
    const zeros = new Array(cloned.categories.length).fill(0);
    cloned.series.push({
      name: newName,
      values: zeros,
    });
    get().updateArtifactData(id, cloned);
  },

  removeSeries: (id: string, seriesIndex: number) => {
    const current = get().artifacts[id];
    if (!current || current.series.length <= 1) return;

    const cloned: ArtifactExtraction = JSON.parse(JSON.stringify(current));
    cloned.series.splice(seriesIndex, 1);
    get().updateArtifactData(id, cloned);
  },

  undo: (id: string) => {
    const currentIdx = get().historyIndex[id] ?? 0;
    const currentHist = get().history[id];
    if (!currentHist || currentIdx <= 0) return;

    const targetIdx = currentIdx - 1;
    const targetState = JSON.parse(JSON.stringify(currentHist[targetIdx]));

    set((state) => ({
      artifacts: {
        ...state.artifacts,
        [id]: targetState,
      },
      historyIndex: {
        ...state.historyIndex,
        [id]: targetIdx,
      },
    }));
  },

  redo: (id: string) => {
    const currentIdx = get().historyIndex[id] ?? 0;
    const currentHist = get().history[id];
    if (!currentHist || currentIdx >= currentHist.length - 1) return;

    const targetIdx = currentIdx + 1;
    const targetState = JSON.parse(JSON.stringify(currentHist[targetIdx]));

    set((state) => ({
      artifacts: {
        ...state.artifacts,
        [id]: targetState,
      },
      historyIndex: {
        ...state.historyIndex,
        [id]: targetIdx,
      },
    }));
  },

  resetToBenchmarks: () => {
    set({
      artifacts: initialMap,
      selectedArtifactId: INITIAL_BENCHMARK_ARTIFACTS[0].id,
      renderMode: getInitialRenderMode(INITIAL_BENCHMARK_ARTIFACTS[0]),
      history: initialHistory,
      historyIndex: initialHistoryIndex,
    });
  },
}));
