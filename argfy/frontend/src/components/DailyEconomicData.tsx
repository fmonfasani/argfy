// frontend/src/components/DailyEconomicData.tsx
'use client'
import { useState, useEffect } from 'react'

interface EconomicData {
  title: string
  value: string
  change: string
  changeType: 'positive' | 'negative' | 'neutral'
  description: string
  icon: string
}

export default function DailyEconomicData() {
  const [data, setData] = useState<EconomicData[]>([])

  useEffect(() => {
    // Datos de demo
    setData([
      {
        title: 'Dólar BNA',
        value: '$987.50',
        change: '+0.8% vs ayer',
        changeType: 'positive',
        description: 'Cotización oficial',
        icon: '🏛️'
      },
      {
        title: 'Dólar Blue',
        value: '$1,047.00',
        change: '+2.3% vs ayer',
        changeType: 'positive',
        description: 'Mercado informal',
        icon: '💵'
      },
      {
        title: 'Dólar MEP',
        value: '$1,023.75',
        change: '-0.5% vs ayer',
        changeType: 'negative',
        description: 'Mercado de valores',
        icon: '📊'
      },
      {
        title: 'Reservas BCRA',
        value: 'US$21.5B',
        change: '+1.2% vs semana',
        changeType: 'positive',
        description: 'Reservas internacionales',
        icon: '🏦'
      },
      {
        title: 'Riesgo País',
        value: '1,642 pb',
        change: '-3.1% vs ayer',
        changeType: 'negative',
        description: 'Índice JP Morgan',
        icon: '📈'
      },
      {
        title: 'Tasa BCRA',
        value: '118.0%',
        change: 'Sin cambios',
        changeType: 'neutral',
        description: 'Tasa de referencia',
        icon: '📊'
      }
    ])
  }, [])

  const getChangeColor = (type: 'positive' | 'negative' | 'neutral') => {
    switch (type) {
      case 'positive': return 'text-emerald-600'
      case 'negative': return 'text-red-600'
      default: return 'text-slate-600'
    }
  }

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">
            💰 Datos Importantes de la Vida Cotidiana
          </h2>
          <p className="text-lg text-slate-600">
            Indicadores económicos que impactan tu día a día
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.map((item, index) => (
            <div key={index} className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow duration-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-800">{item.title}</h3>
                <span className="text-2xl">{item.icon}</span>
              </div>
              <div className="text-2xl font-bold text-slate-700 mb-2">{item.value}</div>
              <div className={`text-sm font-medium ${getChangeColor(item.changeType)}`}>
                {item.change}
              </div>
              <div className="text-xs text-slate-500 mt-1">{item.description}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}