# CTO Playbook — Indie Desktop Enterprise-Grade Software 2026

> Deep Research CoVe 2026 — Sessione S103
> Benchmark: Obsidian, Raycast, Linear, Figma Desktop, 1Password, Notion Desktop, Craft, Bear, Things 3
> Focus: FLUXION — desktop app per PMI italiane, team 1 persona, Tauri + React + SQLite

---

## 1. QA PRE-RELEASE CHECKLIST

### Come operano i migliori team indie

**Obsidian** (team ~10 persone):
- Canary channel: build automatica ogni commit su main, utenti opt-in (~5% userbase)
- Beta channel: release candidate settimanale, community Discord testa e riporta
- Stable: solo dopo 2+ settimane senza regressioni in beta
- Ogni release ha changelog dettagliato con link ai bug fix
- Test interni: combinazione manuale + automated, focus su plugin compatibility

**Raycast** (team ~30):
- Dogfooding intensivo: tutto il team usa la versione corrente ogni giorno
- Beta TestFlight per macOS (fino a 10.000 tester)
- Automated e2e per i flussi critici (search, extensions, clipboard)
- Performance regression: misurano launch time, memory footprint, CPU idle

**Linear** (team ~50):
- Feature flags per rollout graduale (1% -> 10% -> 50% -> 100%)
- Automated visual regression testing (Percy/Chromatic)
- Zero-downtime deploy con rollback automatico

**1Password** (desktop, security-critical):
- Penetration testing prima di ogni major release
- Automated fuzzing su input parsing
- Signed builds con notarizzazione, reproducible builds

### Checklist Pre-Release FLUXION (P0-P2)

#### P0 — Bloccanti (MUST prima di ogni release)

- [ ] `npm run type-check` → 0 errori
- [ ] `npm run build` → build completa senza warning critici
- [ ] Build Tauri su iMac → `.app` + `.dmg` generati
- [ ] Smoke test manuale: avvio app → wizard → prima operazione (5 min max)
- [ ] Test DB migration: DB vuoto → tutte le migration → app funziona
- [ ] Test DB migration: DB versione precedente → upgrade → dati preservati
- [ ] Zero secrets in codebase: `grep -r "sk-\|api_key\|password" src/` → 0 match reali
- [ ] Codesign + notarizzazione macOS (quando attiva)
- [ ] File size check: DMG < 100MB, non cresce senza motivo
- [ ] Crash-free: nessun panic Rust, nessun unhandled rejection JS in 10 min uso

#### P1 — Importanti (SHOULD prima di release)

- [ ] E2E test Playwright: flussi critici (login wizard, crea cliente, crea appuntamento)
- [ ] Performance baseline: app launch < 3s, navigazione pagine < 500ms
- [ ] Memory: dopo 30 min uso, RSS < 300MB
- [ ] SQLite WAL mode attivo, backup funzionante
- [ ] Voice pipeline health check (se Sara attiva): `/health` risponde < 1s
- [ ] Test offline: app funziona senza internet (calendario, clienti, cassa)
- [ ] Test su schermo 1366x768 (minimo supportato)
- [ ] Changelog scritto e comprensibile per utente PMI

#### P2 — Nice to have

- [ ] Visual regression su schermate chiave (screenshot comparison)
- [ ] Test con dati realistici (100+ clienti, 500+ appuntamenti)
- [ ] Test update in-place (versione N-1 → versione N)
- [ ] Test con antivirus attivo (Windows)
- [ ] Accessibility check: navigazione keyboard, contrast ratio

### Beta Testing Strategy per FLUXION

**Fase 1 — Alpha interna (ora)**
- Dogfooding: usare FLUXION per gestire i propri appuntamenti/demo
- 2-3 persone fidate (amici con attivita') testano la versione corrente

**Fase 2 — Beta chiusa (primi 30 acquirenti)**
- Canale Telegram/WhatsApp dedicato per feedback rapido
- Google Form strutturato dopo 7 giorni di uso
- Promessa: "I primi 30 clienti plasmano il prodotto"
- Incentivo: sconto 30% o upgrade gratuito Base -> Pro

**Fase 3 — Beta aperta (dopo 100 vendite)**
- Auto-update con canale "beta" opt-in nelle impostazioni
- Crash reporter automatico (opt-in, privacy-first)
- Changelog in-app con "Novita'" badge

---

## 2. PMI USER TESTING FRAMEWORK

### Profilo Utente Target

| Attributo | Valore tipico |
|-----------|---------------|
| Eta' | 35-55 anni |
| IT skills | Basse — usa WhatsApp, Facebook, Excel base |
| Device | PC Windows 10/11 (80%), Mac (20%) |
| Tempo disponibile | Max 15 min per test |
| Motivazione | "Voglio qualcosa che funzioni subito" |
| Frustrazioni | Software complicati, abbonamenti, supporto lento |

### Protocollo di Test — 5 Fasi

#### Fase 1 — Reclutamento (P0)

**Dove trovare tester PMI italiani:**
1. **Rete personale**: parrucchiere, estetista, meccanico, dentista di fiducia
2. **Gruppi Facebook**: "Parrucchieri Italia", "Gestione Salone", "Estetiste Italiane"
3. **Associazioni**: CNA, Confcommercio, Confartigianato (sezioni locali)
4. **Fiere**: Cosmoprof, Autopromotec (stand o networking)
5. **Cold outreach**: Google Maps → saloni/palestre zona → visita con demo

**Quanti tester?** 5-8 per round (Jakob Nielsen: 5 utenti trovano l'85% dei problemi di usabilita')

**Incentivo**: 30 min del loro tempo → licenza gratuita o sconto 50%

#### Fase 2 — Setup Test (P0)

**Preparazione:**
- PC pulito (o VM) con Windows 10/11 — NO ambiente dev
- Installare FLUXION dal DMG/MSI come farebbe un cliente
- Screen recording attivo (OBS, gratuito) — chiedere consenso
- Foglio con 5 scenari stampato (non sullo schermo)

**Ambiente:**
- Nel loro salone/studio (contesto reale) oppure
- Video call con condivisione schermo (Zoom/Meet)

#### Fase 3 — Scenari di Test (P0)

**Scenario 1 — Primo Avvio (critico)**
> "Hai appena comprato FLUXION. Installalo e configuralo per il tuo salone."
- Misurare: tempo da download a primo appuntamento creato
- Target: < 10 minuti
- Osservare: dove si blocca? Cosa non capisce?

**Scenario 2 — Crea Appuntamento**
> "La signora Maria Rossi vuole un taglio e piega per giovedi' alle 15:00 con Lucia."
- Misurare: click necessari, tempo, errori
- Target: < 30 secondi, max 4 click

**Scenario 3 — Gestisci Cliente**
> "Cerca la scheda di Marco Bianchi e aggiungi una nota: allergia al nichel."
- Misurare: trovabilita' ricerca, completamento task

**Scenario 4 — Chiama Sara (se disponibile)**
> "Chiama il numero del salone e prenota un appuntamento parlando con Sara."
- Misurare: comprensione Sara, completamento booking, soddisfazione

**Scenario 5 — Fine Giornata**
> "Guarda gli appuntamenti di oggi e chiudi la cassa."
- Misurare: trovabilita' funzioni, comprensione report

#### Fase 4 — Raccolta Feedback (P0)

**Durante il test (osservazione):**
- Annotare: dove esita, dove clicca nel posto sbagliato, cosa dice ad alta voce
- MAI aiutare o suggerire — "Cosa faresti adesso?"
- Contare: errori, richieste di aiuto, momenti di frustrazione

**Dopo il test (questionario — Google Form, 5 min):**

```
1. Da 1 a 10, quanto e' stato facile configurare FLUXION? [slider]
2. Da 1 a 10, quanto e' stato facile creare un appuntamento? [slider]
3. Cosa ti ha confuso di piu'? [testo libero]
4. Cosa ti e' piaciuto di piu'? [testo libero]
5. Useresti FLUXION al posto di carta/agenda/Excel? [Si/No/Forse]
6. Quanto pagheresti per questo software? [scelta multipla]
7. Consiglieresti FLUXION a un collega? (0-10) [NPS]
```

**SUS (System Usability Scale)** — 10 domande standard, score target > 72 (sopra la media)

#### Fase 5 — Iterazione (P1)

**Dopo ogni round di 5 tester:**
1. Aggregare problemi per frequenza (>3/5 utenti = P0)
2. Fix i top 3 problemi
3. Ri-testare con 3 nuovi utenti
4. Ripetere fino a SUS > 75 e task completion > 90%

### Metriche Target

| Metrica | Target | Strumento |
|---------|--------|-----------|
| Task completion rate | > 90% | Osservazione manuale |
| Time to first appointment | < 10 min | Cronometro |
| SUS Score | > 75 (buono) | Questionario post-test |
| NPS | > 40 (buono) | Domanda singola |
| Error rate | < 2 per scenario | Osservazione |
| "Userei al posto di carta" | > 80% Si | Questionario |

### Tool Consigliati

| Tool | Uso | Costo |
|------|-----|-------|
| Google Forms | Questionari post-test | Gratuito |
| OBS Studio | Screen recording | Gratuito |
| Zoom/Meet | Test remoti | Gratuito |
| Notion/Sheets | Aggregazione risultati | Gratuito |
| Maze | Test non moderati (fase 3+) | $99/mese |
| Hotjar | Heatmap in-app (se web) | N/A per desktop |

**Per FLUXION desktop: Google Forms + OBS + osservazione diretta e' sufficiente fino a 100 clienti.**

---

## 3. REGOLE OPERATIVE CTO — INDIE DESKTOP SOFTWARE

### 3.1 Decision Framework: Quando Dire "No" a una Feature (P0)

**Il filtro a 5 domande (tutte devono essere SI):**

1. **Serve a > 60% degli utenti target?**
   - No → Feature per nicchia, metti in backlog P2
   - "Ma quel cliente lo vuole!" → Un cliente non e' un mercato

2. **Risolve un problema che blocca una vendita o causa churn?**
   - No → Nice-to-have, non prioritario
   - Si → P0 o P1

3. **Posso implementarlo in < 1 settimana (team 1 persona)?**
   - No → Scomponilo in sotto-feature piu' piccole
   - Se non scomponibile → e' un progetto, non una feature

4. **Aumenta la complessita' del codice significativamente?**
   - Si → Il costo di manutenzione supera il beneficio?
   - Regola: ogni feature aggiunta rende le prossime piu' lente

5. **Lo farebbe Obsidian/Linear?**
   - No → Probabilmente e' scope creep
   - "Ma noi siamo diversi" → quasi sempre una scusa

**Dire NO in pratica:**
- Rispondi: "Ottima idea, la metto in roadmap per la v2."
- Scrivi in un file `FEATURE_REQUESTS.md` con data e richiedente
- Revisiona ogni trimestre: se > 5 richiedenti diversi → rivaluta

### 3.2 Technical Debt Management per Team 1 Persona (P0)

**Regola del 20%:**
- Ogni 5 feature, dedica 1 sessione a debt reduction
- Non negoziabile: il debito tecnico si accumula con interessi composti

**Classificazione Debt:**

| Tipo | Esempio | Azione |
|------|---------|--------|
| **Critico** | Nessun backup DB, no error handling | Fix PRIMA della prossima feature |
| **Strutturale** | Componenti > 500 righe, no test | Refactor quando tocchi quel file |
| **Cosmetico** | Naming inconsistente, commenti stale | Fix durante code review |
| **Intenzionale** | Shortcut documentato con TODO | Accettabile se ha deadline |

**Regole pratiche:**
- MAI lasciare un `// TODO` senza data e contesto
- Se un file supera 400 righe → splitta al prossimo tocco
- Se un bug ritorna 2 volte → scrivi un test, non patchare
- Tieni un `TECH_DEBT.md` con stime di effort

### 3.3 Release Cadence (P0)

**Raccomandazione per FLUXION: Release mensile regolare**

| Cadence | Pro | Contro | Per chi |
|---------|-----|--------|---------|
| Rolling (ogni commit) | Feedback veloce | Instabile, utenti PMI confusi | SaaS, dev tools |
| Settimanale | Iterazione rapida | Troppo frequente per PMI | Beta channel |
| **Mensile** | **Prevedibile, gestibile** | **Ritardo feature** | **Desktop indie, PMI** |
| Trimestrale | Stabile | Troppo lento | Enterprise legacy |

**Calendario tipo:**
```
Settimana 1-2: Feature development
Settimana 3: Bug fix + QA + beta
Settimana 4: Release stable + changelog + comunicazione
```

**Versioning:** Semantic Versioning (1.0.0 → 1.1.0 per feature, 1.0.1 per bugfix)

**Hotfix:** fuori ciclo solo per P0 (crash, data loss, security)

### 3.4 Incident Response per Desktop (P1)

**Crash Reporting — Privacy-First:**

| Soluzione | Costo | Privacy | Raccomandazione |
|-----------|-------|---------|-----------------|
| Sentry (self-hosted) | Gratuito (self) | Ottima | Overkill per team 1 |
| Sentry cloud | $26/mese | Buona (GDPR) | Buona opzione |
| **Custom crash reporter** | **Gratuito** | **Totale controllo** | **Consigliato per FLUXION** |
| Aptabase | Gratuito OSS | Privacy-first | Ottimo per analytics |

**Custom crash reporter per FLUXION (consigliato):**
```
1. Rust panic hook → scrive crash log locale (JSON Lines)
2. Al riavvio: "FLUXION si e' chiuso inaspettatamente. Vuoi inviare il report?"
3. Se SI → POST a Cloudflare Worker con: versione, OS, stack trace (NO dati utente)
4. Worker salva in D1/KV → dashboard admin per CTO
```

**Triage incidenti:**

| Severita' | Definizione | SLA risposta | Azione |
|-----------|-------------|--------------|--------|
| P0 — Critico | Data loss, crash all'avvio, security | 4 ore | Hotfix immediato |
| P1 — Alto | Feature core non funziona | 24 ore | Fix nel prossimo minor |
| P2 — Medio | UI rotta, performance degradata | 1 settimana | Fix nel prossimo release |
| P3 — Basso | Cosmetico, edge case raro | Backlog | Quando possibile |

### 3.5 Security Posture per Desktop con SQLite (P0)

**Threat Model FLUXION:**
- Dati sensibili: clienti (nome, telefono, email), appuntamenti, note mediche (cliniche)
- Storage: SQLite locale, non cloud
- Rischio principale: accesso fisico al PC, malware, backup non cifrati

**Misure obbligatorie:**

| Misura | Priorita' | Stato FLUXION |
|--------|-----------|---------------|
| SQLite WAL mode | P0 | Attivo |
| Backup automatico DB | P0 | Da implementare |
| Cifratura DB (SQLCipher) | P1 | Da valutare — obbligatorio per dati medici |
| No secrets in codice | P0 | Verificato |
| HTTPS per tutte le API call | P0 | Attivo (Cloudflare Worker) |
| License key Ed25519 (non crackabile banalmente) | P0 | Implementato |
| Input sanitization (SQL injection) | P0 | Parametrized queries in Rust |
| Auto-lock dopo inattivita' (opzionale) | P2 | Da implementare |
| Log audit trail operazioni sensibili | P1 | Parziale |
| GDPR: export + cancellazione dati cliente | P0 | Da implementare |

**Per dati medici (tier Clinic):**
- SQLCipher con master password utente
- Export dati cifrato
- Audit trail completo (chi ha visto/modificato cosa)
- Consenso informato tracking

---

## 4. GO-TO-MARKET CHECKLIST — PRIMA VENDITA

### 4.1 Landing Page Requirements (P0)

**Benchmark: le landing page che convertono meglio nel 2026**

Struttura obbligatoria (above the fold → CTA):

```
1. HERO: Headline benefit-driven + sottotitolo + CTA primario
   "Gestisci il tuo salone in meta' tempo. Zero abbonamenti."
   [Prova FLUXION — €497 una tantum]

2. SOCIAL PROOF: "Usato da X saloni/palestre/studi in Italia"
   → Prima delle vendite: testimonianza beta tester
   → Dopo 10 vendite: numero reale + citazioni

3. DEMO VIDEO: 60-90 secondi, senza voce (musica + testo)
   → Mostra: wizard → crea cliente → crea appuntamento → Sara risponde
   → Hosting: YouTube unlisted o Vimeo

4. FEATURE GRID: 3 pilastri con icone
   📱 Comunicazione | 🎯 Marketing | ⚙️ Gestione

5. PRICING: chiaro, comparativo (vs abbonamento mensile competitor)
   "€497 una tantum vs €49/mese = risparmi €1.091 in 3 anni"

6. FAQ: 5-7 domande (funziona offline? serve internet? garanzia?)

7. FOOTER: Privacy Policy, ToS, P.IVA, contatti
```

**Elementi che aumentano conversione:**
- Garanzia 30 giorni soddisfatti o rimborsati (PROMINENTE)
- "Nessun abbonamento" ripetuto 3+ volte
- Screenshot reali dell'app (non mockup)
- Prezzo barrato competitor ("Fresha: €588/anno. FLUXION: €497 per sempre")
- Badge: "Made in Italy", "Privacy-first", "Funziona offline"

### 4.2 Legal — GDPR + Privacy + ToS (P0)

**Documenti obbligatori per vendita software in Italia:**

| Documento | Obbligatorio | Note |
|-----------|-------------|------|
| **Privacy Policy** | SI (GDPR) | Cosa raccoglie l'app, dove salva, diritti utente |
| **Terms of Service** | SI | Licenza, garanzia, limitazioni responsabilita' |
| **Cookie Policy** | SI (landing) | Solo se landing usa cookie/analytics |
| **Informativa ex art. 13 GDPR** | SI | Per dati raccolti dall'app |
| **DPIA** | Forse | Se tratta dati sanitari su larga scala |
| **Condizioni di vendita** | SI | Per LemonSqueezy/e-commerce |

**GDPR per FLUXION (app desktop):**

Dato che FLUXION salva dati LOCALMENTE sul PC del cliente:
- FLUXION e' un **strumento** (data processor tool), il titolare del trattamento e' il cliente PMI
- FLUXION NON raccoglie dati utente → privacy policy semplice
- Eccezioni: phone-home (licenza), crash reports, Sara (audio → Groq API)
- Per Sara: informativa che audio viene processato da API terze (Groq/Cerebras)
- Diritto all'oblio: funzione "Elimina tutti i dati cliente" nell'app

**Azione P0:** Generare Privacy Policy e ToS con template italiano (iubenda.com ~€29/anno oppure template avvocato ~€300 una tantum)

### 4.3 Fiscalita' — IVA e Fattura Elettronica (P0)

**Vendita software digitale in Italia:**

| Aspetto | Regola |
|---------|--------|
| IVA | 22% su vendita a privati/P.IVA italiani |
| B2B EU | Reverse charge (IVA 0% con P.IVA valida) |
| B2C extra-EU | Dipende da paese, LemonSqueezy gestisce |
| Fattura elettronica | Obbligatoria per vendite B2B Italia (SDI) |
| Ricevuta | Per vendite B2C via LemonSqueezy: LemonSqueezy emette ricevuta |
| Regime forfettario | Se applicabile: 5% o 15% flat, no IVA, no fattura elettronica |

**Con LemonSqueezy come Merchant of Record:**
- LemonSqueezy gestisce IVA, ricevute, rimborsi
- Tu ricevi il netto (dopo commissione LemonSqueezy ~5% + payment fees)
- Devi comunque dichiarare i ricavi nel tuo regime fiscale
- Consulta commercialista per regime corretto (forfettario vs ordinario)

### 4.4 Support — Knowledge Base Self-Service (P0)

**Principio FLUXION: ZERO supporto personale. Tutto self-service.**

| Canale | Priorita' | Implementazione |
|--------|-----------|-----------------|
| **Video tutorial in-app** | P0 | 5-7 video da 2 min ciascuno (Loom/OBS) |
| **FAQ in-app** | P0 | Sezione Aiuto con 20 domande frequenti |
| **Guide passo-passo** | P0 | Pagina web statica (Cloudflare Pages) |
| **Email automatica post-acquisto** | P0 | Sequenza 3 email (benvenuto, setup, tips) |
| **Chatbot FAQ** | P1 | Widget sulla landing (Tidio/Crisp free tier) |
| **Video YouTube** | P1 | Playlist pubblica "FLUXION Tutorial" |
| Supporto email | P2 | Solo per bug critici, max 48h risposta |
| Community Discord | P2 | Solo dopo 50+ clienti |
| Supporto telefonico | MAI | Non scalabile per team 1 persona |

**Sequenza email post-acquisto (automazione LemonSqueezy/Mailchimp):**
```
Email 1 (immediata): Link download + guida installazione + video primo avvio
Email 2 (giorno 3): "Hai configurato Sara?" + link tutorial voice
Email 3 (giorno 7): "Consigli avanzati" + link FAQ + richiesta feedback (Google Form)
Email 4 (giorno 30): "Come va?" + NPS + richiesta recensione
```

### 4.5 Onboarding — First-Run Experience (P0)

**Gold standard 2026 — Principi:**
1. **Time to value < 5 minuti** — dall'apertura app alla prima azione utile
2. **Progressive disclosure** — non mostrare tutto subito
3. **Sample data opzionale** — "Vuoi vedere FLUXION con dati demo?"
4. **Wizard max 7 step** — gia' implementato in FLUXION
5. **Skip possibile** — ogni step deve essere skippabile tranne la nicchia

**Checklist onboarding FLUXION:**
- [x] Wizard 7 step (nicchia, info salone, operatori, servizi, orari, email, riepilogo)
- [ ] Video intro 30s nel wizard (opzionale, auto-play muto)
- [ ] Sample data: "Carica dati esempio per esplorare?" [Si/No]
- [ ] Tooltip tour dopo wizard: 5 hotspot sulle funzioni principali
- [ ] Celebrazione: "Tutto pronto! Crea il tuo primo appuntamento" con animazione

---

## 5. POST-LAUNCH OPERATIONS

### 5.1 Monitoring — Privacy-First Analytics (P1)

**Opzioni per desktop app:**

| Soluzione | Costo | Privacy | Raccomandazione |
|-----------|-------|---------|-----------------|
| **Aptabase** | Gratuito OSS | Privacy-first, no PII | Migliore per indie desktop |
| PostHog (self-hosted) | Gratuito | Totale controllo | Overkill |
| Plausible | $9/mese | Privacy-first | Solo web |
| Custom (CF Worker) | Gratuito | Totale controllo | Consigliato per FLUXION |
| Google Analytics | Gratuito | Pessima (GDPR issues) | MAI |

**Cosa tracciare (opt-in, anonimo):**
```
- App version + OS + screen resolution
- Feature usage: quali schermate visita, quanto tempo
- Funnel: wizard completion rate, first appointment time
- Errori: crash count, tipo errore (NO stack trace con dati)
- Sara: usage rate, completion rate booking vocale
- Performance: launch time, response time
```

**Cosa MAI tracciare:**
```
- Dati clienti (nomi, telefoni, email)
- Contenuto appuntamenti/note
- Audio/testo conversazioni Sara
- Posizione GPS
- Qualsiasi dato identificativo
```

**Implementazione consigliata per FLUXION:**
- Riutilizzare il Cloudflare Worker (phone-home) gia' attivo
- Aggiungere endpoint `/analytics` che riceve eventi anonimi
- Dashboard: Cloudflare D1 + pagina admin semplice
- Opt-in al primo avvio: "Aiutaci a migliorare FLUXION inviando dati anonimi di utilizzo"

### 5.2 Feedback Loop (P0)

**In-app feedback (implementare subito):**
- Bottone "Feedback" fisso in sidebar o menu Aiuto
- Click → modal con: rating 1-5 stelle + testo libero + screenshot opzionale
- Invia a Cloudflare Worker → salva in D1 → notifica email al CTO
- Frequenza: max 1 prompt automatico ogni 30 giorni

**NPS (Net Promoter Score):**
- Chiedere dopo 14 giorni di uso: "Da 0 a 10, consiglieresti FLUXION?"
- Detractors (0-6): chiedere "Cosa possiamo migliorare?"
- Promoters (9-10): chiedere "Lasceresti una recensione?"
- Target NPS: > 40 (buono), > 60 (eccellente)

**Feature requests:**
- File `FEATURE_REQUESTS.md` mantenuto dal CTO
- Ogni richiesta: data, fonte (email/feedback/form), descrizione, voti
- Revisione mensile: top 3 richieste → valutare con filtro 5 domande

### 5.3 Update Strategy (P0)

**Auto-update per Tauri:**
- Tauri ha updater built-in (endpoint JSON con versione + URL download)
- Hosting update manifest: GitHub Releases o Cloudflare R2
- Flusso: app controlla update all'avvio → notifica "Aggiornamento disponibile" → download in background → installa al riavvio
- MAI forzare update (utente PMI puo' essere nel mezzo di un appuntamento)

**DB Migration Strategy:**
- Gia' implementata in FLUXION (custom migration runner in `lib.rs`)
- Regola: ogni migration DEVE essere idempotente e backward-compatible
- Test obbligatorio: DB v(N-1) → migration → app funziona
- Backup automatico DB prima di ogni migration
- Rollback: mantenere backup pre-migration per 30 giorni

**Changelog:**
- In-app: sezione "Novita'" con badge "NEW" dopo update
- Sul sito: pagina `/changelog` pubblica
- Formato: data + versione + lista cambiamenti (linguaggio utente, non tecnico)
  - SI: "Ora puoi aggiungere foto ai servizi"
  - NO: "Implementato upload immagini con resize WASM e storage blob SQLite"

### 5.4 Community (P1)

**Raccomandazione per FLUXION — Approccio graduale:**

| Fase | Clienti | Canale | Effort CTO |
|------|---------|--------|------------|
| 0-30 | Early adopter | WhatsApp gruppo | 10 min/giorno |
| 30-100 | Crescita | Telegram canale + gruppo | 20 min/giorno |
| 100-500 | Scala | FAQ + video + email auto | 30 min/giorno |
| 500+ | Maturita' | Community forum (Discourse) | Delegare |

**WhatsApp gruppo (fase 0-30):**
- Max 30 persone, diretto, personale
- "Sei tra i primi 30 clienti FLUXION — la tua voce conta"
- Raccogli feedback, bug, idee
- Quando superi 30: migra a Telegram (piu' scalabile, no limite)

**MAI Discord per utenti PMI italiani** — non lo usano. Telegram o WhatsApp.

---

## 6. PRIORITA' COMPLESSIVE — AZIONI ORDINATE

### P0 — PRIMA DELLA PRIMA VENDITA (bloccanti)

| # | Azione | Effort | Stato |
|---|--------|--------|-------|
| 1 | Smoke test manuale completo (wizard → appuntamento → Sara) | 2h | Da fare |
| 2 | Test su PC pulito (VM Windows o Mac fresh) | 2h | Da fare |
| 3 | Privacy Policy + ToS (italiano, template iubenda) | 3h | Da fare |
| 4 | Landing page: pricing chiaro + garanzia + FAQ | 4h | Parziale |
| 5 | Email post-acquisto automatica con guida | 2h | Da fare |
| 6 | 3 video tutorial (installazione, primo uso, Sara) | 4h | Da fare |
| 7 | LemonSqueezy: checkout funzionante + webhook | 4h | Parziale |
| 8 | DB migration test (vuoto → tutte migration) | 1h | Da fare |
| 9 | GDPR: funzione "Elimina dati cliente" nell'app | 3h | Da fare |
| 10 | Backup automatico DB (pre-update + schedulato) | 3h | Da fare |

### P1 — PRIMI 30 GIORNI POST-LANCIO

| # | Azione | Effort |
|---|--------|--------|
| 11 | Crash reporter custom (Rust panic hook + CF Worker) | 4h |
| 12 | In-app feedback button | 2h |
| 13 | Auto-update Tauri configurato | 4h |
| 14 | User testing con 5 PMI reali | 8h |
| 15 | Analytics anonime opt-in (Aptabase o custom) | 4h |
| 16 | NPS prompt dopo 14 giorni | 2h |
| 17 | Changelog in-app | 2h |
| 18 | FAQ in-app (20 domande) | 3h |

### P2 — PRIMI 90 GIORNI

| # | Azione | Effort |
|---|--------|--------|
| 19 | E2E test Playwright per flussi critici | 8h |
| 20 | Performance baseline automatizzata | 4h |
| 21 | Visual regression testing | 4h |
| 22 | Beta channel opt-in | 4h |
| 23 | Community Telegram | 1h setup |
| 24 | Knowledge base web (Cloudflare Pages) | 4h |
| 25 | SQLCipher per tier Clinic (dati medici) | 8h |

---

## 7. PRINCIPI CTO — REGOLE D'ORO

### Le 10 Regole del CTO Indie Desktop 2026

1. **Ship > Perfect.** Un prodotto buono oggi batte uno perfetto fra 6 mesi. Ma "buono" significa zero crash e dati sicuri.

2. **Il tuo tempo e' il collo di bottiglia.** Ogni feature aggiunta e' una feature da mantenere. Dici "no" il 90% delle volte.

3. **Un utente che perde dati e' un utente perso per sempre.** Backup, migration, WAL mode non sono opzionali.

4. **Testa su PC reali, non sul tuo Mac da sviluppatore.** Il 80% dei tuoi clienti ha un PC Windows con 8GB RAM e 10 programmi in background.

5. **L'onboarding E' il prodotto.** Se non funziona in 5 minuti, non esiste.

6. **Zero supporto manuale scala. L'email non scala.** Ogni domanda ricevuta = un video/FAQ da creare per non riceverla mai piu'.

7. **Misura prima di ottimizzare.** Non indovinare cosa serve ai clienti. Chiedi, osserva, misura.

8. **Release prevedibili > release frequenti.** I tuoi clienti PMI vogliono stabilita', non novita' ogni settimana.

9. **Privacy e' un feature, non un costo.** "I tuoi dati restano sul tuo PC" e' un vantaggio competitivo enorme vs SaaS.

10. **Il primo cliente paga piu' di quanto pensi.** Non in soldi — in feedback, referral, e proof che il prodotto funziona nel mondo reale.

---

## APPENDICE A — Template Documenti

### Privacy Policy (outline italiano)

```
INFORMATIVA SULLA PRIVACY — FLUXION

Titolare del trattamento: [Nome, P.IVA, indirizzo]
Email: fluxion.gestionale@gmail.com

1. DATI RACCOLTI DALL'APPLICAZIONE
   - L'applicazione FLUXION salva i dati esclusivamente sul dispositivo dell'utente
   - Nessun dato viene trasferito a server esterni, ad eccezione di:
     a) Verifica licenza (codice licenza, versione app, OS)
     b) Assistente vocale Sara (audio processato da servizi AI terzi)
     c) Crash report anonimi (solo se autorizzati dall'utente)

2. BASE GIURIDICA
   - Esecuzione contratto (licenza software)
   - Consenso (per crash report e analytics)
   - Legittimo interesse (verifica licenza anti-pirateria)

3. DIRITTI DELL'UTENTE
   - Accesso, rettifica, cancellazione, portabilita' dei propri dati
   - I dati sono sul proprio dispositivo: l'utente ha gia' il pieno controllo
   - Per esercitare diritti relativi ai dati trasmessi: email a [contatto]

4. CONSERVAZIONE
   - Dati locali: finche' l'utente non li cancella
   - Dati licenza su server: per la durata della licenza
   - Crash report: 90 giorni

5. SICURITA'
   - Dati locali protetti dalle credenziali del sistema operativo
   - Comunicazioni cifrate (HTTPS/TLS 1.3)
   - Licenza verificata con crittografia Ed25519
```

### Terms of Service (outline italiano)

```
CONDIZIONI GENERALI DI LICENZA — FLUXION

1. OGGETTO: licenza d'uso perpetua (lifetime) del software FLUXION
2. CONCESSIONE: uso su 1 (uno) dispositivo, uso commerciale consentito
3. RESTRIZIONI: divieto di reverse engineering, redistribuzione, sublicenza
4. GARANZIA: 30 giorni soddisfatti o rimborsati dal momento dell'acquisto
5. LIMITAZIONE RESPONSABILITA': il software e' fornito "as is"
6. ASSISTENTE VOCALE: Sara utilizza servizi AI di terze parti inclusi nella licenza
7. AGGIORNAMENTI: inclusi per la versione major corrente (1.x)
8. DATI: i dati dell'utente restano sul suo dispositivo — nessun accesso da parte nostra
9. FORO COMPETENTE: [Tribunale competente]
10. LEGGE APPLICABILE: legge italiana
```

---

## APPENDICE B — Metriche di Successo per Fase

| Fase | Metrica | Target | Come misurare |
|------|---------|--------|---------------|
| Pre-lancio | Wizard completion (test) | 100% su 5 tester | Osservazione |
| Pre-lancio | Time to first appointment | < 10 min | Cronometro |
| Lancio | Conversione landing | > 2% visitatori | Plausible/CF Analytics |
| Mese 1 | Vendite | > 10 licenze | LemonSqueezy dashboard |
| Mese 1 | Rimborsi | < 10% | LemonSqueezy |
| Mese 1 | NPS | > 30 | Survey in-app |
| Mese 3 | Vendite totali | > 50 licenze | LemonSqueezy |
| Mese 3 | Task completion rate | > 85% | User testing round 2 |
| Mese 3 | Crash-free rate | > 99% | Crash reporter |
| Mese 6 | Revenue | > €25.000 | LemonSqueezy |
| Mese 6 | NPS | > 50 | Survey |
| Anno 1 | Clienti attivi | > 200 | Phone-home analytics |
| Anno 1 | Churn (inattivi) | < 20% | Phone-home |

---

> **Documento generato**: 2026-03-20, Sessione S103
> **Benchmark**: Obsidian, Raycast, Linear, Figma Desktop, 1Password, Things 3, Bear, Craft
> **Applicabilita'**: FLUXION — desktop app Tauri per PMI italiane, team 1 persona
> **Prossima revisione**: dopo primi 30 clienti
