// frontend/src/app/page.tsx
'use client'
import { useState, useEffect } from 'react'
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
  const [indicators, setIndicators] = useState([])

  // Función para abrir el dashboard
  const openDashboard = () => {
    setIsDashboardOpen(true)
  }

  return (
    <>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 min-h-screen py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Data Category Cards */}
          <EconomicDataCards />

          {/* Action Buttons */}
          <div className="text-center space-x-4 mt-16">
            <button 
              onClick={openDashboard}
              className="inline-flex items-center px-8 py-4 bg-white text-slate-800 font-semibold rounded-xl hover:bg-slate-100 transition-all transform hover:scale-105 shadow-xl border border-slate-200"
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

      {/* Banks Section */}
      <BanksSection />

      {/* Government Section */}
      <GovernmentSection />

      {/* BCRA Section */}
      <BCRASection />

      {/* Economics Section */}
      <EconomicsSection />

      {/* Finances Section */}
      <FinancesSection />

      {/* Markets Section */}
      <MarketsSection />

      {/* Daily Economic Data Section */}
      <DailyEconomicData />

      {/* News Section */}
      <NewsSection />

      {/* Economics Analysis Section */}
      <EconomicsSection />

      {/* Footer */}
      <Footer />

      {/* Dashboard Modal */}
      <DashboardModal 
        isOpen={isDashboardOpen}
        onClose={() => setIsDashboardOpen(false)}
      />
    </>
  )
}