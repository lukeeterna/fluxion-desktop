# VERDETTO A3 — SILENZIO (idle-timeout FASE 3.0) 🟢 VERDE

**Call**: `20260711-195320` · harness UAC loopback (porte alte -f, trunk NON toccato)
**Scenario**: chiamante tace dopo il greeting → attesa reprompt → attesa hangup timeout-silenzio → call TERMINA (zero appese).
**Config**: `-echo 0` (OFF) · `inject_at_ms=999999` (nessun beep) · rx_frames=2983 · rx_rms_max=3851.

## Catena di prova (harness_timeline.md + sara3003_window.log)

| Fase | Finestra | Evidenza |
|------|----------|----------|
| Greeting Sara | t=1–9s | rx_rms 3308→894 (TX Sara udibile lato harness) |
| Silenzio chiamante #1 | t=10–32s | rx_rms=0 continuo |
| **Reprompt** | t=33–34s (rx_rms 3378/3758) | log `19:53:51 IDLE: 22s di silenzio chiamante → reprompt` → `19:53:52 canned TTS in coda TX: 'Pronto, è ancora in linea?'` (TTFB 531ms) |
| Silenzio chiamante #2 | t=35–53s | rx_rms=0 continuo |
| **Congedo + hangup** | t=54–59s (rx_rms 3440/3365) | log `19:54:13 HANGUP timeout-silenzio: chiamante muto 18s dopo il reprompt` |
| **CALL_END** | — | log `19:54:20 HANGUP ricevuto da Python` → `CALL_END emesso` → call TERMINA pulita |

## Verdetto
- **IDLE_REPROMPT_S=22s** rispettato: greeting finito ~t=9 → reprompt a ~t=33 (Δ≈24s, entro tolleranza VAD).
- **IDLE_HANGUP_S=18s** rispettato: reprompt a ~t=33 → hangup a ~t=54 (Δ≈18–21s).
- **UN solo reprompt** (non ripetuto) + hangup legittimo su silenzio prolungato: coerente con FSM-HANGUP GUARD «Sara non riaggancia mai per prima, salvo silenzio prolungato».
- Call chiusa pulita (CALL_END), **zero chiamate appese** (difetto originario del loop RX su silenzio totale — risolto FASE 3.0).

**Esito**: 🟢 VERDE. Ultimo scenario di GATE A3. A3 COMPLETO = {D1 barge-in, D2 eco, D3 filler+no-hangup, SILENZIO} tutti 🟢.
