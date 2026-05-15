---
title: "Pricing Tiers"
type: concept
slug: pricing-tiers
sources_consumed: []
last_ingest: 2026-05-04
status: stable
related:
  - license-key
  - sara-voice-agent
  - three-pillars
  - verticals-coverage
verticals: [all]
---

# Pricing Tiers

> Modello commerciale FLUXION: **lifetime license**, NO SaaS, NO subscription. 3 tier (trial / Base / Pro). Source autoritativa: `src/types/setup.ts:202-227`.

## Tesi corrente

FLUXION rifiuta il modello SaaS PMI italiane (€39-99/mese) per allinearsi a preferenza founder-target: pagamento unico lifetime con aggiornamenti permanenti. Pricing posizionato tra "freemium giocattolo" e "enterprise complesso":

- **trial** — €0 / 30 giorni — funzionalità complete (esclusa Sara permanente)
- **Base** — **€497 lifetime** — gestionale completo + 1 verticale (CRM + Calendario + Fatturazione)
- **Pro** — **€897 lifetime** — Base + Sara voice 24/7 + VoIP + WhatsApp automatici + Loyalty

Stripe checkout 1.5% commissione (margine altissimo per founder, prezzo accessibile per PMI 1-15 dipendenti).

## Comparison matrix

| Feature | trial €0 (30gg) | **Base €497** | **Pro €897** |
|---------|-----------------|---------------|--------------|
| **Gestione** | | | |
| CRM clienti illimitati | ✓ | ✓ | ✓ |
| Calendario appuntamenti | ✓ | ✓ | ✓ |
| Schede cliente verticali | 1 macro | 1 macro | 1 macro (espandibile) |
| Cassa + scontrini | ✓ | ✓ | ✓ |
| Fatturazione XML (FatturaPA + SDI) | ✓ | ✓ | ✓ |
| Multi-operatore | ✓ | ✓ | ✓ |
| **Comunicazione** | | | |
| WhatsApp Business reminder | — | — | ✓ |
| Email transazionali (Resend) | ✓ | ✓ | ✓ |
| **Sara voice agent** | trial 30gg | trial 30gg | ✓ permanente |
| VoIP integrato (numero dedicato) | — | — | ✓ |
| **Marketing** | | | |
| Loyalty card / punti | — | — | ✓ |
| Pacchetti / abbonamenti cliente | — | — | ✓ |
| **Lifecycle** | | | |
| Aggiornamenti (semver patch+minor) | ✓ | lifetime | lifetime |
| Self-hosted SQLite (no vendor lock-in) | ✓ | ✓ | ✓ |
| Hardware fingerprint bound | ✓ | ✓ | ✓ |
| Supporto founder via email | best-effort | priority | priority |

## Perché importa per il cliente PMI

- **Saloni / parrucchieri / barbieri** (verticale `hair`): Base €497 = ROI <2 mesi vs gestionale SaaS €49/mese
- **Estetiste / nail / spa** (verticale `beauty`): Pro €897 attraente per Sara booking notturno (segmento beauty alta domanda telefonica)
- **Cliniche / studi medici** (verticale `medico`): tier Pro per Sara + WhatsApp reminder (compliance GDPR critica, vedi [[gdpr-compliance]])
- **Officine / gommisti** (verticale `auto`): Base sufficiente, Sara non priorità (chiamate brevi, walk-in)
- **Palestre / personal trainer** (verticale `wellness`): Pro per Loyalty + Sara prenotazione lezioni gruppo

## Come FLUXION lo realizza tecnicamente

- **License Ed25519** ([[license-key]]) — verifica offline, no phone-home, hardware fingerprint binding
- **Stripe webhook → CF Worker → Resend email** — pipeline acquisto zero-cost (1.5% commissione Stripe + free tier CF + free tier Resend)
- **Setup Wizard** scelta verticale al primo avvio → 1 macro tra 8 ([[verticals-coverage]])
- **Tier upgrade**: nuova license sostituisce vecchia, dati preservati (no migration data)

## Refund policy

⚠️ **Gap documentazione** (S185-bis target). Ad oggi NO refund window/criteri formalizzati. Domande refund → handoff manuale a `fluxion.gestionale@gmail.com`.

## Numeri obsoleti da NON usare

| Source | Tier prezzo citato | Status |
|--------|---------------------|--------|
| `src/types/setup.ts:202-227` | "trial €0 / Base €497 / Pro €897" | ✓ AUTHORITATIVE (source primaria code) |
| `CLAUDE.md` project root | "Base €497 / Pro €897" prezzi ✓ | ⚠️ pricing OK ma feature claim "Base €497: gestionale + WhatsApp + Sara 30gg trial" è OBSOLETO — WhatsApp è in Pro ONLY (vedi setup.ts:217 vs 224). Treat code as source of truth. |
| `PRD-FLUXION-COMPLETE.md` | "Pro €497 / Enterprise €897" | ✓ allineato 2-tier post-S241-P0 cleanup (D-01 VOS) |
| Landing `fluxion-landing.pages.dev` | da verificare aggiornamento | ⚠️ TODO check coerenza |

## Domande aperte / Tech debt

- **Refund policy formalizzata** — gap critico, S185-bis priority
- **License downgrade** (Pro→Base se cliente cost-cutting) — workflow non definito
- **Tier "Clinic"** — citato in CLAUDE.md "nascosto per ora" — roadmap futura
- **Multi-location pricing** — 1 license = 1 attività, gap docs scenario capogruppo

## Sources
- `src/types/setup.ts:202-227` — tier definition autoritativa code-side
- `CLAUDE.md` § Identity — pricing string canonico
- `.claude/rules/architecture-distribution.md` § "Pagamento" — pipeline tecnica
