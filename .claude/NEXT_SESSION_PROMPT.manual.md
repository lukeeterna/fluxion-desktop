# NEXT SESSION — FLUXION — R-01 (S327→S328: VERDE fatto su branch, restano ROSSO + 1 hardening)

> **Stato**: branch `fix/license-interop-r01-s327` contiene TUTTO lo scope VERDE eseguito S327 via
> delegation (backend-architect, context isolato — main Opus bootato a 58% non poteva editare file
> critici inline, REGOLA #25 confermata: MEMORY.md 782 righe bloata il boot in BLOCK_CRITICAL).
> Restano solo confini ROSSO (Luke GO) + 1 hardening sicurezza emerso da research. NON è PARTIAL:
> i 3 task core + A2 + governance sono DONE; il resto è BLOCKED-ON fatti esterni (token/dominio/macOS).

## FATTO S327 (branch fix/license-interop-r01-s327, 4 commit, NON pushato)
- **STEP 0 governance**: `~/.claude/CLAUDE.md` +`### 1c Research-or-escalate` (trigger 2-cicli→escala + self-check lucidatura-vs-E2E). File 221 righe (sopra 200, forma compatta).
- **A2 refund-gate**: gate già in `license-recovery.ts:114-135`. Test 3-rami vitest (null→200/D1, non-JSON→503 fail-closed, `{refunded:true}`→410): **14/14 pass** (commit `5e8da6a`).
- **Task 1**: ASSORBITO da Task 2 (file activate-by-email cancellato → revert response moot).
- **Task 2**: `activate-by-email` RIMOSSO — FE `LicenseManager.tsx` (emailMode/handler/button/import orfani), `src/lib/activate-by-email.ts`, route+import in `index.ts`, `routes/activate-by-email.ts`, `tests/activate-by-email.test.ts`. type-check app+proxy **EXIT=0** (commit `23737c5`).
- **Task 3 EMAIL-EMBED**: già implementato S306/S310 (`stripe-webhook.ts` carica `licensePayload`+`licenseSignature` in `buildEmailHtml`, 3 send path). Corretto copy "Passo 3" stale. proxy suite **37/37 pass** (commit `4d87b66`).

## ASSUNTI ESTERNI — CHIUSI CON RESEARCH (research-fact-checker, fonti ufficiali)
1. **CF KV consistency = CONFIRMED eventually-consistent fino a 60s+** (doc CF "how KV works"). ⇒ il refund-gate A2 KV-only ha **finestra staleness 60s** sfruttabile con timing preciso post-refund. **Mitigazione = fallback D1 (strongly consistent) sul check critico**. Severità: BASSA a lancio (volume basso, finestra stretta) ma da hardenare. **BLOCKED-ON**: `CLOUDFLARE_API_TOKEN` con scope D1 read (ERROR 7403 attuale).
2. **Resend = CONFIRMED**: restrizione `onboarding@resend.dev`→solo owner ancora vigente; consegna a customer reale richiede dominio `status:verified`. `fluxion-app.com` DNS pre-provisioned (S307) ma **BLOCKED-ON**: registrazione CF Registrar + propagazione DNS (Task A S308). Email-embed code è pronto, la consegna reale è bloccata qui.

## DA FARE PROSSIMA SESSIONE
### ROSSO (confine — richiede Luke GO + ambiente)
- **E2E webhook reale**: `wrangler dev` NON gira su MacBook (workerd richiede macOS 13.5+, qui 11.6). → eseguire su **iMac** o CI. Stripe TEST card 4242 → webhook → D1 insert → firma Ed25519 → email Resend che porta la licenza → `activate_license_v1` → `license_cache` popolata → feature attive. Tamper→false. Validator subagent (Opus) sull'evidence PRIMA di Luke.
- **Smoke €1 LIVE** + `wrangler deploy` prod: solo dopo E2E verde su iMac.

### HARDENING (decisione Luke, poi VERDE)
- **A2 D1-fallback**: aggiungere lettura `purchase:{email}` da D1 (source-of-truth) come fallback al check KV nel refund-gate, per chiudere la finestra 60s. PREREQ: token CF con scope D1. Decisione Luke: hardenare ora o accettare rischio basso a lancio?

### MERGE
- Dopo E2E verde: review diff branch `fix/license-interop-r01-s327` (Opus) → merge in `master` → chiude MASTER R-01.

## ACCEPTANCE (stato)
- [x] A2 verificato da test 3-rami verdi (14/14), NON solo tsc.
- [x] Nessun `license_payload`/`license_signature` su endpoint senza HMAC (activate-by-email rimosso).
- [x] `activate-by-email` rimosso; orfano FE migrato; type-check EXIT=0 (app+proxy).
- [x] Assunti esterni #1/#2 chiusi con research (finding KV-staleness documentato).
- [x] Email Resend porta la licenza (code pronto); consegna reale BLOCKED-ON dominio verified.
- [ ] E2E evidence reale G1+G2 → iMac/CI (ROSSO).
- [ ] (opz) A2 D1-fallback hardening → BLOCKED-ON token CF D1.

## NOTA CONTEXT (REGOLA #25)
Boot S327 a 58% (BLOCK_CRITICAL) per MEMORY.md 782 righe/142KB. Karpathy-compile MEMORY.md
(→ COMPILED-STATE.md ≤500 righe) PRIMA della prossima sessione di edit critici, o si ri-boota in BLOCK_CRITICAL.
