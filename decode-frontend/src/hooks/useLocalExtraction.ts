// useLocalExtraction.ts
//
// Minimal, self-contained hook: given a chart crop image (as a File or
// Blob), calls the local /extract endpoint and returns the exact shape
// ArtifactExtraction expects.  No mock data, no fallback, no silent
// failure — errors are surfaced as state so you can SEE when extraction
// fails instead of getting a placeholder that looks fine.

import { useState, useCallback } from "react";
import { ArtifactExtraction } from "../store/useArtifactStore";

const EXTRACTION_API = process.env.NEXT_PUBLIC_EXTRACTION_URL || "http://localhost:8000/extract";

/**
 * Normalizes the raw payload returned by the /extract endpoint into the
 * canonical ArtifactExtraction shape the frontend expects.
 *
 * The backend can return data in several nested forms:
 *   1. { chart_type, render: { categories, series }, preview, ... }
 *   2. { chart_type, categories, series, ... }
 *   3. { chart_type, canonical_data: { categories, series }, ... }
 *
 * This function handles all three, extracting `categories` and `series`
 * from whichever location they live in, and flattening them to top-level
 * fields on the returned ArtifactExtraction.
 */
function normalizeExtractionResult(raw: any): Partial<ArtifactExtraction> {
  if (!raw || typeof raw !== "object") return {};

  // ── Resolve chart_type ──────────────────────────────────────────
  const chart_type: string = (
    raw.chart_type ||
    raw.detected_type ||
    raw.type ||
    "bar"
  ).toString().toLowerCase();

  // ── Resolve title ───────────────────────────────────────────────
  const title: string = raw.title || "";

  // ── Resolve categories ──────────────────────────────────────────
  // Try top-level first, then render.categories, then canonical_data
  let categories: string[] = [];
  if (Array.isArray(raw.categories) && raw.categories.length > 0) {
    categories = raw.categories.map(String);
  } else if (raw.render && Array.isArray(raw.render.categories) && raw.render.categories.length > 0) {
    categories = raw.render.categories.map(String);
  } else if (raw.canonical_data && Array.isArray(raw.canonical_data.categories)) {
    categories = raw.canonical_data.categories.map(String);
  } else if (raw.labels && Array.isArray(raw.labels)) {
    categories = raw.labels.map(String);
  }

  // ── Resolve series ──────────────────────────────────────────────
  // Try top-level first, then render.series, then canonical_data
  let rawSeries: any[] = [];
  if (Array.isArray(raw.series) && raw.series.length > 0) {
    rawSeries = raw.series;
  } else if (raw.render && Array.isArray(raw.render.series) && raw.render.series.length > 0) {
    rawSeries = raw.render.series;
  } else if (raw.canonical_data && Array.isArray(raw.canonical_data.series)) {
    rawSeries = raw.canonical_data.series;
  } else if (Array.isArray(raw.datasets)) {
    rawSeries = raw.datasets;
  }

  // Normalize each series to { name: string, values: number[] }
  const series = rawSeries.map((s: any, idx: number) => {
    const name = String(s.name || s.label || s.key || `Series ${idx + 1}`);

    let values: number[] = [];
    if (Array.isArray(s.values)) {
      values = s.values.map((v: any) => {
        const n = Number(v);
        return Number.isFinite(n) ? n : 0;
      });
    } else if (Array.isArray(s.data)) {
      values = s.data.map((d: any) => {
        if (d && typeof d === "object") {
          const n = Number(d.value ?? d.y ?? d.amount ?? 0);
          return Number.isFinite(n) ? n : 0;
        }
        const n = Number(d);
        return Number.isFinite(n) ? n : 0;
      });
    } else if (Array.isArray(s.points)) {
      values = s.points.map((p: any) => {
        const n = Number(p.value ?? p.y ?? 0);
        return Number.isFinite(n) ? n : 0;
      });
    }

    // If categories came from the series data points, extract them
    if (categories.length === 0 && Array.isArray(s.data)) {
      const catCandidates = s.data
        .filter((d: any) => d && typeof d === "object" && (d.x !== undefined || d.category !== undefined || d.label !== undefined))
        .map((d: any) => String(d.x ?? d.category ?? d.label ?? ""));
      if (catCandidates.length > 0) {
        categories = catCandidates;
      }
    }

    return { name, values, color: s.color || undefined };
  });

  // Align series lengths with categories
  const maxLen = Math.max(categories.length, ...series.map((s: any) => s.values.length));
  if (categories.length < maxLen) {
    while (categories.length < maxLen) {
      categories.push(`Category ${categories.length + 1}`);
    }
  }
  series.forEach((s: any) => {
    while (s.values.length < categories.length) {
      s.values.push(0);
    }
    if (s.values.length > categories.length) {
      s.values = s.values.slice(0, categories.length);
    }
  });

  // ── Resolve confidence ──────────────────────────────────────────
  let confidence = 0.95;
  if (typeof raw.confidence === "number") {
    confidence = raw.confidence > 1 ? raw.confidence / 100 : raw.confidence;
  } else if (raw.confidence && typeof raw.confidence === "object") {
    const cv = raw.confidence.overall || raw.confidence.value;
    if (typeof cv === "number") {
      confidence = cv > 1 ? cv / 100 : cv;
    }
  }

  return {
    chart_type,
    title,
    categories,
    series,
    confidence,
    metadata: raw.metadata || {},
  };
}

export function useLocalExtraction() {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const extract = useCallback(async (imageBlob: Blob, useGemini = true): Promise<ArtifactExtraction> => {
    setStatus("loading");
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", imageBlob, "chart.png");

      const res = await fetch(`${EXTRACTION_API}?use_gemini=${useGemini}`, { method: "POST", body: formData });
      const json = await res.json();

      if (!res.ok || !json.success) {
        throw new Error(json.error || json.detail || `Extraction failed (${res.status})`);
      }

      const rawChart = json.charts?.[0] || json;
      const normalized = normalizeExtractionResult(rawChart);

      setStatus("success");
      return normalized as ArtifactExtraction;
    } catch (e: any) {
      setStatus("error");
      setError(e.message);
      throw e;
    }
  }, []);

  return { extract, status, error };
}
