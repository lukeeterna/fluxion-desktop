# replies.py
"""
Classifica le risposte loggate dal monitor e instrada:
- hot      -> coda handoff (rispondi TU, demo)
- risk     -> do_not_contact=1 + alert (chi chiede "come hai il mio numero" va soppresso subito)
- negative -> do_not_contact=1, nessuna azione
- other    -> coda handoff (review manuale)
Deterministico, zero API (G-NOAPI-AI).
"""
import re
import sqlite3
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)

# Ordine di controllo: RISK -> NEGATIVE -> HOT -> OTHER
RISK = [
    "come hai avuto", "come hai preso", "dove hai preso", "chi ti ha dato",
    "come fai ad avere", "da dove hai", "numero da dove", "spam",
    "ti segnalo", "segnalo", "denuncio", "querela", "garante", "avvocato",
]
NEGATIVE = [
    "non mi interessa", "non interessa", "no grazie", "non sono interessat",
    "stop", "basta", "smettila", "lasciami", "non scrivetemi", "non scrivermi",
    "toglietemi", "toglimi", "rimuovi", "cancellami", "non voglio",
]
HOT = [
    "quanto costa", "quanto viene", "prezzo", "costo", "come funziona",
    "demo", "fammi vedere", "vorrei vedere", "mi interessa", "interessato",
    "interessata", "info", "informazioni", "dettagli", "quando", "prova",
    "va bene", "ok ", "ok,", "si mi", "sì mi", "mi piacerebbe",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def classify(reply_text: str) -> str:
    t = _normalize(reply_text)
    if not t:
        return "other"
    if any(p in t for p in RISK):
        return "risk"
    if any(p in t for p in NEGATIVE):
        return "negative"
    if any(p in t for p in HOT):
        return "hot"
    return "other"


def process_new_replies() -> dict:
    """
    Scansiona i messaggi con status='replied' non ancora classificati,
    assegna intent e instrada. Ritorna conteggi.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT m.id, m.lead_id, m.reply_text, l.business_name, l.phone, l.city
        FROM messages m JOIN leads l ON l.id = m.lead_id
        WHERE m.status = 'replied' AND m.reply_intent IS NULL
    """).fetchall()

    counts = {"hot": 0, "negative": 0, "risk": 0, "other": 0}
    alerts = []

    for r in rows:
        intent = classify(r["reply_text"])
        counts[intent] += 1

        if intent in ("hot", "other"):
            conn.execute(
                "UPDATE messages SET reply_intent=?, handoff_status='queued' WHERE id=?",
                (intent, r["id"]),
            )
            alerts.append((intent, dict(r)))
        elif intent == "negative":
            conn.execute("UPDATE messages SET reply_intent=? WHERE id=?", (intent, r["id"]))
            conn.execute("UPDATE leads SET do_not_contact=1 WHERE id=?", (r["lead_id"],))
        elif intent == "risk":
            conn.execute("UPDATE messages SET reply_intent=?, handoff_status='queued' WHERE id=?",
                         (intent, r["id"]))
            conn.execute("UPDATE leads SET do_not_contact=1 WHERE id=?", (r["lead_id"],))
            alerts.append(("risk", dict(r)))

    conn.commit()
    conn.close()

    if alerts:
        from handoff import notify_batch
        notify_batch(alerts)

    logger.info(f"Replies processate: {counts}")
    return counts
