# FLUXION — Handoff Sessione 69 → 70 (2026-03-13)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: d1ec1b7
fix(fsm): lookbehind in pattern 'è X' per evitare falso positivo su 'De X'
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1477 PASS / 0 FAIL ✅
F07 license server E2E: 22/22 PASS ✅
F08 t1_live_test: 11/11 PASS ✅ (sessione 69)
```

---

## COMPLETATO SESSIONE 69

### 1. F08 — Test Live Sara T1-T5 ✅ DONE

Eseguiti su iMac via HTTP API (127.0.0.1:3002) — Voice Agent v2.1.0

| Scenario | Risultato | Dettaglio |
|----------|-----------|-----------|
| T1: Gino vs Gigio | ✅ PASS | `fsm=disambiguating_name`, suggerisce "Gino di Nanni" |
| T2: Soprannome VIP (Gigi) | ✅ PASS | Riconosciuto come nickname → `waiting_surname` |
| T3: Chiusura Graceful | ✅ PASS | L1_exact, "arrivederci" in risposta, lat=1.7ms |
| T4: Flusso Perfetto | ✅ PASS | Nuovo cliente end-to-end → `confirming_phone` |
| T5: Waitlist | ✅ PASS | Slot handling → registering flow attivato |

**Full t1_live_test.py (11 scenari)**: 11/11 PASS ✅

### 2. Rate Limit Fix ✅ (main.py)
- VAD invia 600 req/min da 127.0.0.1 → saturava limit 100/min
- Fix: middleware esclude 127.0.0.1/::1 da rate limiting
- Errore "Too Many Requests" nella UI durante mic normale → RISOLTO

### 3. STT Name Corrector ✅ (name_corrector.py)
- Layer 1: Whisper prompt injection (top-40 clienti nel prompt)
- Layer 2: Jaro-Winkler ≥ 0.85 phonetic fast-path
- "episcopo" vs "piscopo" = 0.958 → corretto automaticamente
- Integrato in orchestrator.py + stt.py + groq_client.py
- Dipendenza: `jellyfish>=1.0.0` aggiunta a requirements.txt

### 4. FSM Cognomi Nobili (De Piscopo, De Marinis) — 4 Bug Fix ✅

**Bug ROOT CAUSES identificati e risolti:**

| Bug | File | Fix | Commit |
|-----|------|-----|--------|
| new_client_detected L0b hardcodava risposta generica | orchestrator.py | Estratto nome con finditer prima della risposta | 7cd056f |
| re.search ferma al 1° match ("sono cliente" → NON_NAMES) | booking_state_machine.py | Cambiato a re.finditer | ce8e628 |
| bare "sono" → "sono vostro" → falso positivo "Vostro" | entrambi | Rimosso "sono" dalle alternative regex | 178510e |
| r"(?:è\|e)\s+" con IGNORECASE matcha "e" in "De Rossi" | booking_state_machine.py (×2) | (?<!\w) lookbehind | d1ec1b7 |

**Risultato test regressione (su iMac)**:
```
T1 De Piscopo:  registering_phone — Non la trovo tra i nostri clienti... ✅ (no loop)
T2 De Marinis:  registering_phone — Non la trovo tra i nostri clienti... ✅ (no loop)
T3 è Bianchi:   registering_phone — Grazie Luigi Bianchi! ✅ (pattern ancora funziona)
T4 Tullio:      registering_surname — Benvenuto Tullio! Mi può dare il cognome? ✅
```

---

## PENDING (non implementato in S69)

### VAD Open-Mic / Continuous Listening
- Dopo risposta Sara, microfono deve riattivarsi automaticamente (come telefonata reale)
- Priorità: P1 — necessario per EHIWEB VoIP integration
- Research: CoVe 2026 già pianificato ma non eseguito

---

## F15 VoIP — IN ATTESA CREDENZIALI

✅ Architettura implementata | ⏳ Credenziali EHIWEB SIP ancora in arrivo
- `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER` → da inserire in config.env iMac voice-agent

---

## PROSSIMA SESSIONE S70

> **Priorità**: ROADMAP_REMAINING.md — prossima fase

### Da fare S70:
1. `ROADMAP_REMAINING.md` → verificare cosa rimane
2. Se credenziali EHIWEB arrivate → F15 test SIP end-to-end
3. VAD Open-Mic (P1) → CoVe 2026 research + implementazione
4. Candidati: Landing screenshot F16 | altri da roadmap

### Promemoria tecnici:
- **Voice pipeline** porta 3002 bound a `127.0.0.1` — accessibile solo da iMac
- **License server** gestito da LaunchAgent (avvio automatico boot)
- **Cloudflare tunnel** gestito da LaunchAgent `com.fluxion.cloudflared`
- **t1_live_test.py**: BASE corretto è `http://127.0.0.1:3002` (non 192.168.1.2 — hardening F14)
