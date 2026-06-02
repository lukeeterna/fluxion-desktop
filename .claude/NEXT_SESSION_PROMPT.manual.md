# NEXT SESSION — FLUXION — R-01 (V2: research-or-escalate, orientata E2E)

> **Obiettivo sessione = avanzare verso PRODUCTION TESTATA E2E del path acquisto** (€497/€897).
> NON micro-perfezionare. A2 refund-gate è APPLICATO + compila; restano **3 task core + E2E** = le
> uniche cose che producono production testata. Diagnosi S-R-01 (Luke): l'avvitamento — 5 STOP su un
> singolo catch (grep→diff→fail-closed→type-check→checkpoint) — è moto senza avanzamento. La research
> serve a TAGLIARE i loop; se non taglia, non viene usata.
> Branch fix: creare `fix/license-interop-r01-s327` da `audit/e2e-reality-check-s324`.

## STEP 0 — ESTENDERE la governance anti-avvitamento in `~/.claude/CLAUDE.md` (GLOBALE, FILE CRITICO)
> NB V2: CLAUDE.md ha GIÀ `REGOLA #1b` (done-condition esterna + raggiungibile, BLOCKED-ON, no
> re-validazione statica) — copre metà. **Manca solo il trigger esplicito sotto** (2-cicli→escala +
> self-check). NON duplicare #1b: aggiungi solo i TRIGGER come complemento, o referenzia #1b.
Farlo **a context FRESCO (<40%)** — è edit su file critico (BLOCK_CRITICAL >50%, lezione S185-A).
Verifica budget 200 righe (`wc -l ~/.claude/CLAUDE.md`); se sfora → forma compatta o referenzia. Testo:

```
REGOLA ANTI-AVVITAMENTO (research-or-escalate, orientata a E2E)

Obiettivo di ogni sessione = avanzare verso production testata E2E.
Micro-perfezionare un dettaglio mentre i task core non partono = fallimento,
anche se ogni micro-passo è corretto.

TRIGGER research/escalation (obbligatorio, non opzionale):
- Se una decisione dipende dal comportamento di una piattaforma ESTERNA
  (Cloudflare KV/D1 consistency, webhook Stripe, Resend, Tauri, pjsip...)
  → research doc ufficiale e CHIUDI il dubbio in un colpo. Non procedere
  per assunto, non procedere a tentativi.
- Se dopo 2 cicli sullo STESSO punto non è chiuso → STOP avvitamento,
  scrivi un prompt per Claude AI (giudice) e passa al task successivo
  mentre aspetti. Non fare un 3° ciclo da solo.
- Self-check prima di ogni STOP: "questo blocca la strada verso l'E2E,
  o sto lucidando un dettaglio?" Se è lucidatura → non fermarti, procedi
  con l'invariante e logga.

ASSUNTI ESTERNI = DEBITO: ogni "do per scontato che la piattaforma X faccia Y"
non verificato va marcato [ASSUNTO-NON-VERIFICATO] e chiuso con research
PRIMA dell'E2E, non dopo.

NB: lo stop-su-context-degradato (no edit file payment/license >50%) NON è
avvitamento — è invariante sano che protegge la strada verso l'E2E. Tenerlo.
```

## STEP 0-bis — governance esecuzione (correzione sovra-vincolo S-R-01)
- **Delegation-first (REGOLA #0) = VALUTA, non impone l'esecutore.** I 3 task sono multi-file → valuta
  delega a subagent engineering O inline se single edit chirurgico. NON è obbligatorio `backend-architect`
  (era mio sovra-vincolo). Scegli e **documenta** la scelta, non chiederla.
- **Research-or-escalate** attivo su ogni dubbio piattaforma esterna (vedi ASSUNTI sotto).
- **Self-check ad ogni stop**: "blocca la strada verso E2E o sto lucidando?" → lucidatura = procedi+logga.

## STEP 1 — branch
`git checkout -b fix/license-interop-r01-s327` (da `audit/e2e-reality-check-s324`).

## A2 — refund gate in `license-recovery.ts`: APPLICATO + compila, DA VERIFICARE (non rifare l'edit)
Edit già applicato (dopo HMAC :112, prima D1 lookup). Logica: `null`→fall-through D1,
`parse-error`→503 REFUND_CHECK_FAILED (fail-closed), `refunded===true`→410. Key `purchase:${email}`
con `email=emailParam.toLowerCase().trim()` (:100) == refund.ts:262 == stripe-webhook.ts:361 (grep 3 punti).
- Compila (`tsc --noEmit` EXIT=0) ✓ — NON esercita i rami (REGOLA #24: tsc ≠ comportamento).
- **DA FARE — test 3-rami (VERDE)**: vitest unit sul handler recovery, mock `LICENSE_CACHE.get`:
  (1) null→prosegue D1, (2) stringa non-JSON→503, (3) `{refunded:true}`→410. Solo coi 3 verdi A2 è verificato.

## 3 TASK CORE (VERDE — sono questi che producono production testata, NON l'A2-polish)
**Task 1 — REVERT esposizione** `fluxion-proxy/src/routes/activate-by-email.ts:124-159`: rimuovere
`license_payload`+`license_signature` dalla response (e dalla query D1 se non più usata). CHIRURGICO:
preserva `activate_license_v1`, `save_license`, routing paste→V1.

**Task 2 — RIMUOVERE `activate-by-email`** (Luke GO, NO HMAC-dup):
- (a) MIGRARE orfano FE `LicenseManager.tsx`: togliere `emailMode` toggle (:354, :415-431),
  `handleEmailActivation` (:359-408), button (:447-454). Resta SOLO path "Codice Licenza" (paste→`activate_license_v1`).
- (b) eliminare `src/lib/activate-by-email.ts`.
- (c) togliere route+import in `fluxion-proxy/src/index.ts` (:27 import, :85 route) + cancellare
  `routes/activate-by-email.ts` + `tests/activate-by-email.test.ts`.
- (d) `npm run type-check` (app) + `tsc --noEmit` (proxy) EXIT=0.
- Refund downstream: gestito da A2 (gate su license-recovery). refund.ts:350 era SOLO su activate-by-email.

**Task 3 — consegna EMAIL-EMBED**: in `stripe-webhook.ts` (cercare invio Resend) includere
`license_payload`+`license_signature` nell'email (single-recipient=owner). Schema firma INVARIATO.
Client legge da email (link recovery o paste) → `activate_license_v1`.

## ASSUNTI ESTERNI DA CHIUDERE CON RESEARCH *PRIMA* DELL'E2E (debito [ASSUNTO-NON-VERIFICATO])
1. **CF KV consistency**: `purchase:{email}` è eventually-consistent? → doc ufficiale CF KV. Decidi se la
   finestra di staleness sul refund-gate è accettabile. Chiudi in un colpo, non per tentativi.
2. **Resend single-recipient owner** (FBUG-RESEND-SHARED-SENDER-01): ancora valido per email-embed Task 3?
   Verifica stato dominio Resend prima di assumere che l'email arrivi al customer.
3. Se uno di questi resta aperto dopo 2 cicli → prompt al giudice (Claude AI) + procedi su altro task.

## E2E (gate G1+G2) — path EMAIL-EMBED — confine ROSSO
Stripe **test card 4242** (test mode, VERDE) → webhook → D1 insert → firma Ed25519 → email Resend CHE
PORTA la licenza → client `activate_license_v1` → `license_cache` popolata → feature attive. Tamper→false.
- VERDE: vitest A2 3-rami, `wrangler dev` locale, Stripe TEST, type-check, tamper test.
- ROSSO (STOP per Luke): `wrangler deploy` prod, invio email Resend REALE, smoke €1 LIVE.
- Validator subagent (Opus) sull'evidence E2E PRIMA di passarla a Luke. Luke valida → chiude MASTER R-01.

## ACCEPTANCE
- A2 refund gate VERIFICATO da test 3-rami verdi (NON solo tsc).
- Nessun `license_payload`/`license_signature` su endpoint senza HMAC (grep conferma).
- `activate-by-email` rimosso; orfano FE migrato; type-check EXIT=0 (app+proxy).
- Assunti esterni #1/#2 chiusi con research (no [ASSUNTO-NON-VERIFICATO] residui).
- Email Resend porta la licenza; attivazione offline; `license_cache` popolata via path email.
- E2E con evidence reale G1+G2. Tamper→false.

## TOKEN CF (carry, non-blocking per i 3 task)
D1 read bloccato `ERROR 7403` → per #1 (deploy status d46e32f) + #2 (count clienti D1) serve
CLOUDFLARE_API_TOKEN con scope D1 read. Revert (Task 1) procede comunque. Niente credenziali in output.
