"""
Conversation Analytics & Logging Module.

Week 3 Day 5-6: VOICE-AGENT-RAG.md implementation
Structured logging in SQLite for improvement loop and analytics.
"""

import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ConversationOutcome(Enum):
    """Outcome of a conversation."""
    COMPLETED = "completed"         # User goal achieved
    ESCALATED = "escalated"         # Transferred to operator
    ABANDONED = "abandoned"         # User left mid-conversation
    ERROR = "error"                 # Technical failure
    UNKNOWN = "unknown"             # Incomplete data


@dataclass
class ConversationTurn:
    """Single turn in a conversation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    turn_number: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    user_input: str = ""
    intent: str = ""
    intent_confidence: float = 0.0
    response: str = ""
    latency_ms: float = 0.0
    layer_used: str = ""            # L1_exact, L2_intent, L3_faq, L4_groq
    sentiment: str = "neutral"
    frustration_level: int = 0
    used_groq: bool = False
    escalated: bool = False
    entities_extracted: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """Complete conversation session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    verticale_id: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    outcome: ConversationOutcome = ConversationOutcome.UNKNOWN
    total_turns: int = 0
    total_latency_ms: float = 0.0
    groq_usage_count: int = 0
    escalation_reason: Optional[str] = None
    booking_created: bool = False
    booking_id: Optional[str] = None
    user_satisfaction: Optional[int] = None  # 1-5 rating


@dataclass
class AnalyticsMetrics:
    """Aggregated analytics metrics."""
    total_conversations: int = 0
    total_turns: int = 0
    avg_turns_per_conversation: float = 0.0
    avg_latency_ms: float = 0.0
    groq_usage_percent: float = 0.0
    escalation_rate: float = 0.0
    completion_rate: float = 0.0
    avg_satisfaction: float = 0.0
    intent_distribution: Dict[str, int] = field(default_factory=dict)
    layer_usage: Dict[str, int] = field(default_factory=dict)
    peak_hours: Dict[int, int] = field(default_factory=dict)


class ConversationLogger:
    """
    Structured conversation logger with SQLite backend.

    Features:
    - Persistent storage of all conversation turns
    - Analytics queries for improvement loop
    - Privacy-aware logging (anonymization support)
    - Metrics aggregation for dashboard
    """

    SCHEMA = """
    -- Conversations table
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        verticale_id TEXT,
        started_at DATETIME NOT NULL,
        ended_at DATETIME,
        client_id TEXT,
        client_name TEXT,
        outcome TEXT DEFAULT 'unknown',
        total_turns INTEGER DEFAULT 0,
        total_latency_ms REAL DEFAULT 0.0,
        groq_usage_count INTEGER DEFAULT 0,
        escalation_reason TEXT,
        booking_created BOOLEAN DEFAULT FALSE,
        booking_id TEXT,
        user_satisfaction INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Conversation turns table
    CREATE TABLE IF NOT EXISTS conversation_turns (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        turn_number INTEGER NOT NULL,
        timestamp DATETIME NOT NULL,
        user_input TEXT,
        intent TEXT,
        intent_confidence REAL,
        response TEXT,
        latency_ms REAL,
        layer_used TEXT,
        sentiment TEXT DEFAULT 'neutral',
        frustration_level INTEGER DEFAULT 0,
        used_groq BOOLEAN DEFAULT FALSE,
        escalated BOOLEAN DEFAULT FALSE,
        entities_extracted TEXT,  -- JSON
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    );

    -- Indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_conversations_verticale ON conversations(verticale_id);
    CREATE INDEX IF NOT EXISTS idx_conversations_started_at ON conversations(started_at);
    CREATE INDEX IF NOT EXISTS idx_conversations_outcome ON conversations(outcome);
    CREATE INDEX IF NOT EXISTS idx_turns_conversation ON conversation_turns(conversation_id);
    CREATE INDEX IF NOT EXISTS idx_turns_intent ON conversation_turns(intent);
    CREATE INDEX IF NOT EXISTS idx_turns_timestamp ON conversation_turns(timestamp);

    -- FAQ effectiveness tracking
    CREATE TABLE IF NOT EXISTS faq_effectiveness (
        id TEXT PRIMARY KEY,
        faq_id TEXT NOT NULL,
        question_asked TEXT,
        answer_given TEXT,
        was_helpful BOOLEAN,
        follow_up_needed BOOLEAN,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Daily aggregated metrics (pre-computed for dashboard)
    CREATE TABLE IF NOT EXISTS daily_metrics (
        date TEXT PRIMARY KEY,
        verticale_id TEXT,
        total_conversations INTEGER DEFAULT 0,
        total_turns INTEGER DEFAULT 0,
        avg_latency_ms REAL DEFAULT 0.0,
        groq_usage_percent REAL DEFAULT 0.0,
        escalation_rate REAL DEFAULT 0.0,
        completion_rate REAL DEFAULT 0.0,
        avg_satisfaction REAL DEFAULT 0.0,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- VoIP call logs (Week 4)
    CREATE TABLE IF NOT EXISTS voip_calls (
        id TEXT PRIMARY KEY,
        conversation_id TEXT,
        direction TEXT NOT NULL,
        remote_number TEXT,
        start_time DATETIME NOT NULL,
        connect_time DATETIME,
        end_time DATETIME,
        duration_seconds INTEGER DEFAULT 0,
        outcome TEXT DEFAULT 'unknown',
        sip_status_code INTEGER,
        rtp_packets_sent INTEGER DEFAULT 0,
        rtp_packets_received INTEGER DEFAULT 0,
        audio_quality_score REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    );

    CREATE INDEX IF NOT EXISTS idx_voip_calls_start_time ON voip_calls(start_time);
    CREATE INDEX IF NOT EXISTS idx_voip_calls_remote_number ON voip_calls(remote_number);
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        anonymize: bool = False,
        retention_days: int = 90
    ):
        """
        Initialize ConversationLogger.

        Args:
            db_path: Path to SQLite database (default: ~/.fluxion/voice_analytics.db)
            anonymize: Whether to anonymize PII in logs
            retention_days: Days to retain conversation data (GDPR compliance)
        """
        if db_path is None:
            fluxion_dir = Path.home() / ".fluxion"
            fluxion_dir.mkdir(exist_ok=True)
            db_path = str(fluxion_dir / "voice_analytics.db")

        self.db_path = db_path
        self.anonymize = anonymize
        self.retention_days = retention_days

        # Current active sessions
        self._active_sessions: Dict[str, ConversationSession] = {}

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.executescript(self.SCHEMA)
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # =========================================================================
    # Session Management
    # =========================================================================

    def start_session(
        self,
        verticale_id: str,
        client_id: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> str:
        """
        Start a new conversation session.

        Args:
            verticale_id: Business vertical ID
            client_id: Optional client ID
            client_name: Optional client name

        Returns:
            Session ID
        """
        session = ConversationSession(
            verticale_id=verticale_id,
            client_id=client_id,
            client_name=self._anonymize_if_needed(client_name) if client_name else None
        )

        self._active_sessions[session.id] = session

        # Persist to database
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO conversations (
                    id, verticale_id, started_at, client_id, client_name, outcome
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.verticale_id,
                session.started_at.isoformat(),
                session.client_id,
                session.client_name,
                session.outcome.value
            ))
            conn.commit()

        return session.id

    def end_session(
        self,
        session_id: str,
        outcome: ConversationOutcome = ConversationOutcome.UNKNOWN,
        escalation_reason: Optional[str] = None,
        booking_id: Optional[str] = None,
        user_satisfaction: Optional[int] = None
    ):
        """End a conversation session."""
        session = self._active_sessions.get(session_id)
        if session:
            session.ended_at = datetime.now()
            session.outcome = outcome
            session.escalation_reason = escalation_reason
            session.booking_id = booking_id
            session.booking_created = booking_id is not None
            session.user_satisfaction = user_satisfaction

            # Update database
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE conversations SET
                        ended_at = ?,
                        outcome = ?,
                        total_turns = ?,
                        total_latency_ms = ?,
                        groq_usage_count = ?,
                        escalation_reason = ?,
                        booking_created = ?,
                        booking_id = ?,
                        user_satisfaction = ?
                    WHERE id = ?
                """, (
                    session.ended_at.isoformat(),
                    session.outcome.value,
                    session.total_turns,
                    session.total_latency_ms,
                    session.groq_usage_count,
                    session.escalation_reason,
                    session.booking_created,
                    session.booking_id,
                    session.user_satisfaction,
                    session_id
                ))
                conn.commit()

            del self._active_sessions[session_id]

    def update_session_client(
        self,
        session_id: str,
        client_id: Optional[str],
        client_name: Optional[str]
    ):
        """Update session with identified client information."""
        session = self._active_sessions.get(session_id)
        if session:
            session.client_id = client_id
            session.client_name = client_name

            # Update database
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE conversations SET
                        client_id = ?,
                        client_name = ?
                    WHERE id = ?
                """, (client_id, client_name, session_id))
                conn.commit()

    # =========================================================================
    # Turn Logging
    # =========================================================================

    def log_turn(
        self,
        session_id: str,
        user_input: str,
        intent: str,
        response: str,
        latency_ms: float,
        layer_used: str = "unknown",
        intent_confidence: float = 1.0,
        sentiment: str = "neutral",
        frustration_level: int = 0,
        used_groq: bool = False,
        escalated: bool = False,
        entities: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a conversation turn.

        Args:
            session_id: Session to log to
            user_input: User's input text
            intent: Detected intent
            response: Bot's response
            latency_ms: Processing time in milliseconds
            layer_used: Which RAG layer provided the response
            intent_confidence: Confidence score for intent
            sentiment: Detected sentiment
            frustration_level: Frustration level (0-4)
            used_groq: Whether Groq API was called
            escalated: Whether turn triggered escalation
            entities: Extracted entities

        Returns:
            Turn ID
        """
        session = self._active_sessions.get(session_id)
        if not session:
            # Auto-create session if not exists
            session_id = self.start_session("unknown")
            session = self._active_sessions.get(session_id)

        turn = ConversationTurn(
            conversation_id=session_id,
            turn_number=session.total_turns + 1,
            user_input=self._anonymize_if_needed(user_input),
            intent=intent,
            intent_confidence=intent_confidence,
            response=response,
            latency_ms=latency_ms,
            layer_used=layer_used,
            sentiment=sentiment,
            frustration_level=frustration_level,
            used_groq=used_groq,
            escalated=escalated,
            entities_extracted=entities or {}
        )

        # Update session stats
        session.total_turns += 1
        session.total_latency_ms += latency_ms
        if used_groq:
            session.groq_usage_count += 1

        # Persist to database
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO conversation_turns (
                    id, conversation_id, turn_number, timestamp,
                    user_input, intent, intent_confidence, response,
                    latency_ms, layer_used, sentiment, frustration_level,
                    used_groq, escalated, entities_extracted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                turn.id,
                turn.conversation_id,
                turn.turn_number,
                turn.timestamp.isoformat(),
                turn.user_input,
                turn.intent,
                turn.intent_confidence,
                turn.response,
                turn.latency_ms,
                turn.layer_used,
                turn.sentiment,
                turn.frustration_level,
                turn.used_groq,
                turn.escalated,
                json.dumps(turn.entities_extracted)
            ))

            # Update conversation totals
            conn.execute("""
                UPDATE conversations SET
                    total_turns = total_turns + 1,
                    total_latency_ms = total_latency_ms + ?,
                    groq_usage_count = groq_usage_count + ?
                WHERE id = ?
            """, (latency_ms, 1 if used_groq else 0, session_id))

            conn.commit()

        return turn.id

    # =========================================================================
    # Analytics Queries
    # =========================================================================

    def get_metrics(
        self,
        verticale_id: Optional[str] = None,
        days: int = 7
    ) -> AnalyticsMetrics:
        """
        Get aggregated analytics metrics.

        Args:
            verticale_id: Optional filter by verticale
            days: Number of days to analyze

        Returns:
            AnalyticsMetrics with aggregated data
        """
        since = datetime.now() - timedelta(days=days)

        with self._get_connection() as conn:
            # Build base query
            where_clause = "WHERE c.started_at > ?"
            params: List[Any] = [since.isoformat()]

            if verticale_id:
                where_clause += " AND c.verticale_id = ?"
                params.append(verticale_id)

            # Main conversation metrics
            cursor = conn.execute(f"""
                SELECT
                    COUNT(*) as total_conversations,
                    SUM(c.total_turns) as total_turns,
                    AVG(c.total_turns) as avg_turns,
                    AVG(c.total_latency_ms / NULLIF(c.total_turns, 0)) as avg_latency,
                    SUM(c.groq_usage_count) * 100.0 / NULLIF(SUM(c.total_turns), 0) as groq_percent,
                    SUM(CASE WHEN c.outcome = 'escalated' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) as escalation_rate,
                    SUM(CASE WHEN c.outcome = 'completed' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) as completion_rate,
                    AVG(c.user_satisfaction) as avg_satisfaction
                FROM conversations c
                {where_clause}
            """, params)

            row = cursor.fetchone()

            metrics = AnalyticsMetrics(
                total_conversations=row["total_conversations"] or 0,
                total_turns=row["total_turns"] or 0,
                avg_turns_per_conversation=row["avg_turns"] or 0.0,
                avg_latency_ms=row["avg_latency"] or 0.0,
                groq_usage_percent=row["groq_percent"] or 0.0,
                escalation_rate=row["escalation_rate"] or 0.0,
                completion_rate=row["completion_rate"] or 0.0,
                avg_satisfaction=row["avg_satisfaction"] or 0.0
            )

            # Intent distribution
            cursor = conn.execute(f"""
                SELECT t.intent, COUNT(*) as count
                FROM conversation_turns t
                JOIN conversations c ON t.conversation_id = c.id
                {where_clause}
                GROUP BY t.intent
                ORDER BY count DESC
            """, params)

            metrics.intent_distribution = {
                row["intent"]: row["count"]
                for row in cursor.fetchall()
            }

            # Layer usage
            cursor = conn.execute(f"""
                SELECT t.layer_used, COUNT(*) as count
                FROM conversation_turns t
                JOIN conversations c ON t.conversation_id = c.id
                {where_clause}
                GROUP BY t.layer_used
                ORDER BY count DESC
            """, params)

            metrics.layer_usage = {
                row["layer_used"]: row["count"]
                for row in cursor.fetchall()
            }

            # Peak hours
            cursor = conn.execute(f"""
                SELECT strftime('%H', t.timestamp) as hour, COUNT(*) as count
                FROM conversation_turns t
                JOIN conversations c ON t.conversation_id = c.id
                {where_clause}
                GROUP BY hour
                ORDER BY hour
            """, params)

            metrics.peak_hours = {
                int(row["hour"]): row["count"]
                for row in cursor.fetchall()
            }

        return metrics

    def get_failed_queries(
        self,
        verticale_id: Optional[str] = None,
        days: int = 7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get queries where the system failed to provide a good response.

        Identifies queries that:
        - Triggered Groq fallback
        - Had low confidence
        - Were followed by repeat questions
        - Led to escalation

        Returns:
            List of failed queries for review
        """
        since = datetime.now() - timedelta(days=days)

        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    t.user_input,
                    t.intent,
                    t.intent_confidence,
                    t.response,
                    t.layer_used,
                    t.frustration_level,
                    c.outcome,
                    COUNT(*) as occurrence_count
                FROM conversation_turns t
                JOIN conversations c ON t.conversation_id = c.id
                WHERE c.started_at > ?
                    AND (
                        t.used_groq = TRUE
                        OR t.intent_confidence < 0.7
                        OR t.frustration_level >= 2
                        OR t.escalated = TRUE
                    )
                    AND (? IS NULL OR c.verticale_id = ?)
                GROUP BY t.user_input
                ORDER BY occurrence_count DESC, t.frustration_level DESC
                LIMIT ?
            """, (since.isoformat(), verticale_id, verticale_id, limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_conversation_history(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Get full conversation history for a session."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT *
                FROM conversation_turns
                WHERE conversation_id = ?
                ORDER BY turn_number
            """, (session_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_escalation_reasons(
        self,
        verticale_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, int]:
        """Get distribution of escalation reasons."""
        since = datetime.now() - timedelta(days=days)

        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    COALESCE(escalation_reason, 'unknown') as reason,
                    COUNT(*) as count
                FROM conversations
                WHERE started_at > ?
                    AND outcome = 'escalated'
                    AND (? IS NULL OR verticale_id = ?)
                GROUP BY reason
                ORDER BY count DESC
            """, (since.isoformat(), verticale_id, verticale_id))

            return {row["reason"]: row["count"] for row in cursor.fetchall()}

    # =========================================================================
    # Data Management
    # =========================================================================

    def cleanup_old_data(self):
        """Remove data older than retention period (GDPR compliance)."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)

        with self._get_connection() as conn:
            # Get conversation IDs to delete
            cursor = conn.execute("""
                SELECT id FROM conversations WHERE started_at < ?
            """, (cutoff.isoformat(),))

            old_ids = [row["id"] for row in cursor.fetchall()]

            if old_ids:
                placeholders = ",".join(["?"] * len(old_ids))

                # Delete turns first (foreign key constraint)
                conn.execute(f"""
                    DELETE FROM conversation_turns
                    WHERE conversation_id IN ({placeholders})
                """, old_ids)

                # Delete conversations
                conn.execute(f"""
                    DELETE FROM conversations
                    WHERE id IN ({placeholders})
                """, old_ids)

                conn.commit()

                return len(old_ids)

        return 0

    def _anonymize_if_needed(self, text: str) -> str:
        """Anonymize PII if enabled."""
        if not self.anonymize or not text:
            return text

        import re

        # Anonymize phone numbers
        text = re.sub(r'\b\d{10,11}\b', '[PHONE]', text)
        text = re.sub(r'\+\d{2}\s*\d{3}\s*\d{3}\s*\d{4}', '[PHONE]', text)

        # Anonymize email
        text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL]', text)

        return text

    def update_daily_metrics(self, verticale_id: str):
        """Update pre-computed daily metrics for dashboard."""
        today = datetime.now().date().isoformat()
        metrics = self.get_metrics(verticale_id, days=1)

        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO daily_metrics (
                    date, verticale_id, total_conversations, total_turns,
                    avg_latency_ms, groq_usage_percent, escalation_rate,
                    completion_rate, avg_satisfaction, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                today,
                verticale_id,
                metrics.total_conversations,
                metrics.total_turns,
                metrics.avg_latency_ms,
                metrics.groq_usage_percent,
                metrics.escalation_rate,
                metrics.completion_rate,
                metrics.avg_satisfaction,
                datetime.now().isoformat()
            ))
            conn.commit()

    def log_faq_effectiveness(
        self,
        faq_id: str,
        question_asked: str,
        answer_given: str,
        was_helpful: bool,
        follow_up_needed: bool
    ):
        """Log FAQ effectiveness for improvement tracking."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO faq_effectiveness (
                    id, faq_id, question_asked, answer_given,
                    was_helpful, follow_up_needed
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                faq_id,
                question_asked,
                answer_given,
                was_helpful,
                follow_up_needed
            ))
            conn.commit()

    # =========================================================================
    # VoIP Call Logging (Week 4)
    # =========================================================================

    def log_call_start(
        self,
        call_id: str,
        direction: str,
        remote_number: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Log start of VoIP call.

        Args:
            call_id: Unique call identifier
            direction: "inbound" or "outbound"
            remote_number: Remote phone number
            conversation_id: Optional linked conversation session

        Returns:
            Call ID
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO voip_calls (
                    id, conversation_id, direction, remote_number, start_time
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                call_id,
                conversation_id,
                direction,
                self._anonymize_if_needed(remote_number) if self.anonymize else remote_number,
                datetime.now().isoformat()
            ))
            conn.commit()
        return call_id

    def log_call_connected(self, call_id: str):
        """Log call connection time."""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE voip_calls SET connect_time = ? WHERE id = ?
            """, (datetime.now().isoformat(), call_id))
            conn.commit()

    def log_call_end(
        self,
        call_id: str,
        duration_seconds: int,
        outcome: str = "completed",
        sip_status_code: Optional[int] = None,
        rtp_packets_sent: int = 0,
        rtp_packets_received: int = 0,
        audio_quality_score: Optional[float] = None
    ):
        """
        Log end of VoIP call.

        Args:
            call_id: Call identifier
            duration_seconds: Call duration
            outcome: "completed", "missed", "rejected", "failed"
            sip_status_code: Final SIP status code
            rtp_packets_sent: Number of RTP packets sent
            rtp_packets_received: Number of RTP packets received
            audio_quality_score: Optional MOS score (1-5)
        """
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE voip_calls SET
                    end_time = ?,
                    duration_seconds = ?,
                    outcome = ?,
                    sip_status_code = ?,
                    rtp_packets_sent = ?,
                    rtp_packets_received = ?,
                    audio_quality_score = ?
                WHERE id = ?
            """, (
                datetime.now().isoformat(),
                duration_seconds,
                outcome,
                sip_status_code,
                rtp_packets_sent,
                rtp_packets_received,
                audio_quality_score,
                call_id
            ))
            conn.commit()

    def get_call_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get VoIP call metrics.

        Returns:
            Dictionary with call statistics
        """
        with self._get_connection() as conn:
            # Build date filter
            date_filter = ""
            params = []
            if start_date:
                date_filter = " WHERE start_time >= ?"
                params.append(start_date.isoformat())
            if end_date:
                if date_filter:
                    date_filter += " AND start_time <= ?"
                else:
                    date_filter = " WHERE start_time <= ?"
                params.append(end_date.isoformat())

            # Total calls
            row = conn.execute(f"""
                SELECT
                    COUNT(*) as total_calls,
                    SUM(CASE WHEN direction = 'inbound' THEN 1 ELSE 0 END) as inbound_calls,
                    SUM(CASE WHEN direction = 'outbound' THEN 1 ELSE 0 END) as outbound_calls,
                    SUM(CASE WHEN outcome = 'completed' THEN 1 ELSE 0 END) as completed_calls,
                    SUM(CASE WHEN outcome = 'missed' THEN 1 ELSE 0 END) as missed_calls,
                    AVG(duration_seconds) as avg_duration,
                    AVG(audio_quality_score) as avg_quality,
                    SUM(duration_seconds) as total_duration
                FROM voip_calls
                {date_filter}
            """, params).fetchone()

            return {
                "total_calls": row["total_calls"] or 0,
                "inbound_calls": row["inbound_calls"] or 0,
                "outbound_calls": row["outbound_calls"] or 0,
                "completed_calls": row["completed_calls"] or 0,
                "missed_calls": row["missed_calls"] or 0,
                "avg_duration_seconds": row["avg_duration"] or 0,
                "avg_quality_score": row["avg_quality"],
                "total_duration_seconds": row["total_duration"] or 0,
                "answer_rate": (
                    (row["completed_calls"] or 0) / row["total_calls"]
                    if row["total_calls"] else 0
                )
            }


# Global logger instance
_default_logger: Optional[ConversationLogger] = None


def get_logger(db_path: Optional[str] = None) -> ConversationLogger:
    """Get or create default ConversationLogger."""
    global _default_logger
    if _default_logger is None:
        _default_logger = ConversationLogger(db_path=db_path)
    return _default_logger
