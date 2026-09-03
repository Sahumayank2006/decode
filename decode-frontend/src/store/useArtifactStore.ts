"use client";

/* eslint-disable @typescript-eslint/no-unused-vars */
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
  error?: string;
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

export const INITIAL_BENCHMARK_ARTIFACTS: ArtifactExtraction[] = [];

const DIAGRAM_CHART_TYPES = new Set([
  "diagram", "flow", "flowchart", "process", "pipeline",
  "network", "org_chart", "architecture"
]);

function getInitialRenderMode(chart?: ArtifactExtraction): RenderMode {
  if (!chart) return "bar";
  const type = chart.chart_type?.toLowerCase() || "";

  // Diagram / non-numeric types default to original view
  if (DIAGRAM_CHART_TYPES.has(type)) return "original";

  // No data → show original
  if ((!chart.categories || chart.categories.length === 0) &&
      (!chart.series || chart.series.length === 0)) {
    return "original";
  }

  if (type === "table") return "table";
  if (type === "line" || type === "multi_line" || type === "area_spline") return "line";
  if (type === "area") return "area";
  if (type === "pie") return "pie";
  if (type === "donut" || type === "doughnut") return "donut";
  if (type === "radar" || type === "spider") return "radar";
  if (type === "stacked_bar") return "stacked_bar";
  if (type === "grouped_bar") return "bar";
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
  selectedArtifactId: null,
  artifacts: {},
  renderMode: "bar",
  history: {},
  historyIndex: {},

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
      artifacts: {},
      selectedArtifactId: null,
      renderMode: "bar",
      history: {},
      historyIndex: {},
    });
  },
}));
