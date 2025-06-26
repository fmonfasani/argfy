'use client'
import { useEffect, useRef } from 'react'

export default function InternationalMarquee() {
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
          // Índices Principales
          { "proName": "FOREXCOM:SPXUSD", "title": "S&P 500" },
          { "proName": "FOREXCOM:NSXUSD", "title": "NASDAQ 100" },
          { "proName": "FOREXCOM:DJI", "title": "Dow Jones" },
          { "proName": "FOREXCOM:UKXGBP", "title": "FTSE 100" },
          { "proName": "FOREXCOM:DAXEUR", "title": "DAX" },
          { "proName": "FOREXCOM:FRXEUR", "title": "CAC 40" },
          // Forex
          { "proName": "FX_IDC:EURUSD", "title": "EUR/USD" },
          { "proName": "FX_IDC:GBPUSD", "title": "GBP/USD" },
          { "proName": "FX_IDC:USDJPY", "title": "USD/JPY" },
          // Commodities
          { "proName": "COMEX:GC1!", "title": "Oro" },
          { "proName": "NYMEX:CL1!", "title": "Petróleo WTI" },
          { "proName": "CBOT:ZS1!", "title": "Soja" },
          // Crypto
          { "proName": "BITSTAMP:BTCUSD", "title": "Bitcoin" },
          { "proName": "BITSTAMP:ETHUSD", "title": "Ethereum" }
        ],
        "isTransparent": true,
        "colorTheme": "light",
     })

      container.appendChild(script)
    } catch (error) {
      console.error('Error loading International widget:', error)
      container.innerHTML = `
        <div class="bg-green-50 p-2 text-center">
          <span class="text-xs text-green-700">🌍 Mercados Internacionales • Forex • Commodities</span>
        </div>
      `
    }

    return () => {
      if (container) container.innerHTML = ''
    }
  }, [])

  return (
    <div className="bg-slate-50 border-b border-slate-200">
      <div className="tradingview-widget-container marquee-left">
        <div ref={containerRef} className="tradingview-widget-container__widget min-h-[40px]"></div>
      </div>
    </div>
  )
}