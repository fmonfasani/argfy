'use client'
import Link from 'next/link'
import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'

export default function Header() {
  const { user, loading, logout } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="bg-slate-900 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-amber-400 font-bold text-xl">Argfy</span>
          </Link>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            <Link href="/cedears" className="text-white hover:text-amber-400 transition-colors">
              Screener
            </Link>
            <Link href="/pricing" className="text-slate-400 hover:text-white transition-colors">
              Planes
            </Link>
            <Link href="/api" className="text-slate-400 hover:text-white transition-colors">
              API
            </Link>
            {loading ? (
              <div className="w-16 h-8 bg-slate-800 rounded animate-pulse" />
            ) : user ? (
              <div className="flex items-center gap-3">
                <Link href="/account" className="text-slate-400 hover:text-white transition-colors text-sm">
                  {user.nombre || user.email}
                </Link>
                <button onClick={() => logout()} className="text-slate-500 hover:text-white text-sm transition-colors">
                  Salir
                </button>
              </div>
            ) : (
              <>
                <Link href="/auth/login" className="text-slate-300 hover:text-white transition-colors text-sm">
                  Ingresar
                </Link>
                <Link href="/auth/register" className="bg-amber-500 text-slate-900 px-3 py-1.5 rounded-md hover:bg-amber-400 transition-colors font-semibold text-sm">
                  Registrarse
                </Link>
              </>
            )}
          </nav>

          <button onClick={() => setMenuOpen(!menuOpen)} className="md:hidden text-slate-400 hover:text-white p-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen
                ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              }
            </svg>
          </button>
        </div>

        {menuOpen && (
          <nav className="md:hidden py-4 border-t border-slate-800 space-y-3">
            <Link href="/cedears" className="block text-white hover:text-amber-400 text-sm" onClick={() => setMenuOpen(false)}>
              Screener
            </Link>
            <Link href="/pricing" className="block text-slate-400 hover:text-white text-sm" onClick={() => setMenuOpen(false)}>
              Planes
            </Link>
            <Link href="/api" className="block text-slate-400 hover:text-white text-sm" onClick={() => setMenuOpen(false)}>
              API
            </Link>
            {loading ? null : user ? (
              <>
                <Link href="/account" className="block text-slate-400 hover:text-white text-sm" onClick={() => setMenuOpen(false)}>
                  {user.nombre || user.email}
                </Link>
                <button onClick={() => { logout(); setMenuOpen(false) }} className="block text-slate-500 hover:text-white text-sm">
                  Salir
                </button>
              </>
            ) : (
              <>
                <Link href="/auth/login" className="block text-slate-300 hover:text-white text-sm" onClick={() => setMenuOpen(false)}>
                  Ingresar
                </Link>
                <Link href="/auth/register" className="block text-amber-400 font-semibold text-sm" onClick={() => setMenuOpen(false)}>
                  Registrarse
                </Link>
              </>
            )}
          </nav>
        )}
      </div>
    </header>
  )
}
