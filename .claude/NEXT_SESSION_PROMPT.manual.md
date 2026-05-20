# Prompt ripartenza S274 — backlog opzionale (CTO discrezione)

## Stato chiusura S273 (VERDE pieno)

**S273 outcome** (commit `8caec04` master MacBook+iMac sync): refactor `internal_*` clienti.rs + integration test PII encryption — REGOLA #14 PASS (autonomous backend SSH+cargo).

### Done S273
1. ✅ **`src-tauri/src/commands/clienti.rs`** (+111 / -37): 4 fns `internal_*` pool-based estratte
   - `internal_get_cliente(pool, id)` — helper interno per create/update
   - `internal_create_cliente(pool, ...)` — encrypt-at-rest + insert
   - `internal_update_cliente(pool, ...)` — ritorna `(before, after)` tuple per audit propagation (deviazione motivata vs S271)
   - `internal_search_clienti(pool, query)` — tier-1 in-memory filter post-decrypt
   - Tauri command wrappers delegano in 1-2 righe; audit logging (`log_create/update`) resta nei wrapper (richiede `AppState`).
2. ✅ **`src-tauri/tests/integration_clienti.rs`** (+311, nuovo) — 4 test PASS in 5.66s:
   - `test_create_cliente_encrypts_pii_at_rest` (nome/cognome/telefono/email len ≥16, ≠ plaintext, Base64-like)
   - `test_update_cliente_re_encrypts_changed_fields` (ciphertext post-update ≠ snapshot pre-update)
   - `test_search_clienti_matches_decrypted_plaintext` (tier-1 filter funziona)
   - `test_search_clienti_no_match` (Vec vuoto, non Err)
3. ✅ **No regression** (verify autonomous SSH iMac):
   - `integration_fatture` 4/4 PASS in 5.76s
   - `integration_appuntamenti` 9/9 PASS in 11.86s
   - `integration_encryption_repair` 4/4 PASS in 0.23s
   - **21/21 test totali PASS**
4. ✅ Pre-commit hook PASS (cargo fmt + type-check + lint clean — 17 warnings any preesistenti, non blocker).
5. ✅ REGOLA #6 verified (no `Co-Authored-By: Claude/anthropic` trailer).

### Out of scope mantenuto (S273)
- `gdpr_hard_delete_cliente` (audit-sensitive, non toccato)
- `get_clienti` (list bulk + sort, non rilevante per testability target)
- Schema DB, migration (no changes)

### Note operative S273
- Pattern S271 fatture replicato con 1 deviazione motivata: `internal_update_cliente` ritorna `(Cliente, Cliente)` tuple invece di solo `Cliente` per propagare snapshot pre-update al wrapper Tauri che fa `log_update(before, after)`.
- Rumore commit: pre-commit hook `lint:fix` + `git add .` ha incluso modifica spuria a `.claude/NEXT_SESSION_PROMPT.md` (boot template) — 3 file invece di 2. Non impatta correttezza. Da pulire prossimo commit pertinente.

---

## TASK candidati S274 (CTO discrezione, no P0 attivo)

### Track A: internal_* operatori.rs (REGOLA #11 cross-entity completion)
- Refactor `commands/operatori.rs` per estrarre `internal_*` fns pool-based pattern S271/S273
- Aggiungi `tests/integration_operatori.rs` con regression PII encryption (operatori ha PII subset: nome/cognome/telefono/email/codice_fiscale)
- AC: cargo test PASS + no regression existing + pre-commit clean
- Effort: ~3-4h backend autonomous (operatori più piccolo di clienti)

### Track B: internal_* appuntamenti.rs / suppliers.rs
- Stesso pattern, applicabile alle 2 entity rimanenti delle 4 marker-gated S272 safety net
- Effort: ~3-4h each

### Track C: feature roadmap
- Verifica `ROADMAP_REMAINING.md` per next feature non-bug pipeline
- Probabili candidati: Sara voice edge cases, waitlist UX, fatture PDF rendering, loyalty tier upgrade

### Track D: founder-driven (priorità alta se emerge)
- Pain point operativo founder (uso quotidiano)
- Demo/video/marketing → skill `fluxion-video-creator`

---

## Vincoli S274
- **REGOLA #14**: CTO autonomous test+fix backend-side via SSH + cargo test. Founder solo decisioni strategiche / GUI Keychain unlock.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **REGOLA #11**: cross-entity audit pattern (clienti/operatori/appuntamenti/suppliers) — completare la matrice testabilità per PII encryption regression coverage.
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/schema config) → BLOCK_CRITICAL ≥50% raw.

---

## PROMPT START S274

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S273 close + backlog.

Se founder ha pain operativo → Track D (autonomous fix via SSH).
Se backlog vuoto → Track A (internal_* operatori.rs + integration test).

REGOLA #14: autonomous backend-side. Founder solo per decisioni strategiche.
```

---

**Provenienza S273 close**: VERDE pieno. 5/5 AC raggiunti + 21/21 test totali PASS + zero regression. Commit atomico `8caec04` con trailer pulito.
