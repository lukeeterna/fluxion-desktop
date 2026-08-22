#!/usr/bin/env python3
"""Run an exact-SHA Sara HTTP certification server without external side effects.

This launcher is for the release gate only. It loads the same Voice Agent entry
point and business environment as production, but deliberately disables the two
integrations that can create external effects while an isolated candidate is
being exercised in parallel with the live iMac service:

* SIP/VoIP registration (the real EHIWEB call gate is a separate certification);
* WhatsApp auto-start/reminder scheduling.

NLU, FSM, RAG, TTS, database access and the HTTP API are the production code from
the candidate worktree. The caller must pass an explicit env file and candidate
SHA; the shell gate independently proves that the worktree HEAD matches that SHA.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FLUXION exact-SHA Sara certification server")
    parser.add_argument("--env-file", required=True, help="Existing trusted local .env file")
    parser.add_argument("--sha", required=True, help="Candidate commit SHA for evidence logging")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3102)
    return parser.parse_args()


def _load_trusted_env(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"CERT_BLOCKED: env file not found: {path}")
    from dotenv import dotenv_values

    for key, value in dotenv_values(path).items():
        if key and value is not None:
            os.environ[key] = value

    # Exact-SHA HTTP certification must not register a second SIP endpoint.
    os.environ["VOIP_SIP_USER"] = ""
    os.environ["FLUXION_CERT_MODE"] = "1"


class _NoopWhatsAppClient:
    """Minimal side-effect-free stand-in used only by this certification launcher."""

    def __init__(self, *args, **kwargs):
        self.config = type("CertWhatsAppConfig", (), {})()

    def is_connected(self) -> bool:
        # Returning True prevents main.py from spawning whatsapp-service.cjs.
        return True

    def __getattr__(self, name):
        if name.startswith("send"):
            def _disabled(*args, **kwargs):
                return False
            return _disabled
        raise AttributeError(name)


def main() -> int:
    args = _parse_args()
    env_file = Path(args.env_file).expanduser().resolve()
    _load_trusted_env(env_file)

    voice_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(voice_root))

    # Import only after the trusted environment is loaded.
    import main as voice_main
    import src.whatsapp as whatsapp_module

    whatsapp_module.WhatsAppClient = _NoopWhatsAppClient
    voice_main.start_reminder_scheduler = lambda *args, **kwargs: None

    print(
        f"CERT_SERVER_START sha={args.sha} host={args.host} port={args.port} "
        "voip=disabled whatsapp=disabled",
        flush=True,
    )
    asyncio.run(voice_main.main(None, args.port, args.host))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
