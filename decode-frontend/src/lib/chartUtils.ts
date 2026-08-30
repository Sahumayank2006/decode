import type {
  CanonicalChart,
  ChartRenderType,
  ChartDataPoint,
  ChartSeries,
} from "@/store/useChartStore";

/* ============================================================
   VALID CHART TYPES
   ============================================================ */

export function getValidChartTypes(
  chart?: CanonicalChart | null
): ChartRenderType[] {
  const all: ChartRenderType[] = [
    "bar",
    "line",
    "area",
    "scatter",
    "pie",
    "donut",
    "stacked_bar",
    "radar",
    "table",
  ];

  if (!chart) {
    return all;
  }

  return all;
}

/* ============================================================
   NORMALIZE CHART
   ============================================================ */

export function normalizeChart(
  input: unknown
): CanonicalChart {
  const raw = (input ?? {}) as Record<string, unknown>;

  const categories = Array.isArray(raw.categories)
    ? raw.categories.map(String)
    : [];

  const rawSeries = Array.isArray(raw.series)
    ? raw.series
    : [];

  const series: ChartSeries[] =
    rawSeries.map((item, index) => {
      const s =
        (item ?? {}) as Record<string, unknown>;

      const values = Array.isArray(s.values)
        ? s.values.map((v) => Number(v ?? 0))
        : [];

      return {
        id:
          String(
            s.id ??
            `series_${index + 1}`
          ),

        name:
          String(
            s.name ??
            `Series ${index + 1}`
          ),

        values,
      };
    });

  let data: ChartDataPoint[] = [];

  if (Array.isArray(raw.data)) {
    data = raw.data.map((item, index) => {
      const row =
        (item ?? {}) as Record<string, unknown>;

      const result: ChartDataPoint = {
        category:
          String(
            row.category ??
            categories[index] ??
            `Category ${index + 1}`
          ),
      };

      for (const s of series) {
        result[s.id] =
          Number(row[s.id] ?? 0);
      }

      return result;
    });
  } else {
    data = categories.map(
      (category, index) => {
        const row: ChartDataPoint = {
          category,
        };

        for (const s of series) {
          row[s.id] =
            Number(
              s.values?.[index] ?? 0
            );
        }

        return row;
      }
    );
  }

  const chartType =
    String(
      raw.chart_type ??
      raw.activeType ??
      "bar"
    ) as ChartRenderType;

  return {
    id:
      String(
        raw.id ??
        `chart_${Date.now()}`
      ),

    title:
      String(
        raw.title ??
        "Untitled Chart"
      ),

    sourceType:
      String(
        raw.sourceType ??
        "pdf"
      ),

    activeType: chartType,

    chart_type: chartType,

    xAxisLabel:
      raw.xAxisLabel
        ? String(raw.xAxisLabel)
        : undefined,

    yAxisLabel:
      raw.yAxisLabel
        ? String(raw.yAxisLabel)
        : undefined,

    categories,

    series,

    data,

    confidence:
      typeof raw.confidence === "number"
        ? raw.confidence
        : undefined,

    editHistory:
      Array.isArray(raw.editHistory)
        ? raw.editHistory as CanonicalChart["editHistory"]
        : [],

    metadata:
      typeof raw.metadata === "object" &&
      raw.metadata !== null
        ? raw.metadata as Record<string, unknown>
        : undefined,
  };
}

/* ============================================================
   RECONSTRUCT CHART
   ============================================================ */

export function reconstructChart(
  input: unknown
): CanonicalChart {
  return normalizeChart(input);
}

/* ============================================================
   CSV EXPORT
   ============================================================ */

export function exportToCSV(
  chart: CanonicalChart
): string {
  const normalized =
    normalizeChart(chart);

  const headers = [
    "Category",
    ...normalized.series.map(
      (series) => series.name
    ),
  ];

  const rows = normalized.data.map(
    (row) => [
      String(row.category ?? ""),
      ...normalized.series.map(
        (series) =>
          String(
            row[series.id] ?? ""
          )
      ),
    ]
  );

  return [
    headers,
    ...rows,
  ]
    .map((row) =>
      row
        .map((value) => {
          const escaped =
            value.replace(
              /"/g,
              '""'
            );

          return `"${escaped}"`;
        })
        .join(",")
    )
    .join("\n");
}

/* ============================================================
   DOWNLOAD CSV
   ============================================================ */

export function downloadCSV(
  chart: CanonicalChart
): void {
  const csv =
    exportToCSV(chart);

  const blob =
    new Blob(
      [csv],
      {
        type:
          "text/csv;charset=utf-8;",
      }
    );

  const url =
    URL.createObjectURL(blob);

  const anchor =
    document.createElement("a");

  anchor.href = url;

  anchor.download =
    `${chart.title || "decode-chart"}.csv`;

  document.body.appendChild(anchor);

  anchor.click();

  document.body.removeChild(anchor);

  URL.revokeObjectURL(url);
}

/* ============================================================
   COPY CONFIG
   ============================================================ */

export async function copyChartConfig(
  chart: CanonicalChart
): Promise<void> {
  const normalized =
    normalizeChart(chart);

  const payload =
    JSON.stringify(
      normalized,
      null,
      2
    );

  await navigator.clipboard.writeText(
    payload
  );
}

/* ============================================================
   NUMBER FORMATTER
   ============================================================ */

export function formatChartValue(
  value: unknown
): string {
  const numeric =
    Number(value);

  if (!Number.isFinite(numeric)) {
    return String(value ?? "");
  }

  return new Intl.NumberFormat(
    "en-US",
    {
      maximumFractionDigits: 2,
    }
  ).format(numeric);
}
