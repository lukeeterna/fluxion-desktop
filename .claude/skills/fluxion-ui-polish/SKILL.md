# Skill: FLUXION UI Polish — Enterprise Grade

## Descrizione
Skill enterprise per UI/UX polish del gestionale FLUXION. Design system dark theme, bento box layout, micro-animazioni, colori semantici, glassmorphism. Produce output a livello Fresha/Linear/Notion.

## Trigger
Questa skill si attiva quando:
- L'utente chiede "polish UI", "migliora estetica", "rendi più bello"
- L'utente chiede "bento box", "micro-animazioni", "glassmorphism"
- L'utente chiede "design system", "colori semantici"
- Viene identificato un gap UI/UX nell'audit
- Si devono rifare screenshot per materiale marketing

## Stack Tecnico
- **Framework**: React 19 + TypeScript strict (zero `any`)
- **Styling**: Tailwind CSS 3.x (utility-first, dark theme)
- **Components**: shadcn/ui (Radix primitives)
- **Animations**: CSS transitions + `transition-all` (NO framer-motion — bundle size)
- **Icons**: Lucide React
- **Theme**: Dark (bg-slate-950 → bg-slate-900 → bg-slate-800)

## Design System FLUXION — Tokens Definitivi

### Color Palette (Dark Theme)
```
Background:
  page:     bg-slate-950        (#0b0f1a)
  card:     bg-slate-900        (#0f172a)
  elevated: bg-slate-800/50     (con backdrop-blur)
  hover:    bg-slate-800/70

Text:
  primary:   text-white
  secondary: text-slate-400
  muted:     text-slate-500
  disabled:  text-slate-600

Semantic:
  success:   text-emerald-400 / bg-emerald-500/15 / border-emerald-500/30
  warning:   text-amber-400   / bg-amber-500/15   / border-amber-500/30
  danger:    text-red-400     / bg-red-500/15     / border-red-500/30
  info:      text-cyan-400    / bg-cyan-500/15    / border-cyan-500/30

Accent per Verticale:
  parrucchiere: purple-500
  veicoli:      blue-500
  odontoiatrica: red-500
  estetica:     pink-500
  fitness:      green-500
  carrozzeria:  indigo-500
```

### Spacing System (8px grid)
```
xs:  space-y-1  (4px)
sm:  space-y-2  (8px)
md:  space-y-4  (16px)
lg:  space-y-6  (24px)
xl:  space-y-8  (32px)

Card padding: p-5 (20px) — standard
Section gap:  gap-4 (16px) — tra card
Page gap:     space-y-6 (24px) — tra sezioni
```

### Border Radius
```
button:  rounded-lg    (8px)
card:    rounded-xl    (12px)
wrapper: rounded-2xl   (16px)
badge:   rounded-full  (pill)
```

### Shadows (Dark Theme)
```
card:     shadow-lg shadow-black/20
elevated: shadow-xl shadow-black/30
float:    shadow-2xl shadow-black/40
glow:     shadow-lg shadow-[accent]/10  (es. shadow-cyan-500/10)
```

### Typography
```
h1:       text-3xl font-bold text-white
h2:       text-lg font-semibold text-white
h3:       text-sm font-medium text-slate-300
body:     text-sm text-slate-400
caption:  text-xs text-slate-500
mono:     font-mono text-sm
```

## Pattern UI Obbligatori

### 1. Bento Box Layout
```tsx
// Grid asimmetrico — card di dimensioni diverse per gerarchia visiva
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  <div className="lg:col-span-2">  {/* Card larga */}
  <div>                             {/* Card standard */}
  <div>                             {/* Card standard */}
</div>
```

### 2. Glassmorphism Header (SchedaWrapper)
```tsx
// Già implementato — pattern gold standard
<div className="relative overflow-hidden bg-gradient-to-br from-[accent]-950/60 via-slate-900 to-slate-900 border-b border-[accent]-500/10 px-6 py-5">
  {/* Ambient blur circles */}
  <div className="absolute -top-10 -right-10 w-48 h-48 bg-[accent]-500/8 rounded-full blur-3xl" />
</div>
```

### 3. Section Cards (dentro tab content)
```tsx
// Ogni gruppo di campi in una card con titolo
<div className="bg-slate-800/30 rounded-xl border border-slate-700/50 p-5">
  <h3 className="text-sm font-medium text-slate-300 flex items-center gap-2 mb-4">
    <Icon className="w-4 h-4 text-[accent]-400" />
    Titolo Sezione
  </h3>
  {/* Contenuto */}
</div>
```

### 4. Pill Toggle (selezione opzioni)
```tsx
// Sostituisce checkbox e select per opzioni limitate (<8)
<button className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
  active
    ? 'bg-[accent]-500/20 text-[accent]-300 border-[accent]-500/30 border'
    : 'bg-slate-800 text-slate-400 border-slate-700 border hover:bg-slate-700'
}`}>
```

### 5. Micro-Animazioni
```tsx
// Hover su card
className="transition-all duration-200 hover:bg-slate-800/70 hover:border-slate-600 hover:shadow-lg"

// Tab switch — NO animazione pesante, solo opacity+slide
className="transition-colors duration-150"

// Loading skeleton
className="animate-pulse bg-slate-800 rounded"

// Hover su bottone
className="transition-colors duration-150 hover:bg-[accent]-500"
```

### 6. Empty State
```tsx
<div className="text-center py-12">
  <div className="mx-auto w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-3">
    <Icon className="w-6 h-6 text-slate-600" />
  </div>
  <p className="text-sm text-slate-500 mb-1">Nessun elemento</p>
  <p className="text-xs text-slate-600">Aggiungi il primo cliccando il bottone sopra</p>
</div>
```

### 7. Stat Card (Dashboard)
```tsx
// Card con gradient sottile + icona + valore grande
<div className="p-5 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800/70 transition-colors">
  <div className="flex items-start justify-between">
    <div>
      <p className="text-sm text-slate-400 mb-1">Titolo</p>
      <p className="text-3xl font-bold text-[color]-400">Valore</p>
      <p className="text-xs text-slate-500 mt-1">Sottotitolo</p>
    </div>
    <div className="p-2.5 rounded-xl bg-[color]-500/10 border border-[color]-500/20">
      <Icon className="h-5 w-5 text-[color]-400" />
    </div>
  </div>
</div>
```

### 8. List Item Row
```tsx
<div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-700/50 hover:bg-slate-800/50 transition-colors">
  <div className="flex items-center gap-3">
    <StatusIcon />
    <div>
      <p className="text-sm font-medium text-white">Nome</p>
      <p className="text-xs text-slate-400">Dettaglio</p>
    </div>
  </div>
  <span className="text-sm text-slate-300">Valore</span>
</div>
```

## Procedura Automatica (NON NEGOZIABILE)

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Audit Componente                                │
│ Leggi il componente target. Identifica:                │
│ - Classi Tailwind non conformi al design system        │
│ - Mancanza di section cards                            │
│ - Checkbox/select da convertire in pill toggle          │
│ - Empty state mancanti                                  │
│ - Micro-animazioni assenti (hover, transition)          │
│ - Spacing non allineato a 8px grid                     │
│ Se 0 gap → STOP, componente già conforme               │
├─────────────────────────────────────────────────────────┤
│ STEP 2: Implementa Fix                                  │
│ Per ogni gap identificato:                             │
│ - Applica token dal design system sopra                │
│ - Usa Edit tool (mai riscrivere file interi)           │
│ - Mantieni logica e props invariati                    │
│ - Solo styling/layout changes                          │
├─────────────────────────────────────────────────────────┤
│ STEP 3: Verifica                                        │
│ npm run type-check → 0 errori                          │
│ Confronto visivo: before screenshot vs after            │
│ Checklist: spacing, colors, animations, empty states   │
├─────────────────────────────────────────────────────────┤
│ STEP 4: Report                                          │
│ "✅ Polish completato: N fix applicati"                │
│ Lista cambiamenti con before/after classes             │
└─────────────────────────────────────────────────────────┘
```

## Anti-Pattern — MAI FARE
- ❌ framer-motion (bundle bloat 30KB+)
- ❌ CSS-in-JS (styled-components, emotion)
- ❌ Animazioni >300ms (disturbano workflow PMI)
- ❌ Gradients troppo vivaci (restare sobri, dark theme)
- ❌ Font custom (sistema operativo = performance migliore)
- ❌ Opacity <0.05 su blur circles (invisibili = inutili)
- ❌ Box shadow colorati troppo intensi (max /10 o /15)
- ❌ Nested glassmorphism (un solo livello)
- ❌ Border-radius misti nello stesso contesto
- ❌ `any` TypeScript, `@ts-ignore`, `console.log`

## Componenti Condivisi Esistenti
- `SchedaWrapper` — glassmorphism header + stat chips + alerts + save button
- `SchedaTabs` — tab list con badge count + alert dot
- `StatChip` — pill con icona + label + valore
- `Card` (shadcn/ui) — base card component

## File Correlati
- Design system tokens: questo file
- Research: `.claude/cache/agents/ui-crm-pmi-bestpractice-cove2026.md`
- Research: `.claude/cache/agents/ui-competitor-analysis-cove2026.md`
- Gold standard: `src/components/schede-cliente/SchedaParrucchiere.tsx` (in SchedaClienteDynamic)
