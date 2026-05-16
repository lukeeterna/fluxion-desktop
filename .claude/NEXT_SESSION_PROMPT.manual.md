# S253 — Cat 3 P0 #2 chiusura: Step E live + GDPR encryption scope-extension critique-grade

**Generato**: 2026-05-16 fine S252-bis (CLOSED GREEN — research/critique session, no code shipped)
**Repo**: master `a0e4345` (MacBook + iMac sync OK)
**Pipeline iMac**: DOWN_OK
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.
**Mandato S181**: CTO decide P0/P1/P2 autonomamente (founder NON dev).
**Mandato S252-bis** (questa sessione): scope-creep nascosto del piano originale S252 esposto via critique strutturale — plan rivisto sotto.

---

## S252-bis — Cosa è stato fatto in questa sessione (NESSUN code change)

Sessione di research/critique. Sync iMac (era 1 commit indietro `03a1b9b` → ora `a0e4345`). Letti file pattern S249/S251 + schema operatori + schema suppliers + views derivate.

### Findings strutturali (critica rule #4 prima di scrivere codice)

**FINDING 1 — operatori PII: pattern S249 NON ripetibile meccanicamente**

Migration `024_operatori_features.sql` definisce 2 views che leggono direttamente `operatori.nome` / `operatori.cognome`:

```sql
-- v_kpi_operatori (L21-34)
SELECT o.id, o.nome || ' ' || o.cognome AS nome_completo, ...
FROM operatori o LEFT JOIN appuntamenti a ...

-- v_operatori_assenti_oggi (L59-72)
SELECT o.id, o.nome, o.cognome, o.colore, a.tipo, ...
FROM operatori_assenze a JOIN operatori o ON o.id = a.operatore_id ...
```

Post-cifratura:
- `nome_completo` diventa `"BASE64A BASE64B"` (concat di 2 ciphertext) → frontend dashboard widget W1-B mostra Base64 invece di nomi.
- `v_operatori_assenti_oggi.nome` / `.cognome` → Base64 → Dashboard assenze rotto.

**Consumer impactati:**
- `src-tauri/src/commands/operatori.rs:341,365` (`get_kpi_operatore_storico`, `get_top_operatori_mese` — Rust)
- `src/hooks/use-operatori-kpi.ts` (frontend hook React Query)
- Eventuali consumer di `v_operatori_assenti_oggi` (audit in S253)

**Scope reale P1 operatori**: ~3-4h (non 1.5h come prompt S252 originale)
- Migration 039: ALTER VIEW `v_kpi_operatori` → return `nome`/`cognome` separati invece di concat → Rust compone `nome_completo` post-decrypt.
- Migration 039: ALTER VIEW `v_operatori_assenti_oggi` → frontend si arrangia con decrypt at app layer.
- `KpiOperatore` struct: cambiare campo `nome_completo: String` → `nome: String, cognome: String` (breaking change frontend type).
- `get_kpi_operatore_storico` + `get_top_operatori_mese`: decrypt nome/cognome + comporre `nome_completo` nel Rust prima del return.
- `use-operatori-kpi.ts`: aggiornare TS types se il contratto cambia (oppure mantenere `nome_completo` invariato a frontend e fare la composition in Rust).
- Runner `encrypt_operatori_pii_v1` in `data_migration.rs` (analogo a `encrypt_clienti_pii_v1`, 4 colonne: nome/cognome/email/telefono).
- Wire in `lib.rs` post `encrypt_clienti_pii` Ok branch.
- Wire in `commands/operatori.rs`: `ensure_encryption_ready_pool(pool.inner())` + decrypt helper mirrored da clienti.rs.

**FINDING 2 — suppliers PII: pattern S249 NON ripetibile, 2 scope-creep**

Migration `016_suppliers.sql` definisce constraints + `commands/supplier.rs` ha `search_suppliers` con LIKE su 4 campi:

```sql
-- 016_suppliers.sql L14, L18
partita_iva VARCHAR(20) UNIQUE,
...
UNIQUE(nome)
```

```rust
// supplier.rs L249-269 — search_suppliers
WHERE status = 'active' AND (
    LOWER(nome) LIKE ? OR LOWER(email) LIKE ? OR
    telefono LIKE ? OR partita_iva LIKE ?
)
```

Post-cifratura:
- `UNIQUE(nome)`, `UNIQUE(partita_iva)` → effectively disabled. AES-256-GCM con nonce random → stesso plaintext encrypta a ciphertext diversi ogni volta → DB-level UNIQUE non blocca duplicati. User crea 2 suppliers "Acme" senza errore.
- `search_suppliers` → SQL LIKE su Base64 non matcha mai testo plaintext utente → search ROTTA day-1.

**Scope reale P2 suppliers**: ~2-3h (non 1h come prompt S252 originale)
- Migration 040: DROP UNIQUE(nome), DROP UNIQUE(partita_iva) — sposta enforcement a application layer (`create_supplier` check pre-insert via decrypt-all + Rust comparison; OK per piccoli suppliers count <500).
- `search_suppliers`: refactor a tier-1 in-memory filter (pattern `search_clienti` S249) → decrypt all + Rust filter post-decrypt. OK fino ~500 suppliers piccola PMI.
- Runner `encrypt_suppliers_pii_v1` (6 colonne PII: nome/email/telefono/indirizzo/citta/cap/partita_iva — 7 totali ma cap non strettamente sensibile).
- Wire `commands/supplier.rs`: `ensure_encryption_ready_pool` + encrypt/decrypt helpers + dedupe check pre-INSERT.

**FINDING 3 — fatture PII snapshot (P3 prompt originale): audit non eseguito**

Prompt S252 originale chiamava fatture P3. Non auditato in S252-bis per context budget. Assumere stesso scope-creep pattern (probabile: fatture XML FatturaPA hanno schema rigido → cifrare snapshot columns rompe export SDI).

**Action S253**: audit fatture schema + commands prima di plan P3.

**FINDING 4 — clienti.rs era il caso semplice**

`clienti.rs` non ha views derivate aggregate (verified `grep -r v_clienti src-tauri/migrations` = 0). Non ha UNIQUE constraints sui campi PII (verified migration 001_init `clienti` table — solo `id PRIMARY KEY`). `search_clienti` già tier-1 in-memory (S249 implementation L486-525).

**Lezione strutturale (per MEMORY.md)**:
Pattern "S249 ripetibile meccanicamente per altre tabelle PII" → FALSO. Clienti era il caso a complessità minima. Ogni nuova tabella richiede audit:
1. Derived views che leggono columns cifrati?
2. UNIQUE constraints DB-level sui campi cifrati?
3. SQL LIKE / FTS search sui campi cifrati?
4. Frontend hooks/types che dipendono da nome/cognome/etc come plaintext?

---

## S253 — Plan rivisto (critique-grade, scope real)

**Effort totale**: ~6-9h sequenziali su FILE CRITICI. Distribuire su 2-3 sessioni (S253, S254, S255) per rispettare context-budget-gate <40% per FILE CRITICI.

### S253 — Step E live verification + P1 operatori (con scope reale ~3-4h)

#### Pre-requisito: Step E live verification (richiede founder fisicamente iMac)

```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev'
# Verificare startup log iMac display:
#   🔐 GDPR encryption auto-initialized from license_cache
#   🔐 PII migration: N rows encrypted, M already ciphertext, backup at ...
# Creare 3 clienti via UI con nome+telefono+email+CF.
# Inspect raw DB:
ssh imac "sqlite3 ~/Library/Application\ Support/com.fluxion.app/fluxion.db 'SELECT nome, telefono FROM clienti LIMIT 3'"
# → output Base64 NON plaintext
# Restart app → log "PII migration: already applied"
```

Se Step E PASS → Cat 3 P0 #2 step 1/4 chiuso (clienti).

#### P1 operatori — atomic commit unico (~3-4h)

**Pre-flight**:
- `/context` <40% (FILE CRITICI: migration 039 + data_migration.rs + commands/operatori.rs + frontend hook).
- Se >40% → CHIUDI SESSIONE (rule context-budget-gate).

**Step P1.a**: Migration 039 view refactor (FILE CRITICO)
- Rename `v_kpi_operatori` → drop concat, restituisce `id, nome, cognome, mese, ...` separati.
- `v_operatori_assenti_oggi` → invariato strutturalmente, ma deve essere consumato post-decrypt at app layer.
- File: `src-tauri/migrations/039_views_post_encryption.sql`

**Step P1.b**: `data_migration.rs` extend (FILE CRITICO)
- Add `MIGRATION_KEY_OPERATORI = "encrypt_operatori_pii_v1"`.
- Add `ENCRYPTABLE_COLUMNS_OPERATORI = &["nome", "cognome", "telefono", "email"]`.
- Add `pub async fn encrypt_operatori_pii(pool, db_path)` — mirror function (refactor opzionale: extract helper `fn run_pii_migration(pool, db_path, key, table, columns, select_cols)` per evitare duplicazione 2x → tradeoff: helper aggiunge astrazione critique-prone, può rimandare a P3+).
- Backup filename includere migration key: `db.pre-{KEY}-bak-{TS}` per evitare collision quando 2 runner girano in <1s.
- Test parallelo `test_encrypt_operatori_pii_basic_and_idempotent`.

**Step P1.c**: `lib.rs` wire (FILE CRITICO)
- Trigger `encrypt_operatori_pii` post `encrypt_clienti_pii` Ok branch.
- Stesso pattern Ok/Err/already_applied logging + sentry.

**Step P1.d**: `commands/operatori.rs` wire (FILE CRITICO)
- Add `use crate::encryption::{decrypt_field, encrypt_field, ensure_encryption_ready_pool};`.
- Helpers `encrypt_opt`/`encrypt_required`/`decrypt_opt`/`decrypt_required` (copia da clienti.rs).
- `decrypt_operatore_in_place(o: &mut Operatore)` — required: nome, cognome; option: email, telefono.
- `get_operatori`: decrypt each result post fetch.
- `get_operatore`: decrypt result.
- `create_operatore`: encrypt input prima INSERT.
- `update_operatore`: il `get_operatore` interno ritorna plaintext (decrypted); poi encrypt prima UPDATE.
- `get_kpi_operatore_storico`: post fetch da v_kpi_operatori, decrypt `nome` + `cognome` di ogni KpiOperatore, comporre `nome_completo = "{decrypted_nome} {decrypted_cognome}"`.
- `get_top_operatori_mese`: idem.
- `KpiOperatore` struct: lasciare invariato `nome_completo: String` per non rompere frontend type.
- `delete_operatore`, `get_operatore_servizi`, `update_operatore_servizi`, `get_operatore_assenze`, `create_operatore_assenza`, `delete_operatore_assenza`: aggiungere `ensure_encryption_ready_pool` ma NESSUN decrypt necessario (no PII columns in payload).

**Step P1.e**: cargo test + cargo check iMac
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && cargo test --lib data_migration::"
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && cargo check"
# 0 errori atteso, warnings dead-code pre-esistenti invariati.
```

**Step P1.f**: commit atomico
```
feat(S253): GDPR encryption operatori PII — runner + wire + view refactor
```

**Step P1.g**: aggiornare ROADMAP + HANDOFF + MEMORY + chiudere VERDE.

### S254 — P2 suppliers (~2-3h)

Stesso pattern S253 P1 ma su `suppliers`:
- Migration 040: DROP UNIQUE(nome), DROP UNIQUE(partita_iva).
- Runner `encrypt_suppliers_pii_v1` (6 colonne).
- `commands/supplier.rs`:
  - Wire encrypt/decrypt helpers.
  - `search_suppliers`: refactor tier-1 in-memory filter.
  - `create_supplier`: pre-INSERT dedupe via list-decrypt-compare (OK <500 suppliers).
- Test + commit + close.

### S255 — P3 fatture audit + (eventualmente) implementation

- Pre-audit: identify PII fields in `fatture` schema (probabile `cliente_nome`, `cliente_telefono`, `cliente_indirizzo` snapshot al momento emissione).
- Verifica impatto su FatturaPA XML export (`generate_xml_fattura` / SDI integration).
- Critica strutturale 4 punti SU SCRITTO prima di code.
- Eventuale plan S256 separato se scope >3h.

### S256+ — P4 blind-index HMAC (~2-3h, scale-only)

Solo dopo P1+P2+P3 chiusi. Necessario solo se Sara http_bridge phone-lookup latency >50ms su 1000+ clienti (test perf separato).

---

## Vincoli sessione S253 (PERMANENTI)

- **Mandato founder S244**: NO MVP. Tutti i bug strutturali findings devono essere chiusi prima del public launch.
- **Rule #6**: chiudi VERDE o handoff strutturato. Mai ARANCIONE.
- **Rule context-budget-gate**: FILE CRITICI editabili solo <40% context. Sopra 50% → switch a doc/cleanup. Sopra 70% → solo closing.
- **Rule #4 (critica strutturale)**: PRIMA di scrivere code per ogni nuova tabella PII → audit views derivate + UNIQUE constraints + LIKE search + frontend type dependencies.
- **Mai bundle FILE CRITICI multipli in singolo commit**: ogni P1/P2/P3 → 1 commit atomico (anche se più file dentro stesso scope, devono essere logicamente uniti).

## Riferimenti

- Decision Opt A master password: `.claude/cache/agents/s248/master-password-flow-decision.md`
- Pattern wiring tier-1 reference: `src-tauri/src/commands/clienti.rs` (S249)
- Runner reference: `src-tauri/src/data_migration.rs` (S251)
- View definitions blocker: `src-tauri/migrations/024_operatori_features.sql:21-34, 59-72`
- UNIQUE constraint blocker: `src-tauri/migrations/016_suppliers.sql:14, 18`

## Start S253 (comandi)

```bash
# 1. Verify sync
git log --oneline -1                                  # atteso a0e4345
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git log --oneline -1'

# 2. /context baseline. Se >40% chiudi pulito.

# 3. P0 Step E live verification (richiede founder fisicamente iMac):
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev'
# Verificare log + creare 3 clienti UI + sqlite3 SELECT raw → Base64

# 4. Se P0 PASS → procedi P1 operatori (~3-4h, ordine P1.a→P1.g sopra).
# 5. Se context >40% prima di P1.a → chiudi sessione, plan rimane per S254.
```
