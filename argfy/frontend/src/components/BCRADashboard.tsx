// frontend/src/components/BCRADashboard.tsx
'use client'
import { useBCRAReal } from '@/hooks/useBCRAReal'
import { RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'

export function BCRADashboard() {
  const { data, loading, error, lastUpdated, refreshData, isDataFresh } = useBCRAReal()

  if (loading && !data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white rounded-lg p-6 shadow animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold">Error cargando datos BCRA</h3>
        <p className="text-red-600">{error}</p>
        <button 
          onClick={refreshData}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Reintentar
        </button>
      </div>
    )
  }

  const indicators = data?.indicadores_principales || {}
  const cotizaciones = data?.cotizaciones || {}

  return (
    <div className="space-y-6">
      {/* Header con timestamp */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">
          Datos BCRA en Tiempo Real
        </h2>
        <div className="flex items-center space-x-4">
          <span className={`text-sm ${isDataFresh ? 'text-green-600' : 'text-amber-600'}`}>
            {lastUpdated ? `Actualizado: ${lastUpdated.toLocaleTimeString()}` : 'Sin datos'}
          </span>
          <button
            onClick={refreshData}
            disabled={loading}
            className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Indicadores Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(indicators).map(([key, indicator]: [string, any]) => (
          <div key={key} className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-gray-600">{indicator.label}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {key.includes('reservas') 
                    ? `US$${indicator.value?.toLocaleString()}M`
                    : key.includes('tasa') || key.includes('inflacion')
                    ? `${indicator.value}%`
                    : `$${indicator.value?.toLocaleString()}`
                  }
                </p>
                <p className="text-xs text-gray-500">
                  BCRA • {indicator.updated}
                </p>
              </div>
              <div className="text-green-500">
                <TrendingUp className="w-5 h-5" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Cotizaciones */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Cotizaciones Oficiales</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {Object.entries(cotizaciones).map(([moneda, data]: [string, any]) => (
            <div key={moneda} className="text-center p-3 bg-gray-50 rounded">
              <p className="font-semibold text-gray-900">{moneda}</p>
              <p className="text-lg font-bold text-blue-600">
                ${data.value?.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500">BCRA</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer con info de fuente */}
      <div className="text-center text-sm text-gray-500">
        Datos oficiales del Banco Central de la República Argentina (BCRA) • 
        Actualización automática cada 15 minutos
      </div>
    </div>
  )
}