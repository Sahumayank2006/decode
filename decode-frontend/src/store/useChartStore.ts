import { create } from 'zustand';

export interface ChartSeries {
  id: string;
  name: string;
  color?: string;
}

export interface ChartDataPoint {
  id: string;
  category: string;
  values: Record<string, number | null>;
}

export type ChartRenderType =
  | "bar" | "stacked_bar" | "line" | "area" | "pie" | "donut"
  | "scatter" | "radar" | "table";

export interface CanonicalChart {
  id: string;
  title: string;
  sourceType: string;
  activeType: ChartRenderType;
  xAxisLabel?: string;
  yAxisLabel?: string;
  series: ChartSeries[];
  data: ChartDataPoint[];
  confidence: number;
  editHistory: { timestamp: string; field: string; oldValue: any; newValue: any }[];
}

interface ChartState {
  charts: Record<string, CanonicalChart>;
  setChart: (chart: CanonicalChart) => void;
  setActiveType: (chartId: string, type: ChartRenderType) => void;
  updateDataPoint: (chartId: string, categoryId: string, seriesId: string, value: number | null) => void;
  addCategory: (chartId: string, categoryName: string) => void;
  addSeries: (chartId: string, seriesName: string, color?: string) => void;
}

export const useChartStore = create<ChartState>((set) => ({
  charts: {},

  setChart: (chart) => set((state) => ({
    charts: { ...state.charts, [chart.id]: chart }
  })),

  setActiveType: (chartId, type) => set((state) => {
    const chart = state.charts[chartId];
    if (!chart) return state;
    return {
      charts: {
        ...state.charts,
        [chartId]: { ...chart, activeType: type }
      }
    };
  }),

  updateDataPoint: (chartId, categoryId, seriesId, value) => set((state) => {
    const chart = state.charts[chartId];
    if (!chart) return state;

    const dataIndex = chart.data.findIndex(d => d.id === categoryId);
    if (dataIndex === -1) return state;

    const oldDataPoint = chart.data[dataIndex];
    const oldValue = oldDataPoint.values[seriesId];
    if (oldValue === value) return state; // no change

    const newDataPoint = {
      ...oldDataPoint,
      values: { ...oldDataPoint.values, [seriesId]: value }
    };

    const newData = [...chart.data];
    newData[dataIndex] = newDataPoint;

    const editEntry = {
      timestamp: new Date().toISOString(),
      field: `data.${categoryId}.${seriesId}`,
      oldValue,
      newValue: value
    };

    return {
      charts: {
        ...state.charts,
        [chartId]: {
          ...chart,
          data: newData,
          editHistory: [...chart.editHistory, editEntry]
        }
      }
    };
  }),

  addCategory: (chartId, categoryName) => set((state) => {
    const chart = state.charts[chartId];
    if (!chart) return state;

    const newId = `cat_${Date.now()}`;
    const initialValues: Record<string, null> = {};
    chart.series.forEach(s => { initialValues[s.id] = null; });

    const newCategory: ChartDataPoint = {
      id: newId,
      category: categoryName,
      values: initialValues
    };

    return {
      charts: {
        ...state.charts,
        [chartId]: {
          ...chart,
          data: [...chart.data, newCategory],
          editHistory: [
            ...chart.editHistory,
            { timestamp: new Date().toISOString(), field: 'category_add', oldValue: null, newValue: categoryName }
          ]
        }
      }
    };
  }),

  addSeries: (chartId, seriesName, color = '#8884d8') => set((state) => {
    const chart = state.charts[chartId];
    if (!chart) return state;

    const newSeriesId = `series_${Date.now()}`;
    const newSeries: ChartSeries = {
      id: newSeriesId,
      name: seriesName,
      color
    };

    const newData = chart.data.map(d => ({
      ...d,
      values: { ...d.values, [newSeriesId]: null }
    }));

    return {
      charts: {
        ...state.charts,
        [chartId]: {
          ...chart,
          series: [...chart.series, newSeries],
          data: newData,
          editHistory: [
            ...chart.editHistory,
            { timestamp: new Date().toISOString(), field: 'series_add', oldValue: null, newValue: seriesName }
          ]
        }
      }
    };
  })
}));
