# Prompt ripartenza S271 — cargo integration test BUG-FATT-3/4/6 (refactor extract internal_*)

## Stato chiusura S270 (VERDE)

**S270 outcome**: BUG-CLI-1 + BUG-CLI-2 + seed scripts annotation completati autonomously (REGOLA #14 rispettata, no founder click su Step 1/2/3/5). Step 4 restart SKIP (HMR Vite live + data fix non richiede restart). Step 6 cargo integration test → DEFER S271.

### Done S270
1. ✅ **BUG-CLI-1 DB cleanup**: backup `fluxion.db.pre-S270-bug-cli1-bak-20260520-133303` + DELETE 8 row `cli-anna|paolo|sara|marco|elena|giuseppe|francesca|andrea` + 3 row `fat-001|002|003` (+ fatture_righe FK). DB iMac final: 30 clienti encrypted, 1 fattura (S267 test `1/2026` id `18b0c1b033563330`), 0 seed cli-* residual.
2. ✅ **Seed scripts annotated TODO DEPRECATED** (5 file): `seed-test-data.sql`, `seed-sprint1-demo.sql`, `seed-video-demo.sql`, `seed-pacchetti-fedelta.sql`, `seed_demo_data.sql`. Header comment 5-line con riferimento BUG-CLI-1 (S269) + encrypt_clienti_pii_v1 (S256).
3. ✅ **BUG-CLI-2 fix `String(error)`**: `src/pages/Clienti.tsx:131` + `src/hooks/use-appuntamenti-ddd.ts:29`. Grep `'Unknown error'` literal in src/ post-fix = 0 match.
4. ✅ **Verify autonomous BUG-CLI-1** via HTTP Bridge `/api/clienti/search?q=a`: HTTP 200, 10 items returned, `seed_cli_residual=0`, sample plaintext decrypt OK (Stefano Rizzo / 3391234222). REGOLA #14 PASS — no founder UI required.
5. ✅ Type-check 0 errors, lint 0 errors (17 warnings preesistenti, NON introdotti S270).
6. ✅ Fix S268 sanity check repo: `save_fattura_xml_to_file` command present in `commands/fatture.rs`, `dialog:allow-save` in `capabilities/default.json`, 7 occurrences `encrypt_field|encrypt_required` in `commands/fatture.rs`.

### Defer S271
- **Cargo integration test BUG-FATT-3/4/6**: richiede refactor extract `internal_create_fattura(pool: &SqlitePool, ...)`, `internal_add_riga_fattura(...)`, `internal_update_impostazioni_fatturazione(...)`, `internal_save_fattura_xml_to_file(...)` da Tauri command wrappers per testability senza `tauri::State` runtime. Fuori scope S270 (S270 = BUG-CLI primary).
- **BUG-FATT-5 toast z-index live regression**: skip permanente — no UI rendering verify infra. Defer S275+ se Playwright + iMac X-display setup deciso.

---

## TASK S271

### Step 1: Refactor extract `internal_*` functions (4 file)
Spostare business logic da `#[tauri::command]` wrappers a funzioni pubbliche pool-based:

```rust
// src-tauri/src/commands/fatture.rs

pub async fn internal_create_fattura(
    pool: &SqlitePool,
    cliente_id: String,
    tipo_documento: Option<String>,
    data_emissione: String,
    /* ... */
) -> Result<Fattura, String> {
    // Tutta la logica esistente del command, ma usando &SqlitePool invece di State
}

#[tauri::command]
pub async fn create_fattura(
    pool: State<'_, SqlitePool>,
    /* ... */
) -> Result<Fattura, String> {
    internal_create_fattura(pool.inner(), cliente_id, /* ... */).await
}
```

Stesso pattern per:
- `add_riga_fattura` → `internal_add_riga_fattura`
- `update_impostazioni_fatturazione` → `internal_update_impostazioni_fatturazione`
- `save_fattura_xml_to_file` → `internal_save_fattura_xml_to_file`

### Step 2: Scrivere `tests/integration_fatture.rs`

```rust
// Test BUG-FATT-3 regression — cache stale FE (backend totale sync)
#[tokio::test]
async fn test_fattura_totale_aggiornato_dopo_add_riga() {
    let (pool, db_file) = create_test_database().await;
    insert_test_cliente_encrypted(&pool, "cli1", "Mario", "Rossi").await;
    insert_test_impostazioni_fatturazione(&pool).await;

    let fattura = internal_create_fattura(&pool, "cli1".into(), None, "2026-05-20".into(), /*...*/).await.unwrap();
    let riga = internal_add_riga_fattura(&pool, fattura.id.clone(), "Servizio".into(), 1.0, 15.0, 0.0, "N2.2".into(), /*...*/).await.unwrap();

    let fattura_aggiornata = internal_get_fattura(&pool, fattura.id.clone()).await.unwrap();
    assert_eq!(fattura_aggiornata.totale_documento, 15.0, "totale_documento deve riflettere riga aggiunta");
    cleanup_test_database(pool, db_file).await;
}

// Test BUG-FATT-4 regression — telefono encrypted
#[tokio::test]
async fn test_update_impostazioni_telefono_encrypted() {
    let (pool, db_file) = create_test_database().await;
    let updated = internal_update_impostazioni_fatturazione(&pool, /* with telefono="3331234567" */).await.unwrap();

    let raw_telefono: String = sqlx::query_scalar("SELECT telefono FROM impostazioni_fatturazione WHERE id = 1")
        .fetch_one(&pool).await.unwrap();
    assert!(raw_telefono.len() >= 16, "telefono deve essere ciphertext Base64");
    assert_ne!(raw_telefono, "3331234567", "NO plaintext leak");
    cleanup_test_database(pool, db_file).await;
}

// Test BUG-FATT-6 regression — XML file write
#[tokio::test]
async fn test_save_fattura_xml_to_file() {
    let (pool, db_file) = create_test_database().await;
    // setup fattura + xml_content
    let tmpfile = std::env::temp_dir().join("test_xml.xml");
    internal_save_fattura_xml_to_file(&pool, "fat-test".into(), tmpfile.to_string_lossy().to_string()).await.unwrap();

    assert!(tmpfile.exists());
    let content = std::fs::read_to_string(&tmpfile).unwrap();
    assert!(content.contains("<FatturaElettronica"));
    std::fs::remove_file(&tmpfile).ok();
    cleanup_test_database(pool, db_file).await;
}
```

### Step 3: Run tests + verify

```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion/src-tauri" && cargo test --test integration_fatture -- --nocapture 2>&1 | tail -50'
```

### Acceptance Criteria S271
- [ ] 4 `internal_*` functions estratte (create_fattura, add_riga_fattura, update_impostazioni_fatturazione, save_fattura_xml_to_file)
- [ ] Tauri command wrappers delegano a internal_* (no business logic duplication)
- [ ] `tests/integration_fatture.rs` 3 test PASS (BUG-FATT-3/4/6 regression)
- [ ] `cargo test --test integration_fatture` PASS
- [ ] type-check + lint + cargo check 0 errors
- [ ] No regression test esistenti (`cargo test --test integration_appuntamenti` PASS)

CLOSE VERDE se tutti AC PASS. Commit `refactor(S271): extract internal_* fatture functions + integration tests BUG-FATT-3/4/6`.

---

## Vincoli S271
- **REGOLA #14**: autonomous test+fix, cargo test = backend-side, no founder UI required.
- **REGOLA #11**: refactor cross-entity — pattern extract internal_* applicabile in futuro a `clienti.rs`, `operatori.rs`, `appuntamenti.rs` (S272+ se demand emerge).
- **REGOLA #6**: NO Co-Authored-By trailer.
- **Context budget**: refactor 4 file fatture.rs + new test file = task density alta. Monitor /context 50% raw, chiudi a 60%.

---

## PROMPT START S271

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S271.

REGOLA #14: autonomous backend-side (no founder UI).

Step 1: refactor src-tauri/src/commands/fatture.rs — extract internal_create_fattura, internal_add_riga_fattura, internal_update_impostazioni_fatturazione, internal_save_fattura_xml_to_file. Tauri command wrappers delegano.
Step 2: scrivere tests/integration_fatture.rs con 3 test regression (BUG-FATT-3/4/6).
Step 3: ssh imac cargo test --test integration_fatture --nocapture.

CLOSE VERDE se cargo test PASS.
```

---

**Provenienza S270 close**: VERDE pieno. 5/6 step completed autonomously (Step 4 N/A — no restart needed). Cargo integration test deferred S271 con plan refactor explicit.
