"use client"

import { Suspense, useState, useCallback } from "react"
import { useSearchParams, useRouter, usePathname } from "next/navigation"
import FilterSidebar from "@/components/screener/FilterSidebar"
import ScreenerTable from "@/components/screener/ScreenerTable"
import { useScreener } from "@/hooks/useScreener"
import { LoadingSpinner } from "@/components/ui/LoadingSpinner"
import type { ScreenerFilters } from "@/lib/types"

function parseFilters(sp: URLSearchParams): ScreenerFilters {
  const f: ScreenerFilters = { limit: 100, offset: 0 }
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
  const offset = sp.get("offset")
  if (offset) f.offset = Number(offset)
  return f
}

function filtersToParams(f: ScreenerFilters): URLSearchParams {
  const p = new URLSearchParams()
  if (f.per_min != null && f.per_min > 0) p.set("per_min", String(f.per_min))
  if (f.per_max != null && f.per_max < 200) p.set("per_max", String(f.per_max))
  if (f.roe_min != null && f.roe_min > 0) p.set("roe_min", String(f.roe_min))
  if (f.margen_min != null && f.margen_min > -0.5) p.set("margen_min", String(f.margen_min))
  if (f.deuda_max != null && f.deuda_max < 20) p.set("deuda_max", String(f.deuda_max))
  if (f.payout_max != null && f.payout_max < 2) p.set("payout_max", String(f.payout_max))
  if (f.exchange) p.set("exchange", f.exchange)
  if (f.country) p.set("country", f.country)
  if (f.q) p.set("q", f.q)
  if (f.sort_by) p.set("sort_by", f.sort_by)
  if (f.sort_desc) p.set("sort_desc", "true")
  if (f.offset && f.offset > 0) p.set("offset", String(f.offset))
  return p
}

function CedearsContent() {
  const sp = useSearchParams()
  const router = useRouter()
  const pathname = usePathname()
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)

  const filters = parseFilters(sp)
  const { data, isLoading, isError, refetch } = useScreener(filters)

  const syncFilters = useCallback((newFilters: ScreenerFilters) => {
    const qs = filtersToParams(newFilters).toString()
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false })
  }, [pathname, router])

  const handleSort = useCallback((by: string) => {
    const next = { ...filters, offset: 0 }
    if (next.sort_by === by) {
      next.sort_desc = !next.sort_desc
    } else {
      next.sort_by = by
      next.sort_desc = false
    }
    syncFilters(next)
  }, [filters, syncFilters])

  const handlePage = useCallback((offset: number) => {
    syncFilters({ ...filters, offset })
  }, [filters, syncFilters])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="lg:hidden mb-4">
        <button
          onClick={() => setMobileFiltersOpen(true)}
          className="px-4 py-2 bg-slate-800 text-white rounded-md border border-slate-700 text-sm hover:bg-slate-700 transition-colors"
        >
          Filtrar
        </button>
      </div>

      <div className="flex gap-8">
        <FilterSidebar
          filters={filters}
          onFiltersChange={syncFilters}
          isOpen={mobileFiltersOpen}
          onClose={() => setMobileFiltersOpen(false)}
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-white">Screener de CEDEARs</h1>
              <p className="text-slate-400 text-sm mt-1">
                {data ? `${data.total} tickers` : isLoading ? "Cargando datos..." : "Sin resultados"}
              </p>
            </div>
            {isLoading && <LoadingSpinner size="sm" />}
          </div>

          {isError ? (
            <div className="text-center py-20 bg-slate-800/30 rounded-xl border border-slate-700/50">
              <svg className="w-12 h-12 mx-auto text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              <p className="text-lg text-slate-300 mb-2">Error al cargar datos</p>
              <p className="text-sm text-slate-500 mb-6">No se pudo conectar con el servidor.</p>
              <button
                onClick={() => refetch()}
                className="px-5 py-2 bg-amber-500 text-slate-900 rounded-md font-semibold hover:bg-amber-400 transition-colors"
              >
                Reintentar
              </button>
            </div>
          ) : isLoading ? (
            <div className="space-y-2">
              <div className="h-10 bg-slate-800/50 rounded animate-pulse" />
              {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} className="h-10 bg-slate-800/30 rounded animate-pulse" style={{ animationDelay: `${i * 50}ms` }} />
              ))}
            </div>
          ) : data && data.data.length > 0 ? (
            <ScreenerTable
              data={data}
              filters={filters}
              onSort={handleSort}
              onPage={handlePage}
            />
          ) : (
            <div className="text-center py-20 bg-slate-800/30 rounded-xl border border-slate-700/50">
              <svg className="w-12 h-12 mx-auto text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              <p className="text-lg text-slate-300 mb-2">Sin resultados</p>
              <p className="text-sm text-slate-500 mb-6">Probá ajustar los filtros o resetearlos.</p>
              <button
                onClick={() => { syncFilters({}); setMobileFiltersOpen(false) }}
                className="px-5 py-2 border border-slate-600 text-slate-300 rounded-md hover:bg-slate-800 transition-colors"
              >
                Resetear filtros
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function CedearsPage() {
  return (
    <Suspense fallback={
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-800 rounded w-64" />
          <div className="h-96 bg-slate-800 rounded" />
        </div>
      </div>
    }>
      <CedearsContent />
    </Suspense>
  )
}
