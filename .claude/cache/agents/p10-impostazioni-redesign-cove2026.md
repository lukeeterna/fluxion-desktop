# CoVe 2026 — Settings/Preferences Page Redesign Research
## FLUXION Impostazioni — Deep Research

**Data**: 2026-03-10
**Scope**: Settings/Preferences page design per desktop SaaS B2B — gold standard 2026 + gap analysis FLUXION vs competitor

---

## 1. GOLD STANDARD 2026 — STRUTTURA SETTINGS

### 1.1 Pattern Dominante: Left Sidebar Verticale

Il pattern dominante nel 2026 tra i tool B2B desktop-first è la **sidebar verticale sinistra**, non i tab orizzontali. La transizione dai tab alle sidebar è avvenuta tra 2022-2024 e si è consolidata nel 2025-2026.

| Tool | Navigation Pattern | Grouping Logic |
|------|--------------------|----------------|
| **Linear** | Sidebar verticale, 4 macro-sezioni | Account / Features / Administration / Teams |
| **Notion** | Sidebar verticale, 2 livelli | Account-level (personale) / Workspace-level (admin) |
| **Vercel** | Sidebar → resizable, collapsibile | Project-level / Team-level / Billing |
| **GitHub** | Sidebar verticale con Primer NavigationList | Section headers per grouping logico |
| **1Password** | Sidebar a tab con sezioni | Sicurezza / Account / Privacy / Integrazioni |
| **Craft (macOS)** | System Preferences native macOS style | Icone grid → sezione |
| **Raycast** | Extension-per-extension sidebar | Per-extension settings via uniform pattern |

**Verdetto 2026**: Sidebar verticale sinistra, **200-280px** di larghezza, **sezioni raggruppate per header separatore**, item attivo con background highlight. Tab orizzontali sono ancora accettabili solo per 3-5 sezioni max (es. profilo utente singola persona).

### 1.2 Struttura Gerarchica Ottimale — Linear (gold standard)

Linear nel dicembre 2024 ha rifatto le settings da zero. La gerarchia risultante è:

```
Settings
├── ACCOUNT (personale, non-admin)
│   ├── Profile
│   ├── Notifications (per channel: desktop / mobile / email / Slack)
│   └── Security
├── FEATURES (workspace, visibile a tutti)
│   ├── Initiatives
│   ├── Customer Requests
│   └── SLAs
├── ADMINISTRATION (solo admin)
│   ├── Workspace general
│   ├── Members (table layout con filter/sort)
│   ├── Billing
│   └── API / Webhooks
└── YOUR TEAMS (per team)
    └── [Team name]
        ├── General
        ├── Cycles
        └── Templates
```

**Takeaway critico**: Linear separa esplicitamente le impostazioni PERSONALI da quelle WORKSPACE (admin). Questo riduce la confusione del non-tecnico che trova cose "non sue" in mezzo alle sue preferenze.

### 1.3 Discoverability — Come l'utente trova in <10 secondi

**Tre strategie reali**, per ordine di adozione 2026:

1. **Grouping semantico con header separatori** (universale, tutti i tool sopra)
   - Separatori visivi con label "ACCOUNT", "CONFIGURAZIONE", "SISTEMA"
   - L'utente scansiona verticalmente le etichette, non legge ogni item

2. **Search box inline** (adottato quando le sezioni superano 8-10)
   - VS Code: `Cmd+,` apre Settings con focus automatico su search box
   - Raycast: ogni estensione ha search integrata — pattern "type to filter"
   - **Threshold reale**: search nelle settings vale la pena sopra le 12-15 sezioni. Sotto quella soglia, il grouping è sufficiente.

3. **Sticky section nav / scroll-spy** (Vercel, GitHub)
   - Mentre si scrolla, la sidebar evidenzia automaticamente la sezione corrente (scroll-spy)
   - Permette di navigare a colpo d'occhio senza un menu separato

**Anti-pattern**: NON usare accordion collassabili come navigation primaria (usabili solo per sezioni con molti sotto-item, mai come struttura principale). Accordion nasconde informazioni e rallenta la discoverability.

---

## 2. SETTINGS PER PMI / NON-TECNICI

### 2.1 Fresha — Approccio Plain Language (Gold Standard PMI)

Fresha è il benchmark per semplicità PMI. Le loro Settings sono strutturate in:

```
Business Setup
├── Business Details
├── Locations
├── Staff & Resources
└── Online Booking

Notifications
├── Client notifications
└── Staff notifications

Payments & Billing
Integrations
```

**Principi UX di Fresha**:
- **Zero terminologia tecnica**: "Business Details" non "Company Configuration". "Client notifications" non "Notification SMTP settings".
- **Setup guide come primo elemento**: nuovo account → checklist visibile in Settings con % progress.
- **Ogni sezione ha un sottotitolo plain**: "Scegli quando vuoi ricevere i tuoi clienti" — non "Configure availability slots".

### 2.2 Terminologia: Plain Language vs Tecnico

Confronto diretto per le 11 sezioni FLUXION:

| Termine Tecnico (attuale FLUXION) | Plain Language (raccomandato) | Note |
|-----------------------------------|-------------------------------|------|
| Email SMTP | Email per le notifiche | "SMTP" è incomprensibile per il 90% dei titolari PMI |
| SDI Fatturazione | Fatturazione elettronica | Il codice "SDI" non dice nulla all'utente |
| Voice Agent Sara | Sara — Receptionist AI | Il brand è più accessibile della categoria tecnica |
| WhatsApp Auto-Responder | Risposte automatiche WhatsApp | Funzione, non sistema |
| WhatsApp QR | Collega WhatsApp Business | Azione, non tecnologia |
| FLUXION IA | Intelligenza artificiale FLUXION | Scritto per esteso |
| Diagnostica | Stato del sistema | Orientato all'utente, non alla funzione |
| Licenza | Il tuo piano FLUXION | Possessivo aumenta il senso di ownership |

**Regola derivata dalla ricerca**: il label di una sezione settings deve rispondere alla domanda implicita "voglio fare COSA?", non "come si chiama tecnicamente QUESTO?".

### 2.3 Badge/Status Indicators — Pattern Comune nel 2026

Il pattern badge di stato (✅ configurato / ⚠️ da configurare) è **consolidato e raccomandato** per PMI non-tecniche. Fonti specifiche:

- **Carbon Design System (IBM)**: status indicator con colori semantici (verde = ok, giallo = warning, rosso = errore) come pattern ufficiale
- **Linear**: sidebar item con dot notification per elementi che richiedono attenzione
- **Onboarding SaaS 2025**: "green tick appears in front of each tab on the left panel if all the information under that tab is completed" — pattern citato in più fonti come standard

**Implementazione raccomandata**:
```
✅ Orari di Lavoro          → verde = configurato
⚠️  Email Notifiche          → giallo = credenziali mancanti
🔴 Sara — Receptionist AI   → rosso = non attivato (chiave API assente)
⚪ Fatturazione elettronica → grigio = opzionale, non configurato
```

I colori **non devono essere l'unico indicatore** (accessibilità): affiancare sempre testo ("Configurato" / "Richiede attenzione" / "Non attivo").

---

## 3. NAVIGATION PATTERN SPECIFICI

### 3.1 Tab + URL Hash su Tauri Desktop

**Fattibilità**: completamente praticabile su Tauri. React Router funziona identicamente al browser in Tauri (WebView). Il pattern hash routing (`/impostazioni#email-notifiche`) è nativo.

**Implementazione concreta per FLUXION**:
```tsx
// React Router v6 — link diretto a sezione settings
<Link to="/impostazioni#email-notifiche">Configura email</Link>

// Nel componente Impostazioni, scroll-to-section su mount
useEffect(() => {
  const hash = window.location.hash.slice(1);
  if (hash) {
    document.getElementById(hash)?.scrollIntoView({ behavior: 'smooth' });
  }
}, []);
```

**Deep link Tauri** (da notifiche o da altri componenti):
```tsx
import { useNavigate } from 'react-router-dom';
// Redirect diretto a sezione specifica da WhatsApp setup wizard
navigate('/impostazioni#whatsapp-business');
```

**Valore pratico**: un banner "Completa configurazione email" in Dashboard può puntare direttamente a `/impostazioni#email-notifiche` — l'utente arriva nella sezione giusta senza dover navigare manualmente.

### 3.2 Search Box nelle Settings — Quando Vale la Pena

**Threshold evidenziata dalla ricerca**: search nelle settings è giustificabile quando:
- Più di **12-15 sezioni** nella sidebar
- **Utenti power user** (dev, admin IT) che conoscono il nome della feature
- Impostazioni con **sotto-pagine numerose** (GitHub: centinaia di opzioni)

**Per FLUXION (11 sezioni)**:
- La search box NON è necessaria ora
- Il grouping semantico in 4 macro-categorie risolve la discoverability
- Search utile in futuro se le sezioni crescono oltre 15

**Alternativa più utile per FLUXION**: un campo di ricerca in command palette globale (`Cmd+K`) che permette di saltare direttamente a una sezione settings ("email", "WhatsApp", "orari") — questo è il pattern Raycast/Linear e offre il vantaggio della search senza ingombrare la UI settings.

### 3.3 Quick Setup Banner — Esempi Reali

**Pattern documentato nei tool B2B più usati**:

**Stripe** (riferimento industry standard):
```
┌─────────────────────────────────────────────────────┐
│ ⚠️  Completa la configurazione per accettare pagamenti │
│    [Aggiungi dati bancari]  [Verifica identità]       │
└─────────────────────────────────────────────────────┘
```

**Intercom / HubSpot**:
- "Setup checklist" con progress bar (3/7 completato) visibile in header
- Ogni checklist item è cliccabile e porta alla sezione corretta delle settings
- Sparisce automaticamente quando setup al 100%

**Implementazione raccomandata per FLUXION** — "Banner Avvio" in Dashboard:
```
┌──────────────────────────────────────────────────────────────┐
│ 🚀 FLUXION non è ancora pronto — 3 passaggi rimasti          │
│                                                              │
│  ✅ Orari di lavoro configurati                               │
│  ⚠️  Email notifiche → [Configura ora]                        │
│  ⚠️  WhatsApp Business → [Collega ora]                        │
│                                  [Salta per ora →]           │
└──────────────────────────────────────────────────────────────┘
```

**AC misurabile**: banner sparisce quando tutti gli item obbligatori hanno status ✅. Click su [Configura ora] naviga a `/impostazioni#[sezione]`.

---

## 4. ANTI-PATTERN DA EVITARE

### 4.1 Scroll Infinito Non Strutturato (il problema attuale di FLUXION)

L'attuale `Impostazioni.tsx` è una singola pagina con `space-y-8` — 11 Card una dopo l'altra in scroll verticale senza navigazione laterale.

**Problemi documentati** dalla ricerca:
1. **Nessun landmark**: l'utente non può tornare a una posizione precedente ("dove era SMTP?")
2. **Cognitive overload visivo**: tutto visibile contemporaneamente, anche ciò che non serve
3. **Zero stato**: non si vede cosa è configurato e cosa no senza leggere ogni sezione
4. **Deep link impossibile**: non esiste modo di arrivare direttamente a una sezione specifica

**Soluzione**: sidebar + main content con `id` per ogni sezione + scroll-spy + status badge.

### 4.2 Over-Engineering (troppa gerarchia)

**Anti-pattern documentato**: creare 3+ livelli di navigazione (Impostazioni → Categoria → Sotto-categoria → Opzione) per meno di 20 sezioni totali.

**Esempio negativo** (evitare):
```
Impostazioni
└── Comunicazione
    └── WhatsApp
        └── Auto-Responder
            └── Messaggi
                └── Testo messaggio
```

**Regola pratica**: per FLUXION con 11 sezioni, **massimo 2 livelli** (sidebar macro-categoria → sezione nel main content). Nessuna sotto-navigazione interna alla sezione.

### 4.3 Terminologia Tecnica Non Tradotta

**Errori specifici in FLUXION** identificati:
- "SMTP" nel titolo della sezione email
- "SDI" nel titolo della sezione fatturazione
- "QR" come label primario (dovrebbe essere "Collega WhatsApp")
- "Diagnostica" (utente non sa cosa aspettarsi)

**Anti-pattern correlato**: mostrare placeholder tecnici in input fields:
```
❌ Server SMTP: [smtp.gmail.com:587]
✅ Server email: [es. smtp.gmail.com]
```

### 4.4 Form senza Feedback Immediato

**Anti-pattern comune**: form settings con bottone "Salva" a fondo pagina, senza auto-save e senza conferma visiva del salvataggio.

**Standard 2026**:
- Auto-save quando possibile (Notion, Linear lo fanno)
- Toast di conferma ("✅ Salvato") quando non è auto-save
- Se si esce con modifiche non salvate → dialog di conferma

---

## 5. GAP ANALYSIS — FLUXION vs FRESHA / MINDBODY

### 5.1 Cosa Fresha Fa Bene (che FLUXION non fa)

| Feature Fresha | Status FLUXION | Gap |
|----------------|----------------|-----|
| Setup progress bar con % | Assente | Alto |
| Status badge per sezione (configurata/no) | Assente | Alto |
| Plain language labels | Parziale (es. "SMTP") | Medio |
| Quick setup banner per credenziali mancanti | Assente | Alto |
| Sidebar navigazione laterale | Assente (flat scroll) | Alto |
| Deep link a sezione specifica | Non implementato | Medio |
| Sezioni collegate al contesto (es. "da qui imposti gli orari che Sara usa") | Assente | Medio |

### 5.2 Cosa Mindbody Fa Male (FLUXION può fare meglio)

| Problema Mindbody | Opportunità FLUXION |
|-------------------|---------------------|
| "Setup takes longer than Fresha if you want it done properly" | Setup wizard in < 5 minuti con banner guidato |
| Complessità non necessaria per PMI piccole | Settings progressive: sezioni avanzate collassate di default |
| Terminologia B2B enterprise non localizzata per PMI | Italiano puro, zero anglicismi tecnici |
| Non ottimizzato per desktop macOS | Dark theme nativo, Cmd+, per aprire settings, native feel |

### 5.3 Cosa Può Fare Solo FLUXION

1. **Status "Sara è attiva / inattiva"** in Settings → la receptionist AI è un differenziatore unico — lo status deve essere immediatamente visibile in settings e in dashboard
2. **Collegamento contestuale tra sezioni**: configurare WhatsApp → banner "Sara usa questo numero per inviare conferme" → link diretto a Voice Agent
3. **Test inline**: in ogni sezione "Avanzata" (SMTP, Voice Agent), un bottone "Testa adesso" che verifica la configurazione senza uscire dalla pagina
4. **Localizzazione profonda**: termini come "Tessera fedeltà", "Festività", "Ricevuta SDI" sono italiani nativi — Fresha e Mindbody li presentano in inglese o in modo generico

---

## 6. PIANO DI REDESIGN IMPOSTAZIONI — RACCOMANDAZIONI CONCRETE

### 6.1 Nuova Struttura Proposta (4 Macro-Gruppi)

```
Impostazioni FLUXION
│
├── 📅 ATTIVITÀ                          [ID: attivita]
│   ├── Orari di lavoro                  [ID: orari]       ✅
│   └── Festività                        [ID: festivita]   ✅
│
├── 💬 COMUNICAZIONE                     [ID: comunicazione]
│   ├── WhatsApp Business                [ID: whatsapp]    ⚠️ / ✅
│   ├── Risposte automatiche WhatsApp    [ID: risposte-wa] ✅
│   └── Email per le notifiche           [ID: email]       ⚠️ / ✅
│
├── 🤖 AUTOMAZIONE                       [ID: automazione]
│   ├── Sara — Receptionist AI           [ID: sara]        🔴 / ✅
│   └── Intelligenza artificiale         [ID: ia]          ✅
│
└── ⚙️ SISTEMA                           [ID: sistema]
    ├── Fatturazione elettronica         [ID: fatturazione] ⚠️ / ✅
    ├── Pacchetti fedeltà                [ID: fedelta]      ✅
    ├── Il tuo piano FLUXION             [ID: licenza]      ✅
    └── Stato del sistema                [ID: diagnostica]  ✅
```

### 6.2 Acceptance Criteria Misurabili

| AC | Metrica | Target |
|----|---------|--------|
| AC-1: Discoverability | Utente trova sezione desiderata | < 10 secondi da apertura settings |
| AC-2: Status visibility | Badge stato visibile per ogni sezione | 100% sezioni hanno badge ✅/⚠️/🔴 |
| AC-3: Plain language | Zero termini tecnici non spiegati | 0 occorrenze "SMTP", "SDI", "QR" come label primari |
| AC-4: Deep link | Link diretto a sezione specifica | URL `/impostazioni#[id]` funziona e scrolla |
| AC-5: Quick setup | Banner configurazione mancante | Visibile in Dashboard se credenziali assenti |
| AC-6: Navigation | Sidebar sempre visibile su scroll | Sidebar sticky, main content scrolla |
| AC-7: Save feedback | Feedback salvataggio visibile | Toast "✅ Salvato" entro 500ms dopo save |

### 6.3 Layout CSS Struttura Raccomandata

```tsx
// Struttura base Impostazioni.tsx refactored
<div className="flex h-full">
  {/* Sidebar: 240px fisso */}
  <aside className="w-60 shrink-0 border-r border-slate-800 overflow-y-auto sticky top-0 h-full">
    <nav>
      <SectionGroup label="ATTIVITÀ">
        <SectionLink id="orari" label="Orari di lavoro" status="ok" />
        <SectionLink id="festivita" label="Festività" status="ok" />
      </SectionGroup>
      <SectionGroup label="COMUNICAZIONE">
        <SectionLink id="whatsapp" label="WhatsApp Business" status="warning" />
        <SectionLink id="risposte-wa" label="Risposte automatiche" status="ok" />
        <SectionLink id="email" label="Email per le notifiche" status="warning" />
      </SectionGroup>
      {/* ... */}
    </nav>
  </aside>

  {/* Main content: scroll verticale */}
  <main className="flex-1 overflow-y-auto p-8 space-y-12">
    <section id="orari">...</section>
    <section id="festivita">...</section>
    {/* ... */}
  </main>
</div>
```

### 6.4 Status Badge Component

```tsx
type SectionStatus = 'ok' | 'warning' | 'error' | 'inactive' | 'optional';

const STATUS_CONFIG: Record<SectionStatus, { icon: string; label: string; color: string }> = {
  ok:       { icon: '✓', label: 'Configurato',      color: 'text-emerald-400' },
  warning:  { icon: '!', label: 'Da configurare',   color: 'text-amber-400' },
  error:    { icon: '✕', label: 'Errore',           color: 'text-red-400' },
  inactive: { icon: '○', label: 'Non attivo',       color: 'text-slate-500' },
  optional: { icon: '·', label: 'Opzionale',        color: 'text-slate-600' },
};
```

---

## 7. FONTI E RIFERIMENTI

### Tool analizzati
- **Linear** settings redesign: https://linear.app/changelog/2024-12-18-personalized-sidebar
- **Vercel** dashboard redesign: https://vercel.com/changelog/new-dashboard-navigation-available
- **GitHub** settings redesign: https://github.blog/changelog/2022-02-02-redesign-of-githubs-settings-pages/
- **Notion** workspace settings: https://www.notion.com/help/workspace-settings

### Pattern documentation
- Sidebar UX 2026: https://www.alfdesigngroup.com/post/improve-your-sidebar-design-for-web-apps
- SaaS layout best practices: https://medium.com/design-bootcamp/designing-a-layout-structure-for-saas-products-best-practices-d370211fb0d1
- B2B SaaS UX 2026: https://www.onething.design/post/b2b-saas-ux-design
- Settings page glossary: https://nicelydone.club/glossary/settings
- Carbon Design System status patterns: https://carbondesignsystem.com/patterns/status-indicator-pattern/
- Tabs vs sidebar UX: https://www.eleken.co/blog-posts/tabs-ux

### Competitor PMI
- Fresha vs Mindbody comparison: https://www.goodcall.com/appointment-scheduling-software/mindbody-vs-fresha
- Fresha alternatives analysis: https://lunacal.ai/compare/fresha-alternative

### Tauri specifics
- Deep linking Tauri v2: https://v2.tauri.app/plugin/deep-linking/
- React Router + Tauri: https://github.com/tauri-apps/tauri/discussions/7899

---

## 8. DECISIONE FINALE — COSA IMPLEMENTARE

### MUST HAVE (P0 — blocca il valore percepito)
1. **Sidebar verticale** con 4 macro-gruppi → risolve il problema dello scroll infinito
2. **Status badge** per ogni sezione → la PMI vede subito cosa manca
3. **Plain language labels** → rimuove barriera cognitiva per non-tecnici
4. **Quick setup banner** in Dashboard → porta l'utente dove serve

### SHOULD HAVE (P1 — migliora esperienza)
5. **Deep link** `/impostazioni#[id]` → il banner in Dashboard può puntare direttamente
6. **Scroll-spy** — sidebar evidenzia la sezione corrente mentre si scrolla
7. **Test inline** per SMTP e Voice Agent — bottone "Verifica connessione"

### NICE TO HAVE (P2 — power user)
8. **Cmd+,** — shortcut globale per aprire Impostazioni (standard macOS)
9. Search box nelle settings — solo se sezioni crescono oltre 15

### NON IMPLEMENTARE (overkill per target)
- Accordion navigation come struttura primaria
- 3+ livelli di gerarchia
- Search settings box nella versione attuale
- Pagine settings separate con routing completo (overhead non giustificato per 11 sezioni)
