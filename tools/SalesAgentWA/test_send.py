"""Test invio WA al numero del fondatore — eseguire dall'iMac."""
from sender import _send_single_message
from templates import render_template
from playwright.sync_api import sync_playwright
import time

phone = "+393807769822"
msg, key = render_template("parrucchiere", "Test Salone Gianluca", "Milano")
print("Messaggio:")
print(msg)
print()
print("Apro WhatsApp Web in Chromium separato...")
print("Scansiona il QR code col telefono (WhatsApp > Dispositivi collegati)")
print()

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="wa_session",
        headless=False,
        viewport={"width": 1280, "height": 900},
        args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
    print("Attendo login (max 120s)...")
    page.wait_for_selector("#side", timeout=120000)
    print("Login OK! Invio messaggio...")
    time.sleep(3)
    ok = _send_single_message(page, phone, msg)
    print("RISULTATO:", "INVIATO" if ok else "FALLITO")
    time.sleep(5)
    browser.close()
