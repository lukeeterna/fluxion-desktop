# Skill: FLUXION Screenshot Capture — Enterprise Grade

> Automated screenshot system for FLUXION desktop app.
> Handles the fundamental challenge: FLUXION requires Tauri backend (Rust + SQLite) for data,
> but screenshots need to be captured without running the full app.

## Purpose

Capture production-quality screenshots of ALL FLUXION screens with realistic Italian PMI demo data.
Output: `landing/screenshots/` — ready for landing page, marketing, App Store, documentation.

## Architecture: Tauri Mock Layer

FLUXION frontend calls `invoke()` for ALL data (Tauri IPC → Rust → SQLite).
Without the backend, every page shows "Caricamento..." (loading spinner).

**Solution: Browser-injectable mock that intercepts `window.__TAURI_INTERNALS__.invoke()`**

### Mock Data Requirements

The mock MUST provide realistic Italian PMI data:
- **Business**: "Salone Bella Vita" (salone), or contextual per vertical
- **Clients**: 15+ Italian names with phone numbers (3xx xxx xxxx format)
- **Services**: Italian service names with realistic prices (€15-€120)
- **Operators**: 3-4 Italian names with specializations
- **Appointments**: Today + upcoming, various states (confermato, completato, in attesa)
- **Revenue**: Realistic daily/monthly totals for a small Italian business
- **Invoices**: Italian fiscal format (Fattura N. 2026/001, P.IVA, CF)

### Mock Commands to Implement

Priority commands that block screenshots (without these → loading screen):

```
CRITICAL (blocks rendering):
- get_setup_status → { completed: true, step: "done" }
- get_setup_config → full business config
- get_clienti / search_clienti → client list
- get_servizi → service catalog
- get_operatori → operator list
- get_appuntamenti_giorno → today's appointments
- get_appuntamenti_settimana → week view
- get_incassi_oggi → daily revenue
- get_fatture → invoice list
- get_voice_pipeline_status → { running: true, ... }
- get_diagnostics_info → system health
- get_impostazioni → all settings
- get_orari_lavoro → working hours
- get_giorni_festivi → holidays
- check_license → { valid: true, tier: "pro", ... }

SECONDARY (nice to have for richer screenshots):
- get_chiusure_cassa → cash register closings
- get_metodi_pagamento → payment methods
- get_scheda_odontoiatrica → client medical records
- list_faq_categories → FAQ categories
- get_cliente_media → client photos
- get_operatore_servizi → operator-service assignments
- get_operatore_commissioni → commissions
- get_loyalty_stats → loyalty program stats
```

## Procedure

### Step 1: Create Mock Layer (`e2e-tests/fixtures/tauri-mock.ts`)

```typescript
// Inject window.__TAURI_INTERNALS__ before page loads
// Map every invoke() command to mock data
// Export as Playwright fixture
```

### Step 2: Create Screenshot Script (`e2e-tests/tests/screenshots.spec.ts`)

```
For each route:
  1. Inject Tauri mock via page.addInitScript()
  2. Navigate to route
  3. Wait for data rendering (not just DOM load)
  4. Set viewport 1920x1080
  5. Screenshot to landing/screenshots/{NN}-{name}.png
  6. Verify screenshot is NOT a loading screen (check for "Caricamento" absence)
```

### Step 3: Quality Validation

After capture:
- Verify NO screenshot contains "Caricamento..." (loading state)
- Verify ALL screenshots show populated data (not empty states)
- Verify sidebar navigation is visible in all screenshots
- Verify screenshots are 1920x1080 (landing-ready)

## Output

```
landing/screenshots/
  01-dashboard.png          # Panoramica con statistiche del giorno
  02-calendario.png         # Calendario con appuntamenti
  03-clienti.png            # Lista clienti con ricerca
  04-servizi.png            # Catalogo servizi e prezzi
  05-operatori.png          # Team con specializzazioni
  06-fatture.png            # Fatture elettroniche
  07-cassa.png              # Punto cassa con incassi
  08-voice.png              # Sara assistente vocale
  09-fornitori.png          # Gestione fornitori
  10-analytics.png          # Grafici e statistiche
  11-impostazioni.png       # Configurazione
```

## Safety

- Runs ONLY on MacBook (Playwright + Vite dev server porta 1420)
- Does NOT touch iMac, does NOT need Rust build
- Does NOT modify app source code — mock is injected at test runtime
- All mock data is in test fixtures, NOT in production code

## Trigger

- User asks for "screenshot", "cattura schermate", "immagini landing"
- User invokes `/screenshot-capture`
- Part of landing page update workflow

## Dependencies

- `npx playwright` available (checked: v1.58.2)
- Vite dev server on port 1420 (auto-started by Playwright config)
- Firefox browser (configured in playwright.config.ts)
