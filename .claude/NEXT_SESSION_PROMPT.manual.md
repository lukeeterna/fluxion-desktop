# Prompt ripartenza — S376 🟢 PILA-1 E2E VERDE + verdetto giudice 3 review

## 🟢 S376 — PILA-1 PROVATA E2E (charge reale fresco manueldx2014, costo €0)
C1 D1 ✅ · C3 recovery **200** ✅ (path-200) · C4 app **active** su Windows ✅ · C5 refund→**410** ✅. Dettaglio in commit `3b662d4`. Tutti i charge rimborsati.

## VERDETTO GIUDICE (3 review) — ordine di lavoro
Prompt giudice: `.claude/cache/s376-review-giudice.md`. Risposta ricevuta, sintesi:
1. **success_url** (Punto 3) = blocker condizionato, **sondare per primo** (ignoto-letale). → **VERIFICATO S376, vedi sotto**.
2. **Re-prompt licenza in Impostazioni** = blocker fiducia, fix localizzato: la pagina Impostazioni deve **rileggere `license_cache` al mount** invece di assumere "non attivata". (persistenza OK, status=active → è display, non dati).
3. **Wording "licenza del tuo mac"** = NON blocker ma fix obbligatorio 1-stringa: dicitura neutra ("Licenza attiva"/"La tua licenza FLUXION") finché node-lock Q6 non popola `machine_id`. **NON implementare node-lock** (scope chiuso post-CLOSED_WON); `machine_id` vuoto è atteso/corretto.

## 🟢 PUNTO 3 — CHIUSO (S377, verificato alla fonte Stripe LIVE API)
**Risposta**: la landing pubblica (`landing/checkout-consent.html`) usa già i link BUONI:
- Base €497 → `…8boabwRX` (short `…24003`) → success-page ✅ (active=True)
- Pro €897 → `…fn8dioIo` (short `…24004`) → success-page ✅ (active=True)

**Root cause scoperto (REGOLA #11)**: non un singolo link vagante, ma URL checkout pre-S104 stale su più superfici prodotto, tutti →`/grazie`:
- `…24000` (Base zombie ATTIVO) e `…24001` (Pro zombie INATTIVO) erano ancora in: `src/types/license-ed25519.ts`, `voice-agent/data/sales_knowledge_base.json` (Sara sales KB), `fluxion-proxy/src/routes/nlu-proxy.ts`, `src/components/license/SaraTrialBanner.tsx`, + 3 agent docs.
**Fix S377**: tutte ripuntate a `…24003`(Base)/`…24004`(Pro). Zombie attivo `plink_1TD6Dp…D2Hii4hA` → `active=false` via API. Ora NESSUN link attivo punta a `/grazie`. Residui solo in `_clinic_disabled.html` (pagina disabilitata) e `.claude/cache/` (research storica) — non live.

## 🟢 PUNTO 1 — CHIUSO PER FATTO (S378): fingerprint == , NON è instability
Verdetto autonomo via `ssh fluxion-win` (read-only, no fix, no subagent). Confronto byte-per-byte sulla macchina pagante (€1 S376, host `AlessiaManuel`):
- **salvato** (`license_cache` id=1, DB Windows reale `C:\Users\gianluca\AppData\Roaming\com.fluxion.desktop\fluxion.db`, letto con FileShare.ReadWrite perché app accesa): `343865fe7623b3063a50941e55e68e29` — status=active, tier=base, machine_id vuoto (atteso), email manueldx2014.
- **runtime** (`generate_fingerprint()` = SHA-256("hostname:cpu_brand:total_memory:system_name")[..16], sysinfo 0.29.11): ricostruito dai valori LIVE correnti `AlessiaManuel:Intel(R) Core(TM) i5-4210U CPU @ 1.70GHz:8516689920:Windows` → `343865fe7623b3063a50941e55e68e29`.
- **VERDETTO: == (identici)**. Prova per costruzione (input hardware stabili letti ora riproducono lo stored), non deduzione statica.
→ `fp == fingerprint` → niente HARDWARE_MISMATCH (`license_ed25519.rs:544`) → `is_valid=true, is_activated=true`. Re-prompt NON è fingerprint. Combinato con prova sorgente S377 → Punto 1 NON è un bug; eventuale re-prompt passato = build vecchia. Ramo `!=` (node-lock) NON si è verificato → niente da toccare.

## 🟡 PUNTO 1 — (storico S377) INVESTIGATO A SORGENTE: nessun data-bug, ipotesi falsificata
"Impostazioni non rilegge license_cache al mount" NON esiste nel codice attuale. Prova:
- `src-tauri/src/commands/license_ed25519.rs:482-492` — `get_license_status_ed25519` fa `SELECT ... FROM license_cache WHERE id=1` dal pool ad OGNI invocazione (nessun in-memory stale).
- `src/hooks/use-license-ed25519.ts:33-42` — fetch-on-mount + refetchInterval; invalidation post-attivazione `:130-131`.
- `license_ed25519.rs:540-582` — status="active"+license_id+stesso fingerprint → `is_activated=true, is_valid=true`.
- `src/components/license/LicenseManager.tsx:406,509,416` — ActivePlanCard sempre quando status esiste; "Attiva Licenza" collassata di default.
- `src/App.tsx` — NESSUN gate licenza (0 match).
**Root cause strutturale (REGOLA #11)**: 2 sistemi licenza paralleli. Legacy (`src/hooks/use-license.ts`→`get_license_status`, `LicenseStatus.tsx`/`LicenseDialog.tsx`/`useLicenseGate` con `needsActivation`) = il solo che mostrerebbe re-prompt, ma è ORFANO (0 mount/import). Tech-debt da rimuovere (task separato, non urgente).
**BLOCKED-ON walkthrough founder Windows**: aprire Impostazioni → screenshot. Se "Piano Attivo / FLUXION Base" → Punto 1 verde (era build vecchia). Se "registrata su altro Mac"/"Nessuna Licenza" → fingerprint instability (`generate_fingerprint` read-time≠activation-time, `license_ed25519.rs:544`) = task node-lock esplicito (oggi Q4/Q6 NON toccare).

## Ordine prossima sessione
1. ATTESO: output del GIUDICE (Claude AI) su Punto 1 — ingerirlo PRIMA di agire. NB: Punto 1 già chiuso per fatto S378 (fingerprint ==), il giudice conferma/contesta il metodo.
2. Fix Punto 2 (stringa wording neutra "Licenza attiva") — pronto, indipendente, zero-cost.
Tutti zero-cost, nessun codice nuovo significativo, nessuno tocca node-lock.

## NON toccare: T2/T3/Q5 (verde), node-lock Q4/Q6.
⚠️ Hook PostToolUse rigenera questo file in boilerplate dopo ogni Bash → fonte = ultimo commit.
