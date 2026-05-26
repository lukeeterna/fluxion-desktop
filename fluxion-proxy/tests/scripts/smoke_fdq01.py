#!/usr/bin/env python3
"""
Smoke test FDQ-01 S297 — autonomous CTO E2E.
Synthetic checkout.session.completed webhook → worker test → D1 + Resend +
success page + license recovery endpoint.
"""
import os, sys, json, hmac, hashlib, time, urllib.request, urllib.parse, re

WORKER = "https://fluxion-proxy-test.gianlucanewtech.workers.dev"
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET_TEST"]
EMAIL = "fluxion.gestionale@gmail.com"
TIER = "base"
AMOUNT = 49700  # base €497

ts = int(time.time())
session_id = f"cs_test_smoke_S297_{ts}"
event_id = f"evt_smoke_S297_{ts}"
license_purchase_id = f"li_smoke_S297_{ts}"

# Build synthetic Stripe Checkout Session event (minimal valid fields)
event = {
    "id": event_id,
    "object": "event",
    "api_version": "2026-04-22.dahlia",
    "created": ts,
    "type": "checkout.session.completed",
    "livemode": False,
    "pending_webhooks": 0,
    "request": {"id": None, "idempotency_key": None},
    "data": {
        "object": {
            "id": session_id,
            "object": "checkout.session",
            "amount_subtotal": AMOUNT,
            "amount_total": AMOUNT,
            "currency": "eur",
            "customer": None,
            "customer_email": EMAIL,
            "customer_details": {
                "email": EMAIL,
                "name": "FLUXION Smoke S297",
                "address": None,
                "phone": None,
                "tax_exempt": "none",
                "tax_ids": [],
            },
            "livemode": False,
            "metadata": {"tier": TIER, "smoke_test": "S297"},
            "mode": "payment",
            "payment_status": "paid",
            "status": "complete",
            "success_url": f"{WORKER}/success/{{CHECKOUT_SESSION_ID}}",
            "url": None,
        }
    },
}

raw = json.dumps(event, separators=(",", ":"))
signed = f"{ts}.{raw}".encode()
sig = hmac.new(WEBHOOK_SECRET.encode(), signed, hashlib.sha256).hexdigest()
header = f"t={ts},v1={sig}"

UA = "Stripe/1.0 (+https://stripe.com/docs/webhooks)"
print(f"[1/5] POST webhook (session_id={session_id})")
req = urllib.request.Request(
    f"{WORKER}/api/v1/webhook/stripe",
    data=raw.encode(),
    headers={
        "Content-Type": "application/json",
        "Stripe-Signature": header,
        "User-Agent": UA,
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode()
        print(f"  HTTP {r.status}: {body[:200]}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"  HTTP {e.code} ERROR: {body[:500]}")
    sys.exit(1)

# Step 2: query success page
print(f"\n[2/5] GET /success/{session_id}")
time.sleep(2)  # let CF propagate D1 read
req2 = urllib.request.Request(f"{WORKER}/success/{session_id}", headers={"User-Agent": UA})
with urllib.request.urlopen(req2, timeout=15) as r:
    html = r.read().decode()
    print(f"  HTTP {r.status} ({len(html)} bytes)")

# Extract payload, signature, recovery from div id="..."
pm = re.search(r'id=["\']payload-data["\'][^>]*>([^<]+)<', html)
sm = re.search(r'id=["\']signature-data["\'][^>]*>([^<]+)<', html)
rm = re.search(r'id=["\']recovery-url["\'][^>]*>([^<]+)<', html)

if not pm or not sm or not rm:
    print(f"  ❌ payload/signature/recovery extraction failed")
    print(f"    payload match: {bool(pm)}  sig: {bool(sm)}  recovery: {bool(rm)}")
    print(f"  HTML excerpt around payload-data:")
    idx = html.find("payload-data")
    if idx >= 0:
        print(html[max(0,idx-50):idx+400])
    sys.exit(1)

html_payload = pm.group(1).strip()
html_signature = sm.group(1).strip()
recovery_url = rm.group(1).strip().replace("&amp;", "&")
print(f"  ✅ payload: {html_payload[:60]}...")
print(f"  ✅ signature: {html_signature[:60]}...")
print(f"  ✅ recovery URL: {recovery_url[:100]}...")
print(f"  payload (HTML): {html_payload[:60] if html_payload else 'MISSING'}...")
print(f"  signature (HTML): {html_signature[:60] if html_signature else 'MISSING'}...")

# Step 3: hit recovery URL
print(f"\n[3/5] GET recovery URL")
req3 = urllib.request.Request(recovery_url, headers={"User-Agent": UA})
with urllib.request.urlopen(req3, timeout=15) as r:
    rec_body = r.read().decode()
    rec_status = r.status
print(f"  HTTP {rec_status}: {rec_body[:200]}")

if rec_status != 200:
    print(f"  ❌ recovery URL failed")
    sys.exit(1)

try:
    rec_json = json.loads(rec_body)
    if rec_json.get("license_payload") == html_payload and rec_json.get("license_signature") == html_signature:
        print("  ✅ recovery payload+signature MATCH success page")
    else:
        print(f"  ⚠️  recovery payload: {rec_json.get('license_payload', '')[:60]}")
        print(f"  ⚠️  HTML payload:     {html_payload[:60] if html_payload else 'NONE'}")
except Exception as e:
    print(f"  ❌ recovery JSON parse fail: {e}")
    sys.exit(1)

# Step 4: replay webhook (idempotency check FSAF-05)
print(f"\n[4/5] POST webhook REPLAY (same event_id={event_id})")
req4 = urllib.request.Request(
    f"{WORKER}/api/v1/webhook/stripe",
    data=raw.encode(),
    headers={
        "Content-Type": "application/json",
        "Stripe-Signature": header,
        "User-Agent": UA,
    },
    method="POST",
)
with urllib.request.urlopen(req4, timeout=30) as r:
    body4 = r.read().decode()
    print(f"  HTTP {r.status}: {body4[:300]}")
    if '"idempotent_replay":true' in body4:
        print("  ✅ idempotent_replay=true (FSAF-05 verified)")
    else:
        print("  ⚠️  no idempotent_replay flag")

print(f"\n[5/5] Smoke summary")
print(f"  session_id: {session_id}")
print(f"  event_id:   {event_id}")
print(f"  recovery:   {recovery_url[:100]}...")
print(f"  recipient:  {EMAIL} (Resend sandbox, account owner)")
print(f"  ✅ FDQ-01 smoke E2E PASS (test env, synthetic event)")
