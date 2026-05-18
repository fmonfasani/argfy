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

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg p-4 shadow-lg border border-slate-200 animate-pulse">
            <div className="h-4 bg-slate-200 rounded mb-2"></div>
            <div className="h-6 bg-slate-200 rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  const cards = [
    {
      title: 'Dólar Blue',
      type: 'dolar_blue',
      fallback: { indicator_type: 'dolar_blue', value: 1047, source: '', date: '' },
      valueColor: 'text-emerald-600',
      source: 'BCRA',
    },
    {
      title: 'Inflación Mensual',
      type: 'inflacion_mensual',
      fallback: { indicator_type: 'inflacion_mensual', value: 4.2, source: '', date: '' },
      valueColor: 'text-red-600',
      source: 'INDEC',
    },
    {
      title: 'Reservas BCRA',
      type: 'reservas_bcra',
      fallback: { indicator_type: 'reservas_bcra', value: 21500, source: '', date: '' },
      valueColor: 'text-slate-700',
      source: 'BCRA',
    },
    {
      title: 'Riesgo País',
      type: 'riesgo_pais',
      fallback: { indicator_type: 'riesgo_pais', value: 1642, source: '', date: '' },
      valueColor: 'text-red-600',
      source: 'JP Morgan',
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
      {cards.map((card) => {
        const data = indicators.find(i => i.indicator_type === card.type) || card.fallback
        return (
          <div key={card.type} className="bg-white rounded-lg p-4 shadow-lg border border-slate-200">
            <p className="text-xs text-slate-500 mb-1">{card.title}</p>
            <p className={`text-xl font-bold ${card.valueColor}`}>
              {getDisplayValue(data)}
            </p>
            <p className="text-xs text-slate-400 mt-1">{card.source}</p>
          </div>
        )
      })}
    </div>
  )
}
