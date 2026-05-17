import { useQuery } from "@tanstack/react-query"
import { fundamentals } from "@/lib/api"
import type { TickerDetail } from "@/lib/types"

export function useTickerDetail(ticker: string | undefined) {
  return useQuery<TickerDetail>({
    queryKey: ["ticker", ticker],
    queryFn: () => fundamentals.detail(ticker!),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 5,
  })
}
