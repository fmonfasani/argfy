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

