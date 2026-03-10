# P0.5 Onboarding Frictionless — CoVe 2026 Deep Research
## Setup Credenziali Esterne (API Key / Email) per Desktop SaaS B2B

**Data ricerca:** 2026-03-10
**Scope:** Gmail OAuth2 vs App Password, wizard patterns, competitor analysis, decisioni architetturali per FLUXION

---

## 1. GOLD STANDARD 2026: Come gestiscono le credenziali i migliori tool

### Superhuman — Il Gold Standard Assoluto per Email Onboarding

Superhuman è il benchmark più studiato per onboarding email B2B.

**Flusso:** Signup → OAuth Gmail/Outlook (browser popup, zero campi manuali) → 30-min call 1-on-1 con onboarding specialist (obbligatoria in fase early, ora opzionale)

**Pattern chiave:**
- **OAuth sempre**, mai App Password, mai IMAP/password manuale
- Full-screen setup panels (non checklist laterale): 98% completion vs 30% con checklist opzionale
- Sandbox inbox sintetica: l'utente fa pratica senza toccare email reali
- Smart defaults pre-abilitati con spiegazione breve, mai un campo vuoto da configurare
- "Get Me To Zero" (tasto unico per archiviare tutto): 57% opt-in, ~1 miliardo email archiviate

**Dati chiave:**
- Full-screen panels obbligatori: completion 98% (era 30% con checklist skip)
- Human-led onboarding: 2x activation rate vs self-serve
- Feature opt-in: 80% (era 45% con checklist)
- Ogni onboarding specialist genera ~$650k ARR/anno

**Pattern "nascondi la complessità":** L'OAuth è presentato come "Connetti il tuo account Gmail" con un solo bottone. L'utente non vede mai le parole "IMAP", "SMTP", "App Password", "scope". Dopo il click appare il popup di Google, l'utente fa login normale, done.

---

### Linear — Onboarding Wizard B2B Minimalista

**Struttura:** 2 sezioni — "must-do" (signup + email verify) + "get started" (workspace config + invite + integrazioni)

**Pattern chiave:**
- Invite co-workers: presentato come passo early per aumentare retention di team
- Email notifications: subscribe step separato, non bloccante
- GitHub connect: mostrato nel wizard ma skippable senza penalità UX
- 10+ step totali ma ogni step è micro (1 scelta o 1 input), si percepisce fluido

**Credenziali esterne:** Linear usa OAuth per GitHub, Slack, Figma. **Non mostra mai un campo per inserire token API** durante l'onboarding — le integrazioni vengono proposte ma se skippate vengono proposte di nuovo al primo utilizzo contestuale.

---

### Notion — Progressive Profiling Elegante

**Struttura wizard:** 4 step esatti
1. Profile creation (obbligatorio)
2. Workspace setup (obbligatorio)
3. Import data da altri tool (opzionale — skip esplicito)
4. App download mobile/desktop (opzionale — skip esplicito)

**Post-wizard:** Getting Started page interattiva con checklist learn-by-doing. I tooltip appaiono hover-triggered, non forzati.

**Pattern "opzionale":** I step 3 e 4 sono marcati chiaramente come opzionali. Non c'è pressione a completarli. Il sistema personalizza i template mostrando subito contenuto rilevante (marketer vede template marketing) per dare valore immediato prima di chiedere configurazioni.

**Integrazioni:** Nessuna richiesta di API key o credenziali nel wizard. Vengono proposte nel contesto d'uso ("Connetti Figma" appare quando crei una pagina design-related).

---

### 1Password — Onboarding Credenziali Complesse per Non-Tecnici

Caso studio interessante perché il prodotto stesso **è** credenziali.

**Pattern chiave:**
- Secret Key: non viene mai chiamata "chiave crittografica" o spiegata tecnicamente. È semplicemente "la tua Emergency Kit che devi stampare/salvare"
- Emergency Kit: PDF scaricabile con QR code. L'utente la compila a mano (account password). Funge da recovery totale.
- Staging disclosure: "Crea account" → "Salva Emergency Kit" → (poi, quando hai tempo) browser extension / import password / vault sharing
- La complessità del modello a 2 fattori (account password + Secret Key) viene gestita con analogia fisica: "È come la combinazione di una cassaforte + la serratura — servono entrambe"

**AC misurabile:** Completion del setup base (account + Emergency Kit) > 90% perché è il prerequisito per accedere. Setup avanzato (extension, import, sharing) è deferred e promosso contestualmente.

---

### Figma — Onboarding Contestuale + Animazioni

**Pattern chiave:**
- Email verify → workspace setup → animated feature tour con copy brevissimo per tooltip
- Integrazioni (Slack, Jira, etc.): **mai nel wizard iniziale**, proposte al primo evento contestuale (es. quando condividi un file → "Connetti Slack per notifiche")
- No credenziali manuali mai: tutto OAuth

---

### Loom — Branching per Uso Case

**Struttura:** 3-4 domande iniziali (cosa usi Loom? workspace name? invita team? quale recorder?) → path personalizzato

**Pattern chiave:**
- Le domande determinano quale feature viene mostrata prima (aha moment calibrato)
- Scelta recorder nel wizard: Chrome extension vs desktop app — questa è l'unica "credenziale tecnica" e viene gestita con confronto visuale (quality badge)
- Email/notifiche: non configurate nel wizard, vengono attivate post-uso

---

### Raycast — Setup API Key Come Feature Discovery

Raycast è interessante perché gestisce API key di terze parti per ogni estensione.

**Pattern chiave:**
- Ogni estensione che richiede credenziali mostra una **Preferences screen dedicata** prima dell'uso
- Schermata "About This Extension" + README inline + campo singolo per API key
- Il campo è etichettato con testo descrittivo ("API Key dal tuo account OpenAI") + link diretto al provider
- Zero gergo tecnico: "Inserisci il tuo token" con link "Dove trovo il token?" che apre direttamente la pagina giusta del provider

**Pattern replicabile per FLUXION:** Questo è il modello per Groq key — un pannello Settings con un solo campo, label chiara, link "Dove trovo la chiave?" che apre `console.groq.com/keys`.

---

### Zoho CRM — SMB Email Integration Semplificata

**Pattern chiave per email:**
- L'utente clicca "Connetti email" → viene portato fuori in un tab separato per fare login al proprio provider
- Dopo il login, torna in Zoho già connesso — zero configurazione SMTP manuale
- Per chi non ha OAuth: form SMTP con label "Server in uscita" (non "SMTP host"), "Porta" con tooltip "di solito 587 per Gmail", "Il tuo indirizzo email" — terminologia consumer, non tecnica

---

## 2. FRESHA / MINDBODY / JANE APP — Onboarding Notifiche

### Jane App (gestionale cliniche)

**Approccio:** Wizard interno + Account Setup Consultation (call con team Jane schedulata dopo che l'utente ha esplorato il wizard da solo)

**Email notifications:** Completamente astratte dall'infrastruttura tecnica
- Nessuna configurazione SMTP, nessuna App Password
- Jane gestisce l'invio dal proprio dominio — l'utente imposta solo:
  1. Quando inviare (trigger: booking, cancellation, change)
  2. A chi inviare (staff + paziente)
  3. Delay (default: 3 minuti dopo booking per evitare duplicati)

**Pattern vincente:** La guida usa linguaggio azione-basato: "Quando un appuntamento viene prenotato..." → non "Configura il server SMTP". L'infrastruttura è completamente nascosta.

**Obbligatorio vs opzionale:** I trigger automatici (booking confermato) sono ON by default. L'utente può solo disabilitarli. Non c'è una fase di "attivazione" — funzionano subito.

### Mindbody

**Approccio:** Onboarding Wizard + Welcome Webinar + Kick-off Call obbligatoria

**Setup email:**
- Wizard copertura: staff management, auto emails, reporting
- Auto emails: ON by default con template pre-configurati
- L'utente personalizza template e timing — non configura infrastruttura
- Miglioramento 2024: indicatore rapido quali auto-email sono attive (toggle list invece di menu annidato)
- Raccolta opt-in marketing: gestita inline con checkbox pre-impostata (transactional sempre on, promotional opt-in)

**Pattern:** Email funziona subito out-of-the-box senza setup. La personalizzazione avanzata è deferred.

### Fresha

**Approccio:** Completamente self-service, nessuna call obbligatoria, help articles + video

**Email/notifiche:**
- Appointment reminders: email only by default (SMS è addon a pagamento)
- Configurazione: Settings → Notifications → toggle per tipo evento
- Gestione destinatari: Settings → Online Booking → Notifications per controllo granulare chi riceve cosa
- Zero configurazione SMTP — Fresha invia dal suo dominio

**Differenza chiave vs FLUXION:** Fresha è cloud, il dominio mittente è fresha.com. FLUXION è desktop offline-first → il problema di "da quale email mando i reminder?" è reale e richiede configurazione.

---

## 3. GMAIL OAUTH 2026 — Analisi Completa

### Timeline Deprecazioni Google (DEFINITIVA)

| Data | Evento |
|------|--------|
| Giugno 2024 | Rimossa impostazione "Less Secure Apps" da Google Admin. Nuovi utenti non possono creare connessioni basic auth. |
| Settembre 2024 | Enforcement per Google Sync e LSA (Less Secure Apps) per tutti gli account consumer |
| Marzo 14, 2025 | **Hard enforcement completo**: CalDAV, CardDAV, IMAP, SMTP, POP non funzionano più con password legacy (basic auth). |
| Maggio 1, 2025 | Final enforcement per account Google Workspace residui |
| Novembre 2025 | Escalation: Google passa da soft rejection a hard rejection messaggi non autenticati via SMTP |
| **App Password** | **Ancora funzionante** — non pianificata deprecazione. È l'alternativa "legacy" per device che non supportano OAuth (stampanti multifunzione, scanner, app vecchie) |

### App Password: Stato Attuale 2026

**Non sono deprecate.** Google le mantiene come escape hatch per device non-OAuth (MFP, scanner industriali, app legacy).

**Come funzionano con IMAP/SMTP 2026:**
- Richiedono autenticazione a 2 fattori attiva sull'account Google
- Si generano da `myaccount.google.com/apppasswords`
- La "password" generata (16 caratteri) funziona al posto della password normale per SMTP/IMAP
- **Importante:** richiedono che l'utente abiliti 2FA se non l'ha già — questo è un friction point significativo

**Problema per FLUXION con App Password:**
1. L'utente deve attivare 2FA (se non l'ha) — step fuori dall'app
2. L'utente deve navigare su Google, creare App Password, copiarla
3. Procedura incomprensibile per parrucchieri/estetiste non tecniche
4. Se l'utente cambia password Google, l'App Password smette di funzionare (richiede rigenerazione)
5. Google può revocarle senza preavviso in futuro

### Gmail OAuth2 in Tauri Desktop — Fattibilità 2026

**Risposta breve: Fattibile e raccomandato.**

**Plugin disponibili:**
- `tauri-plugin-google-auth` (crates.io): Tauri v2, OAuth2 + PKCE, token refresh, macOS/Windows/Linux
- `tauri-plugin-oauth` (FabianLars): approccio generico con localhost redirect server
- `tauri-plugin-google-auth` su GitHub (Choochmeque): specifico Google, più semplice

**Flusso tecnico:**
1. App apre URL di autorizzazione Google nel browser di sistema
2. Plugin spawna un localhost server temporaneo (es. `http://localhost:8080/callback`)
3. Google redirige a localhost dopo il consenso utente
4. Plugin cattura il code, lo scambia con access_token + refresh_token (PKCE)
5. Token salvati nel keychain di sistema (macOS Keychain, Windows Credential Manager)
6. Access token scade dopo 1 ora → refresh automatico con refresh_token (long-lived)
7. Se refresh_token revocato (utente ha revocato accesso da Google), l'app mostra "Riconnetti Gmail"

**Offline-first:** Con `access_type=offline` e `prompt=consent`, il refresh_token è long-lived. L'app funziona offline — usa il token cached. Quando torna online, refresh automatico.

**Scope per SMTP send:** `https://mail.google.com/` (scope completo) — necessario per SMTP

### Pro/Contro OAuth2 vs App Password per PMI Non-Tecnica

| Criterio | OAuth2 | App Password |
|----------|--------|--------------|
| Setup UX | "Connetti Gmail" → popup browser → done (1 click) | 6+ step fuori app, terminologia tecnica |
| Comprensibilità | Alta — flusso familiare (come login con Google) | Bassa — "App Password"? "16 caratteri"? |
| Manutenzione | Zero (token refresh automatico) | Rigenera se cambi password Google |
| Sicurezza | Altissima (PKCE, no password esposta) | Media (password permanente in chiaro) |
| Robustezza futura | Gold standard — Google non lo depreca | Potrebbe essere deprecata (no timeline) |
| Complessità implementazione | Media (plugin Tauri disponibili) | Bassa (SMTP classico con lettera) |
| Dipendenza Internet per setup | Sì (prima connessione) | Sì (generazione App Password) |
| Richiede 2FA Google | No | Sì — friction extra |

**Verdetto:** OAuth2 è l'unica scelta sensata per il 2026. App Password è accettabile solo come fallback per chi ha account Google Workspace enterprise con policy restrittive OAuth.

---

## 4. WIZARD LENGTH BEST PRACTICES — Dati 2025-2026

### Dati di Abbandono

| Metrica | Valore | Fonte |
|---------|--------|--------|
| Utenti che abbandonano se "troppi step" | 72% | UserGuiding 2026 |
| Completion rate media onboarding checklist | 19.2% (mediana 10.1%) | Userpilot 2025 benchmark |
| Completion con progress bar visibile | +40% vs senza | Vari studi 2024-2025 |
| Ogni minuto extra di onboarding | -3% conversion | Flowjam 2025 |
| Time-to-first-value target | < 2 minuti | B2B SaaS best practice |
| Utenti che preferiscono onboarding adattivo (skip known steps) | 74% | UserGuiding 2026 |
| Completion con full-screen obbligatori (Superhuman) | 98% | Superhuman case study |
| Completion con checklist opzionale | 20-30% | Industry average |
| Notion con progress indicator sottile | 55% completion | vs industry avg 20-30% |
| Onboarding completion con flussi personalizzati | +65% vs generici | Intercom |

### Step Count Ottimale

**Regola pratica 2025:** Max **5-7 step** per il wizard iniziale (core setup). Ogni step deve essere completabile in < 30 secondi.

**Progressione raccomandata:**
- Step 1-3: Obbligatori, bloccanti, valore immediato visibile dopo ogni step
- Step 4-5: Recommended (progress bar mostra quasi completo)
- Step 6+: Opzionali, deferred con reminder contestuale

**Il Zeigarnik Effect:** Iniziare il progress bar al 20% (non 0%) aumenta il senso di "quasi fatto", riducendo l'abbandono.

### Progressive Onboarding vs All-at-Once Wizard

**All-at-once wizard:**
- Pro: Utente sa esattamente quanti step mancano, setup completo prima dell'uso
- Contro: Cognitive overload, abbandono se uno step è troppo complesso (es. inserire SMTP password)
- Quando usare: Setup semplice e veloce (< 3 minuti), tutti i dati sono veramente necessari prima dell'uso

**Progressive onboarding:**
- Pro: Riduce friction iniziale, ogni feature viene spiegata nel contesto d'uso
- Contro: L'utente può usare il prodotto in modo subottimale se salta step importanti
- Quando usare: Prodotti complessi con molte feature, B2B con utenti avanzati

**Per FLUXION (PMI non tecnica):** Ibrido. Wizard breve (3-5 step, max 90 secondi) per setup essenziale, poi checklist contestuale per setup avanzato.

### Pattern per Step Opzionali

**Opzioni UX per step opzionali:**

1. **Skip esplicito (peggiore):** Bottone "Salta" → utente lo clicca senza pensarci → setup rimane incompleto
2. **Defer intelligente (migliore):** "Fallo dopo" con tooltip "Puoi configurarlo in qualsiasi momento da Impostazioni" + reminder contestuale la prima volta che serve
3. **Maybe Later (gold standard):** Copy "Magari dopo" (non "Salta") → ricorda che deve tornare → trigger re-engagement al primo evento contestuale
4. **Obbligatorio con pre-fill smart:** Se il sistema può indovinare un valore sensato, lo pre-compila e chiede conferma invece di lasciare il campo vuoto

**Dati su copy dei deferral button:**
- "Maybe later" > "Skip" per re-engagement (utenti tornano a completare)
- Evitare punteggiatura ("Maybe later..." con ellipsis = sembra che aspetti per sempre)
- Evitare finali bruschi: "Not now" sembra troppo definitivo
- Formula vincente: verbo corto + nessuna punteggiatura: "Magari dopo", "Configura dopo", "Ora no"

---

## 5. GAP ANALYSIS VS COMPETITOR — Cosa FLUXION Può Fare Meglio

### Il Problema Specifico di FLUXION

A differenza di Fresha/Mindbody (cloud, inviano email dal loro dominio), FLUXION è **desktop offline-first**. Questo significa:
- I reminder WA vengono già gestiti (APScheduler + Python)
- Ma per email reminder, serve che il saloncino configuri **il proprio account email** come mittente
- Questo è il vero friction point che nessun competitor gestisce bene (perché i competitor cloud evitano il problema)

### Gap Competitor Identificati

**Fresha:** Zero friction setup notifiche → perché è cloud e bypassa il problema. Se FLUXION diventasse cloud puro, eliminerebbe il problema. Ma FLUXION è offline-first per design.

**Mindbody:** Ha un onboarding wizard + Kick-off Call obbligatoria → funziona ma costoso (richiede team umano). Non scalabile per FLUXION.

**Jane App:** Setup consultation call opzionale + wizard self-service → buon modello. Ma Jane usa il proprio dominio email → zero SMTP config richiesta.

**Zoho CRM:** OAuth per email → buono, ma è web-app. Desktop è diverso.

**Nessun competitor desktop offline-first nel settore beauty/wellness ha risolto elegantemente il setup Gmail per PMI non tecniche.**

### Strategia FLUXION: Opzione A vs B

**Opzione A — Groq Key Bundled (setup AI senza friction):**

AC misurabile: L'utente arriva alla prima risposta AI in < 60 secondi dal primo avvio.

Pattern:
- Step 1 wizard: "FLUXION usa AI per rispondere ai clienti. Abbiamo incluso una chiave di prova gratuita valida X giorni."
- Nessun campo da compilare → AI funziona subito
- Dopo X giorni: contextual upsell "Inserisci la tua chiave Groq gratuita" con link diretto + video 30 secondi

Rischio: costo API key bundled. Mitigazione: key con rate limit aggressivo (es. 100 richieste/giorno), sufficiente per demo e primi giorni.

**Opzione B — Gmail OAuth Wizard (setup email con friction zero):**

AC misurabile: L'utente configura email reminder in < 2 minuti con 0 campi tecnici compilati.

Pattern:
1. Step 1 wizard (obbligatorio): Nome salone + nome titolare → 30 secondi
2. Step 2 wizard (obbligatorio): Numero WhatsApp → pre-compilato se SIM disponibile → 30 secondi
3. Step 3 wizard (opzionale, "Raccomandato"): "Vuoi inviare promemoria via email?" → "Sì, connetti Gmail" (OAuth popup) o "No, uso solo WhatsApp" → 45 secondi
4. Fine wizard → App aperta con dati reali

Per Gmail OAuth:
- Bottone unico: "Connetti il tuo Gmail" → popup browser sistema → Google OAuth flow standard
- L'utente non vede mai: SMTP, porta, App Password, IMAP
- Dopo connessione: test automatico (invio email di prova a se stesso) con feedback "Email configurata! Prova inviata a tuarmail@gmail.com"

**Opzione C — App Password Guidata (fallback):**

Per chi non vuole OAuth o usa Outlook/Yahoo/email business:
- Wizard inline con screenshot step-by-step (video 60 secondi o GIF animata)
- Copy: "Crea una password speciale per FLUXION" (non "App Password")
- Step numerati con screenshot Google: 1. Vai su account.google.com → 2. Cerca "password app" → 3. Copia i 16 caratteri → 4. Incollali qui
- Label campo: "Password speciale Google (16 caratteri)" con icona occhio per mostrare/nascondere

### Differenziatore FLUXION vs Tutti

**Nessun competitor ha fatto questo per il settore beauty/wellness desktop:**

1. **Pre-test silenzioso:** Dopo setup email, FLUXION manda automaticamente email di prova all'utente ("Test da FLUXION — tutto funziona!"). Questo conferma che il setup è corretto senza che l'utente debba sperare che funzioni.

2. **Fallback intelligente:** Se l'email del cliente non è configurata, i reminder vengono inviati solo via WA automaticamente. L'app non si blocca, non mostra errori — degrada gracefully.

3. **Re-engagement contestuale:** La prima volta che l'utente prenota un appuntamento per un cliente che ha email ma non l'ha configurata, appare un banner sottile: "Hai 3 appuntamenti domani — vuoi attivare i reminder email? [Connetti Gmail →]"

4. **Groq key come feature non come prerequisito:** A differenza di tool che bloccano sull'API key setup, FLUXION usa la Groq key bundled per la demo, poi propone la key personale come upgrade/personalizzazione — mai come prerequisito per usare l'app.

---

## DECISIONI RACCOMANDATE (AC MISURABILI)

### Decisione 1: Gmail OAuth come primary path

- **Implementazione:** `tauri-plugin-google-auth` v2 + PKCE + `access_type=offline`
- **AC:** Setup email completato da > 60% degli utenti nel wizard (vs ~10% con App Password guidata)
- **Fallback:** App Password guidata con screenshot per chi usa Gmail ma ha 2FA disabilitato o per Outlook/Yahoo/email business

### Decisione 2: Wizard 3 step obbligatori + 1 opzionale

```
Step 1 (30s, obbligatorio): Nome salone → Auto-fill da OS hostname se possibile
Step 2 (30s, obbligatorio): Numero WhatsApp → con validazione formato IT
Step 3 (45s, raccomandato): Connetti Gmail [bottone OAuth] oppure "Solo WhatsApp per ora"
→ Progress bar: inizia al 25% (Zeigarnik effect)
→ Fine wizard: app aperta, dati reali, WA già testato
```

- **AC:** Completion wizard > 80%, Time-to-first-value < 2 minuti

### Decisione 3: Groq key bundled con scadenza

- **Meccanismo:** Key bundled con rate limit 200 req/giorno, valida 30 giorni
- **Upsell:** Giorno 7: banner "La tua chiave AI gratuita scade tra 23 giorni. Creane una gratuita su Groq →"
- **AC:** > 50% utenti creano propria key entro 30 giorni (misurato da telemetria opt-in)

### Decisione 4: Deferral button copy

- Usare sempre "Configura dopo" (non "Salta", non "Skip")
- Il defer salva lo step come "da completare" e lo propone contestualmente
- Re-engagement: primo appuntamento prenotato → "Ora che hai il tuo primo cliente, vuoi attivare i reminder email?" [Connetti Gmail]

### Decisione 5: No email setup bloccante

- Il wizard non blocca su email se l'utente dice "No"
- L'app è pienamente funzionale con solo WhatsApp
- Email è addizione di valore, non prerequisito
- **Questo è il differenziatore vs Mindbody** che richiede setup completo prima dell'uso

---

## APPENDICE: Pattern Tecnico OAuth2 Tauri per Gmail SMTP

```rust
// tauri-plugin-google-auth approach
// Scope necessario per SMTP send:
const SCOPES: &[&str] = &[
    "https://mail.google.com/",  // SMTP via OAuth2
    "openid",
    "email",
    "profile",
];

// access_type=offline per refresh token long-lived
// prompt=consent per garantire refresh token (anche se già autorizzato)
```

```python
# Python side (reminder_scheduler.py) — Nodemailer equivalent
# Usare smtplib + OAuth2 con tokens dal keychain Tauri
import smtplib
from email.mime.text import MIMEText

def send_with_oauth2(to_email: str, subject: str, body: str, oauth_token: str):
    """
    Gmail SMTP con OAuth2 — token arriva da Tauri keychain
    """
    msg = MIMEText(body, 'html', 'utf-8')
    msg['From'] = f"Salone <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        # OAuth2 string format per Gmail SMTP
        auth_string = f"user={sender_email}\x01auth=Bearer {oauth_token}\x01\x01"
        smtp.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string.encode()).decode())
        smtp.send_message(msg)
```

**Token refresh:** Access token scade dopo 1 ora. Implementare auto-refresh prima di ogni invio email controllando expiry timestamp dal keychain.

---

## FONTI PRINCIPALI

- Gmail OAuth enforcement timeline: Google Workspace Admin Help + GetMailbird 2026
- Superhuman onboarding metrics: First Round Review (Superhuman Onboarding Playbook)
- UserGuiding 100+ onboarding statistics 2026
- Tauri OAuth2 implementation: crates.io tauri-plugin-google-auth, DEV Community
- Jane App email notifications: jane.app/guide/email-notifications
- Mindbody Setup Checklist + Learning Center
- Flowjam SaaS Onboarding Best Practices 2025
- Userpilot Onboarding Checklist Completion Rate Benchmarks 2025
- 1Password Getting Started: support.1password.com
- Notion onboarding analysis: GoodUX/Appcues
- Progressive onboarding patterns: UserGuiding Blog
- Deferral button UX copy: Medium / Riya Jawandhiya 2025
