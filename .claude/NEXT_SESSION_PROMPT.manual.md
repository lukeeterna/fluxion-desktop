# Prompt ripartenza S282 — backlog Gate 1 (Track B/C/F)

## Stato chiusura S281 (VERDE, Track D cargo fmt residual + .gitignore voice-agent/venv)

**S281 outcome**: Track D autonomous via SSH iMac. Research-first (REGOLA #16 nuova) ha verificato:
- Track B (Stripe E2E) BLOCKED — `fluxion-proxy/wrangler.toml` ha SOLO production, no `[env.test]` block. Manca CF_API_TOKEN + Stripe TEST keys + Resend test key (founder credentials).
- Track C (voice live) BLOCKED — porte 3001/3002 OFF su iMac + microfono fisico founder.
- Track D: diff fmt REALE verificato `cargo fmt --check` (4 hunks initial `ipc_bench.rs`) → applicato → 20 file modificati line-break/multiline reflow.

**Commit pulito**: `5e83681e` master (MacBook+iMac+origin allineati 3-way).

### Done S281

1. ✅ **Research-first** eseguita (REGOLA #16 nuova): `git status`, `cargo fmt --check`, `lsof porte iMac`, `cat wrangler.toml`, `ls fluxion-proxy/tests/`, `grep stripe-webhook.ts`. Dati certi PRIMA di propose track.
2. ✅ `cargo fmt` su iMac → 20 file fmt-only (line-break/multiline reflow). Verified zero AST change via diff sampling `license_ed25519.rs`.
3. ✅ `cargo check --tests` 33.37s zero error (solo 7 warning dead code helpers preesistenti).
4. ✅ `.gitignore` esteso con `voice-agent/venv/`.
5. ✅ Commit `5e83681e` (21 file, 259/194 ins/del). Pre-commit Husky PASSED.
6. ✅ Push iMac → origin + pull rebase MacBook con stash temporaneo NEXT_SESSION_PROMPT.md.

### Incidente recovery documentato

Primo commit ha incluso 8866 file (8846 `voice-agent/venv/` Python binary). Husky fail per PATH npm SSH non-interactive → retry catturò venv. Fix: `git reset --soft HEAD~1` + `git reset HEAD voice-agent/venv/` → 20 file puliti. Lesson: SSH wrapper FLUXION future usare `bash -l -c` o `export PATH=/usr/local/bin:$PATH`.

### Verify S281
- Commit `5e83681e` ha solo 21 file (verified `git show --stat HEAD`).
- master MacBook + iMac + origin allineati.
- cargo check --tests 33.37s 0 error.

### Out of scope mantenuto S281
- Track B/C/E/F backlog rimasti.
- BUG-FATT-3 cache stale fatture + BUG-FATT-5 toast z-index ancora defer S267.

---

## TASK candidati S282 (CTO discrezione REGOLA #15 + research-first REGOLA #16)

### Track B — Setup CF Worker test env + Stripe E2E (~5-6h, founder credentials)
- **PREREQ founder**: `CLOUDFLARE_API_TOKEN` env var + Stripe TEST sandbox keys (sk_test_, whsec_test_) + Resend test API key.
- **CTO autonomous**:
  - `[env.test]` block in `fluxion-proxy/wrangler.toml` + KV namespace test separato (`wrangler kv namespace create LICENSE_CACHE --env test`).
  - `wrangler deploy --env test`.
  - Stripe Dashboard webhook endpoint TEST → curl POST `checkout.session.completed` con TEST card 4242 → verify chain (KV `purchase:{email}` scritto, email Resend test arrivata, magic link, activate-by-email 200, phone-home post-refund ritorna `status='revoked'`).
- **Chiude Gate 1 B-4 Step 2 (E2E Stripe full chain con TEST card 4242)** open da S279.

### Track C — B-1 Voice live audio test (~4h, Gate 1 critical, founder presence)
- Pipeline iMac UP (porte 3001/3002 OFF al boot S278-S281) + 5 WAV reali scenari (Gino/Gigio, soprannome VIP, chiusura graceful, flusso perfetto, WAITLIST) + microfono fisico loopback.
- Agent: `voice-tester` + `voice-engineer`.

### Track F — Force phone-home post Stripe webhook refund (~1-2h, autonomous spike)
- Server-side push al client per forzare phone-home immediato senza attendere 24h interval. Research design: SSE? polling più frequente? webhook reverse Tauri? Spike research prima di plan.

### Track E — Migration `017_license_revoked_status.sql` opzionale (~30min, autonomous, low-priority)
- CHECK constraint enum esteso su `status` per documentation + safety futura. Solo se DBA audit lo segnala.

### BUG-FATT-3 cache stale fatture lista (defer S267)
- Re-audit dopo fix S276 use-fatture.ts `await invalidateQueries`. Verifica founder live GUI iMac per confermare end-to-end.

### BUG-FATT-5 toast z-index dialog (defer S267)
- Toast notifications nascosto dietro Dialog overlay. CSS z-index fix Radix UI overlay layer.

---

## Vincoli S282

- **REGOLA #14**: CTO autonomous via SSH+cargo+npm. Founder solo CF/Stripe/Resend credentials + microfono live.
- **REGOLA #15**: NO A/B questions. CTO decide track + parte.
- **REGOLA #16**: research-first PRIMA di QUALSIASI decisione (WebSearch/Read/Grep/--help → dati certi → poi raccomandazione motivata).
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/wrangler.toml [env.test] schema) → BLOCK_CRITICAL ≥50% raw.
- **SSH commit on iMac**: usare `export PATH=/usr/local/bin:$PATH` o `bash -l -c "..."` per husky hooks (lesson S281).

---

## PROMPT START S282

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S281 close + backlog.

REGOLA #16 attiva: research-first prima di decidere track.
REGOLA #15 attiva: decidi autonomamente track senza chiedere founder.

Track suggested:
- Se founder fornisce CF/Stripe/Resend credentials all'avvio → Track B (chiude Gate 1 B-4 Step 2).
- Altrimenti Track F spike autonomous (~1-2h, force phone-home research).
- Alternativa: BUG-FATT-3 re-audit live verify (founder GUI iMac required REGOLA #12).

REGOLA #14: backend autonomous via SSH+cargo. Founder solo override.
```

---

**Provenienza S281 close**: VERDE pieno. Track D cargo fmt 20 file autonomous. REGOLA #16 introdotta + salvata. Carry-over Gate 1: Track B/C/F + BUG-FATT-3/5 backlog. Sara/loyalty/whatsapp/api_access gating S280 confermato by-construction (`is_valid=false` su status='revoked').
