// frontend/src/components/index.ts
// Exportaciones centralizadas de todos los componentes

// LAYOUT COMPONENTS
export { default as Layout } from './layout/Layout'
export { default as Navigation } from './layout/Navigation'
export { default as Footer } from './layout/Footer'
export { default as ThemeToggle } from './layout/ThemeToggle'

// HERO AND LANDING
export { default as HeroSection } from './landing/HeroSection'
export { default as CategoryGrid } from './landing/CategoryGrid'
export { default as CategoryCard } from './landing/CategoryCard'

// DASHBOARD COMPONENTS
export { default as Dashboard } from './dashboard/Dashboard'
export { default as CategorySection } from './dashboard/CategorySection'
export { default as IndicatorCard } from './dashboard/IndicatorCard'
export { default as Sparkline } from './dashboard/Sparkline'

// MODAL AND CHARTS
export { default as IndicatorModal } from './modal/IndicatorModal'
export { default as HistoricalChart } from './charts/HistoricalChart'
export { default as ChartControls } from './charts/ChartControls'
export { default as ChartStats } from './charts/ChartStats'

// UTILITY COMPONENTS
export { default as LoadingSpinner } from './ui/LoadingSpinner'
export { default as ErrorBoundary } from './ui/ErrorBoundary'
export { default as Toast } from './ui/Toast'
export { default as Badge } from './ui/Badge'

// HOOKS
export { default as useIndicators } from '../hooks/useIndicators'
export { default as useTheme } from '../hooks/useTheme'
export { default as useModal } from '../hooks/useModal'

// TYPES
export type {
  Indicator,
  Category,
  HistoricalData,
  ChartConfig,
  ModalConfig
} from '../types'

// ============================================================================
// frontend/src/types/index.ts
// Definiciones de tipos TypeScript

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

// ============================================================================
// frontend/src/config/categories.ts
// Configuración de categorías y colores

export const CATEGORIES: Record<string, Category> = {
  economia: {
    id: 'economia',
    title: '📊 Datos Económicos',
    description: 'IPC, PBI, desempleo, reservas, política monetaria y FX.',
    icon: '📊',
    indicators: ['ipc', 'pbi', 'emae', 'desempleo', 'reservas_bcra', 'dolar_blue'],
    color: 'blue'
  },
  gobierno: {
    id: 'gobierno', 
    title: '🏛️ Datos de Gobierno',
    description: 'Resultado fiscal, deuda pública, gasto gubernamental.',
    icon: '🏛️',
    indicators: ['resultado_fiscal', 'deuda_publica', 'gasto_publico', 'ingresos_tributarios', 'empleo_publico', 'transferencias_sociales'],
    color: 'purple'
  },
  finanzas: {
    id: 'finanzas',
    title: '🏦 Datos Financieros y Bancos', 
    description: 'Plazos fijos, tasas de crédito, depósitos, liquidez bancaria.',
    icon: '🏦',
    indicators: ['plazo_fijo_30', 'tasa_tarjeta_credito', 'depositos_privados', 'prestamos_sector_privado', 'morosidad_bancaria', 'liquidez_bancaria'],
    color: 'green'
  },
  mercados: {
    id: 'mercados',
    title: '📈 Datos de Mercados',
    description: 'MERVAL, bonos, acciones, CEDEARs, panel BYMA.',
    icon: '📈', 
    indicators: ['merval', 'rendimiento_al30', 'precio_gd30', 'volumen_acciones_cedears', 'dolar_ccl', 'panel_general_byma'],
    color: 'indigo'
  },
  tecnologia: {
    id: 'tecnologia',
    title: '💻 Tecnología y Software',
    description: 'Exportaciones SBC, empleo IT, inversión I+D, startups.',
    icon: '💻',
    indicators: ['exportaciones_sbc', 'empleo_it', 'inversion_id', 'penetracion_internet', 'vc_startups', 'facturacion_software'],
    color: 'cyan'
  },
  industria: {
    id: 'industria', 
    title: '🏭 Datos de Industria',
    description: 'IPI manufacturero, PMI, producción automotriz, acero.',
    icon: '🏭',
    indicators: ['ipi_manufacturero', 'pmi', 'produccion_automotriz', 'exportaciones_moi', 'produccion_acero', 'costo_construccion'],
    color: 'orange'
  }
}

export const COLOR_SCHEMES = {
  blue: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-900 dark:text-blue-100',
    accent: 'text-blue-600 dark:text-blue-400',
    button: 'bg-blue-600 hover:bg-blue-700'
  },
  purple: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    border: 'border-purple-200 dark:border-purple-800', 
    text: 'text-purple-900 dark:text-purple-100',
    accent: 'text-purple-600 dark:text-purple-400',
    button: 'bg-purple-600 hover:bg-purple-700'
  },
  green: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    border: 'border-green-200 dark:border-green-800',
    text: 'text-green-900 dark:text-green-100', 
    accent: 'text-green-600 dark:text-green-400',
    button: 'bg-green-600 hover:bg-green-700'
  },
  indigo: {
    bg: 'bg-indigo-50 dark:bg-indigo-900/20',
    border: 'border-indigo-200 dark:border-indigo-800',
    text: 'text-indigo-900 dark:text-indigo-100',
    accent: 'text-indigo-600 dark:text-indigo-400', 
    button: 'bg-indigo-600 hover:bg-indigo-700'
  },
  cyan: {
    bg: 'bg-cyan-50 dark:bg-cyan-900/20',
    border: 'border-cyan-200 dark:border-cyan-800',
    text: 'text-cyan-900 dark:text-cyan-100',
    accent: 'text-cyan-600 dark:text-cyan-400',
    button: 'bg-cyan-600 hover:bg-cyan-700'
  },
  orange: {
    bg: 'bg-orange-50 dark:bg-orange-900/20', 
    border: 'border-orange-200 dark:border-orange-800',
    text: 'text-orange-900 dark:text-orange-100',
    accent: 'text-orange-600 dark:text-orange-400',
    button: 'bg-orange-600 hover:bg-orange-700'
  }
}

// ============================================================================
// frontend/src/hooks/useIndicators.ts
// Hook principal para manejar datos de indicadores

import { useState, useEffect, useCallback } from 'react'
import { Indicator, DashboardData, APIResponse } from '../types'
import { apiClient } from '../lib/api'

export default function useIndicators() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchAllIndicators = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiClient.get<APIResponse<DashboardData>>('/dashboard/complete')
      
      if (response.data.status === 'success') {
        setData(response.data.data!)
        setLastUpdated(new Date())
      } else {
        setError(response.data.message || 'Error fetching data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching indicators:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const refreshData = useCallback(() => {
    fetchAllIndicators()
  }, [fetchAllIndicators])

  const getIndicatorsByCategory = useCallback((category: string): Indicator[] => {
    if (!data || !data[category as keyof DashboardData]) return []
    
    const categoryData = data[category as keyof DashboardData]
    return Object.entries(categoryData)
      .filter(([key]) => !['timestamp', 'category'].includes(key))
      .map(([id, indicatorData]) => ({
        id,
        ...(indicatorData as any),
        category
      }))
  }, [data])

  const getIndicatorById = useCallback((id: string): Indicator | null => {
    if (!data) return null
    
    for (const categoryData of Object.values(data)) {
      if (categoryData[id]) {
        return {
          id,
          ...(categoryData[id] as any)
        }
      }
    }
    return null
  }, [data])

  // Auto-refresh cada 5 minutos
  useEffect(() => {
    fetchAllIndicators()
    
    const interval = setInterval(fetchAllIndicators, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [fetchAllIndicators])

  return {
    data,
    loading,
    error,
    lastUpdated,
    refreshData,
    getIndicatorsByCategory,
    getIndicatorById,
    isDataFresh: lastUpdated && (Date.now() - lastUpdated.getTime()) < 300000 // 5 min
  }
}

// ============================================================================
// frontend/src/lib/api.ts
// Cliente API configurado

import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para logging
apiClient.interceptors.request.use((config) => {
  console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`)
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`)
    return Promise.reject(error)
  }
)

// Funciones específicas de API
export const api = {
  // Dashboard
  getDashboard: () => apiClient.get('/dashboard/complete'),
  
  // Categorías
  getCategory: (category: string) => apiClient.get(`/indicators/${category}`),
  
  // Indicadores individuales
  getIndicator: (id: string) => apiClient.get(`/indicators/${id}`),
  getHistorical: (id: string, days: number = 30) => 
    apiClient.get(`/indicators/${id}/historical?days=${days}`),
  
  // Búsqueda
  search: (query: string, category?: string) => 
    apiClient.get(`/indicators/search?q=${query}${category ? `&category=${category}` : ''}`),
  
  // Configuración
  getCategories: () => apiClient.get('/config/categories'),
  getConfig: () => apiClient.get('/config/indicators'),
  
  // Health
  getHealth: () => apiClient.get('/health/detailed'),
  getStats: () => apiClient.get('/stats'),
  
  // Actualización
  refresh: () => apiClient.post('/indicators/refresh'),
  refreshIndicator: (id: string) => apiClient.post(`/indicators/${id}/refresh`)
}

// ============================================================================
// frontend/src/utils/formatters.ts
// Utilidades para formatear datos

export const formatValue = (value: number | string, unit: string): string => {
  if (typeof value === 'string') return value

  switch (unit) {
    case 'percentage':
    case '%':
      return `${value.toFixed(1)}%`
    
    case 'usd_millions':
      return `US$${(value / 1000000).toFixed(1)}M`
    
    case 'usd_billions':
      return `US$${(value / 1000000000).toFixed(1)}B`
    
    case 'ars_billions':
      return `$${(value / 1000000000).toFixed(1)}B`
    
    case 'ars':
      return `$${value.toLocaleString()}`
    
    case 'usd':
      return `US$${value.toLocaleString()}`
    
    case 'thousands':
      return `${(value / 1000).toFixed(1)}K`
    
    case 'index':
      return value.toFixed(1)
    
    case 'count':
      return value.toLocaleString()
    
    default:
      return value.toLocaleString()
  }
}

export const formatChange = (change: number): { text: string; color: string; icon: string } => {
  const isPositive = change > 0
  const isNeutral = change === 0
  
  return {
    text: isNeutral ? '0%' : `${isPositive ? '+' : ''}${change.toFixed(1)}%`,
    color: isNeutral ? 'text-gray-500' : isPositive ? 'text-green-600' : 'text-red-600',
    icon: isNeutral ? '➡️' : isPositive ? '📈' : '📉'
  }
}

export const formatTimestamp = (timestamp: string): string => {
  return new Date(timestamp).toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

export const getSourceBadgeColor = (source: string): string => {
  const colors: Record<string, string> = {
    'BCRA': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'INDEC': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'BYMA': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    'MECON': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'DEMO': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }
  
  return colors[source] || colors['DEMO']
}

export const getFreshnessStatus = (lastUpdated: Date): {
  status: 'fresh' | 'recent' | 'stale'
  color: string
  text: string
} => {
  const minutes = Math.floor((Date.now() - lastUpdated.getTime()) / 60000)
  
  if (minutes < 5) {
    return { status: 'fresh', color: 'text-green-600', text: 'Datos frescos' }
  } else if (minutes < 30) {
    return { status: 'recent', color: 'text-yellow-600', text: 'Datos recientes' }
  } else {
    return { status: 'stale', color: 'text-red-600', text: 'Datos desactualizados' }
  }
}