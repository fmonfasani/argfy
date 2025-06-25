// frontend/src/components/DashboardModal.tsx
'use client'
import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface DashboardModalProps {
  isOpen: boolean
  onClose: () => void
}

interface IndicatorData {
  indicator_type: string
  value: number
  source: string
  date: string
}

interface ChartData {
  date: string
  value: number
}

export default function DashboardModal({ isOpen, onClose }: DashboardModalProps) {
  const [indicators, setIndicators] = useState<IndicatorData[]>([])
  const [historicalData, setHistoricalData] = useState<{[key: string]: ChartData[]}>({})
  const [loading, setLoading] = useState(true)
  const [selectedIndicator, setSelectedIndicator] = useState('dolar_blue')

  useEffect(() => {
    if (isOpen) {
      fetchDashboardData()
    }
  }, [isOpen])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch current indicators
      const indicatorsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/indicators/current`)
      const indicatorsData = await indicatorsResponse.json()
      setIndicators(indicatorsData.data || [])

      // Fetch historical data for key indicators
      const keyIndicators = ['dolar_blue', 'riesgo_pais', 'inflacion_mensual', 'reservas_bcra']
      const historicalPromises = keyIndicators.map(async (indicator) => {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/indicators/historical/${indicator}?days=30`)
          const data = await response.json()
          return { indicator, data: data.data || [] }
        } catch (error) {
          console.error(`Error fetching ${indicator}:`, error)
          return { indicator, data: [] }
        }
      })

      const historicalResults = await Promise.all(historicalPromises)
      const historicalMap: {[key: string]: ChartData[]} = {}
      
      historicalResults.forEach(({ indicator, data }) => {
        historicalMap[indicator] = data
      })
      
      setHistoricalData(historicalMap)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getDisplayValue = (indicator: IndicatorData) => {
    switch (indicator.indicator_type) {
      case 'dolar_blue':
      case 'dolar_oficial':
        return `$${Math.round(indicator.value).toLocaleString()}`
      case 'inflacion_mensual':
        return `${indicator.value.toFixed(1)}%`
      case 'reservas_bcra':
        return `$${(indicator.value / 1000).toFixed(1)}B`
      case 'riesgo_pais':
        return `${Math.round(indicator.value)}`
      default:
        return indicator.value.toLocaleString()
    }
  }

  const getIndicatorColor = (type: string) => {
    const colors = {
      'dolar_blue': 'text-emerald-600',
      'inflacion_mensual': 'text-red-600', 
      'reservas_bcra': 'text-emerald-600',
      'riesgo_pais': 'text-amber-600'
    }
    return colors[type as keyof typeof colors] || 'text-slate-700'
  }

  const getChartColor = (type: string) => {
    const colors = {
      'dolar_blue': '#059669',
      'inflacion_mensual': '#dc2626',
      'reservas_bcra': '#059669', 
      'riesgo_pais': '#d97706'
    }
    return colors[type as keyof typeof colors] || '#2563eb'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 transition-opacity bg-slate-900 bg-opacity-75"
          onClick={onClose}
        ></div>

        {/* Modal panel */}
        <div className="inline-block w-full max-w-7xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
            <div>
              <h2 className="text-2xl font-bold text-slate-800">📈 Dashboard Interactivo</h2>
              <p className="text-slate-600">Todos los indicadores en tiempo real</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-8 max-h-[80vh] overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <>
                {/* Quick Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                  {indicators.slice(0, 4).map((indicator) => (
                    <div key={indicator.indicator_type} className="bg-slate-50 rounded-lg p-6 text-center border border-slate-200">
                      <div className={`text-2xl font-bold ${getIndicatorColor(indicator.indicator_type)}`}>
                        {getDisplayValue(indicator)}
                      </div>
                      <div className="text-sm text-slate-600 mt-1">
                        {indicator.indicator_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        {indicator.source}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Chart Selection */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">Gráficos Históricos</h3>
                  <div className="flex space-x-2 mb-4">
                    {Object.keys(historicalData).map((indicator) => (
                      <button
                        key={indicator}
                        onClick={() => setSelectedIndicator(indicator)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          selectedIndicator === indicator
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                        }`}
                      >
                        {indicator.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Chart */}
                <div className="bg-slate-50 rounded-lg p-6 border border-slate-200">
                  <h4 className="text-md font-semibold text-slate-800 mb-4">
                    {selectedIndicator.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} - Últimos 30 días
                  </h4>
                  
                  {historicalData[selectedIndicator] && historicalData[selectedIndicator].length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={historicalData[selectedIndicator]}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis 
                          dataKey="date" 
                          stroke="#64748b"
                          fontSize={12}
                        />
                        <YAxis 
                          stroke="#64748b"
                          fontSize={12}
                        />
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: '#f8fafc',
                            border: '1px solid #e2e8f0',
                            borderRadius: '8px'
                          }}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke={getChartColor(selectedIndicator)}
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 4, fill: getChartColor(selectedIndicator) }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-64 flex items-center justify-center text-slate-500">
                      No hay datos históricos disponibles
                    </div>
                  )}
                </div>

                {/* All Indicators Table */}
                <div className="mt-8">
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">Todos los Indicadores</h3>
                  <div className="bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-slate-100">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                              Indicador
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                              Valor
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                              Fuente
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                              Última actualización
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200">
                          {indicators.map((indicator, index) => (
                            <tr key={indicator.indicator_type} className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                                {indicator.indicator_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </td>
                              <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${getIndicatorColor(indicator.indicator_type)}`}>
                                {getDisplayValue(indicator)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                                {indicator.source}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                                {new Date(indicator.date).toLocaleString('es-AR')}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-200 bg-slate-50">
            <div className="flex justify-between items-center">
              <p className="text-sm text-slate-600">
                Demo v0.1 - Datos actualizados en tiempo real
              </p>
              <button
                onClick={onClose}
                className="px-6 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 transition-colors"
              >
                Cerrar Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}