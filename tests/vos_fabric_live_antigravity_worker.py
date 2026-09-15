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
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

AGY_VERSION = "1.2.3"
AGY_BINARY_SHA256 = "c4c8a6722f9b570e370941b0953ba29051336307d7999ec842bdf7500b0ca7c8"
AGY_MODEL = "gemini-3.8-flash-high"
BANNED_ENV = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_BASE_URL")
KNOWN_FINALIZATION_ERROR = "context canceled"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Dict[str, Any]) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def classify_failure(events: bytes, stderr: bytes) -> str:
    """Return a narrow, non-secret failure class equivalent to the A2 qualifier."""
    text = (events + b"\n" + stderr).decode("utf-8", "replace").lower()
    if re.search(r"quota|rate[ -]?limit|resource[_ -]?exhausted|out of credits|usage limit", text):
        return "BLOCKED_QUOTA"
    if re.search(r"authentication required|sign[ -]?in|required.*auth|unauthorized|invalid_grant", text):
        return "BLOCKED_AUTH"
    if re.search(r"model.*(not available|not found|unsupported)|requested model", text):
        return "BLOCKED_MODEL"
    if re.search(r"timed? out|timeout", text):
        return "BLOCKED_TIMEOUT"
    return "RUNTIME_ERROR"


def failure_evidence(
    *,
    mode: str,
    phase: str,
    failure_class: str,
    model: str,
    prompt: bytes,
    events: bytes,
    stderr: bytes,
    settings_before: str,
    settings_after: str,
    exit_code: Optional[int],
) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "mode": mode,
        "phase": phase,
        "failure_class": failure_class,
        "model": model,
        "antigravity_version": AGY_VERSION,
        "antigravity_binary_sha256": AGY_BINARY_SHA256,
        "exit_code": exit_code,
        "events_sha256": sha256_bytes(events),
        "stderr_sha256": sha256_bytes(stderr),
        "prompt_sha256": sha256_bytes(prompt),
        "settings_before_sha256": settings_before,
        "settings_after_sha256": settings_after,
        "structured_output_verified": False,
        "api_key_fallback": 0,
        "credit_fallback": 0,
        "paid_api_fallback": 0,
        "production_mutations": 0,
    }


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


def require_exact_model(agy: Path, expected_model: str, home: Path) -> Tuple[str, str]:
    """Refresh direct-account eligibility exactly as the canonical qualifier does."""
    before = enforce_zero_cost_profile(home)
    completed = subprocess.run(
        [str(agy), "models"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
    )
    after = enforce_zero_cost_profile(home)
    stdout = completed.stdout or b""
    stderr = completed.stderr or b""
    if completed.returncode != 0:
        raise RuntimeError(
            "MODEL_PREFLIGHT:%s:%d:%s:%s:%s:%s"
            % (
                classify_failure(stdout, stderr),
                completed.returncode,
                sha256_bytes(stdout),
                sha256_bytes(stderr),
                before,
                after,
            )
        )
    available = []
    for raw in stdout.decode("utf-8", "replace").splitlines():
        fields = raw.strip().split()
        if not fields:
            continue
        first = fields[0]
        if first.upper() in ("MODEL", "NAME") or set(first) == {"-"}:
            continue
        available.append(first)
    if expected_model not in available:
        raise RuntimeError(
            "MODEL_PREFLIGHT:BLOCKED_MODEL:0:%s:%s:%s:%s"
            % (sha256_bytes(stdout), sha256_bytes(stderr), before, after)
        )
    return before, after


def parse_stream(
    payload: bytes,
    expected_proof: str,
    expected_conversation: Optional[str],
) -> Tuple[str, Dict[str, Any]]:
    """Validate the official stream envelope and exact structured result.

    Antigravity issue #848 documents a print-mode finalization defect where a valid
    finish() is followed by terminal ``status=ERROR`` / ``error=context canceled``.
    That defect is accepted only after all success payload invariants are proven.
    Every other non-SUCCESS status remains fail-closed.
    """
    init_event = None
    result = None
    event_count = 0
    init_count = 0
    result_count = 0
    for raw in payload.decode("utf-8", "replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise RuntimeError("Antigravity stream event must be an object")
        event_count += 1
        if event.get("event") == "init":
            init_count += 1
            init_event = event
        elif event.get("event") == "result":
            result_count += 1
            result = event.get("result")
    if init_count != 1 or result_count != 1:
        raise RuntimeError("Antigravity stream requires exactly one init and one result")
    if not isinstance(init_event, dict) or not isinstance(result, dict):
        raise RuntimeError("Antigravity stream missing init/result")

    structured = result.get("structured_output")
    if (
        not isinstance(structured, dict)
        or set(structured.keys()) != {"proof"}
        or structured.get("proof") != expected_proof
    ):
        raise RuntimeError("Antigravity structured proof mismatch")
    conversation = result.get("conversation_id") or init_event.get("conversation_id")
    if not isinstance(conversation, str) or not conversation:
        raise RuntimeError("Antigravity conversation id missing")
    if expected_conversation is not None and conversation != expected_conversation:
        raise RuntimeError("Antigravity exact resume changed conversation id")

    terminal_status = result.get("status")
    terminal_error = result.get("error")
    accepted_known_bug = False
    terminal_error_class = "NONE"
    if terminal_status == "SUCCESS":
        if terminal_error not in (None, ""):
            raise RuntimeError("Antigravity SUCCESS carried unexpected terminal error")
    elif terminal_status == "ERROR" and terminal_error == KNOWN_FINALIZATION_ERROR:
        accepted_known_bug = True
        terminal_error_class = "KNOWN_AGY_CONTEXT_CANCELED_AFTER_VALID_FINISH"
    else:
        raise RuntimeError("Antigravity terminal status/error is not an accepted completion")

    return conversation, {
        "event_count": event_count,
        "init_count": init_count,
        "result_count": result_count,
        "terminal_status": terminal_status,
        "terminal_error_class": terminal_error_class,
        "accepted_known_cli_finalization_bug": accepted_known_bug,
    }


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

    prompt = Path(args.prompt_file).read_bytes()
    if not prompt or len(prompt) > 8192:
        raise RuntimeError("PUBLIC prompt is empty or unexpectedly large")
    evidence_path = Path(args.evidence_file)
    events_path = Path(args.events_file)
    stderr_path = Path(args.stderr_file)

    try:
        settings_before, _ = require_exact_model(agy, args.model, home)
    except RuntimeError as exc:
        text = str(exc)
        if text.startswith("MODEL_PREFLIGHT:"):
            fields = text.split(":")
            failure_class = fields[1] if len(fields) > 1 else "RUNTIME_ERROR"
            exit_code = int(fields[2]) if len(fields) > 2 and fields[2].isdigit() else None
            settings_before = fields[-2] if len(fields) >= 6 else enforce_zero_cost_profile(home)
            settings_after = fields[-1] if len(fields) >= 6 else settings_before
            write_json(
                evidence_path,
                failure_evidence(
                    mode=args.mode,
                    phase="model_preflight",
                    failure_class=failure_class,
                    model=args.model,
                    prompt=prompt,
                    events=b"",
                    stderr=b"",
                    settings_before=settings_before,
                    settings_after=settings_after,
                    exit_code=exit_code,
                ),
            )
            print("A2_G4_G5_BLOCKED=" + failure_class)
            return 20
        raise

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
        prompt.decode("utf-8"),
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
    events_path.write_bytes(events)
    stderr_path.write_bytes(stderr)
    settings_after = enforce_zero_cost_profile(home)

    if completed.returncode != 0:
        failure_class = classify_failure(events, stderr)
        write_json(
            evidence_path,
            failure_evidence(
                mode=args.mode,
                phase="inference",
                failure_class=failure_class,
                model=args.model,
                prompt=prompt,
                events=events,
                stderr=stderr,
                settings_before=settings_before,
                settings_after=settings_after,
                exit_code=completed.returncode,
            ),
        )
        print("A2_G4_G5_BLOCKED=" + failure_class)
        return 21

    try:
        conversation, parsed = parse_stream(
            events,
            args.expected_proof,
            args.conversation_id if args.mode == "resume" else None,
        )
    except Exception:
        write_json(
            evidence_path,
            failure_evidence(
                mode=args.mode,
                phase="stream_validation",
                failure_class="STREAM_VALIDATION_FAILED",
                model=args.model,
                prompt=prompt,
                events=events,
                stderr=stderr,
                settings_before=settings_before,
                settings_after=settings_after,
                exit_code=completed.returncode,
            ),
        )
        print("A2_G4_G5_BLOCKED=STREAM_VALIDATION_FAILED")
        return 22

    evidence = {
        "schema_version": 1,
        "mode": args.mode,
        "phase": "complete",
        "model": args.model,
        "antigravity_version": AGY_VERSION,
        "antigravity_binary_sha256": AGY_BINARY_SHA256,
        "observed_conversation_id": conversation,
        "events_sha256": sha256_bytes(events),
        "stderr_sha256": sha256_bytes(stderr),
        "prompt_sha256": sha256_bytes(prompt),
        "settings_before_sha256": settings_before,
        "settings_after_sha256": settings_after,
        "event_count": parsed["event_count"],
        "init_count": parsed["init_count"],
        "result_count": parsed["result_count"],
        "terminal_status": parsed["terminal_status"],
        "terminal_error_class": parsed["terminal_error_class"],
        "accepted_known_cli_finalization_bug": parsed["accepted_known_cli_finalization_bug"],
        "structured_output_verified": True,
        "api_key_fallback": 0,
        "credit_fallback": 0,
        "paid_api_fallback": 0,
        "production_mutations": 0,
    }
    write_json(evidence_path, evidence)
    print("A2_G4_G5_MODEL_PREFLIGHT=GREEN")
    print("A2_G4_G5_DIRECT_OFFICIAL=GREEN")
    print("A2_G4_G5_STRUCTURED_OUTPUT=GREEN")
    print(
        "A2_G4_G5_KNOWN_CLI_FINALIZATION_BUG=%d"
        % (1 if parsed["accepted_known_cli_finalization_bug"] else 0)
    )
    print("A2_G4_G5_API_KEY_FALLBACK=0")
    print("A2_G4_G5_CREDIT_FALLBACK=0")
    print("A2_G4_G5_PRODUCTION_MUTATIONS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
