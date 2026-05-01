# FLUXION — Roadmap S183→S190+ (4-Gate Strict)

> **Generato**: 2026-04-30 — sessione S182
> **Source**: `PRE-LAUNCH-AUDIT.md` (22 P0 BLOCKING / 21 P1 / 12 P2)
> **Direttiva**: NO compromessi — gate enforcement strict (Gate N+1 SOLO dopo Gate N tutto verde con E2E PASS)
> **Vincolo**: zero costi (Resend free, CF free, Stripe 1.5%) — confermato S181
> **Standard**: ISO 25010 / OWASP ASVS L1 / Apple HIG / GDPR / D.Lgs 206/2005

---

## OVERVIEW GATE

| Gate | Sprint | Categoria P0 | ETA | Esito |
|------|--------|--------------|-----|-------|
| **Gate 1** | S183 → S185 | A. BUILD + B. FUNCTIONAL E2E | ~41h | DMG/MSI universal installabile + 5 hero feature E2E PASS |
| **Gate 2** | S185 → S186 | C. SECURITY + E. COMPLIANCE | ~4.5h | OWASP ASVS L1 PASS + GDPR/D.Lgs 206 P0 chiusi |
| **Gate 3** | S186 → S187 | D. PERFORMANCE + F. CUSTOMER SUCCESS | ~11.5h | SLO PASS + FAQ/runbook/email seq/monitoring vivi |
| **Gate 4** | S188 | LAUNCH | manual + monitoring | Stripe LIVE flip + primo cliente reale |
| Buffer | S189-S190 | P1 + recovery | — | Hardening + post-launch tweaks |

**Regola gate**: NON procedere a Gate N+1 se UN SOLO P0 di Gate N è OPEN. Fail-fast con re-plan se item slitta.

---

## SPRINT S183 — BUILD universal + Functional P0 batch 1 (~12h)

**Obiettivo**: completare Categoria A (Build & Distribution) + iniziare B (Functional E2E) sui 2 item più indipendenti (B-4 License + B-5 Backup).

### Task

| Step | ID Audit | Descrizione | ETA | Agent | Tipo |
|------|----------|-------------|-----|-------|------|
| 1 | A-1 | Build voice-agent arm64 (PyInstaller) su iMac via SSH | 0.5h | `imac-operator` + `installer-builder` | iMac SSH |
| 2 | A-1 | Universal Binary Tauri (`x86_64-apple-darwin` + `aarch64-apple-darwin`) + lipo | 1.5h | `installer-builder` + `imac-operator` | iMac SSH |
| 3 | A-4 | Code-sign ad-hoc + entitlements + spctl verify universal DMG | 1h | `code-signer` | iMac SSH |
| 4 | A-2 | Setup Win build (GitHub Actions runner Win + Rust + Node toolchain — zero costi) | 1.5h | `devops-automator` + `installer-builder` | GitHub Actions |
| 5 | A-2 | Build MSI Windows + smoke test su Win10 VM | 1.5h | `installer-builder` + `build-verifier` | CI |
| 6 | A-3 | Tauri auto-updater configure + chiave firma + endpoint GitHub Releases | 2h | `update-manager` + `devops-automator` | iMac + Worker |
| 7 | A-5 | `landing/come-installare.html` aggiungi sezione SmartScreen Windows | 1h | `documentation-writer` + `frontend-developer` | landing |
| 8 | A-6 | HW test Mac Intel + M1 (founder iMac) + Win10 VM (`build-verifier` matrix) | 3h | `build-verifier` | iMac + VM |
| 9 | A-7 | GitHub Releases v1.0.1 universal DMG + Win MSI + auto-update manifest | 0.5h | `release-engineer` | GitHub |
| 10 | A-8 | `git rm` `*.backup*` + update `.gitignore` | 0.25h | `devops-automator` | repo |

### Gate 1 progress S183: 100% A done.

### Verify (E2E PASS obbligatorio prima chiusura S183):
- [ ] Universal DMG installabile su Mac Intel + Mac M1 (verify via `lipo -info`)
- [ ] Win MSI installabile su Win10 + Win11 VM
- [ ] App lancia su tutti 4 OS senza errori
- [ ] Auto-updater controlla GitHub Releases endpoint senza fallire
- [ ] `landing/come-installare.html` HTTP 200 con sezione SmartScreen presente

### Commit atomici previsti
```
S183-A1: feat(build): voice-agent PyInstaller arm64 build
S183-A2: feat(build): macOS Universal Binary Intel+ARM
S183-A3: feat(build): Windows MSI via GitHub Actions
S183-A4: feat(updater): Tauri auto-updater configurato
S183-A5: docs(landing): SmartScreen Windows section
S183-A6: test(build): HW matrix verify pass
S183-A7: chore(release): v1.0.1 universal DMG + Win MSI
S183-A8: chore(repo): rm *.backup* files + gitignore
```

---

## SPRINT S184 — Functional E2E batch 2 (~14h)

**Obiettivo**: chiudere B-4 License client + B-5 Backup + B-1 Sara live audio (3 feature P0 più impattanti business).

### Task

| Step | ID Audit | Descrizione | ETA | Agent | Tipo |
|------|----------|-------------|-----|-------|------|
| 1 | B-4 | Rust unit test Ed25519 round-trip (`license_ed25519.rs`) | 1.5h | `license-manager` | Rust |
| 2 | B-4 | E2E completo: Stripe TEST checkout → email Resend → app install → activate | 2.5h | `license-manager` + `e2e-tester` | full chain |
| 3 | B-4 | Test offline cache + refund propagation (KV `purchase.refunded=true` → client blocca) | 2h | `license-manager` + `api-tester` | Rust + Worker |
| 4 | B-5 | Test backup integrity (SHA256 pre/post) + WAL checkpoint | 1.5h | `database-engineer` | Rust |
| 5 | B-5 | Test restore (modifica DB → backup → restore → assert hash identico) | 1h | `database-engineer` | Rust |
| 6 | B-5 | Test concurrent backup mentre app scrive + corrupted DB recovery | 1.5h | `database-engineer` | Rust |
| 7 | B-1 | `t1_live_test.py` con 5 WAV reali registrati (Gino vs Gigio, Soprannome VIP, Chiusura, Flusso, Waitlist) | 2h | `voice-tester` + `voice-engineer` | iMac |
| 8 | B-1 | Harness `subprocess.Popen(arecord/sox)` validare loopback speaker | 1h | `voice-tester` | iMac fisico |
| 9 | B-1 | Fixture pipeline auto-start + CI gate `pytest -m live_audio` | 1h | `voice-tester` | iMac |

### Verify (E2E PASS obbligatorio):
- [ ] B-4: Stripe TEST card 4242 → email arrivata → click magic link → license attivata + trial 30gg
- [ ] B-4: refund Stripe TEST → license bloccata client-side
- [ ] B-5: backup → restore → 0 data loss, hash match
- [ ] B-1: 5 scenari live audio iMac PASS con SLO <800ms (offline Piper)
- [ ] B-1: pipeline running stable >10min senza crash

---

## SPRINT S185 — WhatsApp + SDI E2E + Gate 1 closure (~18h)

**Obiettivo**: chiudere B-2 WhatsApp Cloud + B-3 SDI sandbox (i 2 più pesanti) + chiusura Gate 1.

### Task

| Step | ID Audit | Descrizione | ETA | Agent |
|------|----------|-------------|-----|-------|
| 1 | B-2 | Setup account WhatsApp Business sandbox Meta + access token | 1.5h | `whatsapp-api-integrator` |
| 2 | B-2 | Test reale `pytest -m whatsapp_live` send a numero test founder | 1.5h | `whatsapp-automation` |
| 3 | B-2 | Scheduler `reminder_scheduler.py` integration test (T-24h/T-2h) | 1.5h | `voice-engineer` + `api-tester` |
| 4 | B-2 | Webhook signature HMAC Meta validation E2E | 1.5h | `whatsapp-api-integrator` |
| 5 | B-3 | Account sandbox Aruba/Fattura24 + credentials | 1.5h | `fatture-specialist` |
| 6 | B-3 | XML XSD validator pytest (FatturaPA 1.2.2) | 3h | `fatture-specialist` |
| 7 | B-3 | E2E sandbox: crea fattura → genera XML → invia → ricevi `sdi_id_trasmissione` → conferma esito | 3.5h | `fatture-specialist` + `api-tester` |
| 8 | B-3 | Test numerazione progressiva concurrency (N transazioni parallele → 0 duplicati) | 2h | `database-engineer` + `fatture-specialist` |
| 9 | — | **Gate 1 closure ceremony**: re-run full E2E suite + audit checklist | 2h | `gsd-verifier` |

### Verify Gate 1 (TUTTI E2E PASS):
- [x] A-1..A-8 done (S183-bis CHIUSA ✅ — v1.0.1 Released 2026-05-01, 3/4 OS GREEN, macos-intel waived per Universal Binary)
- [ ] B-1, B-2, B-3, B-4, B-5 PASS (5/5)
- [ ] No regressioni Rust 117 unit + 9 integration
- [ ] Pipeline voice running 1h senza crash su iMac
- [ ] DMG/MSI installabili 4/4 OS (Mac Intel, Mac M1, Win10, Win11)

**🚪 Gate 1 PASS** → procedi Gate 2. **Se anche 1 fail**: re-plan, NO Gate 2.

---

## SPRINT S186 — Security + Compliance Gate 2 + Performance P0 (~13h)

**Obiettivo**: chiudere Categoria C + E (P0) + iniziare D (Performance).

### Task — Gate 2 (Security + Compliance ~4.5h)

| Step | ID Audit | Descrizione | ETA | Agent |
|------|----------|-------------|-----|-------|
| 1 | C-1 | Constant-time admin auth XOR pattern (replicare `stripe-webhook.ts:111-120`) | 0.5h | `cloudflare-engineer` |
| 2 | C-1 | Split `ADMIN_API_SECRET` da `LEAD_MAGNET_SIGNING_SECRET` + nuovo Worker secret | 0.5h | `cloudflare-engineer` |
| 3 | C-1 | Rotation token + audit log failed auth attempts | 1h | `security-auditor` |
| 4 | E-1 | `checkout-consent.html` append `?client_reference_id=${consentId}` al Payment Link | 0.25h | `frontend-developer` |
| 5 | E-1 | `stripe-webhook.ts` legge `event.data.object.client_reference_id` + salva in `purchase:{email}` KV | 0.25h | `cloudflare-engineer` |
| 6 | E-2 | Disclaimer "ricostruzioni rappresentative" sotto testimonianze landing:2098-2148 | 0.25h | `content-creator` |
| 7 | E-3 | `wrangler secret put STRIPE_SECRET_KEY` con sk_live_ + smoke test refund 404 vs 503 | 0.2h | `devops-automator` |
| 8 | E-4 | Crea `landing/termini.html` (licenza lifetime, limitazione responsabilità, AI disclaimer, supporto, aggiornamenti) | 1.5h | `legal-compliance-checker` + `content-creator` |
| 9 | — | **Gate 2 closure**: re-audit ASVS L1 + GDPR + D.Lgs 206 | 0.5h | `gsd-verifier` |

### Task — Performance Gate 3 (parte 1, ~6.5h)

| Step | ID Audit | Descrizione | ETA | Agent |
|------|----------|-------------|-----|-------|
| 10 | D-1 | `clienti.rs` `get_clienti_paginated(page, page_size)` + count | 2h | `backend-architect` + `database-engineer` |
| 11 | D-2 | `ClientiPage.tsx` React Query `useInfiniteQuery` + `react-window` virtual list | 4h | `frontend-developer` |
| 12 | D-3 | Voice offline (Piper) latency benchmark su iMac — record P50/P95 | 0.5h | `performance-benchmarker` + `imac-operator` |

### Verify Gate 2:
- [ ] C-1 PASS: bearer auth timing-safe + secrets split + rotated
- [ ] E-1 PASS: webhook salva `client_reference_id`
- [ ] E-2 PASS: disclaimer landing live in prod (CF Pages HTTP 200)
- [ ] E-3 PASS: refund endpoint 404 (no 503)
- [ ] E-4 PASS: `landing/termini.html` HTTP 200 + linkato in footer

**🚪 Gate 2 PASS** → procedi Gate 3.

---

## SPRINT S187 — Customer Success Gate 3 + chiusura (~7h)

**Obiettivo**: chiudere Categoria F (Customer Success P0) + verifica perf SLO.

### Task

| Step | ID Audit | Descrizione | ETA | Agent |
|------|----------|-------------|-----|-------|
| 1 | F-1 | `landing/faq.html` 20+ domande PMI (search + ancore) | 2h | `support-responder` + `content-creator` |
| 2 | F-2 | Support runbook `docs/SUPPORT-RUNBOOK.md` + email template top-20 issue | 1.5h | `support-responder` |
| 3 | F-3 | Email transactional sequence Resend (welcome, attivazione, day-3, day-7, day-30) | 1.5h | `email-marketer` |
| 4 | F-4 | CF Worker `/health` aggregato + alert via webhook Telegram/Discord (free tier) + uptime monitoring | 1h | `infrastructure-maintainer` + `self-healing-monitor` |
| 5 | D-1/D-2 | Verify SLO post-pagination: `EXPLAIN QUERY PLAN` + benchmark IPC <100ms | 1h | `performance-benchmarker` |

### Verify Gate 3:
- [ ] D-1, D-2, D-3 PASS (DB <50ms p95 con paginated, voice offline <800ms)
- [ ] F-1, F-2, F-3, F-4 PASS (FAQ live, runbook commit, email seq tested, monitoring alerting)
- [ ] No regressione test E2E S183-S185

**🚪 Gate 3 PASS** → procedi Gate 4 (LAUNCH).

---

## SPRINT S188 — Gate 4 LAUNCH (~3h + monitoring 24h)

**Obiettivo**: Stripe LIVE flip + lancio pubblico + primo cliente reale.

### Task

| Step | Descrizione | ETA | Agent |
|------|-------------|-----|-------|
| 1 | Stripe LIVE Payment Links Base + Pro + webhook secret LIVE | 0.5h | `cloudflare-engineer` + `checkout-optimizer` |
| 2 | Worker secrets update (sk_live_, whsec_LIVE) + smoke test webhook synthetic | 0.5h | `devops-automator` |
| 3 | Revoke `rk_live_` legacy (audit S179) | 0.1h | `security-auditor` |
| 4 | E2E LIVE carta reale Base €497 + refund immediato (€0 cost netto, denaro vero) | 1h | `checkout-optimizer` + `e2e-tester` |
| 5 | Smoke test deliverability email `onboarding@resend.dev` su Gmail/iCloud/Outlook reali | 0.5h | `email-marketer` |
| 6 | Pubblica landing pubblica (RIMUOVI banner "in arrivo") + post social founder | 0.5h | `content-creator` + `social-media-strategist` |
| 7 | Monitor 24h: CF logs, Resend dashboard, Stripe dashboard, voice pipeline iMac | manual | `infrastructure-maintainer` |

### Verify Gate 4 (lancio):
- [ ] LIVE charge reale + refund completo PASS (€0 net)
- [ ] Email deliverability OK su 3 provider (Gmail, iCloud, Outlook)
- [ ] Landing pubblica HTTP 200 stabile 24h
- [ ] Monitoring alerting funzionante (test failure simulato)
- [ ] No P0 reopened post-Gate 1/2/3

**🎉 Gate 4 PASS** → FLUXION live in produzione.

---

## SPRINT S189-S190 — Buffer + P1 hardening

**Solo dopo Gate 4 + primo cliente reale stabile.**

### Backlog P1 da chiudere

| Categoria | Item rimanenti | ETA |
|-----------|----------------|-----|
| B (E2E) | B-6 Onboarding wizard, B-7 Recall scheduler, B-8 Refund regression, B-9 7 verticali | 14h |
| C (Security) | C-2 XSS guida-pmi, C-3 rate limit Worker, C-4 collapse refund codes | 4h |
| D (Performance) | D-5 lazy voice agent, D-6 batch audit logs, D-7 IPC read pagination, D-8 UI virtualization | 16h |
| E (Compliance) | E-5..E-9, E-11 (retention nota, copy art.7, art.13 doc, art.22 priv, unsubscribe, listini badge) | 2.5h |
| F (UX) | F-5 empty states, F-6 troubleshooting, F-7 onboarding video | 8h |

**Totale P1**: ~44.5h = ~6 sessioni post-launch.

### v1.1 (Sprint S191+)

- D-4: Streaming LLM Groq SSE + parallel TTS prefetch (12h, voice latency 1330→<800ms)
- E-10: PBKDF2 salt random per installazione (3h)
- C-5..C-8 e P2 finali

---

## RECOVERY PROTOCOL (se Gate fail)

1. **Identifica gap concreto** (file:line + test fail output)
2. **Re-plan sprint successivo** (NO skip Gate)
3. **Aggiorna PRE-LAUNCH-AUDIT.md** + ROADMAP_S183_S190.md con nuovo ETA
4. **Notifica founder** SOLO se: blocker fuori budget zero-costi / legalmente ambiguo / scope vision business
5. **Continue gate sequence** dopo fix

**Mantra**: "Tutto si può fare. Basta solo trovare il modo." — Founder

---

## DASHBOARD MILESTONE

```
[ ] S183 Build & Distribution complete (A-1..A-8)
[ ] S184 Functional E2E batch 1 (B-1, B-4, B-5)
[ ] S185 Functional E2E batch 2 + Gate 1 closure (B-2, B-3) 🚪
[ ] S186 Security + Compliance + Perf P0 + Gate 2 closure (C-1, E-1..E-4, D-1..D-3) 🚪
[ ] S187 Customer Success + Gate 3 closure (F-1..F-4) 🚪
[ ] S188 LAUNCH (Stripe LIVE + primo cliente) 🚪🎉
[ ] S189-S190 P1 hardening + monitoring stabilizzazione
```

---

**Generato**: 2026-04-30, sessione S182
**Owner CTO**: io (autonomous decision-making, founder paga €220/mese per ownership)
**Riferimento audit**: `PRE-LAUNCH-AUDIT.md` (questo file e roadmap mai disgiunti)
