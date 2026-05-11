#!/usr/bin/env python3
"""
Context Budget Gate — Layer 2 enforcement.

Eventi gestiti:
- PostToolUse: track context %, scrive /tmp/claude-ctx-{session_id}.json,
  inietta system-reminder a 40% (warning) e 50% (block file critici).
- PreToolUse Write|Edit|MultiEdit: deny se file critico match + context ≥ 50%.

Source di verita context %:
1. data.context_window.remaining_percentage (statusline-style)
2. data.context_window.used_percentage
3. env CLAUDE_CONTEXT_USED_TOKENS / CLAUDE_CONTEXT_MAX_TOKENS
4. Fallback: stima da transcript_path file size (chars/4 ~= tokens, /1_000_000 budget)

Reference: .claude/rules/context-budget-gate.md
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

THRESH_WARN = 40
THRESH_BLOCK_CRITICAL = 50
THRESH_CLOSING_ONLY = 70
THRESH_HARD_STOP = 80

CRITICAL_PATTERNS = [
    r"(?:^|/)HELPDESK[^/]*\.md$",
    r"(?:^|/)CLAUDE\.md$",
    r"(?:^|/)PLAN(?:-[^/]*)?\.md$",
    r"(?:^|/)AGENTS\.md$",
    r"(?:^|/)INDEX\.md$",
    r"\.claude/rules/[^/]+\.md$",
    r"(?:^|/)tauri\.conf\.json$",
    r"(?:^|/)(?:src-tauri/)?migrations/.+",
    r"openapi.*\.(?:ya?ml|json)$",
    r"\.schema\.json$",
    r"\.proto$",
    r"\.graphql$",
    r"(?:^|/)config[^/]*\.(?:ya?ml)$",
    r"(?:^|/)pyproject\.toml$",
    r"(?:^|/)Cargo\.toml$",
]

CRITICAL_RE = re.compile("|".join(CRITICAL_PATTERNS))


def is_critical_file(path: str) -> bool:
    if not path:
        return False
    return bool(CRITICAL_RE.search(path))


# ---------------------------------------------------------------------------
# Context % source resolution
# ---------------------------------------------------------------------------


def _from_payload(data: dict) -> float | None:
    cw = data.get("context_window") or {}
    if isinstance(cw, dict):
        rem = cw.get("remaining_percentage")
        if isinstance(rem, (int, float)):
            return max(0.0, min(100.0, 100.0 - float(rem)))
        used = cw.get("used_percentage")
        if isinstance(used, (int, float)):
            return max(0.0, min(100.0, float(used)))
        used_tokens = cw.get("used_tokens")
        max_tokens = cw.get("max_tokens") or cw.get("total_tokens")
        if isinstance(used_tokens, (int, float)) and isinstance(max_tokens, (int, float)) and max_tokens > 0:
            return max(0.0, min(100.0, 100.0 * used_tokens / max_tokens))
    return None


def _from_env() -> float | None:
    used = os.environ.get("CLAUDE_CONTEXT_USED_TOKENS")
    total = os.environ.get("CLAUDE_CONTEXT_MAX_TOKENS") or os.environ.get(
        "CLAUDE_CONTEXT_TOTAL_TOKENS"
    )
    try:
        if used and total:
            u = float(used)
            t = float(total)
            if t > 0:
                return max(0.0, min(100.0, 100.0 * u / t))
    except ValueError:
        pass
    return None


# Budget fallback: Claude Code Opus 4.6 ha 1M context (claude-opus-4-7[1m]).
# S5e 2026-05-11 bug VOS: era 200_000 hardcoded → sovrastima 5x, chiusure premature.
# Stesso pattern auditato qui (VOS FASE 1.1 2026-05-11) e allineato.
# Deviation ref: context-gate-budget-5x-wrong. Override via CLAUDE_CONTEXT_MAX_TOKENS env.
_MAX_CONTEXT_TOKENS_FALLBACK = 1_000_000


def _from_transcript(transcript_path: str | None) -> float | None:
    if not transcript_path:
        return None
    try:
        size = Path(transcript_path).stat().st_size
    except OSError:
        return None
    # Rough heuristic: 1 token ~= 4 chars.
    est_tokens = size / 4.0
    return max(0.0, min(100.0, 100.0 * est_tokens / _MAX_CONTEXT_TOKENS_FALLBACK))


def resolve_context_pct(data: dict) -> tuple[float | None, str]:
    val = _from_payload(data)
    if val is not None:
        return val, "payload"
    val = _from_env()
    if val is not None:
        return val, "env"
    val = _from_transcript(data.get("transcript_path"))
    if val is not None:
        return val, "transcript"
    return None, "unknown"


# ---------------------------------------------------------------------------
# State classification
# ---------------------------------------------------------------------------


def classify(pct: float | None) -> str:
    if pct is None:
        return "UNKNOWN"
    if pct < THRESH_WARN:
        return "SAFE"
    if pct < THRESH_BLOCK_CRITICAL:
        return "WARN"
    if pct < THRESH_CLOSING_ONLY:
        return "BLOCK_CRITICAL"
    if pct < THRESH_HARD_STOP:
        return "CLOSING_ONLY"
    return "HARD_STOP"


# ---------------------------------------------------------------------------
# Bridge file (Layer 3 statusline consumer)
# ---------------------------------------------------------------------------


def write_bridge(session_id: str, pct: float | None, state: str, source: str) -> None:
    if not session_id:
        return
    try:
        path = Path(f"/tmp/claude-ctx-{session_id}.json")
        path.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "used_pct": round(pct, 1) if pct is not None else None,
                    "budget_state": state,
                    "source": source,
                    "thresholds": {
                        "warn": THRESH_WARN,
                        "block_critical": THRESH_BLOCK_CRITICAL,
                        "closing_only": THRESH_CLOSING_ONLY,
                        "hard_stop": THRESH_HARD_STOP,
                    },
                }
            )
        )
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Hook handlers
# ---------------------------------------------------------------------------


def reminder(text: str) -> None:
    """Emit additionalContext reminder (PostToolUse-friendly)."""
    print(json.dumps({"additionalContext": text}))


def deny(reason: str) -> None:
    """PreToolUse deny payload."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def handle_post_tool_use(data: dict, pct: float | None, state: str) -> None:
    if pct is None:
        return

    tool_name = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""
    is_write = tool_name in ("Write", "Edit", "MultiEdit", "NotebookEdit")
    is_critical_edit = is_write and is_critical_file(file_path)

    bar = make_bar(pct)

    if state == "SAFE":
        return

    if state == "WARN":
        msg = (
            f"⚠️ CONTEXT BUDGET — {pct:.0f}% {bar}\n"
            f"Stato: WARN (40-50%). File critici ancora OK ma pianificare closing entro {THRESH_BLOCK_CRITICAL}%.\n"
            f"Ref: .claude/rules/context-budget-gate.md"
        )
        reminder(msg)
        return

    if state == "BLOCK_CRITICAL":
        critical_note = (
            f"\n   🔴 Tool appena usato ({tool_name}) ha toccato file critico: {file_path}\n"
            f"   → Verificare che NON sia edit autorevole su schema/config/AC.\n"
            f"   → Se è skeleton/cleanup: OK. Se è edit autorevole: ROLLBACK e schedule next session."
            if is_critical_edit
            else ""
        )
        msg = (
            f"🛑 CONTEXT BUDGET — {pct:.0f}% {bar}\n"
            f"Stato: BLOCK_CRITICAL (50-70%).\n"
            f"VIETATO editing file critici autorevoli (HELPDESK/CLAUDE/PLAN/schema YAML/migration/API contract/.claude/rules).\n"
            f"PERMESSO: skeleton, cleanup, refactor meccanico, doc descrittivi.{critical_note}\n"
            f"Ref: .claude/rules/context-budget-gate.md"
        )
        reminder(msg)
        return

    if state == "CLOSING_ONLY":
        msg = (
            f"🚨 CONTEXT BUDGET — {pct:.0f}% {bar}\n"
            f"Stato: CLOSING_ONLY (70-80%). SOLO HANDOFF.md, MEMORY.md, ROADMAP_REMAINING.md.\n"
            f"NIENTE nuovi file. NIENTE edit critici. Preparare prompt ripartenza next session."
        )
        reminder(msg)
        return

    if state == "HARD_STOP":
        msg = (
            f"💀 CONTEXT BUDGET — {pct:.0f}% {bar}\n"
            f"Stato: HARD_STOP (≥80%). Eseguire /compact o handoff immediato.\n"
            f"Ogni ulteriore decisione è degradata da context rot."
        )
        reminder(msg)
        return


def handle_pre_tool_use(data: dict, pct: float | None, state: str) -> None:
    """Block edits on critical files when context budget is exhausted."""
    if pct is None:
        return  # Cannot enforce without signal — fail-open.

    tool_name = data.get("tool_name") or ""
    if tool_name not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        return

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""

    if not is_critical_file(file_path):
        return

    if state in ("BLOCK_CRITICAL", "CLOSING_ONLY", "HARD_STOP"):
        deny(
            f"CONTEXT BUDGET GATE: rifiuto edit file critico '{file_path}' "
            f"(context {pct:.0f}% — stato {state}).\n"
            f"File schema/config autorevoli richiedono mente fresca (<50%).\n"
            f"Azioni: (1) override esplicito founder, (2) /compact + retry, "
            f"(3) closing pulito + schedule next session.\n"
            f"Ref: .claude/rules/context-budget-gate.md"
        )
        sys.exit(0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_bar(pct: float) -> str:
    filled = int(pct // 10)
    filled = max(0, min(10, filled))
    return "█" * filled + "░" * (10 - filled)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if not isinstance(data, dict):
        sys.exit(0)

    event = data.get("hook_event_name") or data.get("event") or ""
    session_id = data.get("session_id") or os.environ.get("CLAUDE_SESSION_ID") or ""

    pct, source = resolve_context_pct(data)
    state = classify(pct)

    write_bridge(session_id, pct, state, source)

    try:
        if event == "PreToolUse":
            handle_pre_tool_use(data, pct, state)
        else:
            # Default: PostToolUse semantics (richiamato anche da altri eventi senza danno)
            handle_post_tool_use(data, pct, state)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
