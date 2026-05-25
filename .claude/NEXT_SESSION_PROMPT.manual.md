# Prompt ripartenza S290 — Worker License Refactor + Activate-by-Email signed Ed25519 (post S289 production_ready=True)

> ## ⚠️ META-VINCOLO S290 (founder-input 2026-05-25) — VALIDATE-THEN-IMPLEMENT OBBLIGATORIO
>
> **PRIMA di dichiarare CHIUSO qualsiasi anello o ring promote VERIFIED in questa sessione, CTO DEVE eseguire il prompt S187 di validazione qui sotto in FASE 1 e FERMARSI per attendere GO Luke. NO production claim senza output reale di test letto da Luke.**
>
> ---
>
> # S187 — FLUXION License Worker (Ed25519) — VALIDATE-THEN-IMPLEMENT
>
> ## VINCOLO METODO (VOS)
> NON implementare subito. FASE 1 = ricerca + validazione, FASE 2 = implementazione
> SOLO dopo che io (Luke) ho letto la tabella di validazione e dato GO.
> Non dichiarare "production ready" senza output reale di test letto da me.
> Time-box ricerca: 30 min. Consegni tabella + raccomandazione singola motivata, NON lista A/B/C.
>
> ---
>
> ## FASE 1 — RICERCA E VALIDAZIONE (fai questo PRIMA, fermati e aspetta mio GO)
>
> Valida con ricerca reale (docs ufficiali Cloudflare + repo GitHub, non README hype)
> le seguenti 6 domande. Per OGNI domanda: fonte + verdetto + 1 riga di evidenza.
>
> 1. **WebCrypto Ed25519 nativa su Workers** — è supportata stabile oggi? L'algoritmo
>    si chiama "Ed25519" o "NODE-ED25519"? Serve flag `compatibility_date`? Fonte:
>    developers.cloudflare.com (usa la versione .md della pagina).
>
> 2. **Firma vs libreria** — la firma nativa basta per il nostro caso (firmare un JSON
>    di licenza)? O ci sono limiti (es. solo verify, non sign)? Se serve fallback,
>    `@noble/ed25519` (MIT, paulmillr) è la scelta più sicura zero-supply-chain? Conferma
>    ultima versione + che giri su Workers senza WASM.
>
> 3. **Verifica offline lato Tauri/Rust** — `ed25519-dalek` (dalek-cryptography) è la
>    libreria Rust audited corretta per verificare la licenza nell'app desktop FLUXION
>    SENZA chiamare il Worker? Conferma versione + licenza + che la firma WebCrypto/noble
>    sia interoperabile con dalek (stesso RFC-8032, stesso formato 64-byte sig).
>
> 4. **Idempotenza webhook Stripe** — qual è il pattern ufficiale Stripe per garantire
>    che un webhook `checkout.session.completed` consegnato 2 volte generi UNA sola
>    licenza? (event.id dedup in KV/D1? `idempotency_key`?) Fonte: docs Stripe.
>
> 5. **Storage stato licenze su Worker** — per il dedup idempotente serve KV o D1?
>    Quale ha consistenza adatta a "non emettere due volte la stessa licenza"?
>    (KV è eventually-consistent — è un rischio per l'idempotenza?) Fonte: docs CF.
>
> 6. **Verifica firma Stripe webhook** — come si verifica `Stripe-Signature` dentro un
>    Worker (constructEventAsync con Web Crypto, non constructEvent sync)? Fonte: docs Stripe.
>
> ### OUTPUT FASE 1 (consegna e FERMATI):
> Tabella: | # | Domanda | Fonte | Verdetto | Evidenza 1 riga |
> + Raccomandazione singola motivata su: (storage KV vs D1) e (firma nativa vs noble).
> + Lista dei rischi idempotenza che hai trovato.
> NON scrivere codice in FASE 1. Aspetta che io legga e dica GO.
>
> ---
>
> ## FASE 2 — IMPLEMENTAZIONE (solo dopo mio GO, usando i verdetti di FASE 1)
>
> Worker FLUXION con questi requisiti idempotenti NON negoziabili:
>
> ### Requisiti di idempotenza (FSAF-05):
> - Webhook `checkout.session.completed` consegnato N volte → ESATTAMENTE 1 licenza,
>   1 email. Dedup su `event.id` (o `payment_intent`) persistito PRIMA di emettere.
> - Se la riga dedup esiste già → ritorna 200 + la licenza già emessa (NON rigenera,
>   NON re-invia email). Operazione safe-to-retry per Stripe.
> - Generazione licenza deterministica per sessione: stessa session_id → stessa licenza
>   (chiave licenza derivata da session_id + payload, non random non-riproducibile).
> - Scrittura stato in transazione/check-and-set atomico per evitare race su doppia
>   consegna simultanea (usa lo storage che FASE 1 ha indicato come consistente).
>
> ### Endpoint:
> - `POST /webhook/stripe` — verifica Stripe-Signature (async), dedup, genera licenza
>   firmata Ed25519, salva, invia email Resend. Idempotente.
> - `POST /verify` (o verifica offline lato Tauri) — verifica firma + scadenza + payload.
>
> ### Sicurezza:
> - Chiave privata Ed25519 SOLO in `wrangler secret`, MAI nel codice/repo/client.
> - Chiave pubblica imbarcata nel client Tauri per verifica offline.
> - Payload licenza firmato include: license_id, product=FLUXION, customer_email,
>   issued_at, expires_at (o perpetua), session_id. Firma copre tutto il payload.
>
> ### Test richiesti (output reale da mostrarmi — FDQ-01 + FSAF-05):
> 1. FDQ-01: card test 4242 → checkout → licenza firmata → email arriva. Mostra log reale.
> 2. FSAF-05: stesso webhook inviato 2x (replay con stripe CLI) → 1 sola licenza in
>    storage, 1 sola email. Mostra il count dallo storage + log che prova il dedup.
> 3. Verifica firma: licenza valida → verify=true; licenza manomessa (1 byte) → verify=false.
>    Mostra entrambi gli output.
>
> ### Credenziali (Luke fornisce a inizio FASE 2):
> Stripe pk_test_/sk_test_, webhook signing secret whsec_, Resend re_, CF token.
> NON committare credenziali. Placeholder commentati nel codice.
>
> ### Consegna FASE 2:
> Codice Worker completo + wrangler.toml + comandi di deploy test + i 3 output di test
> sopra. Gate visivo finale = Luke su log reali. NON dichiari GO production senza i log.

---

## Stato chiusura S289 (CLOSED VERDE, anello #6 VERIFIED + production_ready=True computational)

### Deliverable S289

1. **Anello #6 attivazione_app VERIFIED** via founder GUI iMac (REGOLA #12 S261 Keychain unlock):
   - **FASE 1 CTO autonomous setup pre-founder** (commit `cfe8a55` + `e4a8602`): `VITE_FLUXION_PROXY_URL` build-time env var override in 4 file TS (`src/lib/phone-home.ts:8`, `src/lib/activate-by-email.ts:6`, `src/hooks/use-network-health.ts:8`, `src/vite-env.d.ts`). Default fallback prod = production-safe. Verifica grep `dist/assets/*.js` ritorna SOLO worker test URL post-build con env var, SOLO prod URL post-build senza env var.
   - **FASE 2-A iMac build #1** (founder-present): ssh imac `npm run tauri build` con `VITE_FLUXION_PROXY_URL=...test...` → 17m 06s SUCCESS. Bundle `Fluxion.app` + `Fluxion_1.0.1_x64.dmg` generati. Founder launch app via Finder → Keychain unlock OK → wizard email **NON proposto** (trial cache S+9d 2026-05-16 ancora valido fino 2026-06-15). Founder navigato Settings → License Manager → "Attiva via email" → **FAIL** "Impossibile contattare il server" istant.
   - **FASE 2-B fix root cause** (commit `d9602b8`): `AbortSignal.timeout(ms)` (Safari 16+ only, WebKit Tauri 2.x macOS Monterey support inconsistente) → causava sync throw mascherato come network error. Replace con `AbortController + setTimeout` pattern (universal, già usato in `src/hooks/use-network-health.ts`). 2 file TS modificati (`src/lib/activate-by-email.ts` + `src/lib/phone-home.ts` 3 fetch totali). Error handling migliorato con detail concreto via `console.error` + error message body.
   - **FASE 2-C iMac build #2 post-fix**: ssh imac rebuild → 12m 57s SUCCESS (cargo incremental). Founder relaunch app → Settings → License Manager → "Attiva via email" con `fluxion.gestionale@gmail.com` → **SUCCESS** "Licenza base attivata, riavvia fluxion per applicare".
   - **Evidence KV server-side verified**: `wrangler kv key list` (CF API REST, wrangler v4 incompat Big Sur) → `activation:fluxion.gestionale@gmail.com` = `{email, tier:base, activated_at:2026-05-25T14:41:29.314Z, purchase_date:2026-05-23T18:31:36.060Z}`.

2. **Architectural clarification documentata in gate-state**: il flusso `activate-by-email` è "no codes, no keys, no files" by-design (commento `fluxion-proxy/src/routes/activate-by-email.ts:1-4`). Persistenza primaria = **localStorage FE** + **KV worker server-side**. SQLite `license_cache` Tauri è usato SOLO dal flusso legacy Ed25519 manual JSON-paste (`LicenseManager.tsx` textarea riga 460 "Incolla qui il codice licenza JSON..."). Il criteria prompt S289 originale `SELECT * FROM license_cache` era **mismatch architetturale**, corretto con evidence_kv_server_side in gate-state.

3. **Production_ready computation = True**:
   ```
   required_rings VERIFIED: [2_checkout_stripe, 3_pagamento_confermato, 4_licenza_generata, 5_email_consegna, 6_attivazione_app] → all_verified=True
   safety_suite passed: 6/8 (>= 6 target) → safety_ok=True
   data_quality_suite passed: 3/4 (>= 3 target) → dq_ok=True
   production_ready = all_verified AND safety_ok AND dq_ok = True
   ```
   Promosso in gate-state `production_ready: true`, `production_ready_promoted_at: 2026-05-25T14:55:00Z`, `production_ready_promotion_session: S289`. Rings 1 (top-funnel marketing optional VERIFIED S287) + 7 (Phase 12 sales agent WA out-of-gate) NON blocking per criteria definition S287.

4. **Track-B FDQ-02 SCA EU 3DS SKIP** in questa sessione (founder browser challenge required + scope ridotto per close S289). Da pianificare S291 (data_quality 4/4 bonus, non blocking).

### Backlog NUOVO S289

- **BACKLOG-ACTIVATE-BY-EMAIL-SIGNED-ED25519** severity HIGH (architectural): worker `activate-by-email` lightweight (no signing) → migrare a flusso end-to-end Ed25519 signed compatibile con Rust `activate_license_ed25519` + SQLite `license_cache` persistence. Richiede: (1) worker `signEd25519()` lib (attualmente solo verify in `fluxion-proxy/src/lib/ed25519.ts`), (2) `ED25519_PRIVATE_KEY` wrangler secret generazione + setup, (3) handshake fingerprint client→server, (4) FE `activate_license_ed25519` invocation post worker response, (5) Resend email embed `license_data` JSON copiabile.
  **Applicare il prompt S187 VALIDATE-THEN-IMPLEMENT obbligatorio** (vedi header sessione) PRIMA di refactor — FASE 1 ricerca 6 domande WebCrypto/storage/idempotenza, FASE 2 implementazione solo post GO Luke.
- **BACKLOG-VOICE-SIDECAR-BUNDLE** severity HIGH (UX cliente): PyInstaller build `voice-agent/voice-agent.spec` → `dist/voice-agent` → copy `src-tauri/binaries/voice-agent-x86_64-apple-darwin` (Tauri sidecar target triple) → re-build Tauri. `tauri.conf.json` `externalBin: ["binaries/voice-agent"]` già configurato. Necessario per evitare che cliente PMI debba aprire terminal per `cd voice-agent && python main.py`.

### Vincoli S290 (non-negoziabili)

- **MAI dichiarare anello CHIUSO o promote VERIFIED senza prima eseguire prompt S187 FASE 1 + GO Luke esplicito** (META-VINCOLO header).
- **MAI stampare valori chiavi** — SOLO SET/UNSET booleano.
- **NO mock** su test E2E. Endpoint reali (Stripe TEST CLI + KV worker test + Resend test inbox).
- **Output incollato per ogni step**, no claim "ready" senza output letto da Luke.
- **REGOLA #12** (S261): Keychain unlock GUI founder-present per qualsiasi flow signing offline lato Tauri.
- **REGOLA #14/#15**: CTO autonomous tutto eccetto fisical iMac + browser founder.
- **REGOLA #16**: research-first prima di qualsiasi proposta tecnica (WebSearch/WebFetch docs ufficiali Cloudflare/Stripe/Resend, no README hype, no training-data guess).

### Pre-flight S290 (10s)

```bash
zsh -c 'for V in CF_API_TOKEN STRIPE_TEST_SECRET_KEY STRIPE_TEST_PUBLISHABLE_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST CLOUDFLARE_API_TOKEN STRIPE_API_KEY; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'
ssh imac "lsof -i :3001 -i :3002 2>/dev/null | head -5"
curl -sI https://fluxion-proxy-test.gianlucanewtech.workers.dev/health | head -2
```

Atteso: 7/7 SET, iMac status, worker test 200.

### Carry-over backlog (defer post-S290)

- **FSAF-06..08**: 3DS challenge fail, dual-machine activation (richiede 2 device fisici), stolen card variants
- **FDQ-02 SCA EU 3DS**: card `4000002500003155` (founder browser challenge required)
- **BACKLOG-DISPUTE-ALERT** (S288): admin Resend notification su `charge.dispute.created`
- **BACKLOG-DISPUTE-AUTO-REVOKE** (S288): auto KV `refunded=true` su `charge.dispute.closed` status=lost
- **Anello #7 sales agent WA**: Phase 12 (out-of-gate)
- **BUG-FATT-3** live verify GUI iMac founder-present (S276)
- **BUG-FATT-5** toast z-index globale
- **Track E** migration 017 license_revoked status enum CHECK
- **Track F** force phone-home post Stripe webhook
- **Resend custom domain** decisione strategica
- **LOGO email template** founder S286 input
- **wrangler v4 upgrade** (BLOCKED Big Sur: macOS 13.5+ required)
- **KV cleanup S285+S286+S287+S289 test entries**
- **landing CF Pages re-deploy** post-FBUG-LM-01

### Files modificati S289 da committare (atomic)

- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file) — S290 scope + S187 META-VINCOLO embedded
- `.claude/NEXT_SESSION_PROMPT.md` — auto-generated update
- `src/lib/activate-by-email.ts` — fix AbortSignal.timeout WebKit Tauri compat (commit `d9602b8` già pushato)
- `src/lib/phone-home.ts` — fix idem (commit `d9602b8` già pushato)

Già committati S289 pre-close:
- `cfe8a55` — Vite env var VITE_FLUXION_PROXY_URL build-time override
- `e4a8602` — extend override to use-network-health
- `7e54297` — NEXT_SESSION_PROMPT.manual.md FASE 1 done documented
- `d9602b8` — fix AbortSignal.timeout WebKit Tauri 2.x compat

Fuori repo FLUXION (NO commit):
- `~/venture-os/state/gate-state-FLUXION.json` — anello #6 VERIFIED + production_ready=True + s289_verification evidence block + production_ready_meta_validation_pending nota S187

Atteso post-Stop S289: 1 commit atomic con files sopra. NEXT_SESSION_PROMPT.manual.md è prompt ripartenza per S290 (path completo `.claude/NEXT_SESSION_PROMPT.manual.md`, MAI sintesi inline REGOLA #13 S267).
