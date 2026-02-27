# LukeAgent — Deep Research CoVe 2026

**Ricercato:** 2026-02-27
**Dominio:** Agente personale AI — macOS OS-level + Telegram + Voice + Social Automation
**Confidenza Complessiva:** MEDIUM (stack verificato, ToS compliance richiede validazione legale)

---

## Executive Summary

LukeAgent e ZeroClaw (il tool dev CLI gia presente nel progetto) sono **complementari, non concorrenti**. ZeroClaw e un runtime sandboxato per agent dev workflow (Rust, <10ms startup, 3.4MB); LukeAgent mira all'OS-level automation, voice input, e marketing automation — un piano superiore nella gerarchia di controllo.

Il best-practice stack 2026 per un agente personale macOS con Telegram + voice e: **aiogram 3.x** (async Telegram), **faster-whisper** (STT locale), **SQLite** (storage primario, DuckDB opzionale per analytics), **LangGraph** (orchestrazione) o **Open Interpreter** (OS actions), **Ayrshare/API ufficiali** (social posting). Il modello whitelist Telegram e necessario ma non sufficiente — richiede mitigazioni aggiuntive (rate limiting, audit log, TOTP/2FA secret).

**Raccomandazione primaria:** Costruire LukeAgent in 2 fasi nette. Fase MVP (2-3 settimane): Telegram bot + faster-whisper + comandi sistema. Fase Expansion (4-6 settimane): social posting via API ufficiali + browser automation limitata. La full vision (creazione account, browser automation illimitata) porta rischi legali e di ban significativi — usare solo API ufficiali platform.

---

## Domanda 1: Maturita vs ZeroClaw — Complementari o Concorrenti?

### Risposta: COMPLEMENTARI — livelli diversi di astrazione

**ZeroClaw** (gia in uso nel progetto):
- Rust runtime agent per task dev: CLI sandboxato, 3.4MB, cold start <10ms
- Scope: ambienti CI/CD, automazione task dev, script code review
- Sandbox: profilo `.sb` macOS, nega accesso file system sensibili
- Confidenza: HIGH (verificato da MEMORY.md + security research gia nel progetto)

**LukeAgent** (progetto proposto):
- Python agent per uso personale: Telegram bot, voice commands, OS monitoring
- Scope: comandi sistema (RAM/disco/processi), social media, browser automation
- Livello: OS-level, NON sandboxato per default — richiede progettazione sicurezza dedicata

**Modello complementare raccomandato:**
```
ZeroClaw          → dev workflow, task CI/CD, ambienti sandboxati
LukeAgent         → personal automation, marketing, monitoring sistema
  └── puo INVOCARE ZeroClaw come strumento (es. "esegui test suite")
```

LukeAgent e concettualmente piu maturo di ZeroClaw in termini di scope (OS-level > dev CLI), ma richiede sforzo implementation piu alto e ha rischi di sicurezza maggiori. Non sostituisce ZeroClaw — lo complementa.

**Confidenza:** HIGH

---

## Domanda 2: Stack Tech — faster-whisper + Telegram + DuckDB per macOS 2026?

### Risposta: Stack parzialmente ottimale — con sostituzioni consigliate

#### STT: faster-whisper — CONFERMATO BEST-PRACTICE

**Status 2026:** faster-whisper e il riferimento standard per STT offline in Python.
- Gia in uso su FLUXION (FluxionSTT con Groq fallback) — riuso diretto del codice
- CPU-only su macOS Intel/Apple Silicon: ~30-60s per voce lunga, ~3-5s per comandi brevi
- Per comandi vocali brevi (10-15 parole), latenza accettabile anche su CPU
- Alterantiva: Groq Whisper API (gia integrata in FLUXION) per latenza ~200ms

**Raccomandazione STT:**
```python
# Riusa FluxionSTT da voice-agent/src/stt.py
# Primary: Groq Whisper (~200ms, richiede internet)
# Fallback: faster-whisper locale (3-5s, offline)
```

**Confidenza:** HIGH (gia verificato in produzione su FLUXION)

#### Telegram Bot Library: aiogram 3.x — RACCOMANDATO

| Library | Versione | Async | Features | Status 2026 |
|---------|----------|-------|----------|-------------|
| **aiogram** | 3.x (v3.25.0 Feb 2026) | SI, nativo | FSM integrato, middleware, type hints | ATTIVO |
| python-telegram-bot | 21.x | SI (v20+) | Stabile, documentazione ricca | ATTIVO |
| telebot (pyTelegramBotAPI) | 4.x | parziale | Semplice, sync-first | MENO ATTIVO |

**Scegliere aiogram 3.x** per:
- Full async con asyncio (compatible con faster-whisper async)
- FSM integrato (utile per dialoghi multi-step: "che comando vuoi?")
- Release febbraio 2026 — piu aggiornata al momento della ricerca
- Type hints completi (compatible con Python 3.10+)

**Installazione:**
```bash
pip install aiogram faster-whisper
```

**Confidenza:** HIGH (multiple fonti concordi, release date verificata)

#### Database: SQLite > DuckDB per agente personale

Per LukeAgent, SQLite e la scelta corretta:
- Comandi sistema = transazioni singole (INSERT log, UPDATE stato) → OLTP
- DuckDB e OLAP (analytics su milioni di righe) — overkill per agente personale
- SQLite: zero dipendenze, gia usato in FLUXION, nessun setup

**Usare DuckDB SOLO se:** vuoi analytics su log storici (es. "quante volte ho avviato X processo negli ultimi 30 giorni")

**Schema minimo SQLite:**
```sql
CREATE TABLE comandi_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    tipo TEXT NOT NULL,      -- 'voice'|'text'
    input TEXT NOT NULL,
    output TEXT,
    esito TEXT               -- 'ok'|'errore'
);
```

**Confidenza:** HIGH

---

## Domanda 3: Social Media Automation — ToS, Rischi, Soluzioni Legali

### Risposta: RISCHIO ALTO senza API ufficiali. Con API ufficiali: LEGALE ma a pagamento.

#### Situazione per piattaforma (2026):

| Piattaforma | API Ufficiale | Automazione POST | Account Ban Risk | Note |
|-------------|--------------|-----------------|------------------|------|
| **Instagram** | SI (Meta Graph API) | SI con approvazione app Meta | ALTISSIMO senza API ufficiale | App Meta richiede review processo |
| **LinkedIn** | SI (Marketing API) | SI per profili/pagine owned | ALTO senza Partner Program | Basic OK per profili personali |
| **TikTok** | SI (Content Posting API) | SI con app approvata | ALTO senza API | Richiede developer account |
| **Twitter/X** | SI (API v2) | SI ma a pagamento ($100/mese Basic) | BASSO con API | Free tier molto limitato |

#### Conseguenze violazione ToS Instagram:
- Primo warning: restriction temporanea 24-72h su azioni specifiche
- Violazioni ripetute: shadowban o disabilitazione permanente account
- Rischio legale: DMCA violations se scraping/reverse engineering (Meta ha precedenti legali)
- L'unica automazione sicura: attraverso official Meta Graph API con app approvata

#### Soluzione raccomandata: Ayrshare API

Ayrshare e il best-practice 2026 per social posting multi-piattaforma compliance:
- Integra direttamente con API ufficiali di ogni piattaforma
- Supporta: Instagram, LinkedIn, TikTok, Twitter/X, Facebook, YouTube, Pinterest, Threads
- Pricing 2026: Free (20 post/mese) | Premium $99/mese (illimitati)
- Compliance: GDPR, CCPA, politiche platform rispettate

**Per use case FLUXION marketing (volume basso):**
```python
import requests

def pubblica_post(testo: str, piattaforme: list, api_key: str):
    url = "https://app.ayrshare.com/api/post"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "post": testo,
        "platforms": piattaforme  # ["instagram", "linkedin"]
    }
    return requests.post(url, json=payload, headers=headers)
```

Free tier (20 post/mese) e sufficiente per marketing organico PMI.

**Alternativa open-source (rischio moderato):** Postiz (self-hosted) che usa API ufficiali

**NON usare:** Instabot, Selenium su Instagram, script follow/unfollow — violazione ToS diretta

**Confidenza:** HIGH per rischi, MEDIUM per pricing Ayrshare (verificato via search, non WebFetch diretto)

---

## Domanda 4: Browser Automation per Marketing — Playwright/Puppeteer su macOS

### Risposta: ALTO RISCHIO DI DETECTION. Usare con estrema cautela.

#### Stato detection 2026:
- Playwright e Puppeteer **entrambi rilevabili** da sistemi anti-bot moderni (Cloudflare, Akamai)
- Runtime.enable CDP method rilevabile da qualsiasi sito
- Dimensioni viewport non-standard (800x600 Puppeteer, 1280x720 Playwright) = fingerprint
- Stealth plugins (puppeteer-extra-plugin-stealth) parzialmente efficaci ma non garantiti
- Pixelscan, Cloudflare Bot Management: rilevano sessioni automatizzate anche con stealth

#### Casi d'uso sicuri vs rischiosi:

| Use Case | Rischio | Raccomandazione |
|----------|---------|-----------------|
| Scraping siti propri | BASSO | OK con Playwright |
| Automazione login propri account | BASSO-MEDIO | OK ma evitare IP dinamico |
| Creazione automatica account social | ALTISSIMO | NON FARE — ban immediato |
| Pubblicazione post su social via browser | ALTO | Usare API ufficiali invece |
| Ricerca competitiva (prezzi, testi) | MEDIO | OK con rate limiting |

#### Per uso personale macOS (es. form filling, download report):
```python
# Playwright Python — uso accettabile per task personali non-ToS violating
from playwright.async_api import async_playwright

async def task_personale():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False riduce detection
        page = await browser.new_page()
        await page.goto("https://example.com")
        # ...
```

**Regola d'oro:** Browser automation OK per siti/servizi propri o dove hai autorizzazione esplicita. Mai su piattaforme social per azioni che violano ToS.

**Confidenza:** HIGH (fonti multiple concordi, rebrowser-bot-detector verificato)

---

## Domanda 5: Architettura Consigliata CoVe 2026

### Risposta: Pattern "Lightweight Orchestrator + Tool Plugins"

#### Confronto framework:

| Framework | Pro | Contro | Adatto per LukeAgent? |
|-----------|-----|--------|----------------------|
| **LangGraph** | State machine, multi-agent, flessibile | Overhead setup, learning curve | SI per full vision |
| **Open Interpreter** | OS-level native, voice "01" project | Meno controllo, dipende da LLM cloud | SI per MVP rapido |
| AutoGPT | Self-prompting, autonomo | Loop senza guardrail, non maturo | NO |
| **Architettura custom** | Controllo totale, nessun overhead | Piu dev time | SI per caso FLUXION |

#### Architettura Raccomandata: Custom Lightweight Orchestrator

Per LukeAgent, date le dipendenze gia presenti in FLUXION:

```
lukeagent/
├── main.py                    # Entry point + Telegram bot (aiogram)
├── src/
│   ├── voice_handler.py       # STT: riusa FluxionSTT da voice-agent/
│   ├── command_router.py      # Intent → Tool dispatch
│   ├── tools/
│   │   ├── system_tools.py    # RAM, disco, processi (psutil)
│   │   ├── social_tools.py    # Ayrshare API wrapper
│   │   └── browser_tools.py   # Playwright per task sicuri
│   ├── memory.py              # SQLite log + contesto sessione
│   └── security.py            # Whitelist, rate limiting, audit log
├── config.yaml                # allowed_chat_ids, API keys env ref
└── tests/
    └── test_commands.py
```

#### Dipendenze Python:
```bash
pip install aiogram faster-whisper psutil ayrshare playwright
pip install langchain-core  # opzionale, per prompt templates
```

#### Pattern Command Router:
```python
# src/command_router.py
import re
from typing import Callable, Dict

COMMAND_PATTERNS: Dict[str, Callable] = {
    r"spazio disco|disk space": tools.system_tools.disk_usage,
    r"ram|memoria": tools.system_tools.ram_usage,
    r"processi|processes": tools.system_tools.top_processes,
    r"pubblica|posta|post": tools.social_tools.publish_post,
    r"apri|open": tools.browser_tools.open_url,
}

def route_command(text: str) -> Callable | None:
    text_lower = text.lower()
    for pattern, handler in COMMAND_PATTERNS.items():
        if re.search(pattern, text_lower):
            return handler
    return None
```

#### Confronto con Claude Computer Use:
Claude Computer Use (Claude Cowork) gira in container virtualizzato Apple Virtualization Framework — sicuro ma richiede abbonamento ($100/mese). Open Interpreter `--os` mode e alternativa free ma richiede LLM API (Groq OK). Per LukeAgent, la custom architecture e preferibile: massimo controllo, nessun costo abbonamento, riuso codice FLUXION.

**Confidenza:** HIGH per architettura, MEDIUM per confronto con Claude Cowork (non testato direttamente)

---

## Domanda 6: Sicurezza — Whitelist + allowed_chat_ids e Sufficiente?

### Risposta: NO — necessario ma non sufficiente. Aggiungere 5 layer.

#### OWASP Top 10 Agentic Applications 2026 — rischi applicabili:

| Rischio OWASP | Applicabilita LukeAgent | Mitigazione |
|---------------|------------------------|-------------|
| **AA1: Agent Behavior Hijacking** | ALTA — prompt injection via messaggi Telegram | Validazione input, no esecuzione testo user diretto |
| **AA2: Tool Misuse** | ALTA — comandi sistema pericolosi | Allowlist comandi esplicita, NON passare input raw a shell |
| **AA3: Identity/Privilege Abuse** | MEDIA — if Telegram account compromesso | 2FA Telegram + rate limiting |
| **AA4: Resource Exhaustion** | MEDIA — loop di comandi | Rate limiting per chat_id |
| **AA9: Prompt Injection** | ALTA — se LLM processa contenuto esterno | Sanitizzazione input |

#### Security Stack Minimo Raccomandato:

```python
# src/security.py

ALLOWED_CHAT_IDS = {int(id) for id in os.getenv("ALLOWED_CHAT_IDS", "").split(",")}
RATE_LIMIT: Dict[int, list] = {}  # chat_id → [timestamp, ...]
MAX_COMMANDS_PER_MINUTE = 10
DANGEROUS_PATTERNS = [
    r"rm\s+-rf", r"sudo", r"chmod\s+777",
    r"curl.*\|.*sh", r"wget.*\|.*bash",
    r";\s*rm", r"&&\s*rm"
]

def is_authorized(chat_id: int) -> bool:
    return chat_id in ALLOWED_CHAT_IDS

def is_rate_limited(chat_id: int) -> bool:
    now = time.time()
    timestamps = RATE_LIMIT.get(chat_id, [])
    recent = [t for t in timestamps if now - t < 60]
    RATE_LIMIT[chat_id] = recent
    if len(recent) >= MAX_COMMANDS_PER_MINUTE:
        return True
    RATE_LIMIT[chat_id].append(now)
    return False

def contains_dangerous_pattern(text: str) -> bool:
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def audit_log(chat_id: int, command: str, result: str):
    # Scrive su SQLite + notifica Telegram canale dedicato
    pass
```

#### 5 Layer di Sicurezza:

1. **Layer 1 — Identity**: `allowed_chat_ids` (necessario, NON sufficiente da solo)
2. **Layer 2 — Rate Limiting**: max 10 comandi/minuto per chat_id
3. **Layer 3 — Command Allowlist**: solo comandi espliciti permessi (NO shell raw)
4. **Layer 4 — Input Sanitization**: blocca pattern shell injection, prompt injection
5. **Layer 5 — Audit Log**: ogni comando loggato su SQLite + alert su canale Telegram separato

**Principio Least-Agency (OWASP 2026):** l'agente NON deve avere sudo, NON deve poter eseguire shell arbitraria, NON deve avere accesso a `~/.ssh`, `~/.aws`, Keychain.

**Token Telegram:** Mai hardcodato nel codice. Usare `.env` con `python-dotenv` o variabile d'ambiente gestita da Tauri/launch script.

**Confidenza:** HIGH (OWASP 2026 verificato, pattern security da fonti multiple)

---

## Valutazione: LukeAgent vs ZeroClaw — Chi e Piu Maturo?

### Risposta: Concetti diversi, comparazione non diretta

```
Maturita del CONCETTO:
  ZeroClaw   = tool dev maturo, scope ristretto, gia in produzione su FLUXION
  LukeAgent  = concept ampio, scope OS-level, NON ancora implementato

Maturita dell'ECOSISTEMA supportante:
  ZeroClaw   = Rust ecosystem maturo (Cargo, tokio)
  LukeAgent  = Python ecosystem MOLTO maturo (aiogram, faster-whisper, psutil)

Complessita di implementazione:
  ZeroClaw   = gia implementato/integrato
  LukeAgent  = MVP 2-3 settimane, full vision 6-8 settimane

Rischi:
  ZeroClaw   = sandboxato, rischio basso
  LukeAgent  = OS-level, social automation → rischio medio-alto se non progettato bene
```

LukeAgent non e "piu maturo" — e uno scope completamente diverso. E un OS agent personale; ZeroClaw e un dev automation tool. La domanda corretta e: "LukeAgent aggiunge valore sopra ZeroClaw?" → SI, per tutto cio che non e dev workflow.

---

## Architettura Raccomandata CoVe 2026 — Schema Finale

```
┌─────────────────────────────────────────────────────────────┐
│                     LUKEAGENT                               │
├──────────────┬──────────────────────┬───────────────────────┤
│  INPUT LAYER │  ORCHESTRATION LAYER │  ACTION LAYER         │
│              │                      │                        │
│  Telegram    │  Command Router      │  System Tools          │
│  (aiogram)   │  (regex + intent)    │  (psutil, subprocess) │
│              │                      │                        │
│  Voice       │  Security Gate       │  Social Tools          │
│  (faster-    │  (whitelist +        │  (Ayrshare API)        │
│   whisper)   │   rate limit +       │                        │
│              │   sanitization)      │  Browser Tools         │
│  Text CLI    │                      │  (Playwright — safe)   │
│  (opzionale) │  Memory (SQLite)     │                        │
│              │  Audit Log           │  ZeroClaw Bridge       │
│              │                      │  (opzionale, dev tasks)│
└──────────────┴──────────────────────┴───────────────────────┘
```

**LLM Integration (opzionale per MVP):**
- Groq API (gia presente in FLUXION) per intent classification NL→comando
- Senza LLM: pure regex command matching (piu veloce, piu sicuro per MVP)

---

## Rischi e Mitigazioni

| Rischio | Probabilita | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Account Instagram bannato per automation non-API | ALTA | ALTO | Usare SOLO Ayrshare/API ufficiali |
| Telegram token esposto (come PAT GitHub nel progetto) | MEDIA | ALTO | .env file, git pre-commit hook check |
| Prompt injection via messaggio Telegram | MEDIA | MEDIO-ALTO | Input sanitization + command allowlist |
| Comando shell pericoloso eseguito per errore | BASSA (se progettato bene) | MOLTO ALTO | MAI eseguire shell raw, allowlist esplicita |
| LukeAgent usato da terzi (se token/bot compromesso) | BASSA | ALTO | 2FA Telegram + rate limit + alert |
| Playwright detection → ban su sito terzo | MEDIA | BASSO | headless=False + solo siti propri |

---

## Stima Effort

### Fase MVP (2-3 settimane, ~40-50 ore)

| Task | Effort |
|------|--------|
| Setup aiogram bot + whitelist security | 4h |
| Integrazione faster-whisper (riuso da FLUXION) | 2h |
| Command router (regex, 5-10 comandi sistema) | 6h |
| System tools: RAM, disco, processi (psutil) | 4h |
| SQLite audit log + rate limiting | 4h |
| Test suite (pytest, mock Telegram) | 6h |
| Deploy su macOS (launchd service) | 4h |
| **Totale MVP** | **~30h** |

**Deliverable MVP:** Bot Telegram risponde a voce/testo, comandi sistema, sicuro, loggato.

### Fase Expansion (4-6 settimane aggiuntive, ~80-100 ore)

| Task | Effort |
|------|--------|
| Integrazione Ayrshare API (social posting) | 8h |
| Template post con tono di voce (LLM prompt) | 6h |
| Playwright browser automation (task sicuri) | 12h |
| Dashboard analytics DuckDB (opzionale) | 10h |
| Integrazione LangGraph per task complessi | 16h |
| Test E2E + sicurezza pentest basico | 12h |
| **Totale Expansion** | **~64h** |

### Full Vision (creazione account, automation avanzata)

NON RACCOMANDATO come priorita. Rischi legali ToS significativi. Stimato 3-6 mesi, ROI incerto. Rimandare a dopo validazione MVP.

---

## Open Questions

1. **Scope "creazione account automatica"**: Questo e quasi certamente violazione ToS di ogni piattaforma social. Richiede decisione esplicita prima di procedere. Raccomandazione: escluderlo dalla roadmap, usare account esistenti via API ufficiali.

2. **Integrazione con FLUXION**: LukeAgent deve avere accesso al DB SQLite di FLUXION? Se si, definire interfaccia read-only vs read-write per sicurezza.

3. **Tono di voce sui social**: Richiede curazione manuale o LLM? Se LLM (Groq), costo per post da considerare. Template fissi piu sicuri e piu economici per MVP.

4. **macOS launchd vs Docker**: Per deployment stabile su iMac, launchd service e piu integrato. Docker aggiunge isolamento. Decisione da prendere prima di deployment.

---

## Fonti

### PRIMARY (HIGH confidence)
- Ricerca OWASP Top 10 Agentic Applications 2026 — genai.owasp.org (verificato multiple fonti)
- aiogram 3.x documentation — aiogram.dev (release Feb 2026 verificata)
- Instagram ToS e help center ufficiale — help.instagram.com (estratto diretto)
- FLUXION MEMORY.md + CLAUDE.md — voice-agent/src/ stack gia verificato in produzione

### SECONDARY (MEDIUM confidence)
- Ayrshare pricing/features — ayrshare.com via search (non WebFetch diretto per permessi)
- ZeroClaw architecture — zeroclaw.net + medium articles (coerenti tra loro)
- Open Interpreter features — github.com/openinterpreter + openinterpreter.com
- DuckDB vs SQLite comparison — datacamp.com + analyticsvidhya.com (concordi)

### TERTIARY (LOW confidence)
- "OpenClaw" references nei risultati search — termine ambiguo, usato per piu prodotti diversi
- Claude Cowork pricing $100/mese — non verificato con WebFetch diretto
- Playwright detection rates 2026 — dati aneddotici da blog, non benchmark formali

---

## Metadata

**Confidence breakdown:**
- ZeroClaw vs LukeAgent complementarity: HIGH — logica architetturale + ricerca
- Stack tech (aiogram, faster-whisper): HIGH — fonti primarie + uso esistente in FLUXION
- Social ToS risks: HIGH — documentazione ufficiale Meta + casi legali noti
- Browser automation risks: HIGH — fonti tecniche multiple concordi
- Security model: HIGH — OWASP 2026 ufficiale
- Effort estimates: MEDIUM — basati su esperienza stack FLUXION, non benchmark esterni

**Research date:** 2026-02-27
**Valid until:** 2026-05-27 (90 giorni — ToS social media cambiano frequentemente, verificare prima di implementation)
