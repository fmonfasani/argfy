// frontend/src/components/TradingViewMarquee.tsx
'use client'
import { useEffect } from 'react'

export default function TradingViewMarquee() {
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js'
    script.async = true
    script.innerHTML = JSON.stringify({
      symbols: [
        { proName: "FOREXCOM:SPXUSD", title: "S&P 500 Index" },
        { proName: "FOREXCOM:NSXUSD", title: "US 100 Cash CFD" },
        { proName: "FX_IDC:EURUSD", title: "EUR to USD" },
        { proName: "BITSTAMP:BTCUSD", title: "Bitcoin" },
        { proName: "BITSTAMP:ETHUSD", title: "Ethereum" },
        { proName: "BCBA:GGAL", title: "Grupo Galicia" },
        { proName: "BCBA:YPFD", title: "YPF" }
      ],
      colorTheme: "light",
      locale: "en",
      largeChartUrl: "",
      isTransparent: false,
      showSymbolLogo: true,
      displayMode: "adaptive"
    })

    const container = document.querySelector('.tradingview-widget-container__widget')
    if (container) {
      container.appendChild(script)
    }

    return () => {
      if (container && script.parentNode) {
        script.parentNode.removeChild(script)
      }
    }
  }, [])

  return (
    <div className="bg-white border-b">
      <div className="text-center py-2">
        <span className="text-sm text-gray-600 italic">Datos de mercado en tiempo real</span>
      </div>
      <div className="tradingview-widget-container">
        <div className="tradingview-widget-container__widget"></div>
      </div>
    </div>
  )
}

// frontend/src/components/SecondaryNav.tsx
'use client'
import { useState } from 'react'

export default function SecondaryNav() {
  const [activeTab, setActiveTab] = useState('US')

  const tabs = [
    'US', 'Products', 'Economic Insights', 'Money and Finance', 
    'Wall Street Live', 'Industry', 'Tech Trends', 'Reports', 'and Opinions'
  ]

  return (
    <div className="bg-slate-800 text-slate-300 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-8 py-3 overflow-x-auto">
          {tabs.map((tab) => (
            <div 
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`nav-tab px-3 py-1 rounded text-sm font-medium whitespace-nowrap cursor-pointer transition-all duration-200 hover:bg-slate-700 ${
                activeTab === tab ? 'bg-slate-100 text-slate-900' : ''
              }`}
            >
              {tab}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

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