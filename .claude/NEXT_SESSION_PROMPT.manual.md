# Prompt ripartenza S276 — backlog opzionale (CTO discrezione, REGOLA #15)

## Stato chiusura S275 (VERDE pieno)

**S275 outcome**: refactor `internal_*` supplier.rs + integration test PII encryption — REGOLA #11 cross-entity completion 4/4 (clienti S273 + operatori S274 + supplier S275 + impostazioni_fatturazione S271 via fatture.rs). REGOLA #14 + REGOLA #15 PASS — 100% autonomous backend SSH+cargo, founder zero touch.

### Done S275 (commit `9bd5107` master, MacBook+iMac sync fast-forward)
1. ✅ **`src-tauri/src/commands/supplier.rs`** (5 fns `internal_*` pool-based estratte):
   - `internal_get_supplier(pool, id)` — helper interno
   - `internal_list_suppliers(pool, include_inactive: bool)` — base per Tauri wrapper + dedupe in create
   - `internal_create_supplier(pool, request)` — pre-INSERT dedupe (nome + p.iva) + encrypt 5 PII (nome required + email/telefono/indirizzo/partita_iva opt)
   - `internal_update_supplier(pool, id, update)` — partial merge `Option<T>.unwrap_or(current)` + re-encrypt 5 PII
   - `internal_search_suppliers(pool, query)` — tier-1 in-memory filter post-decrypt
   - Tauri command wrappers (create/get/list/update/search) delegano in 1 riga
   - Pattern simile a fatture S271 (no audit logging come clienti S273; pre-INSERT dedupe preserved via `internal_list_suppliers` interna).
2. ✅ **`src-tauri/tests/integration_supplier.rs`** (nuovo) — 5 test PASS in 6.75s:
   - `test_create_supplier_encrypts_pii_at_rest` (5 PII: nome/email/telefono/indirizzo/partita_iva len ≥16, ≠ plaintext)
   - `test_update_supplier_re_encrypts_changed_fields` (ciphertext post ≠ snapshot pre, AES-GCM random nonce)
   - `test_get_supplier_decrypts_with_optional_fields_none` (4 opt None pass-through, nome required cifrato)
   - `test_update_supplier_partial_input_preserves_unchanged_fields` (partial merge regression critica per 5 PII)
   - `test_search_suppliers_matches_decrypted_plaintext` (bonus: list ordering plaintext + search empty/match/no-match + email match cross-field)
3. ✅ **No regression** (30/30 test totali PASS via SSH iMac autonomous):
   - integration_supplier 5/5 (nuovo) in 6.75s
   - integration_clienti 4/4 in 6.08s
   - integration_operatori 4/4 in 5.47s
   - integration_fatture 4/4 in 5.70s
   - integration_appuntamenti 9/9 in 12.06s
   - integration_encryption_repair 4/4 in 0.23s
4. ✅ Cargo check 0 errori (9 warnings preesistenti S274 baseline, NON introdotti S275).
5. ✅ Commit pulito S275: solo 2 file rilevanti (supplier.rs + tests/integration_supplier.rs). Reset spurio `.claude/NEXT_SESSION_PROMPT.md` auto-gen boot template pre-commit (cleanup carry-over S273/S274 pattern).
6. ✅ REGOLA #11 cross-entity matrice **CHIUSA 4/4**: clienti / operatori / supplier / impostazioni_fatturazione tutti coperti da integration test PII encryption regression.

### Out of scope mantenuto (S275)
- `supplier_orders` / `supplier_interactions` (no PII proprio — solo FK + status + JSON items)
- `get_supplier_stats` (SELECT COUNT aggregati, no PII path)
- `delete_supplier` (soft delete via `status='inactive'`, no PII touched)
- `appuntamenti.rs` (no PII proprio — FK only verso cliente; decrypt in commands/appuntamenti.rs:462 è solo per join visualizzazione cliente)

### Note operative S275
- 5 PII fields su supplier (nome required + email/telefono/indirizzo/partita_iva opt) vs 4 su operatori (nome/cognome required + email/telefono opt) vs 4 su clienti (nome/cognome required + telefono/email opt).
- `internal_list_suppliers` aggiunto come helper anche per il dedupe pre-INSERT (`internal_create_supplier`) — Migration 040 ha droppato UNIQUE(nome)/UNIQUE(partita_iva) SQL constraints perché AES-GCM random nonce diverge ciphertext per stesso plaintext, dedupe è tier-1 in Rust con full set decrypt.
- Search tier-1: SQL LIKE su ciphertext = zero match, quindi decrypt full set + filter in-memory (cap 20). Tier-2 blind-index HMAC tracked per scale >500 supplier.
- Test salt deterministico `[0xDE; 32]` (S275, diverso da S274 `[0xCD; 32]` e S273 `[0xCC; 32]` per chiarezza session origin).

---

## TASK candidati S276 (CTO discrezione, REGOLA #15 — no A/B, decide e parti)

### Track A: feature roadmap pipeline (highest probable ROI)
- Verifica `ROADMAP_REMAINING.md` per next feature non-bug pipeline
- Probabili candidati: Sara voice edge cases, waitlist UX completamento, fatture PDF rendering (BUG-FATT-6 fix definitivo), loyalty tier upgrade
- Effort variabile a seconda feature

### Track B: BUG-FATT-3 cache stale Fatture lista (P0 defer da S267)
- Founder report S267: lista fatture mostra 0 in colonna `totale_documento` finché non si fa F5 — apertura dettaglio mostra valore corretto
- Root cause candidato: race `useCreateFattura.onSuccess invalidate` vs `add_riga_fattura` ricalcolo `totale_documento`
- Fix candidate: refetchQueries+chain pattern o `await` su `add_riga_fattura` prima di invalidate
- REGOLA #11 audit cross-entity (use-clienti/fornitori/cassa/appuntamenti per pattern similare invalidate+chained mutate)
- Effort: ~2-3h front+back

### Track C: BUG-FATT-5 toast z-index Dialog modal (P1 defer S267)
- Founder report S267: `toast.error('Errore salvataggio impostazioni')` codice presente (`ImpostazioniFatturazioneDialog.tsx:122`) ma toast non visibile quando Dialog modal aperto
- Fix candidate globale: `<Toaster position="top-center" toastOptions={{style:{zIndex:9999}}} />` in main.tsx/App.tsx
- Effort: ~30min (test su tutti i dialog modali esistenti)

### Track D: pulizia cargo fmt residual iMac (igiene repo)
- 14 file con cargo fmt diff residual su iMac NON committati S273/S274 (`fatture.rs`/`dashboard.rs`/`cassa.rs`/etc)
- Run `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && cargo fmt --check"` per diff list completa
- Se diff identico su MacBook → commit unico `chore: cargo fmt` da MacBook → sync iMac
- Effort: ~30min, riduce rumore prossime sessioni

### Track E: founder-driven (priorità alta se emerge pain operativo)
- Pain point uso quotidiano FLUXION (founder GUI report)
- Demo/video/marketing → skill `fluxion-video-creator`

---

## Vincoli S276
- **REGOLA #14**: CTO autonomous test+fix backend via SSH+cargo. Founder solo decisioni strategiche / GUI Keychain unlock.
- **REGOLA #15**: NO domande A/B su scope. Decide best ROI/risk e parti.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **REGOLA #11**: matrice 4/4 CHIUSA. Pattern internal_* solo se nuova entity con PII (raro — non aggiungere refactor su entity esistenti senza PII proprio).
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/schema config) → BLOCK_CRITICAL ≥50% raw.

---

## PROMPT START S276

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S275 close + backlog.

REGOLA #15 attiva: decidi track autonomamente. REGOLA #11 matrice 4/4 ora CHIUSA — pattern internal_* non più carry-over come default.

Track suggested: Track A (feature roadmap) o Track B (BUG-FATT-3 cache stale, P0 defer da S267).

REGOLA #14: backend-side autonomous. Founder solo override su pain operativo.
```

---

**Provenienza S275 close**: VERDE pieno. 5/5 nuovi test PASS + 30/30 totali zero regression + REGOLA #11 matrice CHIUSA 4/4. Commit S275 (`9bd5107`) atomico in chiusura, MacBook+iMac sync fast-forward.
