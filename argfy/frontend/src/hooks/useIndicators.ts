// frontend/src/hooks/useIndicators.ts

import { useState, useEffect, useCallback } from 'react'
import { Indicator, DashboardData } from '../types'

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000/api/v1'


function useIndicators() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchAllIndicators = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const res = await fetch(`${API_BASE}/dashboard/complete`, {
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(10000),
      })

      if (!res.ok) {
        setError(`Error ${res.status}`)
        return
      }

      const json = await res.json()

      if (json.status === 'success' && json.data) {
        setData(json.data)
        setLastUpdated(new Date())
      } else {
        setError(json.message || 'Error fetching data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching indicators:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const refreshData = useCallback(() => {
    fetchAllIndicators()
  }, [fetchAllIndicators])

  const getIndicatorsByCategory = useCallback((category: string): Indicator[] => {
    if (!data || !data[category as keyof DashboardData]) return []
    
    const categoryData = data[category as keyof DashboardData]
    return Object.entries(categoryData)
      .filter(([key]) => !['timestamp', 'category'].includes(key))
      .map(([id, indicatorData]) => ({
        id,
        ...(indicatorData as any),
        category
      }))
  }, [data])

  const getIndicatorById = useCallback((id: string): Indicator | null => {
    if (!data) return null
    
    for (const categoryData of Object.values(data)) {
      if (categoryData[id]) {
        return {
          id,
          ...(categoryData[id] as any)
        }
      }
    }
    return null
  }, [data])

  // Auto-refresh cada 5 minutos
  useEffect(() => {
    fetchAllIndicators()
    
    const interval = setInterval(fetchAllIndicators, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [fetchAllIndicators])

  return {
    data,
    loading,
    error,
    lastUpdated,
    refreshData,
    getIndicatorsByCategory,
    getIndicatorById,
    isDataFresh: lastUpdated && (Date.now() - lastUpdated.getTime()) < 300000 // 5 min
  }
}

export { useIndicators }
export default useIndicators