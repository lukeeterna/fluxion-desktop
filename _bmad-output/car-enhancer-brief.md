# CAR ENHANCER — Project Brief per Claude Code
> CoVe 2026 Research completa. Claude Code: leggi tutto prima di scrivere una riga di codice.
> Data: 2026-03-06

---

## 1. MISSIONE

Sistema di uso **personale** (no SaaS, no API pubblica) per:

1. **Enhancement** immagini auto alta fascia (4K upscaling + detail enhancement)
2. **Watermark removal** da immagini acquisite da internet/fornitori
3. **Background replacement** — nuovo sfondo senza alterare l'auto, enfatizzando bellezza
4. **Video 360° orbitale** da singola foto — presentazioni cliente d'impatto

**NON trasformare l'auto** — l'auto deve rimanere identica. Solo migliorare, non modificare.

---

## 2. HARDWARE DISPONIBILE

| Machine | Ruolo | Note |
|---------|-------|-------|
| MacBook (M-series) | Sviluppo, preprocessing leggero | MPS backend PyTorch |
| iMac (192.168.1.12) | Processing medio, server locale | GPU: **verificare** con `system_profiler SPDisplaysDataType` |
| Kaggle (P100 16GB) | Modelli pesanti (SV3D, FLUX) | 30GB RAM, 60min timeout |

**IMPORTANTE iMac**: Prima di tutto eseguire `system_profiler SPDisplaysDataType | grep "VRAM"` per sapere la VRAM disponibile. Questo determina quali modelli girano in locale vs Kaggle.

---

## 3. COVE 2026 RESEARCH — STATO DELL'ARTE

### 3.1 Segmentazione Auto (fondamentale per tutto)

**Winner 2025-2026: BiRefNet-v2**
- HuggingFace: `ZhengPeng7/BiRefNet` e `ZhengPeng7/BiRefNet-v2`
- Training: HRSOD + DIS dataset — ottimizzato per oggetti strutturati (veicoli, prodotti)
- Performance: supera SAM2 su veicoli, ~370MB, GPU ~0.1s, CPU ~2s
- `rembg -m birefnet-hrsod input.jpg output.png` — zero code required

**Alternativa interattiva: SAM2** (Segment Anything 2, Meta 2024)
- Utile se serve selezione manuale su parti specifiche (cromature, vetri)
- Più pesante (600MB+), richiede prompt click/box

**NON usare**: modelli generici u2net, u2netp — obsoleti per auto

### 3.2 Watermark Removal

**Winner: IOPaint con modello LaMa**
```bash
pip install iopaint
iopaint start --model=lama --device=cuda --port=8080
```
- LaMa (Large Mask): migliore per watermark testo/logo su superfici uniformi
- MAT (Mask-Aware Transformer): migliore per watermark su texture complesse (cofano, cerchi)
- Ha UI web e REST API — perfetto per automazione

**Per watermark ostinati**: SDXL Inpainting con reference image
- `stabilityai/stable-diffusion-xl-refiner-1.0` inpainting mode
- Il modello "ricostruisce" la texture dell'auto sotto il watermark

**CRITICO**: sempre mascherare SOLO il watermark, mai l'auto. BiRefNet + manual mask refinement.

### 3.3 Background Replacement — Pipeline Corretta

**Il problema principale**: quando si cambia sfondo, la LUCE sull'auto non matcha il nuovo sfondo.
Senza relighting: risultato finto anche con segmentazione perfetta.

**Pipeline raccomandata** (in ordine):
```
1. BiRefNet → maschera auto precisa
2. Estrai auto su trasparente (RGBA PNG)
3. Scegli sfondo (foto reale o generato)
4. IC-Light → reilumina l'auto per matchare lo sfondo scelto
5. Compositing finale + color grading
```

**Modelli chiave**:
- **FLUX.1-fill-dev** (`black-forest-labs/FLUX.1-fill-dev`) — inpainting sfondo generativo
  - Dato: auto + maschera sfondo → genera ambiente realistico intorno all'auto
  - Miglior inpainting 2025, supera SDXL XL inpainting
  - Requires: 16GB VRAM (Kaggle) o sequential offload
- **IC-Light** (`lllyasviel/ic-light`) — KILLER FEATURE per realismo
  - Reilumina foreground (auto) per matchare background lighting
  - ~4GB VRAM, gira su iMac se ha GPU
  - Senza IC-Light: risultato sempre "fotomontaggio"
  - Con IC-Light: risultato fotografico
- **ControlNet Canny** — mantiene contorni esatti auto durante inpainting sfondo

**Sfondi pre-definiti utili** (per auto alta fascia):
- Studio fotografico neutro (grigio/bianco)
- Strada asfaltata notturna con riflessi
- Montagna/paesaggio drammatico
- Pista racing

### 3.4 Enhancement e Upscaling

| Modello | Use Case | VRAM | Note |
|---------|----------|------|------|
| **Real-ESRGAN x4plus** | Upscaling 4K base | 4GB | Veloce, affidabile |
| **Clarity Upscaler** (SDXL-based) | Detail enhancement fotografico | 8GB | Miglior qualità per auto |
| **SUPIR** | Massima qualità | 24GB | Solo Kaggle/cloud |
| **SwinIR** | Rimozione rumore/JPEG artifacts | 2GB | Preprocessing prima di upscale |

**Pipeline enhancement raccomandata**:
```
1. SwinIR → rimuovi JPEG artifacts
2. Real-ESRGAN x4 → porta a 4K
3. Clarity Upscaler (img2img 0.3 denoise) → aggiungi dettagli fotografici
```

**Clarity Upscaler HuggingFace Space**: `philz1337x/clarity-upscaler` — già deployment, usabile via API gratuita

### 3.5 Video 360° Orbitale

**Winner 2024-2025: SV3D (Stable Video 3D)**
- HuggingFace: `stabilityai/sv3d`
- Input: 1 foto auto (square 576x576)
- Output: video 21 frame, orbita 360° completa, 6 secondi
- VRAM: 20GB+ full quality, ~12GB con sequential offload (P100 possibile)
- Limitazione: input DEVE essere square, auto centrata su sfondo semplice

**Post-processing video**:
```
1. SV3D → 21 frame PNG
2. Real-ESRGAN → upscale ogni frame (batch)
3. FFMPEG → stitch in MP4/WebM a 60fps (interpolazione)
4. Opzionale: aggiungere sottofondo audio
```

**Alternativa più leggera: Zero123++**
- HuggingFace: `sudo-ai/zero123plus-v1.2`
- Output: 6 viewpoint fissi (non video fluido)
- ~8GB VRAM — gira su iMac se ha GPU discreta
- Buono per still multi-view, non per video orbitale fluido

**Alternativa avanzata: TripoSG (2025)**
- Immagine → mesh 3D → render 360° con materiali
- Qualità superiore ma richiede pipeline 3D rendering (Blender headless)
- Raccomandato SOLO se il progetto scala a uso professionale

---

## 4. DECISIONI CHE CLAUDE CODE DEVE PRENDERE

Claude Code: scegli l'architettura migliore basandoti sulle constraint. Considera:

### 4.1 UI/UX
- **Gradio** — più veloce da implementare, ottimo per uso personale, no frontend
- **FastAPI + HTML** — più flessibile, batch processing, REST API locale
- **CLI scripts** — minimo codice, massimo controllo, perfetto se usi sempre stesse pipeline

**Suggerimento**: Gradio per prototype rapido. Se il workflow diventa ripetitivo, migra a CLI scripts con config YAML.

### 4.2 Struttura Progetto
Decidi tu. Criteri da rispettare:
- Ogni pipeline (segment, watermark, background, enhance, video360) = modulo indipendente
- Config in YAML (paths, model choices, quality settings)
- Output sempre in folder datata (non sovrascrivere originali MAI)
- Log di ogni operazione con timestamp

### 4.3 Quale modello per quale task in locale vs Kaggle
Dipende dalla VRAM iMac (verificare prima). Regola generale:
- <4GB VRAM: tutto su Kaggle tranne BiRefNet e LaMa
- 4-8GB VRAM: locale per segment + watermark + enhance, Kaggle per FLUX + SV3D
- >8GB VRAM: quasi tutto locale tranne SV3D

### 4.4 Gestione Kaggle automatica
Se serve Kaggle per modelli pesanti:
- Script Python che fa push notebook + polling status + download output
- Pattern già provato nel progetto FLUXION (vedi storico errori P100 sotto)

---

## 5. STORICO ERRORI P100 KAGGLE (NON RIPETERE)

**Hardware Kaggle**: Tesla P100-PCIE 15.89GB VRAM, 30GB RAM, Python 3.12

| # | Errore | Causa | Fix |
|---|--------|-------|-----|
| 1 | OOM durante quantization T5 8-bit | T5-XXL 8-bit richiede >5GB VRAM per quantization, ma dopo transformer ne restano solo 5GB | Carica T5 su CPU senza quantization |
| 2 | `cublasLt error` con 8-bit matmul | P100 CC6.0 non supporta cublasLt per certe shape | Non usare bitsandbytes su P100 — usa float16 + sequential_cpu_offload |
| 3 | `Int8Params error` | transformers 5.x incompatibile con bitsandbytes | Pin `transformers==4.46.3` |
| 4 | `NF4 cublasLt error` | 4-bit NF4 non supportato P100 CC6.0 | Non usare NF4 su P100 |
| 5 | RAM OOM (T5 + transformer insieme) | T5 (10GB) + transformer (24GB) > 30GB RAM | Pre-encode con T5, del T5, poi carica transformer |
| 6 | Device mismatch CPU/CUDA | device_map={"": "cpu"} senza confini non aggiunge hooks | Usa AlignDevicesHook manuale o pre-encoding pattern |

**Pattern vincente per P100 con modelli grandi** (testato v19):
```python
# 1. Carica text encoder su CPU → encode → del text_encoder
# 2. Carica modello generativo float16 + enable_sequential_cpu_offload()
# 3. Genera passando embeddings pre-calcolati
# ZERO bitsandbytes = ZERO cublasLt issues
```

---

## 6. DIPENDENZE CHIAVE

```txt
# Core
torch>=2.1.0
torchvision
Pillow>=10.0
numpy>=1.24

# Segmentazione
rembg[gpu]>=2.0.57          # BiRefNet backend

# Inpainting/Watermark
iopaint>=1.3.0               # LaMa + MAT

# Diffusion (background gen + enhancement)
diffusers>=0.30.0
transformers==4.46.3         # PIN: 5.x breaks bitsandbytes if used
accelerate>=0.34.0

# Video
imageio[ffmpeg]
ffmpeg-python

# UI (scegliere)
gradio>=4.0.0                # se si sceglie Gradio
# oppure: fastapi, uvicorn   # se si sceglie FastAPI

# Utility
tqdm
pyyaml
python-dotenv
```

---

## 7. WORKFLOW TIPICO (esempio)

```
Input: foto.jpg (auto Porsche 911 con watermark di agenzia)

STEP 1 — Watermark Removal
  IOPaint/LaMa → maschera watermark manuale → foto_clean.jpg

STEP 2 — Segmentazione
  BiRefNet → foto_clean.jpg → auto_mask.png + auto_rgba.png

STEP 3 — Enhancement originale
  SwinIR → Real-ESRGAN x4 → Clarity → foto_4k.jpg

STEP 4 — Background Replacement
  Scegli: studio / strada / montagna / custom
  IC-Light (relighting) → FLUX.1-fill inpainting → foto_sfondo.jpg

STEP 5 — Video 360°
  SV3D (Kaggle) → 21 frame → Real-ESRGAN batch → FFMPEG → video360.mp4

Output:
  /output/2026-03-06/
    foto_4k.jpg
    foto_sfondo_studio.jpg
    foto_sfondo_strada.jpg
    video360.mp4
```

---

## 8. QUALITY GATES (Acceptance Criteria)

- [ ] Maschera auto: zero pixel auto tagliati, zero sfondo residuo nei pannelli
- [ ] Watermark removal: invisible join, nessuna traccia visibile anche a 200% zoom
- [ ] Background replacement: lighting auto matcha sfondo (IC-Light verificabile visivamente)
- [ ] Enhancement: nessun artefatto, dettagli cromature, vernice, vetri migliorati
- [ ] Video 360°: orbita fluida, auto non deformata, output >=720p

---

## 9. NON FARE

- NON alterare proporzioni/forma dell'auto
- NON modificare il colore carrozzeria (a meno di richiesta esplicita)
- NON sovrascrivere file originali (sempre output in cartella separata)
- NON usare bitsandbytes su P100 (cublasLt errors CC6.0)
- NON caricare T5 + transformer contemporaneamente in RAM (30GB limit)
