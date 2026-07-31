# VERSIONE: stress_verticali_v2.py
# BASELINE: vos/runs/20260731/stress_verticali.py (fd32bc12)
# MODIFICHE RISPETTO ALLA V1:
#   1. Driver booking FSM-driven puro: risponde allo stato attuale di Sara a ogni turno,
#      non a flag temporali sent[]. Corregge il falso FAIL universale della v1 (data inviata
#      troppo tardi perché il loop consumava turni su stati già gestiti).
#   2. FAIL_SARA / FAIL_DRIVER: distinzione esplicita per ogni esito negativo.
#   3. Rilevamento loop FSM: se lo stesso stato si ripete ≥3 volte di fila → FAIL_SARA.
#   4. Limite turni finito: MAX_BOOKING_TURNS=20. Turni esauriti senza booking_created:
#      se l'ultimo stato appartiene alla FSM di booking → FAIL_SARA; altrimenti FAIL_DRIVER.
#   5. Report path e titolo aggiornati a v2.
#   6. Preflight esteso: verifica 12 condizioni prima di avviare la run.
#   7. stdout ≤30 righe (una per verticale + riepilogo + cleanup).
from __future__ import annotations

import atexit
import importlib.util
import json
import math
import os
import re
import signal
import sqlite3
import sys
import time
import unicodedata
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

BASE = "http://127.0.0.1:3002"
SLOW_MS = 5000.0
HTTP_TIMEOUT = 25.0
VERTICAL_BUDGET = 170.0
RUN_BUDGET = 1140.0
RESTORE_VERTICAL = "salone"
MAX_BOOKING_TURNS = 20

# Classificazioni esito — il riepilogo mostra FAIL ma il dettaglio distingue sempre SARA/DRIVER
OK, WARN, FAIL_SARA, FAIL_DRIVER, FAIL, ND = (
    "OK", "WARN", "FAIL_SARA", "FAIL_DRIVER", "FAIL", "ND"
)
SEVERITY = {OK: 0, WARN: 1, FAIL_DRIVER: 2, FAIL_SARA: 2, FAIL: 2, ND: -1}

OUT = Path(__file__).resolve().parent
REPORT = OUT / "stress_verticali_v2.md"
DEBUG = OUT / "stress_verticali_v2_debug.md"
ROOT = Path(__file__).resolve().parents[3]
VOICE = ROOT / "voice-agent"
ASSET = VOICE / "tests" / "e2e" / "test_sara_stress_per_verticale.py"
VERTICAL_DBS = VOICE / "data" / "vertical_dbs"

BOOKING_STATES = {
    "waiting_service", "waiting_name", "waiting_surname", "waiting_date",
    "waiting_time", "waiting_operator", "confirming", "propose_registration",
    "registering_surname", "registering_phone", "confirming_phone",
    "confirming_name", "disambiguating_name", "disambiguating_birth_date",
}
MONTHS = (
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
)
WEEKDAYS = (
    "lunedì", "martedì", "mercoledì", "giovedì",
    "venerdì", "sabato", "domenica",
)
STOPWORDS = {
    "del", "della", "delle", "degli", "dei", "di", "da", "per", "con",
    "senza", "una", "uno", "un", "il", "lo", "la", "le", "gli", "e",
    "ed", "al", "alla", "alle", "ai", "in", "su", "completo", "completa",
    "professionale", "standard", "servizio", "trattamento", "visita", "seduta",
}

# ─── Strutture dati ────────────────────────────────────────────────────────────

@dataclass
class Turn:
    scenario: str
    user: str
    response: str
    fsm: str
    layer: str
    latency_ms: float
    success: bool
    error: str = ""
    booking_action: Optional[Dict[str, Any]] = None
    ts: str = field(default_factory=lambda: now())


@dataclass
class Check:
    category: str
    level: str          # OK | WARN | FAIL_SARA | FAIL_DRIVER
    scenario: str
    message: str
    turn: Optional[Turn] = None
    ts: str = field(default_factory=lambda: now())


@dataclass
class VResult:
    key: str
    label: str
    api: str
    checks: List[Check] = field(default_factory=list)
    turns: List[Turn] = field(default_factory=list)
    duration_s: float = 0.0

    def add(self, category: str, level: str, scenario: str,
            message: str, turn: Optional[Turn] = None) -> None:
        self.checks.append(Check(category, level, scenario, message, turn))

    def status(self, category: str) -> str:
        levels = [c.level for c in self.checks if c.category == category]
        if not levels:
            return ND
        # Mappa FAIL_SARA/FAIL_DRIVER → FAIL per il riepilogo colonna
        mapped = [FAIL if l in (FAIL_SARA, FAIL_DRIVER) else l for l in levels]
        return max(mapped, key=lambda l: SEVERITY.get(l, -1))

    def overall(self) -> str:
        levels = [c.level for c in self.checks if c.category != "SETUP"]
        if not levels:
            return FAIL
        mapped = [FAIL if l in (FAIL_SARA, FAIL_DRIVER) else l for l in levels]
        return max(mapped, key=lambda l: SEVERITY.get(l, -1))

    def kb(self) -> str:
        return worst(self.status("FAQ"), self.status("CATALOGO"))

    def latencies(self) -> Dict[str, float]:
        values = sorted(t.latency_ms for t in self.turns if t.latency_ms > 0)
        if not values:
            return {}
        count = len(values)
        return {
            "avg": sum(values) / count,
            "p50": values[(count - 1) // 2],
            "p95": values[max(0, math.ceil(count * 0.95) - 1)],
            "max": values[-1],
        }

    def fail_sara_count(self) -> int:
        return sum(1 for c in self.checks if c.level == FAIL_SARA)

    def fail_driver_count(self) -> int:
        return sum(1 for c in self.checks if c.level == FAIL_DRIVER)


class BudgetExceeded(RuntimeError):
    pass


# ─── Stato globale ─────────────────────────────────────────────────────────────

class State:
    def __init__(self) -> None:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.tag = f"stress-v2:{stamp}:{os.getpid()}:{uuid.uuid4().hex[:8]}"
        self.source = "stress-verticali-v2-20260731"
        self.db: Optional[Path] = None
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.cleaned = False
        self.cleanup = ND
        self.restored = ND
        self.debug_lines: List[str] = []
        self.preflight_ok = False
        self.preflight_notes: List[str] = []

    def dbg(self, line: str) -> None:
        self.debug_lines.append(line)


STATE = State()

# ─── Utility ───────────────────────────────────────────────────────────────────

def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def has(text: str, needles: Iterable[str]) -> bool:
    value = norm(text)
    return any(norm(item) in value for item in needles)


def worst(*levels: str) -> str:
    valid = [l for l in levels if l != ND]
    return max(valid, key=lambda l: SEVERITY.get(l, -1)) if valid else ND


def request(
    path: str,
    payload: Optional[Dict[str, Any]] = None,
    method: str = "POST",
    timeout: float = HTTP_TIMEOUT,
) -> Tuple[int, Dict[str, Any], float, str]:
    started = time.monotonic()
    data = (
        None if method == "GET"
        else json.dumps(payload or {}, ensure_ascii=False).encode()
    )
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=max(1.0, timeout)) as resp:
            status = int(resp.status)
            raw = resp.read().decode("utf-8", errors="replace")
        body = json.loads(raw) if raw else {}
        if not isinstance(body, dict):
            body = {"data": body}
        body.pop("audio_base64", None)
        body.pop("audio_hex", None)
        return status, body, (time.monotonic() - started) * 1000.0, ""
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"raw": raw}
        if isinstance(body, dict):
            body.pop("audio_base64", None)
        return exc.code, body if isinstance(body, dict) else {}, (time.monotonic() - started) * 1000.0, f"HTTP {exc.code}: {body}"
    except Exception as exc:
        return 0, {}, (time.monotonic() - started) * 1000.0, f"{type(exc).__name__}: {exc}"


def timeout_for(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 1.0:
        raise BudgetExceeded("budget verticale esaurito")
    return min(HTTP_TIMEOUT, remaining)


def load_asset():
    if not ASSET.is_file():
        raise RuntimeError(f"asset assente: {ASSET}")
    spec = importlib.util.spec_from_file_location("sara_stress_asset", ASSET)
    if spec is None or spec.loader is None:
        raise RuntimeError("impossibile importare asset stress")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def specs_from(asset) -> Dict[str, Dict[str, Any]]:
    verticals = asset.VERTICALS
    return {
        "parrucchiere": dict(
            label="Parrucchiere / Barbiere",
            api="salone",
            booking=verticals["salone"]["booking_conversations"][0],
            faq=verticals["salone"]["faq"][:3],
            guard=verticals["salone"]["guardrail_wrong_service"][0],
            argument=(
                "Perché conviene fare una consulenza prima del colore?",
                ["color", "capell", "risultat", "personalizz", "tono"],
            ),
            identity=["salone", "parrucch", "capell", "taglio", "piega"],
            forbidden=["officina", "tagliand", "gomm", "odontoiatr",
                       "fisioterap", "palestra", "pilates"],
            db=["salone", "hair", "barbiere"],
        ),
        "officina": dict(
            label="Officina Auto",
            api="auto",
            booking=verticals["auto"]["booking_conversations"][0],
            faq=verticals["auto"]["faq"][:3],
            guard=verticals["auto"]["guardrail_wrong_service"][0],
            argument=(
                "Perché è importante fare il tagliando regolarmente?",
                ["tagliand", "manutenz", "sicurezza", "motore", "guast"],
            ),
            identity=["officina", "auto", "tagliand", "gomm", "meccan"],
            forbidden=["parrucch", "capell", "piega", "odontoiatr",
                       "fisioterap", "palestra", "pilates", "estetic"],
            db=["auto", "gommista"],
        ),
        "dentista": dict(
            label="Studio Odontoiatrico",
            api="odontoiatra",
            booking=verticals["medical"]["booking_conversations"][0],
            faq=[
                ("Quanto costa una visita odontoiatrica?",
                 ["prezzo", "euro", "costo", "odontoiatr"]),
                ("Gestite le urgenze dentali?",
                 ["urgen", "dolor", "dent", "appuntament", "contatt"]),
                ("Fate anche igiene dentale o pulizia dei denti?",
                 ["igiene", "pulizia", "dent", "ablazione"]),
            ],
            guard=verticals["medical"]["guardrail_wrong_service"][0],
            argument=(
                "Perché è utile fare controlli dentali periodici?",
                ["controll", "preven", "dent", "carie", "salute"],
            ),
            identity=["studio", "dent", "odontoiatr", "igiene", "visita"],
            forbidden=["officina", "tagliand", "gomm", "parrucch",
                       "capell", "palestra", "pilates", "estetic", "fisioterap"],
            db=["odontoiatra", "medical", "medico"],
        ),
        "fisioterapia": dict(
            label="Studio di Fisioterapia",
            api="fisioterapia",
            booking=verticals["medical"]["booking_conversations"][1],
            faq=[
                ("Quanto costa una seduta di fisioterapia?",
                 ["prezzo", "euro", "costo", "fisioterap"]),
                ("Quanto dura una seduta?",
                 ["durata", "minut", "ora", "seduta"]),
                ("Serve la prescrizione medica?",
                 ["prescrizion", "medic", "necessar", "serve", "dipende"]),
            ],
            guard=verticals["medical"]["guardrail_wrong_service"][1],
            argument=(
                "Perché è utile seguire un ciclo di fisioterapia?",
                ["fisioterap", "recuper", "sedut", "continuit", "dolor"],
            ),
            identity=["studio", "fisioterap", "riabilit", "sedut", "recuper"],
            forbidden=["officina", "tagliand", "gomm", "parrucch",
                       "capell", "odontoiatr", "dent", "estetic"],
            db=["fisioterapia", "medical", "medico"],
        ),
        "palestra": dict(
            label="Palestra / Centro Fitness",
            api="palestra",
            booking=verticals["palestra"]["booking_conversations"][0],
            faq=verticals["palestra"]["faq"][:3],
            guard=verticals["palestra"]["guardrail_wrong_service"][0],
            argument=(
                "Quali vantaggi offre seguire un personal trainer?",
                ["personal", "trainer", "allen", "obiettiv", "scheda"],
            ),
            identity=["palestra", "fitness", "allen", "pilates", "trainer"],
            forbidden=["officina", "tagliand", "gomm", "parrucch",
                       "capell", "odontoiatr", "dent", "estetic", "laser"],
            db=["palestra", "wellness", "personal_trainer"],
        ),
        "estetica": dict(
            label="Centro Estetico",
            api="beauty",
            booking=verticals["beauty"]["booking_conversations"][0],
            faq=verticals["beauty"]["faq"][:3],
            guard=verticals["beauty"]["guardrail_wrong_service"][0],
            argument=(
                "Perché fare una consulenza prima dell'epilazione laser?",
                ["laser", "pelle", "tratt", "personalizz", "controindic"],
            ),
            identity=["centro", "estetic", "viso", "laser", "trattament"],
            forbidden=["officina", "tagliand", "gomm", "odontoiatr",
                       "dent", "palestra", "pilates", "parrucch", "capell"],
            db=["beauty", "estetista_corpo", "estetista_viso"],
        ),
    }


# ─── DB helpers ────────────────────────────────────────────────────────────────

def columns(connection: sqlite3.Connection, table: str) -> List[str]:
    name = table.replace('"', '""')
    return [str(row[1]) for row in connection.execute(f'PRAGMA table_info("{name}")')]


def resolve_db() -> Optional[Path]:
    candidates: List[Path] = []
    if os.environ.get("FLUXION_DB_PATH"):
        candidates.append(Path(os.environ["FLUXION_DB_PATH"]).expanduser())
    home = Path.home()
    candidates += [
        home / "Library" / "Application Support" / "com.fluxion.desktop" / "fluxion.db",
        home / "Library" / "Application Support" / "fluxion" / "fluxion.db",
        VOICE / "fluxion.db",
    ]
    return next((p for p in candidates if p.is_file()), None)


def seed_clients(specs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    db = resolve_db()
    if db is None:
        raise RuntimeError("fluxion.db non trovato")
    STATE.db = db
    token = "".join(chr(97 + int(c, 16)) for c in uuid.uuid4().hex[:7])
    first_names = ["Marco", "Giulia", "Luca", "Elena", "Paolo", "Sara"]
    result: Dict[str, Dict[str, Any]] = {}

    with sqlite3.connect(str(db), timeout=10) as conn:
        avail = set(columns(conn, "clienti"))
        required = {"nome", "cognome", "telefono"}
        if not required.issubset(avail):
            raise RuntimeError(f"schema clienti incompatibile: {sorted(avail)}")

        for idx, key in enumerate(specs):
            proposed_id = uuid.uuid4().hex
            values = {
                "nome": first_names[idx],
                "cognome": f"StressV2{key.capitalize()}{token}",
                "telefono": f"389{(int(time.time()) + idx) % 10000000:07d}",
                "note": STATE.tag,
                "fonte": STATE.source,
                "created_at": datetime.now().isoformat(),
                "deleted_at": None,
            }
            names = [n for n in values if n in avail]
            query = (f"INSERT INTO clienti ({','.join(names)}) "
                     f"VALUES ({','.join('?' for _ in names)})")
            try:
                cursor = conn.execute(query, tuple(values[n] for n in names))
            except sqlite3.IntegrityError:
                if "id" not in avail:
                    raise
                names = ["id"] + names
                query = (f"INSERT INTO clienti ({','.join(names)}) "
                         f"VALUES ({','.join('?' for _ in names)})")
                cursor = conn.execute(query, tuple(
                    proposed_id if n == "id" else values[n] for n in names
                ))

            row = conn.execute(
                "SELECT id FROM clienti WHERE telefono=? ORDER BY rowid DESC LIMIT 1",
                (values["telefono"],),
            ).fetchone()
            client_id = row[0] if row and row[0] is not None else proposed_id
            if row and row[0] is None:
                conn.execute("UPDATE clienti SET id=? WHERE rowid=?",
                             (proposed_id, cursor.lastrowid))
            result[key] = {"id": client_id, **values}

        conn.commit()

    STATE.clients = result
    return result


def cleanup() -> None:
    if STATE.cleaned:
        return
    STATE.cleaned = True

    if STATE.db is None or not STATE.db.is_file():
        STATE.cleanup = ("OK: nessuna fixture creata" if not STATE.clients
                         else "FAIL: DB non risolto")
        return

    try:
        with sqlite3.connect(str(STATE.db), timeout=10) as conn:
            conn.execute("PRAGMA foreign_keys=OFF")
            ids = [item["id"] for item in STATE.clients.values()]
            if not ids:
                STATE.cleanup = "OK: nessuna fixture creata"
                return

            marks = ",".join("?" for _ in ids)
            tables = [row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )]
            appt_ids: List[Any] = []
            if "appuntamenti" in tables and "cliente_id" in columns(conn, "appuntamenti"):
                appt_ids = [row[0] for row in conn.execute(
                    f"SELECT id FROM appuntamenti WHERE cliente_id IN ({marks})", ids
                )]

            for table in tables:
                if table in {"clienti", "appuntamenti"}:
                    continue
                avail = set(columns(conn, table))
                qt = table.replace('"', '""')
                for col in ("appuntamento_id", "appointment_id"):
                    if col in avail and appt_ids:
                        am = ",".join("?" for _ in appt_ids)
                        conn.execute(f'DELETE FROM "{qt}" WHERE "{col}" IN ({am})', appt_ids)
                for col in ("cliente_id", "client_id"):
                    if col in avail:
                        conn.execute(f'DELETE FROM "{qt}" WHERE "{col}" IN ({marks})', ids)

            if "appuntamenti" in tables:
                conn.execute(f"DELETE FROM appuntamenti WHERE cliente_id IN ({marks})", ids)
            conn.execute(f"DELETE FROM clienti WHERE id IN ({marks})", ids)
            conn.commit()

            remaining = conn.execute(
                f"SELECT COUNT(*) FROM clienti WHERE id IN ({marks})", ids
            ).fetchone()[0]
            STATE.cleanup = (
                f"OK: rimosse {len(ids)} fixture e relativi dati"
                if remaining == 0
                else f"FAIL: {remaining} fixture residue"
            )
    except Exception as exc:
        STATE.cleanup = f"FAIL: {type(exc).__name__}: {exc}"


def restore() -> None:
    try:
        reset = request("/api/voice/reset", {}, timeout=5)
        switched = request("/api/voice/set-vertical", {"vertical": RESTORE_VERTICAL}, timeout=8)
        STATE.restored = (
            "OK: salone ripristinato"
            if reset[0] == 200 and switched[0] == 200 and switched[1].get("success")
            else f"FAIL: reset={reset[0]}, set={switched[0]}"
        )
    except Exception as exc:
        STATE.restored = f"FAIL: {type(exc).__name__}: {exc}"


def final_cleanup() -> None:
    cleanup()
    if STATE.restored == ND:
        restore()


atexit.register(final_cleanup)


def on_signal(signum, frame) -> None:
    cleanup()
    restore()
    raise KeyboardInterrupt


for _sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(_sig, on_signal)


# ─── Scenario helpers ──────────────────────────────────────────────────────────

def start_scenario(api_vertical: str, deadline: float) -> Tuple[Optional[str], str]:
    reset = request("/api/voice/reset", {}, timeout=timeout_for(deadline))
    if reset[0] != 200 or not reset[1].get("success"):
        return None, reset[3] or str(reset[1])
    switched = request("/api/voice/set-vertical", {"vertical": api_vertical},
                       timeout=timeout_for(deadline))
    if switched[0] != 200 or not switched[1].get("success"):
        return None, switched[3] or str(switched[1])
    time.sleep(0.12)
    return switched[1].get("session_id"), ""


def ask(result: VResult, scenario: str, text: str,
        session_id: Optional[str], deadline: float) -> Turn:
    payload: Dict[str, Any] = {"text": text}
    if session_id:
        payload["session_id"] = session_id
    status, body, elapsed, error = request("/api/voice/process", payload,
                                           timeout=timeout_for(deadline))
    turn = Turn(
        scenario=scenario,
        user=text,
        response=str(body.get("response") or ""),
        fsm=str(body.get("fsm_state") or ""),
        layer=str(body.get("layer") or ""),
        latency_ms=elapsed,
        success=(status == 200 and bool(body.get("success"))),
        error=error or str(body.get("error") or ""),
        booking_action=(body.get("booking_action")
                        if isinstance(body.get("booking_action"), dict) else None),
    )
    result.turns.append(turn)
    return turn


def begin(result: VResult, category: str, scenario: str,
          deadline: float) -> Optional[str]:
    session_id, error = start_scenario(result.api, deadline)
    if error:
        result.add(category, FAIL_DRIVER, scenario,
                   f"reset/set-vertical fallito: {error}")
        return None
    return session_id


def failed_turn(result: VResult, category: str, scenario: str, turn: Turn) -> bool:
    if turn.success:
        return False
    result.add(category, FAIL_DRIVER, scenario,
               f"errore HTTP/runtime turno: {turn.error or ND}", turn)
    return True


def service_tokens(name: str) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9]+", norm(name))
            if len(t) >= 4 and t not in STOPWORDS]


def match_services(text: str, services: Sequence[str]) -> List[str]:
    value = norm(text)
    found = []
    for svc in services:
        tokens = service_tokens(svc)
        hits = sum(t in value for t in tokens)
        if norm(svc) in value or (tokens and hits >= (1 if len(tokens) == 1 else 2)):
            found.append(svc)
    return found


def catalog_for(aliases: Sequence[str]) -> Tuple[List[str], str]:
    path = next((VERTICAL_DBS / f"{n}.db" for n in aliases
                 if (VERTICAL_DBS / f"{n}.db").is_file()), None)
    if path is None:
        return [], "DB verticale non trovato"
    try:
        with sqlite3.connect(str(path), timeout=5) as conn:
            avail = set(columns(conn, "servizi"))
            if "nome" not in avail:
                return [], f"servizi.nome assente in {path.name}"
            sql = "SELECT nome FROM servizi"
            if "attivo" in avail:
                sql += " WHERE attivo=1"
            if "ordine" in avail:
                sql += " ORDER BY ordine"
            return [str(row[0]).strip() for row in conn.execute(sql) if row[0]], str(path)
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"


def next_date(index: int) -> str:
    target = date.today() + timedelta(days=35 + index * 4)
    desired = (index + 1) % 5
    while target.weekday() != desired:
        target += timedelta(days=1)
    return f"{WEEKDAYS[target.weekday()]} {target.day} {MONTHS[target.month - 1]} {target.year}"


def first_time(text: str) -> Optional[str]:
    match = re.search(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b", text)
    return f"{int(match.group(1)):02d}:{match.group(2)}" if match else None


# ─── Driver FSM v2 ─────────────────────────────────────────────────────────────
# CORREZIONE CHIAVE rispetto a v1: ogni turno risponde allo stato FSM ATTUALE.
# Non si usano flag temporali che consumano turni nello stato sbagliato.

def fsm_reply(
    state: str,
    response_text: str,
    client: Dict[str, Any],
    spec: Dict[str, Any],
    target_date: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Ritorna (testo_da_inviare, classificazione_driver).
    classificazione_driver è None se lo stato è gestito, FAIL_DRIVER se inatteso.
    Ritorna (None, None) se lo stato è terminale (booking_created).
    """
    s = norm(state).replace(" ", "_")

    if s == "waiting_service":
        return f"Vorrei prenotare {spec['booking']['name']}", None
    elif s in ("waiting_name", "disambiguating_name"):
        return f"Sono {client['nome']} {client['cognome']}", None
    elif s == "confirming_name":
        return "Sì, sono io", None
    elif s in ("waiting_surname", "registering_surname"):
        return client["cognome"], None
    elif s == "disambiguating_birth_date":
        return "Sono nato il primo gennaio 1985", None
    elif s == "propose_registration":
        return "Sì, registrami", None
    elif s == "registering_phone":
        return client["telefono"], None
    elif s == "confirming_phone":
        return "Sì, confermo il numero", None
    elif s == "waiting_date":
        # INVIO IMMEDIATO — bug principale della v1 era qui
        return target_date, None
    elif s == "waiting_time":
        offered = first_time(response_text)
        return (f"Alle {offered}" if offered else "Alle 10:00"), None
    elif s == "waiting_operator":
        return "Il primo operatore disponibile", None
    elif s == "confirming":
        return "Sì, confermo", None
    elif s == "booking_created":
        return None, None  # terminale OK
    elif s == "completed":
        # Sara usa talvolta 'completed' come alternativa a booking_created.
        # Gestiamo come terminale: il check action viene fatto nel loop booking.
        return None, None  # terminale — classificazione in run_booking
    else:
        # Stato non riconosciuto → FAIL_DRIVER
        return None, FAIL_DRIVER


def run_booking(
    result: VResult,
    spec: Dict[str, Any],
    client: Dict[str, Any],
    deadline: float,
    index: int,
) -> None:
    scenario = f"BOOKING {spec['booking']['name']}"
    session_id = begin(result, "BOOKING", scenario, deadline)
    if session_id is None:
        return

    target_date = next_date(index)

    # Primo turno: apertura richiesta
    turn = ask(result, scenario,
               f"Vorrei prenotare {spec['booking']['name']}", session_id, deadline)
    if failed_turn(result, "BOOKING", scenario, turn):
        return

    prev_state = ""
    loop_count = 0
    completed: Optional[Turn] = None
    fsm_sequence: List[str] = [norm(turn.fsm).replace(" ", "_")]

    for turn_num in range(MAX_BOOKING_TURNS):
        action = turn.booking_action or {}
        state = norm(turn.fsm).replace(" ", "_")
        fsm_sequence.append(state)

        if action.get("action") == "booking_created":
            completed = turn
            break

        # Gestione stato 'completed': Sara ha completato ma action != booking_created
        if state == "completed":
            if action.get("action") == "booking_created":
                completed = turn
            else:
                STATE.dbg(
                    f"[BOOKING:{spec['label']}] FSM=completed ma "
                    f"action={action.get('action','ND')} (atteso booking_created)\n"
                    f"  sequenza: {' → '.join(fsm_sequence)}"
                )
                result.add("BOOKING", FAIL_SARA, scenario,
                           f"FSM=completed ma booking_action.action="
                           f"'{action.get('action','ND')}' (atteso booking_created). "
                           f"Sara completa il booking ma non emette l'action corretta.",
                           turn)
            return

        # Rilevamento loop FSM
        if state == prev_state and state != "":
            loop_count += 1
            if loop_count >= 3:
                STATE.dbg(
                    f"[BOOKING:{spec['label']}] loop FSM rilevato: "
                    f"stato '{state}' ripetuto {loop_count + 1}x consecutivi"
                )
                result.add("BOOKING", FAIL_SARA, scenario,
                           f"loop FSM: stato '{state}' ripetuto {loop_count + 1}x", turn)
                return
        else:
            loop_count = 0
        prev_state = state

        text, driver_class = fsm_reply(state, turn.response, client, spec, target_date)

        if driver_class == FAIL_DRIVER:
            STATE.dbg(
                f"[BOOKING:{spec['label']}] stato FSM non gestito: '{state}' al turno {turn_num + 1}\n"
                f"  sequenza: {' → '.join(fsm_sequence)}"
            )
            result.add("BOOKING", FAIL_DRIVER, scenario,
                       f"stato FSM non gestito dal driver: '{state}' (turno {turn_num + 1})", turn)
            return

        if text is None:
            # booking_created è terminale — gestito sopra, questo è edge case
            break

        turn = ask(result, scenario, text, session_id, deadline)
        if failed_turn(result, "BOOKING", scenario, turn):
            return

    if completed is None:
        last_state = norm(result.turns[-1].fsm).replace(" ", "_") if result.turns else "?"
        seq_str = " → ".join(fsm_sequence)
        STATE.dbg(
            f"[BOOKING:{spec['label']}] booking_created non osservato\n"
            f"  ultimo stato: {last_state}\n"
            f"  sequenza: {seq_str}"
        )
        # Determina FAIL_SARA vs FAIL_DRIVER
        if last_state in BOOKING_STATES:
            # Sara era in uno stato di booking valido ma non ha creato la prenotazione
            result.add("BOOKING", FAIL_SARA, scenario,
                       f"booking_created assente dopo progressione FSM valida. "
                       f"Ultimo stato: {last_state}. Sequenza: {seq_str}",
                       result.turns[-1] if result.turns else None)
        else:
            result.add("BOOKING", FAIL_DRIVER, scenario,
                       f"turni esauriti ({MAX_BOOKING_TURNS}) senza booking_created. "
                       f"Stato finale non in FSM booking: {last_state}",
                       result.turns[-1] if result.turns else None)
        return

    # Booking completato — verifica coerenza
    context = (completed.booking_action or {}).get("context") or {}
    returned = str(context.get("service") or context.get("service_display") or "")
    if returned and not match_services(returned, [spec["booking"]["name"]]):
        result.add("BOOKING", WARN, scenario,
                   f"booking creato con servizio differente: {returned}", completed)
    else:
        result.add("BOOKING", OK, scenario, "prenotazione creata end-to-end", completed)


# ─── Scenari secondari (invariati dalla v1, aggiornata classificazione FAIL) ──

def run_faq(result: VResult, spec: Dict[str, Any], deadline: float) -> None:
    for num, (question, expected) in enumerate(spec["faq"][:3], 1):
        scenario = f"FAQ-{num}"
        session_id = begin(result, "FAQ", scenario, deadline)
        if session_id is None:
            continue
        turn = ask(result, scenario, question, session_id, deadline)
        if failed_turn(result, "FAQ", scenario, turn):
            continue

        matched = has(turn.response, expected)
        in_booking = norm(turn.fsm).replace(" ", "_") in BOOKING_STATES

        if in_booking and not matched:
            result.add("FAQ", FAIL_SARA, scenario,
                       "FAQ deviata nel booking senza risposta", turn)
        elif matched and norm(turn.layer).startswith(("l1", "l3")) and not in_booking:
            result.add("FAQ", OK, scenario,
                       "risposta pertinente e KB/exact grounded", turn)
        elif matched and not in_booking:
            result.add("FAQ", WARN, scenario,
                       f"pertinente ma layer={turn.layer or ND}; KB non certificata", turn)
        elif turn.response.strip() and not in_booking:
            result.add("FAQ", WARN, scenario,
                       "risposta presente ma keyword attese non trovate", turn)
        else:
            result.add("FAQ", FAIL_SARA, scenario,
                       "risposta FAQ vuota o incoerente", turn)


def run_guardrail(result: VResult, spec: Dict[str, Any], deadline: float) -> None:
    scenario = "GUARDRAIL fuori competenza"
    session_id = begin(result, "GUARDRAIL", scenario, deadline)
    if session_id is None:
        return
    question, expected = spec["guard"]
    turn = ask(result, scenario, question, session_id, deadline)
    if failed_turn(result, "GUARDRAIL", scenario, turn):
        return

    response = norm(turn.response)
    refusal = has(turn.response, [
        "non posso", "non ci occup", "fuori competenza",
        "non rientra", "non offriamo", "non forniamo",
        "non trattiamo", "non e un servizio",
    ])
    domain = [item for item in expected if norm(item) not in {"non", "no"}]
    blocked = refusal or ("non" in response[:120] and has(turn.response, domain))
    in_booking = norm(turn.fsm).replace(" ", "_") in BOOKING_STATES

    if in_booking:
        result.add("GUARDRAIL", FAIL_SARA, scenario,
                   "servizio fuori dominio accettato nel booking", turn)
    elif blocked:
        result.add("GUARDRAIL", OK, scenario, "richiesta fuori dominio rifiutata", turn)
    elif turn.response.strip():
        result.add("GUARDRAIL", WARN, scenario,
                   "rifiuto non esplicito, ma booking non avviato", turn)
    else:
        result.add("GUARDRAIL", FAIL_SARA, scenario, "nessuna risposta", turn)


def run_catalog(result: VResult, spec: Dict[str, Any], deadline: float) -> None:
    scenario = "CATALOGO servizi vs knowledge base"
    services, source = catalog_for(spec["db"])

    if not services:
        result.add("CATALOGO", FAIL_DRIVER, scenario,
                   f"catalogo DB non leggibile: {source}")
        return

    if not match_services(spec["booking"]["name"], services):
        result.add("CATALOGO", FAIL_SARA, scenario,
                   f"servizio booking '{spec['booking']['name']}' assente da {Path(source).name}")

    session_id = begin(result, "CATALOGO", scenario, deadline)
    if session_id is None:
        return

    turn = ask(result, scenario,
               "Quali servizi posso prenotare con voi? Elencami i principali.",
               session_id, deadline)
    if failed_turn(result, "CATALOGO", scenario, turn):
        return

    matches = match_services(turn.response, services)
    in_booking = norm(turn.fsm).replace(" ", "_") in BOOKING_STATES

    if in_booking:
        result.add("CATALOGO", FAIL_SARA, scenario,
                   "domanda catalogo deviata nel booking", turn)
    elif has(turn.response, spec["forbidden"]):
        result.add("CATALOGO", FAIL_SARA, scenario,
                   "catalogo contaminato da altro verticale", turn)
    elif len(matches) >= min(2, len(services)):
        result.add("CATALOGO", OK, scenario,
                   f"coerente con DB: {len(matches)}/{len(services)} servizi", turn)
    elif len(matches) == 1:
        result.add("CATALOGO", WARN, scenario,
                   f"catalogo parziale: 1/{len(services)} servizio", turn)
    else:
        result.add("CATALOGO", FAIL_SARA, scenario,
                   f"nessun servizio DB riconosciuto ({Path(source).name})", turn)


def single_content(
    result: VResult, spec: Dict[str, Any], deadline: float,
    category: str, scenario: str, question: str, expected: Sequence[str],
) -> None:
    session_id = begin(result, category, scenario, deadline)
    if session_id is None:
        return
    turn = ask(result, scenario, question, session_id, deadline)
    if failed_turn(result, category, scenario, turn):
        return

    hits = sum(norm(item) in norm(turn.response) for item in expected)
    in_booking = norm(turn.fsm).replace(" ", "_") in BOOKING_STATES

    if in_booking:
        result.add(category, FAIL_SARA, scenario,
                   "domanda informativa deviata nel booking", turn)
    elif has(turn.response, spec["forbidden"]):
        result.add(category, FAIL_SARA, scenario,
                   "risposta contaminata da altro verticale", turn)
    elif hits >= 2:
        result.add(category, OK, scenario, f"contenuto pertinente ({hits} segnali)", turn)
    elif hits == 1 and turn.response.strip():
        result.add(category, WARN, scenario, "contenuto generico ma compatibile", turn)
    else:
        result.add(category, FAIL_SARA, scenario, "contenuto non pertinente o vuoto", turn)


def finalize_latency(result: VResult) -> None:
    if not result.turns:
        result.add("LATENZA", FAIL_SARA, "LATENZA", "nessun turno misurabile")
        return
    slow = sum(t.latency_ms > SLOW_MS for t in result.turns)
    if slow == 0:
        result.add("LATENZA", OK, "LATENZA",
                   f"tutti i {len(result.turns)} turni <= {SLOW_MS:.0f}ms")
    elif slow == 1:
        result.add("LATENZA", WARN, "LATENZA", "1 turno sopra 5000ms")
    else:
        result.add("LATENZA", FAIL_SARA, "LATENZA",
                   f"{slow}/{len(result.turns)} turni sopra 5000ms")


def fill_missing(result: VResult, reason: str) -> None:
    for category in ("BOOKING", "FAQ", "GUARDRAIL", "CATALOGO", "RISPOSTE", "ARGOMENTAZIONI"):
        if result.status(category) == ND:
            result.add(category, FAIL_DRIVER, "BUDGET", reason)


def run_vertical(
    key: str, spec: Dict[str, Any], client: Optional[Dict[str, Any]],
    index: int, global_deadline: float,
) -> VResult:
    result = VResult(key, spec["label"], spec["api"])
    started = time.monotonic()
    deadline = min(started + VERTICAL_BUDGET, global_deadline)

    try:
        if client:
            run_booking(result, spec, client, deadline, index)
        else:
            result.add("BOOKING", FAIL_DRIVER, "BOOKING", "fixture DB non disponibile")

        run_faq(result, spec, deadline)
        run_guardrail(result, spec, deadline)
        run_catalog(result, spec, deadline)

        single_content(result, spec, deadline, "RISPOSTE", "RISPOSTA identità e ambito",
                       "Chi siete e di quali servizi vi occupate?", spec["identity"])

        question, expected = spec["argument"]
        single_content(result, spec, deadline, "ARGOMENTAZIONI",
                       "ARGOMENTAZIONE settoriale", question, expected)

    except BudgetExceeded as exc:
        fill_missing(result, f"verticale oltre budget {VERTICAL_BUDGET:.0f}s: {exc}")
    except Exception as exc:
        result.add("SETUP", FAIL_DRIVER, "RUNTIME", f"{type(exc).__name__}: {exc}")
        fill_missing(result, "scenari non completati per errore runtime")

    result.duration_s = time.monotonic() - started
    finalize_latency(result)
    return result


# ─── Report ────────────────────────────────────────────────────────────────────

def evidence(check: Check) -> List[str]:
    if check.turn is None:
        return ["    USER: ND", "    SARA: ND", "    FSM: ND",
                "    LAYER: ND", "    LATENCY_MS: ND", "    ERROR: ND"]
    t = check.turn
    lines = [f"    USER: {t.user}"]
    lines += [f"    SARA: {line}" for line in (t.response.splitlines() or [ND])]
    lines += [
        f"    FSM: {t.fsm or ND}",
        f"    LAYER: {t.layer or ND}",
        f"    LATENCY_MS: {t.latency_ms:.1f}",
        f"    BOOKING_ACTION: {t.booking_action or ND}",
        f"    ERROR: {t.error or ND}",
    ]
    return lines


def best_vertical(results: Sequence[VResult]) -> str:
    eligible = [r for r in results if r.turns]
    if not eligible:
        return ND

    def score(r: VResult) -> Tuple[int, int, float, int, str]:
        return (
            r.fail_sara_count(),
            r.fail_driver_count(),
            r.latencies().get("p95", float("inf")),
            sum(1 for c in r.checks if c.level == WARN),
            r.label,
        )

    return min(eligible, key=score).label


def report_text(
    results: Sequence[VResult],
    started: str,
    duration: float,
    health: Tuple[int, Dict[str, Any], float, str],
    voip: Tuple[int, Dict[str, Any], float, str],
    preflight_notes: List[str],
) -> str:
    sip = voip[1].get("sip") if isinstance(voip[1].get("sip"), dict) else {}
    lines = [
        "## Stress verticali v2 — certificazione contenuto Sara",
        "",
        f"**Run ID:** {STATE.tag}",
        f"**Commit:** {_git_head()}",
        f"**Inizio:** {started}",
        f"**Durata:** {duration:.1f}s / budget {RUN_BUDGET:.0f}s",
        f"**Endpoint:** {BASE}",
        f"**Health:** HTTP {health[0]} · {health[1].get('status', ND)}",
        (f"**VoIP:** HTTP {voip[0]} · "
         f"registered={sip.get('registered', ND)} · "
         f"reg_status={sip.get('reg_status', ND)}"),
        f"**Preflight:** {'OK' if STATE.preflight_ok else 'FAIL'}",
        "",
        "### Preflight notes",
        "",
    ]
    for note in preflight_notes:
        lines.append(f"- {note}")
    lines += [
        "",
        f"**Cleanup DB:** {STATE.cleanup}",
        f"**Verticale ripristinato:** {STATE.restored}",
        "",
        ("| Verticale | Esito | KB | Risposte | Booking | FAQ | "
         "Guardrail | Catalogo | Argomentazioni | Latenza | "
         "AVG ms | P95 ms | MAX ms | Turni | Durata s |"),
        ("|---|---:|---:|---:|---:|---:|---:|---:|---:|"
         "---:|---:|---:|---:|---:|---:|"),
    ]

    for r in results:
        lat = r.latencies()
        if lat:
            lines.append(
                f"| {r.label} | {r.overall()} | {r.kb()} "
                f"| {r.status('RISPOSTE')} | {r.status('BOOKING')} "
                f"| {r.status('FAQ')} | {r.status('GUARDRAIL')} "
                f"| {r.status('CATALOGO')} | {r.status('ARGOMENTAZIONI')} "
                f"| {r.status('LATENZA')} "
                f"| {lat.get('avg', 0):.0f} | {lat.get('p95', 0):.0f} "
                f"| {lat.get('max', 0):.0f} | {len(r.turns)} | {r.duration_s:.1f} |"
            )
        else:
            lines.append(
                f"| {r.label} | {r.overall()} | {r.kb()} "
                f"| {r.status('RISPOSTE')} | {r.status('BOOKING')} "
                f"| {r.status('FAQ')} | {r.status('GUARDRAIL')} "
                f"| {r.status('CATALOGO')} | {r.status('ARGOMENTAZIONI')} "
                f"| {r.status('LATENZA')} "
                f"| {ND} | {ND} | {ND} | 0 | {r.duration_s:.1f} |"
            )

    # Conteggi separati FAIL_SARA / FAIL_DRIVER
    total_sara = sum(r.fail_sara_count() for r in results)
    total_driver = sum(r.fail_driver_count() for r in results)
    total_warn = sum(sum(1 for c in r.checks if c.level == WARN) for r in results)

    lines += [
        "",
        f"**FAIL_SARA totali:** {total_sara}",
        f"**FAIL_DRIVER totali:** {total_driver}",
        f"**WARN totali:** {total_warn}",
        "",
        "### FAIL — dettaglio",
        "",
    ]

    fails_and_warns = [
        (r, c)
        for r in results
        for c in r.checks
        if c.level in (FAIL_SARA, FAIL_DRIVER, WARN)
    ]

    if not fails_and_warns:
        lines.append("Nessun FAIL o WARN.")
    else:
        for r, c in fails_and_warns:
            lines += [
                f"#### [{c.level}] {r.label} — {c.category} — {c.scenario}",
                f"- Timestamp: {c.ts}",
                f"- Motivo: {c.message}",
                "- Evidenza verbatim:",
                *evidence(c),
                "",
            ]

    lines += [
        "",
        f"**Verticale PIÙ PRONTO:** {best_vertical(results)}",
        "(criteri: meno FAIL_SARA, poi meno FAIL_DRIVER, poi P95 migliore)",
        "",
    ]
    return "\n".join(lines)


def _git_head() -> str:
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True,
            cwd=str(ROOT), timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def write_debug(notes: List[str]) -> None:
    """Scrive il file diagnostico per Sol se ci sono problemi."""
    import platform
    import hashlib

    script_path = Path(__file__).resolve()
    sha256 = "ND"
    try:
        sha256 = hashlib.sha256(script_path.read_bytes()).hexdigest()
    except Exception:
        pass

    db_path = resolve_db()
    lines = [
        "# stress_verticali_v2_debug.md — diagnostica per Sol",
        "",
        "## 1. Ambiente",
        f"- Data/ora: {now()}",
        f"- OS: {platform.system()} {platform.release()} / Python {sys.version.split()[0]}",
        f"- Directory esecuzione: {os.getcwd()}",
        f"- Commit HEAD: {_git_head()}",
        f"- Repository root: {ROOT}",
        f"- Database clienti: {db_path or 'NON TROVATO'}",
        f"- Vertical DBs path: {VERTICAL_DBS}",
        f"- FLUXION_DB_PATH env: {os.environ.get('FLUXION_DB_PATH', 'non impostato')}",
        "",
        "### Porte",
        f"- :3002 (voice agent): vedi preflight",
        f"- :3003: non usata da questo script",
        "",
        "## 2. File",
        f"- Script: {script_path}",
        f"- SHA-256: {sha256}",
        f"- Asset E2E: {ASSET} ({'presente' if ASSET.is_file() else 'ASSENTE'})",
        f"- Modifiche v1→v2: vedi header del file",
        "",
        "## 3. Preflight e note di esecuzione",
        "",
    ]
    for note in notes:
        lines.append(f"- {note}")

    lines += [
        "",
        "## 4. Debug booking",
        "",
    ]
    for dbg_line in STATE.debug_lines:
        lines.append(dbg_line)
        lines.append("")

    lines += [
        "",
        "## 5. Fixture e cleanup",
        f"- Tag run: {STATE.tag}",
        f"- DB: {STATE.db}",
        f"- Clienti creati: {len(STATE.clients)}",
    ]
    for key, client in STATE.clients.items():
        lines.append(f"  - {key}: id={client.get('id')} tel={client.get('telefono')}")

    lines += [
        f"- Stato cleanup: {STATE.cleanup}",
        f"- Verticale ripristinato: {STATE.restored}",
        "",
        "## Richiesta di correzione a Sol",
        "",
        "Se ci sono problemi, descrivili qui:",
        "",
    ]
    atomic_write(DEBUG, "\n".join(lines))


def failed_results(specs: Dict[str, Dict[str, Any]], reason: str) -> List[VResult]:
    output = []
    for key, spec in specs.items():
        r = VResult(key, spec["label"], spec["api"])
        for cat in ("BOOKING", "FAQ", "GUARDRAIL", "CATALOGO", "RISPOSTE", "ARGOMENTAZIONI", "LATENZA"):
            r.add(cat, FAIL_DRIVER, "PREFLIGHT", reason)
        output.append(r)
    return output


def print_summary(results: Sequence[VResult]) -> None:
    """stdout ≤30 righe: una per verticale + riepilogo + cleanup."""
    for r in results:
        lat = r.latencies()
        suffix = f"p95={lat['p95']:.0f}ms" if lat else "p95=ND"
        print(
            f"{r.label}: {r.overall()} "
            f"| kb={r.kb()} risposte={r.status('RISPOSTE')} "
            f"booking={r.status('BOOKING')} faq={r.status('FAQ')} "
            f"guardrail={r.status('GUARDRAIL')} catalogo={r.status('CATALOGO')} "
            f"arg={r.status('ARGOMENTAZIONI')} {suffix} "
            f"[sara={r.fail_sara_count()} drv={r.fail_driver_count()}]"
        )

    total_sara = sum(r.fail_sara_count() for r in results)
    total_driver = sum(r.fail_driver_count() for r in results)
    total_warn = sum(sum(1 for c in r.checks if c.level == WARN) for r in results)
    print(
        f"RIEPILOGO: verticali={len(results)} "
        f"FAIL_SARA={total_sara} FAIL_DRIVER={total_driver} WARN={total_warn} "
        f"più_pronto={best_vertical(results)} "
        f"cleanup={STATE.cleanup}"
    )


# ─── Preflight ─────────────────────────────────────────────────────────────────

def run_preflight(
    health: Tuple[int, Dict[str, Any], float, str],
    voip: Tuple[int, Dict[str, Any], float, str],
) -> Tuple[bool, List[str]]:
    """
    Verifica 12 condizioni prima della run. Ritorna (ok, note).
    """
    notes = []
    ok = True

    # 1. Commit e stato repo
    commit = _git_head()
    notes.append(f"1. commit HEAD: {commit}")

    # 2. Processo :3002
    if health[0] == 200:
        notes.append("2. processo :3002: UP")
    else:
        notes.append(f"2. processo :3002: NON RAGGIUNGIBILE (HTTP {health[0]})")
        ok = False

    # 3. /health
    h_status = health[1].get("status", "?")
    notes.append(f"3. /health: HTTP {health[0]} status={h_status}")
    if h_status != "ok":
        ok = False

    # 4. VoIP status
    sip = voip[1].get("sip") if isinstance(voip[1].get("sip"), dict) else {}
    notes.append(f"4. /api/voice/voip/status: HTTP {voip[0]}")

    # 5. registered=True
    registered = sip.get("registered", False)
    notes.append(f"5. SIP registered: {registered}")
    if not registered:
        notes.append("   ATTENZIONE: SIP non registrato — test booking potrebbero fallire")

    # 6. reg_status
    reg_status = sip.get("reg_status", "?")
    notes.append(f"6. reg_status: {reg_status}")

    # 7. Assenza chiamata/RTP attivi
    call = voip[1].get("call") if isinstance(voip[1].get("call"), dict) else {}
    busy = bool(
        voip[1].get("rtp_active") or voip[1].get("call_active")
        or call.get("active") or call.get("connected")
    )
    notes.append(f"7. linea occupata: {busy}")
    if busy:
        notes.append("   STOP: linea occupata, run non avviata")
        ok = False

    # 8. Verticale corrente
    v_status = request("/api/voice/voip/status", method="GET", timeout=5)
    current_v = v_status[1].get("vertical", "?") if v_status[0] == 200 else "?"
    notes.append(f"8. verticale corrente: {current_v}")

    # 9. Asset E2E del 14/05
    notes.append(f"9. asset E2E: {ASSET} — {'PRESENTE' if ASSET.is_file() else 'ASSENTE'}")
    if not ASSET.is_file():
        ok = False

    # 10. DB verticali
    db_found = [n for n in ["salone", "auto", "odontoiatra", "fisioterapia", "palestra", "beauty"]
                if (VERTICAL_DBS / f"{n}.db").is_file()]
    notes.append(f"10. DB verticali trovati: {db_found}")

    # 11. DB clienti
    db_clienti = resolve_db()
    notes.append(f"11. DB clienti: {db_clienti or 'NON TROVATO'}")
    if db_clienti is None:
        notes.append("    ATTENZIONE: seed fixture impossibile senza DB clienti")

    # 12. Sintassi script (già verificata se siamo qui)
    notes.append("12. sintassi script: OK (importato correttamente)")

    STATE.preflight_ok = ok
    STATE.preflight_notes = notes
    return ok, notes


# ─── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    started_monotonic = time.monotonic()
    started_wall = now()

    health = request("/health", method="GET", timeout=5)
    voip = request("/api/voice/voip/status", method="GET", timeout=5)

    preflight_ok, preflight_notes = run_preflight(health, voip)
    print(f"PREFLIGHT: {'OK' if preflight_ok else 'FAIL'}")

    # Carica asset
    try:
        specs = specs_from(load_asset())
    except Exception as exc:
        STATE.cleanup = "OK: nessuna fixture creata"
        STATE.restored = "OK: verticale non modificato"
        msg = f"FAIL asset: {type(exc).__name__}: {exc}"
        preflight_notes.append(msg)
        atomic_write(REPORT, f"## Stress verticali v2 — certificazione contenuto Sara\n\n{msg}\n")
        write_debug(preflight_notes)
        print(f"RIEPILOGO: FAIL asset={type(exc).__name__}: {exc}")
        return 1

    # Gate linea occupata
    call = voip[1].get("call") if isinstance(voip[1].get("call"), dict) else {}
    busy = bool(
        voip[1].get("rtp_active") or voip[1].get("call_active")
        or call.get("active") or call.get("connected")
    )
    if busy:
        results = failed_results(specs, "linea SIP occupata: run non avviata")
        STATE.cleanup = "OK: nessuna fixture creata"
        STATE.restored = "OK: verticale non modificato"
        atomic_write(REPORT, report_text(results, started_wall,
                     time.monotonic() - started_monotonic, health, voip, preflight_notes))
        write_debug(preflight_notes)
        print_summary(results)
        return 1

    # Gate health
    if health[0] != 200 or health[1].get("status") != "ok":
        results = failed_results(specs,
            f"pipeline :3002 non raggiungibile: HTTP {health[0]} {health[3] or health[1]}")
        STATE.cleanup = "OK: nessuna fixture creata"
        restore()
        atomic_write(REPORT, report_text(results, started_wall,
                     time.monotonic() - started_monotonic, health, voip, preflight_notes))
        write_debug(preflight_notes)
        print_summary(results)
        return 1

    # Seed fixture
    try:
        clients = seed_clients(specs)
        seed_error = ""
    except Exception as exc:
        clients = {}
        seed_error = f"{type(exc).__name__}: {exc}"
        STATE.dbg(f"[SEED] errore: {seed_error}")

    deadline = started_monotonic + RUN_BUDGET
    results: List[VResult] = []

    for index, (key, spec) in enumerate(specs.items()):
        if time.monotonic() >= deadline:
            r = VResult(key, spec["label"], spec["api"])
            fill_missing(r, "run globale oltre budget 20 minuti")
            finalize_latency(r)
        else:
            r = run_vertical(key, spec, clients.get(key), index, deadline)
            if seed_error and key not in clients:
                r.add("SETUP", FAIL_DRIVER, "FIXTURE", f"seed DB fallito: {seed_error}")
        results.append(r)
        # Stampa riga verticale subito (≤30 righe totali)
        lat = r.latencies()
        p95 = f"{lat['p95']:.0f}ms" if lat else "ND"
        print(f"  {r.label}: {r.overall()} p95={p95} "
              f"[sara={r.fail_sara_count()} drv={r.fail_driver_count()}]")

    cleanup()
    restore()

    report_ok = True
    try:
        atomic_write(REPORT, report_text(results, started_wall,
                     time.monotonic() - started_monotonic, health, voip, preflight_notes))
    except Exception as exc:
        report_ok = False
        STATE.dbg(f"[REPORT] errore scrittura: {exc}")

    # Scrivi debug se ci sono problemi
    has_issues = (
        any(r.fail_driver_count() > 0 or r.fail_sara_count() > 0 for r in results)
        or STATE.debug_lines
        or not preflight_ok
    )
    if has_issues:
        write_debug(preflight_notes)
        print(f"DEBUG: {DEBUG}")

    print_summary(results)
    print(f"REPORT: {REPORT}")

    return (
        0 if (
            all(r.overall() != FAIL for r in results)
            and STATE.cleanup.startswith("OK")
            and STATE.restored.startswith("OK")
            and report_ok
        ) else 1
    )


if __name__ == "__main__":
    sys.exit(main())
