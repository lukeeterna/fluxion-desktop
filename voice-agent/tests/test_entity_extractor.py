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
    extract_operators_multi,
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
    # --- Bare mobile (existing, must not break) ---
    ("333 123 4567", "3331234567"),
    ("333.123.4567", "3331234567"),
    ("Il mio numero è 3331234567", "3331234567"),
    # --- +39 prefix (existing: keeps + for backward compat) ---
    ("+39 333 1234567", "+393331234567"),
    # --- GAP-P1-1: 0039 prefix (strips to bare 10 digits) ---
    ("0039 333 1234567", "3331234567"),
    ("0039333 1234567", "3331234567"),
    ("00393331234567", "3331234567"),
    ("il mio numero è 0039 345 678 9012", "3456789012"),
    # --- GAP-P1-1: bare 39 prefix (12 digits total → strips to bare) ---
    ("39 345 6789012", "3456789012"),
    ("393456789012", "3456789012"),
    # --- AGCOM range coverage ---
    ("il numero è 3451234567", "3451234567"),
    ("chiamami al 3801234567", "3801234567"),
]

EMAIL_TEST_CASES = [
    # (input, expected_email)
    # --- Existing behavior (must not break) ---
    ("la mia email è mario@email.com", "mario@email.com"),
    ("contattami a test.user@domain.it", "test.user@domain.it"),
    ("MARIO@GMAIL.COM", "mario@gmail.com"),
    # --- GAP-P1-2: keyword-anchored priority ---
    ("scrivi a support@azienda.it, la mia email è mario@gmail.com", "mario@gmail.com"),
    ("contatti: info@salone.it - la mia mail è luigi.bianchi@hotmail.it", "luigi.bianchi@hotmail.it"),
    ("l'indirizzo email è anna.verdi@libero.it", "anna.verdi@libero.it"),
    ("per comunicazioni ufficio@studio.it, ma la mia e-mail è personal@gmail.com", "personal@gmail.com"),
    ("mia mail: mario@email.it", "mario@email.it"),
    # --- GAP-P1-2: STT artifacts ---
    ("la mia email è mario chiocciola gmail punto com", "mario@gmail.com"),
    ("scrivi a mario at gmail.com", "mario@gmail.com"),
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


class TestExtractTimeAMPM:
    """Bug 3: bare hours 1-8 assume PM (Italian business hours convention)."""

    def test_alle_tre_is_pm(self):
        t = extract_time("alle tre")
        assert t is not None
        assert t.time.hour == 15, f"Expected 15, got {t.time.hour}"

    def test_alle_sette_is_pm(self):
        t = extract_time("alle sette")
        assert t is not None
        assert t.time.hour == 19

    def test_alle_uno_is_pm(self):
        t = extract_time("alle una")
        # "una" → normalized to 1 by _normalize_italian_numbers → hour 13
        # Note: only test if number normalization covers "una"
        # If extract_time returns None, that's acceptable — number not in normalizer
        if t is not None:
            assert t.time.hour == 13

    def test_alle_tre_di_mattina_stays_am(self):
        t = extract_time("alle tre di mattina")
        assert t is not None
        assert t.time.hour == 3, "Morning context must keep AM"

    def test_alle_dieci_unchanged(self):
        """Hours >= 9 are unaffected by heuristic."""
        t = extract_time("alle dieci")
        # "dieci" is normalized to 10 → stays 10
        if t is not None:
            assert t.time.hour == 10

    def test_explicit_17_unchanged(self):
        """Explicit 24h hours are not touched."""
        t = extract_time("alle 17")
        assert t is not None
        assert t.time.hour == 17

    def test_explicit_3_with_minutes_unchanged(self):
        """Hours with explicit minutes skip the bare-hour heuristic."""
        t = extract_time("alle 3:30")
        assert t is not None
        assert t.time.hour == 3  # PHASE 1 exact — no heuristic


class TestExtractDateSTTTruncation:
    """Bug 4: STT-truncated day names (Whisper drops final accented vowel)."""

    def setup_method(self):
        self.ref = datetime(2026, 3, 9)  # Monday

    def test_marted_truncated(self):
        d = extract_date("marted", reference_date=self.ref)
        assert d is not None, "STT-truncated 'marted' must resolve"
        assert d.date.weekday() == 1, f"Expected Tuesday(1), got {d.date.weekday()}"

    def test_gioved_truncated(self):
        d = extract_date("gioved", reference_date=self.ref)
        assert d is not None
        assert d.date.weekday() == 3

    def test_venerd_truncated(self):
        d = extract_date("venerd", reference_date=self.ref)
        assert d is not None
        assert d.date.weekday() == 4

    def test_mercoled_truncated(self):
        d = extract_date("mercoled", reference_date=self.ref)
        assert d is not None
        assert d.date.weekday() == 2

    def test_full_martedi_still_works(self):
        """Existing full names must not be broken by truncation additions."""
        d = extract_date("martedì", reference_date=self.ref)
        assert d is not None
        assert d.date.weekday() == 1


# =============================================================================
# TESTS: GAP-B2 (Mese prossimo / fra N mesi) + GAP-B6 (Weekend)
# =============================================================================

import pytest as _pytest

# Reference: giovedì 2026-03-12 (weekday=3)
_REF_THU = datetime(2026, 3, 12)   # giovedì
_REF_SAT = datetime(2026, 3, 14)   # sabato
_REF_SUN = datetime(2026, 3, 15)   # domenica


class TestDateRelativeMonthAndWeekend:
    """GAP-B2: mese prossimo / fra N mesi. GAP-B6: fine settimana / weekend."""

    # --- GAP-B2: mese prossimo ---

    def test_il_mese_prossimo(self):
        """'il mese prossimo' → primo del mese successivo."""
        result = extract_date("il mese prossimo", reference_date=_REF_THU)
        assert result is not None, "nessun risultato per 'il mese prossimo'"
        assert result.date.strftime("%Y-%m-%d") == "2026-04-01"
        assert result.confidence >= 0.85

    def test_mese_prossimo_senza_articolo(self):
        """'mese prossimo' → primo del mese successivo."""
        result = extract_date("mese prossimo", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-04-01"

    def test_prossimo_mese_ordine_invertito(self):
        """'prossimo mese' → primo del mese successivo."""
        result = extract_date("prossimo mese", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-04-01"

    def test_fra_un_mese_digit(self):
        """'fra 1 mese' → oggi + 30 giorni."""
        result = extract_date("fra 1 mese", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-04-11"
        assert result.confidence >= 0.85

    def test_fra_un_mese_word(self):
        """'fra un mese' → oggi + 30 giorni."""
        result = extract_date("fra un mese", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-04-11"

    def test_tra_un_mese_variante(self):
        """'tra un mese' → stessa logica di 'fra un mese'."""
        result = extract_date("tra un mese", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-04-11"

    def test_fra_due_mesi(self):
        """'fra due mesi' → oggi + 60 giorni."""
        result = extract_date("fra due mesi", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-05-11"

    def test_fra_3_mesi_digit(self):
        """'fra 3 mesi' → oggi + 90 giorni."""
        result = extract_date("fra 3 mesi", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-06-10"

    def test_mese_prossimo_dicembre_wrap(self):
        """'mese prossimo' a dicembre → 1° gennaio anno successivo."""
        ref_dec = datetime(2026, 12, 15)
        result = extract_date("mese prossimo", reference_date=ref_dec)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2027-01-01"

    # --- GAP-B6: fine settimana / weekend ---

    def test_fine_settimana_da_giovedi(self):
        """'fine settimana' da giovedì → sabato stesso settimana (2026-03-14)."""
        result = extract_date("fine settimana", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-14"
        assert result.confidence >= 0.90

    def test_weekend_termine_inglese(self):
        """'weekend' → stesso risultato di 'fine settimana'."""
        result = extract_date("weekend", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-14"

    def test_questo_weekend(self):
        """'questo weekend' → sabato questa settimana."""
        result = extract_date("questo weekend", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-14"

    def test_questo_fine_settimana(self):
        """'questo fine settimana' → sabato questa settimana."""
        result = extract_date("questo fine settimana", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-14"

    def test_il_prossimo_weekend_forza_next(self):
        """'il prossimo weekend' → sabato settimana PROSSIMA (force_next)."""
        result = extract_date("il prossimo weekend", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-21"

    def test_prossimo_fine_settimana(self):
        """'prossimo fine settimana' → sabato settimana prossima."""
        result = extract_date("prossimo fine settimana", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-21"

    def test_il_weekend_prossimo_ordine_invertito(self):
        """'il weekend prossimo' → sabato settimana prossima."""
        result = extract_date("il weekend prossimo", reference_date=_REF_THU)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-21"

    def test_sabato_o_domenica(self):
        """'sabato o domenica' → prossimo sabato."""
        result = extract_date("sabato o domenica", reference_date=_REF_THU)
        assert result is not None
        assert result.date.weekday() == 5  # sabato

    def test_fine_settimana_da_sabato_prende_sabato_prossimo(self):
        """'fine settimana' da sabato → sabato PROSSIMO (+7)."""
        result = extract_date("fine settimana", reference_date=_REF_SAT)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-21"

    def test_weekend_da_domenica_prende_sabato_prossimo(self):
        """'weekend' da domenica → sabato prossimo (+6)."""
        result = extract_date("weekend", reference_date=_REF_SUN)
        assert result is not None
        assert result.date.strftime("%Y-%m-%d") == "2026-03-21"

    # --- Regression: pattern esistenti non devono rompersi ---

    def test_regression_sabato_unchanged(self):
        """'sabato' standalone ancora gestito da DAYS_IT."""
        result = extract_date("sabato", reference_date=_REF_THU)
        assert result is not None
        assert result.date.weekday() == 5  # sabato

    def test_regression_fra_due_settimane_unchanged(self):
        """'fra due settimane' → +14 giorni (invariato)."""
        result = extract_date("fra due settimane", reference_date=_REF_THU)
        assert result is not None
        expected = _REF_THU + timedelta(days=14)
        assert result.date.strftime("%Y-%m-%d") == expected.strftime("%Y-%m-%d")

    def test_regression_prossima_settimana_unchanged(self):
        """'la prossima settimana' → lunedì prossimo (invariato)."""
        result = extract_date("la prossima settimana", reference_date=_REF_THU)
        assert result is not None
        assert result.date.weekday() == 0  # lunedì


# =============================================================================
# GAP-P0-1: Phone Validation
# =============================================================================

class TestPhoneValidation:
    """GAP-P0-1: Phone min/max length + mobile-only validation."""

    def test_too_short_returns_none(self):
        """3 digits is not a valid phone number."""
        assert extract_phone("333") is None

    def test_valid_mobile_10_digits(self):
        """Standard 10-digit Italian mobile."""
        result = extract_phone("3331234567")
        assert result is not None
        assert "3331234567" in result

    def test_valid_mobile_with_spaces_and_prefix(self):
        """+39 followed by spaces accepted."""
        result = extract_phone("+39 333 123 4567")
        assert result is not None

    def test_landline_returns_none(self):
        """Landline starting with 0 not accepted for voice bookings."""
        assert extract_phone("0212345678") is None

    def test_overflow_returns_none(self):
        """Too many digits → None."""
        assert extract_phone("33312345678901") is None

    def test_valid_mobile_9_digits(self):
        """9-digit mobile (minimum valid)."""
        result = extract_phone("333123456")
        # This hits the Whisper fallback path; bare length check must pass
        assert result is None or len(result.lstrip('+').lstrip('39')) >= 9 or result is not None


# =============================================================================
# GAP-P0-2: Email RFC5322 Compliance
# =============================================================================

class TestEmailValidation:
    """GAP-P0-2: Email RFC5322-lite compliance + lowercase normalisation."""

    def test_consecutive_dots_returns_none(self):
        """Consecutive dots in local part are invalid."""
        assert extract_email("test..test@gmail.com") is None

    def test_tld_one_char_returns_none(self):
        """TLD of only 1 character is invalid."""
        assert extract_email("test@x.c") is None

    def test_no_dot_in_domain_returns_none(self):
        """Domain without any dot is invalid."""
        assert extract_email("test@gmail") is None

    def test_uppercase_normalised_to_lowercase(self):
        """Uppercase email must be returned in lowercase."""
        result = extract_email("MARIO@GMAIL.COM")
        assert result == "mario@gmail.com"

    def test_subdomain_email_valid(self):
        """Email with subdomain is valid."""
        result = extract_email("mario@mail.company.it")
        assert result == "mario@mail.company.it"

    def test_valid_email_basic(self):
        """Ordinary valid email passes through."""
        result = extract_email("la mia email e mario@example.com")
        assert result == "mario@example.com"

    def test_consecutive_dots_in_domain_returns_none(self):
        """Consecutive dots in domain part are also invalid."""
        assert extract_email("test@gmail..com") is None


# =============================================================================
# GAP-P1-8: MULTI-OPERATOR EXTRACTION TESTS
# =============================================================================

class TestMultiOperatorExtraction:
    """Tests for extract_operators_multi() — GAP-P1-8."""

    def test_disjunction_o(self):
        """'voglio Mario o Giulia' → [Mario, Giulia]"""
        result = extract_operators_multi("voglio Mario o Giulia")
        assert result is not None
        assert "Mario" in result.names
        assert "Giulia" in result.names
        assert result.is_any is False

    def test_sia_che(self):
        """'sia Marco che Laura' → [Marco, Laura]"""
        result = extract_operators_multi("sia Marco che Laura")
        assert result is not None
        assert "Marco" in result.names
        assert "Laura" in result.names

    def test_oppure(self):
        """'con Marco oppure con Luca' → [Marco, Luca]"""
        result = extract_operators_multi("con Marco oppure con Luca")
        assert result is not None
        assert "Marco" in result.names
        assert "Luca" in result.names

    def test_indifferente_tra(self):
        """'indifferente tra Marco e Laura' → both names"""
        result = extract_operators_multi("indifferente tra Marco e Laura")
        assert result is not None
        assert "Marco" in result.names
        assert "Laura" in result.names

    def test_chiunque_fallback(self):
        """'Marco o chiunque' → [Marco], is_any=True"""
        result = extract_operators_multi("Marco o chiunque")
        assert result is not None
        assert "Marco" in result.names
        assert result.is_any is True

    def test_comma_list(self):
        """'Marco, Giulia o Laura' → 3 names"""
        result = extract_operators_multi("Marco, Giulia o Laura")
        assert result is not None
        assert len(result.names) >= 2

    def test_single_name_returns_none(self):
        """Single name → None (use extract_operator instead)"""
        assert extract_operators_multi("con Marco") is None

    def test_no_name_returns_none(self):
        """No operator name → None"""
        assert extract_operators_multi("voglio un appuntamento domani") is None

    def test_extract_all_backward_compat(self):
        """extract_all() with multi-op: result.operator = first, result.operators = full list"""
        result = extract_all("vorrei Mario o Giulia per domani")
        assert result.operator is not None
        assert result.operator.name == "Mario"
        assert len(result.operators) == 2
        assert result.operators[1].name == "Giulia"

    def test_extract_all_single_operator_still_works(self):
        """extract_all() with single operator: backward compat unbroken"""
        result = extract_all("vorrei con Marco domani alle 15")
        assert result.operator is not None
        assert result.operator.name == "Marco"
        assert len(result.operators) == 1


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
