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

## Critical Rules
1. Mai commit API keys / .env — mai `--no-verify`
2. TypeScript sempre (no JS), async Tauri commands
3. Test prima di commit (`.claude/rules/testing.md`)
4. Task COMPLETATO solo se verificato (DB record, E2E, audio live)
5. Field names API italiani: `servizio`, `data`, `ora`, `cliente_id`
6. Dev MacBook — Rust/build solo su iMac (192.168.1.2) via SSH
7. Riavvio voice pipeline iMac dopo OGNI modifica Python

## Active Sprint
```
branch: master | Voice Agent Enterprise v2.1 — test live audio TODO
Sara: 58/58 test ✅ | iMac: 192.168.1.2:3002
Next: test live → build v0.9.2
```

## Task Critiche 🔴
1. **Test Live Voice Agent** — `ssh imac "python3 t1_live_test.py"` (dettagli: `.claude/rules/voice-agent-details.md`)
2. **WhatsApp Pacchetti Selettivo** — `PacchettiAdmin.tsx`, filtri VIP/stelle, rate 60 msg/h
3. **Voice Greeting Dinamico** — "Buongiorno, sono Sara di {nome_attivita}"
4. **Build v0.9.2** — dopo test live superati

## Comandi Rapidi
```bash
# TypeScript check (MacBook)
npm run type-check

# Test voice (iMac)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && python -m pytest tests/ -v --tb=short 2>&1 | tail -20"

# Sync iMac
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"

# Riavvio voice pipeline iMac
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

## Verticali
6 macro (`macro_categoria`) × N sotto-verticali (`micro_categoria`) in impostazioni key-value.
Fonte di verità: `src/types/setup.ts` (MACRO_CATEGORIE + MICRO_CATEGORIE).
Dettaglio: `.claude/cache/agents/sub-verticals-research.md`

## Documentazione
- **PRD**: `PRD-FLUXION-COMPLETE.md` ⭐
- **Voice Agent**: `.claude/rules/voice-agent-details.md`
- **Verticali research**: `.claude/cache/agents/sub-verticals-research.md`
- **Token saving**: `.claude/cache/agents/token-saving-research.md`
