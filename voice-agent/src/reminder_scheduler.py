"""
FLUXION Reminder Scheduler — Automated -24h/-1h appointment reminders via WhatsApp

World-class: no PMI competitor sends automated pre-appointment reminders locally.
Gap #2 from CoVe 2026 deep research: 30% no-show rate → -40% with reminders.
Revenue impact: -40% no-show = +25% slot fill = Pro tier killer feature.

Architecture:
- APScheduler AsyncIOScheduler (runs in same event loop as voice pipeline)
- Polls SQLite every 15 min for upcoming appointments in reminder windows
- Idempotent: JSON file tracks sent reminders to prevent double-send
- Windows: T-24h ±15min and T-1h ±15min
- Graceful: WA unavailable → logs warning, does not crash pipeline
"""

import json
import logging
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# DB PATH (same resolution as _load_business_name_from_sqlite)
# ═══════════════════════════════════════════════════════════════════

def _get_db_path() -> Optional[Path]:
    """Resolve Fluxion SQLite DB path (same logic as main.py)."""
    home = Path.home()
    db_env = os.environ.get("FLUXION_DB_PATH")
    if db_env:
        p = Path(db_env)
        if p.exists():
            return p

    if sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        candidates = [
            appdata / "com.fluxion.desktop" / "fluxion.db",
            appdata / "fluxion" / "fluxion.db",
        ]
    else:
        candidates = [
            home / "Library" / "Application Support" / "com.fluxion.desktop" / "fluxion.db",
            home / "Library" / "Application Support" / "fluxion" / "fluxion.db",
        ]

    for p in candidates:
        if p.exists():
            return p
    return None


# ═══════════════════════════════════════════════════════════════════
# SENT REMINDERS TRACKING (idempotent — no double-send)
# ═══════════════════════════════════════════════════════════════════

from resource_path import get_writable_root
_SENT_LOG_PATH = get_writable_root() / ".whatsapp-session" / "reminders_sent.json"


def _load_sent_log() -> Dict[str, List[str]]:
    """Load dict of {appointment_id: [reminder_type, ...]} from disk."""
    _SENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _SENT_LOG_PATH.exists():
        return {}
    try:
        with open(_SENT_LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _mark_sent(appointment_id: str, reminder_type: str) -> None:
    """Persist that reminder_type was sent for appointment_id."""
    log = _load_sent_log()
    if appointment_id not in log:
        log[appointment_id] = []
    if reminder_type not in log[appointment_id]:
        log[appointment_id].append(reminder_type)
    try:
        with open(_SENT_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.warning("[Reminder] Cannot write sent log: %s", e)


def _already_sent(appointment_id: str, reminder_type: str) -> bool:
    """Return True if this reminder was already sent."""
    log = _load_sent_log()
    return reminder_type in log.get(appointment_id, [])


# ═══════════════════════════════════════════════════════════════════
# DB QUERIES
# ═══════════════════════════════════════════════════════════════════

def _get_appointments_in_window(
    from_dt: datetime, to_dt: datetime
) -> List[Dict[str, Any]]:
    """
    Return confirmed appointments with data_ora_inizio in [from_dt, to_dt].
    Includes client phone (required for WA reminder).
    """
    db_path = _get_db_path()
    if db_path is None:
        logger.warning("[Reminder] DB not found — skipping reminder check")
        return []

    try:
        with sqlite3.connect(str(db_path), timeout=3) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT
                    a.id          AS appointment_id,
                    a.data_ora_inizio,
                    c.nome        AS cliente_nome,
                    c.telefono    AS cliente_telefono,
                    s.nome        AS servizio_nome
                FROM appuntamenti a
                JOIN clienti c ON a.cliente_id = c.id
                JOIN servizi s ON a.servizio_id = s.id
                WHERE a.stato IN ('Confermato', 'ConfermatoConOverride')
                  AND (a.deleted_at IS NULL OR a.deleted_at = '')
                  AND a.data_ora_inizio BETWEEN ? AND ?
                """,
                (from_dt.strftime("%Y-%m-%dT%H:%M:%S"), to_dt.strftime("%Y-%m-%dT%H:%M:%S")),
            ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        logger.error("[Reminder] DB query error: %s", e)
        return []


# ═══════════════════════════════════════════════════════════════════
# CORE SCHEDULER JOB
# ═══════════════════════════════════════════════════════════════════

async def check_and_send_reminders(wa_client: Any, callback_handler: Any = None) -> None:
    """
    Main scheduler job. Runs every 15 min.
    Checks -24h and -1h windows and sends WA reminders if not already sent.

    Gap #4 CoVe 2026: after sending, register appointment in callback_handler so
    client replies (CONFERMO/CANCELLO/SPOSTO) are correctly attributed.

    World-class: idempotent (JSON log), graceful WA failure, full audit logging.
    """
    now = datetime.now()
    window = timedelta(minutes=15)

    # -24h window: [T-24h-15min, T-24h+15min]
    t24 = now + timedelta(hours=24)
    appointments_24h = _get_appointments_in_window(t24 - window, t24 + window)

    # -1h window: [T-1h-15min, T-1h+15min]
    t1h = now + timedelta(hours=1)
    appointments_1h = _get_appointments_in_window(t1h - window, t1h + window)

    total_sent = 0

    for appt in appointments_24h:
        apt_id = appt["appointment_id"]
        if _already_sent(apt_id, "reminder_24h"):
            continue
        sent = await _send_reminder(wa_client, appt, "reminder_24h", callback_handler)
        if sent:
            _mark_sent(apt_id, "reminder_24h")
            total_sent += 1

    for appt in appointments_1h:
        apt_id = appt["appointment_id"]
        if _already_sent(apt_id, "reminder_1h"):
            continue
        sent = await _send_reminder(wa_client, appt, "reminder_1h", callback_handler)
        if sent:
            _mark_sent(apt_id, "reminder_1h")
            total_sent += 1

    if total_sent:
        logger.info("[Reminder] Sent %d reminders (run at %s)", total_sent, now.strftime("%H:%M"))
    else:
        logger.debug("[Reminder] No reminders due at %s", now.strftime("%H:%M"))


async def _send_reminder(
    wa_client: Any, appt: Dict[str, Any], reminder_type: str, callback_handler: Any = None
) -> bool:
    """
    Send a single WA reminder. Returns True on success.

    Gap #4: after successful send, register appointment in callback_handler so
    client replies (CONFERMO/CANCELLO/SPOSTO) are attributed to this appointment.
    """
    phone = appt.get("cliente_telefono", "")
    nome = appt.get("cliente_nome", "Cliente")
    servizio = appt.get("servizio_nome", "")
    data_ora = appt.get("data_ora_inizio", "")
    apt_id = str(appt.get("appointment_id", ""))

    if not phone:
        logger.warning("[Reminder] No phone for appointment %s — skip", apt_id)
        return False

    # Parse data_ora_inizio (ISO 8601: YYYY-MM-DDTHH:MM:SS)
    try:
        dt = datetime.fromisoformat(data_ora)
        data_str = dt.strftime("%d/%m/%Y")
        ora_str = dt.strftime("%H:%M")
    except ValueError:
        data_str = data_ora[:10]
        ora_str = data_ora[11:16]

    try:
        if wa_client is None or not wa_client.is_connected():
            logger.warning(
                "[Reminder] WA not connected — skipping %s for %s", reminder_type, nome
            )
            return False

        hours_before = 24 if reminder_type == "reminder_24h" else 1
        result = wa_client.send_template(
            phone,
            "reminder_24h" if hours_before >= 24 else "reminder_2h",
            nome=nome,
            servizio=servizio,
            data=data_str,
            ora=ora_str,
        )
        success = result.get("success", False)
        if success:
            logger.info(
                "[Reminder] ✅ %s → %s (%s %s %s)",
                reminder_type, nome, servizio, data_str, ora_str,
            )
            # Gap #4: register pending so client reply is correctly attributed
            if callback_handler is not None and apt_id:
                try:
                    callback_handler.register_pending_appointment(phone, apt_id, nome)
                except Exception as reg_err:
                    logger.warning(
                        "[Reminder] Could not register pending appointment %s: %s", apt_id, reg_err
                    )
        else:
            logger.warning("[Reminder] ❌ %s failed for %s: %s", reminder_type, nome, result)
        return success
    except Exception as e:
        logger.error("[Reminder] Exception sending %s to %s: %s", reminder_type, nome, e)
        return False


# ═══════════════════════════════════════════════════════════════════
# GAP #3 — WAITLIST NOTIFY: check every 5min for freed slots
# ═══════════════════════════════════════════════════════════════════

def _get_waitlist_pending() -> List[Dict[str, Any]]:
    """
    Return active waitlist entries (stato='attivo', not yet notified) with client phone.
    Real schema: servizio TEXT (direct name, not FK), data_preferita, ora_preferita.
    LEFT JOIN servizi by name to resolve servizio_id (may be '' if not matched).
    """
    db_path = _get_db_path()
    if db_path is None:
        return []
    try:
        with sqlite3.connect(str(db_path), timeout=3) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT
                    w.id              AS waitlist_id,
                    w.servizio        AS servizio_nome,
                    COALESCE(s.id, '') AS servizio_id,
                    w.data_preferita  AS data_richiesta,
                    w.ora_preferita   AS ora_richiesta,
                    w.priorita,
                    c.nome            AS cliente_nome,
                    c.telefono        AS cliente_telefono
                FROM waitlist w
                JOIN clienti c ON w.cliente_id = c.id
                LEFT JOIN servizi s ON LOWER(s.nome) = LOWER(w.servizio)
                WHERE w.stato = 'attivo'
                  AND w.notificato_il IS NULL
                  AND (w.data_preferita IS NULL OR w.data_preferita >= date('now'))
                ORDER BY w.priorita DESC, w.creato_il ASC
                """
            ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        logger.error("[Waitlist] DB query error: %s", e)
        return []


def _is_slot_free(servizio_id: str, data_richiesta: str, ora_richiesta: str) -> bool:
    """
    Check if the requested slot is free (no confirmed appointment at that date/time
    for the same service).
    """
    if not servizio_id:
        return False  # Can't check slot without service ID — skip notification
    db_path = _get_db_path()
    if db_path is None:
        return False
    if not data_richiesta or not ora_richiesta:
        return False  # No specific slot — skip
    try:
        dt_str = f"{data_richiesta}T{ora_richiesta}:00"
        with sqlite3.connect(str(db_path), timeout=3) as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) FROM appuntamenti
                WHERE servizio_id = ?
                  AND data_ora_inizio = ?
                  AND stato IN ('Confermato', 'ConfermatoConOverride')
                  AND (deleted_at IS NULL OR deleted_at = '')
                """,
                (servizio_id, dt_str),
            ).fetchone()
        return row[0] == 0
    except sqlite3.Error as e:
        logger.error("[Waitlist] Slot-free check error: %s", e)
        return False


def _mark_waitlist_notified(waitlist_id: str) -> None:
    """Set notificato_il timestamp so we don't re-notify this entry."""
    db_path = _get_db_path()
    if db_path is None:
        return
    try:
        with sqlite3.connect(str(db_path), timeout=3) as conn:
            conn.execute(
                "UPDATE waitlist SET notificato_il = datetime('now'), "
                "scadenza_risposta = datetime('now', '+2 hours') WHERE id = ?",
                (waitlist_id,),
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.error("[Waitlist] Mark-notified error: %s", e)


async def check_and_notify_waitlist(wa_client: Any) -> None:
    """
    Gap #3 periodic job (every 5min).
    Finds waitlist entries where the requested slot is now free,
    sends WA notification, marks entry as 'contattato'.

    World-class: reactive + periodic — catches UI-initiated cancellations
    that the voice-agent reactive trigger (booking_manager) cannot see.
    Revenue: +15-20% conversion on freed slots.
    """
    pending = _get_waitlist_pending()
    if not pending:
        logger.debug("[Waitlist] No pending entries")
        return

    notified = 0
    for entry in pending:
        servizio = entry.get("servizio_nome", "")
        servizio_id = entry.get("servizio_id", "")
        data_pref = entry.get("data_richiesta", "")
        ora_pref = entry.get("ora_richiesta", "")

        # Only notify if a specific slot was requested and it's now free
        if not data_pref or not ora_pref:
            continue

        if not _is_slot_free(servizio_id, data_pref, ora_pref):
            continue

        phone = entry.get("cliente_telefono", "")
        nome = entry.get("cliente_nome", "Cliente")

        if not phone:
            continue

        try:
            if wa_client is None or not wa_client.is_connected():
                logger.warning("[Waitlist] WA not connected — skipping notify for %s", nome)
                continue

            try:
                data_obj = datetime.strptime(data_pref, "%Y-%m-%d")
                data_str = data_obj.strftime("%d/%m/%Y")
            except ValueError:
                data_str = data_pref

            scadenza = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
            message = (
                f"🎉 Buone notizie {nome}!\n\n"
                f"Si è liberato uno slot per *{servizio}*:\n"
                f"📅 {data_str}\n"
                f"🕐 {ora_pref}\n\n"
                f"Rispondi *SI* per confermare entro 2 ore, "
                f"oppure *NO* se non ti serve più.\n\n"
                f"_Questo messaggio scade alle {scadenza}_"
            )
            result = wa_client.send_message(phone, message)
            if result.get("success", False):
                _mark_waitlist_notified(entry["waitlist_id"])
                notified += 1
                logger.info(
                    "[Waitlist] ✅ Notified %s → slot %s %s %s",
                    nome, servizio, data_str, ora_pref,
                )
            else:
                logger.warning("[Waitlist] ❌ WA send failed for %s: %s", nome, result)

        except Exception as e:
            logger.error("[Waitlist] Exception notifying %s: %s", nome, e)

    if notified:
        logger.info("[Waitlist] Sent %d slot-free notifications", notified)


# ═══════════════════════════════════════════════════════════════════
# GAP #6 — BIRTHDAY WA: daily 9:00am greetings for clienti with compleanno oggi
# Revenue: +8% return rate — clienti si sentono ricordati, tornano.
# World-class: Fresha, Mindbody fanno questo. Noi lo facciamo locale, GDPR-safe.
# ═══════════════════════════════════════════════════════════════════

_BIRTHDAY_LOG_PATH = get_writable_root() / ".whatsapp-session" / "birthday_sent.json"


def _load_birthday_log() -> Dict[str, str]:
    """Load dict of {cliente_id: 'YYYY'} — year last birthday WA was sent (idempotent)."""
    _BIRTHDAY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _BIRTHDAY_LOG_PATH.exists():
        return {}
    try:
        with open(_BIRTHDAY_LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _mark_birthday_sent(cliente_id: str, year: str) -> None:
    """Persist that birthday WA was sent for this year."""
    log = _load_birthday_log()
    log[cliente_id] = year
    try:
        with open(_BIRTHDAY_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.warning("[Birthday] Cannot write birthday log: %s", e)


def _already_sent_birthday(cliente_id: str, year: str) -> bool:
    """Return True if birthday WA was already sent this year."""
    return _load_birthday_log().get(cliente_id) == year


def _get_clienti_compleanno_oggi() -> List[Dict[str, Any]]:
    """
    Return clienti whose birthday is today, with WhatsApp consent.
    Query: strftime('%m-%d', data_nascita) = today's MM-DD.
    """
    db_path = _get_db_path()
    if db_path is None:
        return []
    try:
        with sqlite3.connect(str(db_path), timeout=3) as conn:
            conn.row_factory = sqlite3.Row
            today_mmdd = datetime.now().strftime("%m-%d")
            rows = conn.execute(
                """
                SELECT id, nome, telefono
                FROM clienti
                WHERE deleted_at IS NULL
                  AND data_nascita IS NOT NULL
                  AND strftime('%m-%d', data_nascita) = ?
                  AND telefono IS NOT NULL AND telefono != ''
                  AND consenso_whatsapp = 1
                ORDER BY cognome, nome
                """,
                (today_mmdd,)
            ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        logger.warning("[Birthday] DB query error: %s", e)
        return []


async def check_and_send_birthdays(wa_client: Any) -> None:
    """
    Daily job (9:00am). Sends birthday WA to all clienti with compleanno oggi.

    Gap #6 CoVe 2026: +8% return rate. Idempotent (JSON log by year).
    """
    if wa_client is None or not wa_client.is_connected():
        logger.debug("[Birthday] WA not connected — skip birthday check")
        return

    today_year = datetime.now().strftime("%Y")
    clienti = _get_clienti_compleanno_oggi()

    sent = 0
    for cliente in clienti:
        cid = cliente["id"]
        nome = cliente.get("nome", "Cliente")
        phone = cliente.get("telefono", "")

        if _already_sent_birthday(cid, today_year):
            logger.debug("[Birthday] Already sent to %s (%s) this year", nome, cid)
            continue

        try:
            result = wa_client.send_template(phone, "compleanno", nome=nome)
            if result.get("success", False):
                _mark_birthday_sent(cid, today_year)
                sent += 1
                logger.info("[Birthday] 🎂 Sent birthday WA to %s (%s)", nome, phone)
            else:
                logger.warning("[Birthday] ❌ Failed to send to %s: %s", nome, result)
        except Exception as e:
            logger.error("[Birthday] Exception sending to %s: %s", nome, e)

    if sent:
        logger.info("[Birthday] Sent %d birthday messages today", sent)
    else:
        logger.debug("[Birthday] No birthdays today (or all already sent)")


# ═══════════════════════════════════════════════════════════════════
# G2 — DORMANT CLIENT RECALL: daily 10:00am, >60 days without booking
# Revenue: +15% recovery. Clienti dormienti tornano se contattati.
# World-class: Fresha/Mindbody inviano recall automatici.
# ═══════════════════════════════════════════════════════════════════

DORMANT_DAYS_THRESHOLD = 60  # configurable: days without booking to trigger recall
DORMANT_MAX_PER_DAY = 10     # max recall messages per day (avoid WA spam)

_RECALL_LOG_PATH = get_writable_root() / ".whatsapp-session" / "recall_sent.json"


def _load_recall_log() -> Dict[str, str]:
    """Load dict of {cliente_id: 'YYYY-MM-DD'} — last recall date (idempotent, max 1/month)."""
    _RECALL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _RECALL_LOG_PATH.exists():
        return {}
    try:
        with open(_RECALL_LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _mark_recall_sent(cliente_id: str) -> None:
    """Persist that recall was sent today for this client."""
    log = _load_recall_log()
    log[str(cliente_id)] = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(_RECALL_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.warning("[Recall] Cannot write recall log: %s", e)


def _recall_recently_sent(cliente_id: str, min_days: int = 30) -> bool:
    """Return True if recall was sent within min_days (default 30 = max 1/month)."""
    log = _load_recall_log()
    last_sent = log.get(str(cliente_id))
    if not last_sent:
        return False
    try:
        last_dt = datetime.strptime(last_sent, "%Y-%m-%d")
        return (datetime.now() - last_dt).days < min_days
    except ValueError:
        return False


def _get_dormant_clients(days_threshold: int = DORMANT_DAYS_THRESHOLD) -> List[Dict[str, Any]]:
    """
    Return clients who haven't had a confirmed appointment in >days_threshold days,
    have WA consent, and have a phone number.

    Query: last confirmed appointment date per client, filter those >threshold days ago.
    Excludes clients with future appointments (they're already booked).
    """
    db_path = _get_db_path()
    if db_path is None:
        return []
    try:
        with sqlite3.connect(str(db_path), timeout=3) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT
                    c.id,
                    c.nome,
                    c.telefono,
                    MAX(a.data_ora_inizio) AS ultimo_appuntamento,
                    julianday('now') - julianday(MAX(a.data_ora_inizio)) AS giorni_assente
                FROM clienti c
                JOIN appuntamenti a ON a.cliente_id = c.id
                WHERE c.deleted_at IS NULL
                  AND c.telefono IS NOT NULL AND c.telefono != ''
                  AND c.consenso_whatsapp = 1
                  AND a.stato IN ('Confermato', 'ConfermatoConOverride', 'Completato')
                  AND (a.deleted_at IS NULL OR a.deleted_at = '')
                GROUP BY c.id
                HAVING giorni_assente > ?
                  AND c.id NOT IN (
                      SELECT DISTINCT cliente_id FROM appuntamenti
                      WHERE data_ora_inizio > datetime('now')
                        AND stato IN ('Confermato', 'ConfermatoConOverride')
                        AND (deleted_at IS NULL OR deleted_at = '')
                  )
                ORDER BY giorni_assente DESC
                """,
                (days_threshold,),
            ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        logger.error("[Recall] DB query error: %s", e)
        return []


async def check_and_recall_dormant(wa_client: Any) -> None:
    """
    G2 daily job (10:00am). Finds clients dormant >60 days, sends recall WA.

    Idempotent: max 1 recall per client per month (JSON log).
    Throttled: max DORMANT_MAX_PER_DAY per run (avoid WA spam/ban).
    Revenue: +15% recovery rate on dormant clients.
    """
    if wa_client is None or not wa_client.is_connected():
        logger.debug("[Recall] WA not connected — skip dormant recall")
        return

    dormant = _get_dormant_clients()
    if not dormant:
        logger.debug("[Recall] No dormant clients found")
        return

    sent = 0
    for cliente in dormant:
        if sent >= DORMANT_MAX_PER_DAY:
            logger.info("[Recall] Daily limit reached (%d), remaining for tomorrow", DORMANT_MAX_PER_DAY)
            break

        cid = str(cliente["id"])
        nome = cliente.get("nome", "Cliente")
        phone = cliente.get("telefono", "")
        giorni = int(cliente.get("giorni_assente", 0))

        if _recall_recently_sent(cid):
            logger.debug("[Recall] Already recalled %s within 30 days — skip", nome)
            continue

        try:
            message = (
                f"Ciao {nome}! 👋\n\n"
                f"È passato un po' di tempo dalla tua ultima visita "
                f"e volevamo sapere come stai.\n\n"
                f"Abbiamo disponibilità questa settimana — "
                f"rispondi a questo messaggio o chiamaci per prenotare!\n\n"
                f"Ti aspettiamo 😊"
            )
            result = wa_client.send_message(phone, message)
            if result.get("success", False):
                _mark_recall_sent(cid)
                sent += 1
                logger.info(
                    "[Recall] ✅ Sent recall to %s (dormant %d days, phone: %s)",
                    nome, giorni, phone,
                )
            else:
                logger.warning("[Recall] ❌ Failed to send to %s: %s", nome, result)
        except Exception as e:
            logger.error("[Recall] Exception sending to %s: %s", nome, e)

    if sent:
        logger.info("[Recall] Sent %d dormant recall messages today", sent)
    else:
        logger.debug("[Recall] No recalls sent (all recently contacted or no dormant)")


# ═══════════════════════════════════════════════════════════════════
# SCHEDULER LIFECYCLE
# ═══════════════════════════════════════════════════════════════════

def start_reminder_scheduler(wa_client: Any, callback_handler: Any = None) -> Any:
    """
    Start APScheduler AsyncIOScheduler for appointment reminders.

    Args:
        wa_client: WhatsAppClient instance (or None if WA not configured)
        callback_handler: WhatsAppCallbackHandler instance — Gap #4: register pending
            appointments after reminder send so client replies are attributed correctly.

    Returns:
        APScheduler instance (or None if APScheduler not available)
    """
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        logger.warning(
            "[Reminder] APScheduler not installed — reminders disabled. "
            "Install with: pip install apscheduler>=3.10.0"
        )
        return None

    scheduler = AsyncIOScheduler()

    # Job 1: Appointment reminders -24h/-1h (every 15 min)
    # Gap #4: pass callback_handler so pending appointments are registered on send
    scheduler.add_job(
        check_and_send_reminders,
        trigger="interval",
        minutes=15,
        args=[wa_client, callback_handler],
        id="reminder_check",
        name="Appointment Reminder Check (-24h/-1h)",
        next_run_time=datetime.now(),
        misfire_grace_time=60,
    )

    # Job 2: Gap #3 — Waitlist slot-free notifications (every 5 min)
    # World-class: catches UI-initiated cancellations that voice FSM cannot see
    scheduler.add_job(
        check_and_notify_waitlist,
        trigger="interval",
        minutes=5,
        args=[wa_client],
        id="waitlist_check",
        name="Waitlist Slot-Free Notification Check",
        next_run_time=datetime.now(),
        misfire_grace_time=30,
    )

    # Job 3: Gap #6 — Birthday WA (daily at 9:00am)
    # Revenue: +8% return rate. Clienti si sentono ricordati → tornano.
    from apscheduler.triggers.cron import CronTrigger
    scheduler.add_job(
        check_and_send_birthdays,
        trigger=CronTrigger(hour=9, minute=0),
        args=[wa_client],
        id="birthday_check",
        name="Birthday WhatsApp Greetings (daily 9:00am)",
        misfire_grace_time=3600,  # 1h grace — se pipeline riavviata entro 1h, invia comunque
    )

    # Job 4: G2 — Dormant client recall (daily at 10:00am)
    # Revenue: +15% recovery. Max 10/day to avoid WA spam.
    scheduler.add_job(
        check_and_recall_dormant,
        trigger=CronTrigger(hour=10, minute=0),
        args=[wa_client],
        id="dormant_recall",
        name="Dormant Client Recall (daily 10:00am, >60 days)",
        misfire_grace_time=3600,
    )

    # Job 5: G6 — Weekly self-learning loop (Sunday 6:00am)
    # Compounding: each week Sara identifies and improves weak spots.
    try:
        from weekly_learning import run_weekly_learning
        scheduler.add_job(
            run_weekly_learning,
            trigger=CronTrigger(day_of_week="sun", hour=6, minute=0),
            id="weekly_learning",
            name="Weekly Self-Learning Analysis (Sunday 6:00am)",
            misfire_grace_time=7200,  # 2h grace — if pipeline restarted on Sunday morning
        )
    except ImportError:
        logger.warning("[Reminder] weekly_learning module not found — G6 disabled")

    scheduler.start()
    logger.info(
        "[Reminder] ✅ Scheduler started — reminders 15min | waitlist 5min | birthday 9:00 | recall 10:00 | learning Sun 6:00"
    )
    return scheduler
