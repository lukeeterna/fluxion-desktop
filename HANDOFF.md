# FLUXION — Handoff Sessione 68 → 69 (2026-03-13)

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
Branch: master | HEAD: 0b42b9d
feat(f07): LaunchAgent license server — avvio automatico al boot iMac
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1477 PASS / 0 FAIL ✅
F07 license server E2E: 22/22 PASS ✅
```

---

## COMPLETATO SESSIONE 68

### 1. F07 E2E Test — 22/22 PASS ✅

Script: `scripts/license-delivery/e2e_test.py`

**9 scenari testati:**
- T1: Health check
- T2: HMAC firma invalida → 401
- T3: order_created webhook → DB + tier resolution
- T4: Webhook duplicato (idempotenza)
- T5: Tier resolution Base (substring) + Clinic (UUID fallback)
- T6: order_refunded → blocca attivazione → 402
- T7: Attivazione licenza reale (fluxion-keygen) — tier + signature + 409 duplicata
- T8: Ordine inesistente → 404
- T9: Campi mancanti → 400

**Bug fixato in server.py**: keygen scriveva su file (non stdout). Ora usa `tempfile.NamedTemporaryFile` + `--output` flag.

### 2. F07 LaunchAgent — INSTALLATO E ATTIVO ✅

- **Plist**: `~/Library/LaunchAgents/com.fluxion.license-server.plist` (su iMac)
- **Start script**: `/usr/local/bin/fluxion-license-server-start.sh` (su iMac)
- **KeepAlive**: restart automatico se crasha, ThrottleInterval 30s
- **Log**: `/tmp/license-server.log` (applicazione) + `/tmp/license-server-launchd.log` (launchd)
- **Avvio al boot**: `RunAtLoad=true`
- **Repo reference**: `scripts/launchagents/com.fluxion.license-server.plist`

### Comandi gestione LaunchAgent
```bash
# Verifica stato
ssh imac "launchctl list | grep license-server"

# Stop/Start manuale
ssh imac "launchctl unload ~/Library/LaunchAgents/com.fluxion.license-server.plist"
ssh imac "launchctl load ~/Library/LaunchAgents/com.fluxion.license-server.plist"

# Log in tempo reale
ssh imac "tail -f /tmp/license-server.log"
```

---

## F07 — Stato Complessivo

| Componente | Stato |
|-----------|-------|
| LemonSqueezy account + store | ✅ |
| Checkout URLs (3 tier) | ✅ |
| server.py webhook handler | ✅ |
| fluxion-keygen compilato | ✅ |
| config.env iMac | ✅ |
| Cloudflare tunnel + auto-update webhook | ✅ |
| Email retry APScheduler | ✅ |
| E2E test 22/22 PASS | ✅ |
| LaunchAgent boot automatico | ✅ |
| **F07 COMPLETATO** | ✅ |

---

## F15 VoIP — IN ATTESA CREDENZIALI

✅ Architettura implementata | ⏳ Credenziali EHIWEB SIP ancora in arrivo
- `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER` → da inserire in config.env iMac voice-agent

---

## PROSSIMA SESSIONE S69

> **Priorità**: ROADMAP_REMAINING.md — prossima fase dopo F07

### Da leggere all'inizio S69:
1. `ROADMAP_REMAINING.md` → prossima fase ⏳
2. Se credenziali EHIWEB arrivate → F15 test SIP end-to-end

### Promemoria tecnici:
- **Voice pipeline** porta 3002 bound a `127.0.0.1` (hardening intenzionale) — accessibile solo da iMac
- **License server** gestito da LaunchAgent (avvio automatico boot)
- **Cloudflare tunnel** gestito da LaunchAgent `com.fluxion.cloudflared`
