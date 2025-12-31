# 🎨 FLUXION DESIGN BIBLE
## Design System Completo per Gestionale Desktop Enterprise (Tauri 2.x + React 19 + Shadcn/UI)

**Versione**: 1.0  
**Data**: 28 Dicembre 2025  
**Target**: PMI Italiane (Saloni, Palestre, Cliniche, Ristoranti)  
**Stack**: Tauri 2.x + React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui

---

## FASE 1: REFERENCE ANALYSIS — TOP 5 REPOSITORY + PRODOTTI

### 🏆 TOP 5 SELEZIONATI

#### **#1. Linear.app — GOLD STANDARD SaaS UI**
- **Link**: https://linear.app
- **Design Blog**: https://linear.app/now/how-we-redesigned-the-linear-ui
- **Stack**: React + Next.js + Custom CSS variables + Dark mode native
- **Perché scelto**:
  - ✅ **Dark mode como default** (esattamente quello che vuoi)
  - ✅ **Sidebar collapsible ultra-pulito** (pattern perfetto per gestionale)
  - ✅ **Color system a 3 variabili** (HSL-based, perceptually uniform)
  - ✅ **Typography hierarchy raffinata** (font size scale 12px base)
  - ✅ **Micro-interactions eleganti** (hover effects, transitions)
  - ✅ **Enterprise-focused** (not toy app)
  
- **Elementi da "rubare"**:
  1. **Sidebar**: Width 60px (collapsed) → 240px (expanded), smooth transition 200ms
  2. **Color system**: 3 CSS variables (base, accent, contrast) + computed derivations
  3. **Header bar**: Minimal, icon + search + profile, height 56px
  4. **Card design**: Subtle border (1px), soft shadow (rgba 0 0 0 / 5%), border-radius 8px
  5. **Focus ring**: Color accent with 3px offset, glow effect

#### **#2. Vercel Dashboard — Glassmorphism + Data Visualization**
- **Link**: https://vercel.com/dashboard
- **Stack**: Next.js + React + Tailwind CSS + Recharts
- **Perché scelto**:
  - ✅ **Glassmorphism fatto bene** (non overdone, readable)
  - ✅ **Card-based layout** (perfetto per KPI dashboard)
  - ✅ **Chart integration** (Recharts, revenue trends)
  - ✅ **Accessible color contrast** (WCAG AA compliant)
  - ✅ **Micro-animations** (fade-in cards, hover scale 1.02)
  
- **Elementi da "rubare"**:
  1. **Card glassmorphism**: `backdrop-blur-20px` + `border border-white/10` + `bg-white/5`
  2. **KPI layout**: 4 column grid, height 120px per card
  3. **Chart area**: 70% width, 300px height min, interactive tooltip
  4. **Data table**: Hover row background change, alternating row opacity

#### **#3. shadcn-admin (GitHub) — Production-Ready Dashboard Template**
- **Link**: https://github.com/satnaing/shadcn-admin
- **Stack**: React 19 + Vite + TypeScript + Tailwind CSS v4 + shadcn/ui
- **Licenza**: MIT (100% open source)
- **Perché scelto**:
  - ✅ **Copy-paste ready** (zero setup time)
  - ✅ **Shadcn/ui components** (Button, Card, Dialog, Table, etc.)
  - ✅ **Dark mode toggle built-in**
  - ✅ **Responsive sidebar**
  - ✅ **Multiple page examples** (Users, Products, Analytics)
  
- **Elementi da "rubare"**:
  1. **Sidebar component structure** (expand/collapse logic)
  2. **useMediaQuery hook** (responsive breakpoints)
  3. **Navigation routing** (sidebar items → pages)
  4. **Table component** (actions, filtering, sorting)
  5. **Dialog/Modal patterns**

#### **#4. Cal.com Atoms — Booking Component Library**
- **Link**: https://github.com/calcom/cal.com + https://cal.com/integrate
- **Stack**: React + TypeScript + Tailwind CSS
- **Licenza**: AGPL core / Custom Atoms
- **Perché scelto**:
  - ✅ **Booking/Calendar widget funzionante**
  - ✅ **Week view + time slots**
  - ✅ **Drag-drop appointments** (optional)
  - ✅ **Timezone handling automatico**
  - ✅ **Color-coded services/types**
  
- **Elementi da "rubare"**:
  1. **Week view calendar structure** (7 columns, hourly rows)
  2. **Time slot component** (height 60px per ora, interactive)
  3. **Appointment card UI** (gradient based on type, shadow on hover)
  4. **Availability indicator** (green/gray status)
  5. **Resize/drag feedback** (visual border highlight)

#### **#5. Tauri + Shadcn/UI Template (agmmnn/tauri-ui)**
- **Link**: https://github.com/agmmnn/tauri-ui
- **Stack**: Tauri 2.x + React + shadcn/ui + Tailwind CSS
- **Licenza**: MIT (open source)
- **Perché scelto**:
  - ✅ **Desktop-specific optimizations** (native window controls)
  - ✅ **Bundle size ottimizzato** (2.5MB .msi file)
  - ✅ **Native look-and-feel** (not web app in window)
  - ✅ **Dark mode system integration**
  - ✅ **Lucide icons pre-integrated**
  
- **Elementi da "rubare"**:
  1. **Tauri window titlebar integration** (titleBarStyle: 'custom')
  2. **Drag region CSS** (`data-tauri-drag-region`)
  3. **System menu integration**
  4. **Performance optimizations** (lazy loading, code splitting)
  5. **Release workflow** (GitHub Actions cross-platform builds)

---

## FASE 2: PATTERN EXTRACTION — Design Components Specifici

### A) SIDEBAR NAVIGATION

```plaintext
┌─────────────────────────┐
│ F [Fluxion Logo]        │  ← Fixed header (60px)
├─────────────────────────┤
│ 🏠 Home                 │
│ 📅 Calendario           │
│ 👥 Clienti              │
│ 🏪 Servizi              │
│ 📊 Analytics            │  ← Menu items (40px height)
│ ⚙️  Impostazioni         │
├─────────────────────────┤
│ [User Avatar]           │
│ Mario Rossi             │
│ mario@salon.it          │  ← User profile (60px bottom)
└─────────────────────────┘
```

| Property | Value | Note |
|----------|-------|------|
| **Width (expanded)** | 240px | Smooth transition 200ms ease-out |
| **Width (collapsed)** | 60px | Only icons visible |
| **Transition** | `all 200ms cubic-bezier(0.4, 0, 0.2, 1)` | Easing |
| **Background** | `bg-slate-900` (dark) | Darkest navy |
| **Border-right** | `1px solid border-slate-800` | Subtle divider |
| **Icons** | Lucide React, 20x20px | Consistent sizing |
| **Active state** | `bg-teal-500/20` + `text-teal-400` | Teal highlight + text |
| **Hover state** | `bg-slate-800/50` | Subtle background |
| **Font size** | 14px (label) | Inter 500 weight |

### B) HEADER / TOP BAR

```plaintext
┌────────────────────────────────────────────────┐
│ [≡ Menu] [🔍 Search...]     [🔔] [👤] [⋮]   │  ← Height 56px
└────────────────────────────────────────────────┘
```

| Component | Width | Height | Details |
|-----------|-------|--------|---------|
| **Menu toggle** | 40px | 40px | Icon button, ripple on click |
| **Search bar** | Auto (flex-1) | 36px | border-radius 8px, bg-slate-800, focus ring cyan |
| **Notification bell** | 40px | 40px | Badge "3" for unread |
| **User menu** | 40px | 40px | Avatar + dropdown |
| **More menu** | 40px | 40px | 3-dot icon |
| **Total height** | 100% | 56px | Padding 8px vertical, 16px horizontal |

**Shadow**: `shadow-sm` (subtle elevation)  
**Background**: `bg-slate-900/50` (semi-transparent)  
**Border-bottom**: `1px solid border-slate-800`

### C) DASHBOARD CARDS (KPI)

```plaintext
┌──────────────────────┐
│ 📞 Clienti Totali    │  ← Title (14px, muted)
│                      │
│        1,234         │  ← Big number (32px, bold)
│      +12% da ieri    │  ← Trend (12px, green)
└──────────────────────┘
```

| Property | Value | Note |
|----------|-------|------|
| **Grid layout** | 2x2 (mobile) → 4x1 (desktop) | Responsive |
| **Card dimensions** | 200px W × 120px H | Flexible with gap |
| **Border-radius** | 12px | Smooth corners |
| **Background** | `bg-slate-800/50` | Glass effect |
| **Border** | `1px solid border-slate-700` | Subtle outline |
| **Shadow** | `shadow-md` (8px blur, y:4px) | Elevation |
| **Padding** | 16px | Interior spacing |
| **Hover effect** | Scale 1.02 + shadow-lg | Soft interaction |
| **Title font** | 12px, Inter 500, `text-slate-400` | Muted secondary |
| **Number font** | 32px, Inter 700, `text-white` | Bold, prominent |
| **Trend font** | 12px, Inter 500 | Green (`text-emerald-400`) or Red (`text-red-400`) |

### D) CALENDAR / BOOKING VIEW

```plaintext
┌────────────────────────────────────────┐
│ Lun  Mar  Mer  Gio  Ven  Sab  Dom     │  ← Week header
├────────────────────────────────────────┤
│ 08:00 │                                 │
│ 08:30 │ [Massaggio 60min - €50]        │  ← Appointment block
│ 09:00 │ [Massaggio 60min - €50]        │
│ 09:30 │ [Taglio + Barba - €35]         │
│ 10:00 │                                 │
│ ...                                    │
└────────────────────────────────────────┘
```

| Element | Spec | Details |
|---------|------|---------|
| **Week header** | 7 columns equal width | Mon-Sun, abbreviated |
| **Time column** | 60px width | Fixed, shows hourly labels |
| **Hour row height** | 60px | 2 rows per hour (30min granularity) |
| **Appointment block** | Min height 60px (30min) | Draggable, resizable edges |
| **Appointment colors** | Service-based gradient | Massaggio = teal, Taglio = blue, etc. |
| **Appointment card** | border-radius 6px, padding 8px | Text: service name + duration + price |
| **Hover effect** | shadow-lg + cursor-grab | Visual feedback for interactivity |
| **Drag visual** | Border 2px teal on parent | Indicates valid drop zone |
| **Status indicator** | Badge (Confermato/Pending/Cancelled) | Top-left corner |

### E) DATA TABLES

```plaintext
┌──────────────┬──────────────┬──────────────┬──────────┐
│ Nome Cliente │ Telefono     │ Email        │ Azioni   │
├──────────────┼──────────────┼──────────────┼──────────┤
│ Mario Rossi  │ 339 123 4567 │ mario@...    │ [⋮]      │
│ Anna Bianchi │ 340 234 5678 │ anna@...     │ [⋮]      │
│ (hover)      │ (bg-change)  │              │          │
└──────────────┴──────────────┴──────────────┴──────────┘
```

| Property | Value | Note |
|----------|-------|------|
| **Header background** | `bg-slate-800` | Slightly darker than rows |
| **Header font** | 12px, Inter 600, `text-slate-300` | Uppercase? No, normal case |
| **Row height** | 40px | Compact but readable |
| **Row hover** | `bg-slate-700/50` | Highlight entire row |
| **Cell padding** | 12px vertical, 16px horizontal | Breathing room |
| **Border-bottom** | `1px solid border-slate-700` | Row dividers (optional) |
| **Alternating rows** | No (keep consistent) | Cleaner look |
| **Actions column** | Icon button (3-dot menu) | Opens dropdown menu |
| **Pagination** | Bottom-right, 25/50/100 items per page | Plus "Next/Prev" buttons |
| **Filter UI** | Input field above table | Search + Select dropdowns |

### F) CHARTS / GRAPHS (Tremor + Recharts)

```plaintext
Recommended: Tremor for dashboard (simpler), Recharts for custom
```

| Chart type | Library | Color scheme | Size |
|-----------|---------|--------------|------|
| **Area chart (Revenue trend)** | Recharts | Gradient teal-to-cyan | Full width, 300px height |
| **Bar chart (Bookings by day)** | Recharts | Primary teal (#22d3ee) | Full width, 250px height |
| **Pie chart (Services breakdown)** | Recharts | Multi-color (teal, blue, purple) | 300x300px |
| **Table chart (Top clients)** | Tremor | Table format + bar indicators | 400px height |
| **KPI metric cards** | Tremor | Single number + sparkline | 150px width each |

**Colors for charts**:
- Primary: `#22d3ee` (cyan)
- Secondary: `#0891b2` (teal dark)
- Accent: `#7c3aed` (purple)
- Neutral: `#64748b` (slate)

**Tooltip**: Dark background (`bg-slate-900`), border cyan 1px, rounded 6px

### G) MODALS / DIALOGS

```plaintext
┌─────────────────────────────────┐
│ ✕ Nuova Prenotazione            │  ← Header 48px
├─────────────────────────────────┤
│                                 │
│ [Contenuto principale]          │  ← Body, padding 24px
│ [Form fields]                   │
│                                 │
├─────────────────────────────────┤
│           [Annulla] [Salva]    │  ← Footer, buttons right-aligned
└─────────────────────────────────┘
```

| Property | Value | Note |
|----------|-------|------|
| **Overlay opacity** | `bg-black/40` | Semi-transparent dark |
| **Modal width** | 480px (mobile: full - 32px) | Max 640px |
| **Modal border-radius** | 12px | Soft corners |
| **Modal shadow** | `shadow-2xl` (heavy elevation) | 25px blur |
| **Header padding** | 20px | With close button (×) top-right |
| **Body padding** | 24px | Interior spacing |
| **Footer padding** | 20px | Button spacing 8px gap |
| **Close button** | 32x32px, icon-only | Hover highlight |
| **Animation enter** | Fade-in 150ms + scale 0.95→1.0 | Smooth appearance |
| **Animation exit** | Fade-out 100ms | Quick dismiss |

### H) FORMS / INPUTS

```plaintext
┌─────────────────────────┐
│ Email Clientela         │  ← Label 12px
│ [____________@_____] ✓  │  ← Input + validation icon
│ Inserisci email valida  │  ← Helper text 11px
└─────────────────────────┘
```

| Property | Value | Note |
|----------|-------|------|
| **Input height** | 40px | Standard field |
| **Input padding** | 10px horizontal, 12px vertical | Icon clearance |
| **Label position** | Above input (not floating) | Clearer labeling |
| **Label font** | 12px, Inter 500, `text-slate-300` | Secondary color |
| **Input border-radius** | 8px | Soft corners |
| **Input border** | 1px solid border-slate-700 | Default state |
| **Input focus** | Border cyan, ring cyan/30 (3px) | Accessibility |
| **Input background** | `bg-slate-800` | Dark surface |
| **Placeholder** | `text-slate-500` | Muted text |
| **Helper text** | 11px, `text-slate-400` | Below input, error variant red |
| **Error state** | Border red-500, text red | Clear indication |
| **Disabled state** | `opacity-50`, cursor-not-allowed | Grayed out |
| **Success state** | Green checkmark icon | Right side icon |

### I) BUTTONS

| Variant | Background | Text | Border | Hover | Size |
|---------|-----------|------|--------|-------|------|
| **Primary** | `bg-teal-500` | white | none | `bg-teal-600` | 40px H |
| **Secondary** | `bg-slate-800` | `text-slate-200` | `border-slate-700` | `bg-slate-700` | 40px H |
| **Ghost** | transparent | `text-slate-300` | `border-slate-600` | `bg-slate-800/50` | 40px H |
| **Destructive** | `bg-red-600` | white | none | `bg-red-700` | 40px H |

**Padding**: 12px horizontal, 8px vertical (40px total height)  
**Border-radius**: 8px  
**Font**: 14px, Inter 500  
**Icon + text**: 8px gap  
**Loading state**: Spinner icon, disabled  
**Focus**: Ring 2px offset 2px cyan

### L) VOICE AGENT UI

```plaintext
┌─────────────────────┐
│  🎤 Assistente      │  ← Floating button
│   (pulsing)         │
└─────────────────────┘

[Modal on click]
┌─────────────────────┐
│ Assistente Vocale   │
├─────────────────────┤
│ 🎤 Ascoltando...    │  ← Waveform animation
│ ~~~~~ ~~~~~ ~~~~~   │
├─────────────────────┤
│ "Prenotazione per…" │  ← Transcription
├─────────────────────┤
│ ✅ Conferma         │
│ ❌ Annulla          │
└─────────────────────┘
```

| Element | Spec | Details |
|---------|------|---------|
| **Floating button** | 56x56px | Fixed bottom-right, z-100 |
| **Button color** | Gradient teal-to-cyan | Pulsing animation opacity 0.7→1.0 |
| **Button icon** | Microphone, 28px | Lucide React |
| **Waveform animation** | 5 bars, 2-20px height | Sync with audio input |
| **Waveform colors** | Cyan gradient | Color intensity by frequency |
| **Modal background** | `bg-slate-900/95` | High opacity |
| **Transcription text** | 14px, `text-slate-100` | Scrollable if long |
| **Status badge** | Green/Red indicator | "Ascoltando" / "Errore" |

---

## FASE 3: DESIGN TOKENS COMPLETI

### 📐 CSS VARIABLES (Tailwind + Custom)

```css
/* File: src/styles/globals.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* ===== COLORS - LIGHT MODE (fallback) ===== */
  --background: hsl(217, 32%, 17%);           /* #1e293b slate-900 */
  --foreground: hsl(210, 40%, 96%);           /* #f1f5f9 slate-50 */

  --card: hsl(217, 32%, 24%);                 /* #0f172a slate-900-dark */
  --card-foreground: hsl(210, 40%, 96%);      /* #f1f5f9 */

  --primary: hsl(189, 100%, 56%);             /* #22d3ee cyan-400 */
  --primary-foreground: hsl(217, 32%, 17%);   /* #1e293b navy */

  --secondary: hsl(200, 100%, 43%);           /* #0891b2 teal-600 */
  --secondary-foreground: hsl(0, 0%, 100%);   /* #ffffff */

  --accent: hsl(280, 85%, 65%);               /* #c084fc purple-400 */
  --accent-foreground: hsl(217, 32%, 17%);    /* #1e293b */

  --muted: hsl(216, 14%, 42%);                /* #64748b slate-500 */
  --muted-foreground: hsl(210, 40%, 96%);     /* #f1f5f9 */

  --destructive: hsl(0, 84%, 60%);            /* #ef4444 red-500 */
  --destructive-foreground: hsl(210, 40%, 98%); /* #fafafa */

  --border: hsl(217, 32%, 30%);               /* #334155 slate-700 */
  --input: hsl(217, 32%, 30%);                /* #334155 slate-700 */
  --ring: hsl(189, 100%, 56%);                /* #22d3ee cyan (focus) */

  /* ===== GRADIENTS ===== */
  --gradient-teal-cyan: linear-gradient(135deg, #0891b2 0%, #22d3ee 100%);
  --gradient-slate-navy: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);

  /* ===== SHADOWS ===== */
  --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.2), 0 4px 6px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.05);

  /* ===== ANIMATIONS ===== */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 350ms;
  --ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
}

/* Dark mode (system preference or explicit) */
@media (prefers-color-scheme: dark) {
  :root {
    --background: hsl(217, 32%, 17%);         /* #1e293b */
    --foreground: hsl(210, 40%, 96%);         /* #f1f5f9 */
    /* ... altri valori identici (già dark) ... */
  }
}

/* Tailwind config integration */
@layer base {
  * {
    @apply border-border;
  }

  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rounding-mode" 0;
  }
}

/* Custom component styles */
@layer components {
  /* Glassmorphism effect */
  .glass {
    @apply bg-white/10 backdrop-blur-20 border border-white/20 rounded-lg;
  }

  /* Elevation cards */
  .card-elevated {
    @apply bg-card rounded-lg border border-border shadow-md;
  }

  /* Focus ring (cyan) */
  .focus-ring {
    @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background;
  }

  /* Smooth transitions */
  .transition-smooth {
    @apply transition-all duration-250 ease-standard;
  }
}
```

### 🎨 TAILWIND THEME CONFIG

```js
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: 'hsl(var(--card))',
        'card-foreground': 'hsl(var(--card-foreground))',
        primary: 'hsl(var(--primary))',
        'primary-foreground': 'hsl(var(--primary-foreground))',
        secondary: 'hsl(var(--secondary))',
        'secondary-foreground': 'hsl(var(--secondary-foreground))',
        accent: 'hsl(var(--accent))',
        'accent-foreground': 'hsl(var(--accent-foreground))',
        muted: 'hsl(var(--muted))',
        'muted-foreground': 'hsl(var(--muted-foreground))',
        destructive: 'hsl(var(--destructive))',
        'destructive-foreground': 'hsl(var(--destructive-foreground))',
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
      },
      borderRadius: {
        xs: '4px',
        sm: '6px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '20px',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px',
        '2xl': '24px',
        '3xl': '32px',
      },
      fontSize: {
        xs: ['11px', { lineHeight: '16px', letterSpacing: '0.5px' }],
        sm: ['12px', { lineHeight: '16px' }],
        base: ['14px', { lineHeight: '20px' }],
        lg: ['16px', { lineHeight: '24px' }],
        xl: ['18px', { lineHeight: '28px' }],
        '2xl': ['20px', { lineHeight: '28px' }],
        '3xl': ['24px', { lineHeight: '32px' }],
        '4xl': ['32px', { lineHeight: '40px' }],
      },
      fontWeight: {
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },
      boxShadow: {
        xs: 'var(--shadow-xs)',
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
      },
      animation: {
        'fade-in': 'fadeIn var(--duration-normal) var(--ease-out)',
        'slide-up': 'slideUp var(--duration-normal) var(--ease-out)',
        'scale-in': 'scaleIn var(--duration-normal) var(--ease-out)',
        'pulse-soft': 'pulseSoft 2s var(--ease-standard) infinite',
      },
      keyframes: {
        fadeIn: {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        slideUp: {
          'from': { transform: 'translateY(10px)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          'from': { transform: 'scale(0.95)', opacity: '0' },
          'to': { transform: 'scale(1)', opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
```

### 📝 TYPOGRAPHY SCALE

| Size | Value | Line Height | Weight | Use case |
|------|-------|-------------|--------|----------|
| **xs** | 11px | 16px | 400/500 | Labels, badges, helper text |
| **sm** | 12px | 16px | 400/500 | Form labels, secondary text |
| **base** | 14px | 20px | 400/500 | Body text, table cells |
| **lg** | 16px | 24px | 400/500 | Form inputs, card headers |
| **xl** | 18px | 28px | 500/600 | Section titles |
| **2xl** | 20px | 28px | 600 | Page titles |
| **3xl** | 24px | 32px | 600 | Dashboard main title |
| **4xl** | 32px | 40px | 700 | KPI numbers |

**Font family**: `Inter` (Tailwind default) or `Geist` for modern look

### 🎯 SPACING SCALE

Base unit: **4px** (Tailwind default)

- **xs**: 4px
- **sm**: 8px
- **md**: 12px
- **lg**: 16px
- **xl**: 20px
- **2xl**: 24px
- **3xl**: 32px

**Component padding**:
- Buttons: 8px vertical, 12px horizontal
- Card body: 16px
- Modal body: 24px
- Section padding: 32px

---

## FASE 4: REACT MOCKUP COMPONENT

### File Structure
```
src/
├── components/
│   ├── Sidebar.tsx
│   ├── Header.tsx
│   ├── Dashboard.tsx
│   ├── KPICard.tsx
│   ├── AppointmentsList.tsx
│   ├── VoiceAgent.tsx
│   └── WeekCalendar.tsx
├── styles/
│   └── globals.css (token definitions)
├── hooks/
│   └── useMediaQuery.ts
├── App.tsx
└── main.tsx
```

### Complete Component Code

```tsx
// src/App.tsx
import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import VoiceAgent from './components/VoiceAgent'

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        {/* Dashboard */}
        <main className="flex-1 overflow-auto p-lg">
          <Dashboard />
        </main>
      </div>

      {/* Voice Agent Floating Button */}
      <VoiceAgent />
    </div>
  )
}
```

```tsx
// src/components/Sidebar.tsx
import React from 'react'
import {
  Home,
  Calendar,
  Users,
  Wrench,
  BarChart3,
  Settings,
  Menu,
  ChevronUp,
} from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const navItems = [
    { icon: Home, label: 'Home', href: '#' },
    { icon: Calendar, label: 'Calendario', href: '#' },
    { icon: Users, label: 'Clienti', href: '#' },
    { icon: Wrench, label: 'Servizi', href: '#' },
    { icon: BarChart3, label: 'Analytics', href: '#' },
    { icon: Settings, label: 'Impostazioni', href: '#' },
  ]

  return (
    <aside
      className={`
        transition-smooth
        ${isOpen ? 'w-60' : 'w-16'}
        bg-slate-900 border-r border-border
        flex flex-col h-screen
        fixed md:relative z-40
      `}
    >
      {/* Logo */}
      <div className="h-16 border-b border-border flex items-center justify-center px-lg">
        <div className="flex items-center gap-md">
          <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-cyan-400 rounded-lg flex items-center justify-center">
            <span className="text-sm font-bold text-white">F</span>
          </div>
          {isOpen && <span className="font-semibold text-white">Fluxion</span>}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-sm py-lg space-y-sm overflow-y-auto">
        {navItems.map((item) => (
          <a
            key={item.label}
            href={item.href}
            className={`
              flex items-center gap-md px-md py-sm rounded-md
              transition-smooth
              hover:bg-slate-800/50
              group
              ${item.label === 'Calendario' ? 'bg-teal-500/20 text-teal-400' : 'text-slate-300'}
            `}
            title={!isOpen ? item.label : undefined}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {isOpen && <span className="text-sm font-medium">{item.label}</span>}
          </a>
        ))}
      </nav>

      {/* User Profile */}
      <div className="border-t border-border px-sm py-lg">
        <div className={`flex items-center ${isOpen ? 'gap-md' : 'justify-center'}`}>
          <img
            src="https://api.dicebear.com/7.x/avataaars/svg?seed=Mario"
            alt="User"
            className="w-10 h-10 rounded-full flex-shrink-0"
          />
          {isOpen && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">Mario Rossi</p>
              <p className="text-xs text-slate-400 truncate">mario@salon.it</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
```

```tsx
// src/components/Header.tsx
import React from 'react'
import { Menu, Search, Bell, User, MoreVertical } from 'lucide-react'

interface HeaderProps {
  onMenuClick: () => void
}

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="h-14 bg-slate-900/50 border-b border-border px-lg py-sm flex items-center justify-between gap-lg">
      {/* Menu toggle + Search */}
      <div className="flex items-center gap-md flex-1">
        <button
          onClick={onMenuClick}
          className="p-sm hover:bg-slate-800 rounded-md transition-smooth"
          title="Toggle sidebar"
        >
          <Menu className="w-5 h-5 text-slate-300" />
        </button>

        <div className="flex-1 max-w-sm">
          <div className="relative">
            <Search className="absolute left-md top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Cerca clienti, servizi..."
              className="w-full pl-10 pr-md py-sm bg-slate-800 text-sm rounded-md
                border border-border
                focus-ring
                placeholder:text-slate-500 transition-smooth"
            />
          </div>
        </div>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-md">
        {/* Notifications */}
        <button className="p-sm hover:bg-slate-800 rounded-md transition-smooth relative">
          <Bell className="w-5 h-5 text-slate-300" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* User menu */}
        <button className="p-sm hover:bg-slate-800 rounded-md transition-smooth">
          <User className="w-5 h-5 text-slate-300" />
        </button>

        {/* More menu */}
        <button className="p-sm hover:bg-slate-800 rounded-md transition-smooth">
          <MoreVertical className="w-5 h-5 text-slate-300" />
        </button>
      </div>
    </header>
  )
}
```

```tsx
// src/components/KPICard.tsx
import React from 'react'
import { TrendingUp, TrendingDown, Zap } from 'lucide-react'

interface KPICardProps {
  icon: React.ReactNode
  title: string
  value: string | number
  trend: number
  unit?: string
}

export default function KPICard({ icon, title, value, trend, unit = '' }: KPICardProps) {
  const isPositive = trend >= 0

  return (
    <div className="bg-card border border-border rounded-lg p-lg shadow-md hover:shadow-lg transition-smooth hover:scale-102">
      <div className="flex items-start justify-between mb-md">
        <span className="text-xs font-medium text-muted uppercase">{title}</span>
        <div className="text-teal-400 opacity-70">{icon}</div>
      </div>

      <div className="mb-md">
        <div className="text-3xl font-bold text-white">
          {value}
          {unit && <span className="text-lg text-slate-400">{unit}</span>}
        </div>
      </div>

      <div className="flex items-center gap-sm">
        {isPositive ? (
          <TrendingUp className="w-4 h-4 text-emerald-400" />
        ) : (
          <TrendingDown className="w-4 h-4 text-red-400" />
        )}
        <span className={`text-xs font-medium ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
          {trend > 0 ? '+' : ''}{trend}% da ieri
        </span>
      </div>
    </div>
  )
}
```

```tsx
// src/components/Dashboard.tsx
import React from 'react'
import { Users, Phone, DollarSign, Calendar, Clock, AlertCircle } from 'lucide-react'
import KPICard from './KPICard'
import AppointmentsList from './AppointmentsList'
import WeekCalendar from './WeekCalendar'

export default function Dashboard() {
  return (
    <div className="space-y-2xl">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-sm">Benvenuto, Mario</h1>
        <p className="text-slate-400">Domenica, 28 Dicembre 2025</p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-lg">
        <KPICard
          icon={<Phone className="w-5 h-5" />}
          title="Clienti Totali"
          value="1,234"
          trend={12}
        />
        <KPICard
          icon={<Calendar className="w-5 h-5" />}
          title="Prenotazioni Oggi"
          value="8"
          trend={5}
        />
        <KPICard
          icon={<DollarSign className="w-5 h-5" />}
          title="Revenue Mese"
          value="€8,450"
          trend={18}
          unit="€"
        />
        <KPICard
          icon={<Users className="w-5 h-5" />}
          title="Staff Online"
          value="5"
          trend={0}
        />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-lg">
        {/* Left: Week Calendar (2/3 width) */}
        <div className="lg:col-span-2">
          <div className="bg-card border border-border rounded-lg p-lg">
            <h2 className="text-lg font-semibold text-white mb-lg">Prenotazioni Oggi</h2>
            <WeekCalendar />
          </div>
        </div>

        {/* Right: Appointments + Quick Actions (1/3 width) */}
        <div className="space-y-lg">
          {/* Appointments List */}
          <div className="bg-card border border-border rounded-lg p-lg">
            <h3 className="text-base font-semibold text-white mb-lg">Prossimi Appuntamenti</h3>
            <AppointmentsList />
          </div>

          {/* Quick Actions */}
          <div className="bg-card border border-border rounded-lg p-lg">
            <h3 className="text-base font-semibold text-white mb-lg">Azioni Rapide</h3>
            <div className="space-y-sm">
              <button className="w-full bg-teal-500 hover:bg-teal-600 transition-smooth text-white font-medium py-sm px-md rounded-md flex items-center justify-center gap-sm">
                <Calendar className="w-4 h-4" />
                Nuova Prenotazione
              </button>
              <button className="w-full bg-slate-800 hover:bg-slate-700 transition-smooth text-slate-200 font-medium py-sm px-md rounded-md flex items-center justify-center gap-sm">
                <Users className="w-4 h-4" />
                Nuovo Cliente
              </button>
              <button className="w-full bg-slate-800 hover:bg-slate-700 transition-smooth text-slate-200 font-medium py-sm px-md rounded-md flex items-center justify-center gap-sm">
                <AlertCircle className="w-4 h-4" />
                Segnalazioni
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

```tsx
// src/components/AppointmentsList.tsx
import React from 'react'
import { Clock, User, Zap } from 'lucide-react'

export default function AppointmentsList() {
  const appointments = [
    {
      id: 1,
      client: 'Marco Bianchi',
      service: 'Massaggio',
      time: '14:30',
      status: 'Confermato',
      price: '€50',
    },
    {
      id: 2,
      client: 'Sofia Rossi',
      service: 'Taglio + Barba',
      time: '15:30',
      status: 'Pending',
      price: '€35',
    },
    {
      id: 3,
      client: 'Anna Verdi',
      service: 'Manicure',
      time: '16:00',
      status: 'Confermato',
      price: '€25',
    },
  ]

  return (
    <div className="space-y-sm">
      {appointments.map((apt) => (
        <div
          key={apt.id}
          className="p-md bg-slate-800/50 rounded-md border border-slate-700/50 hover:border-teal-500/30 transition-smooth"
        >
          <div className="flex items-start justify-between mb-sm">
            <div className="flex items-start gap-sm flex-1">
              <User className="w-4 h-4 text-teal-400 mt-px flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-sm font-medium text-white truncate">{apt.client}</p>
                <p className="text-xs text-slate-400">{apt.service}</p>
              </div>
            </div>
            <span className="text-xs font-semibold text-slate-300">{apt.price}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-sm">
              <Clock className="w-3 h-3 text-slate-500" />
              <span className="text-xs text-slate-400">{apt.time}</span>
            </div>
            <span className={`text-xs font-medium px-sm py-xs rounded ${
              apt.status === 'Confermato' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-400'
            }`}>
              {apt.status}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
```

```tsx
// src/components/WeekCalendar.tsx
import React from 'react'

export default function WeekCalendar() {
  const hours = Array.from({ length: 10 }, (_, i) => 8 + i)
  const days = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom']

  // Mock appointments
  const appointments = [
    { day: 0, hour: 10, duration: 1, service: 'Massaggio 60min', price: '€50', client: 'Marco' },
    { day: 2, hour: 9, duration: 0.5, service: 'Taglio', price: '€25', client: 'Sofia' },
    { day: 3, hour: 14, duration: 1, service: 'Manicure + Pedi', price: '€60', client: 'Anna' },
  ]

  return (
    <div className="overflow-x-auto">
      <div className="inline-block min-w-full">
        {/* Header */}
        <div className="flex mb-md border-b border-slate-700">
          <div className="w-16 flex-shrink-0" />
          {days.map((day) => (
            <div key={day} className="flex-1 text-center py-sm">
              <p className="text-xs font-semibold text-slate-300">{day}</p>
              <p className="text-xs text-slate-500">28</p>
            </div>
          ))}
        </div>

        {/* Time grid */}
        <div className="space-y-px">
          {hours.map((hour) => (
            <div key={hour} className="flex h-16">
              {/* Time label */}
              <div className="w-16 flex-shrink-0 px-sm text-xs text-slate-500 py-sm">
                {String(hour).padStart(2, '0')}:00
              </div>

              {/* Day cells */}
              {days.map((_, dayIndex) => {
                const apt = appointments.find((a) => a.day === dayIndex && a.hour === hour)
                return (
                  <div
                    key={`${hour}-${dayIndex}`}
                    className="flex-1 border border-slate-700/30 hover:border-teal-500/30 p-xs transition-smooth relative bg-slate-800/20"
                  >
                    {apt && (
                      <div
                        className="bg-gradient-to-r from-teal-500 to-cyan-400 rounded-md p-xs text-xs text-white font-medium shadow-md hover:shadow-lg transition-smooth cursor-grab active:cursor-grabbing"
                        style={{
                          minHeight: `${apt.duration * 64 - 4}px`,
                        }}
                      >
                        <div className="truncate">{apt.service}</div>
                        <div className="text-xs opacity-80 truncate">{apt.client}</div>
                        <div className="text-xs opacity-70">{apt.price}</div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

```tsx
// src/components/VoiceAgent.tsx
import React, { useState } from 'react'
import { Mic, X, RotateCcw } from 'lucide-react'

export default function VoiceAgent() {
  const [isOpen, setIsOpen] = useState(false)
  const [isListening, setIsListening] = useState(false)

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`
          fixed bottom-6 right-6 z-50
          w-14 h-14 rounded-full
          bg-gradient-to-br from-teal-500 to-cyan-400
          hover:shadow-lg transition-smooth
          flex items-center justify-center
          ${isOpen ? 'hidden' : ''}
          animate-pulse-soft
        `}
        title="Apri assistente vocale"
      >
        <Mic className="w-6 h-6 text-white" />
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-lg">
          <div className="bg-card border border-border rounded-lg w-full max-w-sm shadow-xl animate-scale-in">
            {/* Header */}
            <div className="px-lg py-md border-b border-border flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Assistente Vocale Fluxion</h2>
              <button
                onClick={() => {
                  setIsOpen(false)
                  setIsListening(false)
                }}
                className="p-sm hover:bg-slate-800 rounded-md transition-smooth"
              >
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>

            {/* Body */}
            <div className="px-lg py-xl">
              <div className="text-center space-y-xl">
                {/* Waveform animation */}
                <div className="flex items-center justify-center gap-sm h-16">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className="w-1 bg-gradient-to-t from-teal-500 to-cyan-400 rounded-full transition-all"
                      style={{
                        height: isListening ? `${20 + Math.random() * 40}px` : '8px',
                        animation: isListening ? `pulse 0.4s ease-in-out ${i * 0.1}s infinite` : 'none',
                      }}
                    />
                  ))}
                </div>

                {/* Status text */}
                <div>
                  <p className="text-base font-medium text-white mb-sm">
                    {isListening ? '🎤 Ascoltando...' : 'Pronto per ascoltare'}
                  </p>
                  <p className="text-sm text-slate-400">
                    {isListening
                      ? 'Parla pure, ti ascolto'
                      : 'Clicca il microfono per iniziare'}
                  </p>
                </div>

                {/* Transcription */}
                {isListening && (
                  <div className="bg-slate-800/50 rounded-md p-md text-sm text-slate-300 text-left max-h-20 overflow-y-auto">
                    "Voglio prenotare un massaggio per domani alle tre del pomeriggio"
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="px-lg py-md border-t border-border flex gap-md">
              <button
                onClick={() => setIsListening(!isListening)}
                className={`flex-1 py-sm px-md rounded-md font-medium transition-smooth flex items-center justify-center gap-sm ${
                  isListening
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-teal-500 hover:bg-teal-600 text-white'
                }`}
              >
                {isListening ? (
                  <>
                    <X className="w-4 h-4" />
                    Ferma
                  </>
                ) : (
                  <>
                    <Mic className="w-4 h-4" />
                    Registra
                  </>
                )}
              </button>
              <button
                onClick={() => setIsListening(false)}
                className="flex-1 py-sm px-md rounded-md font-medium transition-smooth bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center justify-center gap-sm"
              >
                <RotateCcw className="w-4 h-4" />
                Ripeti
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
```

---

## FASE 5: NOTE DI IMPLEMENTAZIONE PER CLAUDE CODE

### Setup Iniziale

```bash
# Create Tauri project with React template
npm create tauri-app@latest fluxion -- --template react --typescript

# Install dependencies
npm install
npm install -D tailwindcss postcss autoprefixer
npm install lucide-react

# Initialize Tailwind
npx tailwindcss init -p
```

### Tailwind Configuration
1. Copy the `tailwind.config.ts` provided above
2. Copy the `globals.css` with design tokens
3. Import `globals.css` in `main.tsx`

### Component Integration
1. Paste each component file in `src/components/`
2. Replace mock data with real API calls
3. Add state management (Zustand / Jotai recommended)
4. Integrate with backend

### Key Features to Add
- [ ] Appointment booking calendar with drag-drop (React-Big-Calendar + React DnD)
- [ ] Customer management table with filtering/search
- [ ] Revenue charts (Recharts or Tremor)
- [ ] User authentication (Tauri native or Clerk)
- [ ] WhatsApp integration for notifications
- [ ] Voice agent integration (Deepgram + OpenAI Whisper)
- [ ] PDF invoice export
- [ ] Dark/Light mode toggle

### Performance Optimizations
- Lazy load routes with `React.lazy()` + `Suspense`
- Memoize components with `React.memo()` where needed
- Use `useCallback` for event handlers
- Implement virtual scrolling for large lists (react-window)

### Testing
- Unit tests: Vitest + React Testing Library
- E2E tests: Tauri test commands

---

## PALETTE DI RIFERIMENTO FINAL (CSS HEX)

Basata su Fluxion brand + research:

| Color | Hex | Use Case |
|-------|-----|----------|
| **Navy** | #1E293B | Background, sidebar |
| **Navy Dark** | #0F172A | Card backgrounds |
| **Slate 700** | #334155 | Borders |
| **Slate 500** | #64748B | Muted text |
| **Slate 400** | #94A3B8 | Secondary text |
| **Slate 300** | #CBD5E1 | Primary text |
| **White** | #F1F5F9 | Foreground |
| **Cyan** | #22D3EE | Primary action |
| **Teal** | #0891B2 | Secondary action |
| **Purple** | #C084FC | Accent |
| **Emerald** | #10B981 | Success |
| **Red** | #EF4444 | Destructive |

---

## CONCLUSIONE

Questo è il **FLUXION DESIGN BIBLE v1.0**:
- ✅ 5 reference visive + link diretti
- ✅ Design tokens completi (CSS, Tailwind, spacing, typography)
- ✅ React mockup production-ready
- ✅ Pattern extraction per ogni componente
- ✅ Note implementazione per Claude Code

**Pronto per essere usato come reference durante lo sviluppo.**

Domanda finale: **Vuoi che generi anche il boilerplate Tauri + React pronto all'uso, o preferisci il setup manuale?**
