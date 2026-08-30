"use client";
/* eslint-disable */

import { create } from "zustand";

/* ============================================================
   DECODE CANONICAL FRONTEND TYPES
   ============================================================ */

export type ChartRenderType =
  | "bar"
  | "line"
  | "pie"
  | "donut"
  | "scatter"
  | "area"
  | "radar"
  | "stacked_bar"
  | "horizontal_bar"
  | "grouped_bar"
  | "histogram"
  | "funnel"
  | "table";

export interface ChartDataPoint {
  category: string;
  label?: string;
  [key: string]: string | number | null | undefined;
}

export interface ChartSeries {
  id: string;
  name: string;
  key?: string;
  color?: string;
  data?: Array<number | string | null>;
  values?: Array<number | string | null>;
}

export interface CanonicalChart {
  id: string;
  title: string;

  sourceType?: string;

  activeType: ChartRenderType;
  chart_type: ChartRenderType;

  xAxisLabel?: string;
  yAxisLabel?: string;

  categories: string[];

  series: ChartSeries[];

  data: ChartDataPoint[];

  confidence?: number;

  editHistory: ChartEdit[];

  metadata?: Record<string, unknown>;
}

export interface ChartEdit {
  id: string;
  timestamp: string;
  action: string;
  details?: Record<string, unknown>;
}

export interface ProcessingEvent {
  id?: string;
  timestamp?: string;
  stage?: string;
  message?: string;
  status?: string;
}

export type ProcessingStatus =
  | "idle"
  | "uploading"
  | "processing"
  | "completed"
  | "failed";

/* ============================================================
   STORE
   ============================================================ */

interface ChartStore {
  /* Current chart */
  chart: CanonicalChart | null;

  /* Multiple charts */
  charts: Record<string, CanonicalChart>;

  /* UI */
  activeChartId: string | null;
  activeType: ChartRenderType;
  activePanel: "preview" | "data" | "insights" | "export";

  /* Processing */
  processingStatus: ProcessingStatus;
  processingEvents: ProcessingEvent[];

  /* History */
  history: CanonicalChart[];
  historyIndex: number;

  /* Compatibility */
  setChart: (chart: CanonicalChart | null) => void;

  setChartType: (
    chartId: string,
    chartType: ChartRenderType
  ) => void;

  updateChart: (
    chartId: string,
    updates: Partial<CanonicalChart>
  ) => void;

  updateDataPoint: (
    chartId: string,
    rowIndex: number,
    seriesKey: string,
    value: string | number | null
  ) => void;

  addCategory: (
    chartId: string,
    category: string
  ) => void;

  addSeries: (
    chartId: string,
    series: ChartSeries
  ) => void;

  removeSeries: (seriesId: string) => void;

  removeCategory: (index: number) => void;

  updateCategory: (index: number, category: string) => void;

  updateSeriesName: (seriesId: string, name: string) => void;

  setProcessingStatus: (status: ProcessingStatus) => void;

  addProcessingEvent: (event: ProcessingEvent) => void;

  reset: () => void;

  undo: () => void;

  redo: () => void;
}

/* ============================================================
   HELPERS
   ============================================================ */

function cloneChart(chart: CanonicalChart): CanonicalChart {
  return JSON.parse(JSON.stringify(chart));
}

function normalizeChart(chart: CanonicalChart): CanonicalChart {
  const categories =
    chart.categories ??
    chart.data?.map((row) => String(row.category ?? "")) ??
    [];

  const series =
    chart.series ??
    [];

  const data =
    chart.data ??
    categories.map((category, index) => {
      const row: ChartDataPoint = {
        category,
      };

      for (const s of series) {
        row[s.id] = Number(s.values?.[index] ?? 0);
      }

      return row;
    });

  return {
    ...chart,

    chart_type:
      chart.chart_type ??
      chart.activeType ??
      "bar",

    activeType:
      chart.activeType ??
      chart.chart_type ??
      "bar",

    categories,

    series,

    data,

    editHistory: chart.editHistory ?? [],
  };
}

/* ============================================================
   STORE IMPLEMENTATION
   ============================================================ */

export const useChartStore = create<ChartStore>((set, get) => ({
  chart: null,

  charts: {},

  activeChartId: null,

  activeType: "bar",

  activePanel: "preview",

  processingStatus: "idle",

  processingEvents: [],

  history: [],

  historyIndex: -1,

  /* ----------------------------------------------------------
     SET CHART
     ---------------------------------------------------------- */

  setChart: (chart) => {
    set({
      chart: chart,
      activeChartId: chart?.id ?? null,
    });
  },

  /* ----------------------------------------------------------
     SET MULTIPLE CHARTS
     ---------------------------------------------------------- */

  setCharts: (charts: any) => {
    const map: Record<string, CanonicalChart> = {};

    if (Array.isArray(charts)) {
      for (const chart of charts) {
        const normalized = normalizeChart(chart);
        map[normalized.id] = normalized;
      }
    } else {
      for (const [id, chart] of Object.entries(charts)) {
        map[id] = normalizeChart(chart as CanonicalChart);
      }
    }

    const first = Object.values(map)[0] ?? null;

    set({
      charts: map,
      chart: first,
      activeChartId: first?.id ?? null,
      activeType: first?.activeType ?? "bar",
    });
  },

  /* ----------------------------------------------------------
     SET ACTIVE CHART ID
     ---------------------------------------------------------- */

  setActiveChartId: (id: any) => set({ activeChartId: id }),

  /* ----------------------------------------------------------
     GET CHART
     ---------------------------------------------------------- */

  getChart: (id: any) => {
    const state = get();

    if (id) {
      return state.charts[id] ?? null;
    }

    if (state.activeChartId) {
      return state.charts[state.activeChartId] ?? null;
    }

    return state.chart;
  },

  /* ----------------------------------------------------------
     CHART TYPE
     ---------------------------------------------------------- */

  setChartType: (chartId, chartType) => {
    set((state) => {
      const charts = Object.values(state.charts).map((chart) => {
        if (chart.id !== chartId) {
          return chart;
        }

        return {
          ...chart,
          activeType: chartType,
          chart_type: chartType,
        };
      });

      const chartsMap: Record<string, CanonicalChart> = {};
      charts.forEach(c => chartsMap[c.id] = c);

      return {
        charts: chartsMap,
        chart:
          state.chart?.id === chartId
            ? {
                ...state.chart,
                activeType: chartType,
                chart_type: chartType,
              }
            : state.chart,
      };
    });
  },

  updateChart: (chartId, updates) => {
    set((state) => {
      const charts = Object.values(state.charts).map((chart) =>
        chart.id === chartId
          ? {
              ...chart,
              ...updates,
            } as CanonicalChart
          : chart
      );

      const chartsMap: Record<string, CanonicalChart> = {};
      charts.forEach(c => chartsMap[c.id] = c);

      const activeChart =
        state.chart?.id === chartId
          ? {
              ...state.chart,
              ...updates,
            } as CanonicalChart
          : state.chart;

      return {
        charts: chartsMap,
        chart: activeChart,
      };
    });
  },

  /* ----------------------------------------------------------
     PANEL
     ---------------------------------------------------------- */

  setActivePanel: (panel: any) => {
    set({
      activePanel: panel,
    });
  },

  /* ----------------------------------------------------------
     UPDATE DATA POINT
     ---------------------------------------------------------- */

  updateDataPoint: (
    chartId,
    rowIndex,
    seriesKey,
    value
  ) => {
    set((state) => {
      const target = state.charts[chartId] || (state.chart?.id === chartId ? state.chart : null);

      if (!target) {
        return state;
      }

      const data = Array.isArray(target.data)
        ? [...target.data]
        : [];

      const currentRow = {
        ...(data[rowIndex] as Record<string, unknown> | undefined),
      };

      currentRow[seriesKey] = value;

      data[rowIndex] = currentRow as ChartDataPoint;

      const updatedChart = {
        ...target,
        data,
      };

      return {
        charts: {
          ...state.charts,
          [chartId]: updatedChart,
        },
        chart:
          state.chart?.id === chartId
            ? updatedChart
            : state.chart,
      };
    });
  },

  addCategory: (chartId, category) => {
    set((state) => {
      const chart = state.charts[chartId] || (state.chart?.id === chartId ? state.chart : null);

      if (!chart) {
        return state;
      }

      const existingData = Array.isArray(chart.data)
        ? [...chart.data]
        : [];

      existingData.push({
        category,
      } as ChartDataPoint);

      const updatedChart = {
        ...chart,
        data: existingData,
      };

      return {
        charts: {
          ...state.charts,
          [chartId]: updatedChart,
        },
        chart:
          state.chart?.id === chartId
            ? updatedChart
            : state.chart,
      };
    });
  },

  /* ----------------------------------------------------------
     REMOVE CATEGORY
     ---------------------------------------------------------- */

  removeCategory: (index) => {
    set((state) => {
      if (!state.chart) {
        return state;
      }

      const chart = cloneChart(state.chart);

      if (
        index < 0 ||
        index >= chart.categories.length
      ) {
        return state;
      }

      chart.categories.splice(index, 1);
      chart.data.splice(index, 1);

      for (const series of chart.series) {
        if (series.values) series.values.splice(index, 1);
      }

      return {
        chart,

        charts: {
          ...state.charts,
          [chart.id]: chart,
        },
      };
    });
  },

  /* ----------------------------------------------------------
     UPDATE CATEGORY
     ---------------------------------------------------------- */

  updateCategory: (index, category) => {
    set((state) => {
      if (!state.chart) {
        return state;
      }

      const chart = cloneChart(state.chart);

      if (!chart.categories[index]) {
        return state;
      }

      chart.categories[index] = category;

      if (chart.data[index]) {
        chart.data[index].category = category;
      }

      return {
        chart,

        charts: {
          ...state.charts,
          [chart.id]: chart,
        },
      };
    });
  },

  /* ----------------------------------------------------------
     ADD SERIES
     ---------------------------------------------------------- */

  addSeries: (chartId, series) => {
    set((state) => {
      const chart = state.charts[chartId] || (state.chart?.id === chartId ? state.chart : null);

      if (!chart) {
        return state;
      }

      const existingSeries = Array.isArray(chart.series)
        ? [...chart.series]
        : [];

      existingSeries.push(series);

      const updatedChart = {
        ...chart,
        series: existingSeries,
      };

      return {
        charts: {
          ...state.charts,
          [chartId]: updatedChart,
        },
        chart:
          state.chart?.id === chartId
            ? updatedChart
            : state.chart,
      };
    });
  },

  /* ----------------------------------------------------------
     REMOVE SERIES
     ---------------------------------------------------------- */

  removeSeries: (seriesId) => {
    set((state) => {
      if (!state.chart) {
        return state;
      }

      const chart = cloneChart(state.chart);

      chart.series = chart.series.filter(
        (series) => series.id !== seriesId
      );

      for (const row of chart.data) {
        delete row[seriesId];
      }

      return {
        chart,

        charts: {
          ...state.charts,
          [chart.id]: chart,
        },
      };
    });
  },

  /* ----------------------------------------------------------
     UPDATE SERIES NAME
     ---------------------------------------------------------- */

  updateSeriesName: (seriesId, name) => {
    set((state) => {
      if (!state.chart) {
        return state;
      }

      const chart = cloneChart(state.chart);

      const series = chart.series.find(
        (item) => item.id === seriesId
      );

      if (series) {
        series.name = name;
      }

      return {
        chart,

        charts: {
          ...state.charts,
          [chart.id]: chart,
        },
      };
    });
  },

  /* ----------------------------------------------------------
     PROCESSING
     ---------------------------------------------------------- */

  setProcessingStatus: (status) => {
    set({
      processingStatus: status,
    });
  },

  addProcessingEvent: (event) => {
    set((state) => ({
      processingEvents: [
        ...state.processingEvents,
        event,
      ],
    }));
  },

  /* ----------------------------------------------------------
     UNDO
     ---------------------------------------------------------- */

  undo: () => {
    set((state) => {
      if (state.historyIndex <= 0) {
        return state;
      }

      const newIndex =
        state.historyIndex - 1;

      const previous =
        cloneChart(state.history[newIndex]);

      return {
        chart: previous,

        charts: {
          ...state.charts,
          [previous.id]: previous,
        },

        historyIndex: newIndex,

        activeType:
          previous.activeType,
      };
    });
  },

  /* ----------------------------------------------------------
     REDO
     ---------------------------------------------------------- */

  redo: () => {
    set((state) => {
      if (
        state.historyIndex >=
        state.history.length - 1
      ) {
        return state;
      }

      const newIndex =
        state.historyIndex + 1;

      const next =
        cloneChart(state.history[newIndex]);

      return {
        chart: next,

        charts: {
          ...state.charts,
          [next.id]: next,
        },

        historyIndex: newIndex,

        activeType:
          next.activeType,
      };
    });
  },

  /* ----------------------------------------------------------
     RESET
     ---------------------------------------------------------- */

  reset: () => {
    set({
      chart: null,
      charts: {},
      activeChartId: null,
      activeType: "bar",
      activePanel: "preview",
      processingStatus: "idle",
      processingEvents: [],
      history: [],
      historyIndex: -1,
    });
  },
}));

export default useChartStore;
