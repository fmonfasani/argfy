'use client'
import React from 'react'
import { Sparkline } from './Sparkline'
import { Badge } from '../ui/Badge'
import { Indicator } from '@/types'
import { formatValue, formatChange, getSourceBadgeColor } from '@/utils/formatters'

interface IndicatorCardProps {
  indicator: Indicator
  colorScheme: any
  onClick: () => void
}

export function IndicatorCard({ indicator, colorScheme, onClick }: IndicatorCardProps) {
  const changeInfo = indicator.changePercent ? formatChange(indicator.changePercent) : null
  
  return (
    <div 
      onClick={onClick}
      className={`
        ${colorScheme.bg} ${colorScheme.border}
        rounded-xl shadow-sm border p-6 hover:shadow-lg 
        transition-all cursor-pointer group
        hover:scale-[1.02] transform
      `}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          {/* Título del indicador */}
          <p className={`text-sm font-medium ${colorScheme.text} opacity-80`}>
            {indicator.name || indicator.id.replace(/_/g, ' ').toUpperCase()}
          </p>
          
          {/* Valor principal */}
          <p className={`text-3xl font-bold ${colorScheme.text} group-hover:${colorScheme.accent} transition-colors`}>
            {formatValue(indicator.value, indicator.unit || '')}
          </p>
          
          {/* Cambio y tendencia */}
          <div className="flex items-center mt-2 space-x-2">
            {changeInfo && (
              <>
                <svg className={`w-4 h-4 ${changeInfo.color}`} fill="currentColor" viewBox="0 0 20 20">
                  {indicator.trend === 'up' ? (
                    <path d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z"/>
                  ) : indicator.trend === 'down' ? (
                    <path d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z"/>
                  ) : (
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                  )}
                </svg>
                <span className={`text-sm ${changeInfo.color}`}>
                  {changeInfo.text}
                </span>
              </>
            )}
            
            {/* Frecuencia de actualización */}
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {getFrequencyLabel(indicator.frequency)}
            </span>
          </div>
        </div>
        
        {/* Panel derecho */}
        <div className="text-right">
          {/* Badge de fuente */}
          <Badge className={getSourceBadgeColor(indicator.source)}>
            {indicator.source}
          </Badge>
          
          {/* Sparkline */}
          <div className="mt-2">
            <Sparkline 
              data={generateSparklineData(indicator)} 
              color={colorScheme.accent}
              width={60}
              height={24}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper functions
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

function generateSparklineData(indicator: Indicator): number[] {
  // Generar datos demo para el sparkline basado en el tipo de indicador
  const baseValue = typeof indicator.value === 'number' ? indicator.value : 100
  const points = 8
  const data = []
  
  for (let i = 0; i < points; i++) {
    const variation = (Math.random() - 0.5) * 0.1 * baseValue
    data.push(baseValue + variation)
  }
  
  // El último punto debe ser el valor actual
  data[data.length - 1] = typeof indicator.value === 'number' ? indicator.value : baseValue
  
  return data
}
