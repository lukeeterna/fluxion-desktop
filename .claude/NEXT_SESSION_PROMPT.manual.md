# Prompt ripartenza S272 — BUG-FATT-7 code prevention (auto-repair plaintext residual cross-entity)

## Stato chiusura S271 (VERDE)

**S271 outcome**: refactor `internal_*` fatture + 4 cargo integration test PASS + 0 regression. Tutti AC raggiunti.

### Done S271
1. ✅ **6 funzioni pool-based estratte** in `src-tauri/src/commands/fatture.rs`:
   - `internal_get_impostazioni_fatturazione`, `internal_update_impostazioni_fatturazione`
   - `internal_create_fattura`, `internal_add_riga_fattura`, `internal_update_fattura_totals`, `internal_save_fattura_xml_to_file`
   - Tauri command wrappers delegano in 1 riga (zero business logic duplication)
2. ✅ **Lib export**: `pub mod commands` + `pub mod encryption` in `lib.rs` (richiesto da integration test).
3. ✅ **`tests/integration_fatture.rs`** — 4 test PASS:
   - BUG-FATT-3 regression `test_fattura_totale_aggiornato_dopo_add_riga`
   - BUG-FATT-4 regression `test_update_impostazioni_telefono_encrypted`
   - BUG-FATT-6 happy path `test_save_fattura_xml_to_file`
   - BUG-FATT-6 edge cases `test_save_fattura_xml_path_validation`
4. ✅ **Fix collaterale `tests/common/mod.rs`**: replicata logica prod `run_migration` (statement-by-statement + error swallow) per sbloccare migrations storiche (`013_waitlist` CREATE INDEX `priorita_valore`).
5. ✅ **Verify autonomous via SSH iMac**: `cargo test --test integration_fatture` 4/4 PASS in 5.62s + `--test integration_appuntamenti` 9/9 PASS (no regression).
6. ✅ Cargo check 0 errori, lint 0 errori, type-check 0 errori. Commit `e0321bf` + `bc098b3` master MacBook+iMac sync.

### Defer S272
- **BUG-FATT-7 code prevention**: boot sequence step `verify_or_repair_encryption` post-migration runner che rileva plaintext residual (es. `length(denominazione) < 30` AND marker applied = anomaly) → re-encrypt via Rust direct. Stesso pattern audit applicabile a `clienti`, `operatori`, `suppliers`, `impostazioni_fatturazione` (REGOLA #11 cross-entity).
- **Pattern internal_* cross-entity** (low priority, on-demand): replicare refactor S271 su `clienti.rs`, `operatori.rs`, `appuntamenti.rs` solo se serve testability backend-side senza Tauri State.
- **BUG-FATT-5 toast z-index**: skip permanente — no UI rendering verify infra senza Playwright + iMac X-display setup.

---

## TASK S272

### Goal
Prevenire ricaduta BUG-FATT-7 (S270 hotfix runtime) via code: rilevare plaintext residual post-migration encryption marker e re-encrypt automatico al boot. Cross-entity (clienti, operatori, suppliers, impostazioni_fatturazione).

### Step 1: Spec funzione `verify_or_repair_encryption`

Nuovo modulo `src-tauri/src/data_migration/repair.rs` (o estensione esistente `data_migration/`):

```rust
pub async fn verify_or_repair_encryption(pool: &SqlitePool) -> Result<RepairReport, String> {
    // Per ogni (tabella, colonna_sentinella, marker_migration):
    //   1. Verifica che marker_migration sia applied
    //   2. Query SELECT id, colonna FROM tabella WHERE colonna IS NOT NULL AND colonna != ''
    //   3. Per ogni row: tenta decrypt_field; se fail → plaintext residual
    //   4. Re-encrypt + UPDATE row con ciphertext
    //   5. Log audit in repair_report
}

pub struct RepairReport {
    pub total_scanned: usize,
    pub plaintext_residuals_repaired: usize,
    pub per_table: Vec<TableRepair>,
}
```

**Tabelle target** (audit sentinella per detection):
| Tabella | Colonna sentinella | Marker migration |
|---------|-------------------|------------------|
| `clienti` | `nome` | `encrypt_clienti_pii_v1` |
| `operatori` | `nome` | `encrypt_operatori_pii_v1` |
| `suppliers` | `denominazione` | `encrypt_suppliers_pii_v1` |
| `impostazioni_fatturazione` | `denominazione` | `encrypt_impostazioni_fatturazione_pii_v1` |

**Detection logic**: tentativo `decrypt_field(value)` — se ritorna `Err` con "invalid base64" o "decrypt failed" → plaintext. Idempotente: ciphertext valido decifra correttamente → skip.

### Step 2: Chiamata da boot sequence

In `src-tauri/src/lib.rs::init_database` (o equivalente entry point post-migrations):
```rust
match crate::data_migration::repair::verify_or_repair_encryption(&pool).await {
    Ok(report) => {
        if report.plaintext_residuals_repaired > 0 {
            println!("✓ [verify_or_repair_encryption] repaired {} plaintext residuals", ...);
        }
    }
    Err(e) => eprintln!("⚠️  [verify_or_repair_encryption] {}", e), // non-fatal
}
```

### Step 3: Integration test

`src-tauri/tests/integration_encryption_repair.rs`:
1. Setup test DB con marker applied + INSERT manuale di 1 row plaintext (bypass encrypt path)
2. `verify_or_repair_encryption(&pool)` → assert `plaintext_residuals_repaired == 1`
3. Re-run su DB già repaired → assert `plaintext_residuals_repaired == 0` (idempotency)
4. Verify ciphertext post-repair: `decrypt_field(value)` returns plaintext originale

### Acceptance Criteria S272
- [ ] `data_migration/repair.rs` con `verify_or_repair_encryption` per 4 tabelle
- [ ] Chiamata boot post-migrations in `lib.rs`
- [ ] `tests/integration_encryption_repair.rs` PASS (3 scenari: residual detected+repaired, idempotency, roundtrip post-repair)
- [ ] No regression `cargo test --test integration_fatture` + `--test integration_appuntamenti`
- [ ] type-check + lint + cargo check 0 errori

CLOSE VERDE se tutti AC PASS. Commit `feat(S272): verify_or_repair_encryption boot step + cross-entity test`.

---

## Vincoli S272
- **REGOLA #14**: autonomous backend-side, cargo test, no founder UI required.
- **REGOLA #11**: pattern cross-entity (4 tabelle) — audit consistency anti-pattern.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **REGOLA #2**: Verifica fattuale — `decrypt_field` error variants prima di scrivere detection. Check `src-tauri/src/encryption.rs` linee 154+ per pattern errori esatti.
- **Context budget**: nuovo modulo + test file + lib.rs edit (file critico) = ricerca + plan dovrebbero stare sotto 50% raw. Se sopra 50% prima di Step 2, schedule next session.

---

## PROMPT START S272

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S272.

REGOLA #14: autonomous backend-side (no founder UI).

Step 1: implementa src-tauri/src/data_migration/repair.rs::verify_or_repair_encryption per 4 tabelle (clienti/operatori/suppliers/impostazioni_fatturazione).
Step 2: chiama da lib.rs boot post-migrations (non-fatal su error).
Step 3: scrivere tests/integration_encryption_repair.rs con 3 scenari (detect+repair, idempotency, roundtrip).

Verify: ssh imac cargo test --test integration_encryption_repair --nocapture + no regression integration_fatture/appuntamenti.

CLOSE VERDE se cargo test PASS.
```

---

**Provenienza S271 close**: VERDE pieno. 6/6 AC raggiunti + 1 bonus (4° test path validation + fix collaterale common/mod.rs sblocca anche integration_appuntamenti pre-broken).
