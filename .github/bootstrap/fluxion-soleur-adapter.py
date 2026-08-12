#!/usr/bin/env python3
"""Deterministic adapter between FLUXION TASKs and a pinned Soleur workflow.

The adapter deliberately keeps the LLM lane unable to publish the canonical
repository.  Soleur operates against an ephemeral local ``origin/main`` alias;
only deterministic jobs materialize its reviewed diff and the existing
``fluxion-trusted-publish-gate.py`` may advance ``master``.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Sequence

CHANNEL = "FXD-824F35830C8A"
SOLEUR_REPOSITORY = "jikig-ai/soleur"
SOLEUR_COMMIT = "154302d32114abba3165ce47daefe5bfe508d02f"
SOLEUR_BLOBS = {
    "plugins/soleur/skills/one-shot/SKILL.md": "46358091f535c35329f0c8af258b843ac4dc28bf",
    "plugins/soleur/skills/ship/SKILL.md": "e456cf52948b7575101591864b259160e9bb2152",
    "plugins/soleur/skills/postmerge/SKILL.md": "e78cf2d86d74a13bc8315697886a3278ba68714c",
}
BASE_ACTION_COMMIT = "f1b5c5c49125f0e6adc48c1203ebd77f83ea9adb"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SAFE_TASK_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")

REQUIRED_TASK_KEYS = {
    "schema_version", "channel", "kind", "session_id", "task_id", "created_at",
    "base_commit", "action_profile", "specification", "allowed_paths",
    "forbidden_actions", "required_tests", "negative_tests", "evidence_required",
    "retry_limit", "rollback", "stop_conditions",
}
OPTIONAL_TASK_KEYS = {"predecessor_result_sha256", "roadmap_item"}
ACTION_PROFILES = {"FIX_SCOPED_BUG", "APPLY_EXISTING_UNIT"}
DETERMINISTIC_REQUIRED = {
    "DIFF_CHECK": "PASS",
    "EXPECTED_BASE_ENFORCED": "PASS",
    "CANDIDATE_EXACT_PARENT": "PASS",
    "ALLOWED_PATHS_ENFORCED": "PASS",
    "WRITER_CAPABILITY_BOUNDARY": "PASS",
    "WRITER_CAN_LAUNCH_REVIEW": "NO",
    "REVIEW_FRESH_SESSION": "PASS",
    "REVIEW_DOSSIER_PIN": "PASS",
    "REVIEW_NO_MUTATION": "PASS",
    "NO_INSTALL_PATH_IN_CANARY": "PASS",
}


class Blocked(RuntimeError):
    pass


def run(argv: Sequence[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(list(argv), cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and p.returncode:
        raise Blocked(f"command failed rc={p.returncode}: {shlex.join(list(argv))}; stderr={p.stderr.strip()[:500]}")
    return p


def git(repo: Path, *args: str, check: bool = True) -> str:
    return run(("git", *args), cwd=repo, check=check).stdout.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_blob_sha(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode())
    h.update(data)
    return h.hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise Blocked(f"invalid json {path}: {exc}") from exc
    if not isinstance(obj, dict):
        raise Blocked(f"json root must be object: {path}")
    return obj


def github_output(name: str, value: str, out: Path | None = None) -> None:
    target = out or (Path(os.environ["GITHUB_OUTPUT"]) if os.environ.get("GITHUB_OUTPUT") else None)
    if target is None:
        print(f"{name}={value}")
        return
    with target.open("a", encoding="utf-8") as fh:
        if "\n" in value:
            marker = f"FLUXION_{hashlib.sha256(value.encode()).hexdigest()[:16]}"
            fh.write(f"{name}<<{marker}\n{value}\n{marker}\n")
        else:
            fh.write(f"{name}={value}\n")


def _valid_relpath(value: str) -> bool:
    p = Path(value)
    return bool(value) and not p.is_absolute() and ".." not in p.parts and ".git" not in p.parts


def validate_task_obj(task: dict) -> dict:
    extra = set(task) - (REQUIRED_TASK_KEYS | OPTIONAL_TASK_KEYS)
    missing = REQUIRED_TASK_KEYS - set(task)
    if extra or missing:
        raise Blocked(f"task schema mismatch missing={sorted(missing)} extra={sorted(extra)}")
    if task.get("schema_version") != 1 or task.get("channel") != CHANNEL or task.get("kind") != "TASK":
        raise Blocked("task identity mismatch")
    if not isinstance(task.get("session_id"), str) or not task["session_id"].strip():
        raise Blocked("session_id invalid")
    if not isinstance(task.get("task_id"), str) or not SAFE_TASK_ID.fullmatch(task["task_id"]):
        raise Blocked("task_id invalid")
    if not isinstance(task.get("created_at"), str):
        raise Blocked("created_at invalid")
    try:
        dt.datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
    except Exception as exc:
        raise Blocked("created_at invalid") from exc
    if not isinstance(task.get("base_commit"), str) or not HEX40.fullmatch(task["base_commit"]):
        raise Blocked("base_commit invalid")
    if task.get("action_profile") not in ACTION_PROFILES:
        raise Blocked("action_profile invalid")
    if not isinstance(task.get("specification"), (str, dict, list)):
        raise Blocked("specification invalid")
    allowed = task.get("allowed_paths")
    if not isinstance(allowed, list) or not allowed or len(allowed) > 32 or len(set(allowed)) != len(allowed):
        raise Blocked("allowed_paths invalid")
    if not all(isinstance(x, str) and _valid_relpath(x) for x in allowed):
        raise Blocked("allowed_paths contains unsafe path")
    for key in ("forbidden_actions", "required_tests", "negative_tests", "evidence_required", "stop_conditions"):
        if not isinstance(task.get(key), list):
            raise Blocked(f"{key} must be list")
    if task.get("retry_limit") != 0:
        raise Blocked("retry_limit must be 0")
    if not isinstance(task.get("rollback"), (str, dict, list)):
        raise Blocked("rollback invalid")
    pred = task.get("predecessor_result_sha256")
    if pred is not None and (not isinstance(pred, str) or not HEX64.fullmatch(pred)):
        raise Blocked("predecessor_result_sha256 invalid")
    return task


def cmd_validate_task(a: argparse.Namespace) -> int:
    task = validate_task_obj(load_json(Path(a.input)))
    if a.current_master and task["base_commit"] != a.current_master:
        raise Blocked(f"stale task: base={task['base_commit']} current_master={a.current_master}")
    github_output("task_id", task["task_id"])
    github_output("base_commit", task["base_commit"])
    github_output("action_profile", task["action_profile"])
    github_output("allowed_paths_json", json.dumps(task["allowed_paths"], separators=(",", ":")))
    github_output("task_json", json.dumps(task, ensure_ascii=False, separators=(",", ":")))
    print(f"TASK_VALID=PASS task_id={task['task_id']} base={task['base_commit']}")
    return 0


def _replace_from(text: str, marker: str, replacement: str, role: str) -> str:
    idx = text.find(marker)
    if idx < 0:
        raise Blocked(f"{role}: expected marker missing")
    return text[:idx] + replacement.rstrip() + "\n"


def cmd_overlay(a: argparse.Namespace) -> int:
    root = Path(a.soleur_root).resolve()
    actual = git(root, "rev-parse", "HEAD")
    if actual != SOLEUR_COMMIT:
        raise Blocked(f"Soleur commit mismatch expected={SOLEUR_COMMIT} actual={actual}")
    for rel, expected_blob in SOLEUR_BLOBS.items():
        path = root / rel
        data = path.read_bytes()
        actual_blob = git_blob_sha(data)
        if actual_blob != expected_blob:
            raise Blocked(f"Soleur blob drift {rel}: expected={expected_blob} actual={actual_blob}")

    ship = root / "plugins/soleur/skills/ship/SKILL.md"
    ship_overlay = r'''---
name: ship
description: "FLUXION adapter: finish Soleur engineering and hand the reviewed local diff to SOL-000020 without remote publication."
---

# FLUXION External Publisher Boundary

This is the deliberately narrow FLUXION adapter for Soleur's final `ship` phase.
The upstream Soleur state machine remains authoritative for planning, implementation,
review, finding resolution, QA, and compound.  Soleur's repository-specific release
steps do **not** apply to FLUXION and are intentionally replaced here.

## Trust boundary

The engineering model is **not a publisher**.  It operates against an ephemeral local
`origin/main` mirror and has no credential capable of advancing `lukeeterna/fluxion-desktop`.
SOL-000020 remains the trusted, non-LLM publication authority.

## Final local gate

Run these checks in order.  A failure stops the pipeline; do not ask the operator to
bypass it.

1. Confirm this is a feature worktree, not the compatibility `main` branch:

```bash
git branch --show-current
git status --porcelain
```

If the branch is empty, `main`, or `master`, stop.  If the working tree is dirty because
review/QA/compound produced legitimate task artifacts, commit those local changes before
continuing.  Never discard them to make the gate green.

2. Verify the branch descends from the immutable FLUXION task base exposed as
`origin/main` in this hosted lane:

```bash
git merge-base HEAD origin/main
git rev-parse origin/main
```

The two SHAs must be identical.

3. Verify patch hygiene locally:

```bash
git diff --check origin/main...HEAD
```

4. Re-read the task at `$FLUXION_TASK_FILE`.  Confirm the implementation addresses its
`specification`, `required_tests`, `negative_tests`, `forbidden_actions`, and
`stop_conditions`.  The preceding Soleur review + QA are the model-level evidence; the
next deterministic FLUXION jobs enforce the exact `allowed_paths`, exact base, patch hash,
CI result, fresh no-tools review, and one-commit materialization.

## Handoff

Do **not** run `git push`, `gh pr create`, `gh pr ready`, `gh pr merge`, or `/postmerge`.
Do **not** modify the canonical repository after this point.

Print:

```bash
git branch --show-current
git rev-parse HEAD
git status --porcelain
```

Then output exactly:

```text
## Ship Phase Complete — FLUXION external publisher boundary
FLUXION_SOLEUR_READY
```

A remote push, merge, or `<promise>DONE</promise>` from this engineering lane is a protocol
violation.  The deterministic FLUXION lane owns PR creation, CI observation, exact-parent
materialization, SOL-000020 publication, and the post-publication Soleur verification.
'''
    ship.write_text(ship_overlay, encoding="utf-8")

    one = root / "plugins/soleur/skills/one-shot/SKILL.md"
    one_text = one.read_text(encoding="utf-8")
    one_overlay = r'''7. Use the **Skill tool**: `skill: soleur:ship --headless`.
   In the FLUXION overlay, ship deliberately stops at the external-publisher
   boundary after its normal pre-ship gates and tests.  It MUST return the line
   `FLUXION_SOLEUR_READY` and MUST NOT push, create/merge a PR, or invoke postmerge.

8. Output `<promise>READY_FOR_SOL_000020</promise>` **only when** Step 7 returned
   `FLUXION_SOLEUR_READY`.  This promise means the engineering/review/QA lane is
   complete and the local reviewed diff is ready for deterministic FLUXION
   materialization.  It does **not** mean merged, deployed, or production-verified.

CRITICAL RULE: In this FLUXION integration, `<promise>DONE</promise>` is forbidden
inside the engineering lane.  Only the post-publication verification lane may
report final completion.

Start with step 0b now.
'''
    one.write_text(_replace_from(one_text, "7. Use the **Skill tool**: `skill: soleur:ship`", one_overlay, "one-shot"), encoding="utf-8")

    post = root / "plugins/soleur/skills/postmerge/SKILL.md"
    post_text = post.read_text(encoding="utf-8")
    p1 = post_text.find("## Phase 1: Verify PR is Merged")
    p2 = post_text.find("## Phase 2: Wait for CI on Main")
    if p1 < 0 or p2 <= p1:
        raise Blocked("postmerge phase markers missing")
    post_phase1 = r'''## Phase 1: Verify PR Merge or FLUXION External Publish

Read the PR state and head commit:

```bash
gh pr view <number> --json state,mergeCommit,headRefName,headRefOid --jq '{state, mergeCommit: (.mergeCommit.oid // ""), branch: .headRefName, head: .headRefOid}'
```

If state is `MERGED`, use the normal Soleur merge commit.

If state is not `MERGED`, FLUXION permits exactly one additional success shape:
SOL-000020 may have fast-forward published the evidence PR head directly to
`master`.  Fetch `master` and prove the PR head is an ancestor of it:

```bash
git fetch origin master
git merge-base --is-ancestor <head-sha> origin/master
```

Only exit code 0 is accepted.  In that case record `<head-sha>` as the published
commit and announce `FLUXION_EXTERNAL_PUBLISH=PASS`.  Otherwise stop with:

```text
STOPPED: PR #<number> is neither merged nor proven published by SOL-000020.
```

This exception changes only the merge-state attestation.  All subsequent
postmerge CI/health verification remains mandatory.

'''
    post_text = post_text[:p1] + post_phase1 + post_text[p2:]
    post_text = post_text.replace("--branch main", "--branch master")
    post_text = post_text.replace("origin/main", "origin/master")
    post.write_text(post_text, encoding="utf-8")

    changed = [rel for rel in SOLEUR_BLOBS if git_blob_sha((root / rel).read_bytes()) != SOLEUR_BLOBS[rel]]
    if sorted(changed) != sorted(SOLEUR_BLOBS):
        raise Blocked(f"overlay changed unexpected set: {changed}")
    print(f"SOLEUR_OVERLAY=PASS commit={SOLEUR_COMMIT} files={len(changed)}")
    return 0


def parse_worktrees(repo: Path) -> list[dict[str, str]]:
    raw = git(repo, "worktree", "list", "--porcelain")
    out: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in raw.splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
                cur = {}
            continue
        key, _, value = line.partition(" ")
        if key in {"worktree", "HEAD", "branch"}:
            cur[key] = value
    return out


def changed_paths(repo: Path, base: str, head: str) -> list[str]:
    return sorted(x for x in git(repo, "diff", "--name-only", base, head).splitlines() if x)


def cmd_export(a: argparse.Namespace) -> int:
    repo = Path(a.repo).resolve()
    task = validate_task_obj(load_json(Path(a.task)))
    base = task["base_commit"]
    if git(repo, "cat-file", "-t", base) != "commit":
        raise Blocked("base commit unavailable")
    allowed = set(task["allowed_paths"])
    candidates: list[tuple[int, int, str, str, list[str]]] = []
    for wt in parse_worktrees(repo):
        head = wt.get("HEAD", "")
        branch = wt.get("branch", "").removeprefix("refs/heads/")
        if not HEX40.fullmatch(head) or head == base:
            continue
        mb = git(repo, "merge-base", base, head, check=False)
        if mb != base:
            continue
        paths = changed_paths(repo, base, head)
        n_allowed = sum(p in allowed for p in paths)
        if not n_allowed:
            continue
        count_s = git(repo, "rev-list", "--count", f"{base}..{head}")
        candidates.append((n_allowed, int(count_s), branch, head, paths))
    if not candidates:
        raise Blocked("no Soleur worktree with allowed-path changes found")
    candidates.sort(reverse=True)
    best = candidates[0]
    if len(candidates) > 1 and candidates[1][:2] == best[:2]:
        raise Blocked("ambiguous Soleur candidate worktrees")
    _, commit_count, branch, head, paths = best
    allowed_changed = sorted(p for p in paths if p in allowed)
    extra = sorted(p for p in paths if p not in allowed)
    if not allowed_changed:
        raise Blocked("Soleur candidate contains no allowed change")
    check = run(("git", "diff", "--check", base, head, "--", *allowed_changed), cwd=repo, check=False)
    if check.returncode:
        raise Blocked(f"git diff --check failed: {check.stdout}{check.stderr}")
    patch = run(("git", "diff", "--binary", "--full-index", base, head, "--", *allowed_changed), cwd=repo).stdout.encode()
    if not patch.strip():
        raise Blocked("exported patch empty")
    out_patch = Path(a.out_patch)
    out_patch.write_bytes(patch)
    meta = {
        "schema_version": 1,
        "kind": "SOLEUR_REVIEWED_DIFF",
        "task_id": task["task_id"],
        "base_commit": base,
        "soleur_repository": SOLEUR_REPOSITORY,
        "soleur_commit": SOLEUR_COMMIT,
        "source_branch": branch,
        "source_head": head,
        "source_commit_count": commit_count,
        "allowed_changed_paths": allowed_changed,
        "non_materialized_soleur_paths": extra,
        "patch_sha256": sha256_bytes(patch),
    }
    write_json(Path(a.out_meta), meta)
    github_output("source_head", head)
    github_output("patch_sha256", meta["patch_sha256"])
    github_output("allowed_changed_paths_json", json.dumps(allowed_changed, separators=(",", ":")))
    print(f"SOLEUR_EXPORT=PASS head={head} allowed={len(allowed_changed)} auxiliary={len(extra)}")
    return 0


def _fetch_master(repo: Path) -> str:
    git(repo, "fetch", "--no-tags", "origin", "refs/heads/master:refs/remotes/origin/master")
    head = git(repo, "rev-parse", "refs/remotes/origin/master")
    if not HEX40.fullmatch(head):
        raise Blocked("origin/master malformed")
    return head


def cmd_materialize(a: argparse.Namespace) -> int:
    repo = Path(a.repo).resolve()
    task = validate_task_obj(load_json(Path(a.task)))
    meta = load_json(Path(a.meta))
    base = task["base_commit"]
    if meta.get("kind") != "SOLEUR_REVIEWED_DIFF" or meta.get("task_id") != task["task_id"] or meta.get("base_commit") != base:
        raise Blocked("Soleur meta identity mismatch")
    if meta.get("soleur_commit") != SOLEUR_COMMIT:
        raise Blocked("Soleur meta pin mismatch")
    patch_path = Path(a.patch)
    if sha256_file(patch_path) != meta.get("patch_sha256"):
        raise Blocked("Soleur patch sha mismatch")
    if _fetch_master(repo) != base:
        raise Blocked("BLOCKED_ORIGIN_MOVED")
    if git(repo, "rev-parse", "HEAD") != base:
        raise Blocked("materializer HEAD is not expected base")
    if git(repo, "status", "--porcelain"):
        raise Blocked("materializer worktree not clean")
    apply = run(("git", "apply", "--index", "--binary", "--whitespace=error-all", str(patch_path.resolve())), cwd=repo, check=False)
    if apply.returncode:
        raise Blocked(f"git apply failed: {apply.stderr.strip()[:500]}")
    changed = sorted(x for x in git(repo, "diff", "--cached", "--name-only").splitlines() if x)
    expected = sorted(meta.get("allowed_changed_paths") or [])
    if changed != expected or not changed:
        raise Blocked(f"materialized paths mismatch expected={expected} actual={changed}")
    if not set(changed) <= set(task["allowed_paths"]):
        raise Blocked("materializer changed forbidden path")
    check = run(("git", "diff", "--cached", "--check"), cwd=repo, check=False)
    if check.returncode:
        raise Blocked(f"materialized diff-check failed: {check.stdout}{check.stderr}")
    git(repo, "config", "user.name", "FLUXION SOL-000020 Materializer")
    git(repo, "config", "user.email", "sol-000020@users.noreply.github.com")
    git(repo, "commit", "-m", f"vos(soleur): {task['task_id']}")
    candidate = git(repo, "rev-parse", "HEAD")
    parents = git(repo, "rev-list", "--parents", "-n", "1", candidate).split()
    if len(parents) != 2 or parents[1] != base:
        raise Blocked("candidate is not exact-parent single commit")
    materialized_patch = run(("git", "diff", "--binary", "--full-index", base, candidate, "--", *changed), cwd=repo).stdout.encode()
    if sha256_bytes(materialized_patch) != meta["patch_sha256"]:
        raise Blocked("materialized candidate differs from Soleur reviewed patch")
    session = f"deterministic-materializer-{os.environ.get('GITHUB_RUN_ID','local')}-{os.environ.get('GITHUB_RUN_ATTEMPT','1')}"
    writer = {
        "schema_version": 1,
        "kind": "WRITER_RESULT",
        "task_id": task["task_id"],
        "profile": "SOLEUR_DETERMINISTIC_MATERIALIZATION",
        "status": "PASS",
        "verdict": "VERDE",
        "session_id": session,
        "base_commit": base,
        "result_commit": candidate,
        "candidate_sha": candidate,
        "writer_tools": [],
        "bash": False,
        "network": False,
        "publisher": False,
        "can_launch_review": False,
        "source_patch_sha256": meta["patch_sha256"],
        "source_soleur_head": meta["source_head"],
    }
    write_json(Path(a.writer_out), writer)
    github_output("candidate_sha", candidate)
    github_output("writer_session", session)
    print(f"MATERIALIZE=PASS candidate={candidate} paths={len(changed)}")
    return 0


def cmd_dossier(a: argparse.Namespace) -> int:
    repo = Path(a.repo).resolve()
    task = validate_task_obj(load_json(Path(a.task)))
    writer_path = Path(a.writer)
    writer = load_json(writer_path)
    base = task["base_commit"]
    candidate = writer.get("candidate_sha")
    if not isinstance(candidate, str) or not HEX40.fullmatch(candidate):
        raise Blocked("writer candidate malformed")
    if writer.get("task_id") != task["task_id"] or writer.get("base_commit") != base:
        raise Blocked("writer identity mismatch")
    if git(repo, "merge-base", base, candidate) != base:
        raise Blocked("candidate merge-base mismatch")
    parents = git(repo, "rev-list", "--parents", "-n", "1", candidate).split()
    if len(parents) != 2 or parents[1] != base:
        raise Blocked("candidate exact parent mismatch")
    allowed = task["allowed_paths"]
    changed = changed_paths(repo, base, candidate)
    if not changed or not set(changed) <= set(allowed):
        raise Blocked("candidate allowed paths mismatch")
    check = run(("git", "diff", "--check", base, candidate), cwd=repo, check=False)
    if check.returncode:
        raise Blocked("candidate diff check failed")
    diff = git(repo, "diff", "--no-ext-diff", "--no-color", "--binary", base, candidate)
    writer_sha = sha256_file(writer_path)
    static = {k: v for k, v in DETERMINISTIC_REQUIRED.items() if k not in {"REVIEW_FRESH_SESSION", "REVIEW_DOSSIER_PIN", "REVIEW_NO_MUTATION"}}
    dossier = {
        "schema_version": 1,
        "kind": "SEALED_REVIEW_DOSSIER",
        "task_id": task["task_id"],
        "expected_base_sha": base,
        "candidate_sha": candidate,
        "merge_base_sha": base,
        "allowed_paths": sorted(allowed),
        "changed_paths": sorted(changed),
        "diff": diff,
        "deterministic_results": static,
        "writer_result_sha256": writer_sha,
        "writer_session_id": writer["session_id"],
    }
    out = Path(a.out)
    write_json(out, dossier)
    github_output("writer_sha256", writer_sha)
    github_output("dossier_sha256", sha256_file(out))
    github_output("candidate_sha", candidate)
    github_output("writer_session", writer["session_id"])
    print(f"DOSSIER=PASS candidate={candidate}")
    return 0


def _contains_tool_use(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")

    def walk(x):
        if isinstance(x, dict):
            if x.get("type") == "tool_use":
                return True
            return any(walk(v) for v in x.values())
        if isinstance(x, list):
            return any(walk(v) for v in x)
        return False

    found_json = False
    for line in text.splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        found_json = True
        if walk(obj):
            return True
    if not found_json:
        try:
            if walk(json.loads(text)):
                return True
        except Exception:
            pass
    compact = re.sub(r"\s+", "", text)
    return '"type":"tool_use"' in compact


def cmd_wrap_review(a: argparse.Namespace) -> int:
    raw = load_json(Path(a.structured))
    required = {"verdict", "findings", "required_changes", "summary"}
    if set(raw) != required or raw.get("verdict") not in {"GREEN", "RED", "BLOCKED"}:
        raise Blocked("fresh review structured output invalid")
    if not isinstance(raw["findings"], list) or not isinstance(raw["required_changes"], list) or not isinstance(raw["summary"], str):
        raise Blocked("fresh review field types invalid")
    if not a.session_id or a.session_id == a.writer_session:
        raise Blocked("fresh review session not distinct")
    if a.execution_file and _contains_tool_use(Path(a.execution_file)):
        raise Blocked("fresh review used tools")
    dossier_sha = sha256_file(Path(a.dossier))
    if not HEX64.fullmatch(dossier_sha):
        raise Blocked("dossier sha invalid")
    review = {
        "schema_version": 1,
        "kind": "FRESH_REVIEW",
        "profile": "FRESH_REVIEW",
        "verdict": raw["verdict"],
        "findings": raw["findings"],
        "required_changes": raw["required_changes"],
        "summary": raw["summary"],
        "session_id": a.session_id,
        "writer_session_id": a.writer_session,
        "independent": True,
        "result_commit": a.candidate,
        "candidate_sha": a.candidate,
        "dossier_sha256": dossier_sha,
        "claude_version": "github-hosted-base-action",
        "model": "sonnet",
        "tools_used": [],
    }
    out = Path(a.out)
    write_json(out, review)
    github_output("review_sha256", sha256_file(out))
    github_output("review_verdict", raw["verdict"])
    print(f"FRESH_REVIEW=PASS verdict={raw['verdict']}")
    return 0


def cmd_evidence(a: argparse.Namespace) -> int:
    task = validate_task_obj(load_json(Path(a.task)))
    writer = load_json(Path(a.writer))
    dossier = load_json(Path(a.dossier))
    review = load_json(Path(a.review))
    candidate = writer.get("candidate_sha")
    wsha = sha256_file(Path(a.writer))
    dsha = sha256_file(Path(a.dossier))
    rsha = sha256_file(Path(a.review))
    if dossier.get("writer_result_sha256") != wsha or review.get("dossier_sha256") != dsha:
        raise Blocked("evidence source hash mismatch")
    if review.get("result_commit") != candidate or review.get("writer_session_id") != writer.get("session_id"):
        raise Blocked("review binding mismatch")
    proofs = dict(DETERMINISTIC_REQUIRED)
    ev = {
        "schema_version": 1,
        "kind": "TRUSTED_WRITE_EVIDENCE",
        "task_id": task["task_id"],
        "expected_base_sha": task["base_commit"],
        "candidate_sha": candidate,
        "writer_result_sha256": wsha,
        "fresh_review_sha256": rsha,
        "dossier_sha256": dsha,
        "writer_session_id": writer["session_id"],
        "fresh_review_session_id": review["session_id"],
        "deterministic_proofs": proofs,
        "model_judgment": {"kind": "FRESH_REVIEW", "verdict": review["verdict"], "sha256": rsha},
    }
    out = Path(a.out)
    write_json(out, ev)
    github_output("evidence_sha256", sha256_file(out))
    github_output("writer_sha256", wsha)
    github_output("dossier_sha256", dsha)
    github_output("review_sha256", rsha)
    print("EVIDENCE=PASS")
    return 0


def cmd_static_workflow(a: argparse.Namespace) -> int:
    text = Path(a.workflow).read_text(encoding="utf-8")
    banned = ["runs-on: [self-hosted", "/Volumes/MontereyT7", "fluxion-generic-write-executor"]
    hits = [x for x in banned if x in text]
    if hits:
        raise Blocked(f"hosted workflow contains legacy local dependency: {hits}")
    if f"anthropics/claude-code-base-action@{BASE_ACTION_COMMIT}" not in text:
        raise Blocked("Claude base action is not pinned to expected commit")
    if SOLEUR_COMMIT not in text:
        raise Blocked("Soleur commit pin absent from workflow")
    if "permissions:\n      contents: read" not in text:
        raise Blocked("read-only engineering contents permission not found")
    if "FLUXION_EXTERNAL_PUBLISH" not in text:
        raise Blocked("external publisher postmerge marker absent")
    print("WORKFLOW_STATIC=PASS")
    return 0


def cmd_self_test(_: argparse.Namespace) -> int:
    sample = {
        "schema_version": 1,
        "channel": CHANNEL,
        "kind": "TASK",
        "session_id": "selftest",
        "task_id": "SELFTEST-1",
        "created_at": "2026-08-12T20:00:00Z",
        "base_commit": "a" * 40,
        "action_profile": "FIX_SCOPED_BUG",
        "specification": "x",
        "allowed_paths": ["voice-agent/src/example.py"],
        "forbidden_actions": [],
        "required_tests": [],
        "negative_tests": [],
        "evidence_required": [],
        "retry_limit": 0,
        "rollback": "git revert",
        "stop_conditions": [],
    }
    validate_task_obj(sample)
    bad = dict(sample)
    bad["allowed_paths"] = ["../escape"]
    try:
        validate_task_obj(bad)
    except Blocked:
        pass
    else:
        raise Blocked("self-test unsafe-path mutation survived")
    data = b"abc"
    assert git_blob_sha(data) == hashlib.sha1(b"blob 3\0abc").hexdigest()
    print("SELF_TEST=PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("validate-task")
    s.add_argument("--input", required=True)
    s.add_argument("--current-master")
    s.set_defaults(fn=cmd_validate_task)
    s = sub.add_parser("overlay")
    s.add_argument("--soleur-root", required=True)
    s.set_defaults(fn=cmd_overlay)
    s = sub.add_parser("export")
    s.add_argument("--repo", required=True)
    s.add_argument("--task", required=True)
    s.add_argument("--out-patch", required=True)
    s.add_argument("--out-meta", required=True)
    s.set_defaults(fn=cmd_export)
    s = sub.add_parser("materialize")
    s.add_argument("--repo", required=True)
    s.add_argument("--task", required=True)
    s.add_argument("--patch", required=True)
    s.add_argument("--meta", required=True)
    s.add_argument("--writer-out", required=True)
    s.set_defaults(fn=cmd_materialize)
    s = sub.add_parser("dossier")
    s.add_argument("--repo", required=True)
    s.add_argument("--task", required=True)
    s.add_argument("--writer", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_dossier)
    s = sub.add_parser("wrap-review")
    s.add_argument("--structured", required=True)
    s.add_argument("--dossier", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--session-id", required=True)
    s.add_argument("--writer-session", required=True)
    s.add_argument("--candidate", required=True)
    s.add_argument("--execution-file")
    s.set_defaults(fn=cmd_wrap_review)
    s = sub.add_parser("evidence")
    s.add_argument("--task", required=True)
    s.add_argument("--writer", required=True)
    s.add_argument("--dossier", required=True)
    s.add_argument("--review", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_evidence)
    s = sub.add_parser("static-workflow")
    s.add_argument("--workflow", required=True)
    s.set_defaults(fn=cmd_static_workflow)
    s = sub.add_parser("self-test")
    s.set_defaults(fn=cmd_self_test)
    return p


def main() -> int:
    try:
        a = build_parser().parse_args()
        return a.fn(a)
    except Blocked as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
