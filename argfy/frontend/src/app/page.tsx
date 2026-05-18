'use client'
import CedearsLeaderboard from '@/components/CedearsLeaderboard'
import EconomicDataCards from '@/components/EconomicDataCards'
import Footer from '@/components/Footer'

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <p className="text-amber-400 font-semibold text-sm tracking-widest uppercase mb-4">
              argfy · screener de CEDEARs y BYMA
            </p>
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              <span className="bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                Datos económicos
              </span>
              <br />
              <span className="bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
                Argentinos en tiempo real
              </span>
            </h1>
            <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto">
              Screener profesional de CEDEARs y acciones BYMA con datos fundamentalistas de SEC.
              PER, ROE, márgenes, deuda y más — actualizado desde EDGAR.
            </p>
            <a
              href="/cedears"
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 font-semibold rounded-xl hover:from-amber-400 hover:to-amber-500 transition-all transform hover:scale-105 shadow-xl"
            >
              Abrir Screener →
            </a>
          </div>
        </div>
      </section>

      {/* Live Economic Data */}
      <section className="py-12 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-slate-800 mb-8">Indicadores en vivo</h2>
          <EconomicDataCards />
        </div>
      </section>

      {/* CEDEARs Leaderboard */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-slate-800 mb-8">CEDEARs más atractivos</h2>
          <CedearsLeaderboard />
        </div>
      </section>

      <Footer />
    </>
  )
}
