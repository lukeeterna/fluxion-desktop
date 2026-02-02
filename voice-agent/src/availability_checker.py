"""
FLUXION Voice Agent - Availability Checker

Enterprise-grade availability checking module.
Handles time slots, pausa pranzo, giorni festivi, and booking constraints.

Features:
- Opening hours validation
- Lunch break (pausa pranzo) handling
- Holiday/closure calendar
- Min/max advance booking constraints
- Operator-specific availability
- Slot duration by service type
"""

import aiohttp
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, time, timedelta
from enum import Enum


# Default HTTP Bridge URL
HTTP_BRIDGE_URL = "http://127.0.0.1:3001"


class UnavailabilityReason(Enum):
    """Reasons for slot unavailability."""
    AVAILABLE = "available"
    CLOSED = "closed"
    LUNCH_BREAK = "lunch_break"
    HOLIDAY = "holiday"
    ALREADY_BOOKED = "already_booked"
    TOO_SOON = "too_soon"          # Less than min_advance_hours
    TOO_FAR = "too_far"            # More than max_advance_days
    OPERATOR_UNAVAILABLE = "operator_unavailable"
    OUTSIDE_HOURS = "outside_hours"


@dataclass
class TimeSlot:
    """A time slot with availability info."""
    time: str  # HH:MM format
    available: bool = True
    reason: UnavailabilityReason = UnavailabilityReason.AVAILABLE
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None


@dataclass
class AvailabilityConfig:
    """Configuration for availability checking."""
    opening_time: str = "09:00"
    closing_time: str = "19:00"
    lunch_start: str = "13:00"
    lunch_end: str = "14:00"
    slot_duration_minutes: int = 30
    min_advance_hours: int = 2
    max_advance_days: int = 60
    working_days: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5, 6])  # Mon=1..Sat=6
    holidays: List[str] = field(default_factory=list)  # YYYY-MM-DD format

    # Service-specific durations (minutes)
    service_durations: Dict[str, int] = field(default_factory=lambda: {
        "taglio": 30,
        "piega": 45,
        "colore": 90,
        "barba": 20,
        "trattamento": 60,
    })


@dataclass
class AvailabilityResult:
    """Result of availability check."""
    date: str  # YYYY-MM-DD
    available_slots: List[TimeSlot]
    unavailable_reason: Optional[UnavailabilityReason] = None
    message: str = ""
    suggestions: List[str] = field(default_factory=list)

    @property
    def has_slots(self) -> bool:
        return len(self.available_slots) > 0

    def get_slot_times(self) -> List[str]:
        """Get list of available time strings."""
        return [slot.time for slot in self.available_slots if slot.available]


# Response templates
TEMPLATES = {
    "slots_available": "Per il {date}, abbiamo disponibilita alle {slots}. Quale orario preferisce?",
    "no_slots": "Mi dispiace, per il {date} non ci sono piu posti disponibili. Vuole provare un altro giorno?",
    "closed": "Mi dispiace, {date} siamo chiusi. Vuole un altro giorno?",
    "holiday": "Mi dispiace, {date} siamo chiusi per festivita. Le propongo {alternative}?",
    "too_soon": "Mi dispiace, per le prenotazioni serve un preavviso di almeno {hours} ore. Vuole prenotare per un altro momento?",
    "too_far": "Le prenotazioni sono possibili fino a {days} giorni in anticipo. Vuole scegliere una data piu vicina?",
    "lunch_break": "Alle {time} siamo in pausa pranzo. Posso proporle le {slots}?",
    "operator_busy": "{operator} non e disponibile il {date}. Le propongo {alternatives}?",
    "suggest_alternative": "Le propongo invece {alternative}. Va bene?",
}


class AvailabilityChecker:
    """
    Enterprise availability checker.

    Validates and finds available time slots considering:
    - Business hours
    - Lunch breaks
    - Holidays
    - Existing bookings
    - Operator schedules
    - Service durations
    """

    def __init__(
        self,
        config: Optional[AvailabilityConfig] = None,
        http_bridge_url: str = HTTP_BRIDGE_URL
    ):
        self.config = config or AvailabilityConfig()
        self.http_bridge_url = http_bridge_url

    async def check_date(
        self,
        date_str: str,
        service: Optional[str] = None,
        operator_id: Optional[str] = None
    ) -> AvailabilityResult:
        """
        Check availability for a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format
            service: Optional service type for duration calculation
            operator_id: Optional operator ID to filter

        Returns:
            AvailabilityResult with available slots
        """
        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return AvailabilityResult(
                date=date_str,
                available_slots=[],
                unavailable_reason=UnavailabilityReason.CLOSED,
                message="Data non valida"
            )

        # Check if date is too far in advance
        days_ahead = (check_date - date.today()).days
        if days_ahead > self.config.max_advance_days:
            return AvailabilityResult(
                date=date_str,
                available_slots=[],
                unavailable_reason=UnavailabilityReason.TOO_FAR,
                message=TEMPLATES["too_far"].format(days=self.config.max_advance_days)
            )

        # Check if too soon (only for today)
        now = datetime.now()
        if check_date == date.today():
            min_time = now + timedelta(hours=self.config.min_advance_hours)
            # Will filter slots below
        else:
            min_time = None

        # Check working day
        weekday = check_date.isoweekday()  # Mon=1..Sun=7
        if weekday not in self.config.working_days:
            return AvailabilityResult(
                date=date_str,
                available_slots=[],
                unavailable_reason=UnavailabilityReason.CLOSED,
                message=TEMPLATES["closed"].format(date=self._format_date_italian(check_date)),
                suggestions=self._suggest_alternative_dates(check_date, 3)
            )

        # Check holidays
        if date_str in self.config.holidays:
            alternatives = self._suggest_alternative_dates(check_date, 2)
            return AvailabilityResult(
                date=date_str,
                available_slots=[],
                unavailable_reason=UnavailabilityReason.HOLIDAY,
                message=TEMPLATES["holiday"].format(
                    date=self._format_date_italian(check_date),
                    alternative=alternatives[0] if alternatives else "un altro giorno"
                ),
                suggestions=alternatives
            )

        # Generate time slots
        service_duration = self.config.service_durations.get(
            service or "taglio",
            self.config.slot_duration_minutes
        )
        slots = self._generate_slots(check_date, service_duration)

        # Filter by min advance time
        if min_time:
            slots = [s for s in slots if self._time_to_datetime(check_date, s.time) >= min_time]

        # Get booked slots from database
        booked_slots = await self._get_booked_slots(date_str, operator_id)

        # Mark booked slots as unavailable
        for slot in slots:
            if slot.time in booked_slots:
                slot.available = False
                slot.reason = UnavailabilityReason.ALREADY_BOOKED

        # Get available slots
        available = [s for s in slots if s.available]

        if not available:
            suggestions = self._suggest_alternative_dates(check_date, 3)
            return AvailabilityResult(
                date=date_str,
                available_slots=[],
                unavailable_reason=UnavailabilityReason.ALREADY_BOOKED,
                message=TEMPLATES["no_slots"].format(date=self._format_date_italian(check_date)),
                suggestions=suggestions
            )

        # Format response
        slot_times = [s.time for s in available[:6]]  # Max 6 slots in message
        message = TEMPLATES["slots_available"].format(
            date=self._format_date_italian(check_date),
            slots=", ".join(slot_times[:-1]) + " e " + slot_times[-1] if len(slot_times) > 1 else slot_times[0]
        )

        return AvailabilityResult(
            date=date_str,
            available_slots=available,
            message=message
        )

    async def check_slot(
        self,
        date_str: str,
        time_str: str,
        service: Optional[str] = None,
        operator_id: Optional[str] = None
    ) -> Tuple[bool, UnavailabilityReason, str]:
        """
        Check if a specific slot is available.

        Returns:
            Tuple of (is_available, reason, message)
        """
        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            slot_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return False, UnavailabilityReason.CLOSED, "Data o ora non valida"

        # Check if in opening hours
        opening = datetime.strptime(self.config.opening_time, "%H:%M").time()
        closing = datetime.strptime(self.config.closing_time, "%H:%M").time()

        if slot_time < opening or slot_time >= closing:
            return False, UnavailabilityReason.OUTSIDE_HOURS, f"Siamo aperti dalle {self.config.opening_time} alle {self.config.closing_time}"

        # Check lunch break
        lunch_start = datetime.strptime(self.config.lunch_start, "%H:%M").time()
        lunch_end = datetime.strptime(self.config.lunch_end, "%H:%M").time()

        if lunch_start <= slot_time < lunch_end:
            # Get available slots before and after lunch
            result = await self.check_date(date_str, service, operator_id)
            alternative_slots = [s.time for s in result.available_slots[:3]]
            message = TEMPLATES["lunch_break"].format(
                time=time_str,
                slots=", ".join(alternative_slots) if alternative_slots else "altri orari"
            )
            return False, UnavailabilityReason.LUNCH_BREAK, message

        # Check if already booked
        booked = await self._get_booked_slots(date_str, operator_id)
        if time_str in booked:
            result = await self.check_date(date_str, service, operator_id)
            alternatives = [s.time for s in result.available_slots[:3]]
            message = f"Le {time_str} sono gia occupate. Le propongo {', '.join(alternatives)}?" if alternatives else f"Le {time_str} sono gia occupate."
            return False, UnavailabilityReason.ALREADY_BOOKED, message

        return True, UnavailabilityReason.AVAILABLE, "Disponibile!"

    async def check_operator_availability(
        self,
        operator_id: str,
        date_str: str,
        time_str: Optional[str] = None
    ) -> Tuple[bool, List[str], List[Dict]]:
        """
        Check operator availability for a date/time.

        Returns:
            Tuple of (is_available, available_slots, alternative_operators)
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/operatori/disponibilita"
                data = {
                    "operatore_id": operator_id,
                    "data": date_str,
                    "ora": time_str
                }
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return (
                            result.get("disponibile", False),
                            result.get("slots", []),
                            result.get("alternative_operators", [])
                        )
        except Exception as e:
            print(f"Error checking operator availability: {e}")

        return False, [], []

    async def check_week(
        self,
        week_offset: int = 1,
        service: Optional[str] = None,
        operator_id: Optional[str] = None,
        reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Check availability for an entire week.

        Args:
            week_offset: 0=this week, 1=next week, 2=in two weeks
            service: Optional service for duration calculation
            operator_id: Optional operator filter
            reference_date: Reference date (default: today)

        Returns:
            Dict with 'available_days' list and 'week_start' date string
        """
        ref = reference_date or date.today()
        day_names = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato"]

        # Calculate Monday of target week
        current_weekday = ref.isoweekday()  # Mon=1..Sun=7
        if week_offset == 0:
            # This week — start from Monday of current week
            monday = ref - timedelta(days=current_weekday - 1)
        else:
            # Next week(s) — days until next Monday + (offset-1) weeks
            days_to_monday = 8 - current_weekday  # days until next Monday
            monday = ref + timedelta(days=days_to_monday + (week_offset - 1) * 7)

        available_days = []
        for i in range(6):  # Mon-Sat (6 days)
            d = monday + timedelta(days=i)
            # Skip past dates
            if d <= ref:
                continue
            d_str = d.strftime("%Y-%m-%d")
            result = await self.check_date(d_str, service, operator_id)
            if result.has_slots:
                available_days.append({
                    "date": d_str,
                    "day_name": day_names[i],
                    "slot_count": len(result.available_slots)
                })

        return {
            "available_days": available_days,
            "week_start": monday.strftime("%Y-%m-%d")
        }

    def _generate_slots(self, check_date: date, duration_minutes: int) -> List[TimeSlot]:
        """Generate time slots for a day, excluding lunch break."""
        slots = []

        opening = datetime.strptime(self.config.opening_time, "%H:%M")
        closing = datetime.strptime(self.config.closing_time, "%H:%M")
        lunch_start = datetime.strptime(self.config.lunch_start, "%H:%M")
        lunch_end = datetime.strptime(self.config.lunch_end, "%H:%M")

        current = opening
        while current < closing:
            time_str = current.strftime("%H:%M")

            # Check if in lunch break
            if lunch_start <= current < lunch_end:
                slots.append(TimeSlot(
                    time=time_str,
                    available=False,
                    reason=UnavailabilityReason.LUNCH_BREAK
                ))
            else:
                slots.append(TimeSlot(time=time_str))

            current += timedelta(minutes=duration_minutes)

        return slots

    async def _get_booked_slots(
        self,
        date_str: str,
        operator_id: Optional[str] = None
    ) -> List[str]:
        """Get list of booked time slots for a date."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/occupati"
                params = {"data": date_str}
                if operator_id:
                    params["operatore_id"] = operator_id

                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("slots", [])
        except Exception:
            pass

        return []

    def _suggest_alternative_dates(self, from_date: date, count: int) -> List[str]:
        """Suggest next available dates."""
        alternatives = []
        check = from_date + timedelta(days=1)
        attempts = 0
        max_attempts = 14  # Look up to 2 weeks ahead

        while len(alternatives) < count and attempts < max_attempts:
            weekday = check.isoweekday()
            date_str = check.strftime("%Y-%m-%d")

            if weekday in self.config.working_days and date_str not in self.config.holidays:
                alternatives.append(self._format_date_italian(check))

            check += timedelta(days=1)
            attempts += 1

        return alternatives

    def _format_date_italian(self, d: date) -> str:
        """Format date in Italian."""
        days = ["lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato", "domenica"]
        months = [
            "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
            "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"
        ]
        return f"{days[d.weekday()]} {d.day} {months[d.month - 1]}"

    def _time_to_datetime(self, d: date, time_str: str) -> datetime:
        """Combine date and time string to datetime."""
        t = datetime.strptime(time_str, "%H:%M").time()
        return datetime.combine(d, t)


# Singleton instance
_checker: Optional[AvailabilityChecker] = None


def get_availability_checker(config: Optional[AvailabilityConfig] = None) -> AvailabilityChecker:
    """Get singleton availability checker."""
    global _checker
    if _checker is None or config is not None:
        _checker = AvailabilityChecker(config)
    return _checker


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import asyncio

    async def test():
        checker = AvailabilityChecker()

        # Test date check
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"Checking availability for {tomorrow}")
        print("-" * 40)

        result = await checker.check_date(tomorrow, "taglio")
        print(f"Message: {result.message}")
        print(f"Available slots: {result.get_slot_times()[:5]}...")

        # Test slot check (lunch break)
        print("\n" + "=" * 40)
        print("Testing lunch break (13:30)")
        available, reason, msg = await checker.check_slot(tomorrow, "13:30", "taglio")
        print(f"Available: {available}")
        print(f"Reason: {reason.value}")
        print(f"Message: {msg}")

    asyncio.run(test())
