# FLUXION — S335 resume — Sara live-test. Layer 1 VERDE. Layer 2 audio IN ATTESA risposta supporto EHIWEB (SIP 403).

> Scritto 2026-06-03 a chiusura S334. Step 0 (fix SIP): root cause = registrazione incagliata lato EHIWEB. **MAIL DI SUPPORTO INVIATA da Luke** (bozza in `~/Desktop/email-supporto-ehiweb.txt`). **STATO = WAIT su risposta/reset EHIWEB.** Parte verificabile Step 1 (WAV PCM16 8kHz mono) confermata.
>
> ## >>> PRIMA AZIONE S335: NON fare nulla finché Luke non dice "EHIWEB ha resettato/risposto". <<<
> Quando Luke conferma il reset → `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"`. Se `reg_status:200` → procedi a Step 1 harness audio. Se ancora `403` → pjsua2 è fermo (non ritenta dopo 403): restart pulito via voice-engineer per forzare fresh-register, poi ri-leggi. Se persiste 403 → ri-escalare a EHIWEB (secondo livello). NON ritentare REGISTER in loop (rischio ban).

## CHIUSO IN S333 (NON ri-fare) — Layer 1 testo
- **LAYER 1 (testo) FIX + ESTESO** — commit `4f1685c`, file `voice-agent/scripts/test_all_verticals_e2e.py` (MacBook + iMac IDENTICI, shasum `f0c8072d`).
- Risultato: **50 OK / 3 WARN / 0 FAIL** su 53 test, **12/12 verticali**. Run: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python3 scripts/test_all_verticals_e2e.py"` (~6 min). 3 WARN residui = NON difetti (waitlist non forzabile da solo testo, FAQ consulenza legale senza prezzo fisso DB).

## S334 — COSA HO FATTO
### Step 0 — DIAGNOSI SIP (FATTO) → ROOT CAUSE ESTERNA, BLOCKED-ON Luke
- Stato: `curl http://127.0.0.1:3002/api/voice/voip/status` → `registered:false, reg_status:403` (era 200 in S332, 408 in S333). Progressione `200→408→403`.
- Evidenza log `/tmp/voice-pipeline.log`: REGISTER → `401` challenge (realm="asterisk", nonce) → REGISTER con `Authorization: Digest` calcolato → server risponde **`403 Forbidden`** dal `Server: MOR Softswitch` (billing EHIWEB). Il digest è ACCETTATO e processato; il `403` è una **decisione di policy provider**, NON un bug software.
- Credenziali locali `voice-agent/.env` (`VOIP_SIP_USER/PASS/SERVER`, letto da `src/voip.py::SIPConfig.from_env`): TUTTE presenti e valide, `.env` **immutato dal 1 Giu 19:51** (prima del periodo "200 OK"). Quindi NON è cambiata la config locale.
- IP pubblico iMac attuale = `151.72.9.90` (identico a quello nel REGISTER fallito). Non ho il record dell'IP al "200 OK" S332 → cambio IP residenziale dinamico NON escludibile.
- **CONFERMA fresh-register (18:16:14)**: restart pulito pipeline (PID 69944) → ciclo SIP fresco `401`→digest→**`403`**. NON è stale: EHIWEB rifiuta in tempo reale. Health Sara 200 (Sara UP, giù solo gamba SIP). NB pjsua2 si era arreso dopo il 403 delle 16:33 (non ritentava da ~1h40m).
- **Account = PAGATO** (Luke confermato; ordine 472237 07/10/2025 "Attivato", fattura a fine mese). NON è trial scaduto. "VivaVox Free" = nome prodotto, non gratuito.
- **EHIWEB (telefonata Luke) ha ESCLUSO**: blocco IP (151.x ok), filtri, conflitto multi-device ("nessun altro dispositivo oltre te"), limite registrazione singola ("ogni nuova sovrascrive la vecchia"). Primo livello "tutto ok" MA non ha accesso ai log live.
- **EVIDENZA DECISIVA (scambio 18:16)**: digest PERFETTO (nonce fresco `4f294fed`, response corretta, realm/uri/username giusti — lato nostro ineccepibile). E il loro **Asterisk ci manda `OPTIONS` (qualify) verso `151.72.9.90:5080`** (`From:"asterisk"`, `User-Agent: MOR Softswitch`): Asterisk qualifica solo i peer che considera REGISTRATI → **hanno un BINDING RESIDUO/INCAGLIATO** che ci vede peer, ma rifiuta i nostri REGISTER con `403` (non li sovrascrive). OPTIONS RX=2, nostre risposte 200=0, INVITE entranti=0.
- **ROOT CAUSE = stato di registrazione DESYNC/incagliato lato EHIWEB**. NON config (IP/filtri/limiti ok confermato). Fix = EHIWEB resetta/cancella la registrazione del peer (sip reload / clear registration). NESSUN retry nostro (rischio ban).

### >>> AZIONE RICHIESTA DA LUKE (esterna) — ammo per EHIWEB <<<
Dire all'operatore: *"Il vostro MOR/Asterisk mi manda OPTIONS (qualify) verso 151.72.9.90:5080 → avete un binding residuo che mi considera peer registrato, MA rifiutate i miei REGISTER con 403 (dopo 401 challenge, digest corretto). Stato di registrazione incagliato dal vostro lato: RESETTATE/cancellate la registrazione del peer 0972536918 (sip reload) e faccio riprovare. Config IP/filtri/limiti ok come confermato."* Se primo livello non può → secondo livello / chi vede i log live.
- Se EHIWEB rigenera la password → fornirla, aggiorno `voice-agent/.env` (`VOIP_SIP_PASS`).
- Dopo lo sblocco: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` deve dare `registered:true, reg_status:200`. Se serve, restart pipeline via voice-engineer.

### Step 1 (parte verificabile FATTA): generazione WAV TTS-out
- **VERIFICATO su iMac**: `say -o /tmp/raw.aiff "testo"` + `afconvert -f WAVE -d LEI16@8000 -c 1 /tmp/raw.aiff /tmp/out.wav` produce **`1 ch, 8000 Hz, Int16`** (PCM16 8kHz mono), il formato corretto per RTP/SIP. Questo è il lato TTS-out con cui il CTO guida il test (REGOLA #23).

## S335 — PIANO (deciso CTO, REGOLA #15)
### PRIMO COMANDO
`ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"`
- Se ancora `registered:false` → SIP NON sbloccato da Luke: ri-escalare le 3 azioni sopra, NON ritentare/forzare.
- Se `registered:true, reg_status:200` → procedere a Step 1 harness audio.

### Step 1 — Layer 2 AUDIO harness `sara_audio_harness.py` (IL VERO GATE VENDITA, REGOLA #21)
- Architettura: STT è nel path pjsua2/RTP (niente endpoint HTTP audio-in). L'harness deve fare da **2° endpoint SIP** che chiama il numero di Sara e streamma WAV su RTP, poi cattura la risposta RTP di Sara.
- API esistenti in `src/voip.py`: `send_audio(pcm_data, marker)` (riga 1126, RTP-out); già usa `wave.open` (1438). Da capire: come instanziare un secondo leg SIP/RTP per iniettare il MIO audio verso Sara.
- WAV input: PCM16 8kHz mono (ricetta `afconvert` verificata sopra).
- CTO guida via TTS in autonomia (REGOLA #23). Golden-path per verticale + scenari STT-sensitivi (NON tutti via audio).
- Gate (REGOLA #21): Sara "soddisfa pienamente il cliente" su tutti i verticali via voce → poi "pronto a vendere" + Sales Agent WA.

## BLOCKED-ON / RESTA (non blocca il gate Sara)
- Custom domain `fluxion-app.com`: NS su CF, nessun record A → attaccare al worker prod per go-live brandizzato (~10 min).
- Rami client-side tsc-only (offline grace/clock-rollback/banner saraEnabled): GUI iMac Keychain (REGOLA #12).
