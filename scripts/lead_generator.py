#!/usr/bin/env python3
"""
FLUXION Lead Generator — Google Maps → WhatsApp outreach links.

Modes:
  paste  — parse copy-pasted Google Maps results from input file
  api    — query Google Maps Places API directly
  links  — regenerate WA links from existing leads.json

Output (scripts/leads/):
  leads.json       — structured lead data
  wa_links.html    — clickable WhatsApp links per lead
  leads_report.txt — plain-text report (HubSpot import)

Python 3.9+, stdlib only (requests used only for --mode api).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "leads"

# ---------------------------------------------------------------------------
# Vertical detection keywords (lowercase)
# ---------------------------------------------------------------------------
VERTICAL_KEYWORDS: Dict[str, List[str]] = {
    "parrucchiere": [
        "parrucch", "hair", "salon", "capelli", "acconciatur", "coiffeur",
        "hairdress", "hairstyl",
    ],
    "barbiere": ["barber", "barbier"],
    "estetista": [
        "estet", "beauty", "nail", "unghie", "trucco", "makeup",
        "centro estetico", "beauty center",
    ],
    "meccanico": ["meccanico", "meccanica", "officina", "autofficina", "auto repair"],
    "gommista": ["gomm", "pneumatic", "tire", "tyre"],
    "carrozziere": ["carrozz", "carrozzeria", "body shop"],
    "palestra": ["palestr", "fitness", "gym", "crossfit", "bodybuilding"],
    "clinica": ["clinic", "poliambulat", "ambulatorio"],
    "studio_medico": ["medic", "dottore", "dott.", "studio medico"],
    "dentista": ["dentist", "odontoiatr", "dental"],
    "fisioterapista": ["fisio", "physiotherap", "riabilitaz", "osteopat"],
    "commercialista": ["commerc", "contabil", "ragionier", "caf ", "consulen"],
    "avvocato": ["avvocat", "legale", "legal", "studio legale", "law"],
}

# Map fine-grained verticals to macro group for template selection
VERTICAL_GROUP: Dict[str, str] = {
    "parrucchiere": "parrucchiere",
    "barbiere": "parrucchiere",
    "estetista": "estetista",
    "meccanico": "meccanico",
    "gommista": "gommista",
    "carrozziere": "carrozziere",
    "palestra": "palestra",
    "clinica": "clinica",
    "studio_medico": "clinica",
    "dentista": "clinica",
    "fisioterapista": "clinica",
    "commercialista": "studio_professionale",
    "avvocato": "studio_professionale",
}

# ---------------------------------------------------------------------------
# WhatsApp message templates — loaded from wa_first_contact_templates.json
# Falls back to hardcoded if JSON not found
# {nome} placeholder = business name
# ---------------------------------------------------------------------------
def _load_wa_templates() -> Dict[str, str]:
    """Load templates from JSON file, use template_a for each vertical."""
    json_path = Path(__file__).resolve().parent.parent / "voice-agent" / "data" / "wa_first_contact_templates.json"
    templates: Dict[str, str] = {}
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for vertical, variants in data.get("templates", {}).items():
                # Use template_a as default
                if isinstance(variants, dict):
                    first = variants.get("template_a", {})
                    if isinstance(first, dict) and "message" in first:
                        templates[vertical] = first["message"]
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback for any missing vertical
    fallback = "Ciao {nome}, quante telefonate perdi mentre lavori? Con FLUXION hai Sara che risponde per te 24/7 e prende gli appuntamenti. Zero commissioni, paghi una volta sola. Ti interessa? Rispondi e ti spiego in 2 minuti."
    for v in ["parrucchiere", "estetista", "meccanico", "gommista", "carrozziere",
              "palestra", "clinica", "studio_professionale", "generico"]:
        if v not in templates:
            templates[v] = fallback
    return templates

WA_TEMPLATES: Dict[str, str] = _load_wa_templates()


# ===================================================================
# Helpers
# ===================================================================

def detect_vertical(text: str) -> str:
    """Return fine-grained vertical key from free text (name + category)."""
    t = text.lower()
    for vertical, keywords in VERTICAL_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                return vertical
    return "generico"


def template_group(vertical: str) -> str:
    return VERTICAL_GROUP.get(vertical, "generico")


def normalise_phone(raw: str) -> Optional[str]:
    """Return digits-only Italian phone (with 39 prefix) or None."""
    digits = re.sub(r"[^\d+]", "", raw)
    # strip leading +
    digits = digits.lstrip("+")

    # Try as-is first (no country prefix) — handles 392xxx, 02xxx etc.
    if re.match(r"^(3\d{8,9}|0\d{7,10})$", digits):
        return "39" + digits

    # Try stripping country prefix 39
    if digits.startswith("39") and len(digits) > 10:
        digits_no_prefix = digits[2:]
        if re.match(r"^(3\d{8,9}|0\d{7,10})$", digits_no_prefix):
            return "39" + digits_no_prefix

    return None


def wa_link(phone: str, message: str) -> str:
    encoded = urllib.parse.quote(message, safe="")
    return f"https://wa.me/{phone}?text={encoded}"


# ===================================================================
# Paste-mode parser
# ===================================================================

# Regex to find Italian phone numbers in messy text
_PHONE_RE = re.compile(
    r"""
    (?:(?:\+|00)\s?39[\s.\-]?)?    # optional +39 / 0039
    (?:
        3[0-9]{2}[\s.\-]?[0-9]{3,4}[\s.\-]?[0-9]{3,4}           # mobile 3xx
        |
        0[0-9]{1,3}[\s.\-]?[0-9]{3,4}[\s.\-]?[0-9]{3,4}         # landline 02 7634 5821
    )
    """,
    re.VERBOSE,
)

_RATING_RE = re.compile(r"(\d[.,]\d)\s*(?:\(\d[\d.]*\))?|(\d[.,]\d)\s*stelle?", re.I)
_STARS_RE = re.compile(r"(\d[.,]\d)")


def _extract_phones(text: str) -> List[str]:
    phones: List[str] = []
    for m in _PHONE_RE.finditer(text):
        raw = m.group(0)
        norm = normalise_phone(raw)
        if norm and norm not in phones:
            phones.append(norm)
    return phones


def _extract_rating(text: str) -> Optional[float]:
    m = _RATING_RE.search(text)
    if m:
        raw = m.group(1) or m.group(2)
        try:
            return float(raw.replace(",", "."))
        except ValueError:
            pass
    # fallback: lone X.Y at line start
    for line in text.splitlines():
        sm = _STARS_RE.match(line.strip())
        if sm:
            try:
                v = float(sm.group(1).replace(",", "."))
                if 1.0 <= v <= 5.0:
                    return v
            except ValueError:
                pass
    return None


def parse_paste(text: str) -> List[Dict[str, Any]]:
    """
    Parse raw Google Maps copy-paste text into lead dicts.

    Heuristic: split on blank-line boundaries or on lines that look like
    a new business name (title-case, no phone, no rating prefix).
    """
    leads: List[Dict[str, Any]] = []
    # --- Try block-splitting first (double newline) ---
    blocks = re.split(r"\n\s*\n", text.strip())
    if len(blocks) < 2:
        # single block — try single-newline split heuristic
        blocks = _split_single_block(text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lead = _parse_block(block)
        if lead and (lead.get("telefono") or lead.get("nome")):
            leads.append(lead)
    return leads


def _split_single_block(text: str) -> List[str]:
    """
    When the whole paste is one big block (no blank lines), try to split
    on lines that look like a business name (no digits at start, title-ish).
    """
    lines = text.strip().splitlines()
    blocks: List[str] = []
    current: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # heuristic: new business = line that doesn't start with digit,
        # doesn't look like address / phone / rating, and current is non-empty
        is_name_line = (
            not re.match(r"^[\d+(]", stripped)
            and not re.match(r"^(via |corso |piazza |viale |largo |loc\.|v\.le)", stripped, re.I)
            and len(stripped) > 3
            and not stripped.startswith("http")
            and not stripped.startswith("Aperto")
            and not stripped.startswith("Chiuso")
            and not stripped.lower().startswith("orari")
        )
        if is_name_line and current and len(current) >= 2:
            blocks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _parse_block(block: str) -> Optional[Dict[str, Any]]:
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    if not lines:
        return None

    nome = lines[0]
    # If first line looks like a rating, skip it to find real name
    if _STARS_RE.match(nome) and len(lines) > 1:
        nome = lines[1]

    # Clean name: strip leading bullet / number / dash
    nome = re.sub(r"^[\d\.\-·•]+\s*", "", nome).strip()
    if not nome:
        return None

    full_text = "\n".join(lines)
    phones = _extract_phones(full_text)
    rating = _extract_rating(full_text)
    vertical = detect_vertical(full_text)

    # Try to find address (line starting with Via/Corso/Piazza or containing comma + city)
    indirizzo = ""
    _addr_re = re.compile(
        r"^(via |corso |piazza |piazzale |viale |largo |v\.le |loc\.|contrada )",
        re.I,
    )
    for line in lines[1:]:
        if _addr_re.match(line.strip()):
            indirizzo = line.strip()
            break

    # categoria — line that contains the Google Maps category (often line 2)
    categoria = ""
    for line in lines[1:4]:
        l = line.strip()
        if (
            l != indirizzo
            and not _PHONE_RE.search(l)
            and not _STARS_RE.match(l)
            and len(l) > 2
            and not l.startswith("http")
        ):
            categoria = l
            break

    return {
        "nome": nome,
        "telefono": phones[0] if phones else "",
        "telefono_display": _format_display_phone(phones[0]) if phones else "",
        "indirizzo": indirizzo,
        "rating": rating,
        "categoria": categoria,
        "verticale": vertical,
        "fonte": "google_maps_paste",
        "data_import": datetime.now().strftime("%Y-%m-%d"),
    }


def _format_display_phone(phone39: str) -> str:
    """39XXXXXXXXXX → +39 XXX XXX XXXX (for display)."""
    raw = phone39[2:]  # strip 39
    if len(raw) == 10:
        return f"+39 {raw[:3]} {raw[3:6]} {raw[6:]}"
    return f"+39 {raw}"


# ===================================================================
# Google Maps Places API mode
# ===================================================================

def search_places_api(query: str, city: str, api_key: str, max_results: int = 20) -> List[Dict[str, Any]]:
    try:
        import requests  # type: ignore[import]
    except ImportError:
        print("ERROR: 'requests' is required for API mode. Install: pip install requests", file=sys.stderr)
        sys.exit(1)

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} {city}",
        "language": "it",
        "key": api_key,
    }

    leads: List[Dict[str, Any]] = []
    while len(leads) < max_results:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "OK":
            print(f"API error: {data.get('status')} — {data.get('error_message', '')}", file=sys.stderr)
            break

        for place in data.get("results", []):
            place_id = place.get("place_id", "")
            # Get phone via Place Details
            phone = ""
            phone_display = ""
            detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
            detail_params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,international_phone_number",
                "language": "it",
                "key": api_key,
            }
            try:
                dr = requests.get(detail_url, params=detail_params, timeout=10)
                dr.raise_for_status()
                dd = dr.json().get("result", {})
                raw_phone = dd.get("international_phone_number", "") or dd.get("formatted_phone_number", "")
                if raw_phone:
                    norm = normalise_phone(raw_phone)
                    if norm:
                        phone = norm
                        phone_display = _format_display_phone(norm)
            except Exception:
                pass

            name = place.get("name", "")
            full_text = f"{name} {' '.join(place.get('types', []))}"
            vertical = detect_vertical(full_text)

            leads.append({
                "nome": name,
                "telefono": phone,
                "telefono_display": phone_display,
                "indirizzo": place.get("formatted_address", ""),
                "rating": place.get("rating"),
                "categoria": ", ".join(place.get("types", [])[:3]),
                "verticale": vertical,
                "fonte": "google_maps_api",
                "data_import": datetime.now().strftime("%Y-%m-%d"),
            })
            if len(leads) >= max_results:
                break

        next_token = data.get("next_page_token")
        if not next_token:
            break
        import time
        time.sleep(2)  # Google requires delay before next_page_token is valid
        params = {"pagetoken": next_token, "key": api_key}

    return leads


# ===================================================================
# Deduplication
# ===================================================================

def load_existing_leads(path: Path) -> Dict[str, Dict[str, Any]]:
    """Load existing leads.json, keyed by phone."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {l["telefono"]: l for l in data if l.get("telefono")}
    except (json.JSONDecodeError, KeyError):
        return {}


def deduplicate(new_leads: List[Dict[str, Any]], existing: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    unique: List[Dict[str, Any]] = []
    skipped = 0
    seen: set = set(existing.keys())
    for lead in new_leads:
        phone = lead.get("telefono", "")
        if phone and phone in seen:
            skipped += 1
            continue
        if phone:
            seen.add(phone)
        unique.append(lead)
    return unique, skipped


# ===================================================================
# Output generators
# ===================================================================

def write_json(leads: List[Dict[str, Any]], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    print(f"  leads.json        — {len(leads)} lead salvati")


def write_report(leads: List[Dict[str, Any]], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"FLUXION Lead Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"{'='*60}\n")
        f.write(f"Totale lead: {len(leads)}\n\n")
        for i, l in enumerate(leads, 1):
            f.write(f"[{i:03d}] {l['nome']}\n")
            f.write(f"      Tel:       {l.get('telefono_display', l.get('telefono', 'N/A'))}\n")
            f.write(f"      Indirizzo: {l.get('indirizzo', 'N/A')}\n")
            f.write(f"      Rating:    {l.get('rating', 'N/A')}\n")
            f.write(f"      Verticale: {l.get('verticale', 'N/A')}\n")
            f.write(f"      Categoria: {l.get('categoria', '')}\n")
            f.write(f"      Fonte:     {l.get('fonte', '')}\n\n")
    print(f"  leads_report.txt  — report testuale generato")


def write_html(leads: List[Dict[str, Any]], path: Path) -> None:
    leads_with_phone = [l for l in leads if l.get("telefono")]

    rows = []
    for l in leads_with_phone:
        nome = html.escape(l["nome"])
        phone = l["telefono"]
        display_phone = html.escape(l.get("telefono_display", phone))
        indirizzo = html.escape(l.get("indirizzo", ""))
        rating = l.get("rating")
        rating_str = f"{rating}" if rating else "—"
        vertical = l.get("verticale", "generico")
        group = template_group(vertical)
        tpl = WA_TEMPLATES.get(group, WA_TEMPLATES["generico"])
        msg = tpl.format(nome=l["nome"])
        link = wa_link(phone, msg)
        vertical_badge = html.escape(vertical)

        rows.append(f"""
        <tr>
          <td><strong>{nome}</strong><br>
              <span class="cat">{html.escape(l.get('categoria', ''))}</span></td>
          <td>{display_phone}</td>
          <td>{indirizzo}</td>
          <td class="center">{rating_str}</td>
          <td><span class="badge">{vertical_badge}</span></td>
          <td class="center">
            <a class="btn" href="{link}" target="_blank" rel="noopener">
              Invia WhatsApp
            </a>
          </td>
        </tr>""")

    no_phone_section = ""
    leads_no_phone = [l for l in leads if not l.get("telefono")]
    if leads_no_phone:
        no_phone_rows = ""
        for l in leads_no_phone:
            no_phone_rows += f"""
            <tr>
              <td>{html.escape(l['nome'])}</td>
              <td>{html.escape(l.get('indirizzo', ''))}</td>
              <td>{html.escape(l.get('categoria', ''))}</td>
            </tr>"""
        no_phone_section = f"""
        <h2>Lead senza telefono ({len(leads_no_phone)})</h2>
        <table>
          <thead><tr><th>Nome</th><th>Indirizzo</th><th>Categoria</th></tr></thead>
          <tbody>{no_phone_rows}</tbody>
        </table>"""

    page = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FLUXION — WhatsApp Lead Links</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #f5f5f5; color: #333; padding: 24px; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 4px; }}
  .subtitle {{ color: #666; margin-bottom: 20px; font-size: 0.9rem; }}
  .stats {{ display:flex; gap:16px; margin-bottom:20px; flex-wrap:wrap; }}
  .stat {{ background:#fff; border-radius:8px; padding:12px 20px;
           box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .stat strong {{ font-size: 1.5rem; color: #2563eb; }}
  table {{ width:100%; border-collapse:collapse; background:#fff;
           border-radius:8px; overflow:hidden;
           box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-bottom:24px; }}
  th {{ background: #1e293b; color:#fff; padding:10px 12px; text-align:left;
       font-size:0.85rem; text-transform:uppercase; letter-spacing:.03em; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #eee; font-size:0.9rem;
       vertical-align:top; }}
  tr:hover td {{ background: #f0f7ff; }}
  .center {{ text-align:center; }}
  .cat {{ color:#888; font-size:0.8rem; }}
  .badge {{ display:inline-block; background:#e0e7ff; color:#3730a3;
            border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:600; }}
  .btn {{ display:inline-block; background:#25D366; color:#fff; text-decoration:none;
          padding:8px 16px; border-radius:6px; font-weight:600; font-size:0.85rem;
          white-space:nowrap; transition: background .15s; }}
  .btn:hover {{ background:#1ebe57; }}
  h2 {{ font-size:1.2rem; margin:24px 0 12px; }}
</style>
</head>
<body>
  <h1>FLUXION — Lead WhatsApp</h1>
  <p class="subtitle">Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>

  <div class="stats">
    <div class="stat">Lead totali<br><strong>{len(leads)}</strong></div>
    <div class="stat">Con telefono<br><strong>{len(leads_with_phone)}</strong></div>
    <div class="stat">Senza telefono<br><strong>{len(leads_no_phone)}</strong></div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Attivit&agrave;</th><th>Telefono</th><th>Indirizzo</th>
        <th>Rating</th><th>Verticale</th><th>Azione</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows) if rows else '<tr><td colspan="6" class="center">Nessun lead con telefono</td></tr>'}
    </tbody>
  </table>

  {no_phone_section}
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"  wa_links.html     — {len(leads_with_phone)} link WhatsApp pronti")


# ===================================================================
# CLI
# ===================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="FLUXION Lead Generator — Google Maps → WhatsApp outreach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python scripts/lead_generator.py --mode paste --input input_leads.txt
  python scripts/lead_generator.py --mode api --query "parrucchiere" --city "Milano" --api-key $KEY
  python scripts/lead_generator.py --mode links --input scripts/leads/leads.json
        """,
    )
    parser.add_argument("--mode", choices=["paste", "api", "links"], default="paste",
                        help="Modalita' (default: paste)")
    parser.add_argument("--input", "-i", type=str,
                        help="File di input (paste: testo grezzo, links: leads.json)")
    parser.add_argument("--query", "-q", type=str, help="Query Places API (es. 'parrucchiere')")
    parser.add_argument("--city", "-c", type=str, help="Citta' per query API")
    parser.add_argument("--api-key", type=str, help="Google Maps API key")
    parser.add_argument("--vertical", "-v", type=str, default="auto",
                        help="Forza verticale (default: auto-detect)")
    parser.add_argument("--max-results", type=int, default=20,
                        help="Max risultati API (default: 20)")
    parser.add_argument("--output-dir", "-o", type=str, default=str(OUTPUT_DIR),
                        help=f"Cartella output (default: {OUTPUT_DIR})")

    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "leads.json"
    html_path = out_dir / "wa_links.html"
    report_path = out_dir / "leads_report.txt"

    # --- Mode: links (regenerate from existing JSON) ---
    if args.mode == "links":
        src = Path(args.input) if args.input else json_path
        if not src.exists():
            print(f"ERROR: {src} non trovato.", file=sys.stderr)
            sys.exit(1)
        with open(src, "r", encoding="utf-8") as f:
            leads = json.load(f)
        print(f"\nRigenerazione link da {src} ({len(leads)} lead)")
        write_html(leads, html_path)
        write_report(leads, report_path)
        print(f"\nDone. Apri: file://{html_path.resolve()}")
        return

    # --- Mode: paste ---
    if args.mode == "paste":
        src = Path(args.input) if args.input else Path("input_leads.txt")
        if not src.exists():
            print(f"ERROR: File '{src}' non trovato.", file=sys.stderr)
            print("Crea il file con il testo copiato da Google Maps e riprova.", file=sys.stderr)
            sys.exit(1)
        with open(src, "r", encoding="utf-8") as f:
            raw = f.read()
        if not raw.strip():
            print("ERROR: File di input vuoto.", file=sys.stderr)
            sys.exit(1)
        new_leads = parse_paste(raw)
        if args.vertical != "auto":
            for l in new_leads:
                l["verticale"] = args.vertical
        print(f"\nParsati {len(new_leads)} lead dal file paste")

    # --- Mode: api ---
    elif args.mode == "api":
        if not args.query or not args.city:
            print("ERROR: --query e --city sono obbligatori per mode api.", file=sys.stderr)
            sys.exit(1)
        if not args.api_key:
            api_key = os.environ.get("GOOGLE_MAPS_KEY", "")
            if not api_key:
                print("ERROR: --api-key o variabile GOOGLE_MAPS_KEY richiesta.", file=sys.stderr)
                sys.exit(1)
        else:
            api_key = args.api_key
        print(f"\nRicerca API: '{args.query}' a {args.city} (max {args.max_results})...")
        new_leads = search_places_api(args.query, args.city, api_key, args.max_results)
        if args.vertical != "auto":
            for l in new_leads:
                l["verticale"] = args.vertical
        print(f"  Trovati {len(new_leads)} risultati dall'API")

    else:
        parser.print_help()
        sys.exit(1)

    # --- Dedup against existing ---
    existing = load_existing_leads(json_path)
    unique_leads, skipped = deduplicate(new_leads, existing)
    if skipped:
        print(f"  Duplicati skippati: {skipped}")

    # Merge
    all_leads = list(existing.values()) + unique_leads

    # --- Write outputs ---
    print(f"\nOutput in {out_dir}/")
    write_json(all_leads, json_path)
    write_html(all_leads, html_path)
    write_report(all_leads, report_path)

    print(f"\nDone! {len(unique_leads)} nuovi lead aggiunti (totale: {len(all_leads)})")
    print(f"Apri: file://{html_path.resolve()}")


if __name__ == "__main__":
    main()
