import type { RatioSnapshot, ScreenerResponse, TickerDetail } from './types'

const API_BASE =
  process.env.NEXT_INTERNAL_API_BASE ||
  process.env.NEXT_PUBLIC_API_BASE ||
  'http://localhost:8000/api/v1'

const REVALIDATE_SECONDS = 300

async function fetchJSON<T>(path: string, params?: Record<string, string | number>): Promise<T | null> {
  try {
    const url = new URL(`${API_BASE}${path}`)
    if (params) {
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)))
    }
    const res = await fetch(url.toString(), {
      next: { revalidate: REVALIDATE_SECONDS },
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) return null
    return (await res.json()) as T
  } catch {
    return null
  }
}

export interface LandingData {
  topRatios: RatioSnapshot[]
  valueRatios: RatioSnapshot[]
  primary: TickerDetail | null
  secondary: TickerDetail | null
  totalCount: number
}

export async function fetchLandingData(): Promise<LandingData> {
  const [topRes, valueRes, primary, secondary] = await Promise.all([
    fetchJSON<ScreenerResponse>('/fundamentals/screener', {
      limit: 6,
      sort_by: 'per_ttm',
      sort_desc: 'false',
    }),
    fetchJSON<ScreenerResponse>('/fundamentals/screener', {
      limit: 5,
      per_max: 15,
      roe_min: 0.2,
      sort_by: 'per_ttm',
      sort_desc: 'false',
    }),
    fetchJSON<TickerDetail>('/fundamentals/AAPL'),
    fetchJSON<TickerDetail>('/fundamentals/MSFT'),
  ])

  return {
    topRatios: topRes?.data ?? [],
    valueRatios: valueRes?.data ?? [],
    primary,
    secondary,
    totalCount: topRes?.total ?? 0,
  }
}
