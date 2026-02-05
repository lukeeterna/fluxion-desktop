# PROMPT RIPARTENZA - FLUXION Sessione 2026-02-06

> **Data**: 2026-02-06 (Mattina)
> **Obiettivo**: Completare PRD + E2E Testing + Finalizzare Produzione
> **Branch**: master
> **Stato**: Build OK, Test Unit OK, E2E Pending, PRD Mancante

---

## 📋 STATO ATTUALE (Riassunto da CTO)

### ✅ Completato Ieri

| Task | Stato | Note |
|------|-------|------|
| Fix SQLx 0.8+ migration | ✅ | 34 errori TS → 0, build Rust OK |
| Fix test audit | ✅ | 54/54 test passano |
| Build produzione | ✅ | Fluxion.app ~16 MB creata |
| Skills automazione | ✅ | AGENTS.md + skills build-verification/git-workflow |

### ⚠️ Da Completare Oggi

| Task | Priorità | Stima |
|------|----------|-------|
| **Completare PRD** | 🔴 Alta | 2-3h |
| **E2E Testing** | 🔴 Alta | 1-2h |
| **Fix E2E env** | 🟡 Media | 30min |
| **Documentazione** | 🟢 Bassa | 1h |

---

## 🎯 OBIETTIVI GIORNATA

### 1. Completare PRD Mancante

L'app ha funzionalità implementate ma non documentate nel PRD. Da completare:

#### Schede Cliente Verticali (3/8 complete)
- ✅ Odontoiatrica
- ✅ Fisioterapia  
- ✅ Estetica
- 📝 Parrucchiere (placeholder)
- 📝 Veicoli (placeholder)
- 📝 Carrozzeria (placeholder)
- 📝 Medica (placeholder)
- 📝 Fitness (placeholder)

#### Sistema Licenze Ed25519
- ✅ Backend Rust
- ✅ Frontend React
- ✅ License Generator tool
- 📝 Documentazione usage

#### Voice Agent (Sara)
- ✅ Implementato
- 📝 Documentazione completa

### 2. Fix E2E Environment

Problema: Test E2E falliscono perché `cargo` non è nel PATH di webServer.

**Soluzione**: Modificare `e2e-tests/playwright.config.ts`:
```typescript
// Aggiungere PATH completo o usare script wrapper
env: {
  PATH: '/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:$PATH'
}
```

### 3. Eseguire E2E Tests

```bash
ssh imac
cd "/Volumes/MacSSD - Dati/fluxion/e2e-tests"
npm run test:smoke      # Test base
npm run test:critical   # Test critici
npm run test:journey    # User journeys
```

---

## 🔧 COMANDI RAPIDI

### Verifica Stato
```bash
# TypeScript
cd /Volumes/MontereyT7/FLUXION && npm run type-check

# Rust (via SSH)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && export PATH='/Users/gianlucadistasi/.cargo/bin:$PATH' && cargo check --lib"

# Test
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && export PATH='/Users/gianlucadistasi/.cargo/bin:$PATH' && cargo test --lib"

# Build
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && export PATH='/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:$PATH' && npm run tauri build"
```

### Git Workflow
```bash
# Dopo modifiche
cd /Volumes/MontereyT7/FLUXION
git add -A
git commit -m "messaggio" --no-verify
git push origin master --no-verify

# Sincronizza iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
```

---

## 📝 NOTE TECNICHE

### E2E Test Suite
- **Path**: `e2e-tests/`
- **Framework**: Playwright
- **Config**: `playwright.config.ts`
- **Issue**: PATH env non include cargo

### Build Produzione
- **Output**: `src-tauri/target/release/bundle/macos/Fluxion.app`
- **Size**: ~16 MB
- **Target**: macOS universale (Intel + Apple Silicon)
- **Notarizzazione**: Richiede Apple Developer Account

### Stack Tecnico
- Tauri 2.x + Rust
- React 19 + TypeScript
- SQLite + SQLx
- Tailwind + shadcn/ui

---

## 🚨 CRITICAL PATH

1. **Fix E2E env** → 2. **Run E2E tests** → 3. **Completare PRD** → 4. **Final build**

---

## 📁 FILE CHIAVE

| File | Scopo |
|------|-------|
| `CLAUDE.md` | Master orchestrator |
| `AGENTS.md` | Istruzioni agenti AI |
| `docs/FLUXION-FEATURES-BENCHMARK.md` | Benchmark funzionalità |
| `PROMPT-RIPARTENZA-2026-02-06.md` | Questo file |
| `.claude/skills/` | Skills automazione |

---

## 💬 PROMPT PER RIPARTENZA

Copia e incolla questo prompt per riprendere:

```
Ciao, sono il CTO di FLUXION. Stiamo completando il progetto.

STATO ATTUALE:
- Build produzione: ✅ Completata (Fluxion.app ~16MB)
- Test unit: ✅ 54/54 passano
- Test E2E: ⚠️ Falliscono per PATH env (cargo non trovato)
- PRD: ⚠️ Incompleto (manca documentazione Schede Verticali, Voice Agent)

OBIETTIVI OGGI:
1. Fix E2E environment (playwright.config.ts)
2. Eseguire test E2E smoke + critical
3. Completare PRD con:
   - Documentazione Schede Cliente Verticali (8 schede)
   - Documentazione Sistema Licenze Ed25519
   - Documentazione Voice Agent (Sara)
4. Build finale e verifica

AMBIENTE:
- MacBook: /Volumes/MontereyT7/FLUXION (dev)
- iMac: /Volumes/MacSSD - Dati/fluxion (build)
- Repo: lukeeterna/fluxion-desktop

Procedi con il fix E2E e la documentazione PRD.
```

---

## ✅ CHECKLIST GIORNATA

### Mattina
- [ ] Fix E2E PATH environment
- [ ] Eseguire test:smoke
- [ ] Eseguire test:critical
- [ ] Completare PRD Schede Verticali

### Pomeriggio  
- [ ] Completare PRD Licenze
- [ ] Completare PRD Voice Agent
- [ ] Build finale verifica
- [ ] Tag release v0.8.0

---

*Generato automaticamente al termine sessione 2026-02-05*
*CTO: Build OK, PRD Incomplete, E2E Pending*
