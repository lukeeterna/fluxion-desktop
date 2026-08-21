"""P0 escalation contract: live SIP first, WhatsApp only as fallback."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.orchestrator import VoiceOrchestrator


def _orchestrator():
    o = VoiceOrchestrator.__new__(VoiceOrchestrator)
    o._is_voip_call = True
    o._resolve_escalation_contacts = AsyncMock(return_value=(
        "3399999999", "impostazioni.telefono_titolare",
        "3331234567", "voice_agent_config.numero_trasferimento",
    ))
    o._resolve_live_transfer_routes = AsyncMock(return_value=[("3331234567", "operator:op-1")])
    o._last_live_transfer_routes = []
    o._last_bridge_business_open = True
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
async def test_bridge_closed_overrides_python_open_for_voip_escalation():
    o = _orchestrator()

    async def closed_routes():
        o._last_bridge_business_open = False
        return []

    o._resolve_live_transfer_routes = AsyncMock(side_effect=closed_routes)
    o._is_business_hours = MagicMock(return_value=True)
    phone = await o._trigger_wa_escalation_call("explicit_request")

    assert phone == "3331234567"
    o._wa_client.send_message_async.assert_awaited_once()
    sent_message = o._wa_client.send_message_async.await_args.args[1]
    assert "NON URGENTE (fuori orario)" in sent_message


@pytest.mark.asyncio
async def test_bridge_open_overrides_python_closed_and_keeps_live_transfer_first():
    o = _orchestrator()

    async def open_routes():
        o._last_bridge_business_open = True
        return [("3331234567", "operator:op-1")]

    o._resolve_live_transfer_routes = AsyncMock(side_effect=open_routes)
    o._is_business_hours = MagicMock(return_value=False)
    phone = await o._trigger_wa_escalation_call("explicit_request")

    assert phone == "3331234567"
    o._wa_client.send_message_async.assert_not_called()
    assert o._live_transfer_business_open() is True


@pytest.mark.asyncio
async def test_resolver_records_bridge_closed_and_rejects_routes_when_closed():
    o = _orchestrator()
    o._last_bridge_business_open = None
    o._fetch_escalation_route_payload = AsyncMock(return_value={
        "business_open": False,
        "routes": [{"phone": "3331234567", "source": "operator:op-1"}],
    })

    routes = await VoiceOrchestrator._resolve_live_transfer_routes(o)

    assert routes == []
    assert o._last_bridge_business_open is False


@pytest.mark.asyncio
async def test_owner_contact_is_private_notification_only():
    o = _orchestrator()
    o._fetch_escalation_route_payload = AsyncMock(return_value={
        "notification_phone": "3399999999",
        "notification_source": "impostazioni.telefono_titolare",
        "fallback_phone": "3331234567",
        "fallback_source": "voice_agent_config.numero_trasferimento",
    })

    notify, notify_src, public, public_src = await VoiceOrchestrator._resolve_escalation_contacts(o)

    assert notify == "3399999999"
    assert notify_src == "impostazioni.telefono_titolare"
    assert public == "3331234567"
    assert public_src == "voice_agent_config.numero_trasferimento"


@pytest.mark.asyncio
async def test_owner_only_contact_is_never_returned_to_caller():
    o = _orchestrator()
    o._fetch_escalation_route_payload = AsyncMock(return_value={
        "notification_phone": "3399999999",
        "notification_source": "impostazioni.telefono_titolare",
        "fallback_phone": None,
        "fallback_source": None,
    })

    notify, _notify_src, public, _public_src = await VoiceOrchestrator._resolve_escalation_contacts(o)

    assert notify == "3399999999"
    assert public is None


def test_voip_live_route_does_not_require_public_fallback_to_offer_transfer():
    o = _orchestrator()
    o._last_live_transfer_routes = [("3331234567", "operator:op-1")]
    text = o._build_escalation_response("", True)
    assert "passarla" in text.lower()
    assert "3399999999" not in text


def test_voip_without_live_route_never_promises_hold_line_transfer():
    o = _orchestrator()
    o._last_live_transfer_routes = []
    text = o._build_escalation_response("3331234567", True)
    assert "rimanga in linea" not in text.lower()
    assert "3331234567" in text


@pytest.mark.asyncio
async def test_force_notify_sends_whatsapp_after_live_transfer_failure():
    o = _orchestrator()
    phone = await o._trigger_wa_escalation_call("live_transfer_busy", force_notify=True)
    assert phone == "3331234567"
    o._wa_client.send_message_async.assert_awaited_once()
    o._wa_client.normalize_phone.assert_called_once_with("3399999999")
    assert o._last_escalation_wa_sent is True


def test_voip_business_hours_response_does_not_claim_wa_notification():
    o = _orchestrator()
    o._last_live_transfer_routes = [("3331234567", "operator:op-1")]
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
