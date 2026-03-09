# FLUXION — Handoff Sessione 35 → 36 (2026-03-09)

## ⚡ CTO MANDATE — NON NEGOZIABILE (sessione 35)
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature deve battere Fresha sul campo della PMI italiana.
> Ogni task risponde: *"quanti € risparmia o guadagna la PMI?"*
> Se non risponde → non si implementa.

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: 9cff590 | CI: ✅ verde
Working tree: pulito
type-check: 0 errori
```

---

## COMPLETATO SESSIONE 35

| Lavoro | Commit | Impatto |
|--------|--------|---------|
| Commit schede F06 tab layout universale | f45d528 | 8 schede, type-check ✅ |
| Sara UI v2 — waveform hero 48 barre animate | 9cff590 | Differenziatore visivo enterprise |
| Booking confirmation modal (slide-in) | 9cff590 | UX world-class al completamento prenotazione |
| 44 foto stock CC0 Pexels (8 categorie) | 9cff590 | Demo content reale per schede cliente |
| Script download-stock-photos.py | 9cff590 | Riproducibile, PEXELS_API_KEY in .env |
| CoVe 2026 Deep Research completata | — | 10 gap enterprise identificati con ROI |

---

## PROSSIMA SESSIONE 36 — ENTERPRISE GAPS

### Obiettivo
Implementare i **Top 3 gap enterprise** identificati dalla Deep Research, nell'ordine esatto.
Ogni implementazione segue il ciclo: RESEARCH → PLAN → IMPLEMENT → VERIFY → DEPLOY.

### Sequenza obbligatoria

#### 🥇 GAP #1 — LATENCY SARA: da 1330ms a <800ms [XL]
**Perché primo**: Senza questo Sara è un IVR, non un agente AI. Blocca tutto il funnel.
**Benchmark target**: PolyAI P50 <500ms, Twilio P50 491ms → FLUXION target P50 <800ms
**Soluzione**:
- Groq `stream=True` → TTS inizia sui primi 20 token, non aspetta risposta completa
- Timing instrumentation in `orchestrator.py` (misura ogni layer L0-L4)
- HTTP Bridge timeout: 5s → 1s con SQLite local cache fallback
- STT: misura Whisper.cpp CPU vs Groq cloud, scegli il più veloce per contesto

**Files chiave**:
- `voice-agent/src/orchestrator.py` (LLM layer)
- `voice-agent/src/groq_client.py` (streaming)
- `voice-agent/src/tts_handler.py` (chunked synthesis)
- `http-bridge/` (timeout optimization)

#### 🥈 GAP #2 — REMINDER AUTOMATICI -24h/-1h [L]
**Perché secondo**: -40% no-show rate = +25% slot fill = denaro diretto. Feature che PAGA il piano Pro.
**Benchmark**: Fresha invia WA -24h + SMS -2h, no-show reduction 40%
**Soluzione**:
- `APScheduler` in `voice-agent/main.py` (persistent job store SQLite)
- `voice-agent/src/reminder_scheduler.py` — polling ogni 15min
- Schema: aggiungi `reminder_24h_sent`, `reminder_1h_sent` a tabella appuntamenti
- WA templates vertical-aware (salone vs clinica vs palestra hanno toni diversi)

**Schema migration**: `031_reminder_tracking.sql`

#### 🥉 GAP #3 — WAITLIST NOTIFY SLOT LIBERO [M]
**Perché terzo**: Slot cancellato → cliente in lista → WA automatico in <5min. Zero soldi persi.
**Benchmark**: Fresha: slot liberato → scansione waitlist → WA immediato
**Soluzione**:
- `check_and_notify_waitlist()` triggerata quando appuntamento cancellato/spostato
- APScheduler job ogni 5min come fallback
- WA button interattivo: "Sì, confermo slot" | "No, grazie"
- `whatsapp_callback.py` gestisce la risposta button

---

## F07 LEMONSQUEEZY — In attesa azioni Luke

| Step | Stato | Note |
|------|-------|------|
| server.py bugfix | ✅ a6d0d1f | enterprise→clinic |
| Descrizioni prodotti | ✅ | nomi esatti FLUXION Base/Pro/Clinic |
| Screenshots app | ⏳ | Sara UI v2 pronta — fare ora |
| Crea store + 3 prodotti | ⏳ LUKE | nomi esatti, no license keys LS |
| Webhook Signing Secret | ⏳ LUKE | dopo creazione webhook |
| SMTP in config.env | ⏳ | SMTP pass già in .env: `lzhx yujp hvel epyb` |
| Server iMac porta 3010 | ⏳ | dopo config.env |
| Cloudflare Tunnel | ⏳ | dopo server |
| In-app upgrade UI | ⏳ | dopo LemonSqueezy live |

---

## RESEARCH FILES DISPONIBILI

| File | Contenuto |
|------|-----------|
| `cove2026-deep-research-market.md` | 10 gap enterprise + ROI per PMI + roadmap Q2-Q4 |
| `r1-sara-capabilities-audit.md` | Audit completo Sara 15 aree |
| `r2-world-class-benchmarks.md` | Benchmark 2026 voice agents |
| `r3-italian-nlu-edge-cases.md` | Edge cases NLU italiano |

---

## PROMPT RIPARTENZA SESSIONE 36

```
Sessione 36 — Enterprise Gaps: Latency + Reminder + Waitlist

⚠️ GUARDRAIL:
- Working dir: /Volumes/MontereyT7/FLUXION
- Memory: /Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md
- Ignora backup-combaretrovamiauto-* nel T7

CTO MANDATE: "Non accetto mediocrità. Solo enterprise level."

STATO:
- HEAD: 9cff590 | CI ✅ verde | working tree pulito
- Sara UI v2 live (waveform hero + booking modal)
- Deep Research CoVe 2026 COMPLETATA → .claude/cache/agents/cove2026-deep-research-market.md
- F07 in attesa credenziali Luke (LemonSqueezy)

AGENDA SESSIONE 36 — in ordine esatto:

1. LATENCY SARA [PRIMA DI TUTTO]
   - Leggi: voice-agent/src/orchestrator.py + groq_client.py
   - Leggi: .claude/cache/agents/cove2026-deep-research-market.md (sezione #1)
   - Target: P50 da 1330ms → <800ms
   - Plan: timing instrumentation → streaming LLM → TTS chunking → HTTP Bridge timeout

2. REMINDER AUTOMATICI -24h/-1h
   - Leggi: voice-agent/src/booking_state_machine.py (struttura appuntamenti)
   - Schema: migration 031_reminder_tracking.sql
   - APScheduler + reminder_scheduler.py + WA templates

3. WAITLIST NOTIFY
   - Leggi: booking_state_machine.py (PROPOSING_WAITLIST state)
   - check_and_notify_waitlist() + APScheduler + WA button callback

Per ogni gap: RESEARCH (se manca) → PLAN con AC misurabili → IMPLEMENT → VERIFY → DEPLOY

REGOLA FERMA: ogni feature deve rispondere "quanti € risparmia/guadagna la PMI?"
```
