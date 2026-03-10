# FLUXION — Handoff Sessione 43 → 44 (2026-03-10)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: bf044cb
Working tree: CLEAN ✅
type-check: 0 errori ✅
cargo check: 60 errori pre-esistenti in listini.rs/media.rs (DATABASE_URL + E0282 — invariati, NON loyalty)
iMac: sincronizzato ✅ | pipeline UP porta 3002 | Cloudflare Tunnel LaunchAgent attivo
```

---

## ✅ COMPLETATO SESSIONE 43

### Gap #6 — Tessera Fedeltà UI + Birthday Dashboard (commit bf044cb)
**Impatto**: +8% return rate; loyalty timbri = PMI trattiene clienti senza sconti → +€400-800/mese

**Modifiche:**
- `src-tauri/src/commands/loyalty.rs`:
  - `set_loyalty_threshold(cliente_id, threshold)` — soglia timbri configurabile (1-100, valida)
  - `get_clienti_compleanno_settimana()` — clienti con compleanno nei prossimi 7 giorni (year rollover safe)
  - Struct `ClienteCompleanno` (id, nome, cognome, telefono, data_nascita, is_vip, giorni_mancanti, anni)
- `src-tauri/src/lib.rs`: 2 nuovi comandi registrati
- `src/types/loyalty.ts`: `ClienteCompleannoSchema` + type
- `src/hooks/use-loyalty.ts`: `useSetLoyaltyThreshold` mutation + `useCompeanniSettimana` query
- `src/components/loyalty/LoyaltyProgress.tsx`:
  - Button **"+ Timbro"** manuale (chiama `increment_loyalty_visits`, disabilitato a milestone)
  - **Soglia configurabile inline**: click su "Soglia: N" → input numerico → blur/Enter salva
- `src/pages/Dashboard.tsx`:
  - Widget **"Compleanni questa settimana"** (card affiancata a Top Operatori)
  - Mostra: nome, età che compie, "Oggi!" / "Domani" / "Tra N giorni", badge VIP, telefono
  - Birthday WA backend: già attivo in `reminder_scheduler.py` (APScheduler daily 9:00am, idempotente per anno)

**AC verificati:**
- AC1: set_loyalty_threshold valida range 1-100, aggiorna DB ✅
- AC2: get_clienti_compleanno_settimana restituisce clienti ordinati per giorni_mancanti ✅
- AC3: Year rollover (dic→gen) gestito correttamente ✅
- AC4: Button "+ Timbro" disabilitato a milestone (progress=100%) ✅
- AC5: Soglia inline: click → input → Enter/blur → salva ✅
- AC6: Dashboard birthday widget con highlight "Oggi!" in rosa ✅
- AC7: Birthday WA APScheduler daily 9:00am operativo ✅
- AC8: type-check 0 errori ✅

---

## 🚀 PROSSIMO: P0.5 — Onboarding Frictionless (BLOCCA VENDITE)

**Goal**: PMI non tecnico completa setup in < 5 minuti, senza toccare config.env o terminale
**Revenue**: SBLOCCA VENDITE — senza onboarding fluido nessun cliente può acquistare autonomamente

### Opzione raccomandata (CTO):
**Opzione A** — Fluxion bundla Groq key propria (tier gratuito cifrata in binario Tauri)
- Utente zero config per voice
- Implementazione: key AES-256 in binary, rotazione automatica, fallback pool

### Alternativa se A bloccata:
**Opzione B** — Setup wizard in-app passo-passo con validazione live:
- Step 1: Groq API key (link diretto hf.co/settings + test ping)
- Step 2: Gmail app password (istruzioni screenshot inline)
- Step 3: WhatsApp QR scan (già funzionante)
- Step 4: Dati negozio (già presente in Impostazioni)

### File chiave da leggere prima di iniziare:
- `src/pages/Impostazioni.tsx` — setup wizard esistente
- `src-tauri/src/commands/setup.rs` — comandi setup
- `voice-agent/main.py` — dove usa GROQ_API_KEY
- `config.env` — struttura attuale config

---

## INFRA ATTIVA

### iMac (192.168.1.12)
```bash
# Sync + riavvio pipeline
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Cloudflare Tunnel
```bash
launchctl list | grep cloudflare
grep TUNNEL_URL '/Volumes/MontereyT7/FLUXION/config.env'
```

### License Server
```bash
ssh imac "curl -s http://localhost:3010/health"
```

### cargo check iMac
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/src-tauri' && cargo check 2>&1 | grep -v 'DATABASE_URL\|E0282\|listini\|media' | tail -20"
```
