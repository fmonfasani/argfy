'use client'
import { useState, useEffect } from 'react'

export default function ArgentineEconomicMarquee() {
  const [data, setData] = useState([
    { 
      name: "USD Oficial", 
      value: 987.50, 
      change: "+0.8%", 
      color: "positive"
    },
    { 
      name: "USD Blue", 
      value: 1047.00, 
      change: "+2.3%", 
      color: "positive"
    },
    { 
      name: "USD MEP", 
      value: 1023.75, 
      change: "-0.5%", 
      color: "negative"
    },
    { 
      name: "Riesgo País", 
      value: 1642, 
      change: "-15 pb", 
      color: "negative",
      suffix: " pb"
    },
    { 
      name: "Tasa BCRA", 
      value: 118.0, 
      change: "+0.2%", 
      color: "positive",
      suffix: "%"
    },
    { 
      name: "Reservas BCRA", 
      value: 21.5, 
      change: "+1.2%", 
      color: "positive",
      prefix: "US$", 
      suffix: "B"
    },
    { 
      name: "Inflación", 
      value: 4.2, 
      change: "-0.3%", 
      color: "negative",
      suffix: "%"
    },
    { 
      name: "EMAE", 
      value: 148.2, 
      change: "+1.4%", 
      color: "positive"
    },
    { 
      name: "AL30", 
      value: 68.50, 
      change: "-2.1%", 
      color: "negative",
      prefix: "$"
    },
    { 
      name: "GD30", 
      value: 1245, 
      change: "+1.5%", 
      color: "positive",
      prefix: "$"
    },{ 
      name: "USD Oficial", 
      value: 987.50, 
      change: "+0.8%", 
      color: "positive"
    },
    { 
      name: "USD Blue", 
      value: 1047.00, 
      change: "+2.3%", 
      color: "positive"
    },
    { 
      name: "USD MEP", 
      value: 1023.75, 
      change: "-0.5%", 
      color: "negative"
    },
    { 
      name: "Riesgo País", 
      value: 1642, 
      change: "-15 pb", 
      color: "negative",
      suffix: " pb"
    },
    { 
      name: "Tasa BCRA", 
      value: 118.0, 
      change: "+0.2%", 
      color: "positive",
      suffix: "%"
    },
    { 
      name: "Reservas BCRA", 
      value: 21.5, 
      change: "+1.2%", 
      color: "positive",
      prefix: "US$", 
      suffix: "B"
    },
    { 
      name: "Inflación", 
      value: 4.2, 
      change: "-0.3%", 
      color: "negative",
      suffix: "%"
    },
    { 
      name: "EMAE", 
      value: 148.2, 
      change: "+1.4%", 
      color: "positive"
    },
    { 
      name: "AL30", 
      value: 68.50, 
      change: "-2.1%", 
      color: "negative",
      prefix: "$"
    },
    { 
      name: "GD30", 
      value: 1245, 
      change: "+1.5%", 
      color: "positive",
      prefix: "$"
    }
  ])

  useEffect(() => {
    // Simular actualización de datos cada 45 segundos
    const interval = setInterval(() => {
      setData(prevData => 
        prevData.map(item => {
          const variation = (Math.random() - 0.5) * (item.value * 0.001)
          const newValue = Math.max(0, item.value + variation)
          return {
            ...item,
            value: newValue,
          }
        })
      )
    }, 45000)

    return () => clearInterval(interval)
  }, [])

  const formatValue = (item: any) => {
    const formattedValue = typeof item.value === 'number' ? item.value.toFixed(2) : item.value
    return `${item.prefix || ""}${formattedValue}${item.suffix || ""}`
  }

  // Triplicar datos para flujo continuo sin espacios
  const triplicatedData = [...data, ...data, ...data]

  return (
    <div className="marquee-container marquee-blanco">
      <div className="overflow-hidden">
        <div className="marquee-track marquee-right-normal">
          {triplicatedData.map((item, index) => (
            <div key={index} className="inline-flex items-center">
              <div className="marquee-item">
                <span className="marquee-label">{item.name}</span>
                <span className="marquee-value">
                  {formatValue(item)}
                </span>
                <span className={`marquee-change ${item.color}`}>
                  {item.change}
                </span>
              </div>
              {index < triplicatedData.length - 1 && (
                <div className="marquee-separator"></div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}