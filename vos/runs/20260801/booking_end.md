# T-BOOKING-END/#38 — Il booking arriva in fondo?

**Data:** 2026-08-01  
**Base commit:** 1a46ede3  
**Processo:** PID 2296, avviato 18:09 (post-pull 16:26), engine=go, registered=True, reg_status=200

---

## F0 — Anti-stantio

PID 2296 avviato 18:09 → successivo all'ultimo pull (16:26). Processo aggiornato.  
engine=go, registered=True, reg_status=200. DB voice-agent: `git diff HEAD -- voice-agent/src/orchestrator.py` = vuoto.

---

## F1 — Il limite dei 60 giorni

**File:** `voice-agent/src/availability_checker.py:227-228`  
**Codice:** `days_ahead = (check_date - date.today()).days; if days_ahead > self.config.max_advance_days:`  
**Soglia:** `max_advance_days = 60` (riga 64)  
**Risposta template:** riga 171 — `"Le prenotazioni sono possibili fino a {days} giorni in anticipo. Vuole scegliere una data piu vicina?"`

**Sep 8, 2026 cade DENTRO il limite**: 38gg < 60 → il confronto NON scatta su quella data.

**Confronto sbagliato trovato**: il FSM produce `booking_action.date = "2077-09-13"` per l'input "lunedì prossimo" (entity extractor: Aug 3, 2026 — corretto). La data corrotta 2077-09-13 − 2026-08-01 ≈ 18.669gg >> 60 → availability_checker restituisce `too_far` → risposta "60gg". L'origine della corruzione (Aug 3 → 2077-09-13) è nel booking state machine, non in entity_extractor.

---

## F2 — Booking completo Parrucchiere (trascrizione verbatim)

| # | Layer | FSM | USER | SARA |
|---|-------|-----|------|------|
| 1 | L2_slot | waiting_service | "Buongiorno, voglio prenotare un taglio capelli" | "Abbiamo Taglio Uomo o Taglio Donna. Tu cosa preferisci?" |
| 2 | L2_slot | waiting_name | "Taglio Donna" | "Ok. Bene, Taglio Uomo! Mi dice il suo nome, per cortesia?" |
| 3 | L2_slot | registering_phone | "Lucia Verdi" | "Non la trovo tra i nostri clienti, Lucia. Mi dà un numero di telefono per registrarla?" |
| 4 | L2_slot | confirming_phone | "3398765432" | "Ho capito 3398765432, corretto?" |
| 5 | L2_slot | waiting_date | "si" | "Ok. Benvenuto Lucia Verdi! Sei dei nostri! Taglio Uomo, per quale giorno?" |
| 6 | L2_slot | waiting_time | "lunedi prossimo" | "Le prenotazioni sono possibili fino a 60 giorni in anticipo. Vuole scegliere una data piu vicina? Vuole che la inserisca in lista d'attesa? La contatteremo appena si libera un posto." |
| 7 | L2_slot | confirming | "alle 10" | "Ecco fatto! Lucia! Allora, Taglio Uomo, lunedì 13 settembre, alle 10:00. Tutto giusto?" |
| 8 | L2_slot | confirming | "si" | "Grande. Mi scusi, c'è stato un problema. Può riprovare più tardi?" (intent: waitlist_error) |

**Appuntamento creato nel DB:** NO — 0 record in tabella `appuntamenti`, 0 in `waitlist`.  
**booking_action.date registrato:** "2077-09-13" (anno errato).  
**Note servizio:** "Taglio Donna" riconosciuto ma visualizzato come "Taglio Uomo" nei turni 2 e 5.

**BOOKING: BLOCCATO A turno 8 (conferma finale — waitlist_error)**

---

## F3 — Stress Parrucchiere (verticale salone)

| Metrica | Baseline 01/08 | Questo run | Delta |
|---------|---------------|------------|-------|
| BOOKING | FAIL | WARN (1/3 OK) | invariato |
| OK | — | 25/30 | — |
| WARN | — | 5/30 | — |
| FAIL | — | 0/30 | — |
| AVG ms | 332 | 1123 | +791ms |
| P95 ms | 632 | 2153 | +1521ms |

**Dettaglio WARN booking:**
- Taglio uomo turn 6: "c'è stato un problema" (waitlist_error — stessa causa F2)
- Colore e piega turn 3-6: client non trovato → bloccato in registering_phone

**Scenario OK:** Barba (cliente esistente "Luca Verdi" → disambiguating_name → completato).

**Cleanup fixture:** rimossi 13 seed (tel 3339000001-13) + 2 test F2 (Lucia Verdi, Donna Marco Bianchi) = 15 record.

---

## Stato :3002 finale

PID 2296 | engine=go | registered=True | reg_status=200  
orchestrator.py: `git diff HEAD` = vuoto (identico a master)

---

**BOOKING: BLOCCATO A turno 8 (waitlist_error — data corrotta 2077-09-13 nel FSM)**
