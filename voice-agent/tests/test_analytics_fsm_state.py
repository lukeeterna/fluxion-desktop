"""
Tests for A4: FSM state per turn in analytics (S143 GAP-D3).

Validates that ConversationTurn has fsm_state field and that
it is correctly persisted to and read from the SQLite database.
"""

import os
import sqlite3
import tempfile
import pytest

from src.analytics import ConversationTurn, ConversationLogger


# =============================================================================
# Test ConversationTurn Dataclass
# =============================================================================

class TestConversationTurnFSMState:
    """Test that ConversationTurn has the fsm_state field."""

    def test_fsm_state_field_exists(self):
        """ConversationTurn must have fsm_state field."""
        turn = ConversationTurn()
        assert hasattr(turn, "fsm_state")

    def test_fsm_state_default_empty(self):
        """fsm_state should default to empty string."""
        turn = ConversationTurn()
        assert turn.fsm_state == ""

    def test_fsm_state_set_on_creation(self):
        """fsm_state can be set during creation."""
        turn = ConversationTurn(fsm_state="waiting_date")
        assert turn.fsm_state == "waiting_date"

    def test_fsm_state_assignable(self):
        """fsm_state can be assigned after creation."""
        turn = ConversationTurn()
        turn.fsm_state = "confirming"
        assert turn.fsm_state == "confirming"


# =============================================================================
# Test DB Schema
# =============================================================================

class TestAnalyticsDBSchema:
    """Test that the conversation_turns table has fsm_state column."""

    @pytest.fixture
    def logger(self):
        """Create analytics logger with in-memory database."""
        return ConversationLogger(db_path=":memory:")

    def test_fsm_state_column_exists(self, logger):
        """conversation_turns table must have fsm_state column."""
        with logger._get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(conversation_turns)")
            columns = [row[1] for row in cursor.fetchall()]
        assert "fsm_state" in columns

    def test_fsm_state_column_default(self, logger):
        """fsm_state column should have DEFAULT ''."""
        with logger._get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(conversation_turns)")
            for row in cursor.fetchall():
                if row[1] == "fsm_state":
                    assert row[4] == "''"  # DEFAULT value
                    break
            else:
                pytest.fail("fsm_state column not found")


# =============================================================================
# Test Persistence
# =============================================================================

class TestFSMStatePersistence:
    """Test that fsm_state is correctly saved and read from DB."""

    @pytest.fixture
    def logger(self):
        """Create analytics logger with in-memory database."""
        return ConversationLogger(db_path=":memory:")

    def test_log_turn_saves_fsm_state(self, logger):
        """log_turn should persist fsm_state to DB."""
        session_id = logger.start_session("salone")
        turn_id = logger.log_turn(
            session_id,
            user_input="Vorrei un appuntamento",
            intent="PRENOTAZIONE",
            response="Certo! Per quale servizio?",
            latency_ms=50.0,
            layer_used="L2_fsm",
            fsm_state="waiting_service"
        )

        with logger._get_connection() as conn:
            row = conn.execute(
                "SELECT fsm_state FROM conversation_turns WHERE id = ?",
                (turn_id,)
            ).fetchone()

        assert row is not None
        assert row["fsm_state"] == "waiting_service"

    def test_log_turn_empty_fsm_state(self, logger):
        """log_turn without fsm_state should store empty string."""
        session_id = logger.start_session("salone")
        turn_id = logger.log_turn(
            session_id,
            user_input="Buongiorno",
            intent="CORTESIA",
            response="Buongiorno!",
            latency_ms=5.0,
            layer_used="L1_intent"
        )

        with logger._get_connection() as conn:
            row = conn.execute(
                "SELECT fsm_state FROM conversation_turns WHERE id = ?",
                (turn_id,)
            ).fetchone()

        assert row is not None
        assert row["fsm_state"] == ""

    def test_log_turn_object_with_fsm_state(self, logger):
        """log_turn with ConversationTurn object should preserve fsm_state in memory.

        Note: The ConversationTurn object path stores turns in-memory via
        session.add_turn(), not directly to SQLite. This is by design.
        """
        session_id = logger.start_session("salone")
        turn = ConversationTurn(
            conversation_id=session_id,
            user_input="Domani alle 15",
            intent="PRENOTAZIONE",
            response="Confermo domani alle 15?",
            latency_ms=30.0,
            layer_used="L2_fsm",
            fsm_state="confirming"
        )
        turn_id = logger.log_turn(turn)

        # Verify the turn object retains fsm_state
        assert turn.fsm_state == "confirming"
        assert turn_id == turn.id

    def test_multiple_turns_different_fsm_states(self, logger):
        """Multiple turns should each preserve their own fsm_state."""
        session_id = logger.start_session("salone")

        states = ["idle", "waiting_service", "waiting_date", "confirming"]
        turn_ids = []
        for i, state in enumerate(states):
            tid = logger.log_turn(
                session_id,
                user_input=f"turn {i}",
                intent="PRENOTAZIONE",
                response=f"response {i}",
                latency_ms=10.0,
                layer_used="L2_fsm",
                fsm_state=state
            )
            turn_ids.append(tid)

        with logger._get_connection() as conn:
            for tid, expected_state in zip(turn_ids, states):
                row = conn.execute(
                    "SELECT fsm_state FROM conversation_turns WHERE id = ?",
                    (tid,)
                ).fetchone()
                assert row["fsm_state"] == expected_state

    def test_query_turns_by_fsm_state(self, logger):
        """Should be able to query turns filtered by fsm_state."""
        session_id = logger.start_session("salone")

        # Log 3 turns: 2 in waiting_service, 1 in confirming
        for _ in range(2):
            logger.log_turn(
                session_id,
                user_input="test",
                intent="PRENOTAZIONE",
                response="test",
                latency_ms=10.0,
                layer_used="L2_fsm",
                fsm_state="waiting_service"
            )
        logger.log_turn(
            session_id,
            user_input="test",
            intent="PRENOTAZIONE",
            response="test",
            latency_ms=10.0,
            layer_used="L2_fsm",
            fsm_state="confirming"
        )

        with logger._get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM conversation_turns WHERE fsm_state = ?",
                ("waiting_service",)
            ).fetchone()[0]

        assert count == 2


# =============================================================================
# Test Migration (ALTER TABLE on existing DB)
# =============================================================================

class TestFSMStateMigration:
    """Test that existing DBs without fsm_state get the column added."""

    def test_migration_adds_column_to_existing_db(self):
        """Opening a DB created without fsm_state should add the column."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            # Create a DB with the OLD schema (no fsm_state)
            conn = sqlite3.connect(db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    verticale_id TEXT,
                    started_at DATETIME NOT NULL,
                    ended_at DATETIME,
                    outcome TEXT DEFAULT 'unknown',
                    total_turns INTEGER DEFAULT 0,
                    total_latency_ms REAL DEFAULT 0.0,
                    groq_usage_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
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
                    entities_extracted TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            conn.commit()
            conn.close()

            # Now open with ConversationLogger — should add fsm_state
            logger = ConversationLogger(db_path=db_path)

            # Verify column exists
            conn2 = sqlite3.connect(db_path)
            cursor = conn2.execute("PRAGMA table_info(conversation_turns)")
            columns = [row[1] for row in cursor.fetchall()]
            conn2.close()

            assert "fsm_state" in columns
        finally:
            os.unlink(db_path)
