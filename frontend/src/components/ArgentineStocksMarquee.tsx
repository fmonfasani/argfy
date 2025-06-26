'use client'
import { useEffect, useRef } from 'react'

export default function ArgentineStocksMarquee() {
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
          // Índice MERVAL
          { "proName": "BYMA:IMV", "title": "MERVAL" },
          // Acciones BYMA
          { "proName": "BYMA:GGAL", "title": "Galicia" },
          { "proName": "BYMA:YPFD", "title": "YPF" },
          { "proName": "BYMA:PAMP", "title": "Pampa Energía" },
          { "proName": "BYMA:TXAR", "title": "Ternium" },
          { "proName": "BYMA:ALUA", "title": "Aluar" },
          { "proName": "BYMA:COME", "title": "Comes" },
          { "proName": "BYMA:CRES", "title": "Cresud" },
          { "proName": "BYMA:MIRG", "title": "Mirgor" },
          { "proName": "BYMA:TECO2", "title": "Telecom" },
          // ADRs en NYSE
          { "proName": "NYSE:GGAL", "title": "Galicia ADR" },
          { "proName": "NYSE:YPF", "title": "YPF ADR" },
          { "proName": "NYSE:PAM", "title": "Pampa ADR" },
          { "proName": "NYSE:TEO", "title": "Telecom ADR" }
        ],
        "isTransparent": true,
        "colorTheme": "light"
        
      })

      container.appendChild(script)
    } catch (error) {
      console.error('Error loading Argentine Stocks widget:', error)
      container.innerHTML = `
        <div class="bg-green-50 p-2 text-center marquee-left">
          <span class="text-xs text-green-700">🇦🇷 Acciones Argentinas • BYMA • ADRs</span>
        </div>
      `
    }

    return () => {
      if (container) container.innerHTML = ''
    }
  }, [])

  return (
    <div className="bg-green-50 border-b border-green-200">
      <div className="tradingview-widget-container ">
        <div ref={containerRef} className="tradingview-widget-container__widget min-h-[40px]"></div>
      </div>
    </div>
  )
}