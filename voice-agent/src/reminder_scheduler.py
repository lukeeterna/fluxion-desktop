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

_SENT_LOG_PATH = Path(__file__).parent.parent / ".whatsapp-session" / "reminders_sent.json"


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
        conn = sqlite3.connect(str(db_path), timeout=3)
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
        conn.close()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        logger.error("[Reminder] DB query error: %s", e)
        return []


# ═══════════════════════════════════════════════════════════════════
# CORE SCHEDULER JOB
# ═══════════════════════════════════════════════════════════════════

async def check_and_send_reminders(wa_client: Any) -> None:
    """
    Main scheduler job. Runs every 15 min.
    Checks -24h and -1h windows and sends WA reminders if not already sent.

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
        sent = await _send_reminder(wa_client, appt, "reminder_24h")
        if sent:
            _mark_sent(apt_id, "reminder_24h")
            total_sent += 1

    for appt in appointments_1h:
        apt_id = appt["appointment_id"]
        if _already_sent(apt_id, "reminder_1h"):
            continue
        sent = await _send_reminder(wa_client, appt, "reminder_1h")
        if sent:
            _mark_sent(apt_id, "reminder_1h")
            total_sent += 1

    if total_sent:
        logger.info("[Reminder] Sent %d reminders (run at %s)", total_sent, now.strftime("%H:%M"))
    else:
        logger.debug("[Reminder] No reminders due at %s", now.strftime("%H:%M"))


async def _send_reminder(
    wa_client: Any, appt: Dict[str, Any], reminder_type: str
) -> bool:
    """Send a single WA reminder. Returns True on success."""
    phone = appt.get("cliente_telefono", "")
    nome = appt.get("cliente_nome", "Cliente")
    servizio = appt.get("servizio_nome", "")
    data_ora = appt.get("data_ora_inizio", "")

    if not phone:
        logger.warning("[Reminder] No phone for appointment %s — skip", appt["appointment_id"])
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
    Return waitlist entries in 'attesa' stato with phone + preferred slot.
    Joins with clienti for phone number.
    """
    db_path = _get_db_path()
    if db_path is None:
        return []
    try:
        conn = sqlite3.connect(str(db_path), timeout=3)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                w.id              AS waitlist_id,
                w.servizio,
                w.data_preferita,
                w.ora_preferita,
                w.priorita_valore,
                c.nome            AS cliente_nome,
                c.telefono        AS cliente_telefono
            FROM waitlist w
            JOIN clienti c ON w.cliente_id = c.id
            WHERE w.stato = 'attesa'
              AND w.data_preferita >= date('now')
            ORDER BY w.priorita_valore DESC, w.created_at ASC
            """
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        logger.error("[Waitlist] DB query error: %s", e)
        return []


def _is_slot_free(servizio: str, data_preferita: str, ora_preferita: str) -> bool:
    """
    Check if the requested slot is free (no confirmed appointment at that date/time
    for the same service type).
    """
    db_path = _get_db_path()
    if db_path is None:
        return False
    if not data_preferita or not ora_preferita:
        return False  # Flexible waitlist — skip (no specific slot to check)
    try:
        # Build ISO datetime for comparison
        dt_str = f"{data_preferita}T{ora_preferita}:00"
        conn = sqlite3.connect(str(db_path), timeout=3)
        row = conn.execute(
            """
            SELECT COUNT(*) FROM appuntamenti a
            JOIN servizi s ON a.servizio_id = s.id
            WHERE s.nome = ?
              AND a.data_ora_inizio = ?
              AND a.stato IN ('Confermato', 'ConfermatoConOverride')
              AND (a.deleted_at IS NULL OR a.deleted_at = '')
            """,
            (servizio, dt_str),
        ).fetchone()
        conn.close()
        return row[0] == 0  # Free if no confirmed appointment found
    except sqlite3.Error as e:
        logger.error("[Waitlist] Slot-free check error: %s", e)
        return False


def _mark_waitlist_notified(waitlist_id: str) -> None:
    """Mark waitlist entry as 'contattato' so we don't re-notify."""
    db_path = _get_db_path()
    if db_path is None:
        return
    try:
        conn = sqlite3.connect(str(db_path), timeout=3)
        conn.execute(
            "UPDATE waitlist SET stato = 'contattato', contattato_at = datetime('now') WHERE id = ?",
            (waitlist_id,),
        )
        conn.commit()
        conn.close()
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
        servizio = entry.get("servizio", "")
        data_pref = entry.get("data_preferita", "")
        ora_pref = entry.get("ora_preferita", "")

        # Only notify if a specific slot was requested and it's now free
        if not data_pref or not ora_pref:
            continue

        if not _is_slot_free(servizio, data_pref, ora_pref):
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
# SCHEDULER LIFECYCLE
# ═══════════════════════════════════════════════════════════════════

def start_reminder_scheduler(wa_client: Any) -> Any:
    """
    Start APScheduler AsyncIOScheduler for appointment reminders.

    Args:
        wa_client: WhatsAppClient instance (or None if WA not configured)

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
    scheduler.add_job(
        check_and_send_reminders,
        trigger="interval",
        minutes=15,
        args=[wa_client],
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

    scheduler.start()
    logger.info(
        "[Reminder] ✅ Scheduler started — reminders every 15min | waitlist every 5min"
    )
    return scheduler
