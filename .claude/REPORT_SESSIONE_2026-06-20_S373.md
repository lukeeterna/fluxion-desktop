# REPORT SESSIONE S373 — 2026-06-20 — verso full production (onboarding email+copy)

## FATTO (verde, evidenze E2E reali)

### ✅ T2 — MAIL LICENZA (deploy + invio reale + link verificato)
- Worker deployato: Version `4ea8119b` su `fluxion-proxy` (= `fluxion-app.com`).
- Mail di conferma spedita realmente a `gianlucadistasi81@gmail.com` → **Resend id `c06ba11c-0d5e-45df-a364-8e0afacacef4`, HTTP 200**.
- HTML = output ESATTO di `buildEmailHtml` (bundle esbuild della funzione reale, zero-divergenza). `buildEmailHtml` reso `export`; harness `fluxion-proxy/scripts/send-test-confirmation.ts`.
- Guard runtime: nel corpo HTML **zero** `Payload firmato`/`Firma Ed25519`/`base64`/blob → verdetto giudice Q5 confermato a runtime.
- **Bug catturato+fix**: recovery-link prima dava **403 Invalid token** = `LICENSE_RECOVERY_SECRET` del Worker disallineato dal file `~/.claude/.env.s295-recovery-secret`. Riallineato via `wrangler secret put` (64 hex). Nessun cliente reale impattato (per i clienti veri il Worker costruisce E valida il link col proprio secret = self-consistent; tutte le purchase esistenti sono test rimborsate).
- Recovery endpoint verificato (3 esiti reali con token valido): 404 non-acquirente, 410 rimborsato (gate-rimborso OK). Path 200+licenza = BLOCKED-ON prima vendita reale non-rimborsata.

### ✅ T3 — COPY-PONTE post-pagamento
- `checkout-success.ts:156`: `"Versione Windows in arrivo…"` → `"Compatibile con macOS 12+ (Intel e Apple Silicon)."`. Deploy Version `284e96bf`.
- Verifica E2E prod (session LIVE reale `cs_live_a152jM61…`, template completo): `in arrivo`=0, nuova copy presente, title `FLUXION Base — Licenza pronta`.

## Commit
- `5d98592` feat(s373): T2 mail licenza
- `cba2c29` feat(s373): T3 copy-ponte + flag finding Q5

## 🚩 DECISIONI FOUNDER APERTE
1. **Eyeball Gmail** (chiude T2 esterna): apri la mail `c06ba11c` su gianlucadistasi81@gmail.com → conferma logo + copy + pulsante "Recupera". (Click pulsante = 404 per gianluca: non ha acquisto reale, atteso.)
2. **Finding sicurezza Q5-consistency**: la success page (`checkout-success.ts:180-195`) mostra il blob licenza inline ANCHE per purchase rimborsate (bypassa il gate-rimborso, come faceva l'email pre-Q5). Estendere logica Q5 alla success page? → serve verdetto giudice sullo scope (come fu per l'email). NON toccato (fuori scope T3, REGOLA #29).
3. **Anelli 4-8** (walkthrough nativo): PASS / non-fatti / bloccante? → sblocca T4 (Windows download).

## NEXT (raccomandazione CTO)
Verso la prima vendita reale, ordine consigliato:
1. **Q6 — node-lock server-side al retrieve** (anti-abuso, autonomo, no iMac/founder-present): PRIMA verificare a sorgente che la primitiva di re-bind esista (`src-tauri/src/commands/license_ed25519.rs:712-714`, giudice Q4: NON darla per esistente). Senza re-bind testata → NON implementare lock-out (rischio clienti paganti).
2. **Sara live test tutti i verticali** = VERO hard-gate vendita (REGOLA #21). Pipeline iMac attualmente DOWN (3001/3002). Sessione dedicata founder-presente (EHIWEB SIP, harness `voice-agent/scripts/sara_audio_harness.py`).
3. **T4 Windows download** = solo se anelli 4-8 PASS.

## Stato pre-vendita (sintesi)
- Payment rail prod: OK. Onboarding email+copy: OK (T2+T3). Magazzino+alert: GATE PASS (S361).
- Mancano a "pronto a vendere": Sara live (hard-gate), path 200 recovery (col 1° acquisto vero), decisione Q6/Q5-success.
