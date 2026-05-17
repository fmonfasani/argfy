import { z } from "zod"
import {
  ScreenerResponse, ScreenerResponseSchema,
  CoverageResponse, CoverageResponseSchema,
  TickerDetail, TickerDetailSchema,
  PriceHistoryResponse, PriceHistoryResponseSchema,
  MetricHistoryResponse, MetricHistoryResponseSchema,
  ScreenerFilters,
} from "./types"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

class ApiError extends Error {
  status: number
  detail: unknown
  constructor(status: number, detail: unknown) {
    super(`API ${status}`)
    this.status = status
    this.detail = detail
  }
}

async function apiFetch<T>(
  path: string,
  params: Record<string, unknown> | null,
  schema: z.ZodSchema<T>,
): Promise<T> {
  const url = new URL(`${API_BASE}/api/v1${path}`)
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") {
        url.searchParams.set(k, String(v))
      }
    })
  }

  const res = await fetch(url.toString(), {
    headers: { "Content-Type": "application/json" },
    signal: AbortSignal.timeout(15000),
  })

  if (res.status === 404) {
    throw new ApiError(404, `Not found: ${path}`)
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(res.status, body)
  }

  const json = await res.json()
  return schema.parse(json)
}

export const fundamentals = {
  screener: (filters: ScreenerFilters) =>
    apiFetch<ScreenerResponse>("/fundamentals/screener", filters as Record<string, unknown>, ScreenerResponseSchema),

  coverage: () =>
    apiFetch<CoverageResponse>("/fundamentals/coverage", null, CoverageResponseSchema),

  detail: (ticker: string) =>
    apiFetch<TickerDetail>(`/fundamentals/${ticker}`, null, TickerDetailSchema),

  priceHistory: (ticker: string, period = "5y", interval = "1d") =>
    apiFetch<PriceHistoryResponse>(
      `/fundamentals/${ticker}/price`,
      { period, interval },
      PriceHistoryResponseSchema,
    ),

  metricHistory: (ticker: string, metric: string, fromDate?: string, toDate?: string) =>
    apiFetch<MetricHistoryResponse>(
      `/fundamentals/${ticker}/history`,
      { metric, from: fromDate, to: toDate },
      MetricHistoryResponseSchema,
    ),
}
