"""
Fixtures compartidos para tests.
SQLite in-memory para cada test, con datos de ejemplo.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

from app.database import Base, get_db
from app.main import app
from app.models import Company, RatioQuarterly, PlanFeature
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_companies(db_session):
    companies = [
        Company(byma_ticker="AAPL", ticker_sec="AAPL", cik="0000320193",
                nombre="Apple Inc.", exchange="NMS", country="US",
                sector="Technology", industry="Consumer Electronics", has_sec=True),
        Company(byma_ticker="GGAL", ticker_sec="GGAL", cik="0000870762",
                nombre="Grupo Financiero Galicia", exchange="BYMA", country="AR",
                sector="Financial", industry="Banking", has_sec=False),
        Company(byma_ticker="MELI", ticker_sec="MELI", cik="0001099590",
                nombre="MercadoLibre Inc.", exchange="NMS", country="US",
                sector="Technology", industry="E-Commerce", has_sec=True),
    ]
    for c in companies:
        db_session.add(c)
    db_session.commit()
    return companies


@pytest.fixture(scope="function")
def seed_ratios(db_session, seed_companies):
    ratios = [
        RatioQuarterly(
            byma_ticker="AAPL", period_end=date(2025, 12, 31),
            per_ttm=28.5, eps_ttm_diluted=6.2, margen_neto_ttm=0.24,
            roe_cagr_5y=0.35, deuda_total_sobre_ebitda=1.2,
            payout_ttm=0.15, revenue_ttm=395000, netincome_ttm=95000,
            ebitda_ttm=135000, fcf_ttm=100000,
            precio_usd=175.0, currency="USD", exchange="NMS",
            year_high=198.0, year_low=140.0,
        ),
        RatioQuarterly(
            byma_ticker="GGAL", period_end=date(2025, 12, 31),
            per_ttm=6.2, eps_ttm_diluted=3.1, margen_neto_ttm=0.18,
            roe_cagr_5y=0.22, deuda_total_sobre_ebitda=3.5,
            payout_ttm=0.40, revenue_ttm=8500, netincome_ttm=1500,
            ebitda_ttm=2800, fcf_ttm=1200,
            precio_usd=22.0, currency="USD", exchange="BYMA",
            year_high=30.0, year_low=15.0,
        ),
        RatioQuarterly(
            byma_ticker="MELI", period_end=date(2025, 12, 31),
            per_ttm=45.0, eps_ttm_diluted=12.8, margen_neto_ttm=0.08,
            roe_cagr_5y=0.28, deuda_total_sobre_ebitda=2.1,
            payout_ttm=0.0, revenue_ttm=18000, netincome_ttm=1400,
            ebitda_ttm=3500, fcf_ttm=2800,
            precio_usd=1500.0, currency="USD", exchange="NMS",
            year_high=2000.0, year_low=1200.0,
        ),
    ]
    for r in ratios:
        db_session.add(r)
    db_session.commit()
    return ratios


@pytest.fixture(scope="function")
def seed_plan_features(db_session):
    features = [
        PlanFeature(plan="free", feature_key="screener_basic", enabled=True),
        PlanFeature(plan="pro", feature_key="screener_basic", enabled=True),
        PlanFeature(plan="pro", feature_key="historical_prices", enabled=True),
        PlanFeature(plan="pro", feature_key="metric_history", enabled=True),
        PlanFeature(plan="pro", feature_key="csv_export", enabled=True),
        PlanFeature(plan="enterprise", feature_key="screener_basic", enabled=True),
        PlanFeature(plan="enterprise", feature_key="historical_prices", enabled=True),
        PlanFeature(plan="enterprise", feature_key="metric_history", enabled=True),
        PlanFeature(plan="enterprise", feature_key="csv_export", enabled=True),
        PlanFeature(plan="enterprise", feature_key="api_access", enabled=True),
        PlanFeature(plan="enterprise", feature_key="team_invitations", enabled=True),
        PlanFeature(plan="enterprise", feature_key="admin_etl_trigger", enabled=True),
    ]
    for f in features:
        db_session.add(f)
    db_session.commit()
    return features
