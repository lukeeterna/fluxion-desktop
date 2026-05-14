# S234 — Prompt ripartenza (handoff S233 → S234)

**Generato**: 2026-05-14 (chiusura S233 ORANGE — context 72% CLOSING_ONLY)
**Branch**: master @ `481eae1` (MacBook + iMac sync)
**Pipeline iMac**: STOPPED clean (PID 37932 killed end S233)
**Stato S233**: ⚠️ CLOSED ORANGE — primo live test SIP riuscito ma bug audio bridge non discriminato

## TL;DR S233 outcome

- ✅ **Setup live test SIP funzionante per la prima volta**: vivavox.it + 0972536918 + pjsua2 REGISTER 200 OK
- ✅ **2 chiamate ricevute** da founder smartphone (3281536308 Vodafone)
- ⚠️ **Call 2 errore**: `pjsua2.Error in voip_pjsua2.py:235 call_audio.startTransmit(self.audio_port)` — non chiarito se blocking o trace innocuo
- 🔒 **Stripe E-3 blocked**: wrangler iMac OAuth expired 2025-11-29 + CF API token mancante (MacBook + iMac entrambi)
- 📊 **Context lesson**: MEMORY.md 1960 righe = 220KB autoload consuma ~40% context PRIMA del lavoro

## Plan S234 (B-1 Sara stress live Phase 2)

### Pre-flight obbligatorio
1. **PRUNE MEMORY.md** target 500 righe (preserve permanent rules + S233 only). Pattern Karpathy compilation triggered.
2. `ssh imac` verify pipeline status:
   ```bash
   ssh imac 'ps aux | grep "main.py" | grep -v grep; curl -s http://127.0.0.1:3002/api/voice/voip/status'
   ```
3. Se down, restart:
   ```bash
   ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && VOIP_LOCAL_PORT=6080 nohup ./venv/bin/python main.py > /tmp/sara-live-s234.log 2>&1 & echo PID=$!'
   ```
   (Traccar tracker-server.jar PID 1195 occupa 5060-5099 → MUST usare VOIP_LOCAL_PORT=6080)

### Step 1 — Discriminare pjsua2.Error
- Founder chiama 0972536918, parla **normalmente** ("Buongiorno"), aspetta 3-5s.
- **Se sente greeting** "Salone Bella Demo, buon[giorno/asera/pomeriggio]! Come posso aiutarla?" → trace è rumore, procede Step 2.
- **Se silenzio totale** → bug confermato. Fix candidates `voip_pjsua2.py:227-237`:
  - (a) defer `startTransmit` a polling `mi.status == PJSUA_CALL_MEDIA_ACTIVE` con retry
  - (b) re-init `self.audio_port` in `onCallMediaState` se errore precedente
  - (c) check `pj.PJSUA_CALL_MEDIA_ACTIVE` vs altre state (LOCAL_HOLD, REMOTE_HOLD)

### Step 2 — Stress live patterns (2-3 verticali max)

Priorità verticali (zona booking_keyword_miss S232):

**SALONE** (set-vertical: salone):
- "Buongiorno, vorrei taglio e piega. Domani... no aspetta giovedì, alle... vedi tu primo slot. Sono Marco Rosso. Ah no Marco Rossi."
- "Sono Gigi, voglio colore sabato pomeriggio" (disambig Gigi→Gigio)

**AUTO** (set-vertical: auto):
- "Devo fare la revisione" (S232 fix validation live — S232-P1 patch test)
- "Sabato presto, ma non troppo presto" (vague time)

**BEAUTY** (set-vertical: beauty):
- "Vorrei fare epilazione laser totale gambe e ascelle" (S232 multi-zona)
- "Sono Giorgia ma chiamatemi Gio" (nickname VIP)

### Step 3 — Output

`voice-agent/tests/e2e/live-hw-s234.md` con:
- Per-verticale: latency P50/P95 turn, intent classification accuracy, FSM transitions, errori
- Gap list rispetto baseline S232 synthetic 147/0/0
- Decisione Phase 3: optimize latency OR cover restanti 3 verticali (palestra/medical/professionale)

## File chiave S234

- `/Volumes/MontereyT7/FLUXION/voice-agent/src/voip_pjsua2.py:227-237` (audio bridge fix)
- `/Volumes/MontereyT7/FLUXION/voice-agent/.env` (vivavox credentials, valutare gitignore se non già)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/sip_client.py`
- `/Volumes/MontereyT7/FLUXION/voice-agent/main.py:1321-1329` (VoIPManager bootstrap)

## Vincoli S234

- **NO Co-Authored-By** in commit (MEMORY rule #6 / S198)
- **Atomic commits** per topic (1 fix audio bridge / 1 stress patterns / 1 prune MEMORY)
- **Context budget**: PRUNE MEMORY come PRIMO atto, altrimenti context si esaurisce a 40% pre-lavoro
- **Critical files**: voip_pjsua2.py = file critico (schema audio path) → editing solo sotto 50% context
- **Test E2E obbligatorio**: nessun fix audio bridge committed senza chiamata reale superata

## Stripe E-3 (deferred, founder action richiesta)

Per sbloccare prossima sessione che vuole toccare Worker secrets:
1. Founder apre `https://dash.cloudflare.com/profile/api-tokens`
2. Click "Create Token" → template "Edit Cloudflare Workers"
3. Account: gianlucanewtech / Zones: all
4. Copia token e aggiungi a `/Volumes/MacSSD - Dati/FLUXION/.env`:
   ```
   CLOUDFLARE_API_TOKEN=<token>
   ```
5. Anche su MacBook `/Volumes/MontereyT7/FLUXION/.env` per simmetria.

## Comando esatto ripartenza S234 (incolla in nuova sessione)

```
Sessione S234 FLUXION. Leggi MEMORY.md "Stato Corrente sessione 233" +
.claude/NEXT_SESSION_PROMPT.manual.md. Focus: B-1 Sara stress live smartphone Phase 2.
Pre-step OBBLIGATORIO: prune MEMORY.md a 500 righe (preserve permanent rules header + S233 only).
Poi: ssh imac status pipeline + SIP REGISTER check + restart se down con VOIP_LOCAL_PORT=6080.
Discrimina pjsua2.Error live (chiamata test, ascolta greeting).
Vincoli S234: no Co-Authored-By, atomic commits, file critici sotto 50% context.
```
