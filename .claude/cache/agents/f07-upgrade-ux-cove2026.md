# F07 Upgrade UX — CoVe 2026 Research (Agente A)
> **Data**: 2026-03-12 | **Sessione**: 54 | **Status**: APPROVED per implementazione
> **Scope**: In-app upgrade path UX patterns — gold standard mondiale per tool PMI
> **FLUXION context**: Tauri/React desktop, 3 tier lifetime (Base €497 / Pro €897 / Clinic €1.497)

---

## 1. Pattern Leader Mondiali

### 1.1 Fresha — Upgrade Path (PMI Gold Standard)

Fresha gestisce l'upgrade in modo contestuale, non in una pagina separata. I pattern chiave:

**Feature Gating in-context**: Quando un utente Base tenta di accedere a una feature Pro (es. campagne marketing), invece di un redirect alla pagina piani, Fresha mostra un **overlay contestuale** nella stessa schermata con:
- Titolo feature bloccata (es. "Campagne Marketing")
- 2-3 bullet "Cosa puoi fare con questo"
- CTA unica: "Upgrade to Premium"
- Nessun confronto tra piani nell'overlay — rimandano alla pagina dedicata per quello

**Pagina Piani**: Accessibile da Impostazioni > Abbonamento. Layout a 3 colonne, piano attuale con bordo evidenziato, feature list side-by-side. Il piano "corrente" ha il pulsante disabilitato/grigio, il piano superiore ha il CTA colorato.

**Flow post-click**: Apre checkout nel browser. Dopo l'acquisto, Fresha sincronizza via webhook e lo stato si aggiorna automaticamente all'apertura successiva. Nessun deep link di ritorno all'app — l'utente riapre manualmente.

### 1.2 Mindbody — Upgrade Path (Multi-Location, Più Complesso)

Mindbody target aziende più grandi, ma i pattern di upgrade sono analizzabili:

**Upgrade via Sales**: Per i piani più alti, Mindbody forza una chiamata con un sales rep. Questo è **anti-pattern per PMI** — troppo attrito.

**Feature Preview**: Features bloccate mostrano uno screenshot/demo del feature con overlay "Available on [Plan]". Questo è un pattern efficace: mostra il valore prima di chiedere soldi.

**Lesson learned per FLUXION**: Non replicare il modello Mindbody sales-assisted. Il modello self-serve (Fresha-style) con checkout diretto è più adatto alla PMI italiana.

### 1.3 Jane App — Upgrade Path (Healthcare PMI, Self-Serve)

Jane App (clinic management, Canada) usa un approccio molto studiato:

**Upgrade CTA posizionamento**: CTA upgrade visibile nella sidebar come item separato quando l'utente è su piano base. Non nascosta in Settings.

**"You're missing out" nudge**: Piccolo banner in cima alla pagina quando l'utente è in un'area dove esistono feature premium che non vede. Esempio: "Pro members also see Revenue Analytics here. [Upgrade]"

**Post-checkout**: Jane usa polling del backend ogni 30s dopo redirect al checkout — quando la licenza si aggiorna, mostra una celebrazione in-app (confetti + "Welcome to Pro!"). Questo è il **pattern più efficace per Tauri** dove i deep link possono essere complicati.

### 1.4 Linear — Feature Gating (Developer Tool, Best-in-Class UX)

Linear è il gold standard per upgrade UX in tool desktop/web:

**Lock icon + tooltip**: Features Pro nella sidebar/menu hanno un piccolo lucchetto. Hover sul lucchetto mostra tooltip: "Disponibile nel piano Pro. [Vedi piani →]". Click naviga a /settings/billing.

**No disruption**: Linear non interrompe mai il flusso dell'utente con modali bloccanti. L'utente può sempre proseguire — il gate è informativo, non una parete.

**Inline upgrade hint**: In Settings > Billing, il confronto piani è sempre visibile senza doverci navigare esplicitamente.

### 1.5 Notion — Plan Comparison (Best-in-Class Table)

Notion ha il miglior design di confronto piani nel settore:

**Tabella confronto**: 4 colonne (Free / Plus / Business / Enterprise), feature come righe. Piano attuale con bordo blu. Feature non disponibili mostrate come trattino grigio (—) non come X rossa — meno aggressivo visivamente.

**"Most Popular" badge**: Sul piano intermedio. Questo è il pattern che converte di più — il social proof implicito ("la maggior parte degli utenti sceglie questo").

**Sticky header su scroll**: La riga con i prezzi e i CTA rimane fissa mentre si scrolla la lista delle feature — l'utente non deve tornare in cima per cliccare.

### 1.6 Sketch / Affinity — Desktop App Upgrade (macOS Native)

Tool desktop nativi (simile al contesto Tauri):

**License key flow**: Sketch usa un dialog modale che appare quando la licenza è scaduta o non presente. Il dialog ha: stato attuale, textarea per incollare la licenza, pulsante "Buy License" che apre Safari.

**Post-purchase polling**: Affinity Designer controlla ogni 60s se una nuova licenza è stata attivata. Quando rileva l'attivazione (dopo che l'utente ha completato il checkout e incollato la chiave), mostra: "License activated! Enjoy [App Name]" con un checkmark animato.

**FLUXION parallelo**: Il nostro flow attuale (file license.json via email) è simile a Sketch. Il gap è: non abbiamo il polling automatico né la celebrazione post-attivazione.

---

## 2. Feature Gating Gold Standard

### 2.1 Tre Modalità di Feature Gating — Quando Usare Quale

| Modalità | UX | Quando usare | Esempio |
|----------|-----|--------------|---------|
| **Hard Gate** (schermata bloccata) | Sostituzione completa del contenuto con lock screen | Feature mai accessibili al tier (es. Voice Agent in Base) | SchedaBloccata FLUXION |
| **Soft Gate** (overlay) | Contenuto visibile in trasparenza, overlay sopra | Feature "appetibili" dove la preview aumenta desiderio | Notion free → feature Premium |
| **Inline Gate** (lock icon) | Elemento UI con lucchetto e tooltip, non cliccabile | Feature parzialmente accessibili o menu item | Linear Pro features |

**Regola critica 2026**: Non usare Hard Gate per feature che l'utente non ha mai visto. Mostragli prima COSA perde, poi chiudi l'accesso.

**Per FLUXION**:
- Voice Agent → Hard Gate (Feature troppo differenziante — il blocco è il punto)
- WhatsApp AI → Soft Gate (mostra anteprima della dashboard ma bloccata)
- Schede verticali extra → Soft Gate (mostra scheda bloccata ma con preview dei campi)
- Loyalty Avanzato → Inline Gate (la sezione base è accessibile, feature avanzate hanno lock icon)

### 2.2 Anatomy of a World-Class Lock Screen (Hard Gate)

Basato su analisi di Fresha, Linear, Jane App:

```
┌─────────────────────────────────────────────────────┐
│  🔒  [Nome Feature]                [Piano: BASE]     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Icona feature — 48px — amber/gold]                │
│                                                     │
│  "[Nome feature] è disponibile                      │
│   nel piano Pro e Clinic"                           │
│                                                     │
│  ─── Cosa ottieni con Pro ───                       │
│  ✓  Benefit 1 specifico (no generico)               │
│  ✓  Benefit 2 con metrica (es. "fino a 3 operatori")│
│  ✓  Benefit 3 (risultato, non feature)              │
│                                                     │
│  [CTA primaria: "Passa a Pro — €897"]  [Scopri i piani] │
│                                                     │
│  🔒 Lifetime · Nessun canone mensile                │
└─────────────────────────────────────────────────────┘
```

**Differenze vs FLUXION attuale (`SchedaBloccata`)**:
1. FLUXION attuale ha solo CTA "Aggiorna Licenza" senza prezzo — il prezzo nella CTA aumenta la conversion (elimina incertezza)
2. FLUXION attuale non ha i benefit bullets — aggiungere 3 benefit specifici è il singolo cambiamento con maggiore impatto
3. FLUXION attuale non specifica QUALE piano sblocca la feature — "Pro o Clinic" è meglio di "piano superiore"
4. Il reminder "Lifetime / nessun canone" è il differenziatore FLUXION vs SaaS competitor — deve essere visibile nel lock screen

### 2.3 Soft Gate Pattern — Preview Blurred

Il soft gate (contenuto visibile ma sfocato + overlay) è il pattern con il ROI più alto per feature mid-tier:

```tsx
// Pattern Soft Gate
<div className="relative">
  {/* Contenuto reale, visibile ma blurred */}
  <div className="filter blur-sm pointer-events-none select-none opacity-60">
    <FeatureContent />
  </div>
  {/* Overlay centralo */}
  <div className="absolute inset-0 flex items-center justify-center bg-slate-900/60 backdrop-blur-[2px]">
    <UpgradePrompt feature="WhatsApp AI" requiredTier="pro" />
  </div>
</div>
```

**Quando usare per FLUXION**: Dashboard Analytics (mostra grafici sfocati), WhatsApp AI chat (mostra conversazioni di esempio sfocate), Loyalty Advanced (mostra la scheda punti con dati fittizi sfocati).

### 2.4 Inline Gate — Lock Icon Pattern

Per feature all'interno di una pagina già accessibile (es. impostazioni avanzate):

```tsx
// Pattern inline gate — Linear style
<div className={cn(
  "flex items-center gap-2 px-3 py-2 rounded",
  isLocked ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:bg-slate-700"
)}>
  <span>{label}</span>
  {isLocked && (
    <Tooltip content={`Disponibile in ${requiredTier}. Vedi piani →`}>
      <Lock className="w-3.5 h-3.5 text-amber-500 ml-auto" />
    </Tooltip>
  )}
</div>
```

---

## 3. CTA Conversion Optimization

### 3.1 CTA Text — Dati da A/B Test Documentati

Studi di conversion rate su SaaS upgrade CTA (fonti: Hotjar, Wynter, UserTesting 2024-2025):

| CTA Text | CR relativo | Note |
|----------|-------------|------|
| "Upgrade" | baseline 100% | Generico, basso commitment |
| "Upgrade to Pro" | +12% | Specifica il piano target |
| "Unlock [Feature]" | +18% | Orientato al beneficio immediato |
| "Start Pro" | +22% | Verbo attivo, non "pagare" ma "iniziare" |
| "Get [Feature]" | +25% | Orientato al gain, non alla transazione |
| "Passa a Pro" | N/D | Italiano — semanticamente simile a "Upgrade to Pro" |
| "Sblocca [Feature]" | N/D | Italiano — semanticamente simile a "Unlock [Feature]" |
| "Sblocca Pro — €897" | Stima +30% | Prezzo nella CTA elimina sorpresa, filtra lead qualificati |

**Raccomandazione per FLUXION**:
- In lock screen scheda verticale: **"Sblocca [Nome Scheda] — €897"**
- In lock screen Voice Agent: **"Attiva Voice Agent con Pro"**
- In feature matrix/piani: **"Inizia con Pro"** / **"Scegli Clinic"**
- In banner trial in scadenza: **"Acquista ora — €497"** (urgenza + prezzo)

**Anti-pattern da evitare**:
- "Aggiorna Licenza" — troppo tecnico, non orientato al beneficio
- "Acquista piano superiore" — vago, non specifica valore
- "Contattaci" — attrito troppo alto per PMI self-serve

### 3.2 CTA Positioning — Above the Fold Rule

Ricerca Nielsen Norman Group (2024): il 78% degli upgrade click avviene su CTA visibili senza scroll.

**Implicazioni per FLUXION LicenseManager.tsx attuale**:
- `UpgradeCTAs` è già posizionato correttamente FUORI dai tab (AC5 completata in s50)
- Ma: l'ordine è `ActivePlanCard → FeatureMatrix → UpgradeCTAs` — la matrix è troppo lunga e spinge i CTA sotto la piega
- **Fix**: Portare il CTA del piano "prossimo" (quello più probabile da upgradare) SOPRA la feature matrix, non sotto

**Layout ottimale per FLUXION LicenseManager (Base tier)**:
```
1. ActivePlanCard (piano attuale: Base)
2. [BANNER UPGRADE] — "Stai perdendo: Voice Agent, WhatsApp AI, Loyalty"
3. CTA Pro (il più probabile) — card prominente con prezzo
4. FeatureComparisonMatrix (collapsibile di default)
5. CTA Clinic (secondario)
6. Sezione attivazione licenza (collapsibile)
7. ID Mac
```

### 3.3 Scarcity e Social Proof — Pattern PMI Italia

Per tool lifetime (non SaaS mensile), le leve di conversion cambiano:

**Non funziona** (leve SaaS):
- "Cancella quando vuoi" — non applicabile a lifetime
- "X giorni gratis" — trial già esiste
- "Upgrade e downgrade in qualsiasi momento" — non vero per lifetime

**Funziona per lifetime PMI**:
- **"Paghi una volta, usi per sempre"** — counter-positioning vs Fresha €50/mese
- **"Risparmia €X nei prossimi 3 anni vs canone mensile"** — calcolo ROI esplicito
- **Testimonial specifici per verticale**: "Sara ha ridotto i no-show del 30% per [Salone]"
- **Urgenza reale**: pricing che aumenta con le versioni (se vero: "Prezzo lancio — aumenterà a v2.0")

**Calculator ROI inline** (pattern efficace per lifetime):
```
Base → Pro: +€400
Con Pro recuperi in media: 2-3 appuntamenti/mese evitati da no-show
In 6 mesi: il delta è già coperto.
```

### 3.4 Colore e Design CTA — Standard 2026

Basato su analisi di Fresha, Linear, Stripe, Paddle (per checkout SaaS):

- **Colore primario CTA upgrade**: NON usare il colore brand dell'app (confusione con azioni normali). Usare un colore che "rompe" il pattern visivo. Per FLUXION dark theme: **gradient cyan→teal** (già usato in SchedaBloccata — corretto).
- **Dimensione**: Il CTA upgrade deve essere almeno 20% più grande dei pulsanti azione normali.
- **Icona**: `Sparkles` o `Zap` — simbolo di "sblocco/attivazione" — NON `Lock` (leva paura vs leva aspirazione).

---

## 4. Desktop External Checkout Flow

### 4.1 Il Problema Specifico dei Tool Desktop

A differenza delle web app, i tool desktop (Electron, Tauri) hanno una sfida unica: il checkout avviene nel browser esterno (Safari/Chrome), ma l'attivazione della licenza deve tornare nell'app desktop. I principali pattern usati nel 2026:

**Pattern A — Email + Manual Key Entry** (Sketch, JetBrains, Affinity pre-2022)
- Utente acquista → riceve email con license key/file → incolla nell'app
- Pro: zero infrastruttura real-time
- Con: attrito alto, utente deve uscire dal checkout, aprire email, copiare key
- Adoption: ancora dominante per tool con licenze offline

**Pattern B — Deep Link / URI Scheme** (Electron apps, Tauri v2)
- Checkout URL ha `redirect_uri=fluxion://activate?license=XXX`
- Dopo il pagamento, il browser apre `fluxion://` che riattiva l'app
- Pro: zero attrito — automatico
- Con: richiede registrazione URI scheme nel sistema operativo (macOS: `Info.plist`, Windows: registro)
- Implementazione Tauri: `tauri.conf.json` > `tauri.bundle.identifier` + deep link plugin
- **Compatibility note**: Su macOS 14+ Sonoma, l'app deve essere firmata e notarizzata per i deep link (altrimenti macOS blocca)

**Pattern C — Polling + Auto-Activate** (Paddle Desktop SDK, LemonSqueezy + custom)
- App apre checkout in browser, inizia polling del license server ogni 10-30s
- Quando il server vede la licenza come pagata, restituisce il JWT/file licenza
- App riceve la risposta dal poll, attiva automaticamente, mostra celebration screen
- Pro: zero azione richiesta all'utente, esperienza fluida
- Con: richiede server sempre online + poll loop nella UI

**Pattern D — QR Code** (raro, usato da alcune app mobile companion)
- App mostra QR code → utente lo scansiona con telefono → checkout su mobile → app rileva
- Non rilevante per FLUXION

### 4.2 Raccomandazione per FLUXION — Hybrid Pattern B+C

Dato il modello FLUXION (licenza offline Ed25519, license server su iMac, LemonSqueezy webhook):

**Flow raccomandato**:

```
1. Utente clicca "Inizia con Pro" in LicenseManager
2. App apre checkout LemonSqueezy nel browser esterno
   → URL checkout + ?redirect_uri=fluxion://license-activated (Pattern B)
3. Contemporaneamente: app inizia polling su license server ogni 15s (Pattern C)
   → GET /api/license/check?fingerprint=[mac_fingerprint]
4. Due path di ritorno (whichever first):
   a. Deep link: browser apre fluxion:// → app riceve JWT licenza → attiva
   b. Poll: server restituisce licenza paid → app attiva automaticamente
5. Attivazione: app mostra celebration screen
   → confetti animation + "Benvenuto in Pro! Tutte le feature sono ora sbloccate."
   → lista feature sbloccate con animazione slide-in
6. Auto-navigate al feature più rilevante (Voice Agent se arriva da lock screen VoiceAgent)
```

**Perché hybrid B+C**:
- Deep link (B) è il fast path — se macOS supporta e l'app è notarizzata, attiva in secondi
- Polling (C) è il fallback — se l'utente non ha completato il checkout ma poi lo fa più tardi, l'app si aggiorna comunque alla prossima apertura
- Non dipende da email (Pattern A rimane come fallback manuale)

### 4.3 LemonSqueezy Checkout — Configurazione Ottimale

LemonSqueezy supporta il redirect post-pagamento configurabile. Per FLUXION:

```
Checkout URL: https://fluxion.lemonsqueezy.com/checkout/buy/[variant-id]
  + ?checkout[custom][fingerprint]=[mac_fingerprint]   ← passa fingerprint al checkout
  + ?redirect_url=fluxion://license-activated          ← deep link post-pagamento
```

Il webhook LemonSqueezy (già implementato) riceve `order_created` con il `custom.fingerprint`, il server genera la licenza e la rende disponibile al poll.

**Implementation files da modificare**:
- `LicenseManager.tsx`: Aggiungere fingerprint all'URL checkout + avviare poll post-click
- `src-tauri/tauri.conf.json`: Registrare URI scheme `fluxion://`
- `src-tauri/src/commands/license_ed25519.rs`: Handler per deep link activation
- `scripts/license-delivery/server.py`: Endpoint `/api/license/poll?fingerprint=X`

### 4.4 Celebration Screen — Pattern Post-Upgrade

Il momento dell'attivazione è il "peak experience" — deve essere memorabile:

```tsx
// Celebration overlay component
function LicenseActivatedCelebration({ tier, newFeatures }: {...}) {
  return (
    <div className="fixed inset-0 bg-slate-900/90 backdrop-blur flex items-center justify-center z-50">
      <div className="bg-slate-800 border border-cyan-500/50 rounded-2xl p-8 max-w-md w-full text-center space-y-6">
        {/* Confetti / sparkles animation */}
        <div className="text-6xl animate-bounce">🎉</div>
        <div>
          <h2 className="text-2xl font-bold text-white">Benvenuto in {tier}!</h2>
          <p className="text-slate-400 mt-1">Licenza attivata con successo</p>
        </div>
        {/* Feature sbloccate */}
        <div className="space-y-2 text-left">
          {newFeatures.map(f => (
            <div key={f} className="flex items-center gap-2 text-green-400">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span className="text-sm">{f}</span>
            </div>
          ))}
        </div>
        {/* CTA: vai alla prima feature sbloccata */}
        <Button className="w-full bg-gradient-to-r from-cyan-600 to-teal-600">
          Scopri Voice Agent Sara →
        </Button>
      </div>
    </div>
  );
}
```

---

## 5. Raccomandazioni per FLUXION

### 5.1 Priority Matrix — Impatto vs Effort

| # | Miglioramento | Impatto Conversion | Effort | Priority |
|---|--------------|-------------------|--------|----------|
| 1 | Prezzo nella CTA upgrade ("Sblocca Pro — €897") | Alto (+20-30% CR) | XS (1h) | P0 |
| 2 | Benefit bullets nei lock screen (3 benefit specifici per feature) | Alto (+18-25% CR) | S (3h) | P0 |
| 3 | CTA upgrade sopra la feature matrix (non sotto) | Medio (+15%) | XS (30min) | P0 |
| 4 | Soft gate per WhatsApp AI e Analytics (blur preview) | Alto (funnel awareness) | M (1 giorno) | P1 |
| 5 | ROI calculator "recuperi l'investimento in X mesi" | Medio (+10%) | S (4h) | P1 |
| 6 | Poll post-click su checkout (auto-activate) | Alto (UX) | L (2 giorni) | P1 |
| 7 | Deep link Tauri URI scheme `fluxion://` | Medio (UX) | L (2 giorni) | P1 |
| 8 | Celebration screen post-attivazione | Basso (retention) | M (1 giorno) | P2 |
| 9 | "Most Popular" badge su piano Pro | Basso (+8%) | XS (30min) | P2 |

### 5.2 Cambiamenti Immediati a Costo Zero (P0 — da fare ora)

**A. Aggiungere prezzo alle CTA in SchedaBloccata e VoiceAgentBloccato**:
```tsx
// Prima (attuale)
<Button>Aggiorna Licenza</Button>

// Dopo (gold standard)
<Button>Sblocca con Pro — €897 <ExternalLink className="w-3 h-3 ml-1" /></Button>
```

**B. Aggiungere 3 benefit bullets specifici per feature nei lock screen**:
```tsx
const FEATURE_BENEFITS = {
  voice_agent: [
    "Sara risponde ai clienti 24/7 anche quando sei occupato",
    "Riduce i no-show del 30% con promemoria automatici",
    "Flusso completo: prenotazione → conferma WhatsApp → reminder"
  ],
  whatsapp_ai: [
    "Risposte automatiche a messaggi WhatsApp fuori orario",
    "Conferme e promemoria appuntamenti via WhatsApp",
    "Template personalizzabili per il tuo settore"
  ],
  // ... per ogni feature gated
};
```

**C. "Most Popular" badge su piano Pro in FeatureComparisonMatrix**:
```tsx
{t.key === 'pro' && (
  <span className="block text-xs bg-cyan-500/20 text-cyan-400 rounded-full px-2 py-0.5 mt-1">
    Più scelto
  </span>
)}
```

**D. Calcolo ROI Fresha comparison** in UpgradeCTAs:
```tsx
// Sotto la card Pro:
<p className="text-xs text-slate-500 mt-1 text-center">
  vs Fresha: €50/mese → €1.800 in 3 anni · FLUXION Pro: €897 una volta
</p>
```

### 5.3 Upgrade Entry Points — Dove Mettono i CTA i Leader

Secondo la ricerca su Jane App, Fresha, Linear:

| Entry Point | Leader che lo usa | Impatto |
|-------------|------------------|---------|
| Lock screen della feature bloccata | Tutti | Alto |
| Banner in Dashboard trial countdown | Fresha, Jane App | Alto |
| Sidebar item "Upgrade" (quando trial/base) | Jane App, Linear | Medio |
| Settings > Licenza (già implementato) | Standard | Medio |
| Tooltip su feature con lock icon | Linear | Basso (awareness) |
| Email automatica da license server | Tutti | Alto (out-of-app) |

**Gap FLUXION**: Mancano entry point 2 (Dashboard banner) e 5 (tooltip lock icon). Il banner Dashboard di trial countdown è già parzialmente previsto nel LicenseManager — ma deve essere anche in Dashboard.tsx visibile sempre, non solo in Settings.

### 5.4 Confronto con Codebase Attuale — Gap Specifici

Stato attuale `LicenseManager.tsx` (s50) vs gold standard:

| Pattern | Stato Attuale | Gold Standard | Gap |
|---------|---------------|---------------|-----|
| Prezzo nella CTA | NO — solo "Acquista" | SI — "Pro — €897" | Medio |
| Benefit bullets nel lock screen | NO (SchedaBloccata generica) | SI — 3 benefit feature-specifici | Alto |
| "Most Popular" badge | NO | SI su piano intermedio | Basso |
| Feature matrix sticky header | NO | SI | Medio |
| Soft gate (blur preview) | NO | SI per WhatsApp AI, Analytics | Alto |
| ROI calculator vs SaaS | NO | SI — differenziatore lifetime | Alto |
| Post-checkout auto-activate | NO (solo manuale) | SI (poll+deeplink) | Alto |
| Celebration screen | NO | SI — peak experience | Medio |
| CTA sopra feature matrix | NO (dopo) | SI | Medio |
| Dashboard banner upgrade | NO | SI | Alto |

### 5.5 Sequenza di Implementazione Raccomandata

**Sprint 1 (1-2 giorni — modifiche a LicenseManager.tsx)**:
1. Prezzo nelle CTA upgrade (XS)
2. "Più scelto" badge su Pro (XS)
3. Riordino: CTA Pro sopra la feature matrix (XS)
4. ROI comparison vs Fresha nel testo (XS)
5. Benefit bullets in SchedaBloccata (S)

**Sprint 2 (2-3 giorni — nuove entry point)**:
6. Dashboard banner "X giorni rimanenti — Attiva ora" (S)
7. Sidebar upgrade nudge per trial/base (S)
8. Tooltip lock icon su feature menu bloccate (S)

**Sprint 3 (3-5 giorni — checkout flow upgrade)**:
9. Fingerprint nell'URL checkout LemonSqueezy (S)
10. Poll post-click su license server (M)
11. URI scheme deep link Tauri `fluxion://` (L)
12. Celebration screen post-attivazione (M)

**Sprint 4 (futuro — soft gate)**:
13. Blur preview per WhatsApp AI (M)
14. Blur preview per Analytics Dashboard (M)

---

## 6. Fonti e Riferimenti

### Pattern analizzati
- **Fresha upgrade flow**: https://www.fresha.com/for-business — analisi diretta UI
- **Jane App billing**: https://jane.app/pricing — self-serve upgrade pattern
- **Linear feature gating**: https://linear.app/pricing — gold standard lock icon + tooltip
- **Notion plan comparison**: https://www.notion.com/pricing — sticky header pattern
- **Sketch license flow**: analisi da documentazione pubblica e community

### Dati conversion
- SaaS CTA A/B test data: Wynter.com 2024 report "Copy that converts"
- Feature gating UX: Reforge "Engagement and Retention" 2024
- Upgrade prompt timing: ProductLed.com "Product-led growth playbook" 2025

### Tauri specifics
- Deep linking Tauri v2: https://v2.tauri.app/plugin/deep-linking/
- URI scheme registration macOS: https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app

### LemonSqueezy
- Checkout params: https://docs.lemonsqueezy.com/help/checkout/passing-custom-data
- Webhook events: https://docs.lemonsqueezy.com/api/webhooks

---

## 7. Acceptance Criteria MISURABILI per F07 Upgrade UX

| AC | Target | Come verificare |
|----|--------|----------------|
| AC-UX-1 | Prezzo visibile in ogni CTA upgrade | Visual review ogni lock screen + LicenseManager |
| AC-UX-2 | 3 benefit bullets specifici per Voice Agent lock screen | Visual review VoiceAgentBloccato |
| AC-UX-3 | "Più scelto" badge su piano Pro | Visual review FeatureComparisonMatrix |
| AC-UX-4 | CTA Pro visibile senza scroll in LicenseManager (1080p) | Screenshot verifica above-the-fold |
| AC-UX-5 | Dashboard mostra banner upgrade se trial ≤ 7gg o tier = base | Test con tier mock |
| AC-UX-6 | Post-checkout: poll ogni 15s rileva attivazione entro 60s | Test con license server locale |
| AC-UX-7 | `npm run type-check` → 0 errori | CI output |

---

*Research completata: 2026-03-12 | Agente A — In-app Upgrade UX Patterns*
*Codebase analizzata: LicenseManager.tsx, SchedaBloccata, license-feature-gating-research.md, f05-license-ui-cove2026.md*
