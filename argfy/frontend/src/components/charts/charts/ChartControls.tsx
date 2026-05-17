
'use client'
import React from 'react'
import { ChartConfig, Indicator } from '@/types'

interface ChartControlsProps {
  config: ChartConfig
  onChange: (config: ChartConfig) => void
  indicator: Indicator
}

export function ChartControls({ config, onChange, indicator }: ChartControlsProps) {
  const updateConfig = (updates: Partial<ChartConfig>) => {
    onChange({ ...config, ...updates })
  }

  const periodButtons = [
    { key: '1D', label: '1D' },
    { key: '1W', label: '1W' },
    { key: '1M', label: '1M' },
    { key: '3M', label: '3M' },
    { key: '6M', label: '6M' },
    { key: '1Y', label: '1Y' },
    { key: 'MAX', label: 'MAX' }
  ]

  const chartTypes = [
    { key: 'line', label: 'Línea' },
    { key: 'area', label: 'Área' },
    { key: 'bar', label: 'Barras' }
  ]

  return (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Configuración del Gráfico
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500 dark:text-gray-400">Actualización:</span>
          <select 
            className="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
            value={indicator.frequency}
            disabled
          >
            <option value={indicator.frequency}>
              {getFrequencyLabel(indicator.frequency)}
            </option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Período */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Período:
          </label>
          <div className="flex flex-wrap gap-1">
            {periodButtons.map(({ key, label }) => (
              <button
                key={key}
                onClick={() => updateConfig({ period: key as any })}
                className={`px-3 py-1 text-xs rounded ${
                  config.period === key
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Tipo de gráfico */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Tipo:
          </label>
          <select
            value={config.type}
            onChange={(e) => updateConfig({ type: e.target.value as any })}
            className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
          >
            {chartTypes.map(({ key, label }) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {/* Rango de fechas */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Desde:
          </label>
          <input
            type="date"
            defaultValue="2024-06-27"
            className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Hasta:
          </label>
          <input
            type="date"
            defaultValue={new Date().toISOString().split('T')[0]}
            className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
          />
        </div>
      </div>

      {/* Opciones adicionales */}
      <div className="mt-4 flex items-center space-x-6">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={config.showGrid}
            onChange={(e) => updateConfig({ showGrid: e.target.checked })}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Mostrar grilla</span>
        </label>
        
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={config.showTooltip}
            onChange={(e) => updateConfig({ showTooltip: e.target.checked })}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Mostrar tooltip</span>
        </label>
        
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={config.animate}
            onChange={(e) => updateConfig({ animate: e.target.checked })}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Animaciones</span>
        </label>
      </div>
    </div>
  )
}