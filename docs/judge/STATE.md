# STATE — FLUXION

**REGOLA**: CC non scrive mai sotto DIRETTIVA. CC non scrive mai sotto CODA IMPIANTO.

---

## FATTI (scrive CC)

**HEAD**: 7cb6a8be (chore(T-CERT-PREP/#46): macchina di riferimento, runtime e copione per CERT-21)
HEAD ATTESO: 7cb6a8be
**SESSIONE**: 47b6d42b-b12e-4578-a355-81e707853eb7
**DATA**: 2026-08-02

### Stato :3002 (verificato 2026-08-02)
UP — engine=go — SIP registered=True — reg_status=200 — SARA_TEST_CAPTURE=1
Processo PID 3057, avviato 2026-08-02 18:14 CEST (riavviato per SARA_TEST_CAPTURE=1).
Go engine PID 3152, trunk 0972536918@sip.vivavox.it.

### Fix confermati nel codice (HEAD su iMac: 2c25742, dirty=booking_state_machine.py identico a 5250527b)
- FIX-A: `escalation_manager.py:97` (E6-FIX congedo senza collega) — VERIFICATO nel codice
- FIX-C: `booking_state_machine.py:756` (Mi conferma il nome corretto?)
- AI Disclosure: `session_manager.py:743` (EU AI Act art.50)
- FIX-SOL (5250527b): `booking_state_machine.py` — _set_context_date setter unico — VERDE (T-BOOKING-FIX2, booking=9636bbc7 in DB)
- E6 testo: "La faremo richiamare dal salone al più presto. Arrivederci!" — "collega" assente ✓

### Stato macchine (2026-08-02)
- **MacBook** (repo auth): HEAD=7cb6a8be=origin/master, path=/Volumes/MontereyT7/FLUXION
- **iMac** (runtime): HEAD=2c25742 (BEHIND di ~14 commit), booking_state_machine.py dirty=FIX identico a 5250527b

### Appuntamenti DB produzione iMac (17 totali)
- app-001..015: demo statici gennaio 2026 (passati, non interferiscono)
- c57e6ade: 2026-08-03 09:00 voice (residuo stress test)
- 9636bbc7: 2026-08-03 09:30 voice (T-BOOKING-FIX2 VERDE)

### File prodotti in sessione T-CERT-PREP/#46
- `docs/judge/CERT-21-COPIONE.md` — copione certificazione per founder
- `vos/runs/20260802/cert_prep.md` — referto F1..F4 + verdetto

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
