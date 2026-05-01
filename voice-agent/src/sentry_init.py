"""
FLUXION Voice Agent — Sentry Crash Reporter (S184 α.1.4)

No-op silenzioso se SENTRY_DSN_PYTHON assente.
PII filter mandatory: scrub campi cliente italiani prima dell'invio.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("fluxion.voice.sentry")

# Campi sensibili da redactare (GDPR + zero data leak)
_SENSITIVE_KEYS = frozenset(
    {
        "cliente",
        "cliente_id",
        "telefono",
        "email",
        "codice_fiscale",
        "partita_iva",
        "indirizzo",
        "nome",
        "cognome",
        "soprannome",
        "data_nascita",
        "xml_sdi",
        "fattura",
        "license_key",
        "stripe_payment_intent",
        "transcript",  # Audio trascritto può contenere nomi clienti
        "user_text",
    }
)


def _scrub(obj: Any) -> Any:
    """Scrub PII ricorsivamente da dict/list."""
    if isinstance(obj, dict):
        result: dict[str, Any] = {}
        for k, v in obj.items():
            lower = str(k).lower()
            if any(s in lower for s in _SENSITIVE_KEYS):
                result[k] = "[REDACTED]"
            else:
                result[k] = _scrub(v)
        return result
    if isinstance(obj, list):
        return [_scrub(x) for x in obj]
    return obj


def _before_send(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any] | None:
    """Hook Sentry: scrub PII + filtra eventi non azionabili."""
    # Scrub extra/contexts/breadcrumbs
    for key in ("extra", "contexts", "tags"):
        if key in event:
            event[key] = _scrub(event[key])
    if "breadcrumbs" in event and isinstance(event["breadcrumbs"], dict):
        values = event["breadcrumbs"].get("values", [])
        for bc in values:
            if isinstance(bc, dict) and "data" in bc:
                bc["data"] = _scrub(bc["data"])
    # Rimuovi user info (Sentry default include IP)
    event.pop("user", None)
    return event


def init_sentry() -> bool:
    """Inizializza Sentry SDK. Ritorna True se attivo, False altrimenti."""
    dsn = os.environ.get("SENTRY_DSN_PYTHON", "").strip()
    if not dsn:
        logger.info("Sentry DSN non configurato — crash reporter disabilitato")
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.aiohttp import AioHttpIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError as e:
        logger.warning("sentry-sdk non installato (%s) — crash reporter disabilitato", e)
        return False

    # Read version from voice-agent (fallback se PyInstaller frozen)
    version = os.environ.get("FLUXION_VERSION", "1.0.1")

    sentry_sdk.init(
        dsn=dsn,
        release=f"fluxion-voice@{version}",
        environment=os.environ.get("FLUXION_ENV", "production"),
        traces_sample_rate=0.0,
        send_default_pii=False,  # Mandatory GDPR
        attach_stacktrace=True,
        max_breadcrumbs=50,
        integrations=[
            AioHttpIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        before_send=_before_send,
        ignore_errors=[
            "KeyboardInterrupt",
            "SystemExit",
        ],
    )
    logger.info("✅ Sentry crash reporter initialized (Python)")
    return True
