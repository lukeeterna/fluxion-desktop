# FLUXION — Handoff Sessione 31 (2026-03-06) — F06 Sprint C COMPLETE

## ⚡ PRINCIPIO CoVe 2026 — SEMPRE IN OGNI TASK (CTO Approvato Sessione 31)

> **"Non implementare feature. Colma gap reali delle PMI italiane."**
>
> Ogni commento, ogni componente deve portare la risposta: *"perché questo è world-class?"*
> Es: `// World-class: nessun competitor PMI offre annotation nativa su foto danno`
>
> Deep Research CoVe 2026 = **identifica il gap reale** → implementa il salto competitivo.

---

## PROSSIMO TASK: F10 — CI/CD GitHub Actions

Research: da fare con subagente

### Acceptance Criteria F10:
- [ ] `.github/workflows/ci.yml`: type-check + pytest su ogni push
- [ ] Matrix Python 3.9 (iMac runtime) + Python 3.13 (MacBook dev)
- [ ] Badge stato CI nel README
- [ ] Blocco merge se CI fallisce

---

## Completato Sessione 31 — F06 Sprint C

### F06 Media Upload Sprint C ✅ (commit 847fcbe)

**Componenti creati/modificati:**
| File | Descrizione | Gap coperto |
|------|-------------|------------|
| `src/components/media/ImageAnnotator.tsx` | SVG overlay freccia/cerchio/testo su immagine | **UNICO** nel mercato PMI italiano — nessun competitor offre annotation nativa |
| `src/components/schede-cliente/SchedaCarrozzeria.tsx` | Tab "Foto" con workflow Entrata/Lavorazione/Uscita | Nessun competitor ha workflow fotografico per fasi in carrozzeria |
| `src/components/media/MediaGallery.tsx` | Prop `onRecordClick` opzionale | Flessibilità composizione UI |
| `src/types/media.ts` | Categoria `'lavorazione'` aggiunta | Supporto fase lavorazione carrozzeria |
| `src/hooks/use-media.ts` | `useUpdateMediaNote` + `useExportMediaPdf` | Hook per annotazioni e PDF export |
| `src-tauri/src/commands/media.rs` | `update_media_note` + `export_media_pdf` | PDF rapporto fotografico (printpdf) |
| `src-tauri/Cargo.toml` | `printpdf = "0.7"` + `dirs-next = "2"` | PDF generation Rust |

**Note tecniche:**
- ImageAnnotator: SVG `preserveAspectRatio="none"` + coordinate 0-100% → indipendente dalla dimensione reale
- Annotazioni salvate nel campo `note` di `cliente_media` come JSON array
- PDF export: A4 portrait, testo + metadata (no image embedding per MVP — solo lista foto con date/note)
- Tab Foto in SchedaCarrozzeria visibile solo se pratica salvata (`pratica.id` definito)

**Build iMac richiesta** (Rust changes: `cargo build`):
```bash
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master && source ~/.cargo/env && export PATH=/usr/local/bin:$PATH && cargo check 2>&1 | tail -20"
```

---

## Stato Git
```
Branch: master | HEAD: 847fcbe
type-check: ✅ 0 errori
Voice tests: ✅ 1263 PASS / 0 FAIL
```

## Roadmap
| Fase | Task | Status |
|------|------|--------|
| F06 Sprint A | Media Upload base | ✅ DONE 7601ca3 |
| F06 Sprint B | BeforeAfterSlider + Timeline | ✅ DONE 3fdd19a |
| **F06 Sprint C** | **ImageAnnotator + PDF export** | ✅ **DONE 847fcbe** |
| **F10** | **CI/CD GitHub Actions** | **🔄 NEXT** |
| F07 | LemonSqueezy payment | ⏳ |

---

## PROMPT RIPARTENZA SESSIONE 32

```
Sessione 32 — F10 CI/CD GitHub Actions

1. Leggi HANDOFF.md + MEMORY.md
2. Ricorda principio: deep research gap reali PMI → implementa salto competitivo
3. Research su CI/CD GitHub Actions per Tauri + Python: usa subagente → .claude/cache/agents/ci-cd-research.md

Acceptance Criteria F10:
- .github/workflows/ci.yml: type-check + pytest su ogni push/PR
- Matrix: Python 3.9 (iMac runtime) + Python 3.13 (MacBook dev)
- Badge CI nel README
- Blocco merge se CI fallisce
- ROI: -1 checkpoint manuale per ogni fase GSD futura

Build iMac Sprint C: cargo check/build su 192.168.1.12 PRIMA di questo task.
Procedi con RESEARCH → PLAN → IMPLEMENT → VERIFY → DEPLOY
```
