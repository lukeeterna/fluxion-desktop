# STATE — FLUXION

**REGOLA**: CC non scrive mai sotto DIRETTIVA. CC non scrive mai sotto CODA IMPIANTO.

---

## FATTI (scrive CC)

**HEAD**: 1a17f072 (feat(T-MACCHINA): pulse iMac + gate anti-stantio check h) + 15 test OK)
HEAD ATTESO: 1a17f072
**SESSIONE**: 07af0f9d-2104-4612-8035-33fbe830aed4
**DATA**: 2026-08-04

### Stato :3002 (verificato 2026-08-04 T-MACCHINA)
UP — engine=go — SIP registered=True — reg_status=200
IMAC-PULSE.json probed_at=2026-08-04T15:48:31+00:00 — fresco (< 24h).
Go engine, trunk 0972536918@sip.vivavox.it.

### Stato macchine (2026-08-04 — T-MACCHINA)
- **MacBook** (repo auth): HEAD=1a17f072=origin/master, path=/Volumes/MontereyT7/FLUXION
- **iMac** (runtime): HEAD=1a17f072=origin/master (allineato da T-MACCHINA), voice-agent/ pulito

### SHA256 file voce — allineamento verificato (T-CERT-GATE/#47)
- booking_state_machine.py: d64a3934c265c7472da26874db9a59b7b32166997077a75d3262ab4951995afd
- orchestrator.py:          1a632b3204f943c1125c0a9fcd9acfedfcd08e3f618f25dc42b90fdddb0ba7a0
- escalation_manager.py:    ac8b0a5134df28eb89754dc3da2ed6698b68a1664a85184f6849198de9ca3266
- voip_goengine.py:         cbcf00d5109d31515a89f5d51c319fc229fb6449175bcd328379ab1889a857c8

### Appuntamenti DB (T-CERT-GATE/#47)
- src-tauri/fluxion.db (iMac): 15 record (app-001..015 demo statici gen 2026)
- c57e6ade e 9636bbc7 NON presenti (già assenti prima di questa unità — vedi F6)
- voice-agent/fluxion.db appuntamenti: 0 record

### Fix confermati nel codice (HEAD c143dd99 su entrambe le macchine)
- FIX-A: `escalation_manager.py:97` (E6-FIX congedo senza collega)
- FIX-C: `booking_state_machine.py:756` (Mi conferma il nome corretto?)
- AI Disclosure: `session_manager.py:743` (EU AI Act art.50)
- FIX-SOL (5250527b): `booking_state_machine.py` — _set_context_date setter unico
- E6 testo: "La faremo richiamare dal salone al più presto. Arrivederci!" — "collega" assente ✓

### File prodotti in sessione T-CERT-PREP/#46
- `docs/judge/CERT-21-COPIONE.md` — copione certificazione per founder
- `vos/runs/20260802/cert_prep.md` — referto F1..F4 + verdetto

### File prodotti in sessione T-CERT-GATE/#47
- `vos/runs/20260802/cert_gate.md` — referto F1..F6 + tabella SHA + PRONTI A CHIAMARE

---

## DIRETTIVA (scrive SOLO il giudice)

FALSIFICATA: "Segnalare a Sol: fix L1_exact mancante." — il guard esiste a `orchestrator.py:1527` e funziona. Causa reale del loop: processo stantio (1a46ede).

**Blocco attivo**: T-JUDGE-STATE/#35 — questa sessione CC.

**Mandato successivo** (da incollare al prossimo blocco):
> Da definire dal giudice dopo revisione di questa sessione.

**Ipotesi vive**:
- La data corrotta 2077-09-13 origina dal booking FSM in gestione dello stato `waiting_date` → `confirming`. Da investigare: come entity_extractor produce Aug 3 ma il FSM persiste 2077-09-13.
- Il servizio viene rispecchiato erroneamente ("Taglio Donna" → "Taglio Uomo") in turni 2 e 5: possibile problema in `waiting_service` handler.

**Cosa NON fare**:
- Non ritestare via trunk/2°-account/seconda-REGISTER (S244 FALSIFICATA, path pjsua2 morto).
- Non riaprire diagnosi crash lock.c:279 (NDEBUG risolto, S355 VERDE).
- Non toccare U2 CERT-21 via HTTP — è gate founder con chiamata vocale fisica.
- Non proporre workaround sulla soglia 60gg (F-07 FALSIFICATO: è il FSM che corrompe la data).

---

## CODA IMPIANTO (scrive SOLO il giudice)

**REGOLA**: quando una corsia resta senza blocco attivo, si prende la prima voce di questa coda
compatibile con quella corsia, senza attendere il giudice.

1. T-MACCHINA (corsia MACCHINA) — pubblica lo stato dell'iMac nel repo, gate anti-stantio
2. T-EXPOSURE v2 (corsia MACCHINA) — untrack DB, licenza, hook, inventario esposizioni history
3. T-VERIFICA-3K (corsia MACCHINA) — attestazione a tre chiavi e checklist blindatura repo
4. T-CI-TRUTH (corsia WEB) — perché la CI è rossa davvero, sola lettura
