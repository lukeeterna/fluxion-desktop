# 🎯 PROMPT per Claude Opus - Generazione Test E2E FLUXION

**Destinatario**: Claude Opus 4.5
**Obiettivo**: Generare test E2E completi, production-ready per FLUXION Desktop App

---

## 📋 CONTESTO PROGETTO

### Applicazione
**FLUXION** è un gestionale desktop per PMI italiane (saloni, palestre, cliniche) costruito con:
- **Frontend**: React 19 + TypeScript + Tailwind CSS 3.4 + shadcn/ui
- **Backend**: Rust + Tauri 2.x + SQLite (SQLx)
- **Routing**: React Router v7
- **State Management**: TanStack Query v5 + Zustand
- **Form Validation**: React Hook Form + Zod
- **E2E Testing**: WebdriverIO 8.27 + CrabNebula tauri-driver (macOS)

### Entità Principali
1. **Clienti** (id, nome, cognome, email, telefono, indirizzo, note, deleted_at)
2. **Servizi** (id, nome, categoria, descrizione, prezzo, iva_percentuale, durata_minuti, buffer_minuti, colore, ordine, attivo)
3. **Operatori** (id, nome, cognome, email, telefono, ruolo, colore, attivo)
4. **Appuntamenti** (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, note, note_interne)

### Pagine App
- **Dashboard** (`/`) - Stats e overview
- **Clienti** (`/clienti`) - Tabella + CRUD clienti
- **Calendario** (`/calendario`) - Griglia mensile + booking appuntamenti
- **Servizi** (`/servizi`) - Tabella + CRUD servizi
- **Operatori** (`/operatori`) - Tabella + CRUD operatori
- **Fatture** (`/fatture`) - Placeholder
- **Impostazioni** (`/impostazioni`) - Placeholder

---

## 🏗️ STRUTTURA E2E ESISTENTE

```
e2e/
├── tests/                      # Test specs (QUESTI DEVI GENERARE)
│   ├── 01-smoke.spec.ts        # Esistente (da completare)
│   ├── 02-navigation.spec.ts   # Esistente (da completare)
│   ├── 03-clienti-crud.spec.ts # Esistente (da completare)
│   ├── 04-servizi-validation.spec.ts # Esistente (da completare)
│   ├── 05-appuntamenti-conflict.spec.ts # Esistente (da completare)
│   └── ... (NUOVI DA CREARE)
├── pages/                      # Page Objects (ESISTENTI - DA USARE)
│   ├── BasePage.ts
│   ├── DashboardPage.ts
│   ├── ClientiPage.ts
│   ├── ServiziPage.ts
│   ├── CalendarioPage.ts
│   └── index.ts
├── fixtures/
│   └── test-data.ts            # Esistente (DA ESTENDERE)
└── utils/
    └── test-helpers.ts         # Esistente (DA ESTENDERE)
```

---

## 🎯 COSA DEVI GENERARE

### 1. Test Specs Completi (File .spec.ts)

Genera i seguenti file di test **production-ready** e **completi**:

#### **PRIORITÀ ALTA** (Regression Tests per Bug Fixati)

**File**: `e2e/tests/06-regression-bug-fixes.spec.ts`
- Test specifici per verificare che i 3 bug fixati non regressino
- BUG #1: RFC3339 datetime format (appuntamenti creation)
- BUG #2: Error handling robusto (Tauri errors)
- BUG #3: Validazione form servizi (NaN → undefined)

#### **PRIORITÀ ALTA** (CRUD Completo)

**File**: `e2e/tests/07-operatori-crud.spec.ts`
- Create operatore (operatore + admin)
- Read operatori (tabella, search, filtri)
- Update operatore (edit form)
- Delete operatore (soft delete)
- Validazione form (email invalida, ecc.)

**File**: `e2e/tests/08-appuntamenti-crud.spec.ts`
- Create appuntamento completo
- Auto-fill prezzo/durata da servizio
- Edit appuntamento esistente
- Cambio stato (confermato → completato → cancellato)
- Delete appuntamento
- Note cliente e note interne

#### **PRIORITÀ MEDIA** (Workflow End-to-End)

**File**: `e2e/tests/09-booking-workflow-complete.spec.ts`
- Workflow completo: Cliente nuovo → Servizio → Operatore → Appuntamento → Visualizza in calendario
- Test il percorso "happy path" dall'inizio alla fine
- Verifica persistenza dati tra pagine

**File**: `e2e/tests/10-calendar-advanced.spec.ts`
- Navigazione calendario (prev/next month, oggi, year change)
- Visualizzazione appuntamenti nel calendario
- Filtri per operatore/servizio/stato
- Click su appuntamento (view details)
- Indicator "+N altri" quando >3 appuntamenti stesso giorno
- Stats footer aggiornato

**File**: `e2e/tests/11-search-and-filters.spec.ts`
- Search clienti (nome, cognome, telefono, email)
- Search servizi (nome, categoria)
- Search operatori (nome, ruolo)
- Filtri calendario (operatore, servizio, stato)
- Clear filters
- Case insensitive search

#### **PRIORITÀ MEDIA** (Edge Cases Avanzati)

**File**: `e2e/tests/12-edge-cases-advanced.spec.ts`
- Appuntamento a mezzanotte (23:30-00:05 cross-day)
- Appuntamenti back-to-back multipli (chain di 5)
- Conflict detection overlap (start during, end during, complete cover)
- Sconto 100% (prezzo finale = 0)
- Servizio con durata 8 ore (480 min)
- 10 appuntamenti stesso giorno (verifica "+N altri")
- Nome cliente/servizio con emoji, special chars, molto lungo

**File**: `e2e/tests/13-data-persistence.spec.ts`
- Crea cliente → naviga ad altra pagina → torna → verifica cliente esiste
- Crea appuntamento → chiudi app → riapri → verifica appuntamento presente
- Modifica servizio → reload → verifica modifiche salvate
- Test soft delete: elimina → non appare in lista → query DB verifica deleted_at

#### **PRIORITÀ BASSA** (Performance & Stress)

**File**: `e2e/tests/14-performance.spec.ts`
- Crea 100 clienti rapidamente (measure time)
- Crea 50 servizi
- Crea 200 appuntamenti
- Verifica tabelle scrollano smooth
- Verifica search performance con 100+ record
- Nessun memory leak dopo 50 dialog open/close

**File**: `e2e/tests/15-ui-responsiveness.spec.ts`
- Resize window (800px, 600px, fullscreen)
- Sidebar collapse/expand
- Tabelle responsive (scroll orizzontale se necessario)
- Dialog responsive
- Calendar grid responsive

**File**: `e2e/tests/16-keyboard-accessibility.spec.ts`
- Tab navigation tra form fields
- Enter per submit form
- ESC per chiudere dialog
- Arrow keys in dropdowns
- Focus visibile su tutti elementi

#### **PRIORITÀ BASSA** (Error Handling)

**File**: `e2e/tests/17-error-scenarios.spec.ts`
- Form validation errors display
- Network error handling (simula API down)
- Database lock error
- Invalid data input recovery
- Timeout handling
- Duplicate entry errors

---

### 2. Estensioni Fixtures (`fixtures/test-data.ts`)

Aggiungi alla sezione **TestData**:

```typescript
// GENERA QUESTA SEZIONE
export const TestData = {
  // ... esistente ...

  // NUOVI DA AGGIUNGERE:
  appuntamenti: {
    standard: { /* ... */ },
    backToBack: { /* ... */ },
    overlapping: { /* ... */ },
    crossDay: { /* ... */ },
    getUnique: () => ({ /* ... */ }),
  },

  workflows: {
    completeBooking: { /* ... */ },
    multipleAppointmentsSameDay: [ /* ... */ ],
  },

  performance: {
    bulkClienti: (count: number) => [ /* ... */ ],
    bulkServizi: (count: number) => [ /* ... */ ],
    bulkAppuntamenti: (count: number) => [ /* ... */ ],
  },
};
```

---

### 3. Estensioni Helper Functions (`utils/test-helpers.ts`)

Aggiungi queste funzioni:

```typescript
// GENERA QUESTE FUNZIONI

/**
 * Create cliente and return ID
 */
export async function createTestCliente(data?: Partial<Cliente>): Promise<string>

/**
 * Create servizio and return ID
 */
export async function createTestServizio(data?: Partial<Servizio>): Promise<string>

/**
 * Create operatore and return ID
 */
export async function createTestOperatore(data?: Partial<Operatore>): Promise<string>

/**
 * Create appuntamento and return ID
 */
export async function createTestAppuntamento(data: CreateAppuntamentoInput): Promise<string>

/**
 * Complete booking workflow (cliente → servizio → operatore → appuntamento)
 */
export async function completeBookingWorkflow(): Promise<{
  clienteId: string;
  servizioId: string;
  operatoreId: string;
  appuntamentoId: string;
}>

/**
 * Navigate to calendar and verify month/year
 */
export async function navigateToCalendarMonth(year: number, month: number): Promise<void>

/**
 * Count appointments in calendar for specific date
 */
export async function getAppointmentCountForDate(date: string): Promise<number>

/**
 * Measure operation time
 */
export async function measureTime<T>(operation: () => Promise<T>): Promise<{ result: T; timeMs: number }>

/**
 * Create bulk entities for performance testing
 */
export async function createBulkClienti(count: number): Promise<string[]>
export async function createBulkServizi(count: number): Promise<string[]>
export async function createBulkAppuntamenti(count: number): Promise<string[]>

/**
 * Database verification helpers
 */
export async function verifyClienteInDB(id: string): Promise<boolean>
export async function verifyServizioActive(id: string): Promise<boolean>
export async function verifyAppuntamentoExists(id: string): Promise<boolean>
```

---

### 4. Nuove Page Objects Extensions

Aggiungi metodi mancanti ai Page Objects esistenti:

#### `DashboardPage.ts` - Aggiungi:
```typescript
async getStatsValues(): Promise<{ clienti: number; appuntamenti: number; fatturato: number }>
async verifyStatsUpdated(expected: Partial<StatsValues>): Promise<void>
```

#### `ClientiPage.ts` - Aggiungi:
```typescript
async searchAndVerifyResults(query: string, expectedCount: number): Promise<void>
async editClienteByRow(rowIndex: number, newData: Partial<Cliente>): Promise<void>
async verifyClienteInTable(nome: string, cognome: string): Promise<boolean>
```

#### `ServiziPage.ts` - Aggiungi:
```typescript
async editServizioByRow(rowIndex: number, newData: Partial<Servizio>): Promise<void>
async verifyServizioPrice(nome: string, expectedPrice: number): Promise<void>
async deleteServizioByRow(rowIndex: number): Promise<void>
```

#### `CalendarioPage.ts` - Aggiungi:
```typescript
async navigateToMonthYear(year: number, month: number): Promise<void>
async getAppointmentsForDate(date: string): Promise<AppuntamentoDettagliato[]>
async verifyAppointmentInCalendar(date: string, clienteNome: string): Promise<boolean>
async clickFilterByOperatore(operatoreId: string): Promise<void>
async getCalendarStats(): Promise<{ count: number; text: string }>
```

#### `OperatoriPage.ts` - NUOVO FILE DA CREARE:
```typescript
export class OperatoriPage extends BasePage {
  // Selectors, actions per CRUD operatori
  // Simile a ClientiPage ma per operatori
}
```

---

## 📐 FORMATO OUTPUT RICHIESTO

Per **ogni file** che generi, usa questo formato:

```markdown
## 📄 File: `e2e/tests/XX-nome-file.spec.ts`

```typescript
// CODICE COMPLETO DEL FILE
// Includi TUTTI gli import necessari
// Includi TUTTI i test descritti sopra
// Aggiungi commenti esplicativi
// Usa i Page Objects esistenti
// Usa i test fixtures esistenti
// Aggiungi assertion chiare
// Aggiungi screenshot su failure
```

---

**Nota**: Per ogni file generato, NON scrivere "// TODO" o placeholder. Ogni test deve essere **completo ed eseguibile**.
```

---

## 🎯 PRIORITÀ E ORDINE DI GENERAZIONE

Genera i file in questo ordine:

1. **PRIMA**: `06-regression-bug-fixes.spec.ts` (CRITICO)
2. **SECONDA**: `07-operatori-crud.spec.ts` + `08-appuntamenti-crud.spec.ts` (CRUD mancanti)
3. **TERZA**: `09-booking-workflow-complete.spec.ts` (Happy path)
4. **QUARTA**: `10-calendar-advanced.spec.ts` + `11-search-and-filters.spec.ts`
5. **QUINTA**: `12-edge-cases-advanced.spec.ts` + `13-data-persistence.spec.ts`
6. **SESTA**: `14-performance.spec.ts` + `15-ui-responsiveness.spec.ts` + `16-keyboard-accessibility.spec.ts`
7. **ULTIMA**: `17-error-scenarios.spec.ts`

8. **POI**: Estensioni `test-helpers.ts`
9. **POI**: Estensioni `test-data.ts`
10. **INFINE**: Nuovi metodi Page Objects + `OperatoriPage.ts`

---

## 🔧 SELETTORI DA USARE

Dato che **non abbiamo ancora data-testid**, usa questi pattern di selettori:

### Selettori Generici (da aggiornare dopo)
```typescript
// Buttons
'button:has-text("Nuovo Cliente")'
'button:has-text("Crea Servizio")'
'button[type="submit"]'

// Forms
'input[name="nome"]'
'input[name="email"]'
'input[name="prezzo"]'
'select[name="cliente_id"]'

// Tables
'table tbody tr'
'table tbody tr:nth-child(1)'

// Dialogs
'[role="dialog"]'
'[role="alertdialog"]'

// Navigation
'nav a:has-text("Clienti")'
'h1:has-text("Calendario")'

// Calendar
'button:has-text("←")'  // prev month
'button:has-text("→")'  // next month
'button:has-text("Oggi")'
```

### Nota sui Selettori
- Usa **text-based selectors** dove possibile (più stabili)
- Usa **`name` attributes** per form fields (esistono già)
- Aggiungi commenti `// TODO: Replace with data-testid once available`
- Preferisci selettori **semantici** (role, aria-label)

---

## ✅ QUALITY REQUIREMENTS

Ogni test DEVE:

1. **Essere Completo**: Nessun TODO, nessun placeholder
2. **Essere Isolato**: Non dipendere da altri test
3. **Avere Setup**: `beforeEach` per stato iniziale
4. **Avere Cleanup**: `afterEach` per cleanup
5. **Usare Waits**: `waitFor*` invece di `pause`
6. **Avere Assertion**: `expect(...)` chiare e precise
7. **Gestire Errori**: Try-catch dove necessario
8. **Screenshot**: Su failure automatico
9. **Commenti**: Spiega cosa fa ogni sezione
10. **Performance**: Non usare sleep inutili

---

## 📝 ESEMPIO TEST COMPLETO

```typescript
// e2e/tests/06-regression-bug-fixes.spec.ts

import { dashboardPage, calendarioPage, clientiPage, serviziPage } from '../pages';
import { TestData } from '../fixtures/test-data';
import { generateAppointmentDateTime, waitForPageLoad } from '../utils/test-helpers';

describe('Regression Tests - Bug Fixes', () => {
  beforeEach(async () => {
    await waitForPageLoad();
  });

  describe('BUG #1 - RFC3339 Datetime Format', () => {
    it('should create appointment with datetime-local format (YYYY-MM-DDTHH:mm)', async () => {
      // Setup: Navigate to calendar
      await dashboardPage.navigateToCalendario();
      await waitForPageLoad();

      // Create appointment with datetime-local format
      const appointmentData = {
        clienteId: 'test-cliente-id', // TODO: Get real ID from created cliente
        servizioId: 'test-servizio-id',
        operatoreId: 'test-operatore-id',
        dataOraInizio: generateAppointmentDateTime(1, 10), // Format: YYYY-MM-DDTHH:mm
        durata: 30,
        prezzo: 25.0,
      };

      await calendarioPage.createAppuntamento(appointmentData);

      // Verify: Dialog closes successfully (no datetime parse error)
      await calendarioPage.waitUntil(
        async () => !(await calendarioPage.isDialogOpen()),
        {
          timeout: 5000,
          timeoutMsg: 'BUG #1 REGRESSION: Datetime format not converted to RFC3339',
        }
      );

      // Verify: No error message displayed
      const hasError = await calendarioPage.hasConflictError();
      expect(hasError).toBe(false);
    });

    it('should handle various datetime formats gracefully', async () => {
      // Test multiple datetime formats
      const formats = [
        '2025-01-05T14:30',       // Standard datetime-local
        '2025-01-05T14:30:00',    // With seconds
        '2025-01-05T14:30:00Z',   // With timezone
      ];

      for (const format of formats) {
        await calendarioPage.clickNuovoAppuntamento();

        // Fill form with specific datetime format
        await calendarioPage.fillAppuntamentoForm({
          clienteId: 'test-cliente-id',
          servizioId: 'test-servizio-id',
          operatoreId: 'test-operatore-id',
          dataOraInizio: format,
          durata: 30,
        });

        await calendarioPage.saveAppuntamento();

        // Should succeed for all formats
        const dialogClosed = !(await calendarioPage.isDialogOpen());
        expect(dialogClosed).toBe(true);
      }
    });
  });

  describe('BUG #2 - Error Handling Robustness', () => {
    it('should display error message when conflict occurs (not crash)', async () => {
      await dashboardPage.navigateToCalendario();

      // Create first appointment
      const appointmentTime = generateAppointmentDateTime(2, 15);
      await calendarioPage.createAppuntamento({
        clienteId: 'test-cliente-id',
        servizioId: 'test-servizio-id',
        operatoreId: 'test-operatore-id',
        dataOraInizio: appointmentTime,
        durata: 30,
      });

      await browser.pause(1000);

      // Try to create conflicting appointment
      await calendarioPage.createAppuntamento({
        clienteId: 'test-cliente-id-2',
        servizioId: 'test-servizio-id',
        operatoreId: 'test-operatore-id', // SAME operator
        dataOraInizio: appointmentTime,    // SAME time
        durata: 30,
      });

      await browser.pause(1000);

      // Verify: Error message is displayed (not undefined crash)
      const hasConflictError = await calendarioPage.hasConflictError();
      expect(hasConflictError).toBe(true);

      // Verify: App didn't crash (dialog still open)
      const dialogStillOpen = await calendarioPage.isDialogOpen();
      expect(dialogStillOpen).toBe(true);
    });
  });

  describe('BUG #3 - Form Validation (NaN → undefined)', () => {
    it('should block submit when prezzo is empty', async () => {
      await dashboardPage.navigateToServizi();
      await serviziPage.clickNuovoServizio();

      // Fill only nome, leave prezzo and durata empty
      await serviziPage.fillServizioForm({
        nome: 'Test Servizio No Price',
        // prezzo: undefined, // Intentionally empty
        // durata: undefined, // Intentionally empty
      });

      await serviziPage.saveServizio();
      await browser.pause(1000);

      // Verify: Form validation blocks submit
      const dialogStillOpen = await serviziPage.isDialogOpen();
      expect(dialogStillOpen).toBe(true);

      // Verify: Servizio was NOT created
      const initialCount = await serviziPage.getTableRowCount();
      // Count should not increase
    });

    it('should block submit when durata is empty', async () => {
      await dashboardPage.navigateToServizi();
      await serviziPage.clickNuovoServizio();

      await serviziPage.fillServizioForm({
        nome: 'Test Servizio No Duration',
        prezzo: 25.0,
        // durata: undefined, // Intentionally empty
      });

      await serviziPage.saveServizio();
      await browser.pause(1000);

      const dialogStillOpen = await serviziPage.isDialogOpen();
      expect(dialogStillOpen).toBe(true);
    });

    it('should allow creation with all required fields', async () => {
      await dashboardPage.navigateToServizi();

      const servizio = TestData.servizi.getUnique();
      await serviziPage.createServizio(servizio);

      // Should succeed
      const dialogClosed = !(await serviziPage.isDialogOpen());
      expect(dialogClosed).toBe(true);
    });
  });

  afterEach(async function () {
    if (this.currentTest?.state === 'failed') {
      const testName = this.currentTest.title.replace(/\s+/g, '-');
      await browser.saveScreenshot(`./e2e/data/screenshots/regression-${testName}.png`);
    }
  });
});
```

---

## 🎯 DELIVERABLE FINALE

Al termine, fornisci:

1. **Tutti i file .spec.ts** generati (10 file)
2. **Estensioni test-helpers.ts** (funzioni aggiunte)
3. **Estensioni test-data.ts** (fixtures aggiunti)
4. **Nuovi metodi Page Objects** (per file esistenti)
5. **Nuovo file OperatoriPage.ts** (completo)
6. **Summary Table** con:
   - File generato
   - Numero test inclusi
   - Coverage (cosa testa)
   - Priorità (Alta/Media/Bassa)

---

## 📋 SUMMARY TABLE TEMPLATE

Genera anche questa tabella alla fine:

```markdown
| File | Tests | Coverage | Priority |
|------|-------|----------|----------|
| 06-regression-bug-fixes.spec.ts | 7 | BUG #1,#2,#3 regression | 🔴 ALTA |
| 07-operatori-crud.spec.ts | 12 | Operatori CRUD completo | 🔴 ALTA |
| ... | ... | ... | ... |
```

---

## ⚠️ CONSTRAINTS

1. **NO PLACEHOLDER CODE**: Ogni test deve essere eseguibile
2. **NO TODO COMMENTS**: Solo se davvero necessario (es. selector da aggiornare)
3. **USE EXISTING PAGE OBJECTS**: Non riscrivere selettori, usa i PO
4. **USE EXISTING FIXTURES**: Riusa TestData dove possibile
5. **FOLLOW MOCHA/WEBDRIVERIO SYNTAX**: Sintassi corretta
6. **ADD TYPES**: TypeScript strict mode compliant
7. **HANDLE ASYNC**: Tutti i metodi async con await
8. **ERROR HANDLING**: Try-catch dove appropriato

---

## 🚀 START GENERATING

**Inizia con il file di MASSIMA PRIORITÀ**: `06-regression-bug-fixes.spec.ts`

Poi procedi in ordine di priorità elencato sopra.

Per ogni file, usa il formato:

```markdown
---
## 📄 File: `e2e/tests/XX-nome.spec.ts`

```typescript
[CODICE COMPLETO]
```

**Motivazione test inclusi**: [Breve spiegazione]
**Coverage**: [Cosa viene testato]
---
```

**GENERA ORA TUTTI I FILE!** 🚀
