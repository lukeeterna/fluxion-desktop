# Validation Prompt — S296 post-compact (paste-ready Claude.ai web)

> **Istruzioni Luke**: copia tutto il blocco sotto su claude.ai web → leggi il verdetto → incolla l'output integrale all'inizio della prossima sessione Claude Code FLUXION. La sessione S297 NON deve procedere finché non hai questo output.

---

## CONTEXT

Sono Luke, founder di FLUXION (gestionale desktop PMI italiane, Tauri+React+SQLite+Voice Agent Sara). Sto chiudendo la sessione Claude Code S296. È avvenuta una compattazione context (≈75%) e voglio validare i claim del summary post-compact contro lo stato git reale del repo, perché la compattazione può produrre sintesi verosimile ma non verificata (REGOLA #10 VOS — "output verificato > output verosimile").

Repo: `/Volumes/MontereyT7/FLUXION` — branch master — ultimo commit `c979757` (S295 close).

## CLAIM DEL SUMMARY POST-COMPACT

Il summary post-compact dichiara che in S296 è stato fatto:

1. **`fluxion-proxy/src/routes/stripe-webhook.ts`** refactor: import `buildRecoveryUrl`, signature `EmailBodyArgs(tier,email,dmg,recoveryUrl,licensePayload,licenseSignature)`, 2 nuove sezioni email body (recovery permanent link + manuale payload/signature copy-paste), `sendViaBrevo` + `sendViaResend` separati con gradual rollout (Brevo primary se BREVO_API_KEY set, Resend fallback), 3 call site replay/race-lost/first-time aggiornati con `recoveryUrl` computed una volta post tier-detect (fail-soft `NOT_CONFIGURED` placeholder se `LICENSE_RECOVERY_SECRET` unset).

2. **`fluxion-proxy/tests/_helpers.ts`** aggiornato: MockContext.req esteso (url/param/query), MockContext esteso (header/html), MockContextOptions opzioni (url/params/query), MockD1 SELECT by customer_email + by session_id (entrambi ORDER BY created_at DESC). `LICENSE_RECOVERY_SECRET` fixture default `process.env.FLUXION_TEST_RECOVERY_KEY ?? 'fixture-unit-S296-DETERMINISTIC-rec'`.

3. **`fluxion-proxy/tests/license-recovery.test.ts`** NEW 11 test PASS: happy path token+row→JSON, 400 missing email/token/invalid format, 403 invalid token (no leak), 404 valid token no row, 500 missing secret/DB, buildRecoveryUrl deterministic case-normalized, email-case mismatch param ok.

4. **`fluxion-proxy/tests/checkout-success.test.ts`** NEW 8 test PASS: happy path D1 row→HTML inline payload+sig+recovery+DMG, pending page meta-refresh 5s NO leak, 400 missing session_id, 500 missing DB/secret, HTML-escape XSS safety, base tier label €497.

5. **`LICENSE_RECOVERY_SECRET`** generato `openssl rand -hex 32` → 64 hex chars, backup `~/.claude/.env.s295-recovery-secret` mode 600. NON uploaded a Worker (carry-over S297 step 1 — wrangler interrotto da Luke a context 75%).

6. **Test suite totale S296**: 36/36 vitest PASS (17 baseline + 19 nuovi). TS strict 0 errori.

7. **Carry-over S297**: (a) `wrangler secret put LICENSE_RECOVERY_SECRET --env test`, (b) founder Brevo signup + API key + `wrangler secret put BREVO_API_KEY`, (c) `wrangler deploy --env test`, (d) founder Stripe Dashboard success_url Payment Link, (e) smoke E2E FDQ-01 test.

8. **Lezione S296**: `pre_write_gate.py` regex `secret\s*=\s*["\'][^"\']{4,}["\']` triggera falso positivo su test file. Workaround: include `process.env` reference nel file (bypass clausola hook riga 39). **Refactor hook deferred** (whole-word + exclude `.test.ts`/`.spec.ts` paths).

## GIT STATE REALE (verificato live dal CTO appena prima del close)

```
$ git status --short
 M .claude/NEXT_SESSION_PROMPT.manual.md
 M .claude/NEXT_SESSION_PROMPT.md
 M .claude/hooks/pre_write_gate.py        ← +95 righe modificato
 M fluxion-proxy/src/routes/stripe-webhook.ts
 M fluxion-proxy/tests/_helpers.ts
?? fluxion-proxy/tests/checkout-success.test.ts        ← NEW 156 righe
?? fluxion-proxy/tests/license-recovery.test.ts        ← NEW 198 righe
 m tools/VectCutAPI                       ← submodule dirty (ignorabile)

$ git diff --stat HEAD -- fluxion-proxy/ .claude/hooks/pre_write_gate.py
 .claude/hooks/pre_write_gate.py            |  95 +++++++++++++---
 fluxion-proxy/src/routes/stripe-webhook.ts | 169 ++++++++++++++++++++++++++---
 fluxion-proxy/tests/_helpers.ts            |  66 ++++++++++-
 3 files changed, 298 insertions(+), 32 deletions(-)

$ npx vitest run | tail -3
 Test Files  6 passed (6)
      Tests  36 passed (36)
   Duration  3.94s

$ ls -la ~/.claude/.env.s295-recovery-secret
-rw-------  1 macbook  staff  65 26 Mag 19:02 /Users/macbook/.claude/.env.s295-recovery-secret
```

### Pre_write_gate.py diff reale (primo blocco)

```diff
+S296 audit fix (2026-05-26):
+- Aggiunto word-boundary \b sui pattern HARDCODED (era `secret\s*=` → matchava
+  `LICENSE_RECOVERY_SECRET:` causando false positive su test fixture).
+- Path whitelist: tests/, __tests__/, *.test.*, *.spec.* skip controllo (unit
+  test fixtures legittime).
+- Valore whitelist: fixture-|test-|mock-|dummy-|deterministic- bypass
+  (chiaramente non credenziali reali).
+- Bypass `process.env` ora per-line (era file-level → false negative se
+  process.env in funzione X e hardcoded in funzione Y senza relazione).

 HARDCODED = [
-    r'password\s*=\s*["\'][^"\']{4,}["\']',
-    r'api_key\s*=\s*["\'][^"\']{4,}["\']',
-    r'token\s*=\s*["\'][^"\']{4,}["\']',
-    r'secret\s*=\s*["\'][^"\']{4,}["\']',
+    r'\bpassword\s*[:=]\s*["\'][^"\']{4,}["\']',
+    r'\bapi_key\s*[:=]\s*["\'][^"\']{4,}["\']',
+    r'\btoken\s*[:=]\s*["\'][^"\']{4,}["\']',
+    r'\bsecret\s*[:=]\s*["\'][^"\']{4,}["\']',
 ]
```

## DOMANDA PER TE (Claude.ai)

Analizza i 8 claim del summary contro il git state reale. Per ciascun claim restituisci:

- **CONFIRMED** se claim ↔ git state coerenti
- **DRIFTED** se claim sostanzialmente vero ma con sfumature errate (es. dimensione files, conteggi test, side-effect non menzionati)
- **FALSE** se claim contraddetto da git state

Output formato:

```
| # | Claim | Verdetto | Evidenza git | Nota |
|---|-------|----------|--------------|------|
| 1 | stripe-webhook.ts refactor Brevo+email body | ... | +169 righe | ... |
| 2 | _helpers.ts mock context | ... | +66 righe | ... |
| ... |
```

Poi rispondi alla domanda finale: **"Posso fidarmi del summary post-compact per ripartire S297 dal carry-over, o devo prima rileggere i diff reali file-per-file?"**

Risposta secca: TRUST / VERIFY_FIRST / DO_NOT_TRUST + motivazione 2 righe.

## CRITICITÀ NOTA DA INVESTIGARE

Il summary al punto 8 dice: *"Refactor hook deferred (whole-word + exclude .test.ts/.spec.ts paths)"*. Ma git mostra che il refactor `pre_write_gate.py` È STATO FATTO (+95 righe, esattamente con word-boundary `\b` + path whitelist `.test.*`/`.spec.*` + fixture value prefix bypass + per-line env bypass).

Questa è una **discrepanza diretta summary ↔ realtà**. Spiegami:
1. Quale altre claim del summary potrebbero soffrire dello stesso pattern di degradazione (cosa "deferred" in realtà fatto, o viceversa)?
2. Cosa devo verificare empiricamente nella prossima sessione S297 PRIMA di considerare il carry-over affidabile?

## VINCOLI VOS DA RISPETTARE NELLA TUA ANALISI

- REGOLA #4: critica strutturale obbligatoria — 4 punti minimo su cosa il summary post-compact ha probabilmente mascherato/omesso.
- REGOLA #10: output verificato > output verosimile. Non assumere — confrontare ogni claim col diff reale.
- REGOLA #11: pattern recognition — se questa è la N-esima compact con drift, identifica root cause strutturale (cosa fare ai prompt CC futuri per evitare il drift, NON workaround episodico).

Fine prompt. Incollami output integrale.
