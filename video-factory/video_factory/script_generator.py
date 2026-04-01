"""
script_generator.py — FLUXION Video Factory
Genera script + prompt Veo 3 per ogni verticale automaticamente.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

from video_factory.veo3_client import Veo3Request


# ─── Verticale definitions ────────────────────────────────────────────────────

VERTICALI: dict[str, dict] = {

    "parrucchiere": {
        "label": "Salone di Parrucchiere",
        "dolori": [
            "Telefonate perse mentre lavori con le mani occupate",
            "Clienti che saltano l'appuntamento senza avvisare",
            "Agenda di carta sempre disorganizzata",
        ],
        "feature_hero": "Sara risponde al telefono da sola",
        "pain_stat": "Perdi €800 al mese in appuntamenti saltati",
        "transform_text": "Sara ha gestito 23 chiamate mentre tu facevi le pieghe",
        "clips": {
            1: "Close-up, Italian woman hairdresser in 40s, exhausted expression, paper appointment book filled with crossings, phone ringing ignored on counter, warm vintage salon interior with mirrors and waiting customers, soft warm light, authentic handheld documentary, cinematic 4K, 9:16 vertical",
            2: "Extreme close-up, worn paper appointment calendar with many crossed-out entries and pen marks, hand frantically flipping pages, Italian currency visible, dramatic chiaroscuro light, slow motion, cinematic 4K, 9:16 vertical",
            3: "Over-shoulder, woman in salon holding smartphone showing clean digital calendar app, finger tapping to confirm appointment, satisfied smile reflection in mirror, warm window light, commercial photography style, smooth stabilized, cinematic 4K, 9:16 vertical",
        },
    },

    "barbiere": {
        "label": "Barbiere",
        "dolori": [
            "Telefonate che interrompono il lavoro continuamente",
            "Nessun promemoria ai clienti = posti vuoti",
            "Nessuno storico del cliente (barba, prodotti preferiti)",
        ],
        "feature_hero": "Sara prenota mentre tu rasoio in mano",
        "pain_stat": "Ogni posto vuoto = €35 perso",
        "transform_text": "L'agenda è piena. Zero telefonate inutili.",
        "clips": {
            1: "Medium shot, Italian barber in striped apron, phone pressed to ear while trying to continue shaving customer, traditional barbershop with leather chairs and striped pole, warm vintage lighting, frustrated multitasking, authentic documentary, cinematic 4K, 9:16 vertical",
            2: "Close-up, empty barber chair with cloak draped over it, soft focus empty shop, missed opportunity mood, late afternoon light, melancholic commercial aesthetic, cinematic 4K, 9:16 vertical",
            3: "Medium shot, same barber now fully focused on customer, phone notification sound implied, both barber and customer smiling, busy productive barbershop, golden warm light, slow motion, commercial uplifting, cinematic 4K, 9:16 vertical",
        },
    },

    "officina": {
        "label": "Officina Meccanica",
        "dolori": [
            "Clienti che chiamano 10 volte al giorno 'è pronta la mia auto?'",
            "Pezzi di ricambio ordinati senza registro = caos",
            "Nessuna traccia di quando scade la revisione del cliente",
        ],
        "feature_hero": "WhatsApp automatico: 'La tua auto è pronta!'",
        "pain_stat": "10 chiamate al giorno = 1 ora persa. Ogni giorno.",
        "transform_text": "I clienti ricevono il WhatsApp. Zero telefonate inutili.",
        "clips": {
            1: "Medium shot, Italian mechanic man in blue overalls at reception desk, phone ringing, three customers waiting, paper chaos on desk, realistic auto repair shop with tools and cars visible, industrial fluorescent lighting, overwhelmed expression, handheld documentary, cinematic 4K, 9:16 vertical",
            2: "Close-up, mechanic hands covered in grease holding ringing phone, paper order forms scattered, frustrated sigh visible, shallow depth of field, dramatic side lighting, cinematic 4K, 9:16 vertical",
            3: "Wide shot, same mechanic now back under car hood focused and calm, phone screen showing WhatsApp notification sent automatically, customer outside visible receiving message and smiling, organized workshop, cinematic 4K, 9:16 vertical",
        },
    },

    "carrozzeria": {
        "label": "Carrozzeria",
        "dolori": [
            "Gestire perizie, assicurazioni e clienti insieme è impossibile",
            "Stato riparazione: ogni cliente chiama per aggiornamenti",
            "Fatturazione manuale = errori e ritardi",
        ],
        "feature_hero": "Stato riparazione in tempo reale via WhatsApp",
        "pain_stat": "Ogni update manuale ai clienti = 5 minuti persi",
        "transform_text": "Il cliente sa tutto. Senza chiamare.",
        "clips": {
            1: "Wide shot, Italian auto body shop owner in work clothes, surrounded by damaged cars in various repair stages, phone in one hand, clipboard in other, stressed overwhelmed expression, realistic body shop interior, industrial lighting, handheld documentary, cinematic 4K, 9:16 vertical",
            2: "Close-up, hands writing on paper repair estimate form, crossing out numbers and rewriting, pen running out of ink, tension, shallow DOF, cinematic 4K, 9:16 vertical",
            3: "Medium shot, carrosserie owner at desk calmly using tablet, digital repair tracker visible, customer outside through window checking WhatsApp update and nodding satisfied, clean organized office, cinematic 4K, 9:16 vertical",
        },
    },

    "dentista": {
        "label": "Studio Dentistico",
        "dolori": [
            "Pazienti che saltano l'appuntamento = poltrona vuota a €150/h",
            "Anamnesi su carta = rischio errori + perdita tempo",
            "Nessun promemoria = no-show al 30%",
        ],
        "feature_hero": "Promemoria automatico 24h prima = 95% di conferme",
        "pain_stat": "Una poltrona vuota = €150 persi. Ogni volta.",
        "transform_text": "Zero no-show. Ogni poltrona occupata.",
        "clips": {
            1: "Wide shot, Italian dental office, empty dental chair prominently visible, receptionist on phone looking stressed, open paper calendar with crossed-out appointments, clinical white interior, bright medical lighting, slow dolly toward empty chair, melancholic mood, cinematic 4K, 9:16 vertical",
            2: "Close-up, calendar page with multiple cancellations written in pen, white dental chair soft focus in background, each cross-out implies lost money, stark white clinical lighting, cinematic 4K, 9:16 vertical",
            3: "Medium shot, dental chair now occupied with patient, dentist working calmly, receptionist visible in background checking phone with satisfied expression, all appointments confirmed, clean bright dental studio, warm natural light from window, commercial positive mood, cinematic 4K, 9:16 vertical",
        },
    },

    "fisioterapista": {
        "label": "Studio di Fisioterapia",
        "dolori": [
            "Cicli di trattamento non tracciati = paziente recidivo non recuperato",
            "Pazienti che saltano sedute senza avvisare",
            "Documentazione clinica su carta = perdita di tempo",
        ],
        "feature_hero": "Scheda paziente completa + ciclo trattamento digitale",
        "pain_stat": "Ogni seduta saltata senza avviso = €45 persi",
        "transform_text": "Il ciclo di trattamento è sempre aggiornato. Automatico.",
        "clips": {
            1: "Medium shot, Italian physiotherapist in white coat, patient on treatment table waiting patiently, therapist searching through paper files looking stressed, clinical physio studio with equipment, professional medical lighting, time-pressure authentic feel, handheld, cinematic 4K, 9:16 vertical",
            2: "Close-up, physiotherapist hands shuffling through paper patient folders, post-it notes falling off, illegible handwriting visible, frustrated expression in background, soft clinical light, cinematic 4K, 9:16 vertical",
            3: "Medium shot, physiotherapist now treating patient with full focus, tablet nearby showing digital patient card, progress tracking visible on screen, organized studio, calm professional atmosphere, warm clinical light, smooth camera, commercial uplifting, cinematic 4K, 9:16 vertical",
        },
    },

    "palestra": {
        "label": "Palestra / Centro Fitness",
        "dolori": [
            "Abbonamenti scaduti che nessuno rinnova = perdita cliente",
            "Presenze su registro cartaceo = nessun dato reale",
            "Clienti VIP non riconosciuti = poca fidelizzazione",
        ],
        "feature_hero": "Programma fedeltà VIP + promemoria rinnovo automatico",
        "pain_stat": "Il 40% dei clienti non rinnova per mancanza di follow-up",
        "transform_text": "I tuoi VIP rinnovano sempre. Da soli.",
        "clips": {
            1: "Wide shot, Italian gym owner in activewear, holding clipboard with paper attendance sheets, multiple members asking questions simultaneously, phone ringing, modern fitness equipment in background, fluorescent gym lighting, chaotic energy, documentary handheld, cinematic 4K, 9:16 vertical",
            2: "Close-up, paper membership cards and expired stickers, hand writing renewal date manually, spreadsheet partially visible, disorganized desk in gym office, cinematic 4K, 9:16 vertical",
            3: "Medium shot, gym owner now on gym floor engaging confidently with members, phone notification visible in pocket (membership renewal), VIP members wearing special wristbands, upbeat gym atmosphere, dynamic commercial lighting, smooth stabilized, cinematic 4K, 9:16 vertical",
        },
    },

    "nail_artist": {
        "label": "Nail Artist / Centro Unghie",
        "dolori": [
            "Telefonate continue che interrompono il lavoro di precisione",
            "Clienti che prenotano e non si presentano",
            "Nessuno storico del lavoro fatto sul cliente",
        ],
        "feature_hero": "Sara prenota mentre tu lavori. Senza interruzioni.",
        "pain_stat": "Un no-show = 45 minuti persi + cliente al posto vuoto",
        "transform_text": "Ogni posto occupato. Zero interruzioni.",
        "clips": {
            1: "Extreme close-up, nail technician's hands pausing intricate nail work to answer buzzing phone, client's half-done nails clearly visible, small nail studio interior, ring light aesthetic, awkward interruption mood, cinematic 4K, 9:16 vertical",
            2: "Medium shot, nail artist looking at empty nail station, client who cancelled visible only as empty chair, appointment calendar with crossed entry, disappointment expression, beauty studio lighting, cinematic 4K, 9:16 vertical",
            3: "Close-up, nail technician's hands doing intricate nail art uninterrupted, phone face-down showing silent notification (handled), client's nails being transformed beautifully, ring light beauty aesthetic, focus and calm, commercial beauty style, cinematic 4K, 9:16 vertical",
        },
    },

    "centro_estetico": {
        "label": "Centro Estetico",
        "dolori": [
            "Consensi informati su carta = rischio GDPR",
            "Storico trattamenti non tracciato = stessa cosa rifatta due volte",
            "Promozioni pacchetti non gestite = soldi sul tavolo",
        ],
        "feature_hero": "Scheda estetica digitale + pacchetti promo automatici",
        "pain_stat": "Senza pacchetti promo, ogni cliente vale la metà",
        "transform_text": "La scheda cliente è completa. I pacchetti si vendono da soli.",
        "clips": {
            1: "Wide shot, Italian beauty center, esthetician in uniform filling out paper forms with client before treatment, pile of paper folders visible on reception, busy beauty center background, warm beauty lighting, realistic authentic feel, cinematic 4K, 9:16 vertical",
            2: "Close-up, stack of client paper folders with handwritten notes, some faded or torn, a treatment accidentally repeated underlined in red, beauty products and tools around, cinematic 4K, 9:16 vertical",
            3: "Medium shot, esthetician performing treatment calmly, client relaxed, digital tablet nearby with complete client profile visible, organized modern beauty center, soft warm beauty lighting, smooth dolly, commercial premium feel, cinematic 4K, 9:16 vertical",
        },
    },
}


# ─── Prompt builder ──────────────────────────────────────────────────────────

NEGATIVE_PROMPT = (
    "text overlay, watermarks, logos, brand names, blurry, distorted faces, "
    "low quality, overexposed, artifacts, generic stock footage look, CGI, artificial"
)

CTA_FRAME_FFMPEG = {
    "background": "black",
    "lines": [
        ("FLUXION", "Inter-Bold", 72, "white", "center", 120),
        ("Il gestionale che non ti costa ogni mese", "Inter-Regular", 32, "#CCCCCC", "center", 210),
        ("€497 una volta. Per sempre.", "Inter-Bold", 52, "#FFFFFF", "center", 320),
        ("Competitor: €4.320 in 3 anni", "Inter-Regular", 28, "#FF4444", "center", 400),
        ("fluxion.app", "Inter-Bold", 36, "#AAAAFF", "center", 500),
    ],
}


def build_veo3_requests(verticale_key: str) -> list[Veo3Request]:
    """Costruisce i Veo3Request per le 3 clip di una verticale."""
    data = VERTICALI[verticale_key]
    requests = []

    for clip_id, prompt_text in data["clips"].items():
        req = Veo3Request(
            prompt=prompt_text,
            aspect_ratio="9:16",
            duration_seconds=8,
            sample_count=2,
            negative_prompt=NEGATIVE_PROMPT,
        )
        requests.append(req)

    return requests


def build_narration_script(verticale_key: str) -> dict:
    """Costruisce lo script narrazione per Edge-TTS."""
    data = VERTICALI[verticale_key]
    return {
        "verticale": verticale_key,
        "label": data["label"],
        "segments": [
            {
                "clip": 1,
                "start_sec": 0,
                "text": None,  # Apertura silenziosa — solo musica tesa
                "voice": "it-IT-IsabellaNeural",
            },
            {
                "clip": 2,
                "start_sec": 8,
                "text": f"{data['pain_stat']}. Ogni. Singolo. Giorno.",
                "voice": "it-IT-IsabellaNeural",
                "style": "empathetic",
            },
            {
                "clip": 3,
                "start_sec": 16,
                "text": (
                    f"Con FLUXION, {data['feature_hero'].lower()}. "
                    "I tuoi dati restano sul tuo computer. "
                    "Zero abbonamenti. Zero commissioni."
                ),
                "voice": "it-IT-IsabellaNeural",
                "style": "hopeful",
            },
            {
                "clip": "cta",
                "start_sec": 24,
                "text": "FLUXION. Quattrocentonovantasette euro. Una volta. Per sempre.",
                "voice": "it-IT-IsabellaNeural",
                "style": "confident",
            },
        ],
    }


def build_wa_message(verticale_key: str, dealer_name: str = "[nome]") -> str:
    """Messaggio WA per sales agent Luca Ferretti."""
    data = VERTICALI[verticale_key]
    label = data["label"].lower()

    hooks = {
        "parrucchiere": f"Ciao {dealer_name}, gestisci un salone? Questo video è fatto per te.",
        "barbiere": f"Ciao {dealer_name}, ho visto che hai una barberia. 30 secondi, poi mi dici.",
        "officina": f"Ciao {dealer_name}, so che rispondere al telefono in officina è un casino.",
        "carrozzeria": f"Ciao {dealer_name}, questo potrebbe interessarti come carrozziere.",
        "dentista": f"Ciao {dealer_name}, un video su come eliminare i no-show nel tuo studio.",
        "fisioterapista": f"Ciao {dealer_name}, per chi gestisce pazienti e cicli di trattamento.",
        "palestra": f"Ciao {dealer_name}, per palestre che vogliono più rinnovi automatici.",
        "nail_artist": f"Ciao {dealer_name}, per chi lavora di precisione e odia le interruzioni.",
        "centro_estetico": f"Ciao {dealer_name}, per i centri estetici che vogliono gestirsi meglio.",
    }

    hook = hooks.get(verticale_key, f"Ciao {dealer_name}, guarda questo.")

    return (
        f"{hook}\n\n"
        f"[VIDEO_LINK]\n\n"
        f"FLUXION — €497 una volta, nessun abbonamento.\n"
        f"Competitor come Treatwell: €120/mese + commissioni.\n\n"
        f"Se ti interessa: fluxion.app"
    )


def export_all_prompts(output_dir: Path = Path("./video_factory/prompts")) -> None:
    """Esporta tutti i prompt in JSON per review manuale."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for key in VERTICALI:
        requests = build_veo3_requests(key)
        script = build_narration_script(key)
        wa_msg = build_wa_message(key)

        export = {
            "verticale": key,
            "label": VERTICALI[key]["label"],
            "veo3_requests": [
                {
                    "clip": i + 1,
                    "prompt": r.prompt,
                    "aspect_ratio": r.aspect_ratio,
                    "duration_seconds": r.duration_seconds,
                    "negative_prompt": r.negative_prompt,
                }
                for i, r in enumerate(requests)
            ],
            "narration_script": script,
            "cta_frame": CTA_FRAME_FFMPEG,
            "wa_message_template": wa_msg,
        }

        path = output_dir / f"{key}_prompts.json"
        path.write_text(json.dumps(export, indent=2, ensure_ascii=False))
        print(f"Exported: {path}")


if __name__ == "__main__":
    export_all_prompts()
    print(f"\nVerticali disponibili: {list(VERTICALI.keys())}")
