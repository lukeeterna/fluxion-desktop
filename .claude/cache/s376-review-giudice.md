# Prompt per giudice (Claude AI) — review post-attivazione S376

## Contesto (fatti verificati, non opinioni)
FLUXION = gestionale desktop Tauri (React+Rust+SQLite), licenza Ed25519, pricing one-time (Base €497/Pro €897). Pila-1 revenue = Stripe Checkout → webhook CF Worker → licenza firmata in D1 → email + recovery-link → attivazione app (`license_cache` SQLite locale).

In S376 ho collaudato la pila su un **charge €1 reale, mail mai usata** (`manueldx2014@gmail.com`), verificando alla fonte:
- D1: riga licenza con payload(256)+firma(88), license_id `38ce18393a33cfc2`.
- Recovery endpoint `GET /api/v1/license/<mail>?token=HMAC` → **200** + licenza (primo path-200 osservato).
- Attivazione su **Windows reale**: `license_cache` → id=1, license_id `38ce18393a33cfc2`, tier=base, **status=active**, ed25519=1.
- Dopo refund Stripe → recovery → **410** `{"code":"REFUNDED"}`. Gate-rimborso funziona.

La catena E2E è verde. Restano 3 osservazioni UX/coerenza su cui voglio un secondo parere PRIMA di decidere se sono blocker vendita o cosmetici.

## Punto 1 — Re-prompt licenza in Impostazioni
**Osservato dal founder**: inserita la licenza nel wizard di onboarding (accettata), poi la pagina Impostazioni **richiede di nuovo** la licenza.
**Dato oggettivo**: `license_cache.status=active` con la licenza corretta → la persistenza FUNZIONA. Quindi è un bug di display/refresh (Impostazioni non rilegge lo stato attivo), NON perdita dati.
**Domanda al giudice**: è un blocker per il primo cliente (genera sfiducia "ho pagato e mi richiede la licenza") o cosmetico post-vendita? Qual è il fix corretto (rilettura `license_cache` al mount di Impostazioni vs invalidazione cache stato licenza)?

## Punto 2 — Node-lock: wording vs binding reale
**Osservato**: nel campo licenza in Impostazioni compare "questa è la licenza del tuo mac".
**Dato oggettivo**: `license_cache.machine_id` è **VUOTO** nel DB, e l'attivazione è avvenuta su **Windows** (non un Mac). Quindi: (a) wording errato (dice "mac" su Windows), (b) il binding macchina non è popolato.
**Contesto**: node-lock server-side è classificato Q4/Q6 = post-CLOSED_WON (non ancora implementato). 
**Domanda**: la dicitura attuale è fuorviante/dannosa prima che il node-lock sia reale? Rimuoverla finché machine_id non è effettivamente bound, o è innocua?

## Punto 3 — success_url del payment-link
**Dato oggettivo**: il payment-link €1 di test ha `success_url=https://stripe.com` → niente redirect alla success-page FLUXION; il cliente resta su Stripe.
**Domanda**: verificare che i link Base €497/Pro €897 PUBBLICI puntino alla success-page reale `fluxion-app.com/success/...`. È il difetto più vicino a "blocca revenue" se presente anche sui link veri?

## Cosa chiedo
Per ciascun punto: (a) blocker-vendita SÌ/NO con motivo, (b) fix raccomandato singolo (no liste A/B/C), (c) ordine di priorità tra i 3. Vincolo: zero-cost, enterprise-grade, target PMI italiane non-tecniche.
