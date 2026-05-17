import { useQuery } from "@tanstack/react-query"
import { fundamentals } from "@/lib/api"
import type { PriceHistoryResponse } from "@/lib/types"

export function usePriceHistory(
  ticker: string | undefined,
  period = "5y",
  interval = "1d",
) {
  return useQuery<PriceHistoryResponse>({
    queryKey: ["priceHistory", ticker, period, interval],
    queryFn: () => fundamentals.priceHistory(ticker!, period, interval),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 2,
  })
}
