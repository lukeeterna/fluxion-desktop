# REPORT SESSIONE S380 — 2026-06-21

## Obiettivo
Bottone download Windows → asset REALE → HTTP 200 sul percorso del CLIENTE PAGANTE.
Done a livello-download (NON install/attivazione = walkthrough founder).

## Decisione Punto 1 — PROMUOVI (regola secca)
- `tauri.conf.json` = **1.0.1** == versione asset draft **1.0.1** → la draft È la build corrente → PROMUOVI.
- (Cargo.toml = 1.0.0, ma il bundle Tauri segue tauri.conf.json e l'asset si chiama `Fluxion_1.0.1_x64-setup.exe`.)
- Asset reale verificato PRE-azione: `Fluxion_1.0.1_x64-setup.exe`, **423.999.525 byte (424 MB)**, state `uploaded` (non 0-byte).

## Mappa release (gh) — PRIMA
- `/releases/latest/` serve **v1.0.1** (non-draft) → **0 asset** → ogni bottone Win = 404.
- Unico `.exe` esisteva SOLO in draft `v0.0.0-dev`.

## Azioni eseguite

### A) Edit codice/repo (commit 29fe9c2) — nome canonico = nome REALE `Fluxion_1.0.1_x64-setup.exe`
- `landing/grazie/index.html:478` → ripuntato da `Fluxion_1.0.0_windows.msi` (404) al nome reale su `latest/download`.
- `landing/come-installare.html` (4×) → allineato `FLUXION-Setup.msi` → nome reale.
- `public/guida-fluxion.html` (2×) → allineato `FLUXION-Setup.exe` → nome reale.
- `fluxion-proxy/src/routes/checkout-success.ts:149` (il vero `success_url` Stripe, S295) → **AGGIUNTO** bottone "Scarica per Windows". Il percorso pagante aveva SOLO macOS.
- Email `buildEmailHtml` (post-S372): NON porta a download (solo recovery licenza + attivazione) → non toccata, by design giudice S372.

### B) Promozione asset (atto pubblico, approvato da Luke "procedi CTO")
```
gh release download v0.0.0-dev -p "Fluxion_1.0.1_x64-setup.exe" -D /tmp   → DOWNLOADED 423999525
gh release upload v1.0.1 /tmp/Fluxion_1.0.1_x64-setup.exe --clobber       → UPLOAD_DONE
```

## PROVA esterna (done a livello-download) — PASSATA
1. `gh release view v1.0.1` → `isDraft:false`, asset `Fluxion_1.0.1_x64-setup.exe` size 423999525 state `uploaded`. ✓
2. `curl -sIL …/releases/latest/download/Fluxion_1.0.1_x64-setup.exe` → **HTTP 200** (redirect a release-assets, `filename=Fluxion_1.0.1_x64-setup.exe`). ✓
3. Link cliente (grazie:478 + success-page:149) → stessa URL canonica → **stesso 200**. ✓

## URL finale
`https://github.com/lukeeterna/fluxion-desktop/releases/latest/download/Fluxion_1.0.1_x64-setup.exe` → **200**

Da dove lo raggiunge il cliente:
- success-page Stripe (`checkout-success.ts`, vero `success_url`) → bottone "Scarica per Windows".
- pagina grazie (`landing/grazie/index.html:478`) → bottone Windows.

## Propagazione deploy success-page — CHIUSO (2026-06-23, approvato Luke "procedi")
- **Worker `fluxion-proxy` DEPLOYATO**: `npx wrangler deploy` → `Deployed fluxion-proxy`, Version `ee99703a-37e3-49f8-819a-706d0f1990e5`. PRE-deploy: git tree pulito, bottone+link confermati a `checkout-success.ts:149`.
- **PROVA runtime esterna PASSATA** (session_id pagato reale da D1 `fluxion-webhook-events`: `cs_live_a1vYPgFHRrvfjS13I5KgusrysCK7vc0HH2qLGtjtOSW7Qq5MkIHH5wKN6K`, product base):
  - `https://fluxion-app.com/success/<SID>` → **200**, body serve `Scarica per Windows` + `releases/latest/download/Fluxion_1.0.1_x64-setup.exe`, rende `renderSuccessPage` (non pending). SÌ.
  - `fluxion-proxy.gianlucanewtech.workers.dev/success/<SID>` → idem. SÌ.
  - link → **200** riconfermato.
  - Done: **"success-page PROD (fluxion-app.com) serve bottone Windows: SÌ + link → 200"**.
- NB strutturale (`checkout-success.ts:244-264`): il bottone Win è in `renderSuccessPage`, servito SOLO con riga D1 per session_id pagato; session_id ignoto → `renderPendingPage` (solo macOS). La prova ha quindi usato una sessione pagata reale.
- Pages landing (grazie/come-installare/guida) → live al `git push` S380 (auto-deploy CF Pages).

## PARERE TECNICO CC (segnalazione, non fix in questo task)
La success-page **NON fa UA-sniff**: `renderSuccessPage` mostra ENTRAMBI i bottoni (macOS + Windows) a TUTTI i clienti, sempre. Giudizio: **accettabile per ora** — i label sono espliciti ("Scarica per macOS" / "Scarica per Windows"), pattern comune (GitHub releases, molti SaaS elencano tutte le piattaforme); confusione bassa. Il rischio REALE non è il doppio bottone ma che il bottone **macOS punta a un asset probabilmente 404** (vedi nota macOS sotto): un pagante macOS che clicca "Scarica per macOS" sbatte su 404. Quello è il prossimo da chiudere, non l'UA-sniff.

## NON toccato (da vincolo prompt)
licenza/fingerprint (Punto 1 chiuso S379), node-lock Q4/Q6, Q5/T2/T3, bottone macOS (separato), email buildEmailHtml.

## Nota macOS (segnalazione, fuori scope)
`grazie:467` punta a `Fluxion_1.0.0_macOS.pkg` e `DMG_DOWNLOAD_URL_MACOS` (wrangler.toml) a `v1.0.0/Fluxion_1.0.0_x64.dmg`: la v1.0.1 non ha asset macOS, il draft ha `Fluxion_1.0.1_aarch64.dmg` (no Intel, no .pkg). Probabile 404 anche su macOS — task futuro separato.
