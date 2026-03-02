# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: PMI italiane 1-15 dip. (saloni, palestre, cliniche, officine)
- **Model**: Licenza LIFETIME desktop — NO SaaS, NO commissioni, 0% booking fee
- **Voice**: "Sara" — voice agent prenotazioni 24/7, 5-layer RAG, 23 stati FSM
- **License**: Ed25519 offline, 3 tier Base €297 / Pro €497 / Enterprise €897

## I 3 Pilastri
📱 **COMUNICAZIONE** (WhatsApp + Voice) · 🎯 **MARKETING** (Loyalty + Pacchetti) · ⚙️ **GESTIONE** (Calendario + Schede)
> Questi 3 pilastri devono essere PERFETTI.

---

## ⚡ PROTOCOLLO CoVe 2026 — NON NEGOZIABILE

**Ogni task segue obbligatoriamente queste 5 fasi:**

### FASE 1 — RESEARCH (sempre subagente → file)
- Lancia subagente per ricerca → scrive in `.claude/cache/agents/[task].md`
- MAI inline research nel contesto principale
- Verifica con fonti multiple (Chain of Verification)
- Se research file esiste già: leggi e procedi

### FASE 2 — PLAN (verifica contro research)
- Leggi research file → identifica edge case → stima effort reale
- Definisci acceptance criteria MISURABILI prima di iniziare
- Schema DB changes documentati prima di qualsiasi implementazione

### FASE 3 — IMPLEMENT (atomico, verificabile)
- Un commit per feature atomica
- TypeScript strict: zero `any`, zero `as unknown`, zero `@ts-ignore`
- Zero `--no-verify` — mai, in nessun caso

### FASE 4 — VERIFY (obbligatorio prima di "completato")
- `npm run type-check` → 0 errori
- Test esistenti non rotti
- Confronto implementazione vs acceptance criteria FASE 2
- Review edge case identificati in FASE 2

### FASE 5 — DEPLOY
- `git push origin master`
- `ssh imac "git pull origin master"` (se SSH disponibile)
- Update HANDOFF.md + MEMORY.md

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

## Active Sprint (2026-03-02)
```
branch: master
Completati oggi: Fix Impostazioni ✅ | Ricerca clienti ✅ | Operatori CoVe ✅
Prossimo: C1 Fatture SDI → B2 Operatori Servizi → B3 Operatori Orari
Sara: 58/58 test ✅ | iMac: 192.168.1.2:3002 (SSH offline — abilitare Remote Login)
```

## Task Queue (ordine priorità)
| # | Task | Research | Effort |
|---|------|----------|--------|
| C1 | Fatture SDI + XML FatturaPA | `.claude/cache/agents/sdi-fatturapa-research.md` 🔄 | ~1 sessione |
| B2 | Operatori Servizi UI | `.claude/cache/agents/operatori-features-cove2026.md` ✅ | 6h |
| B3 | Operatori Orari/Turni | `.claude/cache/agents/operatori-features-cove2026.md` ✅ | 10h |
| D1 | Landing screenshots | `.claude/cache/agents/landing-conversion-research.md` 🔄 | 1h |
| P2 | Test live voice T1-T5 | `.claude/cache/agents/voice-testing-methodology.md` 🔄 | 1h |
| P3 | Build v0.9.2 tag | — | 30min |

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
