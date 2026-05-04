---
title: "Wiki Overview"
type: overview
slug: overview
sources_consumed: []
last_ingest: 2026-05-04
status: stable
related:
  - pricing-tiers
  - three-pillars
  - verticals-coverage
  - win10-installation
  - sara-voice-agent
  - license-key
verticals: [all]
---

# FLUXION Helpdesk Wiki — Overview

> Entry point synthesis del wiki. Leggi questo PRIMA di rispondere a query support.

## Cosa è FLUXION

**FLUXION** è un gestionale desktop per **PMI italiane** (1-15 dipendenti) di **8 macro-verticali**: medico, beauty, hair, auto, wellness, professionale, pet, formazione.

- **Stack tecnico**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Modello commerciale**: lifetime license, NO SaaS, NO subscription
- **Pricing** ([[pricing-tiers]]): trial €0 (30gg) / Base €497 / Pro €897
- **3 pilastri** ([[three-pillars]]): Comunicazione | Marketing | Gestione
- **Voice agent** ([[sara-voice-agent]]): "Sara" 24/7 (Pro tier), 5-layer RAG, 23 stati FSM

## Wiki structure

Pattern: **Karpathy LLM Wiki** (`raw → wiki → schema`).

```
docs/helpdesk-wiki/
├── HELPDESK.md          ← THE config (workflow + templates)
├── index.md             ← catalogo (sempre aggiornato)
├── log.md               ← chrono append-only
├── raw/                 ← IMMUTABLE source documents
│   ├── install/         ← win10-fresh-compat.md, network-requirements.md
│   ├── product/         ← PRD slices, pricing snapshot
│   ├── voice/           ← SARA-lifetime-spec, PRD-VOICE-AGENT
│   ├── verticals/       ← 8 macro × ~50 micro
│   ├── compliance/      ← GDPR audit trail plan
│   ├── support-emails/  ← email founder→cliente PII-redacted (gitignored)
│   └── transcripts/     ← YouTube/screen-recording (skill youtube-transcript-fetch)
└── wiki/                ← LLM-MANAGED pages
    ├── overview.md      ← questo file
    ├── entities/        ← cose concrete (1 file = 1 cosa nominabile)
    ├── concepts/        ← idee trasversali
    └── sources/         ← 1 page = 1 source consumed (summary + cross-links)
```

**Invariante**: `raw/` è immutable. L'agente LLM scrive solo in `wiki/`.

## How to query (founder)

1. **Domanda specifica**: *"Cliente chiede X"* → agente legge `index.md` → legge 2-5 candidate pages → compose answer con citation `[[link]]` + `[raw/path:lines]`.
2. **Esplora wiki**: `cat docs/helpdesk-wiki/index.md` per vedere catalogo aggiornato.
3. **Cronologia**: `grep "^## \[" docs/helpdesk-wiki/log.md | tail -10`.

Per workflow completi vedi [HELPDESK.md](../HELPDESK.md) sez. 2.

## How to add knowledge (founder)

1. **Drop source** in `raw/<categoria>/<file>.md` (es. `raw/install/new-issue.md`).
2. **Trigger ingest**: dire all'agente *"Ingest raw/install/new-issue.md"*.
3. Agente: discute takeaway → conferma → crea source summary + entity/concept pages → aggiorna index.md + log.md.

**Email cliente**: PII redaction manuale OBBLIGATORIA prima di committare in `raw/support-emails/` (gitignored di default per safety).

## Coverage attuale (S185-A bootstrap)

- ✅ **Cross-cutting**: install (Win10), license key, pricing, network/firewall, GDPR
- ✅ **Voice**: Sara setup (entity)
- ✅ **3 pilastri**: concept page coverage minima
- ⚠️ **Verticali specifici**: 0 pagine (tutto `[all]` v1) — gap S185-bis se support reali emergono
- ⚠️ **Gap noti**: refund, multi-location, auto-update trust, data export, fatturazione XML, WhatsApp UX (vedi [index.md § Gap noti](../index.md#gap-noti))

## Stato sistema (snapshot 2026-05-04)

- **Versione corrente**: FLUXION v1.0.1 (build #19 SHA256 `15db0dbb...60f6` Win MSI)
- **Sara latency**: ~1330ms (target <800ms, tech debt v1.1)
- **Build CI**: 5 root causes S184 risolte, MSI Win + DMG macOS-arm integri
- **Tech debt aperti**: #4 Tauri updater key regen (founder action POST-S184)

## Tone of voice (per response)

- **Italiano** sempre
- **Chiaro, tecnico-friendly, zero gergo**
- **Zero emoji** se non richiesti
- **Citazioni esplicite** sempre (`[[link]]` o `[raw/path:lines]`)
- **Concisione**: risposta diretta in 1-3 frasi, dettagli sotto se utili

## Out of scope wiki v1

- Mirror pubblico (v2 dopo 10 clienti reali)
- Embeddings / RAG vector DB (filesystem + grep bastano sotto 100 pagine)
- Auto-ingest Gmail (PII risk)
- Multi-lingua (italiano only)
