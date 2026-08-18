"""P0 tests for pjsua2 live transfer without native pjsua2 runtime."""
import importlib
import queue
import sys
import threading
import time
import types
from unittest.mock import MagicMock, patch


def _install_fake_pjsua2():
    fake = types.ModuleType("pjsua2")
    class Error(Exception):
        def info(self, *_args):
            return str(self)
    class Endpoint:
        @staticmethod
        def instance():
            return Endpoint()
        def libIsThreadRegistered(self):
            return True
    class AudioMediaPort: pass
    class Call:
        def __init__(self, *_args, **_kwargs): pass
    class Account:
        def __init__(self, *_args, **_kwargs): pass
    class CallOpParam:
        def __init__(self): self.statusCode = 0
    fake.Error = Error
    fake.Endpoint = Endpoint
    fake.AudioMediaPort = AudioMediaPort
    fake.Call = Call
    fake.Account = Account
    fake.CallOpParam = CallOpParam
    fake.PJSUA_INVALID_ID = -1
    fake.PJMEDIA_FRAME_TYPE_AUDIO = 1
    fake.PJSIP_INV_STATE_CONFIRMED = 5
    fake.PJSIP_INV_STATE_DISCONNECTED = 6
    fake.PJSUA_CALL_MEDIA_ACTIVE = 1
    fake.PJMEDIA_TYPE_AUDIO = 1
    fake.PJSIP_TRANSPORT_UDP = 1
    fake.PJ_TURN_TP_UDP = 1
    fake.PJSUA_SIP_TIMER_INACTIVE = 0
    sys.modules["pjsua2"] = fake
    sys.modules.pop("src.voip_pjsua2", None)
    return importlib.import_module("src.voip_pjsua2")


def _manager():
    mod = _install_fake_pjsua2()
    m = mod.VoIPManager(mod.SIPConfig(username="u", password="p", server="sip.example"))
    call = types.SimpleNamespace(connected=True, xfer=MagicMock(), hangup=MagicMock())
    m._current_call = call
    m._account = object()
    return mod, m, call


def test_transfer_destination_is_phone_only():
    mod, m, _ = _manager()
    assert m._normalize_transfer_destination("+39 333-123-4567") == "393331234567"
    assert m._normalize_transfer_destination("sip:333@evil.example") == ""
    assert m._normalize_transfer_destination("333;transport=tcp") == ""
    assert m._normalize_transfer_destination("123") == ""


def test_refer_is_deferred_to_pjsua2_event_thread_drainer():
    mod, m, call = _manager()
    m._pending_transfers.put((call, "393331234567"))
    m._drain_pending_transfers()
    call.xfer.assert_called_once()
    args = call.xfer.call_args.args
    assert args[0] == "sip:393331234567@sip.example"
    assert isinstance(args[1], mod.pj.CallOpParam)


def test_request_transfer_waits_for_final_success_and_hangs_up_existing_leg():
    _mod, m, call = _manager()
    def complete():
        time.sleep(0.02)
        m._on_call_transfer_status(call, 200, "OK", True)
    threading.Thread(target=complete, daemon=True).start()
    assert m._request_transfer("+39 333 123 4567", timeout_s=1) == "success"
    queued_call, queued_digits = m._pending_transfers.get_nowait()
    assert queued_call is call
    assert queued_digits == "393331234567"
    call.hangup.assert_called_once()


def test_busy_is_terminal_without_success_hangup():
    _mod, m, call = _manager()
    def complete():
        time.sleep(0.02)
        m._on_call_transfer_status(call, 486, "Busy Here", True)
    threading.Thread(target=complete, daemon=True).start()
    assert m._request_transfer("3331234567", timeout_s=1) == "busy"
    call.hangup.assert_not_called()


def test_transfer_after_tts_retries_next_route_after_busy():
    _mod, m, call = _manager()
    call.audio_port = types.SimpleNamespace(tx_queue=queue.Queue(), queue_tts_audio=MagicMock())
    m._request_transfer = MagicMock(side_effect=["busy", "success"])
    m._notify_transfer_failure = MagicMock()
    with patch("src.voip_pjsua2.time.sleep", return_value=None):
        m._transfer_after_tts(call, ["3331234567", "3341234567"])
    assert [c.args[0] for c in m._request_transfer.call_args_list] == ["3331234567", "3341234567"]
    m._notify_transfer_failure.assert_not_called()
