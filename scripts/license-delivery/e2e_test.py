#!/usr/bin/env python3
"""
FLUXION F07 — End-to-End Integration Test
Testa il flusso completo: webhook → DB → email → attivazione licenza

Esegui sull'iMac (dove gira il server):
  cd '/Volumes/MacSSD - Dati/FLUXION/scripts/license-delivery'
  python3 e2e_test.py

Prerequisiti:
  - config.env compilato correttamente
  - server.py in ascolto su porta 3010
  - fluxion-keygen compilato su iMac
"""

import hashlib
import hmac
import json
import os
import sqlite3
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── Carica config.env ─────────────────────────────────────────────────────────
def load_env():
    env_path = Path(__file__).parent / "config.env"
    if not env_path.exists():
        print("❌ config.env non trovato")
        sys.exit(1)
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

load_env()

LS_WEBHOOK_SECRET = os.environ.get("LS_WEBHOOK_SECRET", "")
DB_PATH           = os.environ.get("DB_PATH", str(Path(__file__).parent / "orders.db"))
KEYGEN_PATH       = os.path.expanduser(os.environ.get("FLUXION_KEYGEN_PATH", "~/fluxion-keygen"))
KEYPAIR_PATH      = os.path.expanduser(os.environ.get("KEYPAIR_PATH", "~/fluxion-keypair.json"))
BASE_URL          = "http://localhost:3010"

PASS_COUNT = 0
FAIL_COUNT = 0

def ok(msg):
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"  ✅ {msg}")

def fail(msg):
    global FAIL_COUNT
    FAIL_COUNT += 1
    print(f"  ❌ {msg}")

def section(title):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")

# ── Helpers ──────────────────────────────────────────────────────────────────

def sign_payload(payload: bytes) -> str:
    return hmac.new(LS_WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()

def post_json(path: str, data: dict, headers: dict = None) -> tuple[int, dict]:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json", **(headers or {})}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def get_json(path: str) -> tuple[int, dict]:
    req = urllib.request.Request(f"{BASE_URL}{path}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def send_webhook(payload: dict, use_valid_sig: bool = True) -> tuple[int, dict]:
    raw = json.dumps(payload).encode()
    sig = sign_payload(raw) if use_valid_sig else "invalid-sig"
    req = urllib.request.Request(
        f"{BASE_URL}/webhook/lemonsqueezy",
        data=raw,
        method="POST",
        headers={"Content-Type": "application/json", "X-Signature": sig}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def db_get_order(order_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def db_cleanup(order_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
    conn.execute("DELETE FROM activations WHERE order_id = ?", (order_id,))
    conn.commit()
    conn.close()

# ── Test 1: Health ─────────────────────────────────────────────────────────

section("T1 — Health Check")
status, body = get_json("/health")
if status == 200 and body.get("status") == "ok":
    ok(f"Health OK: {body}")
else:
    fail(f"Health fallito: status={status} body={body}")

# ── Test 2: Webhook firma invalida ─────────────────────────────────────────

section("T2 — Webhook firma HMAC invalida → 401")
TEST_ORDER_ID = f"E2E-TEST-{int(time.time())}"
payload = {
    "meta": {"event_name": "order_created"},
    "data": {
        "id": TEST_ORDER_ID,
        "attributes": {
            "user_email": "test@fluxion-e2e.it",
            "first_order_item": {"product_name": "Fluxion Pro"},
        }
    }
}
status, body = send_webhook(payload, use_valid_sig=False)
if status == 401:
    ok("Firma invalida → 401 (firma HMAC verificata correttamente)")
else:
    fail(f"Atteso 401, ricevuto {status}: {body}")

# ── Test 3: order_created webhook ─────────────────────────────────────────

section("T3 — order_created webhook (tier Pro)")
TEST_EMAIL = "gianluca@fluxion-e2e-test.it"
db_cleanup(TEST_ORDER_ID)

status, body = send_webhook(payload)  # valido
if status == 200 and body.get("ok"):
    ok(f"Webhook accettato: {body}")
else:
    fail(f"Webhook fallito: status={status} body={body}")

# Attendi 1s per async DB write
time.sleep(1)

order = db_get_order(TEST_ORDER_ID)
if order:
    ok(f"Ordine salvato in DB: tier={order['tier']} email={order['email']}")
    if order["tier"] == "pro":
        ok("Tier correttamente risolto come 'pro'")
    else:
        fail(f"Tier errato: atteso 'pro', ottenuto '{order['tier']}'")
else:
    fail("Ordine NON trovato in DB dopo webhook")

# ── Test 4: order_created duplicato (idempotenza) ─────────────────────────

section("T4 — Webhook duplicato (idempotenza INSERT OR IGNORE)")
status, body = send_webhook(payload)
if status == 200:
    ok("Webhook duplicato accettato senza errore (200)")
    order_after = db_get_order(TEST_ORDER_ID)
    if order_after and order_after.get("activate_tries", 0) == 0:
        ok("DB non corrotto: ordine invariato")
    else:
        fail("DB potenzialmente corrotto dopo webhook duplicato")
else:
    fail(f"Webhook duplicato → {status}")

# ── Test 5: Risoluzione tier per varianti ─────────────────────────────────

section("T5 — Tier resolution (Base, Clinic, variant UUID)")
BASE_ORDER = f"E2E-BASE-{int(time.time())}"
db_cleanup(BASE_ORDER)
p_base = {
    "meta": {"event_name": "order_created"},
    "data": {
        "id": BASE_ORDER,
        "attributes": {
            "user_email": "base@test.it",
            "first_order_item": {
                "product_name": "Fluxion Base — Gestionale Desktop",
                "variant_id": ""
            },
        }
    }
}
send_webhook(p_base)
time.sleep(0.5)
o = db_get_order(BASE_ORDER)
if o and o["tier"] == "base":
    ok("Tier 'base' risolto correttamente (substring match)")
else:
    fail(f"Tier resolution Base fallita: {o}")

CLINIC_ORDER = f"E2E-CLINIC-{int(time.time())}"
db_cleanup(CLINIC_ORDER)
p_clinic = {
    "meta": {"event_name": "order_created"},
    "data": {
        "id": CLINIC_ORDER,
        "attributes": {
            "user_email": "clinic@test.it",
            "first_order_item": {
                "product_name": "Unknown Product",
                "variant_id": "e3864cc0-937b-486d-b412-a1bebcfe0023"  # UUID Clinic
            },
        }
    }
}
send_webhook(p_clinic)
time.sleep(0.5)
o = db_get_order(CLINIC_ORDER)
if o and o["tier"] == "clinic":
    ok("Tier 'clinic' risolto correttamente (UUID fallback)")
else:
    fail(f"Tier resolution Clinic UUID fallita: {o}")

db_cleanup(BASE_ORDER)
db_cleanup(CLINIC_ORDER)

# ── Test 6: order_refunded ─────────────────────────────────────────────────

section("T6 — order_refunded → blocca attivazione")
REFUND_ORDER = f"E2E-REFUND-{int(time.time())}"
db_cleanup(REFUND_ORDER)

# Crea ordine
p_created = {
    "meta": {"event_name": "order_created"},
    "data": {
        "id": REFUND_ORDER,
        "attributes": {
            "user_email": "refund@test.it",
            "first_order_item": {"product_name": "Fluxion Pro"},
        }
    }
}
send_webhook(p_created)
time.sleep(0.5)

# Rimborsa
p_refunded = {
    "meta": {"event_name": "order_refunded"},
    "data": {"id": REFUND_ORDER}
}
status, body = send_webhook(p_refunded)
if status == 200:
    ok(f"order_refunded accettato: {body}")
else:
    fail(f"order_refunded fallito: status={status}")

time.sleep(0.5)
o = db_get_order(REFUND_ORDER)
if o and o.get("refunded") == 1:
    ok("Ordine marcato come refunded=1 in DB")
else:
    fail(f"refunded flag non settato: {o}")

# Tenta attivazione → deve essere bloccata
status, body = post_json("/api/activate", {
    "email": "refund@test.it",
    "order_id": REFUND_ORDER,
    "fingerprint": "test-fp-refund"
})
if status == 402:
    ok(f"Attivazione bloccata su ordine rimborsato → 402 ✅")
else:
    fail(f"Atteso 402 (rimborsato), ottenuto {status}: {body}")

db_cleanup(REFUND_ORDER)

# ── Test 7: Attivazione licenza reale ──────────────────────────────────────

section("T7 — Attivazione licenza (fluxion-keygen reale)")

# Verifica che fluxion-keygen esista
if not Path(KEYGEN_PATH).exists():
    fail(f"fluxion-keygen non trovato: {KEYGEN_PATH}")
    print("    → Salta test attivazione")
elif not Path(KEYPAIR_PATH).exists():
    fail(f"keypair.json non trovato: {KEYPAIR_PATH}")
    print("    → Salta test attivazione")
else:
    ok(f"fluxion-keygen trovato: {KEYGEN_PATH}")
    ok(f"keypair.json trovato: {KEYPAIR_PATH}")

    ACTIVATE_ORDER = f"E2E-ACTIVATE-{int(time.time())}"
    db_cleanup(ACTIVATE_ORDER)
    TEST_FINGERPRINT = "e2e-test-fingerprint-macbook-2026"

    # Crea ordine
    p_activate = {
        "meta": {"event_name": "order_created"},
        "data": {
            "id": ACTIVATE_ORDER,
            "attributes": {
                "user_email": "activate@test.it",
                "first_order_item": {"product_name": "Fluxion Pro"},
            }
        }
    }
    send_webhook(p_activate)
    time.sleep(1)

    # Attivazione con email sbagliata → 403
    status, body = post_json("/api/activate", {
        "email": "wrong@test.it",
        "order_id": ACTIVATE_ORDER,
        "fingerprint": TEST_FINGERPRINT
    })
    if status == 403:
        ok("Email mismatch → 403 ✅")
    else:
        fail(f"Atteso 403, ottenuto {status}: {body}")

    # Attivazione corretta
    status, body = post_json("/api/activate", {
        "email": "activate@test.it",
        "order_id": ACTIVATE_ORDER,
        "fingerprint": TEST_FINGERPRINT
    })
    if status == 200 and "license" in body:
        lic = body["license"]
        ok(f"Licenza generata! tier={lic.get('tier')} fingerprint_match={lic.get('fingerprint', '')[:20]}...")
        # Verifica struttura licenza
        required_fields = ["tier", "fingerprint", "signature"]
        for f in required_fields:
            if f in lic:
                ok(f"  Campo licenza '{f}' presente")
            else:
                fail(f"  Campo licenza '{f}' MANCANTE")
    else:
        fail(f"Attivazione fallita: status={status} body={body}")

    # Attivazione duplicata → 409
    status, body = post_json("/api/activate", {
        "email": "activate@test.it",
        "order_id": ACTIVATE_ORDER,
        "fingerprint": TEST_FINGERPRINT
    })
    if status == 409:
        ok("Attivazione duplicata → 409 ✅")
    else:
        fail(f"Atteso 409 (already used), ottenuto {status}: {body}")

    db_cleanup(ACTIVATE_ORDER)

# ── Test 8: Attivazione ordine inesistente ─────────────────────────────────

section("T8 — Attivazione ordine inesistente → 404")
status, body = post_json("/api/activate", {
    "email": "nobody@test.it",
    "order_id": "ORDINE-INESISTENTE-XYZ",
    "fingerprint": "fp-test"
})
if status == 404:
    ok(f"Ordine inesistente → 404 ✅")
else:
    fail(f"Atteso 404, ottenuto {status}: {body}")

# ── Test 9: Attivazione campi mancanti → 400 ──────────────────────────────

section("T9 — Attivazione campi mancanti → 400")
status, body = post_json("/api/activate", {"email": "x@test.it"})
if status == 400:
    ok(f"Campi mancanti → 400 ✅")
else:
    fail(f"Atteso 400, ottenuto {status}: {body}")

# ── Cleanup ordine principale ─────────────────────────────────────────────

db_cleanup(TEST_ORDER_ID)

# ── Riepilogo ─────────────────────────────────────────────────────────────

print(f"\n{'═'*55}")
print(f"  RISULTATO F07 E2E: {PASS_COUNT} PASS / {FAIL_COUNT} FAIL")
print(f"{'═'*55}\n")

sys.exit(0 if FAIL_COUNT == 0 else 1)
