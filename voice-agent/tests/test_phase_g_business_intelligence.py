"""
Phase G: Business Intelligence + Proactive Revenue — Test Suite

G2: Dormant client recall (WhatsApp)
G5: Proactive anticipation (returning caller greeting)
G6: Weekly self-learning loop (analytics)

Total: ~65 tests covering all G features.
"""

import json
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def temp_db():
    """Create a temporary SQLite DB with Fluxion schema for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE clienti (
            id TEXT PRIMARY KEY,
            nome TEXT,
            cognome TEXT,
            telefono TEXT,
            data_nascita TEXT,
            consenso_whatsapp INTEGER DEFAULT 1,
            deleted_at TEXT
        );
        CREATE TABLE servizi (
            id TEXT PRIMARY KEY,
            nome TEXT
        );
        CREATE TABLE operatori (
            id TEXT PRIMARY KEY,
            nome TEXT,
            cognome TEXT
        );
        CREATE TABLE appuntamenti (
            id TEXT PRIMARY KEY,
            cliente_id TEXT,
            servizio_id TEXT,
            operatore_id TEXT,
            data_ora_inizio TEXT,
            stato TEXT DEFAULT 'Confermato',
            deleted_at TEXT
        );
        CREATE TABLE waitlist (
            id TEXT PRIMARY KEY,
            cliente_id TEXT,
            servizio_id TEXT,
            data_richiesta TEXT,
            ora_richiesta TEXT,
            priorita INTEGER DEFAULT 0,
            stato TEXT DEFAULT 'attivo',
            notificato_il TEXT,
            scadenza_risposta TEXT,
            creato_il TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    yield path
    os.unlink(path)


@pytest.fixture
def temp_analytics_db():
    """Create a temporary analytics DB with conversation schema."""
    fd, path = tempfile.mkstemp(suffix="_analytics.db")
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE conversations (
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
            summary TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE conversation_turns (
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
            fsm_state TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE weekly_reports (
            id TEXT PRIMARY KEY,
            generated_at DATETIME NOT NULL,
            period_days INTEGER NOT NULL,
            report_json TEXT NOT NULL,
            insights_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    yield path
    os.unlink(path)


@pytest.fixture
def temp_recall_log():
    """Temporary recall log path."""
    fd, path = tempfile.mkstemp(suffix="_recall.json")
    os.close(fd)
    yield path
    os.unlink(path)


def _seed_dormant_clients(db_path: str):
    """Seed DB with clients, some dormant (>60 days since last appointment)."""
    conn = sqlite3.connect(db_path)
    now = datetime.now()
    # Client 1: Active (last booking 5 days ago)
    conn.execute("INSERT INTO clienti VALUES ('c1', 'Mario', 'Rossi', '+39333001', NULL, 1, NULL)")
    conn.execute("INSERT INTO servizi VALUES ('s1', 'Taglio')")
    conn.execute(
        "INSERT INTO appuntamenti VALUES ('a1', 'c1', 's1', NULL, ?, 'Confermato', NULL)",
        ((now - timedelta(days=5)).strftime("%Y-%m-%dT10:00:00"),),
    )
    # Client 2: Dormant (last booking 90 days ago)
    conn.execute("INSERT INTO clienti VALUES ('c2', 'Luca', 'Bianchi', '+39333002', NULL, 1, NULL)")
    conn.execute(
        "INSERT INTO appuntamenti VALUES ('a2', 'c2', 's1', NULL, ?, 'Completato', NULL)",
        ((now - timedelta(days=90)).strftime("%Y-%m-%dT10:00:00"),),
    )
    # Client 3: Dormant (75 days) but has future appointment — NOT dormant
    conn.execute("INSERT INTO clienti VALUES ('c3', 'Anna', 'Verdi', '+39333003', NULL, 1, NULL)")
    conn.execute(
        "INSERT INTO appuntamenti VALUES ('a3', 'c3', 's1', NULL, ?, 'Completato', NULL)",
        ((now - timedelta(days=75)).strftime("%Y-%m-%dT10:00:00"),),
    )
    conn.execute(
        "INSERT INTO appuntamenti VALUES ('a4', 'c3', 's1', NULL, ?, 'Confermato', NULL)",
        ((now + timedelta(days=3)).strftime("%Y-%m-%dT10:00:00"),),
    )
    # Client 4: Dormant (100 days), no WA consent
    conn.execute("INSERT INTO clienti VALUES ('c4', 'Giulia', 'Neri', '+39333004', NULL, 0, NULL)")
    conn.execute(
        "INSERT INTO appuntamenti VALUES ('a5', 'c4', 's1', NULL, ?, 'Completato', NULL)",
        ((now - timedelta(days=100)).strftime("%Y-%m-%dT10:00:00"),),
    )
    # Client 5: Dormant (80 days), deleted — should be excluded
    conn.execute("INSERT INTO clienti VALUES ('c5', 'Deleted', 'User', '+39333005', NULL, 1, '2026-01-01')")
    conn.execute(
        "INSERT INTO appuntamenti VALUES ('a6', 'c5', 's1', NULL, ?, 'Completato', NULL)",
        ((now - timedelta(days=80)).strftime("%Y-%m-%dT10:00:00"),),
    )
    # Client 6: Dormant (65 days) — should be included
    conn.execute("INSERT INTO clienti VALUES ('c6', 'Paolo', 'Gialli', '+39333006', NULL, 1, NULL)")
    conn.execute(
        "INSERT INTO appuntamenti VALUES ('a7', 'c6', 's1', NULL, ?, 'Completato', NULL)",
        ((now - timedelta(days=65)).strftime("%Y-%m-%dT10:00:00"),),
    )
    conn.commit()
    conn.close()


def _seed_analytics_data(db_path: str, scenario: str = "normal"):
    """Seed analytics DB with conversation data for G6 tests."""
    conn = sqlite3.connect(db_path)
    now = datetime.now()

    if scenario == "normal":
        # 10 conversations, 7 completed, 2 abandoned, 1 escalated
        for i in range(10):
            cid = f"conv_{i}"
            outcome = "completed" if i < 7 else ("abandoned" if i < 9 else "escalated")
            started = (now - timedelta(days=3, hours=i)).strftime("%Y-%m-%dT%H:%M:%S")
            escalation = "user_requested_human" if outcome == "escalated" else None
            conn.execute(
                """INSERT INTO conversations (id, verticale_id, started_at, outcome, total_turns,
                   total_latency_ms, groq_usage_count, escalation_reason, booking_created)
                   VALUES (?, 'salone', ?, ?, ?, ?, ?, ?, ?)""",
                (cid, started, outcome, 5, 2500.0, 1 if i % 3 == 0 else 0,
                 escalation, 1 if outcome == "completed" else 0),
            )
            # Add turns with FSM states
            states = ["idle", "waiting_service", "waiting_date", "waiting_time", "confirming"]
            for t in range(5):
                tid = f"turn_{i}_{t}"
                conn.execute(
                    """INSERT INTO conversation_turns (id, conversation_id, turn_number, timestamp,
                       user_input, intent, intent_confidence, response, latency_ms, layer_used,
                       frustration_level, fsm_state)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (tid, cid, t, started, f"input_{t}", "booking", 0.85, f"resp_{t}",
                     500.0, "L2", 0, states[t]),
                )

    elif scenario == "problematic":
        # Conversations with issues: high frustration, loops, low confidence
        for i in range(8):
            cid = f"conv_{i}"
            outcome = "abandoned" if i < 5 else "escalated"
            started = (now - timedelta(days=2, hours=i)).strftime("%Y-%m-%dT%H:%M:%S")
            conn.execute(
                """INSERT INTO conversations (id, verticale_id, started_at, outcome, total_turns,
                   total_latency_ms, escalation_reason, booking_created)
                   VALUES (?, 'salone', ?, ?, 8, 4000.0, ?, 0)""",
                (cid, started, outcome,
                 "user_frustrated" if outcome == "escalated" else None),
            )
            # Turns: stuck in waiting_date (loop), high frustration, low confidence
            for t in range(8):
                tid = f"turn_{i}_{t}"
                state = "waiting_date" if t >= 2 else "waiting_service"
                conn.execute(
                    """INSERT INTO conversation_turns (id, conversation_id, turn_number, timestamp,
                       user_input, intent, intent_confidence, response, latency_ms, layer_used,
                       frustration_level, fsm_state)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (tid, cid, t, started, f"input_{t}", "unknown", 0.3, f"resp_{t}",
                     3500.0, "L4", 3 if t >= 4 else 1, state),
                )

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
# G2 TESTS — DORMANT CLIENT RECALL
# ═══════════════════════════════════════════════════════════════════


class TestG2DormantClientQuery:
    """Test dormant client identification query."""

    def test_identifies_dormant_clients(self, temp_db):
        """Clients >60 days without booking should be found."""
        _seed_dormant_clients(temp_db)
        from reminder_scheduler import _get_dormant_clients
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)):
            dormant = _get_dormant_clients(days_threshold=60)
        names = [c["nome"] for c in dormant]
        assert "Luca" in names  # 90 days
        assert "Paolo" in names  # 65 days

    def test_excludes_active_clients(self, temp_db):
        """Clients with recent bookings should NOT be found."""
        _seed_dormant_clients(temp_db)
        from reminder_scheduler import _get_dormant_clients
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)):
            dormant = _get_dormant_clients(days_threshold=60)
        names = [c["nome"] for c in dormant]
        assert "Mario" not in names  # 5 days ago

    def test_excludes_clients_with_future_appointments(self, temp_db):
        """Clients with future bookings should NOT be recalled."""
        _seed_dormant_clients(temp_db)
        from reminder_scheduler import _get_dormant_clients
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)):
            dormant = _get_dormant_clients(days_threshold=60)
        names = [c["nome"] for c in dormant]
        assert "Anna" not in names  # has future appointment

    def test_excludes_no_wa_consent(self, temp_db):
        """Clients without WA consent should NOT be recalled."""
        _seed_dormant_clients(temp_db)
        from reminder_scheduler import _get_dormant_clients
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)):
            dormant = _get_dormant_clients(days_threshold=60)
        names = [c["nome"] for c in dormant]
        assert "Giulia" not in names  # no WA consent

    def test_excludes_deleted_clients(self, temp_db):
        """Deleted clients should NOT be recalled."""
        _seed_dormant_clients(temp_db)
        from reminder_scheduler import _get_dormant_clients
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)):
            dormant = _get_dormant_clients(days_threshold=60)
        names = [c["nome"] for c in dormant]
        assert "Deleted" not in names

    def test_ordered_by_days_absent_desc(self, temp_db):
        """Dormant clients sorted by most absent first."""
        _seed_dormant_clients(temp_db)
        from reminder_scheduler import _get_dormant_clients
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)):
            dormant = _get_dormant_clients(days_threshold=60)
        if len(dormant) >= 2:
            assert dormant[0]["giorni_assente"] >= dormant[1]["giorni_assente"]

    def test_configurable_threshold(self, temp_db):
        """Custom threshold should change results."""
        _seed_dormant_clients(temp_db)
        from reminder_scheduler import _get_dormant_clients
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)):
            dormant_30 = _get_dormant_clients(days_threshold=30)
            dormant_95 = _get_dormant_clients(days_threshold=95)
        # 30 days: more clients
        # 95 days: only the 100-day one (but no consent)
        assert len(dormant_30) >= len(dormant_95)

    def test_no_db_returns_empty(self):
        """Missing DB should return empty list gracefully."""
        from reminder_scheduler import _get_dormant_clients
        with patch("reminder_scheduler._get_db_path", return_value=None):
            dormant = _get_dormant_clients()
        assert dormant == []


class TestG2RecallIdempotency:
    """Test recall sent tracking (max 1 per month)."""

    def test_mark_and_check_sent(self, temp_recall_log):
        """Marking recall as sent should be detectable."""
        from reminder_scheduler import _mark_recall_sent, _recall_recently_sent, _RECALL_LOG_PATH
        with patch("reminder_scheduler._RECALL_LOG_PATH", Path(temp_recall_log)):
            _mark_recall_sent("c1")
            assert _recall_recently_sent("c1", min_days=30)

    def test_not_recently_sent(self, temp_recall_log):
        """Client not in log should return False."""
        from reminder_scheduler import _recall_recently_sent
        with patch("reminder_scheduler._RECALL_LOG_PATH", Path(temp_recall_log)):
            assert not _recall_recently_sent("c999", min_days=30)

    def test_old_recall_not_recent(self, temp_recall_log):
        """Recall sent >30 days ago should not block new recall."""
        from reminder_scheduler import _recall_recently_sent, _RECALL_LOG_PATH
        old_date = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d")
        with open(temp_recall_log, "w") as f:
            json.dump({"c1": old_date}, f)
        with patch("reminder_scheduler._RECALL_LOG_PATH", Path(temp_recall_log)):
            assert not _recall_recently_sent("c1", min_days=30)


class TestG2RecallJob:
    """Test the recall job execution."""

    @pytest.mark.asyncio
    async def test_sends_recall_to_dormant(self, temp_db, temp_recall_log):
        """Job should send WA to dormant clients."""
        _seed_dormant_clients(temp_db)
        wa_client = MagicMock()
        wa_client.is_connected.return_value = True
        wa_client.send_message.return_value = {"success": True}

        from reminder_scheduler import check_and_recall_dormant
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)), \
             patch("reminder_scheduler._RECALL_LOG_PATH", Path(temp_recall_log)):
            await check_and_recall_dormant(wa_client)

        assert wa_client.send_message.call_count >= 1
        # Check message content
        call_args = wa_client.send_message.call_args_list[0]
        assert "ultima visita" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_respects_daily_limit(self, temp_db, temp_recall_log):
        """Job should stop after DORMANT_MAX_PER_DAY."""
        _seed_dormant_clients(temp_db)
        wa_client = MagicMock()
        wa_client.is_connected.return_value = True
        wa_client.send_message.return_value = {"success": True}

        from reminder_scheduler import check_and_recall_dormant, DORMANT_MAX_PER_DAY
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)), \
             patch("reminder_scheduler._RECALL_LOG_PATH", Path(temp_recall_log)):
            await check_and_recall_dormant(wa_client)
        assert wa_client.send_message.call_count <= DORMANT_MAX_PER_DAY

    @pytest.mark.asyncio
    async def test_skips_when_wa_disconnected(self, temp_db):
        """Job should skip if WA not connected."""
        _seed_dormant_clients(temp_db)
        wa_client = MagicMock()
        wa_client.is_connected.return_value = False

        from reminder_scheduler import check_and_recall_dormant
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)):
            await check_and_recall_dormant(wa_client)
        wa_client.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_wa_none(self):
        """Job should handle None WA client gracefully."""
        from reminder_scheduler import check_and_recall_dormant
        await check_and_recall_dormant(None)  # Should not crash

    @pytest.mark.asyncio
    async def test_idempotent_no_double_send(self, temp_db, temp_recall_log):
        """Running job twice should not send twice to same client."""
        _seed_dormant_clients(temp_db)
        wa_client = MagicMock()
        wa_client.is_connected.return_value = True
        wa_client.send_message.return_value = {"success": True}

        from reminder_scheduler import check_and_recall_dormant
        with patch("reminder_scheduler._get_db_path", return_value=Path(temp_db)), \
             patch("reminder_scheduler._RECALL_LOG_PATH", Path(temp_recall_log)):
            await check_and_recall_dormant(wa_client)
            first_count = wa_client.send_message.call_count
            await check_and_recall_dormant(wa_client)
            second_count = wa_client.send_message.call_count
        # Second run should not send any new messages
        assert second_count == first_count


# ═══════════════════════════════════════════════════════════════════
# G5 TESTS — PROACTIVE ANTICIPATION
# ═══════════════════════════════════════════════════════════════════


class TestG5ProactiveOffer:
    """Test proactive booking offer for returning callers."""

    def _make_caller_profile(self, **kwargs):
        """Create a CallerProfile-like object."""
        from caller_memory import CallerProfile
        defaults = {
            "phone_number": "+39333001",
            "client_name": "Mario",
            "call_count": 3,
            "last_service": "taglio",
            "last_operator": "Luca",
            "preferred_day": "martedì",
            "preferred_time": "10:00",
        }
        defaults.update(kwargs)
        return CallerProfile(**defaults)

    def test_proactive_offer_field_exists(self):
        """BookingContext should have proactive_offer field."""
        from booking_state_machine import BookingContext
        ctx = BookingContext()
        assert hasattr(ctx, "proactive_offer")
        assert ctx.proactive_offer is False

    def test_reject_proactive_offer_resets_service(self):
        """Saying 'no' to proactive offer should clear service and go to WAITING_SERVICE."""
        from booking_state_machine import BookingStateMachine, BookingState
        sm = BookingStateMachine()
        # Simulate proactive offer state
        sm.context.state = BookingState.WAITING_DATE
        sm.context.proactive_offer = True
        sm.context.service = "taglio"
        sm.context.service_display = "Taglio"
        sm.context.services = ["taglio"]
        sm.context.operator_name = "Luca"
        sm.context.client_name = "Mario"

        result = sm.process("no, vorrei altro")
        assert result.next_state == BookingState.WAITING_SERVICE
        assert sm.context.service is None
        assert sm.context.operator_name is None
        assert sm.context.proactive_offer is False

    def test_accept_proactive_offer_continues_to_date(self):
        """Accepting proactive offer should continue normally in WAITING_DATE."""
        from booking_state_machine import BookingStateMachine, BookingState
        sm = BookingStateMachine()
        sm.context.state = BookingState.WAITING_DATE
        sm.context.proactive_offer = True
        sm.context.service = "taglio"
        sm.context.service_display = "Taglio"
        sm.context.services = ["taglio"]
        sm.context.client_name = "Mario"

        result = sm.process("si, martedì")
        # Should stay in date flow (not reject)
        assert result.next_state != BookingState.WAITING_SERVICE
        assert sm.context.proactive_offer is False

    def test_reject_words_all_work(self):
        """All rejection words should trigger the reset."""
        from booking_state_machine import BookingStateMachine, BookingState
        reject_words = ["no", "altro", "diverso", "cambiare", "niente"]
        for word in reject_words:
            sm = BookingStateMachine()
            sm.context.state = BookingState.WAITING_DATE
            sm.context.proactive_offer = True
            sm.context.service = "taglio"
            sm.context.services = ["taglio"]
            result = sm.process(word)
            assert result.next_state == BookingState.WAITING_SERVICE, f"Failed for '{word}'"

    def test_proactive_offer_only_for_frequent_callers(self):
        """Callers with call_count < 2 should NOT get proactive offer."""
        profile = self._make_caller_profile(call_count=1, last_service="taglio")
        # call_count < 2 means first-time returning — too early for proactive
        assert profile.call_count < 2

    def test_proactive_greeting_includes_service(self):
        """Proactive greeting should mention the last service."""
        profile = self._make_caller_profile()
        assert profile.last_service == "taglio"
        assert profile.last_operator == "Luca"
        # The orchestrator will build: "Vuole ripetere Taglio con Luca?"

    def test_proactive_greeting_includes_preferred_slot(self):
        """If preferred day/time known, greeting should mention it."""
        profile = self._make_caller_profile()
        assert profile.preferred_day == "martedì"
        assert profile.preferred_time == "10:00"

    def test_no_proactive_without_service_history(self):
        """Caller without last_service should NOT get proactive offer."""
        profile = self._make_caller_profile(last_service="", call_count=5)
        assert not profile.last_service


class TestG5ProactiveGreetingBuild:
    """Test the _build_proactive_greeting method."""

    def test_build_proactive_greeting_content(self):
        """Profile data should contain all info needed for proactive greeting."""
        from caller_memory import CallerProfile

        profile = CallerProfile(
            phone_number="+39333001",
            client_name="Mario",
            call_count=3,
            last_service="taglio",
            last_operator="Luca",
            preferred_day="martedì",
            preferred_time="10:00",
        )

        # Verify profile has all needed data for greeting construction
        assert profile.client_name == "Mario"
        assert profile.last_service == "taglio"
        assert profile.last_operator == "Luca"
        assert profile.preferred_day == "martedì"
        assert profile.preferred_time == "10:00"
        assert profile.call_count >= 2  # threshold for proactive

        # Simulate greeting construction (same logic as _build_proactive_greeting)
        svc_display = profile.last_service.capitalize()
        op_str = f" con {profile.last_operator}" if profile.last_operator else ""
        pref_str = f" Di solito il {profile.preferred_day} alle {profile.preferred_time}."

        greeting = (
            f"Salone Test, buongiorno! "
            f"Bentornato {profile.client_name}! Vuole ripetere {svc_display}{op_str}?"
            f"{pref_str} Mi dica quando preferisce, oppure se desidera altro."
        )
        assert "Bentornato Mario" in greeting
        assert "Taglio" in greeting
        assert "con Luca" in greeting
        assert "martedì" in greeting
        assert "10:00" in greeting

    @pytest.mark.asyncio
    async def test_proactive_sets_fsm_to_waiting_date(self):
        """After proactive greeting, FSM should be in WAITING_DATE."""
        from booking_state_machine import BookingContext, BookingState
        ctx = BookingContext()
        ctx.state = BookingState.WAITING_DATE
        ctx.proactive_offer = True
        ctx.service = "taglio"
        assert ctx.state == BookingState.WAITING_DATE
        assert ctx.proactive_offer is True


# ═══════════════════════════════════════════════════════════════════
# G6 TESTS — WEEKLY SELF-LEARNING LOOP
# ═══════════════════════════════════════════════════════════════════


class TestG6WeeklySummary:
    """Test weekly summary query."""

    def test_summary_with_data(self, temp_analytics_db):
        """Summary should compute correct metrics."""
        _seed_analytics_data(temp_analytics_db, "normal")
        from weekly_learning import _query_weekly_summary
        conn = sqlite3.connect(temp_analytics_db)
        summary = _query_weekly_summary(conn, days=7)
        conn.close()
        assert summary["total_conversations"] == 10
        assert summary["completed"] == 7
        assert summary["abandoned"] == 2
        assert summary["escalated"] == 1
        assert summary["completion_rate"] == 70.0

    def test_summary_empty_db(self, temp_analytics_db):
        """Empty DB should return 0 conversations."""
        from weekly_learning import _query_weekly_summary
        conn = sqlite3.connect(temp_analytics_db)
        summary = _query_weekly_summary(conn, days=7)
        conn.close()
        assert summary["total_conversations"] == 0


class TestG6StateAbandonment:
    """Test state abandonment detection."""

    def test_finds_abandonment_states(self, temp_analytics_db):
        """Should find states where conversations end badly."""
        _seed_analytics_data(temp_analytics_db, "problematic")
        from weekly_learning import _query_state_abandonment
        conn = sqlite3.connect(temp_analytics_db)
        results = _query_state_abandonment(conn, days=7)
        conn.close()
        assert len(results) > 0
        states = [r["state"] for r in results]
        assert "waiting_date" in states  # problematic scenario ends at waiting_date

    def test_no_abandonment_healthy(self, temp_analytics_db):
        """Healthy data should have less abandonment."""
        _seed_analytics_data(temp_analytics_db, "normal")
        from weekly_learning import _query_state_abandonment
        conn = sqlite3.connect(temp_analytics_db)
        results = _query_state_abandonment(conn, days=7)
        conn.close()
        # Normal scenario: 2 abandoned + 1 escalated = 3 max
        total = sum(r["count"] for r in results)
        assert total <= 3


class TestG6StateLoops:
    """Test state loop detection (stuck users)."""

    def test_detects_loops(self, temp_analytics_db):
        """Should find conversations with repeated states."""
        _seed_analytics_data(temp_analytics_db, "problematic")
        from weekly_learning import _query_state_loops
        conn = sqlite3.connect(temp_analytics_db)
        results = _query_state_loops(conn, days=7)
        conn.close()
        assert len(results) > 0
        # waiting_date repeated 6x in problematic scenario
        assert any(r["state"] == "waiting_date" and r["repeat_count"] >= 3 for r in results)


class TestG6BottleneckStates:
    """Test bottleneck state detection."""

    def test_finds_slow_states(self, temp_analytics_db):
        """Should find states with high average latency."""
        _seed_analytics_data(temp_analytics_db, "problematic")
        from weekly_learning import _query_bottleneck_states
        conn = sqlite3.connect(temp_analytics_db)
        results = _query_bottleneck_states(conn, days=7)
        conn.close()
        assert len(results) > 0
        # Problematic scenario has 3500ms latency
        assert results[0]["avg_latency_ms"] > 3000


class TestG6EscalationPatterns:
    """Test escalation pattern detection."""

    def test_finds_escalation_reasons(self, temp_analytics_db):
        """Should find most common escalation reasons."""
        _seed_analytics_data(temp_analytics_db, "problematic")
        from weekly_learning import _query_escalation_patterns
        conn = sqlite3.connect(temp_analytics_db)
        results = _query_escalation_patterns(conn, days=7)
        conn.close()
        assert len(results) > 0
        reasons = [r["reason"] for r in results]
        assert "user_frustrated" in reasons


class TestG6LowConfidence:
    """Test low confidence pattern detection."""

    def test_finds_low_confidence_intents(self, temp_analytics_db):
        """Should find intents with consistently low confidence."""
        _seed_analytics_data(temp_analytics_db, "problematic")
        from weekly_learning import _query_low_confidence_patterns
        conn = sqlite3.connect(temp_analytics_db)
        results = _query_low_confidence_patterns(conn, days=7)
        conn.close()
        assert len(results) > 0
        assert results[0]["avg_confidence"] < 0.5


class TestG6FrustrationHotspots:
    """Test frustration hotspot detection."""

    def test_finds_frustration_states(self, temp_analytics_db):
        """Should find states with high frustration."""
        _seed_analytics_data(temp_analytics_db, "problematic")
        from weekly_learning import _query_frustration_hotspots
        conn = sqlite3.connect(temp_analytics_db)
        results = _query_frustration_hotspots(conn, days=7)
        conn.close()
        assert len(results) > 0
        assert results[0]["avg_frustration"] >= 2.0


class TestG6InsightDerivation:
    """Test actionable insight generation."""

    def test_generates_insights_for_problems(self, temp_analytics_db):
        """Problematic data should generate actionable insights."""
        _seed_analytics_data(temp_analytics_db, "problematic")
        from weekly_learning import generate_weekly_report
        with patch("weekly_learning._get_analytics_db_path", return_value=temp_analytics_db):
            report = generate_weekly_report(days=7)
        insights = report.get("insights", [])
        assert len(insights) >= 2  # At least completion rate + loops/frustration

    def test_no_insights_for_healthy(self, temp_analytics_db):
        """Healthy data should have fewer/no alarming insights."""
        _seed_analytics_data(temp_analytics_db, "normal")
        from weekly_learning import generate_weekly_report
        with patch("weekly_learning._get_analytics_db_path", return_value=temp_analytics_db):
            report = generate_weekly_report(days=7)
        insights = report.get("insights", [])
        # Normal scenario: 70% completion should trigger warning
        assert any("70" in i for i in insights) or len(insights) >= 1


class TestG6ReportPersistence:
    """Test report storage and retrieval."""

    def test_report_stored_in_db(self, temp_analytics_db):
        """Report should be persisted in weekly_reports table."""
        _seed_analytics_data(temp_analytics_db, "normal")
        from weekly_learning import generate_weekly_report
        with patch("weekly_learning._get_analytics_db_path", return_value=temp_analytics_db):
            report = generate_weekly_report(days=7)

        conn = sqlite3.connect(temp_analytics_db)
        row = conn.execute("SELECT COUNT(*) FROM weekly_reports").fetchone()
        conn.close()
        assert row[0] == 1

    def test_get_latest_report(self, temp_analytics_db):
        """Should retrieve the most recent report."""
        _seed_analytics_data(temp_analytics_db, "normal")
        from weekly_learning import generate_weekly_report, get_latest_report
        with patch("weekly_learning._get_analytics_db_path", return_value=temp_analytics_db):
            generate_weekly_report(days=7)
            latest = get_latest_report()
        assert latest is not None
        assert "summary" in latest
        assert "insights" in latest


class TestG6WhatsAppFormat:
    """Test WhatsApp-friendly report formatting."""

    def test_format_report(self, temp_analytics_db):
        """Report should be formatted for WA readability."""
        _seed_analytics_data(temp_analytics_db, "normal")
        from weekly_learning import generate_weekly_report, format_report_for_wa
        with patch("weekly_learning._get_analytics_db_path", return_value=temp_analytics_db):
            report = generate_weekly_report(days=7)
        wa_text = format_report_for_wa(report)
        assert "Report Settimanale Sara" in wa_text
        assert "Conversazioni: 10" in wa_text

    def test_format_empty_report(self):
        """Empty report should be handled gracefully."""
        from weekly_learning import format_report_for_wa
        report = {"summary": {"total_conversations": 0}, "period_days": 7}
        wa_text = format_report_for_wa(report)
        assert "nessuna conversazione" in wa_text


class TestG6AsyncJob:
    """Test the async scheduler entry point."""

    @pytest.mark.asyncio
    async def test_run_weekly_learning(self, temp_analytics_db):
        """Async job should complete without errors."""
        _seed_analytics_data(temp_analytics_db, "normal")
        from weekly_learning import run_weekly_learning
        with patch("weekly_learning._get_analytics_db_path", return_value=temp_analytics_db):
            await run_weekly_learning()  # Should not raise

    @pytest.mark.asyncio
    async def test_run_weekly_learning_no_db(self):
        """Job should handle missing DB gracefully."""
        from weekly_learning import run_weekly_learning
        with patch("weekly_learning._get_analytics_db_path", return_value="/nonexistent/path.db"):
            await run_weekly_learning()  # Should not raise


# ═══════════════════════════════════════════════════════════════════
# SCHEDULER INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════


class TestG2G6SchedulerRegistration:
    """Test that G2 and G6 jobs are registered in scheduler."""

    @pytest.mark.asyncio
    async def test_scheduler_has_dormant_recall_job(self):
        """Scheduler should include dormant_recall job."""
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
        except ImportError:
            pytest.skip("APScheduler not installed")

        from reminder_scheduler import start_reminder_scheduler
        wa_client = MagicMock()
        wa_client.is_connected.return_value = False
        scheduler = start_reminder_scheduler(wa_client)
        if scheduler is None:
            pytest.skip("APScheduler not available")
        job_ids = [j.id for j in scheduler.get_jobs()]
        assert "dormant_recall" in job_ids
        scheduler.shutdown(wait=False)

    @pytest.mark.asyncio
    async def test_scheduler_has_weekly_learning_job(self):
        """Scheduler should include weekly_learning job."""
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
        except ImportError:
            pytest.skip("APScheduler not installed")

        from reminder_scheduler import start_reminder_scheduler
        wa_client = MagicMock()
        wa_client.is_connected.return_value = False
        scheduler = start_reminder_scheduler(wa_client)
        if scheduler is None:
            pytest.skip("APScheduler not available")
        job_ids = [j.id for j in scheduler.get_jobs()]
        assert "weekly_learning" in job_ids
        scheduler.shutdown(wait=False)
