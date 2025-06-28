'use client'
import React, { useState, useEffect } from 'react'
import { X, Download, Edit, TrendingUp, TrendingDown } from 'lucide-react'
import { HistoricalChart } from '../charts/HistoricalChart'
import { ChartControls } from '../charts/ChartControls'
import { ChartStats } from '../charts/ChartStats'
import { Badge } from '../ui/Badge'
import { LoadingSpinner } from '../ui/LoadingSpinner'
import { Indicator, HistoricalData, ChartConfig } from '@/types'
import { formatValue, getSourceBadgeColor } from '@/utils/formatters'
import { api } from '@/lib/api'

interface IndicatorModalProps {
  indicator: Indicator
  isOpen: boolean
  onClose: () => void
}

export function IndicatorModal({ indicator, isOpen, onClose }: IndicatorModalProps) {
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [chartConfig, setChartConfig] = useState<ChartConfig>({
    type: 'line',
    period: '1Y',
    showGrid: true,
    showTooltip: true,
    animate: true
  })

  // Fetch historical data when modal opens
  useEffect(() => {
    if (isOpen && indicator) {
      fetchHistoricalData()
    }
  }, [isOpen, indicator, chartConfig.period])

  const fetchHistoricalData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const days = getPeriodDays(chartConfig.period)
      const response = await api.getHistorical(indicator.id, days)
      
      if (response.data.status === 'success') {
        setHistoricalData(response.data.historical_data || [])
      } else {
        setError('Error fetching historical data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching historical data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    // Implementar descarga de datos
    const dataStr = JSON.stringify(historicalData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${indicator.id}_historical_data.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      onClose()
    }
  }

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'auto'
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'auto'
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Modal Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                📈 {indicator.name} - Argentina
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {indicator.description} • Actualizado: {new Date().toLocaleTimeString('es-AR')}
              </p>
            </div>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Current Value Display */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-8 w-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582z"/>
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Valor Actual</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatValue(indicator.value, indicator.unit)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingUp className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Variación 1M</p>
                  <p className="text-2xl font-bold text-green-600">
                    {indicator.changePercent ? `${indicator.changePercent > 0 ? '+' : ''}${indicator.changePercent.toFixed(1)}%` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingDown className="h-8 w-8 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Frecuencia</p>
                  <p className="text-2xl font-bold text-yellow-600">
                    {getFrequencyLabel(indicator.frequency)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-8 w-8 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Fuente</p>
                  <div className="text-2xl font-bold">
                    <Badge className={getSourceBadgeColor(indicator.source)}>
                      {indicator.source}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Chart Controls */}
          <ChartControls
            config={chartConfig}
            onChange={setChartConfig}
            indicator={indicator}
          />

          {/* Main Chart */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {indicator.name} - Evolución Histórica
              </h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleDownload}
                  className="text-xs px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  <Download className="w-3 h-3 inline mr-1" />
                  Descargar
                </button>
                <button className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
                  <Edit className="w-3 h-3 inline mr-1" />
                  Editar
                </button>
              </div>
            </div>

            {loading ? (
              <div className="h-80 flex items-center justify-center">
                <LoadingSpinner size="large" />
              </div>
            ) : error ? (
              <div className="h-80 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-red-600 dark:text-red-400">{error}</p>
                  <button 
                    onClick={fetchHistoricalData}
                    className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    Reintentar
                  </button>
                </div>
              </div>
            ) : (
              <div className="h-80 relative">
                <HistoricalChart
                  data={historicalData}
                  config={chartConfig}
                  indicator={indicator}
                />
              </div>
            )}

            <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
              <p>Fuente: {indicator.source} via Argfy®</p>
              <p className="italic">Las áreas sombreadas indican períodos de volatilidad económica.</p>
            </div>
          </div>

          {/* Additional Statistics and Related Indicators */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartStats 
              data={historicalData} 
              indicator={indicator}
            />
            
            <RelatedIndicators 
              category={indicator.category}
              currentIndicator={indicator.id}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper functions
function getPeriodDays(period: string): number {
  const periodMap: Record<string, number> = {
    '1D': 1,
    '1W': 7,
    '1M': 30,
    '3M': 90,
    '6M': 180,
    '1Y': 365,
    'MAX': 730 // 2 años como máximo
  }
  return periodMap[period] || 365
}

function getFrequencyLabel(frequency: string): string {
  const labels: Record<string, string> = {
    'real_time': 'Tiempo real',
    'daily': 'Diario',
    'weekly': 'Semanal',
    'monthly': 'Mensual',
    'quarterly': 'Trimestral',
    'yearly': 'Anual'
  }
  return labels[frequency] || frequency
}