# FLUXION Helpdesk Wiki — Index

> **Catalogo** content-oriented. Aggiornato ad ogni `ingest`.
> Per workflow operativi vedi [HELPDESK.md](HELPDESK.md).
> Per cronologia vedi [log.md](log.md).

**Stato wiki**: bootstrap S185-A | **Pagine totali**: 9 wiki + 1 source raw | **Last update**: 2026-05-04

---

## Overview

- [[overview]] — entry point synthesis del wiki, struttura e how-to-query

---

## Entities

Cose concrete (1 file = 1 cosa nominabile).

| Slug | Title | Verticals | Status | Last ingest |
|------|-------|-----------|--------|-------------|
| [[win10-installation]] | Win10 Installation | all | stable | 2026-05-04 |
| [[license-key]] | License Key | all | stable | 2026-05-04 |
| [[sara-voice-agent]] | Sara Voice Agent | all (Pro tier) | stable | 2026-05-04 |
| [[network-firewall]] | Network & Firewall | all | stable | 2026-05-04 |

---

## Concepts

Idee trasversali (non riducibili a entità singola).

| Slug | Title | Verticals | Status | Last ingest |
|------|-------|-----------|--------|-------------|
| [[pricing-tiers]] | Pricing Tiers | all | stable | 2026-05-04 |
| [[three-pillars]] | Three Pillars (Comunicazione/Marketing/Gestione) | all | stable | 2026-05-04 |
| [[verticals-coverage]] | Verticals Coverage (8 macro) | all | stable | 2026-05-04 |
| [[gdpr-compliance]] | GDPR Compliance | all | stable | 2026-05-04 |

---

## Sources

1 page = 1 source consumed (summary + cross-links).

| Slug | Original source | Status | Last ingest |
|------|----------------|--------|-------------|
| [[win10-fresh-compat-summary]] | raw/install/win10-fresh-compat.md | stable | 2026-05-04 |

---

## Coverage matrix (3 pilastri)

| Pilastro | Entities | Concepts |
|----------|----------|----------|
| Comunicazione (WhatsApp + Voice) | [[sara-voice-agent]] | [[three-pillars]] |
| Marketing (Loyalty + Pacchetti) | — | [[three-pillars]] |
| Gestione (Calendario + Schede) | [[license-key]] | [[verticals-coverage]], [[three-pillars]] |
| Cross-cutting | [[win10-installation]], [[network-firewall]] | [[pricing-tiers]], [[gdpr-compliance]] |

---

## Coverage matrix (8 verticali)

Tutte le pagine attuali sono `verticals: [all]` (cross-vertical). Pagine vertical-specific previste in S185-bis se gap emergono da support reali.

| Macro | Entities specifiche | Concepts specifici |
|-------|--------------------|--------------------|
| medico | — | — |
| beauty | — | — |
| hair | — | — |
| auto | — | — |
| wellness | — | — |
| professionale | — | — |
| pet | — | — |
| formazione | — | — |

---

## Gap noti (da audit research-1, da ingest in S185-bis)

- Refund process / license downgrade
- Bluetooth microphone troubleshooting (Sara)
- Multi-location / multi-branch
- Auto-update trust model (tech debt #4 S184)
- Corporate proxy + Groq API auth
- Data export / GDPR right-to-deletion
- Onboarding operatori aggiuntivi
- Importazione dati legacy (CSV schema)
- WhatsApp Business config UX guide
- Fatturazione XML (FatturaPA) step-by-step
