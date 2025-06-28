export const formatValue = (value: number | string, unit: string): string => {
  if (typeof value === 'string') return value

  switch (unit) {
    case 'percentage':
    case '%':
      return `${value.toFixed(1)}%`
    
    case 'usd_millions':
      return `US$${(value / 1000000).toFixed(1)}M`
    
    case 'usd_billions':
      return `US$${(value / 1000000000).toFixed(1)}B`
    
    case 'ars_billions':
      return `$${(value / 1000000000).toFixed(1)}B`
    
    case 'ars':
      return `$${value.toLocaleString()}`
    
    case 'usd':
      return `US$${value.toLocaleString()}`
    
    case 'thousands':
      return `${(value / 1000).toFixed(1)}K`
    
    case 'index':
      return value.toFixed(1)
    
    case 'count':
      return value.toLocaleString()
    
    default:
      return value.toLocaleString()
  }
}

export const formatChange = (change: number): { text: string; color: string; icon: string } => {
  const isPositive = change > 0
  const isNeutral = change === 0
  
  return {
    text: isNeutral ? '0%' : `${isPositive ? '+' : ''}${change.toFixed(1)}%`,
    color: isNeutral ? 'text-gray-500' : isPositive ? 'text-green-600' : 'text-red-600',
    icon: isNeutral ? '➡️' : isPositive ? '📈' : '📉'
  }
}

export const formatTimestamp = (timestamp: string): string => {
  return new Date(timestamp).toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

export const getSourceBadgeColor = (source: string): string => {
  const colors: Record<string, string> = {
    'BCRA': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'INDEC': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'BYMA': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    'MECON': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'DEMO': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }
  
  return colors[source] || colors['DEMO']
}

export const getFreshnessStatus = (lastUpdated: Date): {
  status: 'fresh' | 'recent' | 'stale'
  color: string
  text: string
} => {
  const minutes = Math.floor((Date.now() - lastUpdated.getTime()) / 60000)
  
  if (minutes < 5) {
    return { status: 'fresh', color: 'text-green-600', text: 'Datos frescos' }
  } else if (minutes < 30) {
    return { status: 'recent', color: 'text-yellow-600', text: 'Datos recientes' }
  } else {
    return { status: 'stale', color: 'text-red-600', text: 'Datos desactualizados' }
  }
}