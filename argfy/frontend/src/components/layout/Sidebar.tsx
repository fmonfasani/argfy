'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'

const navItems = [
  { label: 'Screener', href: '/cedears', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { label: 'Planes', href: '/pricing', icon: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z' },
  { label: 'API', href: '/api', icon: 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
]

const accountItems = [
  { label: 'Mi cuenta', href: '/account' },
  { label: 'Admin', href: '/admin' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { user, loading, logout } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside className={`hidden lg:flex flex-col bg-slate-900 border-r border-slate-800 transition-all duration-200 ${collapsed ? 'w-16' : 'w-56'}`}>
      <div className="flex items-center justify-between h-12 px-3 border-b border-slate-800">
        {!collapsed && <Link href="/" className="text-amber-400 font-bold text-lg">Argfy</Link>}
        <button onClick={() => setCollapsed(!collapsed)} className="text-slate-500 hover:text-white p-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {collapsed
              ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            }
          </svg>
        </button>
      </div>

      <nav className="flex-1 py-2">
        {navItems.map(item => {
          const active = pathname === item.href || (item.href !== '/cedears' && pathname?.startsWith(item.href))
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 mx-2 rounded-md text-sm transition-colors ${
                active ? 'bg-slate-800 text-amber-400' : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} />
              </svg>
              {!collapsed && item.label}
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-slate-800 py-2">
        {loading ? (
          <div className="h-8 bg-slate-800 rounded mx-2 animate-pulse" />
        ) : user ? (
          <>
            {user.role === 'admin' && (
              <Link href="/admin" className="flex items-center gap-3 px-3 py-2 mx-2 rounded-md text-sm text-slate-500 hover:text-white transition-colors">
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                </svg>
                {!collapsed && 'Admin'}
              </Link>
            )}
            <Link href="/account" className="flex items-center gap-3 px-3 py-2 mx-2 rounded-md text-sm text-slate-400 hover:text-white transition-colors">
              <div className="w-5 h-5 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <span className="text-amber-400 text-xs font-bold">{(user.nombre || user.email)[0].toUpperCase()}</span>
              </div>
              {!collapsed && <span className="truncate">{user.nombre || user.email}</span>}
            </Link>
            {!collapsed && (
              <button onClick={() => logout()} className="block w-full text-left px-3 py-2 mx-2 text-sm text-slate-600 hover:text-white transition-colors">
                Salir
              </button>
            )}
          </>
        ) : (
          <div className="px-3 py-2 mx-2">
            <Link href="/auth/login" className="block text-sm text-slate-400 hover:text-white text-center">Ingresar</Link>
          </div>
        )}
      </div>
    </aside>
  )
}
