"use client";

import React from "react";
import {
  BarChart3,
  LineChart,
  PieChart,
  AreaChart,
  Radar,
  Layers3,
} from "lucide-react";

import {
  CanonicalChart,
  ChartRenderType,
  useChartStore,
} from "../../store/useChartStore";

import { getValidChartTypes } from "../../lib/chartUtils";

/* ============================================================
   PROPS
   ============================================================ */

interface Props {
  chart?: CanonicalChart;
}

/* ============================================================
   ICON MAP
   ============================================================ */

const ICONS: Record<string, React.ReactNode> = {
  bar: <BarChart3 size={17} />,
  line: <LineChart size={17} />,
  pie: <PieChart size={17} />,
  donut: <PieChart size={17} />,
  area: <AreaChart size={17} />,
  stacked_bar: <Layers3 size={17} />,
  radar: <Radar size={17} />,
};

/* ============================================================
   LABELS
   ============================================================ */

const LABELS: Record<string, string> = {
  bar: "Bar",
  line: "Line",
  pie: "Pie",
  donut: "Donut",
  area: "Area",
  stacked_bar: "Stacked",
  radar: "Radar",
};

/* ============================================================
   COMPONENT
   ============================================================ */

export function ChartTypeSwitcher({ chart }: Props) {
  const { charts, chart: storeChart, activeChartId, setChartType, updateChart } = useChartStore();

  const activeChart =
    chart ||
    storeChart ||
    (charts && activeChartId
      ? charts[activeChartId]
      : undefined);

  if (!activeChart) {
    return null;
  }

  const activeType =
    activeChart.activeType ||
    activeChart.chart_type ||
    "bar";

  const validTypes = getValidChartTypes(activeChart);

  const setType = (type: ChartRenderType) => {
    if (typeof setChartType === "function") {
      setChartType(activeChart.id, type);
    }
    if (typeof updateChart === "function") {
      updateChart(activeChart.id, {
        activeType: type,
        chart_type: type,
      });
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      {validTypes.map((type) => {
        const isActive = type === activeType;

        return (
          <button
            key={type}
            type="button"
            onClick={() => setType(type)}
            className={[
              "inline-flex items-center gap-2 rounded-xl border px-3 py-2",
              "text-sm font-medium transition-all duration-200",
              "focus:outline-none focus:ring-2 focus:ring-emerald-500/30",
              isActive
                ? "border-emerald-500 bg-emerald-50 text-emerald-700 shadow-sm"
                : "border-slate-200 bg-white text-slate-600 hover:border-emerald-300 hover:bg-emerald-50/40",
            ].join(" ")}
            aria-pressed={isActive}
          >
            {ICONS[type] || <BarChart3 size={17} />}
            <span>{LABELS[type] || type}</span>
          </button>
        );
      })}
    </div>
  );
}

export default ChartTypeSwitcher;
