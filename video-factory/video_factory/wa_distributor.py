"""
wa_distributor.py — FLUXION Video Factory
Integra i video nel WA Intelligence System (Luca Ferretti).
Genera sequenze complete di outreach con link video per ogni verticale.

Si connette all'infrastruttura WA esistente:
  - whatsapp-web.js + PM2 (già attivo)
  - Telegram bot human-in-loop (già attivo)
  - Anti-ban: max 5 nuovi contatti/giorno, SIM italiana

Uso:
  python video_factory/wa_distributor.py --vertical parrucchiere --contacts contacts.csv
  python video_factory/wa_distributor.py --vertical all --preview  # solo stampa messaggi
"""

from __future__ import annotations
import csv
import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

# ─── Config WA Infrastructure ────────────────────────────────────────────────

WA_SERVER_URL     = os.environ.get("WA_SERVER_URL", "http://localhost:3000")
TELEGRAM_BOT_URL  = os.environ.get("TELEGRAM_BOT_URL", "")
TELEGRAM_CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID", "")

MAX_NEW_CONTACTS_PER_DAY = 5     # Anti-ban warm-up
INTER_MESSAGE_DELAY      = 45    # secondi tra messaggi (anti-spam)


# ─── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class Contact:
    name: str
    phone: str          # formato internazionale: +39...
    business_type: str  # verticale corrispondente
    city: str = ""
    notes: str = ""


@dataclass
class OutreachSequence:
    contact: Contact
    day0_message: str
    day2_message: str
    day5_message: str
    day10_message: str
    video_url: str
    verticale: str


# ─── Carica contatti ─────────────────────────────────────────────────────────

def load_contacts(csv_path: Path) -> list[Contact]:
    """
    Carica contatti da CSV.
    Formato atteso: name,phone,business_type,city,notes
    """
    contacts = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            phone = row.get("phone", "").strip()
            if not phone.startswith("+"):
                phone = "+39" + phone.lstrip("0")
            contacts.append(Contact(
                name=row.get("name", ""),
                phone=phone,
                business_type=row.get("business_type", ""),
                city=row.get("city", ""),
                notes=row.get("notes", ""),
            ))
    return contacts


def load_contacts_from_json(json_path: Path) -> list[Contact]:
    """Carica da JSON (formato alternativo)."""
    data = json.loads(json_path.read_text())
    return [
        Contact(
            name=c["name"],
            phone=c["phone"],
            business_type=c.get("business_type", ""),
            city=c.get("city", ""),
        )
        for c in data
    ]


# ─── Genera sequenze outreach ─────────────────────────────────────────────────

def build_outreach_sequence(
    contact: Contact,
    verticale: str,
    video_url: str,
    output_dir: Path,
) -> OutreachSequence:
    """Costruisce la sequenza completa di messaggi per un contatto."""

    # Carica messaggi pre-generati
    wa_files = {
        "day0": output_dir / "wa_message.txt",
        "day2": output_dir / "wa_followup_d2.txt",
        "day5": output_dir / "wa_followup_d5.txt",
        "day10": output_dir / "wa_close_d10.txt",
    }

    messages = {}
    for key, path in wa_files.items():
        if path.exists():
            content = path.read_text()
            # Personalizza con nome e URL
            content = content.replace("[nome]", contact.name.split()[0])
            content = content.replace("[VIDEO_LINK]", video_url)
            content = content.replace("[nome_attività]", contact.notes or "")
            messages[key] = content
        else:
            messages[key] = _fallback_message(key, contact, video_url, verticale)

    return OutreachSequence(
        contact=contact,
        day0_message=messages["day0"],
        day2_message=messages["day2"],
        day5_message=messages["day5"],
        day10_message=messages["day10"],
        video_url=video_url,
        verticale=verticale,
    )


def _fallback_message(
    day_key: str, contact: Contact, video_url: str, verticale: str
) -> str:
    """Messaggi fallback se i file non esistono."""
    name = contact.name.split()[0]
    messages = {
        "day0": (
            f"Ciao {name}, ho visto che hai una {verticale.replace('_', ' ')}.\n\n"
            f"{video_url}\n\n"
            f"FLUXION: €497 una volta, nessun abbonamento.\n"
            f"fluxion-landing.pages.dev"
        ),
        "day2": (
            f"Ciao {name}, hai visto il video?\n\n"
            f"€497. Una volta sola.\n"
            f"fluxion-landing.pages.dev"
        ),
        "day5": (
            f"{name}, quanto paghi al mese per il gestionale?\n\n"
            f"Se è più di €14, FLUXION ti costa meno nell'anno.\n"
            f"fluxion-landing.pages.dev"
        ),
        "day10": (
            f"{name}, chiudo qui.\n"
            f"FLUXION — €497 senza abbonamenti.\n"
            f"fluxion-landing.pages.dev"
        ),
    }
    return messages.get(day_key, "")


# ─── Invio WA (via whatsapp-web.js server) ───────────────────────────────────

def send_wa_message(
    phone: str,
    message: str,
    require_approval: bool = True,
) -> bool:
    """
    Invia messaggio WA tramite il server whatsapp-web.js locale.
    Se require_approval=True, manda prima su Telegram per approvazione.
    """
    if require_approval:
        return _send_via_telegram_approval(phone, message)
    else:
        return _send_direct(phone, message)


def _send_via_telegram_approval(phone: str, message: str) -> bool:
    """
    Invia preview su Telegram e attende approvazione umana.
    Questo è il flow standard — nessun WA senza approvazione.
    """
    if not TELEGRAM_BOT_URL or not TELEGRAM_CHAT_ID:
        logger.warning(
            "TELEGRAM_BOT_URL o TELEGRAM_CHAT_ID non impostati. "
            "Operando in modalità DRY-RUN (nessun messaggio inviato)."
        )
        print(f"\n[DRY RUN] A: {phone}")
        print(f"[DRY RUN] Messaggio:\n{message}\n")
        return False

    preview = (
        f"📤 *Nuovo messaggio WA*\n\n"
        f"*A:* `{phone}`\n\n"
        f"*Messaggio:*\n```\n{message}\n```\n\n"
        f"Rispondi con:\n"
        f"/approva — invia il messaggio\n"
        f"/rifiuta — salta questo contatto\n"
        f"/stop — ferma tutta la sessione"
    )

    telegram_url = f"{TELEGRAM_BOT_URL}/sendMessage"
    resp = requests.post(telegram_url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": preview,
        "parse_mode": "Markdown",
    }, timeout=10)

    if resp.status_code != 200:
        logger.error(f"Telegram send failed: {resp.text}")
        return False

    logger.info(f"Preview inviata su Telegram per {phone}. Attendo approvazione...")
    # Il bot gestisce l'approvazione in modo asincrono
    # Il flag di ritorno indica che la preview è stata inviata
    return True


def _send_direct(phone: str, message: str) -> bool:
    """Invia direttamente tramite whatsapp-web.js API locale."""
    try:
        resp = requests.post(
            f"{WA_SERVER_URL}/api/send",
            json={"phone": phone, "message": message},
            timeout=30,
        )
        if resp.status_code == 200:
            logger.info(f"WA inviato a {phone}")
            return True
        else:
            logger.error(f"WA send failed [{resp.status_code}]: {resp.text}")
            return False
    except Exception as e:
        logger.error(f"WA send error: {e}")
        return False


# ─── Orchestratore campagna ───────────────────────────────────────────────────

def run_campaign(
    verticale: str,
    contacts: list[Contact],
    video_url: str,
    output_dir: Path,
    day: int = 0,                    # 0, 2, 5, 10
    preview_only: bool = False,
    max_contacts: int = MAX_NEW_CONTACTS_PER_DAY,
) -> list[dict]:
    """
    Esegui una sessione di outreach per una verticale.
    day=0: Day 0 messages, day=2: follow-up, ecc.
    """
    results = []
    sent_count = 0

    for contact in contacts[:max_contacts]:
        seq = build_outreach_sequence(contact, verticale, video_url, output_dir)

        day_map = {0: seq.day0_message, 2: seq.day2_message,
                   5: seq.day5_message, 10: seq.day10_message}
        message = day_map.get(day, seq.day0_message)

        if not message:
            logger.warning(f"Nessun messaggio per Day {day}, skip {contact.phone}")
            continue

        result = {
            "phone": contact.phone,
            "name": contact.name,
            "day": day,
            "message_preview": message[:100] + "...",
            "sent": False,
        }

        if preview_only:
            print(f"\n{'─'*40}")
            print(f"A: {contact.name} ({contact.phone})")
            print(f"Giorno: {day}")
            print(f"Messaggio:\n{message}")
        else:
            success = send_wa_message(contact.phone, message, require_approval=True)
            result["sent"] = success
            sent_count += 1

            if sent_count < len(contacts) and not preview_only:
                logger.info(f"Pausa anti-ban {INTER_MESSAGE_DELAY}s...")
                time.sleep(INTER_MESSAGE_DELAY)

        results.append(result)

    # Log sessione
    session_log = output_dir / f"wa_session_day{day}_{int(time.time())}.json"
    session_log.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    logger.info(f"Sessione loggata: {session_log}")

    return results


# ─── Generazione CSV template contatti ───────────────────────────────────────

def generate_contacts_template(output_path: Path) -> None:
    """Genera CSV template per i contatti."""
    headers = ["name", "phone", "business_type", "city", "notes"]
    examples = [
        ["Mario Rossi", "+393331234567", "parrucchiere", "Napoli", "Salone Via Roma"],
        ["Lucia Bianchi", "+393387654321", "officina", "Bari", "Officina Bianchi Srl"],
        ["Dr. Verdi", "+393456789012", "dentista", "Potenza", "Studio Via Mazzini 5"],
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(examples)

    print(f"Template contatti generato: {output_path}")
    print("Popola con i tuoi contatti e passa a --contacts")


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="FLUXION WA Distributor")
    parser.add_argument("--vertical", required=True)
    parser.add_argument("--contacts", type=Path, help="CSV o JSON con contatti")
    parser.add_argument("--day", type=int, default=0, choices=[0, 2, 5, 10],
                        help="Giorno della sequenza (0=primo contatto)")
    parser.add_argument("--max", type=int, default=5,
                        help="Max contatti da processare (default 5, anti-ban)")
    parser.add_argument("--preview", action="store_true",
                        help="Solo stampa messaggi, non invia")
    parser.add_argument("--generate-template", action="store_true",
                        help="Genera CSV template contatti")
    parser.add_argument("--output-base", type=Path, default=Path("./output"))
    args = parser.parse_args()

    if args.generate_template:
        generate_contacts_template(Path("contacts_template.csv"))
        exit(0)

    output_dir = args.output_base / args.vertical

    # Carica URL video dal metadata
    meta_path = output_dir / "metadata.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        urls = meta.get("video_urls", {})
        video_url = (
            urls.get("r2_9x16") or
            urls.get("vimeo_9x16") or
            urls.get("youtube") or
            "[VIDEO_LINK]"
        )
    else:
        video_url = "[VIDEO_LINK]"
        logger.warning(f"metadata.json non trovato — usa URL placeholder")

    # Carica contatti
    if args.contacts:
        if args.contacts.suffix == ".json":
            contacts = load_contacts_from_json(args.contacts)
        else:
            contacts = load_contacts(args.contacts)
        print(f"Caricati {len(contacts)} contatti")
    else:
        # Demo mode senza contatti reali
        contacts = [Contact(
            name="[nome]",
            phone="+39XXXXXXXXXX",
            business_type=args.vertical,
        )]
        logger.info("Nessun file contatti — usando placeholder")
        args.preview = True

    results = run_campaign(
        verticale=args.vertical,
        contacts=contacts,
        video_url=video_url,
        output_dir=output_dir,
        day=args.day,
        preview_only=args.preview,
        max_contacts=args.max,
    )

    print(f"\nProcessati: {len(results)} contatti")
