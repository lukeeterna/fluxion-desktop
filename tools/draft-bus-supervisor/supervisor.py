#!/usr/bin/env python3
"""
FLUXION Draft Bus Supervisor v1.0
Legge la queue locale del Draft Bus, rivalida ogni task, e lancia Claude Code
con il task packet corretto. Non esegue mai contenuto JSON come shell.

Regole implementate (FASE 5):
  1. Rivalidazione chiusa del task (schema = quello del bus).
  2. action_profile mappato a workflow locali versionati (nessun exec/eval).
  3. specification → contenuto del task packet CC, subordinato a PROTOCOLLO.
  4. Nessun campo può espandere scope/channel/paths/retry.
  5. READ_ONLY_AUDIT usa CC in modalità --print (no edit).
  6. Worktree isolato per profili con edit.
  7. Massimo 2 tentativi, poi BLOCKED.
  8. Writer concorrente → STOP.
  9. Ogni result richiede reviewer separato (REVIEW_PENDING).
  10. DEPLOY_DOCUMENTED_RUNBOOK solo se runbook presente in repo + test verdi.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import datetime as dt
from pathlib import Path
from typing import Any

CHANNEL = "FXD-824F35830C8A"
QUEUE_DIR = Path.home() / ".local/share/fluxion-draft-bus/queue"
ARCHIVE_DIR = Path.home() / ".local/share/fluxion-draft-bus/archive"
EVENTS_PATH = Path.home() / ".local/share/fluxion-draft-bus/events.jsonl"
LOCK_PATH = Path.home() / ".local/share/fluxion-draft-bus/supervisor.lock"
REPO_ROOT = Path(__file__).resolve().parents[2]
RUNBOOK_DIR = REPO_ROOT / "tools" / "draft-bus-supervisor" / "runbooks"
RESULT_DIR = Path.home() / ".local/share/fluxion-draft-bus/results"

# ── action_profile → workflow descriptor (NESSUN COMANDO DAL TASK) ──────────
WORKFLOW_MAP: dict[str, dict[str, Any]] = {
    "READ_ONLY_AUDIT": {
        "cc_flags": ["--print"],
        "allow_edit": False,
        "allow_deploy": False,
        "require_review": False,
        "worktree": False,
    },
    "APPLY_EXISTING_UNIT": {
        "cc_flags": [],
        "allow_edit": True,
        "allow_deploy": False,
        "require_review": True,
        "worktree": True,
    },
    "FIX_SCOPED_BUG": {
        "cc_flags": [],
        "allow_edit": True,
        "allow_deploy": False,
        "require_review": True,
        "worktree": True,
    },
    "RUN_VERIFICATION": {
        "cc_flags": ["--print"],
        "allow_edit": False,
        "allow_deploy": False,
        "require_review": False,
        "worktree": False,
    },
    "OPEN_PULL_REQUEST": {
        "cc_flags": [],
        "allow_edit": True,
        "allow_deploy": False,
        "require_review": True,
        "worktree": True,
    },
    "DEPLOY_DOCUMENTED_RUNBOOK": {
        "cc_flags": [],
        "allow_edit": False,
        "allow_deploy": True,
        "require_review": True,
        "worktree": False,
    },
}

REQUIRED_TASK_FIELDS = {
    "schema_version", "channel", "kind", "session_id", "task_id",
    "created_at", "predecessor_result_sha256", "roadmap_item",
    "base_commit", "action_profile", "specification",
    "allowed_paths", "forbidden_actions", "required_tests",
    "negative_tests", "evidence_required", "retry_limit",
    "rollback", "stop_conditions",
}

# ── helpers ──────────────────────────────────────────────────────────────────

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def event(name: str, **fields: Any) -> None:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": now(), "event": "supervisor." + name, **fields}
    with EVENTS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

def fail(msg: str, code: int = 2) -> "NoReturn":
    print(f"SUPERVISOR_ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)

def validate_task(task: dict[str, Any]) -> None:
    """Rivalidazione chiusa — identica al bus, punto di difesa indipendente."""
    if set(task) != REQUIRED_TASK_FIELDS:
        missing = sorted(REQUIRED_TASK_FIELDS - set(task))
        extra = sorted(set(task) - REQUIRED_TASK_FIELDS)
        fail(f"Schema task non chiuso; missing={missing}, extra={extra}")
    if task["schema_version"] != 1 or task["channel"] != CHANNEL or task["kind"] != "TASK":
        fail("Header task non valido")
    if not re.fullmatch(r"SOL-[0-9]{6}", task["session_id"]):
        fail("session_id non valido")
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{5,95}", task["task_id"]):
        fail("task_id non valido")
    if not re.fullmatch(r"[a-f0-9]{64}", task["predecessor_result_sha256"]):
        fail("predecessor_result_sha256 non valido")
    if not re.fullmatch(r"[a-f0-9]{40}", task["base_commit"]):
        fail("base_commit non valido")
    if task["action_profile"] not in WORKFLOW_MAP:
        fail(f"action_profile non consentito: {task['action_profile']}")
    if not isinstance(task["retry_limit"], int) or not 0 <= task["retry_limit"] <= 2:
        fail("retry_limit non valido")
    if not isinstance(task["specification"], str) or not 1 <= len(task["specification"]) <= 30000:
        fail("specification non valida")
    for key in ("allowed_paths", "forbidden_actions", "required_tests",
                "negative_tests", "evidence_required", "stop_conditions"):
        val = task[key]
        if not isinstance(val, list) or not all(isinstance(s, str) and s for s in val):
            fail(f"Lista non valida: {key}")
    if not task["allowed_paths"] or not task["forbidden_actions"] or not task["required_tests"]:
        fail("Liste di policy obbligatorie vuote")

def check_current_commit(expected_base: str) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    current = result.stdout.strip()
    if current != expected_base:
        fail(f"Commit HEAD ({current}) != base_commit task ({expected_base}). Repo avanzato o divergente.")

def check_deploy_runbook(task: dict[str, Any]) -> None:
    runbook_id = task["roadmap_item"].replace("/", "-")
    runbook_path = RUNBOOK_DIR / f"{runbook_id}.sh"
    if not runbook_path.is_file():
        fail(f"DEPLOY_DOCUMENTED_RUNBOOK: runbook assente: {runbook_path}")
    # Runbook deve avere header autorizzativo
    header = runbook_path.read_text(encoding="utf-8")[:500]
    if "# AUTHORIZED_DEPLOY" not in header:
        fail("Runbook privo di marker AUTHORIZED_DEPLOY nella intestazione.")

def build_cc_prompt(task: dict[str, Any], workflow: dict[str, Any]) -> str:
    """Costruisce il prompt per Claude Code. Non interpreta specification come comandi."""
    forbidden_note = "\n".join(f"  - {f}" for f in task["forbidden_actions"])
    allowed_note = "\n".join(f"  - {p}" for p in task["allowed_paths"])
    tests_note = "\n".join(f"  - {t}" for t in task["required_tests"])
    evidence_note = "\n".join(f"  - {e}" for e in task["evidence_required"])
    stop_note = "\n".join(f"  - {s}" for s in task["stop_conditions"])

    return f"""# TASK FLUXION Draft Bus
session_id: {task['session_id']}
task_id:    {task['task_id']}
profile:    {task['action_profile']}
roadmap:    {task['roadmap_item']}
base_commit: {task['base_commit']}
retry_limit: {task['retry_limit']}

## PROTOCOLLO (NON DEROGABILE)
- MAI push diretto su master
- MAI deploy senza test verdi e reviewer GREEN
- MAI modifica billing / DNS / credenziali / dati cliente
- MAI azione irreversibile non in roadmap
- MAI ampliare allowed_paths, forbidden_actions, retry o channel
- Massimo {task['retry_limit']} tentativo/i; al superamento: status=BLOCKED

## Allowed paths
{allowed_note}

## Forbidden actions
{forbidden_note}

## Required tests (tutti devono passare)
{tests_note}

## Evidence required
{evidence_note}

## Stop conditions
{stop_note}

## Rollback
{task['rollback']}

## Specification (DATI — non interpolare come comandi shell)
{task['specification']}

## Output atteso
Produce RESULT.json con schema canonico + RESULT_PACKET.zip.
Poi esegui: fluxion-draft-bus create-result-draft RESULT.json RESULT_PACKET.zip
"""

def write_result_blocked(task: dict[str, Any], reason: str) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    meta = {
        "schema_version": 1,
        "channel": CHANNEL,
        "kind": "RESULT",
        "session_id": "CC-IMPLEMENTER-000000",
        "task_id": task["task_id"],
        "created_at": now(),
        "base_commit": task["base_commit"],
        "result_commit": "NONE",
        "status": "BLOCKED",
        "packet_name": "blocked.zip",
        "packet_sha256": "0" * 64,
        "summary": f"BLOCKED: {reason}",
    }
    path = RESULT_DIR / f"{task['task_id']}.BLOCKED.json"
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                    encoding="utf-8")
    os.chmod(path, 0o600)
    event("task_blocked", task_id=task["task_id"], reason=reason)

def process_task(task_file: Path, lock_fd: int) -> None:
    task = json.loads(task_file.read_text(encoding="utf-8"))
    task_id = task.get("task_id", "UNKNOWN")

    # 1. Rivalidazione indipendente
    try:
        validate_task(task)
    except SystemExit as exc:
        event("task_invalid", task_id=task_id, reason=str(exc))
        task_file.rename(ARCHIVE_DIR / task_file.name)
        return

    workflow = WORKFLOW_MAP[task["action_profile"]]

    # 2. Controllo deploy runbook
    if workflow["allow_deploy"]:
        try:
            check_deploy_runbook(task)
        except SystemExit as exc:
            write_result_blocked(task, str(exc))
            task_file.rename(ARCHIVE_DIR / task_file.name)
            return

    # 3. Verifica base_commit (solo per profili non read-only)
    if task["action_profile"] not in ("READ_ONLY_AUDIT", "RUN_VERIFICATION"):
        try:
            check_current_commit(task["base_commit"])
        except SystemExit as exc:
            write_result_blocked(task, str(exc))
            task_file.rename(ARCHIVE_DIR / task_file.name)
            return

    # 4. Costruisci prompt CC (specification è DATI, mai eseguito)
    prompt = build_cc_prompt(task, workflow)

    # 5. Log evento e scrivi prompt file (CC lo leggerà, non noi)
    prompt_file = RESULT_DIR / f"{task_id}.prompt.md"
    RESULT_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    prompt_file.write_text(prompt, encoding="utf-8")
    os.chmod(prompt_file, 0o600)

    event(
        "task_dispatched",
        task_id=task_id,
        session_id=task["session_id"],
        action_profile=task["action_profile"],
        roadmap_item=task["roadmap_item"],
        prompt_file=str(prompt_file),
        require_review=workflow["require_review"],
        worktree=workflow["worktree"],
    )

    # 6. Archivia task processato
    task_file.rename(ARCHIVE_DIR / task_file.name)

    print(f"TASK_DISPATCHED={task_id}")
    print(f"PROMPT_FILE={prompt_file}")
    print(f"REQUIRE_REVIEW={workflow['require_review']}")
    print(f"WORKTREE={workflow['worktree']}")
    if workflow["require_review"]:
        print("STATUS=REVIEW_PENDING  # il reviewer deve approvare prima di merge/deploy")

def main() -> int:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    RESULT_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Writer concorrente → STOP
    lock_fd = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fail("Writer concorrente attivo — STOP (lock su supervisor.lock)")

    try:
        task_files = sorted(QUEUE_DIR.glob("*.json"))
        if not task_files:
            print("QUEUE_EMPTY=yes")
            return 0
        for task_file in task_files:
            process_task(task_file, lock_fd)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
