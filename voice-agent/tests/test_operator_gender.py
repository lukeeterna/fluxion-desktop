"""Tests for GAP-P1-4: Operator gender preference extraction and filtering."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from operator_gender import extract_operator_gender_preference


class TestExtractOperatorGenderPreference:
    """Unit tests for extract_operator_gender_preference()."""

    # ── Feminine ─────────────────────────────────────────────────
    def test_operatrice(self):
        assert extract_operator_gender_preference("vorrei un'operatrice") == "F"

    def test_una_donna(self):
        assert extract_operator_gender_preference("preferirei una donna") == "F"

    def test_una_donna_variant(self):
        assert extract_operator_gender_preference("voglio una donna grazie") == "F"

    def test_femmina(self):
        assert extract_operator_gender_preference("preferisco femmina") == "F"

    def test_femminile(self):
        assert extract_operator_gender_preference("un operatore femminile per favore") == "F"

    def test_con_operatrice(self):
        assert extract_operator_gender_preference("vorrei prenotare con un'operatrice") == "F"

    def test_con_una_donna(self):
        assert extract_operator_gender_preference("mi trovo meglio con una donna") == "F"

    def test_preferisco_donna(self):
        assert extract_operator_gender_preference("preferisco una donna se possibile") == "F"

    # ── Masculine ────────────────────────────────────────────────
    def test_un_uomo(self):
        assert extract_operator_gender_preference("vorrei un uomo") == "M"

    def test_uomo_solo(self):
        assert extract_operator_gender_preference("mi serve un uomo per il trattamento") == "M"

    def test_maschio(self):
        assert extract_operator_gender_preference("preferirei un maschio") == "M"

    def test_operatore_uomo(self):
        assert extract_operator_gender_preference("con un operatore uomo grazie") == "M"

    def test_con_un_uomo(self):
        assert extract_operator_gender_preference("mi trovo meglio con un uomo") == "M"

    # ── No preference / ambiguous ─────────────────────────────────
    def test_no_preference_generic(self):
        assert extract_operator_gender_preference("buongiorno vorrei prenotare") is None

    def test_no_preference_operatore_alone(self):
        # "operatore" alone without gender indicator → no preference
        assert extract_operator_gender_preference("parlare con un operatore") is None

    def test_no_preference_name(self):
        assert extract_operator_gender_preference("vorrei con Marco") is None

    def test_empty_string(self):
        assert extract_operator_gender_preference("") is None

    def test_no_preference_service(self):
        assert extract_operator_gender_preference("un taglio per favore") is None

    def test_case_insensitive_feminine(self):
        assert extract_operator_gender_preference("OPERATRICE per favore") == "F"

    def test_case_insensitive_masculine(self):
        assert extract_operator_gender_preference("Preferirei UN UOMO") == "M"


class TestGenderFilteringLogic:
    """Test gender filtering logic (unit test of the filtering step)."""

    def _filter_operators(self, operators, gender_pref):
        """Replicate the filtering logic from orchestrator."""
        if not gender_pref:
            return operators
        filtered = [op for op in operators if op.get("genere") == gender_pref]
        return filtered if filtered else operators

    def test_filter_keeps_matching_gender(self):
        ops = [
            {"id": "1", "nome": "Anna", "genere": "F"},
            {"id": "2", "nome": "Marco", "genere": "M"},
        ]
        result = self._filter_operators(ops, "F")
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_fallback_when_no_match(self):
        ops = [
            {"id": "1", "nome": "Marco", "genere": "M"},
            {"id": "2", "nome": "Luca", "genere": "M"},
        ]
        # Prefer F but none available → return all
        result = self._filter_operators(ops, "F")
        assert len(result) == 2

    def test_filter_none_preference(self):
        ops = [
            {"id": "1", "nome": "Anna", "genere": "F"},
            {"id": "2", "nome": "Marco", "genere": "M"},
        ]
        result = self._filter_operators(ops, None)
        assert len(result) == 2

    def test_filter_null_genere_excluded(self):
        ops = [
            {"id": "1", "nome": "Anna", "genere": "F"},
            {"id": "2", "nome": "Senza genere", "genere": None},
        ]
        result = self._filter_operators(ops, "F")
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_multiple_matching(self):
        ops = [
            {"id": "1", "nome": "Anna", "genere": "F"},
            {"id": "2", "nome": "Maria", "genere": "F"},
            {"id": "3", "nome": "Marco", "genere": "M"},
        ]
        result = self._filter_operators(ops, "F")
        assert len(result) == 2
        ids = {op["id"] for op in result}
        assert ids == {"1", "2"}
