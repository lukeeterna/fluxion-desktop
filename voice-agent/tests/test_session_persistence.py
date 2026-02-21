"""
Tests for SessionManager SQLite local persistence (T2).

Verifica:
- create_session() persiste subito in SQLite
- close_session() aggiorna SQLite con stato finale
- _recover_sessions() ripristina sessioni ACTIVE al restart
- load_session() legge da SQLite (senza HTTP Bridge)
- log_audit() scrive in SQLite locale
- persist_session() usa SQLite come primary (Bridge offline = non-fatal)
"""
import asyncio
import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from session_manager import (
    SessionManager, SessionChannel, SessionState,
    VoiceSession, SessionTurn
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Temporary SQLite db path for each test."""
    return str(tmp_path / "test_sessions.db")


@pytest.fixture
def manager(tmp_db):
    """SessionManager with isolated SQLite (no HTTP Bridge needed)."""
    return SessionManager(
        http_bridge_url="http://127.0.0.1:19999",  # porta inesistente
        db_path=tmp_db
    )


# ---------------------------------------------------------------------------
# Schema & Init
# ---------------------------------------------------------------------------

class TestInit:
    def test_creates_db_file(self, tmp_db):
        SessionManager(db_path=tmp_db)
        assert Path(tmp_db).exists()

    def test_creates_schema(self, tmp_db):
        SessionManager(db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        conn.close()
        assert "voice_sessions" in tables
        assert "voice_audit_log" in tables

    def test_idempotent_init(self, tmp_db):
        """Second init doesn't fail (IF NOT EXISTS)."""
        SessionManager(db_path=tmp_db)
        SessionManager(db_path=tmp_db)  # no exception


# ---------------------------------------------------------------------------
# create_session → immediate SQLite write
# ---------------------------------------------------------------------------

class TestCreateSession:
    def test_session_in_memory(self, manager):
        s = manager.create_session("salone", "Salone Test")
        assert manager.get_session(s.session_id) is not None

    def test_session_persisted_to_sqlite(self, manager, tmp_db):
        s = manager.create_session("salone", "Salone Test")
        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT * FROM voice_sessions WHERE session_id = ?", (s.session_id,)
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == s.session_id
        assert row[2] == "active"  # state column

    def test_session_state_is_active(self, manager):
        s = manager.create_session("palestra", "Gym")
        assert s.state == SessionState.ACTIVE


# ---------------------------------------------------------------------------
# add_turn → SQLite via persist_session
# ---------------------------------------------------------------------------

class TestAddTurn:
    def test_add_turn_increments_count(self, manager):
        s = manager.create_session("salone", "Salone")
        manager.add_turn(s.session_id, "Ciao", "greeting", "Buongiorno!", 40.0, "L1_exact")
        session = manager.get_session(s.session_id)
        assert session.total_turns == 1

    @pytest.mark.asyncio
    async def test_persist_after_turns(self, manager, tmp_db):
        s = manager.create_session("salone", "Salone")
        manager.add_turn(s.session_id, "Voglio un taglio", "booking", "Certo!", 80.0, "L2_pattern")
        await manager.persist_session(s.session_id)

        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT turns_json, total_turns FROM voice_sessions WHERE session_id = ?",
            (s.session_id,)
        ).fetchone()
        conn.close()

        assert row is not None
        turns = json.loads(row[0])
        assert len(turns) == 1
        assert turns[0]["user_input"] == "Voglio un taglio"
        assert row[1] == 1


# ---------------------------------------------------------------------------
# close_session → SQLite update
# ---------------------------------------------------------------------------

class TestCloseSession:
    def test_close_updates_state_sqlite(self, manager, tmp_db):
        s = manager.create_session("salone", "Salone")
        manager.close_session(s.session_id, "booking_created", booking_id="BK001")

        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT state, outcome, booking_id FROM voice_sessions WHERE session_id = ?",
            (s.session_id,)
        ).fetchone()
        conn.close()

        assert row[0] == "completed"
        assert row[1] == "booking_created"
        assert row[2] == "BK001"

    def test_close_escalated(self, manager, tmp_db):
        s = manager.create_session("medical", "Studio Medico")
        manager.close_session(s.session_id, "escalated", escalation_reason="cliente arrabbiato")

        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT state, escalation_reason FROM voice_sessions WHERE session_id = ?",
            (s.session_id,)
        ).fetchone()
        conn.close()

        assert row[0] == "escalated"
        assert row[1] == "cliente arrabbiato"

    def test_close_timeout(self, manager, tmp_db):
        s = manager.create_session("auto", "Officina")
        manager.close_session(s.session_id, "timeout")

        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT state FROM voice_sessions WHERE session_id = ?",
            (s.session_id,)
        ).fetchone()
        conn.close()

        assert row[0] == "timeout"


# ---------------------------------------------------------------------------
# _recover_sessions → restart simulation
# ---------------------------------------------------------------------------

class TestRecoverSessions:
    def test_active_sessions_recovered(self, tmp_db):
        # Sessione 1: crea e mantieni active
        manager1 = SessionManager(db_path=tmp_db)
        s = manager1.create_session("salone", "Salone Recovery Test")
        session_id = s.session_id

        # Simula restart: nuovo manager dallo stesso DB
        manager2 = SessionManager(db_path=tmp_db)
        recovered = manager2.get_session(session_id)

        assert recovered is not None
        assert recovered.session_id == session_id
        assert recovered.business_name == "Salone Recovery Test"
        assert recovered.state == SessionState.ACTIVE

    def test_completed_sessions_not_recovered(self, tmp_db):
        manager1 = SessionManager(db_path=tmp_db)
        s = manager1.create_session("salone", "Salone")
        manager1.close_session(s.session_id, "booking_created")

        manager2 = SessionManager(db_path=tmp_db)
        # Completed sessions non devono essere in memoria
        assert s.session_id not in manager2._sessions

    def test_expired_sessions_not_recovered(self, tmp_db):
        manager1 = SessionManager(db_path=tmp_db, session_timeout_minutes=30)
        s = manager1.create_session("salone", "Salone")

        # Forza scadenza direttamente in SQLite
        expired_time = (datetime.now() - timedelta(hours=1)).isoformat()
        conn = sqlite3.connect(tmp_db)
        conn.execute(
            "UPDATE voice_sessions SET expires_at = ? WHERE session_id = ?",
            (expired_time, s.session_id)
        )
        conn.commit()
        conn.close()

        manager2 = SessionManager(db_path=tmp_db)
        assert s.session_id not in manager2._sessions

    def test_multiple_sessions_recovered(self, tmp_db):
        manager1 = SessionManager(db_path=tmp_db)
        ids = []
        for i in range(3):
            s = manager1.create_session("salone", f"Salone {i}")
            ids.append(s.session_id)

        manager2 = SessionManager(db_path=tmp_db)
        for sid in ids:
            assert manager2.get_session(sid) is not None

    def test_turns_preserved_after_recovery(self, tmp_db):
        manager1 = SessionManager(db_path=tmp_db)
        s = manager1.create_session("salone", "Salone")
        manager1.add_turn(s.session_id, "Ciao", "greeting", "Buongiorno!", 30.0, "L1_exact")
        manager1.add_turn(s.session_id, "Taglio", "booking", "Quando?", 60.0, "L2_pattern")
        asyncio.get_event_loop().run_until_complete(manager1.persist_session(s.session_id))

        manager2 = SessionManager(db_path=tmp_db)
        recovered = manager2.get_session(s.session_id)
        assert recovered is not None
        assert recovered.total_turns == 2


# ---------------------------------------------------------------------------
# load_session → SQLite primary (Bridge offline)
# ---------------------------------------------------------------------------

class TestLoadSession:
    @pytest.mark.asyncio
    async def test_load_from_sqlite_no_bridge(self, manager, tmp_db):
        """Load deve funzionare anche con Bridge offline (porta inesistente)."""
        s = manager.create_session("salone", "Salone")
        session_id = s.session_id

        # Rimuovi dalla memoria
        del manager._sessions[session_id]

        # load_session deve trovarlo in SQLite
        loaded = await manager.load_session(session_id)
        assert loaded is not None
        assert loaded.session_id == session_id

    @pytest.mark.asyncio
    async def test_load_nonexistent_returns_none(self, manager):
        result = await manager.load_session("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_load_populates_memory_cache(self, manager):
        s = manager.create_session("salone", "Salone")
        sid = s.session_id
        del manager._sessions[sid]

        await manager.load_session(sid)
        assert sid in manager._sessions


# ---------------------------------------------------------------------------
# persist_session → Bridge offline is non-fatal
# ---------------------------------------------------------------------------

class TestPersistSession:
    @pytest.mark.asyncio
    async def test_persist_returns_true_without_bridge(self, manager):
        """Bridge porta 19999 inesistente — SQLite deve bastare."""
        s = manager.create_session("salone", "Salone")
        result = await manager.persist_session(s.session_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_persist_nonexistent_session(self, manager):
        result = await manager.persist_session("nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_persist_updates_context(self, manager, tmp_db):
        s = manager.create_session("salone", "Salone")
        manager.update_context(s.session_id, {"servizio": "taglio", "ora": "15:00"})
        await manager.persist_session(s.session_id)

        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT context_json FROM voice_sessions WHERE session_id = ?",
            (s.session_id,)
        ).fetchone()
        conn.close()

        ctx = json.loads(row[0])
        assert ctx["servizio"] == "taglio"
        assert ctx["ora"] == "15:00"


# ---------------------------------------------------------------------------
# log_audit → SQLite locale
# ---------------------------------------------------------------------------

class TestLogAudit:
    @pytest.mark.asyncio
    async def test_audit_written_to_sqlite(self, manager, tmp_db):
        s = manager.create_session("salone", "Salone")
        await manager.log_audit(s.session_id, "session_start", {"test": True})

        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT action, details_json FROM voice_audit_log WHERE session_id = ?",
            (s.session_id,)
        ).fetchone()
        conn.close()

        assert row is not None
        assert row[0] == "session_start"
        assert json.loads(row[1])["test"] is True

    @pytest.mark.asyncio
    async def test_audit_returns_true_without_bridge(self, manager):
        """Bridge offline non deve fallire l'audit."""
        s = manager.create_session("salone", "Salone")
        result = await manager.log_audit(s.session_id, "turn", {"intent": "greeting"})
        assert result is True

    @pytest.mark.asyncio
    async def test_audit_multiple_entries(self, manager, tmp_db):
        s = manager.create_session("salone", "Salone")
        await manager.log_audit(s.session_id, "session_start")
        await manager.log_audit(s.session_id, "turn")
        await manager.log_audit(s.session_id, "booking_created", {"booking_id": "BK001"})

        conn = sqlite3.connect(tmp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM voice_audit_log WHERE session_id = ?",
            (s.session_id,)
        ).fetchone()[0]
        conn.close()

        assert count == 3


# ---------------------------------------------------------------------------
# Greeting dinamico
# ---------------------------------------------------------------------------

class TestGreeting:
    def test_greeting_uses_business_name(self, manager):
        s = manager.create_session("salone", "Salone Bella Vita")
        greeting = manager.get_greeting(s.session_id)
        assert "Salone Bella Vita" in greeting
        assert "Sara" in greeting

    def test_greeting_unknown_session(self, manager):
        greeting = manager.get_greeting("nonexistent")
        assert greeting  # Fallback generico, non eccezione
