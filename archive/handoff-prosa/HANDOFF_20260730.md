[FLUXION]

## STATO CORRENTE — 2026-07-30 20:06 UTC+2

**Sessione**: T-F3-SIP-v2 (#34v) — taglia XS
**Commit HEAD**: `5c937796` (pushato, `origin/master` allineato)
**Context usato**: 23.9% SAFE

### Lavoro eseguito questa sessione

1. **Driver v2 ricevuto e integrato** — `vos/runs/20260730/f3_sip_driver_v2.py` (2368 righe, compile OK, path harness verificato)
2. **Sanatoria** — `NEXT_SESSION_PROMPT.md` rimosso; `.husky/pre-commit` riga 32 `git add .` commentata (nota "viola PROTOCOLLO §5")
3. **Rig lanciato** — sara3003+regstub loopback high-port, `registered:true` in 6s
4. **Driver eseguito UNA volta** — chiamata NON raggiunge CONFIRMED: `SIP 480 Temporarly unavailable` dopo `180 Ringing`
5. **Rig spento pulito** — 4 high-port FREE, zero orfani, `:3002` invariato (non attivo)
6. **`docs/judge/STATE.md` aggiornato** con esito reale
7. **Commit + push** — `5c937796` — file confermati nel commit: `.husky/pre-commit`, `docs/judge/STATE.md`, `vos/runs/20260730/f3_sip_driver_v2.py`

### Esito T-F3-SIP-v2: VERDETTO ROSSO

- **SCN-08**: FAIL — gate fallito, scenari non esercitati
- **SCN-09**: FAIL — gate fallito, scenari non esercitati
- **Causa**: go engine emette `480 Temporarly unavailable` su OGNI INVITE del driver pjsua2 — identico alla v1. Il driver v2 ha eliminato il difetto SDP multi-media-line (riusando l'harness), ma il 480 persiste: la causa è a monte nell'accettazione INVITE da parte del go engine.

---

## DISCORDANZE/CONTRADDIZIONI APERTE

1. **`vos_check.sh` 6/7** — FAIL b) residuo: `D .claude/scheduled_tasks.lock` (deleted da hook auto-close sessione precedente, non da questa sessione; non pertinente al mandato corrente)
2. **iMac branch `fix/license-interop-r01-s327`** — non allineato a master; stash pendente; non interferisce con il rig ma va rimosso prima di attività di build

---

## PROSSIMA DIRETTIVA OPERATIVA

**Per il giudice/Sol**: investigare perché go engine emette `480` su ogni INVITE del driver pjsua2 su high-port. Ipotesi da verificare:
- Il go engine su `:15090` accetta INVITE solo da caller già registrato (REGISTER → 200 OK prima dell'INVITE)?
- Serve un Account registrato lato harness sul server SIP regstub prima del makeCall?
- Il SDP offerto da pjsua2 (multi-codec, opus/speex/PCMU) è compatibile con il go engine?
- Log sara3003 riga specifica del `480`: estrarre con `grep -i "480\|unavailable\|error\|reject" /tmp/rig_sara3003.log | head -20` sul prossimo run rig

**Prompt ripartenza per CC**:
```
T-F3-SIP-v2 (#34v) — diagnosi 480. Leggi docs/judge/STATE.md. Il go engine emette 480 su ogni INVITE dal driver pjsua2. Rig: sara3003 :3003 + regstub :15062 + SIP :15090. Obiettivo: identificare la causa del 480 (log sara3003, configurazione go engine) e proporre il fix minimo (non riscrivere il driver). Mandato: una sola ripetizione; STOP se terzo ciclo stesso punto (regola #1c).
```

**vos_check.sh**: 6/7 — residuo `scheduled_tasks.lock` da risolvere con `git add -u .claude/scheduled_tasks.lock && git commit -m "chore: sync lock"` in prossima sessione se non si risolve da solo.
