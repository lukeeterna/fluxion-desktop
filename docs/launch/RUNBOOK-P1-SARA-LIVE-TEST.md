# RUNBOOK P1 — Sara Live VoIP Test (flusso reale Ehiweb/VivaVox SIP)

> **Tempo stimato**: 60-75 min
> **Prerequisito hardware**: founder fisicamente all'iMac + 1 telefono esterno (cellulare proprio o di terzi) per chiamare il DID VoIP
> **Owner**: Gianluca Di Stasi
> **Esito atteso**: PASS su 5 scenari → P0 launch blocker rimosso
> **Riferimento**: `.claude/rules/voice-agent-details.md` § Test Live Scenari + `docs/launch/ONBOARDING-EHIWEB-CLIENTE.md`
>
> ⚠️ **CAMBIO ARCHITETTURALE S202**: Sara è inbound-only via SIP. NON si testa più col microfono iMac (`sara_mic.py` obsoleto per validazione release). Il test simula il flusso reale cliente → DID VoIP → pipeline iMac.

---

## ⚡ Quick Start (TL;DR per founder)

Sei fisicamente all'iMac. Hai a portata di mano un **cellulare esterno** (non lo smartphone collegato all'iMac via Continuity — serve una numerazione PSTN/mobile diversa dal DID). Apri Terminal:

```bash
# 1. Pre-flight: pipeline up + SIP REGISTERED
curl -s http://127.0.0.1:3002/health | python3 -m json.tool
curl -s http://127.0.0.1:3002/api/voice/voip/status | python3 -m json.tool
# Atteso: health.status=ok + voip.sip.registered=true

# 2. Apri log live in secondo Terminal
tail -f /tmp/voice-pipeline.log | grep -E "INVITE|SIP|RTP|intent=|fsm_state=|latency_ms"

# 3. Dal cellulare esterno → componi il DID VivaVox assegnato a Sara
#    (vedi config.env: VOIP_SIP_USER = numero DID, oppure numero VivaVox Free attivato)
#    Sara dovrebbe rispondere entro 2 squilli con saluto vocale.
```

---

## 🚦 Step 0 — Pre-flight (CRITICO)

Prima del test, verifica TUTTO da Terminal iMac. Una sola riga rossa → STOP e fix.

| # | Check | Comando | Atteso |
|---|-------|---------|--------|
| 0.1 | Pipeline up | `curl -s http://127.0.0.1:3002/health \| jq .status` | `"ok"` |
| 0.2 | SIP registered | `curl -s http://127.0.0.1:3002/api/voice/voip/status \| jq .sip.registered` | `true` |
| 0.3 | SIP server raggiungibile | `curl -s http://127.0.0.1:3002/api/voice/voip/status \| jq -r .sip.server` | `sip.vivavox.it` (o server Ehiweb attivo) |
| 0.4 | DID assegnato visibile | `grep VOIP_SIP_USER "/Volumes/MacSSD - Dati/fluxion/voice-agent/config.env"` | numero DID non vuoto |
| 0.5 | NAT/STUN OK | log pipeline contiene `STUN binding ... mapped` | sì |
| 0.6 | Codec G.711 attivo | log contiene `codec=PCMU` o `PCMA` su INVITE | sì |
| 0.7 | RTP ports aperte | `lsof -nP -iUDP -P \| grep python \| awk '{print $9}' \| head` | range 4000-5000 visibile |
| 0.8 | Disco libero | `df -h "/Volumes/MacSSD - Dati"` | Avail >1G |
| 0.9 | Speaker iMac vivo | `say -v Alice "test"` | senti audio (per debug eventuale) |
| 0.10 | Router non blocca UDP | `nc -u -zv sip.vivavox.it 5060` (timeout 3s) | succeeded |

**Cosa fare se ⚠️**:

- **0.1 pipeline down** → riavvio: `ssh imac "kill $(lsof -ti:3002) 2>/dev/null; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &"` poi `tail -f /tmp/voice-pipeline.log` fino a `Running on http://127.0.0.1:3002` + `VoIP service avviato`.
- **0.2 SIP non registrato** → controllare credenziali in `config.env`: `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER`. Se vuoti → VivaVox Free non ancora attivato (vedi `docs/launch/ONBOARDING-EHIWEB-CLIENTE.md` step 1-4). Se popolati → ispezionare log `/tmp/voice-pipeline.log` per stato `401 Unauthorized` (pass errata) o `403 Forbidden` (account sospeso) o `408 Request Timeout` (firewall router blocca UDP 5060).
- **0.5 STUN non binda** → NAT simmetrico router casa. Fix permanente: aprire port-forward UDP 5060 + RTP range 4000-5000 → IP iMac, oppure abilitare `VOIP_TURN_SERVER` (vedi `voip_pjsua2.py` D4). Workaround test singolo: hotspot 4G da cellulare diverso da quello chiamante.
- **0.10 UDP 5060 bloccato** → router casa filtra SIP ALG. Disabilitare `SIP ALG` in router admin (campo spesso chiamato "VoIP passthrough" o "ALG SIP" — sempre da disabilitare per VoIP funzionante).

---

## 📞 Step 1 — Smoke test 1 chiamata (5 min)

Baseline minima: 1 chiamata, 1 saluto, riaggancio. Se questa fallisce, scenari completi non hanno senso.

1. Dal cellulare esterno, componi il DID VoIP assegnato a Sara (es. `+39 0973 xxxxxx`).
2. Atteso: 1-2 squilli → Sara risponde con saluto vocale (esempio: "Buongiorno, sono Sara di [Salone], in cosa posso aiutarla?").
3. Dì: "Buongiorno, è un test."
4. Sara dovrebbe rispondere con qualcosa di sensato (offerta aiuto / chiedi servizio).
5. Riaggancia dal cellulare.
6. Verifica log pipeline secondo Terminal:

```
expected log markers (in ordine):
- "SIP INVITE received from sip:..."
- "Call accepted, audio bridge active"
- "STT transcribed: 'Buongiorno è un test'" (o simile)
- "intent=greeting layer=L1_*"
- "TTS playback queued"
- "Call ended by remote BYE"
```

**PASS smoke**: tutti i 6 marker presenti, audio bidirezionale (tu senti Sara, log mostra trascrizione).
**FAIL smoke**: salta scenari completi, debug puntuale (vedi § Troubleshooting).

---

## 🎬 Step 2 — Test LIVE 5 scenari (45 min)

Ogni scenario = 1 chiamata da cellulare esterno. Dopo ogni chiamata, riaggancia e attendi 5 sec per chiusura sessione pulita.

**Comando reset sessione tra scenari** (in secondo Terminal):

```bash
# Sara FSM si resetta automaticamente su BYE SIP, ma per sicurezza:
curl -X POST http://127.0.0.1:3002/api/voice/reset
```

**Audio quality nota**: codec PSTN G.711 limita banda a 300-3400Hz. STT può degradare vs studio mic. Parla chiaramente, evita ambiente rumoroso lato cellulare, distanza bocca-microfono cellulare ≤10cm.

---

### 📋 Scenario 1 — "Gino vs Gigio" (disambiguazione fonetica)

**Obiettivo**: verificare Levenshtein ≥70% disambigua due nomi simili nel DB.

**Setup DB** (1-tantum, prima del test): assicurati che il DB salone contenga sia Gino che Gigio:

```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "SELECT id, nome, cognome FROM clienti WHERE nome IN ('Gino','Gigio');"
# Se mancano, inseriscili:
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "INSERT OR IGNORE INTO clienti (nome, cognome, telefono) VALUES ('Gino','Rossi','3331111111'),('Gigio','Bianchi','3332222222');"
```

**Copione chiamata**:

| # | Tu dici al telefono | Sara dovrebbe rispondere (gist) | Verifica log |
|---|---------------------|----------------------------------|--------------|
| 1 | (Sara risponde per prima) | saluto + offerta aiuto | `intent=greeting layer=L1_exact` |
| 2 | "Vorrei prenotare un taglio" | "Per quando?" o slot pickup | `fsm_state=COLLECTING_*` |
| 3 | "Domani alle dieci" | offerta slot domani 10:00 + chiede nome | `fsm_state=ASKING_NAME` |
| 4 | "Sono Gigio" | disambiguation tra Gino/Gigio (es. "intende Gigio Bianchi?") | nel log `disambiguation_handler` + `levenshtein_ratio` ≥0.70 |

**Criterio PASS**:
- STT trascrive "Gigio" (NON "Gino", NON "Ggi", NON "Ugio")
- Sara distingue tra "Gino" e "Gigio" via Levenshtein
- Latency turn-end-to-turn-start <2500ms (tollerato; SLO v1.1 <800ms)

**Criterio FAIL**:
- STT confonde "Gigio" con "Gino" sistematicamente → STT bias su banda PSTN (tech debt: fine-tune Whisper su audio G.711)
- Sara fonde i due nomi → disambiguation handler rotto
- Call drop o crash pipeline → bug critico

**Output da catturare**: screenshot Terminal con le 4 righe log corrispondenti + appunto soggettivo qualità audio (1-10).

---

### 📋 Scenario 2 — "Soprannome VIP" (Gigi → Gigio canonical)

**Obiettivo**: nickname "Gigi" deve mappare a cliente canonico "Gigio" se presente in DB.

**Copione chiamata**:

| # | Tu dici al telefono | Sara atteso | Verifica |
|---|---------------------|-------------|----------|
| 1 | (Sara risponde) | saluto | — |
| 2 | "Ciao sono Gigi" | conferma "Gigio?" o procede come Gigio | log `nickname_resolver` o entity con `canonical_name=Gigio` |
| 3 | "Sì, sono io" | conferma identità + chiede servizio | `fsm_state=ASKING_SERVICE` |

**PASS**: Gigi → Gigio mapping eseguito (verifica DB query in log mostra `cliente_id` = ID di Gigio Bianchi).
**FAIL**: Sara crea NUOVO cliente "Gigi" duplicando Gigio.

---

### 📋 Scenario 3 — "Chiusura Graceful"

**Obiettivo**: post-prenotazione, riaggancio cliente OR "Grazie, arrivederci" → FSM transit a `ASKING_CLOSE_CONFIRMATION` e WhatsApp send.

**Copione chiamata**:

| # | Tu dici al telefono | Sara atteso |
|---|---------------------|-------------|
| 1 | (Sara risponde) | saluto |
| 2 | "Vorrei un taglio domani alle 15" | conferma slot disponibile |
| 3 | "Sono Marco Rossi" | match cliente esistente o registrazione |
| 4 | "Sì confermo" | conferma prenotazione + invio WhatsApp |
| 5 | "Grazie, arrivederci" | saluto finale di chiusura |
| 6 | (riaggancia tu dal cellulare) | call termina pulita |

**PASS**: log mostra in sequenza:
1. `fsm_state=ASKING_CLOSE_CONFIRMATION` (transit a turn #5)
2. WhatsApp send attempt (`whatsapp_handler.send_confirmation` — può essere mock se WA non configurato in test mode, l'importante è che l'intent venga emesso)
3. `SIP BYE received` e sessione termina con `final_state=DONE` o `CLOSED`

**FAIL**: Sara dopo "Grazie arrivederci" prova a fare nuova prenotazione (FSM non chiude) → bug FSM transition.

---

### 📋 Scenario 4 — "Flusso Perfetto" (E2E nuovo cliente)

**Obiettivo**: end-to-end nuovo cliente → booking → WA → chiusura → analytics record.

**Setup**: usa nome NON esistente in DB (es. "Federico Marrone" — verifica prima con `SELECT * FROM clienti WHERE nome='Federico'`, se esiste cambia).

**Copione chiamata**:

| # | Tu dici al telefono | Atteso |
|---|---------------------|--------|
| 1 | (Sara risponde) | saluto |
| 2 | "Sono un nuovo cliente, mi chiamo Federico Marrone" | onboarding + registrazione |
| 3 | "Vorrei prenotare un trattamento viso" | chiede data/ora |
| 4 | "Venerdì pomeriggio" | offre slot specifici |
| 5 | "Alle 16 va bene" | conferma slot |
| 6 | "Sì confermo" | invio WA + saluto |
| 7 | "Grazie" | chiusura graceful |
| 8 | (riaggancia) | BYE pulito |

**PASS**: dopo la chiamata, verifica DB:

```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "SELECT nome, cognome, telefono FROM clienti WHERE nome='Federico' ORDER BY id DESC LIMIT 1;"
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "SELECT cliente_id, servizio, data, ora, status FROM appuntamenti ORDER BY id DESC LIMIT 1;"
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/analytics.db" \
  "SELECT session_id, total_turns, final_state, completed, source FROM sessions ORDER BY started_at DESC LIMIT 1;"
```

Atteso:
- Cliente `Federico Marrone` in `clienti`
- Appuntamento venerdì 16:00 servizio "viso" status=confirmed
- Session in `analytics.db`: `completed=1`, `final_state` terminale, `source='voip'` (NON 'mic'/'text')

**FAIL**: cliente non creato OR appuntamento non persistito OR session.source≠'voip'.

---

### 📋 Scenario 5 — "WAITLIST"

**Obiettivo**: slot occupato → Sara propone waitlist → utente accetta → record `WAITLIST_SAVED`.

**Setup**: crea uno slot da occupare:

```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "INSERT INTO appuntamenti (cliente_id, servizio, data, ora, status) VALUES (1, 'taglio', date('now','+1 day'), '11:00', 'confirmed');"
```

**Copione chiamata**:

| # | Tu dici al telefono | Atteso |
|---|---------------------|--------|
| 1 | (Sara risponde) | saluto |
| 2 | "Vorrei un taglio domani alle 11" | "Slot occupato, vuoi lista attesa?" → `PROPOSING_WAITLIST` |
| 3 | "Sì, mettimi in lista" | conferma waitlist → `WAITLIST_SAVED` |
| 4 | "Grazie" | saluto + BYE |

**PASS**: log mostra entrambe le transizioni FSM. DB query:

```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "SELECT * FROM waitlist ORDER BY id DESC LIMIT 1;"
```

Atteso: nuova riga waitlist con data=domani + ora=11:00.

**FAIL**: Sara propone slot diverso INVECE di waitlist (FSM non rileva conflict) OR transizione `PROPOSING_WAITLIST` salta.

**Cleanup post-test**:

```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "DELETE FROM appuntamenti WHERE cliente_id=1 AND ora='11:00' AND data=date('now','+1 day');
   DELETE FROM waitlist WHERE telefono LIKE '+39%' AND data=date('now','+1 day');"
```

---

## 📊 Step 3 — Reporting esito

Crea il report di sessione:

```bash
cat > /tmp/sara-voip-test-$(date +%Y%m%d).md <<EOF
# Sara VoIP Live Test Report — $(date +%Y-%m-%d)

## Pre-flight
- Pipeline /health: PASS/FAIL
- SIP registered: PASS/FAIL (server: ___, user: ___)
- STUN binding: PASS/FAIL
- UDP 5060 raggiungibile: PASS/FAIL

## Smoke test (1 chiamata)
- INVITE → 200 OK: PASS/FAIL
- Audio bidirezionale: PASS/FAIL
- BYE pulito: PASS/FAIL

## Live 5 scenari
- S1 Gino vs Gigio: PASS/FAIL — note: ...
- S2 Soprannome VIP: PASS/FAIL — note: ...
- S3 Chiusura Graceful: PASS/FAIL — note: ...
- S4 Flusso Perfetto: PASS/FAIL — note: ... (DB check OK/KO)
- S5 WAITLIST: PASS/FAIL — note: ... (DB check OK/KO)

## Latency osservata (turn round-trip, da log)
- Min: XXX ms / Avg: XXX ms / Max: XXX ms
- SLO <800ms: PASS/FAIL (target v1.1)

## Audio quality (soggettivo founder, su PSTN G.711)
- TTS intelligibilità su cellulare (1-10): X
- STT accuracy parole italiane (PSTN banda limitata): X/10
- TTS naturalezza intonazione (1-10): X
- Eco/jitter/dropout percepiti: sì/no

## DID utilizzato
- Numero: +39 ___
- Provider: VivaVox Free 30gg / VivaVox Flat / Ehiweb / altro
- Costo test: € 0,00 (Free) / € ___ (Flat)
EOF
```

---

## 🚨 Troubleshooting (VoIP-specific)

| Problema | Causa probabile | Fix |
|----------|----------------|-----|
| Cellulare squilla a vuoto, Sara non risponde | SIP non registrato OR DID non instradato | Step 0.2 → fix registrazione. Se registrato ma squilla a vuoto: VivaVox routing del DID al SIP user errato — verifica pannello VivaVox `Numerazioni → Forward → user=...` |
| Sara risponde ma audio muto (un verso o entrambi) | RTP bloccato da NAT | Disabilita SIP ALG router. Apri port-forward UDP 5060 + 4000-5000 → IP iMac. Verifica STUN/TURN attivo |
| Audio robotico, parole tagliate | Jitter rete OR codec non negoziato | Log: cerca `codec=` e packet loss. Cambia codec preferito (G.711a vs G.711μ) in `voip_pjsua2.py` |
| STT trascrive parole sbagliate sistematicamente | Banda PSTN 300-3400Hz vs Whisper trained 16kHz | Limite intrinseco. Mitigazione: parla lento e scandito. Tech debt: STT fine-tune su corpus telefono italiano |
| Sara risponde "ho perso il segnale" dopo 2-3 turni | VAD timeout troppo aggressivo su silenzi PSTN | Aumenta `VAD_SILENCE_TIMEOUT_MS` in config.env (default 1500ms → prova 2500ms) |
| Latency >3000ms su ogni turno | Groq API lento OR rete iMac satura | `curl https://api.groq.com/openai/v1/models` per check. Considera Cerebras fallback |
| `SIP 401 Unauthorized` ripetuto | Pass VoIP errata | Verifica `VOIP_SIP_PASS` in config.env (no spazi, no quote stray) |
| `SIP 408 Request Timeout` | Firewall router blocca UDP esterno | Disabilita SIP ALG + apri UDP 5060 outbound |
| Call drop dopo 30 sec | Keepalive NAT scaduto | Riduci `VOIP_KEEPALIVE_INTERVAL` da 15 a 10 sec |
| Sentry segnala `pjsua2 assertion` | Bug noto pjsua2 macOS 11 | Salva `/tmp/voice-pipeline.log` + crash trace, apri issue interno |

---

## ✅ Definizione di PASS

Test P0 launch blocker CHIUSO quando:

- [ ] Pre-flight 10/10 verde
- [ ] Smoke test 1 chiamata PASS (INVITE → audio bidirezionale → BYE)
- [ ] Live 5/5 scenari PASS
- [ ] DB check Scenari 4+5 confermano persistenza con `source='voip'`
- [ ] Report `/tmp/sara-voip-test-YYYYMMDD.md` compilato
- [ ] Audio quality soggettivo ≥6/10 su tutte le 3 dimensioni

**Quando tutto PASS**: commit report in `docs/launch/sara-live-test-reports/` + marca `HANDOFF.md` come `P0 Sara VoIP test live ✅ CHIUSO`.

---

## ⚠️ Note CTO — critica strutturale (vincolo #4)

1. **Assunzione VivaVox attivata**: il runbook assume VivaVox Free già attivato e DID assegnato. Open question S202 #1 (timeline attivazione) non chiusa. Se attivazione non completa al momento del test → Step 0.4 fallisce e founder è bloccato senza fallback. **Mitigazione**: prima del test, founder verifica attivazione completa via VivaVox panel (statoaccount + DID visibile).

2. **NAT casa founder non testato**: pipeline su iMac dietro router casa. STUN configurato (`stun.voip.vivavox.it:3478`) ma TURN no. ~20% provider italiani usano CGNAT — se router casa founder è CGNAT, RTP audio fail anche con SIP REGISTER OK. **Tech debt P1**: provisioning TURN server gratuito (Open Relay Project, free tier) se Step 0.5/0.10 falliscono.

3. **PSTN audio quality vs studio mic**: codec G.711 (8kHz banda 300-3400Hz) degrada STT vs mic studio (16-48kHz). Scenari testati con mic in S199 non si replicano 1:1. **Implicazione**: alcuni FAIL in scenari 1-2 possono essere "feature working but degraded audio", NON bug pipeline. Distinguere via log: se `STT confidence <0.6` → audio issue, non logic issue.

4. **5 scenari live = ~45 min effettivi + 30 min setup/cleanup**: rischio fatigue founder e errori procedura. **Mitigazione**: scenari prioritizzati per gravità launch — S1 (disambiguation) + S4 (E2E) sono P0, S2/S3/S5 sono P1. Se tempo limitato, chiudere S1+S4 PASS = release gate verde per soft-launch primi 3 clienti.

---

## ⏭️ Next session prompt post-test

```
Sara VoIP live test PASS 5/5 — report in docs/launch/sara-live-test-reports/YYYYMMDD.md.
Rimosso P0 launch blocker test Sara VoIP. Aggiornare ROADMAP_REMAINING.md +
HANDOFF.md + PRE-LAUNCH-AUDIT.md (categoria Functional E2E → PASS).
Prossimo P0 launch blocker rimanente: Win MSI (RUNBOOK-P2-WIN-MSI-BUILD.md).
```
