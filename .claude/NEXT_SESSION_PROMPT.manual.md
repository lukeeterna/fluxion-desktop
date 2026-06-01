# Prompt ripartenza S322 — Sara stress test vocale 9 verticali, CTO-autonomous via TTS (gate "pronto a vendere")

> **REGOLA #23 (founder-input S321) — CTO GUIDA IL TEST, NON LUKE**: il test vocale Sara va condotto in autonomia dal CTO che parla via TTS sull'iMac e guida la conversazione, catturando le risposte di Sara. MAI chiedere a Luke di chiamare `0972536918` dal telefono. Estensione REGOLA #14 al dominio voce.

> **STATO S321 (2026-06-01) — PRE-FLIGHT + FASE 0 + baseline = ✅ FATTI:**
> - Canale EHIWEB **RIATTIVATO E VERIFICATO**: SIP `registered:true reg_status:200` su `0972536918@sip.vivavox.it`. pjsua2 carica con Python 3.9.6 system + `lib/pjsua2` (sys.path insert + DYLD a runtime in `voip_pjsua2.py:130`). Avvio: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python3 main.py --port 3002 > /tmp/sara.log 2>&1 &"` → `.env` iMac ha già tutto il VoIP → SIP register auto. Verifica `curl http://127.0.0.1:3002/api/voice/voip/status` **SOLO via `ssh imac`** (porta bound 127.0.0.1, NON raggiungibile da MacBook).
> - Baseline HTTP `scripts/test_all_verticals_e2e.py` = **21 OK / 8 WARN / 0 FAIL** su 9 verticali. **7/8 WARN = falsi negativi** (Sara corretta: cliente nuovo→registering_phone, disambiguazione fonetica). **1 WARN reale**: `fisioterapia FAQ "seduta" generica → availability-check invece di prezzo €50` (routing FAQ ambiguo → FIX FASE 4). Evidence: `~/venture-os/state/s321-sara-live-stresstest-evidence.json`.
> - **BLOCKER #1 RESIDUO**: percorso audio RTP E2E mai validato a runtime con voce. SIP register OK ≠ audio funziona.
> - **switch verticale**: `bash scripts/switch_vertical.sh <vert>` (riavvia pipeline + ri-registra SIP ~10s). DB demo in `data/vertical_dbs/` (12). Matrice: salone, barbiere, beauty, odontoiatra, fisioterapia, gommista, toelettatura, palestra, medical.

> **FASE 0-bis S322 (research-first, BLOCKER) — costruire harness audio autonomo:**
> - NON esiste endpoint HTTP audio-in→STT (`main.py:426` `/process-audio`==`process_handler` solo testo; `/api/voice/say` = TTS out). Lo STT reale è dentro il path SIP/RTP pjsua2 (`SaraAudioPort`).
> - Per parlare a Sara in autonomia: secondo client SIP che chiama `0972536918` (o registra su EHIWEB) e riproduce WAV generati via TTS (`say` macOS / Edge-TTS / Piper), catturando la risposta RTP di Sara → trascrizione STT → valutazione. Research-first sul metodo zero-cost (pjsua CLI `--play-file`/`--rec-file`, o secondo account SIP) PRIMA di costruire. Verificare se chiamare il numero PSTN da un secondo client genera costi EHIWEB.
> - Delegabile a `voice-engineer` agent in context isolato (budget).

# (storico) Prompt S321 — Sara LIVE stress test su tutti i verticali (gate "pronto a vendere")

> **META-VINCOLO (REGOLA #18 VALIDATE-THEN-IMPLEMENT)**: prima di dichiarare CHIUSO qualsiasi anello/feature production-critical, eseguire S187 FASE 1 (research + tabella validazione fonte + verdetto + evidenza reale) e FERMARSI per GO Luke. NO production claim senza output reale di test letto da Luke.
> **REGOLA #21 (founder-input S320)**: Sara = pilastro, NON deferrabile. "Pronto a vendere" = Sara testata LIVE su TUTTI i verticali con chiamata reale (iMac + smartphone) + stress test, criterio = "soddisfa pienamente il cliente". Payment rail OK = necessario, non sufficiente.

## ✅ STATO REALE POST-S320 (audit code-truth completato)

| Anello | Stato | Evidenza |
|--------|-------|----------|
| Payment rail €497/€897 | ✅ VERIFIED-E2E-LIVE | smoke €1 Base S317 + Pro S319, webhook 200 + Ed25519 + D1 + Resend delivered + refund |
| C-FLUXI-002 primo CLOSED_WON | ✅ RESOLVED (Luke GO S318) | — |
| Verticali canonici | ✅ RISOLTO da codice S320 | `src/types/setup.ts:66` |
| **Sara live multi-verticale** | 🔴 **BLOCKER #1 — mai eseguito E2E runtime** | server 3002 DOWN |
| Wizard activate GUI cliente | 🟡 CLAIMED (codice ok, mai live) | richiede founder GUI iMac |
| macOS signing ad-hoc + download URL | 🟡 da implementare | #2b deciso €0 S319 |

### Verticali canonici (RISOLTO S320 — non chiedere a Luke)
- Fonte verità: `src/types/setup.ts:66` `MACRO_CATEGORIE` = **8 macro** (medico, beauty, hair, auto, wellness, professionale, pet, formazione) + `MICRO_CATEGORIE:129` ~50 micro con flag `hasScheda`.
- `CATEGORIE_ATTIVITA:238` (5 valori) = `CONSTANTS LEGACY:230` MORTO, ignorare.
- Schede React + DB reali per **6/8 macro** (medico, beauty, hair, auto, wellness, pet). `professionale` + `formazione` = gusci vuoti (no scheda, no demo Sara).
- **Matrice test Sara** = 9 verticali voice-agent con DB demo pronti (`voice-agent/scripts/create_vertical_dbs.py`): salone, barbiere, beauty, odontoiatra, fisioterapia, gommista, toelettatura, palestra, medical.

## 🎯 OBIETTIVO S321
Far chiamare Sara da smartphone reale (Luke), per ogni verticale, sotto stress, misurare le lacune, produrre piano di integrazione/modifiche con test E2E obbligatori.

## 🚦 SCOPE S321 — fasi ordinate

### PRE-FLIGHT (CTO autonomous)
- Voice Pipeline 3002 su iMac: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python main.py > /tmp/sara.log 2>&1 &"` poi `curl http://192.168.1.2:3002/health`.
- HTTP Bridge 3001 già UP (hook). Verificare anche.

### FASE 0 — RIATTIVARE il canale chiamata EHIWEB (metodo NOTO, già usato S244)
- **NON è scaffold, NON serve research del canale**: la chiamata reale smartphone→Sara@iMac è già stata fatta il 2026-05-15. Evidenza: `.claude/cache/agents/s244/sara-live-s244.log` (INVITE 19:33:06, codec PCMU/G.711, 200 OK).
- **Architettura reale**: founder chiama dal telefono normale il numero PSTN **0972536918** (EHIWEB VivaVox, già pagato) → EHIWEB inoltra SIP a `pjsua2` sull'iMac → Sara risponde via RTP G.711 8kHz bidirezionale. Niente softphone, niente cloud terzo, niente costo aggiuntivo.
- **Codice**: `voice-agent/src/voip_pjsua2.py` (`VoIPManager`, `SIPConfig.from_env()`) + gate avvio `voice-agent/main.py:1320` (`if VOIP_SIP_USER`). Bug NAT già fixati S119 (rport parsing + CRLF keepalive 20s).
- **Env richieste** per accendere il VoIP all'avvio pipeline:
  - `VOIP_SIP_USER=0972536918`
  - `VOIP_SIP_PASS=<password EHIWEB>` — **unico secret non nel repo**. PRIMA di chiedere a Luke (REGOLA #19/#300): `grep -ri VOIP_SIP_PASS ~/.claude/.env* ; ssh imac "cat '/Volumes/MacSSD - Dati/fluxion/voice-agent/.env' 2>/dev/null | grep -i voip"`. Se trovata → persist `~/.claude/.env`. Se NON trovata → chiedere a Luke o reset da pannello EHIWEB.
  - `VOIP_SIP_SERVER=sip.vivavox.it` (default)
- **Prerequisiti riattivazione**: (1) lib pjsua2 linkabile su iMac (verificare `lib/pjsua2/` o `brew install pjsip`); (2) router iMac SIP ALG disabilitato / NAT ok.
- **Verifica registrazione**: `curl http://192.168.1.2:3002/api/voice/voip/status` → atteso `{"sip":{"registered":true}}`.
- **Avvio con VoIP**: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && VOIP_SIP_USER=0972536918 VOIP_SIP_PASS=<pwd> VOIP_SIP_SERVER=sip.vivavox.it nohup python main.py --port 3002 > /tmp/sara.log 2>&1 &"` → atteso log `✅ VoIP service avviato (SIP: 0972536918@sip.vivavox.it)`.

### FASE 1 — SETUP harness stress test (CTO autonomous)
- `voice-agent/scripts/switch_vertical.sh` per swap DB demo per verticale + restart pipeline.
- `voice-agent/scripts/create_vertical_dbs.py` (rigenera DB demo se mancanti).
- `voice-agent/scripts/test_all_verticals_e2e.py` (harness booking + faq + triage per i 9 verticali) — usare come baseline automatizzata PRIMA della chiamata vocale umana.

### FASE 2 — RUN test (Luke + CTO)
1. Baseline automatizzata: `test_all_verticals_e2e.py` su tutti i 9 verticali → log strutturati.
2. Chiamata vocale reale: Luke parla da smartphone, scenari per ogni verticale (booking nuovo cliente, FAQ, disambiguazione nome, slot pieno→waitlist, chiusura graceful). Vedi `voice-agent-details.md` "Test Live Scenari".
3. Catturare log per verticale: trascrizione STT, intent NLU, risposta, latenza per turno, TTS.

### FASE 3 — MISURARE LACUNE (criterio "soddisfa pienamente il cliente")
- Scoring per verticale: booking completato sì/no, FAQ corretta sì/no, disambiguazione ok, latenza p95 < 800ms (soglia PLAN), naturalezza/errori. Formato output `e2e-testing.md`: `OK/WARN/FAIL [VERTICAL] [SCENARIO]: input → output`.
- Evidence file: `~/venture-os/state/s321-sara-live-stresstest-evidence.json` (per verticale: pass/fail + lacune + latenze).

### FASE 4 — PIANO INTEGRAZIONE (con E2E obbligatori)
- Da lacune misurate, proporre modifiche prioritizzate (NLU, FSM, RAG, TTS, latenza).
- Ogni modifica DEVE avere test E2E obbligatorio (`e2e-testing.md`): curl `POST /api/voice/process` su iMac + ri-test vocale.
- NO "production ready Sara" senza S187 FASE 1 evidence + GO Luke (META-VINCOLO).

## 🧹 CLEANUP carry-over (context fresco)
- PLAN.md `OBIETTIVO:19` "9 verticali" → "8 macro / 6 implementati" (cosmetico, deferred da S320 per BLOCK_CRITICAL 66%).
- Nascondere `professionale` + `formazione` dal Setup Wizard finché senza scheda+demo (filtro 1-riga, toglie falsa promessa vendita).
- C-LIC-001 `[DEFERRED]`→`[ADDRESSED]` (credenziali LIVE attive da S316).
- #2b macOS ad-hoc signing (€0, deciso S319) + DMG download URL pubblico verificato + wizard activate GUI live.

## REGOLE ATTIVE S321
- **#21** Sara pilastro, gate vendita include Sara live (NUOVA)
- **#14** CTO autonomous (pre-flight, FASE 0/1/4 autonome; FASE 2 chiamata = Luke)
- **#16** research-first (FASE 0 path VoIP zero-cost PRIMA di procedere)
- **#18** VALIDATE-THEN-IMPLEMENT (no "Sara ready" senza evidence + GO Luke)
- **#4** critica + autocritica 4 punti su ogni piano FASE 4
- **#5** chiusura: commit + prompt ripartenza
- **E2E obbligatorio** (`e2e-testing.md`) su ogni modifica FASE 4

## ARTEFATTI PRODUCTION (invariati)
- Stripe LIVE Base `plink_1TcpAk...8boabwRX` €497 / Pro `...fn8dioIo` €897; Webhook `we_1TcpBL...`; Worker prod; Landing `fluxion-landing.pages.dev`; Email `fluxion-app.com` verified. VOS gate VERDE.

## PRIMO COMANDO S321
> **SECRET VoIP RISOLTO (S321)**: `VOIP_SIP_PASS=YR_q9LNV5VU33Kq` GIÀ presente in `/Volumes/MacSSD - Dati/fluxion/voice-agent/.env` su iMac (+ `VOIP_ENABLED=true`, `VOIP_SIP_PORT=5060`). Persistito anche in `~/.claude/.env` (FLUXION_VOIP_SIP_*). NON ri-cercare, NON chiedere a Luke. Poiché è già nel `.env` iMac, NON serve passarlo inline sulla riga ssh — basta che `main.py` carichi il `.env` (verificare con `SIPConfig.from_env()`).

1. Pre-flight + avvio pipeline (il `.env` iMac contiene già tutto il VoIP):
```
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python main.py --port 3002 > /tmp/sara.log 2>&1 &" && sleep 6 && curl -s http://192.168.1.2:3002/api/voice/voip/status
```
Atteso: log `✅ VoIP service avviato (SIP: 0972536918@sip.vivavox.it)` + `{"sip":{"registered":true}}`.
2. Se `from_env()` NON legge il `.env` automaticamente, fallback inline:
```
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && VOIP_SIP_USER=0972536918 VOIP_SIP_PASS=YR_q9LNV5VU33Kq VOIP_SIP_SERVER=sip.vivavox.it nohup python main.py --port 3002 > /tmp/sara.log 2>&1 &" && sleep 6 && curl -s http://192.168.1.2:3002/api/voice/voip/status
```
3. Poi Luke chiama **0972536918** dal telefono → FASE 1/2/3/4.
