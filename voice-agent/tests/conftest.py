"""Shared pytest fixtures for deterministic voice-agent unit tests.

The production booking FSM now requires caller identity before moving from a
selected service to date collection.  Older booking-flow tests in
``test_booking_state_machine.py`` intentionally exercise service/date/time
transitions in isolation, so those scenarios need an already identified
client.  Identity-specific tests remain untouched and still start anonymous.
"""

import pytest


_LEGACY_IDENTIFIED_FLOW_CLASSES = {
    "TestNormalBookingFlow",
    "TestStateTransitions",
    "TestInterruptionHandling",
    "TestConfirmationChanges",
    "TestEntityExtractionIntegration",
}


@pytest.fixture(autouse=True)
def identified_client_for_legacy_booking_flow(request, monkeypatch):
    """Give legacy booking-only scenarios the identity they assume.

    This does not skip or relax any assertion and does not alter production
    code.  It only makes the precondition explicit for tests written before
    the name/surname identity gate was introduced.
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
    if not callable(original_factory):
        return

    def create_identified_state_machine():
        sm = original_factory()
        sm.context.client_id = "test-client"
        sm.context.client_name = "Test"
        sm.context.client_surname = "Client"
        return sm

    monkeypatch.setattr(module, "create_state_machine", create_identified_state_machine)
