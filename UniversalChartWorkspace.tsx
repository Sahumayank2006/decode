/**
 * UniversalChartWorkspace.tsx
 * -----------------------------------------------------------------------
 * Reference implementation for DECODE — Part D (Reconstruction &
 * Interconversion Module).
 *
 * ONE canonical data model -> MANY renderers (bar/line/area/pie/scatter/
 * radar/table). Switching type never mutates or drops data. The table is
 * the canonical editor: edit a cell there, every other view updates
 * instantly because they all read the same store.
 *
 * Drop into a Next.js + TypeScript + Tailwind + shadcn/ui + Recharts +
 * Zustand project (matches the DECODE stack from Part A). Split into
 * separate files once wired to real extraction output — kept as one file
 * here so it's easy to read end to end.
 * -----------------------------------------------------------------------
 */

import React, { useMemo, useState } from "react";
import { create } from "zustand";
import {
  BarChart, Bar,
  LineChart, Line,
  AreaChart, Area,
  PieChart, Pie, Cell,
  ScatterChart, Scatter,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

/* ------------------------------------------------------------------ */
/* 1. Canonical data model                                             */
/* ------------------------------------------------------------------ */

export type ChartRenderType =
  | "bar" | "stacked_bar" | "line" | "area" | "pie" | "donut"
  | "scatter" | "radar" | "table";

export interface ChartSeries {
  id: string;
  name: string;
  color?: string;
}

export interface ChartDataPoint {
  id: string;
  category: string;
  values: Record<string, number | null>; // seriesId -> value | null (unreadable, never invented)
}

export interface EditEvent {
  timestamp: string;
  field: string;
  oldValue: number | string | null;
  newValue: number | string | null;
}

export interface CanonicalChart {
  id: string;
  title: string;
  sourceType: ChartRenderType;   // as originally classified/extracted
  activeType: ChartRenderType;   // as currently displayed
  xAxisLabel?: string;
  yAxisLabel?: string;
  series: ChartSeries[];
  data: ChartDataPoint[];
  confidence: number;
  editHistory: EditEvent[];
}

const PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"];

/* ------------------------------------------------------------------ */
/* 2. Zustand store — single source of truth per chart id             */
/* ------------------------------------------------------------------ */

interface ChartStoreState {
  charts: Record<string, CanonicalChart>;
  loadChart: (chart: CanonicalChart) => void;
  setActiveType: (chartId: string, type: ChartRenderType) => void;
  updateCell: (chartId: string, pointId: string, field: "category" | string, value: string) => void;
  addRow: (chartId: string) => void;
  addSeries: (chartId: string, name: string) => void;
  undo: (chartId: string) => void;
}

export const useChartStore = create<ChartStoreState>((set, get) => ({
  charts: {},

  loadChart: (chart) =>
    set((s) => ({ charts: { ...s.charts, [chart.id]: chart } })),

  setActiveType: (chartId, type) =>
    set((s) => {
      const chart = s.charts[chartId];
      if (!chart) return s;
      // Pure view change — data and series are untouched.
      return { charts: { ...s.charts, [chartId]: { ...chart, activeType: type } } };
    }),

  updateCell: (chartId, pointId, field, rawValue) =>
    set((s) => {
      const chart = s.charts[chartId];
      if (!chart) return s;

      const point = chart.data.find((p) => p.id === pointId);
      if (!point) return s;

      const isCategory = field === "category";
      const oldValue = isCategory ? point.category : point.values[field];

      let newValue: string | number | null;
      if (isCategory) {
        newValue = rawValue;
      } else {
        if (rawValue.trim() === "") {
          newValue = null; // explicit "unreadable/cleared", never coerced to 0
        } else {
          const parsed = Number(rawValue);
          if (Number.isNaN(parsed)) return s; // reject non-numeric silently at store level;
          // the input component below shows the red-outline validation UX
          newValue = parsed;
        }
      }

      const updatedData = chart.data.map((p) =>
        p.id !== pointId
          ? p
          : isCategory
          ? { ...p, category: newValue as string }
          : { ...p, values: { ...p.values, [field]: newValue as number | null } }
      );

      const event: EditEvent = {
        timestamp: new Date().toISOString(),
        field: isCategory ? `${pointId}.category` : `${pointId}.${field}`,
        oldValue,
        newValue,
      };

      return {
        charts: {
          ...s.charts,
          [chartId]: {
            ...chart,
            data: updatedData,
            editHistory: [...chart.editHistory, event].slice(-20),
          },
        },
      };
    }),

  addRow: (chartId) =>
    set((s) => {
      const chart = s.charts[chartId];
      if (!chart) return s;
      const newPoint: ChartDataPoint = {
        id: `pt-${Date.now()}`,
        category: "New category",
        values: Object.fromEntries(chart.series.map((sr) => [sr.id, null])),
      };
      return { charts: { ...s.charts, [chartId]: { ...chart, data: [...chart.data, newPoint] } } };
    }),

  addSeries: (chartId, name) =>
    set((s) => {
      const chart = s.charts[chartId];
      if (!chart) return s;
      const newSeries: ChartSeries = {
        id: `series-${Date.now()}`,
        name,
        color: PALETTE[chart.series.length % PALETTE.length],
      };
      const updatedData = chart.data.map((p) => ({
        ...p,
        values: { ...p.values, [newSeries.id]: null },
      }));
      return {
        charts: {
          ...s.charts,
          [chartId]: { ...chart, series: [...chart.series, newSeries], data: updatedData },
        },
      };
    }),

  undo: (chartId) =>
    set((s) => {
      const chart = s.charts[chartId];
      if (!chart || chart.editHistory.length === 0) return s;
      const last = chart.editHistory[chart.editHistory.length - 1];
      const [pointId, field] = last.field.includes(".category")
        ? [last.field.replace(".category", ""), "category"]
        : [last.field.split(".")[0], last.field.split(".")[1]];
      const updatedData = chart.data.map((p) =>
        p.id !== pointId
          ? p
          : field === "category"
          ? { ...p, category: last.oldValue as string }
          : { ...p, values: { ...p.values, [field]: last.oldValue as number | null } }
      );
      return {
        charts: {
          ...s.charts,
          [chartId]: { ...chart, data: updatedData, editHistory: chart.editHistory.slice(0, -1) },
        },
      };
    }),
}));

/* ------------------------------------------------------------------ */
/* 3. Flat row shape Recharts actually wants — derived, never stored   */
/* ------------------------------------------------------------------ */

function toRechartsRows(chart: CanonicalChart) {
  return chart.data.map((p) => {
    const row: Record<string, string | number | null> = { category: p.category };
    chart.series.forEach((s) => (row[s.id] = p.values[s.id]));
    return row;
  });
}

/* ------------------------------------------------------------------ */
/* 4. Universal renderer                                               */
/* ------------------------------------------------------------------ */

function TypeUnavailableNotice({ reason }: { reason: string }) {
  return (
    <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-slate-300 text-sm text-slate-500 px-6 text-center">
      {reason}
    </div>
  );
}

export function ChartRenderer({ chart }: { chart: CanonicalChart }) {
  const rows = useMemo(() => toRechartsRows(chart), [chart]);

  switch (chart.activeType) {
    case "bar":
    case "stacked_bar":
      return (
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="category" label={{ value: chart.xAxisLabel, position: "insideBottom", offset: -5 }} />
            <YAxis label={{ value: chart.yAxisLabel, angle: -90, position: "insideLeft" }} />
            <Tooltip />
            <Legend />
            {chart.series.map((s) => (
              <Bar
                key={s.id}
                dataKey={s.id}
                name={s.name}
                fill={s.color ?? PALETTE[0]}
                stackId={chart.activeType === "stacked_bar" ? "stack" : undefined}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      );

    case "line":
      return (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="category" />
            <YAxis />
            <Tooltip />
            <Legend />
            {chart.series.map((s) => (
              <Line key={s.id} type="monotone" dataKey={s.id} name={s.name} stroke={s.color ?? PALETTE[0]} connectNulls={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      );

    case "area":
      return (
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="category" />
            <YAxis />
            <Tooltip />
            <Legend />
            {chart.series.map((s) => (
              <Area key={s.id} type="monotone" dataKey={s.id} name={s.name} stroke={s.color ?? PALETTE[0]} fill={s.color ?? PALETTE[0]} fillOpacity={0.25} />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      );

    case "pie":
    case "donut": {
      const primary = chart.series[0];
      if (!primary) return <TypeUnavailableNotice reason="No numeric series to plot." />;
      const pieRows = chart.data.map((p) => ({ name: p.category, value: p.values[primary.id] ?? 0 }));
      return (
        <div>
          {chart.series.length > 1 && (
            <p className="mb-2 text-xs text-slate-500">
              Pie shows &ldquo;{primary.name}&rdquo; only — switch to bar or line to compare all {chart.series.length} series.
            </p>
          )}
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={pieRows}
                dataKey="value"
                nameKey="name"
                innerRadius={chart.activeType === "donut" ? 70 : 0}
                outerRadius={110}
                label
              >
                {pieRows.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      );
    }

    case "scatter": {
      if (chart.series.length < 2) {
        return <TypeUnavailableNotice reason="Scatter needs at least 2 numeric series (X and Y) — this chart only has 1." />;
      }
      const [sx, sy] = chart.series;
      const scatterRows = chart.data.map((p) => ({ x: p.values[sx.id], y: p.values[sy.id], category: p.category }));
      return (
        <ResponsiveContainer width="100%" height={320}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="x" name={sx.name} />
            <YAxis dataKey="y" name={sy.name} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={scatterRows} fill={PALETTE[0]} />
          </ScatterChart>
        </ResponsiveContainer>
      );
    }

    case "radar": {
      if (chart.data.length < 3) {
        return <TypeUnavailableNotice reason={`Radar needs at least 3 categories — this chart only has ${chart.data.length}.`} />;
      }
      return (
        <ResponsiveContainer width="100%" height={320}>
          <RadarChart data={rows}>
            <PolarGrid />
            <PolarAngleAxis dataKey="category" />
            <PolarRadiusAxis />
            {chart.series.map((s) => (
              <Radar key={s.id} name={s.name} dataKey={s.id} stroke={s.color ?? PALETTE[0]} fill={s.color ?? PALETTE[0]} fillOpacity={0.3} />
            ))}
            <Legend />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      );
    }

    case "table":
      return <EditableTable chart={chart} />;

    default:
      return <TypeUnavailableNotice reason={`Unknown render type "${chart.activeType}".`} />;
  }
}

/* ------------------------------------------------------------------ */
/* 5. Editable table — the canonical editor                            */
/* ------------------------------------------------------------------ */

function EditableTable({ chart }: { chart: CanonicalChart }) {
  const { updateCell, addRow, addSeries } = useChartStore();
  const [invalidCell, setInvalidCell] = useState<string | null>(null);

  function handleValueChange(pointId: string, seriesId: string, raw: string) {
    const cellKey = `${pointId}.${seriesId}`;
    if (raw.trim() !== "" && Number.isNaN(Number(raw))) {
      setInvalidCell(cellKey);
      return;
    }
    setInvalidCell(null);
    updateCell(chart.id, pointId, seriesId, raw);
  }

  return (
    <div>
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-slate-300 text-left">
            <th className="py-2 pr-4 font-medium text-slate-600">{chart.xAxisLabel ?? "Category"}</th>
            {chart.series.map((s) => (
              <th key={s.id} className="py-2 pr-4 font-medium text-slate-600">{s.name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {chart.data.map((point) => (
            <tr key={point.id} className="border-b border-slate-100">
              <td className="py-1 pr-4">
                <input
                  className="w-full rounded border border-transparent px-2 py-1 hover:border-slate-200 focus:border-blue-400 focus:outline-none"
                  defaultValue={point.category}
                  onBlur={(e) => updateCell(chart.id, point.id, "category", e.target.value)}
                />
              </td>
              {chart.series.map((s) => {
                const cellKey = `${point.id}.${s.id}`;
                const value = point.values[s.id];
                return (
                  <td key={s.id} className="py-1 pr-4">
                    <input
                      className={`w-24 rounded border px-2 py-1 text-right focus:outline-none ${
                        invalidCell === cellKey
                          ? "border-red-500 focus:border-red-500"
                          : "border-transparent hover:border-slate-200 focus:border-blue-400"
                      } ${value === null ? "text-slate-300 italic" : ""}`}
                      defaultValue={value === null ? "" : String(value)}
                      placeholder="unreadable"
                      onChange={(e) => handleValueChange(point.id, s.id, e.target.value)}
                    />
                    {invalidCell === cellKey && (
                      <div className="text-xs text-red-500">Numbers only</div>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-3 flex gap-2">
        <button
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
          onClick={() => addRow(chart.id)}
        >
          + Add category
        </button>
        <button
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
          onClick={() => addSeries(chart.id, `Series ${chart.series.length + 1}`)}
        >
          + Add series
        </button>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* 6. Export utilities — real Blob downloads, not stubs                */
/* ------------------------------------------------------------------ */

function downloadBlob(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function exportChartAsCSV(chart: CanonicalChart) {
  const header = [chart.xAxisLabel ?? "category", ...chart.series.map((s) => s.name)];
  const lines = chart.data.map((p) =>
    [p.category, ...chart.series.map((s) => (p.values[s.id] ?? ""))].join(",")
  );
  downloadBlob([header.join(","), ...lines].join("\n"), `${chart.title || "chart"}.csv`, "text/csv");
}

export function exportChartConfig(chart: CanonicalChart) {
  navigator.clipboard.writeText(JSON.stringify(chart, null, 2));
}

/**
 * PNG/SVG export of the currently rendered chart: in the real app, wrap the
 * <ChartRenderer> in a ref and use a library already common in this stack
 * (e.g. html-to-image's toPng/toSvg, or Recharts' own SVG node) — pass that
 * ref in from ChartWorkspace. Kept out of this file to avoid a DOM-only
 * dependency in a reference snippet; the contract is: export whatever
 * `activeType` is CURRENTLY on screen, not always chart.sourceType.
 */

/* ------------------------------------------------------------------ */
/* 7. Workspace — toolbar + renderer wired to the store                */
/* ------------------------------------------------------------------ */

const TYPE_OPTIONS: { type: ChartRenderType; label: string }[] = [
  { type: "bar", label: "Bar" },
  { type: "stacked_bar", label: "Stacked" },
  { type: "line", label: "Line" },
  { type: "area", label: "Area" },
  { type: "pie", label: "Pie" },
  { type: "donut", label: "Donut" },
  { type: "scatter", label: "Scatter" },
  { type: "radar", label: "Radar" },
  { type: "table", label: "Table" },
];

function isTypeDisabled(chart: CanonicalChart, type: ChartRenderType): string | null {
  if (type === "scatter" && chart.series.length < 2) return "Needs 2+ numeric series";
  if (type === "radar" && chart.data.length < 3) return "Needs 3+ categories";
  return null;
}

export function ChartWorkspace({ chartId }: { chartId: string }) {
  const chart = useChartStore((s) => s.charts[chartId]);
  const setActiveType = useChartStore((s) => s.setActiveType);
  const undo = useChartStore((s) => s.undo);

  if (!chart) return null;

  return (
    <div className="rounded-xl border border-slate-200 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-800">{chart.title}</h3>
        <span className="text-xs text-slate-400">confidence: {Math.round(chart.confidence * 100)}%</span>
      </div>

      <div className="mb-4 flex flex-wrap gap-1">
        {TYPE_OPTIONS.map(({ type, label }) => {
          const disabledReason = isTypeDisabled(chart, type);
          const active = chart.activeType === type;
          return (
            <button
              key={type}
              title={disabledReason ?? undefined}
              disabled={!!disabledReason}
              onClick={() => setActiveType(chart.id, type)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                active ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              } ${disabledReason ? "cursor-not-allowed opacity-40" : ""}`}
            >
              {label}
            </button>
          );
        })}
      </div>

      <ChartRenderer chart={chart} />

      <div className="mt-3 flex gap-2 border-t border-slate-100 pt-3">
        <button className="text-xs text-slate-500 hover:text-slate-800" onClick={() => exportChartAsCSV(chart)}>
          Export CSV
        </button>
        <button className="text-xs text-slate-500 hover:text-slate-800" onClick={() => exportChartConfig(chart)}>
          Copy config
        </button>
        <button
          className="text-xs text-slate-500 hover:text-slate-800 disabled:opacity-30"
          disabled={chart.editHistory.length === 0}
          onClick={() => undo(chart.id)}
        >
          Undo last edit
        </button>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* 8. Sample data — for local testing only. Replace with real          */
/*    reconstructChart(extraction, chartType) output before shipping.  */
/* ------------------------------------------------------------------ */

export const SAMPLE_CHART: CanonicalChart = {
  id: "chart-1",
  title: "Quarterly Revenue by Region (sample — replace with real extraction)",
  sourceType: "bar",
  activeType: "bar",
  xAxisLabel: "Quarter",
  yAxisLabel: "Revenue ($M)",
  confidence: 0.87,
  editHistory: [],
  series: [
    { id: "s-north", name: "North", color: PALETTE[0] },
    { id: "s-south", name: "South", color: PALETTE[1] },
  ],
  data: [
    { id: "pt-1", category: "Q1", values: { "s-north": 12, "s-south": 9 } },
    { id: "pt-2", category: "Q2", values: { "s-north": 15, "s-south": 11 } },
    { id: "pt-3", category: "Q3", values: { "s-north": null, "s-south": 14 } }, // unreadable in source PDF
    { id: "pt-4", category: "Q4", values: { "s-north": 19, "s-south": 17 } },
  ],
};
