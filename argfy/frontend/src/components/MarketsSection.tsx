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