-- argfy schema · Postgres 16
-- Diseñado para recibir el entregable de Fase 2 (data_export/) 1:1.
--
-- Convenciones:
--   - timestamps UTC con timezone
--   - claves naturales sobre byma_ticker (único universal del proyecto)
--   - JSONB para metricas crudas XBRL/yfinance (queryable + comprimido)
--   - history-friendly: una fila por (ticker, period_end) en fundamentals,
--     una fila por (ticker, date) en precios

SET TIME ZONE 'UTC';

-- =========================================================================
-- companies — master único de tickers
-- =========================================================================
CREATE TABLE IF NOT EXISTS companies (
    byma_ticker   VARCHAR(20)  PRIMARY KEY,
    ticker_sec    VARCHAR(20),
    cik           VARCHAR(20),
    isin          VARCHAR(20),
    nombre        VARCHAR(200),
    exchange      VARCHAR(20),
    country       VARCHAR(8),
    sector        VARCHAR(80),
    industry      VARCHAR(120),
    currency      VARCHAR(8),
    source_tier   SMALLINT,                -- 1=SEC full, 2=yf full, 3=parcial, 4=solo precios
    has_sec       BOOLEAN DEFAULT FALSE,
    has_yf        BOOLEAN DEFAULT FALSE,
    has_fmp       BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_companies_cik        ON companies(cik) WHERE cik IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_companies_ticker_sec ON companies(ticker_sec) WHERE ticker_sec IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_companies_country    ON companies(country);

-- =========================================================================
-- prices_daily — OHLCV diario, una fila por (ticker, date)
-- =========================================================================
CREATE TABLE IF NOT EXISTS prices_daily (
    byma_ticker  VARCHAR(20) NOT NULL REFERENCES companies(byma_ticker) ON DELETE CASCADE,
    date         DATE        NOT NULL,
    open         DOUBLE PRECISION,
    high         DOUBLE PRECISION,
    low          DOUBLE PRECISION,
    close        DOUBLE PRECISION,
    adj_close    DOUBLE PRECISION,
    volume       BIGINT,
    currency     VARCHAR(8),
    source       VARCHAR(20),
    PRIMARY KEY (byma_ticker, date)
);
CREATE INDEX IF NOT EXISTS idx_prices_date ON prices_daily(date);

-- =========================================================================
-- fundamentals_raw — bag de métricas XBRL/yfinance/FMP, una fila por ticker
-- =========================================================================
CREATE TABLE IF NOT EXISTS fundamentals_raw (
    cik          VARCHAR(20) PRIMARY KEY,
    ticker_sec   VARCHAR(20),
    source       VARCHAR(20),
    as_of        TIMESTAMPTZ,
    currency     VARCHAR(8),
    metrics      JSONB       NOT NULL,    -- {"Revenues": {"unit": "USD", "datos": [...]}, ...}
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_fundraw_ticker      ON fundamentals_raw(ticker_sec);
CREATE INDEX IF NOT EXISTS idx_fundraw_metrics_gin ON fundamentals_raw USING GIN (metrics);

-- =========================================================================
-- fundamentals_quarterly — balances trimestrales normalizados
-- una fila por (ticker, period_end), histórica
-- =========================================================================
CREATE TABLE IF NOT EXISTS fundamentals_quarterly (
    byma_ticker      VARCHAR(20) NOT NULL REFERENCES companies(byma_ticker) ON DELETE CASCADE,
    period_end       DATE        NOT NULL,
    period_start     DATE,
    fy               SMALLINT,
    fp               VARCHAR(4),           -- "Q1".."Q4", "FY"
    form             VARCHAR(10),          -- "10-K", "10-Q", "20-F", etc.
    filed            DATE,
    revenue          DOUBLE PRECISION,
    gross_profit     DOUBLE PRECISION,
    ebit             DOUBLE PRECISION,
    ebitda           DOUBLE PRECISION,
    net_income       DOUBLE PRECISION,
    eps_diluted      DOUBLE PRECISION,
    diluted_shares   DOUBLE PRECISION,
    cfo              DOUBLE PRECISION,
    capex            DOUBLE PRECISION,
    fcf              DOUBLE PRECISION,
    dividends_paid   DOUBLE PRECISION,
    lt_debt          DOUBLE PRECISION,
    st_debt          DOUBLE PRECISION,
    total_debt       DOUBLE PRECISION,
    equity           DOUBLE PRECISION,
    total_assets     DOUBLE PRECISION,
    cash             DOUBLE PRECISION,
    currency         VARCHAR(8),
    source           VARCHAR(20),
    PRIMARY KEY (byma_ticker, period_end)
);
CREATE INDEX IF NOT EXISTS idx_fundq_period ON fundamentals_quarterly(period_end);

-- =========================================================================
-- ratios_quarterly — ratios calculados por trimestre (output del motor)
-- una fila por (ticker, period_end)
-- =========================================================================
CREATE TABLE IF NOT EXISTS ratios_quarterly (
    byma_ticker              VARCHAR(20) NOT NULL REFERENCES companies(byma_ticker) ON DELETE CASCADE,
    period_end               DATE        NOT NULL,
    as_of                    TIMESTAMPTZ DEFAULT NOW(),
    ticker_sec               VARCHAR(20),
    cik                      VARCHAR(20),

    -- Precio + 52w (snapshot al period_end o último disponible)
    precio_usd               DOUBLE PRECISION,
    currency                 VARCHAR(8),
    exchange                 VARCHAR(20),
    year_high                DOUBLE PRECISION,
    year_low                 DOUBLE PRECISION,
    dif_max_52w              DOUBLE PRECISION,
    dif_min_52w              DOUBLE PRECISION,

    -- Ratios fundamentales
    per_ttm                  DOUBLE PRECISION,
    eps_ttm_diluted          DOUBLE PRECISION,
    margen_neto_ttm          DOUBLE PRECISION,
    roe_cagr_5y              DOUBLE PRECISION,
    deuda_lp_sobre_ebitda    DOUBLE PRECISION,
    deuda_total_sobre_ebitda DOUBLE PRECISION,
    fcfonce_equity_lp        DOUBLE PRECISION,
    fcfonce_neto_caja        DOUBLE PRECISION,
    payout_ttm               DOUBLE PRECISION,
    cagr_eps_5y              DOUBLE PRECISION,

    -- Componentes crudos (auditoría)
    revenue_ttm              DOUBLE PRECISION,
    netincome_ttm            DOUBLE PRECISION,
    ebitda_ttm               DOUBLE PRECISION,
    fcf_ttm                  DOUBLE PRECISION,
    diluted_shares           DOUBLE PRECISION,
    equity                   DOUBLE PRECISION,
    lt_debt                  DOUBLE PRECISION,
    deuda_total              DOUBLE PRECISION,

    PRIMARY KEY (byma_ticker, period_end)
);
CREATE INDEX IF NOT EXISTS idx_ratios_per                ON ratios_quarterly(per_ttm)                  WHERE per_ttm                  IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ratios_roe                ON ratios_quarterly(roe_cagr_5y)              WHERE roe_cagr_5y              IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ratios_margen_neto_ttm    ON ratios_quarterly(margen_neto_ttm)          WHERE margen_neto_ttm          IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ratios_deuda_total_ebitda ON ratios_quarterly(deuda_total_sobre_ebitda) WHERE deuda_total_sobre_ebitda IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ratios_payout_ttm         ON ratios_quarterly(payout_ttm)               WHERE payout_ttm               IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ratios_exchange           ON ratios_quarterly(exchange)                 WHERE exchange                 IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ratios_period_end         ON ratios_quarterly(period_end);

-- =========================================================================
-- fx_rates — USD/ARS (CCL, MEP, oficial) diario
-- =========================================================================
CREATE TABLE IF NOT EXISTS fx_rates (
    date     DATE NOT NULL,
    ccl      DOUBLE PRECISION,
    mep      DOUBLE PRECISION,
    oficial  DOUBLE PRECISION,
    source   VARCHAR(20),
    PRIMARY KEY (date)
);

-- Views legacy eliminadas. El router de fundamentals lee directo de
-- ratios_quarterly + companies con MAX(period_end) por ticker.
