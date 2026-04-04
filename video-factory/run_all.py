"""
run_all.py — FLUXION Video Factory
Orchestratore principale: genera video per una o tutte le verticali.

Uso:
  python run_all.py --vertical all
  python run_all.py --vertical parrucchiere
  python run_all.py --vertical officina dentista palestra
  python run_all.py --vertical all --skip-veo3 --use-existing ./output
  python run_all.py --vertical all --export-prompts-only
"""

from __future__ import annotations
import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Aggiunge video_factory al path
sys.path.insert(0, str(Path(__file__).parent))

from video_factory.script_generator import (
    VERTICALI,
    build_veo3_requests,
    build_narration_script,
    build_wa_message,
    export_all_prompts,
)
from video_factory.veo3_client import generate_clips_batch
from video_factory.assembly import assemble_video, generate_voiceover, AssemblyJob

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_BASE = Path("./output")


# ─── Pipeline per singola verticale ──────────────────────────────────────────

async def run_verticale(
    verticale: str,
    skip_veo3: bool = False,
    existing_clips_dir: Path | None = None,
) -> dict:
    """Esegui pipeline completa per una verticale. Ritorna metadata risultato."""

    output_dir = OUTPUT_BASE / verticale
    output_dir.mkdir(parents=True, exist_ok=True)
    clips_dir = output_dir / "clips"
    clips_dir.mkdir(exist_ok=True)

    logger.info(f"═══ Avvio verticale: {verticale} ═══")

    # ─ 1. Build Veo 3 requests ───────────────────────────────────────────────
    veo3_requests = build_veo3_requests(verticale)

    # ─ 2. Genera clip con Veo 3 ──────────────────────────────────────────────
    if skip_veo3 and existing_clips_dir:
        logger.info(f"Skip Veo 3 — uso clip esistenti da {existing_clips_dir}")
        clip_paths = sorted((existing_clips_dir / verticale).glob("*_clip*.mp4"))
        if not clip_paths:
            raise FileNotFoundError(
                f"Nessuna clip trovata in {existing_clips_dir}/{verticale}"
            )
    else:
        logger.info(f"Generazione {len(veo3_requests)} clip con Veo 3...")
        results = generate_clips_batch(
            requests_list=veo3_requests,
            output_dir=clips_dir,
            verticale=verticale,
        )
        # Prendi best variant (primo file, indice _v1)
        clip_paths = []
        for result in results:
            if result.local_paths:
                clip_paths.append(result.local_paths[0])

    logger.info(f"Clip pronte: {[p.name for p in clip_paths]}")

    # ─ 3. Genera voiceover ───────────────────────────────────────────────────
    narration = build_narration_script(verticale)
    audio_path = output_dir / f"{verticale}_voiceover.mp3"

    logger.info("Generazione voiceover Edge-TTS...")
    await generate_voiceover(
        segments=narration["segments"],
        output_path=audio_path,
        voice="it-IT-IsabellaNeural",
    )

    # ─ 4. Assembly ───────────────────────────────────────────────────────────
    data = VERTICALI[verticale]

    overlay_texts = [
        {"clip": 2, "text": data["pain_stat"], "position": "center", "color": "white"},
        {"clip": 3, "text": data["feature_hero"], "position": "bottom", "color": "white"},
    ]

    job = AssemblyJob(
        verticale=verticale,
        clip_paths=clip_paths,
        audio_path=audio_path if audio_path.exists() else None,
        output_dir=output_dir,
        overlay_texts=overlay_texts,
    )

    logger.info("Assemblaggio video finale...")
    result = assemble_video(job)

    # ─ 5. Aggiungi musica di sottofondo ─────────────────────────────────────
    try:
        from video_factory.music_layer import get_or_build_music, apply_music_to_video
        import ffmpeg as _ffmpeg
        _probe = _ffmpeg.probe(str(result.vertical_path))
        _dur = float(_probe["format"]["duration"])
        music_path = get_or_build_music(verticale, _dur, output_dir)
        if music_path and music_path.exists():
            final_with_music = output_dir / f"{verticale}_video_9x16.mp4"
            apply_music_to_video(
                video_path=result.vertical_path,
                output_path=final_with_music,
                music_path=music_path,
                voiceover_path=audio_path if audio_path.exists() else None,
                music_volume=0.15,
            )
            logger.info(f"Musica aggiunta: {final_with_music.name}")
    except Exception as e:
        logger.warning(f"Music layer skip: {e}")

    # ─ 6. QA automatico ─────────────────────────────────────────────────────
    try:
        from video_factory.qa_check import qa_video
        _final_path = output_dir / f"{verticale}_video_9x16.mp4"
        if _final_path.exists():
            qa_report = qa_video(_final_path, auto_fix_enabled=True)
            logger.info(qa_report.summary())
            if qa_report.overall == "FAIL":
                logger.warning(f"⚠️  QA FAIL per {verticale} — verifica manualmente")
    except Exception as e:
        logger.warning(f"QA skip: {e}")

    # ─ 7. Genera messaggio WA ─────────────────────────────────────────────────
    wa_msg = build_wa_message(verticale)
    wa_path = output_dir / "wa_message.txt"
    wa_path.write_text(wa_msg, encoding="utf-8")

    # Genera anche i follow-up messages
    from video_factory.wa_distributor import _generate_followup_messages
    _generate_followup_messages(output_dir, verticale, video_url="[VIDEO_LINK]")

    # ─ 8. Genera metadata YT/Vimeo ───────────────────────────────────────────
    metadata = {
        "verticale": verticale,
        "label": data["label"],
        "yt_title": f"Come le {data['label']}i Italiane Smettono di Perdere Clienti — FLUXION",
        "yt_description": (
            f"FLUXION è il gestionale per {data['label'].lower()} che non ti costa ogni mese.\n\n"
            f"✅ {data['feature_hero']}\n"
            f"✅ WhatsApp automatico\n"
            f"✅ Dati sul tuo computer (zero cloud)\n"
            f"✅ €497 una volta — zero abbonamenti\n\n"
            f"vs Treatwell €4.320 in 3 anni, vs XDENT €7.200 in 3 anni.\n\n"
            f"👉 fluxion-landing.pages.dev"
        ),
        "yt_tags": [
            f"gestionale {verticale}",
            "FLUXION",
            "software gestionale PMI",
            "Sara assistente vocale",
            "appuntamenti automatici",
            f"software {data['label'].lower()}",
            "gestione clienti",
            "WhatsApp automatico",
        ],
        "vimeo_title": f"FLUXION — {data['label']} Demo 30s",
        "duration_seconds": result.duration_seconds,
        "files": {
            "video_9x16": str(result.vertical_path),
            "video_16x9": str(result.horizontal_path),
            "thumbnail": str(result.thumbnail_path),
            "voiceover": str(audio_path),
            "wa_message": str(wa_path),
        },
    }

    meta_path = output_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

    logger.info(f"✓ {verticale} completato!")
    logger.info(f"  9:16 → {result.vertical_path}")
    logger.info(f"  16:9 → {result.horizontal_path}")
    logger.info(f"  WA   → {wa_path}")

    return metadata


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="FLUXION Video Factory — Genera video per verticale"
    )
    parser.add_argument(
        "--vertical", nargs="+", default=["all"],
        help="Verticale/i da processare (es: parrucchiere officina) oppure 'all'"
    )
    parser.add_argument(
        "--skip-veo3", action="store_true",
        help="Salta la generazione Veo 3 (usa clip esistenti)"
    )
    parser.add_argument(
        "--use-existing", type=Path, default=None,
        help="Dir con clip esistenti (se --skip-veo3)"
    )
    parser.add_argument(
        "--export-prompts-only", action="store_true",
        help="Esporta solo i prompt JSON senza generare"
    )
    parser.add_argument(
        "--output", type=Path, default=OUTPUT_BASE,
        help="Directory output base (default: ./output)"
    )

    args = parser.parse_args()
    global OUTPUT_BASE
    OUTPUT_BASE = args.output

    # Solo export prompt
    if args.export_prompts_only:
        export_all_prompts(OUTPUT_BASE / "prompts")
        print("\nPrompt esportati in:", OUTPUT_BASE / "prompts")
        return

    # Seleziona verticali
    if "all" in args.vertical:
        targets = list(VERTICALI.keys())
    else:
        targets = []
        for v in args.vertical:
            if v in VERTICALI:
                targets.append(v)
            else:
                logger.warning(f"Verticale '{v}' non trovata, skip")

    if not targets:
        print("Nessuna verticale valida. Disponibili:", list(VERTICALI.keys()))
        return

    print(f"\n{'═'*50}")
    print(f"FLUXION Video Factory")
    print(f"Verticali: {targets}")
    print(f"Output: {OUTPUT_BASE}")
    print(f"{'═'*50}\n")

    results = []
    errors = []

    for verticale in targets:
        try:
            meta = await run_verticale(
                verticale=verticale,
                skip_veo3=args.skip_veo3,
                existing_clips_dir=args.use_existing,
            )
            results.append(meta)
        except Exception as e:
            logger.error(f"ERRORE {verticale}: {e}")
            errors.append({"verticale": verticale, "error": str(e)})

    # Report finale
    print(f"\n{'═'*50}")
    print(f"COMPLETATO: {len(results)}/{len(targets)} verticali")
    for r in results:
        print(f"  ✓ {r['verticale']} ({r['duration_seconds']:.1f}s)")
    if errors:
        print(f"\nERRORI: {len(errors)}")
        for e in errors:
            print(f"  ✗ {e['verticale']}: {e['error']}")
    print(f"{'═'*50}\n")

    # Salva summary
    summary = {
        "completed": results,
        "errors": errors,
        "total": len(targets),
    }
    (OUTPUT_BASE / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    print(f"Summary: {OUTPUT_BASE}/summary.json")


if __name__ == "__main__":
    # Verifica env vars necessarie
    if not os.environ.get("GCP_PROJECT_ID"):
        print("⚠️  Imposta GCP_PROJECT_ID:")
        print('   export GCP_PROJECT_ID="your-project-id"')
        print('   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa.json"')
        print()

    asyncio.run(main())
