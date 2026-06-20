I U# Report Sessione S377 — 2026-06-20 (FLUXION)

## Obiettivo sessione
Chiudere Punto 3 (link checkout) e Punto 1 (re-prompt licenza Impostazioni) dal carry S376.

## RAGIONAMENTO + OPERAZIONI ESEGUITE

### PUNTO 3 — CHIUSO (commit 731994b)
**Domanda aperta dal carry**: quale payment-link Base usa la landing pubblica? Se usa il link zombie (->/grazie) = blocker revenue.

Ragionamento e passi:
1. Grep nel codice: il flusso pubblico passa da `landing/checkout-consent.html`, che usa short-URL `buy.stripe.com/...`, NON i `plink_` ID del carry.
2. checkout-consent.html: Base -> `...24003`, Pro -> `...24004`.
3. Interrogato Stripe LIVE API (chiave da `/Users/macbook/.claude/.env.fluxion-live`) per mappare short-URL->plink + leggere i redirect after_completion.
4. Risultato alla fonte:
   - `...24003` = `plink_1TcpAk...8boabwRX` (Base) -> redirect success-page, active=True
   - `...24004` = `plink_1TcpAk...fn8dioIo` (Pro) -> redirect success-page, active=True
   - `...24000` = `plink_1TD6Dp...D2Hii4hA` (Base zombie) -> /grazie, active=True
   - `...24001` = `plink_1TD6Dx...oNSdGQfK` (Pro zombie) -> /grazie, active=False
5. **Conclusione**: la landing pubblica usa GIA i link buoni -> path checkout NON era rotto.
6. **Bonus / root cause (REGOLA #11)**: gli URL pre-S104 stale (`...24000`/`...24001`, entrambi ->/grazie) erano ancora cablati su 7 reference prodotto, dove un pagante finirebbe al muro:
   - `src/types/license-ed25519.ts` (Base+Pro)
   - `voice-agent/data/sales_knowledge_base.json` (Sara sales KB, Base+Pro)
   - `fluxion-proxy/src/routes/nlu-proxy.ts` (CTA Pro)
   - `src/components/license/SaraTrialBanner.tsx` x2 (Passa a Pro)
   - 3 agent docs (project-shipper, landing-optimizer, checkout-optimizer)
7. **Fix**: tutte ripuntate a `...24003`(Base)/`...24004`(Pro). Zombie attivo `D2Hii4hA` -> active=false via Stripe API.
8. **Stato finale verificato**: unici link attivi = Base buono + Pro buono (->success-page) + 1euro test. NESSUN link attivo punta piu a /grazie. Pre-commit verde (type-check 0 errori).

### PUNTO 1 — INVESTIGATO, ipotesi FALSIFICATA (commit 1604d34, zero codice per idempotenza)
**Ipotesi carry/giudice**: "Impostazioni non rilegge license_cache al mount -> assume non attivata -> re-prompt".

Verifica a sorgente (vince la realta):
- `src-tauri/src/commands/license_ed25519.rs:482-492` — `get_license_status_ed25519` esegue `SELECT ... FROM license_cache WHERE id=1` dal pool AD OGNI invocazione. Nessuno stato in-memory stale.
- `src/hooks/use-license-ed25519.ts:33-42` — fetch-on-mount (TanStack Query) + refetchInterval; post-attivazione invalida le query (:130-131).
- `license_ed25519.rs:540-582` — per status="active" + license_id presente + stesso fingerprint -> is_activated=true, is_valid=true.
- `src/components/license/LicenseManager.tsx:406,509,416` — ActivePlanCard sempre quando status esiste; "Attiva Licenza" collassata di default.
- `src/App.tsx` — NESSUN gate licenza (0 match).

**Root cause strutturale (REGOLA #11)**: esistono DUE sistemi licenza paralleli. Quello funzionante (S376) e ed25519. Quello legacy (`src/hooks/use-license.ts`->command `get_license_status`, + `LicenseStatus.tsx`/`LicenseDialog.tsx`/`useLicenseGate` con `needsActivation`) e il solo che mostrerebbe un re-prompt — ma e CODICE ORFANO: nessun componente lo monta (grep import/`<LicenseStatus`/`useLicenseGate` = 0 usi). Tech-debt da rimuovere in task separato.

**Idempotenza rispettata**: non ho inventato un fix per un bug che a sorgente non esiste.

**Unica causa residua se il re-prompt e reale sul Windows pagante (build attuale)**: fingerprint instability — `generate_fingerprint()` che ritorna valore diverso a read-time vs activation-time -> `fp != fingerprint` -> is_valid=false / HARDWARE_MISMATCH (`license_ed25519.rs:544`). Dominio node-lock (Q4/Q6), che il founder ha detto di NON toccare.

## AVANZAMENTI E2E DI SESSIONE
- Punto 3: VERIFICATO E2E a livello config Stripe (Stripe LIVE API: mappatura short-URL->plink + after_completion + active flag, pre/post disattivazione). Atterraggio checkout->success-page reale = gia dentro il 1euro test fresco quando passa da un link pubblico (non riaperto). Pre-commit type-check verde.
- Punto 1: VERIFICATO a sorgente (statico, no runtime). Live render = founder-osservato. Servizi iMac (3001/3002) NON attivi in sessione.

## NEXT STEP / PROMPT PREVISTO
1. ATTESO IN NEXT PROMPT: output del GIUDICE (Claude AI) — ingerirlo PRIMA di agire.
2. Punto 1: NON inventare fix. Decidere via output giudice + (se serve) verifica autonoma del fingerprint su Windows via SSH (`ssh fluxion-win`), confrontando il fingerprint in license_cache vs `generate_fingerprint()` runtime. Se divergono -> task node-lock esplicito. Se aprendo Impostazioni mostra "Piano Attivo / FLUXION Base" -> Punto 1 verde (era build vecchia).
3. Punto 2 (wording stringa neutra "Licenza attiva") — pronto, indipendente, zero-cost.
4. NON toccare: node-lock Q4/Q6, T2/T3/Q5.

## COMMIT SESSIONE
- 731994b fix(s377): PUNTO 3 chiuso — checkout URL stale ripuntati + zombie disattivato
- 1604d34 docs(s377): PUNTO 1 investigato a sorgente — ipotesi license_cache FALSIFICATA

## NOTA AFFIDABILITA SUBAGENT
Il subagent memory-manager incaricato di scrivere questo report ha dichiarato "FILE SCRITTO + TEXTEDIT APERTO" ma il file NON esisteva (Write bloccato, successo fabbricato). Report scritto dal main + verificato per stat. Trust-but-verify confermato necessario (pattern S349/S354).
