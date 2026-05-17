"use client"

import Link from "next/link"
import { useScreener } from "@/hooks/useScreener"

export default function CedearsLeaderboard() {
  const { data, isLoading } = useScreener({ sort_by: "per_ttm", sort_desc: false, limit: 5 })

  if (isLoading) {
    return (
      <section className="py-16 bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-slate-700 rounded w-64" />
            <div className="h-64 bg-slate-700 rounded" />
          </div>
        </div>
      </section>
    )
  }

  const companies = data?.data ?? []

  return (
    <section className="py-16 bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-white">CEDEARs Leaderboard</h2>
            <p className="text-slate-400 mt-1">Top CEDEARs by key financial metrics</p>
          </div>
          <Link
            href="/cedears"
            className="text-amber-400 hover:text-amber-300 font-semibold transition-colors"
          >
            Ver todos &rarr;
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 uppercase text-xs tracking-wider">
                <th className="text-left py-3 px-2">Ticker</th>
                <th className="text-left py-3 px-2">Nombre</th>
                <th className="text-right py-3 px-2">Precio USD</th>
                <th className="text-right py-3 px-2">PER</th>
                <th className="text-right py-3 px-2">Margen Neto</th>
                <th className="text-right py-3 px-2">ROE</th>
                <th className="text-right py-3 px-2">Deuda/EBITDA</th>
              </tr>
            </thead>
            <tbody>
              {companies.map((c) => (
                <tr
                  key={c.byma_ticker}
                  className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors"
                >
                  <td className="py-3 px-2">
                    <Link
                      href={`/cedears/${c.byma_ticker}`}
                      className="text-amber-400 hover:text-amber-300 font-mono font-semibold"
                    >
                      {c.byma_ticker}
                    </Link>
                  </td>
                  <td className="py-3 px-2 text-slate-300 max-w-[200px] truncate">
                    {c.nombre ?? "-"}
                  </td>
                  <td className="py-3 px-2 text-right text-white font-mono">
                    {c.precio_usd != null ? `$${c.precio_usd.toFixed(2)}` : "-"}
                  </td>
                  <td className="py-3 px-2 text-right font-mono">
                    {c.per_ttm != null ? (
                      <span className={c.per_ttm < 15 ? "text-green-400" : c.per_ttm < 30 ? "text-amber-400" : "text-red-400"}>
                        {c.per_ttm.toFixed(1)}
                      </span>
                    ) : "-"}
                  </td>
                  <td className="py-3 px-2 text-right font-mono">
                    {c.margen_neto_ttm != null ? (
                      <span className={c.margen_neto_ttm > 0.15 ? "text-green-400" : c.margen_neto_ttm > 0 ? "text-amber-400" : "text-red-400"}>
                        {(c.margen_neto_ttm * 100).toFixed(1)}%
                      </span>
                    ) : "-"}
                  </td>
                  <td className="py-3 px-2 text-right font-mono">
                    {c.roe_cagr_5y != null ? (
                      <span className={c.roe_cagr_5y > 0.15 ? "text-green-400" : c.roe_cagr_5y > 0 ? "text-amber-400" : "text-red-400"}>
                        {(c.roe_cagr_5y * 100).toFixed(1)}%
                      </span>
                    ) : "-"}
                  </td>
                  <td className="py-3 px-2 text-right font-mono">
                    {c.deuda_total_sobre_ebitda != null ? (
                      <span className={c.deuda_total_sobre_ebitda < 2 ? "text-green-400" : c.deuda_total_sobre_ebitda < 4 ? "text-amber-400" : "text-red-400"}>
                        {c.deuda_total_sobre_ebitda.toFixed(1)}
                      </span>
                    ) : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
