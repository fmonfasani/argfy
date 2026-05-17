import { useQuery } from "@tanstack/react-query"
import { fundamentals } from "@/lib/api"
import type { MetricHistoryResponse } from "@/lib/types"

export function useMetricHistory(
  ticker: string | undefined,
  metric: string | undefined,
  fromDate?: string,
  toDate?: string,
) {
  return useQuery<MetricHistoryResponse>({
    queryKey: ["metricHistory", ticker, metric, fromDate, toDate],
    queryFn: () => fundamentals.metricHistory(ticker!, metric!, fromDate, toDate),
    enabled: !!ticker && !!metric,
    staleTime: 1000 * 60 * 5,
  })
}
