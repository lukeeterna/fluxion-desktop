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
    scheduler.add_job(
        check_and_send_reminders,
        trigger="interval",
        minutes=15,
        args=[wa_client],
        id="reminder_check",
        name="Appointment Reminder Check (-24h/-1h)",
        # First run immediately at startup (misfire_grace_time allows late start)
        next_run_time=datetime.now(),
        misfire_grace_time=60,
    )
    scheduler.start()
    logger.info("[Reminder] ✅ Scheduler started — checking every 15min for -24h/-1h reminders")
    return scheduler
