"""Shared pytest fixtures for deterministic voice-agent unit tests.

``test_booking_state_machine.py`` defines a fixed January 2026
``REFERENCE_DATE``.  The production FSM also has a date-integrity chokepoint
that consults module-level ``date.today()``.  Freeze that clock for the whole
legacy test module so relative phrases such as ``domani`` and ``venerdì`` are
validated against the same reference date used by the extractor.

The production booking FSM also requires caller identity before moving from a
selected service to date collection.  Older booking-flow classes intentionally
exercise service/date/time transitions in isolation, so only those classes get
an already identified client.  Identity-specific scenarios remain anonymous.
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
def deterministic_booking_state_machine_tests(request, monkeypatch):
    """Supply only the preconditions explicitly assumed by the legacy tests.

    No assertion is skipped or relaxed and production code is not changed.
    Every test in the fixed-date module gets the same deterministic clock; only
    booking-only classes get a synthetic already-identified caller.
    """
    module = getattr(request, "module", None)
    cls = getattr(request, "cls", None)
    if module is None or module.__name__.split(".")[-1] != "test_booking_state_machine":
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

    # Keep the production horizon guard active; only make its clock agree with
    # the test module's explicit REFERENCE_DATE. monkeypatch restores it after
    # each test invocation.
    monkeypatch.setattr(fsm_module, "date", FixedDate)

    class_name = cls.__name__ if cls is not None else ""
    if class_name not in _LEGACY_IDENTIFIED_FLOW_CLASSES:
        return

    # This scenario validates name extraction itself and must remain anonymous.
    if request.node.name == "test_name_extraction":
        return

    def create_identified_state_machine():
        sm = original_factory()
        sm.context.client_id = "test-client"
        sm.context.client_name = "Test"
        sm.context.client_surname = "Client"
        return sm

    monkeypatch.setattr(module, "create_state_machine", create_identified_state_machine)
