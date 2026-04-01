#!/usr/bin/env python3
"""
FLUXION V8 — Final Video Compositing
V7 + Fedelta scene (23-fedelta.png) + "Con Sara lavori ordinato" + fix broken refs.
Reads v8-voiceover-manifest.json.
Output: landing/assets/fluxion-promo-v8.mp4
"""

import json
import subprocess
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path("/Volumes/MontereyT7/FLUXION")
AI_CLIPS = BASE / "landing" / "assets" / "ai-clips-v2"
SCREENSHOTS = BASE / "landing" / "screenshots"
LOGO = BASE / "logo_fluxion.jpg"
MUSIC = BASE / "landing" / "assets" / "background-music.mp3"
OUTPUT = BASE / "landing" / "assets" / "fluxion-promo-v8.mp4"
TMPDIR = BASE / "tmp-video-build"
MANIFEST = TMPDIR / "v8-voiceover-manifest.json"
ENDCARD_VIDEO = TMPDIR / "endcard-extended.mp4"

W, H, FPS = 1280, 720, 30
SCALE_FILTER = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,format=yuv420p"

# Try to find Impact or fallback font
FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/SFNSDisplay.ttf",
]

def get_font(size):
    for fp in FONT_PATHS:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ================================================================
# V8 SCENE DEFINITIONS
# Changes vs V7:
#   - s31: REPLACED broken 21-trasformazioni → "Con Sara lavori ordinato" (AI clip)
#   - s34b: NEW Fedeltà screenshot (23-fedelta.png) after Pacchetti
# ================================================================
SCENES = [
    # CH1: Hook (4 clips, 2s each, silent)
    {"id": "s01", "type": "ai", "file": "V04_palestra.mp4", "trim": (0, 2), "transition": "cut"},
    {"id": "s02", "type": "ai", "file": "V08_gommista.mp4", "trim": (0, 2), "transition": "cut"},
    {"id": "s03", "type": "ai", "file": "V05_estetista.mp4", "trim": (0, 2), "transition": "cut"},
    {"id": "s04", "type": "ai", "file": "V06_nails.mp4", "trim": (0, 2), "transition": "cut"},

    # CH2: Problema + numeri animati
    {"id": "s05", "type": "ai", "file": "V6-13_hook_missed_calls.mp4", "trim": (0, 8), "transition": "crossfade"},
    {"id": "s06", "type": "ai", "file": "V10_frustrazione.mp4", "trim": (0, 8), "transition": "crossfade",
     "numbers": [("250 clienti persi", 2.0, 4.5, "#FFFFFF"), ("€7.500 / anno", 5.0, 7.5, "#FF6B6B")]},
    {"id": "s07", "type": "ai", "file": "V09_elettrauto.mp4", "trim": (3, 8), "transition": "crossfade",
     "numbers": [("€900 / mese", 1.5, 4.0, "#FF6B6B")]},

    # CH3: Sara + dialogo
    {"id": "s08", "type": "ai", "file": "V16_sara_intro.mp4", "trim": (0, 8), "transition": "crossfade"},
    {"id": "s09", "type": "screenshot", "file": "08-voice.png", "transition": "crossfade"},
    {"id": "s10", "type": "ai", "file": "V18_cliente_telefono.mp4", "trim": (0, 4), "transition": "cut"},
    {"id": "s11", "type": "ai", "file": "V17_sara_dialogo.mp4", "trim": (0, 4), "transition": "cut"},
    {"id": "s12", "type": "ai", "file": "V18_cliente_telefono.mp4", "trim": (4, 7), "transition": "cut"},
    {"id": "s13", "type": "ai", "file": "V17_sara_dialogo.mp4", "trim": (4, 8), "transition": "crossfade"},
    {"id": "s14", "type": "ai", "file": "V6-03_proprietario_soddisfatto.mp4", "trim": (0, 6), "transition": "crossfade"},

    # CH4: Dashboard + Calendario
    {"id": "s15", "type": "screenshot", "file": "01-dashboard.png", "transition": "crossfade"},
    {"id": "s16", "type": "ai", "file": "V6-05_imprenditrice_pc.mp4", "trim": (0, 3), "transition": "cut"},
    {"id": "s17", "type": "screenshot", "file": "02-calendario.png", "transition": "crossfade"},

    # CH5: Schede verticali (6 verticali + selector)
    {"id": "s18", "type": "ai", "file": "V01_salone.mp4", "trim": (4, 8), "transition": "cut"},
    {"id": "s19", "type": "screenshot", "file": "12-scheda-parrucchiere.png", "transition": "crossfade"},
    {"id": "s20", "type": "ai", "file": "V02_officina.mp4", "trim": (4, 8), "transition": "cut"},
    {"id": "s21", "type": "screenshot", "file": "18-scheda-veicoli.png", "transition": "crossfade"},
    {"id": "s22", "type": "ai", "file": "V14_medico_paziente.mp4", "trim": (0, 4), "transition": "cut"},
    {"id": "s23", "type": "screenshot", "file": "15-scheda-medica.png", "transition": "crossfade"},
    {"id": "s24", "type": "ai", "file": "V03_dentista.mp4", "trim": (4, 8), "transition": "cut"},
    {"id": "s25", "type": "screenshot", "file": "17-scheda-odontoiatrica.png", "transition": "crossfade"},
    {"id": "s26", "type": "ai", "file": "V07_fisioterapista.mp4", "trim": (3, 7), "transition": "cut"},
    {"id": "s27", "type": "screenshot", "file": "16-scheda-fisioterapia.png", "transition": "crossfade"},
    {"id": "s28", "type": "ai", "file": "V04_palestra.mp4", "trim": (3, 7), "transition": "cut"},
    {"id": "s29", "type": "screenshot", "file": "20-scheda-selector.png", "transition": "crossfade"},

    # CH6: "Con Sara lavori ordinato" (REPLACED broken portfolio scene)
    {"id": "s30", "type": "ai", "file": "V15_foto_portfolio.mp4", "trim": (0, 5), "transition": "crossfade"},
    {"id": "s31", "type": "ai", "file": "V6-03_proprietario_soddisfatto.mp4", "trim": (2, 8), "transition": "crossfade"},

    # CH7: Fidelizzazione + Pacchetti + Fedeltà
    {"id": "s32", "type": "ai", "file": "V11_qrcode.mp4", "trim": (0, 5), "transition": "cut"},
    {"id": "s33", "type": "ai", "file": "V6-04_cliente_whatsapp.mp4", "trim": (0, 4), "transition": "crossfade"},
    {"id": "s34", "type": "screenshot", "file": "22-pacchetti.png", "transition": "crossfade"},
    {"id": "s34b", "type": "screenshot", "file": "23-fedelta.png", "transition": "crossfade"},

    # CH8: Gestione Completa
    {"id": "s35", "type": "screenshot", "file": "05-operatori.png", "transition": "crossfade"},
    {"id": "s36", "type": "ai", "file": "V6-05_imprenditrice_pc.mp4", "trim": (3, 7), "transition": "cut"},
    {"id": "s37", "type": "screenshot", "file": "04-servizi.png", "transition": "crossfade"},
    {"id": "s38", "type": "screenshot", "file": "06-fatture.png", "transition": "crossfade"},
    {"id": "s39", "type": "screenshot", "file": "09-fornitori.png", "transition": "crossfade"},
    {"id": "s40", "type": "screenshot", "file": "07-cassa.png", "transition": "crossfade"},
    {"id": "s41", "type": "screenshot", "file": "10-analytics.png", "transition": "crossfade"},

    # CH9: Prezzo + numeri animati
    {"id": "s42", "type": "ai", "file": "V12_soddisfatta.mp4", "trim": (0, 8), "loop": True, "transition": "crossfade",
     "numbers": [("€120 / mese", 2.0, 7.0, "#FF6B6B"), ("€4.320 in 3 anni", 8.0, 13.0, "#FF6B6B"), ("MAI TUO.", 14.0, 18.0, "#FF4444"), ("SPARISCE TUTTO.", 19.0, 24.0, "#FF4444")]},
    {"id": "s43", "type": "ai", "file": "V6-11_salone_sereno.mp4", "trim": (0, 5), "loop": True, "transition": "crossfade",
     "numbers": [("€497 — PER SEMPRE.", 2.0, 8.0, "#4ECDC4"), ("+ Sara: €897", 9.0, 14.0, "#4ECDC4")]},

    # CH10: CTA + endcard
    {"id": "s44", "type": "ai", "file": "V13_finale.mp4", "trim": (0, 8), "loop": True, "transition": "crossfade",
     "numbers": [("30 GIORNI SODDISFATTI", 3.0, 7.0, "#FFFFFF"), ("O RIMBORSATI.", 7.5, 11.0, "#4ECDC4")]},
    {"id": "s45", "type": "ai", "file": "V16_sara_intro.mp4", "trim": (0, 8), "transition": "crossfade",
     "numbers": [("FLUXION.", 2.0, 5.0, "#4ECDC4"), ("Come ho fatto senza?", 5.5, 8.5, "#FFFFFF")]},
    {"id": "s46", "type": "endcard", "transition": "fade_to_black"},
]


def run_ff(args, label=""):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0 and label:
        print(f"  WARN [{label}]: {r.stderr[:300]}")
    return r


def probe_duration(path):
    r = run_ff(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def burn_logo(img_path, output_path):
    img = Image.open(img_path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    if LOGO.exists():
        logo = Image.open(str(LOGO)).convert("RGBA")
        logo = logo.resize((64, 64), Image.LANCZOS)
        alpha = logo.split()[3].point(lambda p: int(p * 0.7))
        logo.putalpha(alpha)
        img_rgba = img.convert("RGBA")
        img_rgba.paste(logo, (24, 24), logo)
        img = img_rgba.convert("RGB")
    img.save(output_path, quality=95)


def create_number_overlay_video(numbers, duration, output_path):
    """Create a transparent-overlay video with animated numbers using Pillow frames."""
    frame_count = int(duration * FPS)
    frames_dir = TMPDIR / "number_frames"
    frames_dir.mkdir(exist_ok=True)

    # Clear old frames
    for f in frames_dir.glob("frame_*.png"):
        f.unlink()

    font_large = get_font(72)
    font_shadow = get_font(74)

    for fi in range(frame_count):
        t = fi / FPS  # current time in seconds
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        for text, start, end, color in numbers:
            if start <= t <= end:
                # Fade in during first 0.3s
                alpha_factor = min(1.0, (t - start) / 0.3)
                # Slight scale effect (not actually scaling text, but fading the band)
                band_alpha = int(170 * alpha_factor)  # ~65% opacity

                # Draw dark band in bottom third
                band_y = H * 2 // 3
                draw.rectangle([(0, band_y), (W, band_y + 120)], fill=(0, 0, 0, band_alpha))

                # Text centered in band
                text_alpha = int(255 * alpha_factor)
                bbox = draw.textbbox((0, 0), text, font=font_large)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                tx = (W - tw) // 2
                ty = band_y + (120 - th) // 2

                # Shadow
                shadow_color = (0, 0, 0, int(200 * alpha_factor))
                draw.text((tx + 3, ty + 3), text, font=font_large, fill=shadow_color)

                # Main text
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                draw.text((tx, ty), text, font=font_large, fill=(r, g, b, text_alpha))

        img.save(frames_dir / f"frame_{fi:05d}.png")

    # Encode frames to video with alpha (using PNG sequence → mov with prores or just overlay later)
    run_ff([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-vf", "format=rgba",
        "-c:v", "png", "-pix_fmt", "rgba",
        str(output_path)
    ], "number overlay encode")

    return output_path


def build_scene_clip(i, scene, manifest):
    """Build a single scene clip. Returns path or None."""
    sid = scene["id"]
    stype = scene.get("type", "screenshot")
    clip_out = TMPDIR / f"v8_clip_{i:02d}_{sid}.mp4"

    m = manifest.get(sid, {})
    audio = m.get("mp3_path")
    audio_dur = m.get("duration_seconds", 0)
    if audio and not Path(audio).exists():
        audio = None
        audio_dur = 0

    # Endcard
    if stype == "endcard":
        if ENDCARD_VIDEO.exists():
            # Use pre-built extended endcard (animation + hold last frame)
            run_ff([
                "ffmpeg", "-y", "-i", str(ENDCARD_VIDEO),
                "-vf", SCALE_FILTER,
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-c:a", "aac", "-b:a", "192k", "-shortest",
                str(clip_out)
            ], f"endcard")
        else:
            return None

    elif stype == "ai":
        file_path = AI_CLIPS / scene["file"]
        if not file_path.exists():
            print(f"  MISSING: {file_path}")
            return None

        trim_s, trim_e = scene.get("trim", (0, 8))
        trim_dur = trim_e - trim_s
        should_loop = scene.get("loop", False)
        numbers = scene.get("numbers", [])

        if audio and audio_dur > 0:
            target_dur = audio_dur + 0.5
        else:
            target_dur = trim_dur

        cmd = ["ffmpeg", "-y"]
        if should_loop or target_dur > trim_dur:
            cmd += ["-stream_loop", "-1"]
        cmd += [
            "-ss", str(trim_s), "-i", str(file_path),
        ]
        if audio:
            cmd += ["-i", str(audio)]
        else:
            cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]

        cmd += [
            "-t", str(target_dur),
            "-vf", SCALE_FILTER,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-map", "0:v:0", "-map", "1:a:0",
        ]
        if not audio:
            cmd.append("-shortest")
        cmd.append(str(clip_out))
        run_ff(cmd, f"ai {sid}")

        # Apply number overlays if present
        if numbers and clip_out.exists():
            overlay_path = TMPDIR / f"v8_overlay_{sid}.mov"
            create_number_overlay_video(numbers, target_dur, overlay_path)
            if overlay_path.exists():
                final_clip = TMPDIR / f"v8_clip_{i:02d}_{sid}_num.mp4"
                run_ff([
                    "ffmpeg", "-y",
                    "-i", str(clip_out),
                    "-i", str(overlay_path),
                    "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[outv]",
                    "-map", "[outv]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "copy",
                    str(final_clip)
                ], f"overlay {sid}")
                if final_clip.exists() and final_clip.stat().st_size > 1000:
                    clip_out.unlink()
                    final_clip.rename(clip_out)

    elif stype == "screenshot":
        file_path = SCREENSHOTS / scene["file"]
        if not file_path.exists():
            print(f"  MISSING: {file_path}")
            return None

        prepared = TMPDIR / f"v8_prepared_{sid}.png"
        burn_logo(str(file_path), str(prepared))

        if audio and audio_dur > 0:
            target_dur = audio_dur + 0.5
        else:
            target_dur = scene.get("duration", 5)

        if audio:
            run_ff([
                "ffmpeg", "-y",
                "-loop", "1", "-t", str(target_dur), "-i", str(prepared),
                "-i", str(audio),
                "-vf", "format=yuv420p",
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest",
                str(clip_out)
            ], f"ss+voice {sid}")
        else:
            dur = scene.get("duration", 5)
            run_ff([
                "ffmpeg", "-y",
                "-loop", "1", "-t", str(dur), "-i", str(prepared),
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-vf", "format=yuv420p",
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-c:a", "aac", "-b:a", "192k", "-shortest",
                str(clip_out)
            ], f"ss silent {sid}")

    if clip_out.exists() and clip_out.stat().st_size > 1000:
        dur = probe_duration(clip_out)
        return str(clip_out), dur
    return None


def main():
    with open(MANIFEST) as f:
        manifest = json.load(f)

    print("=" * 60)
    print("  FLUXION V8 — Final Video Compositing")
    print(f"  Scenes: {len(SCENES)}")
    print("=" * 60)

    # Phase 1: Manifest loaded
    print("\n[1/5] Voiceover manifest loaded.\n")
    vo_count = sum(1 for v in manifest.values() if v.get("mp3_path"))
    print(f"  {vo_count} voiceovers, {len(SCENES) - vo_count} silent scenes")

    # Phase 2: Build clips
    print(f"\n[2/5] Building {len(SCENES)} individual clips...\n")
    clip_paths = []
    for i, scene in enumerate(SCENES):
        result = build_scene_clip(i, scene, manifest)
        if result:
            path, dur = result
            print(f"  [{i+1:2d}/{len(SCENES)}] {scene['id']}: {dur:.1f}s")
            clip_paths.append(path)
        else:
            print(f"  [{i+1:2d}/{len(SCENES)}] {scene['id']}: FAILED/SKIP")

    if not clip_paths:
        print("ERROR: No clips built!")
        sys.exit(1)

    # Phase 3: Normalize and concatenate
    print(f"\n[3/5] Normalizing and concatenating {len(clip_paths)} clips...\n")
    norm_paths = []
    for ci, cp in enumerate(clip_paths):
        norm_path = TMPDIR / f"v8_norm_{ci:02d}.ts"
        run_ff([
            "ffmpeg", "-y", "-i", cp,
            "-vf", f"scale={W}:{H},format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-af", "aresample=48000",
            "-bsf:v", "h264_mp4toannexb",
            str(norm_path)
        ], f"norm {ci}")
        if norm_path.exists() and norm_path.stat().st_size > 1000:
            norm_paths.append(str(norm_path))

    concat_file = TMPDIR / "v8_concat.txt"
    with open(concat_file, "w") as f:
        for np in norm_paths:
            f.write(f"file '{np}'\n")

    concat_out = TMPDIR / "v8_concatenated.mp4"
    run_ff([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file), "-c", "copy",
        str(concat_out)
    ], "concat")

    total_dur = probe_duration(concat_out)
    print(f"  Total duration: {total_dur:.0f}s ({total_dur/60:.1f} min)")

    # Phase 4: Mix background music
    print(f"\n[4/5] Mixing background music...\n")
    music_out = TMPDIR / "v8_with_music.mp4"
    fade_out_music = max(0, total_dur - 3)
    run_ff([
        "ffmpeg", "-y",
        "-i", str(concat_out),
        "-stream_loop", "-1", "-i", str(MUSIC),
        "-t", str(total_dur),
        "-filter_complex",
        f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.0[voice];"
        f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.12,"
        f"afade=t=in:d=2,afade=t=out:st={fade_out_music}:d=3[music];"
        f"[voice][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(music_out)
    ], "music mix")
    print("  Music mixed.")

    # Phase 5: Final encode
    print(f"\n[5/5] Final encode (H.264 High, CRF 18)...\n")
    fade_out_start = max(0, total_dur - 2.5)
    run_ff([
        "ffmpeg", "-y", "-i", str(music_out),
        "-vf", f"fade=t=in:st=0:d=1.5,fade=t=out:st={fade_out_start}:d=2",
        "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={fade_out_start}:d=2",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-profile:v", "high", "-level", "4.1",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(OUTPUT)
    ], "final encode")

    if not OUTPUT.exists() or OUTPUT.stat().st_size < 1000:
        if music_out.exists() and music_out.stat().st_size > 1000:
            shutil.copy2(str(music_out), str(OUTPUT))
        elif concat_out.exists():
            shutil.copy2(str(concat_out), str(OUTPUT))

    final_dur = probe_duration(OUTPUT)
    size_mb = OUTPUT.stat().st_size / 1024 / 1024 if OUTPUT.exists() else 0

    print("\n" + "=" * 60)
    print(f"  FLUXION V8 — VIDEO COMPLETATO")
    print(f"  Output:   {OUTPUT}")
    print(f"  Durata:   {final_dur:.0f}s ({final_dur/60:.1f} min)")
    print(f"  Size:     {size_mb:.1f} MB")
    print(f"  Scenes:   {len(clip_paths)}")
    print("=" * 60)
    print(f"\n  open '{OUTPUT}'")


if __name__ == "__main__":
    main()
