# FLUXION — Handoff Sessione 104 → 105 (2026-03-20)

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
Branch: master | HEAD: 067ceaf
type-check: 0 errori
iMac: sincronizzato
3 commit S104: 62a6ab6, a84e41f, 067ceaf
```

---

## COMPLETATO SESSIONE 104

### 1. LemonSqueezy → Stripe (COMPLETO)
- LemonSqueezy RIMOSSO da TUTTI i file (11 file puliti)
- Stripe Payment Links LIVE creati via API:
  - **Base €497**: `https://buy.stripe.com/bJe7sM19ZdWegU727E24000`
  - **Pro €897**: `https://buy.stripe.com/00w28sdWL8BU0V9fYu24001`
- Stripe webhook route nel CF Worker (`/api/v1/webhook/stripe`) con signature verification
- Resend email delivery wired nel webhook (conferma acquisto + link download)
- Prodotto test "fluxion test" (`prod_UBT5nbzrbxvjh3`) DA ELIMINARE dal Dashboard Stripe

### 2. PKG Installer macOS (COMPLETO)
- `scripts/build-macos.sh`: build completo 7 step (PyInstaller + Tauri + codesign + PKG + DMG)
- `scripts/pkg-scripts/postinstall`: rimuove quarantine + fix permessi + LaunchServices
- PKG creato: `releases/v1.0.0/Fluxion_1.0.0_macOS.pkg` (68MB)
- **DA TESTARE**: doppio-click PKG → install → app si apre senza avvisi

### 3. Landing Page Aggiornata + Deployata
- "Fattura IVA italiana" RIMOSSO (Prestazione Occasionale, NO P.IVA)
- "Ricevuta inclusa" RIMOSSO
- Copy corretta: "Pagamento sicuro via Stripe · Garanzia 30 giorni"
- Pagina `/installa` creata (macOS Gatekeeper + Windows SmartScreen guide)
- Pagina `/grazie` creata (post-acquisto: download + istruzioni)
- **LIVE**: https://fluxion-landing.pages.dev

### 4. GitHub Release v1.0.0
- **LIVE**: https://github.com/lukeeterna/fluxion-desktop/releases/tag/v1.0.0
- Assets: PKG (68MB) + DMG (71MB)

### 5. EHIWEB VoIP Proposal
- Aggiunta sezione VoIP in SaraTrialBanner (solo durante trial attivo, tier base)
- Copy PMI-friendly, dismissabile, link a guida VoIP

### 6. Stripe Account
- Account Stripe LIVE del fondatore
- API Key (restricted): in `memory/reference_stripe_account.md`
- 3 prodotti creati (Base, Pro, test da eliminare)
- Webhook secrets DA CONFIGURARE: `STRIPE_WEBHOOK_SECRET`, `RESEND_API_KEY`

---

## DA FARE S105 — "GIORNO 0" TEST COMPLETO

### PRIORITA ASSOLUTA: Flusso Completo End-to-End
Il fondatore vuole testare TUTTO il percorso utente come un titolare PMI ignorante.

### BLOCCO 1: Configurare Infra (BLOCCA TUTTO)
- [ ] `wrangler secret put STRIPE_WEBHOOK_SECRET` (dal Dashboard Stripe > Webhooks)
- [ ] `wrangler secret put RESEND_API_KEY` (creare account Resend free)
- [ ] Configurare webhook URL Stripe: `https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe`
- [ ] Eliminare prodotto test "fluxion test" da Stripe Dashboard
- [ ] Deploy CF Worker aggiornato: `wrangler deploy` (con nuova route webhook)

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
- [ ] Alla fine del wizard: dashboard funziona? Empty states chiari?

### BLOCCO 4: Test Flusso Acquisto
- [ ] Clicca "Acquista" su landing → Stripe Checkout si apre
- [ ] Pagamento test → redirect a /grazie
- [ ] Pagina /grazie mostra download link corretto
- [ ] Email di conferma arriva (se Resend configurato)

### BLOCCO 5: Fix Issues Trovati
- [ ] Fix qualsiasi problema UX emerso dal test
- [ ] Copy review TOTALE (nessun testo tecnico, tutto plain language)
- [ ] OpenRouter cleanup se necessario

### BLOCCO 6: Contenuti Mancanti
- [ ] Video demo walkthrough (anche basico 2 min)
- [ ] EHIWEB: copy "a prova di bambino" (utente non sa cos'è VoIP)
- [ ] Guida in-app per OGNI funzionalità

### BLOCCO 7: Windows (Parallelo)
- [ ] MSI Build con WiX
- [ ] Test su Windows reale/VM

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

# Solo PKG da app esistente
ssh imac 'APP="/Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/bundle/macos/Fluxion.app" && codesign --sign - --force "$APP/Contents/MacOS/voice-agent" && codesign --sign - --force "$APP/Contents/MacOS/tauri-app" && codesign --sign - --force --deep "$APP" && mkdir -p "/Volumes/MacSSD - Dati/fluxion/releases/v1.0.0" && PAYLOAD="/tmp/fluxion-pkg-payload" && rm -rf "$PAYLOAD" && mkdir -p "$PAYLOAD" && cp -R "$APP" "$PAYLOAD/Fluxion.app" && xattr -cr "$PAYLOAD/Fluxion.app" && pkgbuild --root "$PAYLOAD" --identifier "com.fluxion.desktop" --version "1.0.0" --install-location "/Applications" --scripts "/Volumes/MacSSD - Dati/fluxion/scripts/pkg-scripts" "/Volumes/MacSSD - Dati/fluxion/releases/v1.0.0/Fluxion_1.0.0_macOS.pkg"'

# Copia PKG su MacBook
scp imac:"/Volumes/MacSSD\ -\ Dati/fluxion/releases/v1.0.0/Fluxion_1.0.0_macOS.pkg" releases/v1.0.0/

# Deploy landing
CLOUDFLARE_API_TOKEN=Jn27vQB1Vp8rkrA9v9cV1PFC-CRSczG6h1DvteBE wrangler pages deploy ./landing --project-name=fluxion-landing

# Deploy CF Worker
cd fluxion-proxy && CLOUDFLARE_API_TOKEN=Jn27vQB1Vp8rkrA9v9cV1PFC-CRSczG6h1DvteBE wrangler deploy

# GitHub Release upload
# GH_TOKEN dalla remote URL del repo
GH_TOKEN="$(git remote get-url origin | grep -oP 'ghp_[^@]+')" gh release upload v1.0.0 releases/v1.0.0/Fluxion_1.0.0_macOS.pkg --clobber

# Test fresh install
sudo rm -rf /Applications/Fluxion.app && rm -rf ~/Library/Application\ Support/com.fluxion.desktop/ && open releases/v1.0.0/Fluxion_1.0.0_macOS.pkg
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 105. CTO MODE FULL.
S104: Stripe LIVE (Payment Links + webhook + Resend email). PKG installer macOS 68MB.
Landing deployata (Stripe URLs reali, /grazie, /installa). GitHub Release v1.0.0 LIVE.
FOCUS S105: Test "Giorno 0" completo — flusso acquisto→download→install→wizard→uso.
Il fondatore testa come PMI ignorante. TUTTO deve essere a prova di bambino.
Configurare: Stripe webhook secret + Resend API key nel CF Worker.
Eliminare prodotto test Stripe. Deploy CF Worker aggiornato.
Pipeline iMac ATTIVA. iMac sincronizzato.
```
