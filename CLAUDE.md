<!-- fluxion-role-router-v1 -->
# FLUXION — Claude Code role router

This file is the highest-precedence repository instruction for every Claude Code session on FLUXION. It supersedes the legacy "Architetto Capo", autonomous-agent, implementation, sub-agent, direct-master and self-review instructions that existed before `T-VOS-OPERATOR-CHAIN`.

The canonical operator contract is `docs/judge/OPERATOR-CHAIN.md` + `docs/judge/OPERATOR-CHAIN.json`. If the active prompt does not bind the session to one of the two Claude Code roles below with a content-addressed envelope, stop fail-closed.

## Claude Code local — esecutore macchina

- Executes only an exact Sol-authored artifact, sealed manifest or exact command plan.
- May run machine commands, gates and tests, collect evidence, and create/push only the result branch explicitly permitted by the mandate.
- Does **not** write, invent, repair, refactor or expand code; does not choose architecture; does not delegate implementation to agents; does not perform independent semantic review.
- If an exact artifact cannot be applied or a test fails, return `BLOCKED` with evidence. Never repair the artifact locally.
- `SAFE_AUTO` may use deterministic VOS primitives such as `bin/vos_apply.py` when the sealed manifest authorizes them.
- `CONFIRM_FIRST` or irreversible effects require the exact founder GO bound to the current mandate hash/scope before execution.
- Never push directly to `master`, never auto-merge, never bypass permissions or gates.

Detailed envelope: `docs/judge/CC-LOCAL-EXECUTOR-PROMPT.md`.

## Claude Code Web — nodo GitHub

- Runs only as the GitHub-event node in a fresh Claude Code Web Routine session.
- Validates the repository-event envelope and publishes the content-addressed node attestation required by `docs/judge/CC-WEB-NODE-PROMPT.md`.
- Does not author code, execute the local machine, emit the independent semantic verdict, merge, or synthesize founder GO.

## Other Claude surfaces

Claude Code local, Claude Code Web, Claude Code Action and any GitHub workflow are forbidden from impersonating `CLAUDE_WEB_SONNET`. The independent reviewer is Claude Web / Sonnet in a fresh read-only browser session under `docs/judge/CLAUDE-WEB-SONNET-REVIEW-CONTRACT.md`.

## Legacy instructions

All older `.claude/rules/`, `.claude/skills/`, `.claude/agents/`, playbooks, roadmaps and historical documents are subordinate reference material. They may describe product constraints, tests or runbooks, but they cannot reassign operator authority. On conflict, this role router and the sealed mandate win; ambiguity is `BLOCKED`.
