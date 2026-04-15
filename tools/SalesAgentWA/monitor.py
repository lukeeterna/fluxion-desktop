"""
FLUXION Sales Agent WA — Reply Monitor.
Scansiona WhatsApp Web per rispote ai messaggi inviati.
Aggiorna leads.db quando un lead risponde.

Approccio: navigazione diretta su ogni chat (no dipendenza dalla lista chat)
wa.me/send?phone=XXXXX → legge ultimo messaggio in arrivo.

Usage:
  python3 agent.py monitor          # una scansione e termina
  python3 agent.py monitor --loop   # loop ogni 15 minuti (daemon)
"""
from __future__ import annotations

import datetime
import logging
import re
import sqlite3
import time
from typing import Dict, List, Optional, Set

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    sync_playwright = None
    PlaywrightTimeout = None

from config import DB_PATH, WA_SESSION_DIR

logger = logging.getLogger(__name__)

MONITOR_INTERVAL_S = 900  # 15 minuti


def _load_sent_phones() -> Dict[str, int]:
    """Ritorna {phone_clean: lead_id} per tutti i lead a cui abbiamo inviato."""
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("""
        SELECT DISTINCT l.phone, l.id
        FROM leads l
        JOIN messages m ON m.lead_id = l.id
        WHERE m.status IN ('sent', 'delivered', 'read')
          AND l.phone IS NOT NULL
    """).fetchall()
    conn.close()
    result = {}
    for phone, lead_id in rows:
        clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        result[clean] = lead_id
    return result


def _update_reply(lead_id: int, reply_text: str):
    """Segna il messaggio come 'replied' e salva il testo della risposta."""
    conn = sqlite3.connect(str(DB_PATH))
    now = datetime.datetime.now().isoformat()
    conn.execute("""
        UPDATE messages
        SET status = 'replied',
            replied_at = ?,
            reply_text = ?
        WHERE lead_id = ?
          AND status IN ('sent', 'delivered', 'read')
        ORDER BY created_at DESC
        LIMIT 1
    """, (now, reply_text, lead_id))
    conn.execute("""
        INSERT INTO daily_stats (date, replied)
        VALUES (?, 1)
        ON CONFLICT(date) DO UPDATE SET replied = replied + 1
    """, (datetime.date.today().isoformat(),))
    conn.commit()
    conn.close()
    logger.info("  RISPOSTA salvata - lead_id=%d: %s", lead_id, reply_text[:80])


def _get_already_replied_ids() -> Set[int]:
    """ID di lead che hanno gia' status=replied."""
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("""
        SELECT DISTINCT lead_id FROM messages WHERE status = 'replied'
    """).fetchall()
    conn.close()
    return {r[0] for r in rows}


def _get_outgoing_text(lead_id: int) -> str:
    """Recupera il testo del messaggio che abbiamo inviato a questo lead."""
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute("""
        SELECT message_text FROM messages
        WHERE lead_id = ? AND status IN ('sent', 'delivered', 'read')
        ORDER BY created_at DESC LIMIT 1
    """, (lead_id,)).fetchone()
    conn.close()
    return (row[0] or "").strip()[:100] if row else ""


def _check_chat_for_reply(page, phone: str, lead_id: int) -> Optional[str]:
    """
    Apre la chat di un numero specifico e verifica se c'è una risposta.
    Ritorna il testo della risposta, o None se nessuna risposta.
    """
    url = f"https://web.whatsapp.com/send?phone={phone}&app_absent=0"
    try:
        page.goto(url, wait_until="domcontentloaded")

        # Attendi che la chat si apra (non il popup "non su WA")
        # Selector per il pannello messaggi principale
        try:
            page.wait_for_selector(
                'div[data-testid="conversation-panel-messages"],'
                'div[data-testid="msg-container"],'
                'div[class*="message-list"],'
                '#main div[role="application"],'
                '#main',
                timeout=12000,
            )
        except Exception:
            logger.debug("  Phone %s — chat non aperta (timeout)", phone)
            return None

        time.sleep(2)  # WA Web carica i messaggi in modo asincrono

        # Verifica che non sia il popup "numero non su WA"
        # (appare come dialog o popup)
        invalid_selectors = [
            'div[data-testid="popup-contents"]',
            'span[data-testid="phonecountry-invalid"]',
        ]
        for sel in invalid_selectors:
            if page.locator(sel).count() > 0:
                # Chiudi il popup e vai avanti
                page.keyboard.press("Escape")
                logger.debug("  Phone %s — non su WA (popup)", phone)
                return None

        # Cerca i messaggi in ARRIVO (incoming) nella chat
        # In WA Web, messaggi in arrivo hanno class "message-in" o data-testid diverso
        # dall'outgoing "message-out"
        incoming_selectors = [
            'div[data-testid="msg-container"] div[class*="message-in"]',
            'div[class*="message-in"]',
            'div[data-testid="msg-container"][class*="in"]',
        ]

        incoming_messages = None
        for sel in incoming_selectors:
            msgs = page.locator(sel).all()
            if msgs:
                incoming_messages = msgs
                break

        if not incoming_messages:
            # Fallback: cerca tutti i messaggi e filtra per posizione
            # I messaggi in arrivo di solito sono allineati a sinistra
            all_msgs = page.locator(
                'div[data-testid="msg-container"]'
            ).all()
            # Prendi solo quelli con class che contiene "in" ma non "out"
            incoming_messages = []
            for msg in all_msgs:
                try:
                    cls = msg.get_attribute("class") or ""
                    if "message-in" in cls or ("in" in cls and "out" not in cls):
                        incoming_messages.append(msg)
                except Exception:
                    pass

        if not incoming_messages:
            logger.debug("  Phone %s — nessun messaggio in arrivo", phone)
            return None

        # Prendi l'ultimo messaggio in arrivo
        last_incoming = incoming_messages[-1]
        try:
            # Cerca il testo del messaggio
            text_el = last_incoming.locator(
                'span[data-testid="msg-container"] span,'
                'div[class*="copyable-text"] span,'
                'span.selectable-text,'
                'div[class*="message-body"]'
            ).first
            if text_el.count() > 0:
                reply_text = text_el.inner_text().strip()
            else:
                reply_text = last_incoming.inner_text().strip()

            # Filtra righe vuote e metadata WA (orari, emoji status)
            lines = [l.strip() for l in reply_text.splitlines() if l.strip()]
            lines = [l for l in lines if not re.match(r'^\d{1,2}:\d{2}$', l)]
            reply_text = " ".join(lines[:5])[:500]

            if reply_text:
                logger.info("  Phone %s — risposta trovata: %s", phone, reply_text[:80])
                return reply_text

        except Exception as e:
            logger.debug("  Phone %s — errore lettura testo: %s", phone, e)

        return None

    except Exception as e:
        logger.error("  Phone %s — errore check_chat: %s", phone, e)
        return None


def _scan_replies_once(page, sent_phones: Dict[str, int], already_replied: Set[int]) -> int:
    """
    Verifica ogni chat dei lead contattati per nuove risposte.
    Approccio diretto: naviga su ogni chat individualmente (no lista chat).
    Ritorna il numero di nuove risposte trovate.
    """
    new_replies = 0
    pending = {phone: lead_id for phone, lead_id in sent_phones.items()
               if lead_id not in already_replied}

    logger.info("Verifica %d chat (esclusi %d gia' risposti)...",
                len(pending), len(already_replied))

    for phone, lead_id in pending.items():
        logger.debug("  Verifico phone %s (lead_id=%d)...", phone, lead_id)
        reply = _check_chat_for_reply(page, phone, lead_id)
        if reply:
            _update_reply(lead_id, reply)
            already_replied.add(lead_id)
            new_replies += 1
        time.sleep(1.5)  # pausa tra chat per non stressare WA Web

    return new_replies


def run_monitor(loop: bool = False):
    """
    Apre WA Web e scansiona le chat per risposte ai nostri lead.
    loop=True: ripete ogni MONITOR_INTERVAL_S secondi.
    """
    if sync_playwright is None:
        logger.error("Playwright non installato.")
        return

    sent_phones = _load_sent_phones()
    if not sent_phones:
        logger.info("Nessun messaggio inviato ancora — monitor non ha nulla da fare.")
        return

    already_replied = _get_already_replied_ids()
    logger.info("Monitor: %d lead contattati, %d gia' rispondenti",
                len(sent_phones), len(already_replied))

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(WA_SESSION_DIR),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        # Login check — vai alla home e aspetta la sidebar
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
        logger.info("Attendo login WA (max 60s)...")
        try:
            page.wait_for_selector(
                'div[data-testid="default-user"],'
                'div[data-testid="chatlist-header"],'
                '#side',
                timeout=60000,
            )
            logger.info("Login WA OK")
        except Exception:
            logger.error("Login WA fallito — scansiona QR")
            browser.close()
            return

        # Attendi che WA Web finisca il caricamento completo
        time.sleep(4)

        while True:
            logger.info("=== Monitor scan: %s ===",
                        datetime.datetime.now().strftime("%H:%M"))
            n = _scan_replies_once(page, sent_phones, already_replied)
            logger.info("Scan completato: %d nuove risposte", n)

            if not loop:
                break

            logger.info("Prossima scan tra %ds...", MONITOR_INTERVAL_S)
            time.sleep(MONITOR_INTERVAL_S)

        browser.close()
