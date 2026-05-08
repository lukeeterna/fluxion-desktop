# Prompt ripartenza S190 — Gate 3 D-1 SQLite perf

**Generato**: 2026-05-08T21:50Z
**Sessione precedente**: S189-B-verify ✅ HARD-STOP validato 4/4 check oggettivi
**Repo**: `/Volumes/MontereyT7/FLUXION` branch `master`
**Last commit S189-B**: `8195a20 feat(S189-B): F-3+F-4 LIVE su CF + fix self-probe + token CF working`

## HARD-STOP S189-B verifica (eseguita 21:23-21:50Z)

- [x] Check 1 — commit `8195a20` reale presente in `git log`
- [x] Check 2 (sostituito) — `wrangler deployments list` no API token MacBook+iMac, MA verifica indiretta OK: `/health` HTTP 200 timestamp live + `/admin/health/status` 401 (route F-4 deployata) + `/admin/email-sequence/preview` 401 (route F-3 deployata)
- [x] Check 3 — `https://fluxion-proxy.gianlucanewtech.workers.dev/health` HTTP 200 236ms `{"status":"ok","version":"1.0.0"}`
- [x] Check 4 — Gmail `from:resend after:2026/05/08`: **5 email** (4 thread Gmail, primo "FLUXION 2" merged 2 msg). Subjects: "Hai già attivato la tua licenza?" + "Inizia da qui: i 3 passi del primo giorno" + "Una settimana insieme. Come va?" + "Un mese insieme: ti va di lasciare una recensione?"
- [ ] Check 5 — Discord webhook RECOVERED alert: founder verifica visivamente (write-only, no programmatic check)

**Verdetto**: claim S189-B "F-3+F-4 LIVE su CF" valido. NO regressione context-pressure 84%.

## Gate 3 status

| Item | Status |
|------|--------|
| F-1 FAQ landing 24 Q&A | ✅ S187 |
| F-2 closing alignment | ✅ S187 |
| F-3 Email sequence (5 step Resend) | ✅ S189-B LIVE + E2E PASS |
| F-4 Health monitor (cron 5min + Discord) | ✅ S189-B LIVE |
| D-1 SQLite EXPLAIN QUERY PLAN clienti 1000+ | ⏳ S190 PRIMA |
| D-2 IPC <100ms benchmark Tauri | ⏳ S190 (richiede Tauri dev MacBook) |
| D-3 Voice Piper P50/P95 | ⏳ S190 (richiede iMac online + voice-pipeline) |

## S190 D-1 priorità ASSOLUTA — MacBook only zero costi

**Scope**: validare query principali `clienti` NON facciano table scan sopra ~1000 record. SLO P95 query lista clienti `<50ms`.

**AC misurabili**:
- [ ] Seed 1000 clienti idempotente (`tools/seed-clienti-1k.{ts,sh}` faker italiano)
- [ ] Audit `docs/perf/D1-sqlite-query-plans.md` con 1 riga per query (SQL + EXPLAIN plan + verdict + index proposed)
- [ ] SCAN TABLE su `clienti` risolti via migration o documentati accettabili (<1000 records lookup)
- [ ] P95 query lista clienti `<50ms` misurato 100 iterazioni
- [ ] Commit atomico `feat(S190 D-1): SQLite EXPLAIN audit clienti + indici performance`

**Bootstrap S190 (eseguire all'inizio nuova sessione)**:
```bash
cd /Volumes/MontereyT7/FLUXION
cat .claude/NEXT_SESSION_PROMPT.md
git log --oneline -3
grep -rn "fluxion.db\|app_data_dir" src-tauri/src/ | head -10
grep -A 30 "CREATE TABLE.*clienti" src-tauri/migrations/*.sql | head -50
grep -rn "SELECT.*clienti\|FROM clienti" src-tauri/src/ | head -20
```

Poi `/gsd:plan-phase` con AC sopra.

## Context discipline

S189-B-verify ha consumato 68%+ → chiusura ordinata. **NUOVA SESSIONE** S190 parte fresca.

**Regola permanente** (S185-A + S186): migrations sono file critici, NO edit sopra 50% context. Se serve migration sopra soglia → split sessione.

## D-2/D-3 considerazioni

- D-2 IPC benchmark richiede `npm run tauri dev` MacBook → eventualmente DEFER se serve Rust build su iMac
- D-3 voice Piper richiede iMac online + voice-pipeline → check `curl http://192.168.1.2:3002/health` PRIMA di pianificare
- D-1 standalone MacBook → priorità ASSOLUTA S190

## Founder action manuale residua S189-B

- Verifica Discord canale (Check 5): apri server → canale webhook → cerca embed alert RECOVERED ultime 30 min (post-deploy `8195a20`). Se presente → S189-B 5/5 ✅ totale.
