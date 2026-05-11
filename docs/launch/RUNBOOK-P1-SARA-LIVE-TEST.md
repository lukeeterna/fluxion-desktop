# RUNBOOK P1 — Sara Live Audio Test (founder iMac fisico)

> **Tempo stimato**: 45-60 min
> **Prerequisito hardware**: founder fisicamente davanti a iMac (microfono integrato + speakers/cuffie)
> **Owner**: Gianluca Di Stasi
> **Esito atteso**: PASS su tutti i 5 scenari → P0 launch blocker rimosso
> **Riferimento**: `.claude/rules/voice-agent-details.md` § Test Live Scenari

---

## ⚡ Quick Start (TL;DR per founder)

Sei fisicamente all'iMac. Apri Terminal e copia-incolla in ordine:

```bash
# 1. Pre-flight: pipeline deve essere ATTIVA
curl -s http://127.0.0.1:3002/health | python3 -m json.tool
# Atteso: {"status": "ok", "service": "FLUXION Voice Agent Enterprise", "version": "2.1.0", ...}

# 2. Smoke test text-mode (5 scenari automatici via HTTP, ~30 sec)
cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
python3 t1_live_test.py
# Atteso: 5/5 ✅ o report puntuale di quali falliscono

# 3. Test LIVE AUDIO (microfono reale, ~30 min, 5 scenari)
source venv/bin/activate
python3 sara_mic.py
# Segui la guida scenari sotto
```

---

## 🚦 Step 0 — Pre-flight checklist

Prima di iniziare, verifica TUTTO da Terminal iMac (NO SSH, fisicamente sull'iMac):

| Check | Comando | Atteso |
|-------|---------|--------|
| Pipeline up | `curl -s http://127.0.0.1:3002/health \| jq .status` | `"ok"` |
| Microfono iMac riconosciuto | `python3 -c "import sounddevice; print(sounddevice.query_devices())"` | almeno 1 input device |
| Output audio funzionante | `say -v Alice "test microfono"` | senti voce italiana |
| Disco libero >1GB | `df -h /Volumes/MacSSD\ -\ Dati/` | Avail >1G |
| Permessi mic Terminal | System Preferences → Security → Microphone → Terminal ✅ | ticked |

**Se uno check fallisce STOP**. Errori comuni:

- Pipeline down → `ssh imac` non serve (sei già lì): `cd "/Volumes/MacSSD - Dati/fluxion/voice-agent" && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &` poi `tail -f /tmp/voice-pipeline.log` finché vedi `Running on http://127.0.0.1:3002`.
- Permesso mic mancante → System Preferences → Security & Privacy → Microphone → spunta `Terminal.app`. **Riavvia Terminal** dopo aver dato il permesso.

---

## 🧪 Step 1 — Smoke test text-mode (5 min)

Questo NON usa il microfono. Manda input testuale via HTTP e verifica che FSM + RAG + intent classifier rispondano correttamente. Baseline prima di passare al test audio.

```bash
cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
python3 t1_live_test.py 2>&1 | tee /tmp/sara-text-test-$(date +%Y%m%d-%H%M).log
```

**Esito atteso**: tutti i 5 scenari `✅`. Se ne fallisce 1+ NON proseguire al test live: il bug è a livello pipeline, non audio. Apri il log, identifica scenario fallito, salvalo per analisi e fermati qui.

---

## 🎤 Step 2 — Test LIVE AUDIO 5 scenari

```bash
cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
source venv/bin/activate
python3 sara_mic.py
```

`sara_mic.py` apre un loop:
- Premi `INVIO` → inizia registrazione
- Parla naturale (3-8 sec)
- Premi `INVIO` di nuovo → Sara processa STT → risponde testo + audio playback
- Comando speciale `reset` → nuova sessione
- Comando speciale `quit` → esci

**Apri un secondo Terminal in parallelo** per monitorare log pipeline:
```bash
tail -f /tmp/voice-pipeline.log
```
Servirà per ispezionare `layer=`, `intent=`, `fsm_state=`, `latency_ms`.

### 📋 Scenario 1 — "Gino vs Gigio" (disambiguazione fonetica)

**Obiettivo**: verificare Levenshtein ≥70% disambigua due nomi simili nel DB.

**Setup**: in `sara_mic.py` digita `reset` + INVIO. Pipeline torna a IDLE.

**Copione** (parla naturale, 1 frase per INVIO):

| # | Tu pronunci | Sara dovrebbe rispondere (gist) | Verifica |
|---|-------------|----------------------------------|----------|
| 1 | "Buongiorno" | saluto + offerta aiuto | `intent=greeting layer=L1_exact` |
| 2 | "Vorrei prenotare un taglio" | "Per quando?" o slot pickup | `fsm_state=COLLECTING_*` |
| 3 | "Domani alle dieci" | offerta slot domani 10:00 + chiede nome | `fsm_state=ASKING_NAME` |
| 4 | "Sono Gigio" | match cliente esistente Gigio (se in DB) o disambiguation tra Gino/Gigio | `intent=client_name` + nel log `disambiguation_handler` |

**Criterio PASS**:
- STT trascrive "Gigio" (NON "Gino", NON "Ggi", NON "Ugio")
- Sara distingue tra eventuale "Gino" e "Gigio" via Levenshtein
- Latency end-to-end <2500ms (tollerato ora, target <800ms v1.1)

**Criterio FAIL**:
- STT trascrive "Gino" quando hai detto "Gigio" → STT bias
- Sara fonde i due nomi → disambiguation handler rotto
- Crash pipeline → bug critico

**Output da catturare**: screenshot Terminal con output Sara + 4 righe log corrispondenti.

---

### 📋 Scenario 2 — "Soprannome VIP" (Gigi → Gigio canonical)

**Obiettivo**: nickname "Gigi" deve essere mappato a cliente canonico "Gigio" se presente in DB.

**Setup**: `reset` + INVIO.

**Copione**:

| # | Tu pronunci | Sara atteso | Verifica |
|---|-------------|-------------|----------|
| 1 | "Ciao sono Gigi" | conferma "Gigio?" o procede come Gigio | log `nickname_resolver` o entity con `canonical_name=Gigio` |
| 2 | "Sì, sono io" | conferma identità + chiede servizio | `fsm_state=ASKING_SERVICE` |

**PASS**: Gigi → Gigio mapping eseguito (verifica DB query in log).
**FAIL**: Sara crea un NUOVO cliente "Gigi" duplicando Gigio.

---

### 📋 Scenario 3 — "Chiusura Graceful"

**Obiettivo**: post-prenotazione, "Grazie, arrivederci" deve transire a `ASKING_CLOSE_CONFIRMATION` e inviare WhatsApp.

**Setup**: `reset` + completare booking fittizio (nome + servizio + data + ora + conferma).

**Copione**:

| # | Tu pronunci | Sara atteso |
|---|-------------|-------------|
| 1 | "Buongiorno" | saluto |
| 2 | "Vorrei un taglio domani alle 15" | conferma slot |
| 3 | "Sono Marco Rossi" | match cliente o registrazione |
| 4 | "Sì confermo" | conferma prenotazione + invio WA |
| 5 | "Grazie arrivederci" | `ASKING_CLOSE_CONFIRMATION` poi saluto finale |

**PASS**: nel log vedi:
1. `fsm_state=ASKING_CLOSE_CONFIRMATION`
2. WhatsApp send attempt (anche se mock/log only — verifica intent)
3. Sessione termina puliti

**FAIL**: Sara dopo "Grazie arrivederci" prova a fare nuova prenotazione (FSM non chiude) → bug FSM transition.

---

### 📋 Scenario 4 — "Flusso Perfetto" (E2E nuovo cliente)

**Obiettivo**: end-to-end completo nuovo cliente → booking → WA → chiusura → analytics record.

**Setup**: `reset`. Usa nome inventato NON esistente in DB (es. "Federico Marrone").

**Copione**:

| # | Tu pronunci | Atteso |
|---|-------------|--------|
| 1 | "Buongiorno" | saluto |
| 2 | "Sono un nuovo cliente" | onboarding flow |
| 3 | "Mi chiamo Federico Marrone" | registrazione |
| 4 | "Vorrei prenotare un trattamento viso" | chiede data/ora |
| 5 | "Venerdì pomeriggio" | offre slot specifici |
| 6 | "Alle 16 va bene" | conferma slot |
| 7 | "Sì confermo" | invio WA + saluto |
| 8 | "Grazie" | chiusura graceful |

**PASS**: dopo il test, verifica DB:
```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "SELECT name, surname, phone FROM clients WHERE name='Federico' ORDER BY id DESC LIMIT 1;"
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/analytics.db" \
  "SELECT session_id, total_turns, final_state, completed FROM sessions ORDER BY started_at DESC LIMIT 1;"
```
Atteso:
- Cliente `Federico Marrone` in `clients`
- Session in `analytics.db` con `completed=1` e `final_state` tra `DONE`/`CLOSED`

**FAIL**: cliente non creato OR session.completed=0 OR final_state non-terminale.

---

### 📋 Scenario 5 — "WAITLIST"

**Obiettivo**: slot occupato → Sara propone waitlist → utente accetta → record WAITLIST_SAVED.

**Setup**: `reset`. Prima crea uno slot DA OCCUPARE manualmente:
```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "INSERT INTO appointments (cliente_id, servizio, data, ora, status) VALUES (1, 'taglio', date('now','+1 day'), '11:00', 'confirmed');"
```

**Copione**:

| # | Tu pronunci | Atteso |
|---|-------------|--------|
| 1 | "Vorrei un taglio domani alle 11" | "Slot occupato, vuoi lista attesa?" → `PROPOSING_WAITLIST` |
| 2 | "Sì, mettimi in lista" | conferma waitlist → `WAITLIST_SAVED` |

**PASS**: log mostra entrambe le transizioni FSM. DB query:
```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "SELECT * FROM waitlist ORDER BY id DESC LIMIT 1;"
```
Atteso: nuova riga waitlist con data domani + ora 11:00.

**FAIL**: Sara propone slot diverso INVECE di waitlist (FSM non rileva conflict) OR transizione `PROPOSING_WAITLIST` salta.

**Cleanup post-test**:
```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "DELETE FROM appointments WHERE cliente_id=1 AND ora='11:00' AND data=date('now','+1 day');"
```

---

## 📊 Step 3 — Reporting esito

Crea un file di report con risultati:

```bash
cat > /tmp/sara-live-test-$(date +%Y%m%d).md <<EOF
# Sara Live Test Report — $(date +%Y-%m-%d)

## Pre-flight
- Pipeline health: PASS/FAIL
- Microfono permesso: PASS/FAIL

## Smoke text-mode (t1_live_test.py)
- Scenario 1 greeting: PASS/FAIL
- Scenario 2 Laura Bianchi: PASS/FAIL
- Scenario 3 Sì/Cognome: PASS/FAIL
- ... (vedi output completo /tmp/sara-text-test-*.log)

## Live audio (5 scenari)
- S1 Gino vs Gigio: PASS/FAIL — note: ...
- S2 Soprannome VIP: PASS/FAIL — note: ...
- S3 Chiusura Graceful: PASS/FAIL — note: ...
- S4 Flusso Perfetto: PASS/FAIL — note: ... (DB check OK/KO)
- S5 WAITLIST: PASS/FAIL — note: ... (DB check OK/KO)

## Latency osservata
- Min: XXX ms
- Avg: XXX ms
- Max: XXX ms
- SLO <800ms: PASS/FAIL (target v1.1)

## Audio quality (soggettivo founder)
- TTS intelligibilità (1-10): X
- STT accuracy parole italiane: X/10
- TTS naturalezza intonazione (1-10): X
EOF
```

---

## 🚨 Troubleshooting

| Problema | Causa probabile | Fix |
|----------|----------------|-----|
| `sounddevice.PortAudioError: Error querying device` | Mic permission Terminal | Sys Pref → Security → Mic → tick Terminal → riavvia Terminal |
| STT trascrive parole sbagliate frequenti | Microfono troppo distante o rumore ambiente | avvicinati ≤30cm + ambiente silenzioso |
| Latency >5000ms | Groq API rate limit o rete lenta | check `curl https://api.groq.com/openai/v1/models` |
| `connection refused 127.0.0.1:3002` | Pipeline killed | restart con comando in Step 0 |
| TTS audio non si sente | Output device sbagliato o `afplay` rotto | `say -v Alice "test"` per verificare; cambia output device Sys Pref → Sound |
| Crash pipeline durante test | Bug Python | salva `/tmp/voice-pipeline.log` e apri ticket subito |

---

## ✅ Definizione di PASS

Test P0 launch blocker è considerato CHIUSO quando:

- [ ] Pre-flight all-green
- [ ] Smoke text-mode 5/5 PASS
- [ ] Live audio 5/5 PASS (scenari 1-5)
- [ ] DB check Scenari 4+5 confermano persistenza
- [ ] Report `/tmp/sara-live-test-YYYYMMDD.md` compilato

**Quando tutto PASS**: commit report in `docs/launch/sara-live-test-reports/` e marcare in `HANDOFF.md` come `P0 Sara test live ✅ CHIUSO`.

---

## ⏭️ Next session prompt post-test

```
Sara live test PASS 5/5 — report in docs/launch/sara-live-test-reports/YYYYMMDD.md.
Rimosso P0 launch blocker test Sara. Aggiornare ROADMAP_REMAINING.md +
HANDOFF.md + PRE-LAUNCH-AUDIT.md (categoria Functional E2E → PASS).
Prossimo P0 launch blocker rimanente: Win MSI (RUNBOOK-P2-WIN-MSI-BUILD.md).
```
