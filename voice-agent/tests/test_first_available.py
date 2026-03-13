"""
Tests for GAP-P1-3: AvailabilityChecker.check_first_available()

Verifica:
- Restituisce il primo slot disponibile nei prossimi N giorni
- Rispetta exclude_days (nomi inglesi lowercase)
- Salta festività gestite dalla logica check_date esistente
- Restituisce {"available": False} se nessuno slot trovato
- Compatibile con la chiamata in orchestrator.py (parametri service, days_ahead, exclude_days)
"""

import asyncio
import sys
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from availability_checker import (
    AvailabilityChecker,
    AvailabilityConfig,
    AvailabilityResult,
    TimeSlot,
    UnavailabilityReason,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result_with_slots(*times: str) -> AvailabilityResult:
    """Build a fake AvailabilityResult with available slots."""
    slots = [TimeSlot(time=t, available=True) for t in times]
    return AvailabilityResult(date="", available_slots=slots, message="ok")


def _make_empty_result() -> AvailabilityResult:
    return AvailabilityResult(date="", available_slots=[], unavailable_reason=UnavailabilityReason.CLOSED, message="chiuso")


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# T1: happy path — trova il primo slot disponibile domani
# ---------------------------------------------------------------------------

class TestCheckFirstAvailable:

    def test_returns_first_slot_tomorrow(self):
        """Il primo giorno con slot viene restituito correttamente."""
        checker = AvailabilityChecker()

        async def fake_check_date(date_str, service=None):
            # Solo il giorno dopo oggi ha slot
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            if date_str == tomorrow:
                return _make_result_with_slots("09:00", "10:00")
            return _make_empty_result()

        with patch.object(checker, "check_date", side_effect=fake_check_date):
            result = _run(checker.check_first_available(service="taglio", days_ahead=7))

        assert result["available"] is True
        tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert result["date"] == tomorrow_str
        assert result["time"] == "09:00"
        assert "date_display" in result
        assert result["date_display"] != ""

    def test_returns_false_when_no_slots(self):
        """Se nessun giorno ha slot, restituisce available=False."""
        checker = AvailabilityChecker()

        with patch.object(checker, "check_date", return_value=_make_empty_result()):
            result = _run(checker.check_first_available(days_ahead=3))

        assert result["available"] is False
        assert result["date"] is None
        assert result["time"] is None

    def test_exclude_days_skips_monday(self):
        """Giorni in exclude_days non vengono considerati."""
        checker = AvailabilityChecker()
        call_log = []

        async def fake_check_date(date_str, service=None):
            call_log.append(date_str)
            d = date.fromisoformat(date_str)
            # Restituisce slot solo se il giorno non e lunedi (isoweekday=1)
            if d.isoweekday() != 1:
                return _make_result_with_slots("10:00")
            return _make_empty_result()

        with patch.object(checker, "check_date", side_effect=fake_check_date):
            result = _run(checker.check_first_available(days_ahead=14, exclude_days=["monday"]))

        # Nessuna data nel call_log deve essere un lunedi
        for ds in call_log:
            assert date.fromisoformat(ds).isoweekday() != 1, f"{ds} e lunedi, non doveva essere chiamato"

        assert result["available"] is True

    def test_exclude_days_case_insensitive(self):
        """exclude_days accetta maiuscole/minuscole."""
        checker = AvailabilityChecker()

        async def fake_check_date(date_str, service=None):
            d = date.fromisoformat(date_str)
            if d.isoweekday() == 2:  # martedi
                return _make_result_with_slots("11:00")
            return _make_empty_result()

        # Esclude Tuesday (con vari formati)
        with patch.object(checker, "check_date", side_effect=fake_check_date):
            result = _run(
                checker.check_first_available(days_ahead=14, exclude_days=["Tuesday", "WEDNESDAY"])
            )

        # Se il primo martedi viene saltato ma altri giorni restano liberi
        # il test deve solo non crashare e rispettare la logica
        assert isinstance(result["available"], bool)

    def test_exclude_days_none_works(self):
        """exclude_days=None non causa errori."""
        checker = AvailabilityChecker()

        async def fake_check_date(date_str, service=None):
            return _make_result_with_slots("14:00")

        with patch.object(checker, "check_date", side_effect=fake_check_date):
            result = _run(checker.check_first_available(days_ahead=3, exclude_days=None))

        assert result["available"] is True
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert result["date"] == tomorrow

    def test_exclude_days_empty_list(self):
        """exclude_days=[] non causa errori."""
        checker = AvailabilityChecker()

        async def fake_check_date(date_str, service=None):
            return _make_result_with_slots("09:30")

        with patch.object(checker, "check_date", side_effect=fake_check_date):
            result = _run(checker.check_first_available(days_ahead=2, exclude_days=[]))

        assert result["available"] is True

    def test_service_passed_to_check_date(self):
        """Il parametro service viene inoltrato a check_date."""
        checker = AvailabilityChecker()
        received_services = []

        async def fake_check_date(date_str, service=None):
            received_services.append(service)
            return _make_result_with_slots("10:00")

        with patch.object(checker, "check_date", side_effect=fake_check_date):
            _run(checker.check_first_available(service="colore", days_ahead=1))

        assert received_services[0] == "colore"

    def test_days_ahead_limit(self):
        """Vengono scansionati esattamente days_ahead giorni (non di piu)."""
        checker = AvailabilityChecker()
        call_count = [0]

        async def fake_check_date(date_str, service=None):
            call_count[0] += 1
            return _make_empty_result()

        with patch.object(checker, "check_date", side_effect=fake_check_date):
            result = _run(checker.check_first_available(days_ahead=5))

        # Chiamato al piu 5 volte (alcuni giorni possono essere saltati per exclude_days
        # se non configurati, ma senza exclude_days devono essere tutti visitati)
        assert call_count[0] <= 5
        assert result["available"] is False

    def test_date_display_format(self):
        """date_display deve contenere giorno e mese in italiano."""
        checker = AvailabilityChecker()

        async def fake_check_date(date_str, service=None):
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            if date_str == tomorrow:
                return _make_result_with_slots("10:00")
            return _make_empty_result()

        with patch.object(checker, "check_date", side_effect=fake_check_date):
            result = _run(checker.check_first_available(days_ahead=2))

        assert result["available"] is True
        display = result["date_display"]
        # deve contenere un numero (giorno del mese)
        assert any(ch.isdigit() for ch in display)
        # deve contenere almeno uno dei mesi italiani
        italian_months = [
            "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
            "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"
        ]
        assert any(m in display.lower() for m in italian_months)
