# FLUXION Codebase Gap Analysis — CoVe 2026 Enterprise
> Generato: 2026-03-02 | Agente: gsd-codebase-mapper | v0.9.2

---

## Executive Summary

**Stato**: Zero TypeScript violations. 25 migrations sequenza corretta (001→025). B2-B5 Operatori + C1 SDI completati. Nessun `any`, nessun `@ts-ignore`.

**Issues critici**: 1 security issue urgente (`window.prompt` cleartext API key). 5 schede verticali placeholder. 13 `window.confirm/alert` anti-pattern. 21 bare `unwrap()` Rust in produzione.

---

## Feature Status

| Feature | Stato | Note |
|---------|-------|------|
| **Calendario/Appuntamenti** | ✅ Completo | `src/pages/Calendario.tsx` |
| **Clienti + Schede base** | ✅ Completo | `src/pages/Clienti.tsx` |
| **Operatori B2 Servizi** | ✅ Completo | `OperatoreServiziSection.tsx` |
| **Operatori B3 Orari** | ✅ Completo | `OperatoreOrariSection.tsx` |
| **Operatori B4 KPI** | ✅ Completo | `OperatoreStatisticheSection.tsx` |
| **Operatori B5 Commissioni** | ✅ Completo | `OperatoreCommissioniSection.tsx` |
| **Fatture + SDI C1** | ✅ Completo | `src/pages/Fatture.tsx` — Fattura24 API |
| **Voice Agent Sara** | ✅ Completo | porta 3002 — P2 100% PASS |
| **WhatsApp Integration** | ⚠️ Parziale | Bulk sender simulato (`loyalty.rs:973`) |
| **Scheda Verticale Parrucchiere** | 🔴 Placeholder | `SchedaClienteDynamic.tsx:102` |
| **Scheda Verticale Veicoli** | 🔴 Placeholder | `SchedaClienteDynamic.tsx:~140` |
| **Scheda Verticale Carrozzeria** | 🔴 Placeholder | `SchedaClienteDynamic.tsx:~170` |
| **Scheda Verticale Medica** | 🔴 Placeholder | `SchedaClienteDynamic.tsx:~200` |
| **Scheda Verticale Fitness** | 🔴 Placeholder | `SchedaClienteDynamic.tsx:~230` |
| **Pacchetti/Prepagati** | 🔴 Non implementato | Nel PRD — feature v1.0 |
| **Loyalty Program** | ⚠️ Parziale | Backend `loyalty.rs` — UI non collegata |
| **Multi-sede** | 🔴 Non implementato | Enterprise tier feature |

---

## Quality Issues

### 🚨 CRITICO — Security

| File | Riga | Issue |
|------|------|-------|
| `src/pages/Fatture.tsx` | 147 | `window.prompt()` per Fattura24 API key in CLEARTEXT |

**Fix richiesto**: Sostituire con `shadcn Dialog` + `<Input type="password">` masked + salvataggio sicuro via Tauri store.

### ⚠️ ALTA — UX Anti-patterns

| Pattern | Count | Fix |
|---------|-------|-----|
| `window.confirm()` | 12 | → `AlertDialog` shadcn |
| `window.alert()` | 1 | → `sonner` toast |
| `window.prompt()` | 1 (security!) | → Dialog shadcn |

### ⚠️ MEDIA — Rust Safety

| File | Count | Issue |
|------|-------|-------|
| `src-tauri/src/commands/appuntamenti.rs` | 21 | `unwrap()` bare — panic risk in produzione |
| Altri file Rust | ~13 | `unwrap()` |

**Fix**: Sostituire con `map_err(|e| e.to_string())?` pattern.

### ℹ️ BASSA — Repo Hygiene

| Issue | Dettaglio |
|-------|-----------|
| 2 file `.backup` nel repo | `git rm` e aggiungere a `.gitignore` |
| PRD pricing outdated | PRD mostra €199/€399/€799 vs corretto €297/€497/€897 |

---

## Database Status

**Migrations**: 001-025 tutte presenti, sequenza consecutiva corretta.

| Migration | File | Contenuto |
|-----------|------|-----------|
| 007 | `fatturazione_elettronica.sql` | fatture + campi SDI |
| 012 | `operatori_voice_agent.sql` | specializzazioni voice |
| 019 | `schede_clienti_verticali.sql` | struttura verticali (verifica placeholder) |
| 024 | `operatori_features.sql` | assenze, KPI views |
| 025 | `operatori_commissioni.sql` | B5 commissioni |

---

## Landing vs App Coverage

**Screenshot presenti nella landing** (7): Calendario, Clienti, Fatture, Dashboard, Operatori base, Voice setup, WhatsApp.

**Screenshot MANCANTI per v0.9.2**:
- Commissioni operatori (B5) — nuovo
- Statistiche/KPI operatori (B4) — nuovo
- Voice Agent UI (Sara) — nuovo
- SDI/Fattura badge esito — nuovo
- Pacchetti prepagati — non implementato ancora
- Loyalty program — non implementato ancora

---

## Priorità Azioni (Top 7)

| # | Priorità | Task | File | Effort |
|---|----------|------|------|--------|
| 1 | 🚨 URGENTE | Fix `window.prompt` API key → Dialog shadcn | `Fatture.tsx:147` | 1h |
| 2 | ⚠️ ALTA | Completare 5 schede verticali | `SchedaClienteDynamic.tsx` | 8-10h |
| 3 | ⚠️ ALTA | Replace 12 `window.confirm` → `AlertDialog` | Multiple files | 2h |
| 4 | 📸 ALTA | D1 Screenshots 8-12 nuove per landing v0.9.2 | `landing/` | 2h |
| 5 | ⚙️ MEDIA | Fix 21 `unwrap()` → `map_err` in appuntamenti.rs | `appuntamenti.rs` | 2h |
| 6 | 📄 MEDIA | Update PRD pricing (€297/€497/€897) | `PRD-FLUXION-COMPLETE.md` | 15min |
| 7 | 🧹 BASSA | `git rm` file `.backup` + WhatsApp bulk sender reale | vari | 1h |

---

## Immediate Actions (Next Session)

```bash
# Priority 1: Rebuild DMG con nuova icona
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull && npm run tauri build"

# Priority 2: Fix window.prompt security issue
# src/pages/Fatture.tsx:147 → Dialog + masked input

# Priority 3: D1 Screenshots
# Cattura manuale da Fluxion.app compilata su iMac
```

---

*Fonte: gsd-codebase-mapper agent — analisi completa v0.9.2 codebase*
