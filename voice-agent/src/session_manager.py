"""
FLUXION Voice Agent - Session Manager

Enterprise-grade session management with SQLite persistence.
Handles conversation state, GDPR compliance, and audit logging.

Features:
- Session persistence to SQLite
- Automatic session timeout
- GDPR audit logging with 30-day anonymization
- Conversation context preservation
- Multi-channel support (voice, whatsapp)
"""

import uuid
import json
import sqlite3
import aiohttp
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path


# HTTP Bridge URL for database operations (secondary/sync)
HTTP_BRIDGE_URL = "http://127.0.0.1:3001"

# Local SQLite path (primary storage — always available)
_FLUXION_DIR = Path.home() / ".fluxion"
DEFAULT_SESSIONS_DB = str(_FLUXION_DIR / "voice_sessions.db")


class SessionChannel(Enum):
    """Session channel types."""
    VOICE = "voice"
    WHATSAPP = "whatsapp"
    WEB = "web"


class SessionState(Enum):
    """Session lifecycle states."""
    ACTIVE = "active"
    IDLE = "idle"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"


@dataclass
class SessionTurn:
    """A single conversation turn."""
    turn_id: str
    timestamp: str
    user_input: str
    intent: str
    response: str
    latency_ms: float
    layer_used: str  # L1_exact, L2_pattern, L3_faq, L4_groq
    sentiment: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def anonymize(self) -> "SessionTurn":
        """Return anonymized copy for GDPR compliance."""
        return SessionTurn(
            turn_id=self.turn_id,
            timestamp=self.timestamp,
            user_input="[ANONYMIZED]",
            intent=self.intent,
            response="[ANONYMIZED]",
            latency_ms=self.latency_ms,
            layer_used=self.layer_used,
            sentiment=self.sentiment,
            entities={}
        )


@dataclass
class VoiceSession:
    """Voice conversation session."""
    session_id: str
    channel: SessionChannel
    state: SessionState
    verticale_id: str
    business_name: str

    # Timestamps
    created_at: str
    updated_at: str
    expires_at: str

    # Client info (optional)
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    phone_number: Optional[str] = None

    # Conversation
    turns: List[SessionTurn] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    # Outcome
    outcome: Optional[str] = None  # booking_created, info_provided, escalated, etc.
    booking_id: Optional[str] = None
    escalation_reason: Optional[str] = None

    # Metrics
    total_turns: int = 0
    avg_latency_ms: float = 0.0
    groq_calls: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["channel"] = self.channel.value
        data["state"] = self.state.value
        data["turns"] = [t.to_dict() for t in self.turns]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoiceSession":
        data["channel"] = SessionChannel(data["channel"])
        data["state"] = SessionState(data["state"])
        data["turns"] = [SessionTurn(**t) for t in data.get("turns", [])]
        return cls(**data)

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        expires = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expires

    @property
    def duration_seconds(self) -> float:
        """Get session duration in seconds."""
        start = datetime.fromisoformat(self.created_at)
        end = datetime.fromisoformat(self.updated_at)
        return (end - start).total_seconds()


class SessionManager:
    """
    Enterprise session manager with persistence.

    Storage strategy (dual-layer):
    - PRIMARY: SQLite locale (~/.fluxion/voice_sessions.db) — sempre disponibile
    - SECONDARY: HTTP Bridge (3001) — sync best-effort, offline-safe

    Features:
    - Automatic recovery after restart (active sessions restored from SQLite)
    - GDPR audit logging in SQLite (no Bridge dependency)
    - Session expiration + cleanup
    """

    SESSIONS_SCHEMA = """
    CREATE TABLE IF NOT EXISTS voice_sessions (
        session_id   TEXT PRIMARY KEY,
        channel      TEXT NOT NULL,
        state        TEXT NOT NULL,
        verticale_id TEXT NOT NULL,
        business_name TEXT NOT NULL,
        created_at   TEXT NOT NULL,
        updated_at   TEXT NOT NULL,
        expires_at   TEXT NOT NULL,
        client_id    TEXT,
        client_name  TEXT,
        phone_number TEXT,
        turns_json   TEXT DEFAULT '[]',
        context_json TEXT DEFAULT '{}',
        outcome      TEXT,
        booking_id   TEXT,
        escalation_reason TEXT,
        total_turns  INTEGER DEFAULT 0,
        avg_latency_ms REAL DEFAULT 0.0,
        groq_calls   INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS voice_audit_log (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id      TEXT NOT NULL,
        action          TEXT NOT NULL,
        timestamp       TEXT NOT NULL,
        details_json    TEXT DEFAULT '{}',
        retention_until TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_sessions_state
        ON voice_sessions(state);
    CREATE INDEX IF NOT EXISTS idx_sessions_expires
        ON voice_sessions(expires_at);
    CREATE INDEX IF NOT EXISTS idx_audit_session
        ON voice_audit_log(session_id);
    """

    def __init__(
        self,
        http_bridge_url: str = HTTP_BRIDGE_URL,
        session_timeout_minutes: int = 30,
        gdpr_retention_days: int = 30,
        db_path: Optional[str] = None
    ):
        self.http_bridge_url = http_bridge_url
        self.session_timeout_minutes = session_timeout_minutes
        self.gdpr_retention_days = gdpr_retention_days
        self.db_path = db_path or DEFAULT_SESSIONS_DB

        # In-memory session cache
        self._sessions: Dict[str, VoiceSession] = {}

        # Initialize local SQLite (creates dir + schema if needed)
        self._init_db()

        # Recover active sessions from SQLite after restart
        self._recover_sessions()

    # =========================================================================
    # SQLite local persistence (PRIMARY)
    # =========================================================================

    def _init_db(self) -> None:
        """Create ~/.fluxion/ dir and sessions schema if not exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._get_db_conn() as conn:
            conn.executescript(self.SESSIONS_SCHEMA)
            conn.commit()

    @contextmanager
    def _get_db_conn(self):
        """Sync SQLite connection context manager (same pattern as analytics.py)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _persist_to_sqlite(self, session: "VoiceSession") -> bool:
        """Write/update session to local SQLite. Always synchronous."""
        try:
            with self._get_db_conn() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO voice_sessions (
                        session_id, channel, state, verticale_id, business_name,
                        created_at, updated_at, expires_at,
                        client_id, client_name, phone_number,
                        turns_json, context_json,
                        outcome, booking_id, escalation_reason,
                        total_turns, avg_latency_ms, groq_calls
                    ) VALUES (
                        :session_id, :channel, :state, :verticale_id, :business_name,
                        :created_at, :updated_at, :expires_at,
                        :client_id, :client_name, :phone_number,
                        :turns_json, :context_json,
                        :outcome, :booking_id, :escalation_reason,
                        :total_turns, :avg_latency_ms, :groq_calls
                    )
                """, {
                    "session_id": session.session_id,
                    "channel": session.channel.value,
                    "state": session.state.value,
                    "verticale_id": session.verticale_id,
                    "business_name": session.business_name,
                    "created_at": session.created_at,
                    "updated_at": session.updated_at,
                    "expires_at": session.expires_at,
                    "client_id": session.client_id,
                    "client_name": session.client_name,
                    "phone_number": session.phone_number,
                    "turns_json": json.dumps([t.to_dict() for t in session.turns], ensure_ascii=False),
                    "context_json": json.dumps(session.context, ensure_ascii=False),
                    "outcome": session.outcome,
                    "booking_id": session.booking_id,
                    "escalation_reason": session.escalation_reason,
                    "total_turns": session.total_turns,
                    "avg_latency_ms": session.avg_latency_ms,
                    "groq_calls": session.groq_calls,
                })
                conn.commit()
            return True
        except Exception as e:
            print(f"[SessionManager] SQLite persist error: {e}")
            return False

    def _load_from_sqlite(self, session_id: str) -> Optional["VoiceSession"]:
        """Load a single session from local SQLite."""
        try:
            with self._get_db_conn() as conn:
                row = conn.execute(
                    "SELECT * FROM voice_sessions WHERE session_id = ?", (session_id,)
                ).fetchone()
                if row:
                    return self._row_to_session(row)
        except Exception as e:
            print(f"[SessionManager] SQLite load error: {e}")
        return None

    def _recover_sessions(self) -> int:
        """
        Restore ACTIVE/IDLE non-expired sessions into memory after restart.
        Returns number of sessions recovered.
        """
        now = datetime.now().isoformat()
        recovered = 0
        try:
            with self._get_db_conn() as conn:
                rows = conn.execute("""
                    SELECT * FROM voice_sessions
                    WHERE state IN ('active', 'idle')
                      AND expires_at > ?
                """, (now,)).fetchall()
                for row in rows:
                    session = self._row_to_session(row)
                    self._sessions[session.session_id] = session
                    recovered += 1
            if recovered:
                print(f"[SessionManager] Recovered {recovered} active session(s) from SQLite.")
        except Exception as e:
            print(f"[SessionManager] Recovery error: {e}")
        return recovered

    def _log_audit_sqlite(
        self,
        session_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Write audit entry directly to local SQLite (sync, no HTTP)."""
        retention_until = (
            datetime.now() + timedelta(days=self.gdpr_retention_days)
        ).isoformat()
        try:
            with self._get_db_conn() as conn:
                conn.execute("""
                    INSERT INTO voice_audit_log
                        (session_id, action, timestamp, details_json, retention_until)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    action,
                    datetime.now().isoformat(),
                    json.dumps(details or {}, ensure_ascii=False),
                    retention_until,
                ))
                conn.commit()
        except Exception as e:
            print(f"[SessionManager] Audit SQLite error: {e}")

    @staticmethod
    def _row_to_session(row: sqlite3.Row) -> "VoiceSession":
        """Deserialize a SQLite row into a VoiceSession object."""
        turns_raw = json.loads(row["turns_json"] or "[]")
        turns = [SessionTurn(**t) for t in turns_raw]
        return VoiceSession(
            session_id=row["session_id"],
            channel=SessionChannel(row["channel"]),
            state=SessionState(row["state"]),
            verticale_id=row["verticale_id"],
            business_name=row["business_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            expires_at=row["expires_at"],
            client_id=row["client_id"],
            client_name=row["client_name"],
            phone_number=row["phone_number"],
            turns=turns,
            context=json.loads(row["context_json"] or "{}"),
            outcome=row["outcome"],
            booking_id=row["booking_id"],
            escalation_reason=row["escalation_reason"],
            total_turns=row["total_turns"],
            avg_latency_ms=row["avg_latency_ms"],
            groq_calls=row["groq_calls"],
        )

    def create_session(
        self,
        verticale_id: str,
        business_name: str,
        channel: SessionChannel = SessionChannel.VOICE,
        phone_number: Optional[str] = None
    ) -> VoiceSession:
        """
        Create a new voice session.

        Args:
            verticale_id: Business vertical ID
            business_name: Business name for greeting
            channel: Communication channel
            phone_number: Caller phone number (if available)

        Returns:
            New VoiceSession
        """
        now = datetime.now()
        expires = now + timedelta(minutes=self.session_timeout_minutes)

        session = VoiceSession(
            session_id=str(uuid.uuid4()),
            channel=channel,
            state=SessionState.ACTIVE,
            verticale_id=verticale_id,
            business_name=business_name,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            expires_at=expires.isoformat(),
            phone_number=phone_number
        )

        self._sessions[session.session_id] = session
        # Persist immediately so session survives a restart even without explicit persist_session()
        self._persist_to_sqlite(session)
        return session

    def get_session(self, session_id: str) -> Optional[VoiceSession]:
        """Get session by ID."""
        session = self._sessions.get(session_id)
        if session and session.is_expired:
            self.close_session(session_id, "timeout")
            return None
        return session

    def add_turn(
        self,
        session_id: str,
        user_input: str,
        intent: str,
        response: str,
        latency_ms: float,
        layer_used: str,
        sentiment: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Add a conversation turn to session.

        Returns:
            Turn ID or None if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        turn_id = str(uuid.uuid4())[:8]
        turn = SessionTurn(
            turn_id=turn_id,
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            intent=intent,
            response=response,
            latency_ms=latency_ms,
            layer_used=layer_used,
            sentiment=sentiment,
            entities=entities or {}
        )

        session.turns.append(turn)
        session.total_turns += 1
        session.updated_at = datetime.now().isoformat()

        # Update metrics
        if layer_used == "L4_groq":
            session.groq_calls += 1

        total_latency = sum(t.latency_ms for t in session.turns)
        session.avg_latency_ms = total_latency / len(session.turns)

        # Extend expiration
        session.expires_at = (
            datetime.now() + timedelta(minutes=self.session_timeout_minutes)
        ).isoformat()

        return turn_id

    def update_client(
        self,
        session_id: str,
        client_id: str,
        client_name: str
    ) -> bool:
        """Update session with identified client."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.client_id = client_id
        session.client_name = client_name
        session.updated_at = datetime.now().isoformat()
        return True

    def update_context(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """Update session context (booking info, etc.)."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.context.update(context)
        session.updated_at = datetime.now().isoformat()
        return True

    def close_session(
        self,
        session_id: str,
        outcome: str,
        booking_id: Optional[str] = None,
        escalation_reason: Optional[str] = None
    ) -> bool:
        """
        Close a session with outcome.

        Args:
            session_id: Session to close
            outcome: Session outcome (booking_created, info_provided, escalated, timeout)
            booking_id: Optional booking ID if booking was created
            escalation_reason: Reason for escalation if escalated

        Returns:
            True if closed successfully
        """
        # Use direct dict access to avoid recursion with get_session()
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.outcome = outcome
        session.booking_id = booking_id
        session.escalation_reason = escalation_reason
        session.updated_at = datetime.now().isoformat()

        if outcome == "escalated":
            session.state = SessionState.ESCALATED
        elif outcome == "timeout":
            session.state = SessionState.TIMEOUT
        else:
            session.state = SessionState.COMPLETED

        # Persist final state immediately to SQLite
        self._persist_to_sqlite(session)
        return True

    async def persist_session(self, session_id: str) -> bool:
        """
        Persist session to storage.

        PRIMARY:   SQLite locale (~/.fluxion/voice_sessions.db) — always available
        SECONDARY: HTTP Bridge (3001) — best-effort sync, non-blocking

        Returns:
            True if SQLite write succeeded (Bridge failure is non-fatal)
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        # PRIMARY: SQLite locale (sync, fast, always works)
        ok = self._persist_to_sqlite(session)

        # SECONDARY: HTTP Bridge sync (best-effort, fire-and-forget)
        try:
            async with aiohttp.ClientSession() as http_session:
                url = f"{self.http_bridge_url}/api/voice/sessions"
                async with http_session.post(
                    url,
                    json=session.to_dict(),
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    if resp.status != 200:
                        print(f"[SessionManager] Bridge sync warning: HTTP {resp.status}")
        except Exception:
            # Bridge offline is expected — SQLite already saved
            pass

        return ok

    async def load_session(self, session_id: str) -> Optional[VoiceSession]:
        """
        Load session by ID.

        Lookup order:
        1. In-memory cache (fastest)
        2. SQLite locale (primary persistent store)
        3. HTTP Bridge (fallback, may be offline)

        Returns:
            VoiceSession or None
        """
        # 1. In-memory cache
        if session_id in self._sessions:
            return self._sessions[session_id]

        # 2. SQLite locale (PRIMARY)
        session = self._load_from_sqlite(session_id)
        if session:
            self._sessions[session_id] = session
            return session

        # 3. HTTP Bridge (FALLBACK — may be offline)
        try:
            async with aiohttp.ClientSession() as http_session:
                url = f"{self.http_bridge_url}/api/voice/sessions/{session_id}"
                async with http_session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        session = VoiceSession.from_dict(data)
                        self._sessions[session_id] = session
                        # Backfill local SQLite from Bridge
                        self._persist_to_sqlite(session)
                        return session
        except Exception:
            pass

        return None

    async def log_audit(
        self,
        session_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log audit entry for GDPR compliance.

        PRIMARY:   SQLite locale (always available, synchronous)
        SECONDARY: HTTP Bridge (best-effort)

        Args:
            session_id: Session ID
            action: Action performed (session_start, turn, booking_created, etc.)
            details: Additional details (anonymized after retention period)

        Returns:
            True always (SQLite write is primary)
        """
        # PRIMARY: SQLite (sync, zero-dependency)
        self._log_audit_sqlite(session_id, action, details)

        # SECONDARY: HTTP Bridge (best-effort)
        try:
            async with aiohttp.ClientSession() as http_session:
                url = f"{self.http_bridge_url}/api/voice/audit"
                data = {
                    "session_id": session_id,
                    "action": action,
                    "timestamp": datetime.now().isoformat(),
                    "details": details or {},
                    "retention_until": (
                        datetime.now() + timedelta(days=self.gdpr_retention_days)
                    ).isoformat()
                }
                async with http_session.post(
                    url,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    pass
        except Exception:
            pass

        return True

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary for analytics."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "channel": session.channel.value,
            "state": session.state.value,
            "duration_seconds": session.duration_seconds,
            "total_turns": session.total_turns,
            "avg_latency_ms": session.avg_latency_ms,
            "groq_calls": session.groq_calls,
            "client_identified": session.client_id is not None,
            "outcome": session.outcome,
            "booking_created": session.booking_id is not None
        }

    def get_greeting(self, session_id: str) -> str:
        """
        Get personalized greeting for session.

        Uses business_name from session config, NOT hardcoded.
        """
        session = self._sessions.get(session_id)
        if not session:
            return "Buongiorno! Come posso aiutarla?"

        hour = datetime.now().hour
        if hour < 12:
            saluto = "Buongiorno"
        elif hour < 18:
            saluto = "Buon pomeriggio"
        else:
            saluto = "Buonasera"

        return f"{saluto}! Sono Sara, l'assistente vocale di {session.business_name}. Come posso aiutarla?"


# Singleton instance
_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get singleton session manager."""
    global _manager
    if _manager is None:
        _manager = SessionManager()
    return _manager


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    manager = SessionManager()

    print("Test: Session Management")
    print("-" * 40)

    # Create session
    session = manager.create_session(
        verticale_id="salone_bella_vita",
        business_name="Salone Bella Vita",
        channel=SessionChannel.VOICE
    )
    print(f"Created session: {session.session_id[:8]}...")
    print(f"Business: {session.business_name}")

    # Get greeting
    greeting = manager.get_greeting(session.session_id)
    print(f"Greeting: {greeting}")

    # Add turns
    turn_id = manager.add_turn(
        session_id=session.session_id,
        user_input="Vorrei prenotare un taglio",
        intent="prenotazione",
        response="Certo! Per quale giorno desidera?",
        latency_ms=45.2,
        layer_used="L2_pattern",
        sentiment="neutral",
        entities={"servizio": "taglio"}
    )
    print(f"\nAdded turn: {turn_id}")

    # Update client
    manager.update_client(session.session_id, "cliente_123", "Mario Rossi")
    print(f"Updated client: Mario Rossi")

    # Get summary
    summary = manager.get_session_summary(session.session_id)
    print(f"\nSession summary:")
    print(f"  Turns: {summary['total_turns']}")
    print(f"  Avg latency: {summary['avg_latency_ms']:.1f}ms")
    print(f"  Client identified: {summary['client_identified']}")

    # Close session
    manager.close_session(session.session_id, "booking_created", "booking_456")
    print(f"\nSession closed with outcome: booking_created")
