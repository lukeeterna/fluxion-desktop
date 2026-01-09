# FLUXION Test Matrix - Module Coverage

> **Per-Module Test Requirements**  
> Master reference per quali test sono obbligatori

---

## Master Matrix

```
┌────────────────────────┬──────────┬──────┬────────┬─────┬──────────┬──────┐
│ MODULO                 │ Criticità│ Unit │ Integ  │ E2E │ AI Live  │ Perf │
├────────────────────────┼──────────┼──────┼────────┼─────┼──────────┼──────┤
│ 📅 Calendario & Appt   │ 🔴 CRIT  │ ✅   │ ✅     │ ✅  │ ✅       │ ✅   │
│ 👥 CRM Clienti        │ 🔴 CRIT  │ ✅   │ ✅     │ ✅  │ ✅       │ ⬜   │
│ 📄 Fatturazione        │ 🔴 CRIT  │ ✅   │ ✅     │ ✅  │ ⬜       │ ⬜   │
│ 💰 Cassa & Scontrini   │ 🟠 ALTA  │ ✅   │ ✅     │ ⬜  │ ⬜       │ ✅   │
│ 🎙️ Voice Agent        │ 🟠 ALTA  │ ✅   │ ✅     │ ⬜  │ ✅       │ ⬜   │
│ 📊 Reporting           │ 🟡 MEDIA │ ✅   │ ✅     │ ⬜  │ ⬜       │ ⬜   │
│ 🔄 Sync/Export         │ 🟡 MEDIA │ ✅   │ ✅     │ ⬜  │ ⬜       │ ⬜   │
│ 🎨 UI Components       │ 🟢 BASSA │ ✅   │ ⬜     │ ⬜  │ ⬜       │ ⬜   │

Legenda: ✅ Obbligatorio | ⬜ Facoltativo (consigliato)
```

---

## MODULO 1: Calendario & Appuntamenti (🔴 CRITICA)

### Criticità
**Highest Priority** - Core business: prenotazioni dipendono da questo

### Unit Tests Richiesti (Frontend - Vitest + React Testing Library)

```typescript
// src/components/Calendar/Calendar.test.tsx
describe('Calendar Component', () => {
  it('should render calendar for current month', () => {
    render(<Calendar />);
    expect(screen.getByText(/january 2026/i)).toBeInTheDocument();
  });
  
  it('should disable past dates', () => {
    render(<Calendar />);
    const pastDate = screen.getByLabelText('2026-01-01');
    expect(pastDate).toHaveAttribute('disabled');
  });
  
  it('should mark selected date as highlighted', () => {
    render(<Calendar onDateSelect={jest.fn()} />);
    fireEvent.click(screen.getByText('15'));
    expect(screen.getByText('15')).toHaveClass('selected');
  });
  
  it('should show availability slots for selected date', () => {
    render(<Calendar />);
    fireEvent.click(screen.getByText('15'));
    expect(screen.getByText(/available slots/i)).toBeInTheDocument();
  });
});
```

### Unit Tests Richiesti (Backend - Rust)

```rust
// src-tauri/src/models/calendar.rs
#[cfg(test)]
mod tests {
  use super::*;
  
  #[test]
  fn test_availability_check_returns_available_slots() {
    let date = "2026-02-15";
    let slots = check_availability(date).unwrap();
    assert!(slots.len() > 0);
  }
  
  #[test]
  fn test_booking_prevents_double_booking() {
    create_booking("2026-02-15", "14:00", 3).unwrap();
    let result = create_booking("2026-02-15", "14:00", 2);
    assert!(result.is_err()); // Should fail
  }
  
  #[test]
  fn test_slot_occupancy_calculation() {
    let occupancy = calculate_occupancy("2026-02-15", "14:00");
    assert!(occupancy <= 100);
  }
}
```

### Integration Tests Richiesti (Cargo)

```rust
// src-tauri/tests/booking_integration.rs
#[tokio::test]
async fn test_create_booking_updates_calendar() {
  let db = setup_test_db().await;
  
  let booking = create_booking(
    &db,
    "2026-02-15",
    "14:00",
    3
  ).await.unwrap();
  
  let availability = get_availability(&db, "2026-02-15").await;
  let time_slot = availability.iter()
    .find(|s| s.time == "14:00")
    .unwrap();
  
  assert_eq!(time_slot.available_seats, 0); // Slot now full
}

#[tokio::test]
async fn test_cancel_booking_frees_slot() {
  let db = setup_test_db().await;
  
  let booking_id = create_booking(&db, "2026-02-15", "14:00", 3)
    .await.unwrap().id;
  
  cancel_booking(&db, booking_id).await.unwrap();
  
  let availability = get_availability(&db, "2026-02-15").await;
  let time_slot = availability.iter()
    .find(|s| s.time == "14:00")
    .unwrap();
  
  assert_eq!(time_slot.available_seats, 3); // Slot freed
}
```

### E2E Tests Richiesti (WebDriverIO)

```typescript
// tests/e2e/booking.spec.ts
describe('Booking Workflow E2E', () => {
  it('should complete full booking flow', async () => {
    // Navigate to booking
    await browser.url('about:blank');
    const bookingBtn = await $('button[href="/booking"]');
    await bookingBtn.click();
    
    // Select date
    const dateInput = await $('input#booking-date');
    await dateInput.setValue('2026-02-15');
    
    // Select time
    const timeSelect = await $('select#time');
    await timeSelect.selectByAttribute('value', '14:00');
    
    // Enter guests
    const guestInput = await $('input#guests');
    await guestInput.setValue('3');
    
    // Submit
    const submitBtn = await $('button[type="submit"]');
    await submitBtn.click();
    
    // Verify success
    await browser.waitUntil(
      async () => {
        const confirmation = await $('.booking-confirmation');
        return confirmation.isDisplayed();
      },
      { timeout: 5000 }
    );
    
    // Verify DB
    const bookingData = await browser.executeScript(
      'return window.__TAURI__.invoke("get_last_booking")',
      []
    );
    expect(bookingData.guest_count).toBe(3);
  });
});
```

### AI Live Tests Richiesti

✅ **Scenario A** - Complete booking workflow (vedi FLUXION-TEST-PROTOCOL.md)

### Performance Tests Richiesti

- ✅ Availability check < 100ms
- ✅ Booking creation < 500ms
- ✅ Calendar rendering < 200ms

---

## MODULO 2: CRM Clienti (🔴 CRITICA)

### Criticità
**Highest Priority** - Dato fondamentale, tutto dipende da clienti

### Unit Tests

```typescript
// src/utils/validation.test.ts
describe('Customer Validation', () => {
  it('should validate email format', () => {
    expect(validateEmail('test@example.com')).toBe(true);
    expect(validateEmail('invalid-email')).toBe(false);
  });
  
  it('should validate phone format (Italian)', () => {
    expect(validatePhone('+39 3331234567')).toBe(true);
    expect(validatePhone('123')).toBe(false);
  });
});
```

```rust
// src-tauri/src/models/customer.rs
#[cfg(test)]
mod tests {
  #[test]
  fn test_duplicate_email_prevention() {
    create_customer("test@example.com", "John").unwrap();
    let result = create_customer("test@example.com", "Jane");
    assert!(result.is_err()); // Should fail - duplicate
  }
  
  #[test]
  fn test_customer_delete_is_soft_delete() {
    let customer_id = create_customer("test@example.com", "John")
      .unwrap().id;
    delete_customer(customer_id).unwrap();
    
    let customer = get_customer(customer_id);
    assert!(customer.is_some()); // Still in DB
    assert!(customer.unwrap().deleted_at.is_some()); // But marked deleted
  }
}
```

### Integration Tests

```rust
#[tokio::test]
async fn test_create_customer_in_db() {
  let db = setup_test_db().await;
  
  let customer = create_customer(
    &db,
    "john@example.com",
    "John Doe",
    "+39 3331234567"
  ).await.unwrap();
  
  let retrieved = get_customer(&db, customer.id).await.unwrap();
  assert_eq!(retrieved.name, "John Doe");
}
```

### E2E Tests

```typescript
describe('Customer CRUD', () => {
  it('should create, edit, and delete customer', async () => {
    // Navigate to CRM
    const crmBtn = await $('button[href="/crm"]');
    await crmBtn.click();
    
    // Create customer
    const createBtn = await $('button[aria-label="new-customer"]');
    await createBtn.click();
    
    const nameInput = await $('input#customer-name');
    await nameInput.setValue('John Doe');
    
    const emailInput = await $('input#customer-email');
    await emailInput.setValue('john@example.com');
    
    const saveBtn = await $('button.save-customer');
    await saveBtn.click();
    
    // Verify in list
    await expect($('text=John Doe')).toBeDisplayed();
  });
});
```

### AI Live Tests

✅ **Scenario B** - Data integrity (customer data persistence)

---

## MODULO 3: Fatturazione Elettronica (🔴 CRITICA)

### Criticità
**COMPLIANCE CRITICAL** - Obbligo legale Italia, errori = sanzioni

### Unit Tests (MUST BE COMPREHENSIVE)

```rust
#[test]
fn test_invoice_number_generation_is_unique() {
  let num1 = generate_invoice_number();
  let num2 = generate_invoice_number();
  assert_ne!(num1, num2);
  assert!(num1.starts_with("FLX"));
}

#[test]
fn test_invoice_date_format_follows_italian_standard() {
  let invoice = create_invoice("2026-02-15".to_string(), vec![]);
  assert_eq!(invoice.date_format(), "15/02/2026"); // Italian format
}

#[test]
fn test_vat_calculation_correct() {
  let line = InvoiceLine::new(100.0, 0.22); // 22% VAT
  assert_eq!(line.calculate_vat(), 22.0);
  assert_eq!(line.total(), 122.0);
}

#[test]
fn test_xml_generation_valid_schema() {
  let invoice = create_test_invoice();
  let xml = invoice.to_xml_string().unwrap();
  
  // Validate against Italian FatturaPA schema
  assert!(xml.contains("<FatturaElettronicaBody>"));
  assert!(xml.contains("<DatiGenerali>"));
  assert!(xml.contains("PA")); // PEC destination
}
```

### Integration Tests

```rust
#[tokio::test]
async fn test_invoice_saved_to_db_and_recoverable() {
  let db = setup_test_db().await;
  
  let invoice = create_invoice(&db, test_invoice_data()).await.unwrap();
  let retrieved = get_invoice(&db, invoice.id).await.unwrap();
  
  assert_eq!(retrieved.number, invoice.number);
  assert_eq!(retrieved.total, invoice.total);
}

#[tokio::test]
async fn test_pdf_generation_produces_valid_file() {
  let invoice = create_test_invoice();
  let pdf_path = invoice.generate_pdf().await.unwrap();
  
  // Verify file exists and has content
  assert!(tokio::fs::metadata(&pdf_path).await.is_ok());
  let size = tokio::fs::metadata(&pdf_path).await.unwrap().len();
  assert!(size > 1000); // PDF should be > 1KB
}

#[tokio::test]
async fn test_pos_xml_export_format() {
  let invoice = create_test_invoice();
  let xml = invoice.to_pos_xml().await.unwrap();
  
  assert!(xml.contains("<?xml version"));
  assert!(xml.contains("<POS"));
}
```

### E2E Tests

```typescript
describe('Invoice Creation & Export', () => {
  it('should create invoice and export to PDF', async () => {
    // Navigate to fatturazione
    await browser.url('about:blank');
    const fatturLink = await $('button[href="/invoices"]');
    await fatturLink.click();
    
    // Create invoice
    const createBtn = await $('button.new-invoice');
    await createBtn.click();
    
    // Fill customer
    const customerSelect = await $('select#invoice-customer');
    await customerSelect.selectByAttribute('value', 'CUST001');
    
    // Add line item
    const descInput = await $('input#item-desc');
    await descInput.setValue('Servizio di prenotazione');
    
    const amountInput = await $('input#item-amount');
    await amountInput.setValue('100.00');
    
    // Submit
    const saveBtn = await $('button.save-invoice');
    await saveBtn.click();
    
    // Verify invoice created
    await expect($('text=FLX-2026-001')).toBeDisplayed();
    
    // Export to PDF
    const exportBtn = await $('button[aria-label="export-pdf"]');
    await exportBtn.click();
    
    // Verify PDF downloaded
    const downloadPath = '/downloads/invoice_FLX-2026-001.pdf';
    await browser.waitUntil(
      async () => fileExists(downloadPath),
      { timeout: 5000 }
    );
  });
});
```

---

## MODULO 4: Cassa & Scontrini (🟠 ALTA)

### Unit Tests
- ✅ `test_calculate_total_with_discounts`
- ✅ `test_calculate_total_with_vat`
- ✅ `test_cash_register_balance`

### Integration Tests
- ✅ `test_transaction_persisted_to_db`
- ✅ `test_daily_closing_accuracy`

### Performance Tests
- ✅ Transaction < 200ms
- ✅ Daily closing < 2 sec

---

## MODULO 5: Voice Agent (🟠 ALTA)

### Unit Tests
- ✅ `test_voice_command_parsing`
- ✅ `test_intent_recognition`
- ✅ `test_response_generation`

### Integration Tests
- ✅ `test_voice_agent_creates_booking`
- ✅ `test_voice_agent_queries_calendar`

### AI Live Tests
- ✅ Scenario A (voice booking creation)

---

## How Claude Uses This Matrix

**When modifying ANY code:**

```typescript
// 1. Identify modules touched
const modulesTouched = ['Calendario & Appuntamenti'];

// 2. Look up test_matrix.md
const testsRequired = {
  'Calendario & Appuntamenti': ['unit', 'integration', 'e2e', 'ai-live', 'perf']
};

// 3. Run all required tests
npm run test:unit:frontend -- --matching='calendar'
cargo test --lib
cargo test --test '*booking*'
npm run test:e2e -- --spec='booking'
npm run test:ai-live -- scenario-a

// 4. If ANY fail → don't commit
// 5. If ALL pass → safe to commit
```

---

**Document Owner:** Gianluca di Stasi  
**Status:** 🟢 ACTIVE - BINDING  
**Last Updated:** 2026-01-09  
**Stack:** Tauri + React + Rust + SQLite