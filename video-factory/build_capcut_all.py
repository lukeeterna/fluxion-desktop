"""
build_capcut_all.py — Genera progetti CapCut per TUTTI i verticali FLUXION
Stessa struttura del parrucchiere: Veo3 hook + 6 screenshot + CTA + audio

Usage:
  python3 build_capcut_all.py                     # tutti gli 8 verticali
  python3 build_capcut_all.py --vertical barbiere # solo uno
"""

import json
import sys
from pathlib import Path

from pycapcut import (
    DraftFolder, VideoSegment, VideoMaterial, AudioSegment, AudioMaterial,
    TextSegment, TextStyle, TextBackground, Timerange,
    KeyframeProperty, ClipSettings, FontType, TrackType, trange,
)

SEC = 1_000_000  # microseconds

# Media DEVE essere su SSD locale — CapCut non legge volumi esterni
LOCAL_MEDIA = Path.home() / "Desktop" / "fluxion_media"
SCREENSHOTS = LOCAL_MEDIA / "screenshots"
OUTPUT_BASE = LOCAL_MEDIA  # clip e voiceover sono in LOCAL_MEDIA/{verticale}/
MUSIC = LOCAL_MEDIA / "music" / "background-music.mp3"
CAPCUT_DRAFTS = str(Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft")

# Mapping verticale → scheda screenshot + sottotitoli specifici
VERTICALI_CONFIG = {
    "barbiere": {
        "label": "Barbiere",
        "scheda": "12-scheda-parrucchiere.png",  # barbiere usa stessa scheda parrucchiere
        "scheda_subtitle": "Scheda cliente — Taglio e barba",
        "competitor_line": "Competitor: €4.320 in 3 anni",
        "screenshots": [
            ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
            ("12-scheda-parrucchiere.png", 17, 26, "Scheda cliente — Taglio e barba"),
            ("02-calendario.png", 26, 34, "Sara prenota mentre tu hai il rasoio in mano"),
            ("22-pacchetti.png", 34, 42, "Crei i tuoi pacchetti — WhatsApp automatico"),
            ("10-analytics.png", 42, 50, "Conferma WhatsApp: 100%"),
            ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
        ],
    },
    "officina": {
        "label": "Officina Meccanica",
        "scheda": "18-scheda-veicoli.png",
        "scheda_subtitle": "Scheda veicolo — Revisione e tagliandi",
        "competitor_line": "FAST Officina: €1.800–5.400 in 3 anni",
        "screenshots": [
            ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
            ("18-scheda-veicoli.png", 17, 26, "Scheda veicolo — Revisione e tagliandi"),
            ("02-calendario.png", 26, 34, "Sara risponde mentre sei sotto al cofano"),
            ("03-clienti.png", 34, 42, "WhatsApp automatico: auto è pronta"),
            ("10-analytics.png", 42, 50, "Zero telefonate — tutto automatico"),
            ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
        ],
    },
    "carrozzeria": {
        "label": "Carrozzeria",
        "scheda": "19-scheda-carrozzeria.png",
        "scheda_subtitle": "Scheda sinistro — Stato riparazione",
        "competitor_line": "Competitor: €2.880–7.200 in 3 anni",
        "screenshots": [
            ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
            ("19-scheda-carrozzeria.png", 17, 26, "Scheda sinistro — Stato riparazione"),
            ("02-calendario.png", 26, 34, "WhatsApp automatico: stato riparazione"),
            ("03-clienti.png", 34, 42, "Il cliente non chiama più — sa già tutto"),
            ("10-analytics.png", 42, 50, "Zero telefonate — tutto automatico"),
            ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
        ],
    },
    "dentista": {
        "label": "Studio Dentistico",
        "scheda": "17-scheda-odontoiatrica.png",
        "scheda_subtitle": "Scheda paziente — Anamnesi digitale",
        "competitor_line": "XDENT: €7.200+ in 3 anni",
        "screenshots": [
            ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
            ("17-scheda-odontoiatrica.png", 17, 26, "Scheda paziente — Anamnesi digitale"),
            ("02-calendario.png", 26, 34, "Promemoria 24h — no-show dal 23% al 7%"),
            ("22-pacchetti.png", 34, 42, "Pacchetti trattamenti — tutto tracciato"),
            ("10-analytics.png", 42, 50, "€200/ora salvati per ogni no-show evitato"),
            ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
        ],
    },
    "centro_estetico": {
        "label": "Centro Estetico",
        "scheda": "14-scheda-estetica.png",
        "scheda_subtitle": "Scheda estetica — Controindicazioni",
        "competitor_line": "Treatwell: €22.500/anno (sul tuo fatturato medio)",
        "screenshots": [
            ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
            ("14-scheda-estetica.png", 17, 26, "Scheda estetica — Controindicazioni"),
            ("02-calendario.png", 26, 34, "I tuoi clienti sono tuoi, non di Treatwell"),
            ("22-pacchetti.png", 34, 42, "Pacchetti promo — sedute tracciate"),
            ("10-analytics.png", 42, 50, "Zero commissioni — zero piattaforme"),
            ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
        ],
    },
    "nail_artist": {
        "label": "Nail Artist",
        "scheda": "14-scheda-estetica.png",  # nail usa scheda estetica
        "scheda_subtitle": "Scheda cliente — Allergie e preferenze",
        "competitor_line": "Competitor: €4.320 in 3 anni",
        "screenshots": [
            ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
            ("14-scheda-estetica.png", 17, 26, "Scheda cliente — Allergie e preferenze"),
            ("02-calendario.png", 26, 34, "Sara prenota — le tue mani restano ferme"),
            ("22-pacchetti.png", 34, 42, "Pacchetti nail art — tutto tracciato"),
            ("10-analytics.png", 42, 50, "No-show giù — postazione sempre occupata"),
            ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
        ],
    },
    "palestra": {
        "label": "Palestra",
        "scheda": "13-scheda-fitness.png",
        "scheda_subtitle": "Scheda fitness — Abbonamenti e certificati",
        "competitor_line": "Competitor: €3.600–7.200 in 3 anni",
        "screenshots": [
            ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
            ("13-scheda-fitness.png", 17, 26, "Scheda fitness — Abbonamenti e certificati"),
            ("02-calendario.png", 26, 34, "Promemoria rinnovo — il 50% non sparisce più"),
            ("23-fedelta.png", 34, 42, "Programma fedeltà — clienti che tornano"),
            ("10-analytics.png", 42, 50, "Retention stabile — anche a febbraio"),
            ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
        ],
    },
    "fisioterapista": {
        "label": "Fisioterapista",
        "scheda": "16-scheda-fisioterapia.png",
        "scheda_subtitle": "Scheda paziente — VAS e sedute",
        "competitor_line": "Competitor: €1.080–2.880 in 3 anni",
        "screenshots": [
            ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
            ("16-scheda-fisioterapia.png", 17, 26, "Scheda paziente — VAS e sedute"),
            ("02-calendario.png", 26, 34, "Promemoria seduta — il ciclo va a termine"),
            ("03-clienti.png", 34, 42, "Progressione tracciata — il paziente guarisce"),
            ("10-analytics.png", 42, 50, "Nessun ciclo interrotto — nessuna recidiva"),
            ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
        ],
    },
}


def pick_best_clip(clips_dir: Path, verticale: str) -> str:
    """Trova la migliore clip Veo 3 per l'hook (preferisci v2, poi v1)."""
    # Cerca clip con naming convention: {verticale}_clip1_v2.mp4, _v1.mp4, etc.
    # Oppure naming parrucchiere: {verticale}_salon_beauty_v2.mp4
    candidates = [
        f"{verticale}_clip1_v2.mp4",
        f"{verticale}_clip1_v1.mp4",
        f"{verticale}_salon_beauty_v2.mp4",
        f"{verticale}_hook_warm_v2.mp4",
        f"{verticale}_hook_warm_v1.mp4",
    ]
    for c in candidates:
        p = clips_dir / c
        if p.exists():
            return str(p)

    # Fallback: any mp4 in clips dir
    mp4s = sorted(clips_dir.glob("*.mp4"))
    if mp4s:
        return str(mp4s[0])

    return None


def build_verticale(verticale: str, config: dict):
    """Genera progetto CapCut per un verticale."""
    label = config["label"]
    clips_dir = OUTPUT_BASE / verticale / "clips"
    voiceover_path = OUTPUT_BASE / verticale / f"{verticale}_voiceover.mp3"

    print(f"\n{'='*60}")
    print(f"FLUXION — CapCut {label}")
    print(f"{'='*60}")

    # Check clip exists
    clip_path = pick_best_clip(clips_dir, verticale)
    if not clip_path:
        print(f"  ⚠️  SKIP: nessuna clip Veo 3 in {clips_dir}")
        return False

    # Create draft
    draft_name = f"FLUXION_{verticale.title().replace('_', '')}"
    folder = DraftFolder(CAPCUT_DRAFTS)
    script = folder.create_draft(draft_name, width=1080, height=1920, fps=30, allow_replace=True)

    # Create tracks
    script.add_track(TrackType.video, "video_main")
    script.add_track(TrackType.text, "subtitles")
    script.add_track(TrackType.text, "cta_text")
    script.add_track(TrackType.audio, "voiceover")
    script.add_track(TrackType.audio, "music")

    # ─── Block 1: Veo 3 Hook (0-8s) ───
    print(f"\n[1] Veo 3 hook: {Path(clip_path).name}")
    vm = VideoMaterial(clip_path)
    vs = VideoSegment(vm, trange(0, 8 * SEC),
                      clip_settings=ClipSettings(scale_x=1.5, scale_y=1.5))
    script.add_segment(vs, "video_main")

    # ─── Blocks 2-7: Screenshots with Ken Burns ───
    print(f"[2] Screenshots...")
    for fname, start, end, subtitle in config["screenshots"]:
        dur = end - start
        img = str(SCREENSHOTS / fname)
        if not (SCREENSHOTS / fname).exists():
            print(f"  ⚠️  Missing: {fname}")
            continue
        vm = VideoMaterial(img)
        vs = VideoSegment(vm, trange(start * SEC, dur * SEC),
                          clip_settings=ClipSettings(scale_x=1.8, scale_y=1.8))
        vs.add_keyframe(KeyframeProperty.scale_x, 0, 1.8)
        vs.add_keyframe(KeyframeProperty.scale_x, dur * SEC, 2.0)
        vs.add_keyframe(KeyframeProperty.scale_y, 0, 1.8)
        vs.add_keyframe(KeyframeProperty.scale_y, dur * SEC, 2.0)
        script.add_segment(vs, "video_main")

        ts = TextSegment(
            subtitle,
            trange(int((start + 0.5) * SEC), int((dur - 1) * SEC)),
            font=FontType.Poppins_Bold,
            style=TextStyle(size=7.0, color=(0.13, 0.83, 0.93)),
            background=TextBackground(color=(0, 0, 0), alpha=0.6),
        )
        script.add_segment(ts, "subtitles")
        print(f"  + {fname} [{start}-{end}s]")

    # ─── Block 8: CTA (60-80s) — sfondo nero + testi in sequenza ───
    print(f"[3] CTA...")
    black_frame = str(LOCAL_MEDIA / "black_frame.png")
    vm_black = VideoMaterial(black_frame)
    vs_black = VideoSegment(vm_black, trange(60 * SEC, 20 * SEC))
    script.add_segment(vs_black, "video_main")
    print(f"  + Black frame [60-80s]")

    # Testi CTA: appaiono in sequenza, ognuno dura 3-4s poi scompare
    cta_texts = [
        (60, 4, "FLUXION", 14.0, (1, 1, 1)),
        (62, 4, "Il gestionale che non ti costa ogni mese", 5.0, (0.67, 0.67, 0.67)),
        (64, 4, "€497", 18.0, (1, 1, 1)),
        (66, 4, "una volta. per sempre.", 7.0, (1, 1, 1)),
        (68, 4, config["competitor_line"], 4.5, (1, 0.33, 0.33)),
        (72, 8, "fluxion-landing.pages.dev", 8.0, (0.47, 0.6, 1)),
    ]
    for i, (t_start, t_dur, text, size, color) in enumerate(cta_texts):
        track_name = f"cta_{i}"
        script.add_track(TrackType.text, track_name)
        ts = TextSegment(
            text,
            trange(int(t_start * SEC), int(t_dur * SEC)),
            font=FontType.Poppins_Bold,
            style=TextStyle(size=size, color=color),
        )
        script.add_segment(ts, track_name)

    # ─── Audio ───
    print(f"[4] Audio...")
    if voiceover_path.exists():
        am = AudioMaterial(str(voiceover_path))
        vo_dur = am.duration
        aus = AudioSegment(am, trange(0, vo_dur), volume=1.0)
        script.add_segment(aus, "voiceover")
        print(f"  + Voiceover ({vo_dur/SEC:.1f}s)")
    else:
        print(f"  ⚠️  No voiceover: {voiceover_path}")

    if MUSIC.exists():
        am2 = AudioMaterial(str(MUSIC))
        music_dur = min(am2.duration, 80 * SEC)
        aus2 = AudioSegment(am2, trange(0, music_dur), volume=0.08)
        script.add_segment(aus2, "music")
        print(f"  + Music ({music_dur/SEC:.1f}s @ 8%)")

    # ─── Save ───
    script.save()
    print(f"\n✅ Draft '{draft_name}' salvato in CapCut!")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertical", "-v", help="Verticale specifico")
    args = parser.parse_args()

    if args.vertical:
        if args.vertical not in VERTICALI_CONFIG:
            print(f"Verticale '{args.vertical}' non trovato. Disponibili: {list(VERTICALI_CONFIG.keys())}")
            sys.exit(1)
        verticali = {args.vertical: VERTICALI_CONFIG[args.vertical]}
    else:
        verticali = VERTICALI_CONFIG

    ok = 0
    skip = 0
    for v, config in verticali.items():
        if build_verticale(v, config):
            ok += 1
        else:
            skip += 1

    print(f"\n{'='*60}")
    print(f"COMPLETATO: {ok} progetti CapCut creati, {skip} skippati (clip mancanti)")
    print(f"Apri CapCut Desktop → troverai i draft FLUXION_*")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
