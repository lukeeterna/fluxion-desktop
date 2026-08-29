"""Shared pytest fixtures for deterministic voice-agent unit tests.

The production booking FSM now requires caller identity before moving from a
selected service to date collection. Older booking-flow tests in
``test_booking_state_machine.py`` intentionally exercise service/date/time
transitions in isolation, so those scenarios need an already identified
client. Those legacy tests also use a fixed January 2026 reference date; the
production date-integrity guard uses ``date.today()``, therefore the test clock
must be frozen to the same reference date to keep relative dates deterministic.
Identity-specific tests remain untouched and still start anonymous.
"""

import sys
from datetime import date as _real_date

import pytest


_LEGACY_IDENTIFIED_FLOW_CLASSES = {
    "TestNormalBookingFlow",
    "TestStateTransitions",
    "TestInterruptionHandling",
    "TestConfirmationChanges",
    "TestEntityExtractionIntegration",
    "TestErrorHandling",
    "TestConfirmationVariations",
}


@pytest.fixture(autouse=True)
def identified_client_for_legacy_booking_flow(request, monkeypatch):
    """Provide the explicit preconditions assumed by legacy booking tests.

    This does not skip or relax assertions and does not alter production code.
    It supplies an already identified client for booking-only scenarios and
    freezes the FSM's notion of today to the file's fixed ``REFERENCE_DATE`` so
    that inputs such as ``domani`` remain inside the production booking horizon.
    """
    module = getattr(request, "module", None)
    cls = getattr(request, "cls", None)
    if module is None or module.__name__.split(".")[-1] != "test_booking_state_machine":
        return

    class_name = cls.__name__ if cls is not None else ""
    if class_name not in _LEGACY_IDENTIFIED_FLOW_CLASSES:
        return

    # This scenario validates name extraction itself and must remain anonymous.
    if request.node.name == "test_name_extraction":
        return

    original_factory = getattr(module, "create_state_machine", None)
    booking_state_machine_cls = getattr(module, "BookingStateMachine", None)
    reference_date = getattr(module, "REFERENCE_DATE", None)
    if not callable(original_factory) or booking_state_machine_cls is None or reference_date is None:
        return

    fsm_module = sys.modules[booking_state_machine_cls.__module__]
    reference_day = reference_date.date()

    class FixedDate(_real_date):
        @classmethod
        def today(cls):
            return cls(reference_day.year, reference_day.month, reference_day.day)

    # _set_context_date() uses the module-level ``date.today()``. Patch only for
    # this legacy test invocation; monkeypatch restores the real clock afterward.
    monkeypatch.setattr(fsm_module, "date", FixedDate)

    def create_identified_state_machine():
        sm = original_factory()
        sm.context.client_id = "test-client"
        sm.context.client_name = "Test"
        sm.context.client_surname = "Client"
        return sm

    monkeypatch.setattr(module, "create_state_machine", create_identified_state_machine)
