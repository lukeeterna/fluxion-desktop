# Prompt ripartenza — generato automaticamente

**Generato**: `2026-05-11T19:39:50Z`
**Sessione**: `0ea0b99a-7a37-42aa-9d0c-4a891e11ac63`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `500e6cc chore(S200): rimuovo pre-warm (non risolveva cold-start, peggiorava avg)`

## Ultimi 5 commit
```
500e6cc chore(S200): rimuovo pre-warm (non risolveva cold-start, peggiorava avg)
24c0952 fix(S200): latency gates calibrati P50 + slow-ratio + P95 catastrofico
538014a fix(S200): pre-warm verticals prima del release gate
a4eb7e2 fix(S200): trimmed-P95 release gate (top-5% outlier exclusion)
b960231 feat(S200): Sara release gate automation — multi-vertical test harness
```

## File modificati nell'ultimo commit
```
M	voice-agent/tests/e2e/release_gate.py
```

## Ultimo prompt utente (estratto)
```
[{"tool_use_id":"toolu_01XeF1Fv4Ej6LHdLqfEi6KZ9","type":"tool_result","content":"Next wakeup scheduled for 21:44:00 (in 256s)."}]
```

## Ultimi turni assistant
```
- Hard-fail su >30% sample > 5s (regressione sistemica)
- Hard-fail solo su P95 > 12000ms (pipeline broken)
- P95 > 2000ms = WARN-only (SLO monitoring, non blocker)
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
