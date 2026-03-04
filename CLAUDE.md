# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: PMI italiane 1-15 dip. (saloni, palestre, cliniche, officine)
- **Model**: Licenza LIFETIME desktop — NO SaaS, NO commissioni, 0% booking fee
- **Voice**: "Sara" — voice agent prenotazioni 24/7, 5-layer RAG, 23 stati FSM
- **License**: Ed25519 offline — Base €497 / Pro €897 / Clinic €1.497 (lifetime, no SaaS)

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

**FASE 1 — RESEARCH** (subagente → file, MAI inline)
- Lancia Agent(Explore/voice-engineer/etc) → scrive `.claude/cache/agents/[task].md`
- Se research file esiste già: leggi e procedi direttamente

**FASE 2 — PLAN**
- Leggi research → identifica edge case → acceptance criteria MISURABILI
- Schema DB changes documentati prima di qualsiasi SQL/Rust

**FASE 3 — IMPLEMENT**
- Un commit per feature atomica — TypeScript strict (zero `any`, `@ts-ignore`)
- Zero `--no-verify` — MAI, in nessun caso

**FASE 4 — VERIFY**
- `npm run type-check` → 0 errori — confronto vs acceptance criteria

**FASE 5 — DEPLOY**
- `git push origin master` + sync iMac + update ROADMAP_REMAINING.md

**Task NON è completato finché tutte le 5 fasi non sono verificate.**

---

## Critical Rules
1. Mai commit API keys / .env — mai `--no-verify`
2. TypeScript sempre (no JS), async Tauri commands, zero `any`
3. Research file PRIMA di implementare (CoVe 2026)
4. Task COMPLETATO solo se verificato (type-check + acceptance criteria)
5. Field names API italiani: `servizio`, `data`, `ora`, `cliente_id`
6. Dev MacBook — Rust/build solo su iMac (192.168.1.2) via SSH
7. Riavvio voice pipeline iMac dopo OGNI modifica Python

---

## Stato Progetto (2026-03-04 — sessione 16)
```
branch: master | v1.0.0 ✅
Voice Sara: 1160 PASS / 0 FAIL ✅
iMac SSH: 192.168.1.12 ✅
Pricing: Base €497 / Pro €897 / Clinic €1.497
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
| F07 | LemonSqueezy | ⏳ (dopo Vimeo) |

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
