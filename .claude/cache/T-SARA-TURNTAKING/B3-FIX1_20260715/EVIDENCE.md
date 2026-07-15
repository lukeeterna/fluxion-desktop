# B3-FIX1 — M5 congedo hangup soppresso — EVIDENZA (2026-07-15, sessione #34v)

## VERDETTO
Fix M5 IMPLEMENTATO + DEPLOYATO + verificato staticamente/compile. Prova BYE live =
BLOCKED-ON rig founder-executed (telefono) — vedi DISCORDANZA.

## ROOT CAUSE (da log B3-LIVE HEAD 4ddceb63, calls/20260714_174544_B3-LIVE/sara_go.log ~356-366)
- `17:36:26 [S142] Standalone goodbye detected: 'a rivederci' → exit=True`
- `17:36:27 HANGUP soppresso (FSM-guard): should_exit ma intent non-congedo ('')`

Due gap nella SUPPLY dell'intent verso il guard (il guard NON è il difetto):
1. `orchestrator.py` `process_audio()` wrapper dict (era ~:5634) NON includeva la chiave
   `intent` → il guard `voip_goengine.py:796` leggeva `result.get("intent")` = None → `''`.
2. `orchestrator.py` `_is_standalone_goodbye` block (era :1346): `intent="goodbye_standalone"`
   era annidato in `if not response:` → saltato quando la frustrazione acustica (log 17:36:25
   score=0.63) aveva già popolato `response` → intent restava vuoto anche col fix #1.

## FIX (1 solo file: voice-agent/src/orchestrator.py — 2 edit)
- Edit1 (:5645): aggiunta `"intent": result.intent,` al wrapper dict di `process_audio`.
- Edit2 (:1341): `intent="goodbye_standalone"` spostata FUORI da `if not response:` →
  impostata incondizionatamente su `_is_standalone_goodbye`.
- GUARD `voip_goengine.py:790-805` INTATTO → VINCOLO rispettato: nessun allargamento a
  should_exit generico / intent vuoto; protezione anti-hangup-spurio (verde D3) preservata.

## CATENA VERIFICATA (statica + compile)
fix → intent="goodbye_standalone" → wrapper la propaga → guard :797 `"goodbye" in _intent`
= True → `_hangup_after_drain` (BYE dopo drain TX). Regressione: should_exit non-congedo →
intent NON contiene goodbye/chiusura → HANGUP soppresso (invariato).

## DEPLOY
- MacBook repo md5 orchestrator.py = aa4dcb0884e9160d066a7d209b712edf
- iMac runtime  md5 orchestrator.py = aa4dcb0884e9160d066a7d209b712edf  (IDENTICI)
- iMac Python 3.9 `py_compile` = PY39_COMPILE_OK
- Backup #1d: MacBook + iMac `src/orchestrator.py.bak-B3FIX1` (md5 pre-fix 049961da…, size 294040)
- Produzione :3002 pjsua2 NON toccata (reg_status 200 baseline; processo in RAM invariato).

## DISCORDANZA (§1.1 — premessa X2 falsificata dal filesystem, REGOLA #31)
| | Premessa mandato | Fatto (iMac) |
|---|---|---|
| Rig | porte alte 15062/15090/sara3003:3003 + `-injectwav` | `b3_open.sh` SOSTITUISCE produzione :3002 con Sara-go |
| Iniezione | harness `-injectwav/-injectat/-dur` | NESSUN binario injectwav (grep vuoto iMac+repo); RUNBOOK_B3 impone TELEFONATA reale al DID 0972536918 |
L'unico rig esistente richiede telefono e tocca :3002 — entrambi VIETATI da questo mandato.
→ X2 come specificato INESEGUIBILE; STOP §1.1/#1c, nessun rig inventato.

## BLOCKED-ON (Rule 1b) — prova BYE live
TERMINAL_FACT: "l'harness/chiamante vede CALL_END da BYE entro ~5s dal congedo".
Raggiungibile SOLO via rig founder-executed `/tmp/b3/b3_open.sh` (SEQUENZA B, telefonata reale)
DOPO che l'iMac carica il fix (già deployato via scp). Non re-validare staticamente.

## X3 DIAG NLU — SKIP DICHIARATO (valve TAGLIA S, context budget)
Parziale da log in-context: NLU ha funzionato (cerebras HTTP 404 model_not_found → fallback
groq/llama-3.1-8b-instant intent=CORTESIA 170ms, corretto). M3 prenotazione-generica NON
spiegata dal provider NLU (groq ha risposto) → sospetto FSM/booking flow, traccia FSM completa
+ dating primo 404 + config cerebras = NON eseguiti (SKIP). Routing NLU CONDIVISO col path
pjsua2 produzione (modulo fluxion.nlu.providers unico) → eventuale degrado varrebbe anche in
produzione: da confermare in sessione dedicata.
