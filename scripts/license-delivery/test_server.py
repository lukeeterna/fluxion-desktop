"""
Test suite per FLUXION License Delivery Server (server.py)

Copertura:
- verify_ls_signature: HMAC-SHA256 validation
- /health GET
- /webhook/lemonsqueezy POST (happy path + edge cases)
- /api/activate POST (happy path + tutti gli errori)

Esegui: python3 -m pytest test_server.py -v
"""

import asyncio
import hashlib
import hmac
import json
import os
import sqlite3
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

# ── Setup env prima di importare server.py ─────────────────────────────────

os.environ["LS_WEBHOOK_SECRET"] = "test-secret-xyz"
os.environ["SMTP_USER"] = "test@example.com"
os.environ["SMTP_PASS"] = "test-pass"
os.environ["FLUXION_KEYGEN_PATH"] = "/fake/fluxion-keygen"
os.environ["KEYPAIR_PATH"] = "/fake/keypair.json"
os.environ["DB_PATH"] = ":memory:"

import server  # noqa: E402

# ── Helpers ───────────────────────────────────────────────────────────────────

SECRET = "test-secret-xyz"

def sign(payload: bytes, secret: str = SECRET) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def order_payload(
    order_id="ORD-001", email="cliente@test.it",
    product_name="Fluxion Pro", event="order_created"
) -> dict:
    return {
        "meta": {"event_name": event},
        "data": {
            "id": order_id,
            "attributes": {
                "user_email": email,
                "first_order_item": {"product_name": product_name},
            },
        },
    }


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY, email TEXT NOT NULL, tier TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0, activate_tries INTEGER NOT NULL DEFAULT 0,
            created_at REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE activations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL,
            fingerprint TEXT NOT NULL, ip TEXT, activated_at REAL NOT NULL
        )
    """)
    conn.commit()
    return conn


def seed(db, order_id="ORD-001", email="user@test.it", tier="pro", used=0, tries=0):
    db.execute(
        "INSERT INTO orders (order_id,email,tier,used,activate_tries,created_at) VALUES(?,?,?,?,?,?)",
        (order_id, email, tier, used, tries, time.time()),
    )
    db.commit()


def make_app(db=None) -> web.Application:
    app = web.Application(middlewares=[server.cors_middleware])
    app["db"] = db or make_db()
    app.router.add_get("/health", server.handle_health)
    app.router.add_post("/webhook/lemonsqueezy", server.handle_webhook_ls)
    app.router.add_post("/api/activate", server.handle_activate)
    return app


GOOD_LICENSE = {"version": "1.0", "tier": "pro", "fingerprint": "FP1", "sig": "SIG"}
KEYGEN_OK   = MagicMock(returncode=0, stdout=json.dumps(GOOD_LICENSE), stderr="")
KEYGEN_FAIL = MagicMock(returncode=1, stdout="", stderr="err")


# ── Sync tests: verify_ls_signature ──────────────────────────────────────────

class TestVerifyLsSignature:

    def test_valid(self):
        p = b'{"test":true}'
        assert server.verify_ls_signature(p, sign(p)) is True

    def test_invalid(self):
        assert server.verify_ls_signature(b"payload", "badfeed") is False

    def test_empty(self):
        assert server.verify_ls_signature(b"payload", "") is False

    def test_tampered_payload(self):
        p = b'{"amount":100}'
        sig = sign(p)
        assert server.verify_ls_signature(b'{"amount":999}', sig) is False

    def test_wrong_secret(self):
        p = b'{"test":true}'
        sig = sign(p, secret="other")
        assert server.verify_ls_signature(p, sig) is False

    def test_whitespace_stripped(self):
        p = b'{"test":true}'
        sig = "  " + sign(p) + "  "
        assert server.verify_ls_signature(p, sig) is True


# ── Async tests ───────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    return make_db()


@pytest.fixture
def app(db):
    return make_app(db)


@pytest.mark.asyncio
async def test_health(app):
    async with TestClient(TestServer(app)) as c:
        r = await c.get("/health")
        assert r.status == 200
        d = await r.json()
        assert d["status"] == "ok"


# ── Webhook ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_webhook_valid_order(app, db):
    payload = json.dumps(order_payload()).encode()
    sig = sign(payload)
    async with TestClient(TestServer(app)) as c:
        with patch("server.send_activation_email", new=AsyncMock()):
            r = await c.post("/webhook/lemonsqueezy", data=payload,
                             headers={"Content-Type": "application/json", "X-Signature": sig})
    assert r.status == 200
    row = db.execute("SELECT * FROM orders WHERE order_id='ORD-001'").fetchone()
    assert row["email"] == "cliente@test.it"
    assert row["tier"] == "pro"
    assert row["used"] == 0


@pytest.mark.asyncio
async def test_webhook_invalid_sig(app):
    payload = json.dumps(order_payload()).encode()
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/webhook/lemonsqueezy", data=payload,
                         headers={"Content-Type": "application/json", "X-Signature": "bad"})
    assert r.status == 401


@pytest.mark.asyncio
async def test_webhook_unknown_event_ignored(app, db):
    payload = json.dumps(order_payload(event="subscription_cancelled")).encode()
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/webhook/lemonsqueezy", data=payload,
                         headers={"Content-Type": "application/json", "X-Signature": sign(payload)})
    assert r.status == 200
    assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0


@pytest.mark.asyncio
async def test_webhook_duplicate_idempotent(app, db):
    payload = json.dumps(order_payload()).encode()
    sig = sign(payload)
    async with TestClient(TestServer(app)) as c:
        with patch("server.send_activation_email", new=AsyncMock()):
            await c.post("/webhook/lemonsqueezy", data=payload,
                         headers={"Content-Type": "application/json", "X-Signature": sig})
            r = await c.post("/webhook/lemonsqueezy", data=payload,
                             headers={"Content-Type": "application/json", "X-Signature": sig})
    assert r.status == 200
    assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("product,expected", [
    ("Fluxion Base", "base"),
    ("Fluxion Pro", "pro"),
    ("Fluxion Enterprise", "enterprise"),
    ("Unknown Product", "pro"),  # default
])
async def test_webhook_tier_mapping(app, db, product, expected):
    oid = f"ORD-{product[:4]}"
    payload = json.dumps(order_payload(order_id=oid, product_name=product)).encode()
    async with TestClient(TestServer(app)) as c:
        with patch("server.send_activation_email", new=AsyncMock()):
            await c.post("/webhook/lemonsqueezy", data=payload,
                         headers={"Content-Type": "application/json", "X-Signature": sign(payload)})
    row = db.execute("SELECT tier FROM orders WHERE order_id=?", (oid,)).fetchone()
    assert row["tier"] == expected


@pytest.mark.asyncio
async def test_webhook_missing_fields_400(app):
    payload = json.dumps({"meta": {"event_name": "order_created"}, "data": {"id": "", "attributes": {}}}).encode()
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/webhook/lemonsqueezy", data=payload,
                         headers={"Content-Type": "application/json", "X-Signature": sign(payload)})
    assert r.status == 400


@pytest.mark.asyncio
async def test_webhook_invalid_json_400(app):
    payload = b"not json"
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/webhook/lemonsqueezy", data=payload,
                         headers={"Content-Type": "application/json", "X-Signature": sign(payload)})
    assert r.status == 400


# ── Activate ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_activate_happy_path(app, db):
    seed(db)
    async with TestClient(TestServer(app)) as c:
        with patch("subprocess.run", return_value=KEYGEN_OK):
            r = await c.post("/api/activate",
                             json={"email": "user@test.it", "order_id": "ORD-001", "fingerprint": "FP1"})
        assert r.status == 200
        data = await r.json()
    assert "license" in data
    assert db.execute("SELECT used FROM orders WHERE order_id='ORD-001'").fetchone()["used"] == 1
    assert db.execute("SELECT COUNT(*) FROM activations WHERE order_id='ORD-001'").fetchone()[0] == 1


@pytest.mark.asyncio
async def test_activate_order_not_found_404(app):
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/api/activate",
                         json={"email": "x@y.it", "order_id": "MISSING", "fingerprint": "FP1"})
    assert r.status == 404


@pytest.mark.asyncio
async def test_activate_email_mismatch_403(app, db):
    seed(db, order_id="ORD-002", email="real@test.it")
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/api/activate",
                         json={"email": "wrong@test.it", "order_id": "ORD-002", "fingerprint": "FP1"})
    assert r.status == 403


@pytest.mark.asyncio
async def test_activate_already_used_409(app, db):
    seed(db, order_id="ORD-003", used=1)
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/api/activate",
                         json={"email": "user@test.it", "order_id": "ORD-003", "fingerprint": "FP1"})
    assert r.status == 409


@pytest.mark.asyncio
async def test_activate_too_many_attempts_429(app, db):
    seed(db, order_id="ORD-004", tries=server.MAX_ACTIVATE_TRIES)
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/api/activate",
                         json={"email": "user@test.it", "order_id": "ORD-004", "fingerprint": "FP1"})
    assert r.status == 429


@pytest.mark.asyncio
async def test_activate_missing_fields_400(app):
    async with TestClient(TestServer(app)) as c:
        r = await c.post("/api/activate", json={"email": "x@y.it"})
    assert r.status == 400


@pytest.mark.asyncio
async def test_activate_keygen_failure_500(app, db):
    seed(db, order_id="ORD-005")
    async with TestClient(TestServer(app)) as c:
        with patch("subprocess.run", return_value=KEYGEN_FAIL):
            r = await c.post("/api/activate",
                             json={"email": "user@test.it", "order_id": "ORD-005", "fingerprint": "FP1"})
    assert r.status == 500


@pytest.mark.asyncio
async def test_activate_keygen_timeout_500(app, db):
    import subprocess
    seed(db, order_id="ORD-006")
    async with TestClient(TestServer(app)) as c:
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="kg", timeout=15)):
            r = await c.post("/api/activate",
                             json={"email": "user@test.it", "order_id": "ORD-006", "fingerprint": "FP1"})
    assert r.status == 500


@pytest.mark.asyncio
async def test_activate_keygen_not_found_500(app, db):
    seed(db, order_id="ORD-007")
    async with TestClient(TestServer(app)) as c:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            r = await c.post("/api/activate",
                             json={"email": "user@test.it", "order_id": "ORD-007", "fingerprint": "FP1"})
    assert r.status == 500


@pytest.mark.asyncio
async def test_activate_tries_incremented_on_fail(app, db):
    seed(db, order_id="ORD-008", tries=0)
    async with TestClient(TestServer(app)) as c:
        with patch("subprocess.run", return_value=KEYGEN_FAIL):
            await c.post("/api/activate",
                         json={"email": "user@test.it", "order_id": "ORD-008", "fingerprint": "FP1"})
    row = db.execute("SELECT activate_tries FROM orders WHERE order_id='ORD-008'").fetchone()
    assert row["activate_tries"] == 1


@pytest.mark.asyncio
async def test_activate_email_case_insensitive(app, db):
    seed(db, order_id="ORD-009", email="user@test.it")
    async with TestClient(TestServer(app)) as c:
        with patch("subprocess.run", return_value=KEYGEN_OK):
            r = await c.post("/api/activate",
                             json={"email": "USER@TEST.IT", "order_id": "ORD-009", "fingerprint": "FP1"})
    assert r.status == 200


@pytest.mark.asyncio
async def test_cors_header(app, db):
    seed(db, order_id="ORD-010")
    async with TestClient(TestServer(app)) as c:
        with patch("subprocess.run", return_value=KEYGEN_OK):
            r = await c.post("/api/activate",
                             json={"email": "user@test.it", "order_id": "ORD-010", "fingerprint": "FP1"})
    assert r.headers.get("Access-Control-Allow-Origin") == "*"
