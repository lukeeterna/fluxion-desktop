"""
FLUXION Voice Agent - Entity Extractor Tests

Test suite for entity extraction (Day 3):
- Date extraction: relative, day names, explicit dates
- Time extraction: exact times, approximate slots
- Name extraction: various Italian patterns
- Phone/Email extraction

Run with: pytest voice-agent/tests/test_entity_extractor.py -v
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from entity_extractor import (
    extract_date,
    extract_time,
    extract_name,
    extract_service,
    extract_phone,
    extract_email,
    extract_all,
)


# =============================================================================
# TEST DATA
# =============================================================================

# Reference date for testing (fixed to avoid flaky tests)
REFERENCE_DATE = datetime(2026, 1, 13, 10, 0, 0)  # Tuesday, January 13, 2026


DATE_TEST_CASES = [
    # (input, expected_days_from_reference, description)
    # Relative dates
    ("domani", 1, "tomorrow"),
    ("dopodomani", 2, "day after tomorrow"),
    ("oggi", 0, "today"),

    # Day names
    ("lunedì", 6, "next Monday (from Tuesday)"),  # Next Monday is 6 days away
    ("mercoledì", 1, "next Wednesday (tomorrow from Tuesday)"),
    ("venerdì", 3, "next Friday"),
    ("sabato", 4, "next Saturday"),
    ("domenica", 5, "next Sunday"),

    # Week references
    ("la prossima settimana", 6, "next week (Monday)"),

    # Explicit dates
    ("il 15 gennaio", 2, "January 15"),
    ("20 gennaio", 7, "January 20"),
]

TIME_TEST_CASES = [
    # (input, expected_hour, expected_minute, description)
    # Exact times
    ("alle 15", 15, 0, "at 15:00"),
    ("alle 15:30", 15, 30, "at 15:30"),
    ("ore 10", 10, 0, "at 10:00"),
    ("10:30", 10, 30, "10:30 standalone"),
    ("alle 9 e mezza", 9, 30, "9:30 with 'mezza'"),

    # Approximate slots
    ("di pomeriggio", 15, 0, "afternoon slot"),
    ("mattina", 10, 0, "morning slot"),
    ("sera", 19, 0, "evening slot"),
    ("mezzogiorno", 12, 0, "noon"),
    ("tardo pomeriggio", 17, 0, "late afternoon"),

    # Ranges
    ("tra le 14 e le 16", 15, 0, "range midpoint"),
]

NAME_TEST_CASES = [
    # (input, expected_name, description)
    ("Sono Mario", "Mario", "simple sono"),
    ("sono mario rossi", "Mario Rossi", "sono with surname"),
    ("Mi chiamo Laura", "Laura", "mi chiamo"),
    ("mi chiamo giovanni bianchi", "Giovanni Bianchi", "mi chiamo with surname"),
    ("Chiamami Luca", "Luca", "chiamami"),
    ("Il mio nome è Anna", "Anna", "il mio nome è"),
    ("sono il signor Verdi", "Verdi", "signor"),
    ("sono la signora Russo", "Russo", "signora"),
]

PHONE_TEST_CASES = [
    # (input, expected_normalized)
    ("333 123 4567", "3331234567"),
    ("333.123.4567", "3331234567"),
    ("+39 333 1234567", "+393331234567"),
    ("Il mio numero è 3331234567", "3331234567"),
]

EMAIL_TEST_CASES = [
    # (input, expected_email)
    ("la mia email è mario@email.com", "mario@email.com"),
    ("contattami a test.user@domain.it", "test.user@domain.it"),
    ("MARIO@GMAIL.COM", "mario@gmail.com"),
]

SERVICE_CONFIG = {
    "taglio": ["taglio", "sforbiciata", "spuntatina", "tagli"],
    "colore": ["colore", "tinta", "colorazione"],
    "piega": ["piega", "messa in piega", "asciugatura"],
}

SERVICE_TEST_CASES = [
    # (input, expected_service)
    ("vorrei un taglio", "taglio"),
    ("una sforbiciata", "taglio"),
    ("fare il colore", "colore"),
    ("una tinta", "colore"),
    ("piega", "piega"),
]


# =============================================================================
# TESTS
# =============================================================================

class TestDateExtraction:
    """Test date extraction."""

    def test_relative_dates(self):
        """Test relative date keywords."""
        for text, expected_days, desc in DATE_TEST_CASES[:3]:  # oggi, domani, dopodomani
            result = extract_date(text, reference_date=REFERENCE_DATE)
            assert result is not None, f"Failed to extract: {text}"

            expected_date = REFERENCE_DATE + timedelta(days=expected_days)
            assert result.date.date() == expected_date.date(), \
                f"Wrong date for '{text}': got {result.date.date()}, expected {expected_date.date()}"

    def test_day_names(self):
        """Test day name extraction."""
        # Test lunedì from Tuesday reference
        result = extract_date("lunedì", reference_date=REFERENCE_DATE)
        assert result is not None
        assert result.date.weekday() == 0  # Monday

        # Test mercoledì (tomorrow from Tuesday)
        result = extract_date("mercoledì", reference_date=REFERENCE_DATE)
        assert result is not None
        assert result.date.weekday() == 2  # Wednesday

    def test_explicit_dates(self):
        """Test explicit date formats."""
        # "15 gennaio" from Jan 13 reference
        result = extract_date("il 15 gennaio", reference_date=REFERENCE_DATE)
        assert result is not None
        assert result.date.day == 15
        assert result.date.month == 1

    def test_week_references(self):
        """Test week reference extraction."""
        result = extract_date("la prossima settimana", reference_date=REFERENCE_DATE)
        assert result is not None
        assert result.date.weekday() == 0  # Should be Monday

    def test_italian_format(self):
        """Test Italian date formatting."""
        result = extract_date("domani", reference_date=REFERENCE_DATE)
        assert result is not None
        italian = result.to_italian()
        assert "mercoledì" in italian  # Tomorrow from Tuesday is Wednesday
        assert "14" in italian
        assert "gennaio" in italian

    def test_no_match_returns_none(self):
        """Test that unrecognized text returns None."""
        result = extract_date("testo senza data")
        assert result is None

    def test_performance(self):
        """Test extraction is fast (<10ms)."""
        start = time.time()
        for _ in range(100):
            extract_date("domani alle 15")
        elapsed = (time.time() - start) * 1000 / 100
        assert elapsed < 10, f"Date extraction too slow: {elapsed:.2f}ms"


class TestTimeExtraction:
    """Test time extraction."""

    def test_exact_times(self):
        """Test exact time patterns."""
        for text, expected_hour, expected_minute, desc in TIME_TEST_CASES[:5]:
            result = extract_time(text)
            assert result is not None, f"Failed to extract: {text}"
            assert result.time.hour == expected_hour, \
                f"Wrong hour for '{text}': got {result.time.hour}, expected {expected_hour}"
            assert result.time.minute == expected_minute, \
                f"Wrong minute for '{text}': got {result.time.minute}, expected {expected_minute}"

    def test_approximate_slots(self):
        """Test approximate time slot keywords."""
        for text, expected_hour, _, desc in TIME_TEST_CASES[5:10]:
            result = extract_time(text)
            assert result is not None, f"Failed to extract: {text}"
            assert result.time.hour == expected_hour, \
                f"Wrong hour for '{text}': got {result.time.hour}, expected {expected_hour}"
            assert result.is_approximate is True

    def test_time_ranges(self):
        """Test time range extraction (midpoint)."""
        result = extract_time("tra le 14 e le 16")
        assert result is not None
        assert result.time.hour == 15  # Midpoint

    def test_no_match_returns_none(self):
        """Test that unrecognized text returns None."""
        result = extract_time("testo senza ora")
        assert result is None

    def test_performance(self):
        """Test extraction is fast (<5ms)."""
        start = time.time()
        for _ in range(100):
            extract_time("alle 15:30")
        elapsed = (time.time() - start) * 1000 / 100
        assert elapsed < 5, f"Time extraction too slow: {elapsed:.2f}ms"


class TestNameExtraction:
    """Test name extraction."""

    def test_name_patterns(self):
        """Test various name introduction patterns."""
        for text, expected_name, desc in NAME_TEST_CASES:
            result = extract_name(text)
            assert result is not None, f"Failed to extract: {text}"
            assert result.name == expected_name, \
                f"Wrong name for '{text}': got '{result.name}', expected '{expected_name}'"

    def test_capitalization(self):
        """Test name capitalization."""
        result = extract_name("sono mario rossi")
        assert result is not None
        assert result.name == "Mario Rossi"  # Should be capitalized

    def test_no_match_returns_none(self):
        """Test that unrecognized text returns None."""
        result = extract_name("voglio un appuntamento")
        assert result is None


class TestPhoneExtraction:
    """Test phone number extraction."""

    def test_phone_patterns(self):
        """Test various phone number formats."""
        for text, expected in PHONE_TEST_CASES:
            result = extract_phone(text)
            assert result is not None, f"Failed to extract: {text}"
            assert result == expected, f"Wrong phone for '{text}': got '{result}'"

    def test_no_match_returns_none(self):
        """Test that text without phone returns None."""
        result = extract_phone("testo senza numero")
        assert result is None


class TestEmailExtraction:
    """Test email extraction."""

    def test_email_patterns(self):
        """Test email extraction."""
        for text, expected in EMAIL_TEST_CASES:
            result = extract_email(text)
            assert result is not None, f"Failed to extract: {text}"
            assert result == expected, f"Wrong email for '{text}': got '{result}'"

    def test_no_match_returns_none(self):
        """Test that text without email returns None."""
        result = extract_email("testo senza email")
        assert result is None


class TestServiceExtraction:
    """Test service extraction with synonyms."""

    def test_service_synonyms(self):
        """Test service extraction with synonym config."""
        for text, expected in SERVICE_TEST_CASES:
            result = extract_service(text, SERVICE_CONFIG)
            assert result is not None, f"Failed to extract: {text}"
            assert result[0] == expected, \
                f"Wrong service for '{text}': got '{result[0]}', expected '{expected}'"

    def test_no_match_returns_none(self):
        """Test unknown service returns None."""
        result = extract_service("massaggio", SERVICE_CONFIG)
        assert result is None


class TestCombinedExtraction:
    """Test combined extraction."""

    def test_extract_all(self):
        """Test extraction of multiple entities."""
        text = "Sono Mario, vorrei prenotare domani alle 15"
        result = extract_all(text, SERVICE_CONFIG)

        assert result.name is not None
        assert result.name.name == "Mario"

        assert result.date is not None
        # domani from today

        assert result.time is not None
        assert result.time.time.hour == 15

    def test_has_booking_info(self):
        """Test booking info check."""
        text = "domani alle 15"
        result = extract_all(text)
        assert result.has_booking_info() is True

        text = "ciao"
        result = extract_all(text)
        assert result.has_booking_info() is False

    def test_to_dict(self):
        """Test dictionary conversion."""
        text = "domani alle 15, email: test@email.com"
        result = extract_all(text)

        d = result.to_dict()
        assert "date" in d
        assert "time" in d
        assert d["time"] == "15:00"
        assert d["email"] == "test@email.com"


class TestPerformance:
    """Overall performance tests."""

    def test_combined_performance(self):
        """Test combined extraction is fast (<20ms)."""
        text = "Sono Mario, vorrei un taglio domani alle 15, tel 333 1234567"

        start = time.time()
        for _ in range(100):
            extract_all(text, SERVICE_CONFIG)
        elapsed = (time.time() - start) * 1000 / 100

        print(f"\nCombined extraction time: {elapsed:.2f}ms")
        assert elapsed < 20, f"Combined extraction too slow: {elapsed:.2f}ms"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
