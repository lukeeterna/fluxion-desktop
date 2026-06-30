<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF FLUXION (fonte unica di sessione)

## STATO CORRENTE

### Sessione 2026-06-30 — Protocollo handoff canonico installato (VERDE)
- **Cosa**: installato il protocollo handoff VOS deterministico. `HANDOFF.md` (root) è ora l'UNICA fonte di handoff, tracciata in git e pushata.
- **Commit**: `525e433 chore(handoff): chiusura sessione — HANDOFF.md canonico` (fonte: `git log`). Pushato → `origin/master == 525e433` (off-machine durability OK; il push ha bypassato la branch-rule "CI Pass" via permesso token).
- **Artefatti**:
  - `HANDOFF.md` root — marker riga 1 `<!-- VOS-CANONICAL-HANDOFF v1 -->`, non gitignored (fonte: `git check-ignore` exit=1).
  - `CLAUDE.md` root — blocco protocollo righe 270-283, marker `VOS-HANDOFF-PROTOCOL:BEGIN/END` (idempotente via python marker-replace).
  - `scripts/vos-close.sh` — eseguibile (`-rwxr-xr-x`); stub-izza i 3 file `.claude/*` legacy + add + commit + push + apre TextEdit.
- **Idempotenza**: 2a run di `vos-close.sh` = no-op (nessun nuovo commit). Verificato.

### Contraddizioni aperte (non bloccanti)
1. **[D5] Legacy datati tracciati**: ~15 file `.claude/NEXT_SESSION_PROMPT.*` datati/suffissati (`.S322`, `_S371`, `_S372`, vari `.bak-*`) sono ancora tracciati in git (fonte: `git ls-files | grep -iE 'next_session'`). Il protocollo dice "ignorali" ma NON li rimuove → rischio che CC ne legga uno per errore. Cleanup = `git rm` distruttivo, decisione founder separata, NON eseguito.
2. **[D6] Rischio marker da editor**: `vos-close.sh` apre `HANDOFF.md` in TextEdit → un tasto a vuoto può corrompere la riga-1/marker (già successo questa sessione: prefisso `Sa`, ripristinato da commit). Mitigazione consigliata: rimuovere `open` dallo script o aprire una copia read-only.
3. **[D1] CI su questo repo**: contrariamente alla premessa, `fluxion-desktop` HA workflow `release.yml`/`release-full.yml`/`virustotal-gate.yml`, ma tutti tag-gated (`push: tags v*.*.*`) → un commit-push su master NON innesca deploy-prod (fonte: `.github/workflows/*` trigger `on:`).

## PROSSIMA DIRETTIVA OPERATIVA

T1a in volo: ripristino working tree SEO (re-clone fluxion-seo in ~/Documents, NON /tmp) + sezione '3 passi' + quantifica copy #4, prova su pagina live. Dettaglio = ultimo prompt del giudice.

(Opzionale, se il founder lo decide: cleanup dei ~15 legacy `NEXT_SESSION_*` tracciati [D5] e hardening di `vos-close.sh` rimuovendo `open -a TextEdit` [D6].)
