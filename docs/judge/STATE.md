# STATE — FLUXION

**REGOLA**: CC non scrive mai sotto DIRETTIVA. CC non scrive mai sotto CODA IMPIANTO.

---

## FATTI (scrive CC)

**HEAD**: f436160f (test(T-BOOKING-END/#38): il booking arriva in fondo?)
HEAD ATTESO: f436160f
**SESSIONE**: d105b455-ef5e-4e29-83e0-daf336989a9b
**DATA**: 2026-08-01

### Stato :3002
UP — engine=go — SIP registered=True — reg_status=200 — health=ok
Processo PID 2296, avviato 2026-08-01 18:09 (post-pull 16:26).

### Fix confermati nel codice (HEAD)
- FIX-A: `escalation_manager.py:97` (E6-FIX congedo senza collega)
- FIX-C: `booking_state_machine.py:756` (Mi conferma il nome corretto?)
- AI Disclosure: `session_manager.py:743` (EU AI Act art.50)
- FIX-SOL (1e6c628f): `orchestrator.py` — skip_for_booking L4 guard CANCELLAZIONE+SPOSTAMENTO — FUNZIONA (processo stantio era la causa del loop, non il codice)

### Esiti misurati — T-BOOKING-END (f436160, 2026-08-01)
- BOOKING: BLOCCATO a turno 8 — `booking_action.date = "2077-09-13"` (corrotta), 0 appuntamenti nel DB
- STRESS Parrucchiere: 25/30 OK, 5/30 WARN (tutti waitlist_error da stessa causa)
- Scenario Barba (cliente esistente): PASS completo
- AVG 1123ms, P95 2153ms
- Causa: entità data estratta correttamente (Aug 3, 2026) ma FSM produce anno 2077; origine in booking_state_machine, non in entity_extractor

### File prodotti in sessione
- `docs/judge/LEDGER.md` (T-JUDGE-STATE/#35)
- `docs/judge/FALSIFICATO.md` (T-JUDGE-STATE/#35)
- `docs/judge/BOOT-GIUDICE.md` (T-JUDGE-STATE/#35)

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
