const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1"

async function userFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("argfy_token") : null
  const res = await fetch(`${API_BASE}${path}`, {
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

export interface BillingInfo {
  subscription_id?: string
  plan: string
  status: string
  cancel_at_period_end: boolean
  current_period_start?: string
  current_period_end?: string
}

export interface ApiKeyInfo {
  id: string
  key_prefix: string | null
  name: string
  last_used: string | null
  created_at: string | null
}

export interface ApiKeyCreateResponse {
  id: string
  key_prefix: string
  raw_key: string
  name: string
}

export const userApi = {
  billing: () => userFetch<BillingInfo>("/billing/portal"),

  cancelSubscription: () =>
    userFetch<{ message: string; cancel_at_period_end: boolean }>("/billing/cancel", { method: "POST" }),

  createCheckout: (plan: string) =>
    userFetch<{ init_point: string; sandbox_init_point: string; preference_id: string; plan: string }>(
      `/billing/create-checkout?plan=${plan}`,
      { method: "POST" },
    ),

  apiKeys: () => userFetch<{ data: ApiKeyInfo[] }>("/auth/api-keys"),

  createApiKey: (name: string) =>
    userFetch<ApiKeyCreateResponse>("/auth/api-keys", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  revokeApiKey: (keyId: string) =>
    userFetch<{ message: string }>(`/auth/api-keys/${keyId}`, { method: "DELETE" }),
}
