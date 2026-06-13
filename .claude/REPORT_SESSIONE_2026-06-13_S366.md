# FLUXION — REPORT COMPLETO DI SESSIONE — S366 — 2026-06-13

> Ruoli: **Claude = CTO/firewall/critico esterno** · **CC = esecutore** Mac+Windows via SSH · **Luke = founder** (firma gate esterni, tocchi GUI).
> Vincoli attivi: WIP=1, anti-falso-verde, dati-first, italiano, €0.
> Ordine VINCOLANTE (verdetto giudice S365, 4-QUATER): **A→Z PRIMA, R1 SOSPESO.**

---

## 1. OBIETTIVO DELLA SESSIONE
Eseguire l'ordine vincolante del verdetto S365 partendo da:
- **Step 0** — backup off-site dei 3 repo (T7 già caduto una volta → rischio reale).
- **Step 1** — 3 fix onboarding (Parte C), headless €0, che bloccano un non-tecnico al primo avvio.

Gate (c) CHARGE E2E = **GIÀ CHIUSO S365**, non riaperto.

---

## 2. COSA È STATO FATTO — con evidenze E2E

### ✅ STEP 0 — Backup off-site (CHIUSO)
Trovato gap reale: FLUXION aveva 64 commit non pushati. ARGOS/venture-os risultavano "ahead" ma per ref locali stale.

**EVIDENZA (output reale):**
```
FLUXION:   git push origin master  →  0ec4d1b..2973d38  master -> master   (64 commit off-site)
venture-os: ahead of github/master = 0                                     (già off-site)
ARGOS:     git push origin master  →  Everything up-to-date                (già off-site; "224 ahead" era ref stale)
```
Verifica anti-falso-verde: fidarsi dell'esito `git push` (contatta il remote), NON del `rev-list` su ref locale stale.

### ✅ STEP 1 / FIX #1 — Copy `checkout-success.ts` Passo 2 (CHIUSO codice)
**Problema (R-01):** la pagina post-pagamento istruiva "inserisci email → FLUXION verifica automaticamente". Quel path è **rimosso** (`LicenseManager.tsx:337`). L'app reale attiva SOLO via link recupero (Passo 3) o paste/upload del payload firmato → un cliente vero cerca un campo email inesistente e si blocca al Day 1.

**Fix:** riscritto Passo 2 sulla sequenza GUI reale verificata S364 (Impostazioni → "Il tuo piano FLUXION" → "Hai già una licenza? Attivala" → carica/incolla → "Attiva Licenza"). Passo 3 promosso a `primary` come fonte del file licenza.

**EVIDENZA:**
```
File:   fluxion-proxy/src/routes/checkout-success.ts  (righe 159-176)
tsc:    npx tsc --noEmit -p tsconfig.json  →  EXIT=0
commit: aa01a92  →  push 2973d38..aa01a92
```

### ✅ STEP 1 / FIX #2 + #3 — `SetupWizard.tsx` (CHIUSO codice)
Delegato a subagent `frontend-developer` (context isolato, REGOLA #0); diff verificato dal main (trust-but-verify).

**Fix #2 — riepilogo errori al submit:** la validazione P.IVA `.length(11)` mostrava errori solo inline, invisibili al click "Avvia FLUXION" → submit bloccato in silenzio. Aggiunto:
- `onInvalid` → `toast.error('Controlla i campi evidenziati…')`
- `handleSubmit(onSubmit, onInvalid)`
- error-box rossa prominente allo step finale (`data-testid="setup-validation-error-summary"`) che elenca i campi in errore
- `toast.error` nel catch di `onSubmit` (prima era solo `console.error` — gap UX noto REGOLA #258)

**Fix #3 — dropdown step 6:** i due `SelectContent` (categoria/regime) ribaltavano verso l'alto sovrapponendosi → `side="bottom" avoidCollisions={false}` + `data-testid` sui trigger.

**EVIDENZA:**
```
File:   src/components/setup/SetupWizard.tsx
diff:   verificato dal main (git diff) — corrisponde al report agente, nessuna sorpresa
tsc:    npx tsc --noEmit  →  EXIT=0  (verificato in autonomia dal main, non solo report agente)
commit: 2710ba3  →  push aa01a92..2710ba3
```

---

## 3. ONESTÀ SULLA VERIFICA (REGOLA #24 — anti-falso-verde)
`tsc=0` = **"compila"**, NON "comportamento verificato". Le done-condition reali sono **APERTE** e **founder-gated**:

| Fix | E2E reale richiesto | Chi/come |
|-----|---------------------|----------|
| #1 worker | `wrangler deploy` + `curl /success/:session_id` (session_id reale in D1) → HTML renderizzato corretto | deploy su PROD (serve OK founder) |
| #2/#3 app | build Tauri iMac → reinstall Windows → walkthrough nativo wizard | founder fisico su Windows |

**Done-condition §3b verdetto:** VERDE solo quando un non-tecnico completa il ciclo wizard su Windows nativo con ZERO inciampi BLOCCANTI. NON marcabile come chiuso senza walkthrough.

---

## 4. STATO STRUTTURALE (invariato, non riaperto)
- 🟢🟢 **Gate (c) CHARGE E2E — CHIUSO S365.** Ultimo ignoto strutturale Pila 1 risolto. NON riaprire.
- 🟢 **Sara viva** su `0972536918@sip.vivavox.it` (`reg_status:200`). Pipeline 3002 UP, 3001 DOWN (non blocca onboarding).
- 🟢 **Windows app gira** (WebView2 v149), attivazione licenza reale verificata alla fonte.

---

## 5. EVIDENZE — riepilogo comandi/commit della sessione
```
push 1:  FLUXION 0ec4d1b..2973d38   (step 0 backup, 64 commit)
push 2:  FLUXION 2973d38..aa01a92   (fix #1 checkout copy)
push 3:  FLUXION aa01a92..2710ba3   (fix #2+#3 wizard)
tsc:     fluxion-proxy  EXIT=0
tsc:     app (root)     EXIT=0
ARGOS / venture-os: già off-site (nessun commit perso)
```
Nota: un hook di sessione rimaneggia/ri-staga `.claude/NEXT_SESSION_PROMPT.md` → finisce nei commit insieme al codice. Innocuo; i fix di codice sono isolati e corretti.

---

## 6. NEXT SESSION PROMPT — S367 (azionabile)

> Carry canonico completo: `.claude/NEXT_SESSION_PROMPT.manual.md` (verdetto 4-QUATER vincolante).
> Questo è il delta operativo S366→S367.

**PRECONDIZIONE GIÀ FATTA:** backup off-site OK (step 0 chiuso).

**STATO STEP 1:** codice dei 3 fix onboarding CHIUSO + pushato (aa01a92, 2710ba3), tsc 0. **Manca solo la verifica E2E founder-gated.**

**ORDINE S367 (vincolante, da verdetto):**
1. **Verificare Step 1 (chiudere la done-condition):**
   - **fix #1:** deploy worker `cd fluxion-proxy && npx wrangler deploy` → `curl https://fluxion-app.com/success/<session_id_reale_in_D1>` → controllare che l'HTML del Passo 2 mostri la nuova sequenza (recovery-link/paste), NON il vecchio "inserisci email". [serve OK founder: prod]
   - **fix #2/#3:** build app su iMac (via SSH) → founder reinstalla su Windows → walkthrough wizard: (a) P.IVA errata → step finale → click "Avvia FLUXION" → error-box rossa + toast visibili; (b) step 6 → aprire i due Select → nessuna sovrapposizione. Solo allora Step 1 = VERDE.
2. **Step 2 — slice "gestione clienti perfetta"** (done-condition CRUD-E2E-zero-bloccanti su Windows nativo: crea cliente con tutti i campi/validazioni P.IVA → cerca/filtra → modifica → associa azione verticale → archivia/elimina con conferma).
3. **Step 3 — guardrail Sara TESTUALI ORA** headless via `POST /api/voice/process` (G1 prompt-injection, G4 mai-negare-di-essere-bot, G5/I3/I4 privacy-GDPR). Pipeline 3002 è UP. Audio reale per ciò che è solo-audio. **Sara tutti-i-verticali su chiamata reale = HARD-GATE pre-vendita** (declassamento RESPINTO dal giudice).
4. **R1 SOSPESO** finché onboarding VERDE + confermato che cold-outreach WA non è illegale.

**RESTART CMD suggerito S367:**
```
ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"   # verifica Sara
# poi: deploy worker + curl (fix #1) OPPURE build iMac per walkthrough (fix #2/#3)
```

**DATO DISPUTED (firewall):** "205 lead / reply 60%" (roadmap riga 23) è smentito dal founder. NON usarlo come evidenza.

---

## 7. DECISIONE APERTA PER IL FOUNDER
**Confermi il deploy del worker `fluxion-proxy` su produzione** (per verificare fix #1 via curl)? È stato condiviso → chiedo OK prima di toccarlo. La build iMac per fix #2/#3 è reversibile e non tocca prod.
