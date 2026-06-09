---
name: Frontend Architecture Snapshot
description: Stack, directory layout, key patterns, and design constraints for FLUXION frontend
type: project
---

**Stack:** React 19 + TypeScript strict + Vite + Tauri 2.x. Tailwind CSS + shadcn/ui. State: TanStack Query (server) + Zustand (UI). No framer-motion. No light mode — permanently dark.

**Design system root:** `bg-slate-950` applied in `MainLayout.tsx`. All pages inherit dark theme. No dark: prefix needed on page-level components (by design).

**ErrorBoundary:** Outer boundary at BrowserRouter level + one wrapping all Routes in AppContent + nested boundary on VoiceAgent + granular per-section boundaries in Impostazioni.

**IPC pattern:** `invoke<T>()` in hooks (`src/hooks/use-*.ts`). Hooks use React Query queryFn/mutationFn. Components call `mutateAsync()` inside try/catch. Tauri 2.x auto-converts camelCase JS params to snake_case Rust: `{ sogliaMinima }` → `soglia_minima: String` in Rust handler.

**Feature gating pattern:** `useFeatureAccessEd25519('feature_key')` returns `boolean`. Pattern in page: `if (!isLoadingAccess && hasAccess === false) return <FeatureBloccato tier={...} />`. Mirror `VoiceAgentBloccato` component style.

**Sidebar badge pattern (S355+):** `NavItem` interface has optional `badge?: number`. `useMagazzinoAlertCount()` drives badge. Expanded sidebar shows amber pill count, collapsed shows 2px dot.

**Why:** App targets PMI with 1-15 employees who need simple, beautiful, offline-capable UI. No online dependencies except WhatsApp bridge and voice pipeline.

**How to apply:** When creating new pages, always handle isLoading + error + empty states. When using mutateAsync in a catch block, always add toast.error(). Never use inline styles for static layout — Tailwind only.
