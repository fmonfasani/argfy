'use client'
import { useEffect, useRef } from 'react'

export default function GlobalMarquee() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const container = containerRef.current
    if (!container) return

    container.innerHTML = ''

    try {
      const script = document.createElement('script')
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js'
      script.async = true
      script.innerHTML = JSON.stringify({
        "symbols": [
          // Índices Mundiales
          {
            "proName": "FOREXCOM:SPXUSD",
            "title": "S&P 500"
          },
          {
            "proName": "FOREXCOM:NSXUSD", 
            "title": "NASDAQ 100"
          },
          {
            "proName": "FOREXCOM:DJI",
            "title": "Dow Jones"
          },
          {
            "proName": "FOREXCOM:UKXGBP",
            "title": "FTSE 100"
          },
          {
            "proName": "FOREXCOM:FRXEUR",
            "title": "CAC 40"
          },
          {
            "proName": "FOREXCOM:DAXEUR", 
            "title": "DAX"
          },
          // Forex Principales
          {
            "proName": "FX_IDC:EURUSD",
            "title": "EUR/USD"
          },
          {
            "proName": "FX_IDC:GBPUSD",
            "title": "GBP/USD"
          },
          {
            "proName": "FX_IDC:USDJPY",
            "title": "USD/JPY"
          },
          {
            "proName": "FX_IDC:USDCHF",
            "title": "USD/CHF"
          },
          // Commodities
          {
            "proName": "COMEX:GC1!",
            "title": "Oro"
          },
          {
            "proName": "COMEX:SI1!",
            "title": "Plata"
          },
          {
            "proName": "NYMEX:CL1!",
            "title": "Petróleo WTI"
          },
          {
            "proName": "NYMEX:NG1!",
            "title": "Gas Natural"
          },
          {
            "proName": "CBOT:ZS1!",
            "title": "Soja"
          },
          {
            "proName": "CBOT:ZW1!",
            "title": "Trigo"
          },
          {
            "proName": "CBOT:ZC1!",
            "title": "Maíz"
          },
          // Crypto
          {
            "proName": "BITSTAMP:BTCUSD",
            "title": "Bitcoin"
          },
          {
            "proName": "BITSTAMP:ETHUSD",
            "title": "Ethereum"
          }
        ],
        "showSymbolLogo": true,
        "isTransparent": false,
        "displayMode": "adaptive",
        "colorTheme": "light",
        "locale": "es"
      })

      container.appendChild(script)
    } catch (error) {
      console.error('Error loading Global TradingView widget:', error)
      container.innerHTML = `
        <div class="bg-blue-50 p-2 text-center">
          <span class="text-xs text-blue-600">Mercados Globales • Forex • Commodities</span>
        </div>
      `
    }

    return () => {
      if (container) {
        container.innerHTML = ''
      }
    }
  }, [])

  return (
    <div className="bg-slate-100 border-b border-slate-200">
      <div className="tradingview-widget-container">
        <div ref={containerRef} className="tradingview-widget-container__widget min-h-[50px]"></div>
      </div>
    </div>
  )
}