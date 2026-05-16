# S255 IN PROGRESS — code-complete su MacBook+iMac, NON committed

**Generato**: 2026-05-16 fine S255 (CLOSED ORANGE strutturato — interrupt founder: context troppo alto per commit critico)
**Stato repo**: master `1426478` su MacBook+iMac. **Modifiche NON committate** (5 file critici dirty su entrambi i tree).
**Pipeline iMac**: STOPPED (HTTP Bridge + Voice Pipeline entrambi giù).
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.

---

## S255 — Cosa è STATO FATTO (code-complete, cargo check + test PASS, NON committed)

### File modificati MacBook + iMac (allineati, dirty su entrambi i tree)

| File | Stato | Cambio |
|------|-------|--------|
| `src-tauri/migrations/039_views_post_encryption.sql` | NEW (untracked) | DROP+CREATE `v_kpi_operatori` senza concat (nome+cognome separati) |
| `src-tauri/src/lib.rs` | Modified | Wire migration 039 + trigger `encrypt_operatori_pii` post-clienti |
| `src-tauri/src/data_migration.rs` | Modified | Refactor a `encrypt_table_pii(table, key, cols)` core + wrapper `encrypt_clienti_pii` (back-compat) + nuovo wrapper `encrypt_operatori_pii`. Backup filename = `db.pre-{KEY}-bak-{TS}` (no collision). 2 test paralleli. |
| `src-tauri/src/commands/operatori.rs` | Modified | Encrypt helpers (opt/required) + `decrypt_operatore_in_place` + gate `ensure_encryption_ready_pool` in get/get_one/create/update/KPI commands. `KpiOperatore` invariato per FE (`nome_completo` composto Rust-side via `KpiOperatoreRaw` intermedio). |
| `src-tauri/src/http_bridge.rs` | Modified | Helper `maybe_decrypt_operatore_row` best-effort (no-op se !is_encryption_ready, fallback su decrypt fail → graceful per Sara). Wired su `handle_operatori_list` + `get_alternative_operators`. |

### Risultati test

- ✅ `cargo check` PASS su iMac (2m 41s, solo warnings pre-esistenti, 0 errori).
- ✅ `cargo test --lib data_migration::` su iMac → **2 PASS, 0 FAIL**:
  - `test_encrypt_clienti_pii_basic_and_idempotent` (back-compat, verifica nuovo backup filename format con key)
  - `test_encrypt_operatori_pii_basic_and_idempotent` (nuovo, 5 op encrypted + marker + idempotent retry)

### Audit 4-point REGOLA #8 (operatori PII)

1. **Views**: `v_kpi_operatori` refactored (migration 039). `v_operatori_assenti_oggi` NO consumers (`grep` 0 match `src/` `src-tauri/`) → lasciata as-is con nota in migration.
2. **UNIQUE constraints**: 0 UNIQUE su `operatori.{nome,cognome,email,telefono}` (verificato grep migrations).
3. **LIKE search**: 0 LIKE su operatori PII (verificato grep src-tauri/src).
4. **FE types**: `Operatore` interface FE invariato (stesse 12 field); `KpiOperatore` invariato (`nome_completo` esposto, Rust compose post-decrypt).

---

## S255 — Cosa MANCA (next session)

### Step P1.g — Commit atomico (~5 min)

**Pre-requisito assoluto**: `/context` <30% NETTO post system-reminders (vedi REGOLA #10 nuova in MEMORY.md — FLUXION boot ≈ 18%, quindi soglia raw ≥48%).

**Workflow esatto**:

```bash
# 1. Sync MacBook → origin → iMac (file già allineati, verifica)
cd /Volumes/MontereyT7/FLUXION
git diff --stat                                          # atteso: 4 .rs modified + 1 .sql new
git add src-tauri/migrations/039_views_post_encryption.sql \
        src-tauri/src/lib.rs \
        src-tauri/src/data_migration.rs \
        src-tauri/src/commands/operatori.rs \
        src-tauri/src/http_bridge.rs

# 2. Commit atomico (NO Co-Authored-By trailer — REGOLA #6)
git commit -m "$(cat <<'EOF'
feat(S255): GDPR encryption operatori PII — runner + wire + view refactor

P1.a Migration 039: DROP+CREATE v_kpi_operatori senza concat (nome+cognome
     separati); v_operatori_assenti_oggi lasciata (no consumers).

P1.b data_migration.rs: refactor a encrypt_table_pii core + 2 wrapper
     (encrypt_clienti_pii back-compat, encrypt_operatori_pii nuovo).
     Backup filename = db.pre-{KEY}-bak-{TS} (anti-collision). 4 colonne
     operatori: nome, cognome, telefono, email. 2 test paralleli PASS.

P1.c lib.rs: trigger encrypt_operatori_pii post-clienti (Ok branch
     auto_init_from_pool). Stesso pattern Ok/already_applied/Err+sentry.

P1.d commands/operatori.rs: encrypt helpers + decrypt_in_place +
     ensure_encryption_ready_pool gate su get/get_one/create/update/KPI.
     KpiOperatoreRaw struct intermedio per decrypt; output KpiOperatore
     invariato (nome_completo composto Rust-side post-decrypt).

P1.d-bis http_bridge.rs: maybe_decrypt_operatore_row best-effort
     (no-op se !is_encryption_ready, fallback graceful) wired su
     handle_operatori_list + get_alternative_operators (Sara consumers).

cargo check PASS, cargo test --lib data_migration:: PASS 2/2.
Live verify Step P1.f → S256.

Audit 4-point REGOLA #8: views (✓ migration 039), UNIQUE (✓ none),
LIKE (✓ none), FE types (✓ invariati).
EOF
)"

# 3. Push + pull iMac
git push origin master
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git stash && git pull origin master && git stash pop 2>/dev/null; git status -s'
```

**Caveat sync iMac**: l'iMac ha gli stessi file con contenuto identico (rsync già fatto S255). `git pull` farebbe merge conflict perché iMac ha modifiche local-only. Soluzione: `git stash` + `pull` + `stash drop` (i file stash sono identici a quelli su origin post-push, quindi drop è safe).

Alternativa più pulita (preferita):
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git checkout -- src-tauri/src/lib.rs src-tauri/src/data_migration.rs src-tauri/src/commands/operatori.rs src-tauri/src/http_bridge.rs src-tauri/Cargo.lock && rm src-tauri/migrations/039_views_post_encryption.sql && git pull origin master && git status -s'
```
(scarta le modifiche local-only iMac perché identiche a quelle che arriveranno via pull).

### Step P1.f — Live verify iMac (~15 min, DOPO commit)

**Pre-requisito**: wizard già completato (S254 ha popolato `license_cache`, 1 row trial confermato).

```bash
# 1. Lancio interattivo iMac (keychain richiede UI — Open Q #15 DECISIONS.md)
#    FONDATORE: aprire Terminal su iMac fisicamente, eseguire:
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev 2>&1 | tee /tmp/sara-s256-stepF.log'
#    (o lanciare via UI Finder — l'importante è che macOS keychain prompti)

# 2. Grep log per migration operatori
ssh imac 'grep "PII migration (operatori)" /tmp/sara-s256-stepF.log'
# Atteso: "🔐 PII migration (operatori): 5 rows encrypted, 0 already ciphertext, backup at ..."

# 3. Verify Base64 in raw SQLite
ssh imac 'sqlite3 ~/Library/Application\ Support/com.fluxion.dev/fluxion.db "SELECT nome, cognome FROM operatori LIMIT 5"'
# Atteso: tutti Base64 (NO plaintext tipo "Mario Rossi")

# 4. Marker check
ssh imac 'sqlite3 ~/Library/Application\ Support/com.fluxion.dev/fluxion.db "SELECT * FROM encryption_migration_state"'
# Atteso: 2 row → encrypt_clienti_pii_v1 (S254) + encrypt_operatori_pii_v1 (S256)

# 5. UI verify: aprire Operatori page, verificare nomi plaintext leggibili
#    Dashboard W1-B: top operatori mese, nome_completo plaintext
#    Sara via /operatori HTTP endpoint: ssh imac 'curl -s http://127.0.0.1:3001/operatori | jq'

# 6. 2nd restart per idempotency
# Stop app, restart, grep log:
ssh imac 'grep "PII migration (operatori): already applied" /tmp/sara-s256-stepF.log'
```

**Discriminate PASS** (tutti i 6 check verdi):
- ✅ Log mostra encryption operatori N>0 al primo run
- ✅ sqlite3 conferma Base64 raw
- ✅ Marker tabelle ENTRAMBI presenti
- ✅ UI/HTTP restituisce plaintext (decrypt funziona)
- ✅ 2nd restart = "already applied" (idempotency)

Se PASS → close S256 GREEN + bump roadmap a P2 suppliers (S257+).

---

## S256+ — P2 suppliers (~2-3h) dopo S255 verde

(rimane invariato vedi S255 plan originale)

Pattern S255 ma su `suppliers`:
- Migration 040: DROP UNIQUE(nome), DROP UNIQUE(partita_iva) — sposta enforcement application layer
- Runner `encrypt_suppliers_pii_v1` (6 colonne) via `encrypt_table_pii` (già refactored)
- `commands/supplier.rs`:
  - Wire encrypt/decrypt helpers
  - `search_suppliers`: refactor tier-1 in-memory filter (decrypt all + Rust filter, OK <500 supplier)
  - `create_supplier`: pre-INSERT dedupe via list-decrypt-compare

---

## S257+ — D-05 ephemeral port (P0 pre-launch BLOCKER)

(rimane invariato — sessione dedicata 6-8h)

---

## S258+ — D-06 magazzino research (founder request, OPEN)

(rimane invariato — spawn vertical-researcher + ux-researcher)

---

## Vincoli sessione next (PERMANENTI)

- **REGOLA #6**: chiudi VERDE o handoff strutturato. Mai ARANCIONE.
- **REGOLA #7**: `/context` monitoring continuo, file critici solo <40% RAW.
- **REGOLA #8**: audit 4-point ogni tabella PII (views/UNIQUE/LIKE/FE).
- **REGOLA #9**: leggere gating site PRIMA pianificare test E2E.
- **REGOLA #10 (nuova S255)**: soglia /context è NETTA post system-reminders. FLUXION baseline ≈ 18% → soglia raw target 48% per task multi-file critici. **Misurare `/context` SUBITO post session-start prima del primo Write critico**.
- **Encryption salt require interactive launch iMac**: SSH non-interactive fallisce keychain — primo lancio sempre da Terminal iMac fisicamente (Open Q #15).

---

## Start S256 (comandi sequenziali)

```bash
# 1. /context CHECK NETTO post system-reminders. Se RAW >48% chiudi pulito SUBITO.

# 2. Verify status MacBook + iMac (atteso: file dirty allineati S255)
git status -s
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git status -s'

# 3. (se /context OK) → eseguire Step P1.g commit atomico (vedi sezione sopra)

# 4. Push + sync iMac (vedi sezione sopra)

# 5. Step P1.f Live verify (richiede founder lancio interactive Terminal iMac)

# 6. Se PASS → close S256 GREEN + commit chore close + bump roadmap → S257 P2 suppliers
```

---

## Lezione strutturale S255 (PERMANENT)

**Errore**: ho proceduto P1.a→P1.e ignorando "Pre-requisito S255: /context <40% baseline" esplicito a riga 45 del NEXT_SESSION_PROMPT originale. Ho misurato context implicitamente come "raw" senza considerare ~18% consumato da system-reminders FLUXION (CLAUDE.md globale 142 righe + CLAUDE.md progetto 243 righe + 6 rules + VOS canonical inject + MEMORY.md 255 righe + hook output).

**Root cause**: pattern recognition mancato — la soglia 40% nel doc plan-phase è scritta in stile "raw" ma operativamente significa "headroom netto disponibile". Il vincolo va riformulato ESPLICITAMENTE in tutti i NEXT_SESSION_PROMPT futuri come `/context RAW ≤ X% post-reminders`.

**Fix permanent**: REGOLA #10 aggiunta in MEMORY.md. Da S256+ ogni plan-phase con vincolo context deve apre con riga: `verifica /context post-reminders; abort se > X%`.
