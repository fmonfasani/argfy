"use client"

import { useState } from "react"
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts"
import { useMetricHistory } from "@/hooks/useMetricHistory"

const TABS: { label: string; metric: string }[] = [
  { label: "PER TTM", metric: "per_ttm" },
  { label: "EPS Diluted", metric: "eps_ttm_diluted" },
  { label: "Margen Neto", metric: "margen_neto_ttm" },
  { label: "FCF TTM", metric: "fcf_ttm" },
  { label: "ROE 5y", metric: "roe_cagr_5y" },
]

const METRIC_LABELS: Record<string, string> = {
  per_ttm: "PER",
  eps_ttm_diluted: "EPS",
  margen_neto_ttm: "Margen Neto",
  fcf_ttm: "FCF TTM",
  roe_cagr_5y: "ROE 5y CAGR",
}

function formatValue(metric: string, value: number): string {
  if (metric === "margen_neto_ttm" || metric === "roe_cagr_5y") {
    return `${(value * 100).toFixed(1)}%`
  }
  if (metric === "eps_ttm_diluted" || metric === "fcf_ttm") {
    return `$${value.toFixed(2)}`
  }
  return value.toFixed(1)
}

function fmtAxis(metric: string, value: number): string {
  if (metric === "margen_neto_ttm" || metric === "roe_cagr_5y") {
    return `${(value * 100).toFixed(0)}%`
  }
  return value.toFixed(1)
}

interface MetricHistoryChartProps {
  ticker: string
}

export default function MetricHistoryChart({ ticker }: MetricHistoryChartProps) {
  const [activeTab, setActiveTab] = useState(TABS[0])
  const { data, isLoading } = useMetricHistory(ticker, activeTab.metric, "2021-01-01")

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

  const points = data?.data ?? []

  return (
    <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold">Evolución fundamentals</h3>
        <div className="flex gap-1 flex-wrap">
          {TABS.map(tab => (
            <button
              key={tab.metric}
              onClick={() => setActiveTab(tab)}
              className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
                activeTab.metric === tab.metric
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/50"
                  : "text-slate-400 hover:text-white border border-transparent"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={points}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="period_end"
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickFormatter={(d: string) => {
                const p = d.split("-")
                return `${p[0]}-${p[1]}`
              }}
              interval="preserveStartEnd"
              minTickGap={30}
            />
            <YAxis
              domain={["auto", "auto"]}
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickFormatter={(v: number) => fmtAxis(activeTab.metric, v)}
              width={60}
            />
            <Tooltip
              contentStyle={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
                fontSize: "13px",
              }}
              labelFormatter={(d: string) => `Periodo: ${d}`}
              formatter={(value: number) => [formatValue(activeTab.metric, value), METRIC_LABELS[activeTab.metric] ?? activeTab.metric]}
            />
            <Bar
              dataKey="value"
              fill="#f59e0b"
              radius={[3, 3, 0, 0]}
              maxBarSize={40}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
