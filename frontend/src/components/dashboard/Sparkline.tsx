
'use client'
import React from 'react'

interface SparklineProps {
  data: number[]
  color?: string
  width?: number
  height?: number
  strokeWidth?: number
  className?: string
}

export function Sparkline({ 
  data, 
  color = '#3B82F6', 
  width = 60, 
  height = 24, 
  strokeWidth = 2,
  className = ''
}: SparklineProps) {
  if (!data || data.length < 2) {
    return <div className={`w-${width} h-${height} ${className}`} />
  }

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  // Generar puntos del path
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * (width - 4) + 2
    const y = height - 2 - ((value - min) / range) * (height - 4)
    return `${x},${y}`
  }).join(' ')

  // Determinar color basado en tendencia
  const trend = data[data.length - 1] > data[0] ? 'up' : 'down'
  const strokeColor = trend === 'up' ? '#10B981' : trend === 'down' ? '#EF4444' : color

  return (
    <svg 
      width={width} 
      height={height} 
      className={`${className} opacity-60 group-hover:opacity-100 transition-opacity`}
      viewBox={`0 0 ${width} ${height}`}
    >
      <polyline
        fill="none"
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
      
      {/* Punto final destacado */}
      {(() => {
        const lastIndex = data.length - 1
        const x = (lastIndex / (data.length - 1)) * (width - 4) + 2
        const y = height - 2 - ((data[lastIndex] - min) / range) * (height - 4)
        return (
          <circle
            cx={x}
            cy={y}
            r={2}
            fill={strokeColor}
            className="opacity-80"
          />
        )
      })()}
    </svg>
  )
}