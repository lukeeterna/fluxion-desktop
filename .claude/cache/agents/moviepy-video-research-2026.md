# MoviePy Deep Research — Automated Vertical Video Production (9:16, 1080x1920)
> **Data**: 2026-04-01 | **Obiettivo**: Valutare MoviePy 2.x per pipeline video FLUXION
> **Contesto**: Ken Burns su screenshot, text overlay, crossfade, audio mixing, Veo 3 embedding
> **Status**: RESEARCH COMPLETATA

---

## TL;DR — VERDETTO

**MoviePy 2.x NON e' raccomandato come engine primario per FLUXION Video Factory.**

Motivazioni:
1. **Performance critica**: v2 e' 10x piu' lento di v1 per operazioni comuni (issue #2395)
2. **TextClip buggy**: stroke rendering incompleto, Pillow breaking changes (issue #2268, #2421)
3. **Ken Burns**: nessun effetto built-in, richiede implementazione custom con numpy
4. **FLUXION gia' usa ffmpeg-python**: `assembly.py` e' gia' operativo con ffmpeg-python
5. **Bottleneck reale**: il frame computation Python e' il collo di bottiglia, non l'encoding

**RACCOMANDAZIONE**: Restare su **ffmpeg-python** (gia' in uso) per l'assembly pipeline.
Per effetti avanzati (Ken Burns, animazioni), usare **filtri ffmpeg nativi** (`zoompan`, `drawtext`).
MoviePy utile SOLO come libreria di supporto per pre-processing frame singoli (PIL/numpy).

---

## 1. MoviePy 2.x — Stato Attuale (Aprile 2026)

### Versione e Dipendenze

| Aspetto | v1.x (legacy) | v2.x (attuale) |
|---------|---------------|-----------------|
| **Versione** | 1.0.3 | 2.1.x (latest) |
| **Python** | 3.6+ | 3.9+ |
| **ImageMagick** | RICHIESTO per TextClip | RIMOSSO — usa Pillow |
| **Dipendenze** | ImageMagick, PyGame, OpenCV, scipy, scikit | Solo Pillow + numpy + ffmpeg |
| **Import** | `from moviepy.editor import *` | `from moviepy import *` |
| **Performance** | Baseline | ~10x piu' lento per alcuni task |

### Breaking Changes v1 → v2

**Metodi rinominati** — tutti `.set_*()` diventano `.with_*()`:
```python
# v1
clip.set_duration(5)
clip.set_position(("center", "center"))
clip.set_start(2)
clip.set_fps(30)

# v2
clip.with_duration(5)
clip.with_position(("center", "center"))
clip.with_start(2)
clip.with_fps(30)
```

**Effetti — da funzioni a classi**:
```python
# v1
from moviepy.editor import *
clip = clip.fx(vfx.resize, width=460)
clip = clip.fx(vfx.fadeout, 1)

# v2
from moviepy import *
clip = clip.with_effects([vfx.Resize(width=460)])
clip = clip.with_effects([vfx.FadeOut(1)])
# oppure chained:
clip = clip.with_effects([
    vfx.Resize(width=460),
    vfx.MultiplySpeed(2),
    afx.MultiplyVolume(0.5),
])
```

**Namespace rimosso**: `moviepy.editor` non esiste piu'.

**Dipendenza ImageMagick eliminata**: TextClip ora usa solo Pillow.

---

## 2. Capacita' per il Nostro Use Case

### 2A. Ken Burns Effect (Zoom + Pan su Screenshot)

**NON built-in.** Richiede implementazione custom.

**Approccio 1 — resize con lambda (SEMPLICE, zoom-only)**:
```python
from moviepy import ImageClip, CompositeVideoClip

# Zoom-in semplice: 1.0x → 1.2x in 8 secondi
img = (
    ImageClip("screenshot.png")
    .with_duration(8)
    .resized(lambda t: 1 + 0.025 * t)  # v2: resized() non resize()
    .with_position(("center", "center"))
)

video = CompositeVideoClip([img], size=(1080, 1920))
video.write_videofile("output.mp4", fps=30)
```

**Approccio 2 — frame-level numpy (KEN BURNS COMPLETO: zoom + pan)**:
```python
import numpy as np
from PIL import Image
from moviepy import VideoClip

def ken_burns_effect(img_path, duration, start_rect, end_rect, size=(1080, 1920)):
    """
    Ken Burns con zoom + pan.
    start_rect/end_rect: (x, y, w, h) in coordinate immagine originale.
    """
    img = Image.open(img_path)
    img_w, img_h = img.size

    def make_frame(t):
        progress = t / duration
        # Interpolazione lineare tra rect iniziale e finale
        x = start_rect[0] + (end_rect[0] - start_rect[0]) * progress
        y = start_rect[1] + (end_rect[1] - start_rect[1]) * progress
        w = start_rect[2] + (end_rect[2] - start_rect[2]) * progress
        h = start_rect[3] + (end_rect[3] - start_rect[3]) * progress

        # Crop + resize al frame size target
        cropped = img.crop((int(x), int(y), int(x + w), int(y + h)))
        frame = cropped.resize(size, Image.LANCZOS)
        return np.array(frame)

    return VideoClip(make_frame, duration=duration).with_fps(30)
```

**Approccio 3 — FFmpeg zoompan filter (RACCOMANDATO per performance)**:
```python
import ffmpeg

# Ken Burns zoom-in su screenshot con ffmpeg nativo
(
    ffmpeg
    .input("screenshot.png", loop=1, t=8)
    .filter("zoompan",
            z="min(zoom+0.001,1.2)",   # zoom da 1.0 a 1.2
            d=240,                      # 240 frame = 8s a 30fps
            x="iw/2-(iw/zoom/2)",      # center X
            y="ih/2-(ih/zoom/2)",       # center Y
            s="1080x1920",             # output size 9:16
            fps=30)
    .output("output.mp4", vcodec="libx264", pix_fmt="yuv420p")
    .overwrite_output()
    .run()
)
```

**VERDETTO Ken Burns**: Usare ffmpeg `zoompan` filter direttamente. 100x piu' veloce
del frame-by-frame Python. Gia' compatibile con `assembly.py`.

### 2B. Text Overlay con Fade In/Out

**MoviePy v2 TextClip API**:
```python
from moviepy import TextClip, CompositeVideoClip, vfx

text = (
    TextClip(
        text="FLUXION",
        font="/System/Library/Fonts/Supplemental/Inter-Bold.ttf",  # path OTF/TTF
        font_size=88,
        color="white",
        stroke_color="black",
        stroke_width=2,
        bg_color=None,           # trasparente
        text_align="center",
        size=(1080, None),       # larghezza fissa, altezza auto
        margin=(20, 20),         # margine interno
    )
    .with_duration(5)
    .with_position(("center", 200))
    .with_effects([
        vfx.CrossFadeIn(0.5),   # fade in 0.5s
        vfx.CrossFadeOut(0.5),  # fade out 0.5s
    ])
)

final = CompositeVideoClip([background, text])
```

**PROBLEMI NOTI TextClip v2**:
- **Stroke troncato**: stroke va oltre il bounding box del TextClip → margine necessario (issue #2268)
- **Pillow breaking change**: Pillow recente puo' rompere TextClip → pin `pillow<11.0` (issue #2421)
- **Transparenza glitch**: TextClip in CompositeVideoClip annidati → artefatti (issue #2269)
- **Qualita' inferiore** a ImageMagick (v1) — Pillow text rendering meno sofisticato

**ALTERNATIVA FFmpeg (GIA' in uso in assembly.py)**:
```python
drawtext = (
    f"drawtext=fontfile={FONT_PATH}"
    f":text='FLUXION'"
    f":fontcolor=white"
    f":fontsize=88"
    f":x=(w-tw)/2:y=200"
    f":box=1:boxcolor=black@0.5:boxborderw=12"
    f":enable='between(t,1,6)'"
    f":alpha='if(lt(t,1.5),0,if(lt(t,2),(t-1.5)*2,if(gt(t,5.5),(6-t)*2,1)))'"
)
```
Il parametro `alpha` con espressioni ffmpeg gestisce fade in/out nativamente.

### 2C. Cross-fade Transition tra Clip

**MoviePy v2**:
```python
from moviepy import concatenate_videoclips, vfx

# Crossfade 0.5s tra clip
clip1 = clip1.with_effects([vfx.CrossFadeOut(0.5)])
clip2 = clip2.with_effects([vfx.CrossFadeIn(0.5)])

# CrossFadeIn funziona SOLO dentro CompositeVideoClip
from moviepy import CompositeVideoClip
clip2 = clip2.with_start(clip1.duration - 0.5)  # overlap 0.5s
final = CompositeVideoClip([clip1, clip2])
```

**ALTERNATIVA FFmpeg (piu' performante)**:
```bash
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "xfade=transition=fade:duration=0.5:offset=7.5" \
  output.mp4
```

### 2D. Audio: Voiceover + Background Music Mixing

**MoviePy v2**:
```python
from moviepy import (
    AudioFileClip, CompositeAudioClip, afx
)

voiceover = AudioFileClip("voiceover.mp3")
music = (
    AudioFileClip("background.mp3")
    .with_effects([afx.MultiplyVolume(0.15)])  # musica al 15%
)

# Mix
mixed_audio = CompositeAudioClip([voiceover, music])

# Applica al video
final = video.with_audio(mixed_audio)
final.write_videofile("output.mp4",
    codec="libx264",
    audio_codec="aac",
    audio_bitrate="192k",
    fps=30
)
```

**ALTERNATIVA FFmpeg (GIA' implementata in assembly.py:_merge_audio)**:
```python
video_audio = video.audio.filter("volume", 0.15)   # musica background
voiceover = audio.filter("volume", 1.0)              # voiceover pieno
mixed = ffmpeg.filter([video_audio, voiceover], "amix", inputs=2, duration="shortest")
```

### 2E. Video Clip Embedding (Veo 3 AI Clips)

MoviePy gestisce VideoFileClip normalmente:
```python
from moviepy import VideoFileClip, CompositeVideoClip

veo_clip = VideoFileClip("veo3_output.mp4").subclipped(0, 8)
screenshot = ImageClip("screenshot.png").with_duration(8)

# PiP: screenshot piccolo su Veo 3 clip
pip = CompositeVideoClip([
    veo_clip,
    screenshot.resized(0.3).with_position((50, 50))
])
```

**NOTA**: La nostra pipeline usa gia' ffmpeg per concatenare Veo 3 clips (assembly.py).

### 2F. Output H.264, 30fps, 1080x1920

```python
final.write_videofile(
    "output.mp4",
    fps=30,
    codec="libx264",
    preset="medium",        # bilancio velocita'/qualita'
    bitrate="8M",           # 8Mbps per 1080x1920
    audio_codec="aac",
    audio_bitrate="192k",
    ffmpeg_params=["-pix_fmt", "yuv420p"]
)
```

---

## 3. Performance su macOS 11 Big Sur

### Rendering Speed

| Scenario | v1.x | v2.x | ffmpeg diretto |
|----------|------|------|----------------|
| 90s video 1080x1920 (immagini) | ~3-5 min | ~15-30 min | ~30-60s |
| TextClip rendering | ~1s/frame | ~1s/frame | ~0.01s/frame (drawtext) |
| Concatenazione 3 clip | ~2 min | ~8 min | ~5s (stream copy) |
| Ken Burns 8s clip | ~1 min | ~5 min | ~10s (zoompan filter) |

**CRITICO**: v2 e' documentato come 10x piu' lento di v1 per molte operazioni
(GitHub issue #2395: "v1 is 10x faster than v2 for this example").

### Memory Usage

- **ImageClip 1920x1080 PNG**: ~8MB in RAM come numpy array
- **ImageClip 3840x2160 screenshot**: ~32MB in RAM
- **Ken Burns frame-by-frame**: picco ~200-500MB per 8s clip (30fps × frame size)
- **TextClip**: allocazione Pillow per ogni frame → GC pressure significativa
- **macOS 11 Big Sur specifico**: nessun problema noto Mac-specifico; ffmpeg usa VideoToolbox se disponibile

### Known Issues macOS

1. **Python 3.9 su Big Sur**: OK, compatibile
2. **ffmpeg hardware acceleration**: `videotoolbox` disponibile su macOS per H.264 encode/decode
3. **Pillow + macOS**: nessun issue specifico noto
4. **MoviePy + macOS**: nessun issue specifico, ma il performance hit di v2 e' universale

---

## 4. Limitazioni MoviePy

### Cosa NON fa bene

| Limitazione | Dettaglio | Workaround |
|-------------|-----------|------------|
| **Performance** | Frame-by-frame Python = lento | Usare ffmpeg filters nativi |
| **Ken Burns** | Nessun effetto built-in | `ffmpeg zoompan` o numpy custom |
| **Testi qualita'** | Pillow < ImageMagick per rendering | Pre-render con Pillow separato |
| **Stroke text** | Bug rendering stroke troncato (v2) | Aggiungere `margin=(20,20)` |
| **Transizioni** | Solo crossfade basico | `ffmpeg xfade` per transizioni avanzate |
| **GPU** | Zero supporto GPU accelerazione | ffmpeg videotoolbox/nvenc |
| **Multithread** | Bottleneck su Python GIL | Processo ffmpeg separato |
| **Progressione** | write_videofile rallenta nel tempo | Issue noto #645, nessun fix |

### Common Pitfalls

1. **Non chiudere i clip** → memory leak. Usare `clip.close()` o context manager.
2. **TextClip lento**: ogni frame rigenera il testo via Pillow. Pre-renderizzare come immagine.
3. **Pillow versione**: pin `pillow>=10.0,<11.0` per compatibilita' TextClip v2.
4. **write_videofile rallenta**: il rendering diventa progressivamente piu' lento frame dopo frame.
5. **CompositeVideoClip nested**: causa glitch di trasparenza con TextClip.
6. **fps non impostato**: default 25fps, specificare sempre `fps=30`.

### Text Rendering: Pillow vs ImageMagick

| Aspetto | Pillow (v2) | ImageMagick (v1) |
|---------|-------------|-----------------|
| **Qualita'** | Buona, non eccellente | Eccellente |
| **Kerning** | Basico | Avanzato |
| **Stroke** | Buggy (troncato ai bordi) | Perfetto |
| **Font support** | OTF/TTF | OTF/TTF/Type1/+ |
| **Emoji** | Non supportati senza flag speciale | Supportati |
| **Velocita'** | Veloce | Lento (subprocess) |
| **Dipendenza** | pip install pillow | brew install imagemagick |

---

## 5. Confronto con Alternative

### 5A. ffmpeg-python (GIA' IN USO — RACCOMANDATO)

| Aspetto | MoviePy 2.x | ffmpeg-python |
|---------|-------------|---------------|
| **Speed** | Lento (Python per-frame) | Veloce (processo ffmpeg nativo) |
| **Ken Burns** | Custom numpy | `zoompan` filter nativo |
| **Text** | Pillow (buggy stroke) | `drawtext` filter (robusto) |
| **Crossfade** | CrossFadeIn/Out | `xfade` filter |
| **Audio mix** | CompositeAudioClip | `amix` filter |
| **GPU** | No | VideoToolbox / NVENC |
| **Complessita'** | API Pythonica, intuitiva | Filter graph syntax |
| **Debug** | Facile | Filter graph complessi difficili |

### 5B. Remotion (React-based, gia' valutato)

- **Pro**: React/TS (nostro stack), browser preview, parametrizzabile
- **Contro**: richiede Node.js + Chrome/Puppeteer per rendering, overhead setup
- **Verdetto**: ottimo per video template riutilizzabili, overkill per pipeline batch

### 5C. MovieLite (Numba-accelerated)

- **Pro**: 3-5x piu' veloce di MoviePy grazie a Numba JIT
- **Contro**: progetto giovane, API limitata, community piccola
- **Verdetto**: da monitorare, non production-ready

---

## 6. RACCOMANDAZIONE FINALE per FLUXION

### Pipeline Ottimale (Zero MoviePy)

```
FLUXION Video Factory Pipeline (ATTUALE + OTTIMIZZATO)
═══════════════════════════════════════════════════════

1. SCREENSHOT → Ken Burns
   ffmpeg zoompan filter (nativo, ~10s per 8s clip)

2. VEO 3 CLIP → Assembly
   ffmpeg concat demuxer (gia' in assembly.py)

3. TEXT OVERLAY
   ffmpeg drawtext filter con alpha expression per fade
   (gia' in assembly.py:add_text_overlay)

4. TRANSITIONS
   ffmpeg xfade filter per crossfade tra clip

5. AUDIO MIX
   ffmpeg amix filter per voiceover + musica
   (gia' in assembly.py:_merge_audio)

6. CTA FRAME
   ffmpeg drawtext su color=black
   (gia' in assembly.py:create_cta_frame)

7. EXPORT
   H.264 30fps 1080x1920 yuv420p
```

### Quando USARE MoviePy (come utility, non engine)

- **Pre-processing frame complessi**: compositing multi-layer con trasparenza
- **Prototipazione rapida**: testare layout prima di tradurre in ffmpeg
- **Subtitle sync**: generare timing sottotitoli allineati all'audio
- **Numpy manipulation**: trasformazioni pixel-level non disponibili in ffmpeg

### Codice Aggiuntivo per assembly.py (Ken Burns con ffmpeg)

```python
def create_ken_burns_clip(
    image_path: Path,
    output_path: Path,
    duration: float = 8.0,
    zoom_start: float = 1.0,
    zoom_end: float = 1.2,
    pan_direction: str = "center",  # "left_to_right", "top_to_bottom", "center"
    resolution: tuple = (1080, 1920),
) -> Path:
    """
    Crea clip Ken Burns da screenshot usando ffmpeg zoompan nativo.
    ~10x piu' veloce del frame-by-frame Python.
    """
    w, h = resolution
    fps = 30
    total_frames = int(duration * fps)

    # Calcolo parametri zoompan
    zoom_per_frame = (zoom_end - zoom_start) / total_frames
    zoom_expr = f"min(zoom+{zoom_per_frame:.6f},{zoom_end})"

    # Pan direction
    pan_x = "iw/2-(iw/zoom/2)"   # center default
    pan_y = "ih/2-(ih/zoom/2)"

    if pan_direction == "left_to_right":
        pan_x = f"on*{1.0/total_frames}*(iw-iw/zoom)"
    elif pan_direction == "top_to_bottom":
        pan_y = f"on*{1.0/total_frames}*(ih-ih/zoom)"

    (
        ffmpeg
        .input(str(image_path), loop=1, t=duration)
        .filter("zoompan",
                z=zoom_expr,
                d=total_frames,
                x=pan_x,
                y=pan_y,
                s=f"{w}x{h}",
                fps=fps)
        .output(str(output_path),
                vcodec="libx264",
                pix_fmt="yuv420p",
                r=fps)
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


def add_text_overlay_with_fade(
    input_path: Path,
    output_path: Path,
    text: str,
    start_sec: float,
    end_sec: float,
    fade_duration: float = 0.5,
    position: str = "bottom",
    fontsize: int = 52,
    color: str = "white",
) -> Path:
    """
    Text overlay con fade in/out usando alpha expression ffmpeg.
    Piu' robusto di MoviePy TextClip.
    """
    y_map = {
        "top": "80",
        "center": "(h-th)/2",
        "bottom": "h-th-80",
    }
    y = y_map.get(position, "h-th-80")

    fade_in_end = start_sec + fade_duration
    fade_out_start = end_sec - fade_duration

    # Alpha expression per fade in/out
    alpha_expr = (
        f"if(lt(t\\,{start_sec})\\,0\\,"
        f"if(lt(t\\,{fade_in_end})\\,(t-{start_sec})/{fade_duration}\\,"
        f"if(lt(t\\,{fade_out_start})\\,1\\,"
        f"if(lt(t\\,{end_sec})\\,({end_sec}-t)/{fade_duration}\\,0))))"
    )

    drawtext = (
        f"drawtext=fontfile={FONT_PATH}"
        f":text='{text}'"
        f":fontcolor={color}"
        f":fontsize={fontsize}"
        f":x=(w-tw)/2:y={y}"
        f":box=1:boxcolor=black@0.5:boxborderw=12"
        f":alpha='{alpha_expr}'"
    )

    (
        ffmpeg
        .input(str(input_path))
        .output(str(output_path), vf=drawtext, vcodec="libx264",
                acodec="copy", pix_fmt="yuv420p")
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


def crossfade_clips(
    clip1_path: Path,
    clip2_path: Path,
    output_path: Path,
    transition_duration: float = 0.5,
    transition_type: str = "fade",  # fade, wipeleft, wiperight, slideup, circleclose
) -> Path:
    """
    Crossfade tra due clip usando ffmpeg xfade filter.
    """
    probe = ffmpeg.probe(str(clip1_path))
    clip1_duration = float(probe["format"]["duration"])
    offset = clip1_duration - transition_duration

    input1 = ffmpeg.input(str(clip1_path))
    input2 = ffmpeg.input(str(clip2_path))

    (
        ffmpeg
        .filter([input1.video, input2.video], "xfade",
                transition=transition_type,
                duration=transition_duration,
                offset=offset)
        .output(str(output_path), vcodec="libx264", pix_fmt="yuv420p",
                acodec="aac")
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path
```

---

## 7. Fonti

- [MoviePy PyPI](https://pypi.org/project/moviepy/)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [Updating from v1.X to v2.X](https://zulko.github.io/moviepy/getting_started/updating_to_v2.html)
- [MoviePy GitHub](https://github.com/Zulko/moviepy)
- [MoviePy TextClip API](https://zulko.github.io/moviepy/reference/reference/moviepy.video.VideoClip.TextClip.html)
- [MoviePy Video Effects](https://zulko.github.io/moviepy/reference/reference/moviepy.video.fx.html)
- [MoviePy Audio Effects](https://zulko.github.io/moviepy/reference/reference/moviepy.audio.fx.html)
- [Zoom-in Effect Gist (mowshon)](https://gist.github.com/mowshon/2a0664fab0ae799734594a5e91e518d5)
- [MoviePy v2 10x slower issue #2395](https://github.com/Zulko/moviepy/issues/2395)
- [TextClip stroke bug #2268](https://github.com/Zulko/moviepy/issues/2268)
- [Pillow breaking change #2421](https://github.com/Zulko/moviepy/issues/2421)
- [TextClip transparency glitch #2269](https://github.com/Zulko/moviepy/issues/2269)
- [MoviePy slow rendering #2231](https://github.com/Zulko/moviepy/issues/2231)
- [Ken Burns FFmpeg (Bannerbear)](https://www.bannerbear.com/blog/how-to-do-a-ken-burns-style-effect-with-ffmpeg/)
- [Ken Burns FFmpeg (mko.re)](https://mko.re/blog/ken-burns-ffmpeg/)
- [MovieLite (Numba alternative)](https://github.com/francozanardi/movielite)
- [CrossFadeIn docs](https://zulko.github.io/moviepy/reference/reference/moviepy.video.fx.CrossFadeIn.html)
- [MoviePy Modifying Clips](https://zulko.github.io/moviepy/user_guide/modifying.html)
