// frontend/src/components/NewsSection.tsx
'use client'
import { useState, useEffect } from 'react'

interface NewsItem {
  id: number
  title: string
  summary: string
  category: string
  source: string
  published_at: string
  is_featured: boolean
}

export default function NewsSection() {
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchNews()
  }, [])

  const fetchNews = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/indicators/news?limit=6`)
      const data = await response.json()
      setNews(data.data || [])
    } catch (error) {
      console.error('Error fetching news:', error)
      // Datos de fallback
      setNews([
        {
          id: 1,
          title: "BCRA mantiene la tasa de interés en 118%",
          summary: "El banco central decidió mantener sin cambios la tasa de política monetaria en su última reunión...",
          category: "ECONOMÍA",
          source: "Argfy News",
          published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          is_featured: true
        },
        {
          id: 2,
          title: "Merval cierra con suba del 2.1%",
          summary: "El índice principal de la Bolsa porteña registró una jornada positiva impulsada por los papeles financieros...",
          category: "MERCADOS",
          source: "Argfy News",
          published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          is_featured: false
        },
        {
          id: 3,
          title: "Soja alcanza US$485 por tonelada",
          summary: "Los precios de la oleaginosa se mantienen firmes en el mercado internacional impulsados por la demanda...",
          category: "COMMODITIES",
          source: "Argfy News",
          published_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          is_featured: false
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Hace menos de 1 hora'
    if (diffInHours < 24) return `Hace ${diffInHours} hora${diffInHours > 1 ? 's' : ''}`
    const diffInDays = Math.floor(diffInHours / 24)
    return `Hace ${diffInDays} día${diffInDays > 1 ? 's' : ''}`
  }

  const getCategoryColor = (category: string) => {
    const colors = {
      'ECONOMÍA': 'text-amber-400',
      'MERCADOS': 'text-emerald-400',
      'COMMODITIES': 'text-blue-400',
      'INFLACIÓN': 'text-red-400',
      'FINTECH': 'text-purple-400',
      'EXPORTACIONES': 'text-green-400'
    }
    return colors[category as keyof typeof colors] || 'text-amber-400'
  }

  if (loading) {
    return (
      <section className="py-16 bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="h-8 w-32 bg-slate-700 rounded mx-auto mb-4 animate-pulse"></div>
            <div className="h-4 w-64 bg-slate-700 rounded mx-auto animate-pulse"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-slate-700 rounded-lg p-6 animate-pulse">
                <div className="h-4 w-20 bg-slate-600 rounded mb-2"></div>
                <div className="h-6 bg-slate-600 rounded mb-3"></div>
                <div className="h-16 bg-slate-600 rounded mb-4"></div>
                <div className="h-3 w-24 bg-slate-600 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="py-16 bg-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">
            📰 News
          </h2>
          <p className="text-lg text-slate-300">
            Últimas noticias económicas y financieras
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {news.map((item) => (
            <div 
              key={item.id}
              className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition-colors cursor-pointer group"
            >
              <div className={`text-sm font-medium mb-2 ${getCategoryColor(item.category)}`}>
                {item.category}
              </div>
              <h3 className="text-white font-semibold mb-3 group-hover:text-amber-100 transition-colors">
                {item.title}
              </h3>
              <p className="text-slate-300 text-sm mb-4 line-clamp-3">
                {item.summary}
              </p>
              <div className="text-slate-400 text-xs">
                {getTimeAgo(item.published_at)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

