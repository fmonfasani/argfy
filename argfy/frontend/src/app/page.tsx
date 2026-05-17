'use client'
import { useState } from 'react'
import Link from 'next/link'
import EconomicDataCards from '@/components/EconomicDataCards'
import DailyEconomicData from '@/components/DailyEconomicData'
import NewsSection from '@/components/NewsSection'
import EconomicsSection from '@/components/EconomicsSection'
import BanksSection from '@/components/BanksSection'
import GovernmentSection from '@/components/GovernmentSection'
import BCRASection from '@/components/BCRASection'
import FinancesSection from '@/components/FinancesSection'
import MarketsSection from '@/components/MarketsSection'
import Footer from '@/components/Footer'
import DashboardModal from '@/components/DashboardModal'
import CedearsLeaderboard from '@/components/CedearsLeaderboard'

export default function HomePage() {
  const [isDashboardOpen, setIsDashboardOpen] = useState(false)

  const openDashboard = () => {
    setIsDashboardOpen(true)
  }

  return (
    <>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
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
          </div>

          {/* 4 Action Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <Link href="/cedears" className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800 hover:border-amber-500/50 transition-all">
              <div className="w-12 h-12 bg-amber-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-amber-500/20 transition-colors">
                <span className="text-2xl">📈</span>
              </div>
              <h3 className="text-white font-semibold mb-2">Explorar screener</h3>
              <p className="text-slate-400 text-sm">Filtrá 415+ CEDEARs por PER, ROE, margen, deuda y más</p>
            </Link>
            <div className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800 transition-all cursor-default">
              <div className="w-12 h-12 bg-slate-700/50 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-white font-semibold mb-2">Tendencias</h3>
              <p className="text-slate-400 text-sm">Evolución de métricas clave por sector y mercado</p>
            </div>
            <div className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800 transition-all cursor-default">
              <div className="w-12 h-12 bg-slate-700/50 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📄</span>
              </div>
              <h3 className="text-white font-semibold mb-2">Metodología</h3>
              <p className="text-slate-400 text-sm">Cálculo de ratios basado en reports SEC 10-K/Q</p>
            </div>
            <Link href="/api" className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800 hover:border-amber-500/50 transition-all">
              <div className="w-12 h-12 bg-amber-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-amber-500/20 transition-colors">
                <span className="text-2xl">🔌</span>
              </div>
              <h3 className="text-white font-semibold mb-2">API docs</h3>
              <p className="text-slate-400 text-sm">Accedé a los datos programáticamente con nuestra API</p>
            </Link>
          </div>

          {/* Data Category Cards */}
          <EconomicDataCards />

          <div className="text-center space-x-4 mt-16">
            <button 
              onClick={openDashboard}
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 font-semibold rounded-xl hover:from-amber-400 hover:to-amber-500 transition-all transform hover:scale-105 shadow-xl"
            >
              <span className="mr-2">📊</span>
              Ver Dashboard
            </button>
            <Link 
              href="/api"
              className="inline-flex items-center px-8 py-4 border-2 border-slate-400 text-white font-semibold rounded-xl hover:bg-slate-800 hover:border-slate-300 transition-all"
            >
              <span className="mr-2">🔧</span>
              API Coming Soon
            </Link>
          </div>
        </div>
      </section>

      {/* CEDEARs Leaderboard */}
      <CedearsLeaderboard />


      {/* Resto del contenido */}
      <BanksSection />
      <GovernmentSection />
      <BCRASection />
      <EconomicsSection />
      <FinancesSection />
      <MarketsSection />
      <DailyEconomicData />
      <NewsSection />
      <Footer />

      <DashboardModal 
        isOpen={isDashboardOpen}
        onClose={() => setIsDashboardOpen(false)}
      />
    </>
  )
}