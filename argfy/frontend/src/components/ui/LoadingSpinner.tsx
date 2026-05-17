
'use client'
import React from 'react'

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  color?: string
  className?: string
}

export function LoadingSpinner({ 
  size = 'medium', 
  color = 'text-blue-600',
  className = '' 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8', 
    large: 'h-12 w-12'
  }

  return (
    <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-current ${sizeClasses[size]} ${color} ${className}`} />
  )
}