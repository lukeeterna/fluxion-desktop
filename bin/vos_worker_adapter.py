#!/usr/bin/env python3
"""Thin VOS worker adapter: sealed task -> existing VOS kernel -> result envelope.

The adapter deliberately does not implement another executor. It validates a
small task envelope, then delegates execution to ``vos_apply.execute_unit``.
All durable control files live under the repository git-dir, never in the
source checkout. Duplicate task delivery is idempotent for the same lease.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from vos_apply import execute_unit, parse_plan, validate_manifest
from vos_common import (
    NONCE_RE,
    SHA256_RE,
    VOSFailure,
    atomic_write_json,
    canonical_json,
    dirty_paths,
    ensure_relative_path,
    git,
    git_dir,
    read_json,
    repo_root,
    sha256_bytes,
    sha256_file,
    utc_now,
)

THREAD_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_TASK_FIELDS = {
    "schema_version",
    "unit_id",
    "plan_path",
    "plan_sha256",
    "mandate_sha256",
    "base_commit",
    "lease_nonce",
    "thread_id",
    "objective_sha256",
}


def task_digest(task: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(task))


def _require_hash(value: Any, label: str) -> str:
    text = str(value)
    if not SHA256_RE.fullmatch(text):
        raise VOSFailure(f"{label} non valido")
    return text


def validate_task(root: Path, task: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Path]:
    missing = sorted(REQUIRED_TASK_FIELDS - set(task))
    if missing:
        raise VOSFailure("task incompleto: " + ", ".join(missing))
    extra = sorted(set(task) - REQUIRED_TASK_FIELDS)
    if extra:
        raise VOSFailure("campi task non ammessi: " + ", ".join(extra))
    if task["schema_version"] != 1:
        raise VOSFailure("schema task non supportato")

    base = str(task["base_commit"])
    if not COMMIT_RE.fullmatch(base):
        raise VOSFailure("base_commit non valido")
    current = git(root, "rev-parse", "HEAD")
    if current != base:
        raise VOSFailure(f"base_commit mismatch: task={base} repo={current}")
    if dirty_paths(root):
        raise VOSFailure("worktree target sporco: worker rifiutato")

    lease = str(task["lease_nonce"])
    if not NONCE_RE.fullmatch(lease):
        raise VOSFailure("lease_nonce non valido")
    thread_id = str(task["thread_id"])
    if not THREAD_RE.fullmatch(thread_id):
        raise VOSFailure("thread_id non valido")
    _require_hash(task["objective_sha256"], "objective_sha256")
    expected_plan_sha = _require_hash(task["plan_sha256"], "plan_sha256")
    expected_mandate_sha = _require_hash(task["mandate_sha256"], "mandate_sha256")

    plan_rel = ensure_relative_path(str(task["plan_path"]))
    plan_path = (root / plan_rel).resolve()
    if root not in (plan_path, *plan_path.parents):
        raise VOSFailure("plan_path fuori repository")
    if sha256_file(plan_path) != expected_plan_sha:
        raise VOSFailure("plan_sha256 mismatch")
    plan = parse_plan(plan_path)
    if plan["head"] != base:
        raise VOSFailure(f"plan HEAD mismatch: {plan['head']} != {base}")
    unit_id = str(task["unit_id"])
    if unit_id not in plan["units"]:
        raise VOSFailure("unità task non presente nel piano")
    manifest = validate_manifest(root, unit_id, plan["head"])
    if manifest["mandate_sha256"] != expected_mandate_sha:
        raise VOSFailure("mandate_sha256 mismatch")
    return plan, manifest, plan_path


def _control_paths(root: Path, lease: str) -> tuple[Path, Path]:
    control = git_dir(root) / "vos-control"
    return (
        control / "worker-started" / f"{lease}.json",
        control / "worker-results" / f"{lease}.json",
    )


def _validate_cached(cached: dict[str, Any], digest: str, task: dict[str, Any]) -> dict[str, Any]:
    if cached.get("task_sha256") != digest:
        raise VOSFailure("lease riusato con task differente")
    if cached.get("lease_nonce") != task["lease_nonce"]:
        raise VOSFailure("cache worker lease incoerente")
    if cached.get("mandate_sha256") != task["mandate_sha256"]:
        raise VOSFailure("cache worker mandato incoerente")
    return cached


def run_task(root: Path, task: dict[str, Any], *, output_path: Path | None = None) -> dict[str, Any]:
    plan, manifest, _ = validate_task(root, task)
    digest = task_digest(task)
    lease = str(task["lease_nonce"])
    started_path, terminal_path = _control_paths(root, lease)

    if terminal_path.exists():
        cached = _validate_cached(read_json(terminal_path), digest, task)
        if output_path is not None:
            atomic_write_json(output_path, cached, 0o600)
        return cached

    atomic_write_json(
        started_path,
        {
            "schema_version": 1,
            "state": "STARTED",
            "lease_nonce": lease,
            "task_sha256": digest,
            "unit_id": task["unit_id"],
            "mandate_sha256": task["mandate_sha256"],
            "started_at_utc": utc_now(),
        },
        0o600,
    )

    try:
        kernel_result = execute_unit(
            root,
            plan,
            str(task["unit_id"]),
            publish=False,
            lease_nonce=lease,
        )
        envelope = {
            "schema_version": 1,
            "status": "PASS",
            "task_sha256": digest,
            "thread_id": task["thread_id"],
            "objective_sha256": task["objective_sha256"],
            "unit_id": task["unit_id"],
            "lease_nonce": lease,
            "mandate_sha256": manifest["mandate_sha256"],
            "base_commit": task["base_commit"],
            "result_commit": kernel_result["result_commit"],
            "result_branch": kernel_result["result_branch"],
            "changed_paths": kernel_result["changed_paths"],
            "log_sha256": kernel_result["log_sha256"],
            "published": False,
            "completed_at_utc": utc_now(),
        }
    except Exception as exc:
        envelope = {
            "schema_version": 1,
            "status": "FAIL",
            "task_sha256": digest,
            "thread_id": task["thread_id"],
            "unit_id": task["unit_id"],
            "lease_nonce": lease,
            "mandate_sha256": task["mandate_sha256"],
            "base_commit": task["base_commit"],
            "error": str(exc),
            "completed_at_utc": utc_now(),
        }
        atomic_write_json(terminal_path, envelope, 0o600)
        if output_path is not None:
            atomic_write_json(output_path, envelope, 0o600)
        raise

    atomic_write_json(terminal_path, envelope, 0o600)
    if output_path is not None:
        atomic_write_json(output_path, envelope, 0o600)
    return envelope


def classify_terminal(root: Path, lease: str) -> str:
    if not NONCE_RE.fullmatch(lease):
        raise VOSFailure("lease_nonce non valido")
    started_path, terminal_path = _control_paths(root, lease)
    if terminal_path.exists():
        status = str(read_json(terminal_path).get("status", ""))
        return "TERMINAL_PASS" if status == "PASS" else "TERMINAL_FAIL"
    if started_path.exists():
        return "DEAD_WITHOUT_MARKER"
    return "NOT_STARTED"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output")
    parser.add_argument("--classify-lease")
    args = parser.parse_args()
    try:
        root = repo_root(Path(args.repo))
        if args.classify_lease:
            print(json.dumps({"status": classify_terminal(root, args.classify_lease)}, sort_keys=True))
            return 0
        task = read_json(Path(args.task).resolve())
        if not isinstance(task, dict):
            raise VOSFailure("task JSON non oggetto")
        output = Path(args.output).resolve() if args.output else None
        result = run_task(root, task, output_path=output)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == "PASS" else 2
    except VOSFailure as exc:
        print(f"ERRORE VOS WORKER: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
