"""
Tests for TTS text preprocessing — GAP-C1.

Verifies that numeric date formats (DD/MM, DD/MM/YYYY) are expanded
to Italian spoken form before synthesis, so Piper reads "tredici marzo"
instead of "tredici barra tre".
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tts import preprocess_for_tts


class TestDatePreprocessing:
    """GAP-C1: date DD/MM → Italian spoken form."""

    def test_short_date_13_03(self):
        assert preprocess_for_tts("13/03") == "tredici marzo"

    def test_short_date_1_01(self):
        assert preprocess_for_tts("1/01") == "primo gennaio"

    def test_short_date_31_12(self):
        assert preprocess_for_tts("31/12") == "trentuno dicembre"

    def test_full_date_with_year(self):
        assert preprocess_for_tts("13/03/2026") == "tredici marzo duemilaventisei"

    def test_date_in_sentence(self):
        result = preprocess_for_tts("Appuntamento il 13/03 alle 10:00")
        assert result == "Appuntamento il tredici marzo alle 10:00"

    def test_full_date_in_sentence(self):
        result = preprocess_for_tts("Conferma per il 25/12/2026 ore 15:00")
        assert result == "Conferma per il venticinque dicembre duemilaventisei ore 15:00"

    def test_booking_confirmation_message(self):
        """Real-world message from _build_booking_confirmation_message."""
        result = preprocess_for_tts(
            "Perfetto! Ho prenotato il taglio per lunedì 13/03 alle 15:30. Confermo?"
        )
        assert "tredici marzo" in result
        assert "13/03" not in result

    def test_invalid_date_untouched(self):
        """Invalid ranges should not be expanded."""
        assert preprocess_for_tts("40/15") == "40/15"

    def test_all_months(self):
        months = [
            (1, "gennaio"), (2, "febbraio"), (3, "marzo"), (4, "aprile"),
            (5, "maggio"), (6, "giugno"), (7, "luglio"), (8, "agosto"),
            (9, "settembre"), (10, "ottobre"), (11, "novembre"), (12, "dicembre"),
        ]
        for month_num, month_name in months:
            result = preprocess_for_tts(f"15/{month_num:02d}")
            assert month_name in result, f"Month {month_num} → expected '{month_name}' in '{result}'"

    def test_no_date_unchanged(self):
        text = "Buongiorno, come posso aiutarla?"
        assert preprocess_for_tts(text) == text

    def test_phone_expansion_still_works(self):
        """Phone preprocessing should still work alongside date preprocessing."""
        result = preprocess_for_tts("Chiamo il 3807769822")
        assert "3 8 0 7 7 6 9 8 2 2" in result


class TestDatePreprocessingEdgeCases:
    """Edge cases for date TTS preprocessing."""

    def test_multiple_dates_in_text(self):
        result = preprocess_for_tts("Dal 01/03 al 31/03")
        assert "primo marzo" in result
        assert "trentuno marzo" in result
        assert "/" not in result.replace("10:00", "").replace("15:30", "")

    def test_year_2025(self):
        assert preprocess_for_tts("12/01/2025") == "dodici gennaio duemilaventicinque"

    def test_ordinal_primo_for_day_1(self):
        """Day 1 should be 'primo' not 'uno' per Italian grammar."""
        assert preprocess_for_tts("1/03") == "primo marzo"


class TestItalianNumberPreprocessing:
    """Italian number-to-words for TTS (dot-separated thousands)."""

    def test_simple_thousands(self):
        assert "tremila" in preprocess_for_tts("Costa 3.000 euro")

    def test_complex_thousands(self):
        result = preprocess_for_tts("Prezzo: 1.500 euro")
        assert "mille" in result
        assert "cinquecento" in result

    def test_million(self):
        result = preprocess_for_tts("Fatturato di 1.500.000 euro")
        assert "un milione" in result
        assert "cinquecentomila" in result

    def test_price_497(self):
        """Small numbers (< 1000) without dots should stay as digits."""
        assert preprocess_for_tts("Piano Base: 497 euro") == "Piano Base: 497 euro"

    def test_price_897(self):
        assert preprocess_for_tts("Piano Pro: 897 euro") == "Piano Pro: 897 euro"

    def test_mixed_text_and_numbers(self):
        result = preprocess_for_tts("Il taglio costa 3.000 euro e il colore 1.500 euro")
        assert "tremila" in result
        assert "mille" in result
        assert "cinquecento" in result

    def test_date_not_confused_with_number(self):
        """Dates like 13/03 should NOT be treated as numbers."""
        result = preprocess_for_tts("Appuntamento il 13/03 alle 10:00")
        assert "tredici marzo" in result

    def test_phone_not_confused_with_number(self):
        """Phone numbers should still be expanded digit-by-digit."""
        result = preprocess_for_tts("Chiamo il 3807769822")
        assert "3 8 0 7 7 6 9 8 2 2" in result

    def test_number_to_italian_zero(self):
        from tts import _number_to_italian
        assert _number_to_italian(0) == "zero"

    def test_number_to_italian_units(self):
        from tts import _number_to_italian
        assert _number_to_italian(1) == "uno"
        assert _number_to_italian(9) == "nove"
        assert _number_to_italian(19) == "diciannove"

    def test_number_to_italian_tens(self):
        from tts import _number_to_italian
        assert _number_to_italian(21) == "ventuno"
        assert _number_to_italian(28) == "ventotto"
        assert _number_to_italian(50) == "cinquanta"

    def test_number_to_italian_hundreds(self):
        from tts import _number_to_italian
        assert _number_to_italian(100) == "cento"
        assert _number_to_italian(200) == "duecento"
        assert _number_to_italian(497) == "quattrocentonovantasette"

    def test_number_to_italian_thousands(self):
        from tts import _number_to_italian
        assert _number_to_italian(1000) == "mille"
        assert _number_to_italian(3000) == "tremila"

    def test_number_to_italian_million(self):
        from tts import _number_to_italian
        assert _number_to_italian(1000000) == "un milione"
        assert "due milioni" in _number_to_italian(2000000)
