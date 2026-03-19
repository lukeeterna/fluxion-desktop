# FLUXION — Handoff Sessione 95 → 96 (2026-03-19)

## CTO MANDATE — NON NEGOZIABILE
> **"Sara deve essere un sistema di prenotazioni PROFESSIONALE world-class. Le feature indicate sono il MINIMO — DEEP RESEARCH CoVe 2026 per trovare TUTTO ciò che serve e implementarlo. ZERO improvvisazione, SOLO dati DB."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | **iMac DISPONIBILE**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22
**Tauri dev su iMac**: `bash -l -c 'cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev'`

---

## STATO GIT
```
Branch: master | HEAD: e9d6a83 (pushato: NO — da pushare)
Uncommitted: HANDOFF.md, ROADMAP_REMAINING.md (da committare)
type-check: 0 errori
Test: 1949 PASS / 3 FAIL pre-esistenti / 46 skipped
```

---

## COMPLETATO SESSIONE 95

### Commit e9d6a83 — F19 Sara DB-Grounded (9 fix P0/P1)

| # | Fix | Descrizione | File |
|---|-----|-------------|------|
| 1 | Servizi dal DB | FSM usa SOLO servizi reali da `SELECT FROM servizi WHERE attivo=1` | orchestrator.py, bsm.py |
| 2 | Operatori dal DB + SQLite fallback | `_search_operators_sqlite_fallback()` + cache nomi validi, entity extractor valida contro DB | orchestrator.py, bsm.py |
| 3 | Cancellazione protetta | Solo "annulla/cancella/non voglio/no" cancellano in CONFIRMING — domande NON cancellano | bsm.py |
| 4 | FSM Backtracking | `_check_backtracking()`: "no, volevo X" → torna allo stato giusto e riverifica DB | bsm.py |
| 5 | Waitlist SQLite + VIP | `_add_to_waitlist_sqlite_fallback()` + `_get_client_vip_priority()` da `clienti.is_vip` | orchestrator.py |
| 6 | Orari dal DB | Slot alternativi usano orari reali da impostazioni (non 9-18 hardcodato) | orchestrator.py |
| 7 | Copy elegante | Pool varianti risposte `_RESPONSE_VARIANTS` + `_vary()` randomizzato | bsm.py |
| 8 | STT anti-allucinazione | `_is_stt_hallucination()` filtra URL, pattern Whisper, parole ripetute | orchestrator.py |
| 9 | Barge-in backend | VAD segnala `barge_in` event quando utente parla durante TTS | vad_http_handler.py |

---

## 🔴 DA FARE S96

### PRIORITÀ 1: Deep Research + Feature mancanti Sara
Il CTO vuole un sistema di prenotazioni PROFESSIONALE. Le 9 fix sopra sono il minimo.
Servono deep research CoVe 2026 per identificare tutte le feature world-class mancanti.

**Possibili aree da ricercare:**
- Multi-appuntamento nella stessa sessione (es. "taglio + colore" con slot combinato)
- Conferma SMS/Email oltre WhatsApp
- Gestione ricorrenze ("stessa ora ogni 4 settimane")
- Gestione no-show + penalità
- Preferenze cliente memorizzate ("sempre con Marco, sempre taglio corto")
- Suggerimenti intelligenti basati su storico
- Gestione pausa pranzo / intervalli operatore
- Servizi con prerequisiti (es. patch test prima di tinta)
- Buffer tempo tra appuntamenti per pulizia/preparazione

### PRIORITÀ 2: Test live voce reale su iMac
I 9 fix devono essere testati con voce reale su iMac per verificare che:
1. Sara propone SOLO servizi dal DB dell'attività
2. Sara propone SOLO operatori dal DB
3. Domanda in CONFIRMING NON cancella il booking
4. Correzione "no, meglio X" funziona
5. Barge-in segnala l'evento al frontend

### PRIORITÀ 3: Push + Sync iMac
```bash
git push origin master
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
# Riavvio pipeline
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

---

## DIRETTIVE CTO (NON NEGOZIABILI)

1. **SARA = SISTEMA PRENOTAZIONI PROFESSIONALE** — deep research per TUTTO, non solo fix indicati
2. **SARA = SOLO DATI DB** — zero improvvisazione, zero entità inventate
3. **SEMPRE skill code reviewer** dopo ogni implementazione significativa
4. **ZERO COSTI** per licensing, protezione, infra
5. **SEMPRE 1 nicchia** — una PMI = un'attività
6. **Deep research CoVe 2026** — SEMPRE subagenti PRIMA di implementare

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 96. PRIORITÀ: Deep research CoVe 2026 per sistema prenotazioni Sara world-class.
Le 9 fix base sono fatte (S95). Ora ricerca TUTTE le feature che mancano per battere Fresha/Mindbody.
Push su iMac, test live voce reale, implementa feature mancanti.
DIRETTIVE: deep research PRIMA, SOLO dati DB, ZERO improvvisazione.
```
