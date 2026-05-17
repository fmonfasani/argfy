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

