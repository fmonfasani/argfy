"use client"

import { useState } from "react"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts"
import { usePriceHistory } from "@/hooks/usePriceHistory"
import type { PeriodOption } from "@/lib/types"

const PERIODS: { label: string; value: PeriodOption }[] = [
  { label: "1M", value: "1m" },
  { label: "6M", value: "6m" },
  { label: "1Y", value: "1y" },
  { label: "5Y", value: "5y" },
  { label: "Max", value: "max" },
]

interface PriceChartProps {
  ticker: string
}

export default function PriceChart({ ticker }: PriceChartProps) {
  const [period, setPeriod] = useState<PeriodOption>("5y")
  const { data, isLoading } = usePriceHistory(ticker, period, "1d")

  if (isLoading) {
    return (
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
        <div className="animate-pulse space-y-4">
          <div className="h-5 bg-slate-700 rounded w-32" />
          <div className="h-64 bg-slate-700 rounded" />
        </div>
      </div>
    )
  }

  const prices = data?.data ?? []

  return (
    <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold">Precio — {ticker}</h3>
        <div className="flex gap-1">
          {PERIODS.map(p => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
                period === p.value
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/50"
                  : "text-slate-400 hover:text-white border border-transparent"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={prices}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="date"
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickFormatter={(d: string) => {
                const parts = d.split("-")
                return `${parts[1]}/${parts[2].slice(0, 2)}`
              }}
              interval="preserveStartEnd"
              minTickGap={40}
            />
            <YAxis
              domain={["auto", "auto"]}
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickFormatter={(v: number) => `$${v.toFixed(0)}`}
              width={60}
            />
            <Tooltip
              contentStyle={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
                fontSize: "13px",
              }}
              labelFormatter={(d: string) => new Date(d).toLocaleDateString("es-AR")}
              formatter={(value: number) => [`$${value.toFixed(2)}`, "Close"]}
            />
            <Line
              type="monotone"
              dataKey="close"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#f59e0b" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
