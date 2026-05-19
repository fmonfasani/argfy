export function formatPct(value: number | null | undefined, decimals = 1): string {
  if (value == null) return "-"
  return `${(value * 100).toFixed(decimals)}%`
}

export function formatRatio(value: number | null | undefined, decimals = 1): string {
  if (value == null) return "-"
  return value.toFixed(decimals)
}

export function formatMoney(value: number | null | undefined, decimals = 2): string {
  if (value == null) return "-"
  return `$${value.toFixed(decimals)}`
}
