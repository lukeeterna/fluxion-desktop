#!/usr/bin/env python3
"""
Sara Stress Test per Verticale — Conversazioni Multi-Turn Live
===============================================================
Simula il flusso IDENTICO alla telefonata reale, multi-turn,
per OGNI verticale. Copre: booking completo, FAQ, guardrail,
disambiguazione, cancel mid-flow, latenza.

Eseguire su iMac (pipeline bound 127.0.0.1:3002):

    ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python tests/e2e/test_sara_stress_per_verticale.py"

Opzioni:
    --vertical salone     # Testa solo un verticale
    --verbose             # Mostra ogni risposta di Sara
    --latency-target 800  # Target latenza ms (default 2000)
"""

import json
import os
import sys
import time
import urllib.request
from typing import Dict, List, Optional, Tuple, Any

URL = os.environ.get("PIPELINE_URL", "http://127.0.0.1:3002")
LATENCY_TARGET_MS = 2000
INTER_VERTICAL_PAUSE = 1.5  # secondi tra un verticale e l'altro
VERBOSE = False


# ============================================================================
# HTTP helpers (stesse di test_sara_massive.py)
# ============================================================================

def api(path, data=None, method="POST", timeout=30):
    # type: (str, Optional[dict], str, int) -> dict
    body = json.dumps(data or {}).encode("utf-8") if data is not None else b"{}"
    req = urllib.request.Request(URL + path, data=body,
        headers={"Content-Type": "application/json"})
    req.get_method = lambda: method
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"success": False, "error": str(e)}


def process(text, session_id=None):
    # type: (str, Optional[str]) -> dict
    payload = {"text": text}
    if session_id:
        payload["session_id"] = session_id
    t0 = time.time()
    r = api("/api/voice/process", payload)
    r["_ms"] = (time.time() - t0) * 1000
    return r


def reset():
    return api("/api/voice/reset")


def set_vertical(v):
    # type: (str,) -> dict
    return api("/api/voice/set-vertical", {"vertical": v})


def health():
    try:
        req = urllib.request.Request(URL + "/health")
        resp = urllib.request.urlopen(req, timeout=5)
        return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


# ============================================================================
# Result tracker con breakdown per verticale
# ============================================================================

class Results:
    def __init__(self):
        self.ok = 0
        self.fail = 0
        self.warn = 0
        self.log = []  # type: List[str]
        self.by_vertical = {}  # type: Dict[str, Dict[str, int]]
        self.latencies = []  # type: List[float]

    def _ensure_vert(self, vert):
        # type: (str,) -> None
        if vert not in self.by_vertical:
            self.by_vertical[vert] = {"ok": 0, "warn": 0, "fail": 0}

    def OK(self, vert, scenario, msg, ms=0.0):
        # type: (str, str, str, float) -> None
        self.ok += 1
        self._ensure_vert(vert)
        self.by_vertical[vert]["ok"] += 1
        if ms > 0:
            self.latencies.append(ms)
        s = "OK   [%s] [%s]: %s" % (vert.upper(), scenario, msg)
        if ms > 0:
            s += " (%.0fms)" % ms
        self.log.append(s)
        print(s)

    def FAIL(self, vert, scenario, msg, ms=0.0):
        # type: (str, str, str, float) -> None
        self.fail += 1
        self._ensure_vert(vert)
        self.by_vertical[vert]["fail"] += 1
        if ms > 0:
            self.latencies.append(ms)
        s = "FAIL [%s] [%s]: %s" % (vert.upper(), scenario, msg)
        if ms > 0:
            s += " (%.0fms)" % ms
        self.log.append(s)
        print(s)

    def WARN(self, vert, scenario, msg, ms=0.0):
        # type: (str, str, str, float) -> None
        self.warn += 1
        self._ensure_vert(vert)
        self.by_vertical[vert]["warn"] += 1
        if ms > 0:
            self.latencies.append(ms)
        s = "WARN [%s] [%s]: %s" % (vert.upper(), scenario, msg)
        if ms > 0:
            s += " (%.0fms)" % ms
        self.log.append(s)
        print(s)

    def summary(self):
        # type: () -> bool
        total = self.ok + self.fail + self.warn
        print("\n" + "=" * 80)
        print("STRESS TEST RESULTS: %d OK / %d WARN / %d FAIL (total %d)" % (
            self.ok, self.warn, self.fail, total))
        print("=" * 80)

        # Per-vertical breakdown
        print("\nBreakdown per verticale:")
        print("%-15s %6s %6s %6s %6s" % ("VERTICALE", "OK", "WARN", "FAIL", "TOTAL"))
        print("-" * 45)
        for vert in sorted(self.by_vertical.keys()):
            v = self.by_vertical[vert]
            t = v["ok"] + v["warn"] + v["fail"]
            print("%-15s %6d %6d %6d %6d" % (vert.upper(), v["ok"], v["warn"], v["fail"], t))

        # Latency stats
        if self.latencies:
            s_lat = sorted(self.latencies)
            p50 = s_lat[len(s_lat) // 2]
            p95 = s_lat[int(len(s_lat) * 0.95)]
            p99 = s_lat[int(len(s_lat) * 0.99)]
            avg = sum(s_lat) / len(s_lat)
            print("\nLatenza (%d campioni):" % len(s_lat))
            print("  AVG: %.0fms | P50: %.0fms | P95: %.0fms | P99: %.0fms | MAX: %.0fms" % (
                avg, p50, p95, p99, s_lat[-1]))
            if p95 > LATENCY_TARGET_MS:
                print("  ** P95 %.0fms SOPRA target %dms **" % (p95, LATENCY_TARGET_MS))

        if self.fail > 0:
            print("\nFAILURES:")
            for line in self.log:
                if line.startswith("FAIL"):
                    print("  " + line)

        return self.fail == 0


R = Results()


# ============================================================================
# Definizione verticali: servizi, FAQ, guardrail, clienti di esempio
# ============================================================================

VERTICALS = {
    "salone": {
        "label": "Salone Parrucchiere",
        # Conversazioni booking complete (multi-turn)
        "booking_conversations": [
            {
                "name": "Taglio uomo",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Vorrei prenotare un taglio uomo", ["nome", "chi", "cortesia"]),
                    ("Marco Rossi", ["data", "quando", "giorno", "quale"]),
                    ("Domani", ["ora", "orario", "che ora", "preferenza"]),
                    ("Alle dieci", ["riepilog", "conferma", "taglio", "domani", "10"]),
                    ("Si, confermo", ["prenotazione", "confermata", "confermat", "whatsapp", "registrat"]),
                ],
            },
            {
                "name": "Colore e piega",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Vorrei colore e piega", ["nome", "chi", "cortesia"]),
                    ("Sono Anna Bianchi", ["data", "quando", "giorno"]),
                    ("Venerdi prossimo", ["ora", "orario", "che ora"]),
                    ("Alle quattordici e trenta", ["riepilog", "conferma", "colore", "piega", "14"]),
                    ("Si confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
            {
                "name": "Barba",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Vorrei fare la barba per favore", ["nome", "chi", "cortesia"]),
                    ("Luca Verdi", ["data", "quando", "giorno"]),
                    ("Lunedi", ["ora", "orario", "che ora"]),
                    ("Alle nove", ["riepilog", "conferma", "barba", "luned", "9"]),
                    ("Si va bene", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
        ],
        "faq": [
            ("Quanto costa un taglio uomo?", ["prezzo", "euro", "costo", "taglio"]),
            ("Che orari avete?", ["orari", "aperto", "chiuso", "luned"]),
            ("Accettate la carta di credito?", ["carta", "pagamento", "contanti", "bancomat"]),
        ],
        "guardrail_wrong_service": [
            ("Vorrei il cambio olio", ["non", "occupo", "salone", "capelli", "parrucchier"]),
            ("Mi serve il tagliando auto", ["non", "occupo", "salone", "parrucchier"]),
            ("Vorrei una visita medica", ["non", "occupo", "salone"]),
        ],
        "disambig_name": "Rossi",
        "cancel_service": "taglio uomo",
    },
    "auto": {
        "label": "Officina Auto",
        "booking_conversations": [
            {
                "name": "Tagliando",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Devo fare il tagliando", ["nome", "chi", "cortesia"]),
                    ("Giuseppe Ferrari", ["data", "quando", "giorno"]),
                    ("Mercoledi prossimo", ["ora", "orario", "che ora"]),
                    ("Alle otto e trenta", ["riepilog", "conferma", "tagliando", "mercoled", "8"]),
                    ("Si confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
            {
                "name": "Cambio gomme",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Cambio gomme stagionale", ["nome", "chi", "cortesia"]),
                    ("Paolo Neri", ["data", "quando", "giorno"]),
                    ("Giovedi", ["ora", "orario", "che ora"]),
                    ("La mattina presto, alle otto", ["riepilog", "conferma", "gomme", "gioved", "8"]),
                    ("Si va bene", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
            {
                "name": "Revisione",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Devo fare la revisione", ["nome", "chi", "cortesia"]),
                    ("Roberto Colombo", ["data", "quando", "giorno"]),
                    ("Sabato", ["ora", "orario", "che ora"]),
                    ("Alle undici", ["riepilog", "conferma", "revision", "sabato", "11"]),
                    ("Confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
        ],
        "faq": [
            ("Quanto costa il tagliando?", ["prezzo", "euro", "costo", "tagliando"]),
            ("Fate il ritiro a domicilio?", ["ritir", "domicilio"]),
            ("Che orari avete?", ["orari", "aperto", "chiuso", "luned"]),
        ],
        "guardrail_wrong_service": [
            ("Vorrei un taglio di capelli", ["non", "occupo", "officina", "auto", "meccan"]),
            ("Vorrei prenotare una visita medica", ["non", "occupo", "officina"]),
            ("Cerco un personal trainer", ["non", "occupo", "officina"]),
        ],
        "disambig_name": "Ferrari",
        "cancel_service": "tagliando",
    },
    "medical": {
        "label": "Studio Medico",
        "booking_conversations": [
            {
                "name": "Visita odontoiatrica",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Vorrei prenotare una visita odontoiatrica", ["nome", "chi", "cortesia"]),
                    ("Francesca Russo", ["data", "quando", "giorno"]),
                    ("Martedi", ["ora", "orario", "che ora"]),
                    ("Alle quindici", ["riepilog", "conferma", "odontoiatr", "marted", "15"]),
                    ("Si confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
            {
                "name": "Seduta fisioterapia",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Ho bisogno di una seduta di fisioterapia", ["nome", "chi", "cortesia"]),
                    ("Davide Esposito", ["data", "quando", "giorno"]),
                    ("Venerdi", ["ora", "orario", "che ora"]),
                    ("Alle dieci e trenta", ["riepilog", "conferma", "fisioterapi", "venerd", "10"]),
                    ("Si va bene confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
        ],
        "faq": [
            ("Quanto costa una visita odontoiatrica?", ["prezzo", "euro", "costo", "visita", "odontoiatr"]),
            ("Devo venire a digiuno?", ["digiuno", "preparazione"]),
            ("Che orari avete?", ["orari", "aperto", "chiuso", "luned"]),
        ],
        "guardrail_wrong_service": [
            ("Vorrei un taglio di capelli", ["non", "occupo", "studio", "medic", "clinic"]),
            ("Cambio gomme per favore", ["non", "occupo", "studio", "medic"]),
        ],
        "disambig_name": "Russo",
        "cancel_service": "visita odontoiatrica",
    },
    "palestra": {
        "label": "Palestra / Centro Fitness",
        "booking_conversations": [
            {
                "name": "Abbonamento mensile",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Vorrei un abbonamento mensile", ["nome", "chi", "cortesia"]),
                    ("Simone Conti", ["data", "quando", "giorno"]),
                    ("Lunedi", ["ora", "orario", "che ora"]),
                    ("Alle diciotto", ["riepilog", "conferma", "abbonam", "luned", "18"]),
                    ("Si confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
            {
                "name": "Personal trainer",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Cerco un personal trainer", ["nome", "chi", "cortesia"]),
                    ("Chiara Mancini", ["data", "quando", "giorno"]),
                    ("Mercoledi", ["ora", "orario", "che ora"]),
                    ("Alle sette di sera, le diciannove", ["riepilog", "conferma", "personal", "trainer", "mercoled", "19"]),
                    ("Confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
        ],
        "faq": [
            ("Quanto costa l'abbonamento mensile?", ["prezzo", "euro", "costo", "abbonam"]),
            ("Avete la piscina?", ["piscina", "vasca", "nuoto"]),
            ("Che orari avete?", ["orari", "aperto", "chiuso"]),
        ],
        "guardrail_wrong_service": [
            ("Vorrei un taglio di capelli", ["non", "occupo", "palestra", "fitness"]),
            ("Devo fare la revisione auto", ["non", "occupo", "palestra"]),
        ],
        "disambig_name": "Conti",
        "cancel_service": "abbonamento mensile",
    },
    "beauty": {
        "label": "Centro Estetico",
        "booking_conversations": [
            {
                "name": "Pulizia del viso",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Vorrei una pulizia del viso", ["nome", "chi", "cortesia"]),
                    ("Elena Moretti", ["data", "quando", "giorno"]),
                    ("Giovedi", ["ora", "orario", "che ora"]),
                    ("Alle sedici", ["riepilog", "conferma", "pulizia", "viso", "gioved", "16"]),
                    ("Si confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
            {
                "name": "Epilazione laser",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Vorrei fare epilazione laser", ["nome", "chi", "cortesia"]),
                    ("Sara Romano", ["data", "quando", "giorno"]),
                    ("Sabato", ["ora", "orario", "che ora"]),
                    ("Alle dieci", ["riepilog", "conferma", "epilazione", "laser", "sabato", "10"]),
                    ("Va bene confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
        ],
        "faq": [
            ("Quanto costa la pulizia del viso?", ["prezzo", "euro", "costo", "pulizia", "viso"]),
            ("Che orari avete?", ["orari", "aperto", "chiuso"]),
            ("Fate anche massaggi?", ["massagg", "trattament"]),
        ],
        "guardrail_wrong_service": [
            ("Vorrei il cambio olio", ["non", "occupo", "centro", "estetic", "beauty"]),
            ("Mi serve il tagliando auto", ["non", "occupo", "centro", "estetic"]),
        ],
        "disambig_name": "Romano",
        "cancel_service": "pulizia del viso",
    },
    "professionale": {
        "label": "Studio Professionale",
        "booking_conversations": [
            {
                "name": "Consulenza legale",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Ho bisogno di una consulenza legale", ["nome", "chi", "cortesia"]),
                    ("Alessandro Gentile", ["data", "quando", "giorno"]),
                    ("Martedi prossimo", ["ora", "orario", "che ora"]),
                    ("Alle undici", ["riepilog", "conferma", "consulenza", "legal", "marted", "11"]),
                    ("Si confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
            {
                "name": "Dichiarazione dei redditi",
                "turns": [
                    ("Buongiorno", ["buongiorno", "sara", "posso"]),
                    ("Devo fare la dichiarazione dei redditi", ["nome", "chi", "cortesia"]),
                    ("Maria Fontana", ["data", "quando", "giorno"]),
                    ("Giovedi", ["ora", "orario", "che ora"]),
                    ("Alle nove e trenta", ["riepilog", "conferma", "dichiarazion", "redditi", "gioved", "9"]),
                    ("Confermo", ["prenotazione", "confermata", "confermat", "whatsapp"]),
                ],
            },
        ],
        "faq": [
            ("Quanto costa una consulenza?", ["prezzo", "euro", "costo", "consulenz"]),
            ("Che orari avete?", ["orari", "aperto", "chiuso"]),
        ],
        "guardrail_wrong_service": [
            ("Vorrei un taglio di capelli", ["non", "occupo", "studio", "profession"]),
            ("Cambio gomme per favore", ["non", "occupo", "studio"]),
        ],
        "disambig_name": "Gentile",
        "cancel_service": "consulenza legale",
    },
}


# ============================================================================
# Core: conversazione multi-turn booking
# ============================================================================

def run_booking_conversation(vert, conv):
    # type: (str, dict) -> None
    """Esegue una conversazione booking completa multi-turn."""
    conv_name = conv["name"]
    turns = conv["turns"]
    tag = vert.upper()
    scenario = "BOOKING %s" % conv_name

    for i, (text, expected_keywords) in enumerate(turns):
        r = process(text)
        resp = r.get("response", "").lower()
        fsm = r.get("fsm_state", "")
        ms = r.get("_ms", 0)
        success = r.get("success", False)

        if VERBOSE:
            print("  [turn %d] USER: %s" % (i + 1, text))
            print("           SARA: %s" % resp[:120])
            print("           FSM: %s | %.0fms" % (fsm, ms))

        if not success:
            R.FAIL(tag, scenario, "Turn %d '%s' -> errore: %s" % (i + 1, text[:30], r.get("error", "")), ms)
            return  # abort conversation

        # Controlla che almeno una keyword attesa sia nella risposta
        matched = any(kw in resp for kw in expected_keywords)

        # Tolleranza: se siamo a meta' flusso e la FSM ha progredito, va bene
        fsm_progressed = fsm in (
            "idle", "waiting_service", "waiting_name", "waiting_surname",
            "waiting_date", "waiting_time", "waiting_operator",
            "confirming", "completed",
            "propose_registration", "registering_surname",
            "registering_phone",
            "disambiguating_name",
            "confirming_phone",
        )

        if matched:
            R.OK(tag, scenario, "Turn %d '%s' -> OK (fsm=%s)" % (i + 1, text[:30], fsm), ms)
        elif fsm_progressed and success:
            # FSM ha progredito ma keywords non matchano esattamente
            R.WARN(tag, scenario, "Turn %d '%s' -> fsm=%s, keywords non trovate in: '%s'" % (
                i + 1, text[:30], fsm, resp[:60]), ms)
        else:
            R.FAIL(tag, scenario, "Turn %d '%s' -> fsm=%s, resp='%s'" % (
                i + 1, text[:30], fsm, resp[:60]), ms)

        # Check latenza
        if ms > LATENCY_TARGET_MS:
            R.WARN(tag, "LATENCY", "Turn %d: %.0fms > %dms target" % (i + 1, ms, LATENCY_TARGET_MS))

    # Chiusura conversazione
    r = process("Grazie, arrivederci")
    resp = r.get("response", "").lower()
    ms = r.get("_ms", 0)
    if any(kw in resp for kw in ["arrivederci", "buona giornata", "presto", "risentir", "ciao"]):
        R.OK(tag, scenario, "Chiusura -> saluto OK", ms)
    else:
        R.WARN(tag, scenario, "Chiusura -> resp='%s'" % resp[:60], ms)


# ============================================================================
# Scenario: FAQ (non deve entrare in booking)
# ============================================================================

def run_faq_test(vert, faq_list):
    # type: (str, list) -> None
    """Testa che domande FAQ vengano risposte senza entrare in booking."""
    tag = vert.upper()
    for text, expected_keywords in faq_list:
        reset()
        set_vertical(vert)
        # Saluto iniziale
        process("Buongiorno")
        # Domanda FAQ
        r = process(text)
        resp = r.get("response", "").lower()
        fsm = r.get("fsm_state", "")
        layer = r.get("layer", "")
        ms = r.get("_ms", 0)

        matched = any(kw in resp for kw in expected_keywords)

        # FAQ non deve mettere la FSM in stati di booking
        in_booking = fsm in ("waiting_name", "waiting_date", "waiting_time", "confirming")

        if matched and not in_booking:
            R.OK(tag, "FAQ", "'%s' -> risposta pertinente (layer=%s)" % (text[:40], layer), ms)
        elif matched and in_booking:
            R.WARN(tag, "FAQ", "'%s' -> risposta OK ma FSM in booking (%s)" % (text[:40], fsm), ms)
        elif not matched and not in_booking:
            R.WARN(tag, "FAQ", "'%s' -> keywords non trovate in: '%s'" % (text[:35], resp[:60]), ms)
        else:
            R.FAIL(tag, "FAQ", "'%s' -> entrato in booking (%s) senza rispondere" % (text[:40], fsm), ms)


# ============================================================================
# Scenario: Guardrail servizio sbagliato
# ============================================================================

def run_guardrail_test(vert, guardrail_list):
    # type: (str, list) -> None
    """Testa che servizi fuori verticale vengano bloccati."""
    tag = vert.upper()
    for text, expected_keywords in guardrail_list:
        reset()
        set_vertical(vert)
        process("Buongiorno")
        r = process(text)
        resp = r.get("response", "").lower()
        fsm = r.get("fsm_state", "")
        ms = r.get("_ms", 0)

        blocked = any(kw in resp for kw in expected_keywords) or "non" in resp[:30]

        # Non deve entrare in booking con servizio sbagliato
        entered_booking = fsm in ("waiting_name", "waiting_date", "waiting_time", "confirming")

        if blocked and not entered_booking:
            R.OK(tag, "GUARDRAIL", "Bloccato: '%s'" % text[:40], ms)
        elif not blocked and not entered_booking:
            R.WARN(tag, "GUARDRAIL", "Non bloccato esplicitamente: '%s' -> '%s'" % (text[:30], resp[:60]), ms)
        else:
            R.FAIL(tag, "GUARDRAIL", "Accettato servizio sbagliato: '%s' -> fsm=%s" % (text[:35], fsm), ms)


# ============================================================================
# Scenario: Disambiguazione nome (cognome comune)
# ============================================================================

def run_disambig_test(vert, surname):
    # type: (str, str) -> None
    """Testa disambiguazione con un cognome che potrebbe avere omonimi."""
    tag = vert.upper()
    reset()
    set_vertical(vert)

    # Prima conversazione: richiesta generica + cognome solo
    conv = VERTICALS[vert]["booking_conversations"][0]
    first_service_text = conv["turns"][1][0]  # la richiesta servizio

    process("Buongiorno")
    process(first_service_text)
    r = process(surname)  # Solo cognome, potrebbe essere ambiguo
    resp = r.get("response", "").lower()
    fsm = r.get("fsm_state", "")
    ms = r.get("_ms", 0)

    # Possibili risultati validi:
    # 1. Disambiguazione (chiede quale dei Rossi)
    # 2. Chiede nome completo
    # 3. Nessun match -> propone registrazione
    # 4. Match unico -> prosegue
    valid_fsm = (
        "disambiguating_name", "disambiguating_birth_date",
        "waiting_surname", "waiting_name",
        "propose_registration", "registering_surname",
        "waiting_date", "waiting_time",
    )

    if fsm in valid_fsm:
        R.OK(tag, "DISAMBIG", "Cognome '%s' -> fsm=%s (gestito)" % (surname, fsm), ms)
    elif "quale" in resp or "cognome" in resp or "nome" in resp or "intend" in resp:
        R.OK(tag, "DISAMBIG", "Cognome '%s' -> chiede chiarimento" % surname, ms)
    else:
        R.WARN(tag, "DISAMBIG", "Cognome '%s' -> fsm=%s, resp='%s'" % (surname, fsm, resp[:60]), ms)


# ============================================================================
# Scenario: Cancel mid-flow
# ============================================================================

def run_cancel_test(vert, service):
    # type: (str, str) -> None
    """Testa cancellazione durante prenotazione."""
    tag = vert.upper()
    reset()
    set_vertical(vert)

    # Inizia booking
    process("Buongiorno")
    process("Vorrei prenotare %s" % service)
    process("Marco Rossi")

    # Ora cancella
    r = process("Lascia perdere, annulla tutto")
    resp = r.get("response", "").lower()
    fsm = r.get("fsm_state", "")
    ms = r.get("_ms", 0)

    cancelled = any(kw in resp for kw in ["annull", "cancell", "altro", "ricominc", "aiutar"])
    back_to_idle = fsm in ("idle", "cancelled", "completed")

    if cancelled or back_to_idle:
        R.OK(tag, "CANCEL", "Annullamento mid-flow -> fsm=%s" % fsm, ms)
    else:
        R.WARN(tag, "CANCEL", "Risposta non chiara: fsm=%s, resp='%s'" % (fsm, resp[:60]), ms)


# ============================================================================
# Scenario: Latenza per step (ogni turn della prima conversazione)
# ============================================================================

def run_latency_test(vert):
    # type: (str,) -> None
    """Misura latenza di ogni step nel primo booking del verticale."""
    tag = vert.upper()
    conv = VERTICALS[vert]["booking_conversations"][0]
    slow_turns = 0

    for i, (text, _) in enumerate(conv["turns"]):
        r = process(text)
        ms = r.get("_ms", 0)
        success = r.get("success", False)

        if not success:
            R.FAIL(tag, "LATENCY", "Turn %d errore: %s" % (i + 1, r.get("error", "")), ms)
            return

        if ms > LATENCY_TARGET_MS:
            slow_turns += 1
            R.WARN(tag, "LATENCY DETAIL", "Turn %d '%s': %.0fms > %dms" % (
                i + 1, text[:25], ms, LATENCY_TARGET_MS), ms)

    if slow_turns == 0:
        R.OK(tag, "LATENCY", "Tutti i turn sotto %dms" % LATENCY_TARGET_MS)
    elif slow_turns <= 1:
        R.WARN(tag, "LATENCY", "%d turn sopra target" % slow_turns)
    else:
        R.FAIL(tag, "LATENCY", "%d/%d turn sopra target %dms" % (
            slow_turns, len(conv["turns"]), LATENCY_TARGET_MS))


# ============================================================================
# Runner principale per un singolo verticale
# ============================================================================

def test_single_vertical(vert):
    # type: (str,) -> None
    """Esegue tutti gli scenari per un verticale."""
    vdata = VERTICALS[vert]
    label = vdata["label"]

    print("\n" + "=" * 80)
    print("VERTICALE: %s (%s)" % (vert.upper(), label))
    print("=" * 80)

    # --- 1. Booking completi (multi-turn) ---
    for conv in vdata["booking_conversations"]:
        print("\n--- Booking: %s ---" % conv["name"])
        reset()
        set_vertical(vert)
        run_booking_conversation(vert, conv)

    # --- 2. FAQ ---
    if vdata.get("faq"):
        print("\n--- FAQ ---")
        run_faq_test(vert, vdata["faq"])

    # --- 3. Guardrail ---
    if vdata.get("guardrail_wrong_service"):
        print("\n--- Guardrail servizio sbagliato ---")
        run_guardrail_test(vert, vdata["guardrail_wrong_service"])

    # --- 4. Disambiguazione nome ---
    if vdata.get("disambig_name"):
        print("\n--- Disambiguazione nome ---")
        run_disambig_test(vert, vdata["disambig_name"])

    # --- 5. Cancel mid-flow ---
    if vdata.get("cancel_service"):
        print("\n--- Cancel mid-flow ---")
        run_cancel_test(vert, vdata["cancel_service"])

    # --- 6. Latenza ---
    print("\n--- Latenza per-step ---")
    reset()
    set_vertical(vert)
    run_latency_test(vert)


# ============================================================================
# MAIN
# ============================================================================

def main():
    # Parse args
    target_vert = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--vertical" and i + 1 < len(sys.argv):
            target_vert = sys.argv[i + 1].lower()
            i += 2
        elif sys.argv[i] == "--verbose":
            global VERBOSE
            VERBOSE = True
            i += 1
        elif sys.argv[i] == "--latency-target" and i + 1 < len(sys.argv):
            global LATENCY_TARGET_MS
            LATENCY_TARGET_MS = int(sys.argv[i + 1])
            i += 2
        else:
            print("Opzione sconosciuta: %s" % sys.argv[i])
            print("Uso: python test_sara_stress_per_verticale.py [--vertical NOME] [--verbose] [--latency-target MS]")
            sys.exit(1)

    print("=" * 80)
    print("FLUXION Sara — Stress Test per Verticale (Multi-Turn Live)")
    print("Pipeline: %s" % URL)
    print("Latency target: %dms" % LATENCY_TARGET_MS)
    print("=" * 80)

    # Health check
    h = health()
    if not h:
        print("FATAL: Pipeline non raggiungibile a %s" % URL)
        sys.exit(1)
    print("Pipeline: %s | STT: %s" % (
        h.get("status", "?"), h.get("features", {}).get("stt", "?")))

    # Verticali da testare
    if target_vert:
        if target_vert not in VERTICALS:
            print("Verticale sconosciuto: '%s'. Disponibili: %s" % (
                target_vert, ", ".join(sorted(VERTICALS.keys()))))
            sys.exit(1)
        verts_to_test = [target_vert]
    else:
        verts_to_test = list(VERTICALS.keys())

    print("Verticali: %s" % ", ".join(v.upper() for v in verts_to_test))
    print("Scenari per verticale: booking(%d-3 conv) + FAQ + guardrail + disambig + cancel + latenza" % (
        max(len(VERTICALS[v]["booking_conversations"]) for v in verts_to_test)))

    # Esecuzione
    for idx, vert in enumerate(verts_to_test):
        if idx > 0:
            print("\n... pausa %.1fs tra verticali ..." % INTER_VERTICAL_PAUSE)
            time.sleep(INTER_VERTICAL_PAUSE)
        test_single_vertical(vert)

    # Summary
    success = R.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
