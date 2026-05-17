"""
Tests de auth: register → login → JWT → protected endpoint.
"""
from fastapi import status


class TestAuth:
    def test_register(self, client, seed_plan_features):
        resp = client.post("/api/v1/auth/register", json={
            "email": "test@argfy.com",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@argfy.com"

    def test_register_duplicate(self, client, seed_plan_features):
        client.post("/api/v1/auth/register", json={
            "email": "dup@argfy.com",
            "password": "testpass123",
        })
        resp = client.post("/api/v1/auth/register", json={
            "email": "dup@argfy.com",
            "password": "testpass123",
        })
        assert resp.status_code == 409

    def test_login(self, client, seed_plan_features):
        client.post("/api/v1/auth/register", json={
            "email": "login@argfy.com",
            "password": "testpass123",
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "login@argfy.com",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client, seed_plan_features):
        client.post("/api/v1/auth/register", json={
            "email": "wrong@argfy.com",
            "password": "correctpass",
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "wrong@argfy.com",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_me_authenticated(self, client, seed_plan_features):
        client.post("/api/v1/auth/register", json={
            "email": "me@argfy.com",
            "password": "testpass123",
        })
        login = client.post("/api/v1/auth/login", json={
            "email": "me@argfy.com",
            "password": "testpass123",
        })
        token = login.json()["access_token"]
        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@argfy.com"

    def test_me_no_auth(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401
