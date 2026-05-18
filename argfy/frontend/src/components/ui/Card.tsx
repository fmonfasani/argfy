'use client'
import React from 'react'

interface CardProps {
  title?: string
  subtitle?: string
  icon?: React.ReactNode
  accent?: boolean
  hover?: boolean
  padding?: 'sm' | 'md' | 'lg'
  className?: string
  children: React.ReactNode
}

export default function Card({
  title,
  subtitle,
  icon,
  accent = false,
  hover = true,
  padding = 'md',
  className = '',
  children,
}: CardProps) {
  const pad = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }

  return (
    <div
      className={`
        bg-slate-800 rounded-xl border
        ${accent ? 'border-amber-500/50' : 'border-slate-700'}
        ${hover ? 'hover:bg-slate-800/80 hover:border-slate-600 transition-all duration-200' : ''}
        ${pad[padding]}
        ${className}
      `}
    >
      {(title || icon) && (
        <div className="flex items-start gap-3 mb-4">
          {icon && (
            <div className="w-10 h-10 bg-amber-500/10 rounded-lg flex items-center justify-center shrink-0">
              {icon}
            </div>
          )}
          <div className="min-w-0">
            {title && <h3 className="text-white font-semibold">{title}</h3>}
            {subtitle && <p className="text-slate-400 text-sm mt-0.5">{subtitle}</p>}
          </div>
        </div>
      )}
      {children}
    </div>
  )
}
