#!/usr/bin/env python3
"""FLUXION VOS — iMac pulse collector.

Raccoglie via SSH lo stato del runtime iMac (HEAD, origine, :3002 health,
SHA256 dei file chiave) e lo scrive in docs/judge/IMAC-PULSE.json.

Il file risultante non contiene IP, username, path assoluti o segreti:
solo digest, HEAD hash e struttura dello stato runtime.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCHEMA_VERSION = 1
PULSE_PATH = Path("docs/judge/IMAC-PULSE.json")
MACHINE_ID = "imac"

# Percorsi relativi al repo iMac; usati solo lato SSH.
_RUNTIME_REPO_PATH = "/Volumes/MacSSD - Dati/fluxion"
_VOICE_AGENT_KEY_FILES = [
    "voice-agent/src/booking_state_machine.py",
    "voice-agent/src/orchestrator.py",
    "voice-agent/src/escalation_manager.py",
    "voice-agent/src/voip_goengine.py",
]

STALE_THRESHOLD_HOURS = 24


class PulseError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(out.stdout.strip()).resolve()


def _ssh(host: str, command: str, timeout: int = 15) -> str:
    """Esegue un comando sul host remoto; lancia PulseError se fallisce."""
    result = subprocess.run(
        [
            "ssh",
            "-i", os.path.expanduser("~/.ssh/id_ed25519"),
            "-o", "StrictHostKeyChecking=no",
            "-o", f"ConnectTimeout={timeout}",
            "-o", "BatchMode=yes",
            f"gianlucadistasi@{host}",
            command,
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise PulseError(
            f"SSH a {host} fallita (rc={result.returncode}): {result.stderr.strip()!r}"
        )
    return result.stdout.strip()


def collect_pulse(host: str) -> dict:
    """Raccoglie lo stato del runtime iMac via SSH e restituisce un dict validato."""
    repo = _RUNTIME_REPO_PATH

    # HEAD e origin/master
    head = _ssh(host, f"cd '{repo}' && git rev-parse HEAD")
    origin_master = _ssh(host, f"cd '{repo}' && git rev-parse origin/master")
    head_equals = head == origin_master

    # SHA256 file chiave (senza contenuto)
    file_sha256: dict[str, str] = {}
    for rel in _VOICE_AGENT_KEY_FILES:
        name = Path(rel).name
        digest = _ssh(host, f"shasum -a 256 '{repo}/{rel}' | awk '{{print $1}}'")
        file_sha256[name] = digest

    # Stato :3002
    voice_raw = _ssh(
        host,
        "curl -s --max-time 5 http://127.0.0.1:3002/api/voice/voip/status 2>/dev/null || echo '{}'",
    )
    try:
        voice_data = json.loads(voice_raw)
    except json.JSONDecodeError:
        voice_data = {}

    # L'endpoint /api/voice/voip/status può restituire due formati:
    # - piatto: {"registered": bool, "reg_status": int, "engine": str, ...}
    # - annidato: {"running": bool, "engine": str, "sip": {"registered": bool, "reg_status": int}, ...}
    sip_block = voice_data.get("sip", {}) or {}
    registered = voice_data.get("registered", sip_block.get("registered", False))
    reg_status = voice_data.get("reg_status", sip_block.get("reg_status", 0))

    pulse = {
        "schema_version": SCHEMA_VERSION,
        "machine_id": MACHINE_ID,
        "probed_at_utc": utc_now(),
        "head": head,
        "origin_master": origin_master,
        "head_equals_origin_master": head_equals,
        "voice_agent": {
            "port": 3002,
            "engine": voice_data.get("engine", "unknown"),
            "registered": registered,
            "reg_status": reg_status,
        },
        "file_sha256": file_sha256,
    }
    return pulse


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def validate_pulse_schema(data: object) -> dict:
    """Verifica i campi obbligatori; lancia PulseError se manca qualcosa."""
    if not isinstance(data, dict):
        raise PulseError("pulse deve essere un oggetto JSON")
    required = {
        "schema_version", "machine_id", "probed_at_utc",
        "head", "origin_master", "head_equals_origin_master",
        "voice_agent", "file_sha256",
    }
    missing = required - data.keys()
    if missing:
        raise PulseError(f"pulse mancante di campi: {sorted(missing)}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise PulseError("schema_version non supportata")
    return data  # type: ignore[return-value]


def check_freshness(pulse: dict, threshold_hours: int = STALE_THRESHOLD_HOURS) -> bool:
    """Restituisce True se probed_at_utc è < threshold_hours fa."""
    raw = pulse.get("probed_at_utc", "")
    try:
        probed = dt.datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        return False
    now = dt.datetime.now(dt.timezone.utc)
    if probed.tzinfo is None:
        probed = probed.replace(tzinfo=dt.timezone.utc)
    age = now - probed
    return age.total_seconds() < threshold_hours * 3600


def read_pulse(path: Path) -> dict:
    """Legge e valida docs/judge/IMAC-PULSE.json."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PulseError(f"pulse non trovato: {path}")
    except json.JSONDecodeError as exc:
        raise PulseError(f"pulse JSON non valido: {exc}")
    return validate_pulse_schema(data)


def cmd_collect(args: argparse.Namespace) -> int:
    root = repo_root()
    out_path = root / PULSE_PATH
    pulse = collect_pulse(args.host)
    validate_pulse_schema(pulse)
    atomic_write(out_path, pulse)
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    print(f"PULSE_WRITTEN {out_path} sha256={sha}")
    print(f"  head={pulse['head'][:12]} head_eq_origin={pulse['head_equals_origin_master']}")
    print(f"  engine={pulse['voice_agent']['engine']} registered={pulse['voice_agent']['registered']}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    root = repo_root()
    pulse_path = root / PULSE_PATH
    try:
        pulse = read_pulse(pulse_path)
        fresh = check_freshness(pulse, args.max_hours)
        if not fresh:
            print(f"PULSE_STALE probed_at={pulse.get('probed_at_utc')} max={args.max_hours}h", file=sys.stderr)
            return 1
        print(f"PULSE_OK machine={pulse['machine_id']} probed_at={pulse['probed_at_utc']}")
        return 0
    except PulseError as exc:
        print(f"PULSE_FAIL {exc}", file=sys.stderr)
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    col = sub.add_parser("collect", help="raccoglie stato iMac via SSH e scrive IMAC-PULSE.json")
    col.add_argument("--host", default="192.168.1.2", help="indirizzo iMac")
    col.set_defaults(func=cmd_collect)

    chk = sub.add_parser("check", help="verifica che IMAC-PULSE.json esista e non sia stale")
    chk.add_argument("--max-hours", type=int, default=STALE_THRESHOLD_HOURS)
    chk.set_defaults(func=cmd_check)

    args = ap.parse_args()
    try:
        return int(args.func(args))
    except PulseError as exc:
        print(f"PULSE_FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
