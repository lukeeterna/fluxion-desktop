# Video Editing Best Practices 2026 — Gold Standard Mondiale per Demo Software Gestionale

> **Data ricerca**: 2026-03-21
> **Obiettivo**: Stato dell'arte MONDIALE del video editing applicato a demo di software gestionale PMI
> **Budget target**: ZERO euro — solo strumenti gratuiti (ffmpeg, Pillow, Edge-TTS)
> **Uso**: Guida operativa con comandi copia-incolla per produrre video demo FLUXION

---

## 1. MOTION DESIGN per Software Demo — Stato dell'Arte 2026

### 1.1 Ken Burns: Morto o Vivo?

Ken Burns (zoom lento + pan) **NON e morto** ma e evoluto. Nel 2026:
- **Uso corretto**: Background ambientali, screenshot statici che devono "vivere"
- **Uso SBAGLIATO**: Come unica tecnica — sembra un slideshow PowerPoint del 2010
- **Evoluzione 2026**: Ken Burns + parallax + easing curves (ease-in-out invece di linear)

**Regola**: Ken Burns va usato come **una** delle tecniche, mai come la sola. Alternare con zoom rapidi, transizioni xfade, e split screen.

### 1.2 Transizioni tra Schermate — Ranking Efficacia 2026

| Transizione | Efficacia | Quando usarla | ffmpeg |
|-------------|-----------|---------------|--------|
| **Dissolve/Crossfade** | 9/10 | Tra schermate dello STESSO flusso | `xfade=transition=dissolve` |
| **Slide Left/Right** | 8/10 | Tra schermate di flussi DIVERSI | `xfade=transition=slideleft` |
| **Fade to Black** | 7/10 | Cambio di sezione/capitolo | `xfade=transition=fadeblack` |
| **Wipe** | 6/10 | Before/After comparisons | `xfade=transition=wipeleft` |
| **Zoom In → Dissolve → Zoom Out** | 10/10 | Transizione premium (Notion-style) | Custom filter chain |
| **Cut secco** | 7/10 | Ritmo veloce, feature highlights | Nessun filtro |
| **Radial** | 5/10 | Raramente — effetto "retro" | `xfade=transition=radial` |

**Gold standard 2026**: Alternare dissolve (80% delle transizioni) con slide (15%) e fade-to-black (5% — solo cambio sezione).

### 1.3 Zoom su Feature Specifiche — Senza Vibrazione

**Il problema**: `zoompan` di ffmpeg produce jitter/vibrazione perche arrotonda i pixel.

**La soluzione**: Pre-scale l'immagine a risoluzione altissima, poi usa zoompan.

```bash
# ANTI-JITTER: Pre-scale a 8000px, poi zoompan
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=8000:-1,zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p smooth_zoom.mp4
```

**Alternativa senza zoompan** (scale+crop animato):
```bash
# Zoom in progressivo con scale+crop (NO jitter)
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=3840:2160,crop='iw-mod(n*2,400)':'ih-mod(n*2,225)':'mod(n,200)':'mod(n,112.5)'" \
  -t 5 -r 30 -c:v libx264 -pix_fmt yuv420p zoom_crop.mp4
```

**Metodo MIGLIORE per zoom preciso su area specifica**:
```bash
# Zoom su area specifica (es. bottone "Prenota" a coordinate 800,400)
# Step 1: Crea video dalla screenshot full
ffmpeg -loop 1 -i screenshot.png -vf "scale=1920:1080" -t 3 -r 30 full.mp4

# Step 2: Crea video zoommato sull'area target
ffmpeg -loop 1 -i screenshot.png -vf \
  "crop=800:450:400:175,scale=1920:1080" -t 3 -r 30 zoomed.mp4

# Step 3: Transizione dissolve dal full allo zoom
ffmpeg -i full.mp4 -i zoomed.mp4 -filter_complex \
  "xfade=transition=dissolve:duration=0.5:offset=2.5" \
  -c:v libx264 -pix_fmt yuv420p zoom_transition.mp4
```

### 1.4 Parallax Effect su Screenshot

Il parallax simula profondita 3D muovendo layers a velocita diverse.

```bash
# Parallax semplice: sfondo si muove lento, UI si muove veloce
# Richiede 2 layer: background (sfondo blur) + foreground (UI)

# Step 1: Crea sfondo blur
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=2200:-1,boxblur=20:20,zoompan=z=1:x='10*sin(2*PI*t/10)':y=0:d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p bg_parallax.mp4

# Step 2: UI in primo piano con movimento opposto
ffmpeg -loop 1 -i screenshot_ui.png -vf \
  "scale=2000:-1,zoompan=z=1:x='iw/2-(iw/2)+20*sin(2*PI*t/10)':y='ih/2-(ih/2)':d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p fg_parallax.mp4

# Step 3: Composita (UI over background)
ffmpeg -i bg_parallax.mp4 -i fg_parallax.mp4 -filter_complex \
  "[1:v]colorkey=0x000000:0.3:0.1[fg];[0:v][fg]overlay=0:0" \
  -c:v libx264 parallax_final.mp4
```

### 1.5 Mockup 3D Device (Laptop con Schermata)

**Strumenti gratuiti per 3D device mockup**:
- **Rotato** (free tier): 9x piu veloce di After Effects per animare screenshot in device 3D
- **Device Frames** (free): Genera mockup 3D con keyframe animation
- **Jitter** (free tier): Template device pre-animati
- **MockRocket** (free): Mockup 3D con animazioni

**Approccio ffmpeg puro** (perspective transform su screenshot):
```bash
# Simula prospettiva 3D con perspective filter (richiede libavfilter compilato con gpl)
# Alternativa: usare Pillow/Python per perspective transform statico,
# poi animare con ffmpeg

# Python (Pillow) per prospettiva 3D:
# from PIL import Image
# img = Image.open('screenshot.png')
# width, height = img.size
# coeffs = find_coeffs(
#     [(0,0),(width,0),(width,height),(0,height)],  # source
#     [(100,50),(width-50,0),(width,height),(50,height-50)]  # dest (perspective)
# )
# img_perspective = img.transform((width,height), Image.PERSPECTIVE, coeffs)
```

### 1.6 Cursor/Click Highlight Animation

```bash
# Metodo 1: Overlay cerchio giallo semi-trasparente su coordinate del click
# Prima crea il cerchio highlight con ffmpeg
ffmpeg -f lavfi -i "color=c=yellow@0.4:s=80x80:d=0.5,format=rgba" \
  -vf "geq=a='if(lt(sqrt((X-40)*(X-40)+(Y-40)*(Y-40)),35),128,0)'" \
  -c:v png cursor_highlight.png

# Overlay con fade in/out su video a coordinate specifiche (es. click a 960,540)
ffmpeg -i screen_recording.mp4 -i cursor_highlight.png -filter_complex \
  "[1:v]fade=in:st=2:d=0.3,fade=out:st=2.5:d=0.3[highlight]; \
   [0:v][highlight]overlay=920:500:enable='between(t,2,3)'" \
  -c:v libx264 highlighted.mp4
```

```bash
# Metodo 2: Drawtext con cerchio pulsante (piu semplice)
ffmpeg -i screen_recording.mp4 -vf \
  "drawbox=x=940:y=520:w=40:h=40:color=yellow@0.5:t=fill:enable='between(t,2,3)', \
   drawbox=x=935:y=515:w=50:h=50:color=yellow@0.3:t=3:enable='between(t,2,3)'" \
  -c:v libx264 click_highlight.mp4
```

### 1.7 Picture-in-Picture (Face Cam)

```bash
# PiP: Video fondatore in basso a destra, ridotto a 1/4
ffmpeg -i screen_recording.mp4 -i facecam.mp4 -filter_complex \
  "[1:v]scale=iw/4:ih/4[pip]; \
   [0:v][pip]overlay=main_w-overlay_w-20:main_h-overlay_h-20" \
  -c:v libx264 -c:a aac pip_output.mp4

# PiP con bordo arrotondato e ombra
ffmpeg -i screen_recording.mp4 -i facecam.mp4 -filter_complex \
  "[1:v]scale=320:240,format=rgba, \
   geq=lum='lum(X,Y)':a='if(gt(abs(X-160)*abs(X-160)+abs(Y-120)*abs(Y-120),14400),0,255)'[pip]; \
   [0:v][pip]overlay=main_w-340:main_h-260" \
  -c:v libx264 pip_rounded.mp4

# PiP con fade in/out
ffmpeg -i screen.mp4 -i facecam.mp4 -filter_complex \
  "[1:v]scale=320:240,fade=in:st=0:d=0.5,fade=out:st=70:d=0.5[pip]; \
   [0:v][pip]overlay=W-w-20:H-h-20:enable='between(t,0,75)'" \
  pip_timed.mp4
```

### 1.8 Motion Graphics Overlay (Lottie-style con ffmpeg)

Per overlay animati senza After Effects:
```bash
# Overlay PNG animato (sequenza di frame) su video
# Prerequisito: esportare animazione Lottie come sequenza PNG con lottie-to-png
ffmpeg -i screen.mp4 -framerate 30 -i 'animation_frame_%04d.png' -filter_complex \
  "[1:v]scale=200:-1[anim]; \
   [0:v][anim]overlay=50:50:shortest=1" \
  -c:v libx264 with_animation.mp4

# Alternativa: testo animato come "motion graphic" leggero
ffmpeg -i screen.mp4 -vf \
  "drawtext=text='FLUXION':fontsize=48:fontcolor=white@0.8: \
   x='if(lt(t,1),W-t*W,0)':y=50:fontfile=/System/Library/Fonts/Helvetica.ttc: \
   enable='between(t,0,3)', \
   drawtext=text='Gestionale PMI':fontsize=28:fontcolor=white@0.6: \
   x='if(lt(t-0.3,1),W-(t-0.3)*W,0)':y=110:fontfile=/System/Library/Fonts/Helvetica.ttc: \
   enable='between(t,0.3,3.3)'" \
  -c:v libx264 motion_text.mp4
```

---

## 2. BENCHMARK Leader Mondiali — Analisi Dettagliata Video Demo

### 2.1 Notion — Maestri del Motion Design Minimalista

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Launch: 2-3 min, Feature: 45-90 sec |
| **Stile transizioni** | Dissolve fluido, zoom cinematografico in/out dall'UI, cursore che si muove con "purpose" |
| **Come mostra l'UI** | Screen recording con dati REALISTICI (non "Lorem Ipsum"), cursore intenzionale, ogni click e significativo |
| **Hook** | Concetto astratto ("Everything you need, in one place") — nessun voice, solo musica + testo |
| **CTA** | Sottile, quasi assente — il prodotto vende se stesso |
| **Tono voce** | Spesso ZERO voiceover. Musica ambient/elettronica + testo overlay minimalista |
| **Lezione FLUXION** | Dati italiani realistici (nomi veri: "Marco Rossi", "Salone Bella"), cursore intenzionale, zero fretta |

### 2.2 Linear — Animazioni Software Ultra-Smooth

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | 30-60 sec per feature, launch 90-120 sec |
| **Stile transizioni** | ZERO transizioni visibili — l'UI si anima come se il software si usasse da solo |
| **Come mostra l'UI** | Sfondo scuro, tipografia monospace, micro-interactions animate (hover, click, drag), suono design |
| **Hook** | Zero intro — dritto nel prodotto, primo frame = UI in azione |
| **CTA** | Tagline finale ("Linear is how modern teams build software") |
| **Tono voce** | ZERO voiceover, ZERO musica (o drone minimale). Sound design: click, whoosh, notification |
| **Lezione FLUXION** | Le micro-animazioni (hover effects, elementi che appaiono) rendono il software "vivo". Troppo freddo per PMI italiane ma la tecnica e oro. |

### 2.3 Arc Browser — Storytelling + Screen Recording Premium

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Vlog: 5-15 min, Launch: 60-90 sec |
| **Stile transizioni** | Cut casuali (vlog-style), split screen, zoom rapidi con motion blur |
| **Come mostra l'UI** | Il CEO usa il browser LIVE alla camera — "Let me show you this..." — demo genuina |
| **Hook** | Persona reale che parla con entusiasmo genuino |
| **CTA** | Community-driven ("Join the waitlist", "Tell us what you think") |
| **Tono voce** | Fondatore appassionato, casual, come un amico che ti mostra qualcosa di figo |
| **Lezione FLUXION** | IL modello per Gianluca. "Ciao, sono Gianluca, e ho creato FLUXION perche..." = fiducia enorme nel mercato italiano |

### 2.4 Figma — Conference Talks + Demo Ibride

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Config talks: 20-40 min, Feature: 2-3 min |
| **Stile transizioni** | Animazioni Figma native (prototipi che si animano), transizioni smooth tra canvas |
| **Come mostra l'UI** | Il design tool che disegna se stesso — meta-demo |
| **Hook** | "What if..." scenario ipotetico che mostra il futuro del design |
| **CTA** | "Try it free" — community-led growth |
| **Tono voce** | Speaker carismatici, tono TED Talk, entusiasmo controllato |
| **Lezione FLUXION** | Mostrare il "workflow completo" (cliente chiama → Sara risponde → prenotazione appare) come una storia fluida |

### 2.5 Monday.com — Video Ads per PMI

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Ads: 15-30 sec (YouTube pre-roll), Landing: 60-90 sec |
| **Stile transizioni** | Rapide, colorate, pop — stile "startup energetica" |
| **Come mostra l'UI** | Mockup floating su sfondo colorato, UI animata con dati che si compilano da soli |
| **Hook** | Domanda diretta ("Still using spreadsheets?") o pain point ("Monday morning chaos") |
| **CTA** | Forte e diretto ("Start free trial — no credit card needed") |
| **Tono voce** | Energetico, ottimista, musica upbeat corporate |
| **Lezione FLUXION** | Il formato "domanda diretta + soluzione visiva" funziona bene per PMI. "Ancora con l'agenda di carta?" |

### 2.6 Canva — Demo che Convertono

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Feature: 30-60 sec, Tutorial: 3-5 min |
| **Stile transizioni** | Fluide, colorate, "drag-and-drop" visivo |
| **Come mostra l'UI** | Il prodotto in uso — qualcuno che crea un design in tempo reale, accelerato |
| **Hook** | Risultato finale prima ("Look at this") poi come si fa |
| **CTA** | "Design anything. Publish anywhere." — aspirazionale |
| **Tono voce** | Amichevole, inclusivo, "anyone can do this" |
| **Lezione FLUXION** | Mostrare il RISULTATO prima del processo. Prima la prenotazione confermata, poi come e arrivata. |

### 2.7 Stripe — Video Tecnici Eleganti

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Product: 2-3 min, Sessions talk: 15-30 min |
| **Stile transizioni** | Minimal, fade, sfondo gradiente scuro con highlight di codice |
| **Come mostra l'UI** | Dashboard con dati realistici, animazioni di flusso pagamento, diagrammi architetturali animati |
| **Hook** | "Payments infrastructure for the internet" — statement di posizionamento |
| **CTA** | Developer-focused ("Read the docs", "Start integrating") |
| **Tono voce** | Sofisticato, tecnico ma accessibile, "premium feel" |
| **Lezione FLUXION** | L'estetica "premium ma accessibile" — dark mode con accent colors e tipografia curata fa percepire qualita alta anche a budget zero |

### 2.8 Calendly — Demo Brevissime Efficaci

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | 45-75 sec (landing), 30 sec (ads) |
| **Stile transizioni** | Animazioni flat design, ritmo velocissimo, testo + musica senza voice |
| **Come mostra l'UI** | Mockup floating, UI semplificata, focus su 1 workflow |
| **Hook** | Problema universale in 5 sec ("Email back-and-forth for scheduling?") |
| **CTA** | "Sign up free" — immediato |
| **Tono voce** | Spesso ZERO voice. Solo testo animato + musica. Quando c'e voice: breve, diretto. |
| **Lezione FLUXION** | La brevita VENDE. 75 secondi bastano per dire tutto se il messaggio e chiaro. |

### 2.9 HubSpot — Video per PMI che Vendono

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Overview: 2-3 min, Feature: 60-90 sec, Academy: 5-15 min |
| **Stile transizioni** | Professional corporate, split screen, annotazioni animate |
| **Come mostra l'UI** | Screen recording con highlight zones, annotazioni frecce/cerchi, dati dashboard realistici |
| **Hook** | Statistiche shock ("67% of customers never call back") + pain point |
| **CTA** | "Get started free" + "Talk to sales" (dual CTA) |
| **Tono voce** | Professionale educativo, tono "trusted advisor" |
| **Lezione FLUXION** | Le statistiche come hook funzionano benissimo. "Il 67% dei clienti non richiama" = motivazione immediata |

### 2.10 Fresha — Demo per Saloni/Beauty

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Landing: 60-90 sec, Tutorial: 3-8 min |
| **Stile transizioni** | Fluide, palette verde acqua, musica lo-fi corporate |
| **Come mostra l'UI** | Screen recording con voiceover professionale, transizioni tra schermate, dati realistici di salone |
| **Hook** | "Gestisci tutto in un posto" — promessa di semplificazione |
| **CTA** | "Start for free" (freemium con commissioni nascoste) |
| **Tono voce** | Calmo, professionale, rassicurante |
| **Lezione FLUXION** | Usare dati di salone realistici (nomi servizi italiani, prezzi reali). Ma BATTERE Fresha sul pricing: "Zero commissioni, per sempre" |

### 2.11 Mindbody — Demo per Fitness/Wellness

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | Hero: 90-120 sec, Tutorial: 5-15 min |
| **Stile transizioni** | Mix live-action + UI, ritmo energetico, produzione enterprise |
| **Come mostra l'UI** | Persone reali in palestra → transizione a schermata → risultati metriche |
| **Hook** | Scenario reale (cliente che prenota lezione) → problema gestione |
| **CTA** | "Get a Demo" (enterprise, demo guidata con sales rep) |
| **Tono voce** | Entusiasta, energetico, musica fitness. Produzione ALTA. |
| **Lezione FLUXION** | Il formato "persona reale → schermata → risultato" e potente. Non replicabile a budget zero ma il concetto si. |

### 2.12 Square — Storytelling Small Business

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | 60-90 sec (ads), 2-4 min (tutorial) |
| **Stile transizioni** | Live-action + screen alternati, musica acustica/indie |
| **Come mostra l'UI** | Small business owner usa il prodotto su tablet/telefono in location reale |
| **Hook** | Titolare racconta la sua giornata → problema → soluzione |
| **CTA** | "Get started free" + "See pricing" |
| **Tono voce** | Autentico, "real people", storytelling emotivo |
| **Lezione FLUXION** | Il titolare VERO che racconta e il formato piu potente per PMI italiane |

### 2.13 Toast POS — Demo per Ristorazione

| Aspetto | Dettaglio |
|---------|-----------|
| **Durata** | 60-90 sec (landing), 3-5 min (vertical-specific) |
| **Stile transizioni** | Fast-paced, split screen, overlay statistiche |
| **Come mostra l'UI** | POS in uso reale in ristorante, cameriere che tocca lo schermo |
| **Hook** | "Your restaurant, running smoothly" — promessa operativa |
| **CTA** | "Get a custom quote" (enterprise approach) |
| **Tono voce** | Pratico, diretto, "niente fronzoli" |
| **Lezione FLUXION** | Per ogni verticale, mostrare il SOFTWARE IN USO nel contesto reale (salone, palestra, etc.) |

---

## 3. TECNICHE DI PRODUZIONE 2026 (Budget ZERO)

### 3.1 Screen Recording + Post-Production con ffmpeg

```bash
# Pipeline completa: record → trim → enhance → export

# 1. Registra (macOS)
ffmpeg -f avfoundation -framerate 30 -capture_cursor 1 -capture_mouse_clicks 1 \
  -i "1:none" -c:v libx264 -preset ultrafast -crf 18 -pix_fmt yuv420p raw.mkv

# 2. Trim (taglia inizio/fine)
ffmpeg -i raw.mkv -ss 00:00:03 -to 00:01:20 -c copy trimmed.mp4

# 3. Normalizza risoluzione + framerate
ffmpeg -i trimmed.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  -r 30 -c:v libx264 -crf 20 -preset slow -c:a aac normalized.mp4

# 4. Speed up (2x con audio pitch correction)
ffmpeg -i normalized.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" \
  -map "[v]" -map "[a]" speedup_2x.mp4
```

### 3.2 Smooth Zoom SENZA Jitter

```bash
# METODO 1: Pre-scale a 8000px (RACCOMANDATO)
# Scala a 8000px prima di zoompan per eliminare arrotondamento pixel
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=8000:-1, \
   zoompan=z='min(zoom+0.001,1.3)': \
   x='iw/2-(iw/zoom/2)': \
   y='ih/2-(ih/zoom/2)': \
   d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p smooth_zoom_in.mp4

# METODO 2: Zoom OUT (da dettaglio a panoramica)
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=8000:-1, \
   zoompan=z='if(lte(zoom,1.001),1.3,max(1.001,zoom-0.002))': \
   x='iw/2-(iw/zoom/2)': \
   y='ih/2-(ih/zoom/2)': \
   d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p smooth_zoom_out.mp4

# METODO 3: Easing (accelerazione/decelerazione naturale)
# Usa espressione sinusoidale per ease-in-out
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=8000:-1, \
   zoompan=z='1+0.3*sin(PI*on/(150*2))': \
   x='iw/2-(iw/zoom/2)': \
   y='ih/2-(ih/zoom/2)': \
   d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p eased_zoom.mp4

# METODO 4: Zoom su punto specifico (es. bottone in basso a destra)
# target_x=0.75, target_y=0.7 (75% da sinistra, 70% dall'alto)
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=8000:-1, \
   zoompan=z='min(zoom+0.001,1.5)': \
   x='0.75*iw-(iw/zoom/2)': \
   y='0.7*ih-(ih/zoom/2)': \
   d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p zoom_to_button.mp4
```

### 3.3 Animazione Screenshot — Dare Vita a Immagini Statiche

```bash
# Tecnica 1: Ken Burns con easing (pan + zoom leggero)
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=8000:-1, \
   zoompan=z='1.05+0.05*sin(2*PI*t/10)': \
   x='iw/2-(iw/zoom/2)+50*sin(2*PI*t/8)': \
   y='ih/2-(ih/zoom/2)+30*cos(2*PI*t/12)': \
   d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p subtle_motion.mp4

# Tecnica 2: Reveal progressivo (da blur a sharp)
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=1920:1080, \
   gblur=sigma='max(0,30-6*t)'" \
  -t 5 -r 30 -c:v libx264 -pix_fmt yuv420p blur_reveal.mp4

# Tecnica 3: Slide-in da sinistra
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=1920:1080, \
   crop=iw:ih:'if(lt(t,1),-iw+iw*t,0)':0" \
  -t 3 -r 30 -c:v libx264 -pix_fmt yuv420p slide_in.mp4
```

### 3.4 Transizioni Professionali con ffmpeg xfade

**Lista COMPLETA transizioni xfade disponibili:**
```
fade, fadeblack, fadewhite, distance, wipeleft, wiperight, wipeup, wipedown,
slideleft, slideright, slideup, slidedown, smoothleft, smoothright, smoothup,
smoothdown, circlecrop, rectcrop, circleopen, circleclose, vertopen, vertclose,
horzopen, horzclose, dissolve, pixelize, diagtl, diagtr, diagbl, diagbr, radial
```

```bash
# Dissolve (la piu usata — elegante e professionale)
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=dissolve:duration=0.8:offset=4" \
  -c:v libx264 -pix_fmt yuv420p dissolve.mp4

# Fade to Black (cambio sezione)
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=fadeblack:duration=1:offset=4" \
  -c:v libx264 fadeblack.mp4

# Slide Left (cambio flusso)
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=slideleft:duration=0.5:offset=4" \
  -c:v libx264 slide.mp4

# Smooth Left (slide con easing — piu elegante)
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=smoothleft:duration=0.6:offset=4" \
  -c:v libx264 smooth.mp4

# Circle Open (reveal circolare — per feature highlight)
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=circleopen:duration=0.8:offset=4" \
  -c:v libx264 circle.mp4

# CHAIN: 3 clip con transizioni diverse
ffmpeg -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 -filter_complex \
  "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=4[v01]; \
   [v01][2:v]xfade=transition=slideleft:duration=0.5:offset=8" \
  -c:v libx264 -pix_fmt yuv420p chained.mp4

# CHAIN con audio
ffmpeg -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 -filter_complex \
  "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=4[v01]; \
   [v01][2:v]xfade=transition=fadeblack:duration=0.5:offset=8[vout]; \
   [0:a][1:a]acrossfade=d=0.5:c1=tri:c2=tri[a01]; \
   [a01][2:a]acrossfade=d=0.5:c1=tri:c2=tri[aout]" \
  -map "[vout]" -map "[aout]" -c:v libx264 chained_audio.mp4
```

### 3.5 Color Grading per UI Dark Mode

```bash
# Aumenta contrasto e saturazione per UI scure
ffmpeg -i dark_ui_recording.mp4 -vf \
  "eq=contrast=1.1:brightness=0.02:saturation=1.2" \
  -c:v libx264 enhanced_dark.mp4

# Curves per un look "tech premium" (azzurro freddo nelle ombre)
ffmpeg -i recording.mp4 -vf \
  "curves=blue='0/0.05 0.5/0.5 1/1':red='0/0 0.5/0.48 1/1'" \
  -c:v libx264 tech_look.mp4

# Look "caldo" per video PMI (piu accogliente)
ffmpeg -i recording.mp4 -vf \
  "curves=red='0/0 0.5/0.55 1/1':blue='0/0.02 0.5/0.45 1/0.95', \
   eq=saturation=1.15:brightness=0.01" \
  -c:v libx264 warm_look.mp4

# Color grading con LUT (scarica LUT gratuite da lutfiles.com)
ffmpeg -i recording.mp4 -vf \
  "lut3d=lut_file.cube" \
  -c:v libx264 graded.mp4
```

### 3.6 Text Overlay Animato

```bash
# Fade in dal basso (slide up + fade in)
ffmpeg -i video.mp4 -vf \
  "drawtext=text='FLUXION - Gestionale PMI': \
   fontsize=48:fontcolor=white: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=(w-text_w)/2: \
   y='if(lt(t-1,0.5),h-(h-100)*(t-1)/0.5,100)': \
   alpha='if(lt(t-1,0),0,if(lt(t-1,0.5),(t-1)*2,1))': \
   enable='between(t,1,5)'" \
  -c:v libx264 text_slide_up.mp4

# Fade in + Fade out
ffmpeg -i video.mp4 -vf \
  "drawtext=text='Zero Abbonamenti. Per Sempre.': \
   fontsize=42:fontcolor=white: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=(w-text_w)/2:y=(h-text_h)/2: \
   alpha='if(lt(t-2,0),0,if(lt(t-2,0.5),(t-2)*2,if(lt(t-5,0),1,if(lt(t-5,0.5),1-(t-5)*2,0))))': \
   enable='between(t,2,5.5)'" \
  -c:v libx264 text_fade_inout.mp4

# Typewriter effect (un carattere alla volta)
ffmpeg -i video.mp4 -vf \
  "drawtext=text='Paghi una volta. Usi per sempre.': \
   fontsize=36:fontcolor=white: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=100:y=h-100: \
   alpha=1: \
   text_shaping=0: \
   enable='between(t,2,6)': \
   text='%{eif\:clip(trunc((t-2)*10)\,0\,30)\:d}'" \
  -c:v libx264 typewriter.mp4

# NOTA: Il typewriter puro con drawtext e limitato.
# Per typewriter reale, generare frame con Python/Pillow e poi composire con ffmpeg.

# Multi-line text overlay con sfondo semi-trasparente
ffmpeg -i video.mp4 -vf \
  "drawbox=x=0:y=ih-120:w=iw:h=120:color=black@0.6:t=fill:enable='between(t,3,8)', \
   drawtext=text='Base €497 — Licenza Lifetime': \
   fontsize=36:fontcolor=white: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=(w-text_w)/2:y=h-100: \
   alpha='if(lt(t-3,0.3),(t-3)/0.3,1)': \
   enable='between(t,3,8)', \
   drawtext=text='Zero abbonamenti · Zero commissioni': \
   fontsize=24:fontcolor=white@0.8: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=(w-text_w)/2:y=h-55: \
   alpha='if(lt(t-3.3,0.3),(t-3.3)/0.3,1)': \
   enable='between(t,3.3,8)'" \
  -c:v libx264 lower_third.mp4
```

### 3.7 Split Screen — Before/After

```bash
# Side by side: sinistra = agenda carta, destra = FLUXION
ffmpeg -i old_way.mp4 -i fluxion_way.mp4 -filter_complex \
  "[0:v]crop=iw/2:ih:0:0,scale=960:1080[left]; \
   [1:v]crop=iw/2:ih:iw/2:0,scale=960:1080[right]; \
   [left][right]hstack=inputs=2[out]" \
  -map "[out]" -c:v libx264 split_screen.mp4

# Con linea divisoria bianca
ffmpeg -i old_way.mp4 -i fluxion_way.mp4 -filter_complex \
  "[0:v]scale=957:1080[left]; \
   [1:v]scale=957:1080[right]; \
   [left][right]hstack=inputs=2[stacked]; \
   [stacked]drawbox=x=957:y=0:w=6:h=ih:color=white:t=fill[out]" \
  -map "[out]" -c:v libx264 split_divider.mp4

# Wipe reveal: prima mostra il "vecchio", poi rivela il "nuovo"
ffmpeg -i old_way.mp4 -i fluxion_way.mp4 -filter_complex \
  "xfade=transition=wipeleft:duration=1.5:offset=3" \
  -c:v libx264 wipe_reveal.mp4

# Split con label
ffmpeg -i old_way.mp4 -i fluxion_way.mp4 -filter_complex \
  "[0:v]scale=957:1080[left]; \
   [1:v]scale=957:1080[right]; \
   [left][right]hstack=inputs=2[stacked]; \
   [stacked]drawtext=text='PRIMA':fontsize=32:fontcolor=red:x=200:y=50:fontfile=/System/Library/Fonts/Helvetica.ttc, \
   drawtext=text='DOPO':fontsize=32:fontcolor=green:x=1150:y=50:fontfile=/System/Library/Fonts/Helvetica.ttc[out]" \
  -map "[out]" -c:v libx264 split_labeled.mp4
```

### 3.8 Musica di Sottofondo — Fonti Gratuite

| Fonte | Costo | Qualita | Licenza | Note |
|-------|-------|---------|---------|------|
| **YouTube Audio Library** | Gratuito | 8/10 | CC / Free use | Integrato in YouTube Studio, ottima selezione corporate/tech |
| **Pixabay Music** | Gratuito | 7/10 | Royalty-free | Nessuna attribuzione richiesta |
| **Freesound.org** | Gratuito | 6/10 | CC varie | Collaborativo, qualita variabile |
| **Mixkit** | Gratuito | 8/10 | Free license | Ottime tracce corporate e tech |
| **Bensound** | Freemium | 9/10 | Free con attribuzione | Qualita premium |
| **Thematic** | Gratuito | 8/10 | Free per YouTube | Artisti indie, tracce trending |

**Generi consigliati per demo software PMI**:
- **Corporate Inspiring**: Per hero video e overview (BPM 100-120)
- **Lo-fi/Ambient Tech**: Per screen recording e tutorial (BPM 70-90)
- **Acoustic/Piano**: Per storytelling fondatore (BPM 80-100)
- **Upbeat Pop**: Per social clips brevi (BPM 110-130)

**Comando per aggiungere musica con fade in/out**:
```bash
# Aggiungi musica con volume basso, fade in 2s, fade out 3s
ffmpeg -i video.mp4 -i background_music.mp3 -filter_complex \
  "[1:a]volume=0.15,afade=t=in:st=0:d=2,afade=t=out:st=72:d=3[music]; \
   [0:a][music]amix=inputs=2:duration=first[aout]" \
  -map "0:v" -map "[aout]" -c:v copy -c:a aac with_music.mp4
```

### 3.9 Sound Design

**Fonti gratuite per effetti sonori**:
- **Mixkit** (mixkit.co): Whoosh, click, notification — gratuiti
- **Freesound.org**: Database collaborativo CC
- **Pixabay Sound Effects**: Royalty-free, no attribuzione
- **Zapsplat**: 100k+ effetti gratuiti con account free

**Effetti chiave per demo software**:
| Effetto | Quando | Durata |
|---------|--------|--------|
| **Click/tap** | Ogni click UI importante | 0.1-0.2s |
| **Whoosh** | Transizione tra schermate | 0.3-0.5s |
| **Notification ding** | Prenotazione confermata, messaggio | 0.5-1s |
| **Success chime** | Azione completata (prenotazione ok) | 0.5-1s |
| **Subtle pop** | Elemento che appare | 0.1-0.3s |
| **Typing** | Compilazione campi | Durata digitazione |

```bash
# Aggiungere effetto sonoro a timestamp specifico
ffmpeg -i video.mp4 -i click.mp3 -filter_complex \
  "[1:a]adelay=3000|3000,volume=0.8[sfx]; \
   [0:a][sfx]amix=inputs=2:duration=first[aout]" \
  -map "0:v" -map "[aout]" -c:v copy -c:a aac with_sfx.mp4

# Multipli effetti sonori
ffmpeg -i video.mp4 -i click.mp3 -i whoosh.mp3 -i ding.mp3 -filter_complex \
  "[1:a]adelay=3000|3000,volume=0.8[sfx1]; \
   [2:a]adelay=5000|5000,volume=0.6[sfx2]; \
   [3:a]adelay=8000|8000,volume=0.7[sfx3]; \
   [0:a][sfx1][sfx2][sfx3]amix=inputs=4:duration=first[aout]" \
  -map "0:v" -map "[aout]" -c:v copy -c:a aac multi_sfx.mp4
```

### 3.10 Pacing — Ritmo Ideale

**Regole d'oro 2026**:

| Regola | Dettaglio |
|--------|-----------|
| **3-5 secondi per shot** | Qualcosa di nuovo deve apparire ogni 3-5 secondi |
| **Hook in 5 secondi** | Se non catturi in 5 sec, perdi il 50% degli spettatori |
| **Nuovo concetto ogni 8-15 sec** | Un concetto/feature ogni 8-15 secondi mantiene engagement |
| **Pausa emotiva ogni 30 sec** | Breve respiro (0.5-1 sec) prima di nuova sezione |
| **CTA entro 75 sec** | Video demo > 90 sec perdono 40%+ retention |

**Template pacing per video 75 secondi**:
```
[0-5s]    HOOK: 1 shot — problema visivo immediato
[5-10s]   PROBLEMA: 1-2 shot — amplificazione pain point
[10-15s]  BRIDGE: 1 shot — "E se ci fosse un modo migliore?"
[15-25s]  SOLUZIONE 1: 2-3 shot — prima feature (calendario)
[25-35s]  SOLUZIONE 2: 2-3 shot — seconda feature (Sara voce)
[35-45s]  SOLUZIONE 3: 2-3 shot — terza feature (WhatsApp)
[45-55s]  DIFFERENZIATORE: 2 shot — "€497 una volta, per sempre"
[55-65s]  SOCIAL PROOF: 1-2 shot — testimonianza/numero clienti
[65-75s]  CTA: 1-2 shot — card finale con prezzo + URL
```

**Totale shot: ~18-22 in 75 secondi = media 3.5 sec/shot**

---

## 4. STRUTTURA NARRATIVA — Gold Standard 2026

### 4.1 Hook (0-5 secondi)

**Cosa funziona**:
- Domanda diretta: "Ancora con l'agenda di carta?"
- Statistica shock: "Il 67% dei clienti non richiama"
- Scenario riconoscibile: Telefono che squilla, nessuno risponde
- Before/After visivo: Caos → Ordine in 3 secondi
- Risultato prima: "3 ore risparmiate ogni giorno"

**Cosa NON funziona**:
- Logo animato lungo (nessuno aspetta il tuo logo)
- "Ciao, benvenuti nel nostro video..." (no!)
- Storia dell'azienda ("Fondata nel 2024...")
- Musica senza contenuto visivo

### 4.2 Problem Statement (5-15 secondi)

**Pattern efficace**: Identificazione → Amplificazione → Costo

```
IDENTIFICAZIONE: "Ogni giorno perdi clienti perche nessuno risponde al telefono"
AMPLIFICAZIONE:  "Prenotazioni su WhatsApp che si perdono. Appuntamenti doppi."
COSTO:           "Quanto ti costa un cliente perso? €50? €100? Ogni settimana."
```

### 4.3 Solution Reveal (15-35 secondi)

**Gold standard**: NON mostrare features — mostra WORKFLOW.

```
SBAGLIATO: "FLUXION ha un calendario, gestione clienti, WhatsApp, voce..."
GIUSTO:    Cliente chiama → Sara risponde → Prenotazione appare nel calendario
           → WhatsApp reminder automatico → Cliente arriva puntuale
```

Il software deve sembrare che **funziona da solo**. Notion e Linear sono maestri in questo: l'UI si compila da sola, il cursore si muove con purpose, tutto e fluido.

### 4.4 Feature Walkthrough (25-55 secondi)

**Tempo per feature**: 8-12 secondi ciascuna, MAX 3-4 features per video.

| Feature | Tempo | Cosa mostrare |
|---------|-------|---------------|
| **Calendario** | 10 sec | Prenotazione che appare, colori per operatore, vista giornaliera |
| **Sara Voice** | 12 sec | Audio reale di Sara che parla + prenotazione in tempo reale |
| **WhatsApp** | 8 sec | Reminder automatico che parte, conferma cliente |
| **Scheda Cliente** | 8 sec | Storico visite, preferenze, note, tutto cercabile |

### 4.5 Social Proof (55-65 secondi)

**Dove va nel video**: Dopo le features, prima del CTA. Serve come "conferma" della decisione che lo spettatore sta gia formando.

**Formati efficaci**:
- Numero clienti: "Gia scelto da 150+ attivita italiane"
- Testimonianza breve (3-5 sec): Citazione di un titolare reale
- Comparazione risparmio: "In 2 anni risparmi €2.000 vs abbonamento mensile"
- Screenshot review/rating

### 4.6 CTA (65-75 secondi)

**Pattern vincente 2026**:
```
FONDATORE alla camera: "Prova FLUXION. Una licenza, per sempre."
CARD FINALE (5 sec):
  Logo FLUXION centrato
  "Da €497 — Licenza Lifetime"
  URL: fluxion-landing.pages.dev
  QR Code (opzionale, per mobile viewers)
```

**CTA da evitare**:
- "Visita il nostro sito web" (troppo generico)
- "Per maggiori informazioni..." (troppo corporate)
- CTA multipli confondono ("iscriviti, seguici, scarica, prova...")

### 4.7 Capitoli YouTube

```
0:00 — Ancora con l'agenda di carta?
0:05 — Il problema delle prenotazioni perse
0:15 — FLUXION: come funziona
0:25 — Il calendario intelligente
0:35 — Sara, la tua assistente vocale 24/7
0:45 — WhatsApp automatico
0:55 — Quanto risparmi (vs abbonamento)
1:05 — Come iniziare — €497 una volta sola
```

---

## 5. METRICHE che Contano

### 5.1 Retention Rate per Durata Video

| Durata video | Retention media | Target FLUXION |
|-------------|-----------------|----------------|
| < 60 sec | 55-65% | 60%+ |
| 60-90 sec | 45-55% | 50%+ |
| 90-120 sec | 35-45% | 40%+ |
| 2-5 min | 30-40% | 35%+ |
| 5-10 min | 25-35% | N/A (tutorial) |

### 5.2 Drop-off Points Tipici

| Momento | % che abbandona | Come mitigare |
|---------|-----------------|---------------|
| **0-5 sec** | 30-50% | Hook FORTE — niente logo, niente intro |
| **15-20 sec** | 15-20% | Mostrare il software ORA — non aspettare |
| **45-60 sec** | 10-15% | Cambiare ritmo/sezione — pausa emotiva |
| **Pre-CTA** | 5-10% | Social proof tiene lo spettatore fino alla fine |

### 5.3 Durata Ideale per Massimo Engagement

**Per demo software gestionale PMI italiano**:
- **Landing page hero**: 75 secondi (sweet spot retention 50%+)
- **YouTube SEO**: 2-3 minuti (favorito dall'algoritmo, abbastanza per profondita)
- **Social ads**: 15-30 secondi (formato nativo Instagram/TikTok/Facebook)
- **Tutorial**: 5-8 minuti (audience gia convinta, vuole dettagli)

### 5.4 CTR Thumbnail

| Tipo thumbnail | CTR medio | Note |
|---------------|-----------|------|
| Screenshot UI + testo bold | 4-6% | Standard, funziona bene |
| Persona + UI floating | 6-8% | Il migliore per trust |
| Before/After split | 5-7% | Molto efficace per PMI |
| Solo testo su sfondo | 2-4% | Troppo generico |

### 5.5 Conversion Rate Video → Acquisto

| Funnel | Rate medio | Target FLUXION |
|--------|-----------|----------------|
| View → Click CTA | 3-5% | 5%+ |
| Click → Landing | 60-80% | 75%+ |
| Landing → Checkout | 2-5% | 3%+ |
| Checkout → Acquisto | 50-70% | 60%+ |
| **End-to-end**: View → Acquisto | 0.1-0.5% | 0.3%+ |

---

## 6. ERRORI DA EVITARE — I 10 Peccati Capitali

### 1. Feature Vomit
**Errore**: Stipare OGNI feature in un video.
**Fix**: Max 3-4 features per video. Un video per ogni workflow.

### 2. Logo Intro Lungo
**Errore**: 5-10 secondi di logo animato prima del contenuto.
**Fix**: Logo in basso a destra come watermark. Il contenuto parte al frame 1.

### 3. Nessun Hook
**Errore**: "Ciao, oggi vi presentiamo il nostro software..."
**Fix**: Problema riconoscibile nei primi 3 secondi. Punto.

### 4. Dati Falsi/Lorem Ipsum
**Errore**: Screenshot con "John Doe", "test@test.com", "Service 1".
**Fix**: Dati REALISTICI italiani. "Marco Rossi", "Taglio + Piega", "Salone Bella".

### 5. Voiceover Robotico/Monotono
**Errore**: TTS senza emozione o lettura piatta.
**Fix**: Edge-TTS IsabellaNeural con SSML per enfasi e pause. O meglio: fondatore vero.

### 6. Zero CTA
**Errore**: Il video finisce... e basta. Lo spettatore non sa cosa fare.
**Fix**: CTA chiaro, specifico, con prezzo e URL. "€497, una volta sola. fluxion.it"

### 7. Non Ottimizzato per Mobile
**Errore**: Testo troppo piccolo, UI illeggibile su smartphone.
**Fix**: Testo min 28px su video 1080p. Zoom sulle aree importanti dell'UI.

### 8. Musica Troppo Alta
**Errore**: La musica copre il voiceover.
**Fix**: Musica a -18dB sotto il voiceover. Volume 0.15 max con ffmpeg.

### 9. Ritmo Piatto
**Errore**: Stesso ritmo dall'inizio alla fine — monotono.
**Fix**: Alternare veloce (feature flash) e lento (zoom su dettaglio). Pausa emotiva ogni 30 sec.

### 10. Aspetto "Amatoriale"
**Errore**: Risoluzione bassa, bordi tagliati, font di sistema, colori casuali.
**Fix**: 1080p minimo, padding consistente, font professionale (San Francisco/Helvetica), palette colori coerente con il brand.

---

## 7. ffmpeg AVANZATO — Ricettario Copia-Incolla

### 7.1 Smooth Pan/Zoom SENZA zoompan

```bash
# Pan orizzontale fluido con scale+crop
ffmpeg -loop 1 -i wide_screenshot.png -vf \
  "scale=3840:-1, \
   crop=1920:1080:'1920*(t/10)':0" \
  -t 10 -r 30 -c:v libx264 -pix_fmt yuv420p smooth_pan.mp4

# Zoom in con scale (NO zoompan, NO jitter)
# Anima il crop progressivamente
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=3840:2160, \
   crop='3840-1920*(t/5)':'2160-1080*(t/5)':'960*(t/5)':'540*(t/5)'" \
  -t 5 -r 30 -c:v libx264 -pix_fmt yuv420p scale_zoom.mp4
```

### 7.2 xfade Transitions Avanzate

```bash
# Dissolve con easing (richiede xfade-easing extension)
# Se compilato con supporto custom expressions:
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=dissolve:duration=1:offset=4:easing=easeInOutCubic" \
  output.mp4

# Diagonal wipe (dall'angolo in alto a sinistra)
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=diagtl:duration=0.8:offset=4" \
  diag_wipe.mp4

# Pixelize transition (effetto "digitale")
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=pixelize:duration=1:offset=4" \
  pixel_transition.mp4
```

### 7.3 Text Overlay con Animazione

```bash
# Slide in dal basso con fade
ffmpeg -i video.mp4 -vf \
  "drawtext=text='Paghi una volta': \
   fontsize=48:fontcolor=white: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=(w-text_w)/2: \
   y='h-100+50*(1-min(1,(t-2)/0.5))': \
   alpha='min(1,(t-2)/0.5)': \
   enable='between(t,2,7)'" \
  -c:v libx264 text_anim.mp4

# Testo con sfondo rettangolare (lower third)
ffmpeg -i video.mp4 -vf \
  "drawbox=x=0:y=ih*0.85:w=iw:h=ih*0.15:color=0x1a1a2e@0.85:t=fill:enable='between(t,3,8)', \
   drawtext=text='FLUXION — Gestionale PMI Italiane': \
   fontsize=36:fontcolor=0x00d4ff: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=40:y=h*0.88: \
   alpha='min(1,(t-3)/0.3)': \
   enable='between(t,3,8)', \
   drawtext=text='Licenza Lifetime da €497': \
   fontsize=24:fontcolor=white@0.8: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=40:y=h*0.94: \
   alpha='min(1,(t-3.3)/0.3)': \
   enable='between(t,3.3,8)'" \
  -c:v libx264 lower_third_branded.mp4
```

### 7.4 Cursor Highlight Circle Animato

```bash
# Crea cerchio highlight giallo pulsante
# Step 1: Genera il cerchio animato come video
ffmpeg -f lavfi -i "color=c=black@0:s=100x100:d=1,format=rgba" -vf \
  "geq=r='if(lt(hypot(X-50,Y-50),40+5*sin(2*PI*t*3)),255,0)': \
       g='if(lt(hypot(X-50,Y-50),40+5*sin(2*PI*t*3)),200,0)': \
       b='if(lt(hypot(X-50,Y-50),40+5*sin(2*PI*t*3)),0,0)': \
       a='if(lt(hypot(X-50,Y-50),40+5*sin(2*PI*t*3)),100,0)'" \
  -t 1 -r 30 -c:v png pulse_circle.mov

# Step 2: Overlay il cerchio sul video alla posizione del click
ffmpeg -i screen.mp4 -i pulse_circle.mov -filter_complex \
  "[1:v]loop=loop=-1:size=30:start=0[circle]; \
   [0:v][circle]overlay=910:490:enable='between(t,3,4.5)'" \
  -c:v libx264 with_cursor_highlight.mp4
```

### 7.5 Picture-in-Picture Avanzato

```bash
# PiP con bordo, ombra, e posizionamento
ffmpeg -i screen.mp4 -i facecam.mp4 -filter_complex \
  "[1:v]scale=320:240, \
   pad=324:244:2:2:color=white, \
   pad=330:250:3:3:color=black@0.3[pip]; \
   [0:v][pip]overlay=W-w-30:H-h-30" \
  -c:v libx264 pip_bordered.mp4

# PiP che appare e scompare con fade
ffmpeg -i screen.mp4 -i facecam.mp4 -filter_complex \
  "[1:v]scale=320:240, \
   fade=in:st=0:d=0.5, \
   fade=out:st=60:d=0.5[pip]; \
   [0:v][pip]overlay=W-w-20:H-h-20:shortest=1:enable='between(t,0,65)'" \
  -c:v libx264 pip_fade.mp4

# PiP che si sposta (in basso a destra → in basso a sinistra)
ffmpeg -i screen.mp4 -i facecam.mp4 -filter_complex \
  "[1:v]scale=320:240[pip]; \
   [0:v][pip]overlay='if(lt(t,30),W-w-20,20)':H-h-20" \
  -c:v libx264 pip_moving.mp4
```

### 7.6 Color Grading (Curves, EQ)

```bash
# Contrasto + saturazione per look professionale
ffmpeg -i raw.mp4 -vf \
  "eq=contrast=1.15:brightness=0.02:saturation=1.2:gamma=1.05" \
  -c:v libx264 graded.mp4

# Curves: look "tech blue" (ombre fredde, highlights caldi)
ffmpeg -i raw.mp4 -vf \
  "curves=r='0/0 0.25/0.22 0.5/0.5 0.75/0.78 1/1': \
         g='0/0.02 0.5/0.5 1/0.98': \
         b='0/0.05 0.25/0.3 0.5/0.52 0.75/0.73 1/0.95'" \
  -c:v libx264 tech_blue.mp4

# Look "warm professional" (ottimo per video PMI)
ffmpeg -i raw.mp4 -vf \
  "curves=r='0/0.02 0.5/0.53 1/1': \
         b='0/0 0.5/0.47 1/0.95', \
   eq=saturation=1.1:brightness=0.01" \
  -c:v libx264 warm_pro.mp4

# Unsharp mask per nitidezza (dopo screen recording)
ffmpeg -i raw.mp4 -vf \
  "unsharp=5:5:0.8:5:5:0.0" \
  -c:v libx264 sharp.mp4
```

### 7.7 Vignette Effect

```bash
# Vignette leggera (bordi scuri — focus al centro)
ffmpeg -i video.mp4 -vf \
  "vignette=PI/5" \
  -c:v libx264 vignette_light.mp4

# Vignette media (piu drammatica)
ffmpeg -i video.mp4 -vf \
  "vignette=PI/4:eval=frame" \
  -c:v libx264 vignette_medium.mp4

# Vignette animata (si chiude lentamente)
ffmpeg -i video.mp4 -vf \
  "vignette='PI/5+PI/10*t/10'" \
  -c:v libx264 vignette_animated.mp4

# Vignette solo bordi (senza toccare il centro)
ffmpeg -i video.mp4 -vf \
  "vignette=angle=PI/4:x0=w/2:y0=h/2" \
  -c:v libx264 vignette_edges.mp4
```

### 7.8 Logo Watermark Animato

```bash
# Logo fade in, resta, fade out
ffmpeg -i video.mp4 -loop 1 -i logo.png -filter_complex \
  "[1:v]scale=150:-1,format=rgba, \
   fade=in:st=0:d=1:alpha=1, \
   fade=out:st=70:d=2:alpha=1[logo]; \
   [0:v][logo]overlay=W-w-20:20:shortest=1" \
  -c:v libx264 with_logo.mp4

# Logo con opacita ridotta (watermark discreto)
ffmpeg -i video.mp4 -loop 1 -i logo.png -filter_complex \
  "[1:v]scale=120:-1,format=rgba, \
   colorchannelmixer=aa=0.5[logo]; \
   [0:v][logo]overlay=W-w-15:15" \
  -c:v libx264 watermark_subtle.mp4

# Logo che appare solo nei primi 5 e ultimi 5 secondi
ffmpeg -i video.mp4 -loop 1 -i logo.png -filter_complex \
  "[1:v]scale=150:-1,format=rgba[logo]; \
   [0:v][logo]overlay=W-w-20:20:enable='lt(t,5)+gt(t,70)'" \
  -c:v libx264 logo_bookend.mp4

# Logo + tagline animati insieme
ffmpeg -i video.mp4 -loop 1 -i logo.png -filter_complex \
  "[1:v]scale=120:-1,format=rgba,fade=in:st=1:d=0.5:alpha=1[logo]; \
   [0:v][logo]overlay=30:H-h-30:shortest=1, \
   drawtext=text='Gestionale PMI': \
   fontsize=18:fontcolor=white@0.7: \
   fontfile=/System/Library/Fonts/Helvetica.ttc: \
   x=160:y=h-45: \
   alpha='min(1,(t-1.5)/0.5)': \
   enable='gte(t,1.5)'" \
  -c:v libx264 logo_tagline.mp4
```

### 7.9 Split Screen Side-by-Side

```bash
# 2 video affiancati con stessa durata
ffmpeg -i left_video.mp4 -i right_video.mp4 -filter_complex \
  "[0:v]scale=960:1080[l]; \
   [1:v]scale=960:1080[r]; \
   [l][r]hstack=inputs=2" \
  -c:v libx264 side_by_side.mp4

# 2 video con gap e sfondo colorato
ffmpeg -i left.mp4 -i right.mp4 -filter_complex \
  "color=c=0x1a1a2e:s=1920x1080:d=10[bg]; \
   [0:v]scale=940:529[l]; \
   [1:v]scale=940:529[r]; \
   [bg][l]overlay=10:275[tmp]; \
   [tmp][r]overlay=970:275" \
  -c:v libx264 split_gap.mp4

# 3 video in griglia (utile per mostrare 3 verticali)
ffmpeg -i salone.mp4 -i palestra.mp4 -i clinica.mp4 -filter_complex \
  "color=c=0x1a1a2e:s=1920x1080:d=10[bg]; \
   [0:v]scale=620:349[v1]; \
   [1:v]scale=620:349[v2]; \
   [2:v]scale=620:349[v3]; \
   [bg][v1]overlay=10:365[t1]; \
   [t1][v2]overlay=650:365[t2]; \
   [t2][v3]overlay=1290:365" \
  -c:v libx264 grid_3.mp4
```

### 7.10 Pipeline Completa — Da Screenshot a Video Professionale

```bash
#!/bin/bash
# Pipeline completa per creare video demo da screenshot FLUXION
# Uso: ./create_demo.sh

OUTPUT_DIR="./demo_output"
mkdir -p "$OUTPUT_DIR"

# === PARAMETRI ===
RESOLUTION="1920x1080"
FPS=30
FONT="/System/Library/Fonts/Helvetica.ttc"
BRAND_COLOR="0x00d4ff"
BG_COLOR="0x1a1a2e"

# === STEP 1: Crea clip da ogni screenshot ===
for i in 01 02 03 04 05 06 07 08 09 10 11; do
  # Ogni screenshot diventa un clip di 5 secondi con zoom leggero
  ffmpeg -loop 1 -i "screenshots/${i}.png" -vf \
    "scale=8000:-1, \
     zoompan=z='min(zoom+0.0008,1.15)': \
     x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)': \
     d=$((FPS*5)):s=${RESOLUTION}:fps=${FPS}" \
    -t 5 -c:v libx264 -pix_fmt yuv420p -crf 18 \
    "${OUTPUT_DIR}/clip_${i}.mp4"
done

# === STEP 2: Aggiungi testo overlay a ogni clip ===
# (Personalizza per ogni schermata)
ffmpeg -i "${OUTPUT_DIR}/clip_01.mp4" -vf \
  "drawbox=x=0:y=ih*0.85:w=iw:h=ih*0.15:color=${BG_COLOR}@0.85:t=fill, \
   drawtext=text='Il Tuo Calendario Intelligente':fontsize=36:fontcolor=${BRAND_COLOR}: \
   fontfile=${FONT}:x=40:y=h*0.88:alpha='min(1,(t-0.5)/0.3)':enable='gte(t,0.5)'" \
  -c:v libx264 -crf 18 "${OUTPUT_DIR}/clip_01_text.mp4"

# === STEP 3: Concatena con transizioni ===
ffmpeg \
  -i "${OUTPUT_DIR}/clip_01_text.mp4" \
  -i "${OUTPUT_DIR}/clip_02.mp4" \
  -i "${OUTPUT_DIR}/clip_03.mp4" \
  -filter_complex \
    "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=4.5[v01]; \
     [v01][2:v]xfade=transition=slideleft:duration=0.5:offset=9[vout]" \
  -map "[vout]" -c:v libx264 -crf 18 "${OUTPUT_DIR}/demo_no_audio.mp4"

# === STEP 4: Aggiungi voiceover TTS ===
# (Generato separatamente con Edge-TTS)
edge-tts --voice "it-IT-IsabellaNeural" \
  --text "Benvenuto in FLUXION. Il gestionale che paghi una volta e usi per sempre." \
  --write-media "${OUTPUT_DIR}/voiceover.mp3"

# === STEP 5: Aggiungi musica + voiceover ===
ffmpeg -i "${OUTPUT_DIR}/demo_no_audio.mp4" \
  -i "${OUTPUT_DIR}/voiceover.mp3" \
  -i background_music.mp3 \
  -filter_complex \
    "[2:a]volume=0.12,afade=t=in:d=2,afade=t=out:st=72:d=3[music]; \
     [1:a]volume=1.0[voice]; \
     [voice][music]amix=inputs=2:duration=first[aout]" \
  -map "0:v" -map "[aout]" -c:v copy -c:a aac \
  "${OUTPUT_DIR}/demo_final.mp4"

# === STEP 6: Aggiungi logo watermark ===
ffmpeg -i "${OUTPUT_DIR}/demo_final.mp4" -loop 1 -i logo.png -filter_complex \
  "[1:v]scale=100:-1,format=rgba,colorchannelmixer=aa=0.6[logo]; \
   [0:v][logo]overlay=W-w-15:15" \
  -c:v libx264 -crf 18 -c:a copy "${OUTPUT_DIR}/FLUXION_Demo_2026.mp4"

echo "Demo video creato: ${OUTPUT_DIR}/FLUXION_Demo_2026.mp4"
```

---

## 8. CHECKLIST PRE-PUBBLICAZIONE

### Video Quality
- [ ] Risoluzione 1920x1080 (1080p) minimo
- [ ] 30fps costante (no frame drop)
- [ ] Bitrate 8-12 Mbps per YouTube
- [ ] Audio: 48kHz, 192kbps AAC
- [ ] Nessun artefatto di compressione visibile
- [ ] Testo leggibile su mobile (min 28px su 1080p)

### Content
- [ ] Hook nei primi 5 secondi
- [ ] Dati realistici italiani (no Lorem Ipsum)
- [ ] Max 3-4 features mostrate
- [ ] CTA chiaro con prezzo e URL
- [ ] Durata 75 sec (hero) / 90 sec (Sara demo)
- [ ] Pacing: qualcosa di nuovo ogni 3-5 secondi

### Audio
- [ ] Voiceover chiaro e udibile
- [ ] Musica di sottofondo a -18dB sotto voce
- [ ] Sound effects per click/transizioni (opzionale ma consigliato)
- [ ] Fade in musica (2s) e fade out (3s)
- [ ] No rumori di fondo

### SEO (YouTube)
- [ ] Titolo con keyword primaria + anno + differenziatore
- [ ] Descrizione con capitoli + link CTA + tag
- [ ] Thumbnail: persona + UI + testo bold (max 5 parole)
- [ ] Tag strategici (gestionale, nicchia, software, PMI)
- [ ] Capitoli YouTube con timestamp

### Brand
- [ ] Logo watermark discreto
- [ ] Palette colori coerente con brand FLUXION
- [ ] Font consistente (San Francisco/Helvetica)
- [ ] Card finale con logo + prezzo + URL
- [ ] Zero riferimenti a tecnologie interne (no "Tauri", "SQLite", "Anthropic")

---

## Fonti Ricerca

- [Ultimate Product Demo Videos Guide 2026](https://www.whatastory.agency/blog/product-demo-videos-guide)
- [How to Create SaaS Demo Video: Complete Guide 2026](https://motionvillee.com/how-to-create-your-saas-demo-video/)
- [16+ Best B2B SaaS Video Examples 2026](https://www.superside.com/blog/saas-video-examples)
- [12 Best SaaS Product Demo Video Examples 2026](https://vidico.com/news/top-12-outstanding-saas-product-demo-videos/)
- [20 Best Product Demo Video Examples That Convert 2026](https://supademo.com/blog/demo-video-examples)
- [11 Common App Demo Mistakes to Avoid 2026](https://www.contentbeta.com/blog/app-demo-video-mistakes-to-avoid/)
- [Demo Video Mistakes — Spiel Creative](https://www.spielcreative.com/blog/demo-video-mistakes/)
- [FFmpeg Xfade Crossfade Filter — OTTVerse](https://ottverse.com/crossfade-between-videos-ffmpeg-xfade-filter/)
- [FFmpeg Xfade Easing Extensions](https://github.com/scriptituk/xfade-easing)
- [Ken Burns Effect with FFmpeg — Bannerbear](https://www.bannerbear.com/blog/how-to-do-a-ken-burns-style-effect-with-ffmpeg/)
- [Smooth Zoompan with No Jiggle](https://www.datarecoveryunion.com/video-ffmpeg-smooth-zoompan-with-no-jiggle/)
- [FFmpeg Drawtext Filter — OTTVerse](https://ottverse.com/ffmpeg-drawtext-filter-dynamic-overlays-timecode-scrolling-text-credits/)
- [FFmpeg Drawtext Animations — Brayden Blackwell](https://www.braydenblackwell.com/blog/ffmpeg-text-rendering)
- [Picture-in-Picture with FFmpeg](https://www.oodlestechnologies.com/blogs/PICTURE-IN-PICTURE-effect-using-FFMPEG/)
- [Color Grading with FFmpeg](https://gabor.heja.hu/blog/2024/12/10/using-ffmpeg-to-color-correct-color-grade-a-video-lut-hald-clut/)
- [Video Clip Length Guide — VidPros](https://vidpros.com/video-clip-length/)
- [Grab Viewers' Attention in 10 Seconds — Demo Duck](https://demoduck.com/blog/grab-viewers-attention-in-10-seconds/)
- [Video Marketing Metrics 2026 — Swydo](https://www.swydo.com/blog/video-marketing-metrics/)
- [State of Demo Conversion Rates 2025](https://www.revenuehero.io/blog/the-state-of-demo-conversion-rates-in-2025)
- [Rotato — 3D Mockup Generator](https://rotato.app/)
- [Mixkit Free Sound Effects](https://mixkit.co/free-sound-effects/)
- [Freesound.org](https://freesound.org/)
- [Pixabay Sound Effects](https://pixabay.com/sound-effects/)
- [YouTube Audio Library](https://studio.youtube.com/channel/UC/music)
- [Bensound Royalty-Free Music](https://www.bensound.com/)
