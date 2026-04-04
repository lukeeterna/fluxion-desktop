"""
build_capcut_v2.py — Genera progetto CapCut con pyCapCut
"""
from pycapcut import (
    DraftFolder, VideoSegment, VideoMaterial, AudioSegment, AudioMaterial,
    TextSegment, TextStyle, TextBackground, Timerange,
    KeyframeProperty, ClipSettings, FontType, TrackType, trange,
)
from pathlib import Path

# Paths
# Media DEVE essere su SSD locale — CapCut non legge volumi esterni
LOCAL_MEDIA = Path.home() / "Desktop" / "fluxion_media"
SCREENSHOTS = (LOCAL_MEDIA / "screenshots").resolve()
CLIPS = (LOCAL_MEDIA / "parrucchiere" / "clips").resolve()
MUSIC = (LOCAL_MEDIA / "music" / "background-music.mp3").resolve()
VOICEOVER = (LOCAL_MEDIA / "parrucchiere" / "parrucchiere_voiceover.mp3").resolve()
CAPCUT_DRAFTS = str(Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft")

SEC = 1_000_000  # microseconds


def main():
    print("=" * 50)
    print("FLUXION — CapCut Parrucchiere (pyCapCut)")
    print("=" * 50)

    # Create draft
    folder = DraftFolder(CAPCUT_DRAFTS)
    script = folder.create_draft("FLUXION_Parrucchiere", width=1080, height=1920, fps=30, allow_replace=True)

    # Create tracks
    script.add_track(TrackType.video, "video_main")
    script.add_track(TrackType.text, "subtitles")
    script.add_track(TrackType.text, "cta_text")
    script.add_track(TrackType.audio, "voiceover")
    script.add_track(TrackType.audio, "music")

    # ─── Block 1: Veo 3 Hook (0-8s) ───
    print("\n[1] Veo 3 hook...")
    clip_path = str(CLIPS / "parrucchiere_salon_beauty_v2.mp4")
    vm = VideoMaterial(clip_path)
    vs = VideoSegment(vm, trange(0, 8 * SEC),
                      clip_settings=ClipSettings(scale_x=1.5, scale_y=1.5))
    script.add_segment(vs, "video_main")
    print(f"  + Veo3 clip [0-8s]")

    # ─── Blocks 2-7: Screenshots with Ken Burns ───
    print("\n[2] Screenshots...")
    screens = [
        ("01-dashboard.png", 8, 17, "Tutto sotto controllo — ogni mattina"),
        ("12-scheda-parrucchiere.png", 17, 26, "Scheda cliente — Formula colore"),
        ("02-calendario.png", 26, 34, "Sara conosce i tuoi clienti e i loro gusti"),
        ("22-pacchetti.png", 34, 42, "Crei i tuoi pacchetti — WhatsApp automatico"),
        ("10-analytics.png", 42, 50, "Conferma WhatsApp: 100%"),
        ("08-voice.png", 50, 60, "Sara — fatture — fornitori — cassa"),
    ]

    for fname, start, end, subtitle in screens:
        dur = end - start
        img = str(SCREENSHOTS / fname)
        vm = VideoMaterial(img)
        vs = VideoSegment(vm, trange(start * SEC, dur * SEC),
                          clip_settings=ClipSettings(scale_x=1.8, scale_y=1.8))
        # Ken Burns zoom keyframes
        vs.add_keyframe(KeyframeProperty.scale_x, 0, 1.8)
        vs.add_keyframe(KeyframeProperty.scale_x, dur * SEC, 2.0)
        vs.add_keyframe(KeyframeProperty.scale_y, 0, 1.8)
        vs.add_keyframe(KeyframeProperty.scale_y, dur * SEC, 2.0)
        script.add_segment(vs, "video_main")

        # Subtitle
        ts = TextSegment(
            subtitle,
            trange(int((start + 0.5) * SEC), int((dur - 1) * SEC)),
            font=FontType.Poppins_Bold,
            style=TextStyle(size=7.0, color=(0.13, 0.83, 0.93)),
            background=TextBackground(color=(0, 0, 0), alpha=0.6),
        )
        script.add_segment(ts, "subtitles")
        print(f"  + {fname} [{start}-{end}s]")

    # ─── Block 8: CTA (60-80s) ───
    print("\n[3] CTA texts...")
    cta_texts = [
        (60, 20, "FLUXION", 14.0, (1, 1, 1)),
        (61.5, 18.5, "Il gestionale che non ti costa ogni mese", 5.0, (0.67, 0.67, 0.67)),
        (63.5, 16.5, "€497", 18.0, (1, 1, 1)),
        (65, 15, "una volta. per sempre.", 7.0, (1, 1, 1)),
        (67, 13, "Treatwell: €4.320 in 3 anni + commissioni", 4.5, (1, 0.33, 0.33)),
        (69.5, 10.5, "fluxion-landing.pages.dev", 8.0, (0.47, 0.6, 1)),
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
    print("  + 6 CTA elements")

    # ─── Audio ───
    print("\n[4] Audio...")
    if VOICEOVER.exists():
        am = AudioMaterial(str(VOICEOVER))
        vo_dur = am.duration  # actual duration in microseconds
        aus = AudioSegment(am, trange(0, vo_dur), volume=1.0)
        script.add_segment(aus, "voiceover")
        print(f"  + Voiceover ({vo_dur/SEC:.1f}s)")

    if MUSIC.exists():
        am2 = AudioMaterial(str(MUSIC))
        music_dur = min(am2.duration, 80 * SEC)
        aus2 = AudioSegment(am2, trange(0, music_dur), volume=0.08)
        script.add_segment(aus2, "music")
        print(f"  + Music ({music_dur/SEC:.1f}s @ 8%)")

    # ─── Save ───
    print("\n[5] Saving...")
    script.save()

    print(f"\n{'=' * 50}")
    print("DONE!")
    print("Chiudi e riapri CapCut → 'FLUXION_Parrucchiere' nei drafts")
    print("Click Esporta per il video finale")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
