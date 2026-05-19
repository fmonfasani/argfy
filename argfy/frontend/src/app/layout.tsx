import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import '@/styles/tokens.css'
import MarqueeBar from '@/components/MarqueeBar'
import Sidebar from '@/components/layout/Sidebar'
import Topbar from '@/components/layout/Topbar'
import Providers from '@/components/Providers'

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
    <html lang="es" className="scroll-smooth dark" suppressHydrationWarning>
      <body className={`${inter.className} min-h-screen`}>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <Topbar />
            <MarqueeBar variant="combined" />
            <main className="flex-1">
              <Providers>{children}</Providers>
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}
