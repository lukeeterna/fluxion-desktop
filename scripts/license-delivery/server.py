#!/usr/bin/env python3
"""
FLUXION License Delivery Server
Porta 3010 — webhook LemonSqueezy + attivazione licenze

Requisiti: aiohttp aiosmtplib
Avvio: python3 server.py (richiede config.env)
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import sqlite3
import subprocess
import time
from pathlib import Path

import aiohttp
from aiohttp import web
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("fluxion-license-server")

# ── Config da env ──────────────────────────────────────────────────────────────
def _require_env(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        raise RuntimeError(f"Variabile d'ambiente mancante: {key}")
    return val

def load_config():
    """Carica .env se esiste, poi legge le variabili d'ambiente."""
    env_path = Path(__file__).parent / "config.env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

load_config()

LS_WEBHOOK_SECRET  = _require_env("LS_WEBHOOK_SECRET")
SMTP_HOST          = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT          = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER          = _require_env("SMTP_USER")
SMTP_PASS          = _require_env("SMTP_PASS")
SMTP_FROM_NAME     = os.environ.get("SMTP_FROM_NAME", "FLUXION")
KEYGEN_PATH        = _require_env("FLUXION_KEYGEN_PATH")
KEYPAIR_PATH       = _require_env("KEYPAIR_PATH")
DB_PATH            = os.environ.get("DB_PATH", str(Path(__file__).parent / "orders.db"))
PORT               = int(os.environ.get("PORT", "3010"))
ACTIVATE_URL_BASE  = os.environ.get("ACTIVATE_URL_BASE", "http://localhost:3010")
MAX_ACTIVATE_TRIES = int(os.environ.get("MAX_ACTIVATE_TRIES", "3"))

# Mappa product name LemonSqueezy → tier Fluxion
LS_PRODUCT_TIER_MAP = {
    "fluxion base":       "base",
    "fluxion pro":        "pro",
    "fluxion enterprise": "enterprise",
    "base":               "base",
    "pro":                "pro",
    "enterprise":         "enterprise",
}

# ── Database ────────────────────────────────────────────────────────────────────

def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id       TEXT PRIMARY KEY,
            email          TEXT NOT NULL,
            tier           TEXT NOT NULL,
            used           INTEGER NOT NULL DEFAULT 0,
            activate_tries INTEGER NOT NULL DEFAULT 0,
            created_at     REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            ip          TEXT,
            activated_at REAL NOT NULL
        )
    """)
    conn.commit()
    log.info("DB inizializzato: %s", DB_PATH)
    return conn

# ── HMAC validation ─────────────────────────────────────────────────────────────

def verify_ls_signature(payload: bytes, signature_header: str) -> bool:
    """Verifica la firma HMAC-SHA256 di LemonSqueezy."""
    if not signature_header:
        return False
    expected = hmac.new(
        LS_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header.strip())

# ── Email ────────────────────────────────────────────────────────────────────────

async def send_activation_email(email: str, order_id: str) -> None:
    """Invia email con link alla pagina di attivazione."""
    activate_url = f"{ACTIVATE_URL_BASE.rstrip('/')}/activate.html"

    subject = "Il tuo acquisto FLUXION — Attiva la licenza"
    html_body = f"""
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"></head>
<body style="font-family:sans-serif;background:#0f172a;color:#e2e8f0;padding:40px;">
  <div style="max-width:560px;margin:0 auto;">
    <img src="https://fluxion.app/assets/logo.png" alt="FLUXION" width="48" style="margin-bottom:24px;">
    <h1 style="color:#fff;font-size:24px;margin-bottom:8px;">Grazie per il tuo acquisto!</h1>
    <p style="color:#94a3b8;line-height:1.7;">
      Il tuo Order ID è: <strong style="color:#06b6d4;font-family:monospace;">{order_id}</strong>
    </p>
    <p style="color:#94a3b8;line-height:1.7;">
      Per attivare FLUXION sul tuo Mac:
    </p>
    <ol style="color:#94a3b8;line-height:2;">
      <li>Scarica e apri FLUXION</li>
      <li>Vai su Impostazioni → Licenza</li>
      <li>Copia il tuo <strong style="color:#e2e8f0;">Hardware Fingerprint</strong></li>
      <li>Vai alla pagina di attivazione e inserisci email, Order ID e Fingerprint</li>
    </ol>
    <a href="{activate_url}" style="display:inline-block;background:#06b6d4;color:#fff;font-weight:600;
       padding:14px 28px;border-radius:10px;text-decoration:none;margin-top:16px;">
      Attiva la tua licenza →
    </a>
    <p style="color:#475569;font-size:12px;margin-top:32px;">
      Problemi? Rispondi a questa email o scrivi a support@fluxion.app con il tuo Order ID.
    </p>
  </div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
    msg["To"] = email
    msg.attach(MIMEText(html_body, "html"))

    try:
        async with aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT) as smtp:
            await smtp.login(SMTP_USER, SMTP_PASS)
            await smtp.send_message(msg)
        log.info("Email inviata a %s (order %s)", email, order_id)
    except Exception as exc:
        log.error("Errore invio email a %s: %s", email, exc)

# ── Handlers ────────────────────────────────────────────────────────────────────

async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "fluxion-license-server"})


async def handle_webhook_ls(request: web.Request) -> web.Response:
    """Riceve webhook LemonSqueezy order_created."""
    payload = await request.read()
    signature = request.headers.get("X-Signature", "")

    if not verify_ls_signature(payload, signature):
        log.warning("Webhook: firma HMAC non valida da %s", request.remote)
        return web.json_response({"error": "invalid signature"}, status=401)

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return web.json_response({"error": "invalid json"}, status=400)

    event = data.get("meta", {}).get("event_name", "")
    if event not in ("order_created", "subscription_payment_success"):
        log.info("Webhook: evento ignorato '%s'", event)
        return web.json_response({"ok": True})

    order_attrs = data.get("data", {}).get("attributes", {})
    order_id    = str(data.get("data", {}).get("id", ""))
    email       = order_attrs.get("user_email", "").lower().strip()

    # Ricava il tier dal primo order item
    items = order_attrs.get("first_order_item", {})
    product_name = items.get("product_name", "").lower().strip()
    tier = LS_PRODUCT_TIER_MAP.get(product_name, "pro")  # default pro

    if not order_id or not email:
        log.warning("Webhook: dati mancanti — order_id=%s email=%s", order_id, email)
        return web.json_response({"error": "missing fields"}, status=400)

    db: sqlite3.Connection = request.app["db"]
    try:
        db.execute(
            "INSERT OR IGNORE INTO orders (order_id, email, tier, created_at) VALUES (?,?,?,?)",
            (order_id, email, tier, time.time()),
        )
        db.commit()
        log.info("Ordine salvato: %s email=%s tier=%s", order_id, email, tier)
    except Exception as exc:
        log.error("DB error: %s", exc)
        return web.json_response({"error": "db error"}, status=500)

    # Invia email in background (non blocca la risposta webhook)
    asyncio.create_task(send_activation_email(email, order_id))

    return web.json_response({"ok": True})


async def handle_activate(request: web.Request) -> web.Response:
    """Genera e restituisce la licenza JSON."""
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "JSON non valido"}, status=400)

    email       = str(body.get("email", "")).lower().strip()
    order_id    = str(body.get("order_id", "")).strip()
    fingerprint = str(body.get("fingerprint", "")).strip()

    if not email or not order_id or not fingerprint:
        return web.json_response({"error": "Campi obbligatori: email, order_id, fingerprint"}, status=400)

    db: sqlite3.Connection = request.app["db"]

    row = db.execute(
        "SELECT * FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()

    if row is None:
        log.warning("Activate: ordine non trovato %s da %s", order_id, request.remote)
        return web.json_response(
            {"error": "Order ID non trovato. Attendi qualche minuto dopo l'acquisto e riprova."},
            status=404,
        )

    if row["email"] != email:
        log.warning("Activate: email mismatch ordine %s (atteso %s, ricevuto %s)",
                    order_id, row["email"], email)
        return web.json_response(
            {"error": "Email non corrisponde all'ordine. Usa la stessa email con cui hai acquistato."},
            status=403,
        )

    if row["used"]:
        log.warning("Activate: ordine già usato %s da %s", order_id, request.remote)
        return web.json_response(
            {"error": "Licenza già generata per questo ordine. Controlla la tua cartella Download o scrivi a support@fluxion.app."},
            status=409,
        )

    if row["activate_tries"] >= MAX_ACTIVATE_TRIES:
        log.warning("Activate: troppi tentativi per ordine %s", order_id)
        return web.json_response(
            {"error": f"Troppi tentativi di attivazione ({MAX_ACTIVATE_TRIES} max). Scrivi a support@fluxion.app."},
            status=429,
        )

    # Incrementa tentativi
    db.execute(
        "UPDATE orders SET activate_tries = activate_tries + 1 WHERE order_id = ?",
        (order_id,),
    )
    db.commit()

    # Chiama fluxion-keygen
    try:
        result = subprocess.run(
            [
                KEYGEN_PATH, "generate",
                "--tier",        row["tier"],
                "--fingerprint", fingerprint,
                "--email",       email,
                "--keypair",     KEYPAIR_PATH,
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        log.error("Activate: fluxion-keygen timeout per ordine %s", order_id)
        return web.json_response({"error": "Timeout generazione licenza. Riprova."}, status=500)
    except FileNotFoundError:
        log.error("Activate: fluxion-keygen non trovato in %s", KEYGEN_PATH)
        return web.json_response({"error": "Errore interno del server."}, status=500)

    if result.returncode != 0:
        log.error("Activate: keygen error per ordine %s: %s", order_id, result.stderr)
        return web.json_response({"error": "Errore generazione licenza. Scrivi a support@fluxion.app."}, status=500)

    try:
        license_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        log.error("Activate: output keygen non è JSON valido: %s", result.stdout[:200])
        return web.json_response({"error": "Errore interno."}, status=500)

    # Marca come usato e salva activation log
    db.execute("UPDATE orders SET used = 1 WHERE order_id = ?", (order_id,))
    db.execute(
        "INSERT INTO activations (order_id, fingerprint, ip, activated_at) VALUES (?,?,?,?)",
        (order_id, fingerprint, request.remote, time.time()),
    )
    db.commit()

    log.info("Licenza generata con successo: ordine=%s tier=%s email=%s", order_id, row["tier"], email)
    return web.json_response({"license": license_data})


# ── CORS middleware ─────────────────────────────────────────────────────────────

@web.middleware
async def cors_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        return web.Response(
            headers={
                "Access-Control-Allow-Origin":  "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# ── App factory ─────────────────────────────────────────────────────────────────

def create_app() -> web.Application:
    app = web.Application(middlewares=[cors_middleware])
    app["db"] = init_db()

    app.router.add_get("/health", handle_health)
    app.router.add_post("/webhook/lemonsqueezy", handle_webhook_ls)
    app.router.add_post("/api/activate", handle_activate)

    # Serve landing pages (opzionale, per test locale)
    landing_dir = Path(__file__).parent.parent.parent / "landing"
    if landing_dir.exists():
        app.router.add_static("/", path=str(landing_dir), name="static")

    return app


# ── Main ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("FLUXION License Delivery Server avviato su porta %d", PORT)
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=PORT, access_log=log)
