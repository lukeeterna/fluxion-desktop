#!/usr/bin/env python3
"""Generic fail-closed Sonnet reviewer for FLUXION pull requests.

The model receives only a sealed, content-addressed dossier and no tools.
Python performs deterministic repository checks, validates the closed JSON
response, publishes one updatable PR comment, and labels the verdict.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any

REVIEW_KEYS = {
    "verdict",
    "summary",
    "findings",
    "required_changes",
    "safe_to_merge",
    "next_action",
}
VERDICTS = {"GREEN", "RED", "BLOCKED"}
COMMENT_MARKER = "<!-- fluxion-sonnet-headless-review -->"
PROVIDER = "Claude Code OAuth / Sonnet"
MODEL = "sonnet"
MAX_CHANGED_FILES = 80
MAX_DIFF_BYTES = 180_000
FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"(^|/)\.env(?:\.|$)", re.I),
    re.compile(r"(^|/)(calls|archive)(/|$)", re.I),
    re.compile(r"\.(pem|p12|pfx|key|crt|cer)$", re.I),
    re.compile(r"(^|/)(id_rsa|id_ed25519)(\.pub)?$", re.I),
)
VERDICT_LABELS = {
    "GREEN": "sonnet-green",
    "RED": "sonnet-red",
    "BLOCKED": "sonnet-blocked",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def git(root: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and proc.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): "
            f"{proc.stderr.strip()[:500]}"
        )
    return proc.stdout


def add_check(
    checks: list[dict[str, Any]],
    ident: str,
    passed: bool,
    detail: str,
) -> None:
    checks.append({"id": ident, "pass": bool(passed), "detail": detail})


def changed_file_inventory(
    root: Path,
    base_sha: str,
    head_sha: str,
    changed: list[str],
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    numstat_rows = {
        row.split("\t", 2)[2]: row.split("\t", 2)[:2]
        for row in git(root, "diff", "--numstat", f"{base_sha}...{head_sha}").splitlines()
        if row.count("\t") >= 2
    }
    for path in changed:
        item: dict[str, Any] = {"path": path}
        row = numstat_rows.get(path)
        if row:
            item["added"] = row[0]
            item["deleted"] = row[1]
            item["binary"] = row[0] == "-" or row[1] == "-"
        else:
            item["binary"] = False
        blob = git(
            root,
            "rev-parse",
            f"{head_sha}:{path}",
            check=False,
        ).strip()
        if re.fullmatch(r"[0-9a-f]{40}", blob):
            item["blob_sha1"] = blob
            size_text = git(root, "cat-file", "-s", blob, check=False).strip()
            item["size_bytes"] = int(size_text) if size_text.isdigit() else None
        else:
            item["deleted_at_head"] = True
        inventory.append(item)
    return inventory


def deterministic_audit(
    root: Path,
    meta: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    base_sha = str(meta["base_sha"])
    head_sha = str(meta["head_sha"])
    observed_head = git(root, "rev-parse", "HEAD").strip()
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_sha, head_sha],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    changed = sorted(
        line
        for line in git(
            root,
            "diff",
            "--name-only",
            f"{base_sha}...{head_sha}",
        ).splitlines()
        if line
    )
    diff_bytes = subprocess.run(
        [
            "git",
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--find-renames",
            "--find-copies",
            f"{base_sha}...{head_sha}",
        ],
        cwd=root,
        capture_output=True,
        check=False,
    ).stdout
    diff_text = diff_bytes.decode("utf-8", errors="replace")
    inventory = changed_file_inventory(root, base_sha, head_sha, changed)

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "TARGET_HEAD",
        observed_head == head_sha,
        f"observed={observed_head} expected={head_sha}",
    )
    add_check(
        checks,
        "BASE_ANCESTOR",
        ancestor.returncode == 0,
        f"base={base_sha} head={head_sha}",
    )
    add_check(checks, "NON_EMPTY_DIFF", bool(changed), f"changed_files={len(changed)}")
    add_check(
        checks,
        "REVIEWABLE_SCOPE",
        len(changed) <= MAX_CHANGED_FILES,
        f"changed_files={len(changed)} limit={MAX_CHANGED_FILES}",
    )

    forbidden = [
        path
        for path in changed
        if any(pattern.search(path) for pattern in FORBIDDEN_PATH_PATTERNS)
    ]
    add_check(
        checks,
        "NO_FORBIDDEN_SECRET_PATHS",
        not forbidden,
        f"forbidden={forbidden}",
    )

    binary = [item["path"] for item in inventory if item.get("binary")]
    add_check(
        checks,
        "TEXT_REVIEWABLE",
        not binary,
        f"binary_files={binary}",
    )
    add_check(
        checks,
        "DIFF_SIZE",
        len(diff_bytes) <= MAX_DIFF_BYTES,
        f"bytes={len(diff_bytes)} limit={MAX_DIFF_BYTES}",
    )

    workflow_escalations: list[str] = []
    for path in changed:
        if not path.startswith(".github/workflows/") or not path.endswith((".yml", ".yaml")):
            continue
        content = git(root, "show", f"{head_sha}:{path}", check=False)
        if re.search(r"(?m)^\s*pull_request_target\s*:", content):
            workflow_escalations.append(f"{path}:pull_request_target")
        if re.search(r"(?m)^\s*permissions\s*:\s*write-all\s*$", content):
            workflow_escalations.append(f"{path}:write-all")
    add_check(
        checks,
        "NO_OBVIOUS_WORKFLOW_ESCALATION",
        not workflow_escalations,
        f"findings={workflow_escalations}",
    )

    failed = [check for check in checks if not check["pass"]]
    audit = {
        "schema_version": 1,
        "repository": meta["repository"],
        "pr_number": meta["pr_number"],
        "title": meta.get("title", ""),
        "base_ref": meta.get("base_ref", ""),
        "head_ref": meta.get("head_ref", ""),
        "base_sha": base_sha,
        "head_sha": head_sha,
        "changed_files": changed,
        "inventory": inventory,
        "diff_sha256": sha256(diff_bytes),
        "diff_bytes": len(diff_bytes),
        "checks": checks,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "execution_observed": False,
        "execution_note": (
            "The reviewer sees repository diff and PR metadata only. "
            "Runtime or local test claims remain evidence claims unless independently "
            "represented in the dossier."
        ),
    }
    return audit, diff_text


def build_prompt(meta: dict[str, Any], audit: dict[str, Any], diff_text: str) -> str:
    dossier = {
        "pr_metadata": {
            "repository": meta["repository"],
            "number": meta["pr_number"],
            "title": meta.get("title", ""),
            "body": meta.get("body", ""),
            "author": meta.get("author", ""),
            "base_ref": meta.get("base_ref", ""),
            "head_ref": meta.get("head_ref", ""),
            "base_sha": meta["base_sha"],
            "head_sha": meta["head_sha"],
        },
        "deterministic_audit": audit,
        "diff": diff_text,
    }
    dossier_bytes = canonical_json(dossier)
    dossier_sha = sha256(dossier_bytes)
    instruction = f"""
You are the independent, fresh, read-only Sonnet reviewer for a FLUXION pull request.

You have no tools and no repository access. Use only the sealed dossier below.
Do not claim that commands, runtime checks, deployments, merges, or tests were
personally observed unless the dossier itself contains machine-verifiable evidence.
Review the actual diff for correctness, regressions, security, privacy, fail-closed
behavior, scope discipline, test quality, and whether the change advances FLUXION
rather than creating process for its own sake.

Verdict rules:
- GREEN only when the diff is correct, appropriately scoped, and safe to merge.
- RED when a concrete defect or required change exists.
- BLOCKED when the dossier is incomplete, inconsistent, unreviewable, or any
  deterministic check failed.
- safe_to_merge must be "yes" only when verdict is GREEN.
- findings and required_changes must be empty only when there is genuinely no issue.
- next_action must be one concise operational action.

Dossier SHA-256: {dossier_sha}

SEALED DOSSIER
{dossier_bytes.decode("utf-8")}
"""
    return instruction.strip() + "\n"


def write_prepare_outputs(artifacts: Path, invoke_model: bool, prompt_path: Path) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return
    with open(github_output, "a", encoding="utf-8") as handle:
        handle.write(f"invoke_model={'true' if invoke_model else 'false'}\n")
        handle.write(f"prompt_path={prompt_path}\n")


def prepare(root: Path, artifacts: Path, meta_path: Path) -> int:
    artifacts.mkdir(parents=True, exist_ok=True)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    audit, diff_text = deterministic_audit(root, meta)
    audit_bytes = canonical_json(audit)
    (artifacts / "AUDIT.json").write_bytes(audit_bytes)
    (artifacts / "AUDIT.sha256").write_text(sha256(audit_bytes) + "\n", encoding="utf-8")

    prompt = build_prompt(meta, audit, diff_text)
    prompt_path = (artifacts / "PROMPT.md").resolve()
    prompt_path.write_text(prompt, encoding="utf-8")
    (artifacts / "PROMPT.sha256").write_text(
        sha256(prompt.encode("utf-8")) + "\n",
        encoding="utf-8",
    )

    invoke_model = audit["checks_failed"] == 0
    if not invoke_model:
        blocked = {
            "verdict": "BLOCKED",
            "summary": "Deterministic pre-review checks failed.",
            "findings": [
                f"{item['id']}: {item['detail']}"
                for item in audit["checks"]
                if not item["pass"]
            ],
            "required_changes": [
                "Resolve all failed deterministic checks and rerun the review."
            ],
            "safe_to_merge": "no",
            "next_action": "Fix deterministic blockers and push a new head.",
        }
        (artifacts / "PRECHECK_RESULT.json").write_bytes(canonical_json(blocked))
    write_prepare_outputs(artifacts, invoke_model, prompt_path)
    print(
        f"PREPARE checks={audit['checks_passed']}/{audit['checks_total']} "
        f"invoke_model={str(invoke_model).lower()} head={audit['head_sha']}"
    )
    return 0


def request_json(
    method: str,
    url: str,
    token: str,
    payload: Any | None = None,
) -> Any:
    data = None if payload is None else canonical_json(payload)
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "fluxion-sonnet-headless-reviewer",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
        return json.loads(body) if body else None


def normalize_result(raw: str) -> dict[str, Any]:
    parsed = json.loads(raw)
    if not isinstance(parsed, dict) or set(parsed) != REVIEW_KEYS:
        raise ValueError(
            f"closed schema mismatch: keys={sorted(parsed) if isinstance(parsed, dict) else type(parsed)}"
        )
    verdict = parsed.get("verdict")
    if verdict not in VERDICTS:
        raise ValueError(f"invalid verdict: {verdict!r}")
    if parsed.get("safe_to_merge") not in {"yes", "no"}:
        raise ValueError("safe_to_merge must be yes|no")
    if verdict != "GREEN" and parsed["safe_to_merge"] != "no":
        raise ValueError("non-GREEN verdict cannot be safe_to_merge=yes")
    for key in ("summary", "next_action"):
        if not isinstance(parsed.get(key), str) or not parsed[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    for key in ("findings", "required_changes"):
        if not isinstance(parsed.get(key), list) or not all(
            isinstance(item, str) for item in parsed[key]
        ):
            raise ValueError(f"{key} must be an array of strings")
    return parsed


def publish(
    meta: dict[str, Any],
    result: dict[str, Any],
    result_sha: str,
    audit: dict[str, Any],
) -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo = meta["repository"]
    pr_number = int(meta["pr_number"])
    api = f"https://api.github.com/repos/{repo}"
    comments = request_json("GET", f"{api}/issues/{pr_number}/comments?per_page=100", token)
    body = (
        f"{COMMENT_MARKER}\n"
        f"## Independent Sonnet headless review\n\n"
        f"- **Verdict:** `{result['verdict']}`\n"
        f"- **Safe to merge:** `{result['safe_to_merge']}`\n"
        f"- **Target head:** `{meta['head_sha']}`\n"
        f"- **Deterministic checks:** `{audit['checks_passed']}/{audit['checks_total']}`\n"
        f"- **Result SHA-256:** `{result_sha}`\n"
        f"- **Provider:** `{PROVIDER}`\n"
        f"- **Execution observed:** `false`\n\n"
        f"### Summary\n{result['summary']}\n\n"
        f"### Findings\n"
        + (
            "\n".join(f"- {item}" for item in result["findings"])
            if result["findings"]
            else "- None."
        )
        + "\n\n### Required changes\n"
        + (
            "\n".join(f"- {item}" for item in result["required_changes"])
            if result["required_changes"]
            else "- None."
        )
        + f"\n\n### Next action\n{result['next_action']}\n"
    )
    existing = next(
        (
            comment
            for comment in comments
            if COMMENT_MARKER in str(comment.get("body", ""))
        ),
        None,
    )
    if existing:
        request_json(
            "PATCH",
            f"{api}/issues/comments/{existing['id']}",
            token,
            {"body": body},
        )
    else:
        request_json(
            "POST",
            f"{api}/issues/{pr_number}/comments",
            token,
            {"body": body},
        )

    target_label = VERDICT_LABELS[result["verdict"]]
    repo_labels = request_json("GET", f"{api}/labels?per_page=100", token)
    repo_label_names = {str(item.get("name")) for item in repo_labels}
    if target_label not in repo_label_names:
        colors = {
            "sonnet-green": "1f883d",
            "sonnet-red": "cf222e",
            "sonnet-blocked": "bf8700",
        }
        try:
            request_json(
                "POST",
                f"{api}/labels",
                token,
                {
                    "name": target_label,
                    "color": colors[target_label],
                    "description": "Headless independent Sonnet review verdict",
                },
            )
        except urllib.error.HTTPError as exc:
            if exc.code != 422:
                raise

    current_labels = request_json("GET", f"{api}/issues/{pr_number}/labels", token)
    current_names = {str(item.get("name")) for item in current_labels}
    for label in VERDICT_LABELS.values():
        if label in current_names:
            try:
                request_json(
                    "DELETE",
                    f"{api}/issues/{pr_number}/labels/{urllib.parse.quote(label, safe='')}",
                    token,
                )
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise
    request_json(
        "POST",
        f"{api}/issues/{pr_number}/labels",
        token,
        {"labels": [target_label]},
    )


def finalize(artifacts: Path, meta_path: Path) -> int:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    audit = json.loads((artifacts / "AUDIT.json").read_text(encoding="utf-8"))
    if audit["checks_failed"]:
        raw = (artifacts / "PRECHECK_RESULT.json").read_text(encoding="utf-8")
    else:
        if os.environ.get("MODEL_STEP_OUTCOME") != "success":
            raw = json.dumps(
                {
                    "verdict": "BLOCKED",
                    "summary": "Sonnet invocation did not complete successfully.",
                    "findings": [
                        f"model_step_outcome={os.environ.get('MODEL_STEP_OUTCOME', 'missing')}"
                    ],
                    "required_changes": [
                        "Restore reviewer authentication or capacity and rerun."
                    ],
                    "safe_to_merge": "no",
                    "next_action": "Rerun the headless review after fixing model access.",
                }
            )
        else:
            raw = os.environ.get("STRUCTURED_OUTPUT", "")
    try:
        result = normalize_result(raw)
    except Exception as exc:
        result = {
            "verdict": "BLOCKED",
            "summary": "Reviewer output failed closed-schema validation.",
            "findings": [str(exc)[:500]],
            "required_changes": [
                "Rerun with a valid closed-schema Sonnet response."
            ],
            "safe_to_merge": "no",
            "next_action": "Rerun the headless review.",
        }

    envelope = {
        "schema_version": 1,
        "repository": meta["repository"],
        "pr_number": meta["pr_number"],
        "base_sha": meta["base_sha"],
        "head_sha": meta["head_sha"],
        "provider": PROVIDER,
        "model": MODEL,
        "execution_observed": False,
        "audit_sha256": (artifacts / "AUDIT.sha256").read_text().strip(),
        "prompt_sha256": (artifacts / "PROMPT.sha256").read_text().strip(),
        "review": result,
    }
    result_bytes = canonical_json(envelope)
    result_sha = sha256(result_bytes)
    (artifacts / "RESULT.json").write_bytes(result_bytes)
    (artifacts / "RESULT.sha256").write_text(result_sha + "\n", encoding="utf-8")
    publish(meta, result, result_sha, audit)
    print(
        f"VERDICT={result['verdict']} SAFE_TO_MERGE={result['safe_to_merge']} "
        f"RESULT_SHA256={result_sha}"
    )
    return 0 if result["verdict"] == "GREEN" else 1


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: fluxion_sonnet_reviewer.py "
            "prepare|finalize <target-root> <artifacts-dir> <pr-meta.json>",
            file=sys.stderr,
        )
        return 2
    command = sys.argv[1]
    target = Path(sys.argv[2]).resolve()
    artifacts = Path(sys.argv[3]).resolve()
    meta_path = Path(sys.argv[4]).resolve()
    if command == "prepare":
        return prepare(target, artifacts, meta_path)
    if command == "finalize":
        return finalize(artifacts, meta_path)
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
