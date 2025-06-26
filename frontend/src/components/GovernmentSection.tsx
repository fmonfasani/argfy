// frontend/src/components/GovernmentSection.tsx
export default function GovernmentSection() {
  return (
    <section className="py-16 bg-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">
            🏛️ Government & Public Policy
          </h2>
          <p className="text-lg text-slate-300">
            Políticas públicas y gestión del sector gubernamental
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Política Fiscal</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">Resultado Primario</span>
                <span className="text-emerald-400 font-semibold">+0.8%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Gasto Público</span>
                <span className="text-slate-300 font-semibold">$58.4T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Recaudación</span>
                <span className="text-emerald-400 font-semibold">$62.1T</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Deuda Pública</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">Deuda/PBI</span>
                <span className="text-red-400 font-semibold">85.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Deuda Externa</span>
                <span className="text-slate-300 font-semibold">US$156B</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Deuda Interna</span>
                <span className="text-slate-300 font-semibold">$89.4T</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Programas Sociales</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">AUH</span>
                <span className="text-amber-400 font-semibold">4.2M</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Potenciar Trabajo</span>
                <span className="text-amber-400 font-semibold">1.1M</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Tarjeta Alimentar</span>
                <span className="text-amber-400 font-semibold">2.8M</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}