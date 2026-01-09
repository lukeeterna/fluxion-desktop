# FLUXION Severity & Release Policy

> **Bug Management + Release Gates**  
> Adattato a FLUXION (GitHub Issues, Tauri desktop)

---

## 1. Bug Severity Levels

### 🔴 BLOCKER
- **Definizione:** App non avviabile o feature core completamente inutilizzabile
- **Esempi:**
  - App crash all'avvio (Tauri non inizializza)
  - Database corrotto, SQLite error
  - Tutti gli utenti non possono accedere
  - Cassa completamente bloccata (nessuno può fare transazione)
- **SLA:** Fix entro **1 ora**
- **Blocca Release?** ✅ **SI - IMMEDIATAMENTE**
- **GitHub Label:** `severity:blocker` + `priority:critical`

### 🟠 CRITICAL
- **Definizione:** Feature core degradata gravemente, rischio perdita dati o legale
- **Esempi:**
  - Doppia prenotazione possibile (overbooking)
  - Fattura generata con IVA errata (obbligo legale)
  - Dati clienti corrotti
  - Scontrino non registrato in cassa (tracciabilità legale)
  - Voice Agent non risponde (feature chiave)
- **SLA:** Fix entro **4 ore**
- **Blocca Release?** ✅ **SI - su area interessata**
- **GitHub Label:** `severity:critical`

### 🟡 MAJOR
- **Definizione:** Feature importante non funziona ma workaround esiste
- **Esempi:**
  - Booking fallisce al primo tentativo, OK al secondo
  - Export PDF lento (> 30 sec)
  - UI visibilmente misallineata su piccoli schermi
  - Filtri CRM non performanti
- **SLA:** Fix entro **24 ore**
- **Blocca Release?** ⚠️ **CASO - richiede coordinamento**
- **GitHub Label:** `severity:major`

### 🟢 MINOR
- **Definizione:** Non blocca operazioni, UX leggermente degradata
- **Esempi:**
  - Typo in etichetta
  - Icona misallineata di 2px
  - Tooltip poco chiaro
- **SLA:** Fix in sprint successivo
- **Blocca Release?** ❌ **NO**
- **GitHub Label:** `severity:minor`

### ⚪ TRIVIAL
- **Definizione:** Puramente cosmetico
- **SLA:** Quando conveniente
- **Blocca Release?** ❌ **NO**
- **GitHub Label:** `severity:trivial`

---

## 2. Release Gate Checklist

**Nessuna release è possibile se UNA sola di queste fallisce:**

```markdown
[ ] ✅ Zero BLOCKER aperti
[ ] ✅ Zero CRITICAL aperti su aree toccate da questa release
[ ] ✅ Tutti i test PASS:
    [ ] Frontend unit tests >= 80% coverage
    [ ] Rust unit tests >= 75% coverage
    [ ] Integration tests all PASS
    [ ] E2E tests all PASS (WebDriverIO)
    [ ] AI Live tests all PASS
[ ] ✅ Code quality PASS:
    [ ] ESLint 0 warnings
    [ ] TypeScript --strict no errors
    [ ] Rust clippy clean
[ ] ✅ Performance OK:
    [ ] App startup < 3 sec
    [ ] Booking creation < 1 sec
    [ ] Invoice export < 5 sec
[ ] ✅ Changelog aggiornato:
    [ ] Features listed
    [ ] Bug fixes listed
    [ ] Known issues listed
[ ] ✅ Sign-offs:
    [ ] Lead Architect (Gianluca) approval
    [ ] Code review complete
```

Se blocco: Crea GitHub Issue con label `release-blocker` e discuti.

---

## 3. GitHub Issues Labeling System

### Severity Labels
- `severity:blocker` (🔴 1h SLA)
- `severity:critical` (🟠 4h SLA)
- `severity:major` (🟡 24h SLA)
- `severity:minor` (🟢 72h SLA)
- `severity:trivial` (⚪ when convenient)

### Type Labels
- `bug` (defect)
- `feature` (new capability)
- `enhancement` (improve existing)
- `test` (testing infrastructure)
- `docs` (documentation)

### Detection Labels
- `bug/ci-detected` (found by test suite)
- `bug/user-reported` (reported by user)
- `bug/manual-qa` (found during manual testing)

### Area Labels
- `area:booking` (Calendario & Appuntamenti)
- `area:crm` (CRM Clienti)
- `area:invoice` (Fatturazione)
- `area:cashier` (Cassa & Scontrini)
- `area:voice` (Voice Agent)
- `area:reporting` (Reporting)
- `area:ui` (UI Components)
- `area:backend` (Rust backend)

### Status Labels
- `status:open` (new issue)
- `status:in-progress` (being worked on)
- `status:testing` (ready for test)
- `status:blocked` (waiting for something)
- `status:closed` (resolved)

### Priority Labels
- `priority:critical` (drop everything)
- `priority:high` (this week)
- `priority:medium` (this sprint)
- `priority:low` (backlog)

---

## 4. Release Decision Tree

```
Code is ready for release
    ↓
Check release gate checklist
    ↓
All items ✅?
├─ YES → Can release
│        [ ] Update version in Cargo.toml + package.json
│        [ ] Create git tag: v1.2.3
│        [ ] Build release: npm run build:release
│        [ ] Upload to server/store
│        [ ] Close release-related GitHub issues
│        [ ] Announce in Slack #releases
│
└─ NO → Release BLOCKED
        [ ] Create GitHub Issue: "🚨 Release Blocked: [reason]"
        [ ] Label: release-blocker
        [ ] Assign to: Gianluca
        [ ] Set milestone: "Release v1.2.3"
        [ ] Fix issues until checklist ✅
        [ ] Close blocker issue
        [ ] Retry release gate
```

---

## 5. SLA Enforcement

### Blocker (🔴 1h SLA)

| Time | Action |
|------|--------|
| 0-15 min | Issue created, auto-assigned |
| 15-30 min | 1st escalation (Slack alert #critical) |
| 30-45 min | 2nd escalation (Slack @gianluca) |
| 45-60 min | 3rd escalation (page if sleeping) |
| 60+ min | Escalate to VP Eng |

### Critical (🟠 4h SLA)

| Time | Action |
|------|--------|
| 0-1h | Issue created |
| 1h | Slack notification #qa-alerts |
| 2h | Progress update expected |
| 4h | Fix expected or plan created |

---

## 6. Known Issue Release (Exception)

**Scenario:** Major/Minor bug ma release timing is critical

**Process:**
1. CTO + Product **concordano per iscritto** su Slack
2. Create GitHub Issue with label `known-issue/accepted`
3. Document workaround in CHANGELOG
4. Set milestone: "Release v1.2.3"
5. Include in release notes: "⚠️ Known Issues"
6. Jira target fix date (e.g., "Fix in v1.2.4, due 2026-02-09")

**Example Changelog:**
```markdown
## v1.2.3 - 2026-02-01

### ⚠️ Known Issues
- [#412] Booking export slow for > 1000 records
  Workaround: Export in smaller batches
  Target fix: v1.2.4 (2026-02-09)
```

---

## 7. Rollback Decision

**When to rollback release:**

✅ If BLOCKER found in production within 1 hour  
✅ If data corruption discovered  
✅ If compliance violation (e.g., wrong invoice format)  
❌ For Minor/Trivial issues (hotfix instead)

**Procedure:**
1. CTO authorizes rollback (Slack #releases)
2. GitHub Actions trigger: "Rollback to v1.2.2"
3. QA verifies app stable on old version
4. Post-mortem: "Why wasn't this caught in testing?"
5. Jira ticket: "[ROOT CAUSE] Bug X escaped release gate"
6. Update test_matrix.md to prevent similar escape

---

**Document Owner:** Gianluca di Stasi  
**Status:** 🟢 ACTIVE - BINDING  
**Last Updated:** 2026-01-09  
**Stack:** GitHub Issues, Tauri