import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";
import { ArtifactExtraction } from "../../store/useArtifactStore";

const PALETTE = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD"];

interface LiveReconstructedPreviewProps {
  currentArtifact: ArtifactExtraction | null;
  renderMode: string;
  chartContainerRef?: React.RefObject<HTMLDivElement | null> | React.MutableRefObject<HTMLDivElement | null> | any;
}

/**
 * Returns true if the artifact is a non-numeric diagram/flow type
 * that cannot be rendered as a chart.
 */
function isDiagramArtifact(artifact: ArtifactExtraction): boolean {
  const type = (artifact.chart_type || "").toLowerCase();
  return (
    type === "diagram" ||
    type === "flow" ||
    type === "flowchart" ||
    type === "process" ||
    type === "pipeline" ||
    type === "network" ||
    type === "org_chart" ||
    type === "architecture"
  );
}

/**
 * Returns true if the artifact has no numeric data to render as a chart.
 */
function hasNoChartData(artifact: ArtifactExtraction): boolean {
  if (!artifact.categories || artifact.categories.length === 0) return true;
  if (!artifact.series || artifact.series.length === 0) return true;
  // Check if ALL values across ALL series are zero or missing
  const hasAnyNonZero = artifact.series.some(
    (s) => (s.values || []).some((v) => v !== 0 && v !== undefined && v !== null)
  );
  return !hasAnyNonZero;
}

export default function LiveReconstructedPreview({
  currentArtifact,
  renderMode,
  chartContainerRef
}: LiveReconstructedPreviewProps) {
  // commonData is derived directly from currentArtifact and shared across all chart modes
  const commonData = useMemo(() => {
    if (!currentArtifact || !currentArtifact.categories || currentArtifact.categories.length === 0) {
      return [];
    }
    return currentArtifact.categories.map((cat, catIdx) => {
      const row: Record<string, any> = {
        name: cat,
        category: cat,
      };
      (currentArtifact.series || []).forEach((s) => {
        const val = s.values?.[catIdx];
        row[s.name] = val !== undefined && val !== null && !isNaN(Number(val)) ? Number(val) : 0;
      });
      return row;
    });
  }, [currentArtifact]);

  // pieData is derived from the first series of currentArtifact
  const pieData = useMemo(() => {
    if (!currentArtifact || !currentArtifact.categories || currentArtifact.categories.length === 0) {
      return [];
    }
    const firstSeries = currentArtifact.series?.[0];
    if (!firstSeries) return [];

    return currentArtifact.categories.map((cat, idx) => {
      const val = firstSeries.values?.[idx];
      return {
        name: cat,
        value: val !== undefined && val !== null && !isNaN(Number(val)) ? Number(val) : 0,
        color: PALETTE[idx % PALETTE.length],
      };
    });
  }, [currentArtifact]);

  if (!currentArtifact) {
    return (
      <div
        ref={chartContainerRef}
        className="h-[380px] w-full bg-[#0f172a] rounded-2xl p-4 border border-slate-800 flex items-center justify-center relative overflow-hidden"
      >
        <p className="text-xs text-slate-500">Select an artifact to preview its reconstruction.</p>
      </div>
    );
  }

  // ── Diagram artifact: render image or "not chart-representable" state ──
  if (isDiagramArtifact(currentArtifact) && renderMode !== "original" && renderMode !== "table") {
    return (
      <div
        ref={chartContainerRef}
        className="h-[380px] w-full bg-[#0f172a] rounded-2xl p-4 border border-slate-800 flex items-center justify-center relative overflow-hidden"
      >
        {currentArtifact.original_image_base64 ? (
          <div className="w-full h-full flex flex-col items-center justify-center gap-3 p-4">
            <img
              src={`data:image/png;base64,${currentArtifact.original_image_base64}`}
              alt={currentArtifact.title || "Diagram"}
              className="max-h-[280px] max-w-full object-contain rounded-lg shadow-lg"
            />
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">
                Diagram Artifact
              </span>
              <span className="text-[10px] text-slate-500">
                No numeric series to chart — showing original diagram
              </span>
            </div>
          </div>
        ) : currentArtifact.original_image_path ? (
          <div className="w-full h-full flex flex-col items-center justify-center gap-3 p-4">
            <img
              src={`http://localhost:5000${currentArtifact.original_image_path}`}
              alt={currentArtifact.title || "Diagram"}
              className="max-h-[280px] max-w-full object-contain rounded-lg shadow-lg"
            />
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">
                Diagram Artifact
              </span>
              <span className="text-[10px] text-slate-500">
                No numeric series to chart — showing original diagram
              </span>
            </div>
          </div>
        ) : (
          <div className="text-center space-y-3">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
              <svg className="w-8 h-8 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-white">{currentArtifact.title || "Diagram Artifact"}</p>
              <p className="text-xs text-slate-400 mt-1">
                This is a diagram/flow artifact — no numeric chart series to render.
              </p>
              <p className="text-[10px] text-slate-500 mt-0.5">
                Switch to "Original" mode to view the extracted diagram.
              </p>
            </div>
          </div>
        )}
      </div>
    );
  }

  // ── No chart data state (for artifacts with empty data) ──
  if (hasNoChartData(currentArtifact) && renderMode !== "original" && renderMode !== "table") {
    return (
      <div
        ref={chartContainerRef}
        className="h-[380px] w-full bg-[#0f172a] rounded-2xl p-4 border border-slate-800 flex items-center justify-center relative overflow-hidden"
      >
        <div className="text-center space-y-3">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center">
            <svg className="w-7 h-7 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-white">{currentArtifact.title || "Artifact"}</p>
            <p className="text-xs text-slate-400 mt-1">
              No numeric data extracted for this artifact.
            </p>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Try "Original" mode to view the source image, or re-extract with different settings.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={chartContainerRef}
      className="h-[380px] w-full bg-[#0f172a] rounded-2xl p-4 border border-slate-800 flex items-center justify-center relative overflow-hidden"
    >
      {renderMode === "original" ? (
        <div className="w-full h-full flex items-center justify-center p-4">
          {currentArtifact.original_image_base64 ? (
            <img
              src={`data:image/png;base64,${currentArtifact.original_image_base64}`}
              alt="Original View"
              className="max-h-full max-w-full object-contain rounded-lg shadow-lg"
            />
          ) : currentArtifact.original_image_path ? (
            <img
              src={`http://localhost:5000${currentArtifact.original_image_path}`}
              alt="Original View"
              className="max-h-full max-w-full object-contain rounded-lg shadow-lg"
            />
          ) : (
            <p className="text-xs text-slate-500">No original image reference available.</p>
          )}
        </div>
      ) : renderMode === "table" ? (
        <div className="w-full h-full overflow-auto text-xs">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/60">
                <th className="p-2.5 font-bold text-slate-300">Category / Label</th>
                {(currentArtifact.series || []).map((s, idx) => (
                  <th key={`tbl-th-${idx}`} className="p-2.5 font-bold text-indigo-300 text-right">
                    {s.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(currentArtifact.categories || []).map((cat, catIdx) => (
                <tr key={`tbl-row-${catIdx}`} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="p-2.5 font-medium text-slate-200">{cat}</td>
                  {(currentArtifact.series || []).map((s, sIdx) => {
                    const rawVal = s.values?.[catIdx];
                    const formatted = rawVal !== undefined && rawVal !== null && !isNaN(Number(rawVal))
                      ? Number(rawVal).toFixed(2)
                      : "0.00";
                    return (
                      <td key={`tbl-val-${sIdx}-${catIdx}`} className="p-2.5 text-right font-mono text-slate-300">
                        {formatted}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : renderMode === "line" ? (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={commonData} margin={{ top: 15, right: 30, left: 10, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0b0f1a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
            {(currentArtifact.series || []).map((s, idx) => (
              <Line
                key={s.name || `series-${idx}`}
                type="monotone"
                dataKey={s.name}
                stroke={PALETTE[idx % PALETTE.length]}
                strokeWidth={2.5}
                dot={{ r: 4, fill: PALETTE[idx % PALETTE.length] }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      ) : renderMode === "area" ? (
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={commonData} margin={{ top: 15, right: 30, left: 10, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0b0f1a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
            {(currentArtifact.series || []).map((s, idx) => (
              <Area
                key={s.name || `series-${idx}`}
                type="monotone"
                dataKey={s.name}
                stroke={PALETTE[idx % PALETTE.length]}
                fill={PALETTE[idx % PALETTE.length]}
                fillOpacity={0.25}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      ) : renderMode === "pie" ? (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              contentStyle={{ backgroundColor: "#0b0f1a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
            />
            <Legend wrapperStyle={{ fontSize: "12px" }} />
            <Pie
              data={pieData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
              labelLine={{ stroke: "#64748b" }}
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      ) : renderMode === "donut" ? (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              contentStyle={{ backgroundColor: "#0b0f1a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
            />
            <Legend wrapperStyle={{ fontSize: "12px" }} />
            <Pie
              data={pieData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={105}
              paddingAngle={3}
              label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
              labelLine={{ stroke: "#64748b" }}
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-donut-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      ) : renderMode === "radar" ? (
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={commonData} margin={{ top: 10, right: 30, left: 30, bottom: 10 }}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="name" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <PolarRadiusAxis stroke="#475569" tick={{ fill: "#64748b", fontSize: 10 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0b0f1a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
            />
            <Legend wrapperStyle={{ fontSize: "12px" }} />
            {(currentArtifact.series || []).map((s, idx) => (
              <RechartsRadar
                key={s.name || `series-${idx}`}
                name={s.name}
                dataKey={s.name}
                stroke={PALETTE[idx % PALETTE.length]}
                fill={PALETTE[idx % PALETTE.length]}
                fillOpacity={0.3}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      ) : renderMode === "stacked_bar" ? (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={commonData} margin={{ top: 15, right: 30, left: 10, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0b0f1a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
            {(currentArtifact.series || []).map((s, idx) => (
              <Bar
                key={s.name || `series-${idx}`}
                dataKey={s.name}
                stackId="stack"
                fill={PALETTE[idx % PALETTE.length]}
                radius={[0, 0, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      ) : (
        /* Default Standard Bar Chart */
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={commonData} margin={{ top: 15, right: 30, left: 10, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0b0f1a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
            {(currentArtifact.series || []).map((s, idx) => (
              <Bar
                key={s.name || `series-${idx}`}
                dataKey={s.name}
                fill={PALETTE[idx % PALETTE.length]}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
