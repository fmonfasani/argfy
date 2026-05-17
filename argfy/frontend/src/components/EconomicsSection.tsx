// frontend/src/components/EconomicsSection.tsx
export default function EconomicsSection() {
  const economicInsights = [
    {
      category: "ANÁLISIS MACROECONÓMICO",
      title: "Perspectivas del PBI para 2024",
      summary: "Analistas prevén un crecimiento del 2.1% para el producto bruto interno argentino en el año fiscal...",
      value: "+2.1%",
      valueColor: "text-emerald-600",
      timeAgo: "Actualizado hoy"
    },
    {
      category: "MERCADO LABORAL",
      title: "Desempleo se mantiene en 6.1%",
      summary: "La tasa de desocupación mostró estabilidad en el último trimestre según datos del INDEC...",
      value: "6.1%",
      valueColor: "text-amber-600",
      timeAgo: "Hace 2 días"
    },
    {
      category: "POLÍTICA FISCAL",
      title: "Superávit fiscal del 0.8%",
      summary: "El resultado fiscal primario mostró números positivos por tercer mes consecutivo...",
      value: "+0.8%",
      valueColor: "text-emerald-600",
      timeAgo: "Hace 3 días"
    },
    {
      category: "COMERCIO EXTERIOR",
      title: "Balanza comercial positiva",
      summary: "Las exportaciones superaron a las importaciones por US$2.1B en el último mes...",
      value: "+US$2.1B",
      valueColor: "text-emerald-600",
      timeAgo: "Hace 4 días"
    },
    {
      category: "ÍNDICES DE PRECIOS",
      title: "IPC núcleo se desacelera",
      summary: "El índice de precios al consumidor núcleo mostró una moderación en su ritmo de crecimiento...",
      value: "3.8%",
      valueColor: "text-red-600",
      timeAgo: "Hace 5 días"
    },
    {
      category: "ACTIVIDAD ECONÓMICA",
      title: "EMAE crece 1.4% mensual",
      summary: "El estimador mensual de actividad económica registró su tercer mes consecutivo de crecimiento...",
      value: "+1.4%",
      valueColor: "text-emerald-600",
      timeAgo: "Hace 1 semana"
    }
  ]

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">
            📈 Economics
          </h2>
          <p className="text-lg text-slate-600">
            Análisis y tendencias económicas profundas
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {economicInsights.map((insight, index) => (
            <div 
              key={index}
              className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow cursor-pointer group"
            >
              <div className="text-slate-600 text-sm font-medium mb-2">
                {insight.category}
              </div>
              <h3 className="text-slate-800 font-semibold mb-3 group-hover:text-slate-900 transition-colors">
                {insight.title}
              </h3>
              <p className="text-slate-600 text-sm mb-4 line-clamp-2">
                {insight.summary}
              </p>
              <div className="flex items-center justify-between">
                <div className="text-slate-500 text-xs">
                  {insight.timeAgo}
                </div>
                <div className={`font-semibold text-sm ${insight.valueColor}`}>
                  {insight.value}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}