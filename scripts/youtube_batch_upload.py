#!/usr/bin/env python3
"""
FLUXION — Batch YouTube Upload (10 video)
Carica landing_v4 + 9 video verticali con metadata SEO ottimizzate.

USO:
    python3 scripts/youtube_batch_upload.py            # dry-run (default)
    python3 scripts/youtube_batch_upload.py --execute  # esegue upload reale
    python3 scripts/youtube_batch_upload.py --execute --only landing_v4
    python3 scripts/youtube_batch_upload.py --execute --privacy public

NOTE:
- Privacy default: "unlisted" (sicurezza primo upload — promuovere a public via Studio)
- Resumable: salta video gia caricati (controllo via youtube_uploads_log.json)
- Token OAuth riusato da youtube_token.json (primo run apre browser)
"""

import argparse
import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
VIDEO_BASE = os.path.join(PROJECT_ROOT, "video-factory", "output")
THUMB_BASE = os.path.join(PROJECT_ROOT, "landing", "assets")

CLIENT_SECRETS = os.path.join(SCRIPT_DIR, "client_secrets.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "youtube_token.json")
UPLOAD_LOG = os.path.join(SCRIPT_DIR, "youtube_uploads_log.json")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# ─── Metadata configurazione ──────────────────────────────────────────────────

LANDING_URL = "https://fluxion-landing.pages.dev"
COMMON_TAGS = [
    "gestionale italiano", "PMI italiane", "FLUXION", "software gestionale",
    "appuntamenti automatici", "WhatsApp business", "agenda digitale",
    "no abbonamento", "una tantum", "497 euro",
]

VIDEOS = [
    {
        "key": "landing_v4",
        "video": os.path.join(VIDEO_BASE, "landing_v4", "landing_v4_16x9.mp4"),
        "thumbnail": os.path.join(THUMB_BASE, "youtube-thumbnail-v8.png"),
        "title": "FLUXION — Il gestionale italiano per PMI. Una volta. Per sempre. €497",
        "description": (
            "FLUXION e il gestionale italiano fatto per le PMI. Una sola volta, €497, per sempre.\n"
            "Niente abbonamenti mensili. Niente commissioni sui clienti. Niente cloud obbligatorio.\n\n"
            "✓ Sara, la segretaria al telefono 24/7 — risponde, prenota, conferma\n"
            "✓ WhatsApp automatico — promemoria, conferme, post-vendita\n"
            "✓ Calendario, schede cliente, cassa — tutto offline, tutto tuo\n"
            "✓ Funziona su Mac e Windows. Setup in 2 click.\n\n"
            "PERCHE FLUXION\n"
            "I tuoi colleghi pagano €120-300/mese a software stranieri.\n"
            "In 3 anni: €4.320-10.800. Per sempre.\n"
            "FLUXION: €497, una volta. Tutto qui.\n\n"
            f"→ Scarica subito: {LANDING_URL}\n\n"
            "VERTICALI SUPPORTATI\n"
            "Parrucchiere · Barbiere · Estetica · Nail · Officina · Carrozzeria\n"
            "Dentista · Fisioterapia · Palestra · Wellness · e altri 17+\n\n"
            "#FLUXION #GestionaleItaliano #PMI"
        ),
        "tags": COMMON_TAGS + [
            "gestionale parrucchiere", "gestionale officina", "gestionale dentista",
            "Sara segretaria AI", "voice agent italiano",
        ],
    },
    {
        "key": "parrucchiere",
        "video": os.path.join(VIDEO_BASE, "parrucchiere", "parrucchiere_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Parrucchiere: 28% di no-show. Treatwell prende il 25%. FLUXION zero. — €497",
        "description": (
            "28 clienti su 100 non si presentano senza promemoria automatico [CNA Benessere 2023].\n"
            "Treatwell prende il 25% su ogni cliente nuovo che ti porta.\n"
            "FLUXION: zero abbonamenti, zero commissioni. €497 una volta.\n\n"
            "Sara risponde al telefono mentre hai le mani nei capelli.\n"
            "Conosce la formula colore di ogni cliente, le allergie, il patch test.\n"
            "Manda i promemoria. I tuoi clienti tornano.\n\n"
            f"→ Scopri di piu: {LANDING_URL}\n\n"
            "#FLUXION #Parrucchiere #SalonManagement"
        ),
        "tags": COMMON_TAGS + ["parrucchiere", "salone bellezza", "Treatwell alternativa", "no-show parrucchiere"],
    },
    {
        "key": "barbiere",
        "video": os.path.join(VIDEO_BASE, "barbiere", "barbiere_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Barbiere: +40% concorrenza in 5 anni. Ogni chiamata persa = cliente regalato. — €497",
        "description": (
            "Le barberie in Italia sono cresciute del 40% in 5 anni [Confartigianato 2023].\n"
            "Quando hai il rasoio in mano, il telefono squilla nel vuoto.\n"
            "Il cliente che aspettava chiama il barbiere dall'altra parte della strada.\n\n"
            "Sara risponde mentre tu lavori. Prenota, conferma, manda il promemoria.\n"
            "I tuoi clienti restano tuoi.\n\n"
            "FLUXION: €497 una volta. Per sempre. Zero abbonamenti.\n"
            f"→ {LANDING_URL}\n\n"
            "#FLUXION #Barbershop #Barbiere"
        ),
        "tags": COMMON_TAGS + ["barbiere", "barbershop", "gestionale barbiere", "prenotazioni telefoniche"],
    },
    {
        "key": "officina",
        "video": os.path.join(VIDEO_BASE, "officina", "officina_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Officina: 13.000 euro l'anno persi al telefono. La revisione scade. — FLUXION €497",
        "description": (
            "20 telefonate al giorno per un'officina di 3 persone.\n"
            "13 sono \"a che punto e la mia auto?\" [stima CNA Meccanica].\n"
            "1 ora persa al giorno × €50/h × 26 gg = €13.000/anno mai fatturati.\n\n"
            "FLUXION manda il WhatsApp \"auto pronta\" automatico.\n"
            "Il promemoria revisione parte 60 giorni prima della scadenza [CdS art. 80].\n"
            "Sara risponde mentre sei sotto al cofano.\n\n"
            "€497 una volta. FAST Officina costa €1.800-5.400 in 3 anni.\n"
            f"→ {LANDING_URL}\n\n"
            "#FLUXION #Officina #Meccanica"
        ),
        "tags": COMMON_TAGS + ["officina meccanica", "gestionale officina", "FAST Officina alternativa", "revisione auto"],
    },
    {
        "key": "carrozzeria",
        "video": os.path.join(VIDEO_BASE, "carrozzeria", "carrozzeria_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Carrozzeria: il cliente chiama 4 volte per l'auto. FLUXION manda WhatsApp. — €497",
        "description": (
            "18.000 carrozzerie indipendenti in Italia [Confartigianato Carrozzieri].\n"
            "Il cliente chiama: \"E pronta?\" Tu sei in cabina di verniciatura.\n"
            "Mani occupate, telefono che squilla, lavoro che si ferma.\n\n"
            "FLUXION manda il WhatsApp automatico:\n"
            "\"Sig. Russo, la sua auto e pronta. Puo venire a ritirarla.\"\n"
            "Sara risponde alle chiamate mentre lavori.\n\n"
            "€497 una volta. Per sempre. Zero abbonamenti.\n"
            f"→ {LANDING_URL}\n\n"
            "#FLUXION #Carrozzeria"
        ),
        "tags": COMMON_TAGS + ["carrozzeria", "gestionale carrozzeria", "WhatsApp officina", "preventivi auto"],
    },
    {
        "key": "centro_estetico",
        "video": os.path.join(VIDEO_BASE, "centro_estetico", "centro_estetico_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Centro Estetico: €22.500/anno regalati a Treatwell. FLUXION zero commissioni. — €497",
        "description": (
            "92.000 centri estetici attivi in Italia [Confartigianato Benessere 2023].\n"
            "Fatturato medio €85.000-95.000/anno.\n"
            "Treatwell prende il 25% sui nuovi clienti = €22.500 regalati ogni anno.\n\n"
            "FLUXION: schede controindicazioni digitali, GDPR-compliant per legge.\n"
            "Sara prenota, conferma, manda il promemoria.\n"
            "Zero abbonamenti. Zero commissioni. Una volta. Per sempre.\n\n"
            f"→ {LANDING_URL}\n\n"
            "#FLUXION #CentroEstetico #Beauty"
        ),
        "tags": COMMON_TAGS + ["centro estetico", "estetista", "Treatwell alternativa", "schede consenso GDPR"],
    },
    {
        "key": "nail_artist",
        "video": os.path.join(VIDEO_BASE, "nail_artist", "nail_artist_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Nail Artist: pennellino 0.5mm, telefono squilla. FLUXION risponde per te. — €497",
        "description": (
            "75 minuti per una nail art completa. Mano ferma, concentrazione totale.\n"
            "Il telefono sul tavolo vibra. Vibra ancora.\n"
            "Un cliente che voleva prenotare ha appena chiamato la nail artist accanto.\n\n"
            "Sara risponde mentre lavori. Conosce le tue tariffe, le tue disponibilita.\n"
            "Prenota, conferma, manda il promemoria.\n\n"
            "FLUXION: €497 una volta. Per sempre.\n"
            f"→ {LANDING_URL}\n\n"
            "#FLUXION #NailArt #Manicure"
        ),
        "tags": COMMON_TAGS + ["nail artist", "manicure", "gestionale nail", "ricostruzione unghie"],
    },
    {
        "key": "dentista",
        "video": os.path.join(VIDEO_BASE, "dentista", "dentista_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Dentista: 23% no-show. Poltrona vuota = €200/ora persi. FLUXION 7%. — €497",
        "description": (
            "47.000 odontoiatri iscritti all'ordine in Italia [FNOMCEO 2023].\n"
            "No-show senza promemoria: 23% degli appuntamenti [Dental Tribune].\n"
            "Con promemoria automatico: 7%.\n"
            "Poltrona dentale: €150-250/ora di costo.\n\n"
            "FLUXION manda il promemoria 24h prima e il giorno stesso.\n"
            "Sara risponde, prenota, gestisce le cancellazioni.\n"
            "Anamnesi digitali, GDPR-compliant.\n\n"
            "€497 una volta. XDENT e altri costano migliaia €/anno.\n"
            f"→ {LANDING_URL}\n\n"
            "#FLUXION #Dentista #StudioDentistico"
        ),
        "tags": COMMON_TAGS + ["dentista", "studio dentistico", "XDENT alternativa", "anamnesi digitale"],
    },
    {
        "key": "fisioterapista",
        "video": os.path.join(VIDEO_BASE, "fisioterapista", "fisioterapista_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Fisioterapia: 25% no-show = ciclo interrotto = recidiva. FLUXION zero. — €497",
        "description": (
            "68.000 fisioterapisti iscritti all'albo [AIFI 2023].\n"
            "Ciclo standard: 10 sedute. No-show senza promemoria: 25% [survey AIFI 2022].\n"
            "Un ciclo interrotto = rischio recidiva documentato.\n\n"
            "FLUXION traccia il percorso paziente seduta per seduta.\n"
            "VAS (Visual Analogue Scale) integrata. Promemoria automatici WhatsApp.\n"
            "Sara prenota, conferma, gestisce ricicli.\n\n"
            "€497 una volta. Per sempre.\n"
            f"→ {LANDING_URL}\n\n"
            "#FLUXION #Fisioterapia"
        ),
        "tags": COMMON_TAGS + ["fisioterapista", "fisioterapia", "VAS dolore", "gestionale fisio"],
    },
    {
        "key": "palestra",
        "video": os.path.join(VIDEO_BASE, "palestra", "palestra_final_16x9.mp4"),
        "thumbnail": None,
        "title": "Palestra: 50% abbandona in 3 mesi. FLUXION +34% retention. — €497",
        "description": (
            "35.000 palestre in Italia, 8,5 milioni iscritti [IHRSA 2023].\n"
            "50% abbandona entro 3 mesi. 67% non rinnova entro 12 mesi.\n"
            "+34% retention con engagement automatico [studi IHRSA].\n\n"
            "FLUXION manda WhatsApp di re-engagement automatici.\n"
            "Tracciamento certificato medico (responsabilita civile titolare).\n"
            "Sara gestisce iscrizioni, prenotazioni corsi, rinnovi.\n\n"
            "€497 una volta. Mindbody costa migliaia €/anno.\n"
            f"→ {LANDING_URL}\n\n"
            "#FLUXION #Palestra #Fitness"
        ),
        "tags": COMMON_TAGS + ["palestra", "fitness", "Mindbody alternativa", "retention palestra"],
    },
]


# ─── Auth ────────────────────────────────────────────────────────────────────

def get_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[auth] refresh token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS):
                print(f"ERROR: client_secrets.json mancante in {CLIENT_SECRETS}")
                sys.exit(1)
            print("[auth] primo run — apertura browser per autorizzazione...")
            print("[auth] account da usare: fluxion.gestionale@gmail.com")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print(f"[auth] token salvato: {TOKEN_FILE}")
    return creds


# ─── Upload log (resumable) ──────────────────────────────────────────────────

def load_log():
    if os.path.exists(UPLOAD_LOG):
        with open(UPLOAD_LOG) as f:
            return json.load(f)
    return {}


def save_log(log):
    with open(UPLOAD_LOG, "w") as f:
        json.dump(log, f, indent=2)


# ─── Single video upload ─────────────────────────────────────────────────────

def upload_one(youtube, item: dict, privacy: str) -> dict:
    from googleapiclient.http import MediaFileUpload

    video_path = item["video"]
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    file_size = os.path.getsize(video_path)
    print(f"  file: {os.path.basename(video_path)} ({file_size/1024/1024:.1f} MB)")
    print(f"  title: {item['title'][:80]}")

    body = {
        "snippet": {
            "title": item["title"][:100],  # YouTube limit 100 chars
            "description": item["description"],
            "tags": item["tags"][:30],     # YouTube limit 30 tags
            "categoryId": "28",            # Science & Technology
            "defaultLanguage": "it",
            "defaultAudioLanguage": "it",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
        },
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=4 * 1024 * 1024)
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    last = -1
    retries = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                p = int(status.progress() * 100)
                if p != last:
                    bar = "#" * (p // 5) + "." * (20 - p // 5)
                    print(f"\r  [{bar}] {p}%", end="", flush=True)
                    last = p
        except Exception as e:
            retries += 1
            print(f"\n  [retry {retries}] {e}")
            if retries > 5:
                raise
            time.sleep(5 * retries)

    print()
    video_id = response["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"  → {url}")

    # Thumbnail (opzionale)
    if item.get("thumbnail") and os.path.exists(item["thumbnail"]):
        try:
            thumb_media = MediaFileUpload(item["thumbnail"], mimetype="image/png")
            youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
            print(f"  ✓ thumbnail uploaded")
        except Exception as e:
            print(f"  ⚠ thumbnail skip: {e}")

    return {
        "video_id": video_id,
        "url": url,
        "embed": f"https://www.youtube.com/embed/{video_id}",
        "title": item["title"],
        "privacy": privacy,
        "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Esegui upload reale (default: dry-run)")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="unlisted")
    parser.add_argument("--only", help="Carica solo un key specifico (es: landing_v4)")
    parser.add_argument("--retry-failed", action="store_true", help="Riprova solo quelli falliti")
    args = parser.parse_args()

    log = load_log()

    targets = VIDEOS if not args.only else [v for v in VIDEOS if v["key"] == args.only]
    if not targets:
        print(f"ERROR: key '{args.only}' non trovato")
        sys.exit(1)

    # Pre-check file
    print(f"\n=== {'EXECUTE' if args.execute else 'DRY-RUN'} | privacy: {args.privacy} | {len(targets)} video ===\n")
    missing = []
    for v in targets:
        ok = os.path.exists(v["video"])
        already = log.get(v["key"], {}).get("video_id")
        size = os.path.getsize(v["video"]) / 1024 / 1024 if ok else 0
        status = "OK" if ok else "MISSING"
        skip = " [SKIP: already uploaded]" if already and not args.retry_failed else ""
        print(f"  [{status}] {v['key']:<18} {size:6.1f} MB  {v['title'][:60]}{skip}")
        if not ok:
            missing.append(v["video"])

    if missing:
        print(f"\nERROR: {len(missing)} file mancanti:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)

    if not args.execute:
        print("\n[dry-run] usa --execute per caricare davvero.")
        return

    # Auth
    print("\n[auth] autenticazione...")
    creds = get_credentials()
    from googleapiclient.discovery import build
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    # Upload loop
    uploaded = []
    failed = []
    for i, v in enumerate(targets, 1):
        if v["key"] in log and log[v["key"]].get("video_id") and not args.retry_failed:
            print(f"\n[{i}/{len(targets)}] {v['key']} — SKIP (gia caricato: {log[v['key']]['url']})")
            continue
        print(f"\n[{i}/{len(targets)}] {v['key']}")
        try:
            result = upload_one(youtube, v, args.privacy)
            log[v["key"]] = result
            save_log(log)
            uploaded.append((v["key"], result["url"]))
            time.sleep(2)  # rate limit gentle
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed.append((v["key"], str(e)))
            log[v["key"]] = {"error": str(e), "failed_at": time.strftime("%Y-%m-%d %H:%M:%S")}
            save_log(log)

    # Summary
    print("\n" + "=" * 70)
    print(f"UPLOAD COMPLETATO — {len(uploaded)} ok, {len(failed)} fail")
    print("=" * 70)
    for key, url in uploaded:
        print(f"  ✓ {key:<18} {url}")
    for key, err in failed:
        print(f"  ✗ {key:<18} {err[:80]}")

    if uploaded:
        print(f"\nPrivacy attuale: {args.privacy}.")
        if args.privacy != "public":
            print("Per promuovere a 'public': YouTube Studio o usa --privacy public")
        print(f"\nLog salvato: {UPLOAD_LOG}")


if __name__ == "__main__":
    main()
