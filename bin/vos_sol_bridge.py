#!/usr/bin/env python3
"""Codex/Sol bridge for zero-prompt-shuttling VOS runs.

The bridge follows the event handling used by the official Codex SDK: JSONL is
parsed line-by-line, ``thread.started.thread_id`` is authoritative, and the
final response is the latest completed ``agent_message``. A start turn selects
one already-sealed SAFE_AUTO unit from a deterministic catalog. A resume turn
feeds the worker result back into the exact same thread and verifies both the
thread id and the result hash echoed by the model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
UNIT_RE = re.compile(r"^[A-Z][A-Z0-9_-]{2,63}$")
MODEL_RE = re.compile(r"^gpt-[A-Za-z0-9._-]+$")


class BridgeError(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    data = canonical_json(value)
    try:
        with tmp.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BridgeError(f"file mancante: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BridgeError(f"JSON non valido: {path}") from exc


def parse_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise BridgeError(f"JSONL mancante: {path}") from exc
    for index, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BridgeError(f"JSONL invalido linea {index}") from exc
        if not isinstance(item, dict):
            raise BridgeError(f"evento JSONL non oggetto linea {index}")
        events.append(item)
    if not events:
        raise BridgeError("stream JSONL vuoto")
    return events


def thread_id(events: list[dict[str, Any]]) -> str:
    ids = {
        str(event.get("thread_id", "")).lower()
        for event in events
        if event.get("type") == "thread.started" and UUID_RE.fullmatch(str(event.get("thread_id", "")))
    }
    if len(ids) != 1:
        raise BridgeError(f"atteso un solo thread.started, trovati {len(ids)}")
    return next(iter(ids))


def final_agent_message(events: list[dict[str, Any]]) -> str:
    text = ""
    for event in events:
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            text = item["text"]
    if not text:
        raise BridgeError("agent_message finale mancante")
    return text.strip()


def strict_json_message(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BridgeError("risposta Sol non è JSON puro") from exc
    if not isinstance(value, dict):
        raise BridgeError("risposta Sol JSON non oggetto")
    return value


def run_codex(command: list[str], *, cwd: Path, jsonl: Path, stderr: Path, timeout: int) -> tuple[list[dict[str, Any]], float]:
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with jsonl.open("w", encoding="utf-8") as out, stderr.open("w", encoding="utf-8") as err:
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                stdout=out,
                stderr=err,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise BridgeError(f"Codex timeout dopo {timeout}s") from exc
    if completed.returncode != 0:
        raise BridgeError(f"Codex terminato rc={completed.returncode}")
    return parse_jsonl(jsonl), time.monotonic() - started


def validate_catalog(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise BridgeError("catalogo vuoto/non lista")
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    required = {"unit_id", "plan_path", "plan_sha256", "mandate_sha256", "base_commit"}
    for raw in value:
        if not isinstance(raw, dict) or set(raw) != required:
            raise BridgeError("catalog entry schema non valido")
        item = {key: str(raw[key]) for key in required}
        if not UNIT_RE.fullmatch(item["unit_id"]):
            raise BridgeError("unit_id catalogo non valido")
        if item["unit_id"] in seen:
            raise BridgeError("unit_id duplicato nel catalogo")
        seen.add(item["unit_id"])
        if not SHA256_RE.fullmatch(item["plan_sha256"]):
            raise BridgeError("plan_sha256 catalogo non valido")
        if not SHA256_RE.fullmatch(item["mandate_sha256"]):
            raise BridgeError("mandate_sha256 catalogo non valido")
        if not COMMIT_RE.fullmatch(item["base_commit"]):
            raise BridgeError("base_commit catalogo non valido")
        plan = Path(item["plan_path"])
        if plan.is_absolute() or ".." in plan.parts or not item["plan_path"]:
            raise BridgeError("plan_path catalogo non sicuro")
        out.append(item)
    return sorted(out, key=lambda x: x["unit_id"])


def _find_rollout(codex_home: Path, tid: str) -> Path | None:
    sessions = codex_home / "sessions"
    if not sessions.is_dir():
        return None
    candidates = sorted(
        (p for p in sessions.rglob("*.jsonl") if tid in p.name.lower()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _models(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in {"model", "model_id", "model_name"} and isinstance(child, str) and MODEL_RE.fullmatch(child):
                found.add(child)
            found.update(_models(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_models(child))
    return found


def prove_model(codex_home: Path, tid: str, expected: str, events: list[dict[str, Any]]) -> bool:
    models = _models(events)
    rollout = _find_rollout(codex_home, tid)
    if rollout is not None:
        try:
            models.update(_models(parse_jsonl(rollout)))
        except BridgeError:
            pass
    return expected in models


def start(*, codex: str, codex_home: Path, model: str, objective: str, catalog_path: Path,
          workspace: Path, evidence: Path, task_path: Path, timeout: int) -> dict[str, Any]:
    if not MODEL_RE.fullmatch(model):
        raise BridgeError("model non valido")
    catalog = validate_catalog(read_json(catalog_path))
    objective_sha = sha256_bytes(objective.encode("utf-8"))
    allowed = [item["unit_id"] for item in catalog]
    prompt = (
        "You are the VOS control-plane planner. No shell commands, no file writes. "
        "Choose exactly one already-sealed SAFE_AUTO unit that best satisfies the objective. "
        f"Objective: {objective}\nAllowed unit_ids: {json.dumps(allowed)}\n"
        'Return ONLY JSON, no markdown: {"unit_id":"<one allowed id>","reason":"<brief>"}'
    )
    jsonl = evidence / "sol-start.jsonl"
    stderr = evidence / "sol-start.stderr"
    events, elapsed = run_codex(
        [codex, "exec", "--json", "--model", model, "--sandbox", "read-only", "--skip-git-repo-check", prompt],
        cwd=workspace,
        jsonl=jsonl,
        stderr=stderr,
        timeout=timeout,
    )
    tid = thread_id(events)
    if not prove_model(codex_home, tid, model, events):
        raise BridgeError("modello effettivo non provato")
    choice = strict_json_message(final_agent_message(events))
    if set(choice) != {"unit_id", "reason"} or not isinstance(choice.get("reason"), str):
        raise BridgeError("schema scelta Sol non valido")
    selected = next((item for item in catalog if item["unit_id"] == choice.get("unit_id")), None)
    if selected is None:
        raise BridgeError("Sol ha selezionato unità fuori catalogo")
    task = {
        "schema_version": 1,
        "unit_id": selected["unit_id"],
        "plan_path": selected["plan_path"],
        "plan_sha256": selected["plan_sha256"],
        "mandate_sha256": selected["mandate_sha256"],
        "base_commit": selected["base_commit"],
        "lease_nonce": secrets.token_hex(16),
        "thread_id": tid,
        "objective_sha256": objective_sha,
    }
    atomic_json(task_path, task)
    return {
        "schema_version": 1,
        "status": "PASS",
        "phase": "START",
        "thread_id": tid,
        "model_actual_proven": model,
        "selected_unit": selected["unit_id"],
        "objective_sha256": objective_sha,
        "task_sha256": sha256_bytes(canonical_json(task)),
        "elapsed_seconds": round(elapsed, 3),
        "jsonl_sha256": sha256_file(jsonl),
    }


def validate_worker_result(task: dict[str, Any], result: dict[str, Any]) -> None:
    if result.get("schema_version") != 1 or result.get("status") != "PASS":
        raise BridgeError("worker result non PASS")
    for key in ("thread_id", "lease_nonce", "mandate_sha256", "base_commit", "objective_sha256", "unit_id"):
        if result.get(key) != task.get(key):
            raise BridgeError(f"worker result mismatch: {key}")
    expected_task_sha = sha256_bytes(canonical_json(task))
    if result.get("task_sha256") != expected_task_sha:
        raise BridgeError("worker result task_sha256 mismatch")
    if not COMMIT_RE.fullmatch(str(result.get("result_commit", ""))):
        raise BridgeError("worker result_commit non valido")
    changed = result.get("changed_paths")
    if not isinstance(changed, list) or not all(isinstance(x, str) for x in changed):
        raise BridgeError("worker changed_paths non valido")


def resume(*, codex: str, task_path: Path, worker_result_path: Path, workspace: Path,
           evidence: Path, bridge_result_path: Path, timeout: int) -> dict[str, Any]:
    task = read_json(task_path)
    worker = read_json(worker_result_path)
    if not isinstance(task, dict) or not isinstance(worker, dict):
        raise BridgeError("task/worker result non oggetto")
    validate_worker_result(task, worker)
    tid = str(task["thread_id"]).lower()
    if not UUID_RE.fullmatch(tid):
        raise BridgeError("thread_id task non valido")
    result_sha = sha256_file(worker_result_path)
    task_sha = sha256_bytes(canonical_json(task))

    if bridge_result_path.exists():
        cached = read_json(bridge_result_path)
        if not isinstance(cached, dict):
            raise BridgeError("bridge cache non oggetto")
        if cached.get("task_sha256") != task_sha or cached.get("worker_result_sha256") != result_sha:
            raise BridgeError("bridge cache collision")
        return cached

    summary = {
        "status": worker["status"],
        "unit_id": worker["unit_id"],
        "lease_nonce": worker["lease_nonce"],
        "mandate_sha256": worker["mandate_sha256"],
        "base_commit": worker["base_commit"],
        "result_commit": worker["result_commit"],
        "changed_paths": worker["changed_paths"],
        "worker_result_sha256": result_sha,
    }
    prompt = (
        "VOS worker completed the sealed task. Evaluate only the trusted result summary below. "
        "Do not run shell commands and do not write files. "
        f"Trusted result: {json.dumps(summary, sort_keys=True)}\n"
        'Return ONLY JSON, no markdown: {"decision":"ACCEPT|REJECT","evidence_hash":"<worker_result_sha256 exactly>","next_action":"<brief>"}'
    )
    jsonl = evidence / "sol-resume.jsonl"
    stderr = evidence / "sol-resume.stderr"
    events, elapsed = run_codex(
        [codex, "exec", "resume", tid, "--json", "--skip-git-repo-check", prompt],
        cwd=workspace,
        jsonl=jsonl,
        stderr=stderr,
        timeout=timeout,
    )
    resumed = thread_id(events)
    if resumed != tid:
        raise BridgeError("exact resume ha cambiato thread_id")
    decision = strict_json_message(final_agent_message(events))
    if set(decision) != {"decision", "evidence_hash", "next_action"}:
        raise BridgeError("schema decisione Sol non valido")
    if decision.get("decision") not in {"ACCEPT", "REJECT"}:
        raise BridgeError("decisione Sol non valida")
    if decision.get("evidence_hash") != result_sha:
        raise BridgeError("Sol non ha restituito l'hash esatto del worker result")
    if not isinstance(decision.get("next_action"), str):
        raise BridgeError("next_action Sol non valida")
    envelope = {
        "schema_version": 1,
        "status": "PASS",
        "phase": "RESUME",
        "thread_id": tid,
        "thread_id_match": "PASS",
        "task_sha256": task_sha,
        "worker_result_sha256": result_sha,
        "decision": decision["decision"],
        "next_action": decision["next_action"],
        "elapsed_seconds": round(elapsed, 3),
        "jsonl_sha256": sha256_file(jsonl),
    }
    atomic_json(bridge_result_path, envelope)
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("--codex", default="codex")
    p_start.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", ""))
    p_start.add_argument("--model", default="gpt-5.6-sol")
    p_start.add_argument("--objective", required=True)
    p_start.add_argument("--catalog", required=True)
    p_start.add_argument("--workspace", required=True)
    p_start.add_argument("--evidence", required=True)
    p_start.add_argument("--task", required=True)
    p_start.add_argument("--timeout", type=int, default=300)

    p_resume = sub.add_parser("resume")
    p_resume.add_argument("--codex", default="codex")
    p_resume.add_argument("--task", required=True)
    p_resume.add_argument("--worker-result", required=True)
    p_resume.add_argument("--workspace", required=True)
    p_resume.add_argument("--evidence", required=True)
    p_resume.add_argument("--bridge-result", required=True)
    p_resume.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    try:
        if args.command == "start":
            if not args.codex_home:
                raise BridgeError("CODEX_HOME mancante")
            result = start(
                codex=args.codex,
                codex_home=Path(args.codex_home).resolve(),
                model=args.model,
                objective=args.objective,
                catalog_path=Path(args.catalog).resolve(),
                workspace=Path(args.workspace).resolve(),
                evidence=Path(args.evidence).resolve(),
                task_path=Path(args.task).resolve(),
                timeout=args.timeout,
            )
        else:
            result = resume(
                codex=args.codex,
                task_path=Path(args.task).resolve(),
                worker_result_path=Path(args.worker_result).resolve(),
                workspace=Path(args.workspace).resolve(),
                evidence=Path(args.evidence).resolve(),
                bridge_result_path=Path(args.bridge_result).resolve(),
                timeout=args.timeout,
            )
        print(json.dumps(result, sort_keys=True))
        return 0
    except BridgeError as exc:
        print(f"ERRORE VOS BRIDGE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
