'use client'
import Link from 'next/link'
import ThemeToggle from './ThemeToggle'
import { useAuth } from '@/hooks/useAuth'

export default function Header() {
  const { user, loading, logout } = useAuth()

  return (
    <header className="bg-slate-900 shadow-lg border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-slate-600 to-slate-800 rounded-lg flex items-center justify-center border border-slate-500">
              <span className="text-amber-400 font-bold text-lg">A</span>
            </div>
            <h1 className="text-2xl font-bold text-white">Argfy</h1>
          </Link>

          {/* Navigation - Desktop */}
          <nav className="hidden lg:flex items-center space-x-6 text-sm font-medium">
            <Link href="/cedears" className="text-white hover:text-amber-400 transition-colors font-semibold">
              CEDEARs
            </Link>
            <Link href="/pricing" className="text-slate-300 hover:text-white transition-colors">
              Planes
            </Link>
            <Link href="/api" className="text-slate-300 hover:text-white transition-colors">
              API
            </Link>
            {loading ? (
              <div className="w-20 h-9 bg-slate-700 rounded-lg animate-pulse" />
            ) : user ? (
              <div className="flex items-center gap-3">
                <Link href="/account" className="text-slate-300 hover:text-white transition-colors text-sm">
                  {user.nombre || user.email}
                </Link>
                <button onClick={() => logout()} className="border border-slate-600 text-slate-300 px-3 py-1.5 rounded-lg hover:bg-slate-800 text-sm transition-colors">
                  Salir
                </button>
              </div>
            ) : (
              <>
                <Link href="/auth/login" className="bg-amber-600 text-slate-900 px-4 py-2 rounded-lg hover:bg-amber-500 transition-colors font-semibold text-sm">
                  Ingresar
                </Link>
                <Link href="/auth/register" className="border border-slate-600 text-slate-300 px-4 py-2 rounded-lg hover:bg-slate-800 hover:text-white transition-colors text-sm">
                  Registrarse
                </Link>
              </>
            )}
            <ThemeToggle />
          </nav>

          {/* Mobile menu button */}
          <div className="lg:hidden flex items-center gap-3">
            <ThemeToggle />
            <Link href="/cedears" className="text-amber-400 font-semibold text-sm">
              CEDEARs
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}
