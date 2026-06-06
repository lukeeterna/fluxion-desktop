# checkout.py
"""
Genera il link di checkout REALE (fluxion-app.com), non la pages.dev,
con client_reference_id=lead_<id> per attribuire la conversione al lead.
NB: i due payment link LIVE (Base €497, Pro €897) li metti tu.
Conferma client_reference_id sui Payment Link nei docs Stripe prima del go-live.
"""
from urllib.parse import urlencode

# <-- INSERISCI I TUOI PAYMENT LINK LIVE REALI -->
PAYMENT_LINKS = {
    "base": "https://buy.stripe.com/XXXXXXXX_BASE_497",   # €497
    "pro":  "https://buy.stripe.com/XXXXXXXX_PRO_897",     # €897
}


def build_checkout_link(lead_id: int, plan: str = "base",
                        category: str = "", city: str = "") -> str:
    base = PAYMENT_LINKS.get(plan, PAYMENT_LINKS["base"])
    params = {
        "client_reference_id": f"lead_{lead_id}",   # ritorna nel webhook -> attribuzione
        "utm_source": "wa", "utm_campaign": category,
        "utm_content": (city or "").lower().replace(" ", "_"),
    }
    sep = "&" if "?" in base else "?"
    return base + sep + urlencode(params)
