# FLUXION — Handoff Sessione 54 → 55 (2026-03-12)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: 162c395
fix(license-server): F07 order_refunded handler + DB migration
Working tree: clean
type-check: 0 errori ✅
iMac: ATTIVO 192.168.1.12 (verificare prima di sync)
```

---

## ✅ COMPLETATO SESSIONE 54 — F07 In-App Upgrade Path

### Commit atomici
| Commit | File | Descrizione |
|--------|------|-------------|
| `0e5fc06` | `LicenseManager.tsx` | openUrl + buildCheckoutUrl + UX world-class |
| `162c395` | `server.py` | order_refunded handler + DB migration |

### Acceptance criteria verificati
- [x] Piano attuale visibile + CTA "Upgrade" in LicenseManager.tsx (era già presente)
- [x] Click → `openUrl()` da `@tauri-apps/plugin-opener` (NON `window.open`)
- [x] `buildCheckoutUrl`: pre-fill `?dark=1 + checkout[email] + checkout[custom][fingerprint]`
- [x] "Più scelto" badge su piano Pro (pattern Linear/Jane App, +15-20% CR stimato)
- [x] Feature bullets per ogni tier (4 max, con CheckCircle2 icon)
- [x] Prezzo nella CTA: "Acquista — €897" (+20-30% CR vs CTA generica)
- [x] `order_refunded` webhook handler in server.py (gap security chiuso)
- [x] DB migration `refunded` column idempotente (try/except)
- [x] `npm run type-check` → 0 errori
- [x] Zero `any`, zero `@ts-ignore`
- [ ] `git push origin master` + iMac `git pull` → ancora da fare quando iMac raggiungibile
- [ ] Configurare evento `order_refunded` su dashboard LemonSqueezy (azione manuale)

### Architettura implementata
```
LicenseManager.tsx:
  - buildCheckoutUrl(baseUrl, {email, fingerprint}) → URL con params LS
  - UpgradeCTAs: props {currentTier, email, fingerprint}
  - handleUpgrade: void openUrl(buildCheckoutUrl(...)) — pattern tauri corretto
  - UI: card con badge "Più scelto", feature bullets, prezzo in CTA

server.py:
  - handle_webhook_ls: gestisce 'order_refunded' → UPDATE orders SET refunded=1
  - init_db: ALTER TABLE orders ADD COLUMN refunded (idempotente)
  - handle_activate: check refunded → 402 prima di check used
```

### CoVe 2026 Research Files
- `.claude/cache/agents/f07-upgrade-ux-cove2026.md` (Agente A — UX patterns)
- `.claude/cache/agents/f07-lemonsqueezy-api-cove2026.md` (Agente B — LS API)

### Pre-existing ESLint issues (NON correlate a F07, da trackare separatamente)
- `localStorage` non definito in Dashboard.tsx (righe 71, 97)
- `IntersectionObserver` non definito in Impostazioni.tsx (righe 179, 185)
- Unnecessary escape in VoiceAgent.tsx (riga 209)

---

## 🎯 PRIORITÀ S55 — PROSSIMA FASE

Leggi `ROADMAP_REMAINING.md` per determinare la fase successiva.
Secondo ROADMAP, le opzioni rimanenti sono:
- **F08** — Test Live Audio Sara T1-T5 (richiede iMac + microfono)
- **F15** — VoIP Integration (prerequisito: F03 done ✅)
- **Pre-existing ESLint errors** — fix rapido (Dashboard + Impostazioni + VoiceAgent)

---

## TODO iMac (quando raggiungibile)
1. `git push origin master` dal MacBook
2. `git pull origin master` su iMac (`/Volumes/MacSSD - Dati/FLUXION`)
3. Riavvio license delivery server se attivo
4. Configurare evento `order_refunded` su dashboard LemonSqueezy
5. Test live T1-T5 con audio reale (F-TEMPORAL: "dopo le 17" → "dopo le 17:00")
6. Catturare `fx_voice_agent.png` per landing

---

## Checkout URLs LemonSqueezy (PERMANENTI — MAI richiedere)
- Base €497: `https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-24c2-4214-a456-320c67056bd3`
- Pro €897: `https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702`
- Clinic €1.497: `https://fluxion.lemonsqueezy.com/checkout/buy/e3864cc0-937b-486d-b412-a1bebcfe0023`
