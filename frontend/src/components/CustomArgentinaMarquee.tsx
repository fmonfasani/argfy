// src/components/CustomArgentinaMarquee.tsx
'use client'
import { useState, useEffect } from 'react'

export default function CustomArgentinaMarquee() {
  const [data, setData] = useState([
    { name: "Dólar BNA", value: 987.50, change: "+0.8%" },
    { name: "Dólar Blue", value: 1047.00, change: "+2.3%" },
    { name: "Dólar MEP", value: 1023.75, change: "-0.5%" },
    { name: "Riesgo País", value: 1642, change: "-15 pb" }
  ])

  return (
    <div className="bg-blue-50 border-b border-blue-200 overflow-hidden">
      <div className="animate-marquee-reverse flex space-x-8 py-2 min-w-max">
        {data.map((item, index) => (
          <div key={index} className="flex items-center space-x-2 whitespace-nowrap">
            <span className="text-sm font-medium text-blue-900">{item.name}:</span>
            <span className="font-bold text-blue-800">${item.value}</span>
            <span className={`text-xs ${item.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
              {item.change}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}