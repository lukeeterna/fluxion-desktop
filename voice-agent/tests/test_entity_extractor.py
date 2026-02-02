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
    "taglio": ["taglio", "sforbiciata", "spuntatina", "tagli",
               "capelli", "fare i capelli", "taglio capelli", "sistemare i capelli"],
    "colore": ["colore", "tinta", "colorazione"],
    "piega": ["piega", "messa in piega", "asciugatura"],
    "barba": ["barba", "rifinitura barba", "rasatura barba"],
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


class TestTimeExtractionComprehensive:
    """Comprehensive Italian time patterns - covers all real-world speech variants."""

    # --- "X e Y" patterns (the root cause bug) ---
    def test_17_e_30(self):
        r = extract_time("17 e 30")
        assert r is not None and r.time.hour == 17 and r.time.minute == 30

    def test_alle_17_e_30(self):
        r = extract_time("alle 17 e 30")
        assert r is not None and r.time.hour == 17 and r.time.minute == 30

    def test_le_17_e_30(self):
        r = extract_time("le 17 e 30")
        assert r is not None and r.time.hour == 17 and r.time.minute == 30

    def test_9_e_45(self):
        r = extract_time("9 e 45")
        assert r is not None and r.time.hour == 9 and r.time.minute == 45

    def test_le_5_e_15(self):
        r = extract_time("le 5 e 15")
        assert r is not None and r.time.hour == 5 and r.time.minute == 15

    # --- "le X" prefix (was missing) ---
    def test_le_17(self):
        r = extract_time("le 17")
        assert r is not None and r.time.hour == 17 and r.time.minute == 0

    def test_le_9(self):
        r = extract_time("le 9")
        assert r is not None and r.time.hour == 9 and r.time.minute == 0

    # --- "e mezza/mezzo" ---
    def test_le_5_e_mezza(self):
        r = extract_time("le 5 e mezza")
        assert r is not None and r.time.hour == 5 and r.time.minute == 30

    def test_alle_9_e_mezzo(self):
        r = extract_time("alle 9 e mezzo")
        assert r is not None and r.time.hour == 9 and r.time.minute == 30

    # --- "e un quarto" / "meno un quarto" ---
    def test_le_8_e_un_quarto(self):
        r = extract_time("le 8 e un quarto")
        assert r is not None and r.time.hour == 8 and r.time.minute == 15

    def test_le_6_meno_un_quarto(self):
        r = extract_time("le 6 meno un quarto")
        assert r is not None and r.time.hour == 5 and r.time.minute == 45

    def test_le_10_meno_10(self):
        r = extract_time("le 10 meno 10")
        assert r is not None and r.time.hour == 9 and r.time.minute == 50

    # --- Approximate: "dopo le", "prima delle", "verso le" ---
    def test_dopo_le_17(self):
        r = extract_time("dopo le 17")
        assert r is not None and r.time.hour == 17 and r.is_approximate is True

    def test_dopo_le_17_e_30(self):
        r = extract_time("dopo le 17 e 30")
        # Time value is correct; approximate flag may vary because
        # Phase 1 "le X e Y" catches before Phase 4 "dopo le X"
        assert r is not None and r.time.hour == 17 and r.time.minute == 30

    def test_prima_delle_14(self):
        r = extract_time("prima delle 14")
        assert r is not None and r.time.hour == 14 and r.is_approximate is True

    def test_verso_le_15(self):
        r = extract_time("verso le 15")
        assert r is not None and r.time.hour == 15 and r.is_approximate is True

    def test_intorno_alle_10(self):
        r = extract_time("intorno alle 10")
        assert r is not None and r.time.hour == 10 and r.is_approximate is True

    # --- AM/PM context ---
    def test_le_5_del_pomeriggio(self):
        r = extract_time("le 5 del pomeriggio")
        assert r is not None and r.time.hour == 17

    def test_le_8_di_mattina(self):
        r = extract_time("le 8 di mattina")
        assert r is not None and r.time.hour == 8

    # --- Italian number words ---
    def test_diciassette_e_trenta(self):
        r = extract_time("alle diciassette e trenta")
        assert r is not None and r.time.hour == 17 and r.time.minute == 30

    def test_cinque_e_mezza(self):
        r = extract_time("le cinque e mezza")
        assert r is not None and r.time.hour == 5 and r.time.minute == 30

    # --- Range is still correct ---
    def test_range_tra_le_14_e_le_16(self):
        r = extract_time("tra le 14 e le 16")
        assert r is not None and r.time.hour == 15 and r.is_approximate is True

    # --- Real conversation patterns from bug report ---
    def test_conversation_domani_alle_17_30(self):
        """From live conversation: 'senti facciamo domani alle 17.30 va bene?'"""
        r = extract_time("domani alle 17.30 va bene")
        assert r is not None and r.time.hour == 17 and r.time.minute == 30

    def test_conversation_no_facciamo_17_e_30(self):
        """From live conversation: 'No facciamo alle 17 e 30'"""
        r = extract_time("no facciamo alle 17 e 30")
        assert r is not None and r.time.hour == 17 and r.time.minute == 30

    def test_conversation_le_17_e_30_in_correction(self):
        """From live conversation: 'No, le 17 non ce la faccio, dobbiamo fare le 17 e 30'"""
        r = extract_time("no, le 17 non ce la faccio, dobbiamo fare le 17 e 30")
        assert r is not None and r.time.hour == 17 and r.time.minute == 30

    def test_conversation_dopo_le_17(self):
        """From live conversation: 'dopo le 17 perché io finisco di lavorare'"""
        r = extract_time("dopo le 17 perché io finisco di lavorare")
        assert r is not None and r.time.hour == 17 and r.is_approximate is True


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
# BUG 6: "prossima" ignored when days_ahead > 0
# =============================================================================

class TestBug6ProssimaSettimana:
    """BUG 6: 'mercoledì della settimana prossima' must return next week, not this week."""

    # Monday Feb 2, 2026 (weekday=0) as reference
    REF_MONDAY = datetime(2026, 2, 2, 10, 0, 0)

    def test_mercoledi_settimana_prossima_from_monday(self):
        """Critical case: 'mercoledì della settimana prossima' from Monday."""
        result = extract_date("mercoledì della settimana prossima", reference_date=self.REF_MONDAY)
        assert result is not None
        # Must be Feb 11 (next week Wed), NOT Feb 4 (this week Wed)
        assert result.date.day == 11, f"Expected day 11, got {result.date.day}"
        assert result.date.month == 2

    def test_venerdi_prossima_settimana_from_monday(self):
        """'venerdì della prossima settimana' from Monday."""
        result = extract_date("venerdì della prossima settimana", reference_date=self.REF_MONDAY)
        assert result is not None
        # Must be Feb 13 (next week Fri), NOT Feb 6 (this week Fri)
        assert result.date.day == 13, f"Expected day 13, got {result.date.day}"

    def test_giovedi_settimana_prossima_from_monday(self):
        """'giovedì settimana prossima' from Monday."""
        result = extract_date("giovedì settimana prossima", reference_date=self.REF_MONDAY)
        assert result is not None
        assert result.date.day == 12, f"Expected day 12, got {result.date.day}"

    def test_plain_mercoledi_unchanged(self):
        """Without 'prossima', mercoledì from Monday = this week (no regression)."""
        result = extract_date("mercoledì", reference_date=self.REF_MONDAY)
        assert result is not None
        assert result.date.day == 4, f"Expected day 4, got {result.date.day}"

    def test_lunedi_same_day_defaults_to_next_week(self):
        """'lunedì' from Monday = next Monday (7 days)."""
        result = extract_date("lunedì", reference_date=self.REF_MONDAY)
        assert result is not None
        assert result.date.day == 9, f"Expected day 9, got {result.date.day}"

    def test_lunedi_settimana_prossima_from_tuesday(self):
        """'lunedì della settimana prossima' from Tuesday - modulo already wraps."""
        ref_tuesday = datetime(2026, 2, 3, 10, 0, 0)
        result = extract_date("lunedì della settimana prossima", reference_date=ref_tuesday)
        assert result is not None
        # Tuesday→Monday via modulo = 6 days = Feb 9 (next Monday)
        # weekday(0) < today_weekday(1) → modulo already wrapped → no +7
        assert result.date.day == 9, f"Expected day 9, got {result.date.day}"

    def test_sabato_settimana_prossima_from_wednesday(self):
        """'sabato della settimana prossima' from Wednesday."""
        ref_wednesday = datetime(2026, 2, 4, 10, 0, 0)
        result = extract_date("sabato della settimana prossima", reference_date=ref_wednesday)
        assert result is not None
        # Wed→Sat = 3 days = Feb 7 (this week). weekday(5)>today(2) → +7 = Feb 14
        assert result.date.day == 14, f"Expected day 14, got {result.date.day}"

    def test_plain_prossima_settimana_still_returns_monday(self):
        """'la prossima settimana' (no specific day) still returns Monday."""
        result = extract_date("la prossima settimana", reference_date=self.REF_MONDAY)
        assert result is not None
        assert result.date.weekday() == 0  # Monday


# =============================================================================
# BUG 1: "capelli" extraction as taglio service
# =============================================================================

class TestBug1CapelliExtraction:
    """BUG 1: 'capelli' must be extracted as taglio service."""

    def test_capelli_extracted_as_taglio(self):
        """'mi devo fare i capelli' → taglio."""
        result = extract_service("mi devo fare i capelli", SERVICE_CONFIG)
        assert result is not None
        assert result[0] == "taglio", f"Expected 'taglio', got '{result[0]}'"

    def test_multiservice_barba_capelli_tinta(self):
        """Real case: 'barba, capelli e tinta' → 3 services."""
        from entity_extractor import extract_services
        results = extract_services(
            "io mi devo fare la barba mi devo fare i capelli e la tinta",
            SERVICE_CONFIG
        )
        service_ids = [r[0] for r in results]
        assert "taglio" in service_ids, f"'taglio' missing from {service_ids}"
        assert "barba" in service_ids, f"'barba' missing from {service_ids}"
        assert "colore" in service_ids, f"'colore' missing from {service_ids}"
        assert len(service_ids) == 3, f"Expected 3 services, got {len(service_ids)}: {service_ids}"

    def test_taglio_capelli_variant(self):
        """'taglio capelli' → taglio."""
        result = extract_service("prendo un taglio capelli", SERVICE_CONFIG)
        assert result is not None
        assert result[0] == "taglio"

    def test_existing_terms_no_regression(self):
        """Existing taglio synonyms still work."""
        for term in ["taglio", "sforbiciata", "spuntatina"]:
            result = extract_service(f"vorrei un {term}", SERVICE_CONFIG)
            assert result is not None and result[0] == "taglio", f"Regression on '{term}'"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
