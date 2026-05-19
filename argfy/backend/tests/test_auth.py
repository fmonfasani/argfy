"""
Tests de auth: register → login → JWT → protected endpoint.
"""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_api_key,
    hash_api_key,
)
from app.config.config import settings


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


class TestPasswordHashing:
    """
    Unit tests del modulo de password hashing.
    Cubre regresion del bug passlib 1.7.4 + bcrypt 4.x (commit f57b2f8):
    passlib trapeaba el AttributeError de bcrypt.__about__ y rechazaba
    passwords legitimas con "password cannot be longer than 72 bytes".
    """

    def test_hash_produces_bcrypt_format(self):
        h = hash_password("testpass123")
        assert h.startswith("$2b$") or h.startswith("$2a$")
        assert len(h) == 60

    def test_hash_is_not_deterministic(self):
        h1 = hash_password("testpass123")
        h2 = hash_password("testpass123")
        assert h1 != h2

    def test_verify_correct_password(self):
        h = hash_password("testpass123")
        assert verify_password("testpass123", h) is True

    def test_verify_wrong_password(self):
        h = hash_password("testpass123")
        assert verify_password("wrongpass", h) is False

    def test_verify_empty_password_against_hash(self):
        h = hash_password("testpass123")
        assert verify_password("", h) is False

    def test_password_at_72_bytes_is_accepted(self):
        pw = "a" * 72
        h = hash_password(pw)
        assert verify_password(pw, h) is True

    def test_password_over_72_bytes_is_truncated_not_rejected(self):
        """REGRESION: passlib rechazaba esto. bcrypt directo trunca."""
        pw = "x" * 200
        h = hash_password(pw)
        assert verify_password(pw, h) is True

    def test_passwords_differing_beyond_72_bytes_collide(self):
        """Documenta el comportamiento: bcrypt trunca a 72 bytes."""
        pw_a = "a" * 72 + "BBBB"
        pw_b = "a" * 72 + "CCCC"
        h = hash_password(pw_a)
        assert verify_password(pw_b, h) is True

    def test_password_with_unicode(self):
        pw = "contraseña-segura-ñ-á-é-ü-2026"
        h = hash_password(pw)
        assert verify_password(pw, h) is True

    def test_password_with_emoji(self):
        pw = "test-🔐-pass"
        h = hash_password(pw)
        assert verify_password(pw, h) is True

    def test_long_unicode_password_does_not_raise(self):
        """Bug original: 'password cannot be longer than 72 bytes'
        cuando los caracteres unicode hacen overflow del limite en bytes."""
        pw = "ñ" * 50
        h = hash_password(pw)
        assert verify_password(pw, h) is True


class TestJWT:
    """JWT create/decode round-trip + edge cases."""

    def test_create_and_decode_roundtrip(self):
        token = create_access_token(
            user_id="user-123",
            tenant_id="tenant-456",
            role="admin",
        )
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["tenant_id"] == "tenant-456"
        assert payload["role"] == "admin"

    def test_decode_invalid_signature_returns_none(self):
        token = create_access_token("u", "t", "admin")
        tampered = token[:-4] + ("AAAA" if token[-4:] != "AAAA" else "BBBB")
        assert decode_access_token(tampered) is None

    def test_decode_garbage_returns_none(self):
        assert decode_access_token("not-a-jwt") is None
        assert decode_access_token("") is None
        assert decode_access_token("a.b.c") is None

    def test_decode_wrong_signing_key_returns_none(self):
        now = datetime.now(timezone.utc)
        fake = jwt.encode(
            {"sub": "evil", "tenant_id": "x", "role": "admin",
             "iat": now, "exp": now + timedelta(hours=1)},
            "wrong-secret",
            algorithm=settings.JWT_ALGORITHM,
        )
        assert decode_access_token(fake) is None

    def test_expired_token_returns_none(self):
        now = datetime.now(timezone.utc)
        expired = jwt.encode(
            {"sub": "u", "tenant_id": "t", "role": "admin",
             "iat": now - timedelta(hours=2),
             "exp": now - timedelta(hours=1)},
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        assert decode_access_token(expired) is None

    def test_token_includes_iat_and_exp(self):
        token = create_access_token("u", "t", "admin")
        payload = decode_access_token(token)
        assert payload is not None
        assert "iat" in payload
        assert "exp" in payload
        assert payload["exp"] > payload["iat"]


class TestApiKey:
    """API key generation + hashing."""

    def test_generate_returns_three_components(self):
        raw, prefix, key_hash = generate_api_key()
        assert raw.startswith("argfy_")
        assert prefix == raw[:16]
        assert len(key_hash) == 64

    def test_generate_is_unique(self):
        keys = {generate_api_key()[0] for _ in range(20)}
        assert len(keys) == 20

    def test_hash_api_key_matches_generated_hash(self):
        raw, _, key_hash = generate_api_key()
        assert hash_api_key(raw) == key_hash

    def test_hash_is_deterministic(self):
        raw = "argfy_test_key_value"
        assert hash_api_key(raw) == hash_api_key(raw)

    def test_hash_differs_for_different_inputs(self):
        assert hash_api_key("argfy_a") != hash_api_key("argfy_b")


class TestPasswordIntegrationWithRouter:
    """Integration: el flow completo register/login funciona con bcrypt direct.
    Cubre el escenario real del bug de f57b2f8."""

    def test_register_with_long_password_succeeds(self, client, seed_plan_features):
        long_pw = "x" * 100
        resp = client.post("/api/v1/auth/register", json={
            "email": "longpw@argfy.com",
            "password": long_pw,
        })
        assert resp.status_code == 200, f"long password rechazada: {resp.json()}"
        assert "access_token" in resp.json()

    def test_register_with_unicode_password_succeeds(self, client, seed_plan_features):
        resp = client.post("/api/v1/auth/register", json={
            "email": "unicode@argfy.com",
            "password": "Pásswörd-ñ-2026",
        })
        assert resp.status_code == 200

    def test_login_after_register_with_long_password(self, client, seed_plan_features):
        long_pw = "y" * 100
        client.post("/api/v1/auth/register", json={
            "email": "longlogin@argfy.com",
            "password": long_pw,
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "longlogin@argfy.com",
            "password": long_pw,
        })
        assert resp.status_code == 200
