const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

async function adminFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("argfy_token") : null
  const res = await fetch(`${API_BASE}/api/v1/admin${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Request failed" }))
    throw new Error(body.detail || "Request failed")
  }
  return res.json()
}

export interface AdminOverview {
  tenant_id: string
  plan: string
  api_calls_today: number
  active_users: number
  etl_runs_today: number
  subscription_status: string
}

export interface AdminUser {
  id: string
  email: string
  nombre: string | null
  role: string
  is_active: boolean
  created_at: string | null
}

export interface ApiKeyInfo {
  id: string
  key_prefix: string | null
  name: string
  last_used: string | null
  created_at: string | null
}

export interface ETLRunInfo {
  id: string
  job_name: string
  trigger: string
  status: string
  started_at: string | null
  finished_at: string | null
  duration_ms: number | null
  rows_inserted: number
  rows_updated: number
  errors_count: number
}

export interface ETLStatus {
  scheduler_running: boolean
  registered_jobs: string[]
  last_runs: Record<string, { status: string; started_at: string | null; finished_at: string | null; duration_ms: number | null } | null>
}

export const adminApi = {
  overview: () => adminFetch<AdminOverview>("/overview"),
  users: () => adminFetch<{ data: AdminUser[] }>("/users"),
  apiKeys: () => adminFetch<{ data: ApiKeyInfo[] }>("/api-keys"),
  createApiKey: (name: string) =>
    adminFetch<{ id: string; key_prefix: string; raw_key: string; name: string }>("/api-keys", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  revokeApiKey: (keyId: string) =>
    adminFetch<{ message: string }>(`/api-keys/${keyId}`, { method: "DELETE" }),
  etlLastRuns: (limit = 20) =>
    adminFetch<{ count: number; data: ETLRunInfo[] }>(`/etl/last-runs?limit=${limit}`),
  etlStatus: () => adminFetch<ETLStatus>("/etl/status"),
  etlTrigger: (jobName: string) =>
    adminFetch<{ message: string; job_name: string }>(`/etl/trigger/${jobName}`, { method: "POST" }),
  billing: () => adminFetch<{ data: any[] }>("/billing"),
  createInvitation: (email: string, role = "member") =>
    adminFetch<{ id: string; email: string; role: string; token: string; expires_at: string }>("/invitations", {
      method: "POST",
      body: JSON.stringify({ email, role }),
    }),
}
