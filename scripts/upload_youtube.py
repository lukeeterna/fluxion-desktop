#!/usr/bin/env python3
"""
FLUXION — YouTube Upload Script
Usa YouTube Data API v3 con resumable upload (immune a blocchi di connessione).

SETUP (una-tantum):
1. Vai su https://console.cloud.google.com
2. Abilita "YouTube Data API v3" nel progetto esistente
3. Crea credenziali OAuth 2.0 → Desktop app → Scarica JSON → salva come client_secrets.json in questa directory
4. Prima run: apre browser per autorizzazione → salva token in youtube_token.json (non serve più)

USO:
    python3 scripts/upload_youtube.py
    python3 scripts/upload_youtube.py --dry-run    # stampa metadata senza uploadare
"""

import json
import os
import sys
import time
import argparse

# ─── Percorsi ───────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

VIDEO_PATH = os.path.join(PROJECT_ROOT, "video-factory", "output", "landing", "landing_final_16x9.mp4")
THUMBNAIL_PATH = os.path.join(PROJECT_ROOT, "landing", "assets", "youtube-thumbnail-v8.png")
METADATA_PATH = os.path.join(PROJECT_ROOT, "landing", "assets", "youtube-metadata-v8.json")
CLIENT_SECRETS = os.path.join(SCRIPT_DIR, "client_secrets.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "youtube_token.json")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

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
            print("Refreshing token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS):
                print(f"""
ERROR: client_secrets.json non trovato in {CLIENT_SECRETS}

SETUP:
1. Vai su https://console.cloud.google.com
2. Abilita "YouTube Data API v3"
3. API & Services → Credentials → Create Credentials → OAuth 2.0 Client IDs
4. Application type: Desktop app
5. Scarica JSON → rinomina in client_secrets.json → metti in scripts/
""")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print(f"Token salvato: {TOKEN_FILE}")

    return creds


# ─── Upload ──────────────────────────────────────────────────────────────────

def upload_video(youtube, metadata: dict, video_path: str) -> str:
    from googleapiclient.http import MediaFileUpload

    file_size = os.path.getsize(video_path)
    print(f"\nVideo: {video_path}")
    print(f"Dimensione: {file_size / 1024 / 1024:.1f} MB")

    # Mappa category_id
    category_map = {"Science & Technology": "28", "Entertainment": "24", "How-to & Style": "26"}
    category_id = category_map.get(metadata.get("category", ""), "28")

    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("tags", []),
            "categoryId": category_id,
            "defaultLanguage": metadata.get("language", "it"),
            "defaultAudioLanguage": metadata.get("language", "it"),
        },
        "status": {
            "privacyStatus": metadata.get("privacy", "public"),
            "selfDeclaredMadeForKids": False,
        },
    }

    print(f"\nTitolo: {body['snippet']['title'][:60]}...")
    print(f"Privacy: {body['status']['privacyStatus']}")
    print(f"Tags: {len(body['snippet']['tags'])}")

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=4 * 1024 * 1024,  # 4MB chunks
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    print("\nUpload in corso...")
    response = None
    last_progress = -1

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                if progress != last_progress:
                    bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
                    print(f"\r  [{bar}] {progress}%", end="", flush=True)
                    last_progress = progress
        except Exception as e:
            print(f"\nChunk error (retry): {e}")
            time.sleep(5)

    print(f"\n\nUpload completato!")
    video_id = response["id"]
    print(f"Video ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    return video_id


def upload_thumbnail(youtube, video_id: str, thumbnail_path: str):
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(thumbnail_path):
        print(f"WARNING: Thumbnail non trovata: {thumbnail_path}")
        return

    print(f"\nUpload thumbnail: {thumbnail_path}")
    media = MediaFileUpload(thumbnail_path, mimetype="image/png")
    youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    print("Thumbnail caricata!")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FLUXION YouTube Uploader")
    parser.add_argument("--dry-run", action="store_true", help="Stampa metadata senza uploadare")
    parser.add_argument("--video", default=VIDEO_PATH, help="Path del video")
    parser.add_argument("--thumbnail", default=THUMBNAIL_PATH, help="Path thumbnail")
    parser.add_argument("--metadata", default=METADATA_PATH, help="Path JSON metadata")
    args = parser.parse_args()

    # Verifica file
    for path, name in [(args.video, "Video"), (args.metadata, "Metadata")]:
        if not os.path.exists(path):
            print(f"ERROR: {name} non trovato: {path}")
            sys.exit(1)

    with open(args.metadata) as f:
        metadata = json.load(f)

    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"Video:     {args.video} ({os.path.getsize(args.video)/1024/1024:.1f} MB)")
        print(f"Thumbnail: {args.thumbnail}")
        print(f"Titolo:    {metadata['title']}")
        print(f"Privacy:   {metadata.get('privacy', 'public')}")
        print(f"Tags:      {len(metadata.get('tags', []))}")
        print(f"Desc:      {len(metadata['description'])} chars")
        return

    # Auth
    print("Autenticazione Google...")
    creds = get_credentials()

    from googleapiclient.discovery import build
    youtube = build("youtube", "v3", credentials=creds)

    # Upload
    video_id = upload_video(youtube, metadata, args.video)
    upload_thumbnail(youtube, video_id, args.thumbnail)

    # Salva risultato
    result = {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "embed": f"https://www.youtube.com/embed/{video_id}",
        "uploaded_at": time.strftime("%Y-%m-%d %H:%M"),
    }
    result_path = os.path.join(SCRIPT_DIR, "youtube_upload_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n=== FATTO ===")
    print(f"URL:   {result['url']}")
    print(f"Embed: {result['embed']}")
    print(f"\nProssimo step: aggiorna landing con questo URL embed")
    print(f"Risultato salvato: {result_path}")


if __name__ == "__main__":
    main()
