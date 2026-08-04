"""Test per bin/vos_imac_pulse.py — T-MACCHINA."""

import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Consente l'import del modulo anche senza che il repo sia nella PYTHONPATH.
sys.path.insert(0, str(Path(__file__).parent.parent / "bin"))
import vos_imac_pulse as pulse_mod


def _make_pulse(
    head: str = "a" * 40,
    origin: str = "a" * 40,
    engine: str = "go",
    registered: bool = True,
    reg_status: int = 200,
    probed_at: str | None = None,
    file_sha: dict | None = None,
) -> dict:
    if probed_at is None:
        probed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return {
        "schema_version": 1,
        "machine_id": "imac",
        "probed_at_utc": probed_at,
        "head": head,
        "origin_master": origin,
        "head_equals_origin_master": head == origin,
        "voice_agent": {
            "port": 3002,
            "engine": engine,
            "registered": registered,
            "reg_status": reg_status,
        },
        "file_sha256": file_sha or {
            "booking_state_machine.py": "b" * 64,
            "orchestrator.py": "c" * 64,
            "escalation_manager.py": "d" * 64,
            "voip_goengine.py": "e" * 64,
        },
    }


class TestValidatePulseSchema(unittest.TestCase):
    def test_valid_pulse_passes(self):
        p = _make_pulse()
        result = pulse_mod.validate_pulse_schema(p)
        self.assertEqual(result["machine_id"], "imac")

    def test_not_dict_raises(self):
        with self.assertRaises(pulse_mod.PulseError):
            pulse_mod.validate_pulse_schema([1, 2, 3])

    def test_missing_field_raises(self):
        p = _make_pulse()
        del p["head"]
        with self.assertRaises(pulse_mod.PulseError):
            pulse_mod.validate_pulse_schema(p)

    def test_wrong_schema_version_raises(self):
        p = _make_pulse()
        p["schema_version"] = 99
        with self.assertRaises(pulse_mod.PulseError):
            pulse_mod.validate_pulse_schema(p)


class TestCheckFreshness(unittest.TestCase):
    def test_fresh_pulse_is_ok(self):
        p = _make_pulse()
        self.assertTrue(pulse_mod.check_freshness(p, threshold_hours=24))

    def test_stale_pulse_fails(self):
        stale_ts = (
            dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=25)
        ).replace(microsecond=0).isoformat()
        p = _make_pulse(probed_at=stale_ts)
        self.assertFalse(pulse_mod.check_freshness(p, threshold_hours=24))

    def test_missing_timestamp_fails(self):
        p = _make_pulse()
        p["probed_at_utc"] = "not-a-timestamp"
        self.assertFalse(pulse_mod.check_freshness(p, threshold_hours=24))


class TestReadPulse(unittest.TestCase):
    def test_read_valid_json(self):
        p = _make_pulse()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as fh:
            json.dump(p, fh)
            tmp = Path(fh.name)
        try:
            result = pulse_mod.read_pulse(tmp)
            self.assertEqual(result["machine_id"], "imac")
        finally:
            tmp.unlink(missing_ok=True)

    def test_read_missing_file_raises(self):
        with self.assertRaises(pulse_mod.PulseError):
            pulse_mod.read_pulse(Path("/nonexistent/IMAC-PULSE.json"))

    def test_read_invalid_json_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as fh:
            fh.write("not json {{{")
            tmp = Path(fh.name)
        try:
            with self.assertRaises(pulse_mod.PulseError):
                pulse_mod.read_pulse(tmp)
        finally:
            tmp.unlink(missing_ok=True)


class TestCollectPulse(unittest.TestCase):
    """Test di collect_pulse con SSH mockato."""

    def _make_ssh_responses(
        self,
        head: str = "a" * 40,
        origin: str = "a" * 40,
        sha_prefix: str = "b",
        voice_json: str | None = None,
    ) -> list[str]:
        """Restituisce le risposte SSH nell'ordine in cui vengono chiamate."""
        if voice_json is None:
            voice_json = json.dumps({"engine": "go", "registered": True, "reg_status": 200})
        shas = [sha_prefix * 64] * len(pulse_mod._VOICE_AGENT_KEY_FILES)
        return [head, origin] + shas + [voice_json]

    def test_collect_returns_valid_pulse(self):
        responses = self._make_ssh_responses()
        call_idx = [0]

        def fake_ssh(host: str, command: str, timeout: int = 15) -> str:
            val = responses[call_idx[0]]
            call_idx[0] += 1
            return val

        with patch.object(pulse_mod, "_ssh", side_effect=fake_ssh):
            result = pulse_mod.collect_pulse("192.168.1.2")

        pulse_mod.validate_pulse_schema(result)
        self.assertEqual(result["machine_id"], "imac")
        self.assertTrue(result["head_equals_origin_master"])

    def test_collect_ssh_failure_raises(self):
        with patch.object(
            pulse_mod, "_ssh", side_effect=pulse_mod.PulseError("SSH timeout")
        ):
            with self.assertRaises(pulse_mod.PulseError):
                pulse_mod.collect_pulse("192.168.1.2")

    def test_collect_invalid_voice_json_uses_defaults(self):
        responses = self._make_ssh_responses(voice_json="malformed{{")
        call_idx = [0]

        def fake_ssh(host: str, command: str, timeout: int = 15) -> str:
            val = responses[call_idx[0]]
            call_idx[0] += 1
            return val

        with patch.object(pulse_mod, "_ssh", side_effect=fake_ssh):
            result = pulse_mod.collect_pulse("192.168.1.2")

        # Dati voce di fallback con campi "unknown"/False/0
        self.assertEqual(result["voice_agent"]["engine"], "unknown")
        self.assertFalse(result["voice_agent"]["registered"])

    def test_collect_nested_sip_format(self):
        """Verifica che il formato annidato {sip: {registered, reg_status}} sia gestito."""
        nested_voice = json.dumps({
            "running": True,
            "engine": "go",
            "rtp_active": False,
            "sip": {"registered": True, "reg_status": 200, "username": "x", "server": "y"},
        })
        responses = self._make_ssh_responses(voice_json=nested_voice)
        call_idx = [0]

        def fake_ssh(host: str, command: str, timeout: int = 15) -> str:
            val = responses[call_idx[0]]
            call_idx[0] += 1
            return val

        with patch.object(pulse_mod, "_ssh", side_effect=fake_ssh):
            result = pulse_mod.collect_pulse("192.168.1.2")

        self.assertEqual(result["voice_agent"]["engine"], "go")
        self.assertTrue(result["voice_agent"]["registered"])
        self.assertEqual(result["voice_agent"]["reg_status"], 200)

    def test_collect_head_neq_origin_master(self):
        head = "a" * 40
        origin = "b" * 40
        responses = self._make_ssh_responses(head=head, origin=origin)
        call_idx = [0]

        def fake_ssh(host: str, command: str, timeout: int = 15) -> str:
            val = responses[call_idx[0]]
            call_idx[0] += 1
            return val

        with patch.object(pulse_mod, "_ssh", side_effect=fake_ssh):
            result = pulse_mod.collect_pulse("192.168.1.2")

        self.assertFalse(result["head_equals_origin_master"])


if __name__ == "__main__":
    unittest.main()
