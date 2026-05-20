# Prompt ripartenza S275 — backlog opzionale (CTO discrezione, REGOLA #15)

## Stato chiusura S274 (VERDE pieno)

**S274 outcome**: refactor `internal_*` operatori.rs + integration test PII encryption — REGOLA #14 PASS (autonomous backend SSH+cargo) + REGOLA #15 introdotta (no A/B questions su scope).

### Done S274
1. ✅ **`src-tauri/src/commands/operatori.rs`** (3 fns `internal_*` pool-based estratte)
   - `internal_get_operatore(pool, id)` — helper interno
   - `internal_create_operatore(pool, input)` — encrypt PII (nome/cognome required + email/telefono opt) + insert
   - `internal_update_operatore(pool, id, input)` — partial merge Option<T>.unwrap_or(current) + re-encrypt PII
   - Tauri command wrappers (`get_operatore`/`create_operatore`/`update_operatore`) delegano in 1 riga
   - **NO audit logging** in operatori (a differenza di clienti S273), pattern semplice come fatture S271 (return Operatore singolo, no tuple)
2. ✅ **`src-tauri/tests/integration_operatori.rs`** (nuovo) — 4 test PASS in 5.69s:
   - `test_create_operatore_encrypts_pii_at_rest` (nome/cognome/email/telefono len ≥16, ≠ plaintext)
   - `test_update_operatore_re_encrypts_changed_fields` (ciphertext post ≠ snapshot pre, AES-GCM random nonce)
   - `test_get_operatore_decrypts_with_optional_fields_none` (Option pass-through corretto)
   - `test_update_operatore_partial_input_preserves_unchanged_fields` (regression critica per partial merge)
3. ✅ **No regression** (25/25 test totali PASS via SSH iMac autonomous):
   - integration_operatori 4/4 (nuovo) in 5.69s
   - integration_clienti 4/4 in 5.64s
   - integration_fatture 4/4 in 5.67s
   - integration_appuntamenti 9/9 in 12.12s
   - integration_encryption_repair 4/4 in 0.21s
4. ✅ Cargo check 0 errori (9 warnings preesistenti S272, NON introdotti S274).
5. ✅ Commit pulito S274: solo 2 file rilevanti (operatori.rs + tests/integration_operatori.rs). Reset spurio `.claude/NEXT_SESSION_PROMPT.md` auto-gen boot template pre-commit (cleanup carry-over S273).
6. ✅ REGOLA #15 INTRODOTTA + memorizzata (feedback_no_ab_questions_cto_autonomous.md): mai chiedere founder A/B su scope sessione.

### Out of scope mantenuto (S274)
- `get_operatori` (list bulk + sort, no PII edge case beyond roundtrip già coperto)
- `delete_operatore` (soft delete via `attivo=0`, no PII touched)
- `operatori_servizi` / `operatori_assenze` / `operatori_commissioni` (no PII proprio)
- KPI views (`v_kpi_operatori` decifrato in `kpi_raw_to_public` — già funzionale)

### Note operative S274
- Pattern S271 fatture replicato (no audit logging — più semplice di S273 clienti che ha audit/tuple return)
- Schema operatori 12 colonne in struct ma DB ha extra colonne post-migrations (specializzazioni, descrizione_positiva, anni_esperienza, genere). sqlx::FromRow è permissivo su extra colonne in row (ignorate silentemente)
- iMac aveva 14 file cargo fmt residual diff pre-S274 (`fatture.rs`/`dashboard.rs`/`cassa.rs`/etc) NON pertinenti — non toccati né committati S274

---

## TASK candidati S275 (CTO discrezione, REGOLA #15 — no A/B, decide e parti)

### Track A: internal_* supplier.rs (REGOLA #11 cross-entity completion — last entity)
- Refactor `commands/supplier.rs` (singolare, da verificare nome esatto) per estrarre `internal_*` fns pool-based
- Aggiungi `tests/integration_supplier.rs` con regression PII encryption
- AC: cargo test PASS + no regression existing (29+/29+ totali) + pre-commit clean
- **Completa matrice REGOLA #11 4/4**: clienti (S273), operatori (S274), supplier (S275), impostazioni_fatturazione (S271 via fatture.rs già coperto)
- Effort: ~3h backend autonomous. `appuntamenti.rs` SKIP — no PII proprio (FK only, decrypt riga 462 solo per join).

### Track B: feature roadmap
- Verifica `ROADMAP_REMAINING.md` per next feature non-bug pipeline
- Probabili candidati: Sara voice edge cases, waitlist UX, fatture PDF rendering, loyalty tier upgrade

### Track C: founder-driven (priorità alta se emerge pain operativo)
- Pain point uso quotidiano FLUXION
- Demo/video/marketing → skill `fluxion-video-creator`

### Track D: pulizia cargo fmt residual iMac (igiene repo)
- 14 file con cargo fmt diff residual su iMac NON committati. Run `cargo fmt` su MacBook → sync iMac → commit unico `chore: cargo fmt` se diff identico
- Effort: ~30min, riduce rumore prossime sessioni

---

## Vincoli S275
- **REGOLA #14**: CTO autonomous test+fix backend via SSH+cargo. Founder solo decisioni strategiche / GUI Keychain unlock.
- **REGOLA #15**: NO domande A/B su scope. Decide best ROI/risk e parti.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **REGOLA #11**: cross-entity audit pattern PII encryption — last entity supplier.rs per chiudere matrice 4/4.
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/schema config) → BLOCK_CRITICAL ≥50% raw.

---

## PROMPT START S275

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S274 close + backlog.

REGOLA #15 attiva: decidi track autonomamente. Track A è il completamento naturale REGOLA #11 cross-entity (supplier.rs).

REGOLA #14: backend-side autonomous. Founder solo override su pain operativo.
```

---

**Provenienza S274 close**: VERDE pieno. 4/4 nuovi test PASS + 25/25 totali zero regression + REGOLA #15 memorizzata. Commit S274 atomico in chiusura.
