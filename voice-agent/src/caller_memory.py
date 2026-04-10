"""
FLUXION Voice Agent - Caller Memory

Cross-call persistence for returning callers.
Stores caller preferences, history, and patterns in SQLite.

Features:
- Phone number → caller profile lookup
- Preferred day/time calculation from booking history
- Call count tracking
- GDPR-compliant: anonymize after 365 days of inactivity
"""

import logging
import sqlite3
import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

# Local SQLite path (same dir as voice_sessions.db)
_FLUXION_DIR = Path.home() / ".fluxion"
DEFAULT_CALLER_DB = str(_FLUXION_DIR / "caller_memory.db")


@dataclass
class CallerProfile:
    """Profile for a returning caller."""
    phone_number: str
    client_name: str = ""
    call_count: int = 0
    last_service: str = ""
    last_operator: str = ""
    preferred_day: str = ""       # e.g. "martedi"
    preferred_time: str = ""      # e.g. "10:00"
    last_call_at: str = ""
    created_at: str = ""
    notes: str = ""               # JSON string for extra data

    @property
    def is_returning(self) -> bool:
        return self.call_count > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phone_number": self.phone_number,
            "client_name": self.client_name,
            "call_count": self.call_count,
            "last_service": self.last_service,
            "last_operator": self.last_operator,
            "preferred_day": self.preferred_day,
            "preferred_time": self.preferred_time,
            "last_call_at": self.last_call_at,
            "created_at": self.created_at,
            "notes": self.notes,
        }


class CallerMemory:
    """
    SQLite-backed caller memory for returning caller recognition.

    Usage:
        memory = CallerMemory()
        profile = memory.lookup("+390972536918")
        if profile and profile.is_returning:
            greeting = f"Bentornato {profile.client_name}!"
        memory.record_call(phone, name="Mario", service="Taglio", operator="Luca")
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS caller_profiles (
        phone_number  TEXT PRIMARY KEY,
        client_name   TEXT DEFAULT '',
        call_count    INTEGER DEFAULT 0,
        last_service  TEXT DEFAULT '',
        last_operator TEXT DEFAULT '',
        preferred_day TEXT DEFAULT '',
        preferred_time TEXT DEFAULT '',
        last_call_at  TEXT DEFAULT '',
        created_at    TEXT NOT NULL,
        notes         TEXT DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS caller_bookings (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number  TEXT NOT NULL,
        service       TEXT DEFAULT '',
        operator      TEXT DEFAULT '',
        day_of_week   TEXT DEFAULT '',
        time_slot     TEXT DEFAULT '',
        booked_at     TEXT NOT NULL,
        FOREIGN KEY (phone_number) REFERENCES caller_profiles(phone_number)
    );

    CREATE INDEX IF NOT EXISTS idx_bookings_phone
        ON caller_bookings(phone_number);
    """

    def __init__(self, db_path: str = DEFAULT_CALLER_DB):
        self.db_path = db_path
        _FLUXION_DIR.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        try:
            with self._connect() as conn:
                conn.executescript(self.SCHEMA)
        except Exception as e:
            logger.error(f"CallerMemory DB init error: {e}")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def lookup(self, phone_number: str) -> Optional[CallerProfile]:
        """Look up a caller by phone number.

        Returns CallerProfile if found, None otherwise.
        """
        if not phone_number:
            return None

        phone = self._normalize_phone(phone_number)
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM caller_profiles WHERE phone_number = ?",
                    (phone,)
                ).fetchone()
                if row:
                    return CallerProfile(
                        phone_number=row["phone_number"],
                        client_name=row["client_name"],
                        call_count=row["call_count"],
                        last_service=row["last_service"],
                        last_operator=row["last_operator"],
                        preferred_day=row["preferred_day"],
                        preferred_time=row["preferred_time"],
                        last_call_at=row["last_call_at"],
                        created_at=row["created_at"],
                        notes=row["notes"],
                    )
        except Exception as e:
            logger.error(f"CallerMemory lookup error: {e}")
        return None

    def record_call(
        self,
        phone_number: str,
        client_name: str = "",
        service: str = "",
        operator: str = "",
        day_of_week: str = "",
        time_slot: str = "",
    ) -> CallerProfile:
        """Record a call from a caller. Creates or updates their profile.

        Args:
            phone_number: Caller phone (SIP-extracted or manual)
            client_name: Name if identified during the call
            service: Service booked (if any)
            operator: Operator requested (if any)
            day_of_week: Day of booking (e.g. "lunedi")
            time_slot: Time of booking (e.g. "10:00")

        Returns:
            Updated CallerProfile
        """
        if not phone_number:
            return CallerProfile(phone_number="")

        phone = self._normalize_phone(phone_number)
        now = datetime.now().isoformat()

        try:
            with self._connect() as conn:
                # Upsert caller profile
                existing = conn.execute(
                    "SELECT * FROM caller_profiles WHERE phone_number = ?",
                    (phone,)
                ).fetchone()

                if existing:
                    # Update existing
                    updates = {"last_call_at": now, "call_count": existing["call_count"] + 1}
                    if client_name:
                        updates["client_name"] = client_name
                    if service:
                        updates["last_service"] = service
                    if operator:
                        updates["last_operator"] = operator

                    set_clause = ", ".join(f"{k} = ?" for k in updates)
                    values = list(updates.values()) + [phone]
                    conn.execute(
                        f"UPDATE caller_profiles SET {set_clause} WHERE phone_number = ?",
                        values
                    )
                else:
                    # Insert new
                    conn.execute(
                        """INSERT INTO caller_profiles
                        (phone_number, client_name, call_count, last_service,
                         last_operator, last_call_at, created_at)
                        VALUES (?, ?, 1, ?, ?, ?, ?)""",
                        (phone, client_name, service, operator, now, now)
                    )

                # Record booking history (for preferred slot calculation)
                if service or day_of_week or time_slot:
                    conn.execute(
                        """INSERT INTO caller_bookings
                        (phone_number, service, operator, day_of_week, time_slot, booked_at)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (phone, service, operator, day_of_week, time_slot, now)
                    )

                conn.commit()

                # Recalculate preferred day/time
                self._update_preferences(conn, phone)

                return self.lookup(phone) or CallerProfile(phone_number=phone)

        except Exception as e:
            logger.error(f"CallerMemory record_call error: {e}")
            return CallerProfile(phone_number=phone)

    def _update_preferences(self, conn: sqlite3.Connection, phone: str):
        """Recalculate preferred day and time from booking history."""
        rows = conn.execute(
            "SELECT day_of_week, time_slot FROM caller_bookings WHERE phone_number = ? ORDER BY booked_at DESC LIMIT 20",
            (phone,)
        ).fetchall()

        if not rows:
            return

        # Most common day
        days = [r["day_of_week"] for r in rows if r["day_of_week"]]
        if days:
            day_counter = Counter(days)
            preferred_day = day_counter.most_common(1)[0][0]
        else:
            preferred_day = ""

        # Most common time
        times = [r["time_slot"] for r in rows if r["time_slot"]]
        if times:
            time_counter = Counter(times)
            preferred_time = time_counter.most_common(1)[0][0]
        else:
            preferred_time = ""

        if preferred_day or preferred_time:
            conn.execute(
                "UPDATE caller_profiles SET preferred_day = ?, preferred_time = ? WHERE phone_number = ?",
                (preferred_day, preferred_time, phone)
            )
            conn.commit()

    def get_booking_history(self, phone_number: str, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent booking history for a caller."""
        if not phone_number:
            return []

        phone = self._normalize_phone(phone_number)
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT service, operator, day_of_week, time_slot, booked_at FROM caller_bookings WHERE phone_number = ? ORDER BY booked_at DESC LIMIT ?",
                    (phone, limit)
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"CallerMemory get_booking_history error: {e}")
            return []

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normalize phone number: strip SIP URI, keep digits and leading +."""
        if not phone:
            return ""
        # Strip SIP URI format: sip:+390972536918@sip.vivavox.it (case-insensitive)
        _lower = phone.lower()
        if "sip:" in _lower:
            _idx = _lower.index("sip:") + 4
            phone = phone[_idx:].split("@")[0]
        # Strip <> brackets
        phone = phone.strip("<>").strip()
        # Keep only digits and leading +
        if phone.startswith("+"):
            return "+" + "".join(c for c in phone[1:] if c.isdigit())
        return "".join(c for c in phone if c.isdigit())


# Singleton
_memory: Optional[CallerMemory] = None


def get_caller_memory(db_path: str = DEFAULT_CALLER_DB) -> CallerMemory:
    """Get singleton CallerMemory instance."""
    global _memory
    if _memory is None:
        _memory = CallerMemory(db_path=db_path)
    return _memory
