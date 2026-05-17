"""
Tests de endpoints críticos: /screener, /coverage, detail.
"""
import pytest
from fastapi import status


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
