"""
Tests for Phase C: Memory + Personalization

C1: CallerMemory SQLite module
C2: Phone number extraction from SIP URI
C3: Personalized greeting for returning callers
C4: Preferred slot suggestion
"""

import os
import sys
import pytest
import tempfile
import sqlite3
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

# Add voice-agent/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from caller_memory import CallerMemory, CallerProfile, get_caller_memory


# =============================================================================
# C1: CallerMemory SQLite Module
# =============================================================================


class TestCallerMemoryInit:
    """Test CallerMemory initialization and schema."""

    def test_creates_db_file(self, tmp_path):
        db_path = str(tmp_path / "test_caller.db")
        mem = CallerMemory(db_path=db_path)
        assert os.path.exists(db_path)

    def test_schema_has_caller_profiles(self, tmp_path):
        db_path = str(tmp_path / "test_caller.db")
        mem = CallerMemory(db_path=db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='caller_profiles'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_schema_has_caller_bookings(self, tmp_path):
        db_path = str(tmp_path / "test_caller.db")
        mem = CallerMemory(db_path=db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='caller_bookings'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_idempotent_init(self, tmp_path):
        """Schema creation is idempotent — multiple CallerMemory instances don't crash."""
        db_path = str(tmp_path / "test_caller.db")
        CallerMemory(db_path=db_path)
        CallerMemory(db_path=db_path)  # No error


class TestCallerProfile:
    """Test CallerProfile dataclass."""

    def test_new_profile_not_returning(self):
        p = CallerProfile(phone_number="+390972536918")
        assert not p.is_returning

    def test_profile_with_calls_is_returning(self):
        p = CallerProfile(phone_number="+390972536918", call_count=1)
        assert p.is_returning

    def test_to_dict(self):
        p = CallerProfile(phone_number="+39333", client_name="Mario", call_count=3)
        d = p.to_dict()
        assert d["phone_number"] == "+39333"
        assert d["client_name"] == "Mario"
        assert d["call_count"] == 3


class TestCallerMemoryLookup:
    """Test lookup by phone number."""

    def test_lookup_unknown_returns_none(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        assert mem.lookup("+390000000000") is None

    def test_lookup_empty_returns_none(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        assert mem.lookup("") is None

    def test_lookup_after_record(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+390972536918", client_name="Mario Rossi")
        profile = mem.lookup("+390972536918")
        assert profile is not None
        assert profile.client_name == "Mario Rossi"
        assert profile.call_count == 1

    def test_lookup_normalizes_phone(self, tmp_path):
        """SIP URI and plain number should match the same profile."""
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("sip:+390972536918@sip.vivavox.it", client_name="Mario")
        profile = mem.lookup("+390972536918")
        assert profile is not None
        assert profile.client_name == "Mario"


class TestCallerMemoryRecord:
    """Test record_call and call counting."""

    def test_first_call_creates_profile(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        profile = mem.record_call("+39333", client_name="Luca")
        assert profile.call_count == 1
        assert profile.client_name == "Luca"

    def test_second_call_increments_count(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", client_name="Luca")
        profile = mem.record_call("+39333")
        assert profile.call_count == 2

    def test_updates_client_name(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", client_name="Luca")
        mem.record_call("+39333", client_name="Luca Bianchi")
        profile = mem.lookup("+39333")
        assert profile.client_name == "Luca Bianchi"

    def test_updates_last_service(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", service="Taglio")
        mem.record_call("+39333", service="Barba")
        profile = mem.lookup("+39333")
        assert profile.last_service == "Barba"

    def test_updates_last_operator(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", operator="Marco")
        profile = mem.lookup("+39333")
        assert profile.last_operator == "Marco"

    def test_empty_phone_returns_empty_profile(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        profile = mem.record_call("")
        assert profile.phone_number == ""

    def test_records_booking_history(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", service="Taglio", day_of_week="martedi", time_slot="10:00")
        history = mem.get_booking_history("+39333")
        assert len(history) == 1
        assert history[0]["service"] == "Taglio"
        assert history[0]["day_of_week"] == "martedi"
        assert history[0]["time_slot"] == "10:00"


class TestCallerMemoryPreferences:
    """Test preferred day/time calculation from booking history."""

    def test_preferred_day_from_history(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        # 3 bookings on martedi, 1 on giovedi
        mem.record_call("+39333", service="Taglio", day_of_week="martedi", time_slot="10:00")
        mem.record_call("+39333", service="Taglio", day_of_week="martedi", time_slot="11:00")
        mem.record_call("+39333", service="Taglio", day_of_week="giovedi", time_slot="10:00")
        mem.record_call("+39333", service="Taglio", day_of_week="martedi", time_slot="10:00")
        profile = mem.lookup("+39333")
        assert profile.preferred_day == "martedi"

    def test_preferred_time_from_history(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", service="Taglio", day_of_week="martedi", time_slot="10:00")
        mem.record_call("+39333", service="Taglio", day_of_week="martedi", time_slot="10:00")
        mem.record_call("+39333", service="Taglio", day_of_week="giovedi", time_slot="15:00")
        profile = mem.lookup("+39333")
        assert profile.preferred_time == "10:00"

    def test_no_preference_without_bookings(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", client_name="Luca")  # No booking data
        profile = mem.lookup("+39333")
        assert profile.preferred_day == ""
        assert profile.preferred_time == ""


class TestBookingHistory:
    """Test get_booking_history."""

    def test_empty_history(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        assert mem.get_booking_history("+39333") == []

    def test_multiple_bookings(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", service="Taglio", day_of_week="lunedi", time_slot="09:00")
        mem.record_call("+39333", service="Barba", day_of_week="martedi", time_slot="10:00")
        history = mem.get_booking_history("+39333")
        assert len(history) == 2
        # Most recent first
        assert history[0]["service"] == "Barba"

    def test_limit_parameter(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        for i in range(5):
            mem.record_call("+39333", service=f"Service{i}", day_of_week="lunedi", time_slot="10:00")
        history = mem.get_booking_history("+39333", limit=3)
        assert len(history) == 3

    def test_empty_phone_returns_empty(self, tmp_path):
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        assert mem.get_booking_history("") == []


# =============================================================================
# C2: Phone Number Extraction from SIP URI
# =============================================================================


class TestPhoneNormalization:
    """Test _normalize_phone static method."""

    def test_sip_uri_with_plus(self):
        result = CallerMemory._normalize_phone("sip:+390972536918@sip.vivavox.it")
        assert result == "+390972536918"

    def test_sip_uri_without_plus(self):
        result = CallerMemory._normalize_phone("sip:0972536918@sip.vivavox.it")
        assert result == "0972536918"

    def test_angle_brackets(self):
        result = CallerMemory._normalize_phone("<sip:+39333@host>")
        assert result == "+39333"

    def test_display_name_and_brackets(self):
        result = CallerMemory._normalize_phone('"Mario" <sip:+39333@host>')
        assert result == "+39333"

    def test_plain_number(self):
        result = CallerMemory._normalize_phone("+390972536918")
        assert result == "+390972536918"

    def test_plain_number_no_plus(self):
        result = CallerMemory._normalize_phone("0972536918")
        assert result == "0972536918"

    def test_empty_string(self):
        assert CallerMemory._normalize_phone("") == ""

    def test_strips_non_digits(self):
        result = CallerMemory._normalize_phone("+39 (097) 253-6918")
        assert result == "+390972536918"


try:
    from voip_pjsua2 import VoIPManager as _VoIPManager
    _HAS_VOIP = True
except (ImportError, OSError):
    _HAS_VOIP = False


@pytest.mark.skipif(not _HAS_VOIP, reason="voip_pjsua2 not available (missing audioop or pjsua2 libs)")
class TestVoIPPhoneExtraction:
    """Test _extract_phone_from_uri on VoIPManager."""

    def test_extract_basic_sip_uri(self):
        result = _VoIPManager._extract_phone_from_uri("sip:+390972536918@sip.vivavox.it")
        assert result == "+390972536918"

    def test_extract_with_brackets(self):
        result = _VoIPManager._extract_phone_from_uri("<sip:0972536918@sip.vivavox.it>")
        assert result == "0972536918"

    def test_extract_with_display_name(self):
        result = _VoIPManager._extract_phone_from_uri('"Mario" <sip:+39333@host>')
        assert result == "+39333"

    def test_extract_empty(self):
        assert _VoIPManager._extract_phone_from_uri("") == ""


# =============================================================================
# C3: Personalized Greeting for Returning Callers
# =============================================================================


class TestPersonalizedGreeting:
    """Test get_greeting with caller_name parameter."""

    def test_default_greeting_no_caller(self):
        from session_manager import SessionManager, SessionChannel
        mgr = SessionManager()
        session = mgr.create_session(
            verticale_id="salone_test",
            business_name="Salone Bella Vita",
            channel=SessionChannel.VOICE
        )
        greeting = mgr.get_greeting(session.session_id)
        assert "Salone Bella Vita" in greeting
        assert "come posso aiutarla?" in greeting.lower()
        assert "bentornato" not in greeting.lower()

    def test_personalized_greeting_returning_caller(self):
        from session_manager import SessionManager, SessionChannel
        mgr = SessionManager()
        session = mgr.create_session(
            verticale_id="salone_test",
            business_name="Salone Bella Vita",
            channel=SessionChannel.VOICE
        )
        greeting = mgr.get_greeting(session.session_id, caller_name="Mario")
        assert "Salone Bella Vita" in greeting
        assert "Bentornato Mario" in greeting
        assert "come posso aiutarla?" in greeting.lower()

    def test_personalized_greeting_contains_saluto(self):
        from session_manager import SessionManager, SessionChannel
        mgr = SessionManager()
        session = mgr.create_session(
            verticale_id="salone_test",
            business_name="Test",
            channel=SessionChannel.VOICE
        )
        greeting = mgr.get_greeting(session.session_id, caller_name="Luca")
        # Should contain a time-based greeting
        hour = datetime.now().hour
        if hour < 12:
            assert "buongiorno" in greeting.lower()
        elif hour < 18:
            assert "buon pomeriggio" in greeting.lower()
        else:
            assert "buonasera" in greeting.lower()

    def test_empty_caller_name_gives_default(self):
        from session_manager import SessionManager, SessionChannel
        mgr = SessionManager()
        session = mgr.create_session(
            verticale_id="salone_test",
            business_name="Test",
            channel=SessionChannel.VOICE
        )
        greeting = mgr.get_greeting(session.session_id, caller_name="")
        assert "Bentornato" not in greeting

    def test_unknown_session_fallback(self):
        from session_manager import SessionManager
        mgr = SessionManager()
        greeting = mgr.get_greeting("nonexistent")
        assert greeting == "Buongiorno! Come posso aiutarla?"


# =============================================================================
# C4: Preferred Slot Suggestion (Integration)
# =============================================================================


class TestSlotSuggestion:
    """Test preferred slot suggestion for returning callers."""

    def test_caller_with_preferred_day_and_time(self, tmp_path):
        """CallerProfile with preferred_day and preferred_time should have suggestion data."""
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        # Build up history
        for _ in range(3):
            mem.record_call("+39333", service="Taglio", day_of_week="martedi", time_slot="10:00")
        profile = mem.lookup("+39333")
        assert profile.preferred_day == "martedi"
        assert profile.preferred_time == "10:00"
        assert profile.is_returning
        assert profile.call_count == 3

    def test_caller_with_only_preferred_day(self, tmp_path):
        """Caller who books on same day but different times."""
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", service="Taglio", day_of_week="venerdi", time_slot="09:00")
        mem.record_call("+39333", service="Taglio", day_of_week="venerdi", time_slot="11:00")
        mem.record_call("+39333", service="Taglio", day_of_week="venerdi", time_slot="15:00")
        profile = mem.lookup("+39333")
        assert profile.preferred_day == "venerdi"
        # All different times, so most common is any one of them
        assert profile.preferred_time in ["09:00", "11:00", "15:00"]

    def test_new_caller_no_preference(self, tmp_path):
        """First-time caller should have no preferences."""
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", client_name="Primo")
        profile = mem.lookup("+39333")
        assert profile.preferred_day == ""
        assert profile.preferred_time == ""


# =============================================================================
# Singleton
# =============================================================================


class TestSingleton:
    """Test get_caller_memory singleton."""

    def test_singleton_returns_same_instance(self, tmp_path):
        import caller_memory as cm
        # Reset singleton
        cm._memory = None
        db_path = str(tmp_path / "singleton.db")
        m1 = cm.get_caller_memory(db_path=db_path)
        m2 = cm.get_caller_memory()
        assert m1 is m2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases and robustness tests."""

    def test_concurrent_records(self, tmp_path):
        """Multiple rapid record_call should not corrupt data."""
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        for i in range(10):
            mem.record_call("+39333", client_name=f"Name{i}", service=f"Service{i}")
        profile = mem.lookup("+39333")
        assert profile.call_count == 10

    def test_special_characters_in_name(self, tmp_path):
        """Names with accents and apostrophes should be stored correctly."""
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+39333", client_name="D'Alessio Niccolò")
        profile = mem.lookup("+39333")
        assert profile.client_name == "D'Alessio Niccolò"

    def test_very_long_phone_number(self, tmp_path):
        """Long international numbers should work."""
        mem = CallerMemory(db_path=str(tmp_path / "test.db"))
        mem.record_call("+44207123456789", client_name="British")
        profile = mem.lookup("+44207123456789")
        assert profile is not None
        assert profile.client_name == "British"

    def test_phone_with_sip_prefix_variations(self):
        """Various SIP URI formats should normalize correctly."""
        assert CallerMemory._normalize_phone("SIP:+39333@host") == "+39333"
        assert CallerMemory._normalize_phone("sip:+39333@host") == "+39333"
        assert CallerMemory._normalize_phone("<SIP:+39333@host>") == "+39333"

    def test_profile_persistence_across_instances(self, tmp_path):
        """Data persists when creating new CallerMemory instances."""
        db_path = str(tmp_path / "persist.db")
        mem1 = CallerMemory(db_path=db_path)
        mem1.record_call("+39333", client_name="Mario")

        mem2 = CallerMemory(db_path=db_path)
        profile = mem2.lookup("+39333")
        assert profile is not None
        assert profile.client_name == "Mario"
