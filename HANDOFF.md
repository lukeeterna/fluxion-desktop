# FLUXION — Handoff Sessione 28 (2026-03-06) — Kaggle v19 COMPLETE

## PROSSIMO TASK: F06 Media Upload Sprint A

Research già completa: `.claude/cache/agents/schede-media-upload-research.md`

### Acceptance Criteria Sprint A (P0):
- [ ] Migration 030 `cliente_media` + ALTER TABLE clienti (consensi GDPR) → registrata in lib.rs
- [ ] 5 Rust commands: `save_media_image`, `save_media_video`, `get_cliente_media`, `delete_media`, `read_media_file`
- [ ] `MediaUploadZone.tsx` — drag-drop, compressione canvas, HEIC support
- [ ] `MediaGallery.tsx` + `MediaLightbox.tsx` — griglia thumbnail + lightbox ESC/frecce
- [ ] `MediaConsentModal.tsx` — GDPR obbligatorio per foto cliniche
- [ ] Integrazione in SchedaParrucchiere (tab "Trasformazioni") + SchedaMedica ("Immagini Cliniche")
- [ ] `npm run type-check` → 0 errori

---

## Completato Sessione 28 — Kaggle v19

### Kaggle FLUX.1-schnell Mockups ✅
- **8/8 PNG generati** in `_bmad-output/mockups/`
- Fix definitivo dopo v11→v19 (8 tentativi, storico errori P100)

### Storico Errori P100 (COMPLETO — non ripetere):
| v | Errore | Causa | Fix |
|---|--------|-------|-----|
| v11 | DeadKernelError RAM OOM | transformer+T5 float16 > 13GB RAM | bitsandbytes 8-bit |
| v12 | CUDA OOM | T5 primo + transformer → supera VRAM | carica transformer PRIMA |
| v13 | Int8Params error | transformers 5.3.0 incompatibile | pin transformers==4.46.3 |
| v14 | cublasLt error | NF4 4-bit non supportato P100 CC6.0 | usa 8-bit (non NF4) |
| v15 | CUDA OOM | T5 (2.4GB) prima, poi transformer > VRAM | ordine invertito |
| v16 | Auth 401 | KGAT token in json sbagliato | `echo "KGAT_..." > ~/.kaggle/access_token` |
| v17 | Device mismatch CPU/CUDA | device_map={"": "cpu"} no hooks | AlignDevicesHook manuale |
| v18 | cublasLt error | bitsandbytes 8-bit stesso problema NF4 su P100 | ZERO bitsandbytes |
| **v19** | **COMPLETE 8/8** | **Pre-encode T5 CPU → del T5 → float16 + sequential_cpu_offload** | ✅ |

### Pattern vincente P100 v19:
```python
# 1. T5+CLIP su CPU → encode → del → gc.collect()
# 2. FluxPipeline.from_pretrained(text_encoder=None, text_encoder_2=None, torch_dtype=float16)
# 3. pipe.enable_sequential_cpu_offload()
# 4. pipe(prompt_embeds=pe, pooled_prompt_embeds=ppe, ...)
# ZERO bitsandbytes = ZERO cublasLt issues
```

### File prodotti:
| File | Size |
|------|------|
| `_bmad-output/mockups/01-scheda-parrucchiere.png` | 340KB |
| `_bmad-output/mockups/02-scheda-fitness.png` | 390KB |
| `_bmad-output/mockups/03-scheda-medica.png` | 346KB |
| `_bmad-output/mockups/04-scheda-estetica.png` | 402KB |
| `_bmad-output/mockups/05-scheda-veicoli.png` | 299KB |
| `_bmad-output/mockups/06-dashboard.png` | 328KB |
| `_bmad-output/mockups/07-calendario.png` | 513KB |
| `_bmad-output/mockups/08-voice-sara.png` | 360KB |

---

## Stato Git
```
Branch: master | HEAD: d77f2fa
type-check: ✅ 0 errori
Voice tests: ✅ 1263 PASS / 0 FAIL
```

## Roadmap
| Fase | Task | Status |
|------|------|--------|
| F05 | LicenseManager UI | ✅ DONE |
| F04 | Schede Mancanti | ✅ DONE |
| Kaggle | 8 mockup UI FLUX.1-schnell | ✅ DONE |
| **F06** | **Media Upload in Schede** | **🔄 NEXT** |
| F10 | CI/CD GitHub Actions | ⏳ |
| F07 | LemonSqueezy payment | ⏳ |

---

## PROMPT RIPARTENZA SESSIONE 29

```
Sessione 29 — F06 Media Upload Sprint A

1. Leggi HANDOFF.md + MEMORY.md (già caricata)
2. Leggi .claude/cache/agents/schede-media-upload-research.md (research già completa)
3. Esegui /gsd:plan-phase per F06 Media Upload Sprint A

Acceptance Criteria Sprint A (P0):
- Migration 030 cliente_media + ALTER TABLE clienti → registrata in lib.rs
- 5 Rust commands: save_media_image, save_media_video, get_cliente_media, delete_media, read_media_file
- MediaUploadZone.tsx — drag-drop, compressione canvas, HEIC support
- MediaGallery.tsx + MediaLightbox.tsx — griglia thumbnail + lightbox
- MediaConsentModal.tsx — GDPR obbligatorio foto cliniche
- Integrazione SchedaParrucchiere (tab Trasformazioni) + SchedaMedica (Immagini Cliniche)
- npm run type-check → 0 errori

Architettura già decisa (da research):
- Storage: AppData/fluxion/media/clienti/{id}/foto|video/ — path relativo in DB
- Serving: convertFileSrc() → asset:// URL (no base64 in RAM)
- Compressione: canvas API JS → max 1200px, 85% JPEG
- GDPR: 3 livelli (interno/social/clinico con firma obbligatoria)
- Migration runner: CUSTOM in lib.rs — aggiungere blocco 030 esplicitamente

CoVe 2026: research già fatta, procedi direttamente con PLAN → IMPLEMENT → VERIFY → DEPLOY
```
