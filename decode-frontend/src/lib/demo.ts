/* eslint-disable */
// @ts-nocheck
/* eslint-disable */
// @ts-nocheck
import type {
  ProcessingEvent,
  ProcessingStatus,
} from "@/lib/api";

import type {
  ChartSeries,
  ChartDataPoint,
  ChartRenderType,
  CanonicalChart,
} from "@/store/useChartStore";

/* eslint-disable */
// @ts-nocheck
import {
  normalizeChart,
} from "@/lib/chartUtils";

/* ============================================================
   DEMO NORMALIZATION HELPERS
   ============================================================ */

export function safeString(
  value: unknown,
  fallback = ""
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return fallback;
  }

  return String(value);
}

export function safeNumber(
  value: unknown,
  fallback = 0
): number {
  const number =
    typeof value === "number"
      ? value
      : Number(value);

  return Number.isFinite(number)
    ? number
    : fallback;
}

export function clamp(
  value: number,
  minimum: number,
  maximum: number
): number {
  return Math.min(
    maximum,
    Math.max(minimum, value)
  );
}

/* ============================================================
   CHART HELPERS
   ============================================================ */

export function chartId(
  chart: ChartRecord
): string {
  return safeString(
    chart.id ||
      chart.chart_id
  );
}

export function chartTitle(
  chart: ChartRecord,
  index = 0
): string {
  return (
    safeString(
      chart.title
    ).trim() ||
    `Detected ${String(
      index + 1
    ).padStart(2, "0")}`
  );
}

export function chartType(
  chart: ChartRecord
): string {
  return safeString(
    chart.chart_type ||
      chart.type ||
      "bar"
  ).toLowerCase();
}

export function chartIsTable(
  chart: ChartRecord
): boolean {
  return (
    chartType(chart) === "table"
  );
}

export function getChartSeries(
  chart: ChartRecord
): ChartSeries[] {
  if (
    Array.isArray(chart.series)
  ) {
    return chart.series;
  }

  if (
    chart.canonical_data &&
    Array.isArray(
      (chart.canonical_data as CanonicalChart).series
    )
  ) {
    return (chart.canonical_data as CanonicalChart)
      .series;
  }

  return [];
}

/* ============================================================
   PROCESSING HELPERS
   ============================================================ */

export type ProcessingStage =
  | "upload"
  | "extract"
  | "normalize"
  | "canonicalize"
  | "visualize"
  | "validate";

export interface StageState {
  stage: ProcessingStage;
  label: string;
  state:
    | "pending"
    | "active"
    | "complete"
    | "error";
}

export const PROCESSING_STAGES: Array<{
  stage: ProcessingStage;
  label: string;
}> = [
  {
    stage: "upload",
    label: "Upload",
  },
  {
    stage: "extract",
    label: "Extract",
  },
  {
    stage: "normalize",
    label: "Normalize",
  },
  {
    stage: "canonicalize",
    label: "Canonicalize",
  },
  {
    stage: "visualize",
    label: "Visualize",
  },
  {
    stage: "validate",
    label: "Validate",
  },
];

export function normalizeProcessingStatus(
  status: ProcessingStatus | null
): string {
  if (!status) {
    return "";
  }

  return safeString(
    status.processing_status ||
      status.status
  ).toLowerCase();
}

export function processingIsComplete(
  status: ProcessingStatus | null
): boolean {
  const normalized =
    normalizeProcessingStatus(
      status
    );

  return [
    "complete",
    "completed",
    "success",
    "succeeded",
    "done",
  ].includes(normalized);
}

export function processingHasFailed(
  status: ProcessingStatus | null
): boolean {
  const normalized =
    normalizeProcessingStatus(
      status
    );

  return [
    "failed",
    "error",
    "failure",
  ].includes(normalized);
}

export function processingLabel(
  status: ProcessingStatus | null
): string {
  if (!status) {
    return "Waiting for document";
  }

  if (
    status.message
  ) {
    return status.message;
  }

  if (
    status.current_stage
  ) {
    return status.current_stage;
  }

  if (
    status.stage
  ) {
    return status.stage;
  }

  const normalized =
    normalizeProcessingStatus(
      status
    );

  if (
    normalized ===
      "completed" ||
    normalized ===
      "complete"
  ) {
    return "Processing complete";
  }

  if (
    normalized ===
      "failed" ||
    normalized ===
      "error"
  ) {
    return (
      status.error ||
      status.error_message ||
      "Processing failed"
    );
  }

  return "Processing document";
}

/* ============================================================
   EVENT HELPERS
   ============================================================ */

export function eventLabel(
  event: ProcessingEvent
): string {
  return (
    safeString(
      event.message
    ) ||
    safeString(
      event.event_type
    ) ||
    safeString(
      event.type
    ) ||
    safeString(
      event.stage
    ) ||
    "Processing event"
  );
}

/* ============================================================
   DATA VALIDATION
   ============================================================ */

export interface ValidationResult {
  valid: boolean;
  message?: string;
}

export function validateSeries(
  series: ChartSeries[],
  chartTypeValue: string
): ValidationResult {
  if (!Array.isArray(series)) {
    return {
      valid: false,
      message:
        "Chart data must contain a valid series.",
    };
  }

  for (
    let seriesIndex = 0;
    seriesIndex <
    series.length;
    seriesIndex += 1
  ) {
    const current =
      series[seriesIndex];

    const values =
      Array.isArray(
        current.values
      )
        ? current.values
        : Array.isArray(
            current.data
          )
        ? current.data
        : [];

    for (
      let valueIndex = 0;
      valueIndex <
      values.length;
      valueIndex += 1
    ) {
      const value =
        values[valueIndex];

      if (
        value === null ||
        value === undefined ||
        value === ""
      ) {
        continue;
      }

      const number =
        typeof value ===
        "number"
          ? value
          : Number(value);

      if (
        !Number.isFinite(
          number
        )
      ) {
        return {
          valid: false,
          message: `Invalid numeric value at series ${
            seriesIndex + 1
          }, row ${
            valueIndex + 1
          }.`,
        };
      }

      if (
        (chartTypeValue ===
          "pie" ||
          chartTypeValue ===
            "donut") &&
        number < 0
      ) {
        return {
          valid: false,
          message:
            "Pie and donut charts require non-negative values.",
        };
      }
    }
  }

  return {
    valid: true,
  };
}

/* ============================================================
   FORMATTING
   ============================================================ */

export function formatNumber(
  value: unknown
): string {
  const number =
    Number(value);

  if (
    !Number.isFinite(
      number
    )
  ) {
    return "—";
  }

  return new Intl.NumberFormat(
    "en-US",
    {
      maximumFractionDigits: 2,
    }
  ).format(number);
}

export function formatPercent(
  value: unknown
): string {
  const number =
    Number(value);

  if (
    !Number.isFinite(
      number
    )
  ) {
    return "—";
  }

  return `${number.toFixed(1)}%`;
}

/* ============================================================
   TEXT
   ============================================================ */

export function truncate(
  value: unknown,
  maximum = 48
): string {
  const text =
    safeString(value);

  if (
    text.length <=
    maximum
  ) {
    return text;
  }

  return `${text.slice(
    0,
    Math.max(
      1,
      maximum - 1
    )
  )}…`;
}
