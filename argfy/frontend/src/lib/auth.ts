const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

export interface AuthUser {
  id: string
  email: string
  nombre: string
  role: string
  tenant_id: string
  is_active?: boolean
  created_at?: string
  subscription?: {
    plan: string
    status: string
    current_period_end?: string
  } | null
}

interface TokenResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export async function register(email: string, password: string, nombre?: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, nombre }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Registration failed" }))
    throw new Error(body.detail || "Registration failed")
  }
  return res.json()
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Login failed" }))
    throw new Error(body.detail || "Login failed")
  }
  return res.json()
}

export async function googleAuth(code: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/v1/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Google auth failed" }))
    throw new Error(body.detail || "Google auth failed")
  }
  return res.json()
}

export async function fetchMe(token: string): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error("Unauthorized")
  return res.json()
}

export function saveToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("argfy_token", token)
  }
}

export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("argfy_token")
  }
  return null
}

export function clearToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("argfy_token")
  }
}
