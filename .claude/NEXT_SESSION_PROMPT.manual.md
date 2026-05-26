# Prompt ripartenza S294 — Valutazione output Claude.ai web + decisione architetturale delivery licenza zero-cost

> ## META-VINCOLO S294 (S290 GO Luke + S291 evidence + S292 prod infra-ready + S293 research-gate)
>
> **S292 Tauri kid:v1 verify dalek CLOSED VERDE** — 8/8 tests PASS interop D1 reale S291 (Gate 3 evidence chiuso).
> **S292 prod infra Worker FASE A CLOSED VERDE** — D1 prod creato, migration applicata, wrangler.toml binding, secrets ED25519 prod uploaded.
> **S293 RESEARCH-GATE OPENED** — vincolo founder zero-cost + DKIM Gmail/Yahoo enforce 2024 = path Resend custom domain SCARTATO.
> **DEFERRED** Worker prod deploy code S291: in attesa decisione delivery licenza zero-cost (output Claude.ai web da valutare S294).
>
> **MAI dichiarare ring VERIFIED in prod** senza nuovo set 3 test reali letti da Luke (REGOLA #18 META-VINCOLO):
> - FDQ-01 prod: card 4242 → checkout sandbox prod → licenza firmata → delivery riuscita (canale TBD post-S294)
> - FSAF-05 prod: replay webhook prod 2x → 1 licenza + 1 delivery + D1 count invariato
> - Tauri activate-by-payload FE: estrai license_payload+signature → `invoke('verify_license_signature_v1')` → activation success

---

## Stato chiusura S293 (CLOSED VERDE — research zero-cost delivery + research-gate aperto, NO file critici modificati)

### Done S293

1. **Pre-flight S293 PASS 4/6**:
   - ✅ Env vars 4/5 SET (CLOUDFLARE_API_TOKEN, STRIPE_TEST_SECRET_KEY, RESEND_TEST_KEY, STRIPE_WEBHOOK_SECRET_TEST)
   - ❌ CLOUDFLARE_ACCOUNT_ID UNSET (uso fallback `22ddff3a4ef544511523a841b3dcadf8` per S293)
   - ✅ Keypair S290 ENTRAMBI persistiti (priv pkcs8 mode 600 + pub hex mode 644)
   - ✅ Worker prod + test entrambi `health=ok`
   - ❌ Resend domains `data:[]` (0 domini configurati)
   - ❌ CF zones `count=0` (founder NON ha registrato alcun dominio reale; `gianlucanewtech` = solo workers.dev subdomain)

2. **Path Resend dominio custom SCARTATO** (vincolo founder REGOLA #5 zero-cost rigoroso):
   - Cloudflare Registrar `.app` at-cost ~€13/yr → rifiutato founder (capex non sostituibile via software ma vincolo no-capex prevale).
   - WHOIS check varianti brand-preserving (fluxion.it/io/cloud/dev/tech/email/eu/tools/services/business/studio/pro/team/zone/global/center/digital/agency/systems/network/solutions/business + getfluxion.com/usefluxion.com/tryfluxion.com/fluxionhq.com): TUTTI taken eccetto hyphenated (`fluxion-app.com`, `fluxion-erp.com`) e `myfluxion.com`/`fluxionsoft.com`/`fluxionsuite.com` (brand-debt vocale o naming-debt).
   - Suggerimenti CF Registrar (`fluxion.app` taken, alternative `morphicion.com`/`fluxive.*`/`fluxion.ltd|media|live|club|icu` etc.) tutti rifiutati per brand-debt o TLD spam-flagged.

3. **Provider ESP free-tier alternativi research-first**:
   - **SendGrid**: free permanente RETIRATO 27 Maggio 2025 → solo trial 60gg poi $19.95/mese. SCARTATO.
   - **SMTP2GO**: free 1000/mese permanente MA signup `https://www.smtp2go.com/signup-custom/` blocca Gmail (private-domain only). SCARTATO.
   - **Brevo**: free 9000/mese permanente + signup Gmail OK + branding footer + DMARC misalignment 3rd-party sender → deliverability inbox <70%. SCARTATO.
   - **Mailjet**: free 6000/mese (200/giorno) + signup unclear + DMARC misalignment stesso problema Brevo. SCARTATO.
   - **Resend free 3000/mese**: sandbox enforced only-owner recipient. SCARTATO (current blocker).
   - **Vincolo strutturale identificato (REGOLA #4)**: Google/Yahoo Bulk Sender Requirements Feb 2024 enforce DKIM-aligned-domain per transactional verso Gmail/Outlook/Yahoo (~85% inbox PMI italiane B2B) → zero-cost + zero-dominio + recipient unrestricted + production-grade è simultaneamente non-soddisfacibile.

4. **Proposta CTO S293 (da challenge S294)**: eliminare email dal critical path delivery → Stripe Checkout `success_url` → CF Worker `/success/:session_id` HTML page con license_payload + signature inline + deep-link `fluxion://activate?payload=...&sig=...` + Tauri `tauri-plugin-deep-link` v2.x handler → `invoke('verify_license_signature_v1')` → activate. Email Resend retained come backup non-bloccante audit founder-owner.

5. **Prompt verification Claude.ai web fornito** (research-gate vincolo #1 verifica fattuale):
   - Richiesta verdetto su 3 sezioni (A vincolo strutturale email senza dominio, B path success_url + deep-link Tauri, C alternative architetturali non considerate)
   - Formato output strutturato: CONFIRMED/DISPUTED/NUANCED + evidence 2+ fonti per ogni claim + critica strutturale 4 punti su proposta CTO
   - Founder incolla in Claude.ai web → output letto + valutato in S294

### Files modificati S293

- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file) — S294 scope con valutazione output Claude.ai web
- Zero altri file (closing-only context 65%+ post system-reminders, REGOLA #7 + context-budget-gate.md)

### Note S293

- **Onestà CTO**: in S293 mid-session ho fatto due errori violazioni REGOLA #1 (verifica fattuale): (a) URL inventato `app-cust.smtp2go.com` SSL handshake fail → corretto a `app.smtp2go.com` ma signup richiede private domain comunque; (b) free tier SMTP2GO claimed "permanente + Gmail signup OK" basato su WebSearch summary non verificato direct su pagina canonica. Pattern: WebSearch summary ≠ doc canonica. Mitigation S294+: SEMPRE WebFetch pagina canonica per claim ESP/pricing/T&C, mai WebSearch summary come fonte autorevole.
- **Vincolo REGOLA #3 violato 2x in S293** → riformulato entrambi con raccomandazione singola motivata dopo hook block. Pattern da memoria-izzare: tabelle comparative con >2 righe + colonna "Verdetto" = lista decisionale anche se solo 1 riga è "WINNER". Future-CTO usa narrativa motivata, non tabella.

### Critica strutturale S293 (REGOLA #4)

1. **Assunzione nascosta CRITICAL**: la proposta success_url + deep-link assume che customer NON chiuda tab pre-copy E che deep-link `fluxion://` funzioni out-of-box su macOS 12+/Windows 10+ Tauri 2.x. Edge case: customer su mobile browser (Stripe Checkout mobile-friendly) → deep-link non esegue Tauri (app non installed) → unrecoverable senza email fallback OR magic-link URL accessibile post-purchase.
2. **30/60/90gg**: Stripe `checkout.sessions.retrieve()` TTL 30 giorni → customer ri-visita success_url dopo 31gg = fail. Mitigation: KV `purchase:{email}` permanent + endpoint alternativo `GET /license/:hmac-token` da founder-shareable manualmente via supporto.
3. **Pattern errore noti**: deep-link scheme conflict (es. altri prodotti con stesso scheme `fluxion://` collisione). Mitigation: scheme univoco `fluxion-app-license://` o `it.gianlucanewtech.fluxion://`.
4. **Sovradimensione**: implementazione ~150 righe worker + tauri-plugin-deep-link + cargo dependency + Tauri config update. Vs status quo (email Resend con dominio €13/yr) = sovradimensione tecnica MOLTO superiore. Trade-off accettabile SOLO se vincolo zero-cost rigoroso prevale strutturalmente vs scope creep.

### Pending S294 (priority order)

| Priority | Task | Owner | Note |
|----------|------|-------|------|
| HIGH | Valutare output Claude.ai web | CTO | Founder incolla risposta Claude.ai → CTO valuta verdetto su 3 sezioni (A/B/C). Se CONFIRMED proposta success_url + deep-link → procedo implement. Se DISPUTED → CTO produce nuova proposta basata su alternative cited. Se NUANCED → CTO richiede chiarimento founder su trade-off specifici. |
| HIGH | Decisione architetturale finale delivery licenza zero-cost | CTO + founder GO | Output Claude.ai = input certificato. CTO produce 1 raccomandazione singola motivata. Founder GO o veto. |
| HIGH | Implementazione path scelto | CTO | Se success_url + deep-link: nuovo route Hono `/success/:session_id` + Stripe Checkout config update + tauri-plugin-deep-link integration + Tauri `lib.rs` listener + vitest + cargo test. Se alternativa: scope da definire post-decisione. |
| HIGH | FDQ-01 prod + FSAF-05 prod + activate-by-payload FE | CTO + founder | META-VINCOLO REGOLA #18 — 3 gate reali letti da Luke prima di `production_ready=True PROD`. |
| MED | KV cleanup test entries | CTO | `wrangler kv key list --binding LICENSE_CACHE --env test` + delete `purchase:test+*`, `session:cs_test_*`, `lead:*`. Riduce noise. |
| MED | `/api/v1/verify` debug endpoint cleanup | CTO | Post Tauri activate-by-payload verified: rimuovere route OR add `Bearer ADMIN_API_SECRET` auth. |
| LOW | Keypair migration macOS Keychain | CTO | Backup locale via `security add-generic-password`. RIMUOVE `~/.claude/.env.s290-*` plaintext. CF Secret resta canonical. |
| LOW | wrangler v4 upgrade | CTO | BLOCKED Big Sur, attesa upgrade macOS o switch dev iMac. |

### Vincoli S294 (non-negoziabili)

- **REGOLA #1 verifica fattuale**: ogni claim ESP/Stripe/Tauri verificato direct su pagina canonica via WebFetch, MAI WebSearch summary come fonte autorevole. Lezione S293 (errore SMTP2GO + Brevo summary non-verified).
- **REGOLA #3 raccomandazione singola**: zero tabelle comparative con colonna "Verdetto", zero liste A/B/C/D anche se mascherate da analisi. Narrativa motivata con dati.
- **REGOLA #4 critica strutturale**: 4 punti obbligatori dopo ogni proposta CTO (assunzioni nascoste, 30/60/90gg, pattern errore noti, sovradimensione).
- **REGOLA #5 zero-cost rigoroso**: confermato S293 — €13/yr dominio NON accettabile. Path scelto deve essere zero-capex, zero-recurring.
- **REGOLA #14/#15/#16 CTO autonomous + research-first**: prima di proposta architetturale, verify su pagina canonica + critica strutturale OBBLIGATORIA.
- **REGOLA #18 META-VINCOLO VALIDATE-THEN-IMPLEMENT**: prima di promote ring VERIFIED PROD, nuovo set 3 gate reali letti da Luke.
- **CLOSING_ONLY soglia ≥70% post system-reminders**: in S294 monitor `/context` ogni 5 tool call, edit file critici BLOCKED sopra 50%.

### Input atteso S294 (founder action)

**Founder**: incollare output Claude.ai web (prompt fornito in S293, conservato sotto in sezione "Prompt verification") nel primo messaggio S294. CTO produce valutazione strutturata:

```
VALUTAZIONE OUTPUT CLAUDE.AI WEB

Sezione A — Vincolo strutturale email senza dominio:
- A.1 Gmail/Yahoo Bulk Sender Requirements Feb 2024 enforce DKIM domain:
  Verdetto Claude.ai: <CONFIRMED|DISPUTED|NUANCED>
  Evidence citate: <count fonti indipendenti>
  CTO judgement: <ACCETTO|RIGETTO + motivazione>
- A.2 ESP free-tier 2026 con DKIM-signed sender DMARC-aligned >85% inbox:
  Verdetto Claude.ai: <...>
- A.3 SMTP2GO Gmail signup block:
  Verdetto Claude.ai: <...>

Sezione B — Path success_url + deep-link Tauri:
- B.1 Stripe success_url template + size limit + scheme restriction
- B.2 stripe.checkout.sessions.retrieve TTL
- B.3 tauri-plugin-deep-link v2.x compatibility macOS 12+/Win10+
- B.4 Recovery flow customer chiude tab

Sezione C — Alternative architetturali non considerate:
- C.1 Pattern license-on-checkout-page SaaS one-time
- C.2 Canali zero-cost production-grade alternativi
- C.3 Self-hosted SMTP iMac residenziale + free DNS subdomain

DECISIONE CTO S294:
- Path scelto: <success_url + deep-link | alternativa Claude.ai | nuova proposta CTO>
- Motivazione singola con dati: <...>
- Critica strutturale 4 punti: <...>
- Procedura operativa: <step CTO autonomous + founder action>
```

### Prompt verification Claude.ai web (riferimento S293)

> Path file fornito in chat S293. Founder ha già copiato. Non duplico inline qui per evitare context bloat.

### Pre-flight S294 (10s)

```bash
# 1. Env vars + keypair S290 ancora persistiti
zsh -c 'for V in CLOUDFLARE_API_TOKEN STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'
ls -la ~/.claude/.env.s290-ed25519-* | wc -l  # 2

# 2. Worker prod/test health
curl -sS https://fluxion-proxy.gianlucanewtech.workers.dev/health
curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health

# 3. Tauri test ancora passa S292
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && cargo test --lib commands::license_ed25519_v1 2>&1 | tail -5"
```

### Carry-over backlog (defer post-S294)

- **FSAF-06..08**: 3DS fail, dual-machine, stolen card (TEST chain)
- **FDQ-02 SCA EU 3DS** (`4000002500003155` browser founder)
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289 Sara auto-start binary client)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** live verify GUI iMac + **BUG-FATT-5** toast z-index
- **Track E** migration 017 license_revoked status enum
- **Track F** force phone-home post Stripe webhook
- **LOGO email template** founder S286 (brand-guardian + visual-storyteller)
- **landing CF Pages re-deploy** post-FBUG-LM-01 S287
- **Migrazione legacy NODE-ED25519 → Ed25519 standard** S291 carry-over

Ripartenza S294 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267 no sintesi inline).
