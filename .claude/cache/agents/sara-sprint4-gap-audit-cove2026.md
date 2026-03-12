# Sara Sprint 4 — Gap Audit CoVe 2026 (S62, 2026-03-12)

## Metodo
Analisi sistematica di: booking_state_machine.py (3658 righe), orchestrator.py (3251 righe), entity_extractor.py, availability_checker.py, 32 file test

## GAP P0 — CRITICI (da fare Sprint 4)

### GAP-P0-1: Phone validation incompleta
- **File**: entity_extractor.py `extract_phone()`
- **Bug**: nessuna validazione lunghezza min/max → accetta "333" come numero valido
- **Impatto**: booking salvato con numero malformato → no SMS/WA reminder → no-show +30%
- **Fix**: validazione `len(normalized) >= 10 and len(normalized) <= 13`, rifiuta fissi (prefix 0)
- **Test mancanti**: numeri corti, fissi, overflow, non-italiani

### GAP-P0-2: Email validation RFC 5322
- **File**: entity_extractor.py `extract_email()`
- **Bug**: regex semplicistica, accetta "test..test@x.c" (TLD 1 char), no lowercase normalization
- **Impatto**: email malformata → delivery failure notifiche
- **Fix**: RFC 5322 regex + lowercase normalization + consecutive dots check
- **Test mancanti**: consecutive dots, short TLD, uppercase, multiple @ signs

### GAP-P0-3: Festività mai caricate da DB
- **File**: orchestrator.py `start_session()`, availability_checker.py
- **Bug**: `holidays: List[str]` definita ma orchestrator NON popola da DB → booking su giorni chiusi
- **Impatto**: prenotazione confermata il 25 dicembre/1 gennaio → cliente si presenta, azienda chiusa
- **Fix**: load `impostazioni.giorni_festivi` in `start_session()`, passare a availability_checker
- **Test mancanti**: zero test festività

### GAP-P0-4: Festività senza alternative proposte
- **File**: availability_checker.py, orchestrator.py
- **Bug**: quando festivo → "mi dispiace, siamo chiusi" ma NO alternative slot proposte → conversazione muore
- **Impatto**: abbandono booking su giorni festivi (alta probabilità proprio per festività quando cliente ha tempo libero)
- **Fix**: quando festivo → genera 3 date alternative non-festive successive, includi nella risposta
- **Test mancanti**: scenari natale, capodanno, ferragosto, pasqua

## GAP P1 — IMPORTANTI (Sprint 5)

| GAP | Bug | Fix |
|-----|-----|-----|
| GAP-P1-1 | Intl phone formats (0039, varianti spazi) | Normalize tutti prefix → "39XXXXXXXXX" |
| GAP-P1-2 | Email extraction da testo complesso | Prioritize post "email/indirizzo" keyword |
| GAP-P1-3 | `extract_exclude_days()` è STUB (P1-13) | Implementa pattern "non il lunedì", "tranne" |
| GAP-P1-4 | Operator gender preference non estratta | `extract_operator_gender_preference()` nuovo |
| GAP-P1-5 | Cancellation window non validata | Check advance hours da impostazioni |
| GAP-P1-6 | Reschedule senza availability check | Verify slot libero prima di spostare |
| GAP-P1-7 | Waitlist auto-assign: zero logic | APScheduler trigger su cancellazione |
| GAP-P1-8 | Multi-operator selection (List[str]) | `extract_operators()` plural |

## GAP P2 — OTTIMIZZAZIONI (Sprint 6)

| GAP | Descrizione |
|-----|-------------|
| GAP-P2-1 | Greeting fillers "eh allora", "vabbeh" |
| GAP-P2-2 | AM/PM inference da contesto orario |
| GAP-P2-3 | Service synonym timing (ante vertical) |
| GAP-P2-4 | Concurrent sessions DB safety |
| GAP-P2-5 | TTS cache coherency su operator change |
| GAP-P2-6 | FAQ fallback chain documentata |
| GAP-P2-7 | WA booking confirm delay telemetry |
