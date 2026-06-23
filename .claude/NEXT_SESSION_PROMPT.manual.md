# NEXT SESSION PROMPT — post S380 (aggiornato 2026-06-23)

## CHIUSO S380 (verde — NON riaprire)
**Download Windows del cliente pagante → asset reale → 200, live in PROD.**
- Asset `Fluxion_1.0.1_x64-setup.exe` (424 MB) promosso da draft `v0.0.0-dev` → **v1.0.1** (servita da `/latest/`). `curl …/releases/latest/download/Fluxion_1.0.1_x64-setup.exe` → **200**.
- Link cliente al nome reale: `grazie:478`, `come-installare.html`, `guida-fluxion.html` + bottone Windows aggiunto a `checkout-success.ts:149`.
- Worker `fluxion-proxy` **deployato** (Version `ee99703a`). Prova runtime: `https://fluxion-app.com/success/<session_id-pagato>` serve "Scarica per Windows" + link → 200. Evidenza verbatim in `.claude/REPORT_SESSIONE_2026-06-21_S380.md`.
- Commit: `29fe9c2` → `7be3aaf` → `a9130c0` (tutti pushati).

## PROSSIMO TASK REALE — download macOS 404 (stessa classe del bug S380, lato Mac)
Il bottone macOS del pagante punta a un asset che NON esiste:
- `landing/grazie/index.html:467` → `Fluxion_1.0.0_macOS.pkg`
- `fluxion-proxy/wrangler.toml:57,92` `DMG_DOWNLOAD_URL_MACOS` → `v1.0.0/Fluxion_1.0.0_x64.dmg`
- v1.0.1 (servita da /latest/) ha **0 asset macOS**; draft `v0.0.0-dev` ha solo `Fluxion_1.0.1_aarch64.dmg` (no Intel, no .pkg).
Done richiesto: bottone macOS della success-page + grazie → asset reale → **200**, sul percorso pagante.
Step probabili (validare, non assumere): decidere se promuovere `Fluxion_1.0.1_aarch64.dmg` a v1.0.1 e ripuntare i link/`DMG_DOWNLOAD_URL_MACOS` al nome reale; verificare copertura Intel (l'app supporta `minimumSystemVersion 10.15`/12+ — se serve x64 dmg, è BLOCKED-ON build su iMac).

## SEGNALAZIONE (no fix, già nel report)
Success-page mostra ENTRAMBI i bottoni a tutti (no UA-sniff): accettabile; il vero problema è il 404 macOS sopra.

## NON TOCCARE
licenza/fingerprint (chiuso S379), node-lock Q4/Q6, Q5/T2/T3, email buildEmailHtml (by design giudice S372), bottone/asset Windows (chiuso S380).

## Nota igiene
`.claude/SESSION_DIRTY.md`, se presente, è rumore dell'hook (trailing-whitespace nel dump auto-generato), NON un conflitto: il lavoro è committato e pushato.
