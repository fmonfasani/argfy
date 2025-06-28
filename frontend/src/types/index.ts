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
export interface Indicator {
  id: string
  name: string
  description: string
  value: number | string
  unit: string
  source: string
  category: string
  frequency: string
  date: string
  status: 'success' | 'demo' | 'error'
  change?: number
  changePercent?: number
  trend?: 'up' | 'down' | 'neutral'
}

  export interface Category {
    id: string
    title: string
    description: string
    icon: string
    indicators: string[]
    color: string
  }

  export interface HistoricalData {
    date: string
    value: number
    period: string
  }

  export interface ChartConfig {
    type: 'line' | 'area' | 'bar'
    period: '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | 'MAX'
    showGrid: boolean
    showTooltip: boolean
    animate: boolean
  }

  export interface ModalConfig {
    isOpen: boolean
    indicator: Indicator | null
    historicalData: HistoricalData[]
    chartConfig: ChartConfig
  }

  export interface APIResponse<T = any> {
    status: 'success' | 'error'
    data?: T
    message?: string
    timestamp: string
  }

  export interface DashboardData {
    economia: Record<string, Indicator>
    gobierno: Record<string, Indicator>
    finanzas: Record<string, Indicator>
    mercados: Record<string, Indicator>
    tecnologia: Record<string, Indicator>
    industria: Record<string, Indicator>
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





