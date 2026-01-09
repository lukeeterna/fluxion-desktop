# 🏛️ FLUXION Test Protocol - Tauri Edition

> **Enterprise-Grade Testing for Tauri Desktop App**  
> Completo, binding, adattato a FLUXION architecture

---

## DOCUMENT CONTROL

| Proprietà | Valore |
|-----------|--------|
| **Nome** | FLUXION Test Protocol - Tauri Edition |
| **Versione** | 1.0 |
| **Data** | 2026-01-09 |
| **Status** | 🟢 ACTIVE - BINDING |
| **Stack** | Tauri + React + Rust + SQLite |
| **Owner** | Gianluca di Stasi (Lead Architect) |
| **Binding** | Claude Code MUST follow this |

---

# SEZIONE 1: TESTING PYRAMID FOR TAURI

```
                        ▲
                       /|\
                      / | \
                     /  |  \
                    /   |   \
                   /  AI Live \ 
                  /  Test Agent \
                 /      (slow)    \
                /___________________\
               /                     \
              /   E2E Tests (slow)    \
             / WebDriverIO + Tauri    \
            /___________________________\
           /                           \
          /  Integration Tests (medium) \
         / Tauri IPC + SQLite queries    \
        /_______________________________ \
       /                                 \
      /  Unit Tests (fast)                \
     / Rust backend + React components    \
    /_____________________________________\
    
    Speed:     Fast → Slow
    Cost:      Cheap → Expensive
    Coverage:  Low → High
    Frequency: Every commit → Nightly
```

---

# SEZIONE 2: TESTING LAYERS SPECIFICATION

## Layer 1: Unit Tests (FAST)

### Frontend (React + TypeScript)

**Tools:** Vitest + React Testing Library  
**Location:** `src/**/*.test.tsx`  
**Command:** `npm run test:unit:frontend`

**Copertura obbligatoria:**
- ✅ Components rendering
- ✅ Hooks logic (useState, useContext)
- ✅ Business logic functions
- ✅ Utilities (formatters, validators)
- ✅ Error boundaries

**Example:**
```typescript
// src/components/BookingForm/BookingForm.test.tsx
describe('BookingForm', () => {
  it('should validate date is future', () => {
    render(<BookingForm />);
    const input = screen.getByLabelText('Data');
    fireEvent.change(input, { target: { value: '2020-01-01' } });
    expect(screen.getByText(/data non valida/i)).toBeInTheDocument();
  });
});
```

**Target:** ≥ 80% coverage on component logic

### Backend (Rust)

**Tools:** Rust built-in `#[cfg(test)]`  
**Location:** `src-tauri/src/**/*.rs` with `#[test]` modules  
**Command:** `cargo test --lib`

**Copertura obbligatoria:**
- ✅ Core business logic (booking rules, pricing, etc.)
- ✅ Data validation
- ✅ Database queries (SQLite integration)
- ✅ Error handling

**Example:**
```rust
// src-tauri/src/models/booking.rs
#[cfg(test)]
mod tests {
  use super::*;

  #[test]
  fn test_booking_date_must_be_future() {
    let past_date = "2020-01-01";
    let result = validate_booking_date(past_date);
    assert!(result.is_err());
  }

  #[test]
  fn test_calculate_price_correctly() {
    let booking = Booking::new(3, 2, "2026-02-01");
    assert_eq!(booking.calculate_price(), 300.0);
  }
}
```

**Target:** ≥ 75% coverage on core business logic

---

## Layer 2: Integration Tests (MEDIUM)

### Tauri IPC Command Tests

**Tools:** Tauri test harness + custom integration tests  
**Location:** `src-tauri/tests/**/*.rs`  
**Command:** `cargo test --test '*'`

**Copertura obbligatoria:**
- ✅ Tauri command invocation (Rust → Frontend)
- ✅ Database state persistence
- ✅ Error propagation
- ✅ Command parameter validation

**Example:**
```rust
// src-tauri/tests/booking_integration.rs
#[tokio::test]
async fn test_create_booking_persists_to_db() {
  // Setup
  let app = setup_test_app().await;
  
  // Execute
  let result = app.invoke_command("create_booking", json!({
    "date": "2026-02-01",
    "guests": 3
  })).await;
  
  // Verify
  assert!(result.is_ok());
  
  // Check DB
  let booking = db::get_booking_by_id(result.unwrap()).await;
  assert_eq!(booking.guest_count, 3);
}
```

### API/HTTP Tests (if applicable)

**Tools:** `reqwest` + `tokio`  
**Location:** `src-tauri/tests/http_*.rs`  
**Command:** `cargo test --test 'http_*'`

**Copertura obbligatoria:**
- ✅ HTTP endpoint responses
- ✅ Status codes (200, 400, 500)
- ✅ JSON serialization/deserialization
- ✅ Authentication (if any)

---

## Layer 3: E2E Tests (SLOW)

### WebDriverIO + Tauri Driver

**Tools:** WebDriverIO + `@tauri-apps/webdriver`  
**Location:** `tests/e2e/**/*.spec.ts`  
**Command:** `npm run test:e2e`

**Copertura obbligatoria:**
- ✅ Happy path scenarios (complete user workflows)
- ✅ Error handling (invalid inputs, network issues)
- ✅ Visual/layout consistency
- ✅ Integration between frontend and backend

**Setup (Tauri WebDriver):**

```typescript
// tests/e2e/wdio.config.ts
export const config = {
  runner: 'local',
  port: 4444,
  capabilities: [
    {
      'tauri:options': {
        application: path.join(__dirname, '../../src-tauri/target/release/fluxion'),
        args: ['--dev']  // Or release build
      }
    }
  ],
  specs: ['./tests/e2e/**/*.spec.ts'],
  framework: 'mocha',
};
```

**Example Test:**

```typescript
// tests/e2e/booking.spec.ts
describe('Booking Workflow', () => {
  it('should complete booking end-to-end', async () => {
    // 1. Open app
    await browser.url('about:blank');
    
    // 2. Navigate to booking page
    const bookingButton = await $('button[href="/booking"]');
    await bookingButton.click();
    
    // 3. Fill form
    const dateInput = await $('input#booking-date');
    await dateInput.setValue('2026-02-01');
    
    const guestInput = await $('input#guests');
    await guestInput.setValue('3');
    
    // 4. Submit
    const submitBtn = await $('button[type="submit"]');
    await submitBtn.click();
    
    // 5. Verify success
    await browser.waitUntil(
      async () => {
        const confirmation = await $('.booking-confirmation');
        return confirmation.isDisplayed();
      },
      { timeout: 5000 }
    );
    
    // 6. Verify DB (via Tauri command)
    const booking = await browser.executeScript('window.__TAURI__.invoke("get_last_booking")', []);
    expect(booking.guest_count).toBe(3);
  });
});
```

**Test Scenarios (Mandatory):**

1. **Happy Path - Booking Creation**
   - Open app → Navigate to booking → Fill form → Submit → Verify DB

2. **Happy Path - Customer Management**
   - Create customer → Edit info → Verify persisted

3. **Happy Path - Invoice Generation**
   - Create invoice → Generate PDF → Verify file exists

4. **Error Handling - Invalid Input**
   - Try invalid date → See error message → Form still functional

5. **State Persistence**
   - Create booking → Close app → Reopen → Verify booking still there

---

## Layer 4: AI Live Testing (via HTTP Bridge)

**Tools:** Claude MCP + HTTP Bridge (port 3001)  
**Location:** `mcp-server/scenarios/fluxion-*.ts`  
**Trigger:** Every PR + nightly cron

**Mandatory Scenarios:**

### Scenario A: Core Workflow (Booking)

```markdown
1. STEP: Start app (verify HTTP bridge responds)
   - GET http://127.0.0.1:3001/health → 200 OK

2. STEP: Booking flow (via browser automation)
   - MCP: navigate to /booking
   - MCP: fill date, guests, submit
   - Verify: success message shown
   - Verify: HTTP requests all 2xx
   - Verify: no JS errors in console

3. STEP: Verify persistence
   - MCP: reload app
   - Verify: booking still visible in list
```

### Scenario B: Data Integrity

```markdown
1. Create 3 bookings via app
2. Verify SQLite has exactly 3 rows in bookings table
3. Modify one booking date
4. Verify change persisted
5. Delete one booking
6. Verify count = 2
```

### Scenario C: Error Recovery

```markdown
1. Try invalid action (e.g., create booking without date)
2. Verify error message displays
3. Verify form is still usable
4. Verify no crash/JS error
```

### Scenario D: UI Consistency

```markdown
1. Take screenshot of main screen
2. Compare against baseline (first run creates baseline)
3. If diff > 5%, flag as visual regression
```

---

# SEZIONE 3: TEST MATRIX - FLUXION MODULES

```
┌────────────────────────┬──────────┬──────┬────────┬─────┬──────────┬──────┐
│ MODULO                 │ Criticità│ Unit │ Integ  │ E2E │ AI Live  │ Perf │
├────────────────────────┼──────────┼──────┼────────┼─────┼──────────┼──────┤
│ 📅 Calendario & Appt   │ 🔴 CRIT  │ ✅   │ ✅     │ ✅  │ ✅       │ ✅   │
│ 👥 CRM Clienti        │ 🔴 CRIT  │ ✅   │ ✅     │ ✅  │ ✅       │ ⬜   │
│ 📄 Fatturazione        │ 🔴 CRIT  │ ✅   │ ✅     │ ✅  │ ⬜       │ ⬜   │
│ 💰 Cassa & Scontrini   │ 🟠 ALTA  │ ✅   │ ✅     │ ⬜  │ ⬜       │ ⬜   │
│ 🎙️ Voice Agent        │ 🟠 ALTA  │ ✅   │ ✅     │ ⬜  │ ✅       │ ⬜   │
│ 📊 Reporting           │ 🟡 MEDIA │ ✅   │ ✅     │ ⬜  │ ⬜       │ ⬜   │
│ 🔄 Sync/Export         │ 🟡 MEDIA │ ✅   │ ✅     │ ⬜  │ ⬜       │ ⬜   │
│ 🎨 UI Components       │ 🟢 BASSA │ ✅   │ ⬜     │ ⬜  │ ⬜       │ ⬜   │

Legenda: ✅ Obbligatorio | ⬜ Facoltativo
```

### Dettagli Modulo: Calendario & Appuntamenti

**Criticità:** 🔴 CRITICA  
**Perché:** Core business - prenotazioni dipendono da questo

**Unit Tests Richiesti (Frontend):**
- ✅ `test_calendar_renders_correct_month()`
- ✅ `test_date_selection_marks_as_selected()`
- ✅ `test_disabled_past_dates()`
- ✅ `test_booking_slot_calculation()`

**Unit Tests Richiesti (Backend/Rust):**
- ✅ `test_availability_check_for_date()`
- ✅ `test_booking_conflict_detection()`
- ✅ `test_slot_occupancy_calculation()`

**Integration Tests Richiesti:**
- ✅ `test_create_booking_updates_calendar()`
- ✅ `test_cancel_booking_frees_slot()`
- ✅ `test_db_consistency_after_bulk_operations()`

**E2E Tests Richiesti:**
- ✅ `test_e2e_complete_booking_flow()` (Scenario A)

**AI Live Tests:**
- ✅ Scenario A (Booking workflow)
- ✅ Scenario B (Data integrity check)

---

### Dettagli Modulo: CRM Clienti

**Criticità:** 🔴 CRITICA  
**Perché:** Dato fondamentale, tutto dipende da questo

**Unit Tests Richiesti:**
- ✅ `test_validate_email_format()`
- ✅ `test_validate_phone_format()`
- ✅ `test_duplicate_email_prevention()`

**Integration Tests:**
- ✅ `test_create_customer_in_db()`
- ✅ `test_update_customer_persists()`
- ✅ `test_customer_delete_soft_delete()`

**E2E Tests:**
- ✅ `test_e2e_customer_crud_operations()`

**AI Live Tests:**
- ✅ Scenario B (Data integrity - customer data)

---

### Dettagli Modulo: Fatturazione Elettronica

**Criticità:** 🔴 CRITICA  
**Perché:** Obbligo legale Italia, errori = sanzioni

**Unit Tests Richiesti:**
- ✅ `test_invoice_number_generation_unique()`
- ✅ `test_invoice_date_format_italian_standard()`
- ✅ `test_vat_calculation_correct()`
- ✅ `test_xml_generation_valid_schema()`

**Integration Tests:**
- ✅ `test_invoice_saved_to_db()`
- ✅ `test_pdf_generation_produces_file()`
- ✅ `test_pos_xml_export_format()`

**E2E Tests:**
- ✅ `test_e2e_create_and_export_invoice()`

---

### Dettagli Modulo: Cassa & Scontrini

**Criticità:** 🟠 ALTA  
**Perché:** Operazioni quotidiane, scontrini legali

**Unit Tests Richiesti:**
- ✅ `test_calculate_total_with_discounts()`
- ✅ `test_cash_register_balance()`
- ✅ `test_receipt_line_formatting()`

**Integration Tests:**
- ✅ `test_transaction_persisted_to_db()`
- ✅ `test_daily_closing_accuracy()`

---

### Dettagli Modulo: Voice Agent

**Criticità:** 🟠 ALTA  
**Perché:** Feature differenziante

**Unit Tests Richiesti:**
- ✅ `test_voice_command_parsing()`
- ✅ `test_intent_recognition_accuracy()`
- ✅ `test_response_generation()`

**Integration Tests:**
- ✅ `test_voice_agent_creates_booking()`
- ✅ `test_voice_agent_queries_calendar()`

**AI Live Tests:**
- ✅ Scenario C (Voice agent interaction)

---

# SEZIONE 4: CI/CD WORKFLOW

## GitHub Actions: test-suite.yml

```yaml
name: 🧪 Test Suite - Tauri Edition

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [main]

jobs:
  frontend-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm install
      - run: npm run test:unit:frontend -- --coverage
      - uses: codecov/codecov-action@v3

  rust-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test --lib
      - run: cargo tarpaulin --out Xml
      - uses: codecov/codecov-action@v3

  integration:
    runs-on: ubuntu-latest
    needs: [frontend-unit, rust-unit]
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: actions/setup-node@v4
      - run: npm install
      - run: cargo test --test '*'

  e2e:
    runs-on: macos-latest  # Tauri needs real window server
    needs: integration
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install
      - name: Install WebDriver
        run: npm install -g webdriverio @tauri-apps/webdriver
      - name: Build Tauri
        run: npm run build:tauri
      - name: Run E2E tests
        run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: e2e-failures
          path: test-results/

  ai-live:
    runs-on: macos-latest
    needs: e2e
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install
      - run: npm run dev &
      - run: npm run start -w mcp-server &
      - run: sleep 5
      - run: npm run test:ai-live
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: ai-live-report
          path: test-reports/

  auto-github-issues:
    if: failure()
    needs: [frontend-unit, rust-unit, integration, e2e, ai-live]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create issue for test failure
        uses: actions/github-script@v7
        with:
          script: |
            const failedJobs = context.payload.workflow_run.jobs_url
              .filter(job => job.conclusion === 'failure')
              .map(job => job.name);
            
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `🚨 CI Test Failed: ${failedJobs.join(', ')}`,
              body: `Test suite failed on commit ${context.sha}\n\n[View workflow run](${context.server_url}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId})`,
              labels: ['bug/ci-detected', 'critical'],
              assignees: ['@maintainer']  // Auto-assign to you
            });

  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install
      - run: npx eslint src --max-warnings 0
      - run: npx tsc --noEmit
```

## Nightly Full Test Run

```yaml
name: 🌙 Nightly Full Test Suite

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM CET

jobs:
  full-suite:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install
      - run: cargo test --lib
      - run: cargo test --test '*'
      - run: npm run test:unit:frontend -- --coverage
      - run: npm run test:e2e
      - run: npm run test:ai-live:full
      
      - name: Generate metrics report
        run: npm run metrics:export
      
      - name: Update Grafana dashboard
        uses: grafana/update-dashboard-action@v1
        with:
          dashboard-id: fluxion-metrics
          metrics: ./metrics/report.json
```

---

# SEZIONE 5: GitHub Issues Integration

## Auto-Create Issue on Test Failure

```typescript
// scripts/auto-create-issue.ts
import { Octokit } from "@octokit/rest";

export async function createTestFailureIssue(
  failedTest: string,
  errorLog: string,
  commitSha: string
) {
  const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
  
  const issue = await octokit.issues.create({
    owner: "gianlucadistasi",
    repo: "fluxion",
    title: `🐛 [CI] Test Failed: ${failedTest}`,
    body: `
## Test Failure Report

**Test:** ${failedTest}
**Commit:** \`${commitSha}\`
**Time:** ${new Date().toISOString()}

### Error Log
\`\`\`
${errorLog}
\`\`\`

### Next Steps
- [ ] Reproduce locally
- [ ] Identify root cause
- [ ] Fix code
- [ ] Verify test passes
- [ ] Commit with message: "Fix: [ISSUE-XXX] ..."
`,
    labels: ["bug/ci-detected", "priority/high"],
    assignees: ["@gianlucadistasi"]
  });
  
  console.log(`✅ Created issue: ${issue.data.html_url}`);
  return issue.data.number;
}
```

## Auto-Close Issue on Fix

```typescript
// When test passes and PR merged
await octokit.issues.createComment({
  owner: "gianlucadistasi",
  repo: "fluxion",
  issue_number: issueNumber,
  body: `✅ Fixed in commit ${commitSha}\n\n[PR #${prNumber}](${prUrl))`
});

await octokit.issues.update({
  owner: "gianlucadistasi",
  repo: "fluxion",
  issue_number: issueNumber,
  state: "closed"
});
```

---

# SEZIONE 6: EXECUTION CHECKLIST FOR CLAUDE CODE

## PRE-MODIFICATION

```markdown
[ ] Ho letto questo documento (FLUXION-TEST-PROTOCOL.md)
[ ] Ho letto severity_policy.md
[ ] Ho identificato moduli toccati dalla mia modifica
[ ] Guardo test_matrix.md: quali test sono obbligatori?

Moduli toccati: _______________________
Test obbligatori: ______________________
```

## DURANTE IMPLEMENTAZIONE

```markdown
[ ] Se tocco frontend React:
    [ ] Ho scritto unit test (Vitest + RTL)
    [ ] Coverage >= 80% su component logic
    [ ] Ho provato: npm run test:unit:frontend

[ ] Se tocco backend Rust:
    [ ] Ho scritto unit test (#[test] module)
    [ ] Coverage >= 75% su business logic
    [ ] Ho provato: cargo test --lib

[ ] Se tocco API/IPC:
    [ ] Ho scritto integration test
    [ ] Ho provato: cargo test --test '*'

[ ] Code quality:
    [ ] npm run lint (ESLint 0 warnings)
    [ ] npx tsc --noEmit (no TypeScript errors)
```

## DOPO - BEFORE MERGE

```markdown
[ ] npm run test:unit:frontend → ✅ GREEN
[ ] cargo test --lib → ✅ GREEN
[ ] cargo test --test '*' → ✅ GREEN
[ ] npm run lint → ✅ PASS (0 warnings)
[ ] GitHub Actions all jobs → ✅ GREEN

[ ] Nel commit message ho incluso:
    "Tested: unit-frontend✅ unit-rust✅ integration✅"

[ ] Nel PR description ho:
    - Elencato test aggiunti/modificati
    - Indicato scenario coperto
    - Confermato severità (se feature/bug)

[ ] Zero Blocker/Critical aperti su modulo toccato
[ ] PR approvato da lead architect
```

## SE FALLISCE UNO DEI TEST

```markdown
❌ Test fallisce → Non posso fare commit
   Azione: Debuggo e fisso finché test non passa

❌ GitHub Actions fallisce → Merge bloccato
   Azione: Leggo error log, ripasso da "DURANTE"

❌ E2E test fallisce → Auto-create GitHub Issue
   Azione: Investigare root cause, fix, rerun

❌ Coverage scende < target → Merge bloccato
   Azione: Aggiungere test finché coverage >= target
```

---

**Document Owner:** Gianluca di Stasi  
**Status:** 🟢 ACTIVE - BINDING  
**Last Updated:** 2026-01-09  
**Stack:** Tauri + React + Rust + SQLite  
**Next Review:** 2026-02-09