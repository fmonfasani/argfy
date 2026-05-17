'use client'
import React, { useState, useEffect } from 'react'
import { Indicator } from '@/types'
import { formatValue } from '@/utils/formatters'
import { api } from '@/lib/api'

interface RelatedIndicatorsProps {
  category: string
  currentIndicator: string
}

function RelatedIndicators({ category, currentIndicator }: RelatedIndicatorsProps) {
  const [relatedIndicators, setRelatedIndicators] = useState<Indicator[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRelatedIndicators()
  }, [category, currentIndicator])

  const fetchRelatedIndicators = async () => {
    try {
      setLoading(true)
      const response = await api.getCategory(category)
      
      if (response.data.status === 'success') {
        const indicators = Object.entries(response.data.data)
          .filter(([key]) => key !== currentIndicator && !['timestamp', 'category'].includes(key))
          .map(([id, data]) => ({ id, ...(data as any) }))
          .slice(0, 4) // Mostrar solo 4 relacionados
        
        setRelatedIndicators(indicators)
      }
    } catch (error) {
      console.error('Error fetching related indicators:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Indicadores Relacionados
      </h3>
      
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4 mb-2"></div>
              <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {relatedIndicators.map((indicator) => (
            <div 
              key={indicator.id}
              className="flex items-center justify-between p-3 bg-white dark:bg-gray-600 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-500 transition-colors"
              onClick={() => window.open(`#${indicator.id}`, '_self')}
            >
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {indicator.name || indicator.id.replace(/_/g, ' ')}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {indicator.description}
                </p>
              </div>
              <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                {formatValue(indicator.value, indicator.unit)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
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