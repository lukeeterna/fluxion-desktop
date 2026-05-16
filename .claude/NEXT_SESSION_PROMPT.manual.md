# S255 — P1 operatori scope-real (post S254 GREEN Step E)

**Generato**: 2026-05-16 fine S254 (CLOSED GREEN — Step E PASS, 30 clienti PII encrypted, marker presente, 5 bug catturati DECISIONS.md)
**Repo**: master (commit S254 in arrivo)
**Pipeline iMac**: app UP (launched interactive via Terminal iMac founder, keychain authorized)
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.
**Mandato S181**: CTO decide P0/P1/P2 autonomamente (founder NON dev).

---

## S254 — Outcome (CLOSED GREEN)

### Step E PASS — Encryption clienti PII LIVE su iMac

| Check | Risultato |
|-------|-----------|
| `license_cache` post-wizard | 1 row, tier=trial, fp_set=1, trial_started_at=2026-05-16T19:27:27 |
| Marker `encryption_migration_state` | `encrypt_clienti_pii_v1`, completed_at=`2026-05-16 19:38:55`, **rows=30** |
| Backup auto runner | `fluxion.db.pre-encryption-bak-20260516-193855` (962KB) |
| Email raw SQLite (clienti 5) | `zeg8iwkAWTeCgMYGXI7OIviVrSp7gb/pdZT0eRiUqxnMUxapst` — Base64 ciphertext (NON plaintext `stefano.rizzo@email.it`) |
| Telefono raw SQLite | `t57ZQiKPUOr47UyNiPYfxLrcvchK9m` — Base64 ciphertext (NON plaintext `3391234222`) |

**Conclusione**: GDPR encryption clienti PII LIVE in produzione iMac. Cat 3 P0 #2 step 1/4 (clienti) → CHIUSO GREEN.

### Bug catturati durante session (5 nuove Open Questions in DECISIONS.md)

- **#9** SetupWizard tier "trial" contraddice modello commerciale (P0 pre-launch)
- **#10** PEC opzionale rompe FatturaPA day-1 (P0 pre-launch)
- **#11** License key opzionale = security bypass (P0 pre-launch security-critical)
- **#12** VoIP Sara "opzionale + 30gg gratis" misleading vs realtà cliente-paga (P0 pre-launch)
- **#13** CF Worker proxy unreachable post-wizard (P1 pre-launch cosmetic)
- **#14** Servizi seed-default NON vertical-scoped (cambio gomme su Hair) (P0 pre-launch UX-critical)
- **#15** Encryption salt requires interactive macOS keychain (P1 pre-launch, workaround available)

### Decisioni nuove (DECISIONS.md)

- **D-05 DECIDED** — Ephemeral port HTTP Bridge + Voice Pipeline (no hardcode 3001/3002), pattern Slack/Discord/Cursor
- **D-06 OPEN** — Modulo Magazzino con sottoscorta + popup riordino per verticali product-heavy (founder input, pending research vertical-researcher + ux-researcher)

---

## S255 — P1 operatori scope-real (~3-4h, atomic commit)

**Pre-requisito S255**: `/context` <40% baseline (FILE CRITICI multipli).

### Pattern S249 NON ripetibile meccanicamente (audit S252-bis):
Views `v_kpi_operatori` + `v_operatori_assenti_oggi` (migration 024) leggono `operatori.nome` / `operatori.cognome` direttamente → concat Base64 rompe frontend dashboard. Audit 4-point REGOLA #8.

### Step P1.a — Migration 039 view refactor (FILE CRITICO)
- Rename `v_kpi_operatori` → drop concat, restituisce `id, nome, cognome, mese, ...` separati
- File: `src-tauri/migrations/039_views_post_encryption.sql`

### Step P1.b — `data_migration.rs` extend (FILE CRITICO)
- Add `MIGRATION_KEY_OPERATORI = "encrypt_operatori_pii_v1"`
- Add `ENCRYPTABLE_COLUMNS_OPERATORI = &["nome", "cognome", "telefono", "email"]`
- Add `pub async fn encrypt_operatori_pii(pool, db_path)` mirror function
- Backup filename: `db.pre-{KEY}-bak-{TS}` (evita collision quando 2 runner girano in <1s)
- Test parallelo `test_encrypt_operatori_pii_basic_and_idempotent`

### Step P1.c — `lib.rs` wire (FILE CRITICO)
- Trigger `encrypt_operatori_pii` post `encrypt_clienti_pii` Ok branch
- Stesso pattern Ok/Err/already_applied logging + sentry

### Step P1.d — `commands/operatori.rs` wire (FILE CRITICO)
- Helpers `encrypt_opt`/`encrypt_required`/`decrypt_opt`/`decrypt_required` (copia clienti.rs)
- `decrypt_operatore_in_place(o: &mut Operatore)` — required: nome, cognome; option: email, telefono
- `get_operatori`/`get_operatore`: decrypt post-fetch
- `create_operatore`: encrypt input pre-INSERT
- `update_operatore`: get returns plaintext, encrypt pre-UPDATE
- `get_kpi_operatore_storico` + `get_top_operatori_mese`: decrypt `nome` + `cognome` post-fetch, compose `nome_completo = "{nome} {cognome}"` (mantieni struct field invariato per non rompere frontend type)

### Step P1.e — Test + verify iMac
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && cargo test --lib data_migration::"
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && cargo check"
```

### Step P1.f — Live verify
- Restart app (interactive launch iMac per keychain — see Open Q #15)
- grep log `🔐 PII migration: N rows encrypted` (operatori table)
- sqlite3 verify operatori raw Base64
- Marker check `encryption_migration_state` 2nd row

### Step P1.g — Commit atomico
```
feat(S255): GDPR encryption operatori PII — runner + wire + view refactor
```

---

## S256 — P2 suppliers (~2-3h) DOPO S255 GREEN

Pattern S255 ma su `suppliers`:
- Migration 040: DROP UNIQUE(nome), DROP UNIQUE(partita_iva) — sposta enforcement application layer
- Runner `encrypt_suppliers_pii_v1` (6 colonne)
- `commands/supplier.rs`:
  - Wire encrypt/decrypt helpers
  - `search_suppliers`: refactor tier-1 in-memory filter (decrypt all + Rust filter)
  - `create_supplier`: pre-INSERT dedupe via list-decrypt-compare (OK <500 suppliers)

---

## S257+ — D-05 ephemeral port implementation (P0 pre-launch BLOCKER)

**Decision**: D-05 DECIDED (S254). Implementation owner sessione dedicata.

Refactor cross-component (~6-8h):
- `src-tauri/src/http_bridge.rs:149` → `bind 127.0.0.1:0` + recover port via `local_addr()`
- Persist in `$APP_DATA/runtime.json` + Tauri command `get_bridge_port()`
- Frontend: `invoke('get_bridge_port')` tutti i client fetch
- `voice-agent/main.py` launch via env `FLUXION_BRIDGE_PORT=N`
- MCP server legge `runtime.json` all'avvio
- Test E2E simulating conflict (server dummy 3001 pre-launch)

---

## S258+ — D-06 magazzino research (founder request, OPEN)

Spawn agents:
- `vertical-researcher`: discriminare quali dei 50 micro-verticali necessitano magazzino (hair tutti, beauty estetista sì, medico dentista sì, etc.)
- `ux-researcher`: opzioni A/B/C/D (full/lite/checklist/vertical-specific) + competitor benchmark Fresha/Treatwell/Mindbody/Vagaro
- Output: plan dettagliato con tables `prodotti` + `movimenti_magazzino` + UI `/magazzino` + hook + popup

---

## Vincoli sessione S255+ (PERMANENTI)

- **REGOLA #6**: chiudi VERDE o handoff strutturato. Mai ARANCIONE.
- **REGOLA #8**: audit 4-point per ogni tabella PII (views, UNIQUE, LIKE search, FE types).
- **REGOLA #9**: leggere gating site PRIMA di pianificare test E2E.
- **REGOLA context-budget**: FILE CRITICI editabili solo <40%. Sopra 50% → switch a doc/cleanup. Sopra 70% → solo closing.
- **Mai bundle FILE CRITICI multipli in singolo commit**: ogni P1/P2/P3 → 1 commit atomico.
- **Encryption salt require interactive launch iMac**: SSH non-interactive fallisce keychain — primo lancio sempre da Terminal iMac fisicamente (Open Q #15).

---

## Start S255 (comandi)

```bash
# 1. Verify sync
git log --oneline -1                                  # atteso commit S254 close
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git log --oneline -1'

# 2. /context baseline. Se >40% chiudi pulito.

# 3. P1 operatori — atomic commit unico (~3-4h, P1.a→P1.g)

# 4. Live verify Step P1.f require launch interactive iMac (Open Q #15)
```
