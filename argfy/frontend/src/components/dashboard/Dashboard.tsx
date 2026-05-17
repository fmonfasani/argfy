'use client'
import React, { useState } from 'react'
import { useIndicators } from '@/hooks/useIndicators'
import { CategorySection } from './CategorySection'
import { Navigation } from '../layout/Navigation'
import { LoadingSpinner } from '../ui/LoadingSpinner'
import { ErrorBoundary } from '../ui/ErrorBoundary'
import { IndicatorModal } from '../modal/IndicatorModal'
import { CATEGORIES } from '@/config/categories'
import { Indicator } from '@/types'

export default function Dashboard() {
  const { data, loading, error, lastUpdated, refreshData, isDataFresh } = useIndicators()
  const [selectedIndicator, setSelectedIndicator] = useState<Indicator | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const handleIndicatorClick = (indicator: Indicator) => {
    setSelectedIndicator(indicator)
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setSelectedIndicator(null)
  }

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navigation />
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="large" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h3 className="text-red-800 font-semibold">Error cargando datos</h3>
            <p className="text-red-600">{error}</p>
            <button 
              onClick={refreshData}
              className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
        <Navigation 
          lastUpdated={lastUpdated} 
          isDataFresh={isDataFresh}
          onRefresh={refreshData}
        />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Header del Dashboard */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Datos Económicos Argentinos
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Indicadores en tiempo real desde fuentes oficiales
            </p>
            
            {/* Status bar */}
            <div className="flex items-center space-x-4 mt-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full animate-pulse ${
                  isDataFresh ? 'bg-green-500' : 'bg-yellow-500'
                }`}></div>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {isDataFresh ? 'Datos actualizados' : 'Actualizando...'}
                </span>
              </div>
              
              {lastUpdated && (
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Última actualización: {lastUpdated.toLocaleTimeString('es-AR')}
                </span>
              )}
            </div>
          </div>

          {/* Secciones de Categorías */}
          <div className="space-y-12">
            {Object.entries(CATEGORIES).map(([categoryId, categoryConfig]) => (
              <CategorySection
                key={categoryId}
                category={categoryConfig}
                data={data?.[categoryId as keyof typeof data] || {}}
                onIndicatorClick={handleIndicatorClick}
              />
            ))}
          </div>
        </main>

        {/* Modal de Indicador */}
        {selectedIndicator && (
          <IndicatorModal
            indicator={selectedIndicator}
            isOpen={modalOpen}
            onClose={closeModal}
          />
        )}
      </div>
    </ErrorBoundary>
  )
}
