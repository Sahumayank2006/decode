/* ============================================================
   DECODE — REAL EXTRACTION ADAPTER
   ------------------------------------------------------------
   Converts backend chart payloads into the canonical structure
   consumed by the demo workspace.

   Backend:
     chart.canonical_data.categories
     chart.canonical_data.series
     chart.canonical_data.metadata

   Frontend:
     CanonicalChart
   ============================================================ */

export type CanonicalSeries = {
  name: string;
  values: number[];
};

export type CanonicalChart = {
  id: string;
  title: string;
  chart_type: string;

  categories: string[];

  series: CanonicalSeries[];

  confidence: number;

  sourcePage?: number | null;

  metadata?: Record<string, unknown>;

  raw?: unknown;
};

export type BackendChart = {
  id?: unknown;
  chart_id?: unknown;

  title?: unknown;
  chart_type?: unknown;
  type?: unknown;
  detected_type?: unknown;

  categories?: unknown;
  labels?: unknown;
  x_values?: unknown;

  series?: unknown;

  canonical_data?: unknown;

  metadata?: unknown;

  confidence?: unknown;

  [key: string]: unknown;
};

/* ============================================================
   BASIC HELPERS
   ============================================================ */

function asRecord(value: unknown): Record<string, unknown> {
  if (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  ) {
    return value as Record<string, unknown>;
  }

  return {};
}

function safeString(
  value: unknown,
  fallback = ""
): string {
  if (
    typeof value === "string" &&
    value.trim().length > 0
  ) {
    return value.trim();
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  return fallback;
}

function safeNumber(
  value: unknown,
  fallback = 0
): number {
  if (typeof value === "number") {
    return Number.isFinite(value)
      ? value
      : fallback;
  }

  if (typeof value === "string") {
    const cleaned = value
      .replace(/,/g, "")
      .replace(/%$/, "")
      .trim();

    const parsed = Number(cleaned);

    return Number.isFinite(parsed)
      ? parsed
      : fallback;
  }

  return fallback;
}

/* ============================================================
   CHART TYPE NORMALIZATION
   ============================================================ */

export function normalizeChartType(
  value: unknown
): string {
  const normalized = String(
    value ?? "bar"
  )
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_")
    .replace(/-/g, "_");

  const aliases: Record<string, string> = {
    column: "bar",
    columns: "bar",
    histogram: "bar",

    spline: "line",
    trend: "line",

    stacked: "stacked_bar",
    stackedcolumn: "stacked_bar",

    area_chart: "area",

    doughnut: "donut",

    radar_chart: "radar",

    scatter_plot: "scatter",
  };

  return aliases[normalized] ?? normalized;
}

/* ============================================================
   VALUE NORMALIZATION
   ============================================================ */

function normalizeValue(
  value: unknown
): number {
  if (
    typeof value === "object" &&
    value !== null
  ) {
    const object = asRecord(value);

    return safeNumber(
      object.value ??
        object.y ??
        object.numeric_value ??
        object.amount ??
        object.data
    );
  }

  return safeNumber(value);
}

/* ============================================================
   SERIES NORMALIZATION
   ============================================================ */

function normalizeSeries(
  value: unknown
): CanonicalSeries[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((rawSeries, index) => {
      const series = asRecord(
        rawSeries
      );

      const name =
        safeString(
          series.name ??
            series.label ??
            series.title ??
            series.key,
          `Series ${index + 1}`
        );

      const rawValues =
        series.values ??
        series.data ??
        series.points ??
        series.y_values ??
        [];

      let values: number[] = [];

      if (Array.isArray(rawValues)) {
        values = rawValues.map(
          normalizeValue
        );
      }

      return {
        name,
        values,
      };
    })
    .filter(
      (series) =>
        series.values.length > 0
    );
}

/* ============================================================
   CATEGORY NORMALIZATION
   ============================================================ */

function normalizeCategories(
  value: unknown
): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map(
    (category, index) =>
      safeString(
        category,
        `Category ${index + 1}`
      )
  );
}

/* ============================================================
   BUILD DATA POINTS
   ============================================================ */

export function buildChartData(
  chart: CanonicalChart
): Array<{
  category: string;
  [key: string]: string | number;
}> {
  return chart.categories.map(
    (category, index) => {
      const row: {
        category: string;
        [key: string]: string | number;
      } = {
        category,
      };

      chart.series.forEach(
        (series) => {
          row[series.name] =
            series.values[index] ?? 0;
        }
      );

      return row;
    }
  );
}

/* ============================================================
   CONFIDENCE
   ============================================================ */

function normalizeConfidence(
  value: unknown
): number {
  const parsed = safeNumber(
    value,
    0
  );

  /*
   * Backend normally returns 0.987.
   * Also support 98.7.
   */

  if (parsed > 1) {
    return Math.min(
      1,
      parsed / 100
    );
  }

  return Math.max(
    0,
    Math.min(1, parsed)
  );
}

/* ============================================================
   MAIN ADAPTER
   ============================================================ */

export function normalizeBackendChart(
  input: unknown,
  fallbackId = "chart"
): CanonicalChart | null {
  if (!input) {
    return null;
  }

  const outer =
    asRecord(input);

  /*
   * IMPORTANT:
   * The real backend payload stores the useful data inside
   * canonical_data.
   */

  const canonicalCandidate =
    outer.canonical_data ??
    outer.canonicalData ??
    (outer.data as Record<string, unknown>)?.["canonical_data"];

  const canonical = asRecord(
    canonicalCandidate
  );

  /*
   * Support both:
   *
   * chart.canonical_data.categories
   *
   * and legacy:
   *
   * chart.categories
   */

  const source =
    Object.keys(canonical).length > 0
      ? canonical
      : outer;

  const categories =
    normalizeCategories(
      source.categories ??
        source.labels ??
        source.x_values
    );

  const series =
    normalizeSeries(
      source.series ??
        source.datasets
    );

  /*
   * Some extraction engines can return a single
   * data array instead of series[].
   */

  if (
    series.length === 0 &&
    Array.isArray(
      source.data
    )
  ) {
    const values =
      source.data.map(
        normalizeValue
      );

    if (values.length > 0) {
      series.push({
        name:
          safeString(
            source.series_name,
            "Value"
          ),
        values,
      });
    }
  }

  /*
   * Do not manufacture a fake chart.
   *
   * If the backend really returned no categories
   * and no series, report null.
   */

  if (
    categories.length === 0 ||
    series.length === 0
  ) {
    return null;
  }

  /*
   * Align all series to the number of categories.
   *
   * Missing values become 0.
   */

  const alignedSeries =
    series.map(
      (item) => ({
        ...item,
        values:
          categories.map(
            (_, index) =>
              item.values[
                index
              ] ?? 0
          ),
      })
    );

  const metadata =
    asRecord(
      canonical.metadata ??
        outer.metadata
    );

  const confidence =
    normalizeConfidence(
      canonical.confidence ??
        outer.confidence ??
        metadata.confidence
    );

  const id =
    safeString(
      outer.id ??
        outer.chart_id ??
        outer.chartId,
      fallbackId
    );

  const title =
    safeString(
      canonical.title ??
        outer.title,
      `Extracted Chart`
    );

  const chartType =
    normalizeChartType(
      canonical.detected_type ??
        canonical.chart_type ??
        outer.chart_type ??
        outer.type ??
        outer.detected_type
    );

  const sourcePage =
    safeNumber(
      metadata.page ??
        metadata.page_number ??
        metadata.source_page,
      0
    );

  return {
    id,
    title,
    chart_type: chartType,
    categories,
    series: alignedSeries,
    confidence,
    sourcePage:
      sourcePage > 0
        ? sourcePage
        : null,
    metadata,
    raw: input,
  };
}

/* ============================================================
   EXTRACT CHART ARRAY FROM ANY API RESPONSE
   ============================================================ */

export function extractBackendCharts(
  payload: unknown
): BackendChart[] {
  if (Array.isArray(payload)) {
    return payload as BackendChart[];
  }

  const root =
    asRecord(payload);

  const candidates = [
    root.charts,
    root.data &&
      asRecord(root.data)
        .charts,
    root.results,
    root.artifacts,
  ];

  for (const candidate of candidates) {
    if (Array.isArray(candidate)) {
      return candidate as BackendChart[];
    }
  }

  /*
   * Sometimes the API returns a single chart.
   */

  if (
    root.canonical_data ||
    root.categories ||
    root.series
  ) {
    return [
      root as BackendChart,
    ];
  }

  return [];
}

/* ============================================================
   NORMALIZE ALL CHARTS
   ============================================================ */

export function normalizeBackendCharts(
  payload: unknown
): CanonicalChart[] {
  const rawCharts =
    extractBackendCharts(
      payload
    );

  return rawCharts
    .map(
      (chart, index) =>
        normalizeBackendChart(
          chart,
          `chart-${index + 1}`
        )
    )
    .filter(
      (
        chart
      ): chart is CanonicalChart =>
        chart !== null
    );
}

/* ============================================================
   SUMMARY
   ============================================================ */

export function getChartSummary(
  charts: CanonicalChart[]
) {
  const categories =
    charts.reduce(
      (sum, chart) =>
        sum +
        chart.categories.length,
      0
    );

  const dataPoints =
    charts.reduce(
      (sum, chart) =>
        sum +
        chart.categories.length *
          chart.series.length,
      0
    );

  const confidenceValues =
    charts
      .map(
        (chart) =>
          chart.confidence
      )
      .filter(
        (value) =>
          value > 0
      );

  const confidence =
    confidenceValues.length > 0
      ? confidenceValues.reduce(
          (sum, value) =>
            sum + value,
          0
        ) /
        confidenceValues.length
      : 0;

  return {
    charts: charts.length,
    categories,
    dataPoints,
    confidence,
  };
}
