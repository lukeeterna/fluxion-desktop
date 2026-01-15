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
import aiohttp
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


# HTTP Bridge URL for database operations
HTTP_BRIDGE_URL = "http://127.0.0.1:3001"


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

    Handles:
    - Session lifecycle (create, update, close)
    - SQLite persistence via HTTP Bridge
    - GDPR audit logging
    - Automatic expiration
    """

    def __init__(
        self,
        http_bridge_url: str = HTTP_BRIDGE_URL,
        session_timeout_minutes: int = 30,
        gdpr_retention_days: int = 30
    ):
        self.http_bridge_url = http_bridge_url
        self.session_timeout_minutes = session_timeout_minutes
        self.gdpr_retention_days = gdpr_retention_days

        # In-memory session cache
        self._sessions: Dict[str, VoiceSession] = {}

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
        session = self.get_session(session_id)
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

        return True

    async def persist_session(self, session_id: str) -> bool:
        """
        Persist session to database via HTTP Bridge.

        Returns:
            True if persisted successfully
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        try:
            async with aiohttp.ClientSession() as http_session:
                url = f"{self.http_bridge_url}/api/voice/sessions"
                async with http_session.post(
                    url,
                    json=session.to_dict(),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"Error persisting session: {e}")
            return False

    async def load_session(self, session_id: str) -> Optional[VoiceSession]:
        """
        Load session from database.

        Returns:
            VoiceSession or None
        """
        try:
            async with aiohttp.ClientSession() as http_session:
                url = f"{self.http_bridge_url}/api/voice/sessions/{session_id}"
                async with http_session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        session = VoiceSession.from_dict(data)
                        self._sessions[session_id] = session
                        return session
        except Exception as e:
            print(f"Error loading session: {e}")

        return None

    async def log_audit(
        self,
        session_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log audit entry for GDPR compliance.

        Args:
            session_id: Session ID
            action: Action performed (session_start, turn, booking_created, etc.)
            details: Additional details (will be anonymized after retention period)

        Returns:
            True if logged successfully
        """
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
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    return resp.status == 200
        except Exception:
            pass

        return False

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
