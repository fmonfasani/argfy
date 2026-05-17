import { useQuery } from "@tanstack/react-query"
import { fundamentals } from "@/lib/api"
import type { ScreenerFilters, ScreenerResponse } from "@/lib/types"

export function useScreener(filters: ScreenerFilters) {
  return useQuery<ScreenerResponse>({
    queryKey: ["screener", filters],
    queryFn: () => fundamentals.screener(filters),
    staleTime: 1000 * 60 * 2,
    retry: 1,
  })
}
