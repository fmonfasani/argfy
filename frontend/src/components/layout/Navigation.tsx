'use client'
import React, { useState } from 'react'
import { ThemeToggle } from './ThemeToggle'
import { RefreshCw } from 'lucide-react'

interface NavigationProps {
  lastUpdated?: Date | null
  isDataFresh?: boolean
  onRefresh?: () => void
}

export function Navigation({ lastUpdated, isDataFresh, onRefresh }: NavigationProps) {
  const [refreshing, setRefreshing] = useState(false)

  const handleRefresh = async () => {
    if (onRefresh && !refreshing) {
      setRefreshing(true)
      await onRefresh()
      setTimeout(() => setRefreshing(false), 1000)
    }
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo y navegación */}
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <svg className="h-8 w-8 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7v10c0 5.55 3.84 9.95 9 11 5.16-1.05 9-5.45 9-11V7l-10-5z"/>
              </svg>
              <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">Argfy</span>
              <span className="ml-2 px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                DEMO
              </span>
            </div>
            
            {/* Navegación desktop */}
            <div className="hidden md:ml-6 md:flex md:space-x-8">
              <a href="#economia" className="text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 px-1 pt-1 text-sm font-medium">
                Economía
              </a>
              <a href="#gobierno" className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 px-1 pt-1 text-sm font-medium">
                Gobierno
              </a>
              <a href="#finanzas" className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 px-1 pt-1 text-sm font-medium">
                Finanzas
              </a>
              <a href="#mercados" className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 px-1 pt-1 text-sm font-medium">
                Mercados
              </a>
              <a href="#tecnologia" className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 px-1 pt-1 text-sm font-medium">
                Tecnología
              </a>
              <a href="#industria" className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 px-1 pt-1 text-sm font-medium">
                Industria
              </a>
            </div>
          </div>
          
          {/* Controles derechos */}
          <div className="flex items-center space-x-4">
            {/* Status de datos */}
            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <span className={`w-2 h-2 rounded-full animate-pulse ${
                isDataFresh ? 'bg-green-500' : 'bg-yellow-500'
              }`}></span>
              <span className="hidden sm:inline">Datos en Vivo</span>
            </div>
            
            {/* Botón de refresh */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50"
              title="Actualizar datos"
            >
              <RefreshCw className={`w-5 h-5 text-gray-600 dark:text-gray-300 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
            
            {/* Toggle de tema */}
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  )
}