# NEXT SESSION PROMPT — post S380 (2026-06-21)

## CHIUSO S380 (verde, done a livello-download)
Bottone download Windows del cliente pagante → asset REALE → **HTTP 200**.
- Asset `Fluxion_1.0.1_x64-setup.exe` (424 MB) **promosso** da draft `v0.0.0-dev` a **v1.0.1** (release servita da `/latest/`, isDraft:false).
- `curl …/releases/latest/download/Fluxion_1.0.1_x64-setup.exe` → **200** (verificato).
- Link cliente ripuntati al nome reale (commit 29fe9c2): `grazie:478`, `come-installare.html` (4×), `guida-fluxion.html` (2×), e **aggiunto** bottone Windows alla success-page Stripe `checkout-success.ts:149` (aveva solo macOS).
- Report: `.claude/REPORT_SESSIONE_2026-06-21_S380.md`.

## RESIDUO #1 (propagazione deploy — NON è il done, ma serve per "live")
- **Worker `fluxion-proxy` da deployare** perché l'edit success-page vada live:
  ```
  cd fluxion-proxy && git status   # verifica tree pulito
  npx wrangler deploy
  ```
  Poi smoke: aprire un success_url reale e verificare il bottone "Scarica per Windows".
- Pages landing (grazie/come-installare/guida): live al `git push` di S380 (auto-deploy CF Pages) — verificare su `fluxion-app.com`.

## RESIDUO #2 (fuori scope S380, segnalato)
- **Download macOS probabilmente 404**: `grazie:467` → `Fluxion_1.0.0_macOS.pkg`; `DMG_DOWNLOAD_URL_MACOS` → `v1.0.0/Fluxion_1.0.0_x64.dmg`. v1.0.1 non ha asset macOS; draft ha solo `Fluxion_1.0.1_aarch64.dmg` (no Intel/.pkg). Decidere build/promozione macOS in sessione dedicata.

## NON TOCCARE
licenza/fingerprint (chiuso S379), node-lock Q4/Q6, Q5/T2/T3, email buildEmailHtml (by design giudice S372).
