-- Migration 001 — Indexes adicionales para el screener
--
-- Contexto: el endpoint /api/v1/fundamentals/screener filtra por 6 columnas
-- de ratios_quarterly. Solo 3 tienen indice (per_ttm, roe_cagr_5y, period_end).
-- Para 213 tickers x N quarters de historia, el seq scan se vuelve doloroso.
--
-- Aplicacion en prod:
--   docker exec argfy-db psql -U <user> -d argfy_prod -f /tmp/001_add_screener_indexes.sql
--
-- Reversible: DROP INDEX IF EXISTS <name>;

\set ON_ERROR_STOP on
SET TIME ZONE 'UTC';

-- Filtros del screener no cubiertos hasta hoy
CREATE INDEX IF NOT EXISTS idx_ratios_margen_neto_ttm
    ON ratios_quarterly(margen_neto_ttm)
    WHERE margen_neto_ttm IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ratios_deuda_total_ebitda
    ON ratios_quarterly(deuda_total_sobre_ebitda)
    WHERE deuda_total_sobre_ebitda IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ratios_payout_ttm
    ON ratios_quarterly(payout_ttm)
    WHERE payout_ttm IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ratios_exchange
    ON ratios_quarterly(exchange)
    WHERE exchange IS NOT NULL;

-- Verificacion
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'ratios_quarterly'
ORDER BY indexname;
