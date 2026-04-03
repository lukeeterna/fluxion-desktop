"""
build_capcut_parrucchiere.py — Genera progetto CapCut per video parrucchiere
Usa VectCutAPI server (localhost:9000)
"""

import requests
import json
import shutil
import os
from pathlib import Path

BASE_URL = "http://localhost:9000"
CAPCUT_DRAFT = Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft"

SCREENSHOTS = Path("../landing/screenshots")
CLIPS = Path("output/parrucchiere/clips")
VOICEOVER = Path("output/parrucchiere")
MUSIC = Path("../landing/assets/background-music.mp3")
LOGO = Path("../landing/logo_fluxion.jpg")

# Absolute paths for CapCut
def abs_path(p):
    return str(Path(p).resolve())


def api(endpoint, data):
    r = requests.post(f"{BASE_URL}/{endpoint}", json=data)
    result = r.json()
    if not result.get("success"):
        print(f"  ERROR {endpoint}: {result.get('error', 'unknown')}")
    return result


def main():
    print("=" * 50)
    print("FLUXION — CapCut Parrucchiere Project Generator")
    print("=" * 50)

    # 1. Create draft 1080x1920
    print("\n[1] Creating draft...")
    result = api("create_draft", {"width": 1080, "height": 1920})
    draft_id = result["output"]["draft_id"]
    print(f"  Draft: {draft_id}")

    # 2. Add Veo 3 hook clip (0-10s)
    print("\n[2] Adding Veo 3 hook...")
    api("add_video", {
        "draft_id": draft_id,
        "video_url": abs_path(CLIPS / "parrucchiere_salon_beauty_v2.mp4"),
        "start": 0,
        "end": 8,
        "target_start": 0,
        "volume": 0.0,
        "track_name": "main_video",
        "scale_x": 1.5,
        "scale_y": 1.5,
    })

    # 3. Add screenshots with Ken Burns keyframes
    screenshots = [
        {"file": "01-dashboard.png", "start": 8, "dur": 9, "subtitle": "Tutto sotto controllo"},
        {"file": "12-scheda-parrucchiere.png", "start": 17, "dur": 9, "subtitle": "Formula colore"},
        {"file": "02-calendario.png", "start": 26, "dur": 8, "subtitle": "Sara prenota"},
        {"file": "22-pacchetti.png", "start": 34, "dur": 8, "subtitle": "Pacchetti WhatsApp"},
        {"file": "10-analytics.png", "start": 42, "dur": 8, "subtitle": "100% conferma WA"},
        {"file": "08-voice.png", "start": 50, "dur": 10, "subtitle": "Sara Voice Agent"},
    ]

    print("\n[3] Adding screenshots with Ken Burns...")
    for i, s in enumerate(screenshots):
        img_path = abs_path(SCREENSHOTS / s["file"])
        api("add_image", {
            "draft_id": draft_id,
            "image_url": img_path,
            "start": s["start"],
            "end": s["start"] + s["dur"],
            "target_start": s["start"],
            "track_name": "main_video",
            "scale_x": 1.8,
            "scale_y": 1.8,
        })

        # Ken Burns zoom keyframe: 1.8 → 2.0 over duration
        api("add_video_keyframe", {
            "draft_id": draft_id,
            "property_type": "scale_x",
            "time_points": [s["start"], s["start"] + s["dur"]],
            "values": [1.8, 2.0],
        })
        api("add_video_keyframe", {
            "draft_id": draft_id,
            "property_type": "scale_y",
            "time_points": [s["start"], s["start"] + s["dur"]],
            "values": [1.8, 2.0],
        })

        # Subtitle text
        api("add_text", {
            "draft_id": draft_id,
            "text": s["subtitle"],
            "start": s["start"] + 0.5,
            "end": s["start"] + s["dur"] - 0.5,
            "font": "Poppins_Bold",
            "font_color": "#22D3EE",
            "font_size": 7.0,
            "track_name": "subtitle_track",
            "transform_y": -0.35,
            "background_color": "#000000",
            "background_alpha": 0.6,
            "background_style": "square",
            "background_round_radius": 0.3,
            "width": 1080,
            "height": 1920,
            "intro_animation": "fade",
            "intro_duration": 0.3,
            "outro_animation": "fade",
            "outro_duration": 0.3,
        })
        print(f"  ✓ {s['file']} [{s['start']}-{s['start']+s['dur']}s]")

    # 4. CTA section (60-80s) — black frame with text sequence
    print("\n[4] Adding CTA texts...")
    cta_start = 60

    # Logo
    if LOGO.exists():
        api("add_image", {
            "draft_id": draft_id,
            "image_url": abs_path(LOGO),
            "start": cta_start,
            "end": cta_start + 20,
            "target_start": cta_start,
            "track_name": "cta_track",
            "scale_x": 0.3,
            "scale_y": 0.3,
            "transform_y": 0.25,
        })

    cta_texts = [
        {"text": "FLUXION", "t": 0, "size": 14.0, "color": "#FFFFFF", "y": 0.05},
        {"text": "Il gestionale che non ti costa ogni mese", "t": 1.5, "size": 5.0, "color": "#AAAAAA", "y": -0.05},
        {"text": "€497", "t": 3.5, "size": 18.0, "color": "#FFFFFF", "y": -0.18},
        {"text": "una volta. per sempre.", "t": 5.0, "size": 7.0, "color": "#FFFFFF", "y": -0.28},
        {"text": "Treatwell: €4.320 in 3 anni + commissioni", "t": 7.0, "size": 4.5, "color": "#FF5555", "y": -0.40},
        {"text": "fluxion-landing.pages.dev", "t": 9.5, "size": 8.0, "color": "#7799FF", "y": -0.52},
    ]

    for ct in cta_texts:
        api("add_text", {
            "draft_id": draft_id,
            "text": ct["text"],
            "start": cta_start + ct["t"],
            "end": cta_start + 20,
            "font": "Poppins_Bold",
            "font_color": ct["color"],
            "font_size": ct["size"],
            "track_name": "cta_text",
            "transform_y": ct["y"],
            "width": 1080,
            "height": 1920,
            "intro_animation": "fade",
            "intro_duration": 0.4,
        })
    print("  ✓ CTA texts added")

    # 5. Add voiceover audio
    print("\n[5] Adding voiceover...")
    vo_path = VOICEOVER / "parrucchiere_voiceover.mp3"
    if vo_path.exists():
        api("add_audio", {
            "draft_id": draft_id,
            "audio_url": abs_path(vo_path),
            "start": 0,
            "end": 80,
            "target_start": 0,
            "volume": 1.0,
            "track_name": "voiceover",
        })
        print(f"  ✓ Voiceover: {vo_path}")

    # 6. Add background music
    print("\n[6] Adding music...")
    if MUSIC.exists():
        api("add_audio", {
            "draft_id": draft_id,
            "audio_url": abs_path(MUSIC),
            "start": 0,
            "end": 80,
            "target_start": 0,
            "volume": 0.08,
            "track_name": "music",
        })
        print(f"  ✓ Music: {MUSIC}")

    # 7. Save draft
    print("\n[7] Saving draft...")
    save_result = api("save_draft", {"draft_id": draft_id})
    print(f"  ✓ Saved: {draft_id}")

    # 8. Copy to CapCut drafts folder
    print("\n[8] Copying to CapCut...")
    src_draft = Path(f"draft_cache/{draft_id}")
    if src_draft.exists():
        dst = CAPCUT_DRAFT / draft_id
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src_draft, dst)
        print(f"  ✓ Copied to: {dst}")
    else:
        # Check VectCutAPI's own draft location
        alt_src = Path(f"tools/VectCutAPI/draft_cache/{draft_id}")
        if alt_src.exists():
            dst = CAPCUT_DRAFT / draft_id
            shutil.copytree(alt_src, dst)
            print(f"  ✓ Copied from alt: {dst}")
        else:
            print(f"  WARN: Draft folder not found at {src_draft} or {alt_src}")
            print(f"  Check: ls draft_cache/")

    print(f"\n{'=' * 50}")
    print("DONE! Apri CapCut Desktop → il progetto appare in 'I miei progetti'")
    print(f"Draft ID: {draft_id}")
    print("Click 'Esporta' per generare il video finale.")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
