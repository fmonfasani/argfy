import { z } from "zod"

// ───── Response schemas (zod, validados en apiFetch) ─────

export const RatioSnapshotSchema = z.object({
  byma_ticker:              z.string(),
  ticker_sec:               z.string().nullable(),
  cik:                      z.string().nullable(),
  period_end:               z.string().nullable(),
  as_of:                    z.string().nullable(),
  precio_usd:               z.number().nullable(),
  currency:                 z.string().nullable(),
  exchange:                 z.string().nullable(),
  nombre:                   z.string().nullable().optional(),
  country:                  z.string().nullable().optional(),
  year_high:                z.number().nullable(),
  year_low:                 z.number().nullable(),
  dif_max_52w:              z.number().nullable(),
  dif_min_52w:              z.number().nullable(),
  per_ttm:                  z.number().nullable(),
  eps_ttm_diluted:          z.number().nullable(),
  margen_neto_ttm:          z.number().nullable(),
  roe_cagr_5y:              z.number().nullable(),
  deuda_lp_sobre_ebitda:    z.number().nullable(),
  deuda_total_sobre_ebitda: z.number().nullable(),
  fcfonce_equity_lp:        z.number().nullable(),
  fcfonce_neto_caja:        z.number().nullable(),
  payout_ttm:               z.number().nullable(),
})

export type RatioSnapshot = z.infer<typeof RatioSnapshotSchema>

export const ScreenerResponseSchema = z.object({
  count:   z.number(),
  total:   z.number(),
  offset:  z.number(),
  limit:   z.number(),
  filters: z.record(z.string(), z.unknown()),
  sort:    z.object({ by: z.string(), desc: z.boolean() }),
  data:    z.array(RatioSnapshotSchema),
})

export type ScreenerResponse = z.infer<typeof ScreenerResponseSchema>

export const CoverageResponseSchema = z.object({
  total:    z.number(),
  coverage: z.record(z.string(), z.object({ con_dato: z.number(), pct: z.number() })),
})

export type CoverageResponse = z.infer<typeof CoverageResponseSchema>

export const TickerDetailSchema = z.object({
  ratios:  RatioSnapshotSchema,
  company: z.object({
    nombre:      z.string().nullable(),
    ticker_sec:  z.string().nullable(),
    cik:         z.string().nullable(),
    exchange:    z.string().nullable(),
    country:     z.string().nullable(),
    sector:      z.string().nullable(),
    industry:    z.string().nullable(),
    has_sec:     z.boolean().nullable(),
    source_tier: z.number().nullable(),
  }),
})

export type TickerDetail = z.infer<typeof TickerDetailSchema>

export const PriceDataPointSchema = z.object({
  date:      z.string(),
  open:      z.number().nullable(),
  high:      z.number().nullable(),
  low:       z.number().nullable(),
  close:     z.number().nullable(),
  adj_close: z.number().nullable(),
  volume:    z.number().nullable(),
})

export const PriceHistoryResponseSchema = z.object({
  byma_ticker: z.string(),
  period:      z.string(),
  interval:    z.string(),
  count:       z.number(),
  data:        z.array(PriceDataPointSchema),
})

export type PriceHistoryResponse = z.infer<typeof PriceHistoryResponseSchema>

export const MetricDataPointSchema = z.object({
  period_end: z.string(),
  value:      z.number().nullable(),
})

export const MetricHistoryResponseSchema = z.object({
  byma_ticker: z.string(),
  metric:      z.string(),
  count:       z.number(),
  data:        z.array(MetricDataPointSchema),
})

export type MetricHistoryResponse = z.infer<typeof MetricHistoryResponseSchema>

// ───── Filter types (no need zod, only used client-side) ─────

export interface ScreenerFilters {
  per_max?:    number
  per_min?:    number
  roe_min?:    number
  margen_min?: number
  deuda_max?:  number
  payout_max?: number
  exchange?:   string
  country?:    string
  q?:          string
  sort_by?:    string
  sort_desc?:  boolean
  offset?:     number
  limit?:      number
}

export type PeriodOption = "1m" | "6m" | "1y" | "5y" | "max"
export type MetricOption =
  | "per_ttm" | "eps_ttm_diluted" | "margen_neto_ttm" | "roe_cagr_5y"
  | "deuda_lp_sobre_ebitda" | "deuda_total_sobre_ebitda"
  | "fcfonce_equity_lp" | "fcfonce_neto_caja" | "payout_ttm" | "cagr_eps_5y"
  | "revenue_ttm" | "netincome_ttm" | "ebitda_ttm" | "fcf_ttm"
