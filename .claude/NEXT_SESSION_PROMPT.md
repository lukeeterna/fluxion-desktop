# Prompt ripartenza S258 — v3 FINAL approved (founder + VOS + Claude)

**Generato**: 2026-05-18 (sessione S257-advisory close)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit input verificato**: `d652060` (S257 GDPR encryption suppliers PII)
**Context expected boot S258**: ~21-23% (sotto soglia WARN 40%, headroom ~27-29%)

---

## TASK S258: live verify S257 P2 (suppliers PII encryption) + decide next encryption target

**STATO INPUT (verificato master + iMac)**:
- Commit `d652060` in master + iMac sync.
- 4 file: migration 040 (DROP UNIQUE nome+partita_iva) + `data_migration.rs` (runner `encrypt_suppliers_pii`) + `lib.rs` (wire + sentry warn) + `commands/supplier.rs` (encrypt/decrypt + dedupe app-layer).
- `cargo check` 0 errori. `cargo test --lib data_migration::` 3/3 PASS.
- Pending: P2.f live verify (founder fisico iMac, keychain prompt al boot app).

**Verifica fattuale supplier.rs (pre-validata sessione advisory)**:
- `commands/supplier.rs:165` → `nome_norm = supplier.nome.trim().to_lowercase()`
- `:169` → `piva_norm = ... .trim().to_lowercase()`
- `:172` → dedupe compare con stessa normalizzazione
- Implicazione test 2.4: se "  acme srl  " passa silently → **BUG encryption-related** (decrypt fail during dedupe list), trattare come HANDOFF rosso, NON feature gap.

═══════════════════════════════════════════════════════════════════
## STEP 0 — PRE-FLIGHT (obbligatorio, 5 min)
═══════════════════════════════════════════════════════════════════

**0.1** SSH iMac → verifica branch:
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git log --oneline -1'
# → expect d652060
```

**0.2** Conta righe suppliers dev DB:
```bash
ssh imac '<sqlite3 path-to-dev-db> "SELECT COUNT(*) FROM suppliers;"'
```

**0.3** Verifica indici post-migration-040:
```bash
ssh imac '<sqlite3 path> "SELECT name FROM sqlite_master WHERE type=\"index\" AND tbl_name=\"suppliers\";"'
# → expect: NO indici "*_unique_nome" o "*_unique_partita_iva" residui
# → se presenti: migration 040 non ancora eseguita (DB pre-encryption), OK
```

**0.4** Decisione branch:
- Se COUNT = 0: SEED 3 row plaintext PRIMA del boot.
  ```sql
  INSERT INTO suppliers (id, nome, email, telefono, indirizzo, partita_iva, citta, cap, status, created_at, updated_at) VALUES
  ('seed-1', 'Acme Srl', 'info@acme.it', '3331234567', 'Via Roma 1', 'IT12345678901', 'Milano', '20100', 'active', datetime('now'), datetime('now')),
  ('seed-2', 'Beta SpA', 'b@beta.it', '3337654321', 'Via Po 5', 'IT98765432109', 'Roma', '00100', 'active', datetime('now'), datetime('now')),
  ('seed-3', 'Gamma Snc', NULL, NULL, NULL, NULL, 'Torino', '10100', 'active', datetime('now'), datetime('now'));
  ```
- Se COUNT > 0: skip seed, procedi con dati esistenti.

═══════════════════════════════════════════════════════════════════
## STEP 1 — LIVE VERIFY BOOT (founder fisico iMac)
═══════════════════════════════════════════════════════════════════

**1.1** Boot app FLUXION dev su iMac fisico (`cargo tauri dev` OPPURE binary release).
- **NOTA**: Voice Pipeline (:3002) NOT REQUIRED per S258 — schermata Fornitori è gestionale puro, no Sara coinvolta. Solo HTTP Bridge (:3001) deve salire. Se :3002 DOWN nel SessionStart hook → IGNORE, non debuggare.

**1.2** Keychain prompt → conferma password.

**1.3** Cattura stdout/stderr in `/tmp/s258-boot1.log`:
```bash
cargo tauri dev 2>&1 | tee /tmp/s258-boot1.log
```

**1.4** Cerca pattern in log:
```bash
grep -E "PII migration \(suppliers\)" /tmp/s258-boot1.log
```
Expected uno di:
- A) `"🔐 PII migration (suppliers): N rows encrypted, M already ciphertext, backup at <path>"`
- B) `"🔐 PII migration (suppliers): already applied (encrypt_suppliers_pii_v1)"`
- C) `"⚠️  PII migration (suppliers) failed (non-fatal...): <err>"`

**1.5** Verifica artefatti DB post-boot1:
- a. Marker:
  ```sql
  SELECT migration_key, applied_at, rows_processed
  FROM encryption_migration_state
  WHERE migration_key='encrypt_suppliers_pii_v1';
  -- → expect 1 row.
  ```
- b. Cifratura on-disk (se N>0 al run):
  ```sql
  SELECT id, substr(nome,1,40), substr(partita_iva,1,40) FROM suppliers LIMIT 3;
  -- → expect Base64 ciphertext (es. "AAAA...="), NO plaintext "Acme"/"IT".
  ```
- c. Backup file:
  ```bash
  ls -lh <db-dir>/*encrypt_suppliers_pii_v1*
  # → expect file .db con timestamp recente, size ≈ DB pre-run.
  ```

**1.6** Boot SECONDO giro (idempotency a 2 livelli):

PRIMA di boot2 — snapshot ciphertext + marker:
```sql
SELECT id, nome AS ct_before, rows_processed FROM suppliers s
  JOIN encryption_migration_state e ON e.migration_key='encrypt_suppliers_pii_v1'
  WHERE s.id='seed-1';
-- save ct_before, rows_processed_before.
```

Boot2:
```bash
cargo tauri dev 2>&1 | tee /tmp/s258-boot2.log
grep "PII migration (suppliers)" /tmp/s258-boot2.log
# → expect "already applied" (log-level).
```

POST boot2 — verifica DB-level identità:
```sql
SELECT id, nome AS ct_after, rows_processed FROM suppliers s
  JOIN encryption_migration_state e ON e.migration_key='encrypt_suppliers_pii_v1'
  WHERE s.id='seed-1';
-- → expect ct_after == ct_before (byte-for-byte)
-- → expect rows_processed_after == rows_processed_before (no double-encrypt).
```

Senza questa verifica DB-level, un bug "re-encrypt-on-boot" passerebbe inosservato perché il marker è già lì.

═══════════════════════════════════════════════════════════════════
## STEP 2 — TEST UI FUNZIONALE (founder fisico, schermata Fornitori)
═══════════════════════════════════════════════════════════════════

- **2.1** List view → verifica 3 nomi visibili plaintext (Acme/Beta/Gamma), NO Base64.
- **2.2** Create supplier dup nome esatto "Acme Srl" → expect error `"Esiste già un fornitore con nome 'Acme Srl'"`.
- **2.3** Create supplier dup partita_iva "IT12345678901" → expect error `"Esiste già un fornitore con partita IVA 'IT12345678901'"`.
- **2.4** Normalizzazione dedupe (edge case):
  - Create supplier "  acme srl  " (case+trim) → codice `supplier.rs` fa `.trim().to_lowercase()` (verificato sessione advisory) → expect stesso error 2.2.
  - **SE passa silently** (nessun error, supplier creato) → **BUG encryption** (decrypt fail durante list-decrypt-compare dedupe) → trattare come HANDOFF rosso, NON feature gap.
- **2.5** Update supplier seed-2 → rename a "Acme Srl" (collision con seed-1):
  - NOTA: il codice attuale NON checka collision in `update_supplier` (gap noto pre-S258).
  - Se passa silently → flag S259 P3.b (feature gap, non bug encryption, non bloccante per VERDE).
- **2.6** Search → query "acme" → expect match seed-1 (case-insensitive plaintext OK).
- **2.7** Search → query "12345" → expect match seed-1 (substring partita_iva OK).
- **2.8** Search → query stringa vuota → expect prime 20 active sorted.

═══════════════════════════════════════════════════════════════════
## STEP 3 — OUTCOME DECISION (verde/handoff, NO arancione)
═══════════════════════════════════════════════════════════════════

**VERDE** (chiusura sessione):
- Tutti 1.4-1.6 (inclusa identità ciphertext+rows_processed boot1↔boot2) + 2.1-2.3 + 2.6-2.8 OK
- Marker presente, ciphertext on-disk, backup file generato, idempotency DB-level confermata
- UI dedupe nome+piva PASS
- 2.4 PASS (normalizzazione funziona) e 2.5 gap update collision = feature gap S259 non bloccante
- Procedi a STEP 4 (audit next target).

**VERDE-CON-ASTERISCO** (chiusura sessione + nota S259):
- Tutto encryption PASS, MA sentry warn benigno documentato (es. "already applied su DB vuoto post-seed").
- Documentare warning testuale in HANDOFF, NO fix in-session.
- Gap 2.5 osservato → annota S259 P3.b.

**HANDOFF STRUTTURATO** (rosso, no fix in-session):
- Qualsiasi: sentry warn non benigno, decrypt fail su row esistente, crash boot, UI list mostra Base64, marker assente, backup mancante, **ct_after != ct_before in 1.6** (double-encrypt latente), rows_processed cambia, **2.4 passa silently** (dedupe normalizzato fail = decrypt bug).
- **ROLLBACK procedure** (ordine obbligatorio):
  - a. STOP app (Ctrl+C su `cargo tauri dev`).
  - b. `cp <db-dir>/<dbname>.db <db-dir>/<dbname>.db.s258-pre-revert`  # safety
  - c. `cp <db-dir>/*encrypt_suppliers_pii_v1_*.db <db-dir>/<dbname>.db`  # restore
    - (ripristina sia plaintext rows SIA schema pre-migration-040 con UNIQUE)
  - d. `git revert d652060` (NO --amend)
  - e. `cargo check` su iMac → expect PASS
  - f. NO push fino a root cause identificata.
- Scrivi `HANDOFF.md` S258→S259 con: stato rosso, log boot1+boot2, query DB pre/post, ipotesi root cause, prompt resume specifico.

═══════════════════════════════════════════════════════════════════
## STEP 4 — AUDIT NEXT ENCRYPTION TARGET (solo se VERDE/VERDE*)
═══════════════════════════════════════════════════════════════════

**4.1** Grep PII columns su tutte le migrations (NO mono-fonte TODO comment):
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && rg -n \
  "(cliente|customer|email|telefono|nome|cognome|indirizzo|partita_iva|fiscale|note|transcript|body|message)" \
  src-tauri/migrations/*.sql | rg -v "(encrypt|backup|index|FOREIGN KEY)" | sort -u | head -50'
```

**4.2** Lista tabelle attive nel DB dev:
```bash
ssh imac '<sqlite3> "SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name;"'
```

**4.3** Per ogni candidato (es. fatture, whatsapp_messages, appointments, audit_log, voice_sessions), conta righe + identifica colonne PII denormalizzate:
```sql
SELECT COUNT(*) FROM <table>;
PRAGMA table_info(<table>);
```

**4.4** Matrice priorità P3 (4 colonne):
| Tabella | PII volume (righe × cols) | Esposizione (UI/export/API?) | Effort refactor |

Effort hint:
- **trivial**: colonne denormalizzate snapshot tipo `fatture.cliente_*` (no UNIQUE, no LIKE search, pattern identico S257 ma più semplice — no dedupe app-layer)
- **medium**: richiede tier-1 in-memory search (LIKE residuo) tipo `whatsapp_messages.body`
- **hard**: freetext con full-text search o JOIN cross-table su PII

Output: scelta motivata con dati (volume + esposizione + effort), non TODO comment.

**4.5** Pattern S257 ripetibile su next target (NON implementare ora, scope-out S258):
- schema check (UNIQUE su col PII?)
- migration N+1 DROP eventuali UNIQUE
- runner wrapper + const + test idempotency in `data_migration.rs`
- wire `lib.rs` dopo suppliers con sentry warn
- re-encrypt in `commands/<entity>.rs` (encrypt/decrypt helpers + dedupe app-layer se UNIQUE droppato, tier-1 search se LIKE usato)

═══════════════════════════════════════════════════════════════════
## CHIUSURA
═══════════════════════════════════════════════════════════════════

**VERDE/VERDE***:
- Update `HANDOFF.md`: S257 DONE + S258 live verify PASS + S259 scope P3 con tabella scelta + nota gap 2.5 (se osservato).
- Commit: `"docs(S258): live verify S257 P2 suppliers PII PASS + scope P3 <table-name>"`
- Verifica CI Pass status PRIMA di push:
  ```bash
  gh run list --branch master --limit 3 --json conclusion,name,headSha
  # → se ultimo run su d652060 = "success" → push OK
  # → se "failure" o "in_progress" → attendi/investiga prima di pushare S258 doc.
  ```

**HANDOFF**:
- Vincolo #6: `HANDOFF.md` strutturato + `NEXT_SESSION_PROMPT.manual.md`.
- NO commit della sessione rotta.
- iMac state lasciato in rollback-ready (backup .db preservato, codice revertato locale ma NO push).

═══════════════════════════════════════════════════════════════════
## VINCOLI HARD
═══════════════════════════════════════════════════════════════════

- Founder action fisica obbligatoria (keychain) — non delegabile a SSH.
- Vincolo #6 zero tolleranza ARANCIONE: solo VERDE / VERDE* / HANDOFF rosso. Niente "fix triviale in session" sopra il 50% context (vincolo #7).
- Vincolo #2: audit grep migrations PRIMA di decisione P3 next target, no TODO mono-fonte.
- Backup .db preservare SEMPRE prima di qualsiasi revert (migration 040 schema change irreversibile via git revert codice).
- Pre-action check DECISIONS FLUXION: verifica nessuna D-01..D-05 founder-level contraddetta da pattern encryption corrente (D-05 sidecar port irrilevante S258, ma scan completo per safety).
- Trade-off S257 (tier-1 dedupe/search <500 supplier, tier-2 blind-index tracked) restano accettati, NON rinegoziare in S258.

---

**Provenienza prompt**: v1 founder → v2 Claude critica strutturale (3 patch) → v3 VOS rifinitura (2 mini-correzioni A+B + 3 nit) → v3 FINAL approved sessione advisory 2026-05-18.
