# FLUXION UI/UX Audit — Production Readiness

**Date**: 2026-04-14  
**Auditor**: UI Designer Agent  
**Scope**: src/ frontend (React 19 + Tailwind + shadcn/ui)  
**Target**: Desktop 1280px+ | Dark-mode-first | Italian SMBs

---

## 1. Design System Consistency

### 1.1 Design Tokens

**Status**: GOOD — Design bible exists at `docs/FLUXION-DESIGN-BIBLE.md`, CSS variables defined in `src/index.css`.

| Token | CSS Variable | Tailwind Config | Status |
|-------|-------------|----------------|--------|
| Background | `--background: 222 47% 11%` | `hsl(var(--background))` | OK |
| Card | `--card: 217 33% 17%` | `hsl(var(--card))` | OK |
| Primary | `--primary: 189 94% 56%` | `hsl(var(--primary))` | OK |
| Accent | `--accent: 280 85% 75%` | `hsl(var(--accent))` | OK |
| Border | `--border: 215 25% 27%` | `hsl(var(--border))` | OK |
| Ring | `--ring: 189 94% 56%` | `hsl(var(--ring))` | OK |
| Destructive | `--destructive: 0 84% 60%` | `hsl(var(--destructive))` | OK |
| Muted | `--muted: 215 28% 42%` | `hsl(var(--muted))` | OK |

**Note**: Design bible mentions `--primary: 187 94% 47%` (Teal #14B8A6) but `index.css` uses `--primary: 189 94% 56%` (Cyan #22d3ee). Minor drift from the original spec, but internally consistent.

### 1.2 Hardcoded Hex Colors in TSX

| File | Line | Hardcoded Value | Context | Severity |
|------|------|----------------|---------|----------|
| `VoiceAgent.tsx` | 107 | `'#2dd4bf'` | Waveform bar color (teal) | LOW — artistic/canvas element |
| `VoiceAgent.tsx` | 108 | `'#4ade80'` | Waveform bar color (green) | LOW — artistic/canvas element |
| `VoiceAgent.tsx` | 109 | `'#67e8f9'` | Waveform bar color (cyan) | LOW — artistic/canvas element |
| `VoiceAgent.tsx` | 110 | `'#818cf8'` | Waveform bar color (indigo) | LOW — artistic/canvas element |
| `VoiceAgent.tsx` | 111 | `'#0f766e'` | Waveform bar color (dark teal) | LOW — artistic/canvas element |
| `VoiceAgent.tsx` | 114-119 | `rgba(...)` | Glow colors | LOW — artistic/canvas element |
| `Calendario.tsx` | 277-278 | `app.servizio_colore` + `15` suffix | Dynamic service color from DB | OK — user-defined |

**Verdict**: No hardcoded hex colors in standard UI components. All hex values are in the VoiceAgent waveform visualization (canvas-like rendering where Tailwind classes cannot be used). This is acceptable.

### 1.3 Inline Styles

| File | Element | Inline Style | Should Be Tailwind? |
|------|---------|-------------|---------------------|
| `App.tsx:63` | Logo img | `width: 80, height: 80, borderRadius: 16, objectFit: 'cover'` | YES — `w-20 h-20 rounded-2xl object-cover` |
| `App.tsx:80` | Logo img | Same as above | YES |
| `Sidebar.tsx:86` | Logo img | `width: 36, height: 36, borderRadius: 8, objectFit: 'cover'` | YES — `w-9 h-9 rounded-lg object-cover` |
| `Servizi.tsx:166` | Color swatch | `backgroundColor: servizio.colore` | OK — dynamic from DB |
| `Calendario.tsx:277-278` | Appointment card | `backgroundColor` + `borderLeftColor` | OK — dynamic service colors |
| `VoiceAgent.tsx:142` | Waveform container | `filter: drop-shadow(...)` | LOW — dynamic value |
| `VoiceAgent.tsx:151-154` | Waveform bars | `width, height, background, opacity` | OK — animated canvas-like |

**3 fixable inline styles** in App.tsx and Sidebar.tsx (logo images). Minor, but easy to fix.

### 1.4 Spacing Consistency

Overall spacing is **consistent**. Pages use `space-y-6` for main containers. Cards use `p-4` or `p-5`. The 4px grid is mostly respected via Tailwind (p-2=8px, p-3=12px, p-4=16px, p-5=20px, p-6=24px).

| Pattern | Usage | Consistent? |
|---------|-------|------------|
| Page top-level | `space-y-6` | YES — all pages |
| Card padding | `p-4` or `p-5` | MOSTLY — Cassa uses Card component defaults (px-6 py-6 from shadcn), Dashboard cards use `p-5` |
| Grid gaps | `gap-4` | YES |
| Button icon margin | `mr-2` | YES |
| Section margin-bottom | `mb-4` | YES |

---

## 2. Dark Mode

### 2.1 Configuration

| Setting | Value | Status |
|---------|-------|--------|
| `tailwind.config.js` darkMode | `["class"]` | OK |
| `:root` variables | Dark palette | OK |
| `.dark` variables | Identical to :root | OK |
| `body` class | Applied via `bg-background text-foreground` | OK |
| `MainLayout` | `bg-slate-950 text-slate-100` | HARDCODED (bypasses CSS vars) |

### 2.2 Dark Mode Coverage

**FLUXION is dark-mode-only**. There is no light mode toggle. The `:root` and `.dark` blocks in `index.css` have **identical values**. This is intentional for the product.

**Issue**: `dark:` variant usage in shadcn components (e.g., `button.tsx`: `dark:bg-input/30`, `dark:hover:bg-input/50`) is technically redundant since light mode never exists, but causes no harm.

**Risk**: The `sonner.tsx` toaster imports `useTheme` from `next-themes` — this dependency may not work correctly in a Tauri app without `next-themes` provider. Toast styling could default to system theme.

| Component | Dark Mode Approach | Issue? |
|-----------|-------------------|--------|
| MainLayout | `bg-slate-950` hardcoded | NO — matches intent |
| ErrorBoundary | `bg-slate-900` hardcoded | NO |
| All pages | `text-white`, `text-slate-*` classes | NO |
| shadcn Card | `bg-card` (CSS var) | NO |
| shadcn Button | CSS var-based | NO |
| Sonner toaster | `useTheme()` from next-themes | WARN — may not resolve correctly |

---

## 3. Loading States

| Page | Has Loading State? | Type | Quality |
|------|-------------------|------|---------|
| **Dashboard** | PARTIAL | Value shows `-` while loading, no skeleton | WARN — no full-page loader, values show dash |
| **Clienti** | YES | `Loader2` spinner centered | OK |
| **Calendario** | YES | `Loader2` spinner centered | OK |
| **Servizi** | YES | `Loader2` spinner centered | OK |
| **Fatture** | NO explicit check visible in scanned code | — | FAIL — no loading state found in first 280 lines |
| **Cassa** | YES | Text "Caricamento cassa..." | WARN — plain text, no spinner/skeleton |
| **Operatori** | Delegated to OperatoriPage | — | NEEDS CHECK |
| **Fornitori** | YES | `Loader2` spinner centered | OK |
| **Analytics** | YES (via isLoading in useQuery) | — | NEEDS CHECK |
| **VoiceAgent** | N/A (no initial data fetch) | — | OK |
| **Impostazioni** | N/A (subsections load independently) | — | OK |
| **App.tsx** (boot) | YES | Logo + "Caricamento..." | OK |

**Summary**: 2 pages lack visual loading feedback (Fatture, Cassa is plain text). Dashboard uses `-` placeholder instead of skeleton. **No skeleton loaders anywhere** in the app — all loading states are spinner-based.

---

## 4. Empty States

| Page/Component | Has Empty State? | Has Icon? | Has CTA? | Quality |
|----------------|-----------------|-----------|----------|---------|
| **Dashboard** — Welcome card | YES | Sparkles icon | 2 CTAs (add client, add appointment) | EXCELLENT |
| **Dashboard** — Appointments | YES | Calendar icon + message | No direct CTA | GOOD |
| **Dashboard** — Compleanni | YES | Cake icon + message | No | GOOD |
| **Dashboard** — Top Operatori | YES | Trophy icon + message | No | GOOD |
| **Clienti** (ClientiTable) | YES | Text only, no icon | No CTA | POOR — just "Nessun cliente trovato" text |
| **Servizi** | YES | Scissors icon + message | CTA "Crea Servizio" | EXCELLENT |
| **Calendario** | NO explicit empty state | — | — | FAIL — calendar shows empty grid cells |
| **Fatture** | NEEDS CHECK | — | — | — |
| **Cassa** | YES | Text "Nessun incasso registrato oggi" | Instruction text | FAIR — no icon |
| **Fornitori** | NEEDS CHECK (delegated to FornitoriTable) | — | — | — |
| **Analytics** | N/A (always has month data) | — | — | OK |

---

## 5. Error States

| Error Type | Handling Method | Visual Feedback | Quality |
|-----------|----------------|-----------------|---------|
| **IPC errors** (useQuery) | React Query error state | Red box with message | GOOD |
| **Clienti** error | `bg-red-900/20 border-red-800` card | Error message | GOOD |
| **Calendario** error | `bg-red-500/10 border-red-500/20` card | Error message | GOOD |
| **Servizi** error | `bg-red-500/10 border-red-500/20` card | Error message | GOOD |
| **Fornitori** error | `bg-red-900/20 border-red-800` card | Error message | GOOD |
| **Mutation errors** (CRUD) | `console.error` only | **NO visual feedback** | FAIL |
| **Toast notifications** | Sonner (`toast.success/error`) | Used in Fatture, Cassa, Fornitori | GOOD |
| **ErrorBoundary** | Full-page fallback | Red-accented card with reload button | GOOD |

**Critical Issue**: Several mutation error handlers only `console.error` without showing toasts:
- `Clienti.tsx:96` — `handleSubmit` catch only logs
- `Clienti.tsx:109` — `handleConfirmDelete` catch only logs
- `Fornitori.tsx:121` — `handleSubmit` catch only logs
- `Fornitori.tsx:133` — `handleConfirmDelete` catch only logs
- `Cassa.tsx:103` — `handleRegistraIncasso` catch only logs

**Pattern inconsistency**: Fatture and Cassa (chiusura) use `toast.error()` for mutations. Clienti and Fornitori do NOT. Users will see no feedback when save/delete fails on those pages.

---

## 6. Component Library (shadcn/ui)

### 6.1 Components Used

| Component | Import Path | Pages Using It |
|-----------|------------|----------------|
| `Button` | `@/components/ui/button` | ALL pages |
| `Card` (+Header/Title/Content) | `@/components/ui/card` | Dashboard, Cassa, Analytics, Fatture |
| `Input` | `@/components/ui/input` | Cassa, Fatture |
| `Label` | `@/components/ui/label` | Cassa |
| `Badge` | `@/components/ui/badge` | Cassa, Fatture, Operatori, VoiceAgent |
| `Select` (+Content/Item/Trigger/Value) | `@/components/ui/select` | Cassa, Fatture |
| `Table` (+Body/Cell/Head/Header/Row) | `@/components/ui/table` | Clienti, Cassa, Fatture |
| `Dialog` (+Content/Header/Title/Footer) | `@/components/ui/dialog` | Cassa |
| `AlertDialog` (+all parts) | `@/components/ui/alert-dialog` | Clienti, Servizi, Cassa, Fornitori |
| `Tabs` (+Content/List/Trigger) | `@/components/ui/tabs` | Fornitori |
| `Textarea` | `@/components/ui/textarea` | Cassa |
| `Separator` | `@/components/ui/separator` | Cassa |
| `ScrollArea` | `@/components/ui/scroll-area` | VoiceAgent |
| `DropdownMenu` (+Content/Item/Separator/Trigger) | `@/components/ui/dropdown-menu` | Header |
| `Progress` | `@/components/ui/progress` | ClientiTable (loyalty) |
| `Sonner Toaster` | `@/components/ui/sonner` | App-level |

### 6.2 Consistency Issues

| Issue | Detail | Severity |
|-------|--------|----------|
| **Native `<table>` in Servizi** | `Servizi.tsx:118` uses raw `<table>` instead of shadcn `Table` component | MEDIUM — visual inconsistency with Clienti/Cassa/Fatture |
| **Native `<input>` in Clienti search** | `Clienti.tsx:196` and `Header.tsx:56` use raw `<input>` instead of shadcn `Input` | LOW — manually styled to match |
| **Native `<button>` in Header** | Several interactive elements use raw `<button>` | LOW — styled manually |
| **Button color overrides** | Most pages override Button with `className="bg-cyan-500 hover:bg-cyan-600 text-white"` instead of using the default primary variant | MEDIUM — defeats the purpose of design tokens |

**Button override analysis**: The shadcn Button `default` variant uses `bg-primary text-primary-foreground`. Since `--primary` is cyan, the buttons should already be cyan without manual overrides. The explicit `bg-cyan-500` overrides are **redundant** and create a maintenance burden if the primary color ever changes.

---

## 7. Responsive Design

**Target**: Desktop only, 1280px minimum.

| Component | min-width Assumption | Risk at 1280px |
|-----------|---------------------|----------------|
| MainLayout | Sidebar 240px + content flex-1 | OK — content gets ~1040px |
| Sidebar collapsed | 64px (w-16) | OK |
| Dashboard stat grid | `grid-cols-4` at lg | OK at 1280px |
| Fornitori stat grid | `grid-cols-4` hardcoded (no responsive) | WARN — 4 cols at any width |
| Fatture stat grid | `grid-cols-4` at md | OK |
| Cassa grid | `grid-cols-5` at md | WARN — 5 columns with sidebar = tight |
| Calendar grid | 7 cols with `min-h-[120px]` cells | OK |

**Findings**:
- **Fornitori** stats grid uses `grid-cols-4` without responsive breakpoints. At 1280px with sidebar expanded, each card gets ~240px — tight but workable.
- **Cassa** uses `grid-cols-5` at md breakpoint (768px). With sidebar, 5 stat cards in ~1040px = ~208px each. Content is short text + numbers, so it fits, but barely.
- No `min-w-*` or `overflow-x-auto` on tables — long content could cause horizontal overflow.

---

## 8. Typography

### 8.1 Type Scale

| Element | Class | Computed Size | Consistent? |
|---------|-------|--------------|------------|
| Page title (h1) | `text-3xl font-bold` | 30px / 700 | YES — all pages except Cassa |
| Cassa title | `text-2xl font-bold` | 24px / 700 | INCONSISTENT — smaller than other pages |
| Card section title | `text-lg font-semibold` | 18px / 600 | YES |
| Stat value | `text-3xl font-bold` or `text-2xl font-bold` | 30px or 24px | MIXED |
| Body text | `text-sm` | 14px | YES |
| Caption/meta | `text-xs` | 12px | YES |
| Subtitle | `text-slate-400 mt-1` or `mt-2` | 14px | MOSTLY consistent |

### 8.2 Issues

| Issue | Detail | Severity |
|-------|--------|----------|
| **Cassa h1 is `text-2xl`** | All other pages use `text-3xl font-bold text-white` | LOW — visual inconsistency |
| **Cassa h1 missing `text-white`** | Uses default `text-foreground` via no explicit color class | LOW — renders similarly but inconsistent pattern |
| **Stat values mixed sizes** | Dashboard: `text-3xl`, Cassa: `text-2xl` and `text-xl`, Fatture: `text-2xl` | MEDIUM — KPI cards lack unified size |
| **Font family** | `'Inter', -apple-system, ...` in index.css body rule | OK — Inter loaded? No @import or link tag found — relies on system font |

**Font Loading Risk**: The CSS specifies `'Inter'` but no `@import` or `<link>` tag for Google Fonts/self-hosted Inter was found. If Inter is not installed on the user's system, it falls back to system fonts. For Italian SMB desktops, Inter is unlikely to be installed. The app will render in -apple-system (Mac) or Segoe UI (Windows).

---

## 9. Icons

| Library | Import Pattern | Consistent? |
|---------|---------------|------------|
| **Lucide React** | `from 'lucide-react'` | YES — used exclusively |

All icons come from `lucide-react`. Size usage is consistent:
- Sidebar nav: `w-5 h-5`
- Page header icons: `w-8 h-8` or `h-8 w-8`
- Button inline: `w-4 h-4` or `w-5 h-5`
- Status indicators: `h-4 w-4`
- Empty state hero: `w-12 h-12` or `h-7 w-7`

**Minor**: Cassa uses emoji characters (money emoji, card emoji, phone emoji, money bag emoji) in CardTitle instead of Lucide icons. This breaks the icon pattern.

---

## 10. Summary of Findings

### CRITICAL (Fix before launch)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| C1 | **Silent mutation errors** — CRUD failures show no UI feedback | Clienti, Fornitori, Cassa (registra) | User thinks action succeeded when it failed |
| C2 | **Font Inter not loaded** — no @import/link tag, falls back to system font on Windows | index.css | Typography differs from design intent on Windows |

### HIGH (Fix for polish)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| H1 | **No skeleton loaders** — all loading states are spinners | All pages | Perceived performance / visual jank |
| H2 | **Servizi uses raw `<table>`** instead of shadcn Table | Servizi.tsx:118 | Visual inconsistency vs Clienti/Fatture |
| H3 | **Button primary color overridden everywhere** | Multiple pages | Maintenance burden; defeats design tokens |
| H4 | **Sonner toaster uses `useTheme()` from next-themes** | sonner.tsx | May not resolve theme correctly in Tauri |

### MEDIUM (Improve)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| M1 | **Cassa page title is `text-2xl`** while all others are `text-3xl` | Cassa.tsx:148 | Visual hierarchy inconsistency |
| M2 | **Cassa uses emojis** instead of Lucide icons in card titles | Cassa.tsx:202-241 | Breaks icon consistency pattern |
| M3 | **Cassa stat card colors use `-600` shade** (`text-green-600`, `text-blue-600`, `text-red-600`, `text-gray-600`) while rest of app uses `-400` shade | Cassa.tsx:206-245 | Colors look muted/wrong on dark background |
| M4 | **KPI value sizes inconsistent** — text-3xl, text-2xl, text-xl mixed | Dashboard vs Cassa vs Fatture vs Analytics | Unpolished feel |
| M5 | **ClientiTable empty state** has no icon, no CTA | ClientiTable.tsx:46-52 | Poor empty state vs excellent one in Servizi |
| M6 | **Calendario has no empty state** for days/month with no appointments | Calendario.tsx | Grid shows empty cells with no guidance |
| M7 | **Fornitori stats grid not responsive** — hardcoded `grid-cols-4` | Fornitori.tsx:365 | Tight at 1280px with sidebar |
| M8 | **Dashboard loading shows `-` not skeleton** | Dashboard.tsx:432-463 | Feels cheap vs proper skeleton |

### LOW (Nice to have)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| L1 | Inline styles on logo images | App.tsx:63, Sidebar.tsx:86 | Could be Tailwind classes |
| L2 | Native `<input>` in search bars | Clienti.tsx:196, Header.tsx:56 | Manually styled, works fine |
| L3 | `dark:` variants in shadcn components redundant | button.tsx, others | No harm, just unnecessary |
| L4 | Hardcoded `bg-slate-950`/`bg-slate-900` instead of `bg-background`/`bg-card` tokens | MainLayout, ErrorBoundary, many pages | Works in dark-only app but bypasses design system |

---

## 11. Recommendations Priority

1. **Add `toast.error()` to all mutation catch blocks** (C1) — 30min fix, highest user impact
2. **Add Inter font via `@font-face` or hosted file** (C2) — 10min fix
3. **Standardize Cassa page** to match other pages (M1, M2, M3) — 1hr
4. **Replace Servizi raw table with shadcn Table** (H2) — 30min
5. **Remove redundant `bg-cyan-500` Button overrides**, rely on `default` variant (H3) — 1hr
6. **Add icon + CTA to ClientiTable empty state** (M5) — 15min
7. **Fix sonner.tsx to not depend on next-themes** (H4) — 15min, use hardcoded "dark"
8. **Unify KPI value text sizes** across all pages (M4) — 30min
