"use client"

import { useRouter } from "next/navigation"
import type { ScreenerResponse, ScreenerFilters } from "@/lib/types"
import RatioCell, { PER_RULE, ROE_RULE, MARGEN_RULE, DEUDA_RULE, PAYOUT_RULE } from "./RatioCell"

interface ScreenerTableProps {
  data: ScreenerResponse
  filters: ScreenerFilters
  onSort: (by: string) => void
  onPage: (offset: number) => void
}

const COLUMNS: { key: string; label: string; sortable: boolean; align: "left" | "right" }[] = [
  { key: "byma_ticker", label: "Ticker", sortable: true, align: "left" },
  { key: "nombre", label: "Nombre", sortable: true, align: "left" },
  { key: "exchange", label: "Exchange", sortable: true, align: "left" },
  { key: "precio_usd", label: "Precio USD", sortable: true, align: "right" },
  { key: "per_ttm", label: "PER", sortable: true, align: "right" },
  { key: "roe_cagr_5y", label: "ROE 5y", sortable: true, align: "right" },
  { key: "margen_neto_ttm", label: "Margen", sortable: true, align: "right" },
  { key: "deuda_total_sobre_ebitda", label: "Deuda/EBITDA", sortable: true, align: "right" },
  { key: "fcfonce_equity_lp", label: "FCF/Equity", sortable: false, align: "right" },
  { key: "payout_ttm", label: "Payout", sortable: true, align: "right" },
  { key: "country", label: "País", sortable: true, align: "right" },
]

function sortIcon(by: string, active: string, desc: boolean): string {
  if (by !== active) return "↕"
  return desc ? "↓" : "↑"
}

function exportCsv(data: ScreenerResponse) {
  const headers = ["Ticker", "Nombre", "Exchange", "Precio USD", "PER", "ROE 5y", "Margen", "Deuda/EBITDA", "FCF/Equity", "Payout", "País"]
  const rows = data.data.map(c => [
    c.byma_ticker,
    `"${(c.nombre ?? "").replace(/"/g, '""')}"`,
    c.exchange ?? "",
    c.precio_usd?.toFixed(2) ?? "",
    c.per_ttm?.toFixed(1) ?? "",
    c.roe_cagr_5y != null ? (c.roe_cagr_5y * 100).toFixed(1) : "",
    c.margen_neto_ttm != null ? (c.margen_neto_ttm * 100).toFixed(1) : "",
    c.deuda_total_sobre_ebitda?.toFixed(1) ?? "",
    c.fcfonce_equity_lp?.toFixed(1) ?? "",
    c.payout_ttm != null ? (c.payout_ttm * 100).toFixed(0) : "",
    c.country ?? "",
  ])

  const csv = [headers.join(","), ...rows.map(r => r.join(","))].join("\n")
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `cedears_screener_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

export default function ScreenerTable({ data, filters, onSort, onPage }: ScreenerTableProps) {
  const router = useRouter()
  const limit = filters.limit ?? 100
  const offset = filters.offset ?? 0
  const totalPages = Math.ceil(data.total / limit)
  const currentPage = Math.floor(offset / limit) + 1
  const from = offset + 1
  const to = Math.min(offset + limit, data.total)

  return (
    <div>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-slate-400">
          Mostrando <span className="text-white">{from}–{to}</span> de <span className="text-white">{data.total}</span>
        </p>
        <button
          onClick={() => exportCsv(data)}
          className="px-3 py-1.5 text-xs font-medium text-slate-300 border border-slate-600 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
        >
          Exportar CSV
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-slate-800">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-800 text-slate-400 uppercase text-xs tracking-wider">
              {COLUMNS.map((col, i) => (
                <th
                  key={col.key}
                  onClick={() => col.sortable && onSort(col.key)}
                  className={`py-3 px-2 ${col.align === "right" ? "text-right" : "text-left"} ${
                    col.sortable ? "cursor-pointer hover:text-white select-none" : ""
                  } ${i === 0 ? "sticky left-0 bg-slate-800 z-10" : ""}`}
                >
                  {col.label}{" "}
                  {col.sortable && (
                    <span className="text-slate-500">{sortIcon(col.key, filters.sort_by ?? "", filters.sort_desc ?? false)}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.data.map((c) => (
              <tr
                key={c.byma_ticker}
                onClick={() => router.push(`/cedears/${c.byma_ticker}`)}
                className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors cursor-pointer"
              >
                <td className="sticky left-0 bg-slate-900 py-3 px-2 font-mono text-amber-400 font-semibold z-10">{c.byma_ticker}</td>
                <td className="py-3 px-2 text-slate-300 max-w-[220px] truncate" title={c.nombre ?? ""}>{c.nombre ?? "-"}</td>
                <td className="py-3 px-2 text-slate-400">{c.exchange ?? "-"}</td>
                <td className="py-3 px-2 text-right"><RatioCell value={c.precio_usd} rule={{ type: "money" }} /></td>
                <td className="py-3 px-2 text-right"><RatioCell value={c.per_ttm} rule={PER_RULE} /></td>
                <td className="py-3 px-2 text-right"><RatioCell value={c.roe_cagr_5y} rule={ROE_RULE} /></td>
                <td className="py-3 px-2 text-right"><RatioCell value={c.margen_neto_ttm} rule={MARGEN_RULE} /></td>
                <td className="py-3 px-2 text-right"><RatioCell value={c.deuda_total_sobre_ebitda} rule={DEUDA_RULE} /></td>
                <td className="py-3 px-2 text-right"><RatioCell value={c.fcfonce_equity_lp} rule={{ type: "ratio", green: 1, red: 0 }} /></td>
                <td className="py-3 px-2 text-right"><RatioCell value={c.payout_ttm} rule={PAYOUT_RULE} /></td>
                <td className="py-3 px-2 text-right text-slate-400">{c.country ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-6">
          <button
            disabled={currentPage <= 1}
            onClick={() => onPage(offset - limit)}
            className="px-4 py-2 text-sm border border-slate-600 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
          >
            Anterior
          </button>
          {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
            let pageNum: number
            if (totalPages <= 7) {
              pageNum = i + 1
            } else if (currentPage <= 4) {
              pageNum = i + 1
            } else if (currentPage >= totalPages - 3) {
              pageNum = totalPages - 6 + i
            } else {
              pageNum = currentPage - 3 + i
            }
            const isActive = pageNum === currentPage
            return (
              <button
                key={pageNum}
                onClick={() => onPage((pageNum - 1) * limit)}
                className={`w-9 h-9 text-sm rounded-lg transition-colors ${
                  isActive
                    ? "bg-amber-500 text-slate-900 font-semibold"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                {pageNum}
              </button>
            )
          })}
          <button
            disabled={currentPage >= totalPages}
            onClick={() => onPage(offset + limit)}
            className="px-4 py-2 text-sm border border-slate-600 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  )
}
