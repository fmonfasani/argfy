// frontend/src/components/Header.tsx
'use client'
import { useState } from 'react'
import Link from 'next/link'
import { MagnifyingGlassIcon, Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('')
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // Implementar búsqueda
    console.log('Searching for:', searchQuery)
  }

  return (
    <header className="bg-slate-900 shadow-lg border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-slate-600 to-slate-800 rounded-lg flex items-center justify-center border border-slate-500">
                <span className="text-amber-400 font-bold text-lg">A</span>
              </div>
              <h1 className="text-2xl font-bold text-white">Argfy</h1>
            </Link>
          </div>
          
          {/* Search Bar - Desktop */}
          <div className="flex-1 max-w-2xl mx-8 hidden md:block">
            <form onSubmit={handleSearch} className="relative">
              <input 
                type="text" 
                placeholder="search for news, data and companies"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 pl-4 pr-12 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all duration-300 focus:scale-102"
              />
              <button 
                type="submit"
                className="absolute right-0 top-0 h-full px-4 bg-slate-700 text-amber-400 rounded-r-lg hover:bg-slate-600 transition-colors border-l border-slate-600"
              >
                <MagnifyingGlassIcon className="w-5 h-5" />
              </button>
            </form>
          </div>
          
          {/* Navigation Links - Desktop */}
          <nav className="hidden lg:flex items-center space-x-6 text-sm font-medium">
            <Link href="/news" className="text-slate-300 hover:text-white transition-colors">
              News
            </Link>
            <Link href="/products" className="text-slate-300 hover:text-white transition-colors">
              Products
            </Link>
            <Link href="/api" className="text-slate-300 hover:text-white transition-colors">
              APIs
            </Link>
            <Link href="/analysis" className="text-slate-300 hover:text-white transition-colors">
              Analysis
            </Link>
            <Link href="/brokers" className="text-slate-300 hover:text-white transition-colors">
              Brokers
            </Link>
            <Link href="/communities" className="text-slate-300 hover:text-white transition-colors">
              Communities
            </Link>
            <button className="bg-amber-600 text-slate-900 px-4 py-2 rounded-lg hover:bg-amber-500 transition-colors font-semibold">
              Sign
            </button>
            <button className="border border-slate-600 text-slate-300 px-4 py-2 rounded-lg hover:bg-slate-800 hover:text-white transition-colors">
              Subscribe
            </button>
          </nav>

          {/* Mobile menu button */}
          <div className="lg:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-slate-300 hover:text-white p-2"
            >
              {isMobileMenuOpen ? (
                <XMarkIcon className="w-6 h-6" />
              ) : (
                <Bars3Icon className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="lg:hidden py-4 border-t border-slate-700">
            {/* Mobile Search */}
            <form onSubmit={handleSearch} className="relative mb-4">
              <input 
                type="text" 
                placeholder="search for news, data and companies"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 pr-12 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
              />
              <button 
                type="submit"
                className="absolute right-2 top-2 p-1 text-amber-400"
              >
                <MagnifyingGlassIcon className="w-5 h-5" />
              </button>
            </form>

            {/* Mobile Navigation */}
            <nav className="flex flex-col space-y-3">
              <Link href="/news" className="text-slate-300 hover:text-white transition-colors py-2">
                News
              </Link>
              <Link href="/products" className="text-slate-300 hover:text-white transition-colors py-2">
                Products
              </Link>
              <Link href="/api" className="text-slate-300 hover:text-white transition-colors py-2">
                APIs
              </Link>
              <Link href="/analysis" className="text-slate-300 hover:text-white transition-colors py-2">
                Analysis
              </Link>
              <div className="flex space-x-3 pt-4">
                <button className="bg-amber-600 text-slate-900 px-4 py-2 rounded-lg hover:bg-amber-500 transition-colors font-semibold flex-1">
                  Sign
                </button>
                <button className="border border-slate-600 text-slate-300 px-4 py-2 rounded-lg hover:bg-slate-800 hover:text-white transition-colors flex-1">
                  Subscribe
                </button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}