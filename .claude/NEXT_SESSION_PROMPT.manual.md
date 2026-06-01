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

**Task 2 — chiudere ORACOLO enumeration** `activate-by-email.ts:67` (solo `includes('@')`):
DECISIONE LUKE PENDING (vedi sotto). Raccomandazione CTO = RIMUOVERE l'endpoint del tutto
(l'attivazione vive su email-embed Task 3 + recovery HMAC `license-recovery.ts`). Mettere HMAC
duplicherebbe il recovery. Se rimosso: aggiornare UI `LicenseManager.tsx:354` (`emailMode`) +
`src/lib/activate-by-email.ts` + `handleEmailActivation` (`:359-408`).

**Task 3 — consegna EMAIL-EMBED**: il Worker include `license_payload`+`license_signature`
nell'email Resend post-acquisto (single-recipient = owner). Modifica minima al sender nel
webhook (`fluxion-proxy/src/routes/stripe-webhook.ts`, cercare invio Resend). Schema firma INVARIATO.
Il client legge da email (link recovery o paste) → `activate_license_v1` (già pronto, #4).

## DECISIONE LUKE PRIMA DI IMPLEMENTARE
Task 2: rimuovere `activate-by-email` (raccomandato) OPPURE proteggerlo con HMAC come il recovery?
- Rimuovere = -1 oracolo, -1 leak PII (R-10), UI "attiva con email" sparisce, resta email-embed + recovery HMAC.
- HMAC = mantiene UI ma duplica il recovery (client deve già avere il token = già ha il recovery link).

## E2E (gate G1+G2) post-implementazione — path EMAIL-EMBED
Stripe test card 4242 → webhook → D1 insert → firma Ed25519 → email Resend CHE PORTA la licenza →
client legge → `activate_license_v1` verifica + popola `license_cache` → UI feature attive.
Tamper payload → `false`. Salvare evidence reale (no claim narrativi). Poi smoke €1 live.

## ACCEPTANCE
- Nessun `license_payload`/`license_signature` su endpoint senza HMAC (grep conferma).
- `activate-by-email` non più oracolo (rimosso o HMAC).
- Email Resend porta la licenza; attivazione offline; `license_cache` popolata via path email.
- E2E con evidence: pagamento → email → attivazione → feature attive (G1+G2). Tamper → false.
