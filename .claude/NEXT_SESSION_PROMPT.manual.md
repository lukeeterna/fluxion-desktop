# NEXT SESSION — FLUXION — R-01-ter: diagnostica FATTA, STOP per ok Luke su scope ridotto

> Sessione R-01-ter ha eseguito la DIAGNOSTICA #1–#4 (read-only) richiesta dal prompt CTO.
> Chiusa a context 72% (CLOSING_ONLY) PRIMA di toccare codice — corretto: il prompt impone
> "STOP per ok" prima di ogni edit, e i file da editare sono security-critical (BLOCK_CRITICAL >50%).
> La sessione fresca implementa Task 1–3 SOLO dopo ok Luke + sniff decisione sotto.
> Branch atteso dal prompt: `fix/license-interop-r01-s327` — ATTUALE `audit/e2e-reality-check-s324`
> (creare/spostarsi sul fix branch all'avvio).

## ESITO DIAGNOSTICA (evidenza file:riga / comando reale)

**#1 — `d46e32f` deployato in prod? → NO. Buco COMMITTATO ma NON LIVE.**
- `git branch -a --contains d46e32f` → solo `audit/e2e-reality-check-s324` (locale). NON master, NON pushed.
- `wrangler deployments list` non eseguibile (`timeout` assente macOS → usare `gtimeout` o nessun wrapper).
- D1 query live → `ERROR 7403 account not authorized` (token scope, pattern noto S307).
- Urgenza BASSA: fix pre-merge, non hotfix prod.

**#2 — righe cliente reali D1? → non recuperabile live** (D1 `ERROR 7403`). Atteso 0. MOOT (buco non deployato).
- Per recuperarlo: fixare token CF (CLOUDFLARE_API_TOKEN con scope D1 read) poi
  `npx wrangler d1 execute fluxion-webhook-events --remote --command "SELECT COUNT(*) AS n FROM webhook_events;"`

**#3 — `FluxionLicense.issued_at` (String) riusato per canonical/verify? → NO. int→string SAFE.**
- Verifica firma usa raw `license_payload` string; int `payload.issued_at: i64` (`license_ed25519.rs:720`)
  parsato dal payload firmato. Conversione int→RFC3339 (`:755-757`) DOPO verifica, solo per display/save
  (`:405,:418,:433`). Il campo String non entra mai in canonical/verify. → **Task 5 = no-op, lasciare.**

**#4 — path PASTE quale command? → GIÀ instradato V1 da `d46e32f`.**
- `onActivate` → `handleActivate` (`LicenseManager.tsx:534-548`): JSON con `license_payload`/`payload`
  → `activate_license_v1` (`:548`); altrimenti legacy. Input V1 ok (`use-license-ed25519.ts:128`).
  → **Task 4 = già fatto.**

## SCOPE REALE RIMANENTE = 3 task (NON 5)

**Task 1 — REVERT esposizione** `fluxion-proxy/src/routes/activate-by-email.ts:124-159`:
rimuovere `license_payload` + `license_signature` dalla response (e dalla query D1 se non più usata).

**Task 2 — RIMUOVERE `activate-by-email`** (DECISIONE LUKE: GO rimozione, NO HMAC-duplicato).
Mappa chiamanti (grep validato R-01-ter):
- Unico chiamante FE endpoint = `LicenseManager.tsx:364-365` (`handleEmailActivation`, UI mode
  "Attiva con Email") via `src/lib/activate-by-email.ts:39` (fetch). = ORFANO da migrare PRIMA.
- Worker: `index.ts:27` (import) + `:85` (route) + handler `routes/activate-by-email.ts` +
  `tests/activate-by-email.test.ts`.
- Rimozione: (a) MIGRARE l'orfano FE → togliere `emailMode` toggle (`LicenseManager.tsx:354,415-431`)
  + `handleEmailActivation` (`:359-408`) + button (`:447-454`); resta SOLO il path "Codice Licenza"
  (paste→V1, già ok #4). (b) eliminare `src/lib/activate-by-email.ts`. (c) togliere route+import in
  `index.ts` + cancellare handler + test. (d) `npm run type-check` EXIT=0.
- RISCHIO DOWNSTREAM (validato): `refund.ts:350` blocca future attivazioni SOLO su activate-by-email;
  `stripe-webhook.ts:589` scrive KV `purchase:{email}`. Rimosso l'endpoint, la licenza firmata
  nell'email resta valida post-refund (firma non codifica refund). → SPOSTARE check refund sul path
  recovery HMAC. **CORRETTO (AMENDMENT, vedi sotto): il flag refund è in KV, NON in D1** — il piano
  originale "lookup D1 refunded+refunded_at" era CIECO/infattibile (D1 `webhook_events` non ha quelle
  colonne, migration 0001). Soluzione = `license-recovery.ts` legge KV `purchase:{email}`. Email-embed
  one-shot pre-refund → OK.

**Task 3 — consegna EMAIL-EMBED**: il Worker include `license_payload`+`license_signature`
nell'email Resend post-acquisto (single-recipient = owner). Modifica minima al sender nel
webhook (`fluxion-proxy/src/routes/stripe-webhook.ts`, cercare invio Resend). Schema firma INVARIATO.
Il client legge da email (link recovery o paste) → `activate_license_v1` (già pronto, #4).

## VINCOLI IMPLEMENTAZIONE (Luke, R-01-ter)
1. Revert CHIRURGICO: solo esposizione `activate-by-email.ts:124-159`. PRESERVA `activate_license_v1`,
   `save_license`, routing paste→V1 di d46e32f.
2. Grep chiamanti PRIMA di rimuovere activate-by-email (già fatto sopra). Se resta orfano → migrare a
   email-embed PRIMA di rimuovere. Riportare i chiamanti.
3. Sbloccare token CF (scope D1 read) e RI-ESEGUIRE #1 (deploy status d46e32f) + #2 (count clienti D1).
   Se #1 deployato → pianificare redeploy Worker post-fix. NIENTE valori credenziali nell'output.
4. E2E path EMAIL con evidence (pay→email-con-licenza→`activate_license_v1`→`license_cache` popolata→
   feature attive). Tamper→false.
5. STOP per yes/no su OGNI modifica (L0). Solo `filesystem:*` MCP.

## E2E (gate G1+G2) post-implementazione — path EMAIL-EMBED
Stripe test card 4242 → webhook → D1 insert → firma Ed25519 → email Resend CHE PORTA la licenza →
client legge → `activate_license_v1` verifica + popola `license_cache` → UI feature attive.
Tamper payload → `false`. Salvare evidence reale (no claim narrativi). Poi smoke €1 live.

## ACCEPTANCE
- Nessun `license_payload`/`license_signature` su endpoint senza HMAC (grep conferma).
- `activate-by-email` non più oracolo (rimosso o HMAC).
- Email Resend porta la licenza; attivazione offline; `license_cache` popolata via path email.
- E2E con evidence: pagamento → email → attivazione → feature attive (G1+G2). Tamper → false.

## AMENDMENT (sessione validazione) — refund residual + deploy epistemics

**A1 — DOVE è il flag refund? → KV, non D1 (validato grep+read).**
- `refund.ts:262` key `purchase:${email}` (`:221` email `.toLowerCase().trim()`); `refund.ts:350-360`
  scrive `refunded:true/refunded_at/refund_reason` su `LICENSE_CACHE.put` = **KV**.
- `stripe-webhook.ts:335-358` stessi campi nascono in KV (`refunded:false`) via `writePurchaseKv`,
  key `:361` `purchase:${customerEmail.toLowerCase().trim()}`. NESSUN handler `charge.refunded` (grep 0).
- `license-recovery.ts:115-124` legge D1 `webhook_events`; `migrations/0001:17-27` la tabella ha SOLO
  event_id/session_id/license_id/customer_email/product/license_payload/license_signature/email_sent_at/
  created_at → **NO colonne refunded**. Lookup D1 sarebbe stato sempre "non rimborsato".

**A2 — fix CORRETTO (key MATCH confermato):** in `license-recovery.ts` DOPO verifica HMAC (`:112`),
PRIMA del lookup D1 (`:114`), leggere KV `purchase:${email}` (`email=:100 .toLowerCase().trim()` =
STESSA key di refund.ts) → se `refunded===true` ritornare 410. HMAC + constant-time INVARIATI.
DIFF PRONTO (in attesa yes/no Luke L0):
```ts
  // Refund gate — flag in KV purchase:{email} (refund.ts:358), NON in D1. Stessa key/normalizzazione.
  const purchaseRaw = await c.env.LICENSE_CACHE.get(`purchase:${email}`);
  if (purchaseRaw) {
    try {
      const p = JSON.parse(purchaseRaw) as { refunded?: boolean; refunded_at?: string | null };
      if (p.refunded === true) {
        return c.json({ error: 'License refunded', code: 'REFUNDED', refunded_at: p.refunded_at ?? null }, 410);
      }
    } catch { /* KV corrotto → fall-through */ }
  }
```

**A3 — residuo (scrivere "mitigato", NON "chiuso"):** il 410-recovery blocca la consegna online
post-refund ma NON ferma refund→uso-offline (licenza bearer, no revoca online = modello v1).
Residuo ACCETTATO da Luke come parte del modello (b). Stato = "mitigato delivery, residuo offline noto".

**B — Deploy #1 = INFERRED-NOT-LIVE, NON confermato.** `d46e32f` non-merged/non-pushed (git);
`wrangler`/D1 bloccati da 7403. R-01/GATE#2 NON "chiuso" finché #1 non gira col token CF risistemato
(scope D1 read). Revert comunque (azione invariata). Niente credenziali nell'output.
