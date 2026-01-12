"""
Analytics & Logging Tests - Week 3 Day 5-6

Tests for ConversationLogger, SQLite schema, and metrics queries.
"""

import os
import pytest
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analytics import (
    ConversationLogger,
    ConversationOutcome,
    ConversationTurn,
    ConversationSession,
    AnalyticsMetrics,
    get_logger,
)


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def temp_db():
    """Create temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def logger(temp_db):
    """Fresh ConversationLogger for each test."""
    return ConversationLogger(db_path=temp_db)


@pytest.fixture
def logger_with_data(logger):
    """Logger with pre-populated test data."""
    # Create some sessions and turns
    for i in range(5):
        session_id = logger.start_session(
            verticale_id="salone_test",
            client_name=f"Client {i}"
        )

        # Add turns
        for j in range(3):
            logger.log_turn(
                session_id=session_id,
                user_input=f"Test input {j}",
                intent="prenotazione" if j == 0 else "info",
                response=f"Test response {j}",
                latency_ms=50.0 + j * 10,
                layer_used="L2_intent",
                used_groq=(j == 2),  # Last turn uses Groq
                frustration_level=j
            )

        # End session
        outcome = ConversationOutcome.COMPLETED if i < 3 else ConversationOutcome.ESCALATED
        logger.end_session(
            session_id=session_id,
            outcome=outcome,
            user_satisfaction=4 if outcome == ConversationOutcome.COMPLETED else 2
        )

    return logger


# ==============================================================================
# Test: Database Initialization
# ==============================================================================

class TestDatabaseInit:
    """Test database schema and initialization."""

    def test_creates_database_file(self, temp_db):
        """Test database file is created."""
        logger = ConversationLogger(db_path=temp_db)
        assert os.path.exists(temp_db)

    def test_creates_conversations_table(self, logger, temp_db):
        """Test conversations table exists."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_creates_turns_table(self, logger, temp_db):
        """Test conversation_turns table exists."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_turns'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_creates_indexes(self, logger, temp_db):
        """Test indexes are created."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        indexes = [row[0] for row in cursor.fetchall()]
        assert "idx_conversations_verticale" in indexes
        assert "idx_turns_conversation" in indexes
        conn.close()


# ==============================================================================
# Test: Session Management
# ==============================================================================

class TestSessionManagement:
    """Test conversation session lifecycle."""

    def test_start_session(self, logger):
        """Test starting a new session."""
        session_id = logger.start_session(
            verticale_id="salone_test",
            client_id="client_001",
            client_name="Mario Rossi"
        )

        assert session_id is not None
        assert len(session_id) > 0
        assert session_id in logger._active_sessions

    def test_end_session(self, logger):
        """Test ending a session."""
        session_id = logger.start_session(verticale_id="salone_test")

        logger.end_session(
            session_id=session_id,
            outcome=ConversationOutcome.COMPLETED,
            user_satisfaction=5
        )

        assert session_id not in logger._active_sessions

    def test_session_persisted_to_db(self, logger, temp_db):
        """Test session is written to database."""
        session_id = logger.start_session(verticale_id="salone_test")
        logger.end_session(session_id, ConversationOutcome.COMPLETED)

        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT * FROM conversations WHERE id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None

    def test_session_with_booking(self, logger):
        """Test session with booking created."""
        session_id = logger.start_session(verticale_id="salone_test")

        logger.end_session(
            session_id=session_id,
            outcome=ConversationOutcome.COMPLETED,
            booking_id="booking_123"
        )

        # Verify in DB
        with logger._get_connection() as conn:
            cursor = conn.execute(
                "SELECT booking_created, booking_id FROM conversations WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()

        assert row["booking_created"] == 1
        assert row["booking_id"] == "booking_123"


# ==============================================================================
# Test: Turn Logging
# ==============================================================================

class TestTurnLogging:
    """Test conversation turn logging."""

    def test_log_turn(self, logger):
        """Test logging a conversation turn."""
        session_id = logger.start_session(verticale_id="salone_test")

        turn_id = logger.log_turn(
            session_id=session_id,
            user_input="Vorrei prenotare un taglio",
            intent="prenotazione",
            response="Perfetto! Per quando?",
            latency_ms=45.5,
            layer_used="L2_intent"
        )

        assert turn_id is not None

    def test_turn_increments_session_stats(self, logger):
        """Test turn logging updates session statistics."""
        session_id = logger.start_session(verticale_id="salone_test")

        logger.log_turn(
            session_id=session_id,
            user_input="Test",
            intent="test",
            response="Response",
            latency_ms=50.0
        )

        session = logger._active_sessions[session_id]
        assert session.total_turns == 1
        assert session.total_latency_ms == 50.0

    def test_turn_tracks_groq_usage(self, logger):
        """Test Groq usage is tracked."""
        session_id = logger.start_session(verticale_id="salone_test")

        logger.log_turn(
            session_id=session_id,
            user_input="Test",
            intent="test",
            response="Response",
            latency_ms=500.0,
            used_groq=True
        )

        session = logger._active_sessions[session_id]
        assert session.groq_usage_count == 1

    def test_turn_persisted_to_db(self, logger, temp_db):
        """Test turn is written to database."""
        session_id = logger.start_session(verticale_id="salone_test")
        turn_id = logger.log_turn(
            session_id=session_id,
            user_input="Test input",
            intent="prenotazione",
            response="Test response",
            latency_ms=30.0
        )

        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM conversation_turns WHERE id = ?",
            (turn_id,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row["user_input"] == "Test input"
        assert row["intent"] == "prenotazione"

    def test_entities_stored_as_json(self, logger, temp_db):
        """Test entities are serialized as JSON."""
        session_id = logger.start_session(verticale_id="salone_test")
        logger.log_turn(
            session_id=session_id,
            user_input="Domani alle 15",
            intent="prenotazione",
            response="Confermo",
            latency_ms=20.0,
            entities={"date": "2024-01-15", "time": "15:00"}
        )

        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT entities_extracted FROM conversation_turns WHERE conversation_id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()

        import json
        entities = json.loads(row[0])
        assert entities["date"] == "2024-01-15"
        assert entities["time"] == "15:00"


# ==============================================================================
# Test: Analytics Metrics
# ==============================================================================

class TestAnalyticsMetrics:
    """Test analytics and metrics queries."""

    def test_get_metrics_empty(self, logger):
        """Test metrics on empty database."""
        metrics = logger.get_metrics(days=7)

        assert metrics.total_conversations == 0
        assert metrics.total_turns == 0

    def test_get_metrics_with_data(self, logger_with_data):
        """Test metrics with populated data."""
        metrics = logger_with_data.get_metrics(days=7)

        assert metrics.total_conversations == 5
        assert metrics.total_turns == 15  # 5 sessions * 3 turns

    def test_escalation_rate(self, logger_with_data):
        """Test escalation rate calculation."""
        metrics = logger_with_data.get_metrics(days=7)

        # 2 out of 5 were escalated = 40%
        assert abs(metrics.escalation_rate - 40.0) < 1.0

    def test_completion_rate(self, logger_with_data):
        """Test completion rate calculation."""
        metrics = logger_with_data.get_metrics(days=7)

        # 3 out of 5 were completed = 60%
        assert abs(metrics.completion_rate - 60.0) < 1.0

    def test_groq_usage_percent(self, logger_with_data):
        """Test Groq usage percentage."""
        metrics = logger_with_data.get_metrics(days=7)

        # 5 groq uses out of 15 turns = 33.3%
        assert abs(metrics.groq_usage_percent - 33.3) < 1.0

    def test_intent_distribution(self, logger_with_data):
        """Test intent distribution aggregation."""
        metrics = logger_with_data.get_metrics(days=7)

        assert "prenotazione" in metrics.intent_distribution
        assert "info" in metrics.intent_distribution
        assert metrics.intent_distribution["prenotazione"] == 5  # One per session

    def test_filter_by_verticale(self, logger):
        """Test filtering metrics by verticale."""
        # Create sessions for different verticali
        s1 = logger.start_session(verticale_id="salone")
        logger.log_turn(s1, "test", "test", "resp", 10.0)
        logger.end_session(s1, ConversationOutcome.COMPLETED)

        s2 = logger.start_session(verticale_id="palestra")
        logger.log_turn(s2, "test", "test", "resp", 10.0)
        logger.end_session(s2, ConversationOutcome.COMPLETED)

        metrics_salone = logger.get_metrics(verticale_id="salone", days=7)
        metrics_palestra = logger.get_metrics(verticale_id="palestra", days=7)
        metrics_all = logger.get_metrics(days=7)

        assert metrics_salone.total_conversations == 1
        assert metrics_palestra.total_conversations == 1
        assert metrics_all.total_conversations == 2


# ==============================================================================
# Test: Failed Queries Analysis
# ==============================================================================

class TestFailedQueries:
    """Test identification of failed/problematic queries."""

    def test_get_failed_queries_low_confidence(self, logger):
        """Test finding low confidence queries."""
        session_id = logger.start_session(verticale_id="salone_test")
        logger.log_turn(
            session_id=session_id,
            user_input="Quanto costa quella cosa li",
            intent="unknown",
            response="Non ho capito",
            latency_ms=100.0,
            intent_confidence=0.3  # Low confidence
        )
        logger.end_session(session_id, ConversationOutcome.ABANDONED)

        failed = logger.get_failed_queries(days=7)

        assert len(failed) > 0
        assert any("cosa" in q["user_input"] for q in failed)

    def test_get_failed_queries_escalated(self, logger):
        """Test finding queries that led to escalation."""
        session_id = logger.start_session(verticale_id="salone_test")
        logger.log_turn(
            session_id=session_id,
            user_input="Voglio un operatore!",
            intent="operatore",
            response="La passo a un operatore",
            latency_ms=20.0,
            escalated=True
        )
        logger.end_session(session_id, ConversationOutcome.ESCALATED)

        failed = logger.get_failed_queries(days=7)

        assert len(failed) > 0


# ==============================================================================
# Test: Data Retention & Privacy
# ==============================================================================

class TestDataRetention:
    """Test GDPR compliance features."""

    def test_cleanup_old_data(self, logger, temp_db):
        """Test data cleanup after retention period."""
        # Create old session (manually set old timestamp)
        session_id = logger.start_session(verticale_id="salone_test")
        logger.end_session(session_id, ConversationOutcome.COMPLETED)

        # Manually backdate the session
        conn = sqlite3.connect(temp_db)
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        conn.execute(
            "UPDATE conversations SET started_at = ? WHERE id = ?",
            (old_date, session_id)
        )
        conn.commit()
        conn.close()

        # Set short retention
        logger.retention_days = 30

        # Cleanup
        deleted = logger.cleanup_old_data()

        assert deleted == 1

        # Verify deleted
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM conversations WHERE id = ?",
            (session_id,)
        )
        assert cursor.fetchone()[0] == 0
        conn.close()

    def test_anonymization_phone(self, logger):
        """Test phone number anonymization."""
        logger.anonymize = True

        result = logger._anonymize_if_needed("Il mio numero è 3331234567")

        assert "3331234567" not in result
        assert "[PHONE]" in result

    def test_anonymization_email(self, logger):
        """Test email anonymization."""
        logger.anonymize = True

        result = logger._anonymize_if_needed("La mia email è mario@example.com")

        assert "mario@example.com" not in result
        assert "[EMAIL]" in result

    def test_no_anonymization_when_disabled(self, logger):
        """Test data is not anonymized when disabled."""
        logger.anonymize = False

        result = logger._anonymize_if_needed("Il mio numero è 3331234567")

        assert "3331234567" in result


# ==============================================================================
# Test: Conversation History
# ==============================================================================

class TestConversationHistory:
    """Test conversation history retrieval."""

    def test_get_conversation_history(self, logger):
        """Test retrieving full conversation history."""
        session_id = logger.start_session(verticale_id="salone_test")

        for i in range(5):
            logger.log_turn(
                session_id=session_id,
                user_input=f"Message {i}",
                intent="test",
                response=f"Response {i}",
                latency_ms=10.0
            )

        logger.end_session(session_id, ConversationOutcome.COMPLETED)

        history = logger.get_conversation_history(session_id)

        assert len(history) == 5
        assert history[0]["turn_number"] == 1
        assert history[4]["turn_number"] == 5


# ==============================================================================
# Test: Escalation Reasons
# ==============================================================================

class TestEscalationReasons:
    """Test escalation reason analysis."""

    def test_get_escalation_reasons(self, logger):
        """Test escalation reason distribution."""
        # Create escalated sessions with different reasons
        for reason in ["user_requested", "frustration", "user_requested"]:
            session_id = logger.start_session(verticale_id="salone_test")
            logger.log_turn(session_id, "test", "test", "resp", 10.0)
            logger.end_session(
                session_id,
                ConversationOutcome.ESCALATED,
                escalation_reason=reason
            )

        reasons = logger.get_escalation_reasons(days=7)

        assert "user_requested" in reasons
        assert reasons["user_requested"] == 2
        assert reasons["frustration"] == 1


# ==============================================================================
# Test: FAQ Effectiveness
# ==============================================================================

class TestFAQEffectiveness:
    """Test FAQ effectiveness tracking."""

    def test_log_faq_effectiveness(self, logger, temp_db):
        """Test logging FAQ effectiveness."""
        logger.log_faq_effectiveness(
            faq_id="faq_001",
            question_asked="Quanto costa?",
            answer_given="35 euro",
            was_helpful=True,
            follow_up_needed=False
        )

        conn = sqlite3.connect(temp_db)
        cursor = conn.execute("SELECT * FROM faq_effectiveness")
        row = cursor.fetchone()
        conn.close()

        assert row is not None


# ==============================================================================
# Test: Daily Metrics
# ==============================================================================

class TestDailyMetrics:
    """Test pre-computed daily metrics."""

    def test_update_daily_metrics(self, logger_with_data, temp_db):
        """Test daily metrics computation."""
        logger_with_data.update_daily_metrics("salone_test")

        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM daily_metrics")
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row["total_conversations"] > 0


# ==============================================================================
# Test: Global Instance
# ==============================================================================

class TestGlobalInstance:
    """Test global logger instance."""

    def test_get_logger_singleton(self, temp_db):
        """Test get_logger returns instance."""
        # Note: This will use default path, not temp_db
        # Just testing the function works
        logger = get_logger(temp_db)
        assert logger is not None


# ==============================================================================
# Test: Dataclasses
# ==============================================================================

class TestDataclasses:
    """Test dataclass structures."""

    def test_conversation_turn(self):
        """Test ConversationTurn dataclass."""
        turn = ConversationTurn(
            conversation_id="test",
            user_input="Hello",
            intent="cortesia",
            response="Buongiorno!"
        )

        assert turn.id is not None
        assert turn.conversation_id == "test"
        assert turn.turn_number == 0

    def test_conversation_session(self):
        """Test ConversationSession dataclass."""
        session = ConversationSession(
            verticale_id="salone",
            client_name="Mario"
        )

        assert session.id is not None
        assert session.outcome == ConversationOutcome.UNKNOWN
        assert session.started_at is not None

    def test_analytics_metrics(self):
        """Test AnalyticsMetrics dataclass."""
        metrics = AnalyticsMetrics(
            total_conversations=100,
            escalation_rate=5.5
        )

        assert metrics.total_conversations == 100
        assert metrics.avg_latency_ms == 0.0  # Default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
