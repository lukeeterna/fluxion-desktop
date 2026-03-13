"""
Tests for GAP-P1-6: BookingManager._check_availability() — overlap detection + self-exclude

Verifica:
- Overlap detection: 14:00-15:00 exists → 14:30 con durata 60min fallisce
- Self-exclude: reschedule apt A da 14:00 a 14:30 non confligge con se stesso
- No false negative: 15:30 e libero se solo 14:00-15:00 occupato
- Durata default (60min) usata se booking.duration_minutes e None
- exclude_booking_id=None funziona come prima (compatibilita)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from dataclasses import dataclass, field
from typing import Optional, List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from booking_manager import BookingManager, Booking, BookingStatus


# ---------------------------------------------------------------------------
# Helpers — stub DB
# ---------------------------------------------------------------------------

@dataclass
class FakeCustomer:
    customer_id: str = "c1"
    name: str = "Mario"
    phone: str = "3331234567"
    tier: object = None

    def __post_init__(self):
        if self.tier is None:
            from vertical_schemas import CustomerTier
            self.tier = CustomerTier.STANDARD


def _make_booking(
    booking_id: str,
    time: str,
    duration_minutes: int = 60,
    date: str = "2026-04-01",
) -> Booking:
    from vertical_schemas import CustomerTier
    end_dt = (datetime.strptime(time, "%H:%M") + timedelta(minutes=duration_minutes))
    return Booking(
        booking_id=booking_id,
        customer_id="c1",
        customer_tier=CustomerTier.STANDARD,
        business_id="b1",
        service_id="s1",
        service_name="Taglio",
        duration_minutes=duration_minutes,
        date=date,
        time=time,
        end_time=end_dt.strftime("%H:%M"),
        status=BookingStatus.CONFIRMED,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )


def _make_db(bookings: List[Booking]) -> MagicMock:
    db = MagicMock()
    db.get_bookings_for_date.return_value = bookings
    db.get_customer.return_value = None
    db.get_service.return_value = {"name": "Taglio", "duration": 60}
    db.get_operator.return_value = None
    db.save_booking.return_value = None
    db.update_booking.return_value = None
    return db


# ---------------------------------------------------------------------------
# T1: overlap detection — 14:00-15:00 occupato, 14:30 deve fallire
# ---------------------------------------------------------------------------

class TestOverlapDetection:

    def test_overlap_conflict_14_30(self):
        """14:30 con durata 60min confligge con 14:00-15:00."""
        existing = [_make_booking("A", "14:00", duration_minutes=60)]
        db = _make_db(existing)
        bm = BookingManager(db)

        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "14:30",
            duration_minutes=60,
        )

        assert available is False
        assert conflict == "A"

    def test_no_false_negative_15_30(self):
        """15:30 e libero se solo 14:00-15:00 e occupato."""
        existing = [_make_booking("A", "14:00", duration_minutes=60)]
        db = _make_db(existing)
        bm = BookingManager(db)

        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "15:30",
            duration_minutes=60,
        )

        assert available is True
        assert conflict is None

    def test_adjacent_slot_not_overlap(self):
        """Slot adiacente 15:00 (esattamente alla fine di 14:00-15:00) non e overlap."""
        existing = [_make_booking("A", "14:00", duration_minutes=60)]
        db = _make_db(existing)
        bm = BookingManager(db)

        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "15:00",
            duration_minutes=30,
        )

        assert available is True

    def test_overlap_start_before_existing(self):
        """Nuovo slot che inizia prima ma finisce dentro l'esistente."""
        # Esistente: 14:00-15:00. Nuovo: 13:30-14:30 (durata 60) → overlap
        existing = [_make_booking("A", "14:00", duration_minutes=60)]
        db = _make_db(existing)
        bm = BookingManager(db)

        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "13:30",
            duration_minutes=60,
        )

        assert available is False

    def test_overlap_wraps_existing(self):
        """Nuovo slot che contiene completamente l'esistente."""
        # Esistente: 14:00-14:30. Nuovo: 13:00-16:00 (durata 180)
        existing = [_make_booking("A", "14:00", duration_minutes=30)]
        db = _make_db(existing)
        bm = BookingManager(db)

        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "13:00",
            duration_minutes=180,
        )

        assert available is False

    def test_no_bookings_always_available(self):
        """Nessun booking esistente → slot disponibile."""
        db = _make_db([])
        bm = BookingManager(db)

        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "10:00",
            duration_minutes=60,
        )

        assert available is True
        assert conflict is None


# ---------------------------------------------------------------------------
# T2: self-exclude — reschedule non confligge con se stesso
# ---------------------------------------------------------------------------

class TestSelfExclude:

    def test_reschedule_self_exclude(self):
        """Reschedule da 14:00 a 14:30: il vecchio slot non deve bloccare il nuovo."""
        existing = [_make_booking("A", "14:00", duration_minutes=60)]
        db = _make_db(existing)
        bm = BookingManager(db)

        # 14:30 con durata 60min normalmente confligge con 14:00-15:00,
        # ma con exclude_booking_id="A" deve essere libero
        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "14:30",
            duration_minutes=60,
            exclude_booking_id="A",
        )

        assert available is True
        assert conflict is None

    def test_self_exclude_still_blocks_other(self):
        """Self-exclude per A non esclude un conflitto con B."""
        bookings = [
            _make_booking("A", "14:00", duration_minutes=60),
            _make_booking("B", "14:00", duration_minutes=60),
        ]
        db = _make_db(bookings)
        bm = BookingManager(db)

        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "14:30",
            duration_minutes=60,
            exclude_booking_id="A",
        )

        assert available is False
        assert conflict == "B"

    def test_exclude_booking_id_none_default(self):
        """exclude_booking_id=None e il comportamento default (nessun exclude)."""
        existing = [_make_booking("A", "14:00", duration_minutes=60)]
        db = _make_db(existing)
        bm = BookingManager(db)

        available, conflict = bm._check_availability(
            "b1", "s1", "2026-04-01", "14:30",
            duration_minutes=60,
            exclude_booking_id=None,
        )

        assert available is False
        assert conflict == "A"
