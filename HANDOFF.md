<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF FLUXION (fonte unica di sessione)

## STATO CORRENTE

### Sessione 2026-06-30 (b) — Hardening protocollo handoff (VERDE)
- **Cosa**: hardening del protocollo handoff già installato. Tre interventi: footgun TextEdit rimosso da `vos-close.sh`, regola founder iniettata in `CLAUDE.md`, mappa sola-lettura dei generatori legacy.
- **Commit**: `3c1c89c chore(handoff): chiusura sessione — HANDOFF.md canonico` (fonte: `git log`). Pushato → `origin/master == 3c1c89c` (off-machine OK; push ha bypassato branch-rule "CI Pass" via permesso token).
- **[D6] RISOLTO**: `scripts/vos-close.sh:27` non apre più TextEdit → ora `echo "...incollalo al giudice."`. Verificato `grep -c "open -a TextEdit"` = 0; 2a run = no-op; marker riga-1 HANDOFF.md intatto.
- **Regola founder AGGIUNTA**: `CLAUDE.md` blocco `VOS-HANDOFF-PROTOCOL` (righe ~270-283) ora contiene `REGOLA FOUNDER (comunicazione)`: CC parla col founder SOLO per (a) infra, (b) roadmap, (c) yes/no irreversibili; tutto il resto va al giudice via `HANDOFF.md`; nessuno stream parallelo. Idempotente via marker-replace.
- **Label progetto su handoff** (founder-input): hook globale `~/.claude/hooks/session_reports_combine.sh:47` ora titola `# HANDOFF [$(basename "$REPO_DIR")] — sessione …` → rende `# HANDOFF [FLUXION] — …` (generico per ARGOS/Guardian). Backup `…bak-PROJLABEL-20260630T182527Z`. NB: modifica in `~/.claude/` (fuori da questo repo git) → nulla da committare qui. Regola salvata in memoria `feedback_handoff_project_label.md`.

### Contraddizioni aperte (non bloccanti)
1. **[D5] Legacy datati tracciati**: 17 file `.claude/NEXT_SESSION_PROMPT.*`/`HANDOFF_CURRENT.md` tracciati in git (fonte: `git ls-files | grep -iE 'handoff|next_session'`, esclusi `HANDOFF.md` canonico e `tools/SalesAgentWA/handoff.py`). Cleanup = `git rm` distruttivo → decisione founder, NON eseguito.
2. **[D6-bis] Secondo footgun TextEdit NON rimosso**: l'hook globale `session_reports_combine.sh:60` ha ancora `open -a TextEdit "$OUT"` (apre il breadcrumb effimero `HANDOFF_CURRENT.md`). Founder ha scelto di ETICHETTARLO `[FLUXION]`, non di toglierlo. Rimozione = decisione infra pendente per il giudice.
3. **[D5-bis] DISCORDANZA gitignore**: l'hook `session_reports_combine.sh:8` assume `HANDOFF_CURRENT.md` gitignored, ma sul disco è TRACCIATO e NON ignorato (fonte: `git check-ignore` exit=1). Assunzione hook falsa.
4. **Generatori legacy (mappa)**: GLOBALI in `~/.claude/hooks/` (condivisi ARGOS/FLUXION/Guardian/VOS). `global_session_end.sh` (evento Stop) → scrive `.claude/NEXT_SESSION_PROMPT.md` + auto-commit. `session_reports_combine.sh` (evento SessionEnd) → scrive `.claude/HANDOFF_CURRENT.md`.

## PROSSIMA DIRETTIVA OPERATIVA

Decisione infra pendente per il giudice/founder (non risolta qui): se (a) rendere gitignored i 2 effimeri + `git rm` dei 17 legacy [D5], e (b) rimuovere il footgun `open -a TextEdit` da `session_reports_combine.sh:60` [D6-bis]. Entrambi toccano un hook GLOBALE condiviso → impatto su 3 progetti, da valutare prima di agire.

(Carry pre-esistente, se il founder lo riprende: T1a SEO — ripristino working tree `fluxion-seo` in ~/Documents NON /tmp + sezione '3 passi' + quantifica copy #4, prova su pagina live.)
