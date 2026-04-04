# Storyboard PAS Schema v1 — FLUXION Video Factory

## Formato
30 secondi totali, 5 beat, struttura PAS (Problem-Agitation-Solution).

## Beat Structure

| Beat | Nome | Timing | Durata | Audio | Scopo |
|------|------|--------|--------|-------|-------|
| 1 | HOOK | 0-6s | 6s | Silenzio + suono diegetico | Catturare attenzione visiva |
| 2 | PROBLEM | 6-14s | 8s | Voiceover Isabella (empatica) | Dato reale + pain point |
| 3 | AGITATION | 14-18s | 4s | Voiceover Isabella (diretta) | "Ogni. Singolo. Giorno." |
| 4 | SOLUTION | 18-26s | 8s | Voiceover Isabella (speranzosa) | FLUXION + Sara risolvono |
| 5 | CTA | 26-30s | 4s | Voiceover Isabella (sicura) | €497 una volta per sempre |

## JSON Schema

```json
{
  "$schema": "fluxion-storyboard-v1",
  "verticale": "string",
  "label": "string",
  "duration_total": 30,
  "beats": [
    {
      "beat": 1,
      "name": "HOOK",
      "start_sec": 0,
      "duration_sec": 6,
      "video_prompt": "string — prompt per AI video gen (Kling/Veo)",
      "voiceover": null,
      "music_mood": "tense_minimal",
      "text_overlay": null
    },
    {
      "beat": 2,
      "name": "PROBLEM",
      "start_sec": 6,
      "duration_sec": 8,
      "video_prompt": "string",
      "voiceover": {
        "text": "string — testo italiano",
        "voice": "it-IT-IsabellaNeural",
        "style": "empathetic"
      },
      "music_mood": "tense_building",
      "text_overlay": null
    },
    {
      "beat": 3,
      "name": "AGITATION",
      "start_sec": 14,
      "duration_sec": 4,
      "video_prompt": "string",
      "voiceover": {
        "text": "Ogni. Singolo. Giorno.",
        "voice": "it-IT-IsabellaNeural",
        "style": "direct"
      },
      "music_mood": "tension_peak",
      "text_overlay": "Ogni. Singolo. Giorno."
    },
    {
      "beat": 4,
      "name": "SOLUTION",
      "start_sec": 18,
      "duration_sec": 8,
      "video_prompt": "string",
      "voiceover": {
        "text": "string",
        "voice": "it-IT-IsabellaNeural",
        "style": "hopeful"
      },
      "music_mood": "uplifting_warm",
      "text_overlay": null
    },
    {
      "beat": 5,
      "name": "CTA",
      "start_sec": 26,
      "duration_sec": 4,
      "video_prompt": null,
      "voiceover": {
        "text": "FLUXION. Quattrocentonovantasette euro. Una volta. Per sempre.",
        "voice": "it-IT-IsabellaNeural",
        "style": "confident"
      },
      "music_mood": "silence",
      "text_overlay": null,
      "cta_frame": {
        "lines": ["FLUXION", "subtitle", "€497 una volta. Per sempre.", "competitor_price", "fluxion-landing.pages.dev"]
      }
    }
  ],
  "video_gen_config": {
    "aspect_ratio": "9:16",
    "duration_per_clip": 8,
    "negative_prompt": "text overlay, watermarks, logos, blurry, distorted faces, low quality, CGI, artificial, stock footage look",
    "style_prefix": "Cinematic 4K, shallow depth of field, warm Mediterranean lighting, authentic documentary feel",
    "kling_mode": "standard",
    "veo_tier": "fast"
  },
  "music_gen_config": {
    "model": "facebook/musicgen-large",
    "duration_sec": 30,
    "genre_hint": "string — per-vertical music flavor"
  }
}
```

## Regole Prompt Video
1. MAI testo nel video (AI genera testo illeggibile)
2. SEMPRE specificare "9:16 vertical" nel prompt
3. SEMPRE menzionare "Italian" per contesto locale
4. Camera movement per ogni clip (dolly, tracking, slow pan)
5. Lighting specifico per mood (freddo=pain, caldo=solution)
6. Negative prompt SEMPRE presente
7. Generare 3+ varianti per clip, scegliere la migliore
