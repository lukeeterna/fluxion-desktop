# Prompt ripartenza — generato automaticamente

## ⏭️ ENTRY S376 — TASK €1 FRESCO / PATH-200 (giudice/founder) — DA ARMARE
> Ordine giudice: collaudare la pipeline cliente ex-novo su charge reale non-rimborsato. Chiude in un colpo: **path-200 recovery** (mai visto finora — fatto chiave), template-reale-via-webhook, no-blob su mail+pagina con charge vivo. **CTO arma+verifica; l'acquisto è atto founder.**
> ⚠️ Stato ARM: NON eseguito in S375 (HARD_STOP budget dopo aver solo localizzato la chiave Stripe `~/.claude/.env.fluxion-live` → `STRIPE_LIVE_SECRET_KEY`). plink status + landing NON verificati. **Primo step S376 = ARM (A) sotto.**

### A) ARMARE il path €1 (idempotente, verifica-alla-fonte PRIMA di mutare)
1. **plink** `plink_1TeCftIW4bHDTsaHJfwJNndD` (a S372/T1 era `active:false`):
   `curl -s https://api.stripe.com/v1/payment_links/plink_1TeCftIW4bHDTsaHJfwJNndD -u "$STRIPE_LIVE_SECRET_KEY:"` → leggi `active`.
   - se `false` → riattiva: `curl -s -X POST .../plink_1TeCftIW4bHDTsaHJfwJNndD -u "$KEY:" -d active=true`.
   - se `true` → skip. **DONE-A1**: GET ri-mostra `active:true` + leggi `url` (= URL diretto €1 da dare al founder).
2. **Landing** `?plan=test` (a S372/T1 il blocco `test:{}` €1 fu RIMOSSO da `landing/checkout-consent.html`, commit 9bbed91):
   - **RACCOMANDATO minimo-impatto**: NON ripristinare la landing. Aprire l'URL diretto del plink (da A1) → bypassa la landing, zero mutazione, Base/Pro pubblici restano puliti.
   - Se founder vuole il path via landing: ripristina blocco `test:{}` (NON committare) + deploy Pages preview; **verifica Base/Pro €497/€897 INTATTI** (`curl` prod: `24003` e `24004` presenti, pulsanti pubblici invariati).
   - **DONE-A2**: `curl` prod che mostra path €1 raggiungibile + Base/Pro intatti.

### B) RUNBOOK FOUNDER (atto founder — dopo conferma ARM)
1. Apri **URL diretto plink** (output A1 `url`) in browser.
2. Usa una **mail secondaria FRESCA mai usata prima** (NON `fluxion.gestionale@`, NON `gianlucadistasi81@`, NON `ilcombeeretrasher@` — tutte già in D1). Annota quale.
3. Paga €1 con carta reale. Atteso a schermo: redirect a `https://fluxion-app.com/success/cs_live_…` → pagina "Licenza FLUXION Base pronta" (Passo 1/2/3, **zero blob** dopo S375), + mail brandizzata in inbox.
4. NON rimborsare ancora. Avvisa il CTO con la mail usata.

### C) VERIFICA POST-ACQUISTO — ORDINE OBBLIGATO (charge vivo PRIMA del refund)
> Se inverti, il refund brucia il path-200. Step 5 NON parte prima che 1-4 siano verdi. Ogni step = fatto terminale (id/curl/grep).
1. **D1**: `wrangler d1 execute fluxion-webhook-events --remote --command "SELECT session_id,license_id,customer_email,length(license_payload) lp,length(license_signature) ls FROM webhook_events WHERE customer_email='<mail-fresca>' ORDER BY created_at DESC LIMIT 1"` → riga nuova, `license_id` non-null, `lp>0 ls>0`.
2. **Mail**: founder eyeball inbox = template reale brandizzato (logo live + zero blob). [esterno founder]
3. **Recovery 200** (FATTO CHIAVE): `token=hex(HMAC-SHA256(LICENSE_RECOVERY_SECRET, mail.toLowerCase().trim()))` → `curl "https://fluxion-app.com/api/v1/license/<mail>?token=$token"` → **200 + licenza** (primo path-200 mai osservato; secret = worker, allineato S373 al file `~/.claude/.env.s295-recovery-secret`).
4. **Attivazione app** (founder apri app + carica licenza) → CTO verifica `license_cache` locale popolata (SSH iMac/Win sqlite, delta id).
5. **SOLO DOPO 1-4 verdi** → refund charge → recovery stessa mail → **410** (prova gate-rimborso su charge vivo).

### Regole
- Step irraggiungibile in-sessione → BLOCKED-ON dichiarato, NON simulare.
- NON toccare: T2/T3/Q5 (verde), node-lock Q4/Q6 (post-CLOSED_WON).

---

**Generato**: `2026-06-20T09:23:06Z`
**Sessione**: `e64492a4-80ff-4210-b9d7-e199820d84d5`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `fabbfdf feat(s375): Q5 success-page — rimuovi blob licenza inline, instrada a recovery-link (rispetta gate-rimborso)`

## Ultimi 5 commit
```
fabbfdf feat(s375): Q5 success-page — rimuovi blob licenza inline, instrada a recovery-link (rispetta gate-rimborso)
b813fab docs(s373): carry S374 — T2/T3 verdi, ricerca Q6 pronta, decisioni founder aperte
d34e9b2 docs(s373): ricerca Q6 node-lock server-side (subagent) — re-bind ESISTE, Q6 fattibile zero-cost
1bb9abe docs(s373): report sessione T2+T3 chiusi + decisioni founder aperte
cba2c29 feat(s373): T3 copy-ponte — rimuovi 'Windows in arrivo' da success page + flag finding Q5
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.md
A	.claude/SESSION_DIRTY.md
M	.claude/session_state.md
M	fluxion-proxy/src/routes/checkout-success.ts
M	vos-out/decisions.jsonl
```

## Ultimo prompt utente (estratto)
```
[{"tool_use_id":"toolu_017qgQhKqzo44YJy8eD7EX5B","type":"tool_result","content":"🔍 Fluxion Pre-Commit Checks...\n⚙️  Formatting Rust...\n⚠️  cargo non disponibile, skip Rust formatting check\n📘 Type-checking TypeScript...\nnpm warn Unknown project config \"PUPPETEER_SKIP_DOWNLOAD\". This will stop working in the next major version of npm. See `npm help npmrc` for supported config options.\nnpm warn Unknown project config \"PUPPETEER_SKIP_CHROMIUM_DOWNLOAD\". This will stop working 
```

## Ultimi turni assistant
```
**Deploy**: Version `18a50a2f-f740-4837-99d7-6561434fbfe0`. **Commit**: `fabbfdf`. **type-check**: EXIT=0.
NON toccati: T2/T3 (verde), node-lock Q4/Q6 (post-CLOSED_WON).
Next prompt: `/Volumes/MontereyT7/FLUXION/.claude/NEXT_SESSION_PROMPT.md`
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
