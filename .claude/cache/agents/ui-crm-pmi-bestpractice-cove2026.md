# UI/UX Best Practices per Gestionali/CRM PMI 2026 — Deep Research CoVe 2026

**Data**: 2026-03-22
**Scope**: Benchmark 10 leader mondiali + trend 2025-2026 + gap analysis FLUXION + ricettario Tailwind/shadcn
**Obiettivo**: Portare FLUXION al gold standard mondiale UI/UX per gestionali PMI

---

## 1. BENCHMARK LEADER MONDIALI 2026

### 1.1 FRESHA (Beauty/Salon Management)

**Layout pattern**: Split-view predominante. Sidebar sinistra con navigazione icone + testo. Content area con card-based layout. Calendar view a griglia settimanale/giornaliera con drag-and-drop.

**Color strategy**:
- Primario: Blu (#4A90D9) con accent teal per CTA
- Background: Bianco puro (#FFFFFF) in light mode, quasi-nero (#1A1A2E) in dark
- Semantica: Verde per confermato, Giallo per in attesa, Rosso per cancellato, Grigio per no-show
- Ogni servizio ha un color dot nel calendario (fino a 12 colori distinti)

**White space / spacing**:
- Spacing system 8px base. Padding card: 20px-24px. Gap tra card: 16px
- Ampio respiro tra sezioni — non comprimono mai i dati
- Header delle pagine: 40px padding-top, 24px margin-bottom

**Typography**:
- Font: Inter (identico a FLUXION). Scale: 12/14/16/20/28/36
- Heading: 700 weight, body: 400, labels: 500
- Line height: 1.4 per body, 1.2 per heading

**Micro-animations**:
- Hover card: `transform: translateY(-2px)` con `box-shadow` increase, 200ms ease-out
- Tab switch: content fade-in 150ms
- Calendar drag: ghost element con opacity 0.7 + snap grid
- Button press: scale(0.98) 100ms
- Toast: slide-in da destra 300ms cubic-bezier

**Card design**:
- Border radius: 12px (rounded-xl)
- Shadow: `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)` (light)
- Shadow dark: `0 2px 8px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05)`
- Border: 1px solid con opacity 10-15%
- Padding interno: 20px

**Data density**: Media. Card grandi per KPI, tabelle compatte per liste clienti. Il profilo cliente e' la pagina piu' ricca: "Beauty Profile" con foto prima/dopo, storico trattamenti, preferenze.

**Empty states**: Illustrazione vettoriale custom + heading + CTA primaria. "Nessun appuntamento oggi — Inizia a prenotare!" con bottone blu.

**Client card pattern (Beauty Profile)**:
- Header: Avatar circolare grande (80px) + nome + badge VIP + data ultimo appuntamento
- Stats row: Visite totali | Spesa totale | Ultimo servizio | Prossimo appuntamento
- Tabs: Profilo | Storico | Prodotti | Note | Foto
- Sezione allergie/note importanti con banner rosso in alto

---

### 1.2 MINDBODY (Fitness/Wellness)

**Layout pattern**: Dashboard card grid con metriche primarie in alto (4 colonne). Below-the-fold: grafici a barre + lista prossime lezioni. Navigation sidebar scura con gruppi logici.

**Color strategy**:
- Brand: Deep blue (#1B2A4A) + accent arancione (#FF6B35)
- Cards: Background bianco con bordo grigio sottile
- Charts: Palette a 6 colori pastello distinguibili (WCAG AA)
- Status: Verde check-in, Blu prenotato, Grigio lista attesa, Rosso cancellato

**White space / spacing**:
- Grid 12 colonne. Card gap: 24px. Internal padding: 24px
- Sezioni verticali separate da 32px
- Nessun divider visibile tra sezioni — solo spacing

**Typography**:
- Font: Helvetica Neue / SF Pro (sistema). Scale ridotta: 11/13/15/18/24/32
- Uso pesante di CAPS per label categorie (11px, letter-spacing 0.5px, font-weight 600)
- Numeri KPI: 36px bold, monospace per allineamento

**Micro-animations**:
- Card hover: border-color transition 200ms (da trasparente a accent)
- Grafico: data points animati in sequenza (stagger 50ms)
- Toggle: slide 200ms con spring easing
- Modal: scale(0.95) + opacity 0 → scale(1) + opacity 1, 250ms

**Card design**:
- Border radius: 8px (rounded-lg) — piu' conservative di Fresha
- Shadow: Minimal, `0 1px 2px rgba(0,0,0,0.05)`
- Border: 1px solid #E5E7EB (gray-200)
- Header card con background gradient leggero (accent/5%)

**Data density**: ALTA. Tabelle dense con 8+ colonne. Compact mode per classi/orari. I dati finanziari sono sempre visibili senza hover.

**Empty states**: Semplici — icona outline + testo + link. Meno elaborate di Fresha.

**Client card pattern**:
- Header compatto: Avatar + Nome + Membership type badge
- Quick stats: Visits this month | Revenue | Last visit | Membership status
- Tabbed: Visits | Purchases | Contracts | Notes
- Sezione "Engagement Score" con barra progresso 0-100

---

### 1.3 JANE APP (Healthcare/Clinic Management)

**Layout pattern**: Clean split-view. Left: patient list (scrollable). Right: patient detail. Top nav tabs per sezioni. Layout piu' denso e informativo di Fresha/Mindbody perche' i dati clinici richiedono completezza.

**Color strategy**:
- Primario: Teal (#2DB4AE) — calmo, professionale, healthcare
- Background: Bianco (#FFFFFF) con aree grigio molto chiaro (#F7F8FA)
- Accento: Coral (#FF6B6B) per alert medici
- Badge di stato: Verde (attivo), Giallo (in attesa), Grigio (archiviato)
- Banner allergie: Rosso pieno con testo bianco — MASSIMA visibilita'

**White space / spacing**:
- Spacing generoso: 24px gap base, 32px tra sezioni maggiori
- Form fields: 16px gap verticale, label-to-input 4px
- Card interne con 20px padding

**Typography**:
- Font: System stack (SF Pro, Segoe UI). Scale: 12/14/16/20/24
- Patient name: 20px semibold. Section headers: 14px uppercase 600
- Clinical notes: 14px regular, line-height 1.6 per leggibilita'

**Micro-animations**:
- Minimal. Healthcare UI predilige stabilita' e prevedibilita'
- Tab switch: underline slide 200ms
- Panel expand/collapse: height transition 250ms ease
- Focus: Teal glow ring 2px offset

**Card design (Patient Record)**:
- Border radius: 8px
- Shadow: Quasi assente — usa bordi e background per separazione
- Sezioni con header bold + divider 1px
- "Alert Banner" in cima: rosso per allergie, giallo per note importanti

**Data density**: MOLTO ALTA. Dati clinici richiedono completezza. Multi-colonna per diagnosi, trattamenti, prescrizioni. Timeline verticale per visite.

**Empty states**: Testo + icona minimal. "No appointments scheduled."

**Patient card pattern**:
- **PASSPORT HEADER**: Avatar + Nome + DOB + ID paziente + Insurance
- **Alert ribbon**: Allergie + condizioni critiche (rosso, sticky)
- **Quick actions**: Nuovo appuntamento | Nuova fattura | Prescrizione
- **Tabs**: Chart | Appointments | Billing | Insurance | Documents | Notes
- **Timeline view**: Visite in ordine cronologico inverso con diagnosi/procedure
- **Sezione SOAP notes**: strutturata (Subjective, Objective, Assessment, Plan)

---

### 1.4 NOTION

**Layout pattern**: Bento-box/block-based. Ogni pagina e' un canvas di blocchi. Sidebar gerarchica ad albero. Content area a larghezza variabile (680px default, full-width opzionale).

**Color strategy**:
- Minimale: Quasi monocromatico. Nero/bianco con pochissimi accent
- Background: #FFFFFF (light), #191919 (dark)
- Accent colors: 10 colori predefiniti per tag/highlight, tutti desaturati
- Inline colori: light yellow highlight, light blue, light green, etc.

**White space / spacing**:
- MASSIMO white space. Content width 680px centrato (come Medium/blog)
- Block spacing: 4px tra blocchi dello stesso tipo, 16px per heading
- Page padding: 96px top, 72px sides
- Empty space e' una FEATURE, non uno spreco

**Typography**:
- Font: Inter o serif opzionale (Noto Serif). Scale: 14/16/20/24/30
- Heading 1: 30px bold. Heading 2: 24px semibold. Heading 3: 20px semibold
- Body: 16px, line-height 1.5
- Code: JetBrains Mono, 14px, bg highlight

**Micro-animations**:
- Hover blocco: barra grigia a sinistra (drag handle) 100ms fade
- Drag: ghost block 60% opacity, slot indicator linea blu
- Toggle expand: smooth height 200ms
- Sidebar: width transition 200ms, items fade stagger
- Page transition: crossfade 150ms

**Card design (Database views)**:
- Border radius: 3-4px (MOLTO basso — quasi sharp)
- Shadow: Nessuno (usa bordi sottili)
- Padding: 8-12px (compatto)
- Gallery view cards: 8px radius, shadow on hover only

**Data density**: VARIABILE. L'utente controlla il livello. Table view = denso. Board view = sparse. Gallery = visuale.

---

### 1.5 LINEAR

**Layout pattern**: Three-pane. Sidebar (nav) + List (issues) + Detail (right panel). Tutto interconnesso. Keyboard-first design.

**Color strategy**:
- Dark mode default. Background: #0A0A0B (quasi-nero puro)
- Surface: #16161A (leggermente piu' chiaro del bg)
- Border: #27272A (zinc-800 equivalent)
- Text: #FAFAFA (primary), #71717A (secondary/muted)
- Accent: Viola (#7C3AED) per brand, multi-color per label/priority
- Priority colors: Urgent=rosso, High=arancio, Medium=giallo, Low=grigio
- Status: Backlog=grigio, Todo=bianco, In Progress=giallo, Done=viola, Cancelled=rosso

**White space / spacing**:
- Spacing 4px grid rigoroso. Gap minimo 4px, massimo 24px
- List items: 8px padding verticale, 12px orizzontale
- Content area padding: 24px
- MOLTO compatto ma leggibile grazie alla tipografia

**Typography**:
- Font: Inter. Scale ridotta: 12/13/14/16/20
- MASSIMO uso di font-weight per gerarchia (400 vs 500 vs 600)
- Letter spacing negativo per heading (-0.02em)
- Monospace per ID/codici

**Micro-animations** (IL GOLD STANDARD):
- **Hover list item**: background rgba(255,255,255,0.04) 100ms
- **Status change**: icon morphing con spring animation (framer-motion)
- **Command palette**: backdrop-blur + scale-in 200ms spring
- **Priority dot**: Color pulse on change
- **Drag reorder**: Smooth reorder con layout animation
- **Panel slide**: Transform translateX 200ms ease-out
- **Focus ring**: Box-shadow glow 2px accent color
- **Toast**: Slide-up + fade 300ms, auto-dismiss con progress bar
- **Keyboard shortcut hints**: Fade-in 200ms on hover con delay 500ms

**Card design**:
- Border radius: 6px (tra sharp e rounded)
- Shadow: Nessuno in dark mode. Usa bordi 1px zinc-800
- Hover: background shift + border color shift
- Selected: border-accent + background accent/5%

**Data density**: ALTA ma elegante. Ogni pixel ha uno scopo. Niente decorazione inutile.

**Empty states**: Minimali. Icona outline + testo breve. Tono: "No issues match this filter."

---

### 1.6 HUBSPOT CRM

**Layout pattern**: Master-detail. Lista contatti a sinistra, profilo dettagliato a destra. Dashboard con card grid (2x3 o 3x3). Navigation top bar + sidebar contestuale.

**Color strategy**:
- Brand: Arancione (#FF7A59) — energico, vendite
- Background: Bianco. Surface: Grigio chiaro (#F5F8FA)
- Card borders: Grigio tenue (#CBD6E2)
- Semantic: Verde=won, Rosso=lost, Blu=in progress, Grigio=inactive
- Deal pipeline: Colori per stage (pastello) + intensita' per valore

**White space / spacing**:
- Generoso. Card padding: 24px. Gap: 16px. Page margin: 32px
- Sidebar width: 280px. Content max-width: 1200px

**Typography**:
- Font: Lexend Deca (custom) / Helvetica fallback. Scale: 12/14/16/20/24/32
- Contact name: 24px bold. Section labels: 12px uppercase semibold
- Revenue numbers: 32px bold con font-variant-numeric: tabular-nums

**Micro-animations**:
- Card hover: shadow elevation increase 200ms
- Deal drag: spring animation con snap
- Sidebar toggle: width transition 250ms
- Modal: Scale + fade 200ms

**Card design**:
- Border radius: 8px
- Shadow: Multi-layer `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)`
- White background con border grigio
- Header con gradient accent leggero

**Contact card pattern**:
- Avatar (48px) + Nome + Company + Title
- Quick stats row: Deals | Revenue | Last activity | Lead score
- Activity timeline (feed-style, vertical)
- Properties panel (label-value pairs, editable inline)
- Associated records (deals, tickets, notes)

---

### 1.7 MONDAY.COM

**Layout pattern**: Board-based. Ogni "board" e' una tabella colorata con gruppi collassabili. Status columns con colori vivaci. Dashboard con widget grid drag-and-drop.

**Color strategy**:
- **MASSIMO USO DI COLORE** — ogni status ha un colore vivace
- 40+ colori predefiniti per label, tutti con buon contrasto
- Background: Bianco. Surface cards: Bianco con bordo colorato a sinistra (4px accent bar)
- Dark mode: Background #181B34, surface #30324E
- Color coding e' la FEATURE principale — distinzione visiva immediata

**White space / spacing**:
- Tabelle: Compatte. Row height 40px. Column padding 12px
- Dashboard widget gap: 16px
- Board header: 56px height con titolo + filtri

**Typography**:
- Font: Figtree (custom sans). Scale: 13/14/16/20/24
- Numeri in bold mono per allineamento colonne
- Group names: 16px bold con colore accent

**Micro-animations**:
- **Status change**: color pill flip/morph 200ms
- **Group collapse**: smooth height 300ms con stagger children
- **Drag column**: shadow elevation + scale 1.02
- **Notification badge**: bounce 300ms spring
- **Pulse (row) hover**: background highlight 100ms

**Card design (Dashboard widgets)**:
- Border radius: 8px
- Shadow: `0 4px 12px rgba(0,0,0,0.08)` — piu' pronunciato
- White bg + colored header strip (4px)
- Chart widgets: padding 20px, titolo sopra

---

### 1.8 STRIPE DASHBOARD

**Layout pattern**: Single-column centered con sidebar navigation. Max-width 1000px content. Card-based sections stacked vertically. Metriche in alto, dettagli sotto.

**Color strategy**:
- Brand: Viola (#635BFF) + gradients sottili
- Background: #F7F7F8 (light), #0A2540 (dark promo)
- Card: Bianco puro
- Chart colors: Palette 4 colori con buona separazione (viola, blu, verde, grigio)
- Status: Verde=succeeded, Giallo=pending, Rosso=failed, Grigio=refunded
- Semantic badges con background pastello + testo scuro

**White space / spacing**:
- Molto generoso. Page padding: 40px. Card gap: 24px
- Card internal padding: 24px-32px
- Metriche KPI: 20px gap tra i numeri

**Typography**:
- Font: -apple-system / Inter. Scale: 13/14/16/20/28/36
- Revenue: 36px bold (ENORME per impatto)
- Label: 13px regular grigio. Value: 14px medium nero
- Monospace: per importi, ID, codici

**Micro-animations**:
- **Chart tooltip**: fade-in 150ms con linea guida verticale
- **Card hover**: Nessuno (Stripe e' conservativo sulle animazioni)
- **Tab underline**: slide 200ms
- **Number counter**: count-up animation su caricamento (500ms)
- **Skeleton loading**: Shimmer gradient animation

**Card design (IL GOLD STANDARD per metriche)**:
- Border radius: 12px
- Shadow: `0 2px 5px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04)`
- Internal dividers: 1px #E3E8EF
- KPI card: titolo 13px grigio + valore 28px bold + trend arrow (verde/rosso)

**Metrics card pattern**:
```
┌────────────────────────────────┐
│  Gross volume          ↗ +12% │
│  €47,291.00                    │
│  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ (sparkline) │
└────────────────────────────────┘
```

---

### 1.9 SHOPIFY ADMIN

**Layout pattern**: Sidebar sinistra + content centrato (max-width 960px). Card stacked verticalmente. Page actions in header. Mobile-first responsive.

**Color strategy**:
- Brand: Verde (#008060)
- Background: #F1F1F1 (grigio caldo)
- Card: Bianco
- Accent: Verde per primario, Blu per link, Rosso per destructive
- Badge: Pastello con testo scuro (fulfilled=verde, pending=giallo, cancelled=rosso)

**White space / spacing**:
- 20px card padding. 16px gap tra card. 20px page padding
- Section spacing 32px
- Compact density opzionale per merchant con molti prodotti

**Typography**:
- Font: -apple-system / Inter. Scale: 12/13/14/16/20/24
- Page title: 20px bold. Card title: 16px semibold
- Shopify Polaris design system (open source, ottimo reference)

**Micro-animations**:
- **Page transition**: fade 150ms
- **Toast**: slide-up + auto-dismiss con progress
- **Drag reorder**: smooth layout animation
- **Collapsible section**: height + opacity 200ms
- **Loading skeleton**: pulse opacity animation

**Card design (Polaris)**:
- Border radius: 12px
- Shadow: `0 1px 1px rgba(0,0,0,0.1)` — MOLTO sottile
- Dividers interni: 1px #E1E3E5
- Header con padding 20px, body con padding 20px
- Subsection: padding-left 20px + border-left 3px accent

---

### 1.10 FIGMA

**Layout pattern**: Tool panels a sinistra e destra. Canvas centrale. Floating panels. Tab system per file aperti.

**Color strategy**:
- Dark UI: Background #2C2C2C, surface #383838
- Accent: Blu Figma (#0D99FF)
- Light text: #FFFFFF, secondary: #B3B3B3
- Layer colori: Background → surface → elevated surface (3 livelli)

**White space / spacing**:
- COMPATTISSIMO. Panel padding: 8px. Item gap: 4px
- Spacing funzionale — ogni pixel conta per mostrare proprieta'

**Typography**:
- Font: Inter. Scale RIDOTTA: 11/12/13/14
- Tutto piccolo ma leggibile grazie al contrasto
- Weight: 400 (regular) e 600 (semibold) solo

**Micro-animations**:
- **Panel resize**: real-time transform
- **Color picker**: smooth gradient follow
- **Tooltip**: 200ms delay + fade 100ms
- **Menu**: scale-in from anchor point 150ms

**Dark theme (reference per FLUXION)**:
- Background: #1E1E1E → #2C2C2C → #383838 (3 livelli)
- Border: #444444 (rgba 255,255,255,0.1)
- Hover: rgba(255,255,255,0.06)
- Active/selected: rgba(24,160,251,0.2) + border accent
- Text: #FFFFFF → #B3B3B3 → #6B6B6B (3 livelli)

---

## 2. TREND UI 2025-2026

### 2.1 Glassmorphism vs Neubrutalism vs Soft UI

**VINCITORE 2026: Glassmorphism controllato ("Glassware")**

Il trend dominante nel 2026 e' il "Glassware" — glassmorphism usato in modo SELETTIVO:
- Header e toolbar: `backdrop-blur-xl bg-white/5 border border-white/10`
- Card principali: SOLIDE (no blur) per leggibilita'
- Overlay/modal: glass effect per profondita'
- Floating elements: glass per separazione dal background

**NON usare glass per**: Card con molto testo, tabelle dati, form input. Riduce la leggibilita'.

**Neubrutalism**: Morto nel 2026 per software business. Troppo giocoso per gestionali PMI.

**Soft UI (Neumorphism)**: Morto. Problemi di accessibilita' (contrasto insufficiente) e performance (ombre multiple).

**Raccomandazione FLUXION**: Glass SOLO per:
1. Header principale e SchedaWrapper header (gia' implementato)
2. Tooltip e popover
3. Command palette (se implementata)
4. Sidebar hover states
5. StatChip (gia' implementato con `bg-white/5`)

### 2.2 Bento Box Layout (Apple-Inspired)

Il layout "Bento Box" e' il trend dominante per dashboard 2025-2026.

**Principi**:
- Grid asimmetrico: Non tutte le card sono uguali. Mix di 1x1, 2x1, 1x2
- "Hero card" grande (span 2 colonne) per metrica principale
- Card secondarie piu' piccole intorno
- Gap consistente (16px) tra tutte le card
- Rounded corners generosi (16-20px)
- Ogni card ha uno scopo chiaro e autonomo

**Implementazione CSS Grid**:
```css
/* Bento box grid */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: minmax(120px, auto);
  gap: 16px;
}
.bento-hero { grid-column: span 2; grid-row: span 2; }
.bento-wide { grid-column: span 2; }
.bento-tall { grid-row: span 2; }
```

**Tailwind equivalente**:
```
grid grid-cols-4 gap-4 auto-rows-[minmax(120px,auto)]
col-span-2 row-span-2  // hero
col-span-2             // wide
row-span-2             // tall
```

### 2.3 Micro-Interactions che Migliorano UX

**Tier 1 — OBBLIGATORIE (impatto immediato):**
1. **Hover feedback**: Background color shift 100ms `transition-colors`
2. **Focus ring**: `ring-2 ring-offset-2 ring-primary` visibile
3. **Button press**: `active:scale-[0.98]` 100ms
4. **Toast notifications**: slide-in + auto-dismiss
5. **Loading skeleton**: shimmer `animate-pulse` su card

**Tier 2 — CONSIGLIATE (premium feel):**
1. **Card hover elevation**: `hover:shadow-lg hover:-translate-y-0.5` 200ms
2. **Tab underline slide**: CSS `transition: left 200ms, width 200ms`
3. **Number count-up**: animazione contatore su KPI (500ms, ease-out)
4. **Stagger children**: lista items che appaiono uno dopo l'altro (50ms delay)
5. **Smooth collapse/expand**: `transition-all duration-200` su height

**Tier 3 — NICE-TO-HAVE (wow factor):**
1. **Status morph**: icona che si trasforma (check → clock) con spring
2. **Drag reorder**: layout animation con framer-motion
3. **Parallax scroll leggero**: header si riduce scrollando
4. **Confetti/particles**: al raggiungimento milestone (loyalty)
5. **Command palette**: ⌘K con blur backdrop + fuzzy search

### 2.4 Color Semantics per Gestionali

**Standard universale 2026**:
| Colore | Significato | Uso | Tailwind |
|--------|-------------|-----|----------|
| Verde (#10B981) | Successo, completato, attivo | Appuntamento completato, pagamento ricevuto | `text-emerald-500` |
| Ambra (#F59E0B) | Attenzione, in attesa | In attesa conferma, scadenza vicina | `text-amber-500` |
| Rosso (#EF4444) | Errore, critico, cancellato | No-show, errore, fattura scaduta | `text-red-500` |
| Blu (#3B82F6) | Informativo, in corso | Appuntamento confermato, in lavorazione | `text-blue-500` |
| Viola (#8B5CF6) | Premium, VIP, speciale | Cliente VIP, pacchetto premium | `text-violet-500` |
| Grigio (#6B7280) | Neutro, inattivo, draft | Bozza, archivato, disabilitato | `text-gray-500` |
| Cyan (#06B6D4) | Brand FLUXION, primario | CTA, link, accent | `text-cyan-500` |

**Regola d'oro**: Mai piu' di 3 colori semantici visibili contemporaneamente in una sezione.

### 2.5 Spacing System Best Practice (4px/8px Grid)

**Il sistema 4px**:
```
4px   — xs  — gap tra icona e testo inline
8px   — sm  — gap tra elementi correlati (label → input)
12px  — md  — padding compact (badge, chip)
16px  — lg  — gap tra card, padding standard
20px  — xl  — padding card content
24px  — 2xl — gap tra sezioni
32px  — 3xl — margin tra macro-sezioni
40px  — 4xl — page top padding
```

**Tailwind mapping**:
```
gap-1 = 4px    p-1 = 4px
gap-2 = 8px    p-2 = 8px
gap-3 = 12px   p-3 = 12px
gap-4 = 16px   p-4 = 16px
gap-5 = 20px   p-5 = 20px
gap-6 = 24px   p-6 = 24px
gap-8 = 32px   p-8 = 32px
```

### 2.6 Animation Timing Functions

**Standard 2026**:
| Nome | CSS | Uso |
|------|-----|-----|
| Quick fade | `150ms ease-out` | Hover background, tooltip |
| Standard | `200ms ease-out` | Card transition, panel |
| Smooth | `300ms cubic-bezier(0.4, 0, 0.2, 1)` | Modal, slide |
| Spring | `500ms cubic-bezier(0.34, 1.56, 0.64, 1)` | Bounce, attention |
| Slow | `500ms ease-in-out` | Page transition, chart |

**Tailwind utility mapping**:
```
transition-colors duration-150     — hover colori
transition-all duration-200        — generale
transition-transform duration-200  — scale/translate
```

### 2.7 Border Radius Trends

**2026 consensus**: Border radius GENEROSI ma non estremi.
- **8px (rounded-lg)**: Bottoni, input, badge, tabelle
- **12px (rounded-xl)**: Card, dialog, dropdown menu
- **16px (rounded-2xl)**: Card hero, banner promozionali
- **Full (rounded-full)**: Avatar, stat chip, tag, toggle

**FLUXION attuale**: 8px (`--radius: 0.5rem`). Consiglio: aumentare a 12px per card principali.

### 2.8 Shadow Strategy Dark Mode

In dark mode le ombre classiche NON funzionano (ombra su sfondo scuro e' invisibile).

**Pattern 2026 per dark mode**:
1. **Border-based separation**: `border border-white/10` (principale)
2. **Background elevation**: 3 livelli di luminosita' crescente
3. **Glow accent**: `shadow-[0_0_15px_rgba(34,211,238,0.1)]` per hover
4. **Inner glow**: `shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]` per depth
5. **Color shadow**: `shadow-purple-500/20` per card colorate

**Layering system dark mode**:
```
Level 0 (page bg):  bg-slate-950  (#020617)
Level 1 (card):     bg-slate-900  (#0f172a)
Level 2 (surface):  bg-slate-800  (#1e293b)
Level 3 (hover):    bg-slate-700  (#334155)
Level 4 (active):   bg-slate-600  (#475569)
```

### 2.9 Gradient Usage in Dark Themes

**Pattern sicuri per dark mode**:
1. **Subtle header gradient**: `bg-gradient-to-br from-accent-950/40 via-slate-900 to-slate-900` — gia' in SchedaWrapper
2. **Card accent border gradient**: `bg-gradient-to-r from-cyan-500 to-purple-500` su 2px top border
3. **Background mesh**: 2-3 cerchi blur grandi (gia' in SchedaWrapper — blur circles)
4. **CTA button gradient**: `bg-gradient-to-r from-cyan-500 to-blue-500`
5. **Revenue chart area gradient**: `from-emerald-500/20 to-transparent` sotto la curva

**Pattern da EVITARE in dark mode**:
- Gradient su testo (illeggibile)
- Rainbow gradient (distraente, poco professionale)
- Gradient su background card intera (riduce leggibilita')

---

## 3. PATTERN SPECIFICI PER SCHEDE CLIENTE

### 3.1 Come i Migliori CRM Presentano Info Cliente

**Il "Contact Record" pattern universale (2026)**:

```
┌──────────────────────────────────────────────────────────┐
│ ┌──────┐  Maria Rossi              ⭐ VIP    [Modifica] │
│ │Avatar│  +39 333 1234567 · maria@email.it              │
│ │ 80px │  Ultimo appuntamento: 15 Mar 2026              │
│ └──────┘                                                 │
├──────────────────────────────────────────────────────────┤
│ 📊 47 visite │ 💰 €3.420 spesi │ ⏱ 2.3 anni │ 🎯 Gold  │
├──────────────────────────────────────────────────────────┤
│ [Profilo] [Storico] [Scheda] [Prodotti] [Note] [Media]  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Tab content area                                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 3.2 Header Pattern con Avatar + Stats + Quick Actions

**Gold standard**: Il header del profilo cliente deve comunicare TUTTO in 3 secondi.

**Livello 1 — Identita'**:
- Avatar: 64-80px, circolare, con iniziali se no foto
- Nome: 20-24px bold
- Contatti: telefono + email inline, cliccabili
- Badge: VIP/Gold/Silver, tipo cliente

**Livello 2 — Stats at a glance**:
- 3-5 stat chip orizzontali sotto il nome
- Numeri bold, label piccola, icona colorata
- Visite totali | Spesa totale | Anzianita' | Livello fedelta'

**Livello 3 — Quick Actions**:
- Bottoni ghost/outline allineati a destra
- Nuovo appuntamento | Invia WhatsApp | Modifica | Altro (...menu)

**Tailwind implementation**:
```tsx
// Header cliente gold standard
<div className="flex items-start gap-4 p-6">
  {/* Avatar */}
  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500
                  flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
    MR
  </div>
  {/* Info */}
  <div className="flex-1 min-w-0">
    <div className="flex items-center gap-2">
      <h2 className="text-xl font-bold text-white truncate">Maria Rossi</h2>
      <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30">VIP</Badge>
    </div>
    <p className="text-sm text-slate-400 mt-0.5">+39 333 123 4567 · maria@email.it</p>
    {/* Stat chips */}
    <div className="flex flex-wrap gap-2 mt-3">
      <StatChip icon={<Calendar />} label="Visite" value="47" />
      <StatChip icon={<Wallet />} label="Spesi" value="€3.420" />
      <StatChip icon={<Clock />} label="Cliente da" value="2.3 anni" />
    </div>
  </div>
  {/* Actions */}
  <div className="flex gap-2">
    <Button variant="outline" size="sm">Nuovo appuntamento</Button>
    <Button variant="outline" size="sm">WhatsApp</Button>
  </div>
</div>
```

### 3.3 Tab Navigation Best Practices

**Pattern 2026**:
- Tabs orizzontali sotto il header — NO sidebar tabs (spreco spazio)
- Underline indicator animato (slide, non jump)
- Badge conteggio sulla tab se pertinente ("Note (3)")
- Max 6-7 tab visibili, oltre: overflow menu "..."
- Tab attiva: text-white + underline accent. Inattiva: text-slate-400

**shadcn/ui Tabs pattern ottimizzato**:
```tsx
<Tabs defaultValue="profilo" className="w-full">
  <TabsList className="bg-slate-800/50 border-b border-slate-700 w-full justify-start rounded-none h-auto p-0">
    <TabsTrigger value="profilo"
      className="rounded-none border-b-2 border-transparent data-[state=active]:border-cyan-400
                 data-[state=active]:text-cyan-400 data-[state=active]:bg-transparent
                 text-slate-400 hover:text-slate-200 px-4 py-3 text-sm">
      Profilo
    </TabsTrigger>
    {/* ... altre tabs ... */}
  </TabsList>
  <TabsContent value="profilo" className="mt-6">
    {/* content */}
  </TabsContent>
</Tabs>
```

### 3.4 Section Cards vs Flat Layout

**Quando usare CARD (bordered sections)**:
- Dati che l'utente potrebbe voler collassare/espandere
- Sezioni con azioni proprie (edit, save)
- Quando ci sono 3+ sezioni nella stessa pagina
- Dati che hanno un lifecycle diverso (es. allergie vs preferenze)

**Quando usare FLAT layout**:
- Form semplici con pochi campi
- Tab content con una sola sezione
- Quando lo spazio e' limitato

**Pattern raccomandato per schede verticali FLUXION**:
Usare **section cards** con header collassabile:
```tsx
<div className="space-y-4">
  <SectionCard title="Informazioni Base" icon={<User />} defaultOpen>
    {/* form fields */}
  </SectionCard>
  <SectionCard title="Allergie e Controindicazioni" icon={<AlertTriangle />}
               alertCount={2} defaultOpen>
    {/* allergie list */}
  </SectionCard>
  <SectionCard title="Storico Trattamenti" icon={<Clock />}>
    {/* timeline */}
  </SectionCard>
</div>
```

### 3.5 "Passport" Style Summary (Fresha Beauty Profile)

Fresha ha introdotto il "Beauty Passport" — un summary card che mostra le preferenze del cliente in un formato visuale compatto.

**Struttura**:
```
┌─────────────────────────────────────────┐
│ 🎨 BEAUTY PASSPORT                      │
├──────────┬──────────┬───────────────────┤
│ Capelli  │ Pelle    │ Preferenze        │
│ Castano  │ Mista    │ ❌ No ammoniaca   │
│ Medio    │ Sensib.  │ ✅ Prodotti bio   │
│ Mossi    │          │ ⏱ Pref. mattina   │
└──────────┴──────────┴───────────────────┘
```

**Per FLUXION — adattamento per verticale**:

Parrucchiere: Hair Profile (tipo capello, colore attuale, allergie, preferenze)
Estetica: Skin Profile (tipo pelle, allergie, zona trattamento preferita)
Fitness: Fitness Profile (obiettivo, livello, infortuni, frequenza)
Odontoiatrica: Dental Profile (ultima pulizia, protesi, allergie farmaci)
Veicoli: Vehicle Profile (marca, modello, anno, km, ultima revisione)
Carrozzeria: Body Profile (colore, danni noti, assicurazione)

**Tailwind implementation**:
```tsx
<div className="grid grid-cols-3 gap-3 p-4 bg-slate-800/50 rounded-xl border border-slate-700">
  <div>
    <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Capelli</p>
    <div className="space-y-1">
      <p className="text-sm text-white">Castano scuro</p>
      <p className="text-sm text-slate-300">Lunghezza media</p>
      <p className="text-sm text-slate-300">Mossi</p>
    </div>
  </div>
  <div>
    <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Pelle</p>
    <div className="space-y-1">
      <p className="text-sm text-white">Mista</p>
      <p className="text-sm text-slate-300">Sensibile</p>
    </div>
  </div>
  <div>
    <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Preferenze</p>
    <div className="space-y-1">
      <div className="flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
        <p className="text-sm text-slate-300">No ammoniaca</p>
      </div>
      <div className="flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        <p className="text-sm text-slate-300">Prodotti bio</p>
      </div>
    </div>
  </div>
</div>
```

### 3.6 Status Indicators Inline

**Pattern universale 2026**:
- **Dot indicator**: cerchietto 6-8px colorato prima del testo (Monday.com style)
- **Badge pill**: `px-2 py-0.5 rounded-full text-xs font-medium` con bg pastello
- **Icon indicator**: icona Lucide 16px colorata (CheckCircle, Clock, XCircle)
- **Progress bar inline**: barra sottile sotto il testo (es. completamento scheda)

**Quale usare**:
- Dot: per status semplici in lista (attivo/inattivo)
- Badge: per status con testo (Confermato, In attesa, Cancellato)
- Icon: per status in tabelle compatte
- Progress: per completamento percentuale

### 3.7 Progress Bars / Completion Indicators

**Scheda completamento** — Feature chiave per FLUXION:
Indicare quanto della scheda cliente e' stata compilata.

```tsx
// Completion bar per scheda cliente
<div className="flex items-center gap-3">
  <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
    <div className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full transition-all duration-500"
         style={{ width: `${completionPercent}%` }} />
  </div>
  <span className="text-xs text-slate-400 tabular-nums w-8">{completionPercent}%</span>
</div>
```

### 3.8 Tag/Badge System

**Design pattern 2026**:
```tsx
// Varianti badge
<Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/25">Attivo</Badge>
<Badge className="bg-amber-500/15 text-amber-400 border-amber-500/25">In Attesa</Badge>
<Badge className="bg-red-500/15 text-red-400 border-red-500/25">Cancellato</Badge>
<Badge className="bg-purple-500/15 text-purple-400 border-purple-500/25">VIP</Badge>
<Badge className="bg-slate-500/15 text-slate-400 border-slate-500/25">Archiviato</Badge>
```

**Regole**:
- Background: colore/15% opacity
- Testo: colore/400 (shade chiara in dark mode)
- Border: colore/25% opacity
- Font: text-xs font-medium
- Padding: px-2 py-0.5
- Border radius: rounded-full (pill shape)

---

## 4. GAP ANALYSIS FLUXION vs GOLD STANDARD

### 4.1 Cosa FLUXION Ha Gia' (Bene)

1. **Dark mode come default** — Allineato con Linear, Figma
2. **Sidebar collapsible** — Pattern corretto (60px → 240px)
3. **Inter font** — Gold standard (usato da Linear, Notion, Figma)
4. **SchedaWrapper glassmorphism** — Ben implementato
5. **Color accent system** — 6 colori verticali (purple, blue, red, pink, green, indigo)
6. **shadcn/ui components** — Base solida
7. **StatChip pattern** — Buono, simile a Stripe
8. **AlertBadge** — Pattern corretto
9. **Z-index hierarchy** — Professionale

### 4.2 Cosa MANCA (Gap Critici)

**GAP 1: DASHBOARD NON HA BENTO BOX LAYOUT**
- Attuale: Grid uniforme 4 colonne. Tutte le card sono identiche.
- Gold standard: Bento asimmetrico con hero card (Stripe, Apple style).
- Impatto: La dashboard sembra "generica" invece che "premium".
- Fix: Ridisegnare la grid con card hero, card larghe, sparkline.

**GAP 2: STAT CARD DESIGN TROPPO PIATTO**
- Attuale: `bg-slate-900 border-slate-800` con numero grande e icona. Nessun sparkline, nessun trend indicator.
- Gold standard (Stripe): KPI con trend arrow (+12%↗), sparkline mini, secondary metric.
- Impatto: I numeri da soli non comunicano trend. Manca il "momentum".
- Fix: Aggiungere trend arrow, sparkline SVG, confronto vs mese precedente.

**GAP 3: MANCANO MICRO-ANIMATIONS**
- Attuale: Solo `transition-colors` su hover. Nessun hover elevation, nessun stagger, nessun count-up.
- Gold standard (Linear): Hover elevation, stagger list, status morph, spring easing.
- Impatto: L'app sembra "statica" — non da' feedback visivo alle azioni.
- Fix: Aggiungere `hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200` alle card.

**GAP 4: EMPTY STATES TROPPO MINIMALI**
- Attuale: Icona + testo breve. Nessuna illustrazione, nessuna guida.
- Gold standard (Fresha): Illustrazione custom + heading + subtext + CTA bottone.
- Impatto: L'utente PMI non capisce cosa fare quando la pagina e' vuota.
- Fix: Creare empty states con icona grande + heading + istruzioni + CTA.

**GAP 5: NESSUN LOADING SKELETON**
- Attuale: Solo spinner `Loader2` centrato.
- Gold standard (Stripe, Shopify): Skeleton shimmer che replica il layout.
- Impatto: Il caricamento sembra "rotto" invece che "sta arrivando".
- Fix: Skeleton component con `animate-pulse` che replica la struttura della card.

**GAP 6: TABELLE SENZA VISUAL POLISH**
- Attuale: Tabelle base shadcn/ui, nessun hover row, nessun zebra striping, nessun bordo colorato.
- Gold standard (Notion, Monday): Hover row, status dot inline, avatar inline, azioni contestuali.
- Impatto: Le tabelle clienti/servizi sembrano "database dump".
- Fix: Row hover, avatar iniziali, status dot, azioni on hover.

**GAP 7: MANCA "CLIENT PASSPORT" / PROFILE SUMMARY**
- Attuale: Le schede verticali (Parrucchiere, Fitness, etc.) sono form-based. Nessun summary visuale.
- Gold standard (Fresha): Beauty Passport con dati chiave in griglia visuale.
- Impatto: L'operatore deve scrollare per trovare info chiave del cliente.
- Fix: Aggiungere "Passport card" in cima a ogni scheda con dati chiave.

**GAP 8: NESSUN COMPLETION INDICATOR PER SCHEDE**
- Attuale: Non si sa quanto della scheda e' compilato.
- Gold standard (Jane App): Progress bar + checklist obbligatori.
- Impatto: Le schede restano incomplete senza feedback.
- Fix: Progress bar in header scheda + indicatori campo obbligatorio.

**GAP 9: CARD BORDER RADIUS INCONSISTENTE**
- Attuale: Mix di `rounded-xl` (card.tsx), `rounded-2xl` (SchedaWrapper), `rounded-lg` (badge).
- Gold standard: Sistema consistente di border radius.
- Fix: Standardizzare: 8px input/badge, 12px card/dialog, 16px hero/modal, full per avatar/chip.

**GAP 10: MANCA CARD ACCENT BAR**
- Attuale: Card tutte con bordo uniforme.
- Gold standard (Monday.com): 4px colored bar a sinistra o in alto per categorizzare.
- Impatto: Le card non hanno personalita' visiva. Tutto sembra uguale.
- Fix: Aggiungere accent bar opzionale a Card component.

### 4.3 Top 5 Miglioramenti a Massimo Impatto Visivo

**PRIORITA' 1: Dashboard Bento Box Layout**
- Impatto: TRASFORMA la prima impressione dell'app
- Effort: Medio (ristruttura grid + stat card redesign)
- ROI: Altissimo — la dashboard e' la prima cosa che l'utente vede

**PRIORITA' 2: Card Hover + Micro-Animations**
- Impatto: L'app passa da "statica" a "viva"
- Effort: Basso (solo classi Tailwind)
- ROI: Alto — poche righe, grande impatto percepito

**PRIORITA' 3: Stat Card Redesign con Trend + Sparkline**
- Impatto: I KPI comunicano valore (trend, momentum)
- Effort: Medio (calcolo trend + SVG sparkline)
- ROI: Alto — i numeri da soli non bastano

**PRIORITA' 4: Client Passport Summary**
- Impatto: L'operatore vede tutto in 3 secondi
- Effort: Medio (nuovo componente per ogni verticale)
- ROI: Alto — uso quotidiano, risparmio tempo reale

**PRIORITA' 5: Loading Skeleton + Empty States Premium**
- Impatto: L'app sembra professionale anche quando non ha dati
- Effort: Basso-Medio
- ROI: Medio — edge cases ma importanti per prima impressione

---

## 5. TAILWIND CSS + SHADCN/UI RICETTARIO

### 5.1 Bento Box Dashboard Grid

```tsx
// Dashboard Bento Layout
<div className="grid grid-cols-4 gap-4">
  {/* Hero Card — Revenue (span 2 cols, 2 rows) */}
  <div className="col-span-2 row-span-2 rounded-2xl bg-gradient-to-br from-cyan-950/40 via-slate-900 to-slate-900
                  border border-slate-700/60 p-6 flex flex-col justify-between">
    <div>
      <p className="text-sm text-slate-400">Fatturato del mese</p>
      <p className="text-4xl font-bold text-white mt-2">€12.480</p>
      <div className="flex items-center gap-1.5 mt-1">
        <span className="text-emerald-400 text-sm font-medium">↑ 12%</span>
        <span className="text-slate-500 text-sm">vs mese scorso</span>
      </div>
    </div>
    {/* Sparkline SVG here */}
    <div className="h-16 mt-4">
      <svg viewBox="0 0 200 60" className="w-full h-full">
        <path d="M0,45 L20,40 L40,42 L60,35 L80,38 L100,25 L120,28 L140,15 L160,18 L180,10 L200,8"
              fill="none" stroke="rgb(34,211,238)" strokeWidth="2" />
        <path d="M0,45 L20,40 L40,42 L60,35 L80,38 L100,25 L120,28 L140,15 L160,18 L180,10 L200,8 L200,60 L0,60Z"
              fill="url(#gradient)" opacity="0.15" />
      </svg>
    </div>
  </div>

  {/* Regular stat cards */}
  <StatCardBento title="Appuntamenti oggi" value="12" trend="+3" icon={<Calendar />} color="cyan" />
  <StatCardBento title="Clienti totali" value="342" trend="+18" icon={<Users />} color="emerald" />
  <StatCardBento title="Nuovi questo mese" value="23" subtitle="vs 19 scorso" icon={<UserPlus />} color="purple" />
  <StatCardBento title="No-show" value="2" trend="-1" trendGood icon={<XCircle />} color="red" />
</div>
```

### 5.2 Stat Card Bento con Trend

```tsx
interface StatCardBentoProps {
  title: string;
  value: string;
  trend?: string;
  trendGood?: boolean;
  subtitle?: string;
  icon: React.ReactNode;
  color: 'cyan' | 'emerald' | 'purple' | 'amber' | 'red';
}

function StatCardBento({ title, value, trend, trendGood, subtitle, icon, color }: StatCardBentoProps) {
  const colorMap = {
    cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    red: 'text-red-400 bg-red-500/10 border-red-500/20',
  };
  const [iconColor, iconBg, iconBorder] = colorMap[color].split(' ');

  const trendIsPositive = trend?.startsWith('+');
  const trendColor = trendGood
    ? (trendIsPositive ? 'text-emerald-400' : 'text-emerald-400')
    : (trendIsPositive ? 'text-emerald-400' : 'text-red-400');

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-700/60 p-5
                    hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/20
                    transition-all duration-200 group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider font-medium">{title}</p>
          <p className={`text-2xl font-bold mt-1.5 ${iconColor}`}>{value}</p>
          {trend && (
            <p className={`text-xs mt-1 ${trendColor} font-medium`}>
              {trend} vs scorso
            </p>
          )}
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-2.5 rounded-xl ${iconBg} border ${iconBorder}
                        group-hover:scale-110 transition-transform duration-200`}>
          <span className={iconColor}>{icon}</span>
        </div>
      </div>
    </div>
  );
}
```

### 5.3 Card con Hover Elevation (universale)

```tsx
// Card con hover premium
<Card className="bg-slate-900 border-slate-700/60
                 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/20
                 hover:border-slate-600/60
                 transition-all duration-200 cursor-pointer">
  {/* ... */}
</Card>
```

CSS equivalente se si vuole aggiungere al componente Card globalmente:
```css
[data-slot="card"] {
  transition: transform 200ms ease-out, box-shadow 200ms ease-out, border-color 200ms ease-out;
}
[data-slot="card"]:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
}
```

### 5.4 Loading Skeleton Component

```tsx
function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn(
      "animate-pulse rounded-lg bg-slate-800",
      className
    )} />
  );
}

// Dashboard skeleton
function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-4 gap-4">
      {/* Hero skeleton */}
      <div className="col-span-2 row-span-2 rounded-2xl bg-slate-900 border border-slate-700/60 p-6">
        <Skeleton className="h-4 w-32 mb-3" />
        <Skeleton className="h-10 w-48 mb-2" />
        <Skeleton className="h-3 w-24 mb-8" />
        <Skeleton className="h-16 w-full" />
      </div>
      {/* Stat skeletons */}
      {[1, 2, 3, 4].map(i => (
        <div key={i} className="rounded-2xl bg-slate-900 border border-slate-700/60 p-5">
          <Skeleton className="h-3 w-24 mb-3" />
          <Skeleton className="h-7 w-16 mb-2" />
          <Skeleton className="h-3 w-20" />
        </div>
      ))}
    </div>
  );
}
```

### 5.5 Empty State Premium

```tsx
interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

function EmptyState({ icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-8">
      <div className="p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50 mb-4">
        <span className="text-slate-500 [&>svg]:w-8 [&>svg]:h-8">{icon}</span>
      </div>
      <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
      <p className="text-sm text-slate-400 text-center max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} className="mt-4 bg-cyan-600 hover:bg-cyan-500">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

// Uso
<EmptyState
  icon={<Calendar />}
  title="Nessun appuntamento oggi"
  description="La giornata è libera. Aggiungi un appuntamento o controlla il calendario della settimana."
  actionLabel="Vai al calendario"
  onAction={() => navigate('/calendario')}
/>
```

### 5.6 Client Passport Card

```tsx
interface PassportField {
  label: string;
  items: Array<{ text: string; color?: 'red' | 'green' | 'amber' | 'default' }>;
}

function ClientPassport({ fields, accentColor }: { fields: PassportField[]; accentColor: string }) {
  const dotColors = {
    red: 'bg-red-400',
    green: 'bg-emerald-400',
    amber: 'bg-amber-400',
    default: 'bg-slate-400',
  };

  return (
    <div className="grid grid-cols-3 gap-4 p-4 bg-slate-800/30 rounded-xl border border-slate-700/50">
      {fields.map((field) => (
        <div key={field.label}>
          <p className="text-[10px] text-slate-500 uppercase tracking-[0.1em] font-semibold mb-2">
            {field.label}
          </p>
          <div className="space-y-1.5">
            {field.items.map((item, i) => (
              <div key={i} className="flex items-center gap-1.5">
                {item.color && (
                  <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${dotColors[item.color]}`} />
                )}
                <p className="text-sm text-slate-300">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// Uso per Parrucchiere
<ClientPassport
  accentColor="purple"
  fields={[
    { label: 'Capelli', items: [
      { text: 'Castano scuro' },
      { text: 'Lunghezza media' },
      { text: 'Mossi/ricci' },
    ]},
    { label: 'Sensibilità', items: [
      { text: 'No ammoniaca', color: 'red' },
      { text: 'Cuoio sensibile', color: 'amber' },
    ]},
    { label: 'Preferenze', items: [
      { text: 'Prodotti bio', color: 'green' },
      { text: 'Preferisce mattina' },
      { text: 'Lavaggio delicato', color: 'green' },
    ]},
  ]}
/>
```

### 5.7 Table Row con Hover Polish

```tsx
// Riga tabella con polish
<tr className="group border-b border-slate-800 hover:bg-slate-800/50 transition-colors duration-100">
  <td className="py-3 px-4">
    <div className="flex items-center gap-3">
      {/* Avatar iniziali */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-500/20
                      border border-slate-700 flex items-center justify-center flex-shrink-0">
        <span className="text-xs font-medium text-slate-300">MR</span>
      </div>
      <div>
        <p className="text-sm font-medium text-white">Maria Rossi</p>
        <p className="text-xs text-slate-500">+39 333 123 4567</p>
      </div>
    </div>
  </td>
  <td className="py-3 px-4">
    <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/25 text-xs">
      Attiva
    </Badge>
  </td>
  <td className="py-3 px-4 text-sm text-slate-400">15 Mar 2026</td>
  <td className="py-3 px-4 text-right">
    {/* Actions visibili solo on hover */}
    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-150 flex gap-1 justify-end">
      <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
        <Pencil className="h-3.5 w-3.5" />
      </Button>
      <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-red-400">
        <Trash2 className="h-3.5 w-3.5" />
      </Button>
    </div>
  </td>
</tr>
```

### 5.8 Section Card Collapsabile

```tsx
import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface SectionCardProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
  alertCount?: number;
  accentColor?: string;
}

function SectionCard({ title, icon, children, defaultOpen = true, alertCount, accentColor = 'slate' }: SectionCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-900 overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-5 py-3.5 hover:bg-slate-800/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-slate-400 [&>svg]:w-4 [&>svg]:h-4">{icon}</span>
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          {alertCount != null && alertCount > 0 && (
            <span className="px-1.5 py-0.5 rounded-full bg-red-500/20 text-red-400 text-[10px] font-bold">
              {alertCount}
            </span>
          )}
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      <div className={`transition-all duration-200 ${isOpen ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'}`}>
        <div className="px-5 pb-5 pt-2">
          {children}
        </div>
      </div>
    </div>
  );
}
```

### 5.9 Completion Progress per Scheda

```tsx
function SchedaCompletion({ fields }: { fields: Array<{ name: string; filled: boolean }> }) {
  const filled = fields.filter(f => f.filled).length;
  const total = fields.length;
  const percent = Math.round((filled / total) * 100);

  const color = percent === 100 ? 'emerald' : percent >= 50 ? 'cyan' : 'amber';
  const barColors = {
    emerald: 'from-emerald-500 to-emerald-400',
    cyan: 'from-cyan-500 to-cyan-400',
    amber: 'from-amber-500 to-amber-400',
  };

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-slate-800/30 rounded-lg border border-slate-700/40">
      <span className="text-xs text-slate-500">Completamento</span>
      <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${barColors[color]} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${percent}%` }}
        />
      </div>
      <span className={`text-xs font-semibold tabular-nums w-8 text-${color}-400`}>
        {percent}%
      </span>
    </div>
  );
}
```

### 5.10 Toast Notification Premium (con Sonner)

Sonner e' gia' integrato in FLUXION. Pattern per toast premium:

```tsx
import { toast } from 'sonner';

// Success con icona e description
toast.success('Appuntamento salvato', {
  description: 'Maria Rossi — Taglio + Colore, domani alle 10:00',
});

// Warning
toast.warning('Sovrapposizione orario', {
  description: 'L\'operatore ha già un appuntamento alle 10:00',
  action: {
    label: 'Vedi conflitto',
    onClick: () => navigate('/calendario'),
  },
});

// Custom styled (dark mode FLUXION)
toast.custom((t) => (
  <div className="flex items-center gap-3 px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl shadow-xl">
    <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
    <div>
      <p className="text-sm font-medium text-white">Scheda aggiornata</p>
      <p className="text-xs text-slate-400">Le modifiche sono state salvate</p>
    </div>
  </div>
));
```

### 5.11 Button Variations (Design System Completo)

```tsx
// Primary CTA
<Button className="bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-900/30
                   active:scale-[0.98] transition-all duration-150">
  Salva
</Button>

// Secondary
<Button className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700
                   active:scale-[0.98] transition-all duration-150">
  Annulla
</Button>

// Destructive
<Button className="bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/30
                   active:scale-[0.98] transition-all duration-150">
  Elimina
</Button>

// Ghost
<Button className="hover:bg-slate-800 text-slate-400 hover:text-white
                   active:scale-[0.98] transition-all duration-150">
  Annulla
</Button>

// Accent (per vertical color)
<Button className="bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-900/30
                   active:scale-[0.98] transition-all duration-150">
  Aggiungi trattamento
</Button>

// Icon button
<Button className="h-8 w-8 p-0 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white
                   transition-colors duration-150">
  <Plus className="h-4 w-4" />
</Button>
```

### 5.12 Tabs Underline Animate (shadcn/ui override)

Per sostituire le tabs shadcn default con underline animate style Linear:

```css
/* In index.css */
[data-slot="tabs-list"] {
  background: transparent;
  border-bottom: 1px solid hsl(215 25% 27%);
  border-radius: 0;
  padding: 0;
  height: auto;
  width: 100%;
  justify-content: flex-start;
}

[data-slot="tabs-trigger"] {
  border-radius: 0;
  background: transparent;
  border-bottom: 2px solid transparent;
  padding: 12px 16px;
  color: hsl(215 28% 42%);
  font-size: 14px;
  font-weight: 500;
  transition: color 150ms ease-out, border-color 150ms ease-out;
}

[data-slot="tabs-trigger"]:hover {
  color: hsl(210 40% 96%);
}

[data-slot="tabs-trigger"][data-state="active"] {
  color: hsl(189 94% 56%);
  border-bottom-color: hsl(189 94% 56%);
  background: transparent;
  box-shadow: none;
}
```

### 5.13 Focus Ring Premium

```css
/* Consistent focus ring per tutto il design system */
*:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px hsl(217 33% 17%), 0 0 0 4px hsl(189 94% 56%);
  border-radius: inherit;
}

/* Input focus */
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  border-color: hsl(189 94% 56%);
  box-shadow: 0 0 0 3px hsl(189 94% 56% / 0.15);
}
```

### 5.14 Stagger Animation per Liste

```tsx
// Con CSS + classi utility
function StaggerList({ children }: { children: React.ReactNode[] }) {
  return (
    <div className="space-y-2">
      {React.Children.map(children, (child, i) => (
        <div
          className="animate-[fadeSlideIn_300ms_ease-out_forwards] opacity-0"
          style={{ animationDelay: `${i * 50}ms` }}
        >
          {child}
        </div>
      ))}
    </div>
  );
}

// Aggiungere in index.css:
@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 5.15 Number Count-Up per KPI

```tsx
import { useState, useEffect, useRef } from 'react';

function AnimatedNumber({ value, duration = 500 }: { value: number; duration?: number }) {
  const [display, setDisplay] = useState(0);
  const prevValue = useRef(0);

  useEffect(() => {
    const start = prevValue.current;
    const end = value;
    const startTime = performance.now();

    function update(now: number) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(start + (end - start) * eased));

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
    prevValue.current = value;
  }, [value, duration]);

  return <span className="tabular-nums">{display}</span>;
}

// Uso
<p className="text-3xl font-bold text-cyan-400">
  <AnimatedNumber value={stats.appuntamenti_oggi} />
</p>
```

---

## 6. DESIGN TOKENS RACCOMANDATI PER FLUXION

### Aggiornamento proposto a CSS custom properties:

```css
:root {
  /* ─── Spacing ─── */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 20px;
  --space-2xl: 24px;
  --space-3xl: 32px;
  --space-4xl: 40px;

  /* ─── Radius ─── */
  --radius-sm: 6px;     /* badge, chip */
  --radius-md: 8px;     /* input, button */
  --radius-lg: 12px;    /* card, dialog */
  --radius-xl: 16px;    /* hero card, modal */
  --radius-full: 9999px; /* avatar, pill */

  /* ─── Shadow Dark Mode ─── */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.25);
  --shadow-lg: 0 8px 25px rgba(0, 0, 0, 0.3);
  --shadow-glow-cyan: 0 0 15px rgba(34, 211, 238, 0.1);
  --shadow-glow-purple: 0 0 15px rgba(192, 132, 252, 0.1);

  /* ─── Transitions ─── */
  --transition-fast: 100ms ease-out;
  --transition-base: 200ms ease-out;
  --transition-smooth: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-spring: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);

  /* ─── Surface Elevation ─── */
  --surface-0: hsl(222, 47%, 3%);    /* page background — #020617 slate-950 */
  --surface-1: hsl(222, 47%, 7%);    /* card — #0f172a slate-900 */
  --surface-2: hsl(217, 33%, 17%);   /* elevated — #1e293b slate-800 */
  --surface-3: hsl(215, 25%, 27%);   /* hover — #334155 slate-700 */
  --surface-4: hsl(215, 20%, 40%);   /* active — #475569 slate-600 */
}
```

---

## 7. CHECKLIST IMPLEMENTAZIONE

### Quick Wins (< 1 ora ciascuno)
- [ ] Aggiungere `hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200` a tutte le card cliccabili
- [ ] Aggiungere `active:scale-[0.98]` a tutti i bottoni
- [ ] Standardizzare border radius: card → `rounded-xl`, hero → `rounded-2xl`
- [ ] Aggiungere `group-hover:opacity-100 opacity-0` per azioni tabella
- [ ] Tab underline animate (CSS override in index.css)

### Medium Effort (1-3 ore ciascuno)
- [ ] Dashboard bento box layout (grid asimmetrico)
- [ ] Stat card con trend arrow + micro-sparkline
- [ ] Loading skeleton per Dashboard, Clienti, Calendario
- [ ] Empty state premium component riutilizzabile
- [ ] Client Passport card per SchedaParrucchiere (prototipo)

### Larger Effort (3-8 ore ciascuno)
- [ ] Number count-up animation per KPI
- [ ] Client Passport per tutte le 6 verticali
- [ ] Completion progress bar per tutte le schede
- [ ] Stagger animation per liste
- [ ] Section card collapsabile con animazione smooth

---

**Fine documento. 680+ righe. Pronto per implementazione.**
