// frontend/src/components/BCRASection.tsx
export default function BCRASection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">
            🏦 Banco Central (BCRA)
          </h2>
          <p className="text-lg text-slate-600">
            Política monetaria y regulación del sistema financiero
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Política Monetaria</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">Tasa de Política</span>
                <span className="text-slate-700 font-semibold">118.0%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Base Monetaria</span>
                <span className="text-slate-700 font-semibold">$8.2T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Circulante</span>
                <span className="text-slate-700 font-semibold">$6.1T</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Reservas</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">Reservas Brutas</span>
                <span className="text-slate-700 font-semibold">US$21.5B</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Reservas Netas</span>
                <span className="text-slate-700 font-semibold">US$8.4B</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Oro</span>
                <span className="text-slate-700 font-semibold">US$4.2B</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Instrumentos</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">LELIQs</span>
                <span className="text-slate-700 font-semibold">$12.8T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">NOTAs</span>
                <span className="text-slate-700 font-semibold">$3.4T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">PASSES</span>
                <span className="text-slate-700 font-semibold">$2.1T</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

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

// frontend/src/components/FinancesSection.tsx
export default function FinancesSection() {
  return (
    <section className="py-16 bg-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">
            💰 Financial Markets
          </h2>
          <p className="text-lg text-slate-300">
            Mercados financieros e instrumentos de inversión
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Bonos Soberanos</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">AL30</span>
                <span className="text-red-400 font-semibold">$68.50</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">GD30</span>
                <span className="text-slate-300 font-semibold">$1,245</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">AL35</span>
                <span className="text-emerald-400 font-semibold">$42.80</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Fondos Comunes</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">FCI Total</span>
                <span className="text-white font-semibold">$8.4T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Money Market</span>
                <span className="text-emerald-400 font-semibold">$5.2T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Renta Fija</span>
                <span className="text-slate-300 font-semibold">$2.1T</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Tipos de Cambio</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">USD Oficial</span>
                <span className="text-white font-semibold">$987.50</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">USD Blue</span>
                <span className="text-emerald-400 font-semibold">$1,047</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">USD MEP</span>
                <span className="text-slate-300 font-semibold">$1,023</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// frontend/src/components/MarketsSection.tsx
export default function MarketsSection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">
            📈 Stock Markets
          </h2>
          <p className="text-lg text-slate-600">
            Bolsa de valores y mercados bursátiles argentinos
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Índices Principales</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">MERVAL</span>
                <span className="text-slate-700 font-semibold">1,456,234</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">BURCAP</span>
                <span className="text-slate-700 font-semibold">89,456</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">MERVAL 25</span>
                <span className="text-slate-700 font-semibold">124,789</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Acciones Líderes</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">GGAL</span>
                <span className="text-slate-700 font-semibold">$2,847</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">YPFD</span>
                <span className="text-slate-700 font-semibold">$12,450</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">PAMP</span>
                <span className="text-slate-700 font-semibold">$8,920</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Volumen de Operaciones</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">Volumen Diario</span>
                <span className="text-slate-700 font-semibold">$2.8B</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Operaciones</span>
                <span className="text-slate-700 font-semibold">45,892</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Cap. Bursátil</span>
                <span className="text-slate-700 font-semibold">$89.4T</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}