#!/usr/bin/env python3
"""
add-features-voiceover.py
Aggiunge voiceover alla sezione FEATURES del video landing FLUXION.

La sezione features in assemble_all.py inizia a hook_dur (18s = 9 clip × 2s)
e dura 19s (8 feature × 2s + 3s finale).

Strategia:
  1. Genera audio voiceover con edge-tts (IsabellaNeural)
  2. Misce il voiceover nel video esistente (solo nel range 18-37s)
  3. Output: landing_final_16x9_v2.mp4

Struttura features (ogni feature 2.0s, finale 3.0s):
  s00  0-2s   Fatture elettroniche
  s01  2-4s   Ordini ai fornitori
  s02  4-6s   Gestione dipendenti
  s03  6-8s   Cassa e prima nota
  s04  8-10s  Schede professionali
  s05  10-12s Segretaria AI 24/7
  s06  12-14s Messaggi automatici
  s07  14-16s Salvataggio automatico
  fin  16-19s Tutti + tagline
"""

import asyncio
import subprocess
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("ERRORE: edge_tts non installato. Esegui: pip install edge-tts")
    sys.exit(1)

BASE        = Path("/Volumes/MontereyT7/FLUXION")
LANDING_OUT = BASE / "video-factory/output/landing"
SRC_VIDEO   = LANDING_OUT / "landing_final_16x9.mp4"
DST_VIDEO   = LANDING_OUT / "landing_final_16x9_v2.mp4"
FEAT_AUDIO  = LANDING_OUT / "features_voiceover.mp3"

# Timing nel video sorgente
FEATURES_START_SEC = 18.0   # dopo hook montage (9 clip × 2s)
FEATURES_DUR_SEC   = 19.0   # 8×2s + 3s finale

# ─── Copy voiceover script ────────────────────────────────────────────────────
# 19 secondi totali. Ogni riga è separata dalla precedente da ~0.3s di pausa
# naturale nel TTS. Le frasi brevi danno ritmo e "valore" a ogni feature.
SCRIPT = """\
Un software che fa tutto.

Fatture elettroniche SDI — un click, fatto.

Ordini ai fornitori automatici — non finisce più nulla.

Turni, ferie e provvigioni dei dipendenti. Basta Excel.

La cassa e la prima nota si aggiornano da sole.

Ogni cliente ha la sua scheda professionale.

Sara risponde al telefono, ventiquattro ore su sette.

Promemoria, auguri, promo — tutto automatico. Tu non tocchi nulla.

I tuoi dati, al sicuro, per sempre.

Un solo acquisto. Per sempre.\
"""

VOICE = "it-IT-IsabellaNeural"


async def generate_audio():
    print(f"Generando voiceover ({VOICE})...")
    communicate = edge_tts.Communicate(SCRIPT, VOICE, rate="+5%", volume="+0%")
    await communicate.save(str(FEAT_AUDIO))
    print(f"  Audio salvato: {FEAT_AUDIO}")


def get_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def run(cmd, label=""):
    if label:
        print(f"  {label}...", end=" ", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRORE")
        print(f"    {r.stderr[-600:]}")
        return False
    if label:
        print("OK")
    return True


def mix_voiceover():
    """
    Mix features_voiceover.mp3 into landing_final_16x9.mp4.

    Tecnica:
    - Prende l'audio originale del video (musica di sottofondo)
    - Aggiunge il voiceover a partire da FEATURES_START_SEC
    - Volume voiceover 1.0, musica 0.15 durante la sezione features
    - Fuori dalla sezione features: musica originale invariata

    FFmpeg:
      [0] sorgente video
      [1] voiceover
      amix con adelay + volume ducking tramite sidechaincompress o
      più semplicemente: amerge con volume expression.
    """
    feat_dur = get_duration(FEAT_AUDIO)
    vid_dur  = get_duration(SRC_VIDEO)
    print(f"  Video: {vid_dur:.1f}s | Features voiceover: {feat_dur:.1f}s")
    print(f"  Features section: {FEATURES_START_SEC}s → {FEATURES_START_SEC + feat_dur:.1f}s")

    delay_ms = int(FEATURES_START_SEC * 1000)

    # FFmpeg filter:
    # - Estrae audio originale e abbassa volume durante features section
    # - Aggiunge voiceover con delay
    # - Mix finale
    filter_complex = (
        f"[0:a]volume=1.0[orig];"                                      # audio originale pieno
        f"[1:a]adelay={delay_ms}|{delay_ms},volume=1.1[vo];"          # voiceover con delay
        f"[orig][vo]amix=inputs=2:duration=first:weights=0.15 1[aout]" # mix: orig 15%, vo 100%
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(SRC_VIDEO),
        "-i", str(FEAT_AUDIO),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(DST_VIDEO),
    ]
    return run(cmd, "Mixando audio")


def main():
    print("=" * 60)
    print("  FLUXION — Features Voiceover Adder")
    print("=" * 60)

    if not SRC_VIDEO.exists():
        print(f"ERRORE: video sorgente non trovato: {SRC_VIDEO}")
        sys.exit(1)

    # 1. Genera audio
    asyncio.run(generate_audio())

    feat_dur = get_duration(FEAT_AUDIO)
    print(f"  Durata audio generato: {feat_dur:.1f}s (section: {FEATURES_DUR_SEC}s)")

    if feat_dur < 5:
        print("ERRORE: audio troppo corto, qualcosa è andato storto con edge-tts")
        sys.exit(1)

    # 2. Mix
    if not mix_voiceover():
        sys.exit(1)

    out_dur = get_duration(DST_VIDEO)
    out_mb  = DST_VIDEO.stat().st_size / 1024 / 1024 if DST_VIDEO.exists() else 0
    print(f"\n  OUTPUT: {DST_VIDEO.name}")
    print(f"  Durata: {out_dur:.1f}s | Dimensione: {out_mb:.1f}MB")
    print(f"\n  ✅ landing_final_16x9_v2.mp4 pronto!")
    print(f"  Preview: open '{DST_VIDEO}'")


if __name__ == "__main__":
    main()
