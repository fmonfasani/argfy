

'use client'
import React from 'react'
import { IndicatorCard } from './IndicatorCard'
import { Category, Indicator } from '@/types'
import { COLOR_SCHEMES } from '@/config/categories'

interface CategorySectionProps {
  category: Category
  data: Record<string, any>
  onIndicatorClick: (indicator: Indicator) => void
}

export function CategorySection({ category, data, onIndicatorClick }: CategorySectionProps) {
  const colorScheme = COLOR_SCHEMES[category.color as keyof typeof COLOR_SCHEMES]
  
  // Filtrar datos válidos y convertir a indicadores
  const indicators: Indicator[] = Object.entries(data)
    .filter(([key]) => !['timestamp', 'category'].includes(key))
    .map(([id, indicatorData]) => ({
      id,
      category: category.id,
      ...(indicatorData as any)
    }))

  if (indicators.length === 0) {
    return null
  }

  return (
    <section id={category.id} className="scroll-mt-20">
      {/* Header de la Sección */}
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          {category.title}
        </h2>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          {category.description}
        </p>
        
        {/* Timestamp de la categoría */}
        {data.timestamp && (
          <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
            Última actualización: {new Date(data.timestamp).toLocaleTimeString('es-AR')}
          </div>
        )}
      </div>

      {/* Grid de Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {indicators.map((indicator) => (
          <IndicatorCard
            key={indicator.id}
            indicator={indicator}
            colorScheme={colorScheme}
            onClick={() => onIndicatorClick(indicator)}
          />
        ))}
      </div>

      {/* Enlace a siguiente sección */}
      <div className="text-center mt-8">
        <a 
          href={`#${getNextCategoryId(category.id)}`}
          className={`inline-flex items-center ${colorScheme.accent} hover:${colorScheme.text}`}
        >
          Ver {getNextCategoryName(category.id)}
          <svg className="w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"/>
          </svg>
        </a>
      </div>
    </section>
  )
}

// Helper functions
function getNextCategoryId(currentId: string): string {
  const categories = Object.keys(CATEGORIES)
  const currentIndex = categories.indexOf(currentId)
  const nextIndex = (currentIndex + 1) % categories.length
  return categories[nextIndex]
}

function getNextCategoryName(currentId: string): string {
  const nextId = getNextCategoryId(currentId)
  return CATEGORIES[nextId].title
}