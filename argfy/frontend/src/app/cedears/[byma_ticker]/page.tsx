"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { useTickerDetail } from "@/hooks/useTickerDetail"
import PriceChart from "@/components/charts/PriceChart"
import MetricHistoryChart from "@/components/charts/MetricHistoryChart"
import RatioCell, { PER_RULE, ROE_RULE, MARGEN_RULE, DEUDA_RULE, PAYOUT_RULE } from "@/components/screener/RatioCell"
import { LoadingSpinner } from "@/components/ui/LoadingSpinner"
import { formatMoney } from "@/lib/utils"

function DetailLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="animate-pulse space-y-3">
        <div className="h-8 bg-slate-800 rounded w-96" />
        <div className="h-4 bg-slate-800/50 rounded w-64" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => <div key={i} className="h-24 bg-slate-800/50 rounded-xl" />)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-72 bg-slate-800/50 rounded-xl" />
        <div className="h-72 bg-slate-800/50 rounded-xl" />
      </div>
    </div>
  )
}

function EmptyState({ message, sub }: { message: string; sub?: string }) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
      <svg className="w-12 h-12 mx-auto text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
      <p className="text-lg text-slate-300 mb-2">{message}</p>
      {sub && <p className="text-sm text-slate-500 mb-6">{sub}</p>}
      <Link href="/cedears" className="text-amber-400 hover:text-amber-300 font-semibold transition-colors">
        Volver al Screener →
      </Link>
    </div>
  )
}

export default function TickerDetailPage() {
  const params = useParams()
  const ticker = params?.byma_ticker as string
  const { data, isLoading, error } = useTickerDetail(ticker)

  if (isLoading) return <DetailLoading />
  if (error || !data) return <EmptyState message="No se pudieron cargar los datos de este ticker." sub="El ticker puede no existir o no haber datos disponibles." />

  const { ratios, company } = data

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <Link href="/cedears" className="text-slate-500 hover:text-white transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <h1 className="text-2xl font-bold text-white">{company.nombre ?? ticker}</h1>
          <span className="text-lg font-mono text-amber-400 font-semibold">{ticker}</span>
          {company.has_sec && (
            <span className="px-2 py-0.5 text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full font-medium">
              SEC verified
            </span>
          )}
        </div>
        <p className="text-sm text-slate-400 space-x-3">
          {company.ticker_sec && <span>{company.ticker_sec}</span>}
          {company.cik && <span>· CIK: {company.cik}</span>}
          {company.exchange && <span>· {company.exchange}</span>}
          {company.country && <span>· {company.country}</span>}
          {company.sector && <span>· {company.sector}</span>}
          {company.industry && <span>· {company.industry}</span>}
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Precio USD</p>
          <p className="text-xl font-bold text-white">{formatMoney(ratios.precio_usd)}</p>
          {ratios.dif_max_52w != null && (
            <p className={`text-xs mt-1 ${ratios.dif_max_52w > 0 ? "text-green-400" : "text-red-400"}`}>
              {ratios.dif_max_52w > 0 ? "+" : ""}{(ratios.dif_max_52w * 100).toFixed(1)}% vs max 52w
            </p>
          )}
        </div>
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">PER TTM</p>
          <p className="text-xl font-bold text-white"><RatioCell value={ratios.per_ttm} rule={PER_RULE} /></p>
        </div>
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">ROE 5y CAGR</p>
          <p className="text-xl font-bold text-white"><RatioCell value={ratios.roe_cagr_5y} rule={ROE_RULE} /></p>
        </div>
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Margen Neto TTM</p>
          <p className="text-xl font-bold text-white"><RatioCell value={ratios.margen_neto_ttm} rule={MARGEN_RULE} /></p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PriceChart ticker={ticker} />
        <MetricHistoryChart ticker={ticker} />
      </div>

      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
        <h3 className="text-white font-semibold mb-4">Components TTM</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Revenue", key: "revenue_ttm" },
            { label: "Net Income", key: "netincome_ttm" },
            { label: "EBITDA", key: "ebitda_ttm" },
            { label: "Free Cash Flow", key: "fcf_ttm" },
          ].map(item => (
            <div key={item.key} className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50">
              <p className="text-xs text-slate-400">{item.label}</p>
              <p className="text-base font-mono text-white mt-1">
                <RatioCell value={(ratios as any)[item.key]} rule={{ type: "money" }} />
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
        <h3 className="text-white font-semibold mb-4">Ratios completos</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 uppercase text-xs tracking-wider">
                <th className="text-left py-2 pr-4">Métrica</th>
                <th className="text-right py-2 pl-4">Valor</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["PER TTM", ratios.per_ttm, PER_RULE],
                ["EPS TTM Diluted", ratios.eps_ttm_diluted, "money"],
                ["Margen Neto TTM", ratios.margen_neto_ttm, MARGEN_RULE],
                ["ROE 5y CAGR", ratios.roe_cagr_5y, ROE_RULE],
                ["Deuda LP / EBITDA", ratios.deuda_lp_sobre_ebitda, DEUDA_RULE],
                ["Deuda Total / EBITDA", ratios.deuda_total_sobre_ebitda, DEUDA_RULE],
                ["FCF / Equity LP", ratios.fcfonce_equity_lp, { type: "ratio", green: 1, red: 0 } as const],
                ["FCF / Neto Caja", ratios.fcfonce_neto_caja, { type: "ratio", green: 1, red: 0 } as const],
                ["Payout TTM", ratios.payout_ttm, PAYOUT_RULE],
                ["Δ Max 52w", ratios.dif_max_52w, { type: "pct", green: 0, red: -0.1 } as const],
                ["Δ Min 52w", ratios.dif_min_52w, { type: "pct", green: 0.1, red: 0 } as const],
              ].map(([label, value, rule]) => (
                <tr key={label as string} className="border-b border-slate-800 last:border-0">
                  <td className="py-2.5 pr-4 text-slate-300">{label as string}</td>
                  <td className="py-2.5 pl-4 text-right">
                    {rule === "money" ? (
                      <RatioCell value={value as number | null | undefined} rule={{ type: "money" }} />
                    ) : (
                      <RatioCell value={value as number | null | undefined} rule={rule as any} />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
