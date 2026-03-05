const API_BASE = "/api";

export interface UploadResponse {
  id: string;
  status: string;
}

export interface UploadStatusResponse {
  id: string;
  filename: string;
  status: string;
  error_message: string | null;
  created_at: string;
  verdict: string | null;
  confidence: number | null;
  visual_score: number | null;
  audio_score: number | null;
  speech_detected: boolean | null;
  audio_weight: number | null;
  file_hash: string | null;
  processing_time: number | null;
  completed_at: string | null;
}

export interface UploadListResponse {
  items: UploadStatusResponse[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface StatsResponse {
  total: number;
  real: number;
  fake: number;
}

export async function uploadVideo(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/uploads`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function getUploadStatus(
  id: string
): Promise<UploadStatusResponse> {
  const res = await fetch(`${API_BASE}/uploads/${id}/status`);
  if (!res.ok) {
    throw new Error("Failed to fetch status");
  }
  return res.json();
}

export async function getUploads(params: {
  page?: number;
  per_page?: number;
  search?: string;
  verdict?: string;
}): Promise<UploadListResponse> {
  const searchParams = new URLSearchParams();
  if (params.page !== undefined) searchParams.set("page", String(params.page));
  if (params.per_page !== undefined)
    searchParams.set("per_page", String(params.per_page));
  if (params.search) searchParams.set("search", params.search);
  if (params.verdict) searchParams.set("verdict", params.verdict);

  const qs = searchParams.toString();
  const res = await fetch(`${API_BASE}/uploads${qs ? `?${qs}` : ""}`);
  if (!res.ok) {
    throw new Error("Failed to fetch uploads");
  }
  return res.json();
}

export async function getStats(): Promise<StatsResponse> {
  const res = await fetch(`${API_BASE}/uploads/stats`);
  if (!res.ok) {
    throw new Error("Failed to fetch stats");
  }
  return res.json();
}
