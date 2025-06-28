// frontend/src/lib/utils.ts - Modificar funciones de formato


import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
export function formatNumber(value: number, withSeparator: boolean = false): string {
  if (withSeparator) {
    return new Intl.NumberFormat('es-AR').format(value)
  } else {
    // Sin separador de miles
    return value.toString()
  }
}
export function formatCurrency(value: number, currency: string = 'ARS', showSymbol: boolean = false): string {
  if (showSymbol) {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value)
  } else {
    // Solo el número sin símbolo
    return value.toFixed(2)
  }
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
export function getIndicatorDisplayValue(indicator: any, simple: boolean = false): string {
  if (simple) {
    // Formato simple sin separadores ni símbolos
    switch (indicator.indicator_type) {
      case 'dolar_blue':
      case 'dolar_oficial':
      case 'dolar_mep':
        return Math.round(indicator.value).toString()
      case 'inflacion_mensual':
        return indicator.value.toFixed(1)
      case 'reservas_bcra':
        return (indicator.value / 1000).toFixed(1)
      case 'riesgo_pais':
        return Math.round(indicator.value).toString()
      case 'merval':
        return Math.round(indicator.value).toString()
      default:
        return indicator.value.toString()
    }
  } 
}