# Prompt ripartenza S273 — backlog opzionale (CTO discrezione)

## Stato chiusura S272 (VERDE pieno)

**S272 outcome** (commit `7ebe7c7` master MacBook+iMac sync): BUG-FATT-7 prevention via code safety net. Tutti gli AC raggiunti.

### Done S272
1. ✅ **`src-tauri/src/data_migration.rs`** esteso con `verify_or_repair_encryption(pool)` cross-entity 4 tabelle (clienti / operatori / suppliers / impostazioni_fatturazione) — marker-gated detection + decrypt_field oracle + UPDATE in place per plaintext residual. ~120 righe append.
2. ✅ **`src-tauri/src/lib.rs`**: `pub mod data_migration` export + chiamata post 4 marker-gated runners (non-fatal log + sentry warn su error, silent log su 0 repairs).
3. ✅ **`src-tauri/tests/integration_encryption_repair.rs`** — 4 test PASS in 0.20s:
   - `test_repair_detects_and_fixes_plaintext_residual` (BUG-FATT-7 regression core)
   - `test_repair_is_idempotent_on_clean_db` (byte-equality cross-pass)
   - `test_repair_skips_tables_without_marker` (pre-migration untouched)
   - `test_repair_cross_entity_4_tables` (4-table single-pass + 2nd pass = 0)
4. ✅ **No regression**: integration_fatture 4/4 PASS + integration_appuntamenti 9/9 PASS.
5. ✅ Cargo check 0 errori, pre-commit hook PASS (type-check + lint clean).

### Defer S273 (opzionale, on-demand)
- **Pattern internal_* cross-entity**: applicare refactor S271 (extract `internal_*` pool-based fns da Tauri wrappers) su `clienti.rs`, `operatori.rs`, `appuntamenti.rs` SOLO se serve testability backend-side senza Tauri State. Low priority — no demand attiva.
- **BUG-FATT-5 toast z-index**: skip permanente — no Playwright + iMac X-display infra.
- **Boot live verify S272**: prossima volta che founder lancia app GUI iMac (Keychain unlock required), log atteso `🔧 PII repair: ...` SOLO se DB ha plaintext residual reale. Se DB pulito → silent (correct behavior, no log spam). Marker `verify_or_repair_encryption` non lascia traccia in `encryption_migration_state` — è safety net su ogni boot, non one-shot.

---

## TASK candidati S273 (CTO discrezione)

Non c'è P0 attivo. Possibili tracce:

### Track A: internal_* clienti.rs (REGOLA #11 cross-entity pattern)
- Refactor `commands/clienti.rs` per estrarre `internal_create_cliente / internal_update_cliente / internal_search_clienti` pool-based fns
- Aggiungi `tests/integration_clienti.rs` con regression test PII encryption + dedupe by (nome, telefono) decrypted comparison
- AC: cargo test PASS + no regression existing + pre-commit clean
- Effort: ~4-5h backend autonomous

### Track B: feature roadmap (consult ROADMAP_REMAINING.md + HANDOFF.md)
- Verifica HANDOFF.md per next feature in pipeline non-bug
- Probabile: Sara voice agent edge cases / waitlist UX / fatture PDF rendering / loyalty tier upgrade

### Track C: founder-driven (priorità alta)
- Se founder ha pain point operativo (uso quotidiano), affrontarlo direttamente
- Se founder vuole demo / video / marketing → consult skill `fluxion-video-creator`

---

## Vincoli S273
- **REGOLA #14**: CTO autonomous test+fix backend-side via SSH + cargo test, MAI founder UI interaction salvo decisioni strategiche / GUI Keychain unlock.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **Context budget**: parti sotto 30% raw. Se task tocca file critici (lib.rs / migrations / schema config), soglia BLOCK_CRITICAL 50% raw.

---

## PROMPT START S273

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S272 close + backlog.
Consulta HANDOFF.md + ROADMAP_REMAINING.md per priorità S273.

Se founder ha pain operativo → Track C (autonomous fix via SSH).
Se backlog vuoto → Track A (internal_* clienti.rs refactor + integration test).

REGOLA #14: autonomous backend-side. Founder solo per decisioni strategiche.
```

---

**Provenienza S272 close**: VERDE pieno. 5/5 AC raggiunti + cross-entity 4-table safety net production-ready. Commit atomico `7ebe7c7`.
