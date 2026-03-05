# FLUXION — Handoff Sessione 23 (2026-03-05) — Framework Upgrade

## PROSSIMO TASK IMMEDIATO (PRIORITÀ ASSOLUTA)

**Implementare le 6 feature del Framework Upgrade** (analizzate sessione 23).
Fonte analisi: `/Users/macbook/Documents/combaretrovamiauto/combaretrovamiauto-claude-framework`

**Ordine implementazione** (totale ~4.5h):
1. `Taskfile.yml` — task runner unificato (2h)
2. `post-write-typescript.sh` — hook TS immediato (30min)
3. Scoped rules via glob frontmatter (30min)
4. `task db:schema` — migration freeze (1h)
5. `pre-compact.sh` — salva stato prima di /compact (30min)
6. Permission hardening settings.json (15min)

---

## Completato Sessione 23 — Analisi Framework

### Analisi eseguita su:
`/Users/macbook/Documents/combaretrovamiauto/combaretrovamiauto-claude-framework`

### Cosa il framework ha che FLUXION non ha:

| Gap | Impatto |
|-----|---------|
| Taskfile.yml come orchestratore unico | 35+ npm scripts → comandi mnemonici `task ci`, `task imac:restart` |
| Post-write hook TypeScript | TS errors scoperti subito, non a fine task |
| Scoped rules via glob | Carica regole solo per directory corrente → -30% token/sessione |
| Migration freeze check automatico | Previene la ripetizione del bug critico 021-029 |
| PreCompact hook reale | Stato sessione salvato prima di /compact |
| Permission deny list completa | No --force push, no rm -rf, no .env read |

---

## Feature #1 — Taskfile.yml

**File da creare**: `/Volumes/MontereyT7/FLUXION/Taskfile.yml`

**Gruppi task da implementare**:
```yaml
# SYNTAX
tc:          → npx tsc --noEmit
lint:        → eslint . --ext .ts,.tsx

# VOICE AGENT (iMac SSH)
voice:test:  → ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && ... pytest"
voice:restart: → ssh imac "kill $(lsof -ti:3002); sleep 2; ... python main.py ..."
voice:health:  → curl -s http://192.168.1.2:3002/health

# DB / RUST (iMac SSH)
db:schema:   → python3 verifica migration 021-029 in lib.rs
imac:build:  → ssh imac "source ~/.cargo/env && ... npm run tauri build"
imac:sync:   → git push origin master && ssh imac "... git pull origin master"

# CI COMPLETO
ci:          → tc → lint → voice:test → playwright (sequenza, fail fast)

# PLAYWRIGHT
playwright:  → cd e2e-tests && npx playwright test tests/impostazioni.spec.ts --reporter=list

# GIT
commit:      → task ci → git add <files> → git commit

# DEFAULT
default:     → task --list
```

**Installazione prerequisito**:
```bash
brew install go-task/tap/go-task
```

---

## Feature #2 — Post-write TypeScript Hook

**File da creare**: `.claude/hooks/post-write-typescript.sh`

```bash
#!/bin/bash
FILE="$1"
[[ "$FILE" != *.ts ]] && [[ "$FILE" != *.tsx ]] && exit 0

# Anti-pattern check immediato (no tsc completo = troppo lento)
if grep -n " any\b" "$FILE" 2>/dev/null | grep -v "// ok-any" | head -3; then
  echo "⚠️  'any' in $FILE — TypeScript strict violation (usa // ok-any per eccezioni)"
fi
if grep -n "@ts-ignore" "$FILE" 2>/dev/null; then
  echo "⚠️  '@ts-ignore' in $FILE — vietato da CLAUDE.md"
fi
echo "✅ $FILE — hook OK"
```

**Wiring da aggiungere in settings.json**:
```json
{
  "matcher": "Write(src/**/*.tsx)",
  "hooks": [{"type": "command", "command": "bash .claude/hooks/post-write-typescript.sh \"$file\""}]
},
{
  "matcher": "Write(src/**/*.ts)",
  "hooks": [{"type": "command", "command": "bash .claude/hooks/post-write-typescript.sh \"$file\""}]
}
```

---

## Feature #3 — Scoped Rules via Glob

**File da modificare** (aggiungere frontmatter YAML):

`.claude/rules/react-frontend.md` → aggiungere in cima:
```yaml
---
glob: "src/**"
---
```

`.claude/rules/rust-backend.md` → aggiungere in cima:
```yaml
---
glob: "src-tauri/**"
---
```

`.claude/rules/voice-agent.md` → aggiungere in cima:
```yaml
---
glob: "voice-agent/**"
---
```

`.claude/rules/testing.md` → aggiungere in cima:
```yaml
---
glob: "e2e-tests/**"
---
```

**NOTA**: `voice-agent-details.md` e `react-frontend.md` già nella dir rules — verificare cosa caricano.

---

## Feature #4 — Migration Freeze (task db:schema)

**Da integrare nel Taskfile** come task standalone E nel CI:
```python
# Verifica inline Python in Taskfile
import re
librs = open('src-tauri/src/lib.rs').read()
migrations = [
    ('021', 'setup_config'),
    ('022', 'whatsapp_invii_pacchetti'),
    ('023', 'groq_setup'),
    ('024', 'operatori_features'),
    ('025', 'operatori_commissioni'),
    ('026', 'impostazioni_sdi_key'),
    ('027', 'scheda_fitness'),
    ('028', 'scheda_medica'),
    ('029', 'sdi_multi_provider'),
]
for num, name in migrations:
    if name not in librs:
        print(f'❌ Migration {num} ({name}) NON in lib.rs')
        exit(1)
print('✅ Tutte le migration 021-029 presenti in lib.rs')
```

**Post-write hook per `.sql`** (da aggiungere in post-write-typescript.sh o file separato):
```bash
if [[ "$FILE" == *migrations/*.sql ]]; then
  MIGNAME=$(basename "$FILE" .sql)
  grep -q "$MIGNAME" src-tauri/src/lib.rs || \
    echo "⚠️  $MIGNAME NON in lib.rs — aggiungila prima del commit!"
fi
```

---

## Feature #5 — PreCompact Hook Reale

**File da creare**: `.claude/hooks/pre-compact.sh`
```bash
#!/bin/bash
{
  echo "## Session State $(date '+%Y-%m-%d %H:%M')"
  echo "Branch: $(git branch --show-current)"
  echo "Last commit: $(git log --oneline -1)"
  echo "Modified files:"
  git status --short | head -15
  echo "Phase from HANDOFF: $(head -3 HANDOFF.md)"
} > .claude/session_state.md
echo "✅ session_state.md aggiornato ($(wc -l < .claude/session_state.md) righe)"
```

**Wiring da aggiungere in settings.json**:
```json
"PreCompact": [{
  "hooks": [{"type": "command", "command": "bash .claude/hooks/pre-compact.sh"}]
}]
```

---

## Feature #6 — Permission Hardening settings.json

**Da aggiungere alla deny list esistente**:
```json
"deny": [
  "Read(.env)",
  "Read(.env.*)",
  "Write(.env)",
  "Bash(git push --force*)",
  "Bash(rm -rf*)",
  "Bash(git reset --hard*)",
  "Read(node_modules/**)",      ← già presente
  "Read(src-tauri/target/**)"   ← già presente
]
```

---

## Stato P0.5 (verificare prima di procedere)

| Piano | Wave | Stato |
|-------|------|-------|
| p0.5-01 | 1 | ✅ VoiceAgentSettings.tsx implementato |
| p0.5-02 | 2 | ✅ public/guida-fluxion.html creato (401 righe) |
| Human verify | — | ⏳ Da fare dall'utente (facoltativo) |

**Uncommitted files** (11): VoiceAgentSettings.tsx, e2e tests, guida HTML.
→ Fare commit P0.5 PRIMA di iniziare Framework Upgrade.

---

## Roadmap Post-Framework-Upgrade

| Fase | Task | Status |
|------|------|--------|
| **FW** | Framework Upgrade (6 feature) | 🔄 NEXT SESSIONE |
| **F04** | Schede Mancanti | ⏳ |
| **F10** | CI/CD GitHub Actions (facilitato da Taskfile) | ⏳ |
| **F07** | LemonSqueezy payment | ⏳ |

---

## Stato Git

```
Branch: master | HEAD: 4cdebed
type-check: ✅ 0 errori
Voice tests: ✅ 1263 PASS / 0 FAIL
Playwright: ✅ 11/11 impostazioni tests
Uncommitted: 11 file (P0.5 wave 1+2)
```

## Riferimento Framework Sorgente
```
/Users/macbook/Documents/combaretrovamiauto/combaretrovamiauto-claude-framework/
├── CLAUDE.md          → identità + CoVe tagging pattern
├── Taskfile.yml       → task runner (COPIA E ADATTA)
├── .claude/settings.json → permission model (COPIA DENY LIST)
├── .claude/hooks/post-write-python.sh → adatta per TypeScript
└── .claude/skills/cove-verify/SKILL.md → pattern checklist
```
