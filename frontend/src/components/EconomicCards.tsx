// frontend/src/components/EconomicCards.tsx
'use client'

import { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  RefreshCw, 
  Activity,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react'

// Tipos TypeScript para las Cards
interface EconomicCard {
  id: string
  title: string
  value: number
  previous_value?: number
  unit: string
  category: string
  status: 'fresh' | 'recent' | 'stale' | 'error'
  change_percent?: number
  change_absolute?: number
  trend: 'up' | 'down' | 'stable'
  last_updated: string
  source: string
  description: string
  icon: string
  color_theme: string
  sparkline_data: number[]
  is_fresh: boolean
  minutes_since_update: number
}

interface HistoricalData {
  indicator_id: string
  title: string
  data_points: {
    date: string
    timestamp: string
    value: number
  }[]
  statistics: {
    current: number
    previous: number
    change_percent: number
    volatility: number
    trend: string
  }
  chart_config: {
    type: string
    smooth: boolean
    gradient: boolean
    color_theme: string
  }
}

// Hook personalizado para obtener cards
function useEconomicCards() {
  const [cards, setCards] = useState<EconomicCard[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchCards = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/cards/`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status === 'success') {
        setCards(result.data)
        setLastUpdated(new Date())
        setError(null)
      } else {
        throw new Error('Error en respuesta del servidor')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      console.error('Error fetching cards:', err)
    } finally {
      setLoading(false)
    }
  }

  const refreshCards = async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/cards/refresh`, {
        method: 'POST'
      })
      // Esperar un poco y luego refrescar
      setTimeout(fetchCards, 2000)
    } catch (err) {
      console.error('Error refreshing cards:', err)
    }
  }

  useEffect(() => {
    fetchCards()
    
    // Auto-refresh cada 5 minutos
    const interval = setInterval(fetchCards, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  return {
    cards,
    loading,
    error,
    lastUpdated,
    refreshCards,
    fetchCards
  }
}

// Componente Sparkline mini
function Sparkline({ data, color }: { data: number[], color: string }) {
  if (!data || data.length < 2) return null

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100
    const y = 100 - ((value - min) / range) * 100
    return `${x},${y}`
  }).join(' ')

  return (
    <div className="w-16 h-8">
      <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          className="opacity-60"
        />
      </svg>
    </div>
  )
}

// Componente Card Individual
function EconomicCardComponent({ 
  card, 
  onClick 
}: { 
  card: EconomicCard
  onClick: () => void 
}) {
  const getTrendIcon = () => {
    switch (card.trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />
      default:
        return <Minus className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusIcon = () => {
    switch (card.status) {
      case 'fresh':
        return <CheckCircle className="w-3 h-3 text-green-500" />
      case 'recent':
        return <Clock className="w-3 h-3 text-yellow-500" />
      case 'stale':
        return <AlertCircle className="w-3 h-3 text-orange-500" />
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-500" />
    }
  }

  const getColorClasses = (theme: string) => {
    const colors = {
      blue: 'border-blue-200 bg-blue-50 hover:bg-blue-100',
      purple: 'border-purple-200 bg-purple-50 hover:bg-purple-100',
      green: 'border-green-200 bg-green-50 hover:bg-green-100',
      red: 'border-red-200 bg-red-50 hover:bg-red-100',
      yellow: 'border-yellow-200 bg-yellow-50 hover:bg-yellow-100'
    }
    return colors[theme as keyof typeof colors] || colors.blue
  }

  const formatValue = (value: number, unit: string) => {
    if (unit === 'USD M') {
      return `US$${value.toLocaleString()}M`
    } else if (unit === 'Points') {
      return value.toLocaleString()
    } else if (unit === '%' || unit === 'pb') {
      return `${value}${unit}`
    } else {
      return `$${value.toLocaleString()}`
    }
  }

  const sparklineColor = {
    blue: '#3b82f6',
    purple: '#8b5cf6',
    green: '#10b981',
    red: '#ef4444',
    yellow: '#f59e0b'
  }[card.color_theme] || '#3b82f6'

  return (
    <div
      onClick={onClick}
      className={`
        p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 
        transform hover:scale-105 hover:shadow-lg
        ${getColorClasses(card.color_theme)}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{card.icon}</span>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">{card.title}</h3>
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              {getStatusIcon()}
              <span>{card.source}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {getTrendIcon()}
          <Sparkline data={card.sparkline_data} color={sparklineColor} />
        </div>
      </div>

      {/* Valor Principal */}
      <div className="mb-2">
        <div className="text-2xl font-bold text-gray-900">
          {formatValue(card.value, card.unit)}
        </div>
        
        {/* Cambio */}
        {card.change_percent !== null && card.change_percent !== undefined && (
          <div className={`
            text-sm font-medium
            ${card.change_percent > 0 ? 'text-green-600' : 
              card.change_percent < 0 ? 'text-red-600' : 'text-gray-600'}
          `}>
            {card.change_percent > 0 ? '+' : ''}{card.change_percent.toFixed(2)}%
            {card.change_absolute && (
              <span className="text-gray-500 ml-1">
                ({card.change_absolute > 0 ? '+' : ''}{card.change_absolute.toFixed(2)})
              </span>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center text-xs text-gray-500">
        <span>{card.description}</span>
        <span>{card.minutes_since_update}min ago</span>
      </div>
    </div>
  )
}

// Modal para Gráfico Histórico
function HistoricalModal({ 
  card, 
  isOpen, 
  onClose 
}: { 
  card: EconomicCard | null
  isOpen: boolean
  onClose: () => void 
}) {
  const [historicalData, setHistoricalData] = useState<HistoricalData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen && card) {
      fetchHistoricalData()
    }
  }, [isOpen, card])

  const fetchHistoricalData = async () => {
    if (!card) return

    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/cards/${card.id}/historical?days=30&chart_type=line`
      )
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status === 'success') {
        setHistoricalData(result.historical_data)
      } else {
        throw new Error('Error obteniendo datos históricos')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen || !card) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-3xl">{card.icon}</span>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{card.title}</h2>
                <p className="text-gray-600">{card.description}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Contenido */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : error ? (
            <div className="text-center text-red-600 p-8">
              <AlertCircle className="w-12 h-12 mx-auto mb-4" />
              <p>Error cargando datos históricos</p>
              <p className="text-sm text-gray-500">{error}</p>
              <button
                onClick={fetchHistoricalData}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Reintentar
              </button>
            </div>
          ) : historicalData ? (
            <div className="space-y-6">
              {/* Estadísticas */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Actual</div>
                  <div className="text-xl font-bold">
                    {historicalData.statistics.current.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Cambio 30d</div>
                  <div className={`text-xl font-bold ${
                    historicalData.statistics.change_percent > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {historicalData.statistics.change_percent > 0 ? '+' : ''}
                    {historicalData.statistics.change_percent.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Volatilidad</div>
                  <div className="text-xl font-bold">
                    {historicalData.statistics.volatility.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Tendencia</div>
                  <div className="flex items-center space-x-1">
                    {historicalData.statistics.trend === 'up' ? (
                      <TrendingUp className="w-5 h-5 text-green-500" />
                    ) : historicalData.statistics.trend === 'down' ? (
                      <TrendingDown className="w-5 h-5 text-red-500" />
                    ) : (
                      <Minus className="w-5 h-5 text-gray-500" />
                    )}
                    <span className="capitalize font-bold">
                      {historicalData.statistics.trend}
                    </span>
                  </div>
                </div>
              </div>

              {/* Gráfico Placeholder */}
              <div className="bg-gray-50 p-8 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">
                  Gráfico Histórico - {historicalData.title}
                </h3>
                <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
                  <div className="text-center text-gray-500">
                    <Activity className="w-12 h-12 mx-auto mb-2" />
                    <p>Gráfico elegante aquí</p>
                    <p className="text-sm">
                      {historicalData.data_points.length} puntos de datos disponibles
                    </p>
                    <p className="text-xs mt-2">
                      Integrar con Recharts o Chart.js para visualización suave
                    </p>
                  </div>
                </div>
              </div>

              {/* Info adicional */}
              <div className="text-sm text-gray-500 text-center">
                Datos de {historicalData.data_points[0]?.date} a {historicalData.data_points[historicalData.data_points.length - 1]?.date}
                • Fuente: {card.source}
                • Última actualización: {new Date(card.last_updated).toLocaleString()}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}

// Componente Principal de Cards Económicas
export default function EconomicCards() {
  const { cards, loading, error, lastUpdated, refreshCards } = useEconomicCards()
  const [selectedCard, setSelectedCard] = useState<EconomicCard | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const categories = [
    { value: 'all', label: 'Todas' },
    { value: 'exchange', label: 'Divisas' },
    { value: 'monetary', label: 'Monetario' },
    { value: 'inflation', label: 'Inflación' },
    { value: 'market', label: 'Mercados' },
    { value: 'risk', label: 'Riesgo' },
    { value: 'reserves', label: 'Reservas' }
  ]

  const filteredCards = selectedCategory === 'all' 
    ? cards 
    : cards.filter(card => card.category === selectedCategory)

  const handleCardClick = (card: EconomicCard) => {
    setSelectedCard(card)
    setModalOpen(true)
  }

  if (loading && cards.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-gray-200 p-6 rounded-xl">
              <div className="h-4 bg-gray-300 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-gray-300 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-300 rounded w-full"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">
          Error cargando Cards Económicas
        </h3>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={refreshCards}
          className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Reintentar
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Cards Económicas</h2>
          <p className="text-gray-600">
            Indicadores en tiempo real con gráficos históricos
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <span className="text-sm text-gray-500">
              Actualizado: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={refreshCards}
            disabled={loading}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-2">
        {categories.map(category => (
          <button
            key={category.value}
            onClick={() => setSelectedCategory(category.value)}
            className={`
              px-4 py-2 rounded-full text-sm font-medium transition-colors
              ${selectedCategory === category.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
          >
            {category.label}
          </button>
        ))}
      </div>

      {/* Grid de Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {filteredCards.map(card => (
          <EconomicCardComponent
            key={card.id}
            card={card}
            onClick={() => handleCardClick(card)}
          />
        ))}
      </div>

      {/* Footer Info */}
      <div className="text-center text-sm text-gray-500 p-4">
        {filteredCards.length} cards mostrando datos de BCRA, INDEC, Bluelytics y BYMA
        • Actualización automática cada 15 minutos
        • Click en cualquier card para ver gráfico histórico
      </div>

      {/* Modal */}
      <HistoricalModal
        card={selectedCard}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  )
}