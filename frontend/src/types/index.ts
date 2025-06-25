// frontend/src/types/index.ts
export interface EconomicIndicator {
  id: number
  indicator_type: string
  value: number
  date: string
  source: string
  is_active: boolean
  metadata_info?: string
}

export interface HistoricalData {
  date: string
  value: number
  source: string
}

export interface NewsItem {
  id: number
  title: string
  summary: string
  category: string
  source: string
  published_at: string
  is_featured: boolean
  url?: string
}

export interface APIResponse<T> {
  data: T
  timestamp: string
  count?: number
  status: string
  message?: string
}

export interface DashboardSummary {
  timestamp: string
  indicators: {
    count: number
    data: EconomicIndicator[]
  }
  news: {
    count: number
    featured: NewsItem[]
  }
  status: string
}

export interface ChartDataPoint {
  date: string
  value: number
  label?: string
}

export type IndicatorType = 
  | 'dolar_blue'
  | 'dolar_oficial'
  | 'dolar_mep'
  | 'inflacion_mensual'
  | 'reservas_bcra'
  | 'riesgo_pais'
  | 'tasa_bcra'
  | 'merval'

export type NewsCategory = 
  | 'ECONOMÍA'
  | 'MERCADOS'
  | 'COMMODITIES'
  | 'INFLACIÓN'
  | 'FINTECH'
  | 'EXPORTACIONES'

export interface LoadingState {
  isLoading: boolean
  error: string | null
}

// frontend/src/lib/utils.ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number, currency: string = 'ARS'): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('es-AR').format(value)
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`
}

export function getTimeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMs = now.getTime() - date.getTime()
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60))
  const diffInDays = Math.floor(diffInHours / 24)
  
  if (diffInHours < 1) return 'Hace menos de 1 hora'
  if (diffInHours < 24) return `Hace ${diffInHours} hora${diffInHours > 1 ? 's' : ''}`
  if (diffInDays < 7) return `Hace ${diffInDays} día${diffInDays > 1 ? 's' : ''}`
  
  const diffInWeeks = Math.floor(diffInDays / 7)
  return `Hace ${diffInWeeks} semana${diffInWeeks > 1 ? 's' : ''}`
}

export function getIndicatorDisplayValue(indicator: any): string {
  switch (indicator.indicator_type) {
    case 'dolar_blue':
    case 'dolar_oficial':
    case 'dolar_mep':
      return `$${Math.round(indicator.value).toLocaleString()}`
    case 'inflacion_mensual':
      return `${indicator.value.toFixed(1)}%`
    case 'reservas_bcra':
      return `US$${(indicator.value / 1000).toFixed(1)}B`
    case 'riesgo_pais':
      return `${Math.round(indicator.value)} pb`
    case 'tasa_bcra':
      return `${indicator.value.toFixed(1)}%`
    case 'merval':
      return `${Math.round(indicator.value / 1000)}K`
    default:
      return indicator.value.toLocaleString()
  }
}

export function getIndicatorColor(type: string, value?: number): string {
  const baseColors = {
    'dolar_blue': 'text-emerald-600',
    'dolar_oficial': 'text-blue-600',
    'dolar_mep': 'text-purple-600',
    'inflacion_mensual': 'text-red-600',
    'reservas_bcra': 'text-emerald-600',
    'riesgo_pais': 'text-amber-600',
    'tasa_bcra': 'text-slate-700',
    'merval': 'text-green-600'
  }
  
  return baseColors[type as keyof typeof baseColors] || 'text-slate-700'
}

// frontend/src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'

export class APIError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'APIError'
  }
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new APIError(`HTTP error! status: ${response.status}`, response.status)
    }

    const data = await response.json()
    return data
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }
    throw new APIError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

export const api = {
  // Indicators
  getCurrentIndicators: () => 
    fetchAPI<APIResponse<EconomicIndicator[]>>('/indicators/current'),
  
  getHistoricalData: (indicatorType: string, days: number = 30) =>
    fetchAPI<APIResponse<HistoricalData[]>>(`/indicators/historical/${indicatorType}?days=${days}`),
  
  // News
  getNews: (limit: number = 6, category?: string) => {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (category) params.append('category', category)
    return fetchAPI<APIResponse<NewsItem[]>>(`/indicators/news?${params}`)
  },
  
  // Dashboard
  getDashboardSummary: () =>
    fetchAPI<DashboardSummary>('/indicators/summary'),
  
  // Refresh
  refreshIndicators: () =>
    fetchAPI<{ message: string }>('/indicators/refresh', { method: 'POST' }),
}

// frontend/src/hooks/useIndicators.ts
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { EconomicIndicator, LoadingState } from '@/types'

export function useIndicators() {
  const [indicators, setIndicators] = useState<EconomicIndicator[]>([])
  const [loading, setLoading] = useState<LoadingState>({
    isLoading: true,
    error: null
  })

  const fetchIndicators = async () => {
    try {
      setLoading({ isLoading: true, error: null })
      const response = await api.getCurrentIndicators()
      setIndicators(response.data)
    } catch (error) {
      setLoading({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Error fetching indicators'
      })
    } finally {
      setLoading(prev => ({ ...prev, isLoading: false }))
    }
  }

  useEffect(() => {
    fetchIndicators()
  }, [])

  return {
    indicators,
    loading: loading.isLoading,
    error: loading.error,
    refetch: fetchIndicators
  }
}

// frontend/src/hooks/useHistoricalData.ts
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { HistoricalData, LoadingState } from '@/types'

export function useHistoricalData(indicatorType: string, days: number = 30) {
  const [data, setData] = useState<HistoricalData[]>([])
  const [loading, setLoading] = useState<LoadingState>({
    isLoading: true,
    error: null
  })

  const fetchData = async () => {
    if (!indicatorType) return
    
    try {
      setLoading({ isLoading: true, error: null })
      const response = await api.getHistoricalData(indicatorType, days)
      setData(response.data)
    } catch (error) {
      setLoading({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Error fetching historical data'
      })
    } finally {
      setLoading(prev => ({ ...prev, isLoading: false }))
    }
  }

  useEffect(() => {
    fetchData()
  }, [indicatorType, days])

  return {
    data,
    loading: loading.isLoading,
    error: loading.error,
    refetch: fetchData
  }
}