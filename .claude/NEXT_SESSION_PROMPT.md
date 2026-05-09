# PROMPT RIPARTENZA — SESSIONE 193 FLUXION

## S192 + S192-bis ✅ CHIUSE (2026-05-09)

- ✅ Push origin master sbloccato (root cause: GitHub Push Protection secret scanning)
- ✅ History sanitizzata via `git filter-repo --replace-text` (8 commit + closure pushati)
- ✅ Memory `reference_cloudflare_token.md` riscritta (procedura on-demand SSH)
- ✅ `.claude/settings.local.json` 9 permission entries con token rimosse
- ✅ Token CF ROTATI: fluxion-tunnel rollato (cfut_→cfat_ Account API Token), DEAD deletato, iMac .env aggiornato, wrangler whoami ✅
- ✅ Temp files con secret cancellati

**Gate 3**: F-1+F-2+F-3+F-4 LIVE | D-1 ✅ | D-2 ✅ (P95 36.9ms) | D-3 ❌ (P95 867ms — Piper bundle tech debt)

## S193 PRIORITY

**P1 — D-3 tech debt Piper bundle** (architettura promette tier OFFLINE Piper ~50ms):
```
ssh imac 'find "/Volumes/MacSSD - Dati/fluxion" -type f \( -name "piper" -o -name "*.onnx" \) 2>/dev/null'
```
Se assente → aggiungere a build PyInstaller, re-run D-3 offline mode, validare SLO P95 <800ms.

**P2 — iMac sync** (history riscritta):
```
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git fetch origin && git reset --hard origin/master"
```

**P3 — PRE-LAUNCH-AUDIT update**: docs/launch/PRE-LAUNCH-AUDIT.md aggiungere D-2 PASS + D-3 FAIL.

**P4 — Verifica deploy CF post-rotate**:
```
cd fluxion-proxy && TOKEN=$(ssh imac "grep CLOUDFLARE_API_TOKEN '/Volumes/MacSSD - Dati/fluxion/.env'" | cut -d= -f2) && CLOUDFLARE_API_TOKEN=$TOKEN CLOUDFLARE_ACCOUNT_ID=22ddff3a4ef544511523a841b3dcadf8 npx wrangler deployments list | head -5 && unset TOKEN
```

## GUARDRAIL PERMANENTE S192
MAI token in .md/commit/handoff/memory. Solo .env gitignored o secret manager.

## CONTEXT BUDGET GATE
File critici sopra 50% NO edit (HELPDESK.md, CLAUDE.md autorevole, PLAN.md, .claude/rules/*.md, migrations/**, tauri.conf.json, *.schema.json).
