---
name: Frontend Architecture Snapshot
description: Stack, directory layout, key patterns, and design constraints for FLUXION frontend
type: project
---

**Stack:** React 19 + TypeScript strict + Vite + Tauri 2.x. Tailwind CSS + shadcn/ui. State: TanStack Query (server) + Zustand (UI). No framer-motion. No light mode — permanently dark.

**Design system root:** `bg-slate-950` applied in `MainLayout.tsx`. All pages inherit dark theme. No dark: prefix needed on page-level components (by design).

**ErrorBoundary:** Outer boundary at BrowserRouter level + one wrapping all Routes in AppContent + nested boundary on VoiceAgent + granular per-section boundaries in Impostazioni.

**IPC pattern:** `invoke<T>()` in hooks (`src/hooks/use-*.ts`). 124 typed invoke calls. Hooks use React Query queryFn/mutationFn. Components call `mutateAsync()` inside try/catch.

**Why:** App targets PMI with 1-15 employees who need simple, beautiful, offline-capable UI. No online dependencies except WhatsApp bridge and voice pipeline.

**How to apply:** When creating new pages, always handle isLoading + error + empty states. When using mutateAsync in a catch block, always add toast.error(). Never use inline styles for static layout — Tailwind only.
