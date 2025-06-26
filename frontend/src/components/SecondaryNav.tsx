// frontend/src/components/SecondaryNav.tsx
'use client'
import { useState } from 'react'

export default function SecondaryNav() {
  const [activeTab, setActiveTab] = useState('US')

  const tabs = [
    'US', 'Products', 'Economic Insights', 'Money and Finance', 
    'Wall Street Live', 'Industry', 'Tech Trends', 'Reports', 'and Opinions'
  ]

  return (
    <div className="bg-slate-800 text-slate-300 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-8 py-3 overflow-x-auto">
          {tabs.map((tab) => (
            <div 
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`nav-tab px-3 py-1 rounded text-sm font-medium whitespace-nowrap cursor-pointer transition-all duration-200 hover:bg-slate-700 ${
                activeTab === tab ? 'bg-slate-100 text-slate-900' : ''
              }`}
            >
              {tab}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

