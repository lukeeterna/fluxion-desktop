# Prompt ripartenza — S381 → prossima sessione

**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Report sessione**: `.claude/REPORT_SESSIONE_2026-06-23_S381.md` (aperto in TextEdit)

## S381 CHIUSO VERDE — mail conferma: aggiunto download
- **Fatto**: `buildEmailHtml` (`fluxion-proxy/src/routes/stripe-webhook.ts`) ora ha **STEP 1 "Scarica"**
  con macOS `${dmgUrl}` (200) + Windows `${winUrl}` canonico (200); "Attiva" → STEP 2. Q5 intatto.
- **Commit**: `4fe9bda`. **Deploy**: worker `fluxion-proxy` Version `f08f29b9-c2e6-4a69-8020-5dd5dc7b095d`.
- **Prova**: render fedele funzione esportata (blob passato negli args → 0 nel corpo) + link → 200 + recovery non-regredito. Zero divergenza render/send (1 def, 1 call-site).

## PROSSIMO TASK REALE — landing `grazie:467` macOS 404 (NON percorso pagante)
- **Fatto verificato S381**: `landing/grazie/index.html:467` → `Fluxion_1.0.0_macOS.pkg` = **404**.
  È la landing pubblica (NON la mail pagante, già chiusa). Stessa classe S380 lato landing.
- **Ipotesi fix**: ripuntare al dmg già 200 (`v1.0.0/Fluxion_1.0.0_x64.dmg`) — coerente con la mail
  e la success-page — OPPURE promuovere un `.pkg`/dmg reale. Decisione = un solo asset canonico macOS.
- **Done richiesto**: bottone macOS della landing `grazie` → asset reale → 200.

## NON TOCCARE
licenza/fingerprint (Punto 1 chiuso S379), node-lock Q4/Q6, Q5 blob (intatto), T2/T3,
success-page (live S380), mail conferma (live S381).

## Nota igiene
`.claude/SESSION_DIRTY.md` se rigenerato dall'auto-close hook = rumore (trailing-whitespace su
prompt auto-generato), NON conflitto reale. Verifica `git log`/commit prima di trattarlo come blocco.
