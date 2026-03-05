# FLUXION — Handoff Sessione 24 (2026-03-05) — F04 Schede Mancanti

## PROSSIMO TASK IMMEDIATO

**F04 — Schede Mancanti**: implementare le schede cliente mancanti per i verticali.

Le 2 schede già aggiunte nelle migration (027 `scheda_fitness`, 028 `scheda_medica`) ma
probabilmente non ancora implementate nel frontend React.

**Prima di iniziare**: verificare cosa esiste già nel frontend per le schede.

---

## Completato Sessione 24 — Framework Upgrade + P0.5 commit

### Commit
- `efa9533` — feat(p0.5): onboarding frictionless (VoiceAgentSettings + guida HTML + Playwright)
- `fe0eeb6` — feat(fw): Framework Upgrade 6 feature

### Framework Upgrade — 6/6 implementate

| # | Feature | Status | Dettaglio |
|---|---------|--------|-----------|
| 1 | **Taskfile.yml** | ✅ | 15 task: tc, lint, db:schema, voice:*, imac:*, playwright, ci |
| 2 | **post-write-typescript.sh** | ✅ | any/@ts-ignore check + SQL migration guard |
| 3 | **Scoped rules glob** | ✅ | testing.md: aggiunto `e2e-tests/**`; altri già avevano `paths:` |
| 4 | **task db:schema** | ✅ | Python verifica 021-029 in lib.rs — integrato in Taskfile + CI |
| 5 | **pre-compact.sh** | ✅ | Salva session_state.md prima di /compact |
| 6 | **Permission hardening** | ✅ | deny: rm-rf, push--force, reset--hard, .env |

### Come usare il Taskfile
```bash
task --list          # Vedi tutti i task
task tc              # TypeScript check
task db:schema       # Verifica migration 021-029
task voice:health    # Ping voice pipeline iMac
task voice:restart   # Riavvia voice pipeline
task imac:sync       # Push + pull iMac
task ci              # CI completo
```

---

## Stato Git

```
Branch: master | HEAD: fe0eeb6
type-check: ✅ 0 errori
Voice tests: ✅ 1263 PASS / 0 FAIL
Playwright: ✅ 11/11 impostazioni tests
task db:schema: ✅ 021-029 tutte presenti
Uncommitted: 0 file
```

## Roadmap

| Fase | Task | Status |
|------|------|--------|
| **FW** | Framework Upgrade (6 feature) | ✅ DONE |
| **F04** | Schede Mancanti | 🔄 NEXT |
| **F10** | CI/CD GitHub Actions | ⏳ |
| **F07** | LemonSqueezy payment | ⏳ |
