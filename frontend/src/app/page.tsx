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

export default function HomePage() {
  const [isDashboardOpen, setIsDashboardOpen] = useState(false)

  const openDashboard = () => {
    setIsDashboardOpen(true)
  }

  return (
    <>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 min-h-[85vh] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero Content */}
          <div className="text-center mb-16">
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
              Accede a indicadores clave, análisis y proyecciones del mercado argentino. 
              API confiable para desarrolladores y traders.
            </p>
          </div>
          
          {/* Data Category Cards */}
          <EconomicDataCards />

          {/* Action Buttons */}
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