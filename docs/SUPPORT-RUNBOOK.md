# FLUXION Support Runbook (S187 F-2)

**Versione**: 1.0  
**Data**: 5 maggio 2026  
**Target**: Founder (Gianluca Di Stasi) — single-operator support  
**Canale**: fluxion.gestionale@gmail.com (Gmail, no helpdesk SaaS)  
**SLA**: Prima risposta <24h business | Risoluzione P0 <4h | Risoluzione P1 <24h | P2 <72h

---

## Indice

1. [Mission](#mission)
2. [Triage Matrix](#triage-matrix)
3. [Canale Flow](#canale-flow)
4. [Top 20 Issue con Fix & Template](#top-20-issue)
5. [Email Template Library](#email-template-library)
6. [Knowledge Base Linking](#knowledge-base-linking)
7. [Escalation Tree](#escalation-tree)
8. [Metrics & Review](#metrics--review)

---

## Mission

FLUXION support automatizzato per ridurre carico founder e risolvere 80%+ issue senza intervento manuale.

### Vincoli operativi
- **Founder è solo**: nessun team support. Automazione + template = chiave SLA gestibile.
- **Zero-cost stack**: Resend free tier (100/giorno), Gmail, Wiki helpdesk privato, CF Workers.
- **Cliente PMI NON-tecnico**: empatia prima, no jargon, procedure concrete step-by-step.
- **Tono**: formale-cordiale, "tu" sempre, firma "Gianluca — Team FLUXION".
- **Garanzia**: 30gg soddisfatti o rimborsati (D.Lgs 206/2005), refund via Stripe <5-10 gg lavorativi.

### Target SLA

| Priorità | Definizione | Response | Resolution |
|----------|------------|----------|------------|
| **P0** | App non si apre / pagamento fail / data loss / crash | <1h | <4h |
| **P1** | Sara non risponde / WhatsApp fail / offline mode fail | <4h | <24h |
| **P2** | UI glitch / feature request / minor bug | <24h | <72h |
| **P3** | Domande generiche / documentazione | <48h | asincrone |

---

## Triage Matrix

**Quando arriva email a fluxion.gestionale@gmail.com**:

1. **STEP 1 — Leggi email** (1 min)
   - Estrai: nome cliente, versione FLUXION (se menciona), SO (Win/Mac), tier (trial/Base/Pro)
   - Identifica keyword problema (crash, offline, Sara, WhatsApp, licenza, backup, etc.)

2. **STEP 2 — Classifica severità** (30 sec)
   - **P0 keywords**: "non si apre", "crash", "pagamento fallito", "dati persi", "rimborso", "GDPR data subject"
   - **P1 keywords**: "Sara non risponde", "WhatsApp offline", "latenza >3s", "microfono non sente"
   - **P2 keywords**: "glitch", "lento", "UI", "esportare dati", feature request, domanda generica
   - **P3 keywords**: "come faccio", "info", "documentazione"

3. **STEP 3 — Mappa a Issue ID** (2 min)
   - Vedi sezione [Top 20 Issue](#top-20-issue): quale numero rispecchia il problema?
   - Se issue non in top-20: crea nota privata in Gmail label `FLUXION/custom`, rispondi con template generico (vedi sezione [Template Library](#email-template-library))

4. **STEP 4 — Esegui fix / diagnosi** (da 5 min a 1h a seconda P0/P1/P2)
   - Leggi issue-specific diagnosis in sezione Top 20
   - Invia email con fix step-by-step (vedi template per ogni issue)
   - Se servono dati cliente (screenshot, log, versione app): chiedi esplicitamente

5. **STEP 5 — Aggiorna label + archive** (30 sec)
   - Marca email con label `FLUXION/P0`, `FLUXION/P1`, `FLUXION/P2`
   - Se risolto: aggiungi label `FLUXION/resolved`
   - Archive (non delete — serve audit log per 10 anni D.Lgs 206/2005)

---

## Canale Flow

```
Email arriva fluxion.gestionale@gmail.com
    ↓
[TRIAGE 2 min] — Leggi + classifica severità + mappa issue ID
    ↓
[IF P0 + non risolvibile <1h] → ESCALATION TREE (sezione 7)
[IF P0/P1 + risolvibile] → Esegui fix/diagnosi + invia template
[IF P2/P3] → Rispondi con template entro 24h
    ↓
[FOLLOW-UP] — Se cliente non risponde entro 3 giorni: invia reminder (vedi template "follow-up day-3")
    ↓
[RESOLUTION] — Marca `FLUXION/resolved` + archive + log in METRICS (sezione 8)
```

---

## Top 20 Issue

### CATEGORIA A — INSTALLAZIONE (4 issue)

#### **ISSUE A1: SmartScreen blocca installer Windows**

**Severità**: P1 (blocca installazione ma fix immediato)

**Sintomi**:
- Cliente clicca Fluxion_1.0.1_x64-setup.exe → SmartScreen mostra "Windows ha protetto il tuo PC"
- Messaggio: "Microsoft Defender SmartScreen. Il programma è stato bloccato."

**Diagnosi**:
- Installer FLUXION è unsigned (vincolo zero-cost code signing — S184 closure).
- SmartScreen è protezione legittima, ma installer è autentico.
- Fix è 3-click guidato.

**Fix Step-by-Step**:
1. Schermata SmartScreen: click "Maggiori informazioni" (tasto in basso)
2. Appare secondo tasto: "Esegui comunque"
3. Click "Esegui comunque" → installer procede
4. NSIS pre-flight checks automatici → Installazione

**Documentazione reference**:
- Wiki: `docs/helpdesk-wiki/wiki/entities/win10-installation.md` § "Errori comuni" → SmartScreen blocca esecuzione
- Landing FAQ: `https://fluxion-landing.pages.dev/faq.html#faq-smartscreen` (TODO update landing F-1)

**Email Template**: [Vedi A1 nella sezione Template Library](#template-a1-smartscreen-blocca-installer)

---

#### **ISSUE A2: Mac Gatekeeper rifiuta app (non verificata da Apple)**

**Severità**: P1 (blocca apertura Mac)

**Sintomi**:
- Cliente doppio-click Fluxion.app → macOS mostra: "Fluxion cannot be opened because it is from an unidentified developer"
- Bottone "Cancel" è l'unico visibile

**Diagnosi**:
- FLUXION è ad-hoc signed (vincolo zero-cost — S184 closure), NON firmato Apple notarize.
- Gatekeeper è protezione legittima per app non-notarizzate.
- Fix è 3-click Finder + Sistema.

**Fix Step-by-Step**:
1. Finder → vai in Applications → trovi Fluxion.app
2. **Tasto destro mouse** su Fluxion.app → "Apri"
3. Dialogo Gatekeeper: click "Apri" (bottone presente con tasto destro, non con doppio-click)
4. macOS ricorda e non chiede più dopo primo avvio

**Alternativa (Terminal per utenti tech)**:
```bash
xattr -d com.apple.quarantine /Applications/Fluxion.app
```

**Documentazione reference**:
- Wiki: (TODO ingest Mac Gatekeeper in S185-bis)
- Landing FAQ: `https://fluxion-landing.pages.dev/faq.html#faq-mac-gatekeeper`

**Email Template**: [Vedi A2 nella sezione Template Library](#template-a2-mac-gatekeeper-rifiuta-app)

---

#### **ISSUE A3: Antivirus quarantena fluxion.exe (falso positivo)**

**Severità**: P1 (blocca avvio app)

**Sintomi**:
- Cliente installa FLUXION su Win10
- Defender/Avast/Norton quarantena `fluxion.exe` o `voice-agent.exe`
- Errore: "Malware detected: Win32/PUA.Fluxion" (inesatto)

**Diagnosi**:
- Installer è unsigned (zero-cost). Alcuni AV flaggano qualsiasi unsigned executable come "potenzialmente pericoloso".
- FLUXION è autentico (verificabile su VirusTotal).
- Fix è whitelisting cartella in AV.

**Fix Step-by-Step**:
1. **Universale**: Aprire AV → Impostazioni → Esclusioni (o Whitelist) → Aggiungi cartella
   - Percorso: `C:\Users\[USERNAME]\AppData\Local\fluxion` (installer standard)
   - Se custom path: chiedi al cliente dove ha installato
2. **Windows Defender specifico**: Impostazioni → Virus e protezione dalle minacce → Gestisci impostazioni → Aggiungi esclusioni → Cartella
3. **Verifica**: doppio-click Fluxion_1.0.1_x64-setup.exe → dovrebbe procedere senza blocco
4. **Second opinion**: Visita https://www.virustotal.com/ → carica `fluxion.exe` → risultato: ~60 AV flaggano falso positivo, nessuno reale malware

**Tech debt**: Submit FLUXION official SHA256 a VirusTotal per ridurre false positive post-S185-bis.

**Email Template**: [Vedi A3 nella sezione Template Library](#template-a3-antivirus-falso-positivo)

---

#### **ISSUE A4: Voice-agent.exe bloccato firewall Windows**

**Severità**: P1 (Sara non funziona)

**Sintomi**:
- Cliente installa FLUXION Pro
- Avvia app → Sara non risponde / timeout
- Task Manager: processo `voice-agent.exe` attivo, ma porta 3002 unreachable

**Diagnosi**:
- Installer ha eseguito `setup-win.bat` (firewall rules localhost 3001/3002)
- Client firewall Windows o corporate proxy blocca comunque
- Setup batch NON ha richiesto admin (esecuzione best-effort, silent fail se no perms)

**Fix Step-by-Step**:
1. **Verifica processo**: Task Manager → Dettagli → cerca `voice-agent.exe`
   - Se assente: Sara sidecar non è partito → Restart app
   - Se presente: continua step 2
2. **Test porta locale**: click Start → digita `cmd` → esegui:
   ```
   netstat -an | find "3002"
   ```
   - Se nulla: porta bloccata firewall
3. **Whitelist manuale**:
   - Start → "Windows Defender Firewall with Advanced Security"
   - Inbound Rules → New Rule → Program → Browse → naviga `C:\Users\[USERNAME]\AppData\Local\fluxion\voice-agent.exe`
   - Action: Allow
   - Apply all profiles (Domain, Private, Public)
4. **Restart FLUXION** → Sara dovrebbe rispondere in ~1s

**Alternative (corporate firewall)**:
- Se IT manager blocca persino localhost: contatta founder (escalation P0)

**Documentazione reference**:
- Wiki: `docs/helpdesk-wiki/wiki/entities/network-firewall.md` § "Errori comuni" → Sara offline

**Email Template**: [Vedi A4 nella sezione Template Library](#template-a4-voice-agent-firewall-bloccato)

---

### CATEGORIA B — ATTIVAZIONE LICENZA (3 issue)

#### **ISSUE B1: License key "non valida" al primo avvio**

**Severità**: P0 (app non funziona senza attivazione)

**Sintomi**:
- Cliente installa FLUXION → Setup Wizard chiede license key
- Copia-incolla key da email → Errore: "License key non valida"
- Retry ripetuti, stessa errore

**Diagnosi**:
- **Typo paste** (98% casi): key contiene spazi, caratteri male copiati, troncata
- **Key scaduta**: typo email → license per altro cliente
- **Hardware fingerprint mismatch**: cliente installa su PC diverso da quello di acquisto (molto raro primo avvio)

**Fix Step-by-Step**:
1. **Chiedi conferma email acquisto**: "Che email hai usato per Stripe Checkout?"
2. **Cerca license email**: chiedi al cliente di cercare in Gmail inbox/spam: mittente `onboarding@resend.dev`, oggetto "FLUXION License Key"
3. **Se email non trovata**: risponi con template "Email license non arrivata" (ISSUE B2 sotto)
4. **Se trovata**: aiuta cliente a **ricopiare key senza spazi**:
   - Template email includa: "Copia SOLO i 88 caratteri tra le due righe trattini. Evita spazi all'inizio/fine."
   - Key format: base64 ~88 char, NO spazi
5. **Se typo confermato ma ripete errore**: hardware fingerprint mismatch → founder genera nuova key manuale (vedi ESCALATION)

**Documentazione reference**:
- Wiki: `docs/helpdesk-wiki/wiki/entities/license-key.md` § "Errori attivazione"

**Email Template**: [Vedi B1 nella sezione Template Library](#template-b1-license-key-non-valida)

---

#### **ISSUE B2: Email license non arrivata (spam/junk)**

**Severità**: P1 (blocca attivazione)

**Sintomi**:
- Cliente completa Stripe Checkout
- Aspetta email license (da `onboarding@resend.dev`)
- Inbox vuota, email non trovata nemmeno in spam

**Diagnosi**:
- **Email spam filter** (80% casi): Resend free tier da `onboarding@resend.dev` non whitelistata. Gmail/Outlook/Libero filtri aggressivi.
- **Ritardo Resend** (<1%, <5 min di lag): webhook Stripe → Resend latenza temporanea
- **Typo email checkout**: cliente ha scritto email errata in Stripe

**Fix Step-by-Step**:
1. **Chiedi email usata in Stripe**: "Che email esatta hai usato in Stripe Checkout?"
2. **Verifica spam/junk**: cliente va in account email → cartella Spam/Junk → cerca `onboarding@resend.dev`
   - Se trovato: Mark as Not Spam → chiedi se è arrivata in inbox (dovrebbe spostarsi)
3. **Se assolutamente non trovata**: founder ricerca manualmente in Stripe dashboard (vedi ESCALATION)
4. **Se ritardo <1h**: chiedi di attendere, poi retry

**Workaround S298 (recovery URL permanente HMAC-SHA256)**:

Da S295/S296 ogni purchase ha **recovery URL deterministico** + **success page inline payload** + **D1 row autoritativa**. Workflow operatore support:

1. **Verifica D1 row** (test env esempio):
   ```bash
   EMAIL="cliente@example.com"
   zsh -c 'source ~/.claude/.env; export CLOUDFLARE_API_TOKEN; \
     npx wrangler d1 execute fluxion-webhook-events-test --env test --remote \
       --command "SELECT license_id, product, email_sent_at, created_at \
                  FROM webhook_events WHERE customer_email='"'"'"$EMAIL"'"'"' \
                  ORDER BY created_at DESC LIMIT 1;"'
   ```
   - `email_sent_at IS NULL` → email NON inviata. Re-trigger replay (sub-step a).
   - `email_sent_at = <unix>` → email inviata. Recovery URL valido (sub-step b).
   - No row → no purchase. Stripe dashboard verify customer.

2a. **Re-trigger replay email** (FSAF-05 idempotent, sicuro su row esistente):
   ```bash
   stripe events resend evt_xxxxxxxxxxxxxx --webhook-endpoint we_xxx
   ```
   Handler `stripe-webhook.ts` riconosce replay, set `email_sent_at = unixepoch()` se NULL al replay.

2b. **Re-compute recovery URL** (HMAC-SHA256 deterministic):
   ```bash
   EMAIL="cliente@example.com"
   SECRET=$(tail -1 ~/.claude/.env.s295-recovery-secret | tr -d '\n ')
   TOKEN=$(python3 -c "import hmac, hashlib; print(hmac.new('$SECRET'.encode(), '$EMAIL'.lower().encode(), hashlib.sha256).hexdigest())")
   echo "https://fluxion-proxy-test.gianlucanewtech.workers.dev/api/v1/license/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$EMAIL'))")?token=$TOKEN"
   ```
   Endpoint risponde JSON: `{license_id, tier, license_payload, license_signature, issued_at}` → cliente attiva via Settings → License Manager → tab "Attivazione manuale" (Tauri `verify_license_signature_v1` Rust dalek).

3. **Verify activate-by-payload Rust path** (S298 smoke E2E verified):
   - Worker `/api/v1/verify` WebCrypto: `valid:true` payload S298 fresco
   - Rust `verify_license_signature_v1` (`ed25519-dalek::verify_strict`): 8/8 test PASS interop dalek↔WebCrypto S291
   - Migration `0002_webhook_events_recovery_index.sql` composite index `(customer_email, created_at DESC)` → recovery query `EXPLAIN QUERY PLAN: SEARCH USING INDEX` (S298 verified test D1).

**Email Template**: [Vedi B2 nella sezione Template Library](#template-b2-email-license-non-arrivata)

**Documentazione reference**:
- Wiki: `docs/helpdesk-wiki/wiki/entities/license-key.md` § "Errori attivazione"
- `fluxion-proxy/src/routes/license-recovery.ts` (recovery HMAC endpoint)
- `fluxion-proxy/src/routes/checkout-success.ts` (success page inline payload)
- `fluxion-proxy/migrations/0002_webhook_events_recovery_index.sql` (S298 composite index)

---

#### **ISSUE B3: Trasferire licenza su altro PC (cambio device)**

**Severità**: P2 (cliente vuole usare FLUXION su altro PC)

**Sintomi**:
- Cliente: "Ho comprato FLUXION su Win10 (PC ufficio), ma voglio usarlo sul portatile. Come faccio?"
- O: "Ho cambiato PC, come attivo su nuovo?"

**Diagnosi**:
- License è bound a hardware fingerprint (hostname + CPU + RAM + OS)
- Cambio PC → fingerprint diverso → "Hardware fingerprint mismatch" errore
- Vincolo: max 2 attivazioni per tier per ridurre reselling. Politica FLUXION.

**Fix Step-by-Step**:
1. **Spiegazione empatica**: "Capisco, supportiamo max 2 device per licenza — è una policy antipirateria ma mantiene il prezzo basso. Se due non bastano, dimmi e troviamo soluzione."
2. **Disattivazione vecchio PC**:
   - FLUXION → Impostazioni → Licenza → Disattiva (se UI supporta, altrimenti chiedi di disinstallare)
   - Founder noter la disattivazione nel log (Firebase event optional per v1.1)
3. **Attivazione nuovo PC**:
   - Installa FLUXION su nuovo PC
   - Setup Wizard → Paste stessa license key da email
   - Se ancora "mismatch": founder genera override manuale (vedi ESCALATION)
4. **Limite**: spiegare che terza attivazione richiede acquisto nuova license

**Documentazione reference**:
- Wiki: `docs/helpdesk-wiki/wiki/entities/license-key.md` § "Hardware fingerprint bound"

**Email Template**: [Vedi B3 nella sezione Template Library](#template-b3-trasferire-licenza-device)

---

### CATEGORIA C — FUNZIONALITÀ (4 issue)

#### **ISSUE C1: Calendario non sincronizza operatori (multi-user)**

**Severità**: P1 (core feature CRM)

**Sintomi**:
- Cliente con salone 3 operatori: "Ho caricato calendar in FLUXION, ma solo il mio utente vede gli slot. Gli altri 2 operatori non vedono nulla."
- Oppure: "Quando fisso appuntamento da tablet, non mi aggiorna sul PC principale."

**Diagnosi**:
- FLUXION **NON supporta sync real-time multi-device** in v1.0 (tech debt futuro)
- SQLite locale → nessun cloud sync
- Ogni device ha DB indipendente
- Soluzione: backup/restore manuale giornaliero O utilizzo single device master

**Fix Step-by-Step**:
1. **Comunicazione realistica**: "In v1.0 FLUXION è single-device per database. Per team con più operatori, raccomandiamo un PC master in ufficio (sempre acceso) che gli altri consultano remotamente (TeamViewer/AnyDesk gratis) O attendete v1.1 sync cloud opzionale (Q4 2026)."
2. **Workaround attuale**:
   - Option A (Team 1-2 persone): Un PC master in ufficio. Ogni mattina operatori sincronizzano visualmente (leggono agenda PC master su monitor condiviso/tablet).
   - Option B (Team 3+): Spreadsheet Google Sheets parallelo per agenda (finché non arrivi v1.1). Fondatore consulta FLUXION, digita manualmente in Sheets, il resto del team legge Sheets.
   - Option C (Enterprise): Aspetta Q4 2026 v1.1 cloud sync opzionale (non gratuito, tier Enterprise €X/mese).
3. **Tech debt**: scheduler sync tra device = P1 futuro roadmap

**Email Template**: [Vedi C1 nella sezione Template Library](#template-c1-calendario-non-sincronizza)

---

#### **ISSUE C2: Fattura SDI rifiutata (Agenzia Entrate)**

**Severità**: P0 (impact fiscale cliente)

**Sintomi**:
- Cliente: "Ho fatturato con SDI tramite FLUXION. L'Agenzia Entrate rifiuta la fattura: 'Errore XML campo [x]'."
- O: "Il cliente dice che non ha ricevuto fattura, ma io l'ho inviata tramite SDI."

**Diagnosi**:
- **Schema XML FatturaPA non conforme** (30% casi): FLUXION v1.0 usa generatore stock che non supporta edge cases (Reverse Charge, sconto merce, ritenuta d'acconto, etc.)
- **Dati cliente incompleti** (40% casi): FLUXION richiede partita IVA validata — se cliente l'ha digitata male, SDI scarta
- **Nominativo indirizzo formato** (20% casi): indirizzo FLUXION non rispetta standard FatturaPA (lunghezza campi, caratteri speciali)
- **Timeout invio SDI** (10% casi): SDI temporaneamente down, retry automatico fallito

**Fix Step-by-Step**:
1. **Chiedi error code Agenzia Entrate**: "Quale errore specifico ha dato l'Agenzia? (es. NS0428, NS0429, …)"
2. **Diagnosi per error code**:
   - **Partita IVA invalida** (NS0427): chiedi conferma P.IVA cliente (formato: 11 cifre IT + P.IVA)
   - **CAP/Indirizzo invalido** (NS0430): verifica indirizzo cliente in FLUXION: città, CAP, indirizzo senza caratteri speciali proibiti
   - **Importi incongruenti** (NS0429): chiedi di stornare fattura in FLUXION, rifare con importi verificati
3. **Se bug FLUXION confermato** (schema XML non conforme):
   - Storna fattura da FLUXION
   - Genera PDF + invia manualmente tramite Aruba/Fatture in Cloud (tools SDI third-party)
   - Report bug a founder: email `[FLUXION BUG]` titolo

**Documentazione reference**:
- Wiki: (TODO ingest SDI error mapping in S185-bis)
- [Agenzia Entrate docs FatturaPA](https://www.agenziaentrate.gov.it/portale/web/guest/aree-tematiche/fatturazione-elettronica)

**Email Template**: [Vedi C2 nella sezione Template Library](#template-c2-fattura-sdi-rifiutata)

---

#### **ISSUE C3: WhatsApp Business template non approvato da Meta**

**Severità**: P1 (Pro feature, bloccante per reminder)

**Sintomi**:
- Cliente Pro attivo: "Ho aggiunto numero WhatsApp Business in FLUXION, scelto template reminder (es. 'Appuntamento domani'), ma Meta dice 'Pending Approval'. A che punto siamo?"
- Oppure: "Dopo 24h ancora 'Pending', non posso mandare reminder."

**Diagnosi**:
- FLUXION usa WhatsApp Cloud API (Meta Business Account) — i template di reminder (messaggi non-conversazionali) devono approvazione Meta (SLA Meta: 24h, a volte >48h)
- Cliente ha connesso WhatsApp ma NON creato Business Account o non ha ID template corretto
- FLUXION mostra status approvazione ma UI NON auto-retry (tech debt minore)

**Fix Step-by-Step**:
1. **Verifica Business Account Meta**: chiedi cliente di andare https://developers.facebook.com/ → Business Manager → WhatsApp → Phone Numbers → contolla se numero è connesso
2. **Se numero NON connesso**: follow Meta guide ufficiale (15 min processo). FLUXION doc: (TODO ingest WhatsApp setup guide in S185-bis)
3. **Se numero connesso**:
   - FLUXION → Impostazioni → WhatsApp → visualizza stato template
   - Status `Pending` = Meta sta revisionando (24-48h normale)
   - Status `Rejected` = template violava policy Meta (es. troppo aggressivo, linguaggio proibito)
4. **Se rejected**: modificare template, risubmittere
5. **Se >48h e ancora Pending**: Meta è lento (accade, load variabile). Aspetta 12h più, o contatta Meta support diretto

**Workaround temporaneo** (Pro only):
- Disabilita template reminder FLUXION
- Manda reminder manuale WhatsApp text (non template) — no approvazione richiesta

**Tech debt**: FLUXION auto-retry submit template se Pending >36h

**Email Template**: [Vedi C3 nella sezione Template Library](#template-c3-whatsapp-template-meta)

---

#### **ISSUE C4: Scheda cliente dati persi (SQLite crash)**

**Severità**: P0 (data loss)

**Sintomi**:
- Cliente apre FLUXION → una scheda cliente (es. "Pinco Pallino") è vuota: telefono, email, note, storico appuntamenti SPARITI
- Oppure: cliente aggiunge appuntamento, riavvia app, appuntamento NON c'è

**Diagnosi**:
- **SQLite locked** (60% casi): processo altro (backup, AV scan) ha bloccato DB. FLUXION non scrive, silente fail.
- **SQLite corrupted** (25% casi): crash hard (power loss, BSOD) ha corrotto pagine DB
- **Bug sync** (10% casi): raro, FLUXION ha sovrascritto dati old sync (v1.0 no sync, improbabile)
- **UI not refreshed** (5% casi): dati ci sono DB, ma UI non mostra (app restart risolve)

**Fix Step-by-Step**:
1. **First: app restart**
   - Chiudi FLUXION completamente
   - Riapri
   - Controlla se dati tornano → IF YES, era UI stale, risolto
2. **Se ancora sparito**: chiedi screenshot scheda (verificare dati realmente assenti)
3. **Se screenshot conferma vuota**:
   - **Backup restore**:
     - FLUXION → Impostazioni → Backup & Restore
     - Click "Restore from backup" se backup automatico disponibile (daily)
     - Select backup più recente (prima che dati scomparissero)
     - Restore → attendi ~30s
     - Verifica dati tornati → IF YES, risolto
   - **Se restore non disponibile** (backup <1 giorno old o disabilitato): escalation founder (vedi ESCALATION)
4. **Prevenzione**: spiegare al cliente che backup automatico giornaliero è attivo. Consigliare manual export CSV (Impostazioni → Esporta) una volta a settimana per ulteriore safety.

**Documentazione reference**:
- Wiki: (TODO ingest backup/restore guide in S185-bis)

**Email Template**: [Vedi C4 nella sezione Template Library](#template-c4-scheda-cliente-dati-persi)

---

### CATEGORIA D — SARA VOICE AGENT (3 issue)

#### **ISSUE D1: Sara non sente input audio (microfono)**

**Severità**: P1 (Sara Pro feature core)

**Sintomi**:
- Cliente Pro: "Ho impostato Sara, apri il test vocale, parlo ma Sara non sente nulla. Dice 'In ascolto…' e basta."
- Oppure: "Il microfono funziona in Teams, ma in FLUXION no."

**Diagnosi**:
- **Permessi macOS/Win insufficienti** (40%): FLUXION (o sidecar voice-agent.exe) non ha permesso microphone accesso sistema
- **Device errato selezionato** (30%): cliente ha microfono USB ma FLUXION è configurato su built-in (non connesso)
- **Microfono spento** (15%): device mute fisico acceso, o volume sistema a 0
- **Bluetooth non supportato** (10%): cliente usa Bluetooth headset — non ufficialmente supportato in v1.0
- **Firewall bloccato porta 3002** (5%): vedi ISSUE A4

**Fix Step-by-Step**:
1. **Verifica permessi sistema**:
   - **macOS**: System Settings → Privacy & Security → Microphone → controlla che FLUXION è nella lista con toggle ON
   - **Windows**: Settings → Privacy & security → Microphone → controlla "Allow apps to access your microphone" ON, poi FLUXION è listed e toggle ON
2. **Verifica device selezionato**:
   - FLUXION → Impostazioni → Sara → Audio Input Device
   - Dropdown mostra device disponibili (es. "Built-in Microphone", "USB Headset", etc.)
   - Se cliente ha microfono USB: selezionare da dropdown
   - Click "Test Microphone" → parla → dovresti sentire echo o conferma
3. **Verifica device fisico**:
   - Microfono acceso? (LED, switch fisico)
   - Volume macOS/Win a >50%?
4. **Se Bluetooth**: spiegare "v1.0 non supporta ufficialmente Bluetooth. Usa cavo USB o built-in laptop. v1.1 (Q4 2026) aggiungerà Bluetooth."
5. **Restart sidecar**:
   - Chiudi FLUXION
   - Task Manager → Dettagli → cerca `voice-agent.exe` → Kill Process
   - Riapri FLUXION
   - Test microfono di nuovo

**Documentazione reference**:
- Wiki: `docs/helpdesk-wiki/wiki/entities/sara-voice-agent.md` § "Errori comuni" → Microfono non rilevato

**Email Template**: [Vedi D1 nella sezione Template Library](#template-d1-sara-non-sente-audio)

---

#### **ISSUE D2: Sara latenza >2s (lento)**

**Severità**: P1 (UX degradata)

**Sintomi**:
- Cliente: "Parlo a Sara, aspetto 2-3 secondi prima che risponda. Sembra lenta."
- Target FLUXION: <800ms (attuale ~1330ms — tech debt S186)

**Diagnosi**:
- **Groq API lento** (40%): free tier rate-limiting, response time Groq variabile (200-800ms)
- **Internet lento** (30%): cliente ha connessione <5 Mbps, round-trip latency alto
- **TTS fallback Piper → SystemTTS** (20%): Edge-TTS offline, fallback è lento (~400ms SystemTTS vs ~500ms Edge)
- **Machine load alto** (10%): processo altro (backup, antivirus scan) occupa CPU

**Fix Step-by-Step**:
1. **Speedtest internet**: chiedi cliente di testare internet (speedtest.net) — almeno 5 Mbps upload è consigliato
2. **TTS tier Switch temporaneo**:
   - FLUXION → Impostazioni → Sara → TTS Engine
   - Switch a "Piper (offline fast)" da "Edge-TTS (premium quality)" se online
   - Latency dovrebbe scendere ~300ms (trade-off: voce qualità 7/10 vs 9/10)
3. **Check Groq API health**:
   - Dire al cliente che Groq free tier è shared — picchi ore lavorative (9-17) possono rallentare
   - Consigliare test in off-hours (serata, weekend)
4. **Process background**:
   - Task Manager → Performance → verificare CPU/RAM non al 100%
   - Se antivirus scanning: escludere FLUXION folder (vedi ISSUE A3)
5. **Expectation**: spiegare che latenza <1s è tech debt v1.1 (S186 roadmap), attuale ~1330ms è known trade-off. Non è bugga, è performance optimization in progress.

**Documentazione reference**:
- Wiki: `docs/helpdesk-wiki/wiki/entities/sara-voice-agent.md` § "Errori comuni" → Latency >2s

**Email Template**: [Vedi D2 nella sezione Template Library](#template-d2-sara-latenza-lenta)

---

#### **ISSUE D3: Sara interpreta male nome cliente (fonetica "Gino vs Gigio")**

**Severità**: P2 (feature edge case, customer experience)

**Sintomi**:
- Cliente: "Quando cliente mi chiama e dice il suo nome 'Gino', Sara scrive 'Gigio' nella scheda. Succede spesso con nomi simili foneticamente."

**Diagnosi**:
- NLU (Natural Language Understanding) di Sara usa Groq LLM + RAG FAQ/KB locale
- Nomi simili foneticamente (Gino ~Gigio, Marco ~Mark, etc.) possono confondere STT (Whisper) + NLU
- FLUXION v1.0 non ha Levenshtein matcher ottimizzato per disambiguazione nomi (tech debt)
- Futura soluzione: cliente crea blocco "Nickname" in settings (es. "Gino" = canonical, "Gigio" = alias)

**Fix Step-by-Step**:
1. **Workaround v1.0**: quando cliente notifica confusione, chiedi di specificare **al microfono**: "Mi chiamo Gino, G-I-N-O, la versione corta di Luigi" — Sara imparerà dal contesto
2. **Database locale RAG**: FLUXION RAG include lista clienti attuali → se cliente è già in DB come "Gino", Sara dovrebbe matching con "Gigio" dirà "Intendi Gino?" (vedi FSM state `DISAMBIGUATION`)
3. **Manual correction**: dopo che Sara scrive nome errato, cliente entra manualmente in scheda e corregge. FLUXION salva nome.
4. **Future v1.1**: Founder implementerà "Nickname alias" feature. Per ora, è known edge case.

**Documentazione reference**:
- Wiki: `docs/helpdesk-wiki/wiki/entities/sara-voice-agent.md` § "Test scenari live" → "Gino vs Gigio"

**Email Template**: [Vedi D3 nella sezione Template Library](#template-d3-sara-fonetica-nome)

---

### CATEGORIA E — PAGAMENTO & REFUND (2 issue)

#### **ISSUE E1: Stripe Checkout fallisce (errore pagamento)**

**Severità**: P0 (blocca vendita)

**Sintomi**:
- Cliente potenziale sulla landing fluxion-landing.pages.dev clicca "Acquista Base €497" → Stripe form carica → inserisce carta → errore "Payment declined" o "Your request has been rejected"
- Oppure: "Checkout è rimasto a caricamento, non completa"

**Diagnosi**:
- **Carta declinata Stripe** (70% casi): cliente ha saldo insufficiente, carta scaduta, banca blocca (anti-frode), oppure emittente non supporta international (raro Italia)
- **Checkout timeout** (15% casi): browser timeout (ricarica), network instabile
- **Stripe API issue** (10% casi): Stripe momentaneamente down (molto raro), oppure SK_LIVE non valida in backend CF Worker
- **3D Secure flow** (5% casi): richiesta di conferma SMS/app — cliente non completa step secondario

**Fix Step-by-Step**:
1. **Chiedi cliente di retry**: "Riprova completare pagamento. A volte è timeout temporaneo."
2. **Se replica errore**: "Controlla con banca se carta è abilitata per acquisti online internazionali (FLUXION è gestito da Stripe inc., USA). Oppure usa carta CREDIT diversa (a volte DEBIT è più restrittivo)."
3. **Se cliente nota è 3D Secure**: attendere sms/notifica app, confermare, retry checkout
4. **Fallback alternativo** (se Stripe fallisce persistente):
   - Dire a cliente: "Purtroppo Stripe declina il pagamento per motivi banca. Contattami a fluxion.gestionale@gmail.com con email + numero telefono, farò tranfer manuale e ti invio license."
   - Founder riceve email → verifica email valida → genera key manuale via tool interno → invia via Resend (o fallback Gmail se Resend fail)
5. **Se bug Stripe API** (test card 4242 fails): escalation founder — controlla SK_LIVE in CF Worker secrets

**Documentazione reference**:
- Landing: (checkout UI già live — test card 4242 per Dev testing)

**Email Template**: [Vedi E1 nella sezione Template Library](#template-e1-stripe-checkout-fallisce)

---

#### **ISSUE E2: Rimborso 30gg — timing e procedura**

**Severità**: P0 (policy vincolante)

**Sintomi**:
- Cliente: "Ho comprato FLUXION Base 3 giorni fa, ma non mi piace. Come faccio a chiedere rimborso?"
- Oppure: "Ho chiesto rimborso 5 giorni fa, quand'è che mi arrivals?"

**Diagnosi**:
- Cliente ha diritto 30gg soddisfatti o rimborsati (D.Lgs 206/2005 art. 52+)
- Procedura è automatica tramite landing `https://fluxion-landing.pages.dev/#garanzia` (modulo refund)
- Stripe accredita entro 5-10 gg lavorativi (dipende banca, non FLUXION)

**Fix Step-by-Step**:
1. **Verifica finestra temporale**: "Quando hai completato l'acquisto su Stripe?" → calcola giorni
   - If ≤30 giorni: idoneo rimborso
   - If >30 giorni: purtroppo fuori finestra (spiegare empaticamente)
2. **Se idoneo**: spiega procedura:
   - Landing https://fluxion-landing.pages.dev/#garanzia (sezione "Garanzia 30 giorni")
   - Form semplice: email acquisto + note opzionali
   - Sistema valida automaticamente → rimborso verso Stripe in tempo reale
   - Riceve email conferma con ID rimborso (es. "refund_1234567890")
   - Stripe accredita sulla carta originale entro 5-10 gg lavorativi (timeline non modificabile, dipende banca)
3. **Se cliente dice "Non riesco accedere form"**: founder genera refund manuale via Stripe dashboard (accedi con prod account) → Search transaction → Refund pulsante
4. **Se cliente chiede "Perché 5-10 giorni?"**: spiegare è timeline Stripe/banca, non FLUXION (trasparenza)
5. **Follow-up giorno 12**: se cliente non ha visto rimborso, chiedi conferma: "Hai visto accredito carta?". Se no: issue banca → suggerire contatti banca customer service

**Documentazione reference**:
- Landing: `landing/termini-rimborso.html` — policy ufficiale
- Stripe: dashboard refund section (internal CTO)

**Email Template**: [Vedi E2 nella sezione Template Library](#template-e2-rimborso-procedura)

---

### CATEGORIA F — PERFORMANCE & DATA (2 issue)

#### **ISSUE F1: App lenta con 1000+ clienti (scalabilità DB)**

**Severità**: P2 (performance degradation)

**Sintomi**:
- Cliente grande (salone catena 50+ dipendenti, ~2000 clienti): "FLUXION è lenta. Quando apro lista clienti, impiega 5 secondi a loadare. Scrolling è scattoso."

**Diagnosi**:
- SQLite locale NON è ottimizzato per query su 2000+ rows senza indici/pagination
- FLUXION v1.0 carica TUTTA la lista in memoria (tech debt D-2 "frontend virtual scroll")
- RAM consumata balloons, rendering React lento
- Soluzione: pagination + virtual scrolling implementate in v1.1

**Fix Step-by-Step**:
1. **Workaround v1.0 interiм**:
   - Segmenta lista clienti per **filtro iniziale**: es. "Clienti attivi ultimi 3 mesi" piuttosto che "Tutti"
   - FLUXION → Impostazioni → Filtri → crea vista "Attivi" che mostra solo ultimi 90 giorni
   - Refresh query riduce dati caricati da 2000 a ~300 → latency scende
2. **DB maintenance**:
   - Chiedi se client ha dati "morti" (clienti non attivi da 2+ anni) — archiviare/scartare riduce DB size
   - Suggerire monthly export+archive CSV per dati history
3. **Machine resources**:
   - Chiedi: quanta RAM ha il PC? (Se <8GB + FLUXION+Sara: RAM exhaustion). Recommenda upgrade o ridurre task background
4. **Expectation**: "v1.0 è ottimizzato per PMI 1-500 clienti. Per team 2000+, suggeriamo v1.1 pagination (Q4 2026) oppure segmentazione workflow sopra. Non è bugga, è architectural limit."

**Documentazione reference**:
- PRD: (performance D-2 roadmap)

**Email Template**: [Vedi F1 nella sezione Template Library](#template-f1-app-lenta-1000-clienti)

---

#### **ISSUE F2: Backup SQLite locked (processo AV bloccato)**

**Severità**: P1 (backup fail = data loss risk)

**Sintomi**:
- Cliente attiva automatic backup giornaliero in FLUXION
- Errore log: "Backup failed: database locked" oppure "Cannot read fluxion.db: file in use"

**Diagnosi**:
- **AV (antivirus) scansionando** DB file durante backup (50% casi)
- **altro processo FLUXION** (es. crash precedente che non ha released lock) (30%)
- **Defender Windows scanning** (15%)
- **Cloud sync service** (OneDrive, Google Drive) che tenta accesso DB (5%)

**Fix Step-by-Step**:
1. **Whitelist AV**: aggiungi FLUXION DB folder a esclusioni antivirus (vedi ISSUE A3 workflow)
   - Cartella: `C:\Users\[USERNAME]\AppData\Local\fluxion\data` (Win) oppure `~/Library/Application Support/fluxion/` (Mac)
2. **Disabilita cloud sync per DB**:
   - Se cliente sincronizza OneDrive/Google Drive folder home: escludere cartella FLUXION da sync
   - Cloud services causano file lock durante upload
3. **Manual backup test**:
   - Chiudi FLUXION completamente
   - Aspetta 10s (rilascia lock)
   - FLUXION → Impostazioni → Backup & Restore → click "Backup Now"
   - Dovrebbe succedere senza errore (se ancora fail: escalation)
4. **Process monitor**: chiedi avvio Task Manager, sort by Handles, cerca se altro processo detiene fluxion.db
   - Se sì: kill processo, retry backup

**Documentazione reference**:
- Wiki: (TODO ingest backup diagnostics in S185-bis)

**Email Template**: [Vedi F2 nella sezione Template Library](#template-f2-backup-locked)

---

### CATEGORIA G — COMPLIANCE & GDPR (1 issue)

#### **ISSUE G1: GDPR Art.20 esportazione dati (diritto portabilità)**

**Severità**: P0 (compliance vincolante)

**Sintomi**:
- Rappresentante legale cliente invia email formale: "Il nostro cliente Mario Rossi chiede l'esportazione tutti i suoi dati (Art.20 GDPR). Scadenza risposta: 30 giorni."

**Diagnosi**:
- GDPR Art.20 = Data Subject Portable Format (diritto portabilità dati)
- Richiesta formale = SLA 30gg non negoziabile
- FLUXION non ha strumento UI export Art.20 completo (tech debt E-6 futuro)
- Soluzione: export manuale SQLite + parsing JSON per founder

**Fix Step-by-Step**:
1. **Verifica autenticità richiesta**: chiedi email ufficiale da avvocato/rappresentante (non da cliente generico — validazione GDPR)
2. **Comunica SLA**: "Confermato: abbiamo 30 giorni per fornire esportazione dati. Procederemo senza indugio."
3. **Internal founder procedure** (NON visible to customer yet):
   - Accedi DB cliente (SQLite crittografato in folder utente)
   - Export query Art.20:
     ```sql
     SELECT * FROM clienti; SELECT * FROM appuntamenti; SELECT * FROM transazioni;
     -- (join con data_subject_id = Mario Rossi)
     ```
   - Convert JSON format:
     ```json
     {
       "data_subject": "Mario Rossi",
       "export_date": "2026-05-05",
       "personal_data": {
         "appointments": [...],
         "transactions": [...],
         "communications": [...]
       }
     }
     ```
   - PII redact: scrivi rimozione campo sensibili (no credit card full, no IP, etc.)
4. **Consegna dati**: invia JSON.gz encrypted (passwod via email separate) a indirizzo email formale richiesta
5. **Documentazione**: mantieni audit log GDPR:
   - Data richiesta, mittente, Data consegna, formato, scope dati (Art.20 § 3 GDPR per audit compliance)
   - Conserva per 10 anni (D.Lgs 196/2003 + GDPR Art.17 storage)

**Documentazione reference**:
- Landing: `landing/privacy.html` § "Art.20 diritti data subject" (TODO ingest full policy S185-bis)
- Sentry: GDPR region DE (telemetry DE-safe)

**Email Template**: [Vedi G1 nella sezione Template Library](#template-g1-gdpr-portabilità-dati)

---

## Email Template Library

### TEMPLATE A1: SmartScreen blocca installer
```
Ciao [NOME_CLIENTE],

Capisco l'inconveniente! Il blocco SmartScreen è una protezione Windows legittima per installer non-firmati. 
È una procedura semplice: 3 click e FLUXION installato.

Ecco i passaggi:

1. Doppio-click su Fluxion_1.0.1_x64-setup.exe
2. Schermata SmartScreen: click **"Maggiori informazioni"** (in basso)
3. Appare bottone **"Esegui comunque"** → click

Pronto! Installazione continua normalmente.

Se hai altri dubbi, sono qui.

Gianluca — Team FLUXION
```

---

### TEMPLATE A2: Mac Gatekeeper rifiuta app
```
Ciao [NOME_CLIENTE],

macOS ha "quarantenato" FLUXION perché non è notarizzato Apple (scelta per mantenere costi zero, come vi diciamo in trasparenza). 
La procedura è semplice: un clic destro e FLUXION parte.

Ecco come:

1. Apri **Finder** → vai in **Applications**
2. Cerca **Fluxion.app**
3. **Tasto destro** (oppure Control+click) su Fluxion.app
4. Click **"Apri"** dal menu
5. Dialogo macOS: click **"Apri"**

Fatto! macOS ricorda e non chiede più dopo il primo avvio.

(Alternativa per utenti terminal: `xattr -d com.apple.quarantine /Applications/Fluxion.app`)

Se bloccato, scrivi a fluxion.gestionale@gmail.com.

Gianluca — Team FLUXION
```

---

### TEMPLATE A3: Antivirus falso positivo
```
Ciao [NOME_CLIENTE],

L'antivirus ha flaggato FLUXION per eccesso di cautela (è unsigned, come detto — zero costi). 
La buona notizia: è un falso positivo, FLUXION è autentico e verificabile su VirusTotal.

Per risolvere, aggiungi FLUXION a esclusioni:

**Windows Defender**:
- Start → Impostazioni → Virus e protezione dalle minacce
- Gestisci impostazioni → "Aggiungi esclusioni"
- Cartella: C:\Users\[TUO_USERNAME]\AppData\Local\fluxion
- Done!

**Altro antivirus** (Avast, Norton, etc.):
- Accedi antivirus settings → Esclusioni/Whitelist
- Aggiungi cartella: C:\Users\[TUO_USERNAME]\AppData\Local\fluxion

Se hai dubbi su quale cartella, scrivi una foto della schermata FLUXION → Impostazioni.

Se AV continua a bloccare, invia un'email e risolviamo manualmente.

Gianluca — Team FLUXION
```

---

### TEMPLATE A4: Voice-agent firewall bloccato
```
Ciao [NOME_CLIENTE],

Sara non risponde perché la porta locale 3002 (dove parla) è bloccata da firewall Windows. 
L'installer ha provato a aprire automaticamente, ma se non ha avuto permessi, devi aggiungere manualmente.

Ecco come:

1. Apri **Command Prompt** (Start → digita `cmd` → Invio)
2. Digita questo comando (copia-incolla esatto):
   ```
   netstat -an | find "3002"
   ```
   - Se vedi riga con "LISTENING": porta è aperta ✓
   - Se nulla: porta è bloccata → continua step 3

3. **Windows Defender Firewall**:
   - Start → digita **"Windows Defender Firewall with Advanced Security"** → Apri
   - Sinistra: click **"Inbound Rules"**
   - Destra: **"New Rule"**
   - Tipo: **"Program"** → Next
   - Browse: naviga `C:\Users\[TUO_USERNAME]\AppData\Local\fluxion\voice-agent.exe`
   - Action: **"Allow"** → Next → Finish
   
4. **Restart FLUXION**: chiudi e riapri app

Sara dovrebbe rispondere in ~1 secondo. Se ancora timeout, scrivi a fluxion.gestionale@gmail.com con screenshot CMD.

Gianluca — Team FLUXION
```

---

### TEMPLATE B1: License key non valida
```
Ciao [NOME_CLIENTE],

"License key non valida" di solito significa copia-incolla incompleta (è facile con 88 caratteri!).

Facciamo una verifica:

1. Controlla la tua email inbox/spam per email da **onboarding@resend.dev** con oggetto "FLUXION License Key"
2. In quella email, copia la key tra i due righe di trattini (vedi esempio):
   ---
   1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j
   ---
3. Incolla in FLUXION Setup Wizard **senza spazi all'inizio o fine**
4. Retry

Se still errore, **che email hai usato in Stripe Checkout?** Rileggerò il record transazione e rigeneero la key se c'è problema.

Gianluca — Team FLUXION
```

---

### TEMPLATE B2: Email license non arrivata
```
Ciao [NOME_CLIENTE],

Email license a volte finisce in spam (filtri email sono aggressivi con onboarding@resend.dev).

Ecco come controlliamo:

1. Accedi tua email (Gmail, Outlook, etc.)
2. Vai in **Spam** o **Junk** (dipende email provider)
3. Cerca mittente: **onboarding@resend.dev**
4. Se la trovi: Mark as "Not Spam" → dovrebbe spostarsi in Inbox

**Se assolutamente non la trovi nemmeno in spam**:
Dimmi:
- Email esatta che hai usato in Stripe Checkout (copiata da ricevuta email Stripe)
- Data/ora acquisto

Accesso dashboard Stripe io, rigeneero key e te la invia manualmente.

Gianluca — Team FLUXION
```

---

### TEMPLATE B3: Trasferire licenza device
```
Ciao [NOME_CLIENTE],

Capisco! FLUXION supporta max 2 device per licenza (policy antipirateria — mantiene il prezzo basso per tutti).

Ecco come trasferisci:

**Step 1 — Disattivazione vecchio PC** (optionale, ma consigliato):
- Vecchio PC: FLUXION → Impostazioni → Licenza → Disattiva
- Se non c'è pulsante "Disattiva": disinstalla FLUXION normalmente (Control Panel → Remove)

**Step 2 — Installazione nuovo PC**:
- Scarica Fluxion_1.0.1_x64-setup.exe dal link email originale (controlla inbox/spam se non trovi)
- Installa sul nuovo PC
- Setup Wizard chiede license key → incolla **stessa key** da email originale
- Done!

Se per qualsiasi ragione il nuovo PC dice "Hardware fingerprint mismatch" (molto raro), scrivi e rigeneero attivazione manuale.

Nota: una **terza attivazione** su terzo device richiede acquisto nuova licenza (è la policy, scusa per la rigidità).

Gianluca — Team FLUXION
```

---

### TEMPLATE C1: Calendario non sincronizza
```
Ciao [NOME_CLIENTE],

Ho capito il problema: FLUXION v1.0 **NON sincronizza calendario** tra device in tempo reale (è un tecnicismo: SQLite locale, no cloud). 
È una limitazione nota che affrontiamo con v1.1 (Q4 2026).

**Per ora, il workaround è**:

**Option A** (Team piccolo 1-2 persone):
Un PC "master" in ufficio rimane acceso. Tutti gli altri consultano agenda da quel PC (monitor condiviso, o TeamViewer gratis per remote view).

**Option B** (Team 3+ persone, breve termine):
Mantieni FLUXION sul PC master per booking/fatture.
Parallelo: Google Sheets condiviso per agenda settimanale (che gli operatori leggono).
Fondatore genera Sheets da FLUXION, il team legge Sheets.

**Option C** (Soluzione definitiva):
Aspetta Q4 2026 v1.1, che introdurrà sync cloud opzionale (paid, non gratuito). Potrai sincronizzare tra device.

Scusa per il limite! È una tradeoff: FLUXION meno care in v1.0 (zero cloud costi), ma v1.1 aggiungerà sync se serve.

Che option preferisci per ora?

Gianluca — Team FLUXION
```

---

### TEMPLATE C2: Fattura SDI rifiutata
```
Ciao [NOME_CLIENTE],

Mi dispiace per l'intoppo! Fatture SDI sono complesse. Mi aiuti a capire l'errore:

**Che codice di errore ha dato l'Agenzia Entrate?** (es. NS0427, NS0428, etc. — dovrebbe essere nell'email Agenzia)

Nel frattempo, verifichiamo dati cliente:

1. Apri FLUXION → scheda cliente
2. Controlla:
   - **Partita IVA**: formato corretto? (11 cifre numeriche, es. 12345678901)
   - **Indirizzo completo**: città, CAP 5 cifre, indirizzo (no caratteri speciali proibiti: &, #, $, etc.)
   - **Nominativo**: solo lettere e spazi (no numeri)
3. Se vedi errori, correggi e **storna fattura** in FLUXION (Impostazioni → Fatturazioni → Storno)
4. Ricrea fattura con dati corretti

Se error code SDI non è nella lista (NS042X), **invia screenshot fattura + error code** a fluxion.gestionale@gmail.com e ricerchiamo insieme.

Se è bugga FLUXION confermato, genero fattura PDF manuale che invii tramite Aruba/Fatture in Cloud.

Gianluca — Team FLUXION
```

---

### TEMPLATE C3: WhatsApp template Meta pending
```
Ciao [NOME_CLIENTE],

WhatsApp Business richiedere approvazione Meta per template (messaggi ripetuti tipo "Appuntamento domani").
Normale SLA Meta: 24-48 ore. A volte più lungo.

**Mentre aspetti approvazione Meta, ecco cosa puoi fare**:

1. **Check status template**:
   - FLUXION → Impostazioni → WhatsApp → visualizza "Template Status"
   - Status `Pending` = Meta sta revisionando (aspetta 24-48h)
   - Status `Rejected` = Meta ha rifiutato (testo violava policy)

2. **Se `Pending` >48h**:
   - Meta è lento (accade, load variabile)
   - Aspetta 12h di più, oppure contatta Meta support diretto

3. **Se `Rejected`**:
   - Modifica template text (rimuovi parole aggressive, link sospetti)
   - Resubmit in FLUXION

4. **Workaround interiм (non template)**:
   - Disabilita template reminder FLUXION
   - Manda reminder **manuale** via WhatsApp text (non template): "Ciao, ricordati appuntamento domani alle 10:00"
   - No approvazione Meta richiesta per testo libero

Non è urgenza — approvazione Meta è asincrona. Continua a usare FLUXION normalmente, quando template approva le notifiche partiranno automatiche.

Se approval non arriva in 72h, scrivi a fluxion.gestionale@gmail.com.

Gianluca — Team FLUXION
```

---

### TEMPLATE C4: Scheda cliente dati persi
```
Ciao [NOME_CLIENTE],

Dati persi sono una nostra priorità massima. Facciamo recovery subito.

**Primo step — App restart**:
1. **Chiudi FLUXION completamente**
2. **Riapri** → naviga alla scheda cliente
3. **I dati sono tornati?** → Se SÌ, era UI cached, risolto! Se NO, continua…

**Secondo step — Restore da backup**:
1. FLUXION → Impostazioni → Backup & Restore
2. Click **"Restore from Backup"**
3. Seleziona backup più recente (prima che scomparissero dati)
4. Click Restore → attendi ~30 secondi
5. Verifica dati tornati → Se SÌ, risolto!

**Se nessun backup disponibile**:
Scrivi a fluxion.gestionale@gmail.com con dettagli:
- Nome cliente scheda persa
- Ultimo appuntamento che ricordi (data/ora)
- Quando hai notato dati spariti

Lato mio: accedo DB e cerco recovery SQLite database (è possibile quasi sempre).

**Prevenzione futura**:
- Backup automatico è attivo ogni 24h
- Consiglio: esporta CSV clienti settimanale (Impostazioni → Esporta) — doppia protezione

Sono qui se servono altri step.

Gianluca — Team FLUXION
```

---

### TEMPLATE D1: Sara non sente audio
```
Ciao [NOME_CLIENTE],

Sara non sente significa microfono non ha permesso accesso o è selezionato device sbagliato. Sistemiamo in 2 minuti.

**Step 1 — Permessi sistema**:

**Windows**:
- Settings → Privacy & security → Microphone
- Assicurati "Allow apps to access your microphone" sia **ON**
- Scorri lista app, trova FLUXION, assicurati toggle sia **ON**

**macOS**:
- System Settings → Privacy & Security → Microphone
- Cerca FLUXION in lista, toggle deve essere **ON**
- Se FLUXION non c'è, apri FLUXION una volta, sistema ripropone permesso

**Step 2 — Device corretto**:
1. FLUXION → Impostazioni → Sara → Audio Input Device
2. Dropdown mostra device disponibili (es. "Built-in Microphone", "USB Headset")
3. **Se hai microfono USB**: selezionalo dal dropdown
4. Click **"Test Microphone"** → parla dentro → dovresti sentire eco

**Se ancora non sente**:
- Verifica microfono fisico: acceso? Volume >50%? Connesso (se USB)?
- Bluetooth mic: v1.0 non supporta ufficialmente (v1.1 aggiungerà)
- Se tutto corretto: restart app completo (Chiudi + Riapri)

Se continua, invia email con screenshot Impostazioni → Sara.

Gianluca — Team FLUXION
```

---

### TEMPLATE D2: Sara latenza lenta
```
Ciao [NOME_CLIENTE],

Sara ~1.3 secondi latenza è il nostro target attuale (v1.0). Target future v1.1 è <800ms.
Frattanto, ecco come velocizzare:

**Step 1 — Verifica internet**:
Visita speedtest.net → test velocità. Almeno 5 Mbps consigliato.

**Step 2 — Switch TTS a Piper (offline fast)**:
1. FLUXION → Impostazioni → Sara → TTS Engine
2. Cambia da "Edge-TTS (premium)" a "Piper (offline fast)"
3. Latency dovrebbe scendere ~300ms
4. Trade-off: voce è 7/10 qualità vs 9/10 (ma velocità 3x)

**Step 3 — Background process**:
Task Manager → Performance → verifica CPU/RAM non al 100%.
Se antivirus scansionando: escludere cartella FLUXION (vedi template A3 antivirus).

**Expectation**: v1.0 è ~1330ms, tech debt da ottimizzare. Non è bugga, è performance roadmap. Versione 1.1 (Q4 2026) avrà latency <800ms prioritario.

Se latency >3s (anomala): invia email, ricerchiamo cause specifiche.

Gianluca — Team FLUXION
```

---

### TEMPLATE D3: Sara sbaglia nome fonetica
```
Ciao [NOME_CLIENTE],

Nomi foneticamente simili (Gino ~Gigio, Marco ~Mark) sono edge case — AI non sempre perfetta! È learning in progress.

**Workaround v1.0**:

1. **Al microfono, specificare meglio**:
   Invece di dire "Mi chiamo Gino", prova: "Mi chiamo Gino, G-I-N-O, la forma corta di Luigi"
   Sara imparerà dal contesto aggiuntivo

2. **Manuale correction**: Dopo che Sara scrive nome errato:
   - Scheda cliente apre
   - Manualmente correggi nome
   - FLUXION salva → Sara imparerà

3. **Future v1.1**: Implementeremo "Nickname Alias" feature (es. "Gino" = canonical, "Gigio" = alias). Per ora è tech debt.

Non è urgenza — accade ~5% interazioni. Resta una feature rara (nomi molto simili).

Se accade frequentemente con un cliente specifico, nota il nome e scrivi a fluxion.gestionale@gmail.com — studiamo pattern.

Gianluca — Team FLUXION
```

---

### TEMPLATE E1: Stripe Checkout fallisce
```
Ciao [NOME_CLIENTE],

Checkout Stripe a volte declina pagamento per motivi banca (carta bloccata, saldo insufficiente, etc.).

**Ecco cosa provi**:

1. **Retry completo**:
   - Torna a https://fluxion-landing.pages.dev
   - Click "Acquista" → riprova checkout con **stessa carta**
   - A volte è timeout momentaneo, retry risolve

2. **Se replica errore "Payment declined"**:
   - Contatta tua **banca**: "Ho ricevuto rifiuto Stripe per acquisto FLUXION. Abilitate pagamenti online internazionali?"
   - Stripe è società USA — alcune banche hanno filtri anti-international

3. **Alternativa**: prova **carta diversa** (CREDIT vs DEBIT — CREDIT spesso meno restrittivo)

4. **Se nessuna carta funziona**:
   - Scrivi a fluxion.gestionale@gmail.com con email + numero telefono
   - Farò transfer manuale e invio license via email
   - No Stripe richiesto — contanti bancari via bonifico (PayPal/Satispay future)

Non è raro. Succede ~10% dei checkout. La soluzione è sempre pratica.

Gianluca — Team FLUXION
```

---

### TEMPLATE E2: Rimborso procedura
```
Ciao [NOME_CLIENTE],

30 giorni soddisfatti o rimborsati — è il nostro impegno. Ecco procedura:

**Step 1 — Verifica timing**:
- Quando hai completato acquisto su Stripe? (data)
- Giorni trascorsi da allora?
- Se ≤30 giorni: idoneo rimborso ✓
- Se >30 giorni: purtroppo fuori finestra

**Step 2 — Richiesta rimborso** (se idoneo):
1. Visita https://fluxion-landing.pages.dev/#garanzia
2. Sezione "Garanzia 30 giorni" → Form rimborso
3. Email acquisto + note opzionali (feedback aiuta noi migliorare)
4. Submit

**Step 3 — Che succede**:
- Sistema valida automaticamente → rimborso parte istantaneamente verso Stripe
- Ricevi email conferma con ID rimborso (es. "refund_1A2B3C")
- **Stripe accredita card originale entro 5-10 giorni lavorativi** (dipende banca, non noi)

**Cosa NON dipende da noi**:
- Timing accredito: dipende da banca, circuito VISA/MC, non modificabile
- Se 10gg e non vedi: contatta banca customer service (noi abbiamo già mandato)

**Dati cliente**:
FLUXION è on-premise — dati rimangono PC tuo, non nei nostri server. Anche dopo rimborso, esporta CSV dati (Impostazioni → Esporta) se vuoi.

Tutto chiaro? Fammi sapere se problemi.

Gianluca — Team FLUXION
```

---

### TEMPLATE F1: App lenta 1000+ clienti
```
Ciao [NOME_CLIENTE],

FLUXION v1.0 è ottimizzato per PMI 1-500 clienti. Se ne hai 2000+, latency è attesa (SQLite non pagina, carica tutto in RAM).

**Workaround v1.0**:

1. **Segmenta lista clienti**:
   - FLUXION → Impostazioni → Filtri
   - Crea vista "Clienti attivi" (ultimi 90gg) anziché "Tutti"
   - Query carica ~300 clienti → latency scende 80%

2. **Archivio dati morti**:
   - Clienti non attivi da 2+ anni: esporta CSV, scarta FLUXION, archivia folder
   - Riduce DB size

3. **RAM machine**:
   - Quanto RAM ha PC tuo? (Start → Task Manager → Performance → Memory)
   - Se <8GB + FLUXION+Sara: upgrade RAM o ridurre task background

**Soluzione vera**: v1.1 (Q4 2026) avrà pagination + virtual scroll → zero lag anche 10k+ clienti.

Per ora: segmenta. È l'unica soluzione pratica.

Dimmi se vuoi aiuto cre-are filtri "Attivi".

Gianluca — Team FLUXION
```

---

### TEMPLATE F2: Backup SQLite locked
```
Ciao [NOME_CLIENTE],

Backup fail "database locked" significa antivirus (o cloud sync) sta scannerizzando file DB mentre FLUXION tenta backup.

**Fix**:

**Step 1 — Whitelist antivirus**:
- Apri antivirus settings (Defender / Avast / Norton)
- Esclusioni/Whitelist
- Aggiungi cartella: `C:\Users\[TUO_USERNAME]\AppData\Local\fluxion\data`
- Salva

**Step 2 — Disabilita cloud sync su DB**:
- Se OneDrive / Google Drive sincronizza home folder: escludere cartella FLUXION da sync
- Cloud services causano file lock

**Step 3 — Test backup**:
- Chiudi FLUXION completamente
- Aspetta 10 secondi
- Riapri FLUXION → Impostazioni → Backup & Restore → "Backup Now"
- Dovrebbe succedere senza errore

Se ancora "locked":
- Task Manager → Dettagli → sort by "Handles"
- Cerca fluxion.db, vedi quale processo lo tiene
- Kill processo, retry backup

Se problema persiste: scrivi a fluxion.gestionale@gmail.com con screenshot Task Manager.

Gianluca — Team FLUXION
```

---

### TEMPLATE G1: GDPR portabilità dati
```
Ciao [NOME_CLIENTE],

Richiesta Art.20 GDPR Data Portability ricevuta. Confermato: abbiamo 30 giorni per fornire esportazione dati.

**Cronologia**:
- Richiesta ricevuta: [DATA]
- Scadenza risposta: [DATA + 30GG]
- Status: IN PROGRESS

**Che dati esportiamo**:
- Appuntamenti cliente
- Transazioni/pagamenti
- Comunicazioni (SMS/WhatsApp)
- Note/storico

**Formato consegna**:
- JSON cifrato (password via email separate)
- Scaricabile da link sicuro (one-time)

**Timeline**:
- Entro 7 giorni lavorativi: esportazione pronta
- Entro 15 giorni: consegna data subject con credenziali

(FLUXION supporta anche future Data Deletion richiesta Art.17 GDPR — contattaci se serve.)

Restiamo in contatto. Domande?

Gianluca — Team FLUXION
```

---

### TEMPLATE — FOLLOW-UP DAY-3 (nessuna risposta cliente)
```
Ciao [NOME_CLIENTE],

Sto seguendo a titolo di gentile ricordo il nostro scambio di [DATE].

Sei riuscito a risolvere il problema di FLUXION con i step che ti ho inviato?

Se non ancora:
- Scrivi pure, no fretta
- Se ti serve aiuto aggiuntivo, sono qui

Se risolto: fantastico! Fammi sapere come è andata — feedback tuo mi aiuta migliorare.

Gianluca — Team FLUXION
```

---

### TEMPLATE — PREVENTIVO CHURN (cliente silenzioso >7gg)
```
Ciao [NOME_CLIENTE],

Non abbiamo tue notizie da una settimana. Tutto bene con FLUXION?

Se c'è problema:
- Scrivimi pure, risolviamo insieme
- No fretta — rispondi quando puoi

Se in generale FLUXION non fa al caso tuo:
- Dimmelo onestamente, zero giudizio
- 30 giorni garanzia rimborso → puoi tornare indietro senza rogne
- Feedback su cosa non ha funzionato mi aiuta migliorare per altri

Sono tutto orecchi.

Gianluca — Team FLUXION
```

---

## Knowledge Base Linking

**Nel rispondere sempre includere link privato wiki helpdesk** (NON pubblico):

```
Maggiori dettagli: docs/helpdesk-wiki/wiki/entities/[ENTITY].md
Landing FAQ (quando disponibile): https://fluxion-landing.pages.dev/faq.html#faq-[ANCHOR]
```

Esempi:
- ISSUE A1 → wiki: `docs/helpdesk-wiki/wiki/entities/win10-installation.md` § SmartScreen
- ISSUE B1 → wiki: `docs/helpdesk-wiki/wiki/entities/license-key.md` § "Errori attivazione"
- ISSUE D1 → wiki: `docs/helpdesk-wiki/wiki/entities/sara-voice-agent.md` § "Errori comuni"
- ISSUE A4 → wiki: `docs/helpdesk-wiki/wiki/entities/network-firewall.md` § "Errori comuni" → Sara offline

---

## Escalation Tree

**Quando coinvolgere founder (non risolvibile support standard)**:

### P0 UNSOLVED >1h
- App crash non riproducibile
- Pagamento fallito (Stripe API issue possibile)
- Data loss confermato (escalation recovery database)
- **Azione**: Label `FLUXION/escalation-P0`, snapshots screenshot + logs, email privata founder

### P1 UNSOLVED >4h
- Sara comportamento inatteso (NLU bug specifico)
- Hardware fingerprint mismatch (attivazione software)
- WhatsApp setup fallito (token Meta)
- **Azione**: Label `FLUXION/escalation-P1`, email privata descrizione dettagliata

### REFUND DISPUTED
- Cliente insiste rimborso >30gg
- Discrepanza Stripe (duplicato, cancellazione manuale)
- **Azione**: Accedi Stripe dashboard, verifica transazione, reversal manuale se justified

### GDPR DATA SUBJECT REQUEST
- Art.20 (portabilità), Art.17 (oblio), Art.21 (diritto di opposizione)
- Richiesta formale avvocato
- **Azione**: Crea task interna con deadline 30gg, log audit compliance, scritto founder

### CHARGEBACK APERTO
- Cliente ha aperto disputa banca (non modulo rimborso FLUXION)
- **Azione**: Attendi risoluzione banca, non azioni parallele. Inform cliente procedura banca tempo 30-90gg.

---

## Metrics & Review

### Gmail Labels (classification)
```
FLUXION/
  ├─ P0 (app crash, data loss, payment fail)
  ├─ P1 (Sara offline, WhatsApp fail)
  ├─ P2 (UI glitch, performance, feature request)
  ├─ P3 (general questions)
  ├─ resolved
  ├─ escalation-P0
  ├─ escalation-P1
  ├─ refund
  ├─ gdpr
  └─ custom (non in top-20)
```

### Weekly Review Checklist
Every Friday — audit email FLUXION label:

- [ ] Total P0 this week: ___ (target: 0 unresolved >4h)
- [ ] Total P1 this week: ___ (target: 0 unresolved >24h)
- [ ] Total refund: ___ (audit Stripe refund success rate)
- [ ] Avg resolution time P0/P1: ___ (target: <24h combined)
- [ ] Escalation issues: ___ (need product fix in v1.1?)
- [ ] Churn risk (no response >7gg): ___ (send template "preventivo churn")
- [ ] Feedback emerging patterns (3+ issues simili?) → aggiornare runbook

### Monthly Metrics Summary (email founder)
```
FLUXION Support — Metriche Mensili [MESE/ANNO]

Total tickets: __
  P0 (resolved <4h): __ / __ (SLA met: __)
  P1 (resolved <24h): __ / __ (SLA met: __)
  P2 (resolved <72h): __ / __ (SLA met: __)
  P3: __

Top 5 issue questa settimana:
  1. [ISSUE]: __ occorrenze
  2. [ISSUE]: __ occorrenze
  ...

Refund requests: __
  Approvate: __
  Disputed: __
  Pending: __

GDPR requests: __

Escalation → product backlog:
  - [Fix needed in v1.1]: impact ___ customers

Satisfaction sentiment:
  - Positive: __%
  - Neutral: __%
  - Negative: __%

Recommendations next month:
  - Aggiorna landing FAQ sezione [X]
  - Wiki ingest [Y] (tech debt S185-bis)
  - Consider automation [Z]
```

---

## Appendix A: Link Reference

- Landing FAQ: https://fluxion-landing.pages.dev/faq.html (attuale minimal — expand F-1)
- Landing Termini Rimborso: https://fluxion-landing.pages.dev/termini-rimborso.html
- Landing Privacy: https://fluxion-landing.pages.dev/privacy.html
- Support email: fluxion.gestionale@gmail.com
- Wiki privata: `/Volumes/MontereyT7/FLUXION/docs/helpdesk-wiki/wiki/entities/`

---

## Appendix B: Versioning

**Runbook version**: 1.0 (2026-05-05)
**Last updated**: S187 F-2 P0 Pre-Launch Audit
**Next review**: After first 10 customers (S188)
**Maintainer**: Founder Gianluca Di Stasi

---

**FINE RUNBOOK**
