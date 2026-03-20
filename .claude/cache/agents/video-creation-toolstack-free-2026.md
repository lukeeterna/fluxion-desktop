# Video Demo FLUXION — Toolstack Gratuito 2026

> Research CoVe 2026 — Creazione video demo professionale a costo ZERO
> Data: 2026-03-20 | Sessione: S106

---

## Obiettivo

Creare un video demo professionale di FLUXION (app Tauri desktop su macOS) con:
- Registrazione schermo LIVE dell'app
- Narrazione italiana TTS (voce professionale)
- Sottotitoli SRT sincronizzati
- Editing professionale (transizioni, zoom, highlight)
- Thumbnail YouTube
- **Costo totale: €0**

---

## 1. Registrazione Schermo

### Opzione A: ffmpeg + AVFoundation (CONSIGLIATA)

La soluzione migliore per macOS. Registra lo schermo a 30fps con qualità lossless.

```bash
# Elenca dispositivi disponibili
ffmpeg -f avfoundation -list_devices true -i ""

# Registra schermo intero a 30fps (device "1" = Capture screen 0)
ffmpeg -f avfoundation -framerate 30 -capture_cursor 1 -capture_mouse_clicks 1 \
  -i "1:none" -c:v libx264 -preset ultrafast -crf 0 \
  -pix_fmt yuv420p raw_screen.mkv

# Con area specifica (crop dopo)
ffmpeg -f avfoundation -framerate 30 -capture_cursor 1 -i "1:none" \
  -vf "crop=1920:1080:0:0" -c:v libx264 -preset ultrafast -crf 0 \
  raw_screen.mkv
```

**Requisiti macOS:**
- Permesso "Registrazione schermo" per Terminal/iTerm2 in System Preferences > Privacy > Screen Recording
- Su iMac: concedere il permesso PRIMA di registrare via SSH
- **NOTA**: Su macOS via SSH, la registrazione schermo richiede una sessione GUI attiva (l'utente deve essere loggato)

**Avvio/Stop automatico:**
```bash
# Avvia registrazione in background (PID salvato)
ffmpeg -f avfoundation -framerate 30 -capture_cursor 1 -capture_mouse_clicks 1 \
  -i "1:none" -c:v libx264 -preset ultrafast -crf 18 \
  -pix_fmt yuv420p raw_screen.mkv &
FFMPEG_PID=$!

# ... esegui azioni nell'app ...

# Stop registrazione
kill -INT $FFMPEG_PID
```

### Opzione B: macOS screencapture (alternativa semplice)

```bash
# Registra schermo (nativo macOS, richiede GUI)
screencapture -v -C screen_recording.mov

# Con timer (10 secondi di attesa)
screencapture -v -T 10 screen_recording.mov
```

Limitazione: meno controllo su framerate e codec rispetto a ffmpeg.

### Opzione C: OBS CLI (NON consigliata)

OBS non ha una vera modalità headless/CLI stabile. Esiste `obs-cli` ma richiede OBS in esecuzione con GUI. Troppo complesso per automazione.

### Opzione D: Playwright (NON applicabile)

Playwright registra solo contenuto WebView tramite `page.video()`, ma NON può registrare una finestra Tauri nativa (la barra del titolo, le decorazioni OS, etc.). Utile solo se servisse registrare SOLO il contenuto web interno.

### VERDETTO: ffmpeg + AVFoundation

---

## 2. Narrazione TTS (Edge-TTS)

### Voci Italiane Disponibili

| Voice ID | Nome | Genere | Stile | Consigliata |
|----------|------|--------|-------|-------------|
| `it-IT-IsabellaNeural` | Isabella | F | Calda, professionale | **SI — PRIMA SCELTA** |
| `it-IT-ElsaNeural` | Elsa | F | Chiara, neutra | Alternativa |
| `it-IT-DiegoNeural` | Diego | M | Maschile, professionale | Per voce maschile |
| `it-IT-GiuseppeNeural` | Giuseppe | M | Naturale | Alternativa maschile |
| `it-IT-BenignoNeural` | Benigno | M | Formale | NO — troppo formale |
| `it-IT-CalimeroNeural` | Calimero | M | Giovane | NO — troppo casual |
| `it-IT-CataldoNeural` | Cataldo | M | Adulto | Alternativa |
| `it-IT-FabiolaNeural` | Fabiola | F | Giovane | NO — troppo giovane |
| `it-IT-FiammaNeural` | Fiamma | F | Energica | Per spot pubblicitari |
| `it-IT-ImeldaNeural` | Imelda | F | Matura | Alternativa matura |
| `it-IT-IrmaNeural` | Irma | F | Naturale | Alternativa |
| `it-IT-LisandroNeural` | Lisandro | M | Profondo | Alternativa |
| `it-IT-PalmiraNeural` | Palmira | F | Professionale | Alternativa |
| `it-IT-PierinaNeural` | Pierina | F | Anziana | NO |
| `it-IT-RinaldoNeural` | Rinaldo | M | Standard | Alternativa |

**SCELTA: `it-IT-IsabellaNeural`** — voce femminile calda, ideale per PMI italiane. Coerente con "Sara" (voce FLUXION).

### Installazione e Uso

```bash
pip install edge-tts
```

### Generare Audio da Script

```bash
# Audio singolo
edge-tts --voice "it-IT-IsabellaNeural" \
  --rate "+0%" --pitch "+0Hz" \
  --text "Benvenuto in FLUXION, il gestionale per la tua attività." \
  --write-media narrazione.mp3 \
  --write-subtitles narrazione.vtt

# Con velocità ridotta per chiarezza (-10%)
edge-tts --voice "it-IT-IsabellaNeural" \
  --rate "-10%" \
  --text "Ecco come gestire i tuoi appuntamenti in modo semplice e veloce." \
  --write-media narrazione.mp3 \
  --write-subtitles narrazione.vtt
```

### Script Python per Narrazione Multi-Segmento

```python
#!/usr/bin/env python3
"""
generate_narration.py — Genera narrazione + sottotitoli per video demo FLUXION
"""
import asyncio
import edge_tts
import json
import os

# === SCRIPT DEL VIDEO (modifica qui) ===
SEGMENTS = [
    {
        "id": "intro",
        "text": "Benvenuto in FLUXION. Il gestionale pensato per la tua attività.",
        "pause_after": 1.5,  # secondi di pausa dopo
    },
    {
        "id": "calendario",
        "text": "Ecco il calendario. Con un click puoi creare un nuovo appuntamento, scegliere il servizio, l'operatore e l'orario.",
        "pause_after": 1.0,
    },
    {
        "id": "clienti",
        "text": "La rubrica clienti ti permette di avere tutto sotto controllo. Storico appuntamenti, preferenze, note personali.",
        "pause_after": 1.0,
    },
    {
        "id": "sara",
        "text": "E poi c'è Sara, la tua assistente vocale. Risponde al telefono ventiquattro ore su ventiquattro, prende prenotazioni e gestisce le cancellazioni. Tutto in automatico.",
        "pause_after": 1.5,
    },
    {
        "id": "whatsapp",
        "text": "Ogni prenotazione viene confermata via WhatsApp. Il cliente riceve data, ora e servizio. Zero telefonate, zero errori.",
        "pause_after": 1.0,
    },
    {
        "id": "cassa",
        "text": "La cassa è semplice e veloce. Registri l'incasso, applichi sconti, gestisci i pacchetti prepagati.",
        "pause_after": 1.0,
    },
    {
        "id": "chiusura",
        "text": "FLUXION. Tutto quello che serve alla tua attività. Senza abbonamenti, senza commissioni. Per sempre tuo.",
        "pause_after": 2.0,
    },
]

VOICE = "it-IT-IsabellaNeural"
RATE = "-5%"  # leggermente più lento per chiarezza
OUTPUT_DIR = "narration_output"


async def generate_segment(segment: dict):
    """Genera audio + sottotitoli per un singolo segmento."""
    communicate = edge_tts.Communicate(
        text=segment["text"],
        voice=VOICE,
        rate=RATE,
    )

    audio_path = os.path.join(OUTPUT_DIR, f"{segment['id']}.mp3")
    vtt_path = os.path.join(OUTPUT_DIR, f"{segment['id']}.vtt")

    await communicate.save(audio_path)

    # Genera sottotitoli VTT con word boundaries
    subtitles = []
    async for chunk in edge_tts.Communicate(text=segment["text"], voice=VOICE, rate=RATE).stream():
        if chunk["type"] == "WordBoundary":
            subtitles.append({
                "offset": chunk["offset"],       # microsecondi
                "duration": chunk["duration"],    # microsecondi
                "text": chunk["text"],
            })

    # Salva metadata sottotitoli
    meta_path = os.path.join(OUTPUT_DIR, f"{segment['id']}_meta.json")
    with open(meta_path, "w") as f:
        json.dump({
            "id": segment["id"],
            "text": segment["text"],
            "pause_after": segment["pause_after"],
            "word_boundaries": subtitles,
        }, f, indent=2, ensure_ascii=False)

    print(f"  [OK] {segment['id']}: {audio_path}")
    return audio_path


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Generazione narrazione con voce: {VOICE}")
    print(f"Segmenti: {len(SEGMENTS)}\n")

    for segment in SEGMENTS:
        await generate_segment(segment)

    print(f"\nTutti i segmenti generati in: {OUTPUT_DIR}/")
    print("Prossimo step: python compose_video.py")


if __name__ == "__main__":
    asyncio.run(main())
```

### SSML — Limitazione Nota

Edge-TTS **NON supporta SSML custom** (Microsoft lo blocca). Per controllare le pause:
- Usa `--rate` per velocità globale
- Inserisci punteggiatura nel testo (virgola = pausa breve, punto = pausa lunga)
- Genera segmenti separati e uniscili con pause ffmpeg tra uno e l'altro

---

## 3. Sottotitoli (SRT)

### Approccio A: Direttamente da Edge-TTS (CONSIGLIATO)

Edge-TTS genera sottotitoli VTT con `--write-subtitles`. I word boundaries nel metadata JSON permettono sincronizzazione precisa.

```bash
# Genera VTT direttamente
edge-tts --voice "it-IT-IsabellaNeural" \
  --text "Benvenuto in FLUXION." \
  --write-media output.mp3 \
  --write-subtitles output.vtt
```

### Conversione VTT → SRT

```python
#!/usr/bin/env python3
"""vtt_to_srt.py — Converte VTT in SRT"""
import re

def vtt_to_srt(vtt_path: str, srt_path: str):
    with open(vtt_path, "r") as f:
        content = f.read()

    # Rimuovi header VTT
    content = re.sub(r"WEBVTT\n\n", "", content)

    # Converti timestamp (. → ,)
    content = content.replace(".", ",")

    # Aggiungi indici
    blocks = content.strip().split("\n\n")
    srt_lines = []
    for i, block in enumerate(blocks, 1):
        srt_lines.append(f"{i}\n{block}\n")

    with open(srt_path, "w") as f:
        f.write("\n".join(srt_lines))

    print(f"Convertito: {vtt_path} → {srt_path}")

if __name__ == "__main__":
    import sys
    vtt_to_srt(sys.argv[1], sys.argv[2])
```

### Approccio B: Whisper su audio TTS (fallback)

Se servono sottotitoli più granulari o riallineati:

```bash
# Installa whisper
pip install openai-whisper

# Trascrivi audio → SRT
whisper narrazione_completa.mp3 \
  --model medium \
  --language it \
  --output_format srt \
  --word_timestamps True \
  --max_line_width 42 \
  --max_line_count 2 \
  --output_dir ./subtitles/
```

### Burn Sottotitoli nel Video

```bash
# Metodo 1: filtro subtitles (supporta stile ASS)
ffmpeg -i video.mp4 -vf \
  "subtitles=sottotitoli.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,BackColour=&HA0000000,BorderStyle=4,Alignment=2,MarginV=30'" \
  -c:a copy output_con_sub.mp4

# Metodo 2: drawtext (per testo singolo, non SRT)
ffmpeg -i video.mp4 -vf \
  "drawtext=text='FLUXION Demo':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=h-60:box=1:boxcolor=black@0.6:boxborderw=10" \
  -c:a copy output.mp4
```

### Stile Sottotitoli Consigliato

```
FontName=Arial
FontSize=22 (per 1080p)
PrimaryColour=&H00FFFFFF (bianco)
OutlineColour=&H00000000 (bordo nero)
Outline=2
Shadow=1
BackColour=&HA0000000 (sfondo semitrasparente nero)
BorderStyle=4 (box opaco dietro testo)
Alignment=2 (centro basso)
MarginV=30 (margine dal basso)
```

---

## 4. Composizione Video (ffmpeg)

### Unire Segmenti Audio con Pause

```bash
# Genera silenzio di 1.5 secondi
ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t 1.5 -q:a 9 silence_1.5s.mp3

# Concatena segmenti: intro + pausa + calendario + pausa + ...
# File lista (concat_list.txt):
# file 'narration_output/intro.mp3'
# file 'silence_1.5s.mp3'
# file 'narration_output/calendario.mp3'
# file 'silence_1.0s.mp3'
# ...

ffmpeg -f concat -safe 0 -i concat_list.txt -c copy narrazione_completa.mp3
```

### Sovrapporre Audio su Video

```bash
# Audio narrazione su registrazione schermo
ffmpeg -i raw_screen.mkv -i narrazione_completa.mp3 \
  -c:v libx264 -preset medium -crf 20 \
  -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 \
  -shortest \
  video_con_audio.mp4
```

### Zoom su Area Specifica (Highlight Click)

```bash
# Zoom 2x su area specifica (es. bottone a coordinate 800,400)
# per 3 secondi a partire dal secondo 15
ffmpeg -i video_con_audio.mp4 -filter_complex "
  [0:v]split[main][zoom];
  [zoom]crop=960:540:320:130,scale=1920:1080[zoomed];
  [main][zoomed]overlay=0:0:enable='between(t,15,18)'
" -c:a copy video_zoom.mp4

# Zoom progressivo (Ken Burns) su area
ffmpeg -i video_con_audio.mp4 -vf "
  zoompan=z='if(between(t,15,18),min(zoom+0.01,2.0),1)':
  x='if(between(t,15,18),800*(1-1/zoom),0)':
  y='if(between(t,15,18),400*(1-1/zoom),0)':
  d=1:s=1920x1080:fps=30
" -c:a copy video_zoom.mp4
```

### Transizioni tra Scene

```bash
# Crossfade tra due clip (1 secondo di transizione)
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex "
  [0:v]fade=t=out:st=9:d=1[v0];
  [1:v]fade=t=in:st=0:d=1[v1];
  [v0][v1]concat=n=2:v=1:a=0[outv];
  [0:a]afade=t=out:st=9:d=1[a0];
  [1:a]afade=t=in:st=0:d=1[a1];
  [a0][a1]concat=n=2:v=0:a=1[outa]
" -map "[outv]" -map "[outa]" output.mp4

# Fade in all'inizio (2 secondi)
ffmpeg -i video.mp4 -vf "fade=t=in:st=0:d=2" -af "afade=t=in:st=0:d=2" \
  -c:v libx264 -crf 20 output.mp4

# Fade out alla fine (2 secondi, assumendo video di 60s)
ffmpeg -i video.mp4 -vf "fade=t=out:st=58:d=2" -af "afade=t=out:st=58:d=2" \
  -c:v libx264 -crf 20 output.mp4
```

### Intro/Outro con Branding FLUXION

```bash
# Crea intro da immagine (5 secondi, con fade)
ffmpeg -loop 1 -i fluxion_intro.png -c:v libx264 -t 5 \
  -pix_fmt yuv420p -vf "fade=t=in:st=0:d=1,fade=t=out:st=4:d=1" \
  -r 30 intro.mp4

# Crea outro da immagine (5 secondi)
ffmpeg -loop 1 -i fluxion_outro.png -c:v libx264 -t 5 \
  -pix_fmt yuv420p -vf "fade=t=in:st=0:d=1,fade=t=out:st=4:d=1" \
  -r 30 outro.mp4

# Concatena: intro + video + outro
cat > final_concat.txt << 'EOF'
file 'intro.mp4'
file 'video_con_sub.mp4'
file 'outro.mp4'
EOF
ffmpeg -f concat -safe 0 -i final_concat.txt -c copy video_finale.mp4
```

### Encoding Finale per YouTube

```bash
# Encoding ottimizzato YouTube (H.264 High Profile, AAC)
ffmpeg -i video_finale.mp4 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -level 4.1 \
  -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 192k -ar 48000 \
  -r 30 -s 1920x1080 \
  "FLUXION_Demo_2026.mp4"
```

---

## 5. Thumbnail

### Metodo A: ImageMagick (CONSIGLIATO)

```bash
# Screenshot dell'app (da ffmpeg o screencapture)
ffmpeg -i raw_screen.mkv -ss 00:00:30 -vframes 1 screenshot.png

# Crea thumbnail 1280x720 con testo e overlay
convert screenshot.png \
  -resize 1280x720^ -gravity center -extent 1280x720 \
  \( -size 1280x200 xc:"rgba(0,0,0,0.7)" \) -gravity south -composite \
  -gravity south -pointsize 64 -fill white -font "Arial-Bold" \
  -annotate +0+110 "FLUXION" \
  -pointsize 32 -fill "#60A5FA" \
  -annotate +0+50 "Il Gestionale per la Tua Attivita" \
  thumbnail.png

# Versione con bordo e ombra
convert screenshot.png \
  -resize 1280x720^ -gravity center -extent 1280x720 \
  -brightness-contrast -10x10 \
  \( -size 1280x250 xc:"rgba(0,0,0,0.75)" \) -gravity south -composite \
  -gravity south -pointsize 72 -fill white -font "Arial-Bold" \
  -stroke black -strokewidth 2 \
  -annotate +0+140 "FLUXION Demo" \
  -stroke none -pointsize 36 -fill "#93C5FD" \
  -annotate +0+70 "Gestionale PMI — Zero Abbonamenti" \
  \( -size 120x120 xc:none -fill "#3B82F6" -draw "circle 60,60 60,10" \
     -fill white -font "Arial-Bold" -pointsize 28 -gravity center \
     -annotate +0+0 "PLAY" \) \
  -gravity center -composite \
  thumbnail_final.png
```

### Metodo B: HTML → Screenshot con Playwright/wkhtmltoimage

```bash
# Se serve un design piu complesso, crea una pagina HTML e fai screenshot
# wkhtmltoimage (gratuito)
wkhtmltoimage --width 1280 --height 720 thumbnail.html thumbnail.png
```

### Metodo C: ffmpeg drawtext (veloce ma limitato)

```bash
ffmpeg -i raw_screen.mkv -ss 00:00:30 -vframes 1 \
  -vf "scale=1280:720,
    drawbox=x=0:y=520:w=1280:h=200:color=black@0.7:t=fill,
    drawtext=text='FLUXION Demo':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=540,
    drawtext=text='Il Gestionale per la Tua Attivita':fontsize=28:fontcolor=0x60A5FA:x=(w-text_w)/2:y=620" \
  thumbnail.png
```

---

## 6. Upload YouTube

### Opzione A: YouTube Data API v3 (Automatizzato)

**Setup (una tantum):**

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea progetto "FLUXION Video"
3. Abilita "YouTube Data API v3"
4. Crea credenziali OAuth 2.0 (tipo "Desktop application")
5. Scarica `client_secrets.json`

**Installazione:**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Script upload:**
```python
#!/usr/bin/env python3
"""upload_youtube.py — Upload video demo FLUXION su YouTube"""
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"

def upload_video(
    video_file: str,
    title: str = "FLUXION Demo — Gestionale PMI Italiane",
    description: str = "",
    tags: list = None,
    category_id: str = "28",  # 28 = Science & Technology
    privacy: str = "public",
    thumbnail_file: str = None,
):
    # Autenticazione OAuth2
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["FLUXION", "gestionale", "PMI", "Italia", "software"],
            "categoryId": category_id,
            "defaultLanguage": "it",
            "defaultAudioLanguage": "it",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    print(f"Upload in corso: {video_file}")
    response = request.execute()
    video_id = response["id"]
    print(f"Upload completato! Video ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")

    # Upload thumbnail (se fornita)
    if thumbnail_file and os.path.exists(thumbnail_file):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_file),
        ).execute()
        print(f"Thumbnail caricata: {thumbnail_file}")

    return video_id


if __name__ == "__main__":
    upload_video(
        video_file="FLUXION_Demo_2026.mp4",
        title="FLUXION — Il Gestionale per la Tua Attivita | Demo Completa",
        description="""FLUXION e il gestionale desktop pensato per le PMI italiane.

Nessun abbonamento. Nessuna commissione. Per sempre tuo.

Funzionalita:
- Calendario appuntamenti intelligente
- Rubrica clienti con storico completo
- Sara: assistente vocale 24/7 per prenotazioni
- Conferme WhatsApp automatiche
- Cassa e gestione pacchetti
- Schede operatore personalizzate

Scopri di piu: https://fluxion-landing.pages.dev

#FLUXION #gestionale #PMI #Italia #software #prenotazioni""",
        tags=[
            "FLUXION", "gestionale", "PMI", "Italia", "software",
            "prenotazioni", "salone", "parrucchiere", "palestra",
            "centro estetico", "assistente vocale", "WhatsApp",
        ],
        thumbnail_file="thumbnail_final.png",
    )
```

**Quota YouTube API:** 10.000 unita/giorno. Un upload costa ~1.600 unita. Piu che sufficiente.

### Opzione B: Upload Manuale (PIU SEMPLICE)

Per un singolo video, l'upload manuale tramite [YouTube Studio](https://studio.youtube.com/) e decisamente piu pratico. Il setup OAuth2 richiede ~30 minuti e ha senso solo per upload ricorrenti.

**Consiglio: upload manuale per il primo video, API solo se servono upload frequenti.**

---

## 7. Pipeline Completa

### Prerequisiti

```bash
# Installa strumenti (tutti gratuiti)
brew install ffmpeg imagemagick
pip install edge-tts

# Opzionali
pip install openai-whisper  # solo se serve riallineare sottotitoli
pip install google-api-python-client google-auth-oauthlib  # solo per upload API
```

### Pipeline Step-by-Step

```
=== PIPELINE VIDEO DEMO FLUXION ===

FASE 1: PREPARAZIONE
  1.1  Scrivi lo script narrazione (testo italiano, ~2-3 min)
  1.2  Prepara l'app FLUXION con dati demo realistici
  1.3  Crea immagini intro/outro (1920x1080, PNG)

FASE 2: NARRAZIONE
  2.1  python generate_narration.py
       → Genera MP3 + VTT per ogni segmento
  2.2  Ascolta ogni segmento, aggiusta testo se necessario
  2.3  Concatena segmenti con pause:
       ffmpeg -f concat -safe 0 -i concat_list.txt -c copy narrazione.mp3

FASE 3: REGISTRAZIONE SCHERMO
  3.1  Apri FLUXION sull'iMac (con dati demo)
  3.2  Concedi permesso Screen Recording a Terminal
  3.3  Avvia registrazione:
       ffmpeg -f avfoundation -framerate 30 -capture_cursor 1 \
         -capture_mouse_clicks 1 -i "1:none" \
         -c:v libx264 -preset ultrafast -crf 18 raw_screen.mkv
  3.4  Esegui le azioni nell'app seguendo lo script
       (sincronizza movimenti con la durata della narrazione)
  3.5  Stop registrazione (Ctrl+C o kill -INT)

FASE 4: SOTTOTITOLI
  4.1  Converti VTT → SRT:
       python vtt_to_srt.py narrazione.vtt narrazione.srt
  4.2  (Opzionale) Verifica sync con:
       ffplay -i raw_screen.mkv -vf "subtitles=narrazione.srt"

FASE 5: COMPOSIZIONE
  5.1  Sincronizza video + audio:
       ffmpeg -i raw_screen.mkv -i narrazione.mp3 \
         -c:v libx264 -crf 20 -c:a aac -b:a 192k \
         -map 0:v -map 1:a -shortest video_base.mp4
  5.2  Burn sottotitoli:
       ffmpeg -i video_base.mp4 -vf \
         "subtitles=narrazione.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,BackColour=&HA0000000,BorderStyle=4,MarginV=30'" \
         -c:a copy video_con_sub.mp4
  5.3  Aggiungi zoom/highlight su aree specifiche (opzionale):
       ffmpeg -i video_con_sub.mp4 -filter_complex \
         "[0:v]zoompan=z='if(between(t,15,18),1.5,1)':x='if(between(t,15,18),480,0)':y='if(between(t,15,18),200,0)':d=1:s=1920x1080:fps=30[v]" \
         -map "[v]" -map 0:a -c:a copy video_zoom.mp4
  5.4  Crea intro/outro:
       ffmpeg -loop 1 -i intro.png -c:v libx264 -t 4 -pix_fmt yuv420p \
         -vf "fade=t=in:st=0:d=1,fade=t=out:st=3:d=1" -r 30 intro.mp4
       ffmpeg -loop 1 -i outro.png -c:v libx264 -t 5 -pix_fmt yuv420p \
         -vf "fade=t=in:st=0:d=1,fade=t=out:st=4:d=1" -r 30 outro.mp4
  5.5  Concatena intro + video + outro:
       echo "file intro.mp4\nfile video_con_sub.mp4\nfile outro.mp4" > final.txt
       ffmpeg -f concat -safe 0 -i final.txt -c copy video_finale.mp4
  5.6  Encoding finale YouTube-optimized:
       ffmpeg -i video_finale.mp4 \
         -c:v libx264 -preset slow -crf 18 -profile:v high \
         -pix_fmt yuv420p -movflags +faststart \
         -c:a aac -b:a 192k -ar 48000 \
         -r 30 -s 1920x1080 FLUXION_Demo_2026.mp4

FASE 6: THUMBNAIL
  6.1  Estrai frame migliore:
       ffmpeg -i video_con_sub.mp4 -ss 00:00:30 -vframes 1 screenshot.png
  6.2  Crea thumbnail:
       convert screenshot.png -resize 1280x720^ -gravity center -extent 1280x720 \
         \( -size 1280x200 xc:"rgba(0,0,0,0.7)" \) -gravity south -composite \
         -gravity south -pointsize 64 -fill white -font "Arial-Bold" \
         -annotate +0+110 "FLUXION" \
         -pointsize 32 -fill "#60A5FA" \
         -annotate +0+50 "Gestionale PMI Italiane" \
         thumbnail_final.png

FASE 7: UPLOAD
  7.1  Upload manuale su YouTube Studio (https://studio.youtube.com/)
       OPPURE
       python upload_youtube.py (se configurato OAuth2)
  7.2  Aggiungi thumbnail personalizzata
  7.3  Imposta: titolo, descrizione, tag, categoria, lingua italiana
  7.4  Pubblica!
```

---

## 8. Riepilogo Tool Stack

| Componente | Tool | Costo | Note |
|-----------|------|-------|------|
| **Screen recording** | ffmpeg + AVFoundation | €0 | Nativo macOS, 30fps, lossless |
| **Narrazione TTS** | edge-tts (IsabellaNeural) | €0 | Voce italiana professionale |
| **Sottotitoli** | edge-tts `--write-subtitles` + VTT→SRT | €0 | Sincronizzazione automatica |
| **Composizione video** | ffmpeg | €0 | Transitions, zoom, concat, burn subs |
| **Thumbnail** | ImageMagick | €0 | Testo overlay su screenshot |
| **Encoding** | ffmpeg H.264 High | €0 | Ottimizzato YouTube |
| **Upload** | YouTube Studio (manuale) | €0 | O API v3 per automazione |
| **TOTALE** | | **€0** | |

---

## 9. Consigli Produzione

### Durata Ideale
- **Demo completa**: 2-3 minuti (attenzione PMI = bassa)
- **Intro**: max 5 secondi
- **Ogni feature**: 20-30 secondi
- **Outro con CTA**: 5-10 secondi

### Script Narrazione — Template

```
[INTRO — 5s]
"FLUXION. Il gestionale per la tua attivita."

[CALENDARIO — 25s]
"Con FLUXION gestisci gli appuntamenti in un click.
Scegli il servizio, l'operatore, l'orario. Fatto."

[CLIENTI — 20s]
"Ogni cliente ha la sua scheda. Storico completo,
preferenze, note. Tutto in un posto."

[SARA — 30s]
"Sara e la tua assistente vocale. Risponde al telefono
ventiquattro ore su ventiquattro. Prende prenotazioni,
gestisce cancellazioni. In automatico."

[WHATSAPP — 15s]
"Ogni prenotazione confermata via WhatsApp.
Zero telefonate, zero errori."

[CASSA — 15s]
"Cassa semplice e veloce. Incassi, sconti,
pacchetti prepagati."

[CHIUSURA — 10s]
"FLUXION. Senza abbonamenti. Senza commissioni.
Per sempre tuo.
Scopri di piu su fluxion-landing.pages.dev"
```

### Best Practice YouTube
- **Titolo**: "FLUXION — Il Gestionale per la Tua Attivita | Demo Completa"
- **Tag**: FLUXION, gestionale, PMI, Italia, prenotazioni, salone, parrucchiere, palestra
- **Categoria**: Science & Technology (28)
- **Lingua**: Italiano
- **Sottotitoli**: carica SRT come traccia separata (oltre al burn-in)
- **End screen**: aggiungi link al sito nei ultimi 20 secondi

---

## 10. Automazione Completa (Script Bash)

```bash
#!/bin/bash
# === build_demo_video.sh ===
# Pipeline completa per video demo FLUXION
# Eseguire su iMac (dove FLUXION gira)

set -euo pipefail

PROJECT_DIR="/Volumes/MacSSD - Dati/fluxion"
OUTPUT_DIR="$PROJECT_DIR/video_demo"
VOICE="it-IT-IsabellaNeural"

echo "=== FLUXION Video Demo Pipeline ==="

# 1. Setup
mkdir -p "$OUTPUT_DIR"/{narration,screens,subtitles,final}

# 2. Genera narrazione
echo "[FASE 2] Generazione narrazione..."
cd "$OUTPUT_DIR"

# Segmento per segmento
declare -A SEGMENTS=(
  [01_intro]="Benvenuto in FLUXION. Il gestionale pensato per la tua attivita."
  [02_calendario]="Ecco il calendario. Con un click puoi creare un nuovo appuntamento. Scegli il servizio, l'operatore e l'orario."
  [03_clienti]="La rubrica clienti ti permette di avere tutto sotto controllo. Storico appuntamenti, preferenze, note personali."
  [04_sara]="E poi c'e Sara, la tua assistente vocale. Risponde al telefono ventiquattro ore su ventiquattro, prende prenotazioni e gestisce le cancellazioni. Tutto in automatico."
  [05_whatsapp]="Ogni prenotazione viene confermata via WhatsApp. Il cliente riceve data, ora e servizio. Zero telefonate, zero errori."
  [06_cassa]="La cassa e semplice e veloce. Registri l'incasso, applichi sconti, gestisci i pacchetti prepagati."
  [07_chiusura]="FLUXION. Tutto quello che serve alla tua attivita. Senza abbonamenti, senza commissioni. Per sempre tuo."
)

for key in $(echo "${!SEGMENTS[@]}" | tr ' ' '\n' | sort); do
  echo "  Generando: $key"
  edge-tts --voice "$VOICE" --rate "-5%" \
    --text "${SEGMENTS[$key]}" \
    --write-media "narration/${key}.mp3" \
    --write-subtitles "narration/${key}.vtt"
done

# 3. Genera silenzi
ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 1.0 -q:a 9 narration/silence_1s.mp3 2>/dev/null
ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 1.5 -q:a 9 narration/silence_1.5s.mp3 2>/dev/null
ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 2.0 -q:a 9 narration/silence_2s.mp3 2>/dev/null

# 4. Concatena narrazione completa
cat > narration/concat.txt << 'NARR'
file '01_intro.mp3'
file 'silence_1.5s.mp3'
file '02_calendario.mp3'
file 'silence_1s.mp3'
file '03_clienti.mp3'
file 'silence_1s.mp3'
file '04_sara.mp3'
file 'silence_1.5s.mp3'
file '05_whatsapp.mp3'
file 'silence_1s.mp3'
file '06_cassa.mp3'
file 'silence_1s.mp3'
file '07_chiusura.mp3'
file 'silence_2s.mp3'
NARR
cd narration && ffmpeg -y -f concat -safe 0 -i concat.txt -c copy ../narrazione_completa.mp3 && cd ..

echo "[FASE 2] Narrazione completata!"

# 5. Registrazione schermo (MANUALE — l'utente deve fare le azioni)
echo ""
echo "[FASE 3] REGISTRAZIONE SCHERMO"
echo "  Apri FLUXION e preparati."
echo "  Premi INVIO per avviare la registrazione..."
read -r

ffmpeg -f avfoundation -framerate 30 -capture_cursor 1 -capture_mouse_clicks 1 \
  -i "1:none" -c:v libx264 -preset ultrafast -crf 18 \
  -pix_fmt yuv420p screens/raw_screen.mkv &
FFMPEG_PID=$!

echo "  Registrazione AVVIATA (PID: $FFMPEG_PID)"
echo "  Esegui le azioni nell'app seguendo lo script."
echo "  Premi INVIO per FERMARE la registrazione..."
read -r

kill -INT $FFMPEG_PID 2>/dev/null || true
wait $FFMPEG_PID 2>/dev/null || true
echo "[FASE 3] Registrazione completata!"

# 6. Genera sottotitoli SRT da narrazione
echo "[FASE 4] Generazione sottotitoli..."
# Usa whisper per SRT preciso (opzionale, richiede whisper installato)
if command -v whisper &>/dev/null; then
  whisper narrazione_completa.mp3 --model small --language it \
    --output_format srt --max_line_width 42 --max_line_count 2 \
    --output_dir subtitles/
else
  echo "  Whisper non installato. Usando VTT da edge-tts."
  # Fallback: converti VTT concatenati (approssimativo)
  echo "  NOTA: Per sottotitoli precisi, installa whisper: pip install openai-whisper"
fi

# 7. Composizione
echo "[FASE 5] Composizione video..."

# Sincronizza video + audio
ffmpeg -y -i screens/raw_screen.mkv -i narrazione_completa.mp3 \
  -c:v libx264 -crf 20 -c:a aac -b:a 192k \
  -map 0:v -map 1:a -shortest \
  final/video_base.mp4

# Burn sottotitoli (se disponibili)
SRT_FILE="subtitles/narrazione_completa.srt"
if [ -f "$SRT_FILE" ]; then
  ffmpeg -y -i final/video_base.mp4 -vf \
    "subtitles=${SRT_FILE}:force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,BackColour=&HA0000000,BorderStyle=4,MarginV=30'" \
    -c:a copy final/video_con_sub.mp4
else
  cp final/video_base.mp4 final/video_con_sub.mp4
fi

# Encoding finale
ffmpeg -y -i final/video_con_sub.mp4 \
  -c:v libx264 -preset slow -crf 18 -profile:v high \
  -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 192k -ar 48000 \
  -r 30 -s 1920x1080 \
  final/FLUXION_Demo_2026.mp4

echo "[FASE 5] Video compilato!"

# 8. Thumbnail
echo "[FASE 6] Generazione thumbnail..."
ffmpeg -y -i final/video_con_sub.mp4 -ss 00:00:30 -vframes 1 final/screenshot.png
convert final/screenshot.png \
  -resize 1280x720^ -gravity center -extent 1280x720 \
  \( -size 1280x200 xc:"rgba(0,0,0,0.7)" \) -gravity south -composite \
  -gravity south -pointsize 64 -fill white -font "Arial-Bold" \
  -annotate +0+110 "FLUXION" \
  -pointsize 32 -fill "#60A5FA" \
  -annotate +0+50 "Gestionale PMI Italiane" \
  final/thumbnail.png

echo ""
echo "=== COMPLETATO ==="
echo "Video:     final/FLUXION_Demo_2026.mp4"
echo "Thumbnail: final/thumbnail.png"
echo ""
echo "Prossimo step: upload su YouTube Studio"
echo "https://studio.youtube.com/"
```

---

## Fonti

- [edge-tts GitHub](https://github.com/rany2/edge-tts)
- [edge-tts PyPI](https://pypi.org/project/edge-tts/)
- [FFmpeg AVFoundation macOS](https://gist.github.com/jbaranski/f61c50cc41ed7ef37cf389301d9c3347)
- [FFmpeg zoompan filter docs](https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/zoompan.html)
- [FFmpeg zoom tutorial - Creatomate](https://creatomate.com/blog/how-to-zoom-images-and-videos-using-ffmpeg)
- [FFmpeg subtitle burning - Bannerbear](https://www.bannerbear.com/blog/how-to-add-subtitles-to-a-video-with-ffmpeg-5-different-styles/)
- [Whisper SRT generation](https://github.com/openai/whisper/discussions/98)
- [YouTube Data API v3 - Upload](https://developers.google.com/youtube/v3/guides/uploading_a_video)
- [YouTube API Python Quickstart](https://developers.google.com/youtube/v3/quickstart/python)
- [ImageMagick Thumbnails](https://imagemagick.org/Usage/thumbnails/)
