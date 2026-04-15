"""
FLUXION Sales Agent WA — Reply Monitor.
Scansiona WhatsApp Web per rispote ai messaggi inviati.
Aggiorna leads.db quando un lead risponde.

Usage:
  python3 agent.py monitor          # una scansione e termina
  python3 agent.py monitor --loop   # loop ogni 15 minuti (daemon)
"""
from __future__ import annotations

import datetime
import logging
import sqlite3
import time
from typing import Dict, List, Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    sync_playwright = None
    PlaywrightTimeout = None

from config import DB_PATH, WA_SESSION_DIR

logger = logging.getLogger(__name__)

MONITOR_INTERVAL_S = 900  # 15 minuti


def _load_sent_phones() -> Dict[str, int]:
    """
    Ritorna {phone_clean: lead_id} per tutti i lead a cui abbiamo inviato.
    phone_clean: solo cifre, senza + o spazi.
    """
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


def _get_already_replied_ids() -> set:
    """ID di lead che hanno gia' status=replied."""
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("""
        SELECT DISTINCT lead_id FROM messages WHERE status = 'replied'
    """).fetchall()
    conn.close()
    return {r[0] for r in rows}


def _scan_replies_once(page, sent_phones: Dict[str, int], already_replied: set) -> int:
    """
    Scansiona la lista chat WA Web per nuove risposte.
    Ritorna il numero di nuove risposte trovate.
    """
    try:
        # Vai alla home WA Web
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
        time.sleep(3)

        # Attendi lista chat
        try:
            page.wait_for_selector(
                '#side div[data-testid="chat-list"],'
                '#pane-side,'
                'div[aria-label="Lista chat"]',
                timeout=30000,
            )
        except Exception:
            logger.warning("Lista chat non trovata — WA ancora in caricamento?")
            return 0

        time.sleep(2)

        # Recupera tutti i chat item visibili
        # In WA Web i chat con messaggi non letti hanno un badge
        new_replies = 0

        # Cerca chat con badge di messaggi non letti
        unread_selectors = [
            'div[data-testid="cell-frame-container"][aria-selected]',
            'div[aria-label*="non letti"]',
            'span[data-testid="icon-unread-count"]',
            'div[data-testid="unread-count"]',
        ]

        # Approccio alternativo: scansiona tutti i chat item
        chat_items = page.locator(
            '#pane-side div[data-testid="cell-frame-container"],'
            '#side div[data-testid="cell-frame-container"],'
            'div[class*="chat-item"]'
        ).all()

        if not chat_items:
            # Fallback: cerca per struttura DOM
            chat_items = page.locator('div[role="listitem"]').all()

        logger.info("Chat items trovati: %d", len(chat_items))

        for item in chat_items:
            try:
                # Cerca badge di messaggi non letti
                has_unread = (
                    item.locator('span[data-testid="icon-unread-count"]').count() > 0 or
                    item.locator('div[data-testid="unread-count"]').count() > 0 or
                    item.locator('[class*="unread"]').count() > 0
                )
                if not has_unread:
                    continue

                # Estrai numero di telefono dall'aria-label o dal testo
                phone_text = ""
                aria = item.get_attribute("aria-label") or ""
                if aria:
                    # aria-label spesso contiene nome/numero
                    phone_text = aria

                # Clicca sulla chat per aprirla e vedere il numero
                item.click()
                time.sleep(1.5)

                # Prova a leggere il numero dal pannello info contatto
                # In WA Web il numero e' visibile nell'header della chat
                header = page.locator(
                    'header[data-testid="conversation-header"],'
                    'div[data-testid="conversation-panel-header"],'
                    '#main header'
                ).first
                if header.count() == 0:
                    continue

                # Il numero e' spesso nell'header come span con cifre
                header_text = header.inner_text() or ""
                # Cerca pattern numero italiano
                import re
                phone_matches = re.findall(r'[\+]?[0-9]{8,15}', header_text.replace(" ", ""))

                phone_clean = ""
                if phone_matches:
                    phone_clean = phone_matches[0].lstrip("+")
                else:
                    # Prova click su header per aprire info contatto
                    try:
                        header.click()
                        time.sleep(1)
                        info_panel = page.locator(
                            'div[data-testid="drawer-right"],'
                            'div[data-testid="contact-info"]'
                        ).first
                        if info_panel.count() > 0:
                            info_text = info_panel.inner_text()
                            phone_matches = re.findall(r'[\+]?[0-9]{8,15}', info_text.replace(" ", ""))
                            if phone_matches:
                                phone_clean = phone_matches[0].lstrip("+")
                        # Chiudi pannello info
                        page.keyboard.press("Escape")
                        time.sleep(0.5)
                    except Exception:
                        pass

                if not phone_clean or phone_clean not in sent_phones:
                    # Prova con prefisso 39
                    for p in list(sent_phones.keys()):
                        if phone_clean and (p.endswith(phone_clean) or phone_clean.endswith(p)):
                            phone_clean = p
                            break

                if phone_clean not in sent_phones:
                    continue

                lead_id = sent_phones[phone_clean]
                if lead_id in already_replied:
                    continue

                # Leggi l'ultimo messaggio ricevuto
                messages_container = page.locator(
                    'div[data-testid="msg-container"],'
                    'div[class*="message-in"]'
                ).last
                reply_text = ""
                if messages_container.count() > 0:
                    try:
                        reply_text = messages_container.inner_text() or ""
                        reply_text = reply_text.strip()[:500]
                    except Exception:
                        reply_text = "(messaggio non leggibile)"

                if not reply_text:
                    reply_text = "(risposta WA)"

                _update_reply(lead_id, reply_text)
                already_replied.add(lead_id)
                new_replies += 1
                logger.info("NUOVA RISPOSTA da %s: %s", phone_clean, reply_text[:60])

            except Exception as e:
                logger.debug("Errore su chat item: %s", e)
                continue

        return new_replies

    except Exception as e:
        logger.error("Errore scan_replies_once: %s", e)
        return 0


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
    logger.info("Monitor: %d lead contattati, %d gia' rispondenti", len(sent_phones), len(already_replied))

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

        # Login check
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

        while True:
            logger.info("=== Monitor scan: %s ===", datetime.datetime.now().strftime("%H:%M"))
            n = _scan_replies_once(page, sent_phones, already_replied)
            logger.info("Scan completato: %d nuove risposte", n)

            if not loop:
                break

            logger.info("Prossima scan tra %ds...", MONITOR_INTERVAL_S)
            time.sleep(MONITOR_INTERVAL_S)

        browser.close()
