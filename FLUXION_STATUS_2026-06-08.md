# FLUXION — STATUS AUDIT 2026-06-08 (READ-ONLY)

> Audit additivo. NON sovrascrive PLAN.md / ROADMAP_REMAINING.md. Nessuna modifica al codice.
> Metodo: 3 sub-agenti read-only (anelli 1-4, anelli 5-8, roadmap) + verifiche dirette del main (wrangler, curl live, git). Ogni stato ha provenienza.
> Tassonomia: ❌ ASSENTE · 📝 SCRITTO_NON_TESTATO · 🧪 TESTATO_LOCALE · 🚀 DEPLOYATO_VERIFICATO

---

## STEP 1 — FONTE DI VERITÀ (cosa la roadmap AFFERMA)

Candidati esistenti:
- `ROADMAP_REMAINING.md` — **roadmap autoritativo** (`riga 1` "ROADMAP AUTORITATIVO (unico)", prodotto S344 2026-06-06).
- `.claude/NEXT_SESSION_PROMPT.manual.md` — carry S356 (8 giu).
- `PLAN.md` — PLAN VOS (ultimo update S320, STATO_FEATURE refresh S308.audit-2).
- `.claude/R01-BIS-GATE-OUTPUT.md`, `PROMPT_CC_SESSIONE_R01.md`, `NEXT_SESSION_PROMPT_R01-TER.md` — dettaglio R-01 (2 giu).
- `HANDOFF.md` — **MANCANTE**.

Cosa la roadmap dichiara:
- **R-01** = problema di **wiring/interop**, NON crypto. Worker firma payload **6 campi (LicensePayloadV1)** chiave V1 senza fingerprint; client legacy verificava **11 campi** chiave legacy + hardware-lock → mismatch → "refund storm" Day-1. (`PROMPT_CC_SESSIONE_R01.md:8-23`, `R01-BIS-GATE-OUTPUT.md:12-19`)
- **Catena licensing**: Stripe→webhook→D1→Ed25519 sign→Resend→activate. Componenti dichiarati funzionanti, ma **E2E pagamento→email→activate live = NO** (`PLAN.md:283`).
- **Deploy Worker**: dichiarato **GIÀ DEPLOYATO** in prod (`PLAN.md:256` version `e18df659`, /health 200; custom domain S342 `ROADMAP_REMAINING.md:13`). Solo il deploy del *fix R-01-ter* è dichiarato BLOCKED-ON (`NEXT_SESSION_PROMPT_R01-TER.md:57`).
- **"token API Cloudflare / scope"** che blocca il deploy: **NON menzionato in nessun file roadmap.** (Esiste solo in MEMORY.md globale REGOLA #20/#21 come incidente storico, risolto a S342 quando il custom domain è andato live.)
- **activate-by-email**: dichiarato **rimosso end-to-end** (commit 23737c5, `NEXT_SESSION_PROMPT_R01-TER.md:11-13`). **split-brain** chiuso. **refund gate** implementato (`license-recovery.ts:107-132`).
- GATE aperti dichiarati: Sara Layer 2 SIP (risolto post-roadmap S355), rami license client gated Keychain GUI iMac, E-3 `STRIPE_SECRET_KEY` mancante su worker prod (refund 503), GATE #1/#2/#3 R-01-bis.
- **"harvesting"**: NON menzionato (termine vicino: "enumeration/esfiltrazione").

---

## STEP 2 — CATENA E2E REVENUE: STATO PER ANELLO

| # | Anello | Stato | Prova |
|---|--------|-------|-------|
| 1 | Stripe checkout | 🚀 config / 🧪 webhook | Payment Links **LIVE** `tools/SalesAgentWA/checkout.py:13-16` (base €497 `buy.stripe.com/8x2…003`, pro €897 `…004`, plink/price LIVE verificati S346 `:11-12`). Webhook firma-verificata `stripe-webhook.ts:576-582`, tier da `amount_total` `:33-36`. Nessuna chiave Stripe hardcoded (grep `sk_live/sk_test`=0); sono secret `wrangler.toml:31,35`. 5 test vitest. **Acquisto reale E2E = NON VERIFICABILE** (nessun log transazione in-repo). |
| 2 | Worker firma Ed25519 6 campi | 🧪 + 🚀 route live | `LicensePayloadV1` = ESATTAMENTE 6 campi `ed25519-sign.ts:126-133` (`kid, license_id, customer_email, product, session_id, issued_at`), canonical order `:160-170`. Firma **unica** in `stripe-webhook.ts:694` (le altre `crypto.subtle.sign` sono HMAC). Struct legacy 11 campi `types.ts:62-74` MAI passata a `signEd25519`. Secret `ED25519_PRIVATE_KEY_PKCS8` `types.ts:12`, fail-loud `stripe-webhook.ts:554-557`. **Endpoint `/api/v1/verify` LIVE** (curl → HTTP 400 "signature_base64 required", non 404). |
| 3 | Consegna Resend | 🧪 (+ smoke prod da MEMORY S342) | `fetch('https://api.resend.com/emails')` `stripe-webhook.ts:202`, from `licenze@fluxion-app.com` `:190`. Payload+firma DAVVERO nel corpo: `licensePayload` `:157`, `licenseSignature` `:159`. Smoke reale msg-id `4b950303…` citato in MEMORY (S342), esterno al repo → in-codice resta 🧪. |
| 4 | activate-by-email | ❌ ASSENTE (rimosso = voluto) | `fluxion-proxy/src/routes/activate-by-email.ts` e `src/lib/activate-by-email.ts` → No such file. Glob `**/*activate*` = 0. `index.ts` non monta route activate. Residui = solo commenti/doc (`stripe-webhook.ts:11,14`, `refund.ts:11`, audit md). |
| 5 | Client Rust verifica firma (CUORE R-01) | 🧪 TESTATO_LOCALE | **ed25519-dalek v2.2.0** (`Cargo.lock:1131`; Cargo.toml:36 dichiara "2"). Verifica V1 `license_ed25519_v1.rs:47-80` `verify_ed25519_signature_dalek` con `VerifyingKey::from_bytes`+`verify_strict` (RFC 8032). Struct **6 campi** `WorkerLicensePayloadV1` `license_ed25519.rs:726-734`, identica al Worker. Comando `activate_license_v1` `:791`, registrato `lib.rs:1155`. 8 unit test interop tra cui `real_worker_signature_verifies_true` con firma reale D1 (`license_ed25519_v1.rs:119-218`). Legacy 11 campi separato (chiave `c61b3c…`, NON nel path Stripe). **File è SU MASTER** (git, da S292/S298 bfc46d8). |
| 6 | Persistenza / split-brain | 🧪 TESTATO_LOCALE | Fonte unica = SQLite `license_cache` via Rust. `grep localStorage + licen/tier/activ` = **0 match**. I 6 usi di localStorage sono flag UI (wizard, banner dismiss, cache phone-home display). Phone-home → SQLite `use-phone-home.ts:106-111` ("authoritative" `:100-103`). **Nessuno split-brain residuo.** |
| 7 | Refund gate (KV) | 📝 SCRITTO_NON_TESTATO | **Asimmetria deliberata**: `license-validate.ts:75-92` (heartbeat runtime) = **FAIL-OPEN** (KV mancante/corrotto → `valid`; solo `refunded===true` → revoked; design "NEVER brick a paying customer"). `license-recovery.ts:117-134` (GET /license/:email) = **FAIL-CLOSED** (corrotto→503, refunded→410). Refund scrive `refunded:true` `refund.ts:350-360`. ⚠️ Il gate runtime principale NON è fail-closed. |
| 8 | Sicurezza GATE #2 (harvesting) | 📝 (codice locale) | `/license/:email` **PROTETTO** HMAC-SHA256 + `constantTimeEqual` + stesso 403 (no enumeration) `license-recovery.ts:52-59,108-112`. ⚠️ `/success/:session_id` `checkout-success.ts:230-288` ritorna payload+firma **senza HMAC** (mitigato da session_id alta entropia, no list-endpoint, ma è l'anello più debole). `/api/v1/verify` non espone licenze (solo `{kid,valid}`). |

---

## STEP 3 — STATO DEPLOY REALE

**Worker DEPLOYATO e LIVE. Il token Cloudflare NON è un blocco. Il "blocco noto" è STALE/risolto.**

- `curl https://fluxion-app.com/health` → **HTTP 200** `{"status":"ok","service":"fluxion-proxy","version":"1.0.0",...}`. Anche `fluxion-proxy.gianlucanewtech.workers.dev/health` → 200.
- `curl -X POST https://fluxion-app.com/api/v1/verify` → **HTTP 400** "payload and signature_base64 required" → route di verifica firma **deployata e viva** (non 404).
- `npx wrangler whoami` → **autenticato**, account `Gianlucanewtech@gmail.com's Account` (`22ddff3a4ef544511523a841b3dcadf8`, lo stesso del prod S342). Token via `CLOUDFLARE_API_TOKEN`.
- **Unica limitazione token**: manca permesso `User → User Details → Read` (whoami non mostra l'email). È **cosmetico**, NON impedisce il deploy del Worker (account + Workers Scripts accessibili: il worker è già live su quell'account). Non è lo scope che bloccava il deploy.

> Nota: NON ho eseguito `wrangler deployments list` perché `timeout` non è disponibile sulla shell e non volevo rischiare un comando che resta appeso; lo stato "deployato" è provato in modo più forte dalle risposte HTTP 200/400 degli endpoint live + whoami autenticato.

---

## STEP 4 — DISCREPANZE ROADMAP vs REALTÀ

| # | Roadmap AFFERMA | Realtà VERIFICATA | Prova |
|---|------------------|--------------------|-------|
| D1 | R-01 vive su branch `fix/license-interop-r01-s327` "NON ancora su master" (`NEXT_SESSION_PROMPT.manual.md:14`) | Il modulo V1 6-campi (`license_ed25519_v1.rs`, `activate_license_v1`) **è GIÀ SU MASTER** dal S292/S298 | `git ls-files` + `git log` bfc46d8/25a5ede su master. Il branch contiene WIP *ulteriore*, non il core verify (che è su master). |
| D2 | "Deploy del fix R-01-ter BLOCKED-ON / deploy live #1 pendente" (`NEXT_SESSION_PROMPT_R01-TER.md:57`) | Worker prod live con route verify/recovery/validate/success attive | curl HTTP 200/400 su `/health` e `/api/v1/verify`. Ambiguità: non determinabile se la versione live includa *tutti* i fix R-01-ter o solo fino a `e18df659` (S313). |
| D3 | (audit prompt) "Worker fermo per errore scope token CF" | Token autenticato, worker live; manca solo `User Details Read` (cosmetico) | `wrangler whoami` OK + endpoint 200. Il blocco token è storia chiusa (S342). |
| D4 | refund gate = fail-closed (implicito nella domanda audit + `E-3` "garanzia operativa") | Gate runtime `license/validate` è **FAIL-OPEN** by design; solo `license/:email` è fail-closed | `license-validate.ts:75-92` vs `license-recovery.ts:117-134`. + E-3 reale: `STRIPE_SECRET_KEY` su worker prod → `refund.ts:202-212` torna 503 se manca (`ROADMAP_REMAINING.md:43`). |
| D5 | GATE #2 "protezione payload+firma" chiuso | `/success/:session_id` espone ancora payload+firma senza HMAC | `checkout-success.ts:230-288`. Per-email è chiuso (HMAC), per-session_id no. |

---

## STEP 5 — IL FATTO TERMINALE

**UN singolo pagamento Stripe reale (anche TEST carta 4242) che attraversa l'INTERA catena una volta, con prova: webhook → firma Ed25519 6-campi → email Resend ricevuta con payload+firma → client Rust `activate_license_v1` verifica `verify_strict` → `license_cache` SQLite popolata → feature sbloccate in UI.**

Oggi ogni anello è verificato **in isolamento** (🧪/route live), ma la catena completa end-to-end **non è MAI stata eseguita una volta** (`PLAN.md:283` "E2E=NO"). Questo è il gate verso il primo `charge_id` reale.

Passi minimi ORDINATI (NON eseguiti):
1. Confermare che la versione del Worker DEPLOYATA includa l'ultimo `stripe-webhook.ts` (firma 6-campi + email) — `wrangler deployments list` e/o diff versione live vs master.
2. Verificare presenza secret sul worker prod: `ED25519_PRIVATE_KEY_PKCS8`, `RESEND_API_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (E-3: senza `STRIPE_SECRET_KEY` il refund path è 503).
3. Eseguire UN pagamento Stripe in TEST mode (4242) sul Payment Link → osservare webhook → email Resend ricevuta con payload+firma.
4. Incollare codice licenza nel wizard FLUXION → `activate_license_v1` → verificare `license_cache` popolata + feature sbloccate (questo step richiede GUI iMac per Keychain, REGOLA #12).
5. Documentare l'esito come prova 🚀 dell'intera catena (primo CLOSED_WON, C-FLUXI-002 `PLAN.md:261`).
6. (Hardening, non bloccante per il primo charge) chiudere D4 (refund gate runtime) e D5 (`/success` senza HMAC).

---

## NON VERIFICATO / NON ACCESSIBILE

- **Acquisto E2E reale completato**: nessun log/output di transazione `charge_id` reale in-repo. Tutti gli anelli sono 🧪 (test) o route-live, nessuno è 🚀 a livello di catena completa.
- **Versione esatta DEPLOYATA del Worker**: non eseguito `wrangler deployments list` (`timeout` assente in shell, evitato comando potenzialmente bloccante). Provato solo che gli endpoint rispondono 200/400 → deployato, ma non quale commit.
- **Secret effettivamente presenti sul worker prod**: referenziati nel codice come secret, ma il loro valore/presenza sul deploy non è ispezionabile read-only senza `wrangler secret list` (non eseguito).
- **Esecuzione test**: nessun `cargo test` / `vitest run` eseguito (audit read-only). I file di test esistono e coprono i path, ma l'output di pass non è stato generato in questa sessione.
- **Smoke Resend S342 / payment rail S331**: citati in MEMORY.md, prove esterne al repo, non re-eseguiti qui.
- **Stato live degli endpoint nella versione deployata vs locale** per anelli 6/7/8: verificato il CODICE locale; la corrispondenza con il deploy non è stata testata endpoint-per-endpoint.
