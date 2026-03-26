# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: PMI italiane 1-15 dip. (saloni, palestre, cliniche, officine)
- **Model**: Licenza LIFETIME desktop — NO SaaS, NO commissioni, 0% booking fee
- **Voice**: "Sara" — voice agent prenotazioni 24/7, 5-layer RAG, 23 stati FSM
- **License**: Ed25519 offline — Base €497 / Pro €897 (lifetime, no SaaS, NO download gratuito)

## I 3 Pilastri
📱 **COMUNICAZIONE** (WhatsApp + Voice) · 🎯 **MARKETING** (Loyalty + Pacchetti) · ⚙️ **GESTIONE** (Calendario + Schede)
> Questi 3 pilastri devono essere PERFETTI.

---

## ⚡ WORKFLOW OBBLIGATORIO: GSD + CoVe 2026

### 🗺️ START DI OGNI SESSIONE
```
1. Leggi HANDOFF.md → identifica fase corrente
2. Leggi ROADMAP_REMAINING.md → prendi prima fase ⏳
3. Esegui /gsd:plan-phase se la fase non ha PLAN.md
4. Esegui /gsd:execute-phase per implementare
5. Fine sessione: aggiorna ROADMAP_REMAINING.md + HANDOFF.md + MEMORY.md
```

### 📋 GSD FASI SISTEMATICHE (NON NEGOZIABILE)
- `/gsd:plan-phase` — prima di OGNI feature significativa (>30min)
- `/gsd:execute-phase` — esecuzione con commit atomici
- `/gsd:verify-work` — validazione UAT prima di "done"
- `/gsd:pause-work` — se sessione interrotta a metà

### ⚡ PROTOCOLLO CoVe 2026 (dentro ogni fase GSD)

**FASE 0 — SKILL IDENTIFICATION** (OBBLIGATORIA — prima di tutto, NON NEGOZIABILE)
- Identifica la **skill enterprise-grade Claude Code** più adatta al task/bug
- Skills disponibili: `fluxion-voice-agent`, `fluxion-tauri-architecture`, `fluxion-build-verification`, `fluxion-git-workflow`, `fluxion-service-rules`, `fluxion-workflow`, `fluxion-nodejs-setup`, `fluxion-mcp-core`
- Se nessuna skill copre il task → **CREA una skill apposita** con documentazione ufficiale Anthropic (https://docs.anthropic.com/claude-code/custom-skills) oppure usa `general-purpose` Agent con prompt specializzato
- **MAI procedere senza aver identificato o creato la skill corretta**
- **OGNI task (anche <30min) deve avere una skill assegnata** — nessuna eccezione
- Skill non trovata nelle defaults? → Deep research CoVe 2026 per trovare lo standard enterprise mondiale → creare skill custom dedicata

**FASE 1 — DEEP RESEARCH CoVe 2026** (subagenti in parallelo, MAI inline)
- Lancia **2+ subagenti** in parallelo (Agent tool, `run_in_background: true`):
  - **Agente A**: Benchmark leader mondiali (Fresha, Mindbody, Nuance, Retell, Vapi, etc.)
  - **Agente B**: Analisi codebase attuale + gap analysis vs gold standard
- Ogni agente scrive in `.claude/cache/agents/[task]-cove2026.md`
- Se research file esiste già e recente: leggi e procedi direttamente
- **Aspetta il completamento** prima di procedere a PLAN

**FASE 2 — PLAN**
- Leggi research → identifica edge case → acceptance criteria MISURABILI
- Schema DB changes documentati prima di qualsiasi SQL/Rust
- Verifica: "È il gold standard mondiale 2026?" — se no, riprogetta

**FASE 3 — IMPLEMENT**
- Un commit per feature atomica — TypeScript strict (zero `any`, `@ts-ignore`)
- Zero `--no-verify` — MAI, in nessun caso
- Usa subagenti per implementazioni complesse (Agent tool con `isolation: worktree`)

**FASE 4 — VERIFY**
- `npm run type-check` → 0 errori — confronto vs acceptance criteria

**FASE 5 — DEPLOY**
- `git push origin master` + sync iMac + update ROADMAP_REMAINING.md

**Task NON è completato finché tutte le 5 fasi (0→4) non sono verificate.**

### 🤖 REGOLA SUBAGENTI (NON NEGOZIABILE)
> Per OGNI task/bug significativo (>15min), il flusso obbligatorio è:
> **Skill ID → SubAgent Research (parallelo) → Plan → SubAgent Implement → Verify**
>
> ❌ MAI implementare direttamente senza research subagente
> ❌ MAI fare research inline (nel main context) — sempre subagente
> ✅ SEMPRE lanciare almeno 2 subagenti in parallelo per research
> ✅ SEMPRE scrivere output research in `.claude/cache/agents/`

### 🔥 PROCESSO ESECUZIONE COMPLETO (NON NEGOZIABILE — IMPRESSO A FUOCO)

```
FASE 1 — RESEARCH:  Skill Agents specializzati (.claude/agents/) in parallelo
                     Ogni agente scrive in .claude/cache/agents/
                     MAI general-purpose se esiste un agente specializzato
                     Agent Studio: 58 agenti in 15 dipartimenti → USARLI TUTTI

FASE 2 — PLANNING:  GSD workflow (/gsd:plan-phase, /gsd:new-milestone)
                     Basato sui dati della research — MAI "a braccio"
                     Acceptance criteria MISURABILI per ogni task

FASE 3 — IMPLEMENT: Skill Agents specializzati per implementazione
                     Commit atomici, TypeScript strict, zero any
                     /gsd:execute-phase per tracciamento

FASE 4 — REVIEW:    /fluxion-code-review dopo OGNI implementazione
                     Code review enterprise-grade 12 dimensioni
                     Fix immediato di ogni finding CRITICAL/HIGH

FASE 5 — VERIFY:    /gsd:verify-work UAT per ogni fase
                     Confronto vs acceptance criteria
                     npm run type-check → 0 errori

FASE 6 — DEPLOY:    git push + sync iMac + update ROADMAP + HANDOFF + MEMORY
```

**ORDINE NON NEGOZIABILE: RESEARCH → GSD PLAN → SKILL IMPLEMENT → CODE REVIEW → VERIFY → DEPLOY**
**MAI saltare una fase. MAI. Il fondatore lo ha detto chiaro: "Imprimilo a fuoco."**

### 📦 AGENT STUDIO — 58 Agenti Specializzati
> `.claude/agents/INDEX.md` — LEGGERE SEMPRE prima di scegliere un agente
> 15 dipartimenti: engineering, voice, video, marketing, sales, design, verticals,
> distribution, infrastructure, whatsapp, customer-success, project-management, studio-operations, testing
> **REGOLA**: USA l'agente del dipartimento giusto, NON general-purpose se ne esiste uno dedicato

---

## 🏆 MISSIONE (NON NEGOZIABILE)
**FLUXION deve essere il MIGLIOR strumento mondiale per PMI italiane.**
Ogni task, ogni feature, ogni scheda deve essere progettata per battere qualsiasi concorrente.
Prima di implementare qualsiasi cosa: deep research CoVe 2026 per trovare lo stato dell'arte mondiale.

### Deep Research CoVe 2026 — OBBLIGATORIO per OGNI task
Per ogni feature/task significativo (>30min):
1. **Benchmarka i leader mondiali** — cosa fa il miglior competitor? (Fresha, Mindbody, Jane App, etc.)
2. **Identifica i gap** — cosa manca nei competitor che noi possiamo fare meglio?
3. **Definisci "world-class"** — qual è il gold standard per questa feature nel 2026?
4. **Implementa sopra lo standard** — non copiare, supera.

> "Non siamo qui per fare uno strumento decente. Siamo qui per fare IL migliore." — CTO

---

## 2 GUARDRAIL — NON NEGOZIABILI

### GUARDRAIL 1: ZERO COSTI
Tutto deve costare €0. Se sembra impossibile, trova il modo. Esiste SEMPRE un'alternativa gratuita enterprise-grade.
- Cloudflare (Workers, Pages, Tunnel, D1, KV) — free tier copre tutto
- GitHub (Releases, Actions, Pages) — free per repo pubblici
- Stripe Checkout (1.5% EU cards — minimo assoluto, viene dal ricavo non dalla tasca)
- Edge-TTS, Piper, Groq/Cerebras free tier — zero costi voce/LLM
- Ad-hoc codesign macOS, MSI unsigned Windows — zero certificati a pagamento
- **Se qualcuno propone una soluzione a pagamento → RIFIUTA e trova quella gratuita**

### GUARDRAIL 2: ENTERPRISE GRADE
Tutto deve essere il gold standard mondiale. Se sembra impossibile, trova il modo. Enterprise e gratuito coesistono SEMPRE.
- Zero `any` TypeScript, zero `--no-verify`, zero `console.log` in prod
- HTTPS sempre, WAL mode, backup automatici, signature verification
- UX che batte Fresha/Mindbody su ogni schermata
- Soluzioni permanenti (sopravvivono a riavvii), auditabili, event-driven
- **Se qualcuno propone un workaround temporaneo → RIFIUTA e implementa lo standard**

> **"Tutto si può fare. Basta solo trovare il modo."** — Fondatore S103
> Research: `.claude/cache/agents/delivery-pipeline-indie-research-2026.md`, `cto-playbook-indie-2026.md`

---

## Critical Rules
1. Mai commit API keys / .env — mai `--no-verify`
2. TypeScript sempre (no JS), async Tauri commands, zero `any`
3. **Deep Research CoVe 2026 PRIMA di implementare** — stato dell'arte mondiale, non solo funzionale
4. Task COMPLETATO solo se verificato (type-check + acceptance criteria)
5. Field names API italiani: `servizio`, `data`, `ora`, `cliente_id`
6. Dev MacBook — Rust/build solo su iMac (192.168.1.2) via SSH
7. Riavvio voice pipeline iMac dopo OGNI modifica Python

---

## 🔒 ARCHITETTURA DISTRIBUZIONE FLUXION — DECISIONI DEFINITIVE (S84, 2026-03-18)

> **Queste decisioni sono PERMANENTI. Deep research CoVe 2026 completata con 4 subagenti.**
> Research files: `.claude/cache/agents/tts-crossplatform-install-research.md`,
> `llm-api-onboarding-research.md`, `install-compatibility-research.md`

### 🎙️ TTS — Architettura 3-Tier Definitiva

| Tier | Engine | Qualità | Latenza | Requisiti | Piattaforme |
|------|--------|---------|---------|-----------|-------------|
| **QUALITY** | Edge-TTS (IsabellaNeural) | 9/10 | ~500ms TTFB | Internet | Win + Mac |
| **FAST/OFFLINE** | Piper TTS (it_IT-paola-medium) | 7/10 | ~50ms | Nessuno | Win + Mac |
| **LAST RESORT** | SystemTTS (macOS `say` / Win SAPI5) | 5/10 | ~400ms | Nessuno | Nativo OS |

**Selezione automatica al primo avvio (Setup Wizard):**
```
Internet disponibile?
  SÌ → Edge-TTS (quality) + Piper fallback offline
  NO → Piper (fast) + SystemTTS fallback
```

**HW Detection + Auto-Selection:**
```
PC capace (≥8GB RAM, ≥4 core, internet):
  → DEFAULT: Edge-TTS IsabellaNeural (quality 9/10)
  → FALLBACK: Piper (se internet cade, auto-switch)
  → LAST RESORT: SystemTTS

PC datato (<8GB RAM o senza internet stabile):
  → DEFAULT: Piper (fast, offline, ~50ms)
  → FALLBACK: SystemTTS
```

**Voce approvata CTO (S76):** Serena (Qwen3-TTS) resta la voce IDEALE.
Quando Qwen3-TTS diventerà praticabile su CPU (<500ms) o quando i clienti avranno GPU,
sarà aggiunto come tier PREMIUM sopra Edge-TTS. Per ora: Edge-TTS IsabellaNeural.

**Download automatico modelli:**
- Piper `it_IT-paola-medium.onnx` (~55MB) → scaricato al primo avvio con progress bar
- Edge-TTS: zero download, streaming diretto
- Checksum SHA256 verificato, retry automatico, resume download

### 🧠 LLM/NLU — Architettura Zero-Config

**DECISIONE: FLUXION Proxy API** (raccomandazione research unanime)

Il cliente PMI **NON deve MAI**:
- Creare account su Groq/Cerebras/OpenRouter
- Gestire API key
- Capire cosa è un "LLM"

**Architettura:**
```
FLUXION App (client) → FLUXION Proxy API (Cloudflare Workers) → Groq/Cerebras
                              ↑
                    Auth: license key Ed25519
                    Rate limit: 200 call NLU/giorno per licenza
                    Costo: €0 (Groq+Cerebras free tier copre centinaia di clienti)
```

**Fallback chain LLM:**
```
1. FLUXION Proxy → Groq llama-3.1-8b-instant (primary, 14.400 RPD)
2. FLUXION Proxy → Cerebras (fallback, 1M TPD)
3. Template NLU locale (offline, zero API, qualità ridotta ma funzionale)
```

**Opzione avanzata (Impostazioni > Avanzate):**
- BYOK (Bring Your Own Key) per utenti tecnici che vogliono key propria
- Disabilita proxy, usa key diretta → zero dipendenza da FLUXION infra

**Comunicazione al cliente:**
> "Sara è inclusa nella licenza. Funziona subito, senza configurazione."
> "Nessun costo aggiuntivo, nessun abbonamento."

### 💳 PAGAMENTO + LICENZE — Stripe + Ed25519 (ZERO piattaforma)

**DECISIONE S103: LemonSqueezy RIMOSSO — Stripe Checkout diretto**

```
Cliente clicca "Acquista" (landing/in-app)
  → Stripe Checkout (hosted, PCI-compliant, 1.5% EU cards)
  → Pagamento OK → webhook POST a CF Worker /webhook/stripe
  → CF Worker firma license key Ed25519 (PRIVATE key in secret)
  → CF Worker invia email con key + download link (Resend free tier)
  → Cliente installa → wizard → incolla key → verifica offline Ed25519
  → Fatto. Zero piattaforma, zero intermediari.
```

**Tier DEFINITIVO (S103 — NON NEGOZIABILE):**
- **NON esiste download gratuito** — il cliente PAGA prima di scaricare
- **Base €497**: gestionale + WA + Sara 30gg trial
- **Pro €897**: 1 nicchia specifica + Sara per sempre
- **SEMPRE 1 sola nicchia** — una PMI = un'attività
- Sara trial Base: 30 giorni → si blocca → reminder upgrade Pro
- Durante il trial: proponi EHIWEB VoIP con copy eloquente + link attivazione semplice
- Key contiene email cliente → visibile in app ("Licenziato a: mario@rossi.com")
- MAI blocco totale del gestionale — solo Sara si blocca

**Infra necessaria (tutta gratuita):**
- Stripe account (0 costi fissi, solo % su vendite)
- CF Worker webhook route (già attivo `fluxion-proxy`)
- Resend free tier (3000 email/mese) per delivery licenze
- GitHub Releases per hosting binari (CDN globale, illimitato)
- Ed25519 PRIVATE key come CF Worker secret

### 💻 COMPATIBILITÀ — Requisiti Sistema DEFINITIVI

**Requisiti Minimi (da comunicare OVUNQUE: landing, checkout, installer, guida):**

| | Minimo | Consigliato |
|--|--------|-------------|
| **OS Windows** | Windows 10 64-bit (April 2018+) | Windows 11 |
| **OS macOS** | macOS 12 Monterey | macOS 14 Sonoma+ |
| **CPU** | x86-64 con SSE2 / Apple Silicon | Intel i3-8100+ / M1+ |
| **RAM** | 4 GB (senza Sara) / **8 GB (con Sara)** | 16 GB |
| **Disco** | 2 GB liberi | SSD, 5 GB liberi |
| **Schermo** | 1366×768 | 1920×1080 |
| **Internet** | Per installazione + Sara voice | Banda ≥10 Mbps |

**IMPORTANTE:** Calendario, clienti, schede, cassa funzionano ANCHE OFFLINE.
Solo Sara (voice + NLU) richiede internet per qualità ottimale, con fallback offline.

### 📦 DISTRIBUZIONE — Code Signing + Bundling

**Code Signing — ZERO COSTI:**
- **macOS**: ad-hoc signing (`codesign --sign -`) + pagina "Come installare" con 3 click Gatekeeper
- **Windows**: MSI unsigned + pagina SmartScreen "Esegui comunque"
- **Costo**: €0 — pagina istruzioni visive riduce ticket 80%+ (benchmark Calibre, Obsidian pre-signing)

**Python Voice Agent Bundling:**
- PyInstaller compila voice agent in binario nativo (sidecar Tauri)
- L'utente finale **NON installa Python** — tutto è nel pacchetto
- Naming: `voice-agent-x86_64-pc-windows-msvc.exe` / `voice-agent-aarch64-apple-darwin`
- Config: `"externalBin": ["binaries/voice-agent"]` in tauri.conf.json
- Bundle size target: ~520MB (ottimizzato, senza torch/spaCy legacy)

**macOS Universal Binary (OBBLIGATORIO):**
- `npm run tauri build -- --target universal-apple-darwin`
- Copre Intel + Apple Silicon in un unico .app

**Windows Installer:**
- Preferire MSI over NSIS (meno false positive antivirus)
- `installMode: "both"` per supporto PC aziendali senza admin
- WebView2: bootstrapper incluso (1.8MB), auto-download se mancante

### ⚠️ PROBLEMI NOTI + MITIGAZIONI

| Problema | Piattaforma | Mitigazione |
|----------|-------------|-------------|
| SmartScreen "Publisher unknown" | Windows | Pagina istruzioni "Esegui comunque" + VirusTotal pre-release |
| Antivirus false positive | Windows | MSI installer + submit VirusTotal pre-release |
| Gatekeeper blocca app | macOS | Pagina istruzioni "Apri comunque" (3 click) |
| Sleep/Wake frontend reload | Windows 11 | Persistenza stato in SQLite + health check |
| AV scansiona SQLite → locking | Windows | WAL mode + retry logic |
| VPN/Proxy blocca API | Tutti | Diagnostica primo avvio + proxy support |
| CPU senza AVX (pre-2013) | Windows | onnxruntime SSE2 baseline, 3x più lento ma funziona |
| OneDrive sync locka DB | Windows | Installare in %LOCALAPPDATA% (fuori sync) |

### 📋 DISCLAIMER — Comunicazione Pre-Acquisto

**Su landing page + checkout (OBBLIGATORIO):**

> **Requisiti sistema:** Windows 10+ / macOS 12+ · 8 GB RAM consigliati · 2 GB disco
>
> **Sara (assistente vocale) richiede connessione internet.**
> Calendario, clienti, schede e cassa funzionano anche offline.
>
> **Servizi inclusi, zero costi nascosti.**
> Sara utilizza tecnologie di intelligenza artificiale incluse nella licenza FLUXION.
> Nessun abbonamento, nessun costo aggiuntivo. I servizi AI sono gratuiti
> finché disponibili; in caso di variazioni, FLUXION attiva automaticamente
> servizi alternativi senza alcun intervento da parte dell'utente.
>
> **Garanzia 30 giorni** soddisfatti o rimborsati.

**Footer legale (termini e condizioni):**

> FLUXION utilizza servizi cloud di terze parti per l'assistente vocale Sara.
> Tali servizi sono inclusi senza costi aggiuntivi per l'utente.
> In caso di indisponibilità di un servizio, il software attiva automaticamente
> servizi alternativi. Le funzionalità base (calendario, gestione clienti,
> fatturazione) funzionano sempre, anche in assenza di connessione internet.

### 🏥 DIAGNOSTICA + SELF-HEALING

**Health check primo avvio (automatico, pre-wizard):**
1. WebView2 presente (Windows) → installa se mancante
2. Internet raggiungibile → warning se assente
3. RAM sufficiente → warning se <4GB, suggerimento se <8GB
4. Spazio disco → warning se <1GB libero
5. Microfono disponibile → opzionale, per STT live

**Self-healing voice pipeline:**
- Health check ogni 30s su `/health`
- 3 fallimenti consecutivi → kill + restart sidecar + notifica utente
- Log: JSON Lines in `%LOCALAPPDATA%\Fluxion\logs\` (Win) / `~/Library/Logs/Fluxion/` (Mac)
- Rotazione: 5 file × 10MB

**Pagina diagnostica in-app (già parzialmente in DiagnosticsPanel):**
- Stato TTS (engine attivo, latenza media)
- Stato LLM (provider attivo, latenza, errori ultimi 24h)
- Stato internet + API raggiungibilità
- RAM/CPU/disco
- Bottone "Invia diagnostica a supporto FLUXION"

### 🗓️ SPRINT DISTRIBUZIONE (da completare PRIMA di prima vendita)

**SPRINT 0 — Bloccanti (priorità ASSOLUTA):**
1. [x] PyInstaller sidecar build (voice agent → binario nativo) — DONE S102
2. [x] Ad-hoc codesign macOS — DONE S102
3. [ ] Pagina "Come installare FLUXION" (Gatekeeper + SmartScreen istruzioni visive)
4. [ ] Universal Binary macOS (Intel + Apple Silicon)
5. [ ] Windows MSI build (WiX)

**SPRINT 1 — UX Installazione:**
6. [ ] FLUXION Proxy API (Cloudflare Workers + Groq backend)
7. [ ] Health check primo avvio automatico
8. [ ] Self-healing voice pipeline (restart su crash)
9. [ ] Wire Edge-TTS + Piper fallback chain
10. [ ] Setup Wizard: HW detection → TTS auto-selection + model download

**SPRINT 2 — Polish:**
11. [ ] Cleanup requirements.txt (rimuovere torch/spaCy legacy)
12. [ ] Log strutturati cross-platform
13. [ ] Pagina diagnostica completa
14. [ ] Responsive layout 1366×768
15. [ ] Landing + Stripe Checkout: allineare requisiti e disclaimer

### 📚 Research Files (S84)
- **TTS Cross-Platform**: `.claude/cache/agents/tts-crossplatform-install-research.md`
- **LLM/API Onboarding**: `.claude/cache/agents/llm-api-onboarding-research.md`
- **Install Compatibility**: `.claude/cache/agents/install-compatibility-research.md`

---

## Stato Progetto (2026-03-04 — sessione 16)
```
branch: master | v1.0.0 ✅
Voice Sara: 1160 PASS / 0 FAIL ✅
iMac SSH: 192.168.1.2 ✅
Pricing: Base €497 (gestionale + WA + Sara 30gg trial) / Pro €897 (1 nicchia + Sara sempre)
```

## Task Queue → ROADMAP_REMAINING.md
> **SEMPRE leggere ROADMAP_REMAINING.md per la fase corrente.**
> Non modificare questa sezione — tutto è in ROADMAP_REMAINING.md.

| Fase | Task | Status |
|------|------|--------|
| F01 | Click-to-sign contratto SetupWizard | 🔄 IN PROGRESS |
| F02 | Vertical system Sara | ⏳ |
| F03 | Latency optimizer | ⏳ |
| F04 | Schede mancanti | ⏳ |
| F07 | Stripe Checkout + License Delivery | ⏳ |

## Comandi Rapidi
```bash
# TypeScript check (MacBook — SEMPRE prima di commit)
npm run type-check

# Test voice (iMac)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && python -m pytest tests/ -v --tb=short 2>&1 | tail -20"

# Sync iMac
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"

# Riavvio voice pipeline iMac
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"

# Verifica T1-T5 via curl (quando iMac attivo)
curl -s http://192.168.1.2:3002/health
curl -s -X POST http://192.168.1.2:3002/api/voice/process -H "Content-Type: application/json" -d '{"text":"Buongiorno, vorrei prenotare un appuntamento"}' | python3 -m json.tool
```

## Verticali
6 macro × 17 sotto-verticali | Fonte: `src/types/setup.ts` + `.claude/cache/agents/sub-verticals-research.md`

## CoVe 2026 Research Files
- **SDI FatturaPA**: `.claude/cache/agents/sdi-fatturapa-research.md`
- **Operatori features**: `.claude/cache/agents/operatori-features-cove2026.md` ✅
- **Landing conversion**: `.claude/cache/agents/landing-conversion-research.md`
- **Voice testing**: `.claude/cache/agents/voice-testing-methodology.md`
- **Skill prompts**: `.claude/cache/agents/cove2026-skill-prompts.md`

## Documentazione
- **PRD**: `PRD-FLUXION-COMPLETE.md` ⭐
- **Voice Agent**: `.claude/rules/voice-agent-details.md`
- **Verticali research**: `.claude/cache/agents/sub-verticals-research.md`

## Strumenti CI/CD
- **Code review automatico su GitHub con Max** (zero costo aggiuntivo):
  https://github.com/anthropics/claude-code-action
  GitHub Action ufficiale Anthropic — funziona con API key propria o con Max tramite Claude Code.

## Risorse Claude Code Skills & Ecosystem
> Riferimenti per skill, pattern e integrazioni enterprise-grade.
> **REGOLA**: Valutare SEMPRE la skill migliore per il task specifico prima di procedere.

| Risorsa | URL | Uso |
|---------|-----|-----|
| Superpowers | https://github.com/obra/superpowers | Skill avanzate Claude Code |
| Awesome Claude Code | https://github.com/hesreallyhim/awesome-claude-code | Catalogo curato risorse |
| GSD (Get Shit Done) | https://github.com/gsd-build/get-shit-done | Workflow esecuzione fasi |
| Claude Mem | https://github.com/thedotmack/claude-mem | Memory management persistente |
| UI UX Pro Max | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill | Skill UI/UX enterprise |
| n8n-MCP | https://github.com/czlonkowski/n8n-mcp | Automazione workflow MCP |
| Obsidian Skills | https://github.com/kepano/obsidian-skills | Pattern skill Obsidian |
| LightRAG | https://github.com/hkuds/lightrag | RAG leggero per retrieval |
| Everything Claude Code | https://github.com/affaan-m/everything-claude-code | Guida completa Claude Code |
| Spec Kit (GitHub) | https://github.com/github/spec-kit | Toolkit specifiche GitHub |
