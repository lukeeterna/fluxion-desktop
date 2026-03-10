# FLUXION — Handoff Sessione 44 → 45 (2026-03-10)

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
Branch: master | HEAD: 51f96c6
Working tree: CLEAN ✅
type-check: 0 errori ✅
cargo check: errori pre-esistenti in listini.rs/media.rs (DATABASE_URL + E0282 — invariati, NON toccare)
iMac: sincronizzato ✅ | pipeline UP porta 3002 | Cloudflare Tunnel LaunchAgent attivo
```

---

## ✅ COMPLETATO SESSIONE 44

### P0.5 — Onboarding Frictionless Groq/Sara (commit 82fdd87)
**Impatto**: SBLOCCA VENDITE AUTONOME — PMI ottiene conferma reale che Sara funziona

**Modifiche:**
- `src-tauri/src/commands/setup.rs`: `test_groq_key` command — chiama realmente `api.groq.com/openai/v1/models`
  - 200 → "✅ Fluxion AI attivo! Sara è pronta" | 401 → "❌ Chiave non valida" | timeout → "❌ Nessuna connessione"
- `src-tauri/src/lib.rs`: `test_groq_key` registrato nel handler Tauri
- `src/hooks/use-setup.ts`: `useTestGroqKey` hook + `GroqTestResult` type
- `src/components/setup/SetupWizard.tsx`: Step 8 usa test reale (rimosso fake ping localhost:3002)
- Decisione: Opzione A (key bundled) SCARTATA — viola Groq ToS + AES in binario reversibile

### Research CoVe 2026 (commit 51f96c6)
- `.claude/cache/agents/p06-onboarding-gmail-cove2026.md` — Gmail OAuth2 vs App Password
- `.claude/cache/agents/p10-impostazioni-redesign-cove2026.md` — Settings sidebar vs tab
- Roadmap P0.6 e P1.0 riscritti con decisioni corrette post-research

---

## 🚀 PROSSIMO: P1.0 — Impostazioni Redesign (priorità raccomandata)

**Perché P1.0 prima di P0.6**: il redesign Impostazioni è prerequisito per il Gmail OAuth2 —
la sezione "Email per le notifiche" deve esistere nella nuova sidebar prima di implementare OAuth.

**Goal**: Sostituire dump verticale 11 Card con sidebar verticale sinistra (Linear pattern)
**Revenue**: Autonomia post-vendita — PMI trova e configura tutto da sola senza supporto

### Architettura P1.0:
```
Sidebar 240px sinistra + area contenuto destra (flex layout)

ATTIVITÀ:      ✅ Orari lavoro · ⚪ Festività
COMUNICAZIONE: ⚠️  Email notifiche · ✅ WhatsApp · ⚪ Risposte auto
AUTOMAZIONE:   🔴 Sara AI · ⚪ IA FLUXION
SISTEMA:       ⚪ Fatturazione · ⚪ Fedeltà · ✅ Il tuo piano · ⚪ Stato sistema
```

### File chiave P1.0:
- `src/pages/Impostazioni.tsx` — riscrivere da zero (sidebar + useSearchParams)
- `src/hooks/use-impostazioni-status.ts` — NUOVO: query DB per stato configurazione
- `src/pages/Dashboard.tsx` — aggiungere quick setup banner
- Research: `.claude/cache/agents/p10-impostazioni-redesign-cove2026.md` (LEGGI PRIMA)

### 8 rename obbligatori (plain language):
| Attuale | Nuovo |
|---|---|
| Email SMTP | Email per le notifiche |
| SDI Fatturazione | Fatturazione elettronica |
| Voice Agent Sara | Sara — Receptionist AI |
| WhatsApp Auto-Responder | Risposte automatiche WhatsApp |
| WhatsApp QR Kit | Collega WhatsApp Business |
| FLUXION IA | Intelligenza artificiale FLUXION |
| Diagnostica | Stato del sistema |
| Licenza | Il tuo piano FLUXION |

### Dopo P1.0: P0.6 — Gmail OAuth2
- `tauri-plugin-oauth` + PKCE + keychain macOS
- Research: `.claude/cache/agents/p06-onboarding-gmail-cove2026.md` (LEGGI PRIMA)
- Trigger contestuale in Fornitori.tsx al primo invio ordine (NON nel wizard)

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
```

### cargo check iMac
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/src-tauri' && cargo check 2>&1 | grep -v 'DATABASE_URL\|E0282\|listini\|media' | tail -20"
```
