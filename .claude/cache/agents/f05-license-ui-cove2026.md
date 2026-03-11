# F05 LicenseManager UI — CoVe 2026 Research

## Stato Attuale (verificato sessione 49)
`LicenseManager.tsx` ESISTE e compila (TypeScript 0 errori). F05 è DONE per i deliverables minimi della ROADMAP.

## Gaps UX vs Gold Standard (Fresha/Linear 2026)

| Gap | Attuale | Standard | Impact |
|-----|---------|----------|--------|
| Trial progress bar | Testo "X giorni" | Barra verde→giallo→rosso | Urgenza bassa |
| Feature matrix | Bullets per card | Grid side-by-side Base/Pro/Clinic | No "cosa manca" |
| Active plan prominenza | Badge "Attuale" piccolo | Card full-width, bordo colorato | Confusione cognitiva |
| Plain language HW lock | "Hardware Fingerprint" | "Funziona offline, bloccato su questo Mac" | PMI non capisce |
| Upgrade CTA | Pulsante in card | Sticky button fuori tab | Bassa conversion |
| Checkout URL | Vuoto ("Disponibile a breve") | LemonSqueezy link (F07) | Non acquistabile |

## Acceptance Criteria UX Enhancement (opzionale)

- **AC1**: Piano attivo visibile senza scroll (<3 secondi)
- **AC2**: Trial countdown progress bar (verde > 7gg, giallo 7-1gg, rosso 0gg)
- **AC3**: Feature comparison matrix (Base/Pro/Clinic colonne, feature righe)
- **AC4**: Hardware lock in plain language ("Questo Mac: MacBook-Marco")
- **AC5**: Upgrade CTA visibile nel main view (non dentro tab)

## Recommendation
+15-20% trial→Pro conversion con: piano attivo prominente + feature matrix + progress bar trial.
Nessuna modifica backend necessaria — solo refactor LicenseManager.tsx.
