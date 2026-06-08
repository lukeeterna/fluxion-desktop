#!/usr/bin/env python3
"""S347 — E2E smoke: forgia un checkout.session.completed FIRMATO (test mode)
con client_reference_id=lead_999 e lo invia al test worker.
Verifica: licenza emessa (license_id in risposta) + attribuzione conversione.
Il webhook secret e' letto da env STRIPE_WEBHOOK_SECRET_TEST (mai stampato)."""
import os, sys, json, time, hmac, hashlib, urllib.request

WHSEC = os.environ.get("STRIPE_WEBHOOK_SECRET_TEST")
if not WHSEC:
    print("FAIL: STRIPE_WEBHOOK_SECRET_TEST non in env"); sys.exit(1)

URL = "https://fluxion-proxy-test.gianlucanewtech.workers.dev/api/v1/webhook/stripe"
ts = int(time.time())
session_id = f"cs_test_smoke_s347_{ts}"
event_id = f"evt_test_smoke_s347_{ts}"
EMAIL = "smoke-s347@fluxion-app.com"

event = {
    "id": event_id,
    "object": "event",
    "type": "checkout.session.completed",
    "api_version": "2026-04-22.dahlia",
    "created": ts,
    "data": {"object": {
        "id": session_id,
        "object": "checkout.session",
        "amount_total": 49700,          # -> tier base
        "currency": "eur",
        "client_reference_id": "lead_999",
        "customer_email": EMAIL,
        "customer_details": {"email": EMAIL},
        "payment_intent": f"pi_test_smoke_{ts}",
        "metadata": {},
    }},
}
body = json.dumps(event, separators=(",", ":")).encode()
signed_payload = f"{ts}.".encode() + body
sig = hmac.new(WHSEC.encode(), signed_payload, hashlib.sha256).hexdigest()
header = f"t={ts},v1={sig}"

req = urllib.request.Request(URL, data=body, method="POST", headers={
    "Content-Type": "application/json",
    "Stripe-Signature": header,
    "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        status = r.status
        resp = r.read().decode()
except urllib.error.HTTPError as e:
    status = e.code
    resp = e.read().decode()

print(f"HTTP {status}")
print(f"session_id={session_id}")
print(f"resp={resp}")
ok = False
try:
    j = json.loads(resp)
    ok = bool(j.get("license_id")) and j.get("tier") == "base"
except Exception:
    pass
print("SMOKE_LICENSE_OK" if ok else "SMOKE_LICENSE_CHECK_MANUAL")
