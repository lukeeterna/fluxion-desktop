---
title: "Verticals Coverage (8 macro)"
type: concept
slug: verticals-coverage
sources_consumed: []
last_ingest: 2026-05-04
status: stable
related:
  - pricing-tiers
  - three-pillars
  - license-key
  - gdpr-compliance
verticals: [all]
---

# Verticals Coverage

> FLUXION supporta **8 macro-categorie × ~50 micro-categorie** PMI italiane. Source autoritativa: `src/types/setup.ts:66-196`. **NON 6 macro × 17 sotto** come citato in CLAUDE.md/PRD obsoleti.

## Tesi corrente

Il setup wizard FLUXION richiede al primo avvio scelta di **1 macro-verticale** che determina:

1. **Schede cliente** mostrate in CRM (es. odontogramma FDI per `medico/odontoiatra`, fototipo Fitzpatrick per `beauty/estetista_viso`)
2. **Servizi mappati** in calendario (preset durate + prezzi default per micro)
3. **NLU patterns Sara** ([[sara-voice-agent]]) — vocabolario verticale-specific (es. "appuntamento taglio" hair vs "visita medica" medico)
4. **WhatsApp template messaggi** — tono + CTA per verticale

**Limite**: 1 license = 1 macro. Cambio macro = nuovo Setup Wizard (dati preservati ma schede cambiano).

## Le 8 macro-categorie

### 1. `medico` (10 micro)
- odontoiatra, fisioterapia, medico_generico, specialista, osteopata, podologo, psicologo, nutrizionista, logopedista, dermatologo
- **Schede dedicate**: ✓ Odontoiatrica (FDI 32 denti, anamnesi, allergie), ✓ Fisioterapia (zone corpo, scale VAS/Oswestry/NDI)
- **GDPR critico**: dati Art.9 sensibili. Vedi [[gdpr-compliance]].

### 2. `beauty` (7 micro)
- estetista_viso, estetista_corpo, nail_specialist, epilazione_laser, centro_abbronzatura, spa, makeup_artist
- **Schede dedicate**: ✓ Estetica (fototipo Fitzpatrick 1-6, routine skincare, allergie)

### 3. `hair` (6 micro)
- salone_donna, barbiere, salone_unisex, extension_specialist, color_specialist, tricologo
- **Schede dedicate**: ⚠️ Parrucchiere (stub, completion roadmap S186+)

### 4. `auto` (7 micro)
- officina_meccanica, carrozzeria, elettrauto, gommista, revisioni, detailing, autolavaggio
- **Schede dedicate**: ⚠️ Auto (stub, completion roadmap S186+)

### 5. `wellness` (6 micro)
- palestra, personal_trainer, yoga_pilates, crossfit, piscina, arti_marziali
- **Schede dedicate**: ⚠️ Fitness (stub, completion roadmap S186+)

### 6. `professionale` (5 micro)
- commercialista, avvocato, consulente, agenzia, architetto
- **Schede dedicate**: nessuna (CRM standard)

### 7. `pet` (4 micro)
- toelettatura, veterinario, pensione_animali, dog_sitter
- **Schede dedicate**: ⚠️ Veterinaria (stub, completion roadmap S186+)

### 8. `formazione` (5 micro)
- scuola_guida, scuola_musica, scuola_danza, scuola_lingue, tutor_ripetizioni
- **Schede dedicate**: nessuna (CRM standard)

## Perché importa per il cliente PMI

- **Onboarding zero-friction**: Setup Wizard mostra solo le 8 macro come visual cards → 1 click → micro-categoria → completato in <2 minuti
- **Schede cliente rilevanti**: dentista non vuole vedere "Routine skincare" tra i campi cliente. Vertical filtering critico per perceived quality.
- **Sara NLU accuracy**: pattern matching verticale-specific evita confusione (es. "appuntamento" → contesto beauty vs medico)
- **WhatsApp template appropriati**: tono + ICS calendar attachment differente per verticale

## Come FLUXION lo realizza tecnicamente

- **`MACRO_CATEGORIE`** + **`MICRO_CATEGORIE`** records in `src/types/setup.ts:66-196`
- **Setup Wizard** in `src/components/Setup*.tsx` consuma type definitions
- **Schede React verticali** in `src/components/schede/<Verticale>Scheda.tsx` (3 complete + 5 stub)
- **Sara verticale config** in `voice-agent/docs/CONFIGURATION.md` (services_mapping per macro)

## Stato implementazione schede cliente

| Macro | Stato scheda | File |
|-------|-------------|------|
| medico/odontoiatra | ✅ complete | `src/components/schede/OdontoiatricaScheda.tsx` (~300 righe) |
| medico/fisioterapia | ✅ complete | `src/components/schede/FisioterapiaScheda.tsx` (~250 righe) |
| beauty/estetista | ✅ complete | `src/components/schede/EstericaScheda.tsx` (~280 righe) |
| hair | ⚠️ stub | `ParrucchiereScheda.tsx` placeholder |
| auto | ⚠️ stub | `AutoScheda.tsx` placeholder |
| medico/specialista | ⚠️ stub | `MedicaScheda.tsx` placeholder |
| wellness | ⚠️ stub | `FitnessScheda.tsx` placeholder |
| pet | ⚠️ stub | `VeterinariaScheda.tsx` placeholder |
| professionale | — | nessuna scheda dedicata (CRM standard) |
| formazione | — | nessuna scheda dedicata (CRM standard) |

## Numeri obsoleti da NON usare

| Source | Verticali citati | Status |
|--------|-------------------|--------|
| `src/types/setup.ts:66-196` | **8 macro × ~50 micro** | ✓ AUTHORITATIVE |
| `CLAUDE.md` § Verticali | "6 macro x 17 sotto-verticali" | ❌ OBSOLETO |
| `PRD-FLUXION-COMPLETE.md` § 3.2 | "6 macro" | ❌ OBSOLETO |

> Quando l'agente trova "6 macro" nei doc → flag contradiction sez. 6.5 [HELPDESK.md], usa fonte code.

## Domande aperte / Tech debt

- **5/8 schede stub** → completion roadmap S186+
- **Multi-vertical license** non disponibile (1 license = 1 macro). Scenario "cliente è sia parrucchiere che estetista" = 2 license.
- **Setup Wizard step-by-step per verticale** (gap docs) — onboarding tour customizzato per macro

## Sources
- `src/types/setup.ts:66-196` — `MACRO_CATEGORIE` + `MICRO_CATEGORIE` records (autoritative)
- `src/components/schede/*.tsx` — implementazione schede React
- `voice-agent/docs/CONFIGURATION.md` — services_mapping verticale-specific
