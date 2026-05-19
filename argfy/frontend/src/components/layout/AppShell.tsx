'use client'

import { usePathname } from 'next/navigation'
import type { ReactNode } from 'react'
import MarqueeBar from '@/components/MarqueeBar'
import Sidebar from '@/components/layout/Sidebar'
import Topbar from '@/components/layout/Topbar'

const FULL_BLEED_ROUTES = ['/']

export default function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  const fullBleed = FULL_BLEED_ROUTES.includes(pathname ?? '')

  if (fullBleed) {
    return <main className="min-h-screen">{children}</main>
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar />
        <MarqueeBar variant="combined" />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  )
}
