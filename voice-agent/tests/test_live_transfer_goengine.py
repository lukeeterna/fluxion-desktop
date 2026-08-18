"P0 regression tests for Sara live SIP transfer over the Go-engine bridge."
import json
import threading
import time
from unittest.mock import MagicMock, patch

from src.voip_goengine import FRAME_TRANSFER, GoEngineVoIPManager, SIPConfig


def _manager():
    m = GoEngineVoIPManager(SIPConfig(username="u", password="p", server="sip.example"))
    m._call_active = True
    m._conn = object()
    m._send_frame = MagicMock()
    return m


def test_transfer_destination_accepts_phone_formatting_only():
    assert GoEngineVoIPManager._normalize_transfer_destination("+39 333-123-4567") == "393331234567"
    assert GoEngineVoIPManager._normalize_transfer_destination("06 1234 5678") == "0612345678"


def test_transfer_destination_rejects_uri_and_header_injection():
    assert GoEngineVoIPManager._normalize_transfer_destination("sip:3331234567@evil.example") == ""
    assert GoEngineVoIPManager._normalize_transfer_destination("3331234567;transport=tcp") == ""
    assert GoEngineVoIPManager._normalize_transfer_destination("123") == ""


def test_request_transfer_sends_only_normalized_digits_and_returns_connected():
    m = _manager()
    def complete():
        time.sleep(0.02)
        m._on_transfer_status(json.dumps({"status":"connected","code":200}).encode())
    threading.Thread(target=complete, daemon=True).start()
    assert m._request_transfer("+39 333 123 4567", timeout_s=1) == "connected"
    m._send_frame.assert_called_once_with(FRAME_TRANSFER, b"393331234567")


def test_request_transfer_propagates_busy_without_hangup_side_effect():
    m = _manager()
    def complete():
        time.sleep(0.02)
        m._on_transfer_status(json.dumps({"status":"busy","code":486}).encode())
    threading.Thread(target=complete, daemon=True).start()
    assert m._request_transfer("3331234567", timeout_s=1) == "busy"
    m._send_frame.assert_called_once_with(FRAME_TRANSFER, b"3331234567")


def test_invalid_destination_never_reaches_engine():
    m = _manager()
    assert m._request_transfer("sip:123456@evil.example", timeout_s=0.1) == "invalid"
    m._send_frame.assert_not_called()


def test_no_active_call_returns_no_route_without_sending():
    m = _manager()
    m._call_active = False
    assert m._request_transfer("3331234567", timeout_s=0.1) == "no_route"
    m._send_frame.assert_not_called()


def test_transfer_after_drain_retries_next_route_after_busy():
    m = _manager()
    m._request_transfer = MagicMock(side_effect=["busy", "connected"])
    m._speak_transfer_fallback = MagicMock()
    with patch("src.voip_goengine.time.sleep", return_value=None):
        m._transfer_after_drain(["3331234567", "3341234567"])
    assert [c.args[0] for c in m._request_transfer.call_args_list] == ["3331234567", "3341234567"]
    m._speak_transfer_fallback.assert_not_called()


def test_transfer_after_drain_falls_back_once_after_all_routes_fail():
    m = _manager()
    m._request_transfer = MagicMock(side_effect=["busy", "no_answer"])
    m._speak_transfer_fallback = MagicMock()
    with patch("src.voip_goengine.time.sleep", return_value=None):
        m._transfer_after_drain(["3331234567", "3341234567"])
    m._speak_transfer_fallback.assert_called_once_with("no_answer")
