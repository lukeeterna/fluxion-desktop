# Research: Zero-Bug Install Flow per FLUXION (S184 α.3 prep)

**Data**: 2026-05-02
**Sprint**: S184 α.3 prep — HW Test Matrix VM
**Target**: ≤ 3 ticket/mese su 100 clienti (PMI Italia non-tecnici)
**Stack**: Tauri 2.x + Python sidecar PyInstaller + Edge-TTS + Groq proxy
**Pricing context**: €497–897 lifetime → ogni cliente irritato = chargeback rischio reale
**Output**: ricerca + raccomandazioni (NO implementazione)

---

## 1. Matrice cause-failure ranked (Win + macOS)

Stima percentuale derivata da: GitHub issues PyInstaller/Tauri, ticket Resilio/nTop/Anything-LLM, esperienza founder S184 α.1/α.2, distribuzione mercato Italia (~80% Win / ~15% Mac / ~5% altro).

### Windows (~80% installazioni)

| # | Causa | % stimata | Severity | Soluzione preventiva (FLUXION) | Stato attuale |
|---|-------|-----------|----------|--------------------------------|---------------|
| W1 | SmartScreen "Windows protected your PC" (binari unsigned, no reputazione MS) | **~70%** | HIGH (friction primo boot) | Doc visiva + click-through 2-step (Ulteriori info → Esegui comunque) + video timestamp deep link | Coperto α.2 (video 4:21 + come-installare.html) |
| W2 | Defender quarantine voice-agent.exe (PyInstaller false positive) | **~25–35%** | CRITICAL (Sara morta, app inutilizzabile) | `setup-win.bat` Add-MpPreference + `Unblock-File` + submit-VirusTotal pre-release | Script α.2 BLIND-WRITTEN (NON validato VM) — α.3 priority |
| W3 | Antivirus terzo (Norton/Kaspersky/Avast/ESET/Bitdefender) blocca PyInstaller | **~10–20%** | CRITICAL | Submission portali whitelist PRIMA di lancio (Avast/Bitdefender risp. <24h, Norton+Kasp. lenti) + retry monthly | Doc esiste (`av-submission-guide.md` α.2) — submission TODO post v1.0.1 |
| W4 | VC++ Redistributable mancante (Tauri 2.x richiede WebView2 + VC++ 2015–2022) | **~5–10%** | HIGH (crash a freddo senza errore parlante) | MSI bundle WebView2 evergreen bootstrapper + check VC++ in pre-flight wizard | NON coperto — TODO α.3 |
| W5 | Firewall corporate / proxy enterprise blocca CF Worker (proxy LLM) | **~3–8%** | MEDIUM (Sara fallback Piper/template) | First-run network test + UI banner "modalità limitata" (esiste S184 α.2) + doc whitelist domini per IT admin PMI | Modal esiste — manca docs IT admin |
| W6 | Conflitto porta 3001 (Tauri bridge) o 3002 (voice-agent) — Skype/Zoom/Teams legacy | **~2–5%** | MEDIUM (voice down, gestionale OK) | Port-scan a startup + auto-fallback porte 3010-3020 + log telemetry | NON coperto — TODO α.3 |
| W7 | Path Unicode/spazi profilo utente ("Mario D'Angelo", "Salone Süd") | **~1–3%** | HIGH (PyInstaller temp dir crash) | Test E2E con username Unicode + path validation pre-install | NON coperto — TODO α.3 |
| W8 | User non-admin tenta install MSI (PMI con IT esterno restrittivo) | **~5–10%** | MEDIUM (UAC fallisce silenzioso) | MSI per-user fallback + messaggio chiaro "richiede admin" + email founder con istruzioni IT | Parziale — TODO documentare |
| W9 | Disk full / antivirus quarantena dopo install (non al primo run) | **~1%** | LOW | Health check periodico + auto-restart + user notification | NON coperto |
| W10 | OneDrive/cloud sync corrompe DB SQLite WAL in Documents | **~2–3%** | CRITICAL (data loss) | DB in `%LOCALAPPDATA%\Fluxion\` (NON sync) + doc esplicita | DA VERIFICARE Tauri bundle path |

### macOS (~15% installazioni)

| # | Causa | % stimata | Severity | Soluzione preventiva | Stato attuale |
|---|-------|-----------|----------|----------------------|---------------|
| M1 | Gatekeeper "non verificato" (ad-hoc signing, no Apple Developer ID €99/anno) | **~90%** primo run | HIGH | DMG con `setup-mac.command` xattr -dr quarantine (esiste α.2) + video CTA visiva | Coperto |
| M2 | Apple Silicon vs Intel (voice-agent build solo x86_64 S177) | **~50%** Mac users | CRITICAL su ARM puro (Rosetta 2 fallback) | Universal Binary build (richiede arm64 PyInstaller) | TODO S183-bis tech debt |
| M3 | macOS 12 (Monterey) vs 14+ — API differences (microfono permission flow) | **~5%** | MEDIUM | Min-version check installer + UI parlante | NON coperto |
| M4 | Microfono permission negata accidentalmente (Sara muta, no errore parlante) | **~15%** | HIGH | First-run wizard test mic con feedback visivo | Modal Network esiste α.2 — manca mic test |
| M5 | iCloud Drive sync DB SQLite | **~3%** | CRITICAL | DB in `~/Library/Application Support/Fluxion/` (esclusa da iCloud) | DA VERIFICARE |

### Critical takeaway
- **W2 + W3 + M2 = 60% dei ticket potenziali**. Investire qui prima di qualsiasi altra cosa.
- **W4 (VC++/WebView2)** = silent killer: crash senza messaggio = ticket "non parte" → 30 min support per ogni occorrenza.
- **W7 (path Unicode)** = bug latente che esplode su Marco D'Angelo, Salone Süd, Officina Èxtrasud → impossibile riprodurre senza VM dedicata.

---

## 2. Pre-flight Wizard pattern (gold standard 2026)

### Pattern leader benchmarked

**1Password** — diagnostics report scaricabile button, browser extension health check con codice colore.
**Bitwarden** — connection test esplicito a server prima di login.
**Discord** — auto-detect firewall block + UI parlante "Sembra che il firewall ti blocchi, clicca qui".
**Spotify** — proxy auto-detect, fallback browser-player se desktop fallisce.
**Linear desktop** — progressive enhancement: app funziona offline, sync silenzioso quando possibile.
**Notion desktop** — onboarding wizard 4-step ma SKIP visibile (rispetta utenti esperti).

### Mockup wizard FLUXION (8 step, max 90 secondi)

```
┌─ FLUXION First Run ───────────────────────────────────┐
│  Benvenuto Gianluca! Verifico setup in 60 secondi…   │
└────────────────────────────────────────────────────────┘

[ STEP 1 ] Sistema operativo                          → PASS / WARN / FAIL
   ✓ Windows 11 Pro 23H2 (compatibile)
   Condizione PASS:  win10+ build 19041+, oppure macOS 12+
   Se FAIL:           blocca install + email founder con OS detail

[ STEP 2 ] Architettura CPU                           → PASS / WARN / FAIL
   ✓ x86_64 (Intel/AMD)
   Condizione PASS:  arch supportata da binario corrente
   Se WARN macOS ARM su build x86: avviso Rosetta 2 fallback (latenza Sara +20%)

[ STEP 3 ] Runtime essenziali (Win only)              → PASS / WARN / FAIL
   ✓ WebView2 Runtime 120.0.x
   ✓ VC++ Redistributable 14.40
   Condizione PASS:  versioni minime presenti
   Se FAIL:           link diretto MS download + retry button (NO blocco)

[ STEP 4 ] Permessi disco                             → PASS / FAIL
   ✓ %LOCALAPPDATA%\Fluxion\ scrivibile
   ✓ DB SQLite test write (1KB scratch + delete)
   Se FAIL:           probabile antivirus aggressivo → suggerisci esclusione

[ STEP 5 ] Network — proxy CF                         → PASS / WARN / OFFLINE
   ✓ https://fluxion-proxy.gianlucanewtech.workers.dev/health 200 OK <500ms
   Condizione PASS:  HTTP 200 entro 5s
   Se WARN (>5s):     "modalità limitata", Sara fallback Piper
   Se OFFLINE:        "gestionale OK, voice agent disabilitato"

[ STEP 6 ] Voice-agent sidecar                        → PASS / FAIL
   ✓ voice-agent.exe avviato, /health 200 OK su 127.0.0.1:3002
   Se FAIL su Win:    suggerisci esclusione Defender (link setup-win.bat)
   Se FAIL su Mac:    suggerisci xattr (link setup-mac.command)
   Se porta occupata: tenta 3003 → 3010 fallback automatico

[ STEP 7 ] Microfono                                  → PASS / SKIP / FAIL
   ✓ Permesso accordato + livello audio rilevato (parla "test")
   Condizione PASS:  RMS audio >threshold per ≥1s
   Se SKIP user:      banner persistente "Sara non funzionerà finché non testi mic"
   Se FAIL Mac:       deep-link System Settings > Privacy > Microphone

[ STEP 8 ] DB initial migration                       → PASS / FAIL
   ✓ Schema v1 applicato, 6 tabelle, integrity_check OK
   Se FAIL:           rollback + email founder con SQLite error

──────────────────────────────────────────────────────────
Riepilogo: 8/8 PASS — tutto pronto. [Inizia]
oppure:    6/8 PASS, 2 WARN — usabile in modalità limitata. [Continua]
oppure:    5/8 PASS, 1 FAIL critico — risoluzione richiesta. [Risolvi]
──────────────────────────────────────────────────────────
[ Salva diagnostics report ] [ Invia a fluxion.gestionale@gmail.com ]
```

**Regole UX critiche**:
- MAI bloccare l'app per WARN — solo per FAIL critici (W4, W10, M2 mismatch arch)
- Tasto SKIP visibile su step opzionali (step 7 mic), MAI su step 1/2/4/8
- Output structured JSON in `%LOCALAPPDATA%\Fluxion\diagnostics-{timestamp}.json`
- Bottone "Invia report" allega diagnostics + ultimi 200 righe log + Sentry event_id (se generato)

---

## 3. Self-diagnosis + Auto-fix pattern

### Auto-fix da implementare in MainLayout (background, silent)

| Problema rilevato | Auto-fix tentato | Fallback se fallisce |
|-------------------|------------------|----------------------|
| voice-agent crash 3 volte in 60s | Kill+restart, log Sentry | Banner UI "Sara temporaneamente offline, riprova in 1min" + button "Manda report" |
| Proxy CF timeout >10s ripetuti | Switch a Cerebras endpoint (esiste fallback chain) | Banner "modalità Piper TTS locale" + Sentry breadcrumb |
| Porta 3002 occupata | Auto-bind 3003-3010 + update bridge URL | Modal con elenco processi conflittuali (tasklist Win / lsof Mac) |
| DB SQLite corrupt (PRAGMA integrity_check FAIL) | Auto-restore da backup .db.bak (rolling 3 ultimi) | Modal "Contatta supporto, allegato log + dump" |
| WAL >100MB (db lento) | Auto-checkpoint + VACUUM background | — |
| Disk space <500MB | Banner persistente "Spazio basso, Sara non potrà registrare audio" | — |

### Pattern rifiuto vs. pattern Discord/Spotify
- Discord chiede esplicitamente admin se firewall blocca → buono per **trust**.
- Spotify auto-detect proxy → buono per **silenzio operativo**.
- **FLUXION mix**: silent retry × 3 → se ancora fail, UI parlante (NON modal nag, ma banner dismissibile).

---

## 4. Customer support zero-touch

### "Send report" button — pattern enterprise

```
┌─ Qualcosa non funziona? ──────────────────────────────┐
│  Premi il bottone qui sotto. Riceveremo:              │
│    • Il tuo errore (anonimizzato)                     │
│    • Le ultime 200 righe di log                       │
│    • La configurazione tecnica (no dati cliente)      │
│    • Uno screenshot dello schermo (opzionale)         │
│                                                        │
│  Email risposta entro 24h: fluxion.gestionale@gmail   │
│                                                        │
│  [ Allega screenshot ] [ ✓ Invia diagnostic report ]  │
└────────────────────────────────────────────────────────┘
                                                Event ID: a8c91f...
```

### Cosa allegare automaticamente (privacy-safe)
- Sentry event_id (se errore già catturato)
- OS version, app version, arch
- Voice-agent /health response
- Last 200 log lines (con scrubbing automatico: regex `cliente_\d+`, telefoni `\d{10}`, email `*@*`)
- Diagnostics JSON wizard (vedi §2)
- Hash MD5 binari (per detect tampering / antivirus rimosso file)

### Cosa MAI allegare
- Database SQLite (anche zip — contiene PII clienti)
- Audio recordings (anche cifrati)
- Screenshot senza consenso esplicito click-through

---

## 5. Telemetry opt-in GDPR-compliant

### Best practice (Sentry + GDPR Art. 6 + D.Lgs 196/2003)

**Cosa raccogliere senza consenso esplicito** (legitimate interest art. 6.1.f):
- Error stack traces (anonimizzati, NO PII)
- App version, OS version, arch
- Crash count + crash type
- Install success/fail (binary)

**Cosa raccogliere SOLO con opt-in esplicito** (consent art. 6.1.a):
- Usage analytics (quali feature usate, frequenza)
- Performance metrics dettagliati (latenza per turn FSM)
- Voice-agent transcripts metadata (NO contenuto)
- User feedback widget testo libero

### Comunicazione trasparente — pattern Cal.com/Linear

Modal one-time al primo run dopo wizard:

```
🛡️  Aiutaci a migliorare FLUXION

Possiamo raccogliere dati anonimi su crash e errori per
risolverli più velocemente? Nessun dato cliente viene mai
inviato — solo informazioni tecniche.

  ☑  Crash report automatici (sempre attivi se accetti)
  ☐  Statistiche di utilizzo anonime (puoi disattivare)
  ☐  Feedback bottone "Aiuto" (sempre opzionale)

Puoi cambiare idea in qualsiasi momento da Impostazioni → Privacy.

[ Accetto ]  [ Rifiuto tutto ]  [ Maggiori info → privacy ]
```

**Dettaglio**: `feedback_e2e_test_mode_only.md` MEMORY già copre Stripe TEST mode. GDPR opt-in è un pattern parallelo: defualt-off in EU, default-on US (FLUXION → default-off sempre, mercato 100% Italia).

---

## 6. Documentation pattern PMI Italia

### Cosa esiste (S184 α.2/α.2-bis)
- ✅ Video tutorial install 4:21 dual-OS (`landing/assets/video/fluxion-tutorial-install.mp4`)
- ✅ Pagina `come-installare.html` 488 righe (HTTP 200)
- ✅ Card "errori comuni" 8 cards (S184 α.2)
- ✅ Doc Gatekeeper visiva
- ✅ Email `fluxion.gestionale@gmail.com` come canale primario

### Cosa manca per zero-touch support PMI

1. **In-app contextual help** — bottone `?` accanto a OGNI feature critica → apre overlay con micro-video 15-30s (NO redirect web). Mancare = ticket "come fa Sara a chiudere conversazione?"
2. **FAQ smart in-app** — search box che indicizza FAQ statica + log errori risolti (Karpathy LLM Wiki pattern, vedi §8). Mancare = ticket ripetuti su stessa domanda.
3. **Video tutorial micro per task** (1-2 min cad) — "primo cliente", "primo SMS", "calendario settimanale", "loyalty card stampa". Manca completamente. PMI Italia preferiscono video a testo (verificato S184 α.2-bis su scelta video tutorial).
4. **WhatsApp Business support escalation** — link `wa.me/39...` accanto a "Send report" (gli italiani PMI rispondono 10× più veloci su WA che email).
5. **Onboarding email automation** giorno 0/3/7/14 con tip contestuale (Resend free tier già attivo S179).

### Doc gerarchia consigliata
```
Self-help (in-app, primo livello) — overlay micro-video, FAQ search, wizard troubleshoot
   ↓ 80% problemi risolti qui
Static docs (landing/come-installare + landing/faq) — secondo livello, search Google
   ↓ 15% rimanenti
Email fluxion.gestionale@gmail (con diagnostic report allegato auto)
   ↓ 5% rimanenti
WhatsApp founder direct (per BETA + cliente €897 Pro)
```

---

## 7. Rollback / Uninstall pattern (refund 30gg)

### Requisito legale (D.Lgs 206/2005 art. 59 + Strada 4 S175)
- Cliente che invoca refund 30gg deve poter rimuovere FLUXION **completamente** in <2 min (UX dignitosa).
- DB SQLite con dati clienti = property cliente → export OBBLIGATORIO prima di delete.

### Uninstall script proposal

**Windows** (`uninstall-win.bat` distribuito accanto a setup-win.bat in CF Pages + GitHub Release):
```
1. Detect install via registry "HKLM\...\Uninstall\Fluxion" → MSI uninstall string
2. PROMPT user: "Vuoi esportare i tuoi dati prima di disinstallare? [Sì/No]"
   Se Sì → invoca FluxionExport.exe → genera ZIP in Desktop\Fluxion-export-{date}.zip
                                       (CSV clienti + appuntamenti + impostazioni + DB raw)
3. msiexec /x {GUID-FLUXION} /qn  → uninstall MSI
4. Rimuovi residui: %LOCALAPPDATA%\Fluxion\, %APPDATA%\Fluxion\
5. Rimuovi regola firewall + esclusione Defender
6. Conferma user "Disinstallazione completata. Email refund inviata."
7. Auto-trigger /api/v1/rimborso (esiste S175) con event uninstall=true
```

**macOS** (`uninstall-mac.command`):
```
1. Detect /Applications/Fluxion.app
2. PROMPT export → ~/Desktop/Fluxion-export-{date}.zip
3. mv /Applications/Fluxion.app ~/.Trash/
4. rm -rf ~/Library/Application\ Support/Fluxion/
   rm -rf ~/Library/Caches/com.fluxion.*
   rm -rf ~/Library/Logs/Fluxion/
   rm -rf ~/Library/Preferences/com.fluxion.*
5. Auto-trigger /api/v1/rimborso
```

### Anti-pattern da evitare
- MAI uninstall "silenzioso" senza export → cliente paga lawyer prima di pagare refund.
- MAI lasciare voice-agent.exe orfano residente in TaskManager.
- MAI lasciare regole firewall/Defender exclusion (security debt + ticket future "perché Defender mi dice ancora Fluxion?").

---

## 8. Beta program structured (12 testers, 6 vertical)

### Obiettivo S186-S187 (per ROADMAP_S183_S190 multi-gate)
- **Goal**: trovare 80% dei bug prima del lancio cold-traffic S188.
- **Size**: 12 tester = 6 vertical × 2 tester (1 vertical-leader + 1 follower per redundancy).
- **Durata**: 14 giorni (1 sprint completo S187).

### Selezione testers — criteri PMI Italia

**Profilo ideale** (per ogni vertical):
- 3-10 dipendenti (sweet spot pricing)
- Già usa gestionale digitale concorrente (Treatwell, Wellness Italia, MioClub, GymHero, ecc.) → ha referente di paragone
- Founder/owner accessibile direttamente via WhatsApp (NO IT manager intermedio)
- 1× tech-savvy (early adopter, tollera bug) + 1× tech-naive (rappresentativo di mercato cold)
- Dipendente sul territorio italiano (no expat, lingua madre IT, fuso orario UE)
- ≥ 1 click su landing CF Pages negli ultimi 30gg (proxy interesse genuino)

**Segmentazione 6 vertical (da `src/types/setup.ts`)**:
1. Salone bellezza (parrucchiere/estetista) — vertical più affollato
2. Palestra / studio fitness — pricing-sensitive
3. Clinica / studio medico — privacy-sensitive (test GDPR rigoroso)
4. Officina meccanica — tech-naive estremo (test wizard semplicità)
5. Studio professionale (commercialista/avvocato) — calendar-heavy
6. Centro benessere / SPA — Sara use-case primario (booking complesso)

### Recruiting funnel
```
LinkedIn outreach (iMessage/WA) → 100 contatti vertical-leader
   ↓ 10% positive (10)
Demo call 30min (Zoom o WA video) → 10 candidate
   ↓ 50% match
Selezione 12 (con 2 substitute) → onboarding pack
```

### Onboarding pack (week 0)
- Email founder con video personalizzato 90s (loom)
- DMG/MSI signed download link unico (token GitHub Release)
- 1 ora call group "kick-off" (Discord o Zoom) per allineare aspettative
- Guida private `/beta-guide.html` (gated da token)
- Slack/Discord canale gated (`#fluxion-beta-private`) per support real-time
- WhatsApp gruppo founder + 12 testers (escalation veloce)

### Feedback loop strutturato

**Daily** (passive):
- Sentry events automatici → dashboard founder
- Diagnostic reports auto-allegati a ticket
- Telemetry feature usage (opt-in S5)

**Weekly** (active):
- 30min 1-on-1 Zoom con ogni tester (rotation 2/giorno × 6 giorni = 12 settimanali — rotazione bisettimanale → 6/settimana × 2 settimane)
- Survey strutturato in-app (whimsy-injector style 5 domande):
  1. Cosa hai usato di più questa settimana?
  2. Cosa ti ha frustrato?
  3. Cosa NON hai capito?
  4. Quanto raccomanderesti FLUXION (NPS 0-10)?
  5. Suggerimento aperto

**End-of-beta** (giorno 14):
- Survey lunga 15min (incentive: licenza Pro lifetime gratis se survey completata)
- 1× call collettiva 1h "what worked / what didn't"
- Public testimonial request (case study landing page)

### Success criteria (gate per launch S188)
- ✅ 12/12 install completata senza founder support diretto entro 30 min
- ✅ ≥ 10/12 raggiunge "primo appuntamento creato" entro 24h
- ✅ ≥ 8/12 raggiunge "Sara prima call test" entro 48h
- ✅ Bug critici (P0) = 0 outstanding al giorno 14
- ✅ NPS medio ≥ 40 (B2B SaaS benchmark)
- ❌ Se anche solo 1 NON soddisfatto → rinvia launch S189

### Bonus: helpdesk auto-generato Karpathy LLM Wiki pattern

**Architettura proposta** (S185 roadmap già pianificato in MEMORY):
```
raw/ ← logs Sentry + ticket WA + diagnostic reports + survey responses
     (immutabile, append-only)
   ↓ ingest (claude-code daily run via cron)
wiki/ ← markdown auto-generato:
       - errori-comuni/{categoria}.md (con frequenza + soluzione + first seen)
       - vertical/{salone,palestra,...}/playbook.md
       - faq-auto/{domanda-canonica}.md (con backlinks a casi reali)
       - install-troubleshooting/{W1,W2,...}.md
   ↓ query (in-app FAQ search → MCP a wiki/)
risposte cliente con citazioni a casi reali precedenti
```

**Differenza chiave da RAG classico** (per VentureBeat 2026 + gist Karpathy):
RAG re-deriva ad ogni query → Wiki compone una sola volta in ingest, knowledge persistente che cresce.

**Esempio uso B2B applicato a FLUXION**:
- Tester salone Marco riporta "Sara non chiude conversazione" → ingest → wiki/voice-fsm/asking-close-confirmation.md aggiornato → tester palestra Lucia 3 giorni dopo cerca FAQ "Sara non finisce" → wiki risponde con risposta strutturata + link a Marco's case.

**Lint operations** (settimanale, founder review):
- Detect contradictions (versione 1.0.1 dice X, 1.0.2 dice Y)
- Stale claim flagging (ticket non aggiornati >30gg)
- Orphan FAQ (mai citate da nessun cliente → da deprecare)

**Implementation cost**: Karpathy gist 442a6bf è ~150 linee bash + CLAUDE.md. Estensione FLUXION = +1 cron daily + 1 MCP server custom. Effort stimato S185: ~12h come da MEMORY.

---

## 9. TOP 7 raccomandazioni implementabili PRIMA di α.3 VM test

Ordinate per impact/effort ratio.

### #1 — Validare `setup-win.bat` su VM Win11 vergine (P0, effort: 4h)
**Why**: blind-written α.2, MAI testato. Probabile bug PowerShell escape o Defender policy aziendale (Add-MpPreference fallisce silenzioso se MS Defender è managed).
**How**: snapshot UTM "vanilla-win11" → copy MSI + bat → eseguire → verificare 4 punti (Defender exclusion presente, Unblock-File OK, firewall rule presente, log scritto).
**Acceptance**: 4/4 PASS su Win11 vergine + 1 retest su Win10 22H2.

### #2 — Pre-flight wizard 8-step (P0, effort: 8h)
**Why**: copre 60% dei ticket potenziali a costo di 8h dev. Pattern industry standard (Notion/1Password/Bitwarden).
**How**: nuovo `src/components/PreflightWizard.tsx` integrato in App.tsx pre-MainLayout, riusando `use-network-health.ts` α.2 + nuovi hook `use-system-health.ts` (W1-W8 check).
**Acceptance**: tutti 8 step completano in ≤90s; output JSON salvato su disco; "Send report" funziona E2E.

### #3 — VirusTotal pre-release submission automated (P0, effort: 2h)
**Why**: detect false positive PRIMA di lancio (vs scoprirlo da cliente paganti). Usato da Tauri community.
**How**: GitHub Actions step post-build: upload MSI + voice-agent.exe a VT API → fail build se >2 vendor flag. Free tier 4 req/min sufficiente.
**Acceptance**: workflow CI green = 0 false positive top-15 AV vendors.

### #4 — Diagnostic report "Send button" + auto-attach (P0, effort: 6h)
**Why**: trasforma "non funziona" generico in ticket actionable. Riduce tempo support 80%.
**How**: nuovo Tauri command `generate_diagnostic_report` → JSON + log scrub regex → POST a Sentry user feedback endpoint o email founder via Resend.
**Acceptance**: 1 click → email a founder con allegato JSON + 200 log lines + Sentry event_id.

### #5 — Validare DB path FUORI da iCloud/OneDrive sync (P0, effort: 1h)
**Why**: data loss critico se DB in `Documents/` o `iCloud/`. Verifica Tauri 2 default path.
**How**: ispezionare `src-tauri/tauri.conf.json` + path runtime su VM Win11 (con OneDrive attivo) e Mac (con iCloud attivo).
**Acceptance**: DB SQLite in `%LOCALAPPDATA%\Fluxion\` (Win) e `~/Library/Application Support/Fluxion/` (Mac), entrambi NON sincronizzati.

### #6 — VC++ Redistributable + WebView2 bundling (P1, effort: 4h)
**Why**: silent killer su Win10 fresh install. Tauri 2 doc raccomanda bootstrapper.
**How**: configurare `tauri.conf.json` `windows.webviewInstallMode: "embedBootstrapper"` + ship VC++ redist nel MSI (WiX custom action).
**Acceptance**: install su Win10 fresh OOBE (no internet pre-install) completa senza errore.

### #7 — Uninstall script `uninstall-win.bat` + `uninstall-mac.command` con export (P1, effort: 4h)
**Why**: requisito legale refund 30gg + UX dignitosa. Evita 1-star reviews.
**How**: vedi proposal §7. Distribuiti nel DMG + MSI install dir.
**Acceptance**: cliente test completa "uninstall + export + refund" in <2min, file ZIP valido, voice-agent.exe non residente.

**Effort totale top 7**: ~29h ≈ 1 sprint focalizzato.

---

## 10. Cosa NON fare (anti-pattern raccolti dalla ricerca)

- ❌ NO EV certificate Win €250-700/anno (rompe ZERO COSTI). Ripiegare su SmartScreen reputation building (10-100 install organici → reputazione MS).
- ❌ NO Apple Developer ID €99/anno (idem). Restare ad-hoc + Gatekeeper doc.
- ❌ NO modal blocking onboarding (Notion docet: SKIP visibile).
- ❌ NO telemetry default-on senza consenso GDPR (Insomnia issue Kong/insomnia#7751 docet — class action risk).
- ❌ NO dipendere da WhatsApp founder per support primario (single point of failure → vacanze = clienti morti).
- ❌ NO submission AV solo a Defender (ESET + Norton coprono 30% Italia PMI).
- ❌ NO testare solo VM Apple Silicon se mercato è 80% Win Intel (verificato S183-bis MEMORY).

---

## Sources

**Install failures Windows**:
- [Resilio SmartScreen troubleshooting](https://www.resilio.com/documentation/content/troubleshooting/general/windows_defender_smartscreen_blocks_management_console_installer/)
- [BEMO Pro SmartScreen blocking](https://support.bemopro.com/hc/en-us/articles/11450999280531)
- [Anything-LLM SmartScreen issue #1469](https://github.com/Mintplex-Labs/anything-llm/issues/1469)
- [Tauri MSI false positive issue #4749](https://github.com/tauri-apps/tauri/issues/4749)
- [PyInstaller false positive issue #6754](https://github.com/pyinstaller/pyinstaller/issues/6754)
- [PyInstaller antivirus fix guide](https://www.pythonguis.com/faq/problems-with-antivirus-software-and-pyinstaller/)
- [Mark Hank — stop Python programs being seen as malware](https://medium.com/@markhank/how-to-stop-your-python-programs-being-seen-as-malware-bfd7eb407a7)

**First-run wizard / health checks**:
- [Microsoft Wizards Design Guidelines](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/bb246463(v=vs.85))
- [Lollypop — Wizard UI Design 2026](https://lollypop.design/blog/2026/january/wizard-ui-design/)
- [Better Stack health checks guide](https://betterstack.com/community/guides/monitoring/health-checks/)
- [Artkai software health check best practices](https://artkai.io/blog/app-healthcheck)
- [Azure Health Endpoint Monitoring pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/health-endpoint-monitoring)

**Sentry / GDPR telemetry**:
- [Sentry User Feedback widget](https://sentry.io/for/user-feedback/)
- [Sentry GDPR data requests](https://sentry.io/contact/gdpr/)
- [Insomnia GDPR issue #7751](https://github.com/Kong/insomnia/issues/7751)

**Beta program B2B**:
- [Ubertesters — B2B beta best practices](https://ubertesters.com/blog/b2b-beta-testing-key-challenges-and-proven-best-practices/)
- [BetaTesting B2B platform](https://betatesting.com/b2b)
- [Patrick Frank — beta testing frameworks SaaS](https://www.patrickfrank.com/post/beta-testing-frameworks-saas-startups)
- [Fluvio — establish successful beta program](https://www.fluviomarketing.com/blog-summary/how-to-establish-a-successful-beta-program)
- [Rapidr — manage feedback from beta testers](https://rapidr.io/blog/manage-feedback-from-beta-testers/)

**Karpathy LLM Wiki**:
- [Karpathy gist 442a6bf](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [VentureBeat — Karpathy LLM Knowledge Base architecture](https://venturebeat.com/data/karpathy-shares-llm-knowledge-base-architecture-that-bypasses-rag-with-an)
- [MindStudio — LLM Wiki guide](https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-knowledge-base-claude-code)
- [Kunal Ganglani — LLM Wiki 2026 guide](https://www.kunalganglani.com/blog/llm-wiki-karpathy-local-knowledge-base)
- [lucasastorian/llmwiki open-source impl](https://github.com/lucasastorian/llmwiki)

**Uninstall pattern**:
- [Macpaw — completely uninstall apps](https://macpaw.com/how-to/uninstall-apps-on-mac)
- [ManageEngine — MSI uninstall](https://www.manageengine.com/products/desktop-central/help/software_installation/uninstall_msi_software.html)
- [Geek Uninstaller](https://geekuninstaller.com/)

**Tauri sidecar best practices**:
- [Tauri sidecar embedding external binaries](https://v2.tauri.app/develop/sidecar/)
- [Tauri Python sidecar discussion #2759](https://github.com/tauri-apps/tauri/discussions/2759)
