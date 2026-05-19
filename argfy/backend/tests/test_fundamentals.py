"""
Tests de endpoints críticos: /screener, /coverage, detail.
"""


class TestScreener:
    def test_screener_returns_data(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 2
        assert data["total"] >= 2

    def test_screener_filter_country(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?country=US")
        assert resp.status_code == 200
        data = resp.json()
        for row in data["data"]:
            assert row["country"] == "US"

    def test_screener_filter_per_max(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?per_max=10")
        assert resp.status_code == 200
        data = resp.json()
        for row in data["data"]:
            assert row["per_ttm"] is None or row["per_ttm"] <= 10

    def test_screener_search_q(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?q=apple")
        assert resp.status_code == 200
        data = resp.json()
        assert any("Apple" in (r.get("nombre") or "") for r in data["data"])

    def test_screener_pagination(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?offset=0&limit=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["limit"] == 1

    def test_screener_sort(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?sort_by=per_ttm&sort_desc=true")
        assert resp.status_code == 200
        data = resp.json()
        if len(data["data"]) >= 2:
            assert data["data"][0]["per_ttm"] >= data["data"][-1]["per_ttm"]


class TestCoverage:
    def test_coverage_returns(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/coverage")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        assert "per_ttm" in data["coverage"]


class TestDetail:
    def test_detail_existing(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/AAPL")
        assert resp.status_code == 200
        data = resp.json()
        assert data["company"]["nombre"] == "Apple Inc."

    def test_detail_not_found(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/INVALID")
        assert resp.status_code == 404


class TestScreenerFilters:
    """Filtros adicionales no cubiertos arriba.
    Seed: AAPL roe=0.35 margen=0.24 deuda=1.2 payout=0.15 exchange=NMS country=US
          GGAL roe=0.22 margen=0.18 deuda=3.5 payout=0.40 exchange=BYMA country=AR
          MELI roe=0.28 margen=0.08 deuda=2.1 payout=0.0  exchange=NMS country=US"""

    def test_filter_roe_min(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?roe_min=0.30")
        assert resp.status_code == 200
        tickers = [r["byma_ticker"] for r in resp.json()["data"]]
        assert "AAPL" in tickers
        assert "GGAL" not in tickers
        assert "MELI" not in tickers

    def test_filter_margen_min(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?margen_min=0.20")
        assert resp.status_code == 200
        tickers = [r["byma_ticker"] for r in resp.json()["data"]]
        assert tickers == ["AAPL"]

    def test_filter_deuda_max(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?deuda_max=2.0")
        assert resp.status_code == 200
        tickers = [r["byma_ticker"] for r in resp.json()["data"]]
        assert "AAPL" in tickers
        assert "GGAL" not in tickers

    def test_filter_payout_max(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?payout_max=0.20")
        assert resp.status_code == 200
        tickers = sorted(r["byma_ticker"] for r in resp.json()["data"])
        assert tickers == ["AAPL", "MELI"]

    def test_filter_exchange(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?exchange=BYMA")
        assert resp.status_code == 200
        tickers = [r["byma_ticker"] for r in resp.json()["data"]]
        assert tickers == ["GGAL"]

    def test_filter_exchange_case_insensitive(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?exchange=byma")
        assert resp.status_code == 200
        assert any(r["byma_ticker"] == "GGAL" for r in resp.json()["data"])

    def test_filter_combined(self, client, seed_ratios):
        resp = client.get(
            "/api/v1/fundamentals/screener?country=US&deuda_max=1.5&roe_min=0.30"
        )
        assert resp.status_code == 200
        tickers = [r["byma_ticker"] for r in resp.json()["data"]]
        assert tickers == ["AAPL"]

    def test_filter_per_range(self, client, seed_ratios):
        resp = client.get(
            "/api/v1/fundamentals/screener?per_min=10&per_max=30"
        )
        assert resp.status_code == 200
        for r in resp.json()["data"]:
            assert 10 <= r["per_ttm"] <= 30

    def test_filter_no_results(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?per_max=0.001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["total"] == 0
        assert data["data"] == []

    def test_filter_country_otros(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?country=OTROS")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0


class TestScreenerValidation:
    def test_offset_negative_rejected(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?offset=-1")
        assert resp.status_code == 422

    def test_limit_zero_rejected(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?limit=0")
        assert resp.status_code == 422

    def test_limit_over_max_rejected(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?limit=5000")
        assert resp.status_code == 422

    def test_invalid_sort_by_silently_ignored(self, client, seed_ratios):
        """Comportamiento actual: sort_by inválido no rompe, simplemente no ordena."""
        resp = client.get("/api/v1/fundamentals/screener?sort_by=not_a_column")
        assert resp.status_code == 200
        assert resp.json()["sort"]["by"] == "not_a_column"

    def test_response_includes_filters_echo(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/screener?country=US&per_max=50")
        body = resp.json()
        assert body["filters"]["country"] == "US"
        assert body["filters"]["per_max"] == 50


class TestCoverageStructure:
    def test_coverage_all_ratio_keys_present(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/coverage")
        cov = resp.json()["coverage"]
        for key in ("per_ttm", "eps_ttm_diluted", "margen_neto_ttm",
                    "roe_cagr_5y", "deuda_total_sobre_ebitda", "payout_ttm"):
            assert key in cov
            assert "con_dato" in cov[key]
            assert "pct" in cov[key]

    def test_coverage_empty_db(self, client):
        resp = client.get("/api/v1/fundamentals/coverage")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["coverage"] == {}


class TestDetailStructure:
    def test_detail_returns_ratios_and_company(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/AAPL")
        body = resp.json()
        assert "ratios" in body
        assert "company" in body
        assert body["ratios"]["byma_ticker"] == "AAPL"
        assert body["ratios"]["per_ttm"] == 28.5
        assert body["company"]["sector"] == "Technology"

    def test_detail_lowercase_ticker_is_normalized(self, client, seed_ratios):
        resp = client.get("/api/v1/fundamentals/aapl")
        assert resp.status_code == 200
        assert resp.json()["ratios"]["byma_ticker"] == "AAPL"
