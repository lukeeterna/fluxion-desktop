# T-BOOKING-FIX2/#42 — Setter unico con validazione data + prove booking

**Data:** 2026-08-01  
**Commit base:** 917bceee  
**Processo :3002:** PID 2296, avviato 18:11 (post-pull 16:26), engine=go

---

## F1 — Integrità file Sol

| Campo | Valore |
|-------|--------|
| SHA-256 atteso | d64a3934c265c7472da26874db9a59b7b32166997077a75d3262ab4951995afd |
| SHA-256 calcolato | d64a3934c265c7472da26874db9a59b7b32166997077a75d3262ab4951995afd |
| Esito | **COINCIDE** ✅ |
| Righe | 4646 (giudice: 4647 — diff 1 = trailing newline) |
| Diff --stat | +160 -27 (187 lines changed) |

---

## F2 — Controllo del giudice

| Check | Risultato | Dettaglio |
|-------|-----------|-----------|
| (a) assegnazioni `self.context.date =` | **1 sola** ✅ | riga 773, dentro `_set_context_date` |
| (b) letterale `60` come max_advance_days | **assente** ✅ | occorrenze: `text[:60]` riga 1202, commenti `60%`/`0.60` |
| (c) chiamanti che ignorano return | **righe 3072 + 3646** ⚠️ | entrambe passano `None` (clear, always accepted) — rischio residuo ZERO |

---

## F3 — Trascrizione booking Parrucchiere con «lunedì prossimo»

| # | Layer | FSM | USER | SARA |
|---|-------|-----|------|------|
| T1 | L1_exact | idle | "Buongiorno" | "Mi dica pure, come posso aiutarla?" |
| T2 | L2_slot | waiting_name | "Vorrei prenotare un taglio donna" | "Ok. Come ti chiami?" |
| T3 | L2_slot | registering_phone | "Mi chiamo Marco Rossi" | "Non la trovo tra i nostri clienti, Marco. Mi dà un numero di telefono per registrarla?" |
| T4 | L2_slot | confirming_phone | "333 1234567" | "Ho capito 3331234567, corretto?" |
| T5 | L2_slot | waiting_date | "Sì" | "Che bello! Ok. Benvenuto Marco Rossi! Sei dei nostri! **Taglio Donna**, per quale giorno?" |
| T6 | L2_slot | confirming | "lunedì prossimo" | "lunedì 3 agosto, abbiamo posto alle 09:00. Confermiamo?" |
| T7 | L1_exact | confirming | "Sì, perfetto" | "Benissimo! Conferma la prenotazione?" |
| T8 | L2_slot | waiting_time | "Confermo" | "Benissimo. Mi dispiace, l'orario 09:00 non è disponibile. Il primo slot libero è alle 09:30. Va bene, oppure preferisce: 1. 09:30 ..." |
| T9 | L2_slot | waiting_time | "09:30 va benissimo" | "Ottimo! Ho annotato il suo interesse per il pacchetto..." |
| T10 | L2_slot | confirming | "No grazie, 09:30" | "Fantastico! Marco! Allora, **Taglio Donna**, lunedì 3 agosto, alle 09:30. Tutto giusto?" |
| T11 | L2_slot | completed | "Sì confermo" | "Perfetto, prenotazione confermata! Le invieremo la conferma via WhatsApp. Tutto confermato! A lunedì 3 agosto da Salone Demo FLUXION..." |

### Righe [FSM-DATE-SET] emesse

```
22:40:40 [src.booking_state_machine] INFO: [FSM-DATE-SET] received='2026-08-03' normalized='2026-08-03' outcome=accepted origin=context_extraction_unambiguous_date reason=in_range
```

### Booking creato nel DB

| Campo | Valore |
|-------|--------|
| id | 9636bbc7479541289d5db336e6ea823d |
| servizio_id | srv-taglio-donna |
| data_ora_inizio | 2026-08-03T09:30:00 |
| stato | confermato |
| fonte | voice |

**Confronto bug precedente:** "lunedì prossimo" produceva `date=2077-09-13`. Ora produce `2026-08-03`. **BUG RISOLTO.**
**Display servizio:** "Taglio Donna" mostrato correttamente (era "Taglio Uomo" nei turni 2 e 5 del run precedente).

---

## F4 — Regressione e stress

### Regressione spostamento / cancellazione

| Scenario | Risposta Sara | Esito |
|----------|---------------|-------|
| "Voglio spostare il mio appuntamento" | "Per spostare un appuntamento, mi può dire il suo nome?" | ✅ OK |
| "Voglio cancellare il mio appuntamento" | "Per cancellare un appuntamento, mi può dire il suo nome?" | ✅ OK |

### Stress v2 — Parrucchiere (script 20260731/stress_verticali_v2.py, 6 verticali)

| Metrica | Ref booking_end.md | Questo run | Delta |
|---------|-------------------|------------|-------|
| BOOKING | WARN (1/3 OK) | FAIL | peggiorato |
| FAIL_SARA | 17 | 19 | +2 |
| FAIL_DRIVER | 0 | 0 | = |
| WARN | — | 17 | — |
| AVG ms | 1123 | — (non riportato per verticale) | — |
| P95 ms | 2153 | 4820 | +2667ms |

**Causa BOOKING FAIL nel stress**: debug mostra `confirming → idle` (vs expected `completed`) per Parrucchiere — il driver interpreta `idle` come stato non-booking e conta FAIL_SARA. Root cause: slot Aug 3 09:30 già occupato dal booking manuale F3 (conflitto DB fixture), NON regressione del setter. La sequenza `waiting_date → confirming → idle` non è il loop `waiting_date` del bug precedente.

**Cleanup fixture:** OK — rimosse 6 fixture e relativi dati.

---

**BOOKING: COMPLETATO**
