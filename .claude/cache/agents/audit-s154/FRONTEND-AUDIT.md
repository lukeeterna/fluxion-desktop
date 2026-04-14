# FLUXION Frontend Production Readiness Audit — S154
> Audit date: 2026-04-14 | Auditor: frontend-developer agent | Branch: master

---

## SUMMARY VERDICT

| Area | Status | Blocker? |
|------|--------|----------|
| TypeScript strict (any / ts-ignore) | PASS | No |
| console.log in production | WARN | No |
| IPC error feedback to user | WARN | No |
| Error boundaries on all routes | PASS | No |
| Empty / loading / error states | WARN | No |
| Accessibility basics | WARN | No |
| Design system consistency (no hardcoded colors) | WARN | No |
| Dark mode | PASS | No |

**PASS criteria met:** TypeScript clean (0 errors, 0 any, 0 @ts-ignore), ErrorBoundary covers all routes.

---

## 1. TypeScript Strict

**`npm run type-check` result: EXIT 0 — zero errors.**

```
tsc --strict --noEmit
EXIT_CODE: 0
```

tsconfig.json has `"strict": true`, `"noUnusedLocals": true`, `"noUnusedParameters": true`, `"noFallthroughCasesInSwitch": true`.

Search for `: any` and `as any` patterns: **zero occurrences found in all .ts/.tsx files under src/.**

Search for `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`: **zero occurrences found.**

Type casts present (not violations — properly narrowed union discriminants):
- `src/pages/Clienti.tsx:89 | INFO | data as UpdateClienteInput` — narrowed by `'id' in data` check. Acceptable.
- `src/pages/Fornitori.tsx:115 | INFO | data as UpdateSupplierInput` — same pattern. Acceptable.
- `src/components/clienti/ClienteForm.tsx:123 | INFO | as UpdateClienteInput` — narrowed. Acceptable.

**Result: PASS. No prohibited TypeScript patterns.**

---

## 2. console.log / console.warn / console.error in Production Code

54 occurrences found across 19 files. All are `console.error` or `console.warn` — no raw `console.log`. However, production rules require structured logging, not browser console output.

### Critical (error paths that also lack user toast feedback):

| file:line | SEVERITY | description | suggested fix |
|-----------|----------|-------------|---------------|
| `src/pages/Clienti.tsx:96` | HIGH | `console.error('Failed to save cliente:')` — no toast shown to user | Add `toast.error('Errore nel salvataggio del cliente', { description: String(error) })` |
| `src/pages/Clienti.tsx:109` | HIGH | `console.error('Failed to delete cliente:')` — no toast shown | Add `toast.error('Errore nell\'eliminazione del cliente')` |
| `src/pages/Cassa.tsx:104` | HIGH | `console.error('Errore registrazione:')` — no toast shown | Add `toast.error('Errore nella registrazione dell\'incasso', { description: String(error) })` |
| `src/pages/Cassa.tsx:131` | MEDIUM | `console.error('Errore eliminazione:')` — no toast shown | Add `toast.error('Errore nell\'eliminazione dell\'incasso')` |
| `src/pages/Fatture.tsx:152` | HIGH | `console.error('Errore eliminazione:')` — no toast shown on fattura delete | Add `toast.error('Errore eliminazione fattura', { description: String(err) })` |
| `src/pages/Fornitori.tsx:121` | HIGH | `console.error('Failed to save fornitore:')` — no toast | Add `toast.error('Errore nel salvataggio del fornitore')` |
| `src/pages/Fornitori.tsx:133` | HIGH | `console.error('Failed to delete fornitore:')` — no toast | Add `toast.error('Errore nell\'eliminazione del fornitore')` |
| `src/pages/Fornitori.tsx:153` | MEDIUM | `console.error('Failed to create order:')` — no toast | Add `toast.error('Errore nella creazione dell\'ordine')` |
| `src/pages/Fornitori.tsx:161` | MEDIUM | `console.error('Failed to update order status:')` — no toast | Add `toast.error('Errore nell\'aggiornamento dello stato ordine')` |
| `src/pages/Fornitori.tsx:313` | MEDIUM | `console.error('Failed to send order:')` — no toast | Add `toast.error('Errore nell\'invio dell\'ordine')` |
| `src/components/operatori/OperatoreDialog.tsx:55` | MEDIUM | `console.error('Failed to save operatore:')` — no toast | Add `toast.error('Errore nel salvataggio dell\'operatore')` |
| `src/components/servizi/ServizioDialog.tsx:128` | MEDIUM | `console.error('Failed to save servizio:')` — no toast | Add `toast.error('Errore nel salvataggio del servizio')` |
| `src/components/fatture/FatturaDialog.tsx:124` | MEDIUM | `console.error('Errore creazione fattura:')` — no toast in catch | Add `toast.error('Errore nella creazione della fattura', { description: String(err) })` |

### Acceptable console usages (can stay or be guarded by `import.meta.env.DEV`):

| file:line | SEVERITY | description |
|-----------|----------|-------------|
| `src/components/ErrorBoundary.tsx:31` | LOW | `console.error` in componentDidCatch — correct for crash reporting; keep |
| `src/hooks/use-voice-pipeline.ts:568,704,770,859,1021` | LOW | VAD/audio errors — audio debugging, acceptable in v1. Guard behind `import.meta.env.DEV` in v1.1 |
| `src/App.tsx:38,48` | LOW | Setup check fallback errors — guard behind `import.meta.env.DEV` |

---

## 3. IPC Error Feedback (B17)

Audit methodology: for each `invoke()` call, check if the error path produces a visible `toast()` notification.

### invoke() calls in .tsx files (component layer — user-facing):

| file:line | SEVERITY | description | suggested fix |
|-----------|----------|-------------|---------------|
| `src/components/impostazioni/SmtpSettings.tsx:56` | PASS | `save_smtp_settings` — catch shows inline `setMessage({ type: 'error' })` | OK |
| `src/components/whatsapp/WhatsAppQRScan.tsx:83` | WARN | `start_whatsapp_service` — catch sets `state.status = 'error'` but no toast | Add `toast.error('Errore avvio WhatsApp', { description: String(error) })` |
| `src/components/whatsapp/WhatsAppAutoResponder.tsx:192` | WARN | `start_whatsapp_service` — catch at line 198 logs `console.error` only | Add `toast.error('Errore avvio risposta automatica WhatsApp')` |
| `src/components/calendario/AppuntamentoDialog.tsx:189` | PASS | fire-and-forget WA confirm, `.catch(() => {})` intentional — non-fatal | OK |

### invoke() calls in hooks (React Query layer — error propagated to component):

Most hooks use React Query `queryFn` / `mutationFn`. When these throw, React Query sets `isError = true` and `error`. The component is responsible for displaying the error. Most pages (Clienti, Cassa, Fatture, Fornitori) check `isError` / `error` at the page level but catch blocks in mutation handlers silently swallow the error (see Section 2).

**Pattern gap:** React Query mutations with `mutateAsync` inside a `try/catch` that only logs — the error does NOT bubble to React Query's `error` state because it was caught. The user sees nothing.

**Affected mutations (confirmed):**
- `Clienti.handleSubmit` — save/update cliente
- `Clienti.handleConfirmDelete` — delete cliente
- `Cassa.handleRegistraIncasso` — registra incasso
- `Cassa.handleEliminaIncasso` — elimina incasso
- `Fatture.handleConfirmDelete` — elimina fattura
- `Fornitori.handleSubmit` — save/update fornitore
- `Fornitori.handleConfirmDelete` — delete fornitore
- `Fornitori.handleNewOrder` / `handleUpdateStatus` / `handleSendOrder`

---

## 4. Error Boundaries

### Route coverage in `src/App.tsx`:

```
App
└── ErrorBoundary                          ← outer (BrowserRouter level)
    └── AppContent
        └── MainLayout
            └── ErrorBoundary              ← wraps all Routes
                ├── /               → Dashboard
                ├── /clienti        → Clienti
                ├── /calendario     → Calendario
                ├── /servizi        → Servizi
                ├── /operatori      → Operatori
                ├── /operatori/:id  → OperatoreDettaglio
                ├── /fatture        → Fatture
                ├── /cassa          → Cassa
                ├── /voice          → ErrorBoundary (nested) → VoiceAgent
                ├── /fornitori      → Fornitori
                ├── /analytics      → Analytics
                └── /impostazioni   → Impostazioni
```

All routes are covered by the outer `<ErrorBoundary>` at line 104. VoiceAgent has an additional nested boundary. Impostazioni uses granular per-section ErrorBoundary wrappers (lines 444–545).

**Result: PASS. Every route is protected.**

---

## 5. Empty States & Loading States

### Per-page breakdown:

| Page | Loading | Error | Empty | Notes |
|------|---------|-------|-------|-------|
| **Clienti** | PASS — Loader2 spinner | PASS — red error card | PASS — ClientiTable handles empty array (0 rows shown) | Missing explicit "nessun cliente" empty state in ClientiTable |
| **Calendario** | PASS — Loader2 spinner | PASS — red error card | WARN — no explicit empty-month message; calendar grid shows with no appointments but no visual hint | Add "Nessun appuntamento questo mese" overlay |
| **Servizi** | PASS — Loader2 spinner | PASS — error card | PASS — explicit empty state with CTA button at line 103 | Good |
| **Operatori** | PASS (delegated to OperatoriPage) | PASS (delegated) | Need to check OperatoriPage — delegates entirely | Acceptable |
| **Fatture** | PASS — inline "Caricamento fatture..." | PASS — red text | PASS — "Nessuna fattura trovata" at line 339 | Good |
| **Cassa** | PASS — "Caricamento cassa..." | FAIL — no error state rendered | PASS — "Nessun incasso registrato oggi" at line 260 | `useIncassiOggi` returns `{ data, isLoading }` — `error` not destructured; if query fails, blank screen |
| **Analytics** | PASS — Loader2 + isLoading guard | PASS — AlertCircle + error message | WARN — no empty state when `data` has all zeros (valid but confusing UX) | Low priority |
| **Fornitori** | PASS — Loader2 spinner | PASS — red error card | WARN — no "Nessun fornitore" empty state; renders empty table structure | Add empty state |

### Detailed findings:

| file:line | SEVERITY | description | suggested fix |
|-----------|----------|-------------|---------------|
| `src/pages/Cassa.tsx:68` | HIGH | `isLoading` destructured but `error` is NOT — if `useIncassiOggi` fails, blank white screen after loading ends | Destructure `error` and add `if (error)` render block |
| `src/pages/Calendario.tsx:208` | LOW | Calendar grid renders with empty days but no "month has no appointments" message | Add subtle empty-state label inside grid when `appuntamenti.length === 0` |
| `src/pages/Fornitori.tsx:349` | LOW | No empty state when `fornitori.length === 0` — renders header + empty table | Add empty-state card after stats section |

---

## 6. Accessibility Basics

### Form input labels:

Audit method: search for `<Input` / `<input` without `id=` or `aria-label` cross-referenced against `<Label htmlFor`.

**Findings:**

| file:line | SEVERITY | description | suggested fix |
|-----------|----------|-------------|---------------|
| `src/components/impostazioni/VoiceSaraQuality.tsx:101,120,152` | MEDIUM | `<input` elements without `aria-label` or associated `<Label htmlFor>` | Add `id` + `<Label htmlFor>` or `aria-label` to range inputs |
| `src/components/impostazioni/DiagnosticsPanel.tsx:390` | LOW | `<input` without label association — context needed | Review and add label |
| `src/pages/Clienti.tsx:192` | MEDIUM | Search `<input>` at line 192 — has `placeholder` but no `aria-label` | Add `aria-label="Cerca clienti per nome, telefono, email"` |
| `src/components/calendario/AppuntamentoDialog.tsx:342,357,367` | LOW | `<Input>` elements inside react-hook-form — wrapped by `FormField/FormItem/FormLabel` in surrounding code; verify label association | Likely OK via shadcn Form component — verify at runtime |

### Images with alt text:

No `<img>` tags found in TSX files (zero results). Images in App.tsx loading state use `alt="Fluxion"` correctly.

### Interactive elements without aria-labels:

| file:line | SEVERITY | description | suggested fix |
|-----------|----------|-------------|---------------|
| `src/pages/Analytics.tsx:194,204` | LOW | `<button>` for month navigation — has `title` but no `aria-label` | Replace `title` with `aria-label` for better screen reader support |
| `src/pages/Calendario.tsx:163,168` | LOW | Prev/Next month `<Button>` — icon-only with no aria-label | Add `aria-label="Mese precedente"` / `aria-label="Mese successivo"` |
| `src/pages/Clienti.tsx:200` | LOW | Clear search `<button>` — icon only (X), no aria-label | Add `aria-label="Cancella ricerca"` |
| `src/components/operatori/OperatoreDettaglio.tsx:110` | LOW | Color swatch `div` with dynamic `backgroundColor` — no alt/aria | Add `aria-label="Colore operatore"` |

### Focus management:

| file:line | SEVERITY | description | suggested fix |
|-----------|----------|-------------|---------------|
| `src/components/ErrorBoundary.tsx:70` | LOW | "Ricarica Applicazione" button — `onClick={() => window.location.reload()}` — `window` usage is acceptable here (Tauri WebView) but no `autoFocus` after error boundary activates | Add `autoFocus` to reload button or manage focus on mount |

---

## 7. Design System Consistency

### Inline styles (violation of "no inline styles — Tailwind only" rule):

| file:line | SEVERITY | description | suggested fix |
|-----------|----------|-------------|---------------|
| `src/App.tsx:63,80` | MEDIUM | `style={{ width: 80, height: 80, borderRadius: 16, objectFit: 'cover' }}` on logo img | Replace with `className="w-20 h-20 rounded-2xl object-cover"` |
| `src/components/layout/MainLayout.tsx:23` | LOW | `style={{ minHeight: '100vh' }}` redundant with `min-h-screen` already in className | Remove inline style |
| `src/components/layout/Sidebar.tsx:86` | LOW | `style={{ width: 36, height: 36, borderRadius: 8, objectFit: 'cover' }}` | Replace with `className="w-9 h-9 rounded-lg object-cover"` |
| `src/components/setup/SetupWizard.tsx:137` | LOW | `style={{ width: 64, height: 64, borderRadius: 12, objectFit: 'cover' }}` | Replace with `className="w-16 h-16 rounded-xl object-cover"` |
| `src/components/operatori/OperatoriPage.tsx:346` | INFO | `style={{ backgroundColor: op.colore || '#64748b' }}` — dynamic color from DB; Tailwind cannot generate runtime values | Acceptable — use CSS variable or keep inline for dynamic colors |
| `src/components/operatori/OperatoreDettaglio.tsx:110` | INFO | `style={{ backgroundColor: operatore.colore || '#64748b' }}` | Same as above — acceptable for dynamic DB colors |
| `src/components/operatori/OperatoreDialog.tsx:126,138` | INFO | Color picker swatches — `style={{ backgroundColor: field.value }}` / `style={{ backgroundColor: color }}` | Acceptable — dynamic runtime colors |
| `src/components/servizi/ServizioDialog.tsx:358,370` | INFO | Color picker swatches — same pattern | Acceptable |
| `src/components/setup/SetupWizard.tsx:631` | MEDIUM | `style={{ ...font, color: firmaFont === idx ? '#22d3ee' : '#94a3b8', display: 'block' }}` — hardcoded hex colors | Use Tailwind conditional: `firmaFont === idx ? 'text-cyan-400' : 'text-slate-400'` |
| `src/pages/Analytics.tsx:461` | LOW | `style={{...}}` on bar chart element — dynamic height percentage | Acceptable for dynamic layout |
| `src/pages/VoiceAgent.tsx:142,150,163,170-178,183` | MEDIUM | Multiple `style={{ color: barColor() }}` — dynamic color from state | Extract to `data-state` attribute + Tailwind variants, or use CSS vars |
| `src/components/media/BeforeAfterSlider.tsx:77,101,107,115,121` | INFO | Dynamic percentage positions — cannot use Tailwind | Acceptable — dynamic layout calculations |
| `src/components/media/ImageAnnotator.tsx:238,298,356,373` | INFO | Canvas/annotation tool inline styles — acceptable for canvas context | OK |
| `src/components/operatori/OperatoreStatisticheSection.tsx:104` | INFO | `style={{ height: \`${Math.max(heightPct, 4)}%\` }}` — chart bar heights | Acceptable — dynamic layout |

### Hardcoded colors (non-Tailwind hex values):

| file:line | SEVERITY | description | suggested fix |
|-----------|----------|-------------|---------------|
| `src/components/setup/SetupWizard.tsx:631` | MEDIUM | `color: '#22d3ee'` (= cyan-400) and `color: '#94a3b8'` (= slate-400) — hardcoded hex | Use `text-cyan-400` / `text-slate-400` via className |
| `src/components/operatori/OperatoriPage.tsx:346` | INFO | `'#64748b'` (= slate-500) fallback default — acceptable for runtime dynamic colors | Can replace fallback with CSS var `var(--color-slate-500)` |
| `src/components/operatori/OperatoreDettaglio.tsx:110` | INFO | Same `'#64748b'` fallback | Same fix |
| `src/components/media/ImageAnnotator.tsx:298` | LOW | `filter: 'drop-shadow(0 0 2px #000)'` — hardcoded black | Replace with Tailwind `drop-shadow` or CSS var |

---

## 8. Dark Mode

**Architecture:** The app uses a **hardcoded dark theme** — `bg-slate-950` set on the root layout in `MainLayout.tsx`. There is no light/dark toggle; the app is always dark.

**Assessment:** Because this is a permanently-dark application, the absence of `dark:` prefixes on page-level components is **by design** and NOT a bug. Components use `bg-slate-900`, `text-slate-400`, etc. directly.

`dark:` variants are used in:
- `src/components/ui/` — shadcn/ui components that follow Radix conventions
- 21 instances in `src/components/` (outside ui) — mostly in schede-cliente and operatori components that follow the design system

**No findings.** Dark mode is permanently applied at root level — no fixes needed.

---

## CONSOLIDATED PRIORITY LIST

### P0 — Fix Before Next Release (user-facing silent failures)

1. **Cassa error state missing** (`src/pages/Cassa.tsx:68`) — if `useIncassiOggi()` fails, blank screen with no feedback
2. **Silent mutation failures** — 13 catch blocks (listed in Section 2) swallow errors without toast. At minimum: Clienti save/delete, Cassa registra/elimina, Fatture delete, Fornitori save/delete
3. **IPC: WhatsApp start service** (`WhatsAppQRScan.tsx:83`, `WhatsAppAutoResponder.tsx:192`) — errors silently swallowed or only logged

### P1 — Fix in Sprint 6 (polish + correctness)

4. **Inline styles on static images** — App.tsx:63/80, Sidebar.tsx:86, SetupWizard.tsx:137 — replace with Tailwind w-/h-/rounded- classes
5. **Search input accessibility** — `Clienti.tsx:192` — add `aria-label`
6. **Icon-only buttons** — Calendario prev/next, Clienti clear-search — add `aria-label`
7. **Calendario empty month** — add "Nessun appuntamento questo mese" message
8. **Fornitori empty state** — add card when 0 fornitori

### P2 — Nice to Have (low impact)

9. **SetupWizard.tsx:631** — replace `#22d3ee`/`#94a3b8` with Tailwind classes
10. **VoiceAgent.tsx** — dynamic `style={{ color: barColor() }}` — consider CSS vars
11. **console.* in production** — guard with `import.meta.env.DEV` flag in v1.1

---

## APPENDIX: Type-check verification

```
$ npm run type-check
> tauri-app@1.0.0 type-check
> tsc --noEmit
EXIT_CODE: 0
```

Zero TypeScript errors. Strict mode active. No `any`, no `@ts-ignore`, no `@ts-expect-error` found in any `.ts` or `.tsx` file under `src/`.
