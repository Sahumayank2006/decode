/* eslint-disable */

import axios, { AxiosError } from "axios";

/* ============================================================
   DECODE API CONFIGURATION
   ============================================================ */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    Accept: "application/json",
  },
});

/* ============================================================
   TYPES
   ============================================================ */

export interface ChartDataPoint {
  category: string;
  [key: string]: string | number;
}

export interface ChartSeries {
  name: string;
  values: number[];
}

export interface ProcessingEvent {
  type?: string;
  event_type?: string;
  stage?: string;
  message?: string;
  timestamp?: string;
  data?: unknown;
}

export interface ProcessingStatus {
  status?: string;
  processing_status?: string;
  stage?: string;
  current_stage?: string;
  message?: string;
  progress?: number;
  error?: boolean;
  error_message?: string;
  completed?: boolean;
  events?: ProcessingEvent[];
  summary?: Record<string, unknown>;
  data?: any;
}

export interface DocumentSummary {
  id: string;
  filename?: string;
  name?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  chart_count?: number;
  table_count?: number;
  [key: string]: unknown;
}

export interface ApiChart {
  id?: string;
  chart_id?: string;

  title?: string;
  chart_type?: string;
  chartType?: string;
  type?: string;
  render_type?: string;

  categories?: string[];
  labels?: string[];

  series?: ChartSeries[];

  data?: ChartDataPoint[] | unknown;
  confidence?: number;

  page?: number;
  page_number?: number;

  [key: string]: unknown;
}



export interface UploadResponse {
  document_id?: string;
  documentId?: string;
  id?: string;

  filename?: string;

  status?: string;

  message?: string;

  data?: any;
}

export interface BackendCanonicalSeries {
  name?: string;
  label?: string;
  values?: unknown[];
  data?: unknown[];
  points?: unknown[];
}

export interface BackendCanonicalData {
  title?: string;
  detected_type?: string;
  chart_type?: string;
  categories?: unknown[];
  labels?: unknown[];
  x_values?: unknown[];
  series?: BackendCanonicalSeries[];
  metadata?: Record<string, unknown>;
  confidence?: number;
}

export interface BackendChartRecord {
  id?: string;
  chart_id?: string;

  title?: string;
  chart_type?: string;
  type?: string;
  detected_type?: string;

  canonical_data?: BackendCanonicalData;

  metadata?: Record<string, unknown>;

  confidence?: number;

  [key: string]: unknown;
}

export interface DocumentChartsResponse {
  document_id?: string;
  count?: number;
  charts: NormalizedChart[];
}

/* ============================================================
   ERROR HANDLING
   ============================================================ */

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as
      | {
          message?: string;
          error?: string;
          detail?: string;
        }
      | undefined;

    return (
      data?.message ||
      data?.error ||
      data?.detail ||
      error.message ||
      "Unable to communicate with the DECODE backend."
    );
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}

/* ============================================================
   HEALTH
   ============================================================ */

export async function healthCheck(): Promise<any> {
  /*
   * Prefer the real production health endpoint.
   *
   * Older demo builds used /demo/health.
   * We keep a fallback for compatibility.
   */

  try {
    const response = await api.get("/health");
    return response.data;
  } catch {
    const response = await api.get("/demo/health");
    return response.data;
  }
}

export async function getDemoHealth(): Promise<any> {
  return healthCheck();
}

/* ============================================================
   DEMO CAPABILITIES
   ============================================================ */

export async function getDemoCapabilities(): Promise<any> {
  const response = await api.get("/demo/capabilities");
  return response.data;
}

export async function getDemoProduct(): Promise<any> {
  const response = await api.get("/demo/product");
  return response.data;
}

/* ============================================================
   DOCUMENT UPLOAD
   ============================================================ */

export async function uploadDocument(
  file: File
): Promise<UploadResponse> {
  if (!file) {
    throw new Error("No PDF was selected.");
  }

  if (
    file.type !== "application/pdf" &&
    !file.name.toLowerCase().endsWith(".pdf")
  ) {
    throw new Error("Please select a valid PDF document.");
  }

  if (file.size <= 0) {
    throw new Error("The selected PDF is empty.");
  }

  /*
   * Backend MAX_CONTENT_LENGTH is 50 MB.
   * Keep frontend validation aligned with it.
   */
  const MAX_SIZE = 50 * 1024 * 1024;

  if (file.size > MAX_SIZE) {
    throw new Error(
      "PDF is larger than the 50 MB backend upload limit."
    );
  }

  const formData = new FormData();

  formData.append("file", file);
  formData.append("run_pipeline", "true");

  const response = await api.post(
    "/documents/upload",
    formData,
    {
      /*
       * Do NOT manually force Content-Type.
       * Axios/browser will add the correct multipart boundary.
       */
      timeout: 120000,

      onUploadProgress: (event) => {
        if (!event.total) return;

        const progress = Math.round(
          (event.loaded / event.total) * 100
        );

        console.debug(
          `DECODE PDF upload: ${progress}%`
        );
      },
    }
  );

  return response.data;
}

/* ============================================================
   DOCUMENT ID NORMALIZATION
   ============================================================ */

export function extractDocumentId(
  payload: unknown
): string | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const value = payload as any;

  const id =
    value.document_id ??
    value.documentId ??
    value.id ??
    value.document?.id ??
    value.data?.document_id ??
    value.data?.documentId ??
    value.data?.id ??
    value.data?.document?.id;

  return typeof id === "string" && id.length > 0
    ? id
    : null;
}

/* ============================================================
   DOCUMENT NAME
   ============================================================ */

export function extractDocumentName(
  payload: unknown
): string | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const value = payload as any;

  const name =
    value.filename ??
    value.file_name ??
    value.document_name ??
    value.name ??
    value.document?.filename ??
    value.document?.file_name ??
    value.document?.name ??
    value.data?.filename ??
    value.data?.file_name ??
    value.data?.document_name;

  return typeof name === "string" && name.length > 0
    ? name.split(/[\\/]/).pop() || name
    : null;
}

/* ============================================================
   DOCUMENTS
   ============================================================ */

export async function getDocuments(): Promise<any> {
  const response = await api.get("/documents");
  return response.data;
}

export async function listDocuments(): Promise<any> {
  return getDocuments();
}

export async function deleteDocument(
  documentId: string
): Promise<any> {
  const response = await api.delete(
    `/documents/${encodeURIComponent(documentId)}`
  );

  return response.data;
}

/* ============================================================
   SINGLE DOCUMENT
   ============================================================ */

export async function getDocument(
  documentId: string
): Promise<any> {
  const response = await api.get(
    `/documents/${encodeURIComponent(documentId)}`
  );

  return response.data;
}

/* ============================================================
   DOCUMENT STATUS
   ============================================================ */

export async function getDocumentStatus(
  documentId: string
): Promise<ProcessingStatus> {
  const response = await api.get(
    `/documents/${encodeURIComponent(documentId)}/status`
  );

  return response.data;
}

/* ============================================================
   DOCUMENT CHARTS
   ============================================================ */

import { normalizeCharts, type NormalizedChart } from "./canonicalNormalizer";

export async function getDocumentCharts(
  documentId: string
): Promise<NormalizedChart[]> {
  const response =
    await api.get<any>(
      `/documents/${documentId}/charts`
    );

  const charts = normalizeCharts(response.data);
  return charts;
}

/* ============================================================
   CHART
   ============================================================ */

export async function getChart(
  chartId: string
): Promise<ApiChart> {
  const response = await api.get(
    `/charts/${encodeURIComponent(chartId)}`
  );

  return response.data;
}

/* ============================================================
   RESCORE
   ============================================================ */

export async function rescoreChart(
  chartId: string,
  payload?: Record<string, unknown>
): Promise<any> {
  const response = await api.post(
    `/charts/${encodeURIComponent(chartId)}/rescore`,
    payload || {}
  );

  return response.data;
}

/* ============================================================
   EXPORT URLS
   ============================================================ */

export function getChartSvgUrl(
  chartId: string
): string {
  return `${API_BASE_URL}/exports/${encodeURIComponent(
    chartId
  )}/svg`;
}

export function getChartPngUrl(
  chartId: string
): string {
  return `${API_BASE_URL}/exports/${encodeURIComponent(
    chartId
  )}/png`;
}

export function getExportUrl(
  chartId: string,
  format: "svg" | "png" = "png"
): string {
  return format === "svg"
    ? getChartSvgUrl(chartId)
    : getChartPngUrl(chartId);
}

/* ============================================================
   GENERIC RENDER
   ============================================================ */

export async function renderChart(
  payload: Record<string, unknown>
): Promise<any> {
  const response = await api.post(
    "/charts/render",
    payload
  );

  return response.data;
}

/* ============================================================
   NORMALIZE CHART TYPE
   ============================================================ */

export function normalizeChartType(
  value: unknown
):
  | "bar"
  | "line"
  | "area"
  | "pie"
  | "donut"
  | "radar" {
  const type = String(
    value ?? "bar"
  )
    .toLowerCase()
    .replace(/[\s-]/g, "_");

  if (type.includes("line")) {
    return "line";
  }

  if (type.includes("area")) {
    return "area";
  }

  if (
    type.includes("donut") ||
    type.includes("doughnut")
  ) {
    return "donut";
  }

  if (type.includes("pie")) {
    return "pie";
  }

  if (type.includes("radar") ||
      type.includes("spider")) {
    return "radar";
  }

  return "bar";
}

/* ============================================================
   NORMALIZE NUMBER
   ============================================================ */

function toNumber(
  value: unknown
): number {
  if (
    typeof value === "number" &&
    Number.isFinite(value)
  ) {
    return value;
  }

  if (
    typeof value === "string" &&
    value.trim() !== ""
  ) {
    const cleaned = value
      .replace(/,/g, "")
      .replace(/%/g, "")
      .trim();

    const parsed = Number(cleaned);

    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  if (
    value &&
    typeof value === "object"
  ) {
    const objectValue = value as any;

    return toNumber(
      objectValue.value ??
      objectValue.y ??
      objectValue.numeric_value ??
      objectValue.number
    );
  }

  return 0;
}

/* ============================================================
   NORMALIZE SERIES
   ============================================================ */

function normalizeSeries(
  rawSeries: unknown
): ChartSeries[] {
  if (!Array.isArray(rawSeries)) {
    return [];
  }

  return rawSeries
    .map((item: any, index) => {
      const name =
        item?.name ??
        item?.label ??
        item?.series_name ??
        item?.key ??
        `Series ${index + 1}`;

      const rawValues =
        item?.values ??
        item?.data ??
        item?.points ??
        [];

      if (!Array.isArray(rawValues)) {
        return null;
      }

      return {
        name: String(name),
        values: rawValues.map(toNumber),
      };
    })
    .filter(
      (item): item is ChartSeries =>
        item !== null
    );
}

/* ============================================================
   EXTRACT CATEGORIES
   ============================================================ */

function extractCategories(
  chart: any
): string[] {
  const direct =
    chart?.categories ??
    chart?.labels ??
    chart?.x_values ??
    chart?.x_labels;

  if (Array.isArray(direct)) {
    return direct.map((value) =>
      String(
        value?.label ??
        value?.name ??
        value
      )
    );
  }

  /*
   * Some pipeline versions return:
   *
   * data: [
   *   { category: "Q1", Revenue: 10 }
   * ]
   */

  const rows =
    Array.isArray(chart?.data)
      ? chart.data
      : null;

  if (rows && rows.length > 0) {
    return rows.map((row: any, index: number) =>
      String(
        row?.category ??
        row?.label ??
        row?.name ??
        row?.x ??
        `Row ${index + 1}`
      )
    );
  }

  return [];
}

/* ============================================================
   DATA-ROW → SERIES
   ============================================================ */

function seriesFromRows(
  rows: any[],
  categories: string[]
): ChartSeries[] {
  if (!rows.length) {
    return [];
  }

  const keys = new Set<string>();

  rows.forEach((row) => {
    if (!row || typeof row !== "object") {
      return;
    }

    Object.keys(row).forEach((key) => {
      if (
        key !== "category" &&
        key !== "label" &&
        key !== "name" &&
        key !== "x"
      ) {
        keys.add(key);
      }
    });
  });

  return Array.from(keys)
    .map((key) => ({
      name: key,
      values: categories.map(
        (_, index) =>
          toNumber(rows[index]?.[key])
      ),
    }))
    .filter((series) =>
      series.values.length > 0
    );
}

/* ============================================================
   NORMALIZE SINGLE CHART
   ============================================================ */

export function normalizeChart(
  payload: unknown,
  index = 0
): NormalizedChart | null {
  if (!payload) {
    return null;
  }

  let chart: any = payload;

  if (
    chart?.chart &&
    typeof chart.chart === "object"
  ) {
    chart = chart.chart;
  }

  if (
    chart?.data?.chart &&
    typeof chart.data.chart === "object"
  ) {
    chart = chart.data.chart;
  }

  const id = String(
    chart?.id ??
    chart?.chart_id ??
    chart?.chartId ??
    `chart-${index + 1}`
  );

  const title = String(
    chart?.title ??
    chart?.name ??
    chart?.chart_title ??
    `Extracted Chart ${index + 1}`
  );

  let categories =
    extractCategories(chart);

  let series =
    normalizeSeries(
      chart?.series ??
      chart?.data?.series
    );

  /*
   * If backend returned row-oriented data,
   * convert it into canonical series.
   */
  if (
    series.length === 0 &&
    Array.isArray(chart?.data)
  ) {
    if (categories.length === 0) {
      categories = extractCategories(
        chart
      );
    }

    series = seriesFromRows(
      chart.data,
      categories
    );
  }

  /*
   * Another common structure:
   *
   * {
   *   data: {
   *      categories: [],
   *      series: []
   *   }
   * }
   */
  if (
    series.length === 0 &&
    chart?.data &&
    typeof chart.data === "object"
  ) {
    const nested = chart.data;

    if (
      categories.length === 0 &&
      Array.isArray(nested.categories)
    ) {
      categories =
        nested.categories.map(
          (value: unknown) =>
            String(value)
        );
    }

    series =
      normalizeSeries(
        nested.series
      );
  }

  if (
    categories.length === 0 &&
    series.length > 0
  ) {
    const maxLength =
      Math.max(
        ...series.map(
          (item) => item.values.length
        )
      );

    categories = Array.from(
      { length: maxLength },
      (_, i) => `Item ${i + 1}`
    );
  }

  /*
   * Align series to category length.
   */
  series = series.map((item) => ({
    ...item,
    values: categories.map(
      (_, index) =>
        item.values[index] ?? 0
    ),
  }));

  const confidenceRaw =
    chart?.confidence ??
    chart?.extraction_confidence ??
    chart?.source_confidence ??
    chart?.metadata?.confidence ??
    0;

  const confidenceNumber =
    Number(confidenceRaw);

  const confidence =
    Number.isFinite(confidenceNumber)
      ? confidenceNumber > 1
        ? confidenceNumber
        : confidenceNumber * 100
      : 0;

  const pageRaw =
    chart?.page ??
    chart?.page_number ??
    chart?.source_page ??
    null;

  const page =
    Number.isFinite(Number(pageRaw))
      ? Number(pageRaw)
      : null;

  if (
    categories.length === 0 ||
    series.length === 0
  ) {
    return {
      id,
      title,
      chart_type: normalizeChartType(
        chart?.chart_type ??
        chart?.chartType ??
        chart?.type ??
        chart?.render_type
      ),
      categories,
      series,
      confidence,
      metadata: {},
      source: chart,
    };
  }

  return {
    id,
    title,
    chart_type: normalizeChartType(
      chart?.chart_type ??
      chart?.chartType ??
      chart?.type ??
      chart?.render_type
    ),
    categories,
    series,
    confidence,
    metadata: {},
    source: chart,
  };
}

/* ============================================================
   NORMALIZE DOCUMENT CHART RESPONSE
   ============================================================ */

export function normalizeChartsResponse(
  payload: unknown
): NormalizedChart[] {
  if (!payload) {
    return [];
  }

  let candidates: any[] = [];

  if (Array.isArray(payload)) {
    candidates = payload;
  } else if (
    typeof payload === "object"
  ) {
    const value = payload as any;

    if (Array.isArray(value.charts)) {
      candidates = value.charts;
    } else if (
      Array.isArray(value.data?.charts)
    ) {
      candidates = value.data.charts;
    } else if (value.chart) {
      candidates = [value.chart];
    } else if (value.data?.chart) {
      candidates = [value.data.chart];
    } else if (
      value.data &&
      typeof value.data === "object"
    ) {
      candidates = [value.data];
    } else {
      candidates = [value];
    }
  }

  return candidates
    .map((chart, index) =>
      normalizeChart(chart, index)
    )
    .filter(
      (chart): chart is NormalizedChart =>
        chart !== null
    );
}

/* ============================================================
   WAIT FOR REAL BACKEND PROCESSING
   ============================================================ */

export async function waitForDocumentCompletion(
  documentId: string,
  options?: {
    intervalMs?: number;
    timeoutMs?: number;
    onStatus?: (
      status: ProcessingStatus
    ) => void;
  }
): Promise<ProcessingStatus> {
  const intervalMs =
    options?.intervalMs ?? 1200;

  const timeoutMs =
    options?.timeoutMs ??
    5 * 60 * 1000;

  const started =
    Date.now();

  let lastStatus: ProcessingStatus = {};

  while (
    Date.now() - started <
    timeoutMs
  ) {
    const status =
      await getDocumentStatus(
        documentId
      );

    lastStatus = status;

    options?.onStatus?.(status);

    const rawStatus = String(
      status?.status ??
      status?.processing_status ??
      ""
    ).toLowerCase();

    const completed =
      status?.completed === true ||
      rawStatus === "completed" ||
      rawStatus === "complete" ||
      rawStatus === "done" ||
      rawStatus === "success" ||
      rawStatus === "succeeded" ||
      rawStatus.includes("complete") ||
      rawStatus.includes("success");

    const failed =
      status?.error === true ||
      rawStatus === "failed" ||
      rawStatus === "error" ||
      rawStatus.includes("failed") ||
      rawStatus.includes("error");

    if (completed) {
      return status;
    }

    if (failed) {
      throw new Error(
        status?.error_message ||
        status?.message ||
        "DECODE processing failed."
      );
    }

    await new Promise(
      (resolve) =>
        setTimeout(
          resolve,
          intervalMs
        )
    );
  }

  /*
   * Do not claim success if the pipeline
   * exceeded our wait window.
   */
  throw new Error(
    `DECODE is still processing after ${Math.round(
      timeoutMs / 1000
    )} seconds. Please wait and refresh the document.`
  );
}

/* ============================================================
   DECODE-VISION SPECIALIST API
   ============================================================ */

export interface DecodeVisionResponse {
  chart_type: "bar" | "grouped_bar" | "stacked_bar" | "line" | "multi_line" | "scatter" | "pie" | "donut" | "radar";
  title: string | null;
  axes: {
    x: { label: string | null; unit: string | null; type: "categorical" | "numeric"; categories: string[]; min: number | null; max: number | null };
    y: { label: string | null; unit: string | null; type: "numeric"; min: number; max: number; scale_type: "linear" | "log" };
  };
  legend: Array<{ series_name: string; color_hint: string; inferred: boolean }>;
  extracted_data: {
    series: Array<{
      name: string;
      data: Array<{ x: string | number; y: number; confidence: "high" | "medium" | "low" }>;
    }>;
  };
  render_spec: {
    library_hint: "recharts" | "chartjs" | "matplotlib";
    series: Array<{ name: string; color: string; values: number[] }>;
    categories: string[];
  };
  verification: {
    checks_passed: string[];
    checks_failed: string[];
    sum_check: string | null;
  };
  confidence: { overall: "high" | "medium" | "low"; notes: string };
  extraction_notes: string;
}

export async function extractWithDecodeVision(
  image: File | string,
  hint?: string
): Promise<DecodeVisionResponse> {
  if (typeof image === "string") {
    const res = await api.post<DecodeVisionResponse>("/extract/decode-vision", {
      image_base64: image,
      hint,
    });
    return res.data;
  } else {
    const formData = new FormData();
    formData.append("file", image);
    if (hint) formData.append("hint", hint);
    const res = await api.post<DecodeVisionResponse>("/extract/decode-vision", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  }
}

export async function runChartDecodeVision(chartId: string): Promise<{
  status: string;
  chart_id: string;
  decode_vision: DecodeVisionResponse;
}> {
  const res = await api.post<{ status: string; chart_id: string; decode_vision: DecodeVisionResponse }>(
    `/charts/${chartId}/decode-vision`
  );
  return res.data;
}

/* ============================================================
   PRODUCT
   ============================================================ */

export async function getProductInfo() {
  return getDemoProduct();
}

/* ============================================================
   DEFAULT EXPORT
   ============================================================ */

export default api;
