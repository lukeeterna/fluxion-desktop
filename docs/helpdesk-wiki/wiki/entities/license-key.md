---
title: "License Key"
type: entity
slug: license-key
sources_consumed: []
last_ingest: 2026-05-04
status: stable
related:
  - pricing-tiers
  - win10-installation
  - sara-voice-agent
  - gdpr-compliance
  - verticals-coverage
verticals: [all]
---

# License Key

> License key Ed25519 offline-verifiable. Distribuita via email post-acquisto Stripe. Determina tier (trial/Base/Pro) e funzionalità abilitate.

## TL;DR
- Key Ed25519 firmata server-side, verificabile **offline** (no phone-home)
- 3 tier: `trial` €0 (30gg) | `base` €497 lifetime | `pro` €897 lifetime ([[pricing-tiers]])
- Hardware fingerprint bound: hostname + CPU + RAM + OS (cambio HW = nuova attivazione)
- License email da `onboarding@resend.dev` (sender Resend free tier)

## Prerequisiti
- Acquisto completato su Stripe Checkout (commissione 1.5%)
- Email valida fornita in checkout
- Hardware target identificato (FLUXION genera fingerprint al primo avvio)

## Procedura attivazione

1. **Acquisto** su landing `fluxion-landing.pages.dev` → Stripe Checkout
2. **Email license**: arriva entro ~1 minuto da `onboarding@resend.dev` con:
   - License key (formato Ed25519, ~88 caratteri base64)
   - Tier acquistato (Base €497 o Pro €897)
   - Link download installer
3. **Primo avvio FLUXION**: Setup Wizard chiede license key
4. **Paste key** → FLUXION:
   - Verifica firma Ed25519 con public key embedded (no internet richiesto)
   - Genera hardware fingerprint locale
   - Salva license + fingerprint in SQLite locale (cifrato AES-256-GCM)
5. **Verticale + Setup**: scegli macro-categoria ([[verticals-coverage]]) → onboarding completato

## Tier comparison

| Feature | trial €0 (30gg) | Base €497 | Pro €897 |
|---------|-----------------|-----------|----------|
| CRM clienti | ✓ | ✓ | ✓ |
| Calendario appuntamenti | ✓ | ✓ | ✓ |
| Fatturazione XML (FatturaPA) | ✓ | ✓ | ✓ |
| 1 verticale (8 macro disponibili) | ✓ | ✓ | ✓ |
| WhatsApp Business reminder | — | — | ✓ |
| Loyalty + Pacchetti | — | — | ✓ |
| **Sara voice agent** ([[sara-voice-agent]]) | trial 30gg | trial 30gg | ✓ permanente |
| VoIP integrato | — | — | ✓ |
| Aggiornamenti lifetime | ✓ | ✓ | ✓ |
| Self-hosted SQLite (no cloud lock-in) | ✓ | ✓ | ✓ |

> **Nota**: prezzi authoritative da `src/types/setup.ts:202-227`. CLAUDE.md/PRD obsoleti citano €297/€497/€897 — IGNORARE.

## Errori attivazione

| Sintomo | Causa | Fix |
|---------|-------|-----|
| "License key non valida" | Typo paste o key per altro tier | Verifica copia integrale email (88 char base64). Re-richiesta via `fluxion.gestionale@gmail.com`. |
| "Hardware fingerprint mismatch" | Cambio HW (nuovo PC, riformat OS) | Founder rilascia nuova attivazione manuale. Email contesto a `fluxion.gestionale@gmail.com`. |
| "License scaduta" su tier lifetime | Bug clock skew sistema | Verifica orologio sistema. Tier Base/Pro non scadono. Email founder. |
| Email license non arrivata | Spam/junk filter | Cerca in junk. Se assente: contatta `fluxion.gestionale@gmail.com` con riferimento Stripe checkout. |
| Trial scaduto, vuole upgrade | Tier change post-trial | Acquisto Base/Pro su landing → nuova license key sostituisce trial. Dati esistenti preservati. |

## Tech debt aperto (S184 closure)

- **#4 Tauri Updater Key Regen** — founder action POST-S184: regenerate `TAURI_SIGNING_PRIVATE_KEY` + GitHub Secrets + `tauri.conf.json::updater.pubkey`. Impatto utenti: nessuno fino a primo update auto-distribuito. Reference: [HANDOFF.md](../../../../HANDOFF.md) (sezione "S184 closure").

## Refund policy

⚠️ **Gap documentazione** (S185-bis target): refund window, criteri, processo reversal Stripe. Ad oggi NO documentazione formale — domande refund vanno gestite manualmente da founder via `fluxion.gestionale@gmail.com`.

## Cross-references
- [[pricing-tiers]] — confronto Base/Pro/trial dettagliato
- [[win10-installation]] — license key richiesta in Setup Wizard
- [[sara-voice-agent]] — Sara permanente solo tier Pro
- [[gdpr-compliance]] — fingerprint HW = pseudonymization, no PII esterne

## Sources
- `src-tauri/src/commands/license_ed25519.rs` — implementazione Ed25519 verify + fingerprint
- `src/types/setup.ts:202-227` — tier definition autoritativa
- (TODO ingest in S185-bis: refund policy doc, license downgrade procedure)
