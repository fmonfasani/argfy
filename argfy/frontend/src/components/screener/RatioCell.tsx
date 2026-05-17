import { formatPct, formatRatio, formatMoney } from "@/lib/utils"

type Rule =
  | { type: "pct"; green: number; red: number }
  | { type: "ratio"; green: number; red: number; inverse?: boolean }
  | { type: "money" }

interface RatioCellProps {
  value: number | null | undefined
  rule: Rule
  decimals?: number
}

function color(value: number, rule: Rule): string {
  switch (rule.type) {
    case "pct":
      if (value >= rule.green) return "text-green-400"
      if (value <= rule.red) return "text-red-400"
      return "text-amber-400"
    case "ratio":
      if (rule.inverse) {
        if (value <= rule.green) return "text-green-400"
        if (value >= rule.red) return "text-red-400"
      } else {
        if (value >= rule.green) return "text-green-400"
        if (value <= rule.red) return "text-red-400"
      }
      return "text-amber-400"
    case "money":
      return "text-white"
  }
}

export default function RatioCell({ value, rule, decimals }: RatioCellProps) {
  if (value == null) return <span className="text-slate-500">-</span>

  const cls = color(value, rule)

  switch (rule.type) {
    case "pct":
      return <span className={`font-mono ${cls}`}>{formatPct(value, decimals ?? 1)}</span>
    case "ratio":
      return <span className={`font-mono ${cls}`}>{formatRatio(value, decimals ?? 1)}</span>
    case "money":
      return <span className={`font-mono ${cls}`}>{formatMoney(value, decimals ?? 2)}</span>
  }
}

export const PER_RULE: Rule = { type: "ratio", green: 15, red: 30 }
export const ROE_RULE: Rule = { type: "pct", green: 0.2, red: 0 }
export const MARGEN_RULE: Rule = { type: "pct", green: 0.15, red: 0 }
export const DEUDA_RULE: Rule = { type: "ratio", green: 2, red: 5 }
export const PAYOUT_RULE: Rule = { type: "pct", green: 0.5, red: 1 }
