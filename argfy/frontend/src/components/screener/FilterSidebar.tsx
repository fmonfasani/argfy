"use client"

import { useCallback, useEffect, useState } from "react"
import { useSearchParams, useRouter, usePathname } from "next/navigation"
import { useCoverage } from "@/hooks/useCoverage"
import { useDebounce } from "@/hooks/useDebounce"
import type { ScreenerFilters } from "@/lib/types"

const EXCHANGES = ["NMS", "NYQ", "NAS", "BYMA", "OTN"] as const
const COUNTRIES = ["US", "AR", "OTROS"] as const

function parseFiltersFromParams(sp: URLSearchParams): ScreenerFilters {
  const f: ScreenerFilters = {}
  const per_min = sp.get("per_min")
  const per_max = sp.get("per_max")
  if (per_min) f.per_min = Number(per_min)
  if (per_max) f.per_max = Number(per_max)
  const roe = sp.get("roe_min")
  if (roe) f.roe_min = Number(roe)
  const margen = sp.get("margen_min")
  if (margen) f.margen_min = Number(margen)
  const deuda = sp.get("deuda_max")
  if (deuda) f.deuda_max = Number(deuda)
  const payout = sp.get("payout_max")
  if (payout) f.payout_max = Number(payout)
  const exchange = sp.get("exchange")
  if (exchange) f.exchange = exchange
  const country = sp.get("country")
  if (country) f.country = country
  const q = sp.get("q")
  if (q) f.q = q
  const sort_by = sp.get("sort_by")
  if (sort_by) f.sort_by = sort_by
  f.sort_desc = sp.get("sort_desc") === "true"
  return f
}

function filtersToParams(f: ScreenerFilters): Record<string, string> {
  const p: Record<string, string> = {}
  if (f.per_min != null && f.per_min > 0) p.per_min = String(f.per_min)
  if (f.per_max != null && f.per_max < 200) p.per_max = String(f.per_max)
  if (f.roe_min != null && f.roe_min > 0) p.roe_min = String(f.roe_min)
  if (f.margen_min != null && f.margen_min > -0.5) p.margen_min = String(f.margen_min)
  if (f.deuda_max != null && f.deuda_max < 20) p.deuda_max = String(f.deuda_max)
  if (f.payout_max != null && f.payout_max < 2) p.payout_max = String(f.payout_max)
  if (f.exchange) p.exchange = f.exchange
  if (f.country) p.country = f.country
  if (f.q) p.q = f.q
  if (f.sort_by) p.sort_by = f.sort_by
  if (f.sort_desc) p.sort_desc = "true"
  return p
}

interface FilterSidebarProps {
  filters: ScreenerFilters
  onFiltersChange: (f: ScreenerFilters) => void
  isOpen?: boolean
  onClose?: () => void
}

export default function FilterSidebar({ filters, onFiltersChange, isOpen, onClose }: FilterSidebarProps) {
  const { data: coverage } = useCoverage()
  const [localQ, setLocalQ] = useState(filters.q ?? "")
  const debouncedQ = useDebounce(localQ, 400)

  useEffect(() => {
    if (debouncedQ !== (filters.q ?? "")) {
      onFiltersChange({ ...filters, q: debouncedQ || undefined })
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQ])

  function set<K extends keyof ScreenerFilters>(key: K, value: ScreenerFilters[K]) {
    onFiltersChange({ ...filters, [key]: value })
  }

  function reset() {
    setLocalQ("")
    onFiltersChange({})
  }

  const content = (
    <div className="space-y-6">
      {/* Coverage counters */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Cobertura</h3>
        <div className="space-y-1 text-sm text-slate-300">
          {coverage ? (
            Object.entries(coverage.coverage).slice(0, 5).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span className="capitalize">{k.replace(/_/g, " ")}</span>
                <span className="font-mono text-slate-400">{(v.pct * 100).toFixed(0)}%</span>
              </div>
            ))
          ) : (
            <div className="animate-pulse space-y-1">
              {[1, 2, 3].map(i => <div key={i} className="h-4 bg-slate-700 rounded w-full" />)}
            </div>
          )}
        </div>
      </div>

      {/* Búsqueda */}
      <div>
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Buscar</label>
        <input
          type="text"
          placeholder="Ticker o nombre..."
          value={localQ}
          onChange={e => setLocalQ(e.target.value)}
          className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
        />
      </div>

      {/* PER TTM */}
      <div>
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
          PER TTM <span className="text-slate-500 normal-case">({filters.per_min ?? 0} – {filters.per_max ?? 200})</span>
        </label>
        <div className="flex items-center gap-3">
          <input
            type="range" min={0} max={200} step={1}
            value={filters.per_min ?? 0}
            onChange={e => set("per_min", Number(e.target.value) || undefined)}
            className="flex-1 accent-amber-500"
          />
          <input
            type="range" min={0} max={200} step={1}
            value={filters.per_max ?? 200}
            onChange={e => set("per_max", Number(e.target.value) < 200 ? Number(e.target.value) : undefined)}
            className="flex-1 accent-amber-500"
          />
        </div>
      </div>

      {/* ROE 5y */}
      <div>
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
          ROE 5y min <span className="text-slate-500 normal-case">{((filters.roe_min ?? 0) * 100).toFixed(0)}%</span>
        </label>
        <input
          type="range" min={0} max={100} step={1}
          value={(filters.roe_min ?? 0) * 100}
          onChange={e => set("roe_min", Number(e.target.value) / 100 || undefined)}
          className="w-full accent-amber-500"
        />
      </div>

      {/* Margen Neto */}
      <div>
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
          Margen Neto TTM min <span className="text-slate-500 normal-case">{((filters.margen_min ?? -0.5) * 100).toFixed(0)}%</span>
        </label>
        <input
          type="range" min={-50} max={100} step={1}
          value={(filters.margen_min ?? -0.5) * 100}
          onChange={e => set("margen_min", Number(e.target.value) / 100 || undefined)}
          className="w-full accent-amber-500"
        />
      </div>

      {/* Deuda / EBITDA */}
      <div>
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
          Deuda/EBITDA máx <span className="text-slate-500 normal-case">{filters.deuda_max ?? 20}x</span>
        </label>
        <input
          type="range" min={0} max={20} step={0.5}
          value={filters.deuda_max ?? 20}
          onChange={e => set("deuda_max", Number(e.target.value) < 20 ? Number(e.target.value) : undefined)}
          className="w-full accent-amber-500"
        />
      </div>

      {/* Payout */}
      <div>
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
          Payout TTM máx <span className="text-slate-500 normal-case">{((filters.payout_max ?? 2) * 100).toFixed(0)}%</span>
        </label>
        <input
          type="range" min={0} max={200} step={5}
          value={(filters.payout_max ?? 2) * 100}
          onChange={e => set("payout_max", Number(e.target.value) / 100 || undefined)}
          className="w-full accent-amber-500"
        />
      </div>

      {/* Exchange */}
      <div>
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Exchange</label>
        <div className="flex flex-wrap gap-2">
          {EXCHANGES.map(ex => (
            <button
              key={ex}
              onClick={() => set("exchange", filters.exchange === ex ? undefined : ex)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                filters.exchange === ex
                  ? "bg-amber-500/20 border-amber-500 text-amber-400"
                  : "border-slate-600 text-slate-400 hover:border-slate-500"
              }`}
            >
              {ex}
            </button>
          ))}
        </div>
      </div>

      {/* País */}
      <div>
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">País</label>
        <div className="flex flex-wrap gap-2">
          {COUNTRIES.map(c => (
            <button
              key={c}
              onClick={() => set("country", filters.country === c ? undefined : c)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                filters.country === c
                  ? "bg-amber-500/20 border-amber-500 text-amber-400"
                  : "border-slate-600 text-slate-400 hover:border-slate-500"
              }`}
            >
              {c === "OTROS" ? "Otros" : c}
            </button>
          ))}
        </div>
      </div>

      {/* Reset */}
      <button
        onClick={reset}
        className="w-full py-2 text-sm text-slate-400 border border-slate-600 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
      >
        Resetear filtros
      </button>
    </div>
  )

  if (isOpen !== undefined) {
    return (
      <>
        {/* Mobile overlay */}
        {isOpen && (
          <div className="fixed inset-0 z-40 lg:hidden" onClick={onClose}>
            <div className="absolute inset-0 bg-black/50" />
          </div>
        )}
        {/* Mobile drawer */}
        <aside className={`fixed top-0 left-0 z-50 h-full w-80 max-w-[85vw] bg-slate-900 border-r border-slate-700 transform transition-transform duration-300 lg:hidden ${isOpen ? "translate-x-0" : "-translate-x-full"}`}>
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
            <h2 className="text-white font-semibold">Filtros</h2>
            <button onClick={onClose} className="text-slate-400 hover:text-white text-xl">&times;</button>
          </div>
          <div className="p-4 overflow-y-auto h-[calc(100%-56px)]">
            {content}
          </div>
        </aside>
        {/* Desktop sidebar */}
        <aside className="hidden lg:block w-72 shrink-0">
          <div className="sticky top-4">
            <h2 className="text-white font-semibold mb-4">Filtros</h2>
            {content}
          </div>
        </aside>
      </>
    )
  }

  return (
    <aside className="w-72 shrink-0">
      <div className="sticky top-4">
        <h2 className="text-white font-semibold mb-4">Filtros</h2>
        {content}
      </div>
    </aside>
  )
}
