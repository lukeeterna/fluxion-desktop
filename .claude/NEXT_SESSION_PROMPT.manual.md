# Prompt ripartenza S270 — fix BUG-CLI-1+2 + carry-over S269 Step 2-5 (autonomous)

## Stato chiusura S269 (commit pending: memory updates + handoff)

**VERDE-CON-ASTERISCO parziale** — Step 1 PASS (Keychain unlocked + HTTP Bridge :3001 UP + dev binary S268 verified). Step 2 BLOCKED da nuovo BUG-CLI-1. Step 3/4/5 not started.

### Lavoro S269
1. ✅ Founder GUI launch + Keychain unlock → HTTP Bridge :3001 UP
2. ✅ Dev binary `target/debug/tauri-app` (PID 4797, mtime 2026-05-20 12:48:55) include S268 fix verified via strings: `save_fattura_xml_to_file`, `update_impostazioni_fatturazione` camelCase args, `encrypt_impostazioni_fatturazione_pii_v1`
3. ✅ Regola #14 saved: [feedback_cto_autonomous_test_fix.md](../../Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/feedback_cto_autonomous_test_fix.md) — CTO autonomous test+fix, NO founder click/DevTools/screenshot da S270 in poi.

### BUG-CLI-1 (P0) — get_clienti "Unknown error"
- **Sintomo**: tab Clienti UI → `"Errore nel caricamento dei clienti: Unknown error"` (src/pages/Clienti.tsx:131)
- **Root cause confermata via DB inspection**:
  - 38 row clienti tutte deleted_at IS NULL
  - **30 row encrypted** (nome length 44-48, telefono 52 = Base64 ciphertext)
  - **8 row PLAINTEXT** created `2026-05-20 10:52:56` con IDs predictable `cli-anna`/`cli-paolo`/`cli-sara`/`cli-marco`/`cli-elena`/`cli-giuseppe`/`cli-francesca`/`cli-andrea` (nome length 4-9 plaintext, telefono length 10 = cellulare italiano)
  - `decrypt_required(nome)` su valore plaintext non-Base64 → error → `get_clienti` throws → React Query `error` non-Error instance → FE `error instanceof Error ? error.message : 'Unknown error'` cade su fallback
- **Origine seed**: `scripts/seed-test-data.sql` + `seed-video-demo.sql` + `seed-sprint1-demo.sql` + `seed-pacchetti-fedelta.sql` contengono riferimenti `cli-anna` etc. INSERT bypassa encryption path Rust (raw SQL injection diretto in sqlite3) → post-migration `encrypt_clienti_pii_v1` (S256) i row plaintext sono inseriti DOPO la migration → migration runner already_applied non re-processa.
- **Anche affetto**: 3 fatture seed `fat-001`/`fat-002`/`fat-003` created stesso timestamp, totali 65€/45€/35€, riferiscono cli-* — da deletare insieme.

### BUG-CLI-2 (P1 bonus) — FE error display
- `src/pages/Clienti.tsx:131`: `error instanceof Error ? error.message : 'Unknown error'`
- `src/hooks/use-appuntamenti-ddd.ts:29`: stesso pattern
- Tauri `invoke()` rigetta con string plain (non Error instance) → fallback `'Unknown error'` nasconde messaggio Rust originale.
- Fix: `error instanceof Error ? error.message : String(error)` (entrambi i siti) — preserva error Rust originale per debug.

---

## TASK S270

### Step 1: Fix BUG-CLI-1 (data cleanup)
```bash
ssh imac '
DB="/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db"

# Backup pre-cleanup
cp "$DB" "$DB.pre-S270-bug-cli1-bak-$(date +%Y%m%d-%H%M%S)"

# Identify seed contaminated rows
sqlite3 "$DB" "SELECT id, length(nome), length(telefono) FROM clienti WHERE id LIKE 'cli-%' AND deleted_at IS NULL;"

# DELETE 8 seed plaintext clienti
sqlite3 "$DB" "DELETE FROM clienti WHERE id IN ('"'"'cli-anna'"'"', '"'"'cli-paolo'"'"', '"'"'cli-sara'"'"', '"'"'cli-marco'"'"', '"'"'cli-elena'"'"', '"'"'cli-giuseppe'"'"', '"'"'cli-francesca'"'"', '"'"'cli-andrea'"'"');"

# DELETE 3 seed fatture dipendenti
sqlite3 "$DB" "DELETE FROM fatture_righe WHERE fattura_id IN ('"'"'fat-001'"'"', '"'"'fat-002'"'"', '"'"'fat-003'"'"');"
sqlite3 "$DB" "DELETE FROM fatture WHERE id IN ('"'"'fat-001'"'"', '"'"'fat-002'"'"', '"'"'fat-003'"'"');"

# Verify
sqlite3 "$DB" "SELECT COUNT(*) AS clienti FROM clienti WHERE deleted_at IS NULL; SELECT COUNT(*) AS fatture FROM fatture WHERE deleted_at IS NULL;"
# Expected: clienti=30, fatture=0
'
```

### Step 2: Annotate seed scripts (prevention)
Aggiungere TODO comment in cima a `scripts/seed-*.sql` che riferiscono `cli-*` o `fat-*` IDs:
```sql
-- ⚠️ DEPRECATED 2026-05-20 (S270): questo seed bypassa encryption path Rust.
-- Inserire clienti via `create_cliente` Tauri command, non via raw SQL INSERT.
-- Riferimento: BUG-CLI-1 (S269) + encrypt_clienti_pii_v1 migration (S256).
```

File da annotare:
- `scripts/seed-test-data.sql`
- `scripts/seed-video-demo.sql`
- `scripts/seed-sprint1-demo.sql`
- `scripts/seed-pacchetti-fedelta.sql`
- `scripts/seed_demo_data.sql` (verifica se ha INSERT clienti plaintext)

### Step 3: Fix BUG-CLI-2 (FE error display)
```typescript
// src/pages/Clienti.tsx:131
// PRIMA: {error instanceof Error ? error.message : 'Unknown error'}
// DOPO:  {error instanceof Error ? error.message : String(error)}

// src/hooks/use-appuntamenti-ddd.ts:29
// PRIMA: return 'Unknown error';
// DOPO:  return String(error);
```
Type-check + audit cross-entity altri siti `'Unknown error'` literal:
```bash
grep -rn "'Unknown error'" src/ --include="*.ts" --include="*.tsx"
```

### Step 4: Restart app iMac (founder GUI launch fisicamente, REGOLA #12 Keychain gate ANCORA APPLICABILE per first boot)
```bash
ssh imac 'pkill -f "target/debug/tauri-app"; sleep 2'
# Founder relauncha via dock o npm run tauri dev
```

### Step 5: Verify BUG-CLI-1 fix via HTTP Bridge (autonomous, REGOLA #14)
```bash
ssh imac '
# Tab Clienti via HTTP Bridge — find endpoint or use Tauri integration test
curl -s http://127.0.0.1:3001/api/clienti/list 2>&1 | head -c 500
# Se endpoint non esiste, usare cargo integration test
cd "/Volumes/MacSSD - Dati/FLUXION/src-tauri" && cargo test --test get_clienti_decrypt -- --nocapture 2>&1 | tail -30
'
```

### Step 6: Carry-over S269 Step 2-5 autonomous (REGOLA #14)
**Step 2 BUG-FATT-3** (cache stale):
```bash
# Create cliente test via Tauri invoke (need integration test or HTTP Bridge)
# Create fattura via POST + verify lista via GET
# Compare totale DB vs response immediato senza F5
ssh imac '
# Find HTTP Bridge endpoint for fatture
curl -s http://127.0.0.1:3001/api/fatture/list 2>&1 | head -c 200
'
```
Se HTTP Bridge non espone endpoint fatture → opzioni:
- (a) Aggiungere endpoint `http_bridge.rs` per fatture (overkill, scope creep)
- (b) Scrivere cargo integration test che simula `useAddRigaFattura.onSuccess` invalidation pattern verify-side
- (c) Tauri WebDriver setup (deferred, complesso)
- **Raccomandazione**: (b) — cargo integration test che setup DB temporanea + chiama `create_fattura` + `add_riga_fattura` + verifica `list_fatture` ritorna `totale_documento=15` immediatamente. Conferma backend OK, FE cache propagation pattern già verificato unit-level via type-check + ESLint.

**Step 3 BUG-FATT-4** (save Impostazioni):
```bash
# Tauri invoke update_impostazioni_fatturazione via HTTP Bridge (se esposto)
# OR cargo integration test che chiama update_impostazioni_fatturazione direttamente
# Verify DB telefono ciphertext Base64 length ≥16
```

**Step 4-5 BUG-FATT-5/6** (toast visibility + Download XML):
- BUG-FATT-5 (toast z-index 9999): unit verify che `App.tsx` mount `<Toaster zIndex=9999 />` (già fatto S268, no regression test live possibile senza UI rendering)
- BUG-FATT-6 (Download XML): cargo integration test su `save_fattura_xml_to_file` command — setup DB con 1 fattura+xml_content, chiama command con tempfile path, verify file scritto + content match.

### Acceptance Criteria S270
- [ ] **BUG-CLI-1**: DB clienti=30 encrypted only + tab Clienti UI carica lista correttamente (NO "Unknown error")
- [ ] **BUG-CLI-2**: 2 file FE fixed + grep `'Unknown error'` literal = 0 match in src/
- [ ] **Seed scripts annotated**: TODO comment in 4-5 file scripts/seed-*.sql
- [ ] **BUG-FATT-3** regression: cargo integration test PASS su create_fattura + add_riga_fattura + list_fatture totale corretto
- [ ] **BUG-FATT-4** regression: cargo integration test PASS su update_impostazioni_fatturazione + DB telefono ciphertext
- [ ] **BUG-FATT-6** regression: cargo integration test PASS su save_fattura_xml_to_file + file scritto + content XML valid
- [ ] **BUG-FATT-5**: skip live regression (no UI rendering verify infra) — defer S275+ Playwright

CLOSE VERDE se tutti checkbox PASS. Commit `fix(S270): BUG-CLI-1+2 + S269 carry-over regression tests`.

---

## Vincoli S270
- **REGOLA #14** (PRIORITY): autonomous test+fix. NO chiedere founder click/DevTools/screenshot. Solo decisioni strategiche + autorizzazione azioni distruttive (DROP, force-push).
- **REGOLA #12**: founder GUI launch dopo restart binary (Step 4) per Keychain unlock — UNICA action founder S270.
- **REGOLA #6**: NO Co-Authored-By Claude trailer su commit.
- **REGOLA #11**: audit cross-entity per BUG-CLI-2 (grep `'Unknown error'` literal cross-codebase).
- **Context budget**: parti fresca, S270 task density alta — monitor /context a 50% raw, chiudi a 60%.

---

## File modificati S268 (riferimento per regression)
- `src/hooks/use-fatture.ts` — BUG-FATT-3 + BUG-FATT-4
- `src/App.tsx` — BUG-FATT-5 Toaster globale zIndex 9999
- `src/pages/Fatture.tsx` + `src/components/fatture/FatturaDetail.tsx` — BUG-FATT-6 download handler
- `src-tauri/src/commands/fatture.rs` — `save_fattura_xml_to_file` command + `update_impostazioni_fatturazione` encrypt path
- `src-tauri/src/lib.rs` — register handler
- `src-tauri/capabilities/default.json` — `dialog:allow-save`

---

## PROMPT START S270 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S270.

REGOLA #14 attiva: autonomous. NO chiedere founder click/DevTools/screenshot.

Step 1: backup DB iMac + DELETE 8 row cli-* + 3 row fat-* seed plaintext.
Step 2: annotate scripts/seed-*.sql con TODO DEPRECATED.
Step 3: fix Clienti.tsx:131 + use-appuntamenti-ddd.ts:29 pattern String(error).
Step 4: restart app iMac + founder GUI Keychain unlock (UNICA founder action).
Step 5: verify BUG-CLI-1 fix via cargo integration test get_clienti_decrypt.
Step 6: carry-over S269 — cargo integration test BUG-FATT-3/4/6 regression.

CLOSE VERDE se tutti AC PASS.
```

---

**Provenienza S269 close**: VERDE-CON-ASTERISCO parziale. Step 1 PASS (Keychain+Bridge UP, binary S268 verified). Step 2-5 BLOCKED da BUG-CLI-1 (8 seed row plaintext cli-* post-migration). REGOLA #14 introdotta (CTO autonomous test+fix, no founder UI requests). Diagnosi completa root cause + fix plan + carry-over scope S270.
