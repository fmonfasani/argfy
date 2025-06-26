'use client'
import { useEffect, useRef } from 'react'

export default function TradingViewMarquee() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const container = containerRef.current
    if (!container) return

    // Limpiar contenido previo
    container.innerHTML = ''

    try {
      const script = document.createElement('script')
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js'
      script.async = true
      script.innerHTML = JSON.stringify({
        "symbols": [
          // Criptomonedas
          {
            "proName": "BITSTAMP:BTCUSD",
            "title": "Bitcoin"
          },
          {
            "proName": "BITSTAMP:ETHUSD", 
            "title": "Ethereum"
          },
          // Índices internacionales
          {
            "proName": "FOREXCOM:SPXUSD",
            "title": "S&P 500"
          },
          {
            "proName": "FOREXCOM:NSXUSD",
            "title": "NASDAQ 100"
          },
          // Forex
          {
            "proName": "FX_IDC:EURUSD",
            "title": "EUR/USD"
          },
          {
            "proName": "FX_IDC:USDARS",
            "title": "USD/ARS"
          },
          // Acciones argentinas (BYMA)
          {
            "proName": "BYMA:GGAL",
            "title": "Galicia"
          },
          {
            "proName": "BYMA:YPFD",
            "title": "YPF"
          },
          {
            "proName": "BYMA:PAMP",
            "title": "Pampa Energía"
          },
          // Commodities
          {
            "proName": "CBOT:ZS1!",
            "title": "Soja"
          },
          {
            "proName": "CBOT:ZW1!",
            "title": "Trigo"
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
      console.error('Error loading TradingView widget:', error)
      // Fallback content
      container.innerHTML = `
        <div class="bg-gray-100 p-4 text-center">
          <span class="text-sm text-gray-600">Datos de mercado no disponibles</span>
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
    <div className="bg-white border-b">
      <div className="text-center py-2">
        
      </div>
      <div className="tradingview-widget-container">
        <div ref={containerRef} className="tradingview-widget-container__widget min-h-[60px]"></div>
      </div>
    </div>
  )
}