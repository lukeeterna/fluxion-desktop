# FLUXION — NEXT SESSION PROMPT — S369 · TEST PIPELINE REALE E2E (charge €1, mail secondaria founder)
> Ruoli: **Claude = CTO/firewall/critico** (no filesystem, verifica claim alla fonte) · **CC = esecutore** Mac+Windows via SSH · **Luke = founder**, firma i gate esterni (HITL), fa il giro fisico.
> Vincoli: **WIP=1**, **anti-falso-verde**, dati-first, italiano, €0 netto. NESSUN atto irreversibile prima di G-APPROVAL founder.

---

## ⚠️ REGOLA #30 (S368) — IL CARRY NON È FONTE DI VERITÀ
Prima di proporre QUALSIASI fix/task come "da fare": `git show --stat <commit>` + grep del marker nel source. Il commit batte il doc. Falso-verde ricorrente S366+S368: 3 fix onboarding riproposti come TODO mentre erano già committati. NON ricascarci.

## 0. STATO REALE VERIFICATO ALLA FONTE (S368) — niente è "da scrivere"
Tutto il codice headless €0 è scritto. Restano solo gate live (walkthrough/charge), non di CC.
- 🟢 **3 fix onboarding Parte C — CODICE COMPLETO, NON-VERDE** (manca walkthrough nativo):
  - #1 copy post-pagamento `fluxion-proxy/src/routes/checkout-success.ts:163` → recovery-link/paste (auto-verify-email rimosso). Commit `aa01a92`.
  - #2 riepilogo errori wizard `src/components/setup/SetupWizard.tsx:129-130,182` → `onInvalid`→`toast.error`. Commit `2710ba3`.
  - #3 dropdown no-overlap `SetupWizard.tsx:493,512` → `<SelectContent side="bottom" avoidCollisions={false}>`. Commit `2710ba3`.
- 🟢 **B1 ciclo cliente — CODICE COMPLETO, NON-VERDE**: `src/components/clienti/ClienteForm.tsx:148` `handleSubmit(handleSubmit, handleInvalid)` → `toast.error('Controlla i campi del modulo')` (riga 137). Commit `0232090`.
- 🟢 **Audit clienti** (`.claude/AUDIT_crea_cliente_S367.md`): fatto, falsi positivi respinti, nota verbale S368.
- 🟢 **(c) charge E2E continuity**: CHIUSA S365 (license_cache id=1 delta verificato). NON riaprire.

---

## GATE ATTIVO S369 — pipeline cliente completa come UNICO flusso reale
Chiude insieme i 2 🔴 aperti (attivazione default email→recovery mai girata live + deliverability mail-licenza) e valida onboarding #1/#2/#3 + B1 + CRUD nel contesto reale. Founder compra dalla landing con **mail secondaria fresca**, charge €1, percorre install+wizard come cliente vero.

### 🟢 PRIMO ATTO S369 = #0.a (read-only, NO G-APPROVAL, esegui subito) — l'acquisto è IPOTETICO finché la modalità Stripe è ignota
S369 NON apre col prompt-acquisto. Apre con due verifiche read-only nello stesso giro (zero atti irreversibili):
1. **Localizza il checkout della landing servita in prod** — quale URL è il checkout reale (`combaretrovamiauto.pages.dev` / `fluxion-landing.pages.dev` / altro)? Payment Link statico o `checkout.sessions.create`? Modalità **`cs_live` o `cs_test`**? Con fonte. Se landing in repo/Pages separato → localizzarlo prima; se irraggiungibile → `BLOCKED-ON`.
2. **GAP 3** — grep che la mail licenza/recovery del path webhook usi lo stesso from verificato `licenze@fluxion-app.com` (S342). Riporta file:riga.

**Esito gate:** `cs_live` confermato → il prompt-acquisto va al G-APPROVAL (con GAP 2 attiva-poi-rimborsa integrato). `cs_test` → **STOP**, riconfigurare su €1 reale prima di procedere (falso-verde §2.3).

### VERIFICA #0 (PRIMA DI TUTTO — è il punto dove il test muore se sbagliato)
- **#0.a LOCALIZZA il checkout della landing servita in prod** (GAP S368): il worker `fluxion-proxy` NON crea il checkout (solo `stripe-webhook.ts`+`refund.ts`, zero `checkout.sessions.create`). Prezzo+modalità live/test stanno LATO LANDING, **non trovata in repo** (`fluxion-landing`/`landing` → 0 match) → potrebbe essere repo/Pages separato. Trovare la definizione e leggere link/chiave.
- **#0.b cs_live vs cs_test**: se è **Payment Link statico** (`buy.stripe.com/...`), la modalità è INCISA nel link → "deploy worker" NON la cambia. Riporta quale dei due, con fonte. **Se cs_test_ → FERMATI**: è il falso-verde §2.3 (metà test/live mai congiunte), il test non vale. Solo `cs_live_` prova la catena reale.

### PRECONDIZIONI (read-only alla fonte, riportare PRIMA che il founder paghi)
1. Prezzo reale landing = €1 (config) + checkout → `cs_live` reale (#0).
2. **From mail licenza** (path webhook) = stesso dominio verificato della refund-mail `licenze@fluxion-app.com` (`refund.ts:185`, dominio fluxion-app.com verificato S342). Se diverge/non-verificato → anello 3 deliverability fallisce per ragione finta. 1 grep su `stripe-webhook.ts`.
3. D1 prod `fluxion-webhook-events` raggiungibile; chiavi Stripe live presenti (cred MAI in chat).
4. Mail secondaria: casella **apribile** dal founder (la deliverability è il punto), fresca, non legata a licenze esistenti.

### PRECONDIZIONE DEPLOY (gate a sé, G-APPROVAL)
`npx wrangler deploy` di `fluxion-proxy` (delega `devops-automator`) — altrimenti la pagina post-pagamento serve copy vecchio e onboarding #1 fallisce per ragione finta. PRIMA: `git diff` prod↔locale per confermare che il deploy porta SOLO il copy Passo 2 di `checkout-success.ts`, nulla di divergente. Riporta range/hash, non "deploy OK".

### ⚠️ SEQUENCING OBBLIGATORIO (GAP S368 — refund vs recovery)
`license-recovery.ts:128-131` è **fail-CLOSED 410** se `refunded===true`. Sul €1 fresco il founder DEVE **ricevere mail + attivare via recovery/payload PRIMA di rimborsare**. Se rimborsa prima → anello 5 (default-path) si blocca per ragione finta. **Ordine: attiva-POI-rimborsa.**

### CLAUSOLA 1 — fatto terminale leg-by-leg, solo OSSERVATO (PASS/FAIL per anello, niente a valle di un FAIL)
1. landing → checkout €1 completato (`cs_live` reale generato)
2. webhook ricevuto → riga in D1 prod per quella session
3. mail licenza/recovery ARRIVA nella casella secondaria e si apre (chiude 🔴 deliverability)
4. pagina post-pagamento mostra copy nuovo (recovery-link/paste), NON "inserisci email auto-verify"
5. attivazione via percorso DEFAULT (link recovery/payload dalla mail), NON carica-file (chiude 🔴 default-path)
6. wizard: P.IVA errata → riepilogo+toast (#2); step 6 dropdown senza overlap (#3)
7. B1: Nuovo Cliente, telefono vuoto → Salva → toast "Controlla i campi"
8. CRUD: crea→cerca/filtra→modifica→archivia/elimina con conferma. Zero BLOCCANTI.
**Done = giro completo, zero nuovi BLOCCANTI.** COSMETICI → backlog. Niente quarto decimale.

### CLAUSOLA 2 — parcheggio
Anello non eseguibile (rete iMac giù — già caduta S356; mail non arriva; checkout fallisce) → `BLOCKED-ON: <anello esatto>`. Un FAIL all'anello 3 (deliverability) è un RISULTATO decisivo, non un blocco da aggirare. Riporta solo ciò che è stato realmente visto.

### VINCOLI
MCP `filesystem:*` per il Mac, mai container Linux. Nessuna cred in chat. `tauri-driver`/headless VIETATO — il giro lo fa il founder fisicamente. WIP=1: nessun lavoro Sara/R1. Mail secondaria isolata (non inquina dati cliente reali). "refund processato" ≠ "gate D4 runtime enforced" (D4 fail-open, distinto — non confondere).

---

## RICHIESTA A CC (S369): esegui #0.a+#0.b + precondizioni read-only → riporta cosa manca/cosa fa fallire per ragione finta (Resend from, prezzo, refund, D1, chiavi live, modalità Stripe) → POI attendi G-APPROVAL founder per deploy + acquisto. Nulla di irreversibile prima.

## APERTI MINORI (non bloccano S369)
- (d) Magazzino+alert scorte 1 verticale: GATE PASS S361 → confermare vendibile.
- Sara: trial 30gg via phone-home (no bug, CHIUSA). Sara tutti-i-verticali chiamata-reale = hard-gate pre-vendita (verdetto giudice S365, NON declassare). Restart pipeline iMac: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python3 main.py --port 3002 > /tmp/sara_pipeline.log 2>&1 &"`.
- R1 Sales Agent → SOSPESO fino a onboarding VERDE (verdetto giudice S365).
