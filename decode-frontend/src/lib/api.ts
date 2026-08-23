import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

// ── Documents ─────────────────────────────────────────────────────────────
export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('run_pipeline', 'true');
  const res = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function listDocuments() {
  const res = await api.get('/documents');
  return res.data;
}

export async function getDocument(id: string) {
  const res = await api.get(`/documents/${id}`);
  return res.data;
}

export async function getDocumentStatus(id: string) {
  const res = await api.get(`/documents/${id}/status`);
  return res.data;
}

export async function getDocumentCharts(id: string) {
  const res = await api.get(`/documents/${id}/charts`);
  return res.data;
}

export async function deleteDocument(id: string) {
  const res = await api.delete(`/documents/${id}`);
  return res.data;
}

// ── Charts ────────────────────────────────────────────────────────────────
export async function getChart(chartId: string) {
  const res = await api.get(`/charts/${chartId}`);
  return res.data;
}

export async function reconstructChart(chartId: string, options: {
  chart_type?: string;
  series?: any[];
  palette?: string;
}) {
  const res = await api.post(`/charts/${chartId}/reconstruct`, options);
  return res.data;
}

export async function rescoreChart(chartId: string) {
  const res = await api.post(`/charts/${chartId}/rescore`);
  return res.data;
}

// ── Exports ───────────────────────────────────────────────────────────────
export function getExportUrl(chartId: string, format: 'png' | 'svg') {
  return `${API_BASE}/exports/${chartId}/${format}`;
}

// ── Palettes ──────────────────────────────────────────────────────────────
export async function getPalettes() {
  const res = await api.get('/palettes');
  return res.data;
}

// ── Stats ─────────────────────────────────────────────────────────────────
export async function getStats() {
  const res = await api.get('/stats');
  return res.data;
}

// ── Health ────────────────────────────────────────────────────────────────
export async function checkHealth() {
  const res = await api.get('/health');
  return res.data;
}

export default api;
