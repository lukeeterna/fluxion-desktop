# NEXT SESSION — FLUXION — R-01: A2 applicato (compila), costituzione autonomia + 3 task + test comportamento

> Sessione precedente (validazione): A2 refund-gate APPLICATO, compila (tsc EXIT=0).
> NON ancora verificato a runtime — i 3 rami (null/parse-error/refunded) vanno esercitati da un test.
> Chiusa a context 53% (BLOCK_CRITICAL, lezione S185-A: no edit file payment/license sopra 50%).
> I 3 task reali toccano 4+ file security-critical → NON iniziati: vanno fatti a context fresco.
> Branch atteso fix: `fix/license-interop-r01-s327` (ora su `audit/e2e-reality-check-s324`).

## STEP -1 — DELEGAZIONE OBBLIGATORIA (root-cause roadmap lenta — vincolo REGOLA #0 + #16)
> Diagnosi S-R-01 (Luke flag 2026-06-02): VOS impone delega/research/escalation-giudice e NON
> li sto rispettando. 60 sessioni / 4 Task = 98% non-delegation → context bloat → ogni sessione
> nasce a ~60%+ (boot S-R-01 = 66% PRIMA di lavorare) → chiusura forzata → roadmap stallata.

1. **MEMORY.md è 141KB/780 righe → COMPILARE per primo** (pattern Karpathy, CLAUDE.md):
   produci `memory/COMPILED-STATE.md` ≤500 righe, archivia il resto. Senza questo il boot
   riparte già in BLOCK_CRITICAL e la sessione muore di nuovo prima di eseguire.
2. **I 3 task + il test A2 NON si eseguono inline in Opus main context.** Delegare a
   `backend-architect` (subagent, contesto isolato), commit atomici per-task. Main Opus =
   SOLO orchestrazione + review diff + validazione E2E. Il subagent ha contesto fresco → niente S185-A.
3. **Escalation al giudice (Claude AI)** per: classificazione rischio NUOVO + validazione evidence E2E finale.

## STEP 0 — applicare la NUOVA COSTITUZIONE AUTONOMIA (decisione Luke, validazione session)
Sostituisce "L0 ask-always su tutto". Destinazione = **GLOBALE `~/.claude/CLAUDE.md`** (governance
cross-progetto ARGOS/FLUXION/Guardian, vincolo #12). PRIMA verifica budget 200 righe
(`wc -l ~/.claude/CLAUDE.md`): se l'aggiunta sfora, inserire forma compatta o referenziare. Testo:

```
REGOLA AUTONOMIA — gate a due livelli (sostituisce "L0 ask-always su tutto")

VERDE → CC procede DA SOLO, nessuno STOP:
  edit di codice locale reversibili, branch non-merged, nessun deploy,
  nessun invio reale (Stripe live / email / WA), nessuna credenziale toccata.
  Prima di procedere CC applica gli INVARIANTI sotto e fa girare il
  validator subagent (Opus) su se stesso. Logga la decisione, non la chiede.

ROSSO → STOP yes/no Luke (irreversibile/esterno):
  merge su master · wrangler deploy · Stripe LIVE · invio email/WA reale ·
  qualsiasi cosa che tocca prod · O un rischio sicurezza/legale NUOVO non
  coperto dagli invarianti (in dubbio sulla classificazione → ROSSO).

INVARIANTI (CC li applica da solo, non li chiede):
  1. Controllo di sicurezza = FAIL-CLOSED. Dubbio → nega, mai concedi.
  2. Un check legge la STESSA key/fonte che il producer scrive. Grep, non
     fidarti del piano (il piano D1 era cieco: il flag era in KV).
  3. "assente" != "corrotto": rami separati (null→procedi, parse-error→blocca).
  4. Diagnostica/grep PRIMA di modificare. Mai assumere path/schema.
  5. Niente "VERIFIED/ready" senza evidence reale su ciò che conta.
     type-check EXIT=0 != comportamento verificato: serve test che esercita i rami.
  6. Revert/modifica CHIRURGICA: tocca solo le righe del problema.

ESCALATION al giudice (Claude AI) — solo per:
  classificazione di un rischio NUOVO, strategia, e validazione dell'evidence
  E2E finale. NON per diff di codice reversibile.
```
NB context-budget-gate resta ORTOGONALE: VERDE abbassa la soglia di ASK, NON la soglia di
edit-su-file-critici a context degradato (>50% = BLOCK_CRITICAL comunque). Per questo i 3 task
sono rinviati: erano VERDE (reversibili, branch non-merged) ma a 53% l'edit multi-file critico = S185-A.

## STEP 0-bis — creare branch
`git checkout -b fix/license-interop-r01-s327` (da audit/e2e-reality-check-s324).

## APPLICATO ma NON VERIFICATO (validazione session) — completare il test, NON rifare l'edit
**A2 — refund gate in license-recovery.ts**: edit APPLICATO (dopo HMAC :112, prima D1 lookup).
Logica: `null`→fall-through D1, `parse-error`→503 REFUND_CHECK_FAILED (fail-closed), `refunded===true`→410.
Key `purchase:${email}` con `email=emailParam.toLowerCase().trim()` (:100) == refund.ts:262
(`body.email.toLowerCase().trim()`) == stripe-webhook.ts:361 → MATCH grep-verificato 3 punti.
HMAC + constantTimeEqual invariati.
- **Compila**: `tsc --noEmit` EXIT=0 ✓ (solo tipi/sintassi — NON esercita i rami).
- **DA FARE — test comportamento (gate, VERDE)**: vitest unit sul handler recovery che mocka
  `LICENSE_CACHE.get` su 3 casi: (1) null→prosegue al D1 lookup, (2) stringa non-JSON→503,
  (3) `{refunded:true,refunded_at}`→410. Solo con questi 3 verdi A2 è "verificato".

## 3 TASK RIMANENTI (VERDE — fare a context fresco, applicando invarianti, NO ask per edit)

**Task 1 — REVERT esposizione** `fluxion-proxy/src/routes/activate-by-email.ts:124-159`:
rimuovere `license_payload` + `license_signature` dalla response (e dalla query D1 se non più usata).
CHIRURGICO (invariante #6): preserva `activate_license_v1`, `save_license`, routing paste→V1.

**Task 2 — RIMUOVERE `activate-by-email`** (Luke: GO, NO HMAC-dup). Ordine:
- (a) MIGRARE orfano FE: `LicenseManager.tsx` togliere `emailMode` toggle (:354, :415-431),
  `handleEmailActivation` (:359-408), button (:447-454). Resta SOLO path "Codice Licenza"
  (paste→`activate_license_v1`, già ok #4 diagnostica).
- (b) eliminare `src/lib/activate-by-email.ts`.
- (c) togliere route+import in `fluxion-proxy/src/index.ts` (:27 import, :85 route) + cancellare
  handler `routes/activate-by-email.ts` + `tests/activate-by-email.test.ts`.
- (d) `npm run type-check` (app) + `tsc --noEmit` (proxy) EXIT=0.
- Refund downstream: gestito da A2 (gate su license-recovery, da verificare col test sopra).
  refund.ts:350 blocco era SOLO su activate-by-email → rimosso l'endpoint, il path recovery HMAC è quello protetto.

**Task 3 — consegna EMAIL-EMBED**: in `fluxion-proxy/src/routes/stripe-webhook.ts` (cercare invio
Resend) includere `license_payload`+`license_signature` nell'email (single-recipient=owner).
Schema firma INVARIATO. Client legge da email (link recovery o paste) → `activate_license_v1`.

## E2E (gate G1+G2) — path EMAIL-EMBED — confine ROSSO
Stripe **test card 4242** (test mode, VERDE) → webhook → D1 insert → firma Ed25519 → email Resend
CHE PORTA la licenza → client `activate_license_v1` → `license_cache` popolata → feature attive.
Tamper payload → false.
- VERDE: vitest A2 3-rami, `wrangler dev` locale, Stripe TEST, type-check, tamper test.
- ROSSO (STOP per Luke): `wrangler deploy` prod, invio email Resend REALE, smoke €1 LIVE.
- Validator subagent (Opus) sull'evidence E2E PRIMA di passarla a Luke.
- Luke valida l'evidence E2E sul path email → chiude MASTER R-01.

## ACCEPTANCE
- A2 refund gate VERIFICATO da test 3-rami (null/parse-error/refunded) verdi — NON solo tsc.
- Nessun `license_payload`/`license_signature` su endpoint senza HMAC (grep conferma).
- `activate-by-email` rimosso; orfano FE migrato; type-check EXIT=0 (app+proxy).
- Email Resend porta la licenza; attivazione offline; `license_cache` popolata via path email.
- E2E con evidence reale G1+G2. Tamper→false.

## TOKEN CF (carry, non-blocking per i 3 task)
D1 read bloccato `ERROR 7403` → per ri-eseguire #1 (deploy status d46e32f) + #2 (count clienti D1)
serve CLOUDFLARE_API_TOKEN con scope D1 read. Revert (Task 1) procede comunque. Niente credenziali in output.
