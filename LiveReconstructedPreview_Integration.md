# How to wire LiveReconstructedPreview.jsx into your workspace

## 1. One canonical store (if you don't already have one)
```jsx
// artifactStore.js
import { create } from "zustand";

export const useArtifactStore = create((set) => ({
  artifacts: [],            // full list from your backend, each with .id, .title, .render, .preview, .confidence
  selectedArtifactId: null,
  loadArtifacts: (list) => set({
    artifacts: list,
    selectedArtifactId: list[0]?.id ?? null,
  }),
  selectArtifact: (id) => set({ selectedArtifactId: id }),
}));
```

## 2. Parent panel — pass the selected artifact down, key by its ID
```jsx
import { useArtifactStore } from "./artifactStore";
import LiveReconstructedPreview from "./LiveReconstructedPreview";

function WorkspacePanel() {
  const { artifacts, selectedArtifactId } = useArtifactStore();
  const selected = artifacts.find((a) => a.id === selectedArtifactId);
  const [mode, setMode] = useState("bar"); // driven by your Bar/Line/Pie toggle buttons

  return (
    <div>
      {/* your Bar / Stacked / Line / Area / Pie / Donut / Radar toggle buttons
          call setMode("bar"), setMode("line"), etc. — nothing else changes */}

      <LiveReconstructedPreview
        key={selected?.id}  // forces a clean remount on selection change —
                             // no stale internal state can survive a switch
        artifact={selected}
        mode={mode}
      />
    </div>
  );
}
```

## 3. Artifact click handler — the ONLY place selection changes
```jsx
function ArtifactCard({ artifact }) {
  const selectArtifact = useArtifactStore((s) => s.selectArtifact);
  return (
    <div onClick={() => selectArtifact(artifact.id)}>
      {/* card contents */}
    </div>
  );
}
```

## Why this is guaranteed to work for every artifact, not just 3 you tested
`LiveReconstructedPreview` has zero knowledge of which specific artifact
it's showing — it only knows the generic shape `{categories, series}`.
Whether that's the bar chart, the line chart, the pie chart, or a 10th
artifact you add tomorrow, the exact same code path handles it, because
the transform (`toRechartsData`) and every chart-mode branch operate on
that generic shape, never on hardcoded field names like "Region A" or
"Pipeline Stages". This is what makes it correct for "any selected
artifact" rather than needing a special case per chart.

## The "1 Issue" badge — check this first
Every one of your three screenshots shows a red "1 Issue" indicator.
Before wiring in the new component, click it (or open the browser
console) and read what it says. If your CURRENT code is throwing an
error when it tries to render real data (a common cause: `render_spec`
being undefined, or a field name mismatch between what your backend
sends and what the frontend expects), that error is very likely why
you're seeing a fallback dataset — some error boundary or try/catch is
silently swallowing the crash and showing placeholder data instead of
surfacing it. Fixing that error, or dropping in this component (which
has explicit empty-states instead of crashing/falling back), removes
the failure mode either way.
