import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import InternationalMarquee from '@/components/InternationalMarquee'
import ArgentineEconomicMarquee from '@/components/ArgentineEconomicMarquee'
import ArgentineStocksMarquee from '@/components/ArgentineStocksMarquee'
import Header from '@/components/Header'
import SecondaryNav from '@/components/SecondaryNav'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Argfy - Financial Data Platform',
  description: 'Datos económicos argentinos en tiempo real para desarrolladores, traders y analistas',
  keywords: 'argentina, economia, finanzas, datos, api, dolar, inflacion, bcra',
  authors: [{ name: 'Argfy Team' }],
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


        {/* Header Principal */}
        <Header />
        {/* MARQUESINAS FINALES - ALTURA 50px */}
        
        {/* 1. Internacional (Celeste, Rápida, ➡️) */}
        <InternationalMarquee />     
               
        {/* 2. Económica Argentina (Blanco, Media, ⬅️) */}
        <ArgentineEconomicMarquee />
        
        {/* 3. Acciones Argentinas (Celeste, Lenta, ➡️) */}
        <ArgentineStocksMarquee />
        

        
        {/* Navegación Secundaria */}
        <SecondaryNav />
        
        {/* Contenido Principal */}
        <main className="relative">
          {children}
        </main>
      </body>
    </html>
  )
}