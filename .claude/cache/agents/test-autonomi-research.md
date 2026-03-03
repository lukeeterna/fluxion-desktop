# Test Autonomi Tauri/React — CoVe 2026 FASE 1 Research
> Generato: 2026-03-03 | Agente: general-purpose | Research test autonomi Tauri 2.x

---

## Stato Attuale FLUXION

FLUXION ha già **due setup E2E parziali**, entrambi non funzionanti:

**`e2e/` — WebdriverIO + tauri-driver**
Il file `wdio.conf.ts` contiene già un `console.warn` esplicito:
`"tauri-driver does NOT support macOS. E2E tests will fail."`.
I test esistenti (`booking.spec.ts`, `crm.spec.ts`, ecc.) usano `browser.$()` (WebdriverIO API) e non possono girare su macOS.

**`e2e-tests/` — Playwright**
80% pronto. Mancano le fixture (`test.fixtures.ts`, `global.setup.ts`, `global.teardown.ts`) e la `BasePage`. Il config punta a `npm run tauri dev` invece che solo `npm run dev` (Vite).

---

## Problema Fondamentale — macOS WKWebView

Apple non fornisce un WebDriver per WKWebView. Questo blocca qualsiasi approccio WebDriver su macOS (MacBook arm64 e iMac x64). Il `tauri-driver` ufficiale supporta **solo Linux e Windows**.

---

## Opzioni Analizzate

| Tool | macOS arm64 | Testa app reale | Stato | Verdict |
|------|-------------|-----------------|-------|---------|
| tauri-driver (ufficiale) | ❌ NO | Sì | Stabile | ESCLUSO su macOS |
| Playwright + mockIPC | ✅ SÌ | No (solo UI/React) | Stabile | **RACCOMANDATO immediato** |
| tauri-webdriver-automation | ✅ SÌ | Sì | Early-stage (Feb 2026) | Per iMac release testing, futuro |
| CrabNebula Cloud | ✅ SÌ | Sì | SaaS commerciale | ESCLUSO (costo) |

---

## Raccomandazione: Playwright frontend-only (priorità immediata)

**Perché**: Funziona su MacBook arm64 senza build Rust, il codice è già all'80% in `e2e-tests/`, i 5 smoke test operativi in ~2h.

### Step necessari per attivare `e2e-tests/`

1. Creare `e2e-tests/fixtures/global.setup.ts` e `global.teardown.ts` (stub)
2. Creare `e2e-tests/pages/BasePage.ts` (Page Object pattern)
3. Creare `e2e-tests/pages/DashboardPage.ts`
4. Creare `e2e-tests/fixtures/test.fixtures.ts` (estende `base` con `dashboardPage` + `clientiPage`)
5. Modificare `e2e-tests/playwright.config.ts`: `webServer.command` da `npm run tauri dev` → `npm run dev`
6. Semplificare `projects`: solo `chromium`, rimuovere firefox/webkit/edge/tauri-webview
7. Eseguire `cd e2e-tests && npm install && npx playwright install chromium`

---

## 5 Smoke Test Acceptance Criteria

| ID | Test | File | Pass Criteria |
|----|------|------|---------------|
| ST-1 | App Load | `smoke.spec.ts` | 0 errori JS console, sidebar visibile entro 5s |
| ST-2 | Navigazione 5 route | `smoke.spec.ts` | Dashboard, Clienti, Calendario, Fatture, Impostazioni raggiungibili |
| ST-3 | Form nuovo cliente | `clienti.spec.ts` | Modal apre, validation errori visibili, Escape chiude |
| ST-4 | Calendario carica | `calendario.spec.ts` | Vista calendario visibile entro 10s, no crash |
| ST-5 | Impostazioni tab | `impostazioni.spec.ts` | 3+ tab navigabili, contenuto cambia |

---

## Compatibilità Piattaforme

- **MacBook M-series (arm64)**: Playwright Chromium OK nativo, Vite dev server OK, tauri-driver NO
- **iMac Intel (x64)**: Playwright OK, `tauri-webdriver-automation` OK (per release testing futuro)

---

## Roadmap

**Sprint corrente (v1.0)**: Fixare Playwright `e2e-tests/` — ~2h implementazione, 5 smoke test funzionanti su MacBook

**Post v1.0**: WebdriverIO + `tauri-webdriver-automation` su iMac — aggiungere `tauri-plugin-webdriver-automation` al Cargo.toml, aggiornare `wdio.conf.ts`, test integrazione SQLite reale

---

## Fonti

- [WebDriver Tauri 2 (ufficiale)](https://v2.tauri.app/develop/tests/webdriver/)
- [WebdriverIO + Tauri 2](https://v2.tauri.app/develop/tests/webdriver/example/webdriverio/)
- [Mocking API Tauri 2](https://v2.tauri.app/develop/tests/mocking/)
- [Issue macOS WKWebView #7068](https://github.com/tauri-apps/tauri/issues/7068)
- [tauri-webdriver-automation (Feb 2026)](https://crates.io/crates/tauri-webdriver-automation)
- [CrabNebula Tauri E2E](https://docs.crabnebula.dev/plugins/tauri-e2e-tests/)
- [WKWebView WebDriver community solution (Feb 2026)](https://danielraffel.me/2026/02/14/i-built-a-webdriver-for-wkwebview-tauri-apps-on-macos/)

---

*Fonte: general-purpose agent — Web search + codebase analysis FLUXION e2e/ e2e-tests/ directories*
