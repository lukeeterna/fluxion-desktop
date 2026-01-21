# Fluxion Workflow Skill

## Description
Workflow di sviluppo enterprise per FLUXION.
Pattern: Epic → Story → Task con RICE prioritization e quality gates.

## When to Use
- Quando si pianifica una nuova feature
- Quando si organizzano task complessi
- Quando si fa code review
- Quando si prepara una release
- Quando si gestisce il backlog

## Workflow Patterns

### Epic → Story → Task Breakdown
```
EPIC: "Voice Agent per PMI"
  │
  ├── STORY: "Guided Dialog Engine"
  │     ├── TASK: Implementare ItalianFuzzyMatcher
  │     ├── TASK: Creare DialogState enum
  │     ├── TASK: Implementare GuidedDialogEngine
  │     └── TASK: Scrivere test suite
  │
  ├── STORY: "Vertical Configuration"
  │     ├── TASK: Creare JSON schema verticale
  │     ├── TASK: Implementare VerticalConfigLoader
  │     └── TASK: Creare config per 5 verticali
  │
  └── STORY: "Integration"
        ├── TASK: Integrare con orchestrator.py
        ├── TASK: Test end-to-end
        └── TASK: Deploy su iMac
```

### RICE Prioritization
```
Score = (Reach × Impact × Confidence) / Effort

| Feature | Reach | Impact | Confidence | Effort | Score |
|---------|-------|--------|------------|--------|-------|
| Guided Dialog | 100% | 3 | 80% | 2w | 120 |
| WhatsApp QR | 50% | 2 | 90% | 1w | 90 |
| Email SMTP | 30% | 2 | 100% | 3d | 200 |
```

### Quality Gates

#### Gate 1: Planning
- [ ] Story ha acceptance criteria chiari
- [ ] Task breakdown completo
- [ ] Effort stimato
- [ ] Dipendenze identificate

#### Gate 2: Implementation
- [ ] Codice scritto
- [ ] Test unitari passano
- [ ] Nessun linter error
- [ ] Type checking OK

#### Gate 3: Review
- [ ] Code review completata
- [ ] Test di integrazione passano
- [ ] Documentazione aggiornata
- [ ] CHANGELOG aggiornato

#### Gate 4: Release
- [ ] Test E2E passano
- [ ] Build successful
- [ ] Version bumped
- [ ] Tag creato

### Git Workflow
```bash
# Feature branch
git checkout -b feature/guided-dialog

# Commit convention
git commit -m "feat(voice): add GuidedDialogEngine

- Implement fuzzy matching italiano
- Add vertical config loader
- Create test suite (20+ tests)

Co-Authored-By: Claude <noreply@anthropic.com>"

# PR creation
gh pr create --title "feat(voice): Guided Dialog Engine" --body "..."
```

### Session Management
```markdown
## Session 2026-01-21

### Completed
- [x] Create guided_dialog.py (850 lines)
- [x] Create 5 vertical configs
- [x] Integrate with orchestrator.py
- [x] Create test suite

### In Progress
- [ ] Test on iMac with real DB

### Blocked
- None

### Next
- Test WhatsApp QR Scan UI
```

## Rules
1. SEMPRE fare breakdown Epic → Story → Task prima di codificare
2. SEMPRE usare RICE per prioritizzare
3. SEMPRE passare tutti i quality gates
4. MAI fare commit senza test
5. SEMPRE aggiornare CLAUDE.md a fine sessione
6. SEMPRE creare branch per feature
7. MAI pushare direttamente su main

## CI/CD Workflows
- `test-suite.yml` - Fast check (develop) + Full suite (PR)
- `e2e-tests.yml` - WebDriverIO (Linux only)
- `release.yml` - Build + release su tag v*

## Files to Reference
- `CLAUDE.md` - Stato progetto
- `docs/FLUXION-ORCHESTRATOR.md` - Procedure
- `.github/workflows/*.yml` - CI/CD
- `docs/context/SESSION-HISTORY.md` - Cronologia
