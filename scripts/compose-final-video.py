#!/usr/bin/env python3
"""
FLUXION V5 — Final Video Compositing
Assembles: AI clips + screenshots + Edge-TTS voiceover + background music + logo overlay
Output: landing/assets/fluxion-promo-v5.mp4
"""

import asyncio
import json
import os
import subprocess
import sys
import shutil
from pathlib import Path

BASE = Path("/Volumes/MontereyT7/FLUXION")
AI_CLIPS = BASE / "landing" / "assets" / "ai-clips-v2"
SCREENSHOTS = BASE / "landing" / "screenshots"
LOGO = BASE / "landing" / "assets" / "logo_fluxion.jpg"
MUSIC = BASE / "landing" / "assets" / "background-music.mp3"
OUTPUT = BASE / "landing" / "assets" / "fluxion-promo-v5.mp4"
TMPDIR = BASE / "tmp-video-build"
TMPDIR.mkdir(exist_ok=True)

VOICE_SARA = "it-IT-IsabellaNeural"
VOICE_CLIENT = "it-IT-DiegoNeural"
RATE_SARA = "-5%"

# ============================================================
# FULL STORYBOARD — Scene sequence with voiceover
# ============================================================
SCENES = [
    # CH1: LA TUA GIORNATA — AI clips montage (no voiceover on clips, voiceover starts on V10)
    {"id": "V01", "type": "ai", "file": "V01_salone.mp4", "voiceover": None},
    {"id": "V02", "type": "ai", "file": "V02_officina.mp4", "voiceover": None},
    {"id": "V03", "type": "ai", "file": "V03_dentista.mp4", "voiceover": None},
    {"id": "V04", "type": "ai", "file": "V04_palestra.mp4", "voiceover": None},
    {"id": "V05", "type": "ai", "file": "V05_estetista.mp4", "voiceover": None},
    {"id": "V06", "type": "ai", "file": "V06_nails.mp4", "voiceover": None},
    {"id": "V07", "type": "ai", "file": "V07_fisioterapista.mp4", "voiceover": None},
    {"id": "V08", "type": "ai", "file": "V08_gommista.mp4", "voiceover": None},
    {"id": "V09", "type": "ai", "file": "V09_elettrauto.mp4", "voiceover": None},

    # CH2: IL PROBLEMA — frustrazione + voiceover
    {"id": "V10", "type": "ai", "file": "V10_frustrazione.mp4",
     "voiceover": "Tu lo sai com'e'. Sei li' che lavori. Le mani occupate. E il telefono squilla. Squilla ancora. E ancora. Non puoi rispondere. Quel cliente che voleva prenotare? Ha gia' chiamato qualcun altro. Un cliente perso al giorno sono duecentocinquanta clienti all'anno. A trenta euro di media, sono settemilacinquecento euro che non torneranno. E una segretaria? Novecento euro al mese. Ogni mese."},

    # CH3: TI PRESENTO SARA
    {"id": "SS01", "type": "screenshot", "file": "08-voice.png",
     "voiceover": "E se ti dicessi che c'e' qualcuno che risponde per te? Sempre. Anche di notte. Anche di domenica. Anche quando sei in ferie. Mi chiamo Sara. Sono la tua assistente. Parlo italiano, capisco cosa vogliono i tuoi clienti, e prenoto per loro. Senza che tu alzi un dito."},

    # Telefonata simulata Sara + Cliente
    {"id": "SS02", "type": "screenshot", "file": "08-voice.png",
     "voiceover_dialogue": [
         {"voice": "client", "text": "Buongiorno, vorrei prenotare un taglio per domani mattina."},
         {"voice": "sara", "text": "Buongiorno Marco! Certo. Vedo che l'ultima volta ha fatto taglio e barba con Roberto. Vuole ripetere?"},
         {"voice": "client", "text": "Si', perfetto!"},
         {"voice": "sara", "text": "Roberto e' disponibile domani alle dieci e trenta. Le va bene?"},
         {"voice": "client", "text": "Perfetto, grazie!"},
         {"voice": "sara", "text": "Prenotato! Le mando conferma su WhatsApp. Buona giornata Marco!"},
     ]},

    {"id": "SS03", "type": "screenshot", "file": "08-voice.png",
     "voiceover": "Sara conosce i tuoi clienti. Sa come si chiamano, cosa hanno fatto l'ultima volta, se hanno allergie, quali farmaci prendono. Non e' un risponditore automatico. E' la collega che hai sempre voluto."},

    # CH4: DASHBOARD
    {"id": "SS04", "type": "screenshot", "file": "01-dashboard.png",
     "voiceover": "Appena apri FLUXION, vedi tutto. Gli appuntamenti di oggi. Quanti clienti hai questo mese. Quanto hai incassato. Qual e' il servizio che va di piu'. Non devi cercare niente, non devi essere un esperto di computer. E' tutto li', chiaro, in italiano."},

    {"id": "SS05", "type": "screenshot", "file": "02-calendario.png",
     "voiceover": "Il calendario. Crei un appuntamento in due click. Scegli il cliente, il servizio, chi lo fa, e l'orario. Fatto. E se il cliente non si presenta? Il promemoria WhatsApp parte in automatico ventiquattro ore prima."},

    # CH5: SCHEDE
    {"id": "SS06", "type": "screenshot", "file": "03-clienti.png",
     "voiceover": "Ogni tuo cliente ha una scheda completa. Nome, contatti, storico visite, preferenze. Ma non solo."},

    {"id": "SS07", "type": "screenshot", "file": "13-scheda-parrucchiere.png",
     "voiceover": "Sei parrucchiere? Sai che tipo di capello ha, il colore preferito, se e' allergico a qualche prodotto. La prossima volta non chiedi, sai gia'."},

    {"id": "SS08", "type": "screenshot", "file": "14-scheda-veicoli.png",
     "voiceover": "Hai un'officina? Targa, marca, modello, chilometri, tagliandi, scadenza assicurazione. Sara quando prende l'appuntamento chiede il modello dell'auto e salva tutto."},

    {"id": "SS09", "type": "screenshot", "file": "15-scheda-odontoiatrica.png",
     "voiceover": "Sei dentista? Anamnesi completa: allergie, farmaci, piano terapeutico. Sara sa che il paziente prende anticoagulanti prima ancora che si sieda in poltrona."},

    {"id": "SS10", "type": "screenshot", "file": "16-scheda-estetica.png",
     "voiceover": "Centro estetico? Tipo di pelle, trattamenti fatti, reazioni. La prossima seduta sai gia' come procedere."},

    {"id": "SS11", "type": "screenshot", "file": "17-scheda-fitness.png",
     "voiceover": "Palestra? Obiettivi, misurazioni, progressi. Sai se il cliente sta migliorando o se sta per mollare."},

    # CH6: GESTIONE
    {"id": "SS12", "type": "screenshot", "file": "04-servizi.png",
     "voiceover": "I tuoi servizi, organizzati. Prezzi, durate, categorie. Li crei in un minuto. Non serve un informatico."},

    {"id": "SS13", "type": "screenshot", "file": "05-operatori.png",
     "voiceover": "I tuoi collaboratori. Ognuno col suo profilo, i turni, le ferie. Sai chi lavora oggi e chi ha generato piu' fatturato."},

    {"id": "SS14", "type": "screenshot", "file": "09-fornitori.png",
     "voiceover": "I fornitori. Contatti, ordini, listini. Tutto in un posto. Basta foglietti attaccati al frigorifero."},

    {"id": "SS15", "type": "screenshot", "file": "06-fatture.png",
     "voiceover": "Le fatture. Le crei con due click, le invii direttamente allo SDI. Il commercialista riceve tutto in automatico. Risparmi tempo e soldi."},

    {"id": "SS16", "type": "screenshot", "file": "07-cassa.png",
     "voiceover": "La cassa. Quanto hai incassato oggi. Contanti, carte, Satispay. Ogni euro tracciato."},

    {"id": "SS17", "type": "screenshot", "file": "10-analytics.png",
     "voiceover": "I numeri che contano. Fatturato, servizi, operatori. Non servono fogli Excel. FLUXION te lo dice chiaro."},

    # CH7: COMUNICAZIONE
    {"id": "V11", "type": "ai", "file": "V11_qrcode.mp4",
     "voiceover": "Il QR code sul bancone. Il cliente lo scansiona e resta in contatto con te. Promemoria, promozioni, auguri di compleanno. Tutto automatico. Tu non devi fare niente."},

    # CH8: PREZZO
    {"id": "V12", "type": "ai", "file": "V12_soddisfatta.mp4",
     "voiceover": "Un gestionale in abbonamento costa seicento euro all'anno. In tre anni milleottocento. E non sara' mai tuo. FLUXION costa quattrocentonovantasette euro. Una volta sola. Per sempre. Calendario, clienti, cassa, fatture, fornitori, tutto. Vuoi anche Sara? Ottocentonovantasette euro. Una volta. Per sempre. Si ripaga in tre settimane."},

    # CH9: CTA
    {"id": "V13", "type": "ai", "file": "V13_finale.mp4",
     "voiceover": "Parrucchieri, barbieri, officine, gommisti, elettrauto, dentisti, fisioterapisti, centri estetici, palestre, nail artist. Non importa qual e' la tua attivita'. FLUXION e' il partner che ti mancava. Trenta giorni soddisfatti o rimborsati. FLUXION. Paghi una volta. Usi per sempre. E ti chiederai... come ho fatto senza?"},
]


async def generate_tts(text, output_path, voice=VOICE_SARA, rate=RATE_SARA):
    """Generate TTS audio, return duration."""
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(output_path)
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", output_path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def burn_logo(img_path, output_path):
    """Burn FLUXION logo on image via Pillow."""
    from PIL import Image
    img = Image.open(img_path).convert("RGB")
    if img.size != (1280, 720):
        img = img.resize((1280, 720), Image.LANCZOS)

    if LOGO.exists():
        logo = Image.open(str(LOGO)).convert("RGBA")
        logo = logo.resize((64, 64), Image.LANCZOS)
        alpha = logo.split()[3].point(lambda p: int(p * 0.7))
        logo.putalpha(alpha)
        img_rgba = img.convert("RGBA")
        img_rgba.paste(logo, (24, 24), logo)
        img = img_rgba.convert("RGB")

    img.save(output_path, quality=95)


async def main():
    print("=" * 60)
    print("  FLUXION V5 — Final Video Compositing")
    print(f"  Scenes: {len(SCENES)}")
    print("=" * 60)

    # Phase 1: Generate all voiceovers
    print("\n[1/5] Generating voiceovers (Edge-TTS)...\n")
    clip_data = []

    for i, scene in enumerate(SCENES):
        scene_id = scene["id"]
        audio_path = TMPDIR / f"voice_{scene_id}.mp3"

        if "voiceover_dialogue" in scene:
            # Multi-voice dialogue
            parts = []
            for j, line in enumerate(scene["voiceover_dialogue"]):
                part_path = TMPDIR / f"voice_{scene_id}_part{j}.mp3"
                voice = VOICE_CLIENT if line["voice"] == "client" else VOICE_SARA
                rate = "+0%" if line["voice"] == "client" else RATE_SARA
                dur = await generate_tts(line["text"], str(part_path), voice=voice, rate=rate)
                parts.append(str(part_path))
                print(f"  {scene_id} part{j} ({line['voice']}): {dur:.1f}s")

            # Concat dialogue parts with 0.3s gaps
            concat_file = TMPDIR / f"concat_{scene_id}.txt"
            silence = TMPDIR / "silence_300ms.mp3"
            if not silence.exists():
                subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                               "anullsrc=r=24000:cl=mono", "-t", "0.3",
                               "-c:a", "libmp3lame", str(silence)],
                              capture_output=True)
            with open(concat_file, "w") as f:
                for pi, p in enumerate(parts):
                    f.write(f"file '{p}'\n")
                    if pi < len(parts) - 1:
                        f.write(f"file '{silence}'\n")

            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                           "-i", str(concat_file), "-c", "copy", str(audio_path)],
                          capture_output=True)
        elif scene.get("voiceover"):
            dur = await generate_tts(scene["voiceover"], str(audio_path))
            print(f"  {scene_id}: {dur:.1f}s")
        else:
            audio_path = None
            print(f"  {scene_id}: no voiceover")

        clip_data.append({"scene": scene, "audio": str(audio_path) if audio_path else None})

    # Phase 2: Build individual clips
    print("\n[2/5] Building individual clips...\n")
    clip_paths = []

    for i, cd in enumerate(clip_data):
        scene = cd["scene"]
        scene_id = scene["id"]
        audio = cd["audio"]
        clip_out = TMPDIR / f"clip_{i:02d}_{scene_id}.mp4"

        if scene["type"] == "ai":
            video_src = AI_CLIPS / scene["file"]
            if not video_src.exists():
                print(f"  MISSING: {video_src}")
                continue

            if audio:
                # Get audio duration + 0.5s padding
                r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                                   "format=duration", "-of", "csv=p=0", audio],
                                  capture_output=True, text=True)
                audio_dur = float(r.stdout.strip()) + 0.5
                # AI clip is 8s, if voiceover longer, loop the video
                duration = max(8.0, audio_dur)

                # Scale to 1280x720, overlay logo, add voiceover
                subprocess.run([
                    "ffmpeg", "-y",
                    "-stream_loop", "-1", "-i", str(video_src),
                    "-i", audio,
                    "-t", str(duration),
                    "-vf", f"scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(clip_out)
                ], capture_output=True)
            else:
                # AI clip without voiceover — trim to 3s for montage
                # Add silent audio track so concat works with audio clips
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(video_src),
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", "3",
                    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k", "-shortest",
                    str(clip_out)
                ], capture_output=True)

        elif scene["type"] == "screenshot":
            img_src = SCREENSHOTS / scene["file"]
            if not img_src.exists():
                print(f"  MISSING: {img_src}")
                continue

            # Burn logo on screenshot
            prepared = TMPDIR / f"prepared_{scene_id}.png"
            burn_logo(str(img_src), str(prepared))

            if audio:
                r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                                   "format=duration", "-of", "csv=p=0", audio],
                                  capture_output=True, text=True)
                duration = float(r.stdout.strip()) + 0.5

                subprocess.run([
                    "ffmpeg", "-y",
                    "-loop", "1", "-t", str(duration), "-i", str(prepared),
                    "-i", audio,
                    "-vf", "format=yuv420p",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(clip_out)
                ], capture_output=True)

        if clip_out.exists():
            r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                               "format=duration", "-of", "csv=p=0", str(clip_out)],
                              capture_output=True, text=True)
            dur = float(r.stdout.strip()) if r.stdout.strip() else 0
            print(f"  [{i+1:2d}] {scene_id}: {dur:.1f}s")
            clip_paths.append(str(clip_out))

    # Phase 3: Concatenate all clips
    print(f"\n[3/5] Concatenating {len(clip_paths)} clips...\n")
    concat_file = TMPDIR / "final_concat.txt"
    with open(concat_file, "w") as f:
        for cp in clip_paths:
            f.write(f"file '{cp}'\n")

    # First normalize all clips to same format (1280x720, h264, aac, 48000Hz stereo)
    print("  Normalizing all clips...")
    norm_paths = []
    for ci, cp in enumerate(clip_paths):
        norm_path = TMPDIR / f"norm_{ci:02d}.ts"
        subprocess.run([
            "ffmpeg", "-y", "-i", cp,
            "-vf", "scale=1280:720,format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-bsf:v", "h264_mp4toannexb",
            str(norm_path)
        ], capture_output=True)
        if norm_path.exists() and norm_path.stat().st_size > 1000:
            norm_paths.append(str(norm_path))

    concat_file = TMPDIR / "final_concat.txt"
    with open(concat_file, "w") as f:
        for np in norm_paths:
            f.write(f"file '{np}'\n")

    concat_out = TMPDIR / "concatenated.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(concat_out)
    ], capture_output=True)

    # Get duration
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                       "format=duration", "-of", "csv=p=0", str(concat_out)],
                      capture_output=True, text=True)
    total_dur = float(r.stdout.strip())
    print(f"  Total duration: {total_dur:.0f}s ({total_dur/60:.1f} min)")

    # Phase 4: Mix in background music
    print(f"\n[4/5] Mixing background music (-20dB under voice)...\n")
    music_out = TMPDIR / "with_music.mp4"

    # Loop music to match video length, lower volume to -20dB below voice
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(concat_out),
        "-stream_loop", "-1", "-i", str(MUSIC),
        "-t", str(total_dur),
        "-filter_complex",
        "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.0[voice];"
        "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.08,afade=t=in:d=2,afade=t=out:st=" + str(total_dur - 3) + ":d=3[music];"
        "[voice][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(music_out)
    ], capture_output=True)
    print("  Music mixed.")

    # Phase 5: Final encode with fade in/out
    print(f"\n[5/5] Final encode (H.264 High, fade in/out)...\n")
    fade_out_start = max(0, total_dur - 2.5)

    subprocess.run([
        "ffmpeg", "-y", "-i", str(music_out),
        "-vf", f"fade=t=in:st=0:d=1.5,fade=t=out:st={fade_out_start}:d=2",
        "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={fade_out_start}:d=2",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-profile:v", "high", "-level", "4.1",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(OUTPUT)
    ], capture_output=True)

    # Final info
    if not OUTPUT.exists() or OUTPUT.stat().st_size < 1000:
        # Fallback: copy with_music as final if encode failed
        if music_out.exists() and music_out.stat().st_size > 1000:
            shutil.copy2(str(music_out), str(OUTPUT))
        elif concat_out.exists():
            shutil.copy2(str(concat_out), str(OUTPUT))

    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                       "format=duration,size", "-of", "json", str(OUTPUT)],
                      capture_output=True, text=True)
    try:
        info = json.loads(r.stdout)
        dur = float(info["format"]["duration"])
        size_mb = int(info["format"]["size"]) / 1024 / 1024
    except (json.JSONDecodeError, KeyError):
        dur = total_dur
        size_mb = OUTPUT.stat().st_size / 1024 / 1024 if OUTPUT.exists() else 0

    print("\n" + "=" * 60)
    print(f"  FLUXION V5 — CAPOLAVORO COMPLETATO")
    print(f"  Video:    {OUTPUT}")
    print(f"  Durata:   {dur:.0f}s ({dur/60:.1f} min)")
    print(f"  Size:     {size_mb:.1f} MB")
    print("=" * 60)
    print(f"\n  open '{OUTPUT}'")


if __name__ == "__main__":
    asyncio.run(main())
