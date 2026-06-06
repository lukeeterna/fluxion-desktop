# handoff.py
"""
Handoff a umano. Canale: notifica macOS nativa (zero infra) + coda in dashboard.
NON usa il bot Telegram ARGOS. Per push, crea un bot Telegram SEPARATO per FLUXION.
"""
import subprocess
import logging

logger = logging.getLogger(__name__)


def _macos_notify(title: str, message: str):
    """Notifica nativa macOS via osascript (nessuna dipendenza)."""
    try:
        safe = message.replace('"', "'")
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{safe}" with title "{title}" sound name "Glass"'],
            check=False, timeout=5,
        )
    except Exception as e:
        logger.warning(f"Notifica macOS fallita: {e}")


def notify_batch(alerts: list):
    hot = [a for a in alerts if a[0] == "hot"]
    risk = [a for a in alerts if a[0] == "risk"]
    other = [a for a in alerts if a[0] == "other"]

    if hot:
        names = ", ".join(a[1]["business_name"] for a in hot[:3])
        _macos_notify(f"FLUXION — {len(hot)} risposte CALDE",
                      f"Rispondi tu: {names}. Apri dashboard.")
    if risk:
        _macos_notify(f"FLUXION — {len(risk)} alert",
                      "Contatti che chiedono dei dati: soppressi + da gestire a mano.")
    if other:
        _macos_notify(f"FLUXION — {len(other)} risposte da rivedere", "Apri dashboard.")

    # OPZIONALE: push su Telegram FLUXION (bot separato, non ARGOS)
    # send_telegram(f"{len(hot)} caldi, {len(risk)} alert, {len(other)} review")


def claim(message_id: int):
    """Segna la conversazione come presa in carico da te: l'automazione non risponde più."""
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE messages SET handoff_status='claimed' WHERE id=?", (message_id,))
    conn.commit()
    conn.close()
