/* ============================================================
 * DECODE - Canonical Chart Normalizer
 *
 * Converts all backend/legacy chart shapes into ONE safe shape.
 * This is intentionally defensive because the extraction
 * pipeline can return slightly different representations.
 * ============================================================ */

export type NormalizedSeries = {
  name: string;
  values: number[];
};

export type NormalizedChart = {
  id: string;
  title: string;
  chart_type: string;
  categories: string[];
  series: NormalizedSeries[];
  confidence: number | null;
  page_number?: number;
  original_image_path?: string;
  original_image_base64?: string;
  export_svg_path?: string;
  export_png_path?: string;
  compliance?: {
    overall_score?: number;
    risk_level?: string;
    ssim_score?: number;
    color_similarity?: number;
    layout_similarity?: number;
    flagged?: boolean;
    flags?: string[];
    recommendations?: string[];
  };
  metadata: Record<string, unknown>;
  source?: Record<string, unknown>;
};

function isRecord(value: unknown): value is Record<string, any> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const cleaned = value
      .replace(/₹/g, "")
      .replace(/[$€£,%]/g, "")
      .replace(/,/g, "")
      .trim();

    const parsed = Number(cleaned);

    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return 0;
}

function normalizeConfidence(value: unknown): number | null {
  const n = toNumber(value);

  if (!Number.isFinite(n)) {
    return null;
  }

  if (n > 1) {
    return Math.min(1, n / 100);
  }

  return n;
}

function normalizeCategories(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map((item, index) => {
    if (item === null || item === undefined) {
      return `Category ${index + 1}`;
    }

    if (isRecord(item)) {
      return String(
        item.label ??
          item.name ??
          item.category ??
          item.x ??
          item.key ??
          `Category ${index + 1}`
      );
    }

    return String(item);
  });
}

function normalizeSeries(
  seriesValue: unknown,
  categories: string[]
): NormalizedSeries[] {
  if (!Array.isArray(seriesValue)) {
    return [];
  }

  return seriesValue
    .map((rawSeries, seriesIndex) => {
      /*
       * Standard backend form:
       *
       * {
       *   name: "Revenue",
       *   values: [118, 136, 149, 151]
       * }
       */

      if (isRecord(rawSeries)) {
        const name = String(
          rawSeries.name ??
            rawSeries.label ??
            rawSeries.key ??
            `Series ${seriesIndex + 1}`
        );

        let values: number[] = [];

        if (Array.isArray(rawSeries.values)) {
          values = rawSeries.values.map(toNumber);
        } else if (Array.isArray(rawSeries.data)) {
          values = rawSeries.data.map((item: unknown) => {
            if (isRecord(item)) {
              return toNumber(
                item.value ??
                  item.y ??
                  item.amount ??
                  item.numeric_value
              );
            }

            return toNumber(item);
          });
        }

        /*
         * If values are stored as an object:
         *
         * {
         *   Q1: 118,
         *   Q2: 136
         * }
         */
        if (
          values.length === 0 &&
          isRecord(rawSeries.values)
        ) {
          values = categories.map((category) =>
            toNumber(rawSeries.values[category])
          );
        }

        /*
         * Keep array aligned with categories.
         */
        while (values.length < categories.length) {
          values.push(0);
        }

        if (values.length > categories.length) {
          values = values.slice(0, categories.length);
        }

        return {
          name,
          values,
        };
      }

      /*
       * Very old representation:
       *
       * series: [
       *   [118, 136, 149, 151]
       * ]
       */
      if (Array.isArray(rawSeries)) {
        return {
          name: `Series ${seriesIndex + 1}`,
          values: rawSeries.map(toNumber),
        };
      }

      return null;
    })
    .filter(
      (series): series is NormalizedSeries =>
        series !== null
    );
}

function extractRows(
  rows: unknown,
  categories: string[]
): NormalizedSeries[] {
  if (!Array.isArray(rows) || rows.length === 0) {
    return [];
  }

  const seriesNames = new Set<string>();

  for (const row of rows) {
    if (!isRecord(row)) continue;

    const values = isRecord(row.values)
      ? row.values
      : {};

    Object.keys(values).forEach((key) =>
      seriesNames.add(key)
    );
  }

  if (seriesNames.size === 0) {
    return [];
  }

  return Array.from(seriesNames).map((name) => ({
    name,
    values: categories.map((_, index) => {
      const row = rows[index];

      if (!isRecord(row)) {
        return 0;
      }

      if (!isRecord(row.values)) {
        return 0;
      }

      return toNumber(row.values[name]);
    }),
  }));
}

export function normalizeChart(
  input: unknown,
  fallbackId = "chart-1"
): NormalizedChart | null {
  if (!isRecord(input)) {
    return null;
  }

  /*
   * Backend:
   *
   * chart.canonical_data
   *
   * Legacy:
   *
   * chart.data
   *
   * Some responses may directly contain the canonical object.
   */

  const canonical =
    isRecord(input.canonical_data)
      ? input.canonical_data
      : isRecord(input.data)
        ? input.data
        : input;

  const id = String(
    input.id ??
      input.chart_id ??
      canonical.id ??
      fallbackId
  );

  const title = String(
    canonical.title ??
      input.title ??
      `Extracted Chart ${fallbackId.replace(
        "chart-",
        ""
      )}`
  );

  const chartType = String(
    canonical.detected_type ??
      canonical.chart_type ??
      input.chart_type ??
      input.type ??
      "bar"
  ).toLowerCase();

  /*
   * Categories can exist directly on canonical data.
   */
  let categories = normalizeCategories(
    canonical.categories ??
      canonical.labels ??
      canonical.x_axis ??
      canonical.x_labels
  );

  /*
   * Standard series representation.
   */
  let series = normalizeSeries(
    canonical.series ??
      canonical.datasets ??
      input.series ??
      input.datasets,
    categories
  );

  /*
   * Legacy row representation.
   */
  if (series.length === 0) {
    const rows =
      canonical.rows ??
      input.rows ??
      canonical.data_rows;

    if (Array.isArray(rows)) {
      if (categories.length === 0) {
        categories = rows.map((row, index) => {
          if (!isRecord(row)) {
            return `Category ${index + 1}`;
          }

          return String(
            row.category ??
              row.label ??
              row.name ??
              row.x ??
              `Category ${index + 1}`
          );
        });
      }

      series = extractRows(rows, categories);
    }
  }

  /*
   * Another common backend representation:
   *
   * data: [
   *   { category: "Q1", Revenue: 118, Profit: 42 },
   *   ...
   * ]
   */
  if (
    series.length === 0 &&
    Array.isArray(canonical.data)
  ) {
    const dataRows = canonical.data.filter(isRecord);

    if (dataRows.length > 0) {
      if (categories.length === 0) {
        categories = dataRows.map((row, index) =>
          String(
            row.category ??
              row.label ??
              row.name ??
              row.x ??
              `Category ${index + 1}`
          )
        );
      }

      const ignoredKeys = new Set([
        "category",
        "label",
        "name",
        "x",
      ]);

      const keys = new Set<string>();

      for (const row of dataRows) {
        Object.keys(row).forEach((key) => {
          if (!ignoredKeys.has(key)) {
            keys.add(key);
          }
        });
      }

      series = Array.from(keys).map((name) => ({
        name,
        values: dataRows.map((row) =>
          toNumber(row[name])
        ),
      }));
    }
  }

  /*
   * Final alignment.
   */
  if (categories.length > 0) {
    series = series.map((item) => {
      const values = [...item.values];

      while (values.length < categories.length) {
        values.push(0);
      }

      return {
        ...item,
        values: values.slice(0, categories.length),
      };
    });
  }

  /*
   * A chart without both categories and series is not usable.
   */
  if (
    categories.length === 0 &&
    series.length === 0
  ) {
    return {
      id,
      title,
      chart_type: chartType,
      categories: [],
      series: [],
      confidence: normalizeConfidence(
        canonical.metadata &&
          isRecord(canonical.metadata)
          ? canonical.metadata.confidence
          : input.confidence
      ),
      metadata: isRecord(canonical.metadata)
        ? canonical.metadata
        : {},
      source: input,
    };
  }

  const page_number = Number(input.page_number ?? (isRecord(canonical.metadata) ? canonical.metadata.page_number : 1) ?? 1);
  const original_image_path = String(input.original_image_path ?? "");
  const original_image_base64 = String(input.original_image_base64 ?? "");
  const export_svg_path = String(input.export_svg_path ?? "");
  const export_png_path = String(input.export_png_path ?? "");
  const compliance = isRecord(input.compliance) ? input.compliance : undefined;

  return {
    id,
    title,
    chart_type: chartType,
    categories,
    series,
    confidence: normalizeConfidence(
      canonical.metadata &&
        isRecord(canonical.metadata)
        ? canonical.metadata.confidence
        : canonical.confidence ??
            input.confidence
    ),
    page_number,
    original_image_path,
    original_image_base64,
    export_svg_path,
    export_png_path,
    compliance,
    metadata: isRecord(canonical.metadata)
      ? canonical.metadata
      : {},
    source: input,
  };
}

export function normalizeCharts(
  response: unknown
): NormalizedChart[] {
  if (Array.isArray(response)) {
    return response
      .map((item, index) => normalizeChart(item, `chart-${index + 1}`))
      .filter((chart): chart is NormalizedChart => chart !== null);
  }

  if (!isRecord(response)) {
    return [];
  }

  const rawCharts = Array.isArray(response.charts)
    ? response.charts
    : Array.isArray(response.data)
      ? response.data
      : [];

  return rawCharts
    .map((item, index) =>
      normalizeChart(item, `chart-${index + 1}`)
    )
    .filter(
      (chart): chart is NormalizedChart =>
        chart !== null
    );
}

export function toRechartsData(
  chart: NormalizedChart | null | undefined
): Array<Record<string, unknown>> {
  if (!chart) {
    return [];
  }

  const categories = Array.isArray(chart.categories)
    ? chart.categories
    : [];

  const series = Array.isArray(chart.series)
    ? chart.series
    : [];

  return categories.map(
    (category, categoryIndex) => {
      const row: Record<string, unknown> = {
        category,
      };

      for (const item of series) {
        if (!item) continue;

        const name =
          typeof item.name === "string" &&
          item.name.trim()
            ? item.name
            : "Series";

        const value = Array.isArray(item.values)
          ? item.values[categoryIndex]
          : 0;

        row[name] =
          typeof value === "number"
            ? value
            : Number(value) || 0;
      }

      return row;
    }
  );
}
