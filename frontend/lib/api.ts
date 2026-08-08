const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, init);
  if (!res.ok) {
    throw new Error(`API request to ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export interface HealthResponse {
  status: string;
}

// The only endpoint that exists so far — real data endpoints (seasons, games, ...) land in
// build-order steps 4-5 once Game Score calculation (step 3) gives them something to serve.
export function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}
