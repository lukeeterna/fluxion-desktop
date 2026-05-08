# Prompt ripartenza S191 — Gate 3 D-2 + D-3 closure

**Generato**: 2026-05-08T20:05Z (S190 chiusura)
**Sessione precedente**: S190 ✅ D-1 SQLite EXPLAIN audit clienti 1000+ — 8/8 PASS
**Repo**: `/Volumes/MontereyT7/FLUXION` branch `master`

## S190 esito

D-1 chiuso senza nuova migration: gli indici di S154 (migration 036) bastano fino a 1000 clienti.

| Query | P95 | SLO | Status |
|-------|-----|-----|--------|
| Q1 list-all | 24.50ms | 50ms | PASS |
| Q2 by-id | 0.07ms | 5ms | PASS |
| Q3 search LIKE | 1.55ms | 50ms | PASS |
| Q4 count-active | 0.11ms | 10ms | PASS |
| Q5 count-vip | 0.10ms | 10ms | PASS |
| Q6 export | 10.25ms | 50ms | PASS |
| Q7 by-telefono | 0.04ms | 5ms | PASS |
| Q8 by-email | 0.03ms | 5ms | PASS |

Output: `docs/perf/D1-sqlite-query-plans.md` + tool riutilizzabile `tools/perf-d1/audit.py`.

## Gate 3 status

- F-1 / F-2 / F-3 / F-4 ✅ ✅ ✅ ✅
- D-1 SQLite ✅ S190
- D-2 IPC Tauri ⏳ S191 (MacBook only)
- D-3 Voice Piper ⏳ S191 (NEEDS iMac online)

## S191 priorità

### D-2 IPC <100ms benchmark Tauri (MacBook)

**Pre-flight**:
```bash
curl -s http://192.168.1.2:3002/health  # iMac online?
ls "/Users/macbook/Library/Application Support/com.fluxion.desktop/fluxion.db"  # DB esiste?
```

**AC misurabili**:
- [ ] Avviare `npm run tauri dev` MacBook (HTTP bridge porta 3001 + UI)
- [ ] Bench IPC `get_clienti` round-trip 100 iterazioni con DevTools console (`performance.now()`)
- [ ] Bench IPC `search_clienti` con query reale 50 iterazioni
- [ ] Bench IPC `get_cliente(id)` 100 iterazioni
- [ ] P95 < 100ms target per ogni
- [ ] Output `docs/perf/D2-ipc-latency.md` con tabella + raccomandazioni

**Bottleneck atteso**: serializzazione JSON Tauri IPC + 33 colonne `Cliente` carico anche su lista. Eventuale ottimizzazione: `ClienteListRow` projection ridotta.

### D-3 Voice Piper P50/P95 (NEEDS iMac online)

**Pre-flight**:
```bash
ssh imac "curl -s http://localhost:3002/health"  # voice pipeline up?
ssh imac "lsof -i:3002"  # binding 127.0.0.1 atteso
```

**AC misurabili**:
- [ ] Voice pipeline su iMac running con TTS forced=Piper offline
- [ ] Test corpus 50 utterance italiano realistico (booking, FAQ, disambiguazione)
- [ ] Misurare end-to-end latency: STT input → TTS audio chunk first byte
- [ ] P50 / P95 / P99 + breakdown layer (STT / LLM / TTS / VAD)
- [ ] Target P95 < 800ms (offline mode)
- [ ] Output `docs/perf/D3-voice-latency.md`

**Skip se iMac offline** → solo D-2 (D-3 deferred S192).

## Context discipline

S190 ha consumato 51% (entro WARN, sotto soglia 60% chiusura). **Sessione S191 parte fresca**.

**Regola permanente** (S185-A + S186): file critici NO edit sopra 50% (HELPDESK.md, CLAUDE.md autorevole, PLAN.md AC, .claude/rules/*.md, migrations/**, tauri.conf.json, *.schema.json). D-2 può richiedere lettura `commands/clienti.rs` (non critico, OK).

## Bootstrap S191

```bash
cd /Volumes/MontereyT7/FLUXION
cat .claude/NEXT_SESSION_PROMPT.md | head -50
git log --oneline -5
curl -s http://192.168.1.2:3002/health  # iMac status decision tree D-3
```
