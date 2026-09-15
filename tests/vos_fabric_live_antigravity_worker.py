#!/usr/bin/env python3
"""Live Google Antigravity DIRECT_OFFICIAL worker for VOS Fabric G4/G5.

This helper runs only inside the isolated vos-worker. It accepts a fixed PUBLIC
prompt file from the VOS harness, invokes the exact certified Antigravity CLI,
validates structured output deterministically, and writes a narrow evidence file.
It never authorizes work and never enables an API-key or credit fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

AGY_VERSION = "1.2.3"
AGY_BINARY_SHA256 = "c4c8a6722f9b570e370941b0953ba29051336307d7999ec842bdf7500b0ca7c8"
AGY_MODEL = "gemini-3.8-flash-high"
BANNED_ENV = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_BASE_URL")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Dict[str, Any]) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def enforce_zero_cost_profile(home: Path) -> str:
    for key in BANNED_ENV:
        if os.environ.get(key):
            raise RuntimeError("%s is forbidden" % key)
    settings = home / ".gemini" / "antigravity-cli" / "settings.json"
    if not settings.is_file():
        raise RuntimeError("Antigravity settings missing")
    raw = json.loads(settings.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError("Antigravity settings must be an object")
    if raw.get("modelProvider") == "gemini":
        raise RuntimeError("Gemini API provider override is forbidden")
    raw.pop("modelProvider", None)
    raw["useG1Credits"] = False
    tmp = settings.with_name(settings.name + ".vos-g4-g5.tmp")
    tmp.write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.chmod(str(tmp), 0o600)
    os.replace(str(tmp), str(settings))
    check = json.loads(settings.read_text(encoding="utf-8"))
    if check.get("useG1Credits") is not False:
        raise RuntimeError("Antigravity credit fallback is not disabled")
    if check.get("modelProvider") == "gemini":
        raise RuntimeError("Gemini API provider override appeared")
    return sha256_path(settings)


def parse_stream(
    payload: bytes,
    expected_proof: str,
    expected_conversation: Optional[str],
) -> Tuple[str, Dict[str, Any]]:
    init_event = None
    result = None
    event_count = 0
    for raw in payload.decode("utf-8", "replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise RuntimeError("Antigravity stream event must be an object")
        event_count += 1
        if event.get("event") == "init":
            init_event = event
        elif event.get("event") == "result":
            result = event.get("result")
    if not isinstance(init_event, dict) or not isinstance(result, dict):
        raise RuntimeError("Antigravity stream missing init/result")
    if result.get("status") != "SUCCESS":
        raise RuntimeError("Antigravity terminal status is not SUCCESS")
    structured = result.get("structured_output")
    if not isinstance(structured, dict) or structured.get("proof") != expected_proof:
        raise RuntimeError("Antigravity structured proof mismatch")
    conversation = result.get("conversation_id") or init_event.get("conversation_id")
    if not isinstance(conversation, str) or not conversation:
        raise RuntimeError("Antigravity conversation id missing")
    if expected_conversation is not None and conversation != expected_conversation:
        raise RuntimeError("Antigravity exact resume changed conversation id")
    return conversation, {"event_count": event_count}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("start", "resume"), required=True)
    parser.add_argument("--agy-bin", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--events-file", required=True)
    parser.add_argument("--stderr-file", required=True)
    parser.add_argument("--evidence-file", required=True)
    parser.add_argument("--expected-proof", required=True)
    parser.add_argument("--conversation-id")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    home = Path(os.environ.get("HOME", "")).resolve()
    if str(home) != "/home/ubuntu":
        raise RuntimeError("unexpected HOME")
    agy = Path(args.agy_bin).resolve()
    if str(agy) != "/home/ubuntu/.local/bin/agy" or not agy.is_file():
        raise RuntimeError("unexpected Antigravity executable")
    if sha256_path(agy) != AGY_BINARY_SHA256:
        raise RuntimeError("Antigravity binary SHA-256 drift")
    version = subprocess.run(
        [str(agy), "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
        check=False,
    )
    if version.returncode != 0 or AGY_VERSION not in version.stdout:
        raise RuntimeError("Antigravity version drift")
    if args.model != AGY_MODEL:
        raise RuntimeError("Antigravity model drift")
    if args.mode == "resume" and not args.conversation_id:
        raise RuntimeError("resume requires conversation id")
    if args.mode == "start" and args.conversation_id:
        raise RuntimeError("start must not receive conversation id")
    if args.timeout_seconds <= 0 or args.timeout_seconds > 300:
        raise RuntimeError("timeout outside bounded certification range")

    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    if not prompt or len(prompt.encode("utf-8")) > 8192:
        raise RuntimeError("PUBLIC prompt is empty or unexpectedly large")

    settings_before = enforce_zero_cost_profile(home)
    schema = json.dumps(
        {
            "type": "object",
            "properties": {"proof": {"type": "string"}},
            "required": ["proof"],
            "additionalProperties": False,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    command = [
        str(agy),
        "-p",
        prompt,
        "--model",
        args.model,
        "--output-format",
        "stream-json",
        "--json-schema",
        schema,
        "--sandbox",
        "--print-timeout",
        "2m",
    ]
    if args.mode == "resume":
        command.extend(["--conversation", args.conversation_id])

    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=args.timeout_seconds,
        check=False,
    )
    events = completed.stdout or b""
    stderr = completed.stderr or b""
    events_path = Path(args.events_file)
    stderr_path = Path(args.stderr_file)
    events_path.write_bytes(events)
    stderr_path.write_bytes(stderr)
    settings_after = enforce_zero_cost_profile(home)

    if completed.returncode != 0:
        raise RuntimeError(
            "Antigravity runtime failed rc=%d events_sha256=%s stderr_sha256=%s"
            % (completed.returncode, sha256_bytes(events), sha256_bytes(stderr))
        )

    conversation, parsed = parse_stream(
        events,
        args.expected_proof,
        args.conversation_id if args.mode == "resume" else None,
    )
    evidence = {
        "schema_version": 1,
        "mode": args.mode,
        "model": args.model,
        "antigravity_version": AGY_VERSION,
        "antigravity_binary_sha256": AGY_BINARY_SHA256,
        "observed_conversation_id": conversation,
        "events_sha256": sha256_bytes(events),
        "stderr_sha256": sha256_bytes(stderr),
        "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "settings_before_sha256": settings_before,
        "settings_after_sha256": settings_after,
        "event_count": parsed["event_count"],
        "structured_output_verified": True,
        "api_key_fallback": 0,
        "credit_fallback": 0,
        "paid_api_fallback": 0,
        "production_mutations": 0,
    }
    write_json(Path(args.evidence_file), evidence)
    print("A2_G4_G5_DIRECT_OFFICIAL=GREEN")
    print("A2_G4_G5_STRUCTURED_OUTPUT=GREEN")
    print("A2_G4_G5_API_KEY_FALLBACK=0")
    print("A2_G4_G5_CREDIT_FALLBACK=0")
    print("A2_G4_G5_PRODUCTION_MUTATIONS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
