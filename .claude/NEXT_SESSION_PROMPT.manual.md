# Prompt ripartenza S277 — backlog opzionale (CTO discrezione, REGOLA #15)

## Stato chiusura S276 (VERDE, fix surgical FE)

**S276 outcome**: BUG-FATT-3 cache stale Fatture lista — fix surgical 3 hook `use-fatture.ts` con `await` su `invalidateQueries`. Race window FE chiusa. REGOLA #14 + REGOLA #15 PASS — 100% autonomous FE, founder zero touch.

### Done S276
1. ✅ **`src/hooks/use-fatture.ts`** (+30 / -16 net): 3 mutations chained convertite `onSuccess` da sync a `async` + `await`:
   - `useAddRigaFattura.onSuccess` — `await Promise.all([invalidate(detail), invalidate(all)])`. Garantisce refetch list completato prima che `mutateAsync` ritorni → `FatturaDialog.handleSubmit` chiude dialog dopo cache aggiornata col `totale_documento` corretto.
   - `useDeleteRigaFattura.onSuccess` — `await invalidate(all)`. Backend chiama `internal_update_fattura_totals` su delete.
   - `useRegistraPagamento.onSuccess` — `await Promise.all([invalidate(detail), invalidate(all)])`. Backend aggiorna `stato_pagamento` / `stato='pagata'` su fatture row.
2. ✅ **Audit REGOLA #11 cross-entity**: nessun fix necessario su use-clienti/fornitori/cassa/loyalty/listini/appuntamenti. Pattern parent-row-with-denormalized-totale è UNICO al flow fatture. Altre entity usano SUM aggregati ricalcolati a SELECT time (no UPDATE su parent).
3. ✅ **Type-check**: 0 errori.
4. ✅ **Lint**: 0 errori (17 warnings preesistenti in e2e-tests/, nessuna in src/hooks/).
5. ⏭️ **Cargo backend smoke**: skip motivato — fix è 100% FE, zero modifiche Rust. Baseline S275 `integration_fatture` 4/4 PASS ancora valida by-construction.

### Analisi root cause (per posterità)

Flow `FatturaDialog.handleSubmit` con `importoRapido`:
1. `createFattura.mutateAsync()` → Rust insert fattura row (`totale_documento=0`, no righe ancora) → onSuccess sync `invalidateQueries(all)` → refetch #1 parte (in-flight)
2. `addRiga.mutateAsync()` → Rust insert riga + `internal_update_fattura_totals(fattura_id)` → DB aggiornato (`totale_documento=15.0`) → onSuccess sync `invalidateQueries(all)` → refetch #2 parte
3. `setCreateDialogOpen(false)` chiamato (`onSuccess` prop callback)

**Race window pre-fix**: refetch #2 NON await-ata → `mutateAsync` ritorna immediato → dialog chiude → ma cache list può ancora avere snapshot stale dal refetch #1 (in-flight quando refetch #2 ha tentato dedup, oppure completed con `totale=0` se refetch #1 era veloce e refetch #2 tardivo). TanStack Query v5 dedupa con AbortController, però la finestra dipende dal timing exact.

**Fix S276**: `await invalidateQueries(...)` in onSuccess `useAddRigaFattura` → `mutateAsync` aspetta che refetch finale completi prima di ritornare. Dialog chiude DOPO cache list aggiornata. Finestra di race chiusa.

Backend (`internal_add_riga_fattura` chiama `internal_update_fattura_totals` PRIMA di ritornare — line 991 `fatture.rs`) era già corretto; verificato in S271 da `test_fattura_totale_aggiornato_dopo_add_riga` 4/4 PASS.

### Verify live carry-over

Live E2E verify (founder GUI):
1. Crea fattura nuova con `importoRapido=15.00` → controlla che colonna `Importo` mostri €15.00 immediatamente (senza F5)
2. Apri dettaglio → verifica righe aggiornate
3. Aggiungi/elimina riga in dettaglio → verifica `totale` aggiornato in lista
4. Registra pagamento → verifica stato `pagata` in lista

Carry-over a S277+ founder GUI Keychain unlock available.

### Out of scope mantenuto (S276)
- `useCreateFattura.onSuccess`: lasciato `sync` (può essere chiamato standalone "Crea Bozza" senza addRiga; in chained flow lo sovrascrive `useAddRigaFattura.onSuccess` await-ato).
- `useEmettiFattura` / `useAnnullaFattura` / `useDeleteFattura` / `useInviaSdiFattura` / `useAggiornaEsitoSdi`: single-mutation chiamate standalone dalla pagina Fatture, no chain → sync invalidate OK.
- `useUpdateImpostazioniFatturazione`: single-mutation, no chain.
- BUG-FATT-5 toast z-index Dialog (P1): skip permanente, no UI rendering verify infra disponibile MacBook.

---

## TASK candidati S277 (CTO discrezione, REGOLA #15 — no A/B, decide e parti)

### Track A: feature roadmap pipeline (highest probable ROI)
- Verifica `ROADMAP_REMAINING.md` per next feature non-bug pipeline.
- Probabili candidati: Sara voice edge cases, waitlist UX completamento, fatture PDF rendering, loyalty tier upgrade.
- Effort variabile.

### Track B: live verify BUG-FATT-3 + BUG-FATT-5 toast z-index (P1 defer S267)
- Live E2E founder GUI iMac con Keychain unlock per confermare S276 fix funziona end-to-end.
- Se OK, fix definitivo BUG-FATT-5: `<Toaster position="top-center" toastOptions={{style:{zIndex:9999}}} />` globale in `App.tsx` o `main.tsx`.
- Effort: ~30min se live verify ok + 30min fix toast.

### Track C: pulizia cargo fmt residual iMac (igiene repo)
- 14 file con cargo fmt diff residual su iMac NON committati da S273/S274/S275.
- `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && cargo fmt --check"` per diff completo.
- Effort: ~30min.

### Track D: founder-driven (priorità alta se emerge pain operativo)

---

## Vincoli S277
- **REGOLA #14**: CTO autonomous test+fix backend via SSH+cargo. Founder solo decisioni strategiche / GUI Keychain unlock.
- **REGOLA #15**: NO domande A/B su scope. Decide best ROI/risk e parti.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **REGOLA #11**: matrice 4/4 CHIUSA da S275. BUG-FATT-3 fix S276 era FE-only, REGOLA #11 audit cross-entity confermato NO altro fix necessario.
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/schema config) → BLOCK_CRITICAL ≥50% raw.

---

## PROMPT START S277

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S276 close + backlog.

REGOLA #15 attiva: decidi track autonomamente.

Track suggested: Track B (live verify BUG-FATT-3 + BUG-FATT-5 fix se founder GUI disponibile) o Track A (roadmap pipeline).

REGOLA #14: backend-side autonomous. Founder solo override su pain operativo.
```

---

**Provenienza S276 close**: VERDE pieno. Fix surgical 3-hook `use-fatture.ts` + type-check 0 errors + lint 0 errors + audit REGOLA #11 cross-entity NO altro fix necessario. Commit S276 atomico in chiusura.
