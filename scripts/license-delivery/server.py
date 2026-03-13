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
import tempfile
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
# Usa substring match (startswith) — robusto anche se il nome prodotto ha suffissi
LS_PRODUCT_TIER_MAP = {
    "fluxion base":   "base",
    "fluxion pro":    "pro",
    "fluxion clinic": "clinic",
    "base":           "base",
    "pro":            "pro",
    "clinic":         "clinic",
}

# Checkout variant IDs (UUID nel link /checkout/buy/UUID)
# Store: https://fluxion.lemonsqueezy.com
LS_VARIANT_TIER_MAP = {
    "c73ec6bb-24c2-4214-a456-320c67056bd3": "base",    # €497
    "14806a0d-ac44-44af-a051-8fe8c559d702": "pro",     # €897
    "e3864cc0-937b-486d-b412-a1bebcfe0023": "clinic",  # €1.497
}


def _resolve_tier(product_name: str, variant_id: str = "") -> str:
    """
    Ricava il tier da product_name (substring match) o variant_id.
    Fallback: "pro".
    """
    pn = product_name.lower().strip()
    # 1. Exact match
    if pn in LS_PRODUCT_TIER_MAP:
        return LS_PRODUCT_TIER_MAP[pn]
    # 2. Substring match (gestisce nomi con suffissi tipo "— Gestionale Desktop...")
    for key, tier in LS_PRODUCT_TIER_MAP.items():
        if pn.startswith(key):
            return tier
    # 3. Variant UUID fallback
    if variant_id and variant_id in LS_VARIANT_TIER_MAP:
        return LS_VARIANT_TIER_MAP[variant_id]
    return "pro"  # default sicuro

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
    # Migration: aggiunge colonna refunded se non esiste (idempotente)
    try:
        conn.execute("ALTER TABLE orders ADD COLUMN refunded INTEGER NOT NULL DEFAULT 0")
        conn.commit()
        log.info("DB: migrazione 'refunded' colonna aggiunta")
    except Exception:
        pass  # colonna già esiste
    # Migration: aggiunge colonna email_sent (0=pending, 1=sent, -1=failed) (idempotente)
    try:
        conn.execute("ALTER TABLE orders ADD COLUMN email_sent INTEGER DEFAULT 0")
        conn.commit()
        log.info("DB: migrazione 'email_sent' colonna aggiunta")
    except Exception:
        pass  # colonna già esiste
    # Migration: aggiunge colonna email_retry_count per tracciare tentativi (idempotente)
    try:
        conn.execute("ALTER TABLE orders ADD COLUMN email_retry_count INTEGER DEFAULT 0")
        conn.commit()
        log.info("DB: migrazione 'email_retry_count' colonna aggiunta")
    except Exception:
        pass  # colonna già esiste
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

async def send_activation_email(email: str, order_id: str) -> bool:
    """Invia email con link alla pagina di attivazione. Restituisce True se successo."""
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
        return True
    except Exception as exc:
        log.error("Errore invio email a %s: %s", email, exc)
        return False

# ── Handlers ────────────────────────────────────────────────────────────────────

async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "fluxion-license-server"})


async def handle_webhook_ls(request: web.Request) -> web.Response:
    """Riceve webhook LemonSqueezy (order_created / order_refunded)."""
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

    # ── Rimborso: blocca attivazioni future per questo ordine ─────────────────
    if event == "order_refunded":
        order_id = str(data.get("data", {}).get("id", ""))
        if order_id:
            db: sqlite3.Connection = request.app["db"]
            db.execute(
                "UPDATE orders SET refunded = 1 WHERE order_id = ?",
                (order_id,),
            )
            db.commit()
            log.info("Rimborso: ordine %s marcato come refunded", order_id)
        return web.json_response({"ok": True})

    if event not in ("order_created", "subscription_payment_success"):
        log.info("Webhook: evento ignorato '%s'", event)
        return web.json_response({"ok": True})

    order_attrs = data.get("data", {}).get("attributes", {})
    order_id    = str(data.get("data", {}).get("id", ""))
    email       = order_attrs.get("user_email", "").lower().strip()

    # Ricava il tier dal primo order item (product_name + variant_id come fallback)
    items = order_attrs.get("first_order_item", {})
    product_name = items.get("product_name", "")
    variant_id   = str(items.get("variant_id", ""))
    tier = _resolve_tier(product_name, variant_id)

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
    # Se successo → email_sent=1; se fallisce → rimane 0 per il retry scheduler
    async def _send_and_mark(app_db: sqlite3.Connection, _email: str, _order_id: str) -> None:
        success = await send_activation_email(_email, _order_id)
        if success:
            app_db.execute("UPDATE orders SET email_sent=1 WHERE order_id=?", (_order_id,))
            app_db.commit()

    asyncio.create_task(_send_and_mark(db, email, order_id))

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

    if row["refunded"]:
        log.warning("Activate: ordine rimborsato %s da %s", order_id, request.remote)
        return web.json_response(
            {"error": "Questo ordine risulta rimborsato e non può essere attivato. Per assistenza scrivi a support@fluxion.app."},
            status=402,
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

    # Chiama fluxion-keygen — scrive su file temporaneo per evitare conflitti
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                KEYGEN_PATH, "generate",
                "--tier",        row["tier"],
                "--fingerprint", fingerprint,
                "--email",       email,
                "--keypair",     KEYPAIR_PATH,
                "--output",      tmp_path,
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        Path(tmp_path).unlink(missing_ok=True)
        log.error("Activate: fluxion-keygen timeout per ordine %s", order_id)
        return web.json_response({"error": "Timeout generazione licenza. Riprova."}, status=500)
    except FileNotFoundError:
        Path(tmp_path).unlink(missing_ok=True)
        log.error("Activate: fluxion-keygen non trovato in %s", KEYGEN_PATH)
        return web.json_response({"error": "Errore interno del server."}, status=500)

    if result.returncode != 0:
        Path(tmp_path).unlink(missing_ok=True)
        log.error("Activate: keygen error per ordine %s: %s", order_id, result.stderr)
        return web.json_response({"error": "Errore generazione licenza. Scrivi a support@fluxion.app."}, status=500)

    try:
        license_data = json.loads(Path(tmp_path).read_text())
    except (json.JSONDecodeError, OSError) as exc:
        log.error("Activate: lettura licenza JSON fallita per ordine %s: %s", order_id, exc)
        return web.json_response({"error": "Errore interno."}, status=500)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # Marca come usato e salva activation log
    db.execute("UPDATE orders SET used = 1 WHERE order_id = ?", (order_id,))
    db.execute(
        "INSERT INTO activations (order_id, fingerprint, ip, activated_at) VALUES (?,?,?,?)",
        (order_id, fingerprint, request.remote, time.time()),
    )
    db.commit()

    log.info("Licenza generata con successo: ordine=%s tier=%s email=%s", order_id, row["tier"], email)
    return web.json_response({"license": license_data})


# ── Email Retry Scheduler ───────────────────────────────────────────────────────

MAX_EMAIL_RETRIES = 3
EMAIL_RETRY_INTERVAL = 300  # 5 minuti in secondi

async def _retry_pending_emails(db: sqlite3.Connection) -> None:
    """Ritenta invio email per ordini con email_sent=0 creati nelle ultime 24h."""
    cutoff = time.time() - 86400  # ultime 24 ore
    try:
        rows = db.execute(
            """SELECT order_id, email, tier FROM orders
               WHERE email_sent = 0
                 AND refunded = 0
                 AND email_retry_count < ?
                 AND created_at > ?""",
            (MAX_EMAIL_RETRIES, cutoff),
        ).fetchall()
    except Exception as exc:
        log.error("Email retry: errore lettura DB: %s", exc)
        return

    if not rows:
        return

    log.info("Email retry: trovati %d ordini con email non consegnata", len(rows))

    for row in rows:
        order_id = row["order_id"]
        email    = row["email"]

        # Incrementa retry count prima del tentativo
        try:
            db.execute(
                "UPDATE orders SET email_retry_count = email_retry_count + 1 WHERE order_id = ?",
                (order_id,),
            )
            db.commit()
        except Exception as exc:
            log.error("Email retry: errore aggiornamento retry count per %s: %s", order_id, exc)
            continue

        # Verifica se siamo al limite
        try:
            updated_row = db.execute(
                "SELECT email_retry_count FROM orders WHERE order_id = ?", (order_id,)
            ).fetchone()
            retry_count = updated_row["email_retry_count"] if updated_row else MAX_EMAIL_RETRIES
        except Exception:
            retry_count = MAX_EMAIL_RETRIES

        if retry_count > MAX_EMAIL_RETRIES:
            # Marca come fallito definitivamente
            try:
                db.execute("UPDATE orders SET email_sent = -1 WHERE order_id = ?", (order_id,))
                db.commit()
            except Exception:
                pass
            log.error("Email retry: fallimento definitivo per ordine %s (>%d tentativi)", order_id, MAX_EMAIL_RETRIES)
            continue

        success = await send_activation_email(email, order_id)
        if success:
            try:
                db.execute("UPDATE orders SET email_sent = 1 WHERE order_id = ?", (order_id,))
                db.commit()
                log.info("Email retry: successo per ordine %s (tentativo %d)", order_id, retry_count)
            except Exception as exc:
                log.error("Email retry: errore aggiornamento email_sent per %s: %s", order_id, exc)
        else:
            if retry_count >= MAX_EMAIL_RETRIES:
                try:
                    db.execute("UPDATE orders SET email_sent = -1 WHERE order_id = ?", (order_id,))
                    db.commit()
                except Exception:
                    pass
                log.error("Email retry: fallimento definitivo per ordine %s dopo %d tentativi", order_id, retry_count)
            else:
                log.warning("Email retry: tentativo %d/%d fallito per ordine %s — riprovare al prossimo ciclo", retry_count, MAX_EMAIL_RETRIES, order_id)


async def _email_retry_loop(app: web.Application) -> None:
    """Background loop: ritenta email non consegnate ogni EMAIL_RETRY_INTERVAL secondi."""
    # Attendi 60s prima del primo ciclo (server warmup)
    await asyncio.sleep(60)
    while True:
        try:
            await _retry_pending_emails(app["db"])
        except Exception as exc:
            log.error("Email retry loop: errore inatteso: %s", exc)
        await asyncio.sleep(EMAIL_RETRY_INTERVAL)


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

async def _start_background_tasks(app: web.Application) -> None:
    """Avvia i task asyncio in background all'avvio dell'app."""
    app["email_retry_task"] = asyncio.create_task(_email_retry_loop(app))


async def _stop_background_tasks(app: web.Application) -> None:
    """Cancella i task in background allo shutdown."""
    task = app.get("email_retry_task")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def create_app() -> web.Application:
    app = web.Application(middlewares=[cors_middleware])
    app["db"] = init_db()

    app.on_startup.append(_start_background_tasks)
    app.on_cleanup.append(_stop_background_tasks)

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
