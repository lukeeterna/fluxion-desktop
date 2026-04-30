# S182 — OWASP ASVS L1 Audit (Pre-Launch)

> Scope: src-tauri (Rust/Tauri 2), fluxion-proxy (Cloudflare Worker), voice-agent (Python aiohttp 127.0.0.1:3002)
> Method: static grep + targeted file reads. No false positives — every finding has file:line verified.
> Date: 2026-04-30 (S182 re-audit)

## Counts
CRITICAL: 0 | HIGH: 2 | MEDIUM: 6 | LOW: 4 | P0 blockers: 1

---

## HIGH-1 — guida-pmi.html: HTML injection via macro/sub-vertical names in onclick handlers
- ASVS V5.3.3 (Output encoding / contextual escaping) | File: `landing/guida-pmi.html:3242,3246-3251`
- Impatto: `selectMacro()` writes `sv.name` via `innerHTML` and emits inline `onclick="selectVertical(...id...)"` with no escaping. Today `SUB_VERTICALS` is a static literal so risk is bounded; any future move of those names to fetch/CMS or query-string instantly becomes stored/reflected XSS. Same file lines 3408/3442/3460 also assemble `innerHTML` from data structures.
- Fix: replace `innerHTML` with `textContent` for the title; build child elements via `document.createElement` + `addEventListener` instead of inline `onclick`. Quick patch: HTML-escape `id`/`name`/`desc` and JS-escape inside the inline handler.
- P1 | 1h

## HIGH-2 — admin-resend Bearer auth uses non-constant-time string equality
- ASVS V2.10.1 / V11.1.7 (Timing-safe credential comparison) | File: `fluxion-proxy/src/routes/admin-resend.ts:22-25`
- Impatto: header equality check uses regular `===` triple-equals. Combined with a public endpoint that gates DELETE on `/admin/resend/domains/:id` (and create/verify), this is theoretically vulnerable to timing oracles. With a 256-bit-entropy secret in CF Workers practical risk is low, but ASVS L1 V2 still requires constant-time check on auth tokens. Endpoint also has no rate-limit / no audit log of failed auth attempts.
- Fix: use the byte-XOR pattern already present in `stripe-webhook.ts:111-120` (length check + XOR loop); increment a counter on failure; add 401 backoff (~300ms).
- P0 | 1h

---

## MEDIUM-1 — Worker exposes `/admin/resend/*` on the same domain as public API; admin secret reused as lead-magnet HMAC key
- ASVS V1.4.1 / V13.2.1 (Trusted enforcement points) | File: `fluxion-proxy/src/index.ts:84-89`, `routes/admin-resend.ts:3` (comment "reused, no new secret needed")
- Impatto: a leak of the admin Bearer (also reused for HMAC of GDPR download tokens) gives an attacker DELETE on Resend domains AND ability to forge GDPR download tokens. Memory MEMORY.md already flags rotation as tech debt.
- Fix: (a) split secrets — admin must NOT reuse the lead-magnet HMAC key; (b) move admin routes behind a separate Worker route or CF Access policy; (c) rotate the admin token after S182.
- P0 | 1.5h (paired with HIGH-2)

## MEDIUM-2 — Public endpoints have no global rate-limit, only `/api/v1/lead-magnet` does
- ASVS V11.1.4 (Anti-automation) | Files: `fluxion-proxy/src/routes/refund.ts` (whole route), `consent-log.ts` (whole route), `routes/activate-by-email.ts` (referenced `index.ts:70`)
- Impatto: `/api/v1/rimborso`, `/api/v1/consent-log`, `/api/v1/activate-by-email` are public, do KV writes and can be flooded to: (a) burn KV write quota, (b) enumerate purchases via distinct error codes (see MEDIUM-3), (c) write 10y-TTL spam consent rows. `lead-magnet.ts:342-355` already has a clean per-IP KV rate-limit pattern — replicate it.
- Fix: per-IP rate limit (~20/h on rimborso, 60/h on consent-log) using `rl_refund:{ip}` / `rl_consent:{ip}` KV keys with TTL 3600.
- P1 | 2h

## MEDIUM-3 — Refund endpoint enables purchase-email enumeration
- ASVS V3.4.4 / V8.3.4 (Authentication enumeration) | File: `fluxion-proxy/src/routes/refund.ts:266-275, 285-294`
- Impatto: distinct error codes (`PURCHASE_NOT_FOUND` 404, `ALREADY_REFUNDED` 409, `REFUND_WINDOW_EXPIRED` 410) let an unauth caller enumerate which emails are paying customers. Combined with no rate-limit (MEDIUM-2) this is a directory attack on the customer base.
- Fix: collapse non-actionable outcomes into a neutral 200/202 response (`{ ok: false, code: "REFUND_NOT_AVAILABLE" }`); keep detailed codes only in server log; alternatively require one-time email confirmation link before processing.
- P1 | 1h

## MEDIUM-4 — Stripe webhook timestamp tolerance ±5 min using `Math.abs`
- ASVS V9.2.4 (Replay protection) | File: `fluxion-proxy/src/routes/stripe-webhook.ts:82-85`
- Impatto: `Math.abs(now - timestamp) > 300` accepts events with timestamps **up to 5 min in the future**. Stripe SDK only allows past skew. Combined with replay window this widens the attack surface to ~10 min total instead of 5.
- Fix: replace with one-sided check — allow ~30s clock skew, reject anything in the future > 30s.
- P2 | 15m

## MEDIUM-5 — voice-agent CORS `_is_allowed_origin` uses `startswith` (origin prefix bypass)
- ASVS V14.5.3 (CORS allow-list) | File: `voice-agent/main.py:61-68`
- Impatto: `origin.startswith("http://localhost")` matches `http://localhost.evil.com`, `http://localhost@attacker`. Pipeline binds 127.0.0.1 (defense-in-depth holds), but a future bind to LAN (e.g., remote SIP testing) instantly opens it. Same loose-match exists for `http://127.0.0.1`.
- Fix: parse with `urllib.parse.urlsplit(origin)` and require exact host match in `{"localhost","127.0.0.1"}` plus allowed scheme `http/tauri`.
- P2 | 30m

## MEDIUM-6 — voice-agent allows empty Origin → reflected as `http://localhost`
- ASVS V14.5.3 | File: `voice-agent/main.py:64, 81, 90`
- Impatto: `if not origin: return True` then header reflects `origin or "http://localhost"`. Browser-driven CSRF from any non-CORS context (form submit, image, etc.) succeeds because no `Origin` is sent on simple requests. Pipeline state-changing endpoints accept POST.
- Fix: require an explicit allowed Origin OR a custom header `X-Fluxion-IPC: 1` set by the Tauri client; otherwise return 403 on POST.
- P2 | 45m

---

## LOW-1 — Backup files in repo (`src-tauri/src.backup.20260205/`, `voice_pipeline.rs.backup.20260218_135028`)
- ASVS V14.3.2 (Source-tree hygiene) | Files: `src-tauri/src.backup.20260205/commands/voice_pipeline.rs:593`, `src-tauri/src/commands/voice_pipeline.rs.backup.20260218_135028`
- Impatto: backups duplicate logic and produced false positives in this audit (env-parser stays in two places). Distributed in DMG bundle if not excluded by Tauri resource filter.
- Fix: `git rm -r src-tauri/src.backup.* src-tauri/**/*.backup.*` and add `*.backup*` / `*.backup.*` to `.gitignore`.
- P2 | 15m

## LOW-2 — `audit_repository.rs` uses `format!` to build SELECT (parameters bound, NOT injection)
- ASVS V5.3.5 (Parameterized queries) | File: `src-tauri/src/infra/repositories/audit_repository.rs:316`
- Impatto: NO injection — `where_clause` is composed only of fixed column-name fragments produced by `build_query_conditions()`; bound values flow through `.bind`. Flagged because the pattern is fragile to future edits.
- Fix: add a unit test asserting `build_query_conditions()` only emits keys from a static allow-list, OR migrate to `sqlx::QueryBuilder`.
- P2 | 30m

## LOW-3 — Python dynamic SQL in `caller_memory.py` builds SET clause from dict keys
- ASVS V5.3.5 | File: `voice-agent/src/caller_memory.py:201-205`
- Impatto: `set_clause = ", ".join(...)` — keys are hard-coded literals at lines 193-199, NO user input flows in. Safe today, brittle to future maintainers.
- Fix: inline allow-list assertion `assert set(updates).issubset({...static allow-list...})`.
- P2 | 10m

## LOW-4 — `landing/index.html:2481` builds success message via `innerHTML` with literal HTML
- ASVS V5.3.3 | File: `landing/index.html:2479-2485`
- Impatto: literal string only, no interpolation — safe. Flagged for consistency with HIGH-1 fix.
- Fix: convert to `createElement` for consistency.
- P2 | 10m

---

## Verified PASS (no finding)
- **Stripe webhook HMAC verify**: timing-safe XOR loop OK (`stripe-webhook.ts:111-120`).
- **Tauri `Command::new` calls**: all use static binary names (`node`, `python`, `df`, `afplay`, `aplay`, `paplay`, `powershell`, sidecar `path` derived from app dir) — no user-string interpolation reachable via IPC. (`voice.rs:127-150`, `whatsapp.rs:82-134`, `voice_pipeline.rs:475-498`, `support.rs:143/889`, `remote_assist.rs:112`)
- **Python `subprocess`**: every call uses **list form** (no `shell=True`); only Popen with user-derived data is `whatsapp.py:572` and arg `message` is passed as a separate list element (no shell injection). PASS.
- **Voice-agent server bind**: `127.0.0.1` default with explicit doc comment (`main.py:1184`), rate-limit middleware in place (`main.py:99-142`), state-evicting LRU cap to bound memory.
- **Worker CORS**: explicit allow-list (no `*`), correct `allowMethods`/`allowHeaders`. (`index.ts:43-54`)
- **License middleware**: Ed25519 verify + revocation check + hardware fingerprint binding + 24h cache. (`middleware/auth.ts`)
- **NLU proxy rate limit**: 200/day per license enforced via KV counter, 429 on exceed. (`nlu-proxy.ts:44-58`)
- **Lead-magnet flow**: honeypot + MX-record check + per-IP KV rate limit + 72h one-time HMAC tokens + KV-lookup token compare. (`lead-magnet.ts:310-355`, `gdpr-download.ts:79-114`)
- **Python `eval/exec`**: only one match — `tests/test_humanness_b1_b2_b3.py:49` `ast.literal_eval(node.value)` (test fixture, safe AST traversal). NO dynamic eval on user data.
- **Secrets in repo**: only placeholder strings in `tools/VectCutAPI/pattern/002-relationship.py` ("your qwen api key" etc.) and a clearly-test fixture in `scripts/license-delivery/test_server.py`. NO live keys committed. `voice_pipeline.rs:810` reads the LLM key from environment, doesn't embed it.

---

## Verdetto: PASS — 1 P0 blocker prima del lancio

### P0 (MUST fix before launch)
1. **HIGH-2 + MEDIUM-1 combined**: (a) constant-time admin auth, (b) split admin Bearer from lead-magnet HMAC key, (c) rotate the admin token. ETA ~2h. Without this, leak of one secret gives DELETE on Resend domains AND ability to forge GDPR download tokens.

### P1 (fix in S183, before first 10 paying customers)
2. **HIGH-1** Sanitize `innerHTML` paths in `guida-pmi.html`.
3. **MEDIUM-2 + MEDIUM-3** Add per-IP rate-limit on rimborso/consent-log + collapse refund enumeration codes.

### P2 (post-launch maintenance)
4. **MEDIUM-4** Tighten Stripe replay window to past-only.
5. **MEDIUM-5/6** Harden voice-agent origin allow-list (parse URL, require exact host).
6. **LOW-1** Remove `*.backup*` from repo + add to `.gitignore`.
7. **LOW-2/3** Add allow-list assertions on dynamic-SQL builders.

---

## Output path
`/Volumes/MontereyT7/FLUXION/.claude/cache/agents/s182-security-owasp-asvs-l1.md`
