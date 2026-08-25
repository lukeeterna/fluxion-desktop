#!/usr/bin/env python3
"""Fail-closed Codex qualification for the VOS control node.

This helper never performs login and never reads or prints credential material.
It assumes CODEX_HOME already points at the preserved external-disk location.
It proves, using one harmless read-only inference and one exact resume:

- active ChatGPT authentication is present;
- the requested model can complete a real call;
- `codex exec --json` yields a durable session identifier;
- the exact identifier can be resumed;
- the resumed turn keeps the same identifier and remembers prior context.

Raw JSONL and stderr are written only to the caller-provided evidence directory.
The terminal stdout is a compact JSON summary without prompts or credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Iterable

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
MODEL_RE = re.compile(r"^gpt-[A-Za-z0-9._-]+$")
SESSION_KEYS = ("thread_id", "session_id", "conversation_id")


class QualificationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise QualificationError(f"invalid JSONL at line {lineno}") from exc
            if not isinstance(value, dict):
                raise QualificationError(f"JSONL event {lineno} is not an object")
            events.append(value)
    if not events:
        raise QualificationError("empty JSONL event stream")
    return events


def walk(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def event_kind(event: dict[str, Any]) -> str:
    for key in ("type", "event", "kind"):
        value = event.get(key)
        if isinstance(value, str):
            return value.lower()
    return ""


def extract_session_ids(events: list[dict[str, Any]]) -> set[str]:
    found: set[str] = set()
    for event in events:
        kind = event_kind(event)
        for key, value in walk(event):
            if not isinstance(value, str) or not UUID_RE.fullmatch(value):
                continue
            key_lower = key.lower()
            if key_lower in SESSION_KEYS:
                found.add(value.lower())
            elif key_lower == "id" and ("thread" in kind or "session" in kind):
                found.add(value.lower())
    return found


def require_single_session_id(events: list[dict[str, Any]], label: str) -> str:
    ids = extract_session_ids(events)
    if len(ids) != 1:
        raise QualificationError(f"{label}: expected exactly one session id, found {len(ids)}")
    return next(iter(ids))


def extract_models(value: Any) -> set[str]:
    found: set[str] = set()
    for key, child in walk(value):
        if key.lower() in {"model", "model_id", "model_name"} and isinstance(child, str):
            if MODEL_RE.fullmatch(child):
                found.add(child)
    return found


def find_session_rollout(codex_home: Path, session_id: str) -> Path | None:
    sessions = codex_home / "sessions"
    if not sessions.is_dir():
        return None
    candidates = sorted(
        (p for p in sessions.rglob("*.jsonl") if session_id in p.name.lower()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def model_evidence(events: list[dict[str, Any]], rollout: Path | None) -> set[str]:
    models = extract_models(events)
    if rollout is not None:
        try:
            rollout_events = parse_jsonl(rollout)
        except QualificationError:
            rollout_events = []
        models.update(extract_models(rollout_events))
    return models


def marker_present(value: Any, marker: str) -> bool:
    if isinstance(value, str):
        return marker in value
    if isinstance(value, dict):
        return any(marker_present(v, marker) for v in value.values())
    if isinstance(value, list):
        return any(marker_present(v, marker) for v in value)
    return False


def run_capture(command: list[str], *, cwd: Path, stdout_path: Path, stderr_path: Path,
                timeout: int) -> tuple[int, float]:
    started = time.monotonic()
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                text=True,
                stdout=out,
                stderr=err,
                timeout=timeout,
                check=False,
            )
            rc = completed.returncode
        except subprocess.TimeoutExpired as exc:
            raise QualificationError(f"command timeout after {timeout}s") from exc
    return rc, time.monotonic() - started


def login_status(codex: str, *, cwd: Path, timeout: int = 90) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            [codex, "login", "status"],
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise QualificationError("codex login status timed out") from exc
    return completed.returncode, completed.stdout or ""


def qualify(*, codex: str, codex_home: Path, evidence: Path, model: str,
            workspace: Path, timeout: int) -> dict[str, Any]:
    if not MODEL_RE.fullmatch(model):
        raise QualificationError("invalid model name")
    if not codex_home.is_dir():
        raise QualificationError("CODEX_HOME does not exist")
    evidence.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)

    login_rc, login_text = login_status(codex, cwd=workspace)
    login_lower = login_text.lower()
    api_key_markers = ("api key", "openai_api_key", "api-key")
    if login_rc != 0:
        raise QualificationError("ChatGPT authentication is not active")
    if any(marker in login_lower for marker in api_key_markers):
        raise QualificationError("API-key authentication is forbidden for this qualification")

    marker = f"VOSQUAL-{uuid.uuid4()}"
    first_prompt = (
        "VOS qualification, read-only. Do not run shell commands and do not write files. "
        f"Remember this marker for the next turn: {marker}. "
        "Reply briefly that the marker is stored."
    )
    first_jsonl = evidence / "exec-first.jsonl"
    first_stderr = evidence / "exec-first.stderr"
    first_cmd = [
        codex, "exec", "--json", "--model", model, "--sandbox", "read-only",
        "--skip-git-repo-check", first_prompt,
    ]
    first_rc, first_elapsed = run_capture(
        first_cmd, cwd=workspace, stdout_path=first_jsonl, stderr_path=first_stderr, timeout=timeout
    )
    if first_rc != 0:
        raise QualificationError(f"first codex exec failed with rc={first_rc}")
    first_events = parse_jsonl(first_jsonl)
    session_before = require_single_session_id(first_events, "first exec")
    rollout = find_session_rollout(codex_home, session_before)
    models = model_evidence(first_events, rollout)
    if model not in models:
        raise QualificationError(
            "requested model completed but actual model is not proven in JSONL/session evidence"
        )

    resume_prompt = (
        "What exact qualification marker did I ask you to remember in the previous turn? "
        "Return the marker exactly; do not invent a new value."
    )
    resume_jsonl = evidence / "exec-resume.jsonl"
    resume_stderr = evidence / "exec-resume.stderr"
    resume_cmd = [
        codex, "exec", "resume", session_before, "--json",
        "--skip-git-repo-check", resume_prompt,
    ]
    resume_rc, resume_elapsed = run_capture(
        resume_cmd, cwd=workspace, stdout_path=resume_jsonl, stderr_path=resume_stderr, timeout=timeout
    )
    if resume_rc != 0:
        raise QualificationError(f"codex exec resume failed with rc={resume_rc}")
    resume_events = parse_jsonl(resume_jsonl)
    session_after = require_single_session_id(resume_events, "resume")
    if session_after != session_before:
        raise QualificationError("resume returned a different session id")
    if not marker_present(resume_events, marker):
        raise QualificationError("resume did not demonstrate context continuity")

    return {
        "schema_version": 1,
        "status": "PASS",
        "auth": "PASS",
        "model_requested": model,
        "model_actual_proven": model,
        "exec_json": "PASS",
        "exact_resume": "PASS",
        "thread_id_match": "PASS",
        "context_continuity": "PASS",
        "session_id": session_before,
        "first_exit_code": first_rc,
        "resume_exit_code": resume_rc,
        "first_elapsed_seconds": round(first_elapsed, 3),
        "resume_elapsed_seconds": round(resume_elapsed, 3),
        "first_jsonl_sha256": sha256_file(first_jsonl),
        "resume_jsonl_sha256": sha256_file(resume_jsonl),
        "rollout_evidence_present": rollout is not None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", ""))
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    summary_path = Path(args.evidence) / "qualification-summary.json"
    try:
        if not args.codex_home:
            raise QualificationError("CODEX_HOME is not set")
        result = qualify(
            codex=args.codex,
            codex_home=Path(args.codex_home).resolve(),
            evidence=Path(args.evidence).resolve(),
            model=args.model,
            workspace=Path(args.workspace).resolve(),
            timeout=args.timeout,
        )
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
        return 0
    except QualificationError as exc:
        failure = {"schema_version": 1, "status": "FAIL", "error": str(exc)}
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(failure, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
