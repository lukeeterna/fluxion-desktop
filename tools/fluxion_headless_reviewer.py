#!/usr/bin/env python3
"""Fail-closed, stateless, read-only reviewer for FLUXION PR #2.

The wrapper performs deterministic preflight, gives the model a sealed dossier
instead of repository/tool access, validates a closed JSON verdict, posts the
content-addressed result to the PR, and writes an artifact packet.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO = "lukeeterna/fluxion-desktop"
PR_NUMBER = 2
BASE = "439c71f822ba7b41747a309ca51c197cf42ebb3a"
HEAD = "22938cf3ce13a9559d7f6eeda5216f2f3225ef1c"
EVENT = "CLAUDE_HEADLESS_REREVIEW_PR_2"
EXPECTED_CHANGED = [
    "docs/judge/mandati/README.md",
    "docs/judge/mandati/T-EXPOSURE.json",
    "docs/judge/mandati/T-EXPOSURE.md",
]
MANIFEST_KEYS = {
    "allowed_paths",
    "base_commit",
    "key",
    "label",
    "lane",
    "mandate_md",
    "mandate_sha256",
    "risk",
    "schema_version",
    "steps",
    "unit_id",
}
OUTPUT_KEYS = {
    "verdict",
    "summary",
    "findings",
    "required_changes",
    "safe_to_request_founder_go",
}
DOSSIER_PATHS = [
    "docs/judge/mandati/T-EXPOSURE.md",
    "docs/judge/mandati/T-EXPOSURE.json",
    "docs/judge/mandati/README.md",
    "docs/judge/PROTOCOLLO.md",
    "docs/judge/STATE.md",
    ".gitignore",
    "bin/vos_check.sh",
    "bin/vos_apply.py",
    "tests/test_vos_apply.py",
    "tests/test_vos_seed_mandates.py",
]
PRIOR_RED = r"""
1. Manifest/Markdown hash mismatch and key propagation.
2. Exact-HEAD base gate created a structural deadlock.
3. vos_check thresholds required nine outcomes although the script emits eight.
4. db-shm and db-wal were tracked but absent from the authorized perimeter.
5. base_commit needed ancestor semantics.
6. Manifest step IDs collided with manual phase IDs.
7. .claude/cache and local tooling perimeter were broader/incorrectly classified.
8. README had stale T-MACCHINA state.
""".strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=check
    )


def canonical_json(data: Any) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def strip_json_fence(text: str) -> str:
    value = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", value, flags=re.S | re.I)
    return match.group(1).strip() if match else value


def validate_preflight(root: Path) -> dict[str, Any]:
    observed_head = run_git(root, "rev-parse", "HEAD").stdout.strip()
    if observed_head != HEAD:
        raise RuntimeError(f"HEAD mismatch: expected {HEAD}, observed {observed_head}")

    ancestor = run_git(root, "merge-base", "--is-ancestor", BASE, HEAD, check=False)
    if ancestor.returncode != 0:
        raise RuntimeError(f"base {BASE} is not an ancestor of {HEAD}")

    changed = sorted(
        line for line in run_git(root, "diff", "--name-only", f"{BASE}...{HEAD}").stdout.splitlines() if line
    )
    if changed != sorted(EXPECTED_CHANGED):
        raise RuntimeError(f"changed-file scope mismatch: {changed}")

    md_path = root / "docs/judge/mandati/T-EXPOSURE.md"
    manifest_path = root / "docs/judge/mandati/T-EXPOSURE.json"
    md_bytes = md_path.read_bytes()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if set(manifest) != MANIFEST_KEYS:
        raise RuntimeError(
            f"manifest schema mismatch: missing={sorted(MANIFEST_KEYS-set(manifest))} "
            f"extra={sorted(set(manifest)-MANIFEST_KEYS)}"
        )
    md_sha = sha256_bytes(md_bytes)
    if manifest["mandate_sha256"] != md_sha:
        raise RuntimeError(
            f"mandate hash mismatch: manifest={manifest['mandate_sha256']} calculated={md_sha}"
        )
    if not str(manifest["key"]).endswith(md_sha[:12]):
        raise RuntimeError("manifest key does not carry the mandate digest prefix")
    if manifest["base_commit"] != f"ancestor:{BASE}":
        raise RuntimeError(f"unexpected base_commit: {manifest['base_commit']}")
    if (manifest["label"], manifest["risk"], manifest["lane"]) != (
        "CONFIRM_FIRST",
        "C",
        "MACCHINA",
    ):
        raise RuntimeError("label/risk/lane mismatch")
    if manifest["unit_id"] != "T-EXPOSURE" or manifest["schema_version"] != 1:
        raise RuntimeError("unit/schema mismatch")

    return {
        "base": BASE,
        "head": HEAD,
        "changed_files": changed,
        "mandate_sha256": md_sha,
        "manifest_sha256": sha256_bytes(manifest_path.read_bytes()),
    }


def build_dossier(root: Path, preflight: dict[str, Any]) -> str:
    sections: list[str] = []
    for rel in DOSSIER_PATHS:
        path = root / rel
        if not path.is_file():
            raise RuntimeError(f"required dossier file missing: {rel}")
        sections.append(f"\n===== FILE: {rel} =====\n{path.read_text(encoding='utf-8', errors='strict')}")

    diff = run_git(root, "diff", "--no-ext-diff", "--unified=80", f"{BASE}...{HEAD}").stdout
    sections.append(f"\n===== PR DIFF {BASE}...{HEAD} =====\n{diff}")

    schema = {
        "verdict": "GREEN|RED|BLOCKED",
        "summary": "string",
        "findings": ["string"],
        "required_changes": ["string"],
        "safe_to_request_founder_go": "yes|no",
    }
    prompt = f"""
You are the fresh-context, independent semantic reviewer for FLUXION.
EVENT={EVENT}
REPOSITORY={REPO}
PR={PR_NUMBER}
BASE={BASE}
HEAD={HEAD}
MANDATE_SHA256={preflight['mandate_sha256']}
MANIFEST_SHA256={preflight['manifest_sha256']}

ROLE CONTRACT
- Review only. You did not author the patch.
- You have no tools and must reason only from this sealed dossier.
- Do not write code, propose out-of-scope redesigns, merge, execute, or request secrets.
- Be skeptical and fail closed.
- Verify the correction of every prior RED finding, then search for new structural
  impossibilities, unreachable gates, insufficient/overbroad paths, unsafe DB handling,
  hidden history rewrite permission, incorrect pre/post-merge states, and contradictions
  with PROTOCOLLO, STATE, .gitignore, vos_check, vos_apply, and tests.
- A GREEN verdict means the mandate is internally executable and safe to advance to the
  founder GO gate; it does NOT authorize execution, merge, runtime change, or production.
- RED means a content defect requires a new Sol patch.
- BLOCKED means the dossier is insufficient or internally unverifiable.

PRIOR RED FINDINGS THAT MUST EACH BE RECHECKED
{PRIOR_RED}

OUTPUT CONTRACT
Return exactly one JSON object and no prose or Markdown. Exact keys:
{json.dumps(schema, ensure_ascii=False, indent=2)}
Rules:
- verdict must be GREEN, RED, or BLOCKED.
- safe_to_request_founder_go may be yes only when verdict is GREEN.
- findings and required_changes must be arrays of strings; use [] when empty.
- Every RED/BLOCKED finding must identify the conflicting file/section or invariant.

SEALED DOSSIER
{''.join(sections)}
""".strip()
    return prompt


def blocked_result(reason: str, preflight: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "verdict": "BLOCKED",
        "summary": "Headless independent review could not complete fail-closed.",
        "findings": [reason],
        "required_changes": [],
        "safe_to_request_founder_go": "no",
        "infrastructure_blocked": True,
        "preflight": preflight or {},
    }


def invoke_reviewer(prompt: str) -> tuple[dict[str, Any], dict[str, Any]]:
    executable = shutil.which("claude")
    if not executable:
        return blocked_result("claude CLI not found on the self-hosted runner"), {"cli_found": False}

    command = [
        executable,
        "-p",
        prompt,
        "--model",
        "opus",
        "--output-format",
        "json",
        "--max-turns",
        "1",
        "--permission-mode",
        "plan",
        "--disallowedTools",
        "Bash,Edit,Write,Read,Grep,Glob,WebFetch,WebSearch,NotebookEdit",
    ]
    env = os.environ.copy()
    env["DISABLE_AUTOUPDATER"] = "1"
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    with tempfile.TemporaryDirectory(prefix="fluxion-reviewer-") as td:
        try:
            completed = subprocess.run(
                command,
                cwd=td,
                env=env,
                text=True,
                capture_output=True,
                timeout=900,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return blocked_result("claude CLI timed out after 900 seconds"), {
                "cli_found": True,
                "timeout": True,
            }

    meta = {
        "cli_found": True,
        "returncode": completed.returncode,
        "stderr_sha256": sha256_bytes(completed.stderr.encode("utf-8")),
        "stdout_sha256": sha256_bytes(completed.stdout.encode("utf-8")),
    }
    if completed.returncode != 0:
        safe_stderr = completed.stderr.strip().splitlines()[-1:] or ["no stderr"]
        return blocked_result(f"claude CLI failed with code {completed.returncode}: {safe_stderr[0][:300]}"), meta

    try:
        wrapper = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return blocked_result(f"claude CLI output wrapper is not JSON: {exc}"), meta

    candidate: Any = wrapper.get("result") if isinstance(wrapper, dict) else wrapper
    if isinstance(candidate, str):
        try:
            candidate = json.loads(strip_json_fence(candidate))
        except json.JSONDecodeError as exc:
            return blocked_result(f"reviewer result is not valid JSON: {exc}"), meta

    if not isinstance(candidate, dict):
        return blocked_result("reviewer result is not a JSON object"), meta
    if set(candidate) != OUTPUT_KEYS:
        return blocked_result(
            f"reviewer schema mismatch: missing={sorted(OUTPUT_KEYS-set(candidate))} "
            f"extra={sorted(set(candidate)-OUTPUT_KEYS)}"
        ), meta
    if candidate["verdict"] not in {"GREEN", "RED", "BLOCKED"}:
        return blocked_result(f"invalid verdict: {candidate['verdict']!r}"), meta
    if candidate["safe_to_request_founder_go"] not in {"yes", "no"}:
        return blocked_result("safe_to_request_founder_go must be yes or no"), meta
    if candidate["verdict"] != "GREEN" and candidate["safe_to_request_founder_go"] != "no":
        return blocked_result("non-GREEN verdict attempted to authorize founder GO"), meta
    if not isinstance(candidate["summary"], str):
        return blocked_result("summary must be a string"), meta
    for key in ("findings", "required_changes"):
        if not isinstance(candidate[key], list) or not all(isinstance(x, str) for x in candidate[key]):
            return blocked_result(f"{key} must be an array of strings"), meta
    return candidate, meta


def post_pr_comment(packet: dict[str, Any], packet_sha: str) -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN missing; cannot publish review result")
    verdict = packet["review"]["verdict"]
    review = packet["review"]
    body = "\n".join(
        [
            f"<!-- FLUXION_HEADLESS_REVIEW sha256={packet_sha} -->",
            f"## `{EVENT}` — `{verdict}`",
            "",
            f"- Reviewer profile: fresh stateless independent / no tools",
            f"- Reviewed head: `{HEAD}`",
            f"- Mandate SHA-256: `{packet['preflight']['mandate_sha256']}`",
            f"- Result packet SHA-256: `{packet_sha}`",
            "",
            f"**SUMMARY**  ",
            review["summary"],
            "",
            "**FINDINGS**",
            *(f"- {item}" for item in review["findings"]),
            "- None" if not review["findings"] else "",
            "",
            "**REQUIRED_CHANGES**",
            *(f"- {item}" for item in review["required_changes"]),
            "- None" if not review["required_changes"] else "",
            "",
            f"**SAFE_TO_REQUEST_FOUNDER_GO:** `{review['safe_to_request_founder_go']}`",
            "",
            "This review does not merge or execute T-EXPOSURE.",
        ]
    ).replace("\n\n- None\n", "\n- None\n")
    payload = json.dumps({"body": body}).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments",
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "fluxion-headless-reviewer/1",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status not in {200, 201}:
                raise RuntimeError(f"GitHub comment returned HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub comment failed HTTP {exc.code}") from exc


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: fluxion_headless_reviewer.py TARGET_REPO ARTIFACT_DIR", file=sys.stderr)
        return 64
    root = Path(sys.argv[1]).resolve()
    artifact_dir = Path(sys.argv[2]).resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)

    preflight: dict[str, Any] | None = None
    try:
        preflight = validate_preflight(root)
        prompt = build_dossier(root, preflight)
        review, reviewer_meta = invoke_reviewer(prompt)
    except Exception as exc:  # Fail closed, but still publish a structured packet.
        review = blocked_result(f"deterministic wrapper failure: {type(exc).__name__}: {exc}", preflight)
        reviewer_meta = {"wrapper_exception": type(exc).__name__}

    packet = {
        "schema_version": 1,
        "event": EVENT,
        "repository": REPO,
        "pull_request": PR_NUMBER,
        "base": BASE,
        "head": HEAD,
        "reviewer_profile": "fresh-stateless-independent-headless-no-tools",
        "preflight": preflight or {},
        "reviewer_meta": reviewer_meta,
        "review": review,
    }
    packet_bytes = canonical_json(packet)
    packet_sha = sha256_bytes(packet_bytes)
    (artifact_dir / "RESULT.json").write_bytes(packet_bytes)
    (artifact_dir / "RESULT.sha256").write_text(f"{packet_sha}  RESULT.json\n", encoding="utf-8")

    try:
        post_pr_comment(packet, packet_sha)
    except Exception as exc:
        (artifact_dir / "PUBLISH_ERROR.txt").write_text(
            f"{type(exc).__name__}: {exc}\n", encoding="utf-8"
        )
        print(f"publish failed: {exc}", file=sys.stderr)
        return 3

    print(f"VERDICT={review['verdict']}")
    print(f"SAFE_TO_REQUEST_FOUNDER_GO={review['safe_to_request_founder_go']}")
    print(f"RESULT_SHA256={packet_sha}")
    return 0 if not review.get("infrastructure_blocked") else 2


if __name__ == "__main__":
    raise SystemExit(main())
