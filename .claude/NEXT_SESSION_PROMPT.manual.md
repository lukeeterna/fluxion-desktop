# Prompt ripartenza S279 — backlog Gate 1 S184/S185 (CTO discrezione, REGOLA #15)

## Stato chiusura S278 (VERDE, Track A Gate 1 critical path)

**S278 outcome**: B-5 backup/restore integration tests 7/7 PASS + 30/30 regression PASS + 5/5 license unit PASS = **42/42 backend test, zero regression**. ROADMAP_S183_S190.md SPRINT S184 Step 4-5-6 DONE. REGOLA #14 + REGOLA #15 PASS — 100% autonomous backend SSH+cargo, founder zero touch.

### Done S278
1. ✅ **Refactor `src-tauri/src/commands/support.rs`**: estratti `internal_backup_database(pool, backup_dir)` async + `internal_restore_database(backup, db, emergency_dir)` sync. Tauri wrapper delegano in 1-3 righe.
2. ✅ **Test file `tests/integration_backup.rs`** (NUOVO, 7 test, 9.77s):
   - Step 4 (backup integrity + WAL): valid sqlite identical data + uncheckpointed WAL data
   - Step 5 (restore round-trip): preserves pre-backup state + emergency backup auto-create
   - Step 6 (concurrent + corrupted): tokio writer in loop durante VACUUM INTO + corruption 1024 byte recovery
   - Bonus: file SHA256 stable across reads
3. ✅ **Helpers**: `sha256_file`, `sha256_clienti_canonical` (row dump robusto a non-determinism sqlite), `open_pool` (re-attach post-restore).
4. ✅ **Verify**: integration_backup 7/7 PASS + regression 30/30 + license unit 5/5 = 42/42 PASS.

### Analisi critica strutturale (vincolo #4)
- **Assunzione**: VACUUM INTO esegue checkpoint implicito WAL → test 4-B la verifica esplicitamente.
- **Cosa rompe a 30gg**: se prod abilitasse `PRAGMA wal_autocheckpoint=0` (disable auto), VACUUM INTO continuerebbe a includere WAL ma il test andrebbe rivisto per scenari edge. Improbabile.
- **Pattern noto**: SQLite file size può aumentare leggermente post-VACUUM (page compaction non perfetta) — i test usano row-level hash, non file-byte hash, quindi safe.
- **Dove sovradimensiono**: il 7° test (file SHA256 stability) è bonus paranoia helper. Tengo per garantire che future modifiche a `sha256_file` siano deterministiche.

---

## TASK candidati S279 (CTO discrezione, REGOLA #15 — no A/B)

### Track A: B-1 voice live audio test (Step 7-9 S184, ~4h, Gate 1 critical)
- ROADMAP_S183_S190.md:81-83: `t1_live_test.py` con 5 WAV reali (Gino vs Gigio, Soprannome VIP, Chiusura, Flusso, Waitlist) + harness `subprocess.Popen(arecord/sox)` loopback + fixture pipeline auto-start + CI gate `pytest -m live_audio`.
- BLOCKER: richiede voice pipeline iMac UP (porta 3002 down al boot S278), founder presence per microfono/speaker fisico ottimale o WAV pre-registrati.
- Agent: `voice-tester` + `voice-engineer`.
- Effort: ~4h, parzialmente autonomous (WAV pre-registrati OK via SSH), parte test live richiede founder.

### Track B: B-4 Step 2-3 E2E Stripe TEST → email → activate + refund propagation (~4.5h)
- ROADMAP_S183_S190.md:76-77: full chain checkout TEST card 4242 → webhook CF Worker → Resend test email → magic link → app activate.
- Setup richiesto: Stripe TEST keys (sk_test_) + Resend test inbox + CF Worker test env vars.
- Verifica preliminare: `wrangler secret list` su CF Worker test environment, account Stripe sandbox.
- Agent: `license-manager` + `e2e-tester` + `api-tester`.
- Effort: ~4.5h, 100% autonomous se setup esistente.

### Track C: B-2/B-3 WhatsApp + SDI E2E (S185, ~12h pesante)
- ROADMAP_S183_S190.md:99-110: WhatsApp Business sandbox + SDI sandbox Aruba/Fattura24 + XML XSD 1.2.2 validator + numerazione progressiva concurrency.
- Sotto-blocchi separabili da S185 Step 1-4 (WA, ~6h) e Step 5-8 (SDI, ~10h).
- Agent: `whatsapp-api-integrator`, `whatsapp-automation`, `fatture-specialist`, `database-engineer`.
- Effort: 6-10h per blocco, infra-heavy.

### Track D: founder-driven (priorità alta se emerge pain operativo)

---

## Vincoli S279
- **REGOLA #14**: CTO autonomous test+fix backend via SSH+cargo. Founder solo decisioni strategiche / GUI Keychain unlock / microfono fisico per voice live.
- **REGOLA #15**: NO domande A/B su scope. Decide best ROI/risk e parti.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/schema config) → BLOCK_CRITICAL ≥50% raw.

---

## PROMPT START S279

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S278 close + backlog Gate 1.

REGOLA #15 attiva: decidi track autonomamente.

Track suggested: Track B (B-4 Stripe E2E full chain 4.5h, gate critical path, 100% autonomous se setup esistente). In subordine Track A (voice live audio, blocker pipeline DOWN al boot).

REGOLA #14: backend-side autonomous. Founder solo override su pain operativo.
```

---

**Provenienza S278 close**: VERDE pieno. 42/42 test backend (7 backup + 5 license unit + 30 regression). REGOLA #14 PASS + REGOLA #15 PASS. Commit S278 atomico in chiusura.
