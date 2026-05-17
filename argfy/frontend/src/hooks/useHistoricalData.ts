// frontend/src/hooks/useHistoricalData.ts
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { HistoricalData, LoadingState } from '@/types'

export function useHistoricalData(indicatorType: string, days: number = 30) {
  const [data, setData] = useState<HistoricalData[]>([])
  const [loading, setLoading] = useState<LoadingState>({
    isLoading: true,
    error: null
  })

  const fetchData = async () => {
    if (!indicatorType) return
    
    try {
      setLoading({ isLoading: true, error: null })
      const response = await api.getHistoricalData(indicatorType, days)
      setData(response.data)
    } catch (error) {
      setLoading({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Error fetching historical data'
      })
    } finally {
      setLoading(prev => ({ ...prev, isLoading: false }))
    }
  }

  useEffect(() => {
    fetchData()
  }, [indicatorType, days])

  return {
    data,
    loading: loading.isLoading,
    error: loading.error,
    refetch: fetchData
  }
}