#!/usr/bin/env python3
"""Durable context rollover for the VOS Sol control plane.

Conversation state is never canonical. A completed zero-shuttle run is sealed
into a checkpoint. Immediately before opening a new Codex thread, this helper
performs its own deterministic read-only live-state probe (Git HEAD, clean
worktree, platform), seals that probe with a nonce + SHA-256, and injects both
sealed envelopes into a brand-new Sol thread. The model is not trusted to run
tools for certification; controller-produced evidence is canonical.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import secrets
import subprocess
import sys
from pathlib import Path
from typing import Any

import vos_sol_bridge as bridge

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
NONCE_RE = re.compile(r"^[0-9a-f]{32}$")


class RolloverError(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    import hashlib
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with tmp.open("wb") as handle:
            handle.write(canonical_json(value))
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
        raise RolloverError(f"file mancante: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RolloverError(f"JSON non valido: {path}") from exc


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=str(repo), text=True, capture_output=True, check=False, timeout=30
    )
    if completed.returncode != 0:
        raise RolloverError(f"git {' '.join(args)} rc={completed.returncode}")
    return completed.stdout.strip()


def validate_inputs(task: dict[str, Any], worker: dict[str, Any], prior_bridge: dict[str, Any]) -> None:
    try:
        bridge.validate_worker_result(task, worker)
    except bridge.BridgeError as exc:
        raise RolloverError(str(exc)) from exc
    if prior_bridge.get("schema_version") != 1 or prior_bridge.get("status") != "PASS":
        raise RolloverError("bridge precedente non PASS")
    if prior_bridge.get("decision") != "ACCEPT":
        raise RolloverError("bridge precedente non ACCEPT")
    if prior_bridge.get("thread_id_match") != "PASS":
        raise RolloverError("bridge precedente senza thread match")
    if prior_bridge.get("thread_id") != task.get("thread_id"):
        raise RolloverError("thread bridge/task mismatch")
    task_sha = sha256_bytes(canonical_json(task))
    if prior_bridge.get("task_sha256") != task_sha:
        raise RolloverError("bridge task_sha256 mismatch")


def create_checkpoint(*, repo: Path, task_path: Path, worker_result_path: Path,
                      bridge_result_path: Path, checkpoint_path: Path) -> dict[str, Any]:
    task = read_json(task_path)
    worker = read_json(worker_result_path)
    prior = read_json(bridge_result_path)
    if not all(isinstance(value, dict) for value in (task, worker, prior)):
        raise RolloverError("task/worker/bridge devono essere oggetti JSON")
    validate_inputs(task, worker, prior)
    head = git(repo, "rev-parse", "HEAD")
    if not COMMIT_RE.fullmatch(head):
        raise RolloverError("HEAD live non valido")
    if git(repo, "status", "--porcelain"):
        raise RolloverError("repo non pulita al checkpoint")
    if head != task.get("base_commit"):
        raise RolloverError("HEAD live differisce dalla base sigillata")
    worker_sha = sha256_file(worker_result_path)
    if prior.get("worker_result_sha256") != worker_sha:
        raise RolloverError("bridge worker_result_sha256 mismatch")

    payload = {
        "schema_version": 1,
        "source_thread_id": task["thread_id"],
        "objective_sha256": task["objective_sha256"],
        "task_sha256": sha256_bytes(canonical_json(task)),
        "worker_result_sha256": worker_sha,
        "prior_bridge_result_sha256": sha256_file(bridge_result_path),
        "unit_id": task["unit_id"],
        "lease_nonce": task["lease_nonce"],
        "mandate_sha256": task["mandate_sha256"],
        "expected_repo_head": head,
        "result_commit": worker["result_commit"],
        "prior_decision": prior["decision"],
        "next_action": prior.get("next_action", ""),
        "expected_platform": platform.system(),
    }
    digest = sha256_bytes(canonical_json(payload))
    envelope = {"schema_version": 1, "checkpoint": payload, "checkpoint_sha256": digest}
    atomic_json(checkpoint_path, envelope)
    return envelope


def validate_checkpoint(envelope: Any) -> tuple[dict[str, Any], str]:
    if not isinstance(envelope, dict) or set(envelope) != {"schema_version", "checkpoint", "checkpoint_sha256"}:
        raise RolloverError("checkpoint envelope schema non valido")
    if envelope["schema_version"] != 1 or not isinstance(envelope["checkpoint"], dict):
        raise RolloverError("checkpoint envelope non valido")
    digest = str(envelope["checkpoint_sha256"])
    if not SHA256_RE.fullmatch(digest):
        raise RolloverError("checkpoint_sha256 non valido")
    actual = sha256_bytes(canonical_json(envelope["checkpoint"]))
    if actual != digest:
        raise RolloverError("checkpoint alterato: sha256 mismatch")
    checkpoint = envelope["checkpoint"]
    required = {
        "schema_version", "source_thread_id", "objective_sha256", "task_sha256",
        "worker_result_sha256", "prior_bridge_result_sha256", "unit_id", "lease_nonce",
        "mandate_sha256", "expected_repo_head", "result_commit", "prior_decision",
        "next_action", "expected_platform",
    }
    if set(checkpoint) != required or checkpoint.get("schema_version") != 1:
        raise RolloverError("checkpoint payload schema non valido")
    if not bridge.UUID_RE.fullmatch(str(checkpoint["source_thread_id"])):
        raise RolloverError("source_thread_id non valido")
    for key in ("objective_sha256", "task_sha256", "worker_result_sha256", "prior_bridge_result_sha256", "mandate_sha256"):
        if not SHA256_RE.fullmatch(str(checkpoint[key])):
            raise RolloverError(f"{key} non valido")
    for key in ("expected_repo_head", "result_commit"):
        if not COMMIT_RE.fullmatch(str(checkpoint[key])):
            raise RolloverError(f"{key} non valido")
    if checkpoint["prior_decision"] != "ACCEPT":
        raise RolloverError("checkpoint non deriva da ACCEPT")
    return checkpoint, digest


def create_live_probe(*, repo: Path, checkpoint: dict[str, Any], evidence: Path) -> tuple[dict[str, Any], str]:
    head = git(repo, "rev-parse", "HEAD")
    status = git(repo, "status", "--porcelain")
    system = platform.system()
    if head != checkpoint["expected_repo_head"]:
        raise RolloverError("stato Git live è cambiato prima del rollover")
    if status:
        raise RolloverError("repo dirty prima del rollover")
    if system != checkpoint["expected_platform"]:
        raise RolloverError("piattaforma live diversa dal checkpoint")
    payload = {
        "schema_version": 1,
        "nonce": secrets.token_hex(16),
        "repo_head": head,
        "worktree_clean": True,
        "platform": system,
    }
    digest = sha256_bytes(canonical_json(payload))
    envelope = {"schema_version": 1, "probe": payload, "live_probe_sha256": digest}
    atomic_json(evidence / "context-live-probe.json", envelope)
    return envelope, digest


def validate_live_probe(envelope: Any, checkpoint: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if not isinstance(envelope, dict) or set(envelope) != {"schema_version", "probe", "live_probe_sha256"}:
        raise RolloverError("live probe envelope schema non valido")
    if envelope.get("schema_version") != 1 or not isinstance(envelope.get("probe"), dict):
        raise RolloverError("live probe envelope non valido")
    probe = envelope["probe"]
    required = {"schema_version", "nonce", "repo_head", "worktree_clean", "platform"}
    if set(probe) != required or probe.get("schema_version") != 1:
        raise RolloverError("live probe payload schema non valido")
    digest = str(envelope["live_probe_sha256"])
    if not SHA256_RE.fullmatch(digest) or digest != sha256_bytes(canonical_json(probe)):
        raise RolloverError("live probe alterato: sha256 mismatch")
    if not NONCE_RE.fullmatch(str(probe["nonce"])):
        raise RolloverError("live probe nonce non valido")
    if probe["repo_head"] != checkpoint["expected_repo_head"] or not COMMIT_RE.fullmatch(str(probe["repo_head"])):
        raise RolloverError("live probe HEAD mismatch")
    if probe["worktree_clean"] is not True:
        raise RolloverError("live probe worktree non pulita")
    if probe["platform"] != checkpoint["expected_platform"]:
        raise RolloverError("live probe platform mismatch")
    return probe, digest


def no_file_changes(events: list[dict[str, Any]]) -> bool:
    return not any(
        event.get("type") == "item.completed"
        and isinstance(event.get("item"), dict)
        and event["item"].get("type") == "file_change"
        for event in events
    )


def rollover(*, codex: str, codex_home: Path, model: str, repo: Path,
             checkpoint_path: Path, evidence: Path, result_path: Path, timeout: int) -> dict[str, Any]:
    envelope = read_json(checkpoint_path)
    checkpoint, checkpoint_sha = validate_checkpoint(envelope)
    source_thread = str(checkpoint["source_thread_id"]).lower()

    # Idempotent replay still verifies live state before returning cached evidence.
    live_head = git(repo, "rev-parse", "HEAD")
    if live_head != checkpoint["expected_repo_head"]:
        raise RolloverError("stato Git live è cambiato prima del rollover")
    if git(repo, "status", "--porcelain"):
        raise RolloverError("repo dirty prima del rollover")
    if platform.system() != checkpoint["expected_platform"]:
        raise RolloverError("piattaforma live diversa dal checkpoint")
    if result_path.exists():
        cached = read_json(result_path)
        if not isinstance(cached, dict) or cached.get("checkpoint_sha256") != checkpoint_sha:
            raise RolloverError("cache rollover collision")
        return cached

    probe_envelope, live_probe_sha = create_live_probe(repo=repo, checkpoint=checkpoint, evidence=evidence)
    probe, verified_probe_sha = validate_live_probe(probe_envelope, checkpoint)
    if verified_probe_sha != live_probe_sha:
        raise RolloverError("live probe hash interno mismatch")

    prompt = (
        "You are continuing a VOS control-plane task from durable state. The prior conversation is not canonical. "
        "The VOS controller has already performed the read-only live-state verification; do not run shell commands, tools, or modify files. "
        f"Checkpoint SHA256: {checkpoint_sha}. Checkpoint JSON: {json.dumps(checkpoint, sort_keys=True)}. "
        f"Live probe SHA256: {live_probe_sha}. Live probe JSON: {json.dumps(probe, sort_keys=True)}. "
        "Return ONLY JSON with exactly these keys: "
        '{"checkpoint_sha256":"<exact checkpoint hash>","live_probe_sha256":"<exact live probe hash>",'
        '"source_thread_id":"<exact old thread>","observed_head":"<repo_head from live probe>",'
        '"platform":"<platform from live probe>","worktree_clean":true,'
        '"prior_result_commit":"<result commit from checkpoint>","continuation":"CONTINUE"}'
    )
    jsonl = evidence / "context-rollover.jsonl"
    stderr = evidence / "context-rollover.stderr"
    events, elapsed = bridge.run_codex(
        [codex, "exec", "--json", "--model", model, "--sandbox", "read-only", prompt],
        cwd=repo,
        jsonl=jsonl,
        stderr=stderr,
        timeout=timeout,
    )
    new_thread = bridge.thread_id(events)
    if new_thread == source_thread:
        raise RolloverError("rollover non ha creato un nuovo thread")
    if not bridge.prove_model(codex_home, new_thread, model, events):
        raise RolloverError("modello effettivo del nuovo thread non provato")
    if not no_file_changes(events):
        raise RolloverError("rollover ha prodotto file_change")

    response = bridge.strict_json_message(bridge.final_agent_message(events))
    required = {
        "checkpoint_sha256", "live_probe_sha256", "source_thread_id", "observed_head",
        "platform", "worktree_clean", "prior_result_commit", "continuation",
    }
    if set(response) != required:
        raise RolloverError("schema risposta rollover non valido")
    expected = {
        "checkpoint_sha256": checkpoint_sha,
        "live_probe_sha256": live_probe_sha,
        "source_thread_id": source_thread,
        "observed_head": probe["repo_head"],
        "platform": probe["platform"],
        "worktree_clean": True,
        "prior_result_commit": checkpoint["result_commit"],
        "continuation": "CONTINUE",
    }
    if response != expected:
        raise RolloverError("risposta rollover non coincide con checkpoint/live probe")

    result = {
        "schema_version": 1,
        "status": "PASS",
        "checkpoint_sha256": checkpoint_sha,
        "checkpoint_hash_match": "PASS",
        "live_probe_sha256": live_probe_sha,
        "live_probe_hash_match": "PASS",
        "source_thread_id": source_thread,
        "new_thread_id": new_thread,
        "new_thread_distinct": "PASS",
        "model_actual_proven": model,
        "live_repo_head": probe["repo_head"],
        "live_platform": probe["platform"],
        "live_state_match": "PASS",
        "worktree_clean": True,
        "prior_result_commit": checkpoint["result_commit"],
        "continuation": "CONTINUE",
        "elapsed_seconds": round(elapsed, 3),
        "jsonl_sha256": sha256_file(jsonl),
    }
    atomic_json(result_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    seal = sub.add_parser("seal")
    seal.add_argument("--repo", required=True)
    seal.add_argument("--task", required=True)
    seal.add_argument("--worker-result", required=True)
    seal.add_argument("--bridge-result", required=True)
    seal.add_argument("--checkpoint", required=True)

    run = sub.add_parser("run")
    run.add_argument("--codex", default="codex")
    run.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", ""))
    run.add_argument("--model", default="gpt-5.6-sol")
    run.add_argument("--repo", required=True)
    run.add_argument("--checkpoint", required=True)
    run.add_argument("--evidence", required=True)
    run.add_argument("--result", required=True)
    run.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    try:
        if args.command == "seal":
            result = create_checkpoint(
                repo=Path(args.repo).resolve(),
                task_path=Path(args.task).resolve(),
                worker_result_path=Path(args.worker_result).resolve(),
                bridge_result_path=Path(args.bridge_result).resolve(),
                checkpoint_path=Path(args.checkpoint).resolve(),
            )
        else:
            if not args.codex_home:
                raise RolloverError("CODEX_HOME mancante")
            result = rollover(
                codex=args.codex,
                codex_home=Path(args.codex_home).resolve(),
                model=args.model,
                repo=Path(args.repo).resolve(),
                checkpoint_path=Path(args.checkpoint).resolve(),
                evidence=Path(args.evidence).resolve(),
                result_path=Path(args.result).resolve(),
                timeout=args.timeout,
            )
        print(json.dumps(result, sort_keys=True))
        return 0
    except (RolloverError, bridge.BridgeError) as exc:
        print(f"ERRORE VOS ROLLOVER: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
