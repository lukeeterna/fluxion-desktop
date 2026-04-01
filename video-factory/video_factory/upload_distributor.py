"""
upload_distributor.py — FLUXION Video Factory
Upload automatico su YouTube, Vimeo e Cloudflare R2.
Ritorna URL pubblici per i messaggi WA di Luca Ferretti.

Installazione:
  pip install PyVimeo google-api-python-client google-auth-oauthlib boto3

Configurazione:
  export VIMEO_TOKEN=...
  export VIMEO_KEY=...
  export VIMEO_SECRET=...
  export CLOUDFLARE_ACCOUNT_ID=...
  export CLOUDFLARE_R2_TOKEN=...
  export R2_BUCKET_NAME=fluxion-videos
  export R2_PUBLIC_URL=https://videos.fluxion.app
"""

from __future__ import annotations
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────

VIMEO_TOKEN   = os.environ.get("VIMEO_TOKEN", "")
VIMEO_KEY     = os.environ.get("VIMEO_KEY", "")
VIMEO_SECRET  = os.environ.get("VIMEO_SECRET", "")

CF_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
CF_R2_TOKEN   = os.environ.get("CLOUDFLARE_R2_TOKEN", "")
R2_BUCKET     = os.environ.get("R2_BUCKET_NAME", "fluxion-videos")
R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL", "https://videos.fluxion.app")

YT_CLIENT_SECRETS = os.environ.get("YT_CLIENT_SECRETS", "")


# ─── Vimeo Upload ─────────────────────────────────────────────────────────────

def upload_vimeo(
    video_path: Path,
    title: str,
    description: str,
    privacy: str = "unlisted",   # "unlisted" per WA, "public" per Vimeo channel
) -> str:
    """Upload video su Vimeo. Ritorna URL del video."""
    try:
        import vimeo
    except ImportError:
        raise ImportError("pip install PyVimeo")

    if not VIMEO_TOKEN:
        raise EnvironmentError("VIMEO_TOKEN non impostato")

    client = vimeo.VimeoClient(
        token=VIMEO_TOKEN,
        key=VIMEO_KEY,
        secret=VIMEO_SECRET,
    )

    logger.info(f"Upload Vimeo: {video_path.name}...")

    # Upload
    uri = client.upload(
        str(video_path),
        data={
            "name": title,
            "description": description,
            "privacy": {"view": privacy, "download": False},
        },
    )

    # Ottieni URL diretto
    response = client.get(uri + "?fields=link,player_embed_url")
    data = response.json()

    video_url = data.get("link", f"https://vimeo.com{uri}")
    logger.info(f"Vimeo URL: {video_url}")
    return video_url


# ─── Cloudflare R2 Upload ────────────────────────────────────────────────────

def upload_r2(
    video_path: Path,
    object_key: str | None = None,
    content_type: str = "video/mp4",
) -> str:
    """Upload video su Cloudflare R2. Ritorna URL pubblico CDN."""
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        raise ImportError("pip install boto3")

    if not CF_ACCOUNT_ID or not CF_R2_TOKEN:
        raise EnvironmentError(
            "CLOUDFLARE_ACCOUNT_ID e CLOUDFLARE_R2_TOKEN devono essere impostati"
        )

    if object_key is None:
        object_key = video_path.name

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{CF_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=CF_R2_TOKEN.split(":")[0] if ":" in CF_R2_TOKEN else CF_R2_TOKEN,
        aws_secret_access_key=CF_R2_TOKEN.split(":")[1] if ":" in CF_R2_TOKEN else CF_R2_TOKEN,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

    logger.info(f"Upload R2: {video_path.name} → {R2_BUCKET}/{object_key}...")

    with open(video_path, "rb") as f:
        s3.upload_fileobj(
            f,
            R2_BUCKET,
            object_key,
            ExtraArgs={
                "ContentType": content_type,
                "CacheControl": "public, max-age=31536000",
            },
        )

    public_url = f"{R2_PUBLIC_URL}/{object_key}"
    logger.info(f"R2 URL: {public_url}")
    return public_url


# ─── YouTube Upload ──────────────────────────────────────────────────────────

def upload_youtube(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "22",         # 22 = People & Blogs
    privacy: str = "public",         # "public" | "unlisted" | "private"
) -> str:
    """Upload video su YouTube. Ritorna URL del video."""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google_auth_oauthlib.flow import InstalledAppFlow
        import google.auth
    except ImportError:
        raise ImportError("pip install google-api-python-client google-auth-oauthlib")

    if not YT_CLIENT_SECRETS or not Path(YT_CLIENT_SECRETS).exists():
        raise EnvironmentError(
            f"YT_CLIENT_SECRETS non trovato: {YT_CLIENT_SECRETS}\n"
            "Genera il file su: https://console.cloud.google.com/apis/credentials"
        )

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    flow = InstalledAppFlow.from_client_secrets_file(YT_CLIENT_SECRETS, SCOPES)
    creds = flow.run_local_server(port=0)

    youtube = build("youtube", "v3", credentials=creds)

    logger.info(f"Upload YouTube: {video_path.name}...")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": category_id,
            "defaultLanguage": "it",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info(f"YouTube upload: {int(status.progress() * 100)}%")

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info(f"YouTube URL: {video_url}")
    return video_url


# ─── Orchestratore distribuzione ─────────────────────────────────────────────

def distribute_video(
    verticale: str,
    output_dir: Path,
    targets: list[str],              # ["vimeo", "r2", "youtube"]
    metadata: dict | None = None,
) -> dict[str, str]:
    """
    Distribuisce i video di una verticale su tutti i target richiesti.
    Ritorna mapping target→URL.

    targets: combinazione di "vimeo", "r2", "youtube"
    """
    output_dir = Path(output_dir)

    # Carica metadata se disponibile
    if metadata is None:
        meta_path = output_dir / "metadata.json"
        if meta_path.exists():
            metadata = json.loads(meta_path.read_text())
        else:
            metadata = {
                "yt_title": f"FLUXION — {verticale.title()} Demo",
                "yt_description": "FLUXION — gestionale desktop per PMI. €497 una volta.\nfluxion.app",
                "yt_tags": ["FLUXION", "gestionale", verticale],
                "vimeo_title": f"FLUXION — {verticale.title()} 30s",
            }

    # Trova i file video
    video_9x16 = output_dir / f"{verticale}_video_9x16.mp4"
    video_16x9 = output_dir / f"{verticale}_video_16x9.mp4"

    if not video_9x16.exists() and not video_16x9.exists():
        raise FileNotFoundError(
            f"Nessun video trovato in {output_dir}. "
            "Esegui prima: python run_all.py --vertical {verticale}"
        )

    urls = {}

    # ── Vimeo (usa 9:16 per WA Reels)
    if "vimeo" in targets and video_9x16.exists():
        try:
            url = upload_vimeo(
                video_path=video_9x16,
                title=metadata.get("vimeo_title", f"FLUXION {verticale}"),
                description=metadata.get("yt_description", ""),
                privacy="unlisted",
            )
            urls["vimeo_9x16"] = url
            logger.info(f"✓ Vimeo 9:16: {url}")
        except Exception as e:
            logger.error(f"Vimeo 9:16 upload fallito: {e}")

    if "vimeo" in targets and video_16x9.exists():
        try:
            url = upload_vimeo(
                video_path=video_16x9,
                title=f"{metadata.get('vimeo_title', 'FLUXION')} — 16:9",
                description=metadata.get("yt_description", ""),
                privacy="public",
            )
            urls["vimeo_16x9"] = url
        except Exception as e:
            logger.error(f"Vimeo 16:9 upload fallito: {e}")

    # ── Cloudflare R2 (CDN per link WA diretto)
    if "r2" in targets and video_9x16.exists():
        try:
            key = f"fluxion/{verticale}_9x16_v1.mp4"
            url = upload_r2(video_9x16, object_key=key)
            urls["r2_9x16"] = url
            logger.info(f"✓ R2 9:16: {url}")
        except Exception as e:
            logger.error(f"R2 upload fallito: {e}")

    # ── YouTube (usa 16:9)
    if "youtube" in targets and video_16x9.exists():
        try:
            url = upload_youtube(
                video_path=video_16x9,
                title=metadata.get("yt_title", f"FLUXION — {verticale}"),
                description=metadata.get("yt_description", ""),
                tags=metadata.get("yt_tags", ["FLUXION"]),
                privacy="public",
            )
            urls["youtube"] = url
            logger.info(f"✓ YouTube: {url}")
        except Exception as e:
            logger.error(f"YouTube upload fallito: {e}")

    # Salva URLs nel metadata
    if urls:
        metadata["video_urls"] = urls
        meta_path = output_dir / "metadata.json"
        meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

        # Aggiorna wa_message con URL reale
        _update_wa_message(output_dir, verticale, urls)

    return urls


def _update_wa_message(output_dir: Path, verticale: str, urls: dict) -> None:
    """Sostituisce [VIDEO_LINK] nel messaggio WA con l'URL reale."""
    wa_path = output_dir / "wa_message.txt"
    if not wa_path.exists():
        return

    # Priorità: R2 (diretto) > Vimeo (unlisted) > YouTube
    best_url = (
        urls.get("r2_9x16") or
        urls.get("vimeo_9x16") or
        urls.get("youtube") or
        ""
    )

    if not best_url:
        return

    content = wa_path.read_text()
    updated = content.replace("[VIDEO_LINK]", best_url)
    wa_path.write_text(updated)
    logger.info(f"WA message aggiornato con URL: {best_url}")

    # Genera anche i follow-up
    _generate_followup_messages(output_dir, verticale, best_url)


def _generate_followup_messages(
    output_dir: Path, verticale: str, video_url: str
) -> None:
    """Genera messaggi WA per Day 2, Day 5, Day 10."""
    from video_factory.script_generator import VERTICALI
    data = VERTICALI.get(verticale, {})
    label = data.get("label", verticale).lower()

    followups = {
        "wa_followup_d2.txt": (
            f"[nome], hai visto il video?\n\n"
            f"La parte con Sara che risponde è quella che cambia tutto.\n"
            f"€497. Una volta sola.\n"
            f"fluxion.app"
        ),
        "wa_followup_d5.txt": (
            f"[nome], ultima cosa.\n\n"
            f"Quanto paghi al mese per il gestionale?\n"
            f"Se è più di €14, FLUXION ti costa meno nel primo anno.\n"
            f"Puoi vederlo qui: fluxion.app"
        ),
        "wa_close_d10.txt": (
            f"[nome], chiudo qui.\n\n"
            f"FLUXION per {label} — €497, nessun abbonamento.\n"
            f"Se cambi idea: fluxion.app"
        ),
    }

    for filename, content in followups.items():
        path = output_dir / filename
        if not path.exists():
            path.write_text(content)
            logger.info(f"Follow-up generato: {filename}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="FLUXION Video Distributor")
    parser.add_argument("--vertical", nargs="+", required=True,
                        help="Verticale/i o 'all'")
    parser.add_argument("--targets", nargs="+", default=["r2", "vimeo"],
                        choices=["vimeo", "r2", "youtube"],
                        help="Target di distribuzione")
    parser.add_argument("--output-base", type=Path, default=Path("./output"))
    args = parser.parse_args()

    from video_factory.script_generator import VERTICALI

    targets_list = list(args.vertical)
    if "all" in targets_list:
        targets_list = list(VERTICALI.keys())

    all_urls = {}
    for v in targets_list:
        output_dir = args.output_base / v
        if not output_dir.exists():
            logger.warning(f"Directory non trovata: {output_dir} — skip")
            continue

        try:
            urls = distribute_video(v, output_dir, args.targets)
            all_urls[v] = urls
            print(f"\n✓ {v}:")
            for target, url in urls.items():
                print(f"  {target}: {url}")
        except Exception as e:
            logger.error(f"Errore distribuzione {v}: {e}")

    # Salva summary URLs
    summary_path = args.output_base / "video_urls.json"
    summary_path.write_text(json.dumps(all_urls, indent=2, ensure_ascii=False))
    print(f"\nURLs salvati: {summary_path}")
