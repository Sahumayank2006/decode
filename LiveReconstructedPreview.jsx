// LiveReconstructedPreview.jsx
//
// Complete replacement for the "Live Reconstructed Preview" panel.
// Works identically for ANY selected artifact (bar, stacked, line, area,
// pie, donut, radar) — there is exactly one data path, and no hardcoded
// fallback dataset anywhere in this file. If you see a chart that isn't
// the selected artifact's real data after dropping this in, the bug is
// upstream (whatever passes `artifact` into this component), not here.

import React, { useMemo } from "react";
import {
  BarChart, Bar,
  LineChart, Line,
  AreaChart, Area,
  PieChart, Pie, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ComposedChart,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

const PALETTE = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD"];

/**
 * Expected shape of `artifact.render` (this MUST come from your backend's
 * chart_pipeline.py `to_frontend_payload()` output — see render_spec in
 * the schema. Do not hand-roll a different shape here.):
 * {
 *   library_hint: "recharts",
 *   categories: ["Solar", "Wind", "Hybrid", "GridAI"],
 *   series: [{ name: "Region A", color: "#4C72B0", values: [62, 71, 78, 91] }, ...]
 * }
 */

// --- Step 1: one shared transform, used by every mode below ------------
// This is the whole fix. Every chart mode reads from THIS array. There is
// no per-mode data source, so modes can never show different numbers.
function toRechartsData(renderSpec) {
  if (!renderSpec || !renderSpec.categories || !renderSpec.series) return [];
  return renderSpec.categories.map((cat, i) => {
    const row = { name: cat };
    renderSpec.series.forEach((s) => {
      row[s.name] = s.values[i];
    });
    return row;
  });
}

// Pie/Donut charts need a flat [{name, value}] shape instead of the
// multi-series row shape above. Only used when a single series is being
// visualized as a pie — if there are multiple series, pie mode isn't
// meaningful and we show a message instead of guessing.
function toPieData(renderSpec) {
  if (!renderSpec || renderSpec.series.length !== 1) return null;
  const s = renderSpec.series[0];
  return renderSpec.categories.map((cat, i) => ({ name: cat, value: s.values[i] }));
}

export default function LiveReconstructedPreview({ artifact, mode }) {
  // `artifact` = the currently selected artifact's full object, expected
  // to contain `.render` (render_spec) and `.title`. NOTHING else in this
  // component holds its own copy of chart data — it is derived fresh
  // every render from this one prop.

  const chartData = useMemo(() => toRechartsData(artifact?.render), [artifact]);
  const pieData = useMemo(() => toPieData(artifact?.render), [artifact]);
  const seriesNames = artifact?.render?.series?.map((s) => s.name) ?? [];
  const seriesColors = Object.fromEntries(
    (artifact?.render?.series ?? []).map((s, i) => [s.name, s.color || PALETTE[i % PALETTE.length]])
  );

  // --- Guard: no artifact selected, or it has no render data yet -------
  if (!artifact) {
    return <EmptyState message="Select an artifact to preview its reconstruction." />;
  }
  if (!artifact.render || chartData.length === 0) {
    return <EmptyState message="No extracted data available for this artifact yet." />;
  }

  return (
    <ResponsiveContainer width="100%" height={360}>
      {renderChart(mode, chartData, pieData, seriesNames, seriesColors)}
    </ResponsiveContainer>
  );
}

// --- Step 2: mode switch is ONLY a visualization choice -----------------
// Every branch below reads from the SAME `chartData` (or `pieData`,
// itself derived from the same render_spec). Switching modes changes
// how the numbers are drawn, never what the numbers are.
function renderChart(mode, chartData, pieData, seriesNames, seriesColors) {
  switch (mode) {
    case "bar":
      return (
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A3350" />
          <XAxis dataKey="name" stroke="#8A93B8" />
          <YAxis stroke="#8A93B8" />
          <Tooltip />
          <Legend />
          {seriesNames.map((name) => (
            <Bar key={name} dataKey={name} fill={seriesColors[name]} />
          ))}
        </BarChart>
      );

    case "stacked":
      return (
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A3350" />
          <XAxis dataKey="name" stroke="#8A93B8" />
          <YAxis stroke="#8A93B8" />
          <Tooltip />
          <Legend />
          {seriesNames.map((name) => (
            <Bar key={name} dataKey={name} stackId="stack" fill={seriesColors[name]} />
          ))}
        </BarChart>
      );

    case "line":
      return (
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A3350" />
          <XAxis dataKey="name" stroke="#8A93B8" />
          <YAxis stroke="#8A93B8" />
          <Tooltip />
          <Legend />
          {seriesNames.map((name) => (
            <Line key={name} type="monotone" dataKey={name} stroke={seriesColors[name]} dot />
          ))}
        </LineChart>
      );

    case "area":
      return (
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A3350" />
          <XAxis dataKey="name" stroke="#8A93B8" />
          <YAxis stroke="#8A93B8" />
          <Tooltip />
          <Legend />
          {seriesNames.map((name) => (
            <Area key={name} type="monotone" dataKey={name} fill={seriesColors[name]} stroke={seriesColors[name]} fillOpacity={0.35} />
          ))}
        </AreaChart>
      );

    case "pie":
    case "donut":
      if (!pieData) {
        return <EmptyState message="Pie/Donut view needs a single-series chart. This artifact has multiple series — try Bar or Line instead." />;
      }
      return (
        <PieChart>
          <Pie
            data={pieData}
            dataKey="value"
            nameKey="name"
            innerRadius={mode === "donut" ? 60 : 0}
            outerRadius={110}
            label
          >
            {pieData.map((entry, i) => (
              <Cell key={entry.name} fill={PALETTE[i % PALETTE.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      );

    case "radar":
      return (
        <RadarChart data={chartData}>
          <PolarGrid stroke="#2A3350" />
          <PolarAngleAxis dataKey="name" stroke="#8A93B8" />
          <PolarRadiusAxis stroke="#8A93B8" />
          {seriesNames.map((name) => (
            <Radar key={name} name={name} dataKey={name} stroke={seriesColors[name]} fill={seriesColors[name]} fillOpacity={0.3} />
          ))}
          <Legend />
        </RadarChart>
      );

    default:
      // "bar" as a safe default — never fall back to a mock dataset
      return (
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A3350" />
          <XAxis dataKey="name" stroke="#8A93B8" />
          <YAxis stroke="#8A93B8" />
          <Tooltip />
          <Legend />
          {seriesNames.map((name) => (
            <Bar key={name} dataKey={name} fill={seriesColors[name]} />
          ))}
        </BarChart>
      );
  }
}

function EmptyState({ message }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "center",
      height: 360, color: "#8A93B8", fontSize: 14, textAlign: "center", padding: "0 24px",
    }}>
      {message}
    </div>
  );
}
