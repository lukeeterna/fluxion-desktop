#!/usr/bin/env python3
"""Bounded live Codex resume/fork adapter for VOS Fabric G4/G5 certification.

This executable is run only inside the isolated vos-worker. It never reads API keys,
never mutates production, and writes evidence only below the supplied temporary work dir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def thread_and_usage(events_path: Path) -> Tuple[str, Mapping[str, Any]]:
    thread_id = None
    usage: Mapping[str, Any] = {}
    turn_completed = False
    with events_path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            event = json.loads(raw)
            if event.get("type") == "thread.started" and not thread_id:
                candidate = event.get("thread_id")
                if isinstance(candidate, str) and candidate:
                    thread_id = candidate
            if event.get("type") == "turn.completed":
                turn_completed = True
                raw_usage = event.get("usage")
                if isinstance(raw_usage, Mapping):
                    usage = dict(raw_usage)
    if not thread_id:
        raise RuntimeError("thread.started missing")
    if not turn_completed:
        raise RuntimeError("turn.completed missing")
    return thread_id, usage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("resume", "fork"), required=True)
    parser.add_argument("--thread-id", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--events-file", required=True)
    parser.add_argument("--message-file", required=True)
    parser.add_argument("--evidence-file", required=True)
    parser.add_argument("--expected-message", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()

    work = Path(args.work_dir).resolve()
    prompt_path = Path(args.prompt_file).resolve()
    events_path = Path(args.events_file).resolve()
    message_path = Path(args.message_file).resolve()
    evidence_path = Path(args.evidence_file).resolve()

    for path in (prompt_path, events_path, message_path, evidence_path):
        if work != path.parent and work not in path.parents:
            raise SystemExit("evidence/prompt path outside work-dir")
    if args.timeout_seconds < 1 or args.timeout_seconds > 300:
        raise SystemExit("timeout outside 1..300")
    if not prompt_path.is_file():
        raise SystemExit("prompt file missing")

    cmd = [
        "/usr/local/bin/codex", "exec", "--json",
        "--sandbox", "read-only",
        "-c", 'approval_policy="never"',
        "--model", args.model,
        "--skip-git-repo-check",
        "--cd", str(work),
        "--output-last-message", str(message_path),
        args.mode, args.thread_id, "-",
    ]
    with prompt_path.open("rb") as prompt, events_path.open("wb") as events:
        completed = subprocess.run(
            cmd,
            stdin=prompt,
            stdout=events,
            stderr=subprocess.PIPE,
            timeout=args.timeout_seconds,
            check=False,
            env=dict(os.environ),
        )
    if completed.returncode != 0:
        raise SystemExit("Codex returned nonzero rc=%d stderr_sha256=%s" % (
            completed.returncode,
            hashlib.sha256(completed.stderr or b"").hexdigest(),
        ))

    actual_message = message_path.read_text(encoding="utf-8").strip()
    if actual_message != args.expected_message:
        raise SystemExit("unexpected last message")

    observed_thread, usage = thread_and_usage(events_path)
    if args.mode == "resume" and observed_thread != args.thread_id:
        raise SystemExit("resume changed thread id")
    if args.mode == "fork" and observed_thread == args.thread_id:
        raise SystemExit("fork reused source thread id")

    evidence: Dict[str, Any] = {
        "schema_version": 1,
        "mode": args.mode,
        "source_thread_id": args.thread_id,
        "observed_thread_id": observed_thread,
        "model_requested": args.model,
        "events_sha256": sha256_file(events_path),
        "last_message_sha256": sha256_file(message_path),
        "usage": dict(usage),
        "codex_exit_code": completed.returncode,
        "paid_api_fallback": 0,
    }
    evidence_path.write_text(
        json.dumps(evidence, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print("LIVE_CODEX_WORKER=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
