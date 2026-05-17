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
          { "proName": "FOREXCOM:SPXUSD", "title": "S&P 500" },
          { "proName": "FOREXCOM:NSXUSD", "title": "NASDAQ" },
          { "proName": "FOREXCOM:DJI", "title": "Dow Jones" },
          { "proName": "FOREXCOM:UKXGBP", "title": "FTSE 100" },
          { "proName": "FOREXCOM:DEU40", "title": "DAX" },
          { "proName": "FX_IDC:EURUSD", "title": "EUR/USD" },
          { "proName": "FX_IDC:GBPUSD", "title": "GBP/USD" },
          { "proName": "FX_IDC:USDJPY", "title": "USD/JPY" },
          { "proName": "TVC:GOLD", "title": "Gold" },
          { "proName": "TVC:USOIL", "title": "Oil" },
          { "proName": "CBOT:ZS1!", "title": "Soybeans" },
          { "proName": "BITSTAMP:BTCUSD", "title": "Bitcoin" },
          { "proName": "BITSTAMP:ETHUSD", "title": "Ethereum" }
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
      console.error('Error loading International widget:', error)
      // Solo usar fallback si TradingView falla completamente
      container.innerHTML = `
        <div class="marquee-track marquee-left-fast">
          <div class="marquee-item">
            <span class="marquee-label">S&P 500</span>
            <span class="marquee-value">4,892.45</span>
            <span class="marquee-change positive">+1.2%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">NASDAQ</span>
            <span class="marquee-value">15,234.67</span>
            <span class="marquee-change positive">+0.8%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">EUR/USD</span>
            <span class="marquee-value">1.0845</span>
            <span class="marquee-change negative">-0.3%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">Gold</span>
            <span class="marquee-value">2,054.80</span>
            <span class="marquee-change positive">+0.5%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">Bitcoin</span>
            <span class="marquee-value">43,567</span>
            <span class="marquee-change positive">+2.1%</span>
          </div>
          <div class="marquee-separator"></div>
          <div class="marquee-item">
            <span class="marquee-label">Oil</span>
            <span class="marquee-value">78.45</span>
            <span class="marquee-change positive">+0.1%</span>
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
      <div className="tradingview-widget-container">
        <div ref={containerRef} className="tradingview-widget-container__widget"></div>
      </div>
    </div>
  )
}