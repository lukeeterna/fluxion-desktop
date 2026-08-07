#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


class GateError(RuntimeError):
    pass


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = Path("docs/judge/OPERATOR-CHAIN.json")
EXPECTED_KEYS = {
    "schema_version",
    "contract_id",
    "markdown_path",
    "markdown_sha256",
    "operators",
    "transports",
    "forbidden_substitutions",
    "green_requires",
}
EXPECTED_IDS = ["SOL_WEB", "CC_LOCAL", "CC_WEB", "CLAUDE_WEB_SONNET", "FOUNDER"]
FORBIDDEN_ACTIVE_PATHS = [
    Path(".github/workflows/fluxion-sonnet-review.yml"),
    Path("tools/fluxion_sonnet_reviewer.py"),
    Path("vos/autorun.sh"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_phrases(text: str, phrases: tuple[str, ...], label: str) -> None:
    lowered = text.lower()
    for phrase in phrases:
        if phrase.lower() not in lowered:
            raise GateError(f"{label} missing: {phrase}")


def validate(root: Path) -> dict:
    path = root / CONTRACT
    data = json.loads(path.read_text(encoding="utf-8"))
    if set(data) != EXPECTED_KEYS:
        raise GateError("contract closed-schema mismatch")
    if data["schema_version"] != 1 or data["contract_id"] != "FLUXION-OPERATOR-CHAIN-V1":
        raise GateError("contract header mismatch")

    md_rel = Path(data["markdown_path"])
    if md_rel.is_absolute() or ".." in md_rel.parts:
        raise GateError("unsafe markdown path")
    if sha256(root / md_rel) != data["markdown_sha256"]:
        raise GateError("markdown hash mismatch")

    ops = data["operators"]
    if not isinstance(ops, list) or [o.get("id") for o in ops] != EXPECTED_IDS:
        raise GateError("operator order/identity mismatch")
    expected_identities = {
        "SOL_WEB": "GPT-5.6 Sol Web",
        "CC_LOCAL": "Claude Code local",
        "CC_WEB": "Claude Code Web",
        "CLAUDE_WEB_SONNET": "Claude Web Sonnet",
        "FOUNDER": "Founder",
    }
    if {o.get("id"): o.get("identity") for o in ops} != expected_identities:
        raise GateError("operator identity reassignment")

    exact_capabilities = {
        "SOL_WEB": {
            "required": {"AUTHOR_CODE", "AUTHOR_TESTS", "AUTHOR_SPECIFICATIONS", "ORCHESTRATE"},
            "forbidden": {"EXECUTE_MACHINE", "INDEPENDENT_SEMANTIC_REVIEW", "FOUNDER_GO"},
        },
        "CC_LOCAL": {
            "required": {"EXECUTE_MACHINE", "APPLY_EXACT_SOL_ARTIFACT", "RUN_TESTS", "COLLECT_EVIDENCE"},
            "forbidden": {"AUTHOR_CODE", "REPAIR_CODE", "ORCHESTRATE", "INDEPENDENT_SEMANTIC_REVIEW", "FOUNDER_GO", "DIRECT_MASTER_PUSH"},
        },
        "CC_WEB": {
            "required": {"GITHUB_EVENT_NODE", "VALIDATE_EVENT_ENVELOPE", "PUBLISH_NODE_ATTESTATION"},
            "forbidden": {"AUTHOR_CODE", "EXECUTE_MACHINE", "INDEPENDENT_SEMANTIC_REVIEW", "FOUNDER_GO"},
        },
        "CLAUDE_WEB_SONNET": {
            "required": {"INDEPENDENT_SEMANTIC_REVIEW", "READ_ONLY", "FRESH_STATELESS_SESSION"},
            "forbidden": {"AUTHOR_CODE", "EXECUTE_MACHINE", "WRITE_GITHUB", "FOUNDER_GO"},
        },
        "FOUNDER": {
            "required": {"AUTHORIZE_CONFIRM_FIRST", "AUTHORIZE_IRREVERSIBLE"},
            "forbidden": {"ORDINARY_MACHINE_EXECUTION", "ORDINARY_COPY_PASTE"},
        },
    }
    for op in ops:
        if set(op) != {"id", "identity", "required_capabilities", "forbidden_capabilities"}:
            raise GateError(f"operator schema mismatch: {op.get('id')}")
        required = set(op["required_capabilities"])
        forbidden = set(op["forbidden_capabilities"])
        if required & forbidden:
            raise GateError(f"capability conflict: {op['id']}")
        expected = exact_capabilities[op["id"]]
        if required != expected["required"] or forbidden != expected["forbidden"]:
            raise GateError(f"operator capability reassignment: {op['id']}")

    required_substitutions = {
        "CC_LOCAL_AS_AUTHOR",
        "CC_LOCAL_AS_REVIEWER",
        "CC_ACTION_AS_CLAUDE_WEB_REVIEWER",
        "CC_WEB_AS_SEMANTIC_REVIEWER",
        "LEGACY_AUTORUN_DIRECT_MASTER",
        "LEGACY_CLAUDE_MD_ARCHITECT_ROLE",
        "SOL_SELF_REVIEW",
        "AUTOMATED_FOUNDER_GO",
    }
    if set(data["forbidden_substitutions"]) != required_substitutions:
        raise GateError("forbidden substitutions mismatch")

    required_transports = {"GMAIL_DRAFT_BUS", "GITHUB", "BROWSER_RELAY_BYTE_EXACT", "VOS_DETERMINISTIC_EXECUTOR"}
    if set(data["transports"]) != required_transports:
        raise GateError("transport contract mismatch")

    role_router = (root / "CLAUDE.md").read_text(encoding="utf-8")
    require_phrases(
        role_router,
        (
            "<!-- fluxion-role-router-v1 -->",
            "Claude Code local — esecutore macchina",
            "write, invent, repair, refactor or expand code",
            "Never push directly to `master`",
            "supersedes the legacy \"Architetto Capo\"",
        ),
        "root role router",
    )

    local_executor = (root / "docs/judge/CC-LOCAL-EXECUTOR-PROMPT.md").read_text(encoding="utf-8")
    require_phrases(
        local_executor,
        (
            "<!-- fluxion-cclocal-executor -->",
            "ROLE=CC_LOCAL",
            "You do not author or repair code",
            "bin/vos_apply.py",
            "Never push directly to `master`",
            "exact founder GO",
        ),
        "CC local executor contract",
    )

    node = (root / "docs/judge/CC-WEB-NODE-PROMPT.md").read_text(encoding="utf-8")
    require_phrases(
        node,
        ("non revisionare semanticamente", "<!-- fluxion-ccweb-node -->", "ready_for_claude_web_review"),
        "CC Web node contract",
    )
    review = (root / "docs/judge/CLAUDE-WEB-SONNET-REVIEW-CONTRACT.md").read_text(encoding="utf-8")
    for phrase in ("CLAUDE_WEB_SONNET", "GREEN|RED|BLOCKED", "safe_to_merge"):
        if phrase not in review:
            raise GateError(f"Claude Web review contract missing: {phrase}")

    forbidden_present = [str(p) for p in FORBIDDEN_ACTIVE_PATHS if (root / p).exists()]
    return {
        "schema_version": 1,
        "contract_sha256": sha256(path),
        "markdown_sha256": data["markdown_sha256"],
        "operators": EXPECTED_IDS,
        "forbidden_active_paths_present": forbidden_present,
        "static_status": "PASS" if not forbidden_present else "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.root.resolve())
    except (OSError, ValueError, KeyError, GateError) as exc:
        if args.json:
            print(json.dumps({"static_status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        else:
            print(f"OPERATOR_CHAIN BLOCKED: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"OPERATOR_CHAIN {result['static_status']}")
    return 0 if result["static_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
