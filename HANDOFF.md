# FLUXION — Handoff Sessione 67 → 68 (2026-03-13)

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
Branch: master | HEAD: a0b9a0e
fix(f07): test_server make_db schema + Enterprise→Clinic tier
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1477 PASS / 0 FAIL ✅
F07 license server pytest: 29/29 PASS ✅
```

---

## COMPLETATO SESSIONE 67

### 1. F07 config.env iMac — COMPLETATO ✅
Tutte le credenziali ora presenti in `/Volumes/MacSSD - Dati/FLUXION/scripts/license-delivery/config.env`:
- `LS_WEBHOOK_SECRET` ✅
- `LS_API_KEY` ✅ (JWT LemonSqueezy)
- `LS_WEBHOOK_ID=79826` ✅ (recuperato via API)
- `SMTP_USER=fluxion.gestionale@gmail.com` ✅
- `SMTP_PASS` ✅ (Gmail App Password aggiornata)
- `FLUXION_KEYGEN_PATH=~/fluxion-keygen` ✅ (compilato release su iMac)
- `KEYPAIR_PATH=~/fluxion-keypair.json` ✅ (copiato da MacBook)
- `ACTIVATE_URL_BASE` ✅ (auto-aggiornato da Cloudflare tunnel script)

### 2. fluxion-keygen compilato su iMac
- Build release da `fluxion-license-generator/` → `~/fluxion-keygen` (1.3MB)
- keypair copiato via scp: `~/fluxion-keypair.json`

### 3. License server avviato e testato ✅
- **29/29 PASS** su `test_server.py`
- Fix: `make_db()` nel test mancava colonne `refunded` + `email_sent`
- Fix: tier "Enterprise" inesistente → "Clinic" (tier reali: Base/Pro/Clinic)
- Commit: `a0b9a0e`

---

## F07 — License Server (OPERATIVO)

### Avvio manuale iMac
```bash
ssh imac "kill \$(lsof -ti:3010) 2>/dev/null; sleep 1; cd '/Volumes/MacSSD - Dati/FLUXION/scripts/license-delivery' && nohup python3 server.py > /tmp/license-server.log 2>&1 &"
```

### Avvio tunnel Cloudflare (per webhook pubblico)
```bash
ssh imac "launchctl load ~/Library/LaunchAgents/com.fluxion.cloudflared.plist"
```
Dopo avvio: aggiorna webhook LS con nuovo URL (auto se `LS_API_KEY`+`LS_WEBHOOK_ID` settati ✅)

### Test health
```bash
curl http://192.168.1.12:3010/health
```

---

## F15 VoIP — IN ATTESA CREDENZIALI

✅ Architettura implementata | ⏳ Credenziali EHIWEB SIP ancora in arrivo
- `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER` → da inserire in config.env iMac voice-agent

---

## PROSSIMA SESSIONE S68

> **Skill**: `fluxion-tauri-architecture` (F07 end-to-end) o `fluxion-voice-agent` (F15 SIP)

### Priorità S68 (in ordine):
1. **F07 end-to-end test** — simula acquisto → webhook → email → attivazione licenza
2. **SE credenziali EHIWEB arrivate** → F15 test SIP end-to-end
3. **F07 LaunchAgent** — avvio automatico license server al boot iMac (enterprise grade)

### Test F07 end-to-end da fare:
```bash
# 1. Avvia license server
ssh imac "kill \$(lsof -ti:3010) 2>/dev/null; sleep 1; cd '/Volumes/MacSSD - Dati/FLUXION/scripts/license-delivery' && nohup python3 server.py > /tmp/license-server.log 2>&1 &"

# 2. Verifica health
curl http://192.168.1.12:3010/health

# 3. Simula webhook order_created (con firma corretta)
# 4. Verifica email inviata a fluxion.gestionale@gmail.com
# 5. Test attivazione licenza con fingerprint
```
