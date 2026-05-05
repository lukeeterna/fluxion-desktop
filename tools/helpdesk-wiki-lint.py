#!/usr/bin/env python3
"""
helpdesk-wiki-lint.py — FLUXION Helpdesk Wiki linter.

Implementa la checklist sez. 6 di docs/helpdesk-wiki/HELPDESK.md.

Output: docs/helpdesk-wiki/wiki/_lint-report.md (overwrite).
Exit code: 0 = 0 CRITICAL | 1 = >=1 CRITICAL (PII leak / fatal).

Usage:
    python3 tools/helpdesk-wiki-lint.py [--apply-fixes]

Senza flag = report-only. --apply-fixes propone bidirectional related fix.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "docs" / "helpdesk-wiki" / "wiki"
REPORT_PATH = WIKI_DIR / "_lint-report.md"

# Schema enums (HELPDESK sez. 4.2)
VALID_TYPES = {"entity", "concept", "source-summary", "overview", "lint-report", "query-test"}
VALID_STATUS = {"draft", "stable", "stale", "contradicted"}
VALID_VERTICALS = {"all", "medico", "beauty", "hair", "auto", "wellness", "professionale", "pet", "formazione"}
REQUIRED_FIELDS = ["title", "type", "slug", "sources_consumed", "last_ingest", "status", "related", "verticals"]

# White-list (HELPDESK sez. 6.5)
EMAIL_WHITELIST = {"fluxion.gestionale@gmail.com", "onboarding@resend.dev", "noreply@anthropic.com"}
DOMAIN_WHITELIST = {
    "fluxion-landing.pages.dev",
    "fluxion-proxy.gianlucanewtech.workers.dev",
    "github.com",
    "api.groq.com",
    "api.stripe.com",
    "api.resend.com",
    "sentry.io",
    "microsoft.com",
    "learn.microsoft.com",
    "tauri.app",
    "v2.tauri.app",
    "rust-lang.github.io",
    "go.microsoft.com",
}

# Regex (sez. 6.5 + 6.7)
LINK_RE = re.compile(r"\[\[([\w\-]+)(?:#[\w\-]+)?\]\]")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_IT_RE = re.compile(r"(?<!\d)\+?39[\s.-]?\d{3}[\s.-]?\d{6,7}(?!\d)")
URL_RE = re.compile(r"https?://([a-z0-9][a-z0-9.-]*[a-z0-9])", re.IGNORECASE)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
FENCE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)


def strip_code(text: str) -> str:
    """Remove fenced code blocks + inline code so we don't lint code samples."""
    text = FENCE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def parse_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str]:
    """Return (frontmatter_dict, body) or (None, raw) if missing/invalid."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        return None, raw
    end = raw.find("\n---\n", 4)
    if end == -1:
        return None, raw
    fm_text = raw[4:end]
    body = raw[end + 5 :]
    try:
        fm = yaml.safe_load(fm_text)
        if not isinstance(fm, dict):
            return None, raw
        return fm, body
    except yaml.YAMLError:
        return None, raw


def collect_pages() -> dict[str, dict[str, Any]]:
    """Walk wiki/ and return {slug: {path, fm, body, errors[]}}."""
    pages: dict[str, dict[str, Any]] = {}
    for path in sorted(WIKI_DIR.rglob("*.md")):
        slug_from_filename = path.stem
        fm, body = parse_frontmatter(path)
        entry = {
            "path": path,
            "rel": path.relative_to(ROOT).as_posix(),
            "slug_from_filename": slug_from_filename,
            "fm": fm,
            "body": body,
            "errors": [],
        }
        if fm is None:
            entry["errors"].append(("CRITICAL", "frontmatter YAML missing or unparsable"))
        pages[slug_from_filename] = entry
    return pages


def check_frontmatter(entry: dict[str, Any]) -> None:
    fm = entry["fm"]
    if fm is None:
        return
    for f in REQUIRED_FIELDS:
        if f not in fm:
            entry["errors"].append(("CRITICAL", f"missing required field '{f}'"))
    if fm.get("type") not in VALID_TYPES:
        entry["errors"].append(("WARN", f"invalid type '{fm.get('type')}' (allowed: {sorted(VALID_TYPES)})"))
    if fm.get("status") not in VALID_STATUS:
        entry["errors"].append(("WARN", f"invalid status '{fm.get('status')}'"))
    if fm.get("slug") != entry["slug_from_filename"]:
        entry["errors"].append(("CRITICAL", f"slug '{fm.get('slug')}' != filename '{entry['slug_from_filename']}'"))
    verticals = fm.get("verticals") or []
    if not isinstance(verticals, list):
        entry["errors"].append(("CRITICAL", "verticals must be a list"))
    else:
        for v in verticals:
            if v not in VALID_VERTICALS:
                entry["errors"].append(("CRITICAL", f"invalid vertical '{v}' (allowed: {sorted(VALID_VERTICALS)})"))
    related = fm.get("related") or []
    if not isinstance(related, list):
        entry["errors"].append(("CRITICAL", "related must be a list"))


def check_link_integrity(pages: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    """Return inbound_map = {slug: {referrers}}."""
    known_slugs = set(pages.keys())
    inbound: dict[str, set[str]] = defaultdict(set)
    for slug, entry in pages.items():
        body_no_code = strip_code(entry["body"])
        for m in LINK_RE.finditer(body_no_code):
            target = m.group(1)
            if target == slug:
                continue
            if target not in known_slugs:
                entry["errors"].append(("WARN", f"broken link [[{target}]] (no such wiki page)"))
            else:
                inbound[target].add(slug)
    return inbound


META_TYPES = {"overview", "lint-report", "query-test"}


def is_meta_page(entry: dict[str, Any]) -> bool:
    """Meta pages (overview, lint-report, query-test, slug starting with _) are
    excluded from bidirectional `related` reciprocity requirements (HELPDESK sez. 5).
    Rationale: overview is the hub (0 inbound expected), meta tests cite many pages
    without semantic 'related' meaning.
    """
    if entry["slug_from_filename"].startswith("_"):
        return True
    fm = entry["fm"] or {}
    return fm.get("type") in META_TYPES


def check_bidirectional(pages: dict[str, dict[str, Any]]) -> list[tuple[str, str]]:
    """Return list of asymmetric pairs (A, B) where A.related has B but B.related missing A.
    Skips pairs where either A or B is a meta page (overview, lint-report, query-test, _*).
    """
    asymmetric: list[tuple[str, str]] = []
    for slug, entry in pages.items():
        fm = entry["fm"]
        if not fm:
            continue
        if is_meta_page(entry):
            continue
        related = fm.get("related") or []
        for target in related:
            if target == slug:
                continue
            target_entry = pages.get(target)
            if not target_entry or not target_entry["fm"]:
                entry["errors"].append(("WARN", f"related '{target}' does not exist as a wiki page"))
                continue
            if is_meta_page(target_entry):
                continue
            target_related = target_entry["fm"].get("related") or []
            if slug not in target_related:
                asymmetric.append((slug, target))
    return asymmetric


def check_pii(pages: dict[str, dict[str, Any]]) -> list[tuple[str, str]]:
    """Return CRITICAL PII matches as (slug, detail)."""
    findings: list[tuple[str, str]] = []
    for slug, entry in pages.items():
        body_no_code = strip_code(entry["body"])
        # Phone IT
        for m in PHONE_IT_RE.finditer(body_no_code):
            findings.append((slug, f"italian phone number leak: '{m.group(0)}'"))
            entry["errors"].append(("CRITICAL", f"PII phone leak: '{m.group(0)}'"))
        # Email non-whitelist
        for m in EMAIL_RE.finditer(body_no_code):
            email = m.group(0).lower()
            if email not in EMAIL_WHITELIST:
                findings.append((slug, f"non-whitelist email: '{email}'"))
                entry["errors"].append(("CRITICAL", f"PII email leak: '{email}'"))
    return findings


def check_domains(pages: dict[str, dict[str, Any]]) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for slug, entry in pages.items():
        body_no_code = strip_code(entry["body"])
        for m in URL_RE.finditer(body_no_code):
            host = m.group(1).lower()
            # Strip subdomain prefix progressively to match whitelist
            allowed = any(host == d or host.endswith("." + d) for d in DOMAIN_WHITELIST)
            if not allowed:
                findings.append((slug, host))
                entry["errors"].append(("WARN", f"non-whitelist domain: '{host}'"))
    return findings


def check_obsolete_strings(pages: dict[str, dict[str, Any]]) -> list[tuple[str, str]]:
    """Detect known-obsolete strings: 6 macro × 17, €297, etc.
    Skip pages that explicitly flag them as obsoleto/IGNORARE/OBSOLETO.
    """
    findings: list[tuple[str, str]] = []
    obsolete_patterns = [
        (re.compile(r"6\s*macro\s*[x×]\s*17"), "obsolete '6 macro x 17'"),
        (re.compile(r"€\s*297\b"), "obsolete tier price '€297'"),
    ]
    for slug, entry in pages.items():
        body = entry["body"]
        body_no_code = strip_code(body)
        for pat, label in obsolete_patterns:
            for m in pat.finditer(body_no_code):
                # Look at surrounding context (200 chars) for OBSOLETO / IGNORARE / obsoleti
                start = max(0, m.start() - 200)
                end = min(len(body_no_code), m.end() + 200)
                ctx = body_no_code[start:end].upper()
                if "OBSOLET" in ctx or "IGNORARE" in ctx or "NON USARE" in ctx:
                    continue  # explicitly flagged as obsoleto
                findings.append((slug, label))
                entry["errors"].append(("WARN", label))
    return findings


def check_freshness(pages: dict[str, dict[str, Any]]) -> None:
    today = date.today()
    for slug, entry in pages.items():
        fm = entry["fm"]
        if not fm:
            continue
        last = fm.get("last_ingest")
        if isinstance(last, str):
            try:
                last_d = datetime.strptime(last, "%Y-%m-%d").date()
            except ValueError:
                entry["errors"].append(("WARN", f"last_ingest '{last}' not YYYY-MM-DD"))
                continue
        elif isinstance(last, date):
            last_d = last
        else:
            entry["errors"].append(("WARN", "last_ingest missing or wrong type"))
            continue
        age = (today - last_d).days
        if age > 90 and fm.get("status") == "stable":
            entry["errors"].append(("INFO", f"last_ingest {age}d ago — consider 'stale' status"))
        if fm.get("status") == "draft" and age > 14:
            entry["errors"].append(("INFO", f"draft for {age}d — promote or delete"))


def check_coverage(pages: dict[str, dict[str, Any]]) -> list[str]:
    """Return list of coverage gap warnings."""
    warnings: list[str] = []
    pillars = {
        "Comunicazione": ["sara-voice-agent"],
        "Marketing": [],  # known gap
        "Gestione": ["license-key", "verticals-coverage"],
    }
    for pillar, expected in pillars.items():
        if not any(p in pages for p in expected):
            warnings.append(f"pillar '{pillar}' has no entity reference (expected one of {expected})")
    return warnings


def render_report(
    pages: dict[str, dict[str, Any]],
    inbound: dict[str, set[str]],
    asymmetric: list[tuple[str, str]],
    pii_findings: list[tuple[str, str]],
    domain_findings: list[tuple[str, str]],
    obsolete_findings: list[tuple[str, str]],
    coverage_gaps: list[str],
) -> str:
    counts = {"CRITICAL": 0, "WARN": 0, "INFO": 0}
    for entry in pages.values():
        for sev, _ in entry["errors"]:
            counts[sev] = counts.get(sev, 0) + 1

    today = date.today().isoformat()
    lines: list[str] = []
    lines.append("---")
    lines.append('title: "Lint Report — Wiki Health"')
    lines.append("type: lint-report")
    lines.append("slug: _lint-report")
    lines.append("sources_consumed: []")
    lines.append(f"last_ingest: {today}")
    lines.append("status: stable")
    lines.append("related: []")
    lines.append("verticals: [all]")
    lines.append("---")
    lines.append("")
    lines.append("# Lint Report — Wiki Health")
    lines.append("")
    lines.append(f"> Auto-generated by `tools/helpdesk-wiki-lint.py` on {today}.")
    lines.append(f"> Scope: {len(pages)} wiki files in `docs/helpdesk-wiki/wiki/`.")
    lines.append("> Target AC9: **0 CRITICAL (PII leak / fatal schema)**.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Severity | Count | Target |")
    lines.append("|----------|-------|--------|")
    lines.append(f"| CRITICAL | **{counts['CRITICAL']}** | 0 |")
    lines.append(f"| WARN | {counts['WARN']} | unbounded (review) |")
    lines.append(f"| INFO | {counts['INFO']} | unbounded |")
    lines.append("")

    # Inbound link map
    lines.append("## Inbound link map")
    lines.append("")
    lines.append("| Page | Inbound count | Referrers |")
    lines.append("|------|---------------|-----------|")
    for slug in sorted(pages.keys()):
        refs = sorted(inbound.get(slug, set()))
        ref_display = ", ".join(refs) if refs else "—"
        lines.append(f"| `{slug}` | {len(refs)} | {ref_display} |")
    lines.append("")

    # Asymmetric related
    lines.append("## Bidirectional consistency (HELPDESK sez. 6.3)")
    lines.append("")
    if not asymmetric:
        lines.append("All `related` arrays are bidirectional. ✅")
    else:
        lines.append("| Source | Missing reciprocal in target |")
        lines.append("|--------|------------------------------|")
        for a, b in asymmetric:
            lines.append(f"| `{a}.related` contains `{b}` | `{b}.related` missing `{a}` |")
        lines.append("")
        lines.append("Auto-fix proposal (run with `--apply-fixes`): add missing reciprocal slugs to target pages.")
    lines.append("")

    # PII findings
    lines.append("## PII leak (CRITICAL — sez. 6.7)")
    lines.append("")
    if not pii_findings:
        lines.append("No PII leaks detected. ✅")
        lines.append("")
        lines.append(f"- Email whitelist enforced: `{', '.join(sorted(EMAIL_WHITELIST))}`")
        lines.append("- Italian phone regex `+?39 ddd dddddd[d]` → 0 matches")
    else:
        for slug, detail in pii_findings:
            lines.append(f"- **`{slug}`** — {detail}")
    lines.append("")

    # Domain whitelist
    lines.append("## Domain whitelist (sez. 6.5)")
    lines.append("")
    if not domain_findings:
        lines.append("All URLs match domain whitelist. ✅")
    else:
        seen: set[tuple[str, str]] = set()
        lines.append("| Page | Non-whitelist domain |")
        lines.append("|------|----------------------|")
        for slug, host in domain_findings:
            key = (slug, host)
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"| `{slug}` | `{host}` |")
    lines.append("")

    # Obsolete strings
    lines.append("## Obsolete strings (sez. 6.5)")
    lines.append("")
    if not obsolete_findings:
        lines.append("No unflagged obsolete strings detected. ✅")
        lines.append("")
        lines.append("- `6 macro × 17 sotto` → only in pages explicitly flagging as OBSOLETO")
        lines.append("- `€297` → only in pages explicitly flagging as OBSOLETO")
    else:
        for slug, detail in obsolete_findings:
            lines.append(f"- **`{slug}`** — {detail} (not flagged with OBSOLETO/IGNORARE/NON USARE in surrounding context)")
    lines.append("")

    # Coverage
    lines.append("## Coverage 3 pilastri (sez. 6.6)")
    lines.append("")
    if coverage_gaps:
        for w in coverage_gaps:
            lines.append(f"- ⚠️ {w}")
    else:
        lines.append("All 3 pillars have ≥1 entity reference. ✅")
    lines.append("")

    # Per-page errors
    lines.append("## Per-page issues")
    lines.append("")
    any_issue = False
    for slug in sorted(pages.keys()):
        errs = pages[slug]["errors"]
        if not errs:
            continue
        any_issue = True
        lines.append(f"### `{slug}`")
        lines.append("")
        for sev, msg in errs:
            lines.append(f"- **{sev}** — {msg}")
        lines.append("")
    if not any_issue:
        lines.append("No per-page issues. ✅")
        lines.append("")

    # Conclusion
    lines.append("## Conclusion")
    lines.append("")
    if counts["CRITICAL"] == 0:
        lines.append(f"**AC9 PASS** — 0 CRITICAL, {counts['WARN']} WARN, {counts['INFO']} INFO.")
    else:
        lines.append(f"**AC9 FAIL** — {counts['CRITICAL']} CRITICAL findings block commit.")
    lines.append("")
    return "\n".join(lines) + "\n"


RELATED_BLOCK_RE = re.compile(
    r"(^related:\s*\n(?:[ \t]+-[^\n]*\n)+)",
    re.MULTILINE,
)
RELATED_EMPTY_RE = re.compile(r"^related:\s*\[\s*\]\s*$", re.MULTILINE)


def apply_bidirectional_fixes(pages: dict[str, dict[str, Any]], asymmetric: list[tuple[str, str]]) -> int:
    """Add missing reciprocal slug to target page's related array preserving file format.

    Strategy: textual append to the existing block-list (`  - slug`) instead of yaml
    round-trip, so quotes/indent/trailing newlines are preserved verbatim.
    """
    fixes_per_target: dict[str, set[str]] = defaultdict(set)
    for source, target in asymmetric:
        fixes_per_target[target].add(source)

    applied = 0
    for target, missing in fixes_per_target.items():
        entry = pages[target]
        path: Path = entry["path"]
        text = path.read_text(encoding="utf-8")

        # Determine existing indent for related items by inspecting current YAML
        match = RELATED_BLOCK_RE.search(text)
        if match:
            block = match.group(1)
            # Find indent of first item
            first_item = re.search(r"^([ \t]+)-[ \t]", block, re.MULTILINE)
            indent = first_item.group(1) if first_item else "  "
            existing_slugs = {m.group(1) for m in re.finditer(r"^[ \t]+-[ \t]+([\w\-]+)\s*$", block, re.MULTILINE)}
            additions = ""
            for slug in sorted(missing):
                if slug in existing_slugs:
                    continue
                additions += f"{indent}- {slug}\n"
                applied += 1
            if additions:
                new_block = block + additions
                text = text[: match.start(1)] + new_block + text[match.end(1) :]
                path.write_text(text, encoding="utf-8")
        elif RELATED_EMPTY_RE.search(text):
            # Convert `related: []` to block list with new entries
            new_lines = "related:\n"
            for slug in sorted(missing):
                new_lines += f"  - {slug}\n"
                applied += 1
            text = RELATED_EMPTY_RE.sub(new_lines.rstrip(), text, count=1)
            path.write_text(text, encoding="utf-8")
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description="FLUXION Helpdesk Wiki linter")
    parser.add_argument("--apply-fixes", action="store_true", help="Apply bidirectional related auto-fixes")
    args = parser.parse_args()

    if not WIKI_DIR.is_dir():
        print(f"ERROR: wiki dir not found: {WIKI_DIR}", file=sys.stderr)
        return 2

    pages = collect_pages()
    for entry in pages.values():
        check_frontmatter(entry)

    check_freshness(pages)
    inbound = check_link_integrity(pages)
    asymmetric = check_bidirectional(pages)
    pii_findings = check_pii(pages)
    domain_findings = check_domains(pages)
    obsolete_findings = check_obsolete_strings(pages)
    coverage_gaps = check_coverage(pages)

    if args.apply_fixes and asymmetric:
        applied = apply_bidirectional_fixes(pages, asymmetric)
        print(f"Applied {applied} bidirectional fixes. Re-run lint to regenerate report.")
        return 0

    report = render_report(pages, inbound, asymmetric, pii_findings, domain_findings, obsolete_findings, coverage_gaps)
    REPORT_PATH.write_text(report, encoding="utf-8")

    critical_count = sum(1 for e in pages.values() for sev, _ in e["errors"] if sev == "CRITICAL")
    warn_count = sum(1 for e in pages.values() for sev, _ in e["errors"] if sev == "WARN")
    print(f"Lint complete: {critical_count} CRITICAL, {warn_count} WARN, asymmetric={len(asymmetric)}, pii={len(pii_findings)}")
    print(f"Report written: {REPORT_PATH.relative_to(ROOT)}")
    return 1 if critical_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
