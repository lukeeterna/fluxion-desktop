# DECISIONE: ADATTO voice-agent/tests/e2e/test_sara_stress_per_verticale.py, il runner live già collaudato su :3002.
# RIUSO: conversazioni booking, FAQ, guardrail e soglia 5000 ms; non ricopio né sostituisco il patrimonio del 14/05.
# MODIFICHE: sei verticali di ricerca, catalogo DB-grounded, contenuto/argomentazioni, budget, fixture uniche e cleanup.
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
OK, WARN, FAIL, ND = "OK", "WARN", "FAIL", "ND"
SEVERITY = {OK: 0, WARN: 1, FAIL: 2, ND: -1}

OUT = Path(__file__).resolve().parent
REPORT = OUT / "stress_verticali.md"
ROOT = Path(__file__).resolve().parents[3]
VOICE = ROOT / "voice-agent"
ASSET = VOICE / "tests" / "e2e" / "test_sara_stress_per_verticale.py"
VERTICAL_DBS = VOICE / "data" / "vertical_dbs"

BOOKING_STATES = {
    "waiting_service", "waiting_name", "waiting_surname", "waiting_date",
    "waiting_time", "waiting_operator", "confirming", "propose_registration",
    "registering_surname", "registering_phone", "confirming_phone",
    "disambiguating_name", "disambiguating_birth_date",
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
    level: str
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

    def add(
        self,
        category: str,
        level: str,
        scenario: str,
        message: str,
        turn: Optional[Turn] = None,
    ) -> None:
        self.checks.append(Check(category, level, scenario, message, turn))

    def status(self, category: str) -> str:
        levels = [
            check.level
            for check in self.checks
            if check.category == category
        ]
        return max(levels, key=SEVERITY.get) if levels else ND

    def overall(self) -> str:
        levels = [
            check.level
            for check in self.checks
            if check.category != "SETUP"
        ]
        return max(levels, key=SEVERITY.get) if levels else FAIL

    def kb(self) -> str:
        return worst(self.status("FAQ"), self.status("CATALOGO"))

    def latencies(self) -> Dict[str, float]:
        values = sorted(
            turn.latency_ms
            for turn in self.turns
            if turn.latency_ms > 0
        )
        if not values:
            return {}

        count = len(values)
        return {
            "avg": sum(values) / count,
            "p50": values[(count - 1) // 2],
            "p95": values[max(0, math.ceil(count * 0.95) - 1)],
            "max": values[-1],
        }


class BudgetExceeded(RuntimeError):
    pass


class State:
    def __init__(self) -> None:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.tag = (
            f"stress-verticali:{stamp}:{os.getpid()}:"
            f"{uuid.uuid4().hex[:8]}"
        )
        self.source = "stress-verticali-20260731"
        self.db: Optional[Path] = None
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.cleaned = False
        self.cleanup = ND
        self.restored = ND


STATE = State()


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    ).lower()


def has(text: str, needles: Iterable[str]) -> bool:
    value = norm(text)
    return any(norm(item) in value for item in needles)


def worst(*levels: str) -> str:
    valid = [level for level in levels if level != ND]
    return max(valid, key=SEVERITY.get) if valid else ND


def request(
    path: str,
    payload: Optional[Dict[str, Any]] = None,
    method: str = "POST",
    timeout: float = HTTP_TIMEOUT,
) -> Tuple[int, Dict[str, Any], float, str]:
    started = time.monotonic()
    data = (
        None
        if method == "GET"
        else json.dumps(
            payload or {},
            ensure_ascii=False,
        ).encode()
    )
    request_object = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )

    try:
        with urllib.request.urlopen(
            request_object,
            timeout=max(1.0, timeout),
        ) as response:
            status = int(response.status)
            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

        body = json.loads(raw) if raw else {}
        if not isinstance(body, dict):
            body = {"data": body}

        body.pop("audio_base64", None)
        body.pop("audio_hex", None)

        return (
            status,
            body,
            (time.monotonic() - started) * 1000.0,
            "",
        )

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"raw": raw}

        if isinstance(body, dict):
            body.pop("audio_base64", None)
            body.pop("audio_hex", None)

        return (
            exc.code,
            body if isinstance(body, dict) else {},
            (time.monotonic() - started) * 1000.0,
            f"HTTP {exc.code}: {body}",
        )

    except Exception as exc:
        return (
            0,
            {},
            (time.monotonic() - started) * 1000.0,
            f"{type(exc).__name__}: {exc}",
        )


def timeout_for(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 1.0:
        raise BudgetExceeded("budget verticale esaurito")
    return min(HTTP_TIMEOUT, remaining)


def load_asset():
    if not ASSET.is_file():
        raise RuntimeError(f"asset assente: {ASSET}")

    spec = importlib.util.spec_from_file_location(
        "sara_stress_asset",
        ASSET,
    )
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
            forbidden=[
                "officina", "tagliand", "gomm", "odontoiatr",
                "fisioterap", "palestra", "pilates",
            ],
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
            forbidden=[
                "parrucch", "capell", "piega", "odontoiatr",
                "fisioterap", "palestra", "pilates", "estetic",
            ],
            db=["auto", "gommista"],
        ),
        "dentista": dict(
            label="Studio Odontoiatrico",
            api="odontoiatra",
            booking=verticals["medical"]["booking_conversations"][0],
            faq=[
                (
                    "Quanto costa una visita odontoiatrica?",
                    ["prezzo", "euro", "costo", "odontoiatr"],
                ),
                (
                    "Gestite le urgenze dentali?",
                    ["urgen", "dolor", "dent", "appuntament", "contatt"],
                ),
                (
                    "Fate anche igiene dentale o pulizia dei denti?",
                    ["igiene", "pulizia", "dent", "ablazione"],
                ),
            ],
            guard=verticals["medical"]["guardrail_wrong_service"][0],
            argument=(
                "Perché è utile fare controlli dentali periodici?",
                ["controll", "preven", "dent", "carie", "salute"],
            ),
            identity=["studio", "dent", "odontoiatr", "igiene", "visita"],
            forbidden=[
                "officina", "tagliand", "gomm", "parrucch",
                "capell", "palestra", "pilates", "estetic", "fisioterap",
            ],
            db=["odontoiatra", "medical", "medico"],
        ),
        "fisioterapia": dict(
            label="Studio di Fisioterapia",
            api="fisioterapia",
            booking=verticals["medical"]["booking_conversations"][1],
            faq=[
                (
                    "Quanto costa una seduta di fisioterapia?",
                    ["prezzo", "euro", "costo", "fisioterap"],
                ),
                (
                    "Quanto dura una seduta?",
                    ["durata", "minut", "ora", "seduta"],
                ),
                (
                    "Serve la prescrizione medica?",
                    ["prescrizion", "medic", "necessar", "serve", "dipende"],
                ),
            ],
            guard=verticals["medical"]["guardrail_wrong_service"][1],
            argument=(
                "Perché è utile seguire un ciclo di fisioterapia?",
                ["fisioterap", "recuper", "sedut", "continuit", "dolor"],
            ),
            identity=[
                "studio", "fisioterap", "riabilit", "sedut", "recuper",
            ],
            forbidden=[
                "officina", "tagliand", "gomm", "parrucch",
                "capell", "odontoiatr", "dent", "estetic",
            ],
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
            forbidden=[
                "officina", "tagliand", "gomm", "parrucch",
                "capell", "odontoiatr", "dent", "estetic", "laser",
            ],
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
            forbidden=[
                "officina", "tagliand", "gomm", "odontoiatr",
                "dent", "palestra", "pilates", "parrucch", "capell",
            ],
            db=["beauty", "estetista_corpo", "estetista_viso"],
        ),
    }


def columns(
    connection: sqlite3.Connection,
    table: str,
) -> List[str]:
    name = table.replace('"', '""')
    return [
        str(row[1])
        for row in connection.execute(
            f'PRAGMA table_info("{name}")'
        )
    ]


def resolve_db() -> Optional[Path]:
    candidates: List[Path] = []

    if os.environ.get("FLUXION_DB_PATH"):
        candidates.append(
            Path(os.environ["FLUXION_DB_PATH"]).expanduser()
        )

    home = Path.home()
    candidates += [
        home
        / "Library"
        / "Application Support"
        / "com.fluxion.desktop"
        / "fluxion.db",
        home
        / "Library"
        / "Application Support"
        / "fluxion"
        / "fluxion.db",
        VOICE / "fluxion.db",
    ]

    return next(
        (
            path
            for path in candidates
            if path.is_file()
        ),
        None,
    )


def seed_clients(
    specs: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    db = resolve_db()
    if db is None:
        raise RuntimeError("fluxion.db non trovato")

    STATE.db = db
    token = "".join(
        chr(97 + int(character, 16))
        for character in uuid.uuid4().hex[:7]
    )
    first_names = [
        "Marco", "Giulia", "Luca",
        "Elena", "Paolo", "Sara",
    ]
    result: Dict[str, Dict[str, Any]] = {}

    with sqlite3.connect(str(db), timeout=10) as connection:
        available_columns = set(columns(connection, "clienti"))
        required = {"nome", "cognome", "telefono"}

        if not required.issubset(available_columns):
            raise RuntimeError(
                "schema clienti incompatibile: "
                f"{sorted(available_columns)}"
            )

        for index, key in enumerate(specs):
            proposed_id = uuid.uuid4().hex
            values = {
                "nome": first_names[index],
                "cognome": f"Stress{key.capitalize()}{token}",
                "telefono": (
                    "388"
                    + f"{(int(time.time()) + index) % 10000000:07d}"
                ),
                "note": STATE.tag,
                "fonte": STATE.source,
                "created_at": datetime.now().isoformat(),
                "deleted_at": None,
            }
            names = [
                name
                for name in values
                if name in available_columns
            ]
            query = (
                f"INSERT INTO clienti ({','.join(names)}) "
                f"VALUES ({','.join('?' for _ in names)})"
            )

            try:
                cursor = connection.execute(
                    query,
                    tuple(values[name] for name in names),
                )
            except sqlite3.IntegrityError:
                if "id" not in available_columns:
                    raise

                names = ["id"] + names
                query = (
                    f"INSERT INTO clienti ({','.join(names)}) "
                    f"VALUES ({','.join('?' for _ in names)})"
                )
                cursor = connection.execute(
                    query,
                    tuple(
                        proposed_id if name == "id" else values[name]
                        for name in names
                    ),
                )

            row = connection.execute(
                "SELECT id FROM clienti "
                "WHERE telefono=? ORDER BY rowid DESC LIMIT 1",
                (values["telefono"],),
            ).fetchone()
            client_id = (
                row[0]
                if row and row[0] is not None
                else proposed_id
            )

            if row and row[0] is None:
                connection.execute(
                    "UPDATE clienti SET id=? WHERE rowid=?",
                    (proposed_id, cursor.lastrowid),
                )

            result[key] = {
                "id": client_id,
                **values,
            }

        connection.commit()

    STATE.clients = result
    return result


def cleanup() -> None:
    if STATE.cleaned:
        return

    STATE.cleaned = True

    if STATE.db is None or not STATE.db.is_file():
        STATE.cleanup = (
            "OK: nessuna fixture creata"
            if not STATE.clients
            else "FAIL: DB non risolto"
        )
        return

    try:
        with sqlite3.connect(
            str(STATE.db),
            timeout=10,
        ) as connection:
            connection.execute("PRAGMA foreign_keys=OFF")
            identifiers = [
                item["id"]
                for item in STATE.clients.values()
            ]

            if not identifiers:
                STATE.cleanup = "OK: nessuna fixture creata"
                return

            marks = ",".join("?" for _ in identifiers)
            tables = [
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%'"
                )
            ]
            appointment_ids: List[Any] = []

            if (
                "appuntamenti" in tables
                and "cliente_id" in columns(
                    connection,
                    "appuntamenti",
                )
            ):
                appointment_ids = [
                    row[0]
                    for row in connection.execute(
                        "SELECT id FROM appuntamenti "
                        f"WHERE cliente_id IN ({marks})",
                        identifiers,
                    )
                ]

            for table in tables:
                if table in {"clienti", "appuntamenti"}:
                    continue

                available_columns = set(
                    columns(connection, table)
                )
                quoted_table = table.replace('"', '""')

                for column in (
                    "appuntamento_id",
                    "appointment_id",
                ):
                    if (
                        column in available_columns
                        and appointment_ids
                    ):
                        appointment_marks = ",".join(
                            "?"
                            for _ in appointment_ids
                        )
                        connection.execute(
                            f'DELETE FROM "{quoted_table}" '
                            f'WHERE "{column}" '
                            f"IN ({appointment_marks})",
                            appointment_ids,
                        )

                for column in (
                    "cliente_id",
                    "client_id",
                ):
                    if column in available_columns:
                        connection.execute(
                            f'DELETE FROM "{quoted_table}" '
                            f'WHERE "{column}" IN ({marks})',
                            identifiers,
                        )

            if "appuntamenti" in tables:
                connection.execute(
                    "DELETE FROM appuntamenti "
                    f"WHERE cliente_id IN ({marks})",
                    identifiers,
                )

            connection.execute(
                f"DELETE FROM clienti WHERE id IN ({marks})",
                identifiers,
            )
            connection.commit()

            remaining = connection.execute(
                "SELECT COUNT(*) FROM clienti "
                f"WHERE id IN ({marks})",
                identifiers,
            ).fetchone()[0]

            STATE.cleanup = (
                f"OK: rimosse {len(identifiers)} fixture e relativi dati"
                if remaining == 0
                else f"FAIL: {remaining} fixture residue"
            )

    except Exception as exc:
        STATE.cleanup = (
            f"FAIL: {type(exc).__name__}: {exc}"
        )


def restore() -> None:
    try:
        reset = request(
            "/api/voice/reset",
            {},
            timeout=5,
        )
        switched = request(
            "/api/voice/set-vertical",
            {"vertical": RESTORE_VERTICAL},
            timeout=8,
        )
        STATE.restored = (
            "OK: salone ripristinato"
            if (
                reset[0] == 200
                and switched[0] == 200
                and switched[1].get("success")
            )
            else (
                f"FAIL: reset={reset[0]}, "
                f"set={switched[0]}"
            )
        )
    except Exception as exc:
        STATE.restored = (
            f"FAIL: {type(exc).__name__}: {exc}"
        )


def final_cleanup() -> None:
    cleanup()
    if STATE.restored == ND:
        restore()


atexit.register(final_cleanup)


def on_signal(signum, frame) -> None:
    cleanup()
    restore()
    raise KeyboardInterrupt


for _signal in (
    signal.SIGINT,
    signal.SIGTERM,
):
    signal.signal(_signal, on_signal)


def start_scenario(
    api_vertical: str,
    deadline: float,
) -> Tuple[Optional[str], str]:
    reset = request(
        "/api/voice/reset",
        {},
        timeout=timeout_for(deadline),
    )
    if reset[0] != 200 or not reset[1].get("success"):
        return None, reset[3] or str(reset[1])

    switched = request(
        "/api/voice/set-vertical",
        {"vertical": api_vertical},
        timeout=timeout_for(deadline),
    )
    if (
        switched[0] != 200
        or not switched[1].get("success")
    ):
        return None, switched[3] or str(switched[1])

    time.sleep(0.12)
    return switched[1].get("session_id"), ""


def ask(
    result: VResult,
    scenario: str,
    text: str,
    session_id: Optional[str],
    deadline: float,
) -> Turn:
    payload: Dict[str, Any] = {"text": text}
    if session_id:
        payload["session_id"] = session_id

    status, body, elapsed, error = request(
        "/api/voice/process",
        payload,
        timeout=timeout_for(deadline),
    )
    turn = Turn(
        scenario=scenario,
        user=text,
        response=str(body.get("response") or ""),
        fsm=str(body.get("fsm_state") or ""),
        layer=str(body.get("layer") or ""),
        latency_ms=elapsed,
        success=(
            status == 200
            and bool(body.get("success"))
        ),
        error=error or str(body.get("error") or ""),
        booking_action=(
            body.get("booking_action")
            if isinstance(
                body.get("booking_action"),
                dict,
            )
            else None
        ),
    )
    result.turns.append(turn)
    return turn


def begin(
    result: VResult,
    category: str,
    scenario: str,
    deadline: float,
) -> Optional[str]:
    session_id, error = start_scenario(
        result.api,
        deadline,
    )
    if error:
        result.add(
            category,
            FAIL,
            scenario,
            f"reset/set-vertical fallito: {error}",
        )
        return None
    return session_id


def failed_turn(
    result: VResult,
    category: str,
    scenario: str,
    turn: Turn,
) -> bool:
    if turn.success:
        return False

    result.add(
        category,
        FAIL,
        scenario,
        f"errore turno: {turn.error or ND}",
        turn,
    )
    return True


def service_tokens(name: str) -> List[str]:
    return [
        token
        for token in re.findall(
            r"[a-z0-9]+",
            norm(name),
        )
        if (
            len(token) >= 4
            and token not in STOPWORDS
        )
    ]


def match_services(
    text: str,
    services: Sequence[str],
) -> List[str]:
    value = norm(text)
    found = []

    for service in services:
        tokens = service_tokens(service)
        hits = sum(
            token in value
            for token in tokens
        )

        if (
            norm(service) in value
            or (
                tokens
                and hits >= (
                    1
                    if len(tokens) == 1
                    else 2
                )
            )
        ):
            found.append(service)

    return found


def catalog_for(
    aliases: Sequence[str],
) -> Tuple[List[str], str]:
    path = next(
        (
            VERTICAL_DBS / f"{name}.db"
            for name in aliases
            if (
                VERTICAL_DBS / f"{name}.db"
            ).is_file()
        ),
        None,
    )
    if path is None:
        return [], "DB verticale non trovato"

    try:
        with sqlite3.connect(
            str(path),
            timeout=5,
        ) as connection:
            available_columns = set(
                columns(connection, "servizi")
            )
            if "nome" not in available_columns:
                return (
                    [],
                    f"servizi.nome assente in {path.name}",
                )

            sql = "SELECT nome FROM servizi"
            if "attivo" in available_columns:
                sql += " WHERE attivo=1"
            if "ordine" in available_columns:
                sql += " ORDER BY ordine"

            return (
                [
                    str(row[0]).strip()
                    for row in connection.execute(sql)
                    if row[0]
                ],
                str(path),
            )
    except Exception as exc:
        return (
            [],
            f"{type(exc).__name__}: {exc}",
        )


def next_date(index: int) -> str:
    target = date.today() + timedelta(
        days=35 + index * 4
    )
    desired = (index + 1) % 5

    while target.weekday() != desired:
        target += timedelta(days=1)

    return (
        f"{WEEKDAYS[target.weekday()]} "
        f"{target.day} "
        f"{MONTHS[target.month - 1]} "
        f"{target.year}"
    )


def first_time(text: str) -> Optional[str]:
    match = re.search(
        r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b",
        text,
    )
    return (
        f"{int(match.group(1)):02d}:{match.group(2)}"
        if match
        else None
    )


def run_booking(
    result: VResult,
    spec: Dict[str, Any],
    client: Dict[str, Any],
    deadline: float,
    index: int,
) -> None:
    scenario = (
        f"BOOKING {spec['booking']['name']}"
    )
    session_id = begin(
        result,
        "BOOKING",
        scenario,
        deadline,
    )
    if session_id is None:
        return

    text = spec["booking"]["turns"][1][0]
    sent = {
        name: False
        for name in (
            "name",
            "surname",
            "phone",
            "date",
            "time",
            "operator",
            "confirm",
        )
    }
    target_date = next_date(index)
    completed: Optional[Turn] = None

    for _ in range(10):
        turn = ask(
            result,
            scenario,
            text,
            session_id,
            deadline,
        )
        if failed_turn(
            result,
            "BOOKING",
            scenario,
            turn,
        ):
            return

        action = turn.booking_action or {}
        if action.get("action") == "booking_created":
            completed = turn
            break

        state = norm(turn.fsm).replace(" ", "_")
        response = norm(turn.response)

        if state == "waiting_service":
            text = (
                "Vorrei prenotare "
                f"{spec['booking']['name']}"
            )
        elif (
            state in {
                "waiting_name",
                "disambiguating_name",
            }
            and not sent["name"]
        ):
            text = (
                f"Sono {client['nome']} "
                f"{client['cognome']}"
            )
            sent["name"] = True
        elif (
            state == "waiting_surname"
            and not sent["surname"]
        ):
            text = client["cognome"]
            sent["surname"] = True
        elif state == "propose_registration":
            text = "Sì, registrami"
        elif (
            state == "registering_phone"
            and not sent["phone"]
        ):
            text = client["telefono"]
            sent["phone"] = True
        elif state == "confirming_phone":
            text = "Sì, confermo il numero"
        elif (
            state == "waiting_date"
            and not sent["date"]
        ):
            text = target_date
            sent["date"] = True
        elif state == "waiting_time":
            offered = first_time(turn.response)
            text = (
                f"Alle {offered}"
                if offered
                else "Alle dieci"
            )
            sent["time"] = True
        elif (
            state == "waiting_operator"
            and not sent["operator"]
        ):
            text = "Il primo operatore disponibile"
            sent["operator"] = True
        elif (
            state == "confirming"
            or has(
                response,
                ["conferm", "riepilog"],
            )
        ):
            text = "Sì, confermo"
            sent["confirm"] = True
        elif not sent["name"]:
            text = (
                f"Sono {client['nome']} "
                f"{client['cognome']}"
            )
            sent["name"] = True
        elif not sent["date"]:
            text = target_date
            sent["date"] = True
        elif not sent["time"]:
            text = "Alle dieci"
            sent["time"] = True
        elif not sent["confirm"]:
            text = "Sì, confermo"
            sent["confirm"] = True
        else:
            break

    if completed is None:
        result.add(
            "BOOKING",
            FAIL,
            scenario,
            "booking_action=booking_created non osservata",
            result.turns[-1] if result.turns else None,
        )
        return

    context = (
        (completed.booking_action or {}).get("context")
        or {}
    )
    returned = str(
        context.get("service")
        or context.get("service_display")
        or ""
    )

    if (
        returned
        and not match_services(
            returned,
            [spec["booking"]["name"]],
        )
    ):
        result.add(
            "BOOKING",
            WARN,
            scenario,
            (
                "booking creato con servizio "
                f"differente: {returned}"
            ),
            completed,
        )
    else:
        result.add(
            "BOOKING",
            OK,
            scenario,
            "prenotazione creata end-to-end",
            completed,
        )


def run_faq(
    result: VResult,
    spec: Dict[str, Any],
    deadline: float,
) -> None:
    for number, (
        question,
        expected,
    ) in enumerate(spec["faq"][:3], 1):
        scenario = f"FAQ-{number}"
        session_id = begin(
            result,
            "FAQ",
            scenario,
            deadline,
        )
        if session_id is None:
            continue

        turn = ask(
            result,
            scenario,
            question,
            session_id,
            deadline,
        )
        if failed_turn(
            result,
            "FAQ",
            scenario,
            turn,
        ):
            continue

        matched = has(
            turn.response,
            expected,
        )
        in_booking = (
            norm(turn.fsm).replace(" ", "_")
            in BOOKING_STATES
        )

        if in_booking and not matched:
            result.add(
                "FAQ",
                FAIL,
                scenario,
                "FAQ deviata nel booking senza risposta",
                turn,
            )
        elif (
            matched
            and norm(turn.layer).startswith(
                ("l1", "l3")
            )
            and not in_booking
        ):
            result.add(
                "FAQ",
                OK,
                scenario,
                "risposta pertinente e KB/exact grounded",
                turn,
            )
        elif matched and not in_booking:
            result.add(
                "FAQ",
                WARN,
                scenario,
                (
                    "pertinente ma "
                    f"layer={turn.layer or ND}; "
                    "KB non certificata"
                ),
                turn,
            )
        elif turn.response.strip() and not in_booking:
            result.add(
                "FAQ",
                WARN,
                scenario,
                (
                    "risposta presente ma keyword "
                    "attese non trovate"
                ),
                turn,
            )
        else:
            result.add(
                "FAQ",
                FAIL,
                scenario,
                "risposta FAQ vuota o incoerente",
                turn,
            )


def run_guardrail(
    result: VResult,
    spec: Dict[str, Any],
    deadline: float,
) -> None:
    scenario = "GUARDRAIL fuori competenza"
    session_id = begin(
        result,
        "GUARDRAIL",
        scenario,
        deadline,
    )
    if session_id is None:
        return

    question, expected = spec["guard"]
    turn = ask(
        result,
        scenario,
        question,
        session_id,
        deadline,
    )
    if failed_turn(
        result,
        "GUARDRAIL",
        scenario,
        turn,
    ):
        return

    response = norm(turn.response)
    refusal = has(
        turn.response,
        [
            "non posso",
            "non ci occup",
            "fuori competenza",
            "non rientra",
            "non offriamo",
            "non forniamo",
            "non trattiamo",
            "non e un servizio",
        ],
    )
    domain = [
        item
        for item in expected
        if norm(item) not in {"non", "no"}
    ]
    blocked = (
        refusal
        or (
            "non" in response[:120]
            and has(turn.response, domain)
        )
    )
    in_booking = (
        norm(turn.fsm).replace(" ", "_")
        in BOOKING_STATES
    )

    if in_booking:
        result.add(
            "GUARDRAIL",
            FAIL,
            scenario,
            (
                "servizio fuori dominio "
                "accettato nel booking"
            ),
            turn,
        )
    elif blocked:
        result.add(
            "GUARDRAIL",
            OK,
            scenario,
            "richiesta fuori dominio rifiutata",
            turn,
        )
    elif turn.response.strip():
        result.add(
            "GUARDRAIL",
            WARN,
            scenario,
            (
                "rifiuto non esplicito, "
                "ma booking non avviato"
            ),
            turn,
        )
    else:
        result.add(
            "GUARDRAIL",
            FAIL,
            scenario,
            "nessuna risposta",
            turn,
        )


def run_catalog(
    result: VResult,
    spec: Dict[str, Any],
    deadline: float,
) -> None:
    scenario = "CATALOGO servizi vs knowledge base"
    services, source = catalog_for(spec["db"])

    if not services:
        result.add(
            "CATALOGO",
            FAIL,
            scenario,
            f"catalogo DB non leggibile: {source}",
        )
        return

    if not match_services(
        spec["booking"]["name"],
        services,
    ):
        result.add(
            "CATALOGO",
            FAIL,
            scenario,
            (
                f"servizio booking "
                f"'{spec['booking']['name']}' "
                f"assente da {Path(source).name}"
            ),
        )

    session_id = begin(
        result,
        "CATALOGO",
        scenario,
        deadline,
    )
    if session_id is None:
        return

    turn = ask(
        result,
        scenario,
        (
            "Quali servizi posso prenotare con voi? "
            "Elencami i principali."
        ),
        session_id,
        deadline,
    )
    if failed_turn(
        result,
        "CATALOGO",
        scenario,
        turn,
    ):
        return

    matches = match_services(
        turn.response,
        services,
    )
    in_booking = (
        norm(turn.fsm).replace(" ", "_")
        in BOOKING_STATES
    )

    if in_booking:
        result.add(
            "CATALOGO",
            FAIL,
            scenario,
            "domanda catalogo deviata nel booking",
            turn,
        )
    elif has(
        turn.response,
        spec["forbidden"],
    ):
        result.add(
            "CATALOGO",
            FAIL,
            scenario,
            "catalogo contaminato da altro verticale",
            turn,
        )
    elif len(matches) >= min(2, len(services)):
        result.add(
            "CATALOGO",
            OK,
            scenario,
            (
                f"coerente con DB: "
                f"{len(matches)}/{len(services)} servizi"
            ),
            turn,
        )
    elif len(matches) == 1:
        result.add(
            "CATALOGO",
            WARN,
            scenario,
            (
                f"catalogo parziale: "
                f"1/{len(services)} servizio"
            ),
            turn,
        )
    else:
        result.add(
            "CATALOGO",
            FAIL,
            scenario,
            (
                "nessun servizio DB riconosciuto "
                f"({Path(source).name})"
            ),
            turn,
        )


def single_content(
    result: VResult,
    spec: Dict[str, Any],
    deadline: float,
    category: str,
    scenario: str,
    question: str,
    expected: Sequence[str],
) -> None:
    session_id = begin(
        result,
        category,
        scenario,
        deadline,
    )
    if session_id is None:
        return

    turn = ask(
        result,
        scenario,
        question,
        session_id,
        deadline,
    )
    if failed_turn(
        result,
        category,
        scenario,
        turn,
    ):
        return

    hits = sum(
        norm(item) in norm(turn.response)
        for item in expected
    )
    in_booking = (
        norm(turn.fsm).replace(" ", "_")
        in BOOKING_STATES
    )

    if in_booking:
        result.add(
            category,
            FAIL,
            scenario,
            "domanda informativa deviata nel booking",
            turn,
        )
    elif has(
        turn.response,
        spec["forbidden"],
    ):
        result.add(
            category,
            FAIL,
            scenario,
            "risposta contaminata da altro verticale",
            turn,
        )
    elif hits >= 2:
        result.add(
            category,
            OK,
            scenario,
            f"contenuto pertinente ({hits} segnali)",
            turn,
        )
    elif hits == 1 and turn.response.strip():
        result.add(
            category,
            WARN,
            scenario,
            "contenuto generico ma compatibile",
            turn,
        )
    else:
        result.add(
            category,
            FAIL,
            scenario,
            "contenuto non pertinente o vuoto",
            turn,
        )


def finalize_latency(result: VResult) -> None:
    if not result.turns:
        result.add(
            "LATENZA",
            FAIL,
            "LATENZA",
            "nessun turno misurabile",
        )
        return

    slow = sum(
        turn.latency_ms > SLOW_MS
        for turn in result.turns
    )

    if slow == 0:
        result.add(
            "LATENZA",
            OK,
            "LATENZA",
            (
                f"tutti i {len(result.turns)} "
                f"turni <= {SLOW_MS:.0f}ms"
            ),
        )
    elif slow == 1:
        result.add(
            "LATENZA",
            WARN,
            "LATENZA",
            "1 turno sopra 5000ms",
        )
    else:
        result.add(
            "LATENZA",
            FAIL,
            "LATENZA",
            (
                f"{slow}/{len(result.turns)} "
                "turni sopra 5000ms"
            ),
        )


def fill_missing(
    result: VResult,
    reason: str,
) -> None:
    for category in (
        "BOOKING",
        "FAQ",
        "GUARDRAIL",
        "CATALOGO",
        "RISPOSTE",
        "ARGOMENTAZIONI",
    ):
        if result.status(category) == ND:
            result.add(
                category,
                FAIL,
                "BUDGET",
                reason,
            )


def run_vertical(
    key: str,
    spec: Dict[str, Any],
    client: Optional[Dict[str, Any]],
    index: int,
    global_deadline: float,
) -> VResult:
    result = VResult(
        key,
        spec["label"],
        spec["api"],
    )
    started = time.monotonic()
    deadline = min(
        started + VERTICAL_BUDGET,
        global_deadline,
    )

    try:
        if client:
            run_booking(
                result,
                spec,
                client,
                deadline,
                index,
            )
        else:
            result.add(
                "BOOKING",
                FAIL,
                "BOOKING",
                "fixture DB non disponibile",
            )

        run_faq(result, spec, deadline)
        run_guardrail(result, spec, deadline)
        run_catalog(result, spec, deadline)

        single_content(
            result,
            spec,
            deadline,
            "RISPOSTE",
            "RISPOSTA identità e ambito",
            "Chi siete e di quali servizi vi occupate?",
            spec["identity"],
        )

        question, expected = spec["argument"]
        single_content(
            result,
            spec,
            deadline,
            "ARGOMENTAZIONI",
            "ARGOMENTAZIONE settoriale",
            question,
            expected,
        )

    except BudgetExceeded as exc:
        fill_missing(
            result,
            (
                f"verticale oltre budget "
                f"{VERTICAL_BUDGET:.0f}s: {exc}"
            ),
        )
    except Exception as exc:
        result.add(
            "SETUP",
            FAIL,
            "RUNTIME",
            f"{type(exc).__name__}: {exc}",
        )
        fill_missing(
            result,
            (
                "scenari non completati "
                "per errore runtime"
            ),
        )

    result.duration_s = (
        time.monotonic() - started
    )
    finalize_latency(result)
    return result


def evidence(check: Check) -> List[str]:
    if check.turn is None:
        return [
            "    USER: ND",
            "    SARA: ND",
            "    FSM: ND",
            "    LAYER: ND",
            "    LATENCY_MS: ND",
            "    ERROR: ND",
        ]

    turn = check.turn
    lines = [f"    USER: {turn.user}"]
    lines += [
        f"    SARA: {line}"
        for line in (
            turn.response.splitlines()
            or [ND]
        )
    ]
    lines += [
        f"    FSM: {turn.fsm or ND}",
        f"    LAYER: {turn.layer or ND}",
        f"    LATENCY_MS: {turn.latency_ms:.1f}",
        f"    ERROR: {turn.error or ND}",
    ]
    return lines


def best_vertical(
    results: Sequence[VResult],
) -> str:
    eligible = [
        result
        for result in results
        if result.turns
    ]
    if not eligible:
        return ND

    def score(
        result: VResult,
    ) -> Tuple[int, float, int, str]:
        failures = sum(
            check.level == FAIL
            for check in result.checks
        )
        warnings = sum(
            check.level == WARN
            for check in result.checks
        )
        return (
            failures,
            result.latencies().get(
                "p95",
                float("inf"),
            ),
            warnings,
            result.label,
        )

    return min(
        eligible,
        key=score,
    ).label


def report_text(
    results: Sequence[VResult],
    started: str,
    duration: float,
    health: Tuple[int, Dict[str, Any], float, str],
    voip: Tuple[int, Dict[str, Any], float, str],
) -> str:
    sip = (
        voip[1].get("sip")
        if isinstance(
            voip[1].get("sip"),
            dict,
        )
        else {}
    )
    lines = [
        "## Stress verticali — certificazione contenuto Sara",
        "",
        f"**Run:** {STATE.tag}",
        f"**Inizio:** {started}",
        (
            f"**Durata:** {duration:.1f}s / "
            f"budget {RUN_BUDGET:.0f}s"
        ),
        f"**Endpoint:** {BASE}",
        (
            f"**Health:** HTTP {health[0]} · "
            f"{health[1].get('status', ND)}"
        ),
        (
            "**VoIP produzione (solo lettura):** "
            f"HTTP {voip[0]} · "
            f"registered={sip.get('registered', ND)}"
        ),
        f"**Cleanup DB:** {STATE.cleanup}",
        f"**Verticale ripristinato:** {STATE.restored}",
        "",
        (
            "| Verticale | Esito | KB | Risposte | Booking | FAQ | "
            "Guardrail | Catalogo | Argomentazioni | Latenza | "
            "AVG ms | P95 ms | MAX ms | Turni | Durata s |"
        ),
        (
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
            "---:|---:|---:|---:|---:|---:|"
        ),
    ]

    for result in results:
        latency = result.latencies()

        if latency:
            lines.append(
                f"| {result.label} "
                f"| {result.overall()} "
                f"| {result.kb()} "
                f"| {result.status('RISPOSTE')} "
                f"| {result.status('BOOKING')} "
                f"| {result.status('FAQ')} "
                f"| {result.status('GUARDRAIL')} "
                f"| {result.status('CATALOGO')} "
                f"| {result.status('ARGOMENTAZIONI')} "
                f"| {result.status('LATENZA')} "
                f"| {latency.get('avg', 0):.0f} "
                f"| {latency.get('p95', 0):.0f} "
                f"| {latency.get('max', 0):.0f} "
                f"| {len(result.turns)} "
                f"| {result.duration_s:.1f} |"
            )
        else:
            lines.append(
                f"| {result.label} "
                f"| {result.overall()} "
                f"| {result.kb()} "
                f"| {result.status('RISPOSTE')} "
                f"| {result.status('BOOKING')} "
                f"| {result.status('FAQ')} "
                f"| {result.status('GUARDRAIL')} "
                f"| {result.status('CATALOGO')} "
                f"| {result.status('ARGOMENTAZIONI')} "
                f"| {result.status('LATENZA')} "
                f"| {ND} | {ND} | {ND} "
                f"| 0 | {result.duration_s:.1f} |"
            )

    failures = [
        (result, check)
        for result in results
        for check in result.checks
        if check.level == FAIL
    ]

    lines += [
        "",
        "### FAIL",
        "",
    ]

    if not failures:
        lines.append("Nessun FAIL.")

    for result, check in failures:
        lines += [
            (
                f"#### {result.label} — "
                f"{check.category} — "
                f"{check.scenario}"
            ),
            f"- Timestamp: {check.ts}",
            f"- Motivo: {check.message}",
            "- Evidenza verbatim:",
            *evidence(check),
            "",
        ]

    lines += [
        "",
        (
            f"**Verticale PIÙ PRONTO:** "
            f"{best_vertical(results)} — "
            "minor numero di FAIL e, a parità, P95 migliore."
        ),
        "",
    ]
    return "\n".join(lines)


def atomic_write(
    path: Path,
    text: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.tmp"
    )

    try:
        temporary.write_text(
            text,
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except OSError:
            pass


def failed_results(
    specs: Dict[str, Dict[str, Any]],
    reason: str,
) -> List[VResult]:
    output = []

    for key, spec in specs.items():
        result = VResult(
            key,
            spec["label"],
            spec["api"],
        )
        for category in (
            "BOOKING",
            "FAQ",
            "GUARDRAIL",
            "CATALOGO",
            "RISPOSTE",
            "ARGOMENTAZIONI",
            "LATENZA",
        ):
            result.add(
                category,
                FAIL,
                "PREFLIGHT",
                reason,
            )
        output.append(result)

    return output


def print_summary(
    results: Sequence[VResult],
) -> None:
    for result in results:
        latency = result.latencies()
        suffix = (
            f"p95={latency['p95']:.0f}ms"
            if latency
            else "p95=ND"
        )
        print(
            f"{result.label}: {result.overall()} "
            f"| kb={result.kb()} "
            f"risposte={result.status('RISPOSTE')} "
            f"booking={result.status('BOOKING')} "
            f"faq={result.status('FAQ')} "
            f"guardrail={result.status('GUARDRAIL')} "
            f"catalogo={result.status('CATALOGO')} "
            f"arg={result.status('ARGOMENTAZIONI')} "
            f"{suffix}"
        )

    failures = sum(
        check.level == FAIL
        for result in results
        for check in result.checks
    )
    print(
        f"RIEPILOGO: verticali={len(results)} "
        f"FAIL={failures} "
        f"più_pronto={best_vertical(results)} "
        f"cleanup={STATE.cleanup}"
    )


def main() -> int:
    started_monotonic = time.monotonic()
    started_wall = now()

    health = request(
        "/health",
        method="GET",
        timeout=5,
    )
    voip = request(
        "/api/voice/voip/status",
        method="GET",
        timeout=5,
    )

    try:
        specs = specs_from(load_asset())
    except Exception as exc:
        STATE.cleanup = "OK: nessuna fixture creata"
        STATE.restored = "OK: verticale non modificato"
        atomic_write(
            REPORT,
            (
                "## Stress verticali — "
                "certificazione contenuto Sara\n\n"
                f"FAIL: {type(exc).__name__}: {exc}\n"
            ),
        )
        print(
            "RIEPILOGO: FAIL "
            f"asset={type(exc).__name__}: {exc}"
        )
        return 1

    call = (
        voip[1].get("call")
        if isinstance(
            voip[1].get("call"),
            dict,
        )
        else {}
    )
    busy = bool(
        voip[1].get("rtp_active")
        or voip[1].get("call_active")
        or call.get("active")
        or call.get("connected")
    )

    if busy:
        results = failed_results(
            specs,
            (
                "linea SIP occupata: run non avviata "
                "per non interferire"
            ),
        )
        STATE.cleanup = "OK: nessuna fixture creata"
        STATE.restored = "OK: verticale non modificato"
        atomic_write(
            REPORT,
            report_text(
                results,
                started_wall,
                time.monotonic() - started_monotonic,
                health,
                voip,
            ),
        )
        print_summary(results)
        return 1

    if (
        health[0] != 200
        or health[1].get("status") != "ok"
    ):
        results = failed_results(
            specs,
            (
                "pipeline :3002 non raggiungibile: "
                f"HTTP {health[0]} "
                f"{health[3] or health[1]}"
            ),
        )
        STATE.cleanup = "OK: nessuna fixture creata"
        restore()
        atomic_write(
            REPORT,
            report_text(
                results,
                started_wall,
                time.monotonic() - started_monotonic,
                health,
                voip,
            ),
        )
        print_summary(results)
        return 1

    try:
        clients = seed_clients(specs)
        seed_error = ""
    except Exception as exc:
        clients = {}
        seed_error = (
            f"{type(exc).__name__}: {exc}"
        )

    deadline = (
        started_monotonic
        + RUN_BUDGET
    )
    results: List[VResult] = []

    for index, (key, spec) in enumerate(
        specs.items()
    ):
        if time.monotonic() >= deadline:
            result = VResult(
                key,
                spec["label"],
                spec["api"],
            )
            fill_missing(
                result,
                "run globale oltre budget 20 minuti",
            )
            finalize_latency(result)
        else:
            result = run_vertical(
                key,
                spec,
                clients.get(key),
                index,
                deadline,
            )
            if (
                seed_error
                and key not in clients
            ):
                result.add(
                    "SETUP",
                    FAIL,
                    "FIXTURE",
                    (
                        "seed DB fallito: "
                        f"{seed_error}"
                    ),
                )

        results.append(result)

    cleanup()
    restore()

    report_ok = True
    try:
        atomic_write(
            REPORT,
            report_text(
                results,
                started_wall,
                time.monotonic() - started_monotonic,
                health,
                voip,
            ),
        )
    except Exception:
        report_ok = False

    print_summary(results)

    return (
        0
        if (
            all(
                result.overall() != FAIL
                for result in results
            )
            and STATE.cleanup.startswith("OK")
            and STATE.restored.startswith("OK")
            and report_ok
        )
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
