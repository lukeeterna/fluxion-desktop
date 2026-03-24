# Video Pipeline Composition Research — CoVe 2026
> **Data**: 2026-03-23 | **Obiettivo**: Pipeline produzione video promozionale ~4min
> **Contesto**: FLUXION gestionale PMI italiane — combinare AI footage + screenshot app

---

## 1. HYBRID PIPELINE: AI Footage + Screenshot Compositing

### 1A. Approccio Raccomandato: Image-to-Video + Compositing

Il workflow 2026 gold standard e':

```
FASE 1: Generare still frame (Flux/DALL-E/Midjourney)
   ↓ immagini statiche alta qualita' di scene PMI italiane
FASE 2: Animare con Image-to-Video (Kling/Seedance/Luma)
   ↓ clip 5-10s con movimento realistico
FASE 3: Compositing finale (Remotion o MoviePy + FFmpeg)
   ↓ sovrapporre screenshot app, transizioni, voiceover
FASE 4: Export finale H.264
```

### 1B. Tecniche di Compositing Screenshot nell'AI Footage

**Picture-in-Picture (PiP) — App su schermo laptop/tablet:**
- Generare immagine AI di persona davanti a laptop/tablet con schermo visibile
- In post: sovrapporre screenshot FLUXION nello spazio schermo
- FFmpeg overlay filter: `[0:v][1:v]overlay=x:y:enable='between(t,start,end)'`
- Per prospettiva realistica: OpenCV `cv2.getPerspectiveTransform()` + `cv2.warpPerspective()`

**Split Screen — B-roll a sinistra, App a destra:**
- Dividere il frame 60/40: scena PMI | screenshot FLUXION
- Piu' semplice da implementare, molto usato nei SaaS demo
- FFmpeg: `[0:v]crop=iw*0.6:ih:0:0[left];[1:v]scale=w*0.4:h[right];[left][right]hstack`

**Transizioni tra B-roll e Screenshot:**
- Crossfade 0.5-1s tra clip AI e screenshot full-screen
- Wipe/slide: screenshot scivola dentro da destra sopra il B-roll
- Zoom-in: dal B-roll si zooma verso lo schermo → diventa screenshot full

### 1C. Consistenza Visiva tra Clip AI

Per mantenere stile coerente tra tutti i clip:
1. **Reference image**: generare UN'immagine reference per ogni verticale, usarla come base
2. **Prompt template fisso**: stessa struttura prompt per ogni scena
3. **Lighting consistency**: specificare SEMPRE lo stesso tipo di illuminazione
4. **Color grading finale**: applicare LUT uniforme in post-produzione
5. **Multi-shot storyboard** (Kling 3.0): mantiene personaggi coerenti tra scene

---

## 2. STRUMENTI VIDEO EDITING PROGRAMMATICI

### 2A. Remotion (RACCOMANDATO per FLUXION)

| Aspetto | Dettaglio |
|---------|-----------|
| **Costo** | GRATIS per team <=3 persone (perfect per FLUXION) |
| **Stack** | React 19 + TypeScript (GIA' il nostro stack!) |
| **Rendering** | Locale, nessun cloud necessario |
| **Transizioni** | `<TransitionSeries>` con crossfade, slide, wipe built-in |
| **Overlay** | `<AbsoluteFill>` per PiP, sovrapposizioni, watermark |
| **Audio** | Supporto nativo MP3/WAV con sync frame-preciso |
| **Subtitles** | Componenti React per sottotitoli animati |
| **Export** | MP4 H.264, WebM, ProRes |

**Vantaggi specifici per FLUXION:**
- Scritto in React/TS = il team lo conosce gia'
- Versione controllabile con Git
- Parametrizzabile: cambiare screenshot/voiceover senza riscrivere
- Locale, zero costi cloud
- Preview in browser durante sviluppo

**Struttura progetto Remotion per FLUXION:**
```
fluxion-video/
  src/
    Root.tsx              # Composizioni registrate
    scenes/
      HookScene.tsx       # Scena 1: B-roll + screenshot blur
      DashboardScene.tsx  # Dashboard reveal
      CalendarScene.tsx   # Calendario demo
      SaraScene.tsx       # Voice agent demo
      PricingScene.tsx    # Confronto prezzo
      CTAScene.tsx        # Call to action finale
    components/
      ScreenshotFrame.tsx # Screenshot in cornice laptop/tablet
      LogoWatermark.tsx   # Logo overlay persistente
      SubtitleBar.tsx     # Sottotitoli animati bottom
      TransitionWipe.tsx  # Transizioni custom
    assets/
      screenshots/        # Screenshot FLUXION
      ai-clips/           # B-roll AI generati
      voiceover.mp3       # Audio Edge-TTS
```

### 2B. MoviePy (Python — alternativa valida)

| Aspetto | Dettaglio |
|---------|-----------|
| **Costo** | GRATIS, open source (MIT) |
| **Versione** | 2.2.1 (2026) |
| **Compositing** | `CompositeVideoClip` per overlay multipli |
| **PiP** | Nativo con `.set_position()` e `.resize()` |
| **Transizioni** | crossfadein/crossfadeout, fadein/fadeout |
| **Limite** | NO perspective transform nativo (serve OpenCV) |

**Pipeline MoviePy + OpenCV per screen mockup:**
```python
import cv2
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

# 1. Caricare B-roll AI (persona con laptop)
broll = VideoFileClip("ai-salon-laptop.mp4")

# 2. Perspective transform screenshot → schermo laptop
screenshot = cv2.imread("dashboard.png")
pts_src = np.float32([[0,0], [1920,0], [1920,1080], [0,1080]])
pts_dst = np.float32([[420,180], [1120,195], [1100,680], [440,665]])  # coordinate schermo nel B-roll
M = cv2.getPerspectiveTransform(pts_src, pts_dst)
warped = cv2.warpPerspective(screenshot, M, (1920,1080))

# 3. Compositing
overlay = ImageClip(warped).with_duration(broll.duration)
final = CompositeVideoClip([broll, overlay])
```

### 2C. FFmpeg (per assemblaggio finale)

FFmpeg resta indispensabile per:
- Concat demuxer (unire clip)
- Crossfade tra scene: `xfade=transition=fade:duration=0.5:offset=X`
- Overlay watermark logo
- Encoding finale H.264 High Profile

**Comando PiP FFmpeg:**
```bash
ffmpeg -i broll.mp4 -i screenshot.png \
  -filter_complex "[1:v]scale=640:360[pip];[0:v][pip]overlay=W-w-20:H-h-20:enable='between(t,5,15)'" \
  -c:v libx264 -crf 18 output.mp4
```

### 2D. Shotstack (scartato)

- Free tier: solo 20 min/mese, watermark
- Rendering cloud (dipendenza esterna)
- $0.20/min per produzione — viola guardrail ZERO COSTI
- **Verdetto: SCARTATO**

### 2E. Creatomate (scartato)

- Free tier: solo 50 credits iniziali (non rinnovabili)
- Credit-based pricing
- **Verdetto: SCARTATO**

---

## 3. IMAGE-TO-VIDEO: Workflow e Confronto Qualita'

### 3A. Pipeline Raccomandata

```
STEP 1: Flux Schnell (free, Apache 2.0)
   → Generare still frame ad alta qualita'
   → 4-8 step, velocissimo
   → Prompt specifici per scene PMI italiane

STEP 2: Seedance 2.0 (free tier: 100 crediti/giorno)
   → Image-to-video, 1080p, NO watermark
   → Uso commerciale consentito
   → Clip 5-10 secondi per immagine
   → Accesso a 10+ modelli (Kling, Wan, Veo 3, Sora 2)

FALLBACK: Kling AI (free: 66 crediti/giorno)
   → Image-to-video 720p
   → Watermark su free tier
   → Buona qualita' movimenti umani
```

### 3B. Confronto Qualita' Image-to-Video (2026)

| Strumento | Qualita' | Risoluzione Free | Watermark Free | Commerciale Free | Clip Max |
|-----------|----------|-----------------|----------------|-----------------|----------|
| **Seedance 2.0** | 9/10 | 1080p | NO watermark | SI | 5-10s |
| **Kling 2.6/3.0** | 9/10 | 720p | SI watermark | Limitato | 5-10s |
| **Luma Ray3** | 8.5/10 | 720p | SI watermark | NO | 5s |
| **Runway Gen-4.5** | 9.5/10 | 720p | SI watermark | NO | 10s |
| **Pika** | 7/10 | 720p | NO watermark | SI | 5s |

### 3C. Quanti Clip Servono?

Per un video di ~4 minuti con struttura ibrida:
- **8-12 clip AI** da 5-10s ciascuno (scene PMI: salone, officina, studio medico, palestra)
- **15+ screenshot** app (gia' disponibili in `landing/screenshots/`)
- **Totale B-roll AI necessario**: ~60-90 secondi
- **Con 100 crediti/giorno Seedance**: completabile in 2-3 giorni

### 3D. Tipi di Clip AI Necessari per FLUXION

| # | Scena | Descrizione | Durata |
|---|-------|-------------|--------|
| 1 | Hook | Parrucchiera con mani occupate, telefono che squilla | 8s |
| 2 | Salone | Cliente in poltrona, atmosfera calda, specchio | 6s |
| 3 | Officina | Meccanico sotto auto, mani sporche, telefono lontano | 6s |
| 4 | Studio dentistico | Dentista con paziente, ambiente clinico pulito | 6s |
| 5 | Palestra | Personal trainer con cliente, energia, spazio moderno | 6s |
| 6 | Reception vuota | Banco reception vuoto, telefono che squilla (problema) | 5s |
| 7 | Persona al laptop | Imprenditore italiano al laptop, sorride (soluzione) | 6s |
| 8 | Tablet in mano | Mani che tengono tablet con schermata (per overlay) | 6s |
| 9 | WhatsApp notifica | Telefono con notifica WhatsApp (conferma prenotazione) | 5s |
| 10 | Fine giornata | Imprenditore soddisfatto, chiude negozio, tramonto | 6s |

---

## 4. PROMPT ENGINEERING per Scene PMI Italiane

### 4A. Template Prompt Universale

```
[SOGGETTO], [AZIONE], Italian small business interior,
warm ambient lighting, modern clean decor,
shot on Sony A7III 35mm f/1.8, shallow depth of field,
natural color grading, 4K cinematic quality,
Mediterranean atmosphere, authentic Italian setting
```

### 4B. Prompt Specifici per Verticale

**Parrucchiere/Salone:**
```
Italian female hairstylist in her 30s cutting hair of a client in a modern salon,
warm golden lighting, mirrors reflecting, styling tools on counter,
she looks stressed as phone rings on counter, hands occupied with scissors,
shot on Sony A7III 35mm f/1.8, shallow depth of field,
authentic Italian hair salon interior, marble counter, elegant decor
```

**Officina Meccanica:**
```
Italian male mechanic in his 40s working under a car on hydraulic lift,
industrial lighting, tools organized on red pegboard wall,
grease-stained hands, phone buzzing on workbench out of reach,
shot on Canon R5 24mm f/2.8, industrial interior,
authentic Italian auto repair shop, well-organized garage
```

**Studio Odontoiatrico:**
```
Italian female dentist in white coat examining patient in modern dental chair,
bright clinical lighting, dental equipment visible, clean white interior,
tablet on desk showing patient records,
shot on Sony A7III 50mm f/1.4, professional medical setting,
modern Italian dental clinic, calming blue-white color scheme
```

**Palestra/Fitness:**
```
Italian male personal trainer showing exercise to client in modern gym,
natural daylight from large windows, equipment in background,
energetic atmosphere, motivational posters on walls,
shot on Canon R5 35mm f/2.0, dynamic composition,
modern Italian fitness studio, clean minimal design
```

### 4C. Trucchi per Evitare Uncanny Valley

1. **Mai primi piani estremi dei volti** — usare inquadrature medie/ambientali
2. **Movimenti lenti** — camera lenta, slow tracking, evitare gesti rapidi
3. **Focus sulle mani/ambiente** — le mani occupate sono il tema, non i volti
4. **Shallow depth of field** — sfocatura nasconde imperfezioni AI
5. **Illuminazione calda** — la luce calda perdona molto piu' della fredda
6. **Clip corti (5-6s)** — meno tempo = meno probabilita' di artefatti
7. **Niente parlato nei clip AI** — solo B-roll silenzioso, voiceover separato

### 4D. Consistenza tra Clip

- Usare SEMPRE lo stesso seed/style reference quando possibile
- Stessa palette colori: toni caldi mediterranei (#F5E6D3, #D4A574, #8B6914)
- Stessa "camera" in ogni prompt (Sony A7III 35mm)
- Post-produzione: applicare STESSO LUT/color grade a tutti i clip
- FFmpeg color correction: `eq=saturation=1.1:contrast=1.05:brightness=0.02`

---

## 5. PIPELINE COMPLETA RACCOMANDATA

### 5A. Opzione A: Remotion (RACCOMANDATA — Gold Standard)

**Perche' Remotion:**
- Stack identico a FLUXION (React + TypeScript)
- GRATIS per team <=3 persone
- Rendering locale, zero cloud
- Compositing programmatico = riproducibile, versionabile
- Preview in browser = iterazione velocissima
- Supporto nativo per overlay, transizioni, audio sync

**Pipeline End-to-End:**

```
GIORNO 1: Preparazione Assets (4h)
├── Generare 10 still frame con Flux Schnell (30min)
├── Animare con Seedance 2.0 → 10 clip 5-8s (2h, batch)
├── Generare voiceover Edge-TTS IsabellaNeural (30min)
├── Generare sottotitoli SRT con Edge-TTS (automatico)
└── Preparare screenshot FLUXION (gia' pronti)

GIORNO 2: Progetto Remotion (6h)
├── Setup progetto: npx create-video@latest (10min)
├── Creare componenti scena (15 scene) (3h)
├── Implementare transizioni crossfade (1h)
├── Logo watermark overlay (30min)
├── Sottotitoli animati (1h)
└── Preview e fine-tuning (30min)

GIORNO 3: Rendering + Polish (3h)
├── Render locale MP4 H.264 1080p (30min)
├── Review e fix eventuali (1.5h)
├── Export finale con chapters metadata (30min)
└── Upload YouTube + ottimizzazione SEO (30min)

TOTALE: ~13h su 3 giorni
```

**Setup Remotion:**
```bash
npx create-video@latest fluxion-promo
cd fluxion-promo
npm i  # gia' include tutto
# Preview: npx remotion studio
# Render: npx remotion render src/index.ts MainVideo out/fluxion-promo.mp4
```

### 5B. Opzione B: MoviePy + FFmpeg (Fallback Python)

**Perche' sceglierla:**
- Se si vuole restare 100% Python (coerenza con voice-agent)
- Piu' semplice per chi non vuole un progetto React separato
- Meno elegante ma funzionale

**Pipeline:**
```python
# pipeline.py
from moviepy import *
import edge_tts, asyncio

# 1. Generare voiceover
async def generate_voiceover(text, output):
    tts = edge_tts.Communicate(text, "it-IT-IsabellaNeural", rate="-5%")
    await tts.save(output)

# 2. Per ogni scena: creare clip
scenes = [
    {"type": "ai", "file": "ai-clips/salon-phone.mp4", "duration": 8},
    {"type": "screenshot", "file": "screenshots/01-dashboard.png", "duration": 12},
    # ...
]

clips = []
for scene in scenes:
    if scene["type"] == "ai":
        clip = VideoFileClip(scene["file"]).subclipped(0, scene["duration"])
    else:
        clip = ImageClip(scene["file"]).with_duration(scene["duration"])
    clips.append(clip)

# 3. Transizioni crossfade
from moviepy.video.compositing import transitions
final_clips = []
for i, clip in enumerate(clips):
    if i > 0:
        clip = clip.crossfadein(0.5)
    final_clips.append(clip)

# 4. Compositing con overlay
video = CompositeVideoClip(final_clips)
logo = ImageClip("logo.png").with_duration(video.duration).with_position(("left","top")).resized(0.15).with_opacity(0.7)
final = CompositeVideoClip([video, logo])

# 5. Aggiungere audio
voiceover = AudioFileClip("voiceover.mp3")
final = final.with_audio(voiceover)

# 6. Export
final.write_videofile("fluxion-promo.mp4", fps=30, codec="libx264",
                      audio_codec="aac", bitrate="8000k")
```

### 5C. Opzione C: Puro FFmpeg (Minimalista)

Simile a V4 screenplay attuale ma con AI B-roll intercalato:
```bash
# Concatenare alternando B-roll AI e screenshot
ffmpeg -i broll1.mp4 -loop 1 -t 12 -i screenshot1.png -i broll2.mp4 ... \
  -filter_complex "
    [0:v]scale=1920:1080[v0];
    [1:v]scale=1920:1080[v1];
    [v0][v1]xfade=transition=fade:duration=0.5:offset=8[vt1];
    ..." \
  -c:v libx264 -crf 18 output.mp4
```

### 5D. Confronto Opzioni

| Criterio | Remotion | MoviePy | FFmpeg puro |
|----------|----------|---------|-------------|
| **Costo** | GRATIS | GRATIS | GRATIS |
| **Qualita'** | Eccellente | Buona | Buona |
| **Flessibilita'** | Massima | Alta | Media |
| **Compositing** | Nativo React | Con OpenCV | Limitato |
| **Transizioni** | 20+ built-in | Base | xfade filter |
| **PiP/Overlay** | Triviale (JSX) | Buono | Complesso |
| **Sottotitoli** | Animati custom | Semplici | Basici |
| **Preview** | Browser live | No | No |
| **Curva apprendimento** | Media (React) | Bassa (Python) | Alta (filtergraph) |
| **Riproducibilita'** | Git-versionabile | Script Python | Script bash |
| **Tempo setup** | 2h | 1h | 30min |

---

## 6. STRUTTURA VIDEO 4 MINUTI (Evoluzione da V4)

### Struttura Raccomandata

```
0:00-0:15  HOOK          — B-roll AI: mani occupate, telefono squilla (PROBLEMA)
0:15-0:30  AGITAZIONE    — B-roll AI: reception vuota + numeri sovrapposti (COSTO)
0:30-0:50  SOLUZIONE     — Transizione a screenshot Dashboard (REVEAL)
0:50-1:10  CALENDARIO    — Screenshot + mini B-roll tablet in mano
1:10-1:30  CLIENTI       — Screenshot rubrica + B-roll salone
1:30-1:50  VERTICALE 1   — Parrucchiere: B-roll → screenshot scheda
1:50-2:10  VERTICALE 2   — Officina: B-roll → screenshot veicoli
2:10-2:30  VERTICALE 3   — Dentista: B-roll → screenshot odontoiatrica
2:30-2:50  SARA VOICE    — Screenshot + B-roll persona che riceve WhatsApp
2:50-3:10  SARA COSTO    — Split screen: receptionist vs Sara
3:10-3:25  CASSA+REPORT  — Screenshot cassa → analytics
3:25-3:45  PREZZO        — Grafica confronto abbonamento vs lifetime
3:45-4:00  CTA           — B-roll imprenditore soddisfatto + logo FLUXION
```

### YouTube Chapters
```
0:00 Il problema che ti costa 7.500 euro all'anno
0:30 FLUXION: tutto in un colpo d'occhio
0:50 Calendario intelligente
1:10 Rubrica clienti completa
1:30 Schede verticali personalizzate
2:30 Sara: la tua receptionist AI
3:10 Cassa e report
3:25 Quanto costa (spoiler: meno di 3 settimane di incassi)
3:45 Provalo ora - 30 giorni garantiti
```

---

## 7. COSTI TOTALI

| Voce | Costo |
|------|-------|
| Flux Schnell (immagini) | GRATIS (Apache 2.0, HuggingFace) |
| Seedance 2.0 (image-to-video) | GRATIS (100 crediti/giorno, commerciale OK) |
| Remotion (compositing) | GRATIS (team <=3) |
| Edge-TTS (voiceover) | GRATIS (no API key) |
| FFmpeg (encoding) | GRATIS (open source) |
| **TOTALE** | **EUR 0** |

---

## 8. QUALITA' ATTESA

- **B-roll AI**: 8-9/10 con Seedance 2.0 a 1080p — realistico se inquadrature medie
- **Compositing**: 9/10 con Remotion — transizioni professionali, overlay precisi
- **Voiceover**: 8/10 con IsabellaNeural — naturale, buona prosodia italiana
- **Risultato complessivo**: Paragonabile a video SaaS da $2-5K budget
- **Limite**: i clip AI NON reggono primi piani volti o movimenti rapidi
- **Mitigazione**: usare B-roll come "atmosfera", screenshot come "sostanza"

---

## 9. RACCOMANDAZIONE FINALE

### Pipeline Gold Standard per FLUXION:

```
Flux Schnell (still) → Seedance 2.0 (animate) → Remotion (compose) → MP4
                                                      ↑
                                          Edge-TTS voiceover + SRT
                                          Screenshot FLUXION reali
                                          Logo watermark
                                          Transizioni crossfade
```

**Remotion e' la scelta ottimale** perche':
1. **GRATIS** per team <=3 (guardrail zero costi rispettato)
2. **React + TypeScript** = stesso stack di FLUXION
3. **Compositing nativo** per overlay screenshot su B-roll AI
4. **Preview browser** per iterazione rapida
5. **Git-versionabile** = riproducibile al 100%
6. **Sottotitoli animati** personalizzabili in JSX
7. **Transizioni professionali** built-in

**Timeline realistica**: 3 giorni lavorativi (13h totali)
- Giorno 1: Generare assets (immagini AI, animarle, voiceover)
- Giorno 2: Progetto Remotion (scene, transizioni, overlay)
- Giorno 3: Render, review, upload YouTube

---

## FONTI

- [Remotion — Make videos programmatically](https://www.remotion.dev/)
- [Remotion License — Free for <=3 people](https://www.remotion.dev/docs/license)
- [Remotion Transitions](https://www.remotion.dev/docs/transitioning)
- [Remotion Overlays](https://www.remotion.dev/docs/overlay)
- [Claude + Remotion tutorial](https://dev.to/mayu2008/new-clauderemotion-to-create-amazing-videos-using-ai-37bp)
- [MoviePy — Python video editing](https://github.com/Zulko/moviepy)
- [Seedance AI — Free 1080p no watermark](https://www.seedance.tv/blog/ai-video-generator-free-no-limits)
- [Kling AI Pricing Guide 2026](https://aitoolanalysis.com/kling-ai-pricing/)
- [Luma Dream Machine Plans](https://lumalabs.ai/pricing)
- [Flux Schnell on HuggingFace](https://huggingface.co/black-forest-labs/FLUX.1-schnell)
- [AI Multi-Shot Consistency Guide](https://www.aimagicx.com/blog/ai-multi-shot-video-character-consistency-2026)
- [Veo 3.1 Prompting Guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [AI B-Roll Generation Blueprint 2026](https://www.aifire.co/p/generate-professional-ai-b-roll-footage-2026-blueprint)
- [FFmpeg Picture-in-Picture](https://ffmpeg-api.com/learn/ffmpeg/recipe/picture-in-picture)
- [Shotstack Pricing](https://shotstack.io/pricing/)
- [Best Video Editing APIs 2026](https://www.plainlyvideos.com/blog/best-video-editing-api)
- [Image-to-Video Comparison 2026](https://www.clipcat.com/blog/top-6-image-to-video-ai-generators-in-2025-a-side-by-side-comparison/)
- [Edge-TTS GitHub](https://github.com/rany2/edge-tts)
