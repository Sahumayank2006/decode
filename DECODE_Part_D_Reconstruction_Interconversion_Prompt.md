# DECODE — Part D: Universal Chart Reconstruction & Interconversion Module

This is a direct continuation of `DECODE_Master_Reference.md` (Parts A–C).
Paste the section below labeled **"PROMPT TO GIVE THE CODING TOOL"** into
your coding assistant (Claude Code, Cursor, etc.) as-is. It assumes Stages 1–3
(Ingestion, Detection, Extraction) already output real `series` / `axis_labels`
/ `legend` data per chart, as described in Part A Section 4.

---

## Why this part exists

Right now each chart likely has ONE reconstructed view (whatever type was
classified). For the judge-facing demo, the requirement is: **any chart can
become any other visual representation of the same underlying data, live, with
zero data loss** — bar ↔ line ↔ area ↔ pie ↔ scatter ↔ table, in any
direction, as many times as the user clicks. This is the single most
"wow"-able feature in the product because it visibly proves the extraction
was real (fake/mock data can't survive being reshaped five different ways).

---

## PROMPT TO GIVE THE CODING TOOL

```
Build the Universal Chart Reconstruction & Interconversion module for DECODE.

CORE PRINCIPLE — ONE CANONICAL DATA MODEL, MANY VIEWS
Every chart, regardless of its detected or current display type, must be
stored and edited as ONE canonical data shape. Every visual representation
(bar, line, area, pie, scatter, table) is a pure render function OF that
canonical shape — never a separate copy of the data. Switching chart type
must NEVER touch, transform-in-place, or lossily reduce the underlying data.
Only the renderer changes.

Canonical shape (TypeScript):

  interface ChartSeries {
    id: string;
    name: string;          // legend label
    color?: string;
  }

  interface ChartDataPoint {
    id: string;
    category: string;      // x-axis / row label (e.g. "Q1", "2021", "Group A")
    values: Record<string, number | null>; // seriesId -> value, null = unreadable (never fabricated)
  }

  interface CanonicalChart {
    id: string;
    title: string;
    sourceType: string;        // originally-detected type, kept for the compliance module
    activeType: ChartRenderType; // currently displayed as
    xAxisLabel?: string;
    yAxisLabel?: string;
    series: ChartSeries[];
    data: ChartDataPoint[];
    confidence: number;        // from extraction stage, never hardcoded
    editHistory: { timestamp: string; field: string; oldValue: any; newValue: any }[];
  }

  type ChartRenderType =
    | "bar" | "stacked_bar" | "line" | "area" | "pie" | "donut"
    | "scatter" | "radar" | "table";

REQUIREMENTS

1. Reconstruction stage output contract
   `reconstructChart(extraction, chartType)` must build exactly ONE
   `CanonicalChart` object from `extraction.series` / `extraction.axis_labels`
   / `extraction.legend`. Do not branch into type-specific data shapes here —
   the canonical shape is type-agnostic by design. `activeType` starts as
   whatever `chartType` was classified, but nothing else about the object is
   type-specific.

2. Universal renderer
   Build ONE component, `<ChartRenderer chart={canonicalChart} />`, that
   switches on `chart.activeType` and maps the SAME `chart.series` /
   `chart.data` into the Recharts component for that type:
   - bar / stacked_bar → <BarChart>
   - line → <LineChart>
   - area → <AreaChart>
   - pie / donut → <PieChart> (auto-collapses to the FIRST numeric series
     only if there are multiple series; show a small non-blocking notice
     "Pie shows [series name] only — switch to bar/line to compare all
     series" rather than silently dropping data)
   - scatter → <ScatterChart> (requires >=2 numeric series; if only 1 series
     exists, disable this option in the switcher with a tooltip explaining
     why, don't let the user land on a broken empty chart)
   - radar → <RadarChart>
   - table → an editable HTML table (see requirement 4)
   No chart type is allowed its own parallel data array. If you catch
   yourself writing `barData`, `lineData`, `pieData` as separate variables,
   stop — derive all of them from `chart.data` at render time instead.

3. Chart type switcher
   A segmented control / icon toolbar above the chart with one button per
   ChartRenderType. Clicking a type:
   - Sets `chart.activeType` only. Does not mutate `chart.data` or
     `chart.series`.
   - Is instant (no reload, no server round-trip) — this is a pure client
     re-render.
   - Disables (not hides) any type that is structurally invalid for the
     current data (e.g. scatter with 1 series, radar with <3 categories),
     with a one-line tooltip explaining exactly why, computed from the real
     data shape — never a generic "not available" with no reason.

4. Editable table view (the interconversion anchor)
   The `table` view is not just another display — it is the canonical
   editor. Every cell (`category` and each series value) is directly
   editable inline. On edit:
   - Validate: numeric fields reject non-numeric input inline with a red
     outline and a specific message, never a silent revert.
   - Update `chart.data` in place (still the same canonical object).
   - Push an entry to `chart.editHistory` (field, old value, new value,
     timestamp) — this is real audit trail, not decorative.
   - If the user is currently viewing bar/line/pie/etc. and switches to
     table, edits, then switches back — the edited values must appear in
     the chart immediately. Write a test for this exact round-trip.
   - Support adding a new row (new category) and adding a new series
     (new column) from the table view, with the new series/point
     automatically available in every other chart type.

5. Compliance module contract (do not break Part A's scoring)
   The similarity/compliance score always compares the ORIGINAL detected
   image against the render of `chart.sourceType` (or the type the user
   currently has open, your choice — pick one and document it in a code
   comment), never against a type the data structurally can't support.
   Re-run compliance scoring on: (a) any manual data edit, (b) explicit
   "Rescore" click. Do NOT re-run it on every type switch — that would
   conflate "does this look like the original" with "did the user just
   look at it differently," which are different questions.

6. Export
   - PNG / SVG export must export whatever `activeType` is CURRENTLY
     rendered, not always the original type.
   - Table view exports as real CSV (and XLSX if the xlsx library is
     already in the stack) — export the literal current values, including
     any edits.
   - "Copy config" copies the full canonical `CanonicalChart` JSON, so it
     can be pasted into the LLM API prompt debugger or saved externally.

7. State management
   Use Zustand (already in the stack per Part A). One store,
   `useChartStore`, keyed by chart id, holding the canonical objects.
   `activeType` and `data` edits both go through the same store so undo/redo
   (basic, last-20-actions) works uniformly across "switched to pie" and
   "edited cell Q3=42."

8. Non-negotiables (same bar as Part A Section 6)
   - No dummy/mock data. If `extraction.series` came back with `null` for
     a value, the table shows a visibly empty/dashed cell — never a
     fabricated 0 or an invented interpolated number.
   - No console errors switching through every type on every sample chart
     in the test PDFs from Part C.
   - Loading state only on the FIRST render of a chart (data fetch);
     every subsequent type switch is synchronous and instant — do not add
     a spinner to a type switch, that is a client-side reshape of data
     already in memory.
   - Responsive: the type switcher wraps to a second row on narrow
     viewports rather than overflowing.

9. Verification checklist (append to Part A Section 7 Definition of Done)
   - [ ] Take one real extracted bar chart, switch it to line, area, pie,
         scatter (if valid), radar (if valid), and table — every view shows
         the SAME numbers, just reshaped.
   - [ ] Edit a value in table view, switch to bar, confirm the bar height
         changed and matches the new number exactly.
   - [ ] Add a new category row in table view, switch to line, confirm a
         new point appears on the x-axis in the right position.
   - [ ] Force a chart to pie with 2 series, confirm the "showing X only"
         notice appears and is accurate to whichever series was chosen.
   - [ ] Export PNG from bar view, switch to line, export PNG again, confirm
         the two files actually differ and both are real (non-blank) images.
   - [ ] Confirm editHistory has a real entry after every manual edit, with
         correct old/new values — not empty, not a placeholder string.

Implement this now. Reuse the existing Recharts setup, shadcn/ui components,
and Zustand store patterns already in the codebase from Part A — do not
introduce a second charting library or a second state management approach.
```

---

## Reference implementation (drop-in starting point)

A working single-file reference component implementing the canonical model,
the universal renderer, the type switcher, and the editable table is provided
alongside this document: **`UniversalChartWorkspace.tsx`**. It's intentionally
self-contained (one file) so you — or your coding tool — can read it end to
end, then split it into the project's real file structure
(`store/`, `components/chart-workspace/`, etc.) once it's wired to real
extraction data instead of the sample data at the bottom of the file.

It demonstrates:
- The `CanonicalChart` model exactly as specified above
- A Zustand store with `setActiveType`, `updateCell`, `addRow`, `addSeries`,
  `undo`
- One `<ChartRenderer>` switching over `bar / line / area / pie / scatter /
  radar / table`
- An inline-editable table that writes back into the same store the charts
  read from
- CSV export and "copy config" (JSON) export, wired up to real Blob/download
  logic — not stubs

Feed both files to your coding tool in the same message so it has the exact
contract, not just a description of it.
