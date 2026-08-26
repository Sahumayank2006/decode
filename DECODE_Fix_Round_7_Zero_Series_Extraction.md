# DECODE — Fix Round 7: Extraction Returns "0 Series" / Blank Reconstruction / Compliance Stuck

Continuation of `DECODE_Master_Reference.md` (Parts A–C) and
`DECODE_Part_D_Reconstruction_Interconversion_Prompt.md`. Paste the section
below into your coding tool as-is — it now has a Gemini key in `.env`, so
part of this fix is also confirming that key is actually being used.

---

## Evidence (from the live screenshot)

- **Left panel ("Original Chart")**: a clean, correctly rendered bar chart —
  4 x-axis groups (Baseline, Enhanced, Hybrid, DECODE), 3 series (Dataset A/B/C),
  y-axis "Accuracy (%)" 0–100, title "Figure 1. Model Performance Across
  Experimental Conditions." This is ground truth — the source PDF chart is
  clean and fully OCR-able.
- **Right panel ("Chart Workspace")**: the chart-type toolbar (Bar / Stacked
  Bar / Line / Area / Pie / Donut / Scatter / Radar / Table) renders fine and
  "Area" is selected — but the plot area is **completely blank**, no axes, no
  data, no error message.
- **Extracted Data panel**:
  - `Title`: correct — "Figure 1. Model Performance Across Experimental Conditions"
  - `Series`: **"0 found"** — should be 3 (Dataset A, Dataset B, Dataset C)
  - `X-Axis`: **"Dataset B"** — wrong; that's a legend entry, not the real
    x-axis label ("Method")
  - `Y-Axis`: **blank** — should be "Accuracy (%)"
  - `Confidence`: **"0%"**
- **Copyright Compliance panel**: stuck on "Compliance data not yet
  available" with a visible "Re-score" button that presumably does nothing
  useful yet.

This is the same *category* of bug as Fix Round 3/4 (real detection, wrong
downstream mapping/plumbing) — the title extracted perfectly, which proves
OCR on this region is working. The failure is specifically in how axis
labels vs. legend labels vs. series get assigned, and in how (or whether)
that empty result propagates into reconstruction and compliance.

---

## PROMPT TO GIVE THE CODING TOOL

```
Fix the chart currently showing "Series: 0 found", X-Axis "Dataset B", blank
Y-Axis, and 0% confidence in the Extracted Data panel — this is the exact
chart visible in Chart Workspace for "Figure 1. Model Performance Across
Experimental Conditions" (4 x-groups: Baseline/Enhanced/Hybrid/DECODE; 3
series: Dataset A/B/C; y-axis "Accuracy (%)"). Since the title extracted
correctly, OCR on this region is NOT broken — the bug is in how OCR'd text
gets classified into title vs. x-axis label vs. y-axis label vs. legend vs.
series, and in how an empty extraction result is (or isn't) handled
downstream. Work through this in order:

STEP 1 — Confirm a Gemini key is actually being used now
A GEMINI_API_KEY has just been added to .env. Before touching extraction
logic:
- Log, for this exact chart's extraction call, which path executed:
  real Gemini call or rule-based fallback. Do this via the existing
  isLLMAvailable() helper from Part B — add a one-line log
  `[extraction] path=llm` or `[extraction] path=fallback` at the top of
  extractChartData().
- If it logs `path=fallback` despite the key being present: isLLMAvailable()
  is not reading the env var correctly, or the server was not restarted
  after the key was added, or the key is present but the extraction
  function was never wired to check it in the first place (it may have
  been built fallback-only during earlier rounds and never revisited).
  Fix so the real Gemini call is used, then re-test this exact chart.
- If it logs `path=llm`: the bug is in the Gemini prompt/response parsing,
  not availability — go to Step 2 with that in mind, and log the RAW
  Gemini response text for this chart so you can see exactly what came
  back vs. what got mapped.

STEP 2 — Find where "0 series" actually happens
- Add a log immediately after OCR/text-region extraction for this chart,
  before any classification into title/axis/legend/series, printing the
  full raw OCR'd text list with each fragment's bounding-box position.
  Confirm "Dataset A", "Dataset B", "Dataset C", "Baseline", "Enhanced",
  "Hybrid", "DECODE", and "Accuracy (%)" are ALL present in that raw list
  (title already proves OCR works on this region, so they almost certainly
  are — this step is to rule that out definitively, not to re-fix OCR).
- If they're all present in the raw OCR output but `series` still comes
  back empty: the bug is in the classification/mapping step that decides
  "this fragment is a legend entry -> becomes a series" vs. "this fragment
  is an x-axis tick -> becomes a category." Find that function and check:
  does it require a color swatch adjacent to text to count something as a
  legend/series entry? If the swatch-detection (small colored square next
  to "Dataset A" etc.) is failing or missing, that's why series comes back
  empty even though the text itself was read correctly. Fix swatch
  detection (color-block contour near text, same OpenCV contour approach
  used in Fix Round 5) and re-derive series from swatch+label pairs.

STEP 3 — Fix the X-Axis / legend confusion directly
"Dataset B" ending up in the `X-Axis` field is a strong, specific clue: the
mapping code is taking the SECOND (or some fixed index) OCR'd label it finds
below the plot area and calling it the x-axis label, without checking
whether that label sits directly under the axis line (a real x-axis label
like "Method") versus inside the legend block (like "Dataset B"). Fix the
x-axis-label detection to require: text positioned directly below/adjacent
to the horizontal axis line itself (use the same axis-line detection from
Fix Round 6's has_numeric_axis reference), not just "some text found in the
lower half of the region." Legend entries (text next to a color swatch,
typically below or beside the plot, not touching the axis line) must never
be eligible to become the x-axis label candidate.

STEP 4 — Real confidence, not a stuck 0%
0% confidence on a chart whose title extracted correctly and whose image
crop is clearly clean is itself evidence the confidence field is either
(a) computed from series.length (so it's mechanically 0 because series is
empty — expected once Steps 1-3 are fixed, verify it updates), or (b) never
actually set for this code path and silently defaulting to 0. Log which of
these it is. After Steps 1-3 are fixed, confidence must reflect a real
computed value (e.g. weighted average of per-field OCR/classification
confidence), never hardcoded.

STEP 5 — Reconstruction must not render a silently blank chart
Right now the Chart Workspace toolbar renders normally and the plot area is
just empty — this looks like a bug rather than a clear signal, and it will
confuse your judge. Add an explicit empty/needs-review state to the
ChartRenderer component: if the canonical chart's series array is empty OR
its data array is empty, render a clear message ("No usable series data was
extracted for this chart") with a "Re-extract" action, instead of an axis-
less blank canvas. Reference implementation for this exact guard clause is
in UniversalChartWorkspace.tsx (already updated) — port the same check into
the real ChartRenderer in this codebase. This must never be reached once
Steps 1-4 are fixed for THIS chart, but it must exist for any future chart
where extraction genuinely fails, per the "no dummy data, honest empty
states" rule from Part A Section 6.

STEP 6 — Compliance panel must not hang forever
"Compliance data not yet available" with a live "Re-score" button that does
nothing is the same class of problem as Step 5: confirm scoreCompliance()
is either (a) never being called because it's gated on series.length > 0
(expected, and fine, AS LONG AS fixing extraction makes it fire
automatically once real data exists — verify this happens without a manual
click), or (b) being called but failing silently (add real error logging
and surface the error, don't just leave the panel in "not yet available"
forever). Clicking "Re-score" manually must always either produce a real
score or a real visible error — never a silent no-op.

STEP 7 — Verify end-to-end on this exact chart
- Series: 3 found (Dataset A, Dataset B, Dataset C), each with the correct
  color.
- X-Axis: "Method". Y-Axis: "Accuracy (%)".
- Confidence: a real non-zero number reflecting actual extraction quality
  on this clean, well-formed chart (should be high, e.g. 85%+, given how
  clean the source image is).
- Chart Workspace right panel renders real bars matching the left panel's
  values for Baseline/Enhanced/Hybrid/DECODE across all 3 datasets.
- Switch through every type in the toolbar (Bar, Stacked Bar, Line, Area,
  Pie, Donut, Scatter — should be enabled since there are 3 series, Radar —
  should be enabled since there are 4 categories, Table) and confirm every
  one shows the SAME 12 numbers (4 categories x 3 series) reshaped, never
  blank.
- Compliance panel shows a real score and risk band without needing a
  manual click, and "Re-score" also works on demand.
- Re-run this same check on 2-3 OTHER charts already in the system to
  confirm this wasn't a one-chart fluke and didn't regress anything that
  was previously working.
```

---

## Why this is almost certainly an extraction-mapping bug, not a chart bug

The right-panel toolbar, type highlighting, and export buttons are all
rendering correctly — that part of the reconstruction/interconversion
module built in Part D is doing exactly what it should with whatever data
it's given. The problem is one level upstream: it's being given an empty
`series` array, so there's nothing to reshape into any chart type. Confirm
this yourself in one query before handing anything to the coding tool if
you want: check the stored extraction record for this chart directly (DB or
local storage per Part C's Fix Round 1/2 pattern) — if `series` is `[]`
there too, it confirms the bug is in extraction, not in rendering.
