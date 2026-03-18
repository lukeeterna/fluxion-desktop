# ARGOS AUTOMOTIVE — Specifiche Integrazione per Fluxion
## Lead Generation + Dashboard + Sales Agent + TTS Voice Stack

**Data**: 2026-03-18 | **Autore**: CTO ARGOS (Claude Opus 4.6)
**Regola**: TUTTI i file ARGOS referenziati sono in SOLA LETTURA. MAI modificare.

---

## 1. COS'E' ARGOS

ARGOS Automotive e' un sistema B2B di vehicle scouting EU→IT. Trova veicoli premium (BMW/Mercedes/Audi 2018-2023) dai mercati europei (DE/BE/NL/AT/FR/SE/CZ) e li propone a concessionari italiani family-business del Sud Italia (30-80 auto in stock). Fee: €800-1.200 a success, zero anticipi.

**Persona**: Luca Ferretti, Vehicle Sourcing Specialist, basato a Bruxelles.
**Target**: Concessionari family-business Sud Italia.
**Stato**: 8 dealer in pipeline zona Salerno, Day 1 inviato a 2 dealer.

---

## 2. ARCHITETTURA COMPLETA ARGOS

```
CLASSIFICATORE ARCHETIPI:
  SVM (TF-IDF, ngram 1-3, LinearSVC) → 9 archetipi dealer
  CV 79.6% su 1.319 conversazioni sintetiche
  Zero API, tutto locale

RESPONSE GENERATION:
  Haiku 4.5 via OpenRouter → genera risposta per archetipo → auto-valida → auto-invia
  Costo: ~$0.002/risposta

OUTREACH MULTICANALE:
  Day 1: WA testo (per archetipo)
  Day 3: WA testo follow-up + veicolo specifico
  Day 7: WA VOICE NOTE (edge-tts DiegoNeural, 40sec)
  Day 10: WA testo ultimo touchpoint + social proof
  Day 14: Pausa 30gg → re-engage

TTS STACK:
  Primario: edge-tts 7.2.7, voce it-IT-DiegoNeural (maschile, 9/10)
  Fallback: Piper it_IT-riccardo-medium (offline, 7/10)
  Output: MP3 → WA voice note via whatsapp-web.js (sendAudioAsVoice: true)

DASHBOARD:
  FastAPI + HTMX + Tabler dark + ECharts
  5 pagine: Overview, Pipeline, Conversazioni, Finance, System
  WA Auth integrata (QR inline)
  ~45MB RAM, porta 8080

INFRA:
  iMac (ssh gianlucadistasi@192.168.1.2)
  PM2: argos-dashboard, argos-tg-bot, argos-wa-daemon
  DB: SQLite WAL (pipeline) + DuckDB (CoVe scoring)
  CF Tunnel: cloudflared quick tunnel (--config /dev/null per non interferire con Fluxion!)
```

---

## 3. FILE REFERENCE — SOLA LETTURA

**Working directory ARGOS**: `/Users/macbook/Documents/combaretrovamiauto-enterprise`

### Core Engine
| File | Descrizione | NOTA |
|------|-------------|------|
| `src/cove/cove_engine_v4.py` | Motore CoVe scoring (DuckDB) | **MAI MODIFICARE** |
| `src/marketing/archetype_classifier.py` | SVM classifier 9 archetipi | Read-only |
| `src/marketing/train_svm_classifier.py` | Training pipeline SVM | Read-only |

### WA Intelligence (iMac runtime)
| File | Descrizione |
|------|-------------|
| `wa-intelligence/wa-daemon.js` | WA daemon v2.2 — /send + /send-voice + SQLite logging |
| `wa-intelligence/response-analyzer.py` | LLM autonomo (Haiku 4.5 via OpenRouter) |
| `wa-intelligence/telegram-handler.py` | Bot Telegram per founder (/costi, corrections) |
| `wa-intelligence/auth-qr-server.js` | QR auth server (porta 8765, Chromium) |
| `wa-intelligence/ecosystem.config.js` | PM2 config con env OpenRouter |

### Dashboard
| File | Descrizione |
|------|-------------|
| `wa-intelligence/dashboard/app.py` | FastAPI app — 5 pagine + API + WA Auth |
| `wa-intelligence/dashboard/db.py` | 16 query + 5 write + audit |
| `wa-intelligence/dashboard/auth.py` | Cookie session (itsdangerous) |
| `wa-intelligence/dashboard/static/css/argos-theme.css` | Tema nero + oro |
| `wa-intelligence/dashboard/templates/*.html` | Jinja2 templates (Tabler) |
| `wa-intelligence/run_dashboard.py` | Launcher uvicorn |

### Training Data
| File | Descrizione |
|------|-------------|
| `data/training/*.json` | 50+ file, 1.319 conversazioni sintetiche, 9 archetipi |
| `data/tfidf_index/` | Matrice TF-IDF + vectorizer pre-trained |
| `data/training/archetypes_v2.json` | Definizioni 9 archetipi con trigger/tono/esempi |

### Tools
| File | Descrizione |
|------|-------------|
| `tools/salerno_pipeline_loader.py` | Carica 8 dealer Salerno in SQLite |
| `tools/review_conversations.py` | Review conversazioni + profila dealer |
| `tools/generate_training_dataset.py` | Genera dataset sintetico per SVM |
| `tools/sync_db_snapshot.sh` | Sync SQLite da iMac a MacBook |

### Config
| File | Descrizione |
|------|-------------|
| `.mcp.json` | MCP config: Playwright + SQLite |
| `.claude/agents/` | 7 agenti specializzati (sales, research, cove, finance, ops, recovery, marketing) |
| `.claude/prompts/` | Prompt per sessioni (build-dashboard, S64) |

---

## 4. I 9 ARCHETIPI DEALER

Il classificatore SVM identifica il profilo comportamentale del dealer per personalizzare ogni comunicazione:

| Archetipo | Tono | Trigger |
|-----------|------|---------|
| **RAGIONIERE** | Numeri precisi, ROI esplicito, zero fuffa | "quanto margine?", "i conti tornano?" |
| **BARONE** | Rispetto, "su misura per lei", esclusivita' | "mi faccia capire", atteggiamento superiore |
| **PERFORMANTE** | Velocita', "48h", risultati, efficienza | "quanto ci vuole?", impazienza |
| **NARCISO** | Esclusivita', "selezionato", "riservato" | autoreferenziale, vuole sentirsi speciale |
| **TECNICO** | Documentazione, specifiche, report DAT | domande su km, tagliandi, VIN |
| **RELAZIONALE** | Calore, "ci lavoriamo insieme", empatia | chiacchierone, vuole rapporto personale |
| **CONSERVATORE** | Sicurezza, "nessuna sorpresa", garanzie | diffidente, vuole rassicurazioni |
| **DELEGATORE** | Semplicita', "gestisco tutto io" | "fate voi", non vuole complicazioni |
| **OPPORTUNISTA** | Margine concreto, "i numeri parlano" | cerca solo il prezzo migliore |

---

## 5. API OPENROUTER — PER SALES AGENT

Fluxion puo' usare questa API per il suo sales agent / voice agent quando deve generare risposte in stile ARGOS:

```
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=anthropic/claude-haiku-4-5
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

**Credito**: $5 (sufficiente per ~2.500 risposte Haiku)
**Uso**: SOLO per sales agent / generazione risposte dealer. Non per altri scopi.

**Esempio chiamata:**
```python
import httpx

response = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    },
    json={
        "model": "anthropic/claude-haiku-4-5",
        "messages": [
            {"role": "system", "content": "Sei Luca Ferretti di ARGOS Automotive..."},
            {"role": "user", "content": "messaggio dealer..."}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
)
```

---

## 6. STRATEGIA COMMERCIALE COMPLETA

### 6.1 Posizionamento
- **Brand**: ARGOS Automotive
- **Persona**: Luca Ferretti, Vehicle Sourcing Specialist
- **Base operativa**: Bruxelles (cuore aste EU — BCA, eCarsTrade, CarOnSale sono li')
- **Proposta**: Scouting veicoli premium EU per concessionari italiani selezionati
- **Fee**: €800-1.200 success fee a veicolo consegnato, zero anticipi
- **Moat**: Regime margine IVA (vantaggio competitivo vs import diretto)

### 6.2 Target
- Concessionari family-business Sud Italia
- 30-80 auto in stock
- Titolare/socio operativo (non catena corporate)
- Fascia BMW/Mercedes/Audi 2018-2023
- Priorita': Campania, Puglia, Sicilia, Calabria, Basilicata

### 6.3 Lead Generation
- **Fase attuale**: 8 dealer zona Salerno (test manuale)
- **Scouting**: Autoscout24, Subito.it, Google Maps, pagine social dealer
- **Scoring CoVe**: confidence 0.0-1.0, threshold PROCEED >= 0.75
- **Pipeline**: SQLite con step tracking (PENDING → DAY1_SENT → ENGAGED → NEGOTIATING → DEAL)

### 6.4 Sequenza Outreach (Multi-step, per archetipo)
```
Day 1:  WA testo primo contatto (personalizzato per archetipo)
Day 3:  WA testo follow-up + esempio veicolo specifico per il loro stock
Day 7:  WA VOICE NOTE (edge-tts DiegoNeural, 30-40 sec, personalizzato)
Day 10: WA testo "ultimo touchpoint" + social proof ("un collega a Battipaglia...")
Day 14: Pausa 30 giorni
Day 44: Re-engage con trigger diverso (nuovo veicolo, nuova offerta)
```

### 6.5 Gestione Risposte
- **Automatica**: Haiku 4.5 genera risposta per archetipo, auto-valida tono
- **Escalation**: Se trattativa avanza → intervento manuale (futuro)
- **Obiezioni comuni**: IVA, garanzia, km, tempi consegna — tutte gestite nel prompt

### 6.6 Regole Immutabili Messaggi Dealer
- MAI "CarFax EU" → "DAT Fahrzeughistorie / TUV report"
- MAI margine senza IVA → specificare sempre inclusa/esclusa
- MAI Handlergarantie → solo garanzia costruttore UE
- MAI "non possiamo fatturare" → "bonifico e' piu' efficiente"
- MAI menzionare CoVe, Claude, AI, Anthropic, embedding, RAG
- Regime margine IVA = vantaggio competitivo, non problema

### 6.7 Narrativa Credibilita'
**Competitor reali con stesso modello operativo (verificati):**
- Bolidem (Nizza, FR) — fee €950-1790, nessun ufficio IT
- Autonao (Labenne, FR) — B2B dealer, 24 anni, solo numero FR
- eCarsTrade (Overijse, BE) — B2B aste, solo numero belga

**Se dealer chiede perche' non rispondi al telefono:**
"Sono spesso tra Bruxelles e Monaco per le aste. WA e' il canale piu' affidabile. Se vuole fissiamo una chiamata in un orario preciso."

**Se dealer nota vocale digitale:**
"Uso un sistema di messaggistica assistita per i primi contatti — mi permette di seguire piu' concessionari mentre sono tra le aste. Nella trattativa sono io direttamente."

### 6.8 Fatturazione
- **Ora**: Prestazione occasionale (max €5.000/anno, no P.IVA)
- **Dopo validazione**: P.IVA forfettaria (5% per 5 anni)
- **Per il dealer**: meccanismo noto, ricevuta o fattura + bonifico

### 6.9 KPI Target
- Tasso risposta Day 1-3: 15-25%
- Tasso risposta con voice note Day 7: +30% su chi non ha risposto
- Conversione risposta → trattativa: 40-50%
- Conversione trattativa → deal: 20-30%
- Target: 1-2 deal/mese nei primi 3 mesi, poi scale

---

## 7. TTS STACK — COME REPLICARE

Fluxion ha gia' edge-tts e Piper. Per replicare il voice note ARGOS:

```python
# Genera voice note
import asyncio, edge_tts

async def genera_vocale(testo: str, output_path: str):
    comm = edge_tts.Communicate(testo, "it-IT-DiegoNeural")
    await comm.save(output_path)

asyncio.run(genera_vocale(
    "Buongiorno, sono Luca Ferretti di ARGOS Automotive...",
    "/tmp/argos_voice.mp3"
))
```

```javascript
// Invia come voice note WA
const { MessageMedia } = require('whatsapp-web.js');
const media = MessageMedia.fromFilePath('/tmp/argos_voice.mp3');
await client.sendMessage('39XXXXXXXXX@c.us', media, { sendAudioAsVoice: true });
```

**Voce disponibili italiano:**
- `it-IT-DiegoNeural` — maschile, professionale (USARE PER LUCA)
- `it-IT-IsabellaNeural` — femminile, naturale (usare per Sara futura)
- `it-IT-ElsaNeural` — femminile, alternativa

---

## 8. COSA PUO' FARE FLUXION CON QUESTE SPECIFICHE

1. **Lead Generation**: Implementare scouting dealer via web scraping (Autoscout24, Subito, Google Maps) con scoring CoVe-like
2. **Dashboard**: Replicare il modello ARGOS (pipeline funnel, KPI, conversazioni) nella UI Tauri
3. **Sales Agent Voice**: Usare il voice-agent Fluxion con prompt ARGOS per chiamate/vocali dealer
4. **Outreach WA**: Integrare whatsapp-web.js (gia' nel package.json Fluxion) per sequenza multi-step
5. **TTS Voice Notes**: edge-tts DiegoNeural → MP3 → WA voice note (stack identico)
6. **Response Generation**: OpenRouter Haiku 4.5 per risposte personalizzate per archetipo

---

## 9. REGOLE CRITICHE

```
⚠️  TUTTI i file in /Users/macbook/Documents/combaretrovamiauto-enterprise sono READ-ONLY
⚠️  MAI modificare ~/.cloudflared/config.yml (config Fluxion tunnel!)
⚠️  MAI esporre CoVe/Claude/AI/Anthropic nei materiali dealer
⚠️  MAI modificare cove_engine_v4.py
⚠️  API OpenRouter: SOLO per sales agent, non sprecare credito
⚠️  Il founder NON vuole fare il commerciale — il sistema deve essere AUTONOMO
```

---

*Generato da ARGOS CTO (Claude Opus 4.6) — Session 63, 2026-03-18*
