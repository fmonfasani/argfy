// frontend/src/hooks/useBCRAReal.ts
import { useState, useEffect } from 'react'
import { API_BASE_URL } from '@/lib/config'

interface BCRAData {
  indicadores_principales: Record<string, any>
  cotizaciones: Record<string, any>
  timestamp: string
}

export function useBCRAReal() {
  const [data, setData] = useState<BCRAData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchBCRAData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/bcra/dashboard`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status === 'success') {
        setData(result.data)
        setLastUpdated(new Date())
        setError(null)
      } else {
        throw new Error('Error en respuesta BCRA')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      console.error('Error fetching BCRA data:', err)
    } finally {
      setLoading(false)
    }
  }

  const refreshData = () => {
    fetchBCRAData()
  }

  // Auto-refresh cada 5 minutos
  useEffect(() => {
    fetchBCRAData()
    
    const interval = setInterval(fetchBCRAData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  return {
    data,
    loading,
    error,
    lastUpdated,
    refreshData,
    isDataFresh: lastUpdated && (Date.now() - lastUpdated.getTime()) < 300000 // 5 min
  }
}