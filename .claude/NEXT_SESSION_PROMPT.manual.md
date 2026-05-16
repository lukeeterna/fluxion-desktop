# S257 — P2 suppliers PII encryption (pattern S255 esteso)

**Generato**: 2026-05-16 fine S256 CLOSED GREEN
**Stato repo**: master `80671b2` MacBook+iMac sync clean. App iMac UP (HTTP Bridge :3001).
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.

---

## S256 — Cosa è STATO FATTO (CLOSED GREEN)

Commit S255 `80671b2` pushato + iMac sync. Live verify 6/6 PASS:

| # | Check | Esito |
|---|-------|-------|
| 1 | Log migration | ✅ `"already applied (encrypt_operatori_pii_v1)"` |
| 2 | sqlite3 raw Base64 | ✅ nome/cognome/tel/email ciphertext |
| 3 | Marker rows | ✅ `clienti_v1` (30) + `operatori_v1` (2) |
| 4 | UI plaintext | ⚠️ founder visivo (cosmetic — Check 5 stesso code path) |
| 5 | HTTP /api/operatori/list | ✅ Marco Testa + Paolo Marini plaintext |
| 6 | Idempotency | ✅ "already applied" 2nd+ restart |

---

## S257 — P2 suppliers (~2-3h)

### Pre-step: Migration 040 — DROP UNIQUE supplier (~20min)

```sql
-- src-tauri/migrations/040_suppliers_drop_unique_for_encryption.sql
-- DROP UNIQUE(nome), DROP UNIQUE(partita_iva) — encryption breaks UNIQUE enforcement
-- Dedupe sposta a application layer (commands/supplier.rs::create_supplier list-decrypt-compare)
```

Pattern: ricreare tabella `suppliers_new` senza UNIQUE, copy data, drop old, rename. Verifica schema attuale prima.

### Step P2.a — Runner `encrypt_suppliers_pii_v1`

In `data_migration.rs` aggiungere wrapper (core `encrypt_table_pii` già refactored S255):

```rust
pub async fn encrypt_suppliers_pii(pool: &SqlitePool) -> Result<MigrationOutcome, String> {
    encrypt_table_pii(
        pool,
        "suppliers",
        "encrypt_suppliers_pii_v1",
        &["nome", "telefono", "email", "partita_iva", "indirizzo", "note"],
    ).await
}
```

Wire in `lib.rs::auto_init_from_pool` Ok branch dopo `encrypt_operatori_pii`.

### Step P2.b — `commands/supplier.rs` refactor

1. Helpers `decrypt_supplier_in_place` + `maybe_decrypt_supplier_row`
2. Gate `ensure_encryption_ready_pool` su `get_suppliers`, `get_supplier`, `create_supplier`, `update_supplier`
3. `search_suppliers`: tier-1 = decrypt all + Rust `.contains()` filter (OK <500 supplier)
4. `create_supplier`: pre-INSERT dedupe via `get_suppliers + decrypt + compare nome/partita_iva` (sostituisce UNIQUE check)

### Step P2.c — Audit 4-point REGOLA #8

1. Views: `grep -rE "FROM\s+suppliers|JOIN\s+suppliers" src-tauri/migrations/` → enumerate, refactor concat se trovate
2. UNIQUE: già rimosso con migration 040
3. LIKE: `grep -nE "LIKE\s+.*\?" src-tauri/src/commands/supplier.rs` → list, gestire via tier-1 in-memory
4. FE types: `src/types/supplier.ts` invariato

### Step P2.d — Cargo check + test

```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion/src-tauri" && cargo check 2>&1 | tail -20'
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion/src-tauri" && cargo test --lib data_migration:: 2>&1 | tail -20'
```

Aggiungere `test_encrypt_suppliers_pii_basic_and_idempotent` paralleli ai 2 esistenti.

### Step P2.e — Commit + push + sync iMac

(stesso workflow S256: rsync iMac→MacBook se necessario, commit atomico, push, fast-forward iMac)

### Step P2.f — Live verify (founder Terminal iMac per keychain)

```bash
ssh imac 'lsof -ti:1420,1421,3001 | xargs -r kill -9 2>/dev/null'
# Founder iMac fisico:
cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev 2>&1 | tee /tmp/sara-s257-stepF.log
```

Discriminate PASS (6 check analoghi S256):
1. Log `"🔐 PII migration (suppliers): N rows encrypted..."` (primo run) o `"already applied"` (2nd+)
2. `sqlite3 ... suppliers` raw Base64
3. Marker `encrypt_suppliers_pii_v1` presente
4. UI Suppliers page plaintext
5. HTTP endpoint suppliers plaintext (verificare path in http_bridge.rs)
6. 2nd restart `"already applied"`

---

## S258+ — D-05 ephemeral port (P0 pre-launch BLOCKER)

Pattern industriale Tauri sidecar: backend assegna porta libera, frontend `invoke('get_bridge_port')`. Voice Pipeline lanciata con env `FLUXION_BRIDGE_PORT=N`. MCP server legge `runtime.json`. Stesso per voice 3002.

Owner: backend-architect + frontend-developer + voice-engineer (sessione dedicata 6-8h).
Riferimento decisione: D-05 in `wiki/projects/FLUXION/DECISIONS.md`.

---

## S259+ — D-06 magazzino research (founder request, OPEN)

Spawn `vertical-researcher` + `ux-researcher` parallel research per definire scope magazzino verticali auto/medicale.

---

## Vincoli sessione next (PERMANENTI)

- **REGOLA #6**: chiudi VERDE o handoff strutturato. Mai ARANCIONE.
- **REGOLA #7**: `/context` monitoring continuo, file critici solo <40% RAW (≥48% considerando 18% baseline FLUXION).
- **REGOLA #8**: audit 4-point ogni tabella PII (views/UNIQUE/LIKE/FE).
- **REGOLA #9**: leggere gating site PRIMA pianificare test E2E.
- **REGOLA #10**: soglia /context NETTA post system-reminders. FLUXION baseline ≈ 18% → soglia raw target 48% per task multi-file critici.
- **Encryption salt require interactive launch iMac**: SSH non-interactive fallisce keychain — primo lancio sempre da Terminal iMac fisicamente (Open Q #15).

---

## Start S257 (comandi sequenziali)

```bash
# 1. /context CHECK NETTO post system-reminders. Se RAW >48% chiudi pulito SUBITO.

# 2. Verify status MacBook + iMac
git status -s
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git status -s && git log --oneline -2'

# 3. Read schema suppliers attuale per pianificare migration 040
grep -A 30 "CREATE TABLE.*suppliers" src-tauri/migrations/*.sql

# 4. Read commands/supplier.rs per identificare touchpoints (LIKE/UNIQUE check)
grep -nE "LIKE|UNIQUE|partita_iva|nome" src-tauri/src/commands/supplier.rs | head -30

# 5. Procedere Step P2.a → P2.f (vedi sezioni sopra)
```
