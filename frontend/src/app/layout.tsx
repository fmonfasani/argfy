// frontend/src/app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'
// import TradingViewMarquee from '@/components/TradingViewMarquee'  // ← COMENTADO
import SecondaryNav from '@/components/SecondaryNav'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Argfy - Financial Data Platform',
  description: 'Datos económicos argentinos en tiempo real para desarrolladores, traders y analistas',
  keywords: 'argentina, economia, finanzas, datos, api, dolar, inflacion, bcra',
  authors: [{ name: 'Argfy Team' }],
  // viewport: 'width=device-width, initial-scale=1',  // ← MOVER A viewport export
  // themeColor: '#0f172a',  // ← MOVER A viewport export
  openGraph: {
    title: 'Argfy - Financial Data Platform',
    description: 'Plataforma de datos económicos argentinos en tiempo real',
    type: 'website',
    locale: 'es_AR',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es" className="scroll-smooth">
      <body className={`${inter.className} bg-slate-100 min-h-screen`}>
        {/* Main Header */}
        <Header />
        
        {/* TradingView Marquee - TEMPORALMENTE DESHABILITADO */}
        {/* <TradingViewMarquee /> */}
        
        {/* Secondary Navigation */}
        <SecondaryNav />
        
        {/* Main Content */}
        <main className="relative">
          {children}
        </main>
        
        {/* Scripts externos - COMENTADO */}
        {/* <script 
          src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" 
          async 
        /> */}
      </body>
    </html>
  )
}