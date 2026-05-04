---
title: "Three Pillars (Comunicazione/Marketing/Gestione)"
type: concept
slug: three-pillars
sources_consumed: []
last_ingest: 2026-05-04
status: stable
related:
  - sara-voice-agent
  - pricing-tiers
  - verticals-coverage
verticals: [all]
---

# Three Pillars

> Modello mentale FLUXION: 3 pilastri funzionali coprono il ciclo di vita PMI italiana. **Comunicazione** | **Marketing** | **Gestione**. Coerente in tutti i materiali (landing, PRD, voice agent positioning).

## Tesi corrente

FLUXION posiziona la propria offerta in 3 macro-aree dominio invece di un elenco feature:

1. **Comunicazione** — interazione cliente esterna (telefono + WhatsApp + email)
2. **Marketing** — retention + LTV (loyalty + pacchetti + campagne)
3. **Gestione** — operations interne (calendario + clienti + fatturazione + cassa)

Ogni pilastro mappa a feature concrete con tier-gating distinto ([[pricing-tiers]]).

## I 3 pilastri in dettaglio

### 1. Comunicazione (touchpoint cliente)

**Obiettivo**: ridurre carico telefonico founder/operatore, aumentare reachability 24/7.

| Feature | Tier | Note |
|---------|------|------|
| **Sara voice agent** ([[sara-voice-agent]]) | Pro €897 | 24/7 booking automatizzato, 23 stati FSM, italiano nativo |
| WhatsApp Business reminder | Base + Pro | Conferma appuntamento + promemoria T-24h |
| VoIP integrato (numero dedicato) | Pro €897 | Forwarding configurabile |
| Email transazionali (Resend) | tutti | Notifiche post-acquisto, license, ricevute |

**Verticali alta domanda**: beauty, hair, medico, wellness (settori con prenotazione telefonica intensa).

### 2. Marketing (retention + LTV)

**Obiettivo**: massimizzare lifetime value cliente PMI senza sforzo founder.

| Feature | Tier | Note |
|---------|------|------|
| Loyalty card / punti | Pro €897 | Sistema punti configurabile per verticale |
| Pacchetti / abbonamenti | Pro €897 | Es. "10 sedute massaggio", scadenze auto |
| Campagne riattivazione | TODO | Gap roadmap (clienti inattivi >60gg) |
| Recensioni Google integration | TODO | Gap roadmap (post-appuntamento auto-prompt) |

**Verticali alta priorità**: beauty, wellness, hair (recurring revenue model).

### 3. Gestione (operations interne)

**Obiettivo**: sostituire 3-5 tool separati (Excel + WhatsApp + cassa + calendario carta + fatturatore SaaS).

| Feature | Tier | Note |
|---------|------|------|
| CRM clienti illimitati | tutti | Schede vertical-specific (vedi [[verticals-coverage]]) |
| Calendario appuntamenti | tutti | Multi-operatore, drag&drop, ricorrenze |
| Cassa + scontrino | tutti | POS basic, no fiscal printer integration v1 |
| Fatturazione XML (FatturaPA + SDI) | tutti | Conforme normativa IT |
| Schede cliente verticali | tutti | 3/8 macro complete (medico/fisio/estetica), 5/8 stub |
| Multi-operatore | tutti | Roles + permessi base |
| Backup + export dati | tutti | Self-hosted SQLite, no vendor lock-in |

**Verticali**: tutti — la gestione è cross-vertical, schede sono verticale-specific ([[verticals-coverage]]).

## Perché importa per il cliente PMI

- **Decision maker semplice**: invece di valutare 30 feature, valuta "ho bisogno solo Gestione (Base €497) o anche Comunicazione/Marketing (Pro €897)?"
- **Onboarding wizard guidato**: Setup Wizard chiede in primis quali pilastri attivare → propone tier coerente
- **Pricing logic chiaro**: Sara (Comunicazione 24/7) è premium → giustifica tier Pro

## Mapping tier → pilastri attivati

| Tier | Comunicazione | Marketing | Gestione |
|------|---------------|-----------|----------|
| trial €0 | parziale (no WA, Sara trial 30gg) | — | ✓ completa |
| Base €497 | parziale (WA sì, Sara trial) | — | ✓ completa |
| Pro €897 | ✓ completa | ✓ completa | ✓ completa |

## Domande aperte / Tech debt

- **Marketing pilastro è il più immaturo** — Loyalty + Pacchetti coperti, ma campagne riattivazione + reviews Google = gap roadmap
- **Comunicazione esterna out-of-band** — SMS + chiamate cellulare non coperte (solo WhatsApp + VoIP integrato)
- **Gestione schede 5/8 verticali stub** — Parrucchiere/Auto/Medica/Fitness/Veterinaria placeholder, completion roadmap S186+
- **Cassa fiscale stampante** — integrazione fiscal printer non v1 (gap critico per cassa cliente reale Italia)

## Sources
- `CLAUDE.md` § Identity — "3 Pilastri: COMUNICAZIONE | MARKETING | GESTIONE"
- `PRD-FLUXION-COMPLETE.md` § 2-4 — feature breakdown per pilastro
- Landing `fluxion-landing.pages.dev` — positioning marketing public
