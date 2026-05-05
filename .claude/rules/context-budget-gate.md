# Context Budget Gate — Disciplinare

> **Regola zero-config**: stratificazione threshold context per tipo di task.
> Lezione S185-A (2026-05-04): editing file schema/config sopra 50% propaga errori a tutto downstream.
> Reference memoria: `feedback_critical_schema_files_context_threshold.md` + `feedback_context_rot_50pct.md`.

## Soglie (PERMANENTI)

| Range | Stato | Azioni permesse | Azioni VIETATE |
|-------|-------|-----------------|----------------|
| 0–40% | `SAFE` | Tutto, anche file critici | — |
| 40–50% | `WARN` | Tutto + flag soft su file critici | — |
| 50–70% | `BLOCK_CRITICAL` | Skeleton, cleanup, refactor meccanico, doc descrittivi | **Edit file critici autorevoli** |
| 70–80% | `CLOSING_ONLY` | HANDOFF.md, MEMORY.md, ROADMAP_REMAINING.md | Nuovi file, edit critici |
| ≥80% | `HARD_STOP` | `/compact` o handoff immediato | Tutto il resto |

## File critici (slugs match)

Pattern path che attivano `BLOCK_CRITICAL` sopra 50%:

- `HELPDESK*.md`, `HELPDESK.md`
- `CLAUDE.md` (sezioni autorevoli)
- `PLAN.md`, `PLAN-*.md` (AC misurabili)
- `AGENTS.md`, `INDEX.md`
- `.claude/rules/*.md`
- `tauri.conf.json`
- `src-tauri/migrations/**`, `migrations/**`
- `**/openapi*.{yaml,yml,json}`, `**/*.schema.json`, `**/*.proto`, `**/*.graphql`
- `**/config*.{yaml,yml}` (orchestration config)
- `pyproject.toml`, `Cargo.toml` (dependency-critical sections)

File `tolerabili` 50–70% (NON critici):
- README descrittivi, CHANGELOG, doc tutorial
- `.gitignore`, `.gitkeep`, scaffolding directory
- Test scaffolding (NON test logic critica)
- Cleanup/refactor meccanico rinominazioni

## Self-monitoring obbligatorio

1. **Ogni inizio task**: stimare context %. Se >50% → applicare matrice sopra.
2. **Ogni Write/Edit**: matchare file_path contro pattern critici. Se match + >50% → STOP, schedule next session.
3. **Ogni 5 tool call**: rileggere statusline budget_state.
4. **Closing checklist obbligatoria sopra 50%**:
   - HANDOFF.md update con stato esatto
   - MEMORY.md update con learnings sessione
   - ROADMAP_REMAINING.md update
   - Prompt ripartenza dettagliato (parametri, file, prereq verificati)

## Onestà CTO

Ammettere "non riesco a completare X in questa sessione" è meglio di handoff sporco.
Lasciare bootstrap + research + PLAN.md è meglio di HELPDESK.md sbagliato.

## Enforcement

- **Layer 1 (questo file)**: regola disciplinare auto-load.
- **Layer 2** (`.claude/hooks/context_budget_gate.py`): PostToolUse hook → inietta system-reminder a 40%/50% + scrive `/tmp/claude-ctx-{session_id}.json`. PreToolUse Write|Edit → deny se file critico + ≥50%.
- **Layer 3** (statusline): legge `/tmp/claude-ctx-{session_id}.json` → badge `SAFE|WARN|BLOCK_CRIT|CLOSING|HARD_STOP` real-time.
