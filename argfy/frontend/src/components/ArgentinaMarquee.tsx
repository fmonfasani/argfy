'use client'
import { useEffect, useRef } from 'react'

export default function ArgentinaMarquee() {
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
          // Dólares Argentinos
          {
            "proName": "FX_IDC:USDARS",
            "title": "USD/ARS Oficial"
          },
          // Acciones Argentinas en BYMA
          {
            "proName": "BYMA:GGAL",
            "title": "Galicia"
          },
          {
            "proName": "BYMA:YPF", 
            "title": "YPF"
          },
          {
            "proName": "BYMA:PAMP",
            "title": "Pampa Energía"
          },
          {
            "proName": "BYMA:TXAR",
            "title": "Ternium"
          },
          {
            "proName": "BYMA:ALUA",
            "title": "Aluar"
          },
          {
            "proName": "BYMA:COME",
            "title": "Comes"
          },
          {
            "proName": "BYMA:CRES",
            "title": "Cresud"
          },
          {
            "proName": "BYMA:MIRG",
            "title": "Mirgor"
          },
          // Índice MERVAL
          {
            "proName": "BYMA:IMV",
            "title": "MERVAL"
          },
          // ADRs Argentinos en NYSE
          {
            "proName": "NYSE:GGAL",
            "title": "Galicia ADR"
          },
          {
            "proName": "NYSE:YPF",
            "title": "YPF ADR"
          },
          {
            "proName": "NYSE:PAM",
            "title": "Pampa ADR"
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
      console.error('Error loading Argentina TradingView widget:', error)
      container.innerHTML = `
        <div class="bg-blue-50 p-3 text-center">
          <span class="text-sm text-blue-700">🇦🇷 Mercado Argentino • Dólares • Acciones BYMA • ADRs</span>
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
    <div className="bg-white border-b border-slate-200">
      <div className="text-center py-1 bg-slate-50">
        <span className="text-xs text-slate-600">🇦🇷 Mercado Argentino</span>
      </div>
      <div className="tradingview-widget-container">
        <div ref={containerRef} className="tradingview-widget-container__widget min-h-[60px]"></div>
      </div>
    </div>
  )
}