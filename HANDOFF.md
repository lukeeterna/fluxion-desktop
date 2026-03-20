# FLUXION — Handoff Sessione 105 → 106 (2026-03-20)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni. MAI presentare problemi senza soluzioni. MAI fare il compitino."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 (127.0.0.1) | **iMac DISPONIBILE + PIPELINE ATTIVA**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22
**Tauri dev su iMac**: `bash -l -c 'cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev'`

---

## STATO GIT
```
Branch: master | HEAD: aaa728f
type-check: 0 errori
iMac: sincronizzato
Commit S105: aaa728f (fix 5 UX audit bugs)
```

---

## COMPLETATO SESSIONE 105

### 1. Bug UX Audit — TUTTI FIXATI (commit aaa728f)
- **BUG-1** (CRITICO): VoiceAgentSettings — rimosso campo Groq API key, ora mostra "Gestita automaticamente da FLUXION AI" con health check pipeline live ogni 30s
- **BUG-2** (CRITICO): SmtpSettings già aveva guida Gmail App Password completa (4 step + link myaccount.google.com/apppasswords) — nessuna modifica necessaria
- **BUG-3** (MEDIO): Dashboard Welcome Card per DB vuoto — CTA "Aggiungi primo cliente" + "Crea appuntamento", appare solo quando 0 clienti e 0 appuntamenti
- **BUG-4** (BASSO): Creata `landing/voip-guida/index.html` — guida EHIWEB a prova di bambino, 3 step, FAQ, costi (~2 €/mese)
- **BUG-5** (MEDIO): `activate.html` riscritta — rimossa API call rotta a `/api/activate`, ora guida statica "3 passi" (controlla email → installa → incolla chiave)

### 2. CF Worker Deployato (LIVE)
- **URL**: https://fluxion-proxy.gianlucanewtech.workers.dev
- **Health**: `/health` → `{"status":"ok","service":"fluxion-proxy","version":"1.0.0"}`
- **Webhook Stripe**: route `/api/v1/webhook/stripe` — pronta, serve secrets
- **Secrets già configurati**: `ED25519_PUBLIC_KEY`, `GROQ_API_KEY`, `CEREBRAS_API_KEY`, `OPENROUTER_API_KEY`
- **Secrets MANCANTI**: `STRIPE_WEBHOOK_SECRET`, `RESEND_API_KEY`, `ED25519_PRIVATE_KEY`

### 3. Landing Redeployata
- **URL**: https://fluxion-landing.pages.dev
- **Nuove pagine**: `/voip-guida/` (200 OK), `/activate.html` (riscritta, no API call rotta)

---

## DA FARE S106 — "GIORNO 0" COMPLETO

### BLOCCO 1: Secrets + Stripe Webhook (fondatore deve fare)
- [ ] Creare account Resend (resend.com) → copiare API key
- [ ] `CLOUDFLARE_API_TOKEN=Jn27... npx wrangler secret put RESEND_API_KEY` → incollare `re_...`
- [ ] Su Stripe Dashboard → Webhooks → Add endpoint:
      URL: `https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe`
      Events: `checkout.session.completed`
- [ ] Copiare il "Signing secret" (whsec_...) dal webhook appena creato
- [ ] `CLOUDFLARE_API_TOKEN=Jn27... npx wrangler secret put STRIPE_WEBHOOK_SECRET` → incollare `whsec_...`
- [ ] Eliminare prodotto test "fluxion test" (`prod_UBT5nbzrbxvjh3`) dal Dashboard Stripe
- [ ] Test: fare acquisto Stripe test → webhook ricevuto → email Resend arriva

### BLOCCO 2: Test Installazione macOS
- [ ] Cancellare app precedente: `sudo rm -rf /Applications/Fluxion.app`
- [ ] Cancellare DB dev: `rm -rf ~/Library/Application\ Support/com.fluxion.desktop/`
- [ ] Doppio-click PKG → install → verifica ZERO avvisi
- [ ] Aprire FLUXION da Launchpad → wizard funziona da zero
- [ ] Verificare ogni step del wizard (nicchia, orari, email, operatori)

### BLOCCO 3: Test Wizard UX "A Prova di Bambino"
- [ ] Step email: Gmail App Password guida chiara? L'utente capisce?
- [ ] Step nicchia: selezione semplice?
- [ ] Step operatori: aggiunta facile?
- [ ] Step orari: impostazione intuitiva?
- [ ] Alla fine del wizard: dashboard funziona? Welcome card visibile? Empty states chiari?

### BLOCCO 4: Test Flusso Acquisto
- [ ] Clicca "Acquista" su landing → Stripe Checkout si apre
- [ ] Pagamento test → redirect a /grazie
- [ ] Pagina /grazie mostra download link corretto
- [ ] Email di conferma arriva (se Resend configurato)

### BLOCCO 5: Fix Issues Trovati
- [ ] Fix qualsiasi problema UX emerso dal test
- [ ] Copy review TOTALE (nessun testo tecnico, tutto plain language)

### BLOCCO 6: Contenuti Mancanti
- [ ] Video demo walkthrough (anche basico 2 min)
- [ ] EHIWEB: copy "a prova di bambino" (utente non sa cos'è VoIP)
- [ ] Guida in-app per OGNI funzionalità

---

## STRIPE INFO
```
Account: LIVE
API Key (restricted): rk_live_51TD5XvIW4...nNlfuWI (in memory)
Base product: prod_UBT1Dg0l0bYO4C (price: price_1TD65hIW4bHDTsaHFs3O3iMk)
Pro product: prod_UBT51LsziQDyYd (price: price_1TD69aIW4bHDTsaHnhBXkI2H)
Test product: prod_UBT5nbzrbxvjh3 — DA ELIMINARE
Base Payment Link: https://buy.stripe.com/bJe7sM19ZdWegU727E24000
Pro Payment Link: https://buy.stripe.com/00w28sdWL8BU0V9fYu24001
CF Worker webhook URL: https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe
```

---

## DIRETTIVE FONDATORE (NON NEGOZIABILI)

1. **CTO MODE** — porta soluzioni, non problemi
2. **A PROVA DI BAMBINO** — 2 click massimo per qualsiasi operazione
3. **ZERO COSTI** — tutto €0, trova il modo
4. **ENTERPRISE GRADE** — gold standard mondiale
5. **ZERO SUPPORTO MANUALE** — ogni feature funziona senza telefonata
6. **MAI riferimenti Anthropic/Claude** — zero nel codice, commit, UI
7. **SARA = SOLO DATI DB** — zero improvvisazione
8. **SEMPRE 1 nicchia** (micro-categoria) — una PMI = un'attività
9. **TUTTO "FLUXION AI"** — mai esporre Groq/Cerebras all'utente
10. **NO download gratuito** — il cliente paga prima di scaricare
11. **NO fattura IVA** — Prestazione Occasionale, NO ricevuta menzionata
12. **COPY PERFETTO** — zero tecnicismi, PMI plain language sempre
13. **UI/UX ENTERPRISE** — skill Claude Code, deep research CoVe 2026

---

## BUILD COMMANDS

```bash
# Build completo su iMac (7 step: sidecar + frontend + Tauri + codesign + PKG + DMG)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master && bash scripts/build-macos.sh"

# Deploy landing
CLOUDFLARE_API_TOKEN=Jn27vQB1Vp8rkrA9v9cV1PFC-CRSczG6h1DvteBE wrangler pages deploy ./landing --project-name=fluxion-landing

# Deploy CF Worker
cd fluxion-proxy && CLOUDFLARE_API_TOKEN=Jn27vQB1Vp8rkrA9v9cV1PFC-CRSczG6h1DvteBE wrangler deploy

# Test fresh install
sudo rm -rf /Applications/Fluxion.app && rm -rf ~/Library/Application\ Support/com.fluxion.desktop/ && open releases/v1.0.0/Fluxion_1.0.0_macOS.pkg
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 106. CTO MODE FULL.
S105: 5 bug UX audit fixati (zero-config Sara, welcome card, voip-guida, activate page).
CF Worker deployato LIVE. Landing redeployata con nuove pagine.
FOCUS S106: BLOCCO 1 (Stripe webhook secrets) → BLOCCO 2-3 (test installazione + wizard).
Serve: fondatore crea account Resend + configura webhook Stripe Dashboard.
Pipeline iMac ATTIVA. iMac sincronizzato.
```
