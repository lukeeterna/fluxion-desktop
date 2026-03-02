# CoVe 2026 — Skills Claude Code Enterprise Mapping
> Generato: 2026-03-02 | Agente: general-purpose | Research D1+Skills

---

## CoVe 2026 FASE → Skills Mapping

| Fase CoVe | Skills Ottimali | Quando Usarle |
|-----------|----------------|---------------|
| **FASE 1 RESEARCH** | `bmad-bmm-research` · `gsd:map-codebase` · `bmad-bmm-architect.agent` | Ogni nuovo task — research file PRIMA di qualsiasi implementazione |
| **FASE 2 PLAN** | `gsd:plan-phase` · `bmad-bmm-sprint-planning` · `bmad-review-adversarial-general` | Plan PLAN.md con acceptance criteria misurabili; review avversariale del piano |
| **FASE 3 IMPLEMENT** | `gsd:execute-phase` · `bmad-bmm-quick-dev` · `bmad-bmm-dev-story` · `bmad-bmm-dev.agent` | Implement atomico; dev-story per TDD; dev.agent per multi-file complex |
| **FASE 4 VERIFY** | `gsd:verify-work` · `bmad-bmm-code-review` · `bmad-bmm-testarch-nfr` · `gsd:debug` | Verifica acceptance criteria; adversarial review; NFR per performance |
| **FASE 5 DEPLOY** | `gsd:pause-work` · `bmad-bmm-retrospective` | HANDOFF.md update; retrospective dopo epic major |

---

## Task → Skills Mapping (FLUXION pending)

| Task | F1 Research | F2 Plan | F3 Implement | F4 Verify | F5 Deploy | Parallelizzabile? |
|------|-------------|---------|--------------|-----------|-----------|-------------------|
| **Rebuild DMG** | — (no code) | — | SSH iMac build | `gsd:verify-work` | `gsd:pause-work` | No — sequenziale |
| **D1 Screenshots** | ✅ fatto | `gsd:plan-phase` | Cattura manuale iMac | `gsd:verify-work` | `gsd:pause-work` | Cattura + optimize parallelo |
| **D2 Cloudflare** | — | — | ZIP+upload | `gsd:verify-work` | `gsd:pause-work` | Dopo D1 |
| **Fix SDI API key** | ✅ sdi-fatturapa-research.md | `gsd:plan-phase` | `bmad-bmm-quick-dev` | `bmad-bmm-code-review` | `gsd:pause-work` | Sì — parallelo con Dashboard KPI |
| **Dashboard KPI** | ✅ operatori-features-cove2026.md | `gsd:plan-phase` | `bmad-bmm-quick-dev` | `bmad-bmm-code-review` | `gsd:pause-work` | Sì — parallelo con SDI fix |
| **Schede Verticali** | `bmad-bmm-research` (NEW) | `gsd:plan-phase` | `bmad-bmm-dev-story` | `bmad-bmm-code-review` + `gsd:verify-work` | `gsd:pause-work` | Parrucchiere ∥ Fitness |
| **Voice Latency** | ✅ latency_optimizer.py esiste | `gsd:plan-phase` | `bmad-bmm-dev.agent` (Python iMac) | `bmad-bmm-testarch-nfr` | `gsd:pause-work` | No — iMac required |
| **LemonSqueezy** | `bmad-bmm-research` (NEW) | `gsd:plan-phase` + `bmad-bmm-architect.agent` | `bmad-bmm-dev.agent` | `bmad-bmm-code-review` + `gsd:verify-work` | `gsd:pause-work` | Sì con research parallela |
| **v1.0 Planning** | `bmad-bmm-research` | `bmad-bmm-sprint-planning` | — | `bmad-review-adversarial-general` | `gsd:pause-work` | Sì — research ∥ sprint planning |

---

## Enterprise Orchestration Pattern

### Pattern 1 — Parallel Research Wave (FASE 1)
```
# Quando si inizia un nuovo epic: lancia research in parallelo
Subagente A: bmad-bmm-research → [task]-research.md
Subagente B: gsd:map-codebase → codebase-gap-analysis.md
Subagente C: bmad-bmm-architect.agent → schema decisions
# Tutti scrivono in .claude/cache/agents/[task].md
# Main context legge i 3 file dopo → FASE 2
```

### Pattern 2 — Sequential Plan→Implement (FASE 2→3)
```
# gsd:plan-phase DEVE completare prima di gsd:execute-phase
# PLAN.md deve esistere con acceptance criteria MISURABILI
# Mai implementare senza PLAN.md
```

### Pattern 3 — Parallel Verify (FASE 4)
```
# Questi 3 possono girare in parallelo:
bmad-bmm-code-review     → code quality + anti-pattern
gsd:verify-work          → acceptance criteria check
bmad-bmm-testarch-nfr    → performance/security NFR
# Solo quando tutti e 3 passano → FASE 5
```

### Pattern 4 — FASE 5 Sempre Ultimo
```
# gsd:pause-work o bmad-bmm-retrospective SOLO dopo FASE 4 completa
# Mai deploy senza verifica
# Update HANDOFF.md + MEMORY.md sempre
```

---

## Template Invocazioni FLUXION

### Rebuild DMG (iMac)
```bash
# FASE 3: Build
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull && export PATH='/usr/local/bin:$PATH' && cargo tauri build 2>&1 | tail -20"
# FASE 4: Verifica
/gsd:verify-work — DMG si apre, icona Fluxion 3D visibile, versione 0.9.2
```

### D1 Screenshots
```bash
# FASE 1: Research completata (landing-screenshots-research.md)
# FASE 3: Cattura manuale su iMac (workflow in research file)
# FASE 4:
/gsd:verify-work — tutti 8 screenshot <250KB, no placeholder data, Sara pipeline visibile
```

### Fix SDI API Key (W1-A)
```bash
# FASE 2:
/gsd:plan-phase — migration 026, Rust struct update, Fatture.tsx fix, acceptance criteria
# FASE 3:
/bmad-bmm-quick-dev — implementa migration + Rust + UI in un atomic workflow
# FASE 4:
npm run type-check && /bmad-bmm-code-review adversarial
```

### Schede Verticali (W2-A/B)
```bash
# FASE 1:
/bmad-bmm-research schede-verticali: review SchedaOdontoiatrica pattern, migration 019 existing schema, Rust schede_cliente.rs commands
# FASE 2:
/gsd:plan-phase SchedaParrucchiere: schema capelli+colorazione+storico, Rust CRUD, React component replacing placeholder
# FASE 3:
/bmad-bmm-dev-story — TDD: failing test first, then implementation
# FASE 4:
/gsd:verify-work + /bmad-bmm-code-review adversarial
```

### LemonSqueezy Integration (futuro)
```bash
# FASE 1 (parallelo):
# Subagente A:
/bmad-bmm-research LemonSqueezy API: webhook events, license key validation, Ed25519 offline check, GDPR Italian data residency
# Subagente B:
/gsd:map-codebase focus=licensing — current license system in FLUXION
# FASE 2:
/gsd:plan-phase LemonSqueezy: webhook handler + DB migration + activation UI
/bmad-bmm-architect.agent — decisioni architetturali API key storage, webhook security
```

### v1.0 Planning
```bash
# FASE 1 (parallelo):
# Subagente A: /bmad-bmm-research — PMI italiana 2026 trends, competitor gaps
# Subagente B: /bmad-bmm-sprint-planning — epic breakdown v1.0
# FASE 2:
/gsd:plan-phase — wave plan v1.0 con Definition of Done misurabili
# FASE 4:
/bmad-review-adversarial-general — review avversariale del piano v1.0
```

---

## Anti-Pattern Vietati (CoVe 2026)

| Anti-pattern | Skill sbagliata | Skill corretta |
|-------------|----------------|----------------|
| Implement senza research | gsd:quick diretto | FASE 1 prima |
| Plan senza verifica avversariale | gsd:plan-phase solo | + bmad-review-adversarial-general |
| Verify solo con type-check | npm run type-check solo | + gsd:verify-work + bmad-bmm-code-review |
| Deploy senza HANDOFF update | git push diretto | + gsd:pause-work |
| Research inline nel contesto | inline text | subagente → file → leggi file |

---

*Fonte: Research agente general-purpose + WebSearch 2026 + analisi FLUXION codebase*
