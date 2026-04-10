"""
Tests for A5 — Auto-summary post-call via Groq LLM.

Verifies:
- Summary generation from conversation turns
- Summary stored in ConversationSession and VoiceSession
- Summary persisted to DB (both analytics and session_manager)
- Empty conversations produce a minimal summary
- Groq failure gracefully falls back to a template summary
"""

import asyncio
import pytest
import sys
import os
import types
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# Helpers: standalone _generate_call_summary extracted for unit testing
# (avoids importing orchestrator.py which requires groq SDK)
# ---------------------------------------------------------------------------

async def _generate_call_summary_standalone(groq_client, turns, outcome="completed"):
    """
    Standalone version of FluxionOrchestrator._generate_call_summary for testing.
    Mirrors the real implementation exactly.
    """
    n_turns = len(turns)

    if n_turns == 0:
        return f"Chiamata di 0 turni, esito: {outcome}"

    transcript_lines = []
    for t in turns:
        u = getattr(t, 'user_input', '') or ''
        r = getattr(t, 'response', '') or ''
        if u:
            transcript_lines.append(f"Cliente: {u}")
        if r:
            transcript_lines.append(f"Sara: {r}")
    transcript = "\n".join(transcript_lines)
    if len(transcript) > 800:
        transcript = transcript[:800] + "..."

    if not getattr(groq_client, 'client', None):
        return f"Chiamata di {n_turns} turni, esito: {outcome}"

    try:
        summary = await groq_client.generate_response(
            messages=[{"role": "user", "content": transcript}],
            system_prompt=(
                "Riassumi questa conversazione telefonica in 1-2 frasi. "
                "Solo i fatti: chi ha chiamato, cosa voleva, esito. "
                "Rispondi SOLO con il riassunto, massimo 200 caratteri."
            ),
            temperature=0.3,
            max_tokens=120,
        )
        if len(summary) > 200:
            summary = summary[:197] + "..."
        return summary
    except Exception:
        return f"Chiamata di {n_turns} turni, esito: {outcome}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_groq_client():
    """GroqClient mock that returns a canned summary."""
    client = MagicMock()
    client.client = MagicMock()  # sync Groq client exists (not None)

    async def fake_generate(messages, system_prompt=None, temperature=0.3,
                            max_tokens=120):
        return "Cliente Marco Rossi ha prenotato taglio per giovedi ore 15."

    client.generate_response = AsyncMock(side_effect=fake_generate)
    return client


@pytest.fixture
def mock_groq_client_failing():
    """GroqClient mock that raises on generate_response."""
    client = MagicMock()
    client.client = MagicMock()
    client.generate_response = AsyncMock(
        side_effect=RuntimeError("LLM timeout (>3s): Groq non risponde")
    )
    return client


@dataclass
class FakeTurn:
    user_input: str = ""
    response: str = ""


@pytest.fixture
def sample_turns():
    """Minimal turn-like objects with user_input and response."""
    return [
        FakeTurn(user_input="Buongiorno, vorrei prenotare un taglio",
                 response="Certamente! A che nome?"),
        FakeTurn(user_input="Marco Rossi",
                 response="Per quale giorno desidera, signor Rossi?"),
        FakeTurn(user_input="Giovedi alle 15",
                 response="Perfetto, taglio per giovedi 10 aprile ore 15. Confermo?"),
        FakeTurn(user_input="Si confermo",
                 response="Prenotazione confermata! Arrivederci."),
    ]


# ---------------------------------------------------------------------------
# Test _generate_call_summary logic (isolated, no orchestrator import)
# ---------------------------------------------------------------------------

class TestGenerateCallSummary:
    """Test the summary generation logic in isolation."""

    @pytest.mark.asyncio
    async def test_summary_from_turns(self, mock_groq_client, sample_turns):
        """Summary is generated from conversation turns via Groq."""
        summary = await _generate_call_summary_standalone(
            mock_groq_client, sample_turns, outcome="completed"
        )

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert len(summary) <= 200
        mock_groq_client.generate_response.assert_called_once()
        call_args = mock_groq_client.generate_response.call_args
        assert "Riassumi" in call_args.kwargs.get("system_prompt", "")

    @pytest.mark.asyncio
    async def test_summary_truncated_to_200_chars(self, sample_turns):
        """Summary longer than 200 chars is truncated."""
        long_response = "A" * 300
        groq = MagicMock()
        groq.client = MagicMock()
        groq.generate_response = AsyncMock(return_value=long_response)

        summary = await _generate_call_summary_standalone(
            groq, sample_turns, outcome="completed"
        )
        assert len(summary) <= 200

    @pytest.mark.asyncio
    async def test_empty_conversation_template_summary(self, mock_groq_client):
        """Empty turn list produces template summary without calling Groq."""
        summary = await _generate_call_summary_standalone(
            mock_groq_client, [], outcome="completed"
        )

        assert isinstance(summary, str)
        assert "0 turni" in summary
        mock_groq_client.generate_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_groq_failure_fallback_template(self, mock_groq_client_failing, sample_turns):
        """On Groq failure, returns template summary."""
        summary = await _generate_call_summary_standalone(
            mock_groq_client_failing, sample_turns, outcome="completed"
        )

        assert isinstance(summary, str)
        assert "4 turni" in summary
        assert "completed" in summary

    @pytest.mark.asyncio
    async def test_groq_failure_no_client(self, sample_turns):
        """When groq.client is None (offline mode), returns template."""
        groq = MagicMock()
        groq.client = None  # offline mode

        summary = await _generate_call_summary_standalone(
            groq, sample_turns, outcome="completed"
        )

        assert isinstance(summary, str)
        assert "4 turni" in summary

    @pytest.mark.asyncio
    async def test_transcript_truncated_for_long_conversations(self, mock_groq_client):
        """Very long conversations have their transcript truncated to 800 chars."""
        long_turns = [
            FakeTurn(user_input="A" * 200, response="B" * 200)
            for _ in range(10)
        ]
        summary = await _generate_call_summary_standalone(
            mock_groq_client, long_turns, outcome="completed"
        )
        assert isinstance(summary, str)
        # Verify the transcript passed to Groq was truncated
        call_args = mock_groq_client.generate_response.call_args
        transcript = call_args.kwargs["messages"][0]["content"]
        assert len(transcript) <= 803 + 3  # 800 + "..."

    @pytest.mark.asyncio
    async def test_outcome_in_template(self, mock_groq_client_failing, sample_turns):
        """Template summary includes the outcome string."""
        summary = await _generate_call_summary_standalone(
            mock_groq_client_failing, sample_turns, outcome="escalated"
        )
        assert "escalated" in summary


# ---------------------------------------------------------------------------
# Test analytics.py summary field
# ---------------------------------------------------------------------------

class TestAnalyticsSummary:
    """Test summary field in ConversationSession and DB persistence."""

    def test_conversation_session_has_summary_field(self):
        """ConversationSession dataclass has a summary field."""
        from analytics import ConversationSession
        session = ConversationSession()
        assert hasattr(session, 'summary')
        assert session.summary == ""

    def test_summary_stored_in_session(self):
        """Summary can be set on ConversationSession."""
        from analytics import ConversationSession
        session = ConversationSession()
        session.summary = "Cliente ha prenotato taglio."
        assert session.summary == "Cliente ha prenotato taglio."

    def test_summary_saved_to_db_on_end_session(self):
        """Summary is persisted to conversations table when session ends."""
        from analytics import ConversationLogger, ConversationOutcome

        logger = ConversationLogger(db_path=":memory:")
        sid = logger.start_session("salone_test")

        # Set summary on the active session
        session = logger._active_sessions[sid]
        session.summary = "Prenotazione taglio confermata per Marco Rossi."

        logger.end_session(sid, outcome=ConversationOutcome.COMPLETED)

        # Verify in DB
        with logger._get_connection() as conn:
            row = conn.execute(
                "SELECT summary FROM conversations WHERE id = ?", (sid,)
            ).fetchone()
            assert row is not None
            assert row[0] == "Prenotazione taglio confermata per Marco Rossi."

    def test_summary_default_empty_in_db(self):
        """Conversations without summary have empty string in DB."""
        from analytics import ConversationLogger, ConversationOutcome

        logger = ConversationLogger(db_path=":memory:")
        sid = logger.start_session("salone_test")
        logger.end_session(sid, outcome=ConversationOutcome.COMPLETED)

        with logger._get_connection() as conn:
            row = conn.execute(
                "SELECT summary FROM conversations WHERE id = ?", (sid,)
            ).fetchone()
            assert row is not None
            assert row[0] == ""


# ---------------------------------------------------------------------------
# Test session_manager.py summary field
# ---------------------------------------------------------------------------

class TestSessionManagerSummary:
    """Test summary field in VoiceSession and session_manager DB."""

    def test_voice_session_has_summary_field(self):
        """VoiceSession dataclass has a summary field."""
        from session_manager import VoiceSession, SessionChannel, SessionState
        from datetime import datetime, timedelta

        now = datetime.now()
        session = VoiceSession(
            session_id="test-123",
            channel=SessionChannel.VOICE,
            state=SessionState.ACTIVE,
            verticale_id="salone",
            business_name="Test",
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            expires_at=(now + timedelta(minutes=30)).isoformat(),
        )
        assert hasattr(session, 'summary')
        assert session.summary == ""

    def test_summary_in_to_dict(self):
        """VoiceSession.to_dict() includes summary."""
        from session_manager import VoiceSession, SessionChannel, SessionState
        from datetime import datetime, timedelta

        now = datetime.now()
        session = VoiceSession(
            session_id="test-123",
            channel=SessionChannel.VOICE,
            state=SessionState.ACTIVE,
            verticale_id="salone",
            business_name="Test",
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            expires_at=(now + timedelta(minutes=30)).isoformat(),
            summary="Test summary",
        )
        d = session.to_dict()
        assert d["summary"] == "Test summary"

    def test_summary_persisted_to_sqlite(self, tmp_path):
        """Summary is saved in voice_sessions table via _persist_to_sqlite."""
        from session_manager import SessionManager

        db_file = str(tmp_path / "test_sessions.db")
        mgr = SessionManager(
            db_path=db_file,
            http_bridge_url="http://127.0.0.1:19999",
        )
        session = mgr.create_session(
            verticale_id="salone",
            business_name="Test Salone",
        )
        session.summary = "Chiamata per info orari."
        mgr._persist_to_sqlite(session)

        # Read back from DB
        with mgr._get_db_conn() as conn:
            row = conn.execute(
                "SELECT summary FROM voice_sessions WHERE session_id = ?",
                (session.session_id,)
            ).fetchone()
            assert row is not None
            assert row[0] == "Chiamata per info orari."

    def test_summary_default_empty_in_sqlite(self, tmp_path):
        """Session without summary has empty string in DB."""
        from session_manager import SessionManager

        db_file = str(tmp_path / "test_sessions2.db")
        mgr = SessionManager(
            db_path=db_file,
            http_bridge_url="http://127.0.0.1:19999",
        )
        session = mgr.create_session(
            verticale_id="salone",
            business_name="Test Salone",
        )
        # Don't set summary — should default to ""

        with mgr._get_db_conn() as conn:
            row = conn.execute(
                "SELECT summary FROM voice_sessions WHERE session_id = ?",
                (session.session_id,)
            ).fetchone()
            assert row is not None
            assert row[0] == ""
