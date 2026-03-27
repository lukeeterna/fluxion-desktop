#!/usr/bin/env python3
"""
FLUXION V7 — Generate all voiceovers from storyboard.
Reads VIDEO_STORYBOARD_V7 scenes, generates Edge-TTS MP3s + manifest JSON.
"""

import asyncio
import json
import subprocess
from pathlib import Path

BASE = Path("/Volumes/MontereyT7/FLUXION")
TMPDIR = BASE / "tmp-video-build"
TMPDIR.mkdir(exist_ok=True)

VOICE_SARA = "it-IT-IsabellaNeural"
VOICE_CLIENT = "it-IT-DiegoNeural"
RATE_SARA = "-5%"
RATE_CLIENT = "+0%"

# V7 Scenes — from approved storyboard
SCENES = [
    # CH1: La Tua Giornata (0:00-0:08) — no voiceover
    {"id": "v7_scene_01", "vo": None},
    {"id": "v7_scene_02", "vo": None},
    {"id": "v7_scene_03", "vo": None},
    {"id": "v7_scene_04", "vo": None},

    # CH2: Il Problema (0:08-0:45)
    {"id": "v7_scene_05", "vo": "Tu lo sai com'e'. Sei li' che lavori. Le mani occupate. E il telefono squilla. Squilla ancora.", "voice": "sara"},
    {"id": "v7_scene_06", "vo": "Un cliente perso al giorno sono duecentocinquanta clienti all'anno. A trenta euro di media: settemilacinquecento euro.", "voice": "sara"},
    {"id": "v7_scene_07", "vo": "E una segretaria? Novecento euro al mese. Ogni mese.", "voice": "sara"},

    # CH3: Ti Presento Sara (0:45-1:55)
    {"id": "v7_scene_08", "vo": "E se ti dicessi che c'e' qualcuno che risponde per te? Sempre. Anche di notte. Anche di domenica.", "voice": "sara"},
    {"id": "v7_scene_09", "vo": "Mi chiamo Sara. Sono la tua assistente vocale. Parlo italiano, capisco cosa vogliono i tuoi clienti, e prenoto per loro.", "voice": "sara"},
    # Dialogue scenes
    {"id": "v7_scene_10", "vo": "Buongiorno, vorrei prenotare un taglio per domani mattina.", "voice": "client"},
    {"id": "v7_scene_11", "vo": "Buongiorno Marco! L'ultima volta taglio e barba con Roberto. Vuole ripetere?", "voice": "sara"},
    {"id": "v7_scene_12", "vo": "Si', perfetto!", "voice": "client"},
    {"id": "v7_scene_13", "vo": "Roberto e' disponibile domani alle dieci e trenta. Prenotato! Le mando conferma su WhatsApp.", "voice": "sara"},
    {"id": "v7_scene_14", "vo": "Non e' un risponditore automatico. Sara conosce i tuoi clienti. Il nome, l'ultimo servizio, le preferenze.", "voice": "sara"},

    # CH4: Tutto in un Colpo d'Occhio (1:55-2:25)
    {"id": "v7_scene_15", "vo": "Appena apri FLUXION, vedi tutto. Appuntamenti di oggi, clienti del mese, fatturato, il servizio piu' richiesto. Chiaro, in italiano.", "voice": "sara"},
    {"id": "v7_scene_16", "vo": None},  # visual break
    {"id": "v7_scene_17", "vo": "Il calendario. Un nuovo appuntamento in due click. Il promemoria WhatsApp parte da solo ventiquattro ore prima.", "voice": "sara"},

    # CH5: La Scheda Per la Tua Attivita' (2:25-3:30)
    {"id": "v7_scene_18", "vo": "Sei parrucchiere?", "voice": "sara"},
    {"id": "v7_scene_19", "vo": "Tipo di capello, colore preferito, allergie ai prodotti. La prossima volta non chiedi. Sai gia'.", "voice": "sara"},
    {"id": "v7_scene_20", "vo": "Hai un'officina?", "voice": "sara"},
    {"id": "v7_scene_21", "vo": "Targa, marca, modello, tagliandi, scadenza revisione e assicurazione. Sara salva tutto.", "voice": "sara"},
    {"id": "v7_scene_22", "vo": "Uno studio medico?", "voice": "sara"},
    {"id": "v7_scene_23", "vo": "Anamnesi completa. Allergie, farmaci in corso, piano terapeutico. Dal medico di base allo specialista. Tutto in una scheda.", "voice": "sara"},
    {"id": "v7_scene_24", "vo": "Dentista?", "voice": "sara"},
    {"id": "v7_scene_25", "vo": "Odontogramma digitale, storia clinica, abitudini igieniche. Sara sa che il paziente e' allergico al lattice prima ancora che si sieda.", "voice": "sara"},
    {"id": "v7_scene_26", "vo": "Fisioterapista?", "voice": "sara"},
    {"id": "v7_scene_27", "vo": "Diagnosi, sedute completate, scala del dolore, progressi nel tempo. Sai esattamente a che punto e' il percorso riabilitativo.", "voice": "sara"},
    {"id": "v7_scene_28", "vo": "Estetica, palestra, carrozzeria... qualunque sia la tua attivita', FLUXION ha la scheda giusta.", "voice": "sara"},

    # CH6: Cattura i Momenti (3:30-3:50)
    {"id": "v7_scene_29", "vo": "I risultati del tuo lavoro meritano di essere visti.", "voice": "sara"},
    {"id": "v7_scene_30", "vo": "Foto prima e dopo, galleria lavori, il portfolio della tua attivita'. I clienti lo vedono. E tornano.", "voice": "sara"},

    # CH7: Fidelizza (3:50-4:10)
    {"id": "v7_scene_31", "vo": "Il QR code sul bancone. Il cliente lo scansiona e resta in contatto con te.", "voice": "sara"},
    {"id": "v7_scene_32", "vo": None},  # visual break
    {"id": "v7_scene_33", "vo": "Pacchetti fedelta'. Cinque sedute colore a prezzo scontato. Il cliente paga oggi e torna sempre. Sara propone il pacchetto al momento giusto.", "voice": "sara"},

    # CH8: Gestione Completa (4:10-4:30)
    {"id": "v7_scene_34", "vo": "La cassa. Quanto hai incassato oggi. Contanti, carte, Satispay. Ogni euro tracciato.", "voice": "sara"},
    {"id": "v7_scene_35", "vo": None},  # visual break imprenditrice
    {"id": "v7_scene_36", "vo": "Fatturato mensile, top servizi, classifica operatori. Senza fogli Excel.", "voice": "sara"},

    # CH9: Quanto Costa Non Averlo (4:25-5:00)
    {"id": "v7_scene_37", "vo": "Facciamo due conti. Un gestionale in abbonamento ti costa centoventi euro al mese. Ogni mese. Per sempre. In tre anni: quattromilatrecentoventi euro. E non e' mai tuo. Se smetti di pagare, perdi tutto.", "voice": "sara"},
    {"id": "v7_scene_38", "vo": "FLUXION costa quattrocentonovantasette euro. Una volta sola. Per sempre tuo. Vuoi anche Sara? Ottocentonovantasette euro. Si ripaga in tre settimane.", "voice": "sara"},

    # CH10: Come Ho Fatto Senza? (5:00-5:20)
    {"id": "v7_scene_39", "vo": "Parrucchieri, officine, dentisti, fisioterapisti, centri estetici, palestre. Non importa qual e' la tua attivita'. FLUXION e' il partner che ti mancava. Trenta giorni soddisfatti o rimborsati.", "voice": "sara"},
    {"id": "v7_scene_40", "vo": "FLUXION. Paghi una volta. Usi per sempre. E ti chiederai... come ho fatto senza?", "voice": "sara"},
    {"id": "v7_scene_41", "vo": None},  # endcard
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


async def main():
    print("=" * 60)
    print("  FLUXION V7 — Voiceover Generation (Edge-TTS)")
    print(f"  Scenes: {len(SCENES)}")
    print("=" * 60)

    manifest = {}

    for scene in SCENES:
        sid = scene["id"]
        vo = scene.get("vo")
        voice_type = scene.get("voice", "sara")

        if not vo:
            manifest[sid] = {
                "mp3_path": None,
                "duration_seconds": 0.0,
                "type": "silent"
            }
            print(f"  {sid}: silent")
            continue

        mp3_path = str(TMPDIR / f"{sid}.mp3")

        if voice_type == "client":
            voice = VOICE_CLIENT
            rate = RATE_CLIENT
        else:
            voice = VOICE_SARA
            rate = RATE_SARA

        dur = await generate_tts(vo, mp3_path, voice=voice, rate=rate)
        manifest[sid] = {
            "mp3_path": mp3_path,
            "duration_seconds": round(dur, 2),
            "type": "dialogue" if voice_type == "client" else "narration",
            "voice": voice.split("-")[-1]
        }
        print(f"  {sid}: {dur:.1f}s ({voice_type})")

    # Save manifest
    manifest_path = TMPDIR / "v7-voiceover-manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest: {manifest_path}")

    total = sum(v["duration_seconds"] for v in manifest.values())
    print(f"Total voiceover: {total:.0f}s ({total/60:.1f} min)")


if __name__ == "__main__":
    asyncio.run(main())
