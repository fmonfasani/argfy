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
          { "proName": "BYMA:IMV", "title": "MERVAL" },
          { "proName": "BYMA:GGAL", "title": "GGAL" },
          { "proName": "BYMA:YPFD", "title": "YPF" },
          { "proName": "BYMA:PAMP", "title": "PAMP" },
          { "proName": "BYMA:TXAR", "title": "TXAR" },
          { "proName": "BYMA:ALUA", "title": "ALUA" },
          { "proName": "BYMA:COME", "title": "COME" },
          { "proName": "BYMA:TECO2", "title": "TECO2" },
          { "proName": "BYMA:MIRG", "title": "MIRG" },
          { "proName": "NASDAQ:GGAL", "title": "GGAL ADR" },
          { "proName": "NYSE:YPF", "title": "YPF ADR" },
          { "proName": "NYSE:PAM", "title": "PAM ADR" },
          { "proName": "NYSE:TEO", "title": "TEO ADR" },
          { "proName": "NASDAQ:MELI", "title": "MELI" },
          { "proName": "NASDAQ:GLOB", "title": "GLOB" }
        ],
        "showSymbolLogo": false,
        "isTransparent": true,
        "displayMode": "adaptive",
        "colorTheme": "light",
        "locale": "en",
        "largeChartUrl": ""
      })

      container.appendChild(script)
    } catch (error) {
      console.error('Error loading Argentine Stocks widget:', error)
      // Solo usar fallback si TradingView falla completamente
      container.innerHTML = `
        <div class="marquee-track marquee-left-slow">
          <div class="marquee-item">
            <span class="marquee-label">MERVAL</span>
            <span class="marquee-value">1,456,234</span>
            <span class="marquee-change positive">+2.1%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">GGAL</span>
            <span class="marquee-value">2,847</span>
            <span class="marquee-change positive">+3.2%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">YPFD</span>
            <span class="marquee-value">12,450</span>
            <span class="marquee-change positive">+1.8%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">PAMP</span>
            <span class="marquee-value">8,920</span>
            <span class="marquee-change negative">-0.5%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">GGAL ADR</span>
            <span class="marquee-value">28.45</span>
            <span class="marquee-change positive">+4.1%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">YPF ADR</span>
            <span class="marquee-value">14.78</span>
            <span class="marquee-change negative">-1.2%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">MELI</span>
            <span class="marquee-value">1,234.56</span>
            <span class="marquee-change positive">+3.4%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">GLOB</span>
            <span class="marquee-value">187.92</span>
            <span class="marquee-change positive">+1.7%</span>
          </div>
        </div>
      `
    }

    return () => {
      if (container) container.innerHTML = ''
    }
  }, [])

  return (
    <div className="marquee-container marquee-celeste">
      <div className="tradingview-widget-container ">
        <div ref={containerRef} className="tradingview-widget-container__widget"></div>
      </div>
    </div>
  )
}