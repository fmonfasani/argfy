'use client'
import React from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'
import { HistoricalData, ChartConfig, Indicator } from '@/types'
import { formatValue } from '@/utils/formatters'

interface HistoricalChartProps {
  data: HistoricalData[]
  config: ChartConfig
  indicator: Indicator
}

export function HistoricalChart({ data, config, indicator }: HistoricalChartProps) {
  // Preparar datos para Recharts
  const chartData = data.map(point => ({
    ...point,
    date: new Date(point.date).toLocaleDateString('es-AR', {
      month: 'short',
      day: 'numeric'
    }),
    formattedValue: formatValue(point.value, indicator.unit)
  }))

  // Calcular promedio para línea de referencia
  const average = data.length > 0 
    ? data.reduce((sum, point) => sum + point.value, 0) / data.length
    : 0

  // Configuración de colores
  const colors = {
    line: '#3B82F6',
    area: '#3B82F6',
    areaFill: 'rgba(59, 130, 246, 0.1)',
    bar: '#6366F1',
    grid: '#E5E7EB',
    reference: '#F59E0B'
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">{label}</p>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.formattedValue}
          </p>
          <p className="text-xs text-gray-500">
            {indicator.source} • {indicator.name}
          </p>
        </div>
      )
    }
    return null
  }

  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    }

    const axisProps = {
      xAxis: {
        dataKey: 'date',
        axisLine: false,
        tickLine: false,
        tick: { fontSize: 12, fill: '#6B7280' }
      },
      yAxis: {
        axisLine: false,
        tickLine: false,
        tick: { fontSize: 12, fill: '#6B7280' },
        domain: ['dataMin - dataMin*0.05', 'dataMax + dataMax*0.05']
      }
    }

    switch (config.type) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            {config.showGrid && <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />}
            <XAxis {...axisProps.xAxis} />
            <YAxis {...axisProps.yAxis} />
            {config.showTooltip && <Tooltip content={<CustomTooltip />} />}
            <ReferenceLine y={average} stroke={colors.reference} strokeDasharray="5 5" />
            <Area
              type="monotone"
              dataKey="value"
              stroke={colors.area}
              fill={colors.areaFill}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: colors.area }}
              animationDuration={config.animate ? 1000 : 0}
            />
          </AreaChart>
        )

      case 'bar':
        return (
          <BarChart {...commonProps}>
            {config.showGrid && <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />}
            <XAxis {...axisProps.xAxis} />
            <YAxis {...axisProps.yAxis} />
            {config.showTooltip && <Tooltip content={<CustomTooltip />} />}
            <ReferenceLine y={average} stroke={colors.reference} strokeDasharray="5 5" />
            <Bar
              dataKey="value"
              fill={colors.bar}
              radius={[2, 2, 0, 0]}
              animationDuration={config.animate ? 1000 : 0}
            />
          </BarChart>
        )

      default: // line
        return (
          <LineChart {...commonProps}>
            {config.showGrid && <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />}
            <XAxis {...axisProps.xAxis} />
            <YAxis {...axisProps.yAxis} />
            {config.showTooltip && <Tooltip content={<CustomTooltip />} />}
            <ReferenceLine y={average} stroke={colors.reference} strokeDasharray="5 5" />
            <Line
              type="monotone"
              dataKey="value"
              stroke={colors.line}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: colors.line }}
              animationDuration={config.animate ? 1000 : 0}
            />
          </LineChart>
        )
    }
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      {renderChart()}
    </ResponsiveContainer>
  )
}