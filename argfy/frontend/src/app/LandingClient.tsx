'use client'

import Link from 'next/link'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import type { RatioSnapshot, TickerDetail } from '@/lib/types'
import type { LandingData } from '@/lib/landing-data'

const NAV_LINKS = [
  { label: 'Producto', href: '#producto' },
  { label: 'Precios', href: '/pricing' },
  { label: 'API', href: '/api' },
  { label: 'Recursos', href: '#recursos' },
  { label: 'Blog', href: '#blog' },
]

const FEATURE_TAGS = [
  'Screener de CEDEARs y BYMA',
  'PER, ROE, márgenes, deuda',
  'Datos de SEC/EDGAR',
  'Histórico trimestral',
  'API REST',
  'Sin tarjeta de crédito',
]

const TESTIMONIALS = [
  {
    quote:
      'Argfy me ahorra horas todas las semanas. Antes armaba el screener a mano en planillas, ahora filtro 200 CEDEARs en segundos.',
    author: 'Lautaro M.',
    role: 'Analista buy-side · Buenos Aires',
  },
  {
    quote:
      'Los ratios fundamentales coinciden con lo que veo en la SEC. Por fin algo serio para el inversor argentino que mira el exterior.',
    author: 'Sofía R.',
    role: 'Asesora financiera independiente',
  },
  {
    quote:
      'La API la pegamos a una notebook y armamos backtests en una tarde. El plan PRO se paga solo con el primer rebalance.',
    author: 'Iván P.',
    role: 'Quant retail · Rosario',
  },
  {
    quote:
      'Datos limpios, sin telebanca rota, sin scrappear EDGAR a las 3am. Vale cada peso.',
    author: 'Camila T.',
    role: 'Trader de CEDEARs',
  },
]

const COMPARE_LINKS = ['IOL', 'Cocos Capital', 'Balanz', 'Bull Market Brokers', 'Rava Bursátil', 'PPI', 'InvertirOnline', 'Yahoo Finance']

export default function LandingClient({ data }: { data: LandingData }) {
  const router = useRouter()
  const { isAuthenticated, loading } = useAuth()

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.replace('/cedears')
    }
  }, [loading, isAuthenticated, router])

  if (loading || isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-amber-500/30 border-t-amber-500 rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="bg-slate-950 text-slate-100 min-h-screen">
      <LandingNav />
      <Hero topRatios={data.topRatios} totalCount={data.totalCount} />
      <FeatureTags />
      <ProductShowcase detail={data.primary} />
      <Testimonials />
      <FeatureHighlights valueRatios={data.valueRatios} secondary={data.secondary} />
      <CtaBanner />
      <LandingFooter />
    </div>
  )
}

function LandingNav() {
  return (
    <header className="border-b border-slate-900/80 bg-slate-950/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
            Argfy
          </span>
        </Link>
        <nav className="hidden md:flex items-center gap-7 text-sm">
          {NAV_LINKS.map((l) => (
            <Link key={l.href} href={l.href} className="text-slate-400 hover:text-white transition-colors">
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <Link href="/auth/login" className="text-sm text-slate-300 hover:text-white">
            Iniciar sesión
          </Link>
          <Link
            href="/auth/register"
            className="bg-amber-500 hover:bg-amber-400 text-slate-900 font-semibold text-sm px-4 py-2 rounded-md transition-colors"
          >
            Inscripción gratuita
          </Link>
        </div>
      </div>
    </header>
  )
}

function Hero({ topRatios, totalCount }: { topRatios: RatioSnapshot[]; totalCount: number }) {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(245,158,11,0.15),_transparent_60%)]" />
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 lg:pt-24 lg:pb-28 grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.05]">
            <span className="text-white">Invertí como Wall Street</span>{' '}
            <span className="bg-gradient-to-r from-amber-300 via-amber-400 to-amber-600 bg-clip-text text-transparent">
              con datos de verdad
            </span>
          </h1>
          <p className="mt-6 text-lg text-slate-400 max-w-xl">
            Screener profesional de CEDEARs y acciones BYMA con fundamentos sacados directo de los filings de la SEC.
            PER, ROE, márgenes, deuda y más — listos para filtrar, comparar y exportar.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-3 sm:items-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center justify-center px-7 py-3.5 bg-amber-500 hover:bg-amber-400 text-slate-900 font-semibold rounded-lg transition-colors shadow-lg shadow-amber-500/20"
            >
              Empezá GRATIS →
            </Link>
            <p className="text-sm text-slate-500">No se necesita tarjeta de crédito</p>
          </div>
          <div className="mt-10 flex items-center gap-4">
            <div className="flex -space-x-2">
              {['#f59e0b', '#0ea5e9', '#10b981', '#f43f5e', '#8b5cf6'].map((c) => (
                <div
                  key={c}
                  className="w-9 h-9 rounded-full border-2 border-slate-950"
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>
            <div className="text-sm">
              <div className="text-white font-semibold">+1.500 inversores argentinos</div>
              <div className="text-slate-500">ya usan Argfy todas las semanas</div>
            </div>
          </div>
        </div>

        <LiveScreenerCard ratios={topRatios} totalCount={totalCount} />
      </div>
    </section>
  )
}

function LiveScreenerCard({ ratios, totalCount }: { ratios: RatioSnapshot[]; totalCount: number }) {
  const rows = ratios.length > 0 ? ratios : []
  return (
    <div className="relative">
      <div className="absolute -inset-4 bg-gradient-to-tr from-amber-500/20 via-transparent to-transparent rounded-2xl blur-2xl" />
      <div className="relative rounded-xl border border-slate-800 bg-slate-900/80 shadow-2xl overflow-hidden">
        <div className="h-9 bg-slate-900 border-b border-slate-800 flex items-center gap-1.5 px-3">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
          <span className="ml-3 text-xs text-slate-500">argfy.com/cedears</span>
          <span className="ml-auto inline-flex items-center gap-1.5 text-xs text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            LIVE
          </span>
        </div>
        <div className="p-4 text-xs">
          <div className="flex items-center justify-between mb-3">
            <div className="text-white font-semibold">Screener · CEDEARs</div>
            <div className="text-amber-400">
              {totalCount > 0 ? `${totalCount} resultados` : 'Datos en vivo'}
            </div>
          </div>
          {rows.length === 0 ? (
            <EmptyCard />
          ) : (
            <table className="w-full">
              <thead className="text-slate-500 border-b border-slate-800">
                <tr>
                  <th className="text-left py-2 font-medium">Ticker</th>
                  <th className="text-right py-2 font-medium">PER</th>
                  <th className="text-right py-2 font-medium">ROE</th>
                  <th className="text-right py-2 font-medium">Margen</th>
                  <th className="text-right py-2 font-medium">D/EBITDA</th>
                </tr>
              </thead>
              <tbody className="text-slate-300">
                {rows.map((r) => (
                  <tr key={r.byma_ticker} className="border-b border-slate-800/60 last:border-0">
                    <td className="py-2 font-semibold text-amber-400">{r.byma_ticker}</td>
                    <td className="py-2 text-right">{fmtNum(r.per_ttm, 1)}</td>
                    <td className="py-2 text-right text-emerald-400">{fmtPct(r.roe_cagr_5y)}</td>
                    <td className="py-2 text-right">{fmtPct(r.margen_neto_ttm)}</td>
                    <td className="py-2 text-right">{fmtNum(r.deuda_total_sobre_ebitda, 1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

function EmptyCard() {
  return (
    <div className="py-10 text-center text-slate-600">
      <svg className="w-10 h-10 mx-auto mb-3 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
      </svg>
      Conectando con el backend...
    </div>
  )
}

function FeatureTags() {
  return (
    <section className="border-y border-slate-900 bg-slate-950/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-wrap gap-x-8 gap-y-3 justify-center text-sm text-slate-400">
        {FEATURE_TAGS.map((t) => (
          <div key={t} className="flex items-center gap-2">
            <svg className="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
            {t}
          </div>
        ))}
      </div>
    </section>
  )
}

function ProductShowcase({ detail }: { detail: TickerDetail | null }) {
  return (
    <section id="producto" className="py-20 lg:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <p className="text-amber-400 text-sm font-semibold tracking-widest uppercase mb-3">
            Análisis fundamental
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
            Herramienta de análisis fundamental{' '}
            <span className="text-slate-400">para inversores serios</span>
          </h2>
        </div>
        <TickerDetailCard detail={detail} />
      </div>
    </section>
  )
}

function TickerDetailCard({ detail }: { detail: TickerDetail | null }) {
  const r = detail?.ratios
  const c = detail?.company
  const ticker = r?.byma_ticker ?? 'AAPL'
  const nombre = c?.nombre ?? r?.nombre ?? 'Datos en vivo'
  const price = r?.precio_usd
  const dif = r?.dif_max_52w
  const yearHigh = r?.year_high
  const yearLow = r?.year_low

  return (
    <div className="relative rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-2xl">
      <div className="h-10 bg-slate-900 border-b border-slate-800 flex items-center gap-2 px-4">
        <span className="w-3 h-3 rounded-full bg-rose-500/60" />
        <span className="w-3 h-3 rounded-full bg-amber-500/60" />
        <span className="w-3 h-3 rounded-full bg-emerald-500/60" />
        <span className="ml-4 text-xs text-slate-500">argfy.com/cedears/{ticker}</span>
      </div>
      <div className="p-6 lg:p-10">
        <div className="flex items-baseline gap-3 mb-1 flex-wrap">
          <h3 className="text-2xl font-bold text-white">
            {nombre} · {ticker}
          </h3>
          <span className="text-sm text-slate-500">
            {c?.exchange ?? r?.exchange ?? 'CEDEAR · BYMA'}
          </span>
        </div>
        <div className="flex items-baseline gap-4 mb-8">
          <span className="text-4xl font-bold text-white">
            {price != null ? `USD ${price.toFixed(2)}` : '—'}
          </span>
          {dif != null && (
            <span className={dif < 0 ? 'text-emerald-400 font-semibold' : 'text-slate-400 font-semibold'}>
              {dif < 0 ? '' : '-'}
              {(Math.abs(dif) * 100).toFixed(2)}% vs. 52w high
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <KpiBox label="PER TTM" value={fmtNum(r?.per_ttm, 1)} />
          <KpiBox label="ROE 5Y CAGR" value={fmtPct(r?.roe_cagr_5y)} />
          <KpiBox label="Margen neto" value={fmtPct(r?.margen_neto_ttm)} />
          <KpiBox label="Deuda/EBITDA" value={fmtNum(r?.deuda_total_sobre_ebitda, 1, 'x')} />
          <KpiBox label="EPS diluido" value={fmtNum(r?.eps_ttm_diluted, 2)} />
          <KpiBox label="Payout" value={fmtPct(r?.payout_ttm)} />
          <KpiBox label="FCF/Equity LP" value={fmtNum(r?.fcfonce_equity_lp, 2)} />
          <KpiBox
            label="52w range"
            value={
              yearLow != null && yearHigh != null
                ? `${yearLow.toFixed(0)}–${yearHigh.toFixed(0)}`
                : '—'
            }
          />
        </div>

        <Sparkline yearLow={yearLow} yearHigh={yearHigh} price={price} />
      </div>
    </div>
  )
}

function KpiBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
      <div className="text-xs text-slate-500 mb-1">{label}</div>
      <div className="text-lg font-semibold text-white">{value}</div>
    </div>
  )
}

function Sparkline({
  yearLow,
  yearHigh,
  price,
}: {
  yearLow: number | null | undefined
  yearHigh: number | null | undefined
  price: number | null | undefined
}) {
  // Sparkline visual orientativa: si tenemos 52w low/high/precio, marcamos donde está parado el precio.
  let pricePct = 50
  if (yearLow != null && yearHigh != null && price != null && yearHigh > yearLow) {
    pricePct = Math.max(0, Math.min(100, ((price - yearLow) / (yearHigh - yearLow)) * 100))
  }
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>52w low {yearLow != null ? yearLow.toFixed(0) : '—'}</span>
        <span>Precio actual</span>
        <span>52w high {yearHigh != null ? yearHigh.toFixed(0) : '—'}</span>
      </div>
      <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="absolute inset-y-0 left-0 bg-gradient-to-r from-rose-500/40 via-amber-500/40 to-emerald-500/40"
          style={{ width: '100%' }}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-amber-400 border-2 border-slate-950 shadow"
          style={{ left: `calc(${pricePct}% - 6px)` }}
        />
      </div>
    </div>
  )
}

function Testimonials() {
  return (
    <section className="py-20 lg:py-24 bg-slate-900/30 border-y border-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
            Mirá por qué nuestros usuarios{' '}
            <span className="bg-gradient-to-r from-amber-300 to-amber-500 bg-clip-text text-transparent">
              eligen Argfy
            </span>
          </h2>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {TESTIMONIALS.map((t, i) => (
            <figure key={i} className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 flex flex-col">
              <svg className="w-7 h-7 text-amber-500 mb-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9.583 17.321C8.553 16.227 8 15 8 13.011c0-3.5 2.457-6.637 6.03-8.188l.893 1.378c-3.335 1.804-3.987 4.145-4.247 5.621.537-.278 1.24-.375 1.929-.311 1.804.167 3.226 1.648 3.226 3.489a3.5 3.5 0 01-3.5 3.5c-1.073 0-2.099-.49-2.748-1.179zm10 0C18.553 16.227 18 15 18 13.011c0-3.5 2.457-6.637 6.03-8.188l.893 1.378c-3.335 1.804-3.987 4.145-4.247 5.621.537-.278 1.24-.375 1.929-.311 1.804.167 3.226 1.648 3.226 3.489a3.5 3.5 0 01-3.5 3.5c-1.073 0-2.099-.49-2.748-1.179z" />
              </svg>
              <blockquote className="text-slate-300 text-sm leading-relaxed flex-1">
                &ldquo;{t.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-5 pt-4 border-t border-slate-800">
                <div className="text-white font-semibold text-sm">{t.author}</div>
                <div className="text-slate-500 text-xs">{t.role}</div>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  )
}

function FeatureHighlights({
  valueRatios,
  secondary,
}: {
  valueRatios: RatioSnapshot[]
  secondary: TickerDetail | null
}) {
  const items: Array<{
    eyebrow: string
    title: string
    body: string
    bullets: string[]
    render: () => React.ReactNode
  }> = [
    {
      eyebrow: 'Screener',
      title: 'Filtrá 200+ CEDEARs por fundamentos en segundos',
      body:
        'PER, ROE, EPS, márgenes, deuda/EBITDA, payout y más. Ordená, filtrá y exportá. Los datos vienen directo de los 10-K/10-Q de la SEC, no de scraping flojo.',
      bullets: ['Más de 30 ratios por empresa', 'Histórico trimestral', 'Export CSV / JSON'],
      render: () => <ValueScreenerCard ratios={valueRatios} />,
    },
    {
      eyebrow: 'Ficha por ticker',
      title: 'Análisis fundamental serio, sin abrir 5 pestañas',
      body:
        'Entrá a cualquier CEDEAR y vas a tener precio actual, ratios TTM, evolución por trimestre, comparación con peers y links directos al filing original en EDGAR.',
      bullets: ['Precio + ratios + histórico en una pantalla', 'Comparación contra peers', 'Source link al 10-K'],
      render: () => <TickerCompactCard detail={secondary} />,
    },
    {
      eyebrow: 'API',
      title: 'Tus modelos, tus notebooks, nuestros datos',
      body:
        'Endpoint REST con auth por API key. Misma data que ves en el screener, lista para Python, Excel o tu stack favorito. Rate limits razonables incluso en Free.',
      bullets: ['REST + JSON', 'API keys por proyecto', 'Docs OpenAPI'],
      render: () => <ApiSnippet sampleTicker={valueRatios[0]?.byma_ticker} />,
    },
  ]

  return (
    <section className="py-20 lg:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-24">
        {items.map((f, i) => (
          <div
            key={i}
            className={`grid lg:grid-cols-2 gap-12 lg:gap-16 items-center ${
              i % 2 === 1 ? 'lg:[&>*:first-child]:order-2' : ''
            }`}
          >
            <div>
              <p className="text-amber-400 text-sm font-semibold tracking-widest uppercase mb-3">
                {f.eyebrow}
              </p>
              <h3 className="text-3xl sm:text-4xl font-bold text-white mb-5 leading-tight">
                {f.title}
              </h3>
              <p className="text-slate-400 text-lg leading-relaxed mb-6">{f.body}</p>
              <ul className="space-y-3">
                {f.bullets.map((b) => (
                  <li key={b} className="flex items-start gap-3 text-slate-300">
                    <svg className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    </svg>
                    {b}
                  </li>
                ))}
              </ul>
            </div>

            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-tr from-amber-500/10 via-transparent to-transparent rounded-2xl blur-2xl" />
              <div className="relative rounded-xl border border-slate-800 bg-slate-900/60 aspect-[4/3] overflow-hidden">
                {f.render()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

function ValueScreenerCard({ ratios }: { ratios: RatioSnapshot[] }) {
  return (
    <div className="w-full h-full p-6 text-xs flex flex-col">
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        <div className="px-2 py-1 rounded bg-amber-500/20 text-amber-300 font-semibold">PER &lt; 15</div>
        <div className="px-2 py-1 rounded bg-amber-500/20 text-amber-300 font-semibold">ROE &gt; 20%</div>
      </div>
      {ratios.length === 0 ? (
        <EmptyCard />
      ) : (
        <table className="w-full">
          <thead className="text-slate-500">
            <tr>
              <th className="text-left py-1.5">Ticker</th>
              <th className="text-right py-1.5">PER</th>
              <th className="text-right py-1.5">ROE</th>
              <th className="text-right py-1.5">Mg</th>
            </tr>
          </thead>
          <tbody className="text-slate-300">
            {ratios.map((r) => (
              <tr key={r.byma_ticker} className="border-b border-slate-800/60 last:border-0">
                <td className="py-2 text-amber-400 font-semibold">{r.byma_ticker}</td>
                <td className="py-2 text-right">{fmtNum(r.per_ttm, 1)}</td>
                <td className="py-2 text-right text-emerald-400">{fmtPct(r.roe_cagr_5y)}</td>
                <td className="py-2 text-right">{fmtPct(r.margen_neto_ttm)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

function TickerCompactCard({ detail }: { detail: TickerDetail | null }) {
  const r = detail?.ratios
  const c = detail?.company
  if (!detail) {
    return <div className="w-full h-full flex items-center justify-center"><EmptyCard /></div>
  }
  return (
    <div className="w-full h-full p-6 text-xs flex flex-col">
      <div className="text-white font-semibold text-base mb-1">
        {c?.nombre ?? r?.nombre ?? r?.byma_ticker} · {r?.byma_ticker}
      </div>
      <div className="text-slate-500 mb-4">{c?.exchange ?? r?.exchange ?? 'CEDEAR · BYMA'}</div>
      <div className="grid grid-cols-2 gap-2 mb-4">
        <MiniKpi label="PER" value={fmtNum(r?.per_ttm, 1)} />
        <MiniKpi label="ROE" value={fmtPct(r?.roe_cagr_5y)} />
        <MiniKpi label="Margen" value={fmtPct(r?.margen_neto_ttm)} />
        <MiniKpi label="D/EBITDA" value={fmtNum(r?.deuda_total_sobre_ebitda, 1, 'x')} />
      </div>
      <div className="mt-auto text-slate-500 text-[10px]">
        Período: {r?.period_end ?? '—'} · Fuente: SEC EDGAR
      </div>
    </div>
  )
}

function MiniKpi({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-950/60 border border-slate-800 rounded p-2">
      <div className="text-slate-500">{label}</div>
      <div className="text-white font-semibold text-sm">{value}</div>
    </div>
  )
}

function ApiSnippet({ sampleTicker }: { sampleTicker?: string }) {
  const t = sampleTicker || 'AAPL'
  return (
    <div className="w-full h-full p-6 text-xs font-mono">
      <div className="text-slate-500 mb-2"># Python · requests</div>
      <pre className="text-slate-300 leading-relaxed whitespace-pre-wrap">
{`import requests

r = requests.get(
  "https://api.argfy.com/v1/fundamentals/${t}",
  headers={"X-API-Key": "ak_..."},
)
data = r.json()
print(data["ratios"]["per_ttm"])`}
      </pre>
      <div className="mt-3 text-emerald-400">→ 200 OK · 124ms</div>
    </div>
  )
}

function CtaBanner() {
  return (
    <section className="px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-7xl mx-auto rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-slate-800 overflow-hidden">
        <div className="relative px-8 sm:px-12 py-16 lg:py-20 text-center">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(245,158,11,0.15),_transparent_60%)]" />
          <div className="relative">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-5">
              Empezá a invertir con{' '}
              <span className="bg-gradient-to-r from-amber-300 to-amber-500 bg-clip-text text-transparent">
                datos de verdad
              </span>
            </h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto mb-8">
              Probá Argfy gratis. Sin tarjeta. Sin compromiso. Sólo datos limpios y un screener que te va a hacer la vida más fácil.
            </p>
            <Link
              href="/auth/register"
              className="inline-flex items-center px-8 py-4 bg-amber-500 hover:bg-amber-400 text-slate-900 font-semibold rounded-lg transition-colors shadow-lg shadow-amber-500/20"
            >
              Crear cuenta gratis →
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}

function LandingFooter() {
  return (
    <footer className="border-t border-slate-900 bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid md:grid-cols-4 gap-10">
          <div>
            <div className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent mb-3">
              Argfy
            </div>
            <p className="text-sm text-slate-500 max-w-xs">
              Screener fundamental de CEDEARs y BYMA. Datos de SEC/EDGAR, listos para invertir.
            </p>
          </div>
          <FooterColumn
            title="Empresa"
            links={[
              { label: 'Sobre nosotros', href: '#sobre' },
              { label: 'Blog', href: '#blog' },
              { label: 'Contacto', href: 'mailto:hola@argfy.com' },
              { label: 'Términos', href: '/legal/terms' },
              { label: 'Privacidad', href: '/legal/privacy' },
            ]}
          />
          <FooterColumn
            title="Producto"
            links={[
              { label: 'Screener', href: '/cedears' },
              { label: 'Precios', href: '/pricing' },
              { label: 'API', href: '/api' },
              { label: 'Documentación', href: '/api' },
            ]}
          />
          <FooterColumn
            title="Compará Argfy con"
            links={COMPARE_LINKS.map((l) => ({ label: l, href: '#' }))}
          />
        </div>
        <div className="mt-12 pt-8 border-t border-slate-900 flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-slate-600">
          <div>
            <p>La información provista no constituye asesoramiento financiero.</p>
            <p>Datos as-is. Consultá a un agente registrado ante la CNV.</p>
          </div>
          <p>© {new Date().getFullYear()} Argfy · Hecho en Argentina</p>
        </div>
      </div>
    </footer>
  )
}

function FooterColumn({ title, links }: { title: string; links: { label: string; href: string }[] }) {
  return (
    <div>
      <h4 className="text-white font-semibold text-sm mb-4">{title}</h4>
      <ul className="space-y-2.5">
        {links.map((l) => (
          <li key={l.label}>
            <Link href={l.href} className="text-sm text-slate-500 hover:text-amber-400 transition-colors">
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}

function fmtNum(v: number | null | undefined, decimals = 2, suffix = ''): string {
  if (v == null || !Number.isFinite(v)) return '—'
  return `${v.toFixed(decimals)}${suffix}`
}

function fmtPct(v: number | null | undefined): string {
  if (v == null || !Number.isFinite(v)) return '—'
  return `${(v * 100).toFixed(1)}%`
}
