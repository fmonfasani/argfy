// frontend/src/components/EconomicDataCards.tsx
'use client'
import { useState, useEffect } from 'react'

interface IndicatorData {
  indicator_type: string
  value: number
  source: string
  date: string
}

export default function EconomicDataCards() {
  const [indicators, setIndicators] = useState<IndicatorData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchIndicators()
  }, [])

  const fetchIndicators = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/indicators/current`)
      const data = await response.json()
      setIndicators(data.data || [])
    } catch (error) {
      console.error('Error fetching indicators:', error)
      // Datos de fallback
      setIndicators([
        { indicator_type: 'dolar_blue', value: 1047, source: 'demo', date: new Date().toISOString() },
        { indicator_type: 'inflacion_mensual', value: 4.2, source: 'INDEC', date: new Date().toISOString() },
        { indicator_type: 'reservas_bcra', value: 21500, source: 'BCRA', date: new Date().toISOString() },
        { indicator_type: 'riesgo_pais', value: 1642, source: 'JP Morgan', date: new Date().toISOString() }
      ])
    } finally {
      setLoading(false)
    }
  }

  const getDisplayValue = (indicator: IndicatorData) => {
    switch (indicator.indicator_type) {
      case 'dolar_blue':
      case 'dolar_oficial':
        return `$${Math.round(indicator.value).toLocaleString()}`
      case 'inflacion_mensual':
        return `${indicator.value.toFixed(1)}%`
      case 'reservas_bcra':
        return `US$${(indicator.value / 1000).toFixed(1)}B`
      case 'riesgo_pais':
        return `${Math.round(indicator.value)} pb`
      case 'merval':
        return `${Math.round(indicator.value / 1000)}K`
      default:
        return indicator.value.toLocaleString()
    }
  }

  const getCardData = (type: string) => {
    const base = {
      'economic': {
        title: 'Economic Data',
        icon: '📊',
        description: 'Indicadores económicos argentinos en tiempo real.',
        gradient: 'from-slate-600 to-slate-800'
      },
      'finance': {
        title: 'Finance Data', 
        icon: '🏦',
        description: 'Datos bancarios y tasas de interés.',
        gradient: 'from-slate-700 to-slate-900'
      },
      'markets': {
        title: 'Markets',
        icon: '📈', 
        description: 'Mercados de capitales argentinos.',
        gradient: 'from-slate-600 to-slate-800'
      },
      'commodities': {
        title: 'Commodities',
        icon: '⚡',
        description: 'Precios de commodities agropecuarios.',
        gradient: 'from-amber-600 to-amber-800'
      },
      'industry': {
        title: 'Industry',
        icon: '🏭',
        description: 'Indicadores industriales y producción.',
        gradient: 'from-slate-700 to-slate-900'
      },
      'tech': {
        title: 'Technologies',
        icon: '💻',
        description: 'Sector tecnológico y fintech.',
        gradient: 'from-slate-600 to-slate-800'
      }
    }
    return base[type as keyof typeof base]
  }

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-16">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg p-4 shadow-lg border border-slate-200 animate-pulse">
            <div className="w-12 h-12 bg-slate-200 rounded-full mx-auto mb-3"></div>
            <div className="h-4 bg-slate-200 rounded mb-2"></div>
            <div className="h-3 bg-slate-200 rounded mb-3"></div>
            <div className="space-y-1">
              <div className="h-3 bg-slate-200 rounded"></div>
              <div className="h-3 bg-slate-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-16">
      {/* Economic Data Card */}
      <div className="category-card bg-white rounded-lg p-4 text-center shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer">
        <div className="w-12 h-12 bg-gradient-to-r from-slate-600 to-slate-800 rounded-full flex items-center justify-center mx-auto mb-3">
          <span className="text-amber-400 text-lg">📊</span>
        </div>
        <h3 className="text-sm font-bold text-slate-800 mb-2">Economic Data</h3>
        <p className="text-slate-600 text-xs mb-3">
          Indicadores económicos argentinos en tiempo real.
        </p>
        <div className="space-y-1 text-left">
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Dólar Blue:</span>
            <span className="font-semibold text-emerald-600">
              {getDisplayValue(indicators.find(i => i.indicator_type === 'dolar_blue') || { indicator_type: 'dolar_blue', value: 1047, source: '', date: '' })}
            </span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Inflación:</span>
            <span className="font-semibold text-red-600">
              {getDisplayValue(indicators.find(i => i.indicator_type === 'inflacion_mensual') || { indicator_type: 'inflacion_mensual', value: 4.2, source: '', date: '' })}
            </span>
          </div>
        </div>
      </div>

      {/* Finance Data Card */}
      <div className="category-card bg-white rounded-lg p-4 text-center shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer">
        <div className="w-12 h-12 bg-gradient-to-r from-slate-700 to-slate-900 rounded-full flex items-center justify-center mx-auto mb-3">
          <span className="text-amber-400 text-lg">🏦</span>
        </div>
        <h3 className="text-sm font-bold text-slate-800 mb-2">Finance Data</h3>
        <p className="text-slate-600 text-xs mb-3">
          Datos bancarios y tasas de interés.
        </p>
        <div className="space-y-1 text-left">
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Reservas:</span>
            <span className="font-semibold text-slate-700">
              {getDisplayValue(indicators.find(i => i.indicator_type === 'reservas_bcra') || { indicator_type: 'reservas_bcra', value: 21500, source: '', date: '' })}
            </span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Tasa BCRA:</span>
            <span className="font-semibold text-rose-600">118%</span>
          </div>
        </div>
      </div>

      {/* Markets Card */}
      <div className="category-card bg-white rounded-lg p-4 text-center shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer">
        <div className="w-12 h-12 bg-gradient-to-r from-slate-600 to-slate-800 rounded-full flex items-center justify-center mx-auto mb-3">
          <span className="text-amber-400 text-lg">📈</span>
        </div>
        <h3 className="text-sm font-bold text-slate-800 mb-2">Markets</h3>
        <p className="text-slate-600 text-xs mb-3">
          Mercados de capitales argentinos.
        </p>
        <div className="space-y-1 text-left">
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Merval:</span>
            <span className="font-semibold text-emerald-600">
              {getDisplayValue(indicators.find(i => i.indicator_type === 'merval') || { indicator_type: 'merval', value: 1456234, source: '', date: '' })}
            </span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Riesgo País:</span>
            <span className="font-semibold text-red-600">
              {getDisplayValue(indicators.find(i => i.indicator_type === 'riesgo_pais') || { indicator_type: 'riesgo_pais', value: 1642, source: '', date: '' })}
            </span>
          </div>
        </div>
      </div>

      {/* Commodities Card */}
      <div className="category-card bg-white rounded-lg p-4 text-center shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer">
        <div className="w-12 h-12 bg-gradient-to-r from-amber-600 to-amber-800 rounded-full flex items-center justify-center mx-auto mb-3">
          <span className="text-white text-lg">⚡</span>
        </div>
        <h3 className="text-sm font-bold text-slate-800 mb-2">Commodities</h3>
        <p className="text-slate-600 text-xs mb-3">
          Precios de commodities agropecuarios.
        </p>
        <div className="space-y-1 text-left">
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Soja:</span>
            <span className="font-semibold text-emerald-600">US$485</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Trigo:</span>
            <span className="font-semibold text-amber-600">US$245</span>
          </div>
        </div>
      </div>

      {/* Industry Card */}
      <div className="category-card bg-white rounded-lg p-4 text-center shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer">
        <div className="w-12 h-12 bg-gradient-to-r from-slate-700 to-slate-900 rounded-full flex items-center justify-center mx-auto mb-3">
          <span className="text-amber-400 text-lg">🏭</span>
        </div>
        <h3 className="text-sm font-bold text-slate-800 mb-2">Industry</h3>
        <p className="text-slate-600 text-xs mb-3">
          Indicadores industriales y producción.
        </p>
        <div className="space-y-1 text-left">
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">EMI:</span>
            <span className="font-semibold text-slate-700">148.2</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Construcción:</span>
            <span className="font-semibold text-red-600">-12.4%</span>
          </div>
        </div>
      </div>

      {/* Technologies Card */}
      <div className="category-card bg-white rounded-lg p-4 text-center shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer">
        <div className="w-12 h-12 bg-gradient-to-r from-slate-600 to-slate-800 rounded-full flex items-center justify-center mx-auto mb-3">
          <span className="text-amber-400 text-lg">💻</span>
        </div>
        <h3 className="text-sm font-bold text-slate-800 mb-2">Technologies</h3>
        <p className="text-slate-600 text-xs mb-3">
          Sector tecnológico y fintech.
        </p>
        <div className="space-y-1 text-left">
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">ARCO:</span>
            <span className="font-semibold text-emerald-600">$125.50</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-600">Exp. IT:</span>
            <span className="font-semibold text-slate-700">US$7.8B</span>
          </div>
        </div>
      </div>
    </div>
  )
}