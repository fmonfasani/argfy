'use client'
import { useState, useEffect } from 'react'

interface IndicatorData {
  indicator_type: string
  value: number
  source: string
  date: string
}

const cards = [
  { title: 'Dólar Blue', type: 'dolar_blue', fallback: 1047, color: 'text-emerald-400' },
  { title: 'Inflación Mensual', type: 'inflacion_mensual', fallback: 4.2, color: 'text-red-400' },
  { title: 'Reservas BCRA', type: 'reservas_bcra', fallback: 21500, color: 'text-slate-300' },
  { title: 'Riesgo País', type: 'riesgo_pais', fallback: 1642, color: 'text-amber-400' },
]

function getDisplay(type: string, value: number): string {
  switch (type) {
    case 'dolar_blue': case 'dolar_oficial': return `$${Math.round(value).toLocaleString()}`
    case 'inflacion_mensual': return `${value.toFixed(1)}%`
    case 'reservas_bcra': return `US$${(value / 1000).toFixed(1)}B`
    case 'riesgo_pais': return `${Math.round(value)} pb`
    case 'merval': return `${Math.round(value / 1000)}K`
    default: return value.toLocaleString()
  }
}

export default function EconomicDataCards() {
  const [indicators, setIndicators] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE}/indicators/current`)
      .then(r => r.json())
      .then(data => {
        const map: Record<string, number> = {}
        for (const i of data.data || []) map[i.indicator_type] = i.value
        setIndicators(map)
      })
      .catch(() => {
        setIndicators({ dolar_blue: 1047, inflacion_mensual: 4.2, reservas_bcra: 21500, riesgo_pais: 1642 })
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 animate-pulse">
            <div className="h-3 bg-slate-700 rounded mb-2 w-16" />
            <div className="h-6 bg-slate-700 rounded w-20" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map(card => {
        const value = indicators[card.type] ?? card.fallback
        return (
          <div key={card.type} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
            <p className="text-xs text-slate-500 mb-1">{card.title}</p>
            <p className={`text-xl font-bold ${card.color}`}>{getDisplay(card.type, value)}</p>
          </div>
        )
      })}
    </div>
  )
}
