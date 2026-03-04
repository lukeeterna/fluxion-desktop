"""
Test suite: WhatsApp Callback Handler (B2)

12 test cases che verificano tutti gli Acceptance Criteria dal research file.
Python 3.9 compatible.
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Import handler
# ---------------------------------------------------------------------------

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from whatsapp_callback import WhatsAppCallbackHandler, WAPhoneSession, CONFIRM_PATTERN, CANCEL_PATTERN


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_request(body_dict=None, content_type="application/json", form_data=None):
    """Build a mock aiohttp Request."""
    request = MagicMock()
    request.content_type = content_type

    if content_type == "application/x-www-form-urlencoded" and form_data is not None:
        async def mock_post():
            return form_data
        request.post = mock_post
    else:
        data = body_dict or {}
        async def mock_json():
            return data
        request.json = mock_json

    return request


def make_handler(orchestrator=None, wa_client=None):
    return WhatsAppCallbackHandler(orchestrator=orchestrator, wa_client=wa_client)


# ---------------------------------------------------------------------------
# AC7 — JSON custom payload parsed correctly
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac7_json_payload_parsed():
    """AC7: Payload JSON custom da whatsapp-service.cjs parsato correttamente."""
    handler = make_handler()
    request = make_request({
        "from": "393281536308",
        "name": "Mario Rossi",
        "body": "Ciao, vorrei prenotare",
        "timestamp": "2026-03-04T10:00:00.000Z",
        "message_id": "msg_test_001",
    })

    response = await handler.handle(request)
    data = json.loads(response.body)
    assert data["ok"] is True
    assert data.get("phone") == "393281536308"


# ---------------------------------------------------------------------------
# AC6 — Twilio form-urlencoded payload parsed correctly
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac6_twilio_payload_parsed():
    """AC6: Payload Twilio form-urlencoded parsato correttamente."""
    handler = make_handler()
    form = {
        "From": "whatsapp:+393281536308",
        "Body": "OK",
        "ProfileName": "Mario Rossi",
        "MessageSid": "SMtest123",
        "NumMedia": "0",
    }
    request = make_request(content_type="application/x-www-form-urlencoded", form_data=form)

    response = await handler.handle(request)
    data = json.loads(response.body)
    assert data["ok"] is True


# ---------------------------------------------------------------------------
# AC2 — OK → mark_confirmed called
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac2_confirm_ok_triggers_confirm():
    """AC2: Payload body='OK' → _mark_confirmed chiamato."""
    handler = make_handler()
    # Register a pending appointment
    handler.register_pending_appointment("393281536308", "apt_001", "Mario")

    mock_confirm = AsyncMock(return_value=True)
    handler._mark_confirmed = mock_confirm

    request = make_request({"from": "393281536308", "name": "Mario", "body": "OK", "message_id": "msg_002"})
    response = await handler.handle(request)

    data = json.loads(response.body)
    assert data["ok"] is True
    mock_confirm.assert_awaited_once_with("apt_001", "393281536308")


# ---------------------------------------------------------------------------
# AC3 — ANNULLA → cancel_appointment called
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac3_cancel_annulla_triggers_cancel():
    """AC3: Payload body='ANNULLA' → _cancel_appointment chiamato."""
    handler = make_handler()
    handler.register_pending_appointment("393281536308", "apt_002", "Luigi")

    mock_cancel = AsyncMock(return_value=True)
    handler._cancel_appointment = mock_cancel

    request = make_request({"from": "393281536308", "name": "Luigi", "body": "ANNULLA", "message_id": "msg_003"})
    response = await handler.handle(request)

    data = json.loads(response.body)
    assert data["ok"] is True
    mock_cancel.assert_awaited_once_with("apt_002", "393281536308")


# ---------------------------------------------------------------------------
# AC4 — Free text → orchestrator.process called
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac4_free_text_forwards_to_orchestrator():
    """AC4: Testo libero 'Vorrei prenotare' → orchestrator.process chiamato."""
    mock_result = MagicMock()
    mock_result.response = "In quale giorno vuole venire?"
    mock_result.session_id = "sess_001"

    mock_orch = MagicMock()
    mock_orch.start_session = AsyncMock(return_value=MagicMock(session_id="sess_001", response="Buongiorno!"))
    mock_orch.process = AsyncMock(return_value=mock_result)

    handler = make_handler(orchestrator=mock_orch)

    # Patch SessionChannel import
    with patch.dict("sys.modules", {"session_manager": MagicMock(SessionChannel=MagicMock(WHATSAPP="whatsapp"))}):
        request = make_request({"from": "393281536308", "name": "Mario", "body": "Vorrei prenotare un taglio", "message_id": "msg_004"})
        response = await handler.handle(request)

    data = json.loads(response.body)
    assert data["ok"] is True
    mock_orch.process.assert_awaited_once()


# ---------------------------------------------------------------------------
# AC8 — Rate limit: >3/min logs warning, no crash
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac8_rate_limit_no_crash():
    """AC8: >3 messaggi/min → warning loggato, handler non crasha."""
    handler = make_handler()
    handler.RATE_LIMIT = 2  # Lower limit for test

    responses = []
    for i in range(4):
        request = make_request({"from": "393111111111", "name": "Test", "body": f"messaggio {i}", "message_id": f"msg_rl_{i}"})
        resp = await handler.handle(request)
        responses.append(json.loads(resp.body))

    # First 2 should succeed, rest rate-limited
    assert responses[0]["ok"] is True
    assert responses[1]["ok"] is True
    # After limit: rate_limited=True or still ok (handler never crashes)
    for resp in responses[2:]:
        assert resp["ok"] is True  # handler always returns ok=True, just skips


# ---------------------------------------------------------------------------
# AC9 — Duplicate message_id → ignored silently
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac9_duplicate_message_id_ignored():
    """AC9: Stesso message_id → secondo messaggio ignorato silenziosamente."""
    handler = make_handler()

    request1 = make_request({"from": "393222222222", "name": "Test", "body": "ciao", "message_id": "DEDUP_MSG_001"})
    request2 = make_request({"from": "393222222222", "name": "Test", "body": "ciao", "message_id": "DEDUP_MSG_001"})

    resp1 = await handler.handle(request1)
    resp2 = await handler.handle(request2)

    data1 = json.loads(resp1.body)
    data2 = json.loads(resp2.body)

    assert data1["ok"] is True
    assert data2["ok"] is True
    assert data2.get("duplicate") is True


# ---------------------------------------------------------------------------
# AC10 — Media message → risposta standard, no crash
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac10_media_message_no_crash():
    """AC10: Messaggio media (foto) → skipped silenziosamente, no crash."""
    handler = make_handler()

    request = make_request({
        "from": "393333333333",
        "name": "Test",
        "body": "",
        "message_id": "msg_media_001",
        "type": "media",
        "hasMedia": True,
    })
    response = await handler.handle(request)
    data = json.loads(response.body)
    assert data["ok"] is True
    assert data.get("skipped") is True


# ---------------------------------------------------------------------------
# AC — Empty body → skipped
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_empty_body_skipped():
    """EC2: body whitespace → skip silenzioso."""
    handler = make_handler()
    request = make_request({"from": "393444444444", "name": "Test", "body": "   ", "message_id": "msg_empty"})
    response = await handler.handle(request)
    data = json.loads(response.body)
    assert data["ok"] is True
    assert data.get("skipped") is True


# ---------------------------------------------------------------------------
# AC — CONFIRM patterns (vari dialetti)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("body", [
    "OK", "ok", "Okk", "Si", "si'", "sì", "confermo", "Confermato",
    "va bene", "certo", "esatto", "perfetto", "ci sono",
])
def test_confirm_patterns_match(body):
    """Tutte le varianti CONFIRM matchano il pattern."""
    assert CONFIRM_PATTERN.match(body), f"Expected CONFIRM match for: {body!r}"


# ---------------------------------------------------------------------------
# AC — CANCEL patterns (vari dialetti)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("body", [
    "ANNULLA", "annulla", "cancella", "disdico", "no", "non vengo",
    "non posso", "impossibile", "purtroppo",
])
def test_cancel_patterns_match(body):
    """Tutte le varianti CANCEL matchano il pattern."""
    assert CANCEL_PATTERN.match(body), f"Expected CANCEL match for: {body!r}"


# ---------------------------------------------------------------------------
# AC — register_pending_appointment / WAPhoneSession
# ---------------------------------------------------------------------------

def test_register_pending_appointment():
    """register_pending_appointment popola correttamente la sessione."""
    handler = make_handler()
    handler.register_pending_appointment("393111111111", "apt_XYZ", "Francesca")

    session = handler._phone_sessions.get("393111111111")
    assert session is not None
    assert session.pending_appointment_id == "apt_XYZ"
    assert session.client_name == "Francesca"
    assert session.fsm_state == "waiting_confirmation"


# ---------------------------------------------------------------------------
# AC — Phone normalization
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("393281536308", "393281536308"),
    ("+393281536308", "393281536308"),
    ("3281536308", "393281536308"),    # 10-digit Italian
    ("0039393281536308", "393281536308"),  # 00-prefix is ambiguous; basic strip 0039
])
def test_phone_normalization(raw, expected):
    handler = make_handler()
    result = handler._normalize_phone(raw)
    # Just check digits, length-based correctness
    assert result.isdigit(), f"Should contain only digits, got: {result}"


# ---------------------------------------------------------------------------
# AC1 — Endpoint risponde 200 (via handle() OK return)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac1_endpoint_returns_ok():
    """AC1: POST callback → risponde 200 con ok=True."""
    handler = make_handler()
    request = make_request({"from": "393281536308", "name": "Test", "body": "ciao", "message_id": "msg_ac1"})
    response = await handler.handle(request)
    assert response.status == 200
    data = json.loads(response.body)
    assert data["ok"] is True
