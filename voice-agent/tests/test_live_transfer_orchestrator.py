"""P0 escalation contract: live SIP first, WhatsApp only as fallback."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.orchestrator import VoiceOrchestrator


def _orchestrator():
    o = VoiceOrchestrator.__new__(VoiceOrchestrator)
    o._is_voip_call = True
    o._resolve_escalation_phone = AsyncMock(return_value=("3331234567", "voice_agent_config"))
    o._resolve_live_transfer_routes = AsyncMock(return_value=[("3331234567", "operator:op-1")])
    o._last_live_transfer_routes = []
    o._is_business_hours = MagicMock(return_value=True)
    o._wa_client = MagicMock()
    o._wa_client.normalize_phone = MagicMock(return_value="393331234567")
    o._wa_client.send_message_async = AsyncMock(return_value={"success": True})
    o.booking_sm = SimpleNamespace(context=SimpleNamespace(
        client_name="Mario", service_display="Taglio", service="taglio",
        date_display="domani", date="2026-08-18", time_display="10:00", time="10:00",
        client_phone="+393331112222", state=SimpleNamespace(value="WAITING_DATE"),
    ))
    return o


@pytest.mark.asyncio
async def test_in_hours_voip_defers_whatsapp_until_live_transfer_fails():
    o = _orchestrator()
    phone = await o._trigger_wa_escalation_call("explicit_request")
    assert phone == "3331234567"
    o._wa_client.send_message_async.assert_not_called()
    assert o._last_escalation_phone == "3331234567"
    assert o._last_escalation_wa_sent is False


@pytest.mark.asyncio
async def test_force_notify_sends_whatsapp_after_live_transfer_failure():
    o = _orchestrator()
    phone = await o._trigger_wa_escalation_call("live_transfer_busy", force_notify=True)
    assert phone == "3331234567"
    o._wa_client.send_message_async.assert_awaited_once()
    assert o._last_escalation_wa_sent is True


def test_voip_business_hours_response_does_not_claim_wa_notification():
    o = _orchestrator()
    text = o._build_escalation_response("3331234567", True)
    assert "passarla" in text.lower()
    assert "notifica" not in text.lower()
    assert "ricontatteranno" not in text.lower()


@pytest.mark.asyncio
async def test_in_hours_voip_without_live_routes_notifies_whatsapp_immediately():
    o = _orchestrator()
    o._resolve_live_transfer_routes = AsyncMock(return_value=[])
    phone = await o._trigger_wa_escalation_call("explicit_request")
    assert phone == "3331234567"
    o._wa_client.send_message_async.assert_awaited_once()
    assert o._last_escalation_wa_sent is True
