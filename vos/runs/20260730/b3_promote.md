# B3-PROMOTE — 2026-07-30 — Rapporto esecuzione mandato

## Procedura eseguita

### GATE-0 + SANATORIA
- **G0-1**: HANDOFF.md spostato da root a `archive/handoff-prosa/HANDOFF_20260730.md` ✅
- **G0-2**: `scripts/vos-close.sh` riga 7 ripuntata da `HANDOFF.md` a `docs/judge/STATE.md`
  (check-ignore guard aggiornata; commento riga 8-9 obsoleto lasciato come nota storica; DISCORDANZA: senso identico, file target cambiato) ✅
- **G0-3**: `.claude/scheduled_tasks.lock` PRESENTE ✅
- **G0-4**: `.claude/NEXT_SESSION_PROMPT.md` rimosso (era causa FAIL check e) di vos_check.sh) ✅

### F1 — RICOGNIZIONE (≤10 righe)
1. `:3002` DOWN — nessun pid su iMac (verificato `lsof -ti:3002` via SSH)
2. Engine attuale: NESSUNO (servizio non attivo)
3. Meccanismo switch: `os.getenv("VOICE_ENGINE","pjsua2")` in `voice-agent/main.py:1326`
4. File go engine: `voice-agent/src/voip_goengine.py` PRESENTE su iMac (`/Volumes/MacSSD - Dati/fluxion/`)
5. Procedura documentata: `b3_open.sh` → CHECKPOINT 1 cattura PID da `:3002`; con servizio DOWN → ABORT immediato
6. **Passaggio mancante**: argv standard di avvio Sara NON documentato nel repo; b3_open.sh lo cattura solo da processo vivo
7. **BLOCCO**: procedura non univoca — F2 non eseguito

### F2 — PROMOZIONE
NON ESEGUITA. Prerequisito non soddisfatto: `:3002` DOWN, `b3_open.sh` richiederebbe il processo vivo per catturare argv.

## Stato finale di :3002
DOWN — nessuna modifica al servizio. Stato identico all'ingresso del mandato.

## Verifiche
- engine go attivo: NO (servizio non avviato)
- registrazione SIP: NON VERIFICABILE (:3002 assente)
- disclosure AI Act: NON VERIFICATA (servizio assente)
- FIX-A / FIX-C: codice presente nel repo ma servizio non avviato

## Cosa manca per la prossima sessione
Per promuovere B3 servono due fatti prerequisito verificati prima di eseguire mandato:
1. **argv standard Sara**: documentare il comando esatto di avvio (`python3 main.py --port 3002` o equivalente con path assoluto) in un file nel repo (es. `voice-agent/docs/startup.md`)
2. **:3002 UP con pjsua2**: avviare Sara normalmente su iMac prima del mandato B3-PROMOTE, oppure definire procedura di avvio diretto con `VOICE_ENGINE=go` senza dipendere da `b3_open.sh`

## vos_check.sh finale
```
PASS=5 FAIL=2
FAIL b) porcelain-dirty (archivio HANDOFF non committato)
FAIL e) NEXT_SESSION_PROMPT.md [risolto in questa sessione → si chiuderà a PASS dopo commit]
```
Post-commit atteso: PASS=7 FAIL=0 (b) risolto da git add archive/ + commit)

## VERDETTO: ROSSO

Causa: procedura switch non univoca con :3002 DOWN. Nessuna modifica al servizio di produzione.
