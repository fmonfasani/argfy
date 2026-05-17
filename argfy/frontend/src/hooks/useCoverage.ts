import { useQuery } from "@tanstack/react-query"
import { fundamentals } from "@/lib/api"
import type { CoverageResponse } from "@/lib/types"

export function useCoverage() {
  return useQuery<CoverageResponse>({
    queryKey: ["coverage"],
    queryFn: () => fundamentals.coverage(),
    staleTime: 1000 * 60 * 10,
  })
}
