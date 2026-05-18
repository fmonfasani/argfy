'use client'
import { useState, useEffect, useRef } from 'react'

interface MarqueeItem {
  name: string
  value: number
  change: string
  color: 'positive' | 'negative'
  prefix?: string
  suffix?: string
}

interface TradingViewSymbol {
  proName: string
  title: string
}

interface MarqueeConfig {
  colorTheme: 'celeste' | 'blanco'
  animationClass: string
  useTradingView: boolean
  tradingViewSymbols?: TradingViewSymbol[]
  staticData?: MarqueeItem[]
  tradingViewTitle?: string
}

interface MarqueeBarProps {
  variant: 'international' | 'economic' | 'stocks' | 'combined'
}

const ECONOMIC_DATA: MarqueeItem[] = [
  { name: "USD Oficial", value: 987.50, change: "+0.8%", color: "positive" },
  { name: "USD Blue", value: 1047.00, change: "+2.3%", color: "positive" },
  { name: "USD MEP", value: 1023.75, change: "-0.5%", color: "negative" },
  { name: "Riesgo País", value: 1642, change: "-15 pb", color: "negative", suffix: " pb" },
  { name: "Tasa BCRA", value: 118.0, change: "+0.2%", color: "positive", suffix: "%" },
  { name: "Reservas BCRA", value: 21.5, change: "+1.2%", color: "positive", prefix: "US$", suffix: "B" },
  { name: "Inflación", value: 4.2, change: "-0.3%", color: "negative", suffix: "%" },
  { name: "EMAE", value: 148.2, change: "+1.4%", color: "positive" },
  { name: "AL30", value: 68.50, change: "-2.1%", color: "negative", prefix: "$" },
  { name: "GD30", value: 1245, change: "+1.5%", color: "positive", prefix: "$" },
]

const CONFIGS: Record<MarqueeBarProps['variant'], MarqueeConfig> = {
  combined: {
    colorTheme: 'celeste',
    animationClass: 'marquee-left-fast',
    useTradingView: true,
    tradingViewTitle: 'Mercados',
    tradingViewSymbols: [
      { proName: "FOREXCOM:SPXUSD", title: "S&P 500" },
      { proName: "FOREXCOM:NSXUSD", title: "NASDAQ" },
      { proName: "FOREXCOM:DJI", title: "Dow Jones" },
      { proName: "FX_IDC:EURUSD", title: "EUR/USD" },
      { proName: "FX_IDC:USDARS", title: "USD/ARS" },
      { proName: "TVC:GOLD", title: "Gold" },
      { proName: "TVC:USOIL", title: "Oil" },
      { proName: "CBOT:ZS1!", title: "Soybeans" },
      { proName: "BITSTAMP:BTCUSD", title: "Bitcoin" },
      { proName: "BYMA:GGAL", title: "GGAL" },
      { proName: "BYMA:YPFD", title: "YPF" },
      { proName: "BYMA:PAMP", title: "PAMP" },
      { proName: "NASDAQ:GGAL", title: "GGAL ADR" },
      { proName: "NYSE:YPF", title: "YPF ADR" },
      { proName: "NASDAQ:MELI", title: "MELI" },
    ],
  },
  international: {
    colorTheme: 'celeste',
    animationClass: 'marquee-left-fast',
    useTradingView: true,
    tradingViewTitle: 'Mercados Globales',
    tradingViewSymbols: [
      { proName: "FOREXCOM:SPXUSD", title: "S&P 500" },
      { proName: "FOREXCOM:NSXUSD", title: "NASDAQ" },
      { proName: "FOREXCOM:DJI", title: "Dow Jones" },
      { proName: "FOREXCOM:UKXGBP", title: "FTSE 100" },
      { proName: "FOREXCOM:DEU40", title: "DAX" },
      { proName: "FX_IDC:EURUSD", title: "EUR/USD" },
      { proName: "FX_IDC:GBPUSD", title: "GBP/USD" },
      { proName: "FX_IDC:USDJPY", title: "USD/JPY" },
      { proName: "TVC:GOLD", title: "Gold" },
      { proName: "TVC:USOIL", title: "Oil" },
      { proName: "CBOT:ZS1!", title: "Soybeans" },
      { proName: "BITSTAMP:BTCUSD", title: "Bitcoin" },
      { proName: "BITSTAMP:ETHUSD", title: "Ethereum" },
    ],
  },
  economic: {
    colorTheme: 'blanco',
    animationClass: 'marquee-right-normal',
    useTradingView: false,
    staticData: ECONOMIC_DATA,
  },
  stocks: {
    colorTheme: 'celeste',
    animationClass: 'marquee-left-slow',
    useTradingView: true,
    tradingViewTitle: 'Acciones Argentinas',
    tradingViewSymbols: [
      { proName: "BYMA:IMV", title: "MERVAL" },
      { proName: "BYMA:GGAL", title: "GGAL" },
      { proName: "BYMA:YPFD", title: "YPF" },
      { proName: "BYMA:PAMP", title: "PAMP" },
      { proName: "BYMA:TXAR", title: "TXAR" },
      { proName: "BYMA:ALUA", title: "ALUA" },
      { proName: "BYMA:COME", title: "COME" },
      { proName: "BYMA:TECO2", title: "TECO2" },
      { proName: "BYMA:MIRG", title: "MIRG" },
      { proName: "NASDAQ:GGAL", title: "GGAL ADR" },
      { proName: "NYSE:YPF", title: "YPF ADR" },
      { proName: "NYSE:PAM", title: "PAM ADR" },
      { proName: "NYSE:TEO", title: "TEO ADR" },
      { proName: "NASDAQ:MELI", title: "MELI" },
      { proName: "NASDAQ:GLOB", title: "GLOB" },
    ],
  },
}

const TV_FALLBACK: Record<string, MarqueeItem[]> = {
  international: [
    { name: "S&P 500", value: 4892.45, change: "+1.2%", color: "positive" },
    { name: "NASDAQ", value: 15234.67, change: "+0.8%", color: "positive" },
    { name: "EUR/USD", value: 1.0845, change: "-0.3%", color: "negative" },
    { name: "Gold", value: 2054.80, change: "+0.5%", color: "positive" },
    { name: "Bitcoin", value: 43567, change: "+2.1%", color: "positive" },
    { name: "Oil", value: 78.45, change: "+0.1%", color: "positive" },
  ],
  stocks: [
    { name: "MERVAL", value: 1456234, change: "+2.1%", color: "positive" },
    { name: "GGAL", value: 2847, change: "+3.2%", color: "positive" },
    { name: "YPFD", value: 12450, change: "+1.8%", color: "positive" },
    { name: "PAMP", value: 8920, change: "-0.5%", color: "negative" },
    { name: "GGAL ADR", value: 28.45, change: "+4.1%", color: "positive" },
    { name: "YPF ADR", value: 14.78, change: "-1.2%", color: "negative" },
    { name: "MELI", value: 1234.56, change: "+3.4%", color: "positive" },
    { name: "GLOB", value: 187.92, change: "+1.7%", color: "positive" },
  ],
}

function TradingViewWidget({ config }: { config: MarqueeConfig }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const container = containerRef.current
    if (!container) return

    container.innerHTML = ''
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js'
    script.async = true
    script.innerHTML = JSON.stringify({
      symbols: config.tradingViewSymbols,
      showSymbolLogo: false,
      isTransparent: true,
      displayMode: "adaptive",
      colorTheme: "light",
      locale: "en",
    })

    container.appendChild(script)

    return () => {
      if (container) container.innerHTML = ''
    }
  }, [config])

  return (
    <div className="tradingview-widget-container">
      <div ref={containerRef} className="tradingview-widget-container__widget"></div>
    </div>
  )
}

function StaticMarquee({ config }: { config: MarqueeConfig }) {
  const [data, setData] = useState(config.staticData || [])

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => prev.map(item => {
        const variation = (Math.random() - 0.5) * (item.value * 0.001)
        return { ...item, value: Math.max(0, item.value + variation) }
      }))
    }, 45000)
    return () => clearInterval(interval)
  }, [])

  const triplicated = [...data, ...data, ...data]

  return (
    <div className="overflow-hidden">
      <div className={`marquee-track ${config.animationClass}`}>
        {triplicated.map((item, i) => (
          <div key={i} className="inline-flex items-center">
            <div className="marquee-item">
              <span className="marquee-label">{item.name}</span>
              <span className="marquee-value">
                {item.prefix || ""}{typeof item.value === 'number' ? item.value.toFixed(2) : item.value}{item.suffix || ""}
              </span>
              <span className={`marquee-change ${item.color}`}>{item.change}</span>
            </div>
            {i < triplicated.length - 1 && <div className="marquee-separator"></div>}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function MarqueeBar({ variant }: MarqueeBarProps) {
  const config = CONFIGS[variant]

  return (
    <div className={`marquee-container marquee-${config.colorTheme}`}>
      {config.useTradingView ? (
        <TradingViewWidget config={config} />
      ) : (
        <StaticMarquee config={config} />
      )}
    </div>
  )
}
