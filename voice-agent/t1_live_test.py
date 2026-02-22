#!/usr/bin/env python3
"""
T1 Test Live - Voice Agent "Sara"
Verifica i 5 scenari critici con i bug fix applicati.
"""
import json
import urllib.request
import urllib.error
import time

BASE = "http://192.168.1.2:3002"

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        BASE + path,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def show(resp, check_fn=None):
    if "error" in resp:
        print(f"  ❌ ERROR: {resp['error']}")
        return False
    r = resp.get("response", "N/A")
    intent = resp.get("intent", "?")
    layer = resp.get("layer", "?")
    fsm = resp.get("fsm_state", "?")
    latency = resp.get("latency_ms", "?")
    print(f"  Sara: \"{r}\"")
    print(f"  intent={intent} layer={layer} fsm={fsm} latency={latency}ms")
    if check_fn:
        ok, msg = check_fn(resp)
        print(f"  {'✅' if ok else '❌'} {msg}")
        return ok
    return True

def reset():
    r = post("/api/voice/reset", {})
    sid = r.get("session_id", "?")
    print(f"  (reset → session {sid[:8] if sid != '?' else '?'}...)")
    time.sleep(0.3)

# =============================================================================
print("=" * 65)
print("  T1 LIVE TEST - FLUXION Voice Agent 'Sara'")
print(f"  Target: {BASE}")
print("=" * 65)

# Health check
h = get("/health")
if h.get("status") != "ok":
    print(f"❌ Pipeline non raggiungibile: {h}")
    exit(1)
print(f"✅ Pipeline OK (v{h.get('version')})\n")

results = {}

# =============================================================================
print("─" * 65)
print("SCENARIO 1: Greeting semplice (2° turno — 1° turno skip intenzionale)")
print("─" * 65)
reset()
# L'orchestratore salta CORTESIA al 1° turno per evitare doppio saluto
# → mandiamo prima un messaggio non-cortesia, poi il saluto
post("/api/voice/process", {"text": "vorrei informazioni"})  # 1° turno
r = post("/api/voice/process", {"text": "Buongiorno"})       # 2° turno → L1
ok = show(r, lambda d: (
    d.get("layer") in ("L1_exact", "l1_exact"),
    f"layer={d.get('layer')} (atteso L1_exact al 2° turno)"
))
results["S1_greeting"] = ok

# =============================================================================
print()
print("─" * 65)
print("SCENARIO 2: BUG 1 Fix - 'Sono Laura Bianchi' (era → 'Ura')")
print("─" * 65)
reset()
# Simula flusso: nuovo cliente
post("/api/voice/process", {"text": "Buongiorno"})
post("/api/voice/process", {"text": "Vorrei prenotare un taglio"})
post("/api/voice/process", {"text": "Domani alle 15"})
r = post("/api/voice/process", {"text": "non sono cliente, sono nuova"})
show(r)
r2 = post("/api/voice/process", {"text": "Sono Laura Bianchi"})
resp_text = r2.get("response", "")
name_ok = "Laura" in resp_text and "Ura" not in resp_text
ok = show(r2, lambda d: (
    name_ok,
    f"'Laura' in response={name_ok} (BUG1 fix {'✅' if name_ok else '❌'})"
))
results["S2_laura_name"] = ok

# =============================================================================
print()
print("─" * 65)
print("SCENARIO 3: BUG 2 Fix - 'Sì, confermo' non diventa cognome")
print("─" * 65)
reset()
post("/api/voice/process", {"text": "Buongiorno"})
post("/api/voice/process", {"text": "Vorrei un taglio"})
post("/api/voice/process", {"text": "Domani alle 10"})
r = post("/api/voice/process", {"text": "non sono cliente"})
show(r)
post("/api/voice/process", {"text": "Mi chiamo Marco"})
# Ora in REGISTERING_SURNAME - utente dice 'Sì' invece del cognome
r2 = post("/api/voice/process", {"text": "Sì, confermo"})
resp_text = r2.get("response", "")
bug2_ok = "Sì" not in resp_text.split(",")[0] and "Confermo" not in resp_text
ok = show(r2, lambda d: (
    bug2_ok,
    f"'Sì/Confermo' non nel nome={bug2_ok} (BUG2 fix {'✅' if bug2_ok else '❌'})"
))
results["S3_si_cognome"] = ok

# =============================================================================
print()
print("─" * 65)
print("SCENARIO 4: BUG 5 Fix - 'Grazie mille, arrivederci' → L1 (2° turno)")
print("─" * 65)
reset()
# Il 1° turno cortesia è skip intenzionale — testiamo al 2° turno
post("/api/voice/process", {"text": "Buongiorno"})  # 1° turno (va a L4, intenzionale)
r = post("/api/voice/process", {"text": "Grazie mille, arrivederci"})  # 2° turno → L1
ok = show(r, lambda d: (
    d.get("layer") in ("L1_exact", "l1_exact"),
    f"layer={d.get('layer')} (atteso L1_exact — BUG5 fix)"
))
results["S4_arrivederci"] = ok

# =============================================================================
print()
print("─" * 65)
print("SCENARIO 5: BUG 6 Fix - fsm_state presente nel JSON")
print("─" * 65)
reset()
r = post("/api/voice/process", {"text": "Buongiorno"})
fsm = r.get("fsm_state")
ok = fsm is not None and fsm != "?"
print(f"  fsm_state nel response: '{fsm}'")
print(f"  {'✅' if ok else '❌'} fsm_state {'presente' if ok else 'ASSENTE'} (BUG6 fix)")
results["S5_fsm_state"] = ok

# =============================================================================
print()
print("─" * 65)
print("SCENARIO 6: Chiusura graceful - 'arrivederci' standalone")
print("─" * 65)
reset()
post("/api/voice/process", {"text": "Buongiorno"})
r = post("/api/voice/process", {"text": "arrivederci"})
resp_text = r.get("response", "")
ok = show(r, lambda d: (
    d.get("layer") in ("L1_exact", "l1_exact") and "arrivederci" in d.get("response","").lower(),
    f"goodbye via L1 (BUG5)"
))
results["S6_goodbye"] = ok

# =============================================================================
# SEZIONE 2: TEST MULTI-VERTICALE
# =============================================================================
print()
print("=" * 65)
print("  SEZIONE 2: TEST VERTICALI")
print("=" * 65)

def reset_vertical(vertical):
    r = post("/api/voice/reset", {"vertical": vertical})
    v = r.get("vertical", "?")
    sid = r.get("session_id", "?")
    print(f"  (reset → vertical={v} session={sid[:8] if sid != '?' else '?'}...)")
    time.sleep(0.3)

# Scenario 7: Palestra/Wellness
print()
print("─" * 65)
print("SCENARIO 7: Verticale PALESTRA - prenotazione corso")
print("─" * 65)
reset_vertical("palestra")
post("/api/voice/process", {"text": "Vorrei prenotare"})
r = post("/api/voice/process", {"text": "Corso di spinning domani alle 10"})
ok = show(r, lambda d: (
    d.get("fsm_state") not in (None, "?") and "error" not in d,
    f"FSM attiva verticale palestra (state={d.get('fsm_state')})"
))
results["S7_palestra"] = ok

# Scenario 8: Medical
print()
print("─" * 65)
print("SCENARIO 8: Verticale MEDICAL - prenotazione visita")
print("─" * 65)
reset_vertical("medical")
post("/api/voice/process", {"text": "Buongiorno"})
r = post("/api/voice/process", {"text": "Vorrei prenotare una visita dal dottore"})
ok = show(r, lambda d: (
    d.get("fsm_state") not in (None, "?") and "error" not in d,
    f"FSM attiva verticale medical (state={d.get('fsm_state')})"
))
results["S8_medical"] = ok

# Scenario 9: Auto/Officina
print()
print("─" * 65)
print("SCENARIO 9: Verticale AUTO - prenotazione revisione")
print("─" * 65)
reset_vertical("auto")
post("/api/voice/process", {"text": "Buongiorno"})
r = post("/api/voice/process", {"text": "Devo portare la macchina per il cambio gomme"})
ok = show(r, lambda d: (
    d.get("fsm_state") not in (None, "?") and "error" not in d,
    f"FSM attiva verticale auto (state={d.get('fsm_state')})"
))
results["S9_auto"] = ok

# Scenario 10: Salone (verifica ripristino)
print()
print("─" * 65)
print("SCENARIO 10: Ripristino SALONE dopo switch verticale")
print("─" * 65)
reset_vertical("salone")
post("/api/voice/process", {"text": "Buongiorno"})
r = post("/api/voice/process", {"text": "Voglio un taglio di capelli"})
ok = show(r, lambda d: (
    d.get("fsm_state") not in (None, "?") and "error" not in d,
    f"Salone ripristinato correttamente (state={d.get('fsm_state')})"
))
results["S10_salone_restore"] = ok

# =============================================================================
print()
print("=" * 65)
print("  RIEPILOGO T1 COMPLETO")
print("=" * 65)
passed = sum(1 for v in results.values() if v)
total = len(results)

print()
print("  --- Bug Fix (S1-S6) ---")
for name, ok in list(results.items())[:6]:
    print(f"  {'✅' if ok else '❌'} {name}")

print()
print("  --- Multi-Verticale (S7-S10) ---")
for name, ok in list(results.items())[6:]:
    print(f"  {'✅' if ok else '❌'} {name}")

print()
print(f"  TOTALE: {passed}/{total} scenari OK")
if passed == total:
    print("  🎉 TUTTI I SCENARI PASSATI → pronto per Build v0.9.0")
else:
    print(f"  ⚠️  {total - passed} scenari falliti → da investigare")
print()
