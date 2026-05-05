---
title: "Lint Report — Wiki Health"
type: lint-report
slug: _lint-report
sources_consumed: []
last_ingest: 2026-05-04
status: stable
related: []
verticals: [all]
---

# Lint Report — Wiki Health (S185-A bootstrap)

> Generato 2026-05-04 da script Python inline (vedi `log.md` entry lint).
> Scope: 10 wiki files (1 overview + 4 entities + 4 concepts + 1 source + this report).
> Target AC9: **0 CRITICAL (PII), max 2 WARN acceptable seed-state**.

## Summary

| Categoria | Count | Target | Status |
|-----------|-------|--------|--------|
| CRITICAL (PII leak) | **0** | 0 | ✅ PASS |
| WARN | 2 | ≤2 | ✅ PASS (false positives, see below) |
| INFO | 0 | unbounded | ✅ |

## Inbound link map

| Page | Inbound count | Note |
|------|--------------|------|
| `license-key` | 10 | hub naturale (referenced by tutti) |
| `sara-voice-agent` | 10 | hub Pro tier feature |
| `pricing-tiers` | 8 | cross-cutting commerciale |
| `network-firewall` | 8 | cross-cutting tecnico |
| `gdpr-compliance` | 6 | cross-cutting compliance |
| `verticals-coverage` | 6 | cross-cutting product |
| `win10-installation` | 3 | install-specific |
| `three-pillars` | 2 | concept ad alto livello |
| `win10-fresh-compat-summary` | 1 | source summary (atteso 1 dal entity) |
| `overview` | 0 | entry point — 0 inbound atteso ✅ |

## CRITICAL issues

Nessuna. ✅

- ✅ Nessuna email NON white-list (`fluxion.gestionale@gmail.com` o `onboarding@resend.dev` only)
- ✅ Nessun numero telefono italiano in chiaro
- ✅ Nessun nome cliente esposto

## WARN issues

### W1+W2: `wiki/overview.md` 2 broken link `[[link]]`

**False positive**: il pattern `[[link]]` appare in posizione inline-code backtick come **esempio illustrativo** del format link nel template:

```
sez. "How to query": "compose answer con citation `[[link]]` + `[raw/path:lines]`"
sez. "Tone of voice": "Citazioni esplicite sempre (`[[link]]` o `[raw/path:lines]`)"
```

**Verdict**: NOT a real broken link. Tech debt minore: refinare regex lint per skippare span code (`` `...` ``). Tracked come WARN acceptable seed-state.

## Coverage 3 pilastri (sez. 6.6 lint checklist)

| Pilastro | Entity ≥1 | Concept ≥1 | Status |
|----------|----------|------------|--------|
| Comunicazione | ✅ `sara-voice-agent` | ✅ `three-pillars` | OK |
| Marketing | — | ✅ `three-pillars` (parziale) | ⚠️ entity gap (deferred S185-bis) |
| Gestione | ✅ `license-key` (CRM/cassa via tier) | ✅ `verticals-coverage`, `three-pillars` | OK |
| Cross-cutting | ✅ `win10-installation`, `network-firewall` | ✅ `pricing-tiers`, `gdpr-compliance` | OK |

## Coverage 8 macro-verticali (sez. 6.6)

Tutte pagine `verticals: [all]` (cross-vertical) — accettabile bootstrap state. Verticale-specific pages = roadmap S185-bis se support reali emergono.

## Frontmatter validity (AC10)

✅ Tutti 10 file con YAML parsabile da `yaml.safe_load`. Campi obbligatori presenti su tutti.

## Slug uniqueness (AC11)

✅ Nessun duplicato slug across `entities/concepts/sources/`.

## Verticals coherence (AC12)

✅ Tutti `verticals` valori in `{all, medico, beauty, hair, auto, wellness, professionale, pet, formazione}`.

## Endpoint whitelist (sez. 6.5)

Spot-check su `network-firewall.md`: tutti FQDN citati nella whitelist documentata in HELPDESK.md sez. 6.5. ✅

## Email whitelist (sez. 6.5)

✅ Solo `fluxion.gestionale@gmail.com` e `onboarding@resend.dev` referenziate.

## Verticals number coherence (sez. 6.5)

✅ Tutti riferimenti a verticali usano "8 macro" (NOT "6 macro × 17 sotto" obsoleto). Pagine `verticals-coverage.md` + `pricing-tiers.md` esplicitamente flaggano CLAUDE.md/PRD obsoleti.

## Pricing coherence (sez. 6.5)

✅ Tutti riferimenti pricing usano canonico `trial €0 / Base €497 / Pro €897`. Pagine flaggano esplicitamente `€297` PRD obsoleto.

## Versioni coherence (sez. 6.5)

✅ Tutte citazioni versione = `v1.0.1` (build #19 S184 closure).

## Conclusione

**AC9 PASS**: 0 CRITICAL + 2 WARN false-positive accettabili in stato bootstrap.

Wiki S185-A pronto per consumption operativa founder. Prossimi step: ingest support email reali → identificare coverage gap → expand pages.
