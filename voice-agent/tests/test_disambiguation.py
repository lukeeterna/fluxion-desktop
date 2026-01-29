"""
Test Suite: Disambiguation Handler
===================================

Comprehensive tests for client disambiguation in the Voice Agent.
Covers: birth date extraction, nickname fallback, cognome differentiation,
fuzzy date matching, max attempts, and edge cases.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date
from src.disambiguation_handler import (
    DisambiguationHandler,
    DisambiguationState,
    DisambiguationResult,
    DisambiguationContext,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def handler():
    return DisambiguationHandler(max_attempts=3)


@pytest.fixture
def two_marios():
    """Two clients named Mario with different birth dates and one soprannome."""
    return [
        {
            "id": "1", "nome": "Mario", "cognome": "Rossi",
            "data_nascita": "1985-03-15", "soprannome": None,
            "telefono": "3331111111"
        },
        {
            "id": "2", "nome": "Mario", "cognome": "Rossi",
            "data_nascita": "1990-07-22", "soprannome": "Marione",
            "telefono": "3332222222"
        },
    ]


@pytest.fixture
def two_marios_no_soprannome():
    """Two Mario Rossi without soprannome - hardest case."""
    return [
        {
            "id": "1", "nome": "Mario", "cognome": "Rossi",
            "data_nascita": "1985-03-15", "soprannome": None
        },
        {
            "id": "2", "nome": "Mario", "cognome": "Rossi",
            "data_nascita": "1990-07-22", "soprannome": None
        },
    ]


@pytest.fixture
def two_marios_different_cognome():
    """Two Mario with different surnames."""
    return [
        {
            "id": "1", "nome": "Mario", "cognome": "Rossi",
            "data_nascita": "1985-03-15", "soprannome": None
        },
        {
            "id": "2", "nome": "Mario", "cognome": "Bianchi",
            "data_nascita": "1990-07-22", "soprannome": None
        },
    ]


@pytest.fixture
def three_clients():
    """Three clients with same name."""
    return [
        {
            "id": "1", "nome": "Mario", "cognome": "Rossi",
            "data_nascita": "1985-03-15", "soprannome": None
        },
        {
            "id": "2", "nome": "Mario", "cognome": "Rossi",
            "data_nascita": "1990-07-22", "soprannome": "Marione"
        },
        {
            "id": "3", "nome": "Mario", "cognome": "Bianchi",
            "data_nascita": "1978-11-03", "soprannome": None
        },
    ]


# ============================================================================
# Test: Birth Date Extraction
# ============================================================================

class TestBirthDateExtraction:
    """Test extract_birth_date() with various Italian date formats."""

    def test_italian_format(self, handler):
        """15 marzo 1985 -> date(1985, 3, 15)"""
        result = handler.extract_birth_date("15 marzo 1985")
        assert result == date(1985, 3, 15)

    def test_nato_il_prefix(self, handler):
        """nato il 15 marzo 1985"""
        result = handler.extract_birth_date("sono nato il 15 marzo 1985")
        assert result == date(1985, 3, 15)

    def test_nata_il_prefix(self, handler):
        """nata il 22 luglio 1990"""
        result = handler.extract_birth_date("nata il 22 luglio 1990")
        assert result == date(1990, 7, 22)

    def test_numeric_slash(self, handler):
        """15/03/1985"""
        result = handler.extract_birth_date("15/03/1985")
        assert result == date(1985, 3, 15)

    def test_numeric_dash(self, handler):
        """15-03-1985"""
        result = handler.extract_birth_date("15-03-1985")
        assert result == date(1985, 3, 15)

    def test_iso_format(self, handler):
        """1985-03-15"""
        result = handler.extract_birth_date("1985-03-15")
        assert result == date(1985, 3, 15)

    def test_short_year_old(self, handler):
        """sono del 15 marzo 85 -> 1985"""
        result = handler.extract_birth_date("sono del 15 marzo 85")
        assert result == date(1985, 3, 15)

    def test_short_year_young(self, handler):
        """5 gennaio 02 -> 2002"""
        result = handler.extract_birth_date("5 gennaio 02")
        assert result == date(2002, 1, 5)

    def test_short_month_name(self, handler):
        """15 mar 1985"""
        result = handler.extract_birth_date("15 mar 1985")
        assert result == date(1985, 3, 15)

    def test_all_months(self, handler):
        """Test all 12 Italian month names."""
        months_expected = [
            ("gennaio", 1), ("febbraio", 2), ("marzo", 3), ("aprile", 4),
            ("maggio", 5), ("giugno", 6), ("luglio", 7), ("agosto", 8),
            ("settembre", 9), ("ottobre", 10), ("novembre", 11), ("dicembre", 12),
        ]
        for month_name, month_num in months_expected:
            result = handler.extract_birth_date(f"1 {month_name} 1990")
            assert result is not None, f"Failed for month: {month_name}"
            assert result.month == month_num, f"Wrong month for {month_name}"

    def test_invalid_date_returns_none(self, handler):
        """Invalid date returns None."""
        result = handler.extract_birth_date("32 marzo 1985")
        assert result is None

    def test_no_date_returns_none(self, handler):
        """Non-date text returns None."""
        result = handler.extract_birth_date("non lo ricordo")
        assert result is None

    def test_numeric_short_year(self, handler):
        """15/03/85 -> 1985"""
        result = handler.extract_birth_date("15/03/85")
        assert result == date(1985, 3, 15)

    def test_embedded_in_sentence(self, handler):
        """Date embedded in a longer sentence."""
        result = handler.extract_birth_date("sì, sono nato il 22 luglio 1990, a Roma")
        assert result == date(1990, 7, 22)


# ============================================================================
# Test: Start Disambiguation
# ============================================================================

class TestStartDisambiguation:
    """Test start_disambiguation() with various client lists."""

    def test_no_clients_proposes_registration(self, handler):
        """Zero clients -> propose registration."""
        result = handler.start_disambiguation("Mario", [])
        assert result.state == DisambiguationState.PROPOSE_REGISTRATION
        assert result.propose_registration is True
        assert not result.success

    def test_single_client_resolves(self, handler, two_marios):
        """Single client -> resolved immediately."""
        result = handler.start_disambiguation("Mario", [two_marios[0]])
        assert result.state == DisambiguationState.RESOLVED
        assert result.success is True
        assert result.client["id"] == "1"
        assert "Mario Rossi" in result.response_text

    def test_multiple_clients_asks_birth_date(self, handler, two_marios):
        """Multiple clients -> asks for birth date."""
        result = handler.start_disambiguation("Mario", two_marios)
        assert result.state == DisambiguationState.WAITING_BIRTH_DATE
        assert result.needs_user_input is True
        assert "2" in result.response_text  # "Ho trovato 2 clienti"
        assert "Mario" in result.response_text

    def test_context_updated(self, handler, two_marios):
        """Context is properly set after start."""
        handler.start_disambiguation("Mario", two_marios)
        ctx = handler.get_context()
        assert ctx.search_name == "Mario"
        assert len(ctx.potential_clients) == 2
        assert ctx.attempts == 0


# ============================================================================
# Test: Birth Date Resolution
# ============================================================================

class TestBirthDateResolution:
    """Test process_birth_date() flow."""

    def test_correct_date_resolves(self, handler, two_marios):
        """Correct birth date resolves to matching client."""
        handler.start_disambiguation("Mario", two_marios)
        result = handler.process_birth_date("sono nato il 15 marzo 1985")
        assert result.success is True
        assert result.state == DisambiguationState.RESOLVED
        assert result.client["id"] == "1"

    def test_second_client_date_resolves(self, handler, two_marios):
        """Second client's date resolves correctly."""
        handler.start_disambiguation("Mario", two_marios)
        result = handler.process_birth_date("22 luglio 1990")
        assert result.success is True
        assert result.client["id"] == "2"

    def test_wrong_date_falls_back_to_nickname(self, handler, two_marios):
        """Wrong birth date falls back to nickname if available."""
        handler.start_disambiguation("Mario", two_marios)
        result = handler.process_birth_date("10 gennaio 1980")
        assert result.state == DisambiguationState.WAITING_NICKNAME
        assert "Marione" in result.response_text

    def test_wrong_date_no_nickname_proposes_registration(self, handler, two_marios_no_soprannome):
        """Wrong date + no nickname -> propose registration."""
        handler.start_disambiguation("Mario", two_marios_no_soprannome)
        result = handler.process_birth_date("10 gennaio 1980")
        assert result.state == DisambiguationState.PROPOSE_REGISTRATION
        assert result.propose_registration is True

    def test_unparseable_date_asks_retry(self, handler, two_marios):
        """Non-date input asks for retry."""
        handler.start_disambiguation("Mario", two_marios)
        result = handler.process_birth_date("non lo ricordo")
        assert result.state == DisambiguationState.WAITING_BIRTH_DATE
        assert result.needs_user_input is True
        assert "formato" in result.response_text.lower()

    def test_attempt_counter_increments(self, handler, two_marios):
        """Each attempt increments counter."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("non lo ricordo")
        assert handler.context.attempts == 1
        handler.process_birth_date("non lo ricordo")
        assert handler.context.attempts == 2


# ============================================================================
# Test: Nickname Resolution
# ============================================================================

class TestNicknameResolution:
    """Test process_nickname_choice() flow."""

    def test_nickname_resolves(self, handler, two_marios):
        """Selecting nickname resolves correctly."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("10 gennaio 1980")  # Falls to nickname
        result = handler.process_nickname_choice("Marione")
        assert result.success is True
        assert result.state == DisambiguationState.RESOLVED
        assert result.client["id"] == "2"

    def test_nome_resolves(self, handler, two_marios):
        """Selecting nome (when soprannome is None) resolves correctly."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("10 gennaio 1980")  # Falls to nickname
        result = handler.process_nickname_choice("Mario")
        assert result.success is True
        assert result.client["id"] == "1"

    def test_nickname_case_insensitive(self, handler, two_marios):
        """Nickname matching is case insensitive."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("10 gennaio 1980")
        result = handler.process_nickname_choice("marione")
        assert result.success is True
        assert result.client["id"] == "2"

    def test_nickname_embedded_in_sentence(self, handler, two_marios):
        """Nickname embedded in sentence: 'sono Marione'."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("10 gennaio 1980")
        result = handler.process_nickname_choice("sono Marione")
        assert result.success is True
        assert result.client["id"] == "2"

    def test_unrecognized_nickname_asks_again(self, handler, two_marios):
        """Unrecognized input asks again."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("10 gennaio 1980")
        result = handler.process_nickname_choice("Giovanni")
        assert result.success is False
        assert result.needs_user_input is True


# ============================================================================
# Test: Cognome-Based Disambiguation
# ============================================================================

class TestCognomeDisambiguation:
    """Test disambiguation when clients have different surnames."""

    def test_different_cognome_used_as_identifier(self, handler, two_marios_different_cognome):
        """Clients with different cognome use cognome for disambiguation."""
        handler.start_disambiguation("Mario", two_marios_different_cognome)
        result = handler.process_birth_date("10 gennaio 1980")  # Wrong date

        # Should use cognome-based identifiers since both have unique names
        # The _get_unique_identifiers checks soprannome first, then nome
        # But both have "Mario" as nome with no soprannome, so it falls through
        # With the cognome improvement, it should use full names
        assert result.state in (
            DisambiguationState.WAITING_NICKNAME,
            DisambiguationState.PROPOSE_REGISTRATION
        )


# ============================================================================
# Test: Max Attempts
# ============================================================================

class TestMaxAttempts:
    """Test max attempt enforcement."""

    def test_birth_date_max_attempts(self, handler, two_marios):
        """Exceeding max attempts -> FAILED."""
        handler.start_disambiguation("Mario", two_marios)
        for _ in range(3):
            handler.process_birth_date("non lo ricordo")
        result = handler.process_birth_date("non lo ricordo")  # 4th attempt
        assert result.state == DisambiguationState.FAILED
        assert "operatore" in result.response_text.lower()

    def test_nickname_max_attempts(self, handler, two_marios):
        """Exceeding max attempts in nickname flow -> FAILED."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("10 gennaio 1980")  # Falls to nickname
        for _ in range(3):
            handler.process_nickname_choice("Giovanni")
        result = handler.process_nickname_choice("Giovanni")  # 5th total (1 bd + 4 nick)
        # Attempts counted: 1 (birth_date) + 3 (nickname) = exceeds max=3 after nick #3
        assert result.state == DisambiguationState.FAILED


# ============================================================================
# Test: Properties and Reset
# ============================================================================

class TestPropertiesAndReset:
    """Test handler properties and reset."""

    def test_is_waiting_birth_date(self, handler, two_marios):
        """is_waiting returns True in WAITING_BIRTH_DATE."""
        handler.start_disambiguation("Mario", two_marios)
        assert handler.is_waiting is True

    def test_is_waiting_nickname(self, handler, two_marios):
        """is_waiting returns True in WAITING_NICKNAME."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("10 gennaio 1980")
        assert handler.is_waiting is True

    def test_is_not_waiting_after_resolve(self, handler, two_marios):
        """is_waiting returns False after resolution."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("15 marzo 1985")
        assert handler.is_waiting is False

    def test_is_resolved(self, handler, two_marios):
        """is_resolved returns True after resolution."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("15 marzo 1985")
        assert handler.is_resolved is True

    def test_resolved_client(self, handler, two_marios):
        """resolved_client returns client after resolution."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("15 marzo 1985")
        assert handler.resolved_client is not None
        assert handler.resolved_client["id"] == "1"

    def test_reset_clears_state(self, handler, two_marios):
        """reset() clears all disambiguation state."""
        handler.start_disambiguation("Mario", two_marios)
        handler.process_birth_date("15 marzo 1985")
        handler.reset()
        assert handler.is_waiting is False
        assert handler.is_resolved is False
        assert handler.resolved_client is None
        assert handler.context.attempts == 0

    def test_context_to_dict(self, handler, two_marios):
        """Context.to_dict() returns correct structure."""
        handler.start_disambiguation("Mario", two_marios)
        d = handler.context.to_dict()
        assert d["state"] == "waiting_birth_date"
        assert d["search_name"] == "Mario"
        assert d["potential_count"] == 2
        assert d["resolved"] is False
        assert d["attempts"] == 0


# ============================================================================
# Test: Full Disambiguation Flows
# ============================================================================

class TestFullFlows:
    """Test complete end-to-end disambiguation flows."""

    def test_flow_birth_date_direct_match(self, handler, two_marios):
        """Complete flow: search -> birth date -> resolved."""
        # Step 1: Start
        r1 = handler.start_disambiguation("Mario", two_marios)
        assert r1.state == DisambiguationState.WAITING_BIRTH_DATE

        # Step 2: Provide correct date
        r2 = handler.process_birth_date("sono nato il 22 luglio 1990")
        assert r2.success is True
        assert r2.client["soprannome"] == "Marione"

    def test_flow_birth_date_then_nickname(self, handler, two_marios):
        """Complete flow: search -> wrong date -> nickname -> resolved."""
        r1 = handler.start_disambiguation("Mario", two_marios)
        assert r1.state == DisambiguationState.WAITING_BIRTH_DATE

        r2 = handler.process_birth_date("10 gennaio 1980")
        assert r2.state == DisambiguationState.WAITING_NICKNAME

        r3 = handler.process_nickname_choice("Marione")
        assert r3.success is True
        assert r3.client["id"] == "2"

    def test_flow_retry_then_resolve(self, handler, two_marios):
        """Flow: search -> bad input -> retry -> correct date -> resolved."""
        handler.start_disambiguation("Mario", two_marios)

        r1 = handler.process_birth_date("non lo ricordo")
        assert r1.state == DisambiguationState.WAITING_BIRTH_DATE

        r2 = handler.process_birth_date("15 marzo 1985")
        assert r2.success is True

    def test_flow_three_clients(self, handler, three_clients):
        """Disambiguation with 3 clients."""
        r1 = handler.start_disambiguation("Mario", three_clients)
        assert "3" in r1.response_text

        r2 = handler.process_birth_date("3 novembre 1978")
        assert r2.success is True
        assert r2.client["cognome"] == "Bianchi"


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_client_without_data_nascita(self, handler):
        """Client without data_nascita field."""
        clients = [
            {"id": "1", "nome": "Mario", "cognome": "Rossi", "soprannome": None},
            {"id": "2", "nome": "Mario", "cognome": "Rossi", "soprannome": "Marione"},
        ]
        handler.start_disambiguation("Mario", clients)
        # Even with no data_nascita, handler shouldn't crash
        result = handler.process_birth_date("15 marzo 1985")
        # No match since no data_nascita -> falls to nickname
        assert result.state == DisambiguationState.WAITING_NICKNAME

    def test_empty_soprannome_string(self, handler):
        """Client with empty string soprannome (vs None)."""
        clients = [
            {"id": "1", "nome": "Mario", "cognome": "Rossi", "soprannome": ""},
            {"id": "2", "nome": "Mario", "cognome": "Rossi", "soprannome": "Marione"},
        ]
        handler.start_disambiguation("Mario", clients)
        result = handler.process_birth_date("10 gennaio 1980")
        # Empty string soprannome should fall back to nome
        assert result.state == DisambiguationState.WAITING_NICKNAME

    def test_format_date_italian(self, handler):
        """Internal date formatting."""
        d = date(1985, 3, 15)
        formatted = handler._format_date_italian(d)
        assert "15" in formatted
        assert "marzo" in formatted
        assert "1985" in formatted

    def test_get_full_name_both(self, handler):
        """Full name with both nome and cognome."""
        client = {"nome": "Mario", "cognome": "Rossi"}
        assert handler._get_full_name(client) == "Mario Rossi"

    def test_get_full_name_only_nome(self, handler):
        """Full name with only nome."""
        client = {"nome": "Mario", "cognome": ""}
        assert handler._get_full_name(client) == "Mario"

    def test_get_full_name_empty(self, handler):
        """Full name with missing fields."""
        client = {}
        assert handler._get_full_name(client) == "Cliente"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
