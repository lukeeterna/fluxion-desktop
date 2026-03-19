# FLUXION — Handoff Sessione 94 → 95 (2026-03-19)

## CTO MANDATE — NON NEGOZIABILE
> **"SARA DEVE LAVORARE SOLO CON DATI REALI DEL DB. Registrare clienti, riconoscerli, prenotare solo con servizi/operatori/slot REALI. Waitlist con VIP priority. Conferma + Reminder WA OBBLIGATORI. ZERO improvvisazione."**

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
Branch: master | HEAD: 3552c53 (pushato)
Uncommitted: nessuno
type-check: 0 errori
```

---

## COMPLETATO SESSIONE 94

### Nessun commit (sessione di analisi e test)

### Attività completate
1. **Landing page redeployata** su Cloudflare Pages — https://fluxion-landing.pages.dev — tutte le pagine 200 OK
2. **Test VAD live con microfono su iMac** — primo test REALE con voce umana
3. **Tauri dev avviato su iMac** via SSH (`bash -l` per cargo env)
4. **Conversazione live completa analizzata** — 13 turni, booking flow end-to-end

### AUDIT LIVE SARA — Bug Critici Scoperti (S94)

**Primo test con voce umana reale. Risultato: Sara NON è pronta per distribuzione.**

#### Conversazione registrata (13 turni):
| # | Utente (STT) | Sara | Bug |
|---|---|---|---|
| 1 | "mi chiamo Mario e vorrei prenotare un taglio" | "Piacere Mario! Mi dice il cognome?" | ✅ OK |
| 2 | "Frazzini" | "Non la trovo... Mi dà un numero di telefono?" | ✅ OK |
| 3 | "Un attimo solo, glielo do subito" | "Certo, mi dica." | ✅ OK |
| 4 | "331 49 29" (incompleto) | "Mi ripete il numero?" | ✅ OK |
| 5 | "331 49 28 901" | "Ho capito 3314928901, è corretto?" | ✅ OK |
| 6 | "Esatto, è corretto" | "Benvenuto Mario Frazzini!" | ✅ OK |
| 7 | "taglio + barba + tinta barba" | "Bene, Taglio e Colore e Barba! Per quale giorno?" | ✅ OK |
| 8 | "il colore alla barba è chiaro?" | "Per quale giorno?" | ⚠️ Non capisce la correzione |
| 9 | "domani dopo le 17" | "con **Cara o Ascoltami o Mario**" | 🔴 **P0**: operatori fantasma |
| 10 | "chi sono cara Ascoltami e Mario?" | Cancella il booking | 🔴 **P0**: cancellazione involontaria |
| 11-13 | Varie | Booking già cancellato | — |

#### 5 Bug P0 identificati:

**BUG-1: Operatori fantasma** — Entity extractor prende parole dalla conversazione ("Cara, che bella voce! Ascoltami") come nomi operatori. ZERO validazione contro DB.

**BUG-2: Cancellazione involontaria** — In stato `confirming`, qualsiasi frase non riconosciuta cancella il booking. Una domanda ("chi sono?") non deve cancellare.

**BUG-3: Servizi hardcodati** — FSM riconosce solo 5 servizi fissi (taglio, piega, colore, barba, trattamento). Servizi custom dell'attività ignorati.

**BUG-4: Operatori senza fallback SQLite** — Se HTTP Bridge offline → lista vuota. NESSUN fallback SQLite per operatori.

**BUG-5: Waitlist senza fallback SQLite + VIP ignorato** — Solo via HTTP Bridge. Priorità VIP mai usata (sempre "normale").

#### Problemi aggiuntivi:
- **LLM NLU timeout**: 15 timeout su 13 turni (Groq+Cerebras+OpenRouter)
- **OpenRouter**: collegato ma 3x empty response, 2x timeout 3s → inutile
- **STT allucinazioni**: Whisper inventa frasi su rumore ambientale ("Il nostro corso gratuito è www.mesmerism.info")
- **Turn troppo lunghi**: VAD cattura 6-12s per frasi di 2-5 parole

---

## 🔴 DA FARE S95 — PRIORITÀ ASSOLUTA: SARA DB-GROUNDED

### PROBLEMA FONDAMENTALE
Sara improvvisa entità invece di lavorare SOLO con dati reali del DB. Fix strutturale, non patch.

### Fix strutturale richiesto (in ordine):

#### 1. Servizi dinamici dal DB (P0)
- All'avvio pipeline: `SELECT nome, sinonimi FROM servizi WHERE attivo=1`
- Costruire mapping sinonimi dinamico (sostituisce `DEFAULT_SERVICES` hardcodato)
- FSM riconosce SOLO servizi presenti nel DB dell'attività
- **File**: `booking_state_machine.py:293-309`, `orchestrator.py:2093`

#### 2. Operatori dal DB con fallback SQLite (P0)
- Aggiungere `_search_operators_sqlite_fallback()` come per clienti
- `SELECT id, nome, cognome FROM operatori WHERE attivo=1`
- Entity extractor valida nomi operatore SOLO contro lista DB
- MAI prendere nomi operatore dal testo della conversazione
- **File**: `orchestrator.py:2992-3004`

#### 3. Cancellazione protetta in stato confirming (P0)
- In stato `confirming`: SOLO "no", "cancella", "annulla" cancellano
- Qualsiasi altra frase → chiedere chiarimento, NON cancellare
- **File**: `booking_state_machine.py` handler stato confirming

#### 4. Waitlist con fallback SQLite + VIP priority (P1)
- `INSERT INTO waitlist` diretto se Bridge offline
- Leggere punteggio VIP dal cliente → passare a waitlist
- **File**: `orchestrator.py:3087-3111`

#### 5. Orari apertura dal DB (P1)
- Alternative slot: leggere orari reali, non 9-18 hardcodato
- **File**: `orchestrator.py:2884-2990`

#### 6. BARGE-IN — Interruzione elegante (P0)
- Se VAD rileva `start_of_speech` durante TTS (`is_tts_playing=True`), Sara FERMA il TTS
- Risponde con copy elegante: "Mi scusi, la ascolto..." / "Prego, mi dica." / "Scusi, non ho capito bene, può ripetere?"
- **Struttura esistente**: `vad_http_handler.py` ha `tts_suppressed` + `start_of_speech` event
- **Manca**: frontend ferma playback TTS + invia turno interrotto → Sara risponde con cortesia
- **File**: `vad_http_handler.py`, frontend `VoiceAgent.tsx` o equivalente

#### 7. FSM BACKTRACKING — Correzioni cliente (P0)
- Sara deve poter TORNARE INDIETRO negli stati quando il cliente corregge
- Es: "Taglio e Colore" → "No, voglio tingere la barba" → torna a `waiting_service` → verifica DB
- Es: "venerdì alle 17" → "No, meglio sabato" → torna a `waiting_date`
- Implementare `_handle_correction()`: rileva "no, volevo...", "non ho detto...", "intendevo..."
- Ogni stato FSM tiene `previous_state` per backtrack
- Dopo backtrack: SEMPRE riverificare l'entità corretta nel DB
- **File**: `booking_state_machine.py` — tutti gli handler di stato

#### 8. COPY ELEGANTE — Pool di varianti (P1)
- Tutte le risposte di Sara: cortesi, professionali, mai robotiche
- Pool di varianti per ogni risposta (non sempre la stessa frase)
- Es: "Mi ripete il numero?" → "Potrebbe ripetermi il numero per cortesia?" / "Scusi, me lo ridice?"
- **File**: `booking_state_machine.py` — tutti i `return` con testo

#### 9. STT anti-allucinazione (P1)
- Scartare trascrizioni < threshold confidenza
- Ignorare frasi senza senso in contesto booking (URL, frasi in altre lingue)
- **File**: `orchestrator.py` dove riceve STT result

### Requisiti CTO per Sara (NON NEGOZIABILI):
- ✅ Registra clienti (nome, cognome, telefono)
- ✅ Riconosce clienti (soprannome, data nascita)
- 🔴 Prende prenotazioni SOLO con dati DB reali (servizi, operatori, slot)
- 🔴 Waitlist se slot occupato (priorità VIP)
- 🔴 Barge-in: se il cliente interrompe, Sara si ferma con cortesia
- 🔴 Backtracking: se il cliente corregge, Sara torna indietro e riverifica
- ✅ Contatto clienti via WhatsApp
- ✅ Conferma prenotazione WA
- ✅ Reminder -24h/-1h

---

## DIRETTIVE CTO (NON NEGOZIABILI)

1. **SARA = SOLO DATI DB** — zero improvvisazione, zero entità inventate
2. **SEMPRE skill code reviewer** dopo ogni implementazione significativa
3. **Code signing GRATIS** — ad-hoc macOS + MSI unsigned Windows
4. **ZERO COSTI** per licensing, protezione, infra
5. **VoIP EHIWEB** — ~€2/mese, BLOCCATO attesa numero
6. **SEMPRE 1 nicchia** — una PMI = un'attività
7. **Deep research CoVe 2026** — SEMPRE subagenti PRIMA di implementare

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 95. PRIORITÀ UNICA: Sara enterprise-grade DB-grounded.
9 fix da S94: servizi dal DB, operatori dal DB, cancellazione protetta, waitlist VIP,
barge-in (interruzione elegante), FSM backtracking (correzioni cliente),
copy elegante (pool varianti), STT anti-allucinazione, orari apertura dal DB.
Sara deve lavorare SOLO con dati reali. Se il cliente corregge, Sara torna indietro.
Se il cliente interrompe, Sara si ferma con cortesia.
DIRETTIVE: SEMPRE code reviewer, ZERO improvvisazione Sara, SOLO dati DB.
```
