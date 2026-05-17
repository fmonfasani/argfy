// frontend/src/components/BanksSection.tsx
export default function BanksSection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">
            🏦 Banking System
          </h2>
          <p className="text-lg text-slate-600">
            Sistema bancario argentino y entidades financieras
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Bancos Públicos</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">Banco Nación</span>
                <span className="text-emerald-600 font-semibold">Active</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Banco Provincia</span>
                <span className="text-emerald-600 font-semibold">Active</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Banco Ciudad</span>
                <span className="text-emerald-600 font-semibold">Active</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Bancos Privados</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">Galicia</span>
                <span className="text-emerald-600 font-semibold">$2,847</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Macro</span>
                <span className="text-slate-700 font-semibold">$1,245</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Supervielle</span>
                <span className="text-slate-700 font-semibold">$892</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Indicadores</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">Total Depósitos</span>
                <span className="text-slate-700 font-semibold">$45.2T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Préstamos</span>
                <span className="text-slate-700 font-semibold">$28.7T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Morosidad</span>
                <span className="text-red-600 font-semibold">3.2%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

