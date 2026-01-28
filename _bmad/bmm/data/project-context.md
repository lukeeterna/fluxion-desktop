# Fluxion Project Context

## Environment Configuration

| Machine | Host | Path | Usage |
|---------|------|------|-------|
| **MacBook** | localhost | `/Volumes/MontereyT7/FLUXION` | Development |
| **iMac** | 192.168.1.9 | `/Volumes/MacSSD - Dati/fluxion` | Live Testing |

> **NOTA**: Tauri 2.x NON funziona su macOS Big Sur. Dev su MacBook, test su iMac (Monterey 12.7.4).

---

## BMAD Task Execution Protocol

### Ogni Task DEVE seguire questo workflow:

```
1. Implementare il codice
2. Eseguire test locali (pytest, cargo test, npm run type-check)
3. Sync su iMac: scp file imac:/path/
4. Restart servizi se Python modificato: ssh imac "..."
5. TEST LIVE su iMac - verifica funzionalità REALE
6. Solo se LIVE OK → Commit e Push
```

### Test Locali (MacBook)

```bash
# TypeScript
npm run type-check && npm run lint

# Rust (se modificato)
cd src-tauri && cargo test && cd ..

# Python (se modificato)
cd voice-agent && pytest tests/ -v && cd ..
```

### Sync su iMac

```bash
# Sync singolo file
scp /Volumes/MontereyT7/FLUXION/path/to/file.py \
    "imac:/Volumes/MacSSD\ -\ Dati/fluxion/path/to/"

# Sync directory
scp -r /Volumes/MontereyT7/FLUXION/voice-agent/src/ \
    "imac:/Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/src/"
```

### Restart Servizi iMac

```bash
# Restart voice pipeline (se Python modificato)
ssh imac "lsof -ti :3002 | xargs kill -9 2>/dev/null; \
  cd /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent && \
  source venv/bin/activate && \
  nohup python main.py > /tmp/voice.log 2>&1 &"

# Verifica servizi attivi
ssh imac "curl -s http://localhost:3001/health && \
          curl -s http://localhost:3002/health"
```

### Test LIVE su iMac

```bash
# Test voice agent via HTTP
ssh imac "curl -X POST http://localhost:3002/api/voice/process \
  -H 'Content-Type: application/json' \
  -d '{\"session_id\": \"test\", \"text\": \"INPUT DA TESTARE\"}'"

# Verifica risposta contiene i valori attesi
# Es: intent corretto, layer corretto, response attesa
```

---

## Servizi Attivi

| Servizio | Porta | Descrizione |
|----------|-------|-------------|
| HTTP Bridge | 3001 | Rust/Tauri backend API |
| Voice Pipeline | 3002 | Python voice agent |

---

## Voice Agent Pipeline

### 4-Layer Architecture

```
L0: Special Commands (annulla, stop, aiuto) → Regex
L1: Intent Classification (PRENOTAZIONE, CANCELLAZIONE, etc.) → Patterns
L2: Slot Filling (Booking State Machine)
L3: FAQ Retrieval
L4: Groq LLM Fallback
```

### Intent Priority

1. **L1** handles CANCELLAZIONE/SPOSTAMENTO BEFORE L2 booking SM
2. PRENOTAZIONE goes to L2 for slot filling
3. FAQ/general queries go to L3/L4

---

## Commit Protocol

```bash
# Pre-commit checklist
1. npm run type-check  ✅
2. npm run lint        ✅
3. cargo test          ✅ (se Rust)
4. pytest tests/       ✅ (se Python)
5. LIVE test su iMac   ✅ (OBBLIGATORIO)

# Commit
git add <files>
git commit -m "type(scope): description"
git push origin <branch>
```

---

## Quality Gates (Local)

| Gate | Criterio | Tool |
|------|----------|------|
| Type Safety | 0 errori TypeScript | `npm run type-check` |
| Lint | 0 errori ESLint | `npm run lint` |
| Rust Tests | Tutti passati | `cargo test` |
| Python Tests | Tutti passati | `pytest` |
| **LIVE Test** | Funziona su iMac | Manual / curl |

---

## CI/CD Pipeline (GitHub Actions)

### Workflow Files

| File | Trigger | OS | Scopo |
|------|---------|----|----|
| `test-suite.yml` | push develop, PR main | ubuntu | Unit + Integration |
| `e2e-tests.yml` | push, PR, manual | ubuntu, macOS, Windows | E2E Full Matrix |
| `release.yml` | tag v* | macOS, Windows | Build + Release |
| `release-full.yml` | manual | macOS | Full verification |

### test-suite.yml Jobs

| Job | Trigger | OS | Durata |
|-----|---------|----|----|
| **fast-check** | push develop | ubuntu | 5 min |
| **full-suite** | PR to main | ubuntu | 15 min |
| **nightly-ai-tests** | cron 2AM | ubuntu | 10 min |
| **e2e-tests** | label 'e2e' | ubuntu-22.04 | 35 min |
| **release-verification** | label 'release' | macOS-12 | 45 min |

### e2e-tests.yml Jobs

| Job | Trigger | OS | Tests |
|-----|---------|----|----|
| **smoke-tests** | every push | ubuntu | Basic navigation |
| **e2e-full** | after smoke | macOS + Windows | Full suite matrix |
| **visual-tests** | PR | ubuntu | Screenshot diff |
| **a11y-tests** | after smoke | ubuntu | WCAG 2.1 AA |
| **allure-report** | always | ubuntu | Report generation |

### PR Labels per Trigger

| Label | Workflow | Note |
|-------|----------|------|
| `e2e` | test-suite.yml → e2e-tests | Run WebDriverIO E2E |
| `release` | test-suite.yml → release-verification | Full macOS build |

### CI/CD Test Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                           │
├─────────────────────────────────────────────────────────────┤
│  push develop → fast-check (ubuntu, 5min)                   │
│  PR to main   → full-suite (ubuntu, 15min)                  │
│  PR + 'e2e'   → e2e-tests (ubuntu + tauri-driver, 35min)    │
│  PR + 'release' → release-verification (macOS, 45min)       │
│  cron 2AM     → nightly-ai-tests (ubuntu, 10min)            │
├─────────────────────────────────────────────────────────────┤
│  e2e-tests.yml:                                             │
│  every push   → smoke-tests (ubuntu)                        │
│  after smoke  → e2e-full (macOS + Windows matrix)           │
│  PR           → visual-tests (ubuntu)                       │
│  after smoke  → a11y-tests (ubuntu)                         │
└─────────────────────────────────────────────────────────────┘
```

### Quando Aggiungere Labels

```bash
# Per PR che modificano UI critica
gh pr edit <PR_NUMBER> --add-label "e2e"

# Per PR pre-release
gh pr edit <PR_NUMBER> --add-label "release"

# Trigger manuale E2E
gh workflow run e2e-tests.yml -f test_suite=all
```

---

## Test Completo Pre-Merge

### Checklist Completa

```
LOCAL:
  [ ] npm run type-check
  [ ] npm run lint
  [ ] cargo test (se Rust)
  [ ] pytest tests/ (se Python)
  [ ] LIVE test su iMac

CI/CD (automatico su PR):
  [ ] fast-check passa
  [ ] full-suite passa
  [ ] e2e-tests passa (se label 'e2e')
  [ ] release-verification passa (se label 'release')

SOLO DOPO TUTTO VERDE:
  [ ] Merge PR
```

---

*Aggiornato: 2026-01-28*
