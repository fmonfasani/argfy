'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'

export default function Topbar() {
  const { user, loading, logout } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="h-12 bg-slate-900 border-b border-slate-800 flex items-center px-4 lg:px-6">
      <Link href="/" className="lg:hidden text-amber-400 font-bold text-lg mr-4">Argfy</Link>

      <nav className="hidden md:flex items-center gap-6 text-sm font-medium flex-1">
        <Link href="/cedears" className="text-slate-400 hover:text-white transition-colors">Screener</Link>
        <Link href="/pricing" className="text-slate-400 hover:text-white transition-colors">Planes</Link>
        <Link href="/api" className="text-slate-400 hover:text-white transition-colors">API</Link>
      </nav>

      <div className="ml-auto flex items-center gap-3">
        {loading ? (
          <div className="w-16 h-7 bg-slate-800 rounded animate-pulse" />
        ) : user ? (
          <div className="flex items-center gap-3">
            <span className="hidden sm:block text-slate-400 text-sm">{user.nombre || user.email}</span>
            <button onClick={() => logout()} className="text-slate-500 hover:text-white text-sm transition-colors">Salir</button>
          </div>
        ) : (
          <>
            <Link href="/auth/login" className="hidden sm:block text-slate-300 hover:text-white text-sm">Ingresar</Link>
            <Link href="/auth/register" className="bg-amber-500 text-slate-900 px-3 py-1.5 rounded-md hover:bg-amber-400 transition-colors font-semibold text-sm">Registrarse</Link>
          </>
        )}

        <button onClick={() => setMenuOpen(!menuOpen)} className="md:hidden text-slate-400 hover:text-white p-1">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {menuOpen
              ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            }
          </svg>
        </button>
      </div>

      {menuOpen && (
        <>
          <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setMenuOpen(false)} />
          <nav className="fixed top-12 right-0 w-48 bg-slate-900 border border-slate-800 rounded-bl-lg shadow-xl z-50 py-2 md:hidden">
            <Link href="/cedears" className="block px-4 py-2 text-sm text-slate-300 hover:text-white" onClick={() => setMenuOpen(false)}>Screener</Link>
            <Link href="/pricing" className="block px-4 py-2 text-sm text-slate-400 hover:text-white" onClick={() => setMenuOpen(false)}>Planes</Link>
            <Link href="/api" className="block px-4 py-2 text-sm text-slate-400 hover:text-white" onClick={() => setMenuOpen(false)}>API</Link>
            {!loading && !user && (
              <>
                <Link href="/auth/login" className="block px-4 py-2 text-sm text-slate-300 hover:text-white" onClick={() => setMenuOpen(false)}>Ingresar</Link>
                <Link href="/auth/register" className="block px-4 py-2 text-sm text-amber-400 font-semibold" onClick={() => setMenuOpen(false)}>Registrarse</Link>
              </>
            )}
          </nav>
        </>
      )}
    </header>
  )
}
