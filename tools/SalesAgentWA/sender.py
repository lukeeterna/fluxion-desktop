"""
FLUXION Sales Agent WA — Playwright-based WhatsApp Web automation.
Anti-ban: delay gaussiano, variazione testo, orari business, pausa lunga ogni 5 msg.
Session persistence: profilo browser salvato in wa_session/ — QR login una volta sola.
"""
from __future__ import annotations

import time
import random
import logging
import sqlite3
import datetime
from typing import List, Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    sync_playwright = None
    PlaywrightTimeout = None

from config import (
    DB_PATH, WA_SESSION_DIR,
    DELAY_MEAN_S, DELAY_STD_S, DELAY_MIN_S, DELAY_MAX_S,
    LONG_PAUSE_EVERY, LONG_PAUSE_MIN_S, LONG_PAUSE_MAX_S,
    BUSINESS_HOURS,
)
from templates import render_template, estimate_variation
from utm import build_utm_youtube

logger = logging.getLogger(__name__)


def _is_business_hours() -> bool:
    """Controlla se siamo in orario operativo (lun-ven, 9-12 e 14-17 IT)."""
    now = datetime.datetime.now()
    if now.weekday() >= 5:
        return False
    h = now.hour
    morning = BUSINESS_HOURS["morning_start"] <= h < BUSINESS_HOURS["morning_end"]
    afternoon = BUSINESS_HOURS["afternoon_start"] <= h < BUSINESS_HOURS["afternoon_end"]
    return morning or afternoon


def _wait_until_business_hours():
    """Aspetta che siano orari operativi, loggando ogni 10 minuti."""
    while not _is_business_hours():
        now = datetime.datetime.now()
        logger.info("Fuori orario (%s) - aspetto...", now.strftime("%H:%M %a"))
        time.sleep(600)


def _random_delay():
    """Delay gaussiano tra messaggi."""
    delay = random.gauss(DELAY_MEAN_S, DELAY_STD_S)
    delay = max(DELAY_MIN_S, min(DELAY_MAX_S, delay))
    logger.info("  Delay: %.0fs", delay)
    time.sleep(delay)


def _long_pause():
    """Pausa lunga per simulare comportamento umano."""
    pause = random.uniform(LONG_PAUSE_MIN_S, LONG_PAUSE_MAX_S)
    logger.info("  Pausa lunga: %.0fs (%.1f min)", pause, pause / 60)
    time.sleep(pause)


def _get_daily_sent() -> int:
    """Conta messaggi inviati oggi."""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute(
        "SELECT sent FROM daily_stats WHERE date = ?", (today,)
    ).fetchone()
    conn.close()
    return row[0] if row else 0


def _increment_daily_stats(field: str):
    """Incrementa contatore nel daily_stats per oggi."""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO daily_stats (date, {f}) VALUES (?, 1) "
        "ON CONFLICT(date) DO UPDATE SET {f} = {f} + 1".format(f=field),
        (today,),
    )
    conn.commit()
    conn.close()


def _get_pending_leads(limit: int, category: Optional[str] = None) -> List[dict]:
    """Recupera lead pendenti con numero WA valido, non ancora contattati."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    query = """
        SELECT l.id, l.business_name, l.phone, l.city, l.category
        FROM leads l
        WHERE l.phone IS NOT NULL
          AND l.wa_registered IS NOT 0
          AND NOT EXISTS (
              SELECT 1 FROM messages m
              WHERE m.lead_id = l.id
                AND m.status IN ('sent', 'delivered', 'read', 'replied')
          )
    """
    params = []  # type: List
    if category:
        query += " AND l.category = ?"
        params.append(category)
    query += " ORDER BY l.google_rating DESC NULLS LAST LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _save_message(
    lead_id: int,
    template_key: str,
    message_text: str,
    utm_url: str,
    status: str,
    error_msg: Optional[str] = None,
):
    conn = sqlite3.connect(str(DB_PATH))
    sent_at = datetime.datetime.now().isoformat() if status == "sent" else None
    conn.execute("""
        INSERT INTO messages (
            lead_id, template_key, message_text, utm_url,
            status, sent_at, error_msg
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (lead_id, template_key, message_text, utm_url, status, sent_at, error_msg))
    conn.commit()
    conn.close()


def _send_single_message(page, phone: str, message: str) -> bool:
    """Invia un messaggio WhatsApp tramite wa.me deep link."""
    phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    wa_url = "https://web.whatsapp.com/send?phone={}".format(phone_clean)

    try:
        page.goto(wa_url, wait_until="domcontentloaded", timeout=30000)

        try:
            page.wait_for_selector(
                'div[data-testid="conversation-panel-wrapper"]',
                timeout=15000,
            )
        except PlaywrightTimeout:
            logger.warning("  %s: numero non su WhatsApp", phone)
            return False

        # Controlla popup "numero non su WA"
        invalid_selectors = [
            'div[data-testid="confirm-popup"]',
            'div[data-icon="alert-circle"]',
        ]
        for sel in invalid_selectors:
            if page.locator(sel).count() > 0:
                logger.warning("  %s: WA mostra numero non valido", phone)
                return False

        # Trova la text box e scrivi il messaggio
        box = page.locator('div[data-testid="conversation-compose-box-input"]')
        box.wait_for(state="visible", timeout=10000)
        box.click()

        # Digita con pause simulate (anti-bot)
        for chunk in _chunk_text(message):
            box.type(chunk, delay=random.randint(20, 60))
            time.sleep(random.uniform(0.1, 0.3))

        time.sleep(random.uniform(0.5, 1.5))

        # Invia
        send_btn = page.locator('button[data-testid="compose-btn-send"]')
        send_btn.wait_for(state="visible", timeout=5000)
        send_btn.click()

        time.sleep(2)
        logger.info("  INVIATO: %s", phone)
        return True

    except PlaywrightTimeout as e:
        logger.error("  TIMEOUT %s: %s", phone, e)
        return False
    except Exception as e:
        logger.error("  ERRORE %s: %s", phone, e)
        return False


def _chunk_text(text: str, max_chunk: int = 50) -> List[str]:
    """Spezza il testo in chunk per digitazione simulata."""
    chunks = []
    words = text.split(" ")
    current = ""
    for word in words:
        if len(current) + len(word) > max_chunk:
            if current:
                chunks.append(current)
            current = word + " "
        else:
            current += word + " "
    if current:
        chunks.append(current)
    return chunks


def run_sender(
    daily_limit: int,
    category: Optional[str] = None,
    dry_run: bool = False,
):
    """
    Ciclo principale di invio messaggi.
    - dry_run=True: prepara messaggi ma non li invia (test)
    - Rispetta orari business, daily limit, rate limiting
    """
    sent_today = _get_daily_sent()
    remaining = daily_limit - sent_today

    if remaining <= 0:
        logger.info("Limite giornaliero raggiunto (%d). A domani.", daily_limit)
        return

    logger.info("=== Sales Agent WA - %d messaggi da inviare ===", remaining)

    leads = _get_pending_leads(remaining + 10, category)
    if not leads:
        logger.info("Nessun lead pendente. Aggiungi lead con 'scrape'.")
        return

    logger.info("Lead disponibili: %d", len(leads))

    if dry_run:
        logger.info("=== DRY RUN - nessun messaggio inviato ===")
        for lead in leads[:5]:
            msg, key = render_template(lead["category"], lead["business_name"], lead["city"])
            print("\n--- {} ({}) ---".format(lead["business_name"], lead["phone"]))
            print(msg)
        return

    # Attendi orari operativi prima di inviare
    _wait_until_business_hours()

    if sync_playwright is None:
        logger.error("Playwright non installato. Installa con: pip3 install playwright && python3 -m playwright install chromium")
        return

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

        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

        logger.info("Attendo login WhatsApp Web (max 60s)...")
        try:
            page.wait_for_selector(
                'div[data-testid="default-user"],'
                'div[data-testid="chatlist-header"],'
                '#side',
                timeout=60000,
            )
            logger.info("Login WA OK")
        except PlaywrightTimeout:
            logger.error("Login WA fallito - scansiona il QR code dalla finestra del browser")
            browser.close()
            return

        last_messages = []  # type: List[str]
        sent_count = 0

        for lead in leads:
            if sent_count >= remaining:
                break

            if not _is_business_hours():
                logger.info("Uscito dagli orari operativi - fermo per oggi")
                break

            phone = lead["phone"]
            if not phone:
                continue

            # Genera messaggio con variazione garantita
            attempts = 0
            while True:
                msg, key = render_template(
                    lead["category"],
                    lead["business_name"],
                    lead["city"],
                )
                if not last_messages:
                    break
                variation = estimate_variation(msg, last_messages[-1])
                if variation >= 0.40 or attempts >= 5:
                    break
                attempts += 1

            utm_url = build_utm_youtube(lead["category"], lead["city"])

            logger.info("[%d/%d] %s (%s)", sent_count + 1, remaining,
                        lead["business_name"], phone)

            success = _send_single_message(page, phone, msg)

            if success:
                _save_message(lead["id"], key, msg, utm_url, "sent")
                _increment_daily_stats("sent")
                last_messages.append(msg)
                if len(last_messages) > 5:
                    last_messages.pop(0)
                sent_count += 1

                if sent_count % LONG_PAUSE_EVERY == 0:
                    _long_pause()
                else:
                    _random_delay()
            else:
                _save_message(lead["id"], key, msg, utm_url, "failed",
                              error_msg="WA not registered or timeout")
                conn = sqlite3.connect(str(DB_PATH))
                conn.execute(
                    "UPDATE leads SET wa_registered = 0 WHERE id = ?",
                    (lead["id"],)
                )
                conn.commit()
                conn.close()
                time.sleep(5)

        logger.info("=== Fine invio: %d messaggi inviati ===", sent_count)
        browser.close()
