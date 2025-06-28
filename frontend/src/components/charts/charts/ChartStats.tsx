
'use client'
import React from 'react'
import { HistoricalData, Indicator } from '@/types'
import { formatValue } from '@/utils/formatters'

interface ChartStatsProps {
  data: HistoricalData[]
  indicator: Indicator
}

export function ChartStats({ data, indicator }: ChartStatsProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Estadísticas Históricas
        </h3>
        <p className="text-gray-500 dark:text-gray-400">No hay datos disponibles</p>
      </div>
    )
  }

  const values = data.map(d => d.value)
  const max = Math.max(...values)
  const min = Math.min(...values)
  const avg = values.reduce((sum, val) => sum + val, 0) / values.length
  const latest = values[values.length - 1]
  const change = values.length > 1 ? ((latest - values[0]) / values[0]) * 100 : 0

  const stats = [
    {
      label: 'Máximo (período):',
      value: formatValue(max, indicator.unit),
      color: 'text-green-600'
    },
    {
      label: 'Mínimo (período):',
      value: formatValue(min, indicator.unit),
      color: 'text-red-600'
    },
    {
      label: 'Promedio (período):',
      value: formatValue(avg, indicator.unit),
      color: 'text-blue-600'
    },
    {
      label: 'Cambio total:',
      value: `${change > 0 ? '+' : ''}${change.toFixed(1)}%`,
      color: change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-gray-600'
    },
    {
      label: 'Última actualización:',
      value: new Date().toLocaleDateString('es-AR'),
      color: 'text-gray-600'
    },
    {
      label: 'Puntos de datos:',
      value: data.length.toString(),
      color: 'text-gray-600'
    }
  ]

  return (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Estadísticas Históricas
      </h3>
      <div className="space-y-3">
        {stats.map((stat, index) => (
          <div key={index} className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</span>
            <span className={`text-sm font-medium ${stat.color}`}>{stat.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
