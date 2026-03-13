"""
GAP-P1-7: Waitlist auto-trigger on cancellation

Tests that cancelling an appointment immediately triggers the waitlist
check instead of waiting for the 5-minute APScheduler cycle.

Note: Tests requiring Orchestrator/main.py (full venv) are marked with
pytest.mark.skipif to allow MacBook runs (limited deps).
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


HAS_FULL_DEPS = False
try:
    import aiohttp  # noqa: F401
    import groq  # noqa: F401 — only available in iMac venv
    HAS_FULL_DEPS = True
except ImportError:
    pass


# ─────────────────────────────────────────────────────────────
# Integration: _cancel_booking triggers waitlist on success
# Requires full venv (iMac only)
# ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(not HAS_FULL_DEPS, reason="requires full voice-agent venv (iMac)")
@pytest.mark.asyncio
async def test_cancel_booking_triggers_waitlist_on_success():
    """After successful cancellation, waitlist check is triggered fire-and-forget."""
    import asyncio as _asyncio
    from unittest.mock import AsyncMock, MagicMock, patch

    # Lazy import to avoid ModuleNotFoundError on MacBook
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.orchestrator import Orchestrator

    orch = Orchestrator.__new__(Orchestrator)
    orch.http_bridge_url = "http://127.0.0.1:3001"
    orch._current_session = None
    orch._wa_client = MagicMock()

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"success": True})
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    triggered = []

    async def fake_waitlist(wa_client):
        triggered.append(wa_client)

    with patch("src.orchestrator.shared_session", return_value=mock_session):
        import src.reminder_scheduler as rs_mod
        original = getattr(rs_mod, "check_and_notify_waitlist", None)
        rs_mod.check_and_notify_waitlist = fake_waitlist
        try:
            result = await orch._cancel_booking("appt-123")
        finally:
            if original:
                rs_mod.check_and_notify_waitlist = original

    assert result.get("success") is True
    await _asyncio.sleep(0.05)
    assert len(triggered) == 1, "Waitlist check should have been triggered once"


@pytest.mark.skipif(not HAS_FULL_DEPS, reason="requires full voice-agent venv (iMac)")
@pytest.mark.asyncio
async def test_cancel_booking_no_waitlist_trigger_on_failure():
    """When cancellation fails (success=False), waitlist check NOT triggered."""
    import asyncio as _asyncio
    from unittest.mock import AsyncMock, MagicMock, patch

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.orchestrator import Orchestrator

    orch = Orchestrator.__new__(Orchestrator)
    orch.http_bridge_url = "http://127.0.0.1:3001"
    orch._current_session = None
    orch._wa_client = MagicMock()

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"success": False, "error": "Not found"})
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    triggered = []

    async def fake_waitlist(wa_client):
        triggered.append(wa_client)

    with patch("src.orchestrator.shared_session", return_value=mock_session):
        import src.reminder_scheduler as rs_mod
        original = getattr(rs_mod, "check_and_notify_waitlist", None)
        rs_mod.check_and_notify_waitlist = fake_waitlist
        try:
            result = await orch._cancel_booking("appt-404")
        finally:
            if original:
                rs_mod.check_and_notify_waitlist = original

    await _asyncio.sleep(0.05)
    assert len(triggered) == 0, "Waitlist check should NOT be triggered on failed cancel"


# ─────────────────────────────────────────────────────────────
# Unit: reminder_scheduler.check_and_notify_waitlist signature
# MacBook-safe (no heavy deps)
# ─────────────────────────────────────────────────────────────

def test_check_and_notify_waitlist_is_async():
    """check_and_notify_waitlist must be an async function."""
    import asyncio
    from reminder_scheduler import check_and_notify_waitlist
    assert asyncio.iscoroutinefunction(check_and_notify_waitlist), (
        "check_and_notify_waitlist must be async for create_task to work"
    )


def test_check_and_notify_waitlist_accepts_none_wa_client():
    """check_and_notify_waitlist must handle wa_client=None gracefully."""
    import asyncio
    from reminder_scheduler import check_and_notify_waitlist
    # Should not raise — just logs warning and skips
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(check_and_notify_waitlist(None))
    except Exception as e:
        pytest.fail(f"check_and_notify_waitlist(None) raised: {e}")
    finally:
        loop.close()
