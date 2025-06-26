'use client'
import { useState, useEffect } from 'react'

export default function ArgentineEconomicMarquee() {
  const [data, setData] = useState([
    { name: "Dólar BNA", value: 987.50, change: "+0.8%", color: "text-blue-600" },
    { name: "Dólar Blue", value: 1047.00, change: "+2.3%", color: "text-green-600" },
    { name: "Dólar MEP", value: 1023.75, change: "-0.5%", color: "text-red-600" },
    { name: "Riesgo País", value: 1642, change: "-15 pb", color: "text-red-600", suffix: " pb" },
    { name: "Tasa BCRA", value: 118.0, change: "Sin cambios", color: "text-amber-600", suffix: "%" },
    { name: "Reservas BCRA", value: 21.5, change: "+1.2%", color: "text-green-600", prefix: "US$", suffix: "B" },
    { name: "Base Monetaria", value: 8.2, change: "+5.4%", color: "text-green-600", prefix: "$", suffix: "T" },
    { name: "AL30", value: 68.50, change: "-2.1%", color: "text-red-600", prefix: "$" },
    { name: "GD30", value: 1245, change: "+1.5%", color: "text-green-600", prefix: "$" },
    { name: "Inflación Mensual", value: 4.2, change: "-0.3%", color: "text-red-600", suffix: "%" },
    { name: "EMAE", value: 148.2, change: "+1.4%", color: "text-green-600" },
    { name: "Desempleo", value: 6.1, change: "Estable", color: "text-amber-600", suffix: "%" },
  ])

  useEffect(() => {
    // Simular actualización de datos cada 30 segundos
    const interval = setInterval(() => {
      setData(prevData => 
        prevData.map(item => ({
          ...item,
          value: item.value + (Math.random() - 0.5) * (item.value * 0.001), // Variación pequeña
        }))
      )
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-amber-50 border-b border-amber-200 overflow-hidden">
      <div className="animate-marquee-left flex space-x-8 py-3 min-w-max">
        {data.concat(data).map((item, index) => (
          <div key={index} className="flex items-center space-x-2 whitespace-nowrap">
            <span className="text-sm font-medium text-amber-900">{item.name}:</span>
            <span className="font-bold text-amber-800">
              {item.prefix || ""}{typeof item.value === 'number' ? item.value.toFixed(2) : item.value}{item.suffix || ""}
            </span>
            <span className={`text-xs font-semibold ${
              item.change.startsWith('+') ? 'text-green-600' : 
              item.change.startsWith('-') ? 'text-red-600' : 'text-amber-600'
            }`}>
              {item.change}
            </span>
            <div className="w-1 h-1 bg-amber-400 rounded-full"></div>
          </div>
        ))}
      </div>
    </div>
  )
}