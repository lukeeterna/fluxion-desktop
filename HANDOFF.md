# FLUXION — Handoff Sessione 49 → 50 (2026-03-11)

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
Branch: master | HEAD: d4a3932
Working tree: CLEAN ✅
type-check: 0 errori ✅
ESLint pre-esistenti (non bloccanti): localStorage Dashboard.tsx, IntersectionObserver Impostazioni.tsx, useless-escape VoiceAgent.tsx
iMac: sincronizzato ✅ | voice pipeline: UP 127.0.0.1:3002 ✅
```

---

## ✅ COMPLETATO SESSIONE 49

| Task | Commit | Impatto |
|---|---|---|
| F05 LicenseManager UI verificata DONE | d4a3932 | Era già completa — TypeScript 0 err |
| CoVe 2026 research LicenseManager | d4a3932 | 5 gap UX vs Fresha/Linear identificati |

---

## 🎯 PRIORITÀ CTO — ORDINE ESECUZIONE S50

### ⚡ PRIORITÀ 1 — REVENUE FUNNEL COMPLETO (~2.5h)

**F07b + F05b: Wire checkout URLs + LicenseManager UX**

La MEMORY rivela che F07 backend è GIÀ COMPLETO:
- Account LS ✅ | Store ✅ | Webhook → DB → email ✅
- **Manca SOLO**: wiring checkout URLs in `src/types/license-ed25519.ts` (TierInfo) + UX potenziata

**Step 1 — Wire checkout URLs** (30min, MacBook, solo TypeScript):
```typescript
// src/types/license-ed25519.ts — aggiungere a LicenseTierInfo:
checkout_url?: string
// Valori da MEMORY (PERMANENTI — MAI richiedere):
// Base   €497:   https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-24c2-4214-a456-320c67056bd3
// Pro    €897:   https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702
// Clinic €1.497: https://fluxion.lemonsqueezy.com/checkout/buy/e3864cc0-937b-486d-b412-a1bebcfe0023
```

**Step 2 — LicenseManager UX Enhancement** (~2h):
- Progress bar trial countdown (verde→giallo→rosso <7gg)
- Active plan prominente SENZA tab (visibile subito, niente scroll)
- Feature comparison matrix (Base/Pro/Clinic side-by-side)
- Plain language hardware lock ("Bloccato su questo Mac")
- Upgrade CTA visibile → link a checkout LemonSqueezy
- Research: `.claude/cache/agents/f05-license-ui-cove2026.md`

**ROI**: +15-20% trial→Pro conversion + funnel acquisto completo → PRIMA VENDITA POSSIBILE

---

### PRIORITÀ 2 — F16 Landing Page Upgrade (3h)

- Screenshot app reali (sostituzione placeholder)
- Copy PMI-friendly: "Nessun canone mensile", "Funziona offline", "No per-user fees"
- Benchmark prezzi vs Fresha (€50/mese) — FLUXION vince su pricing
- CTA A/B test
- Landing attuale: https://fluxion-landing.pages.dev

---

### PRIORITÀ 3 — F08 Test Live Audio Sara T1-T5 (1h)

- Richiede: iMac + microfono reale
- Scenari T1-T5 da `.claude/rules/voice-agent-details.md`

---

### PRIORITÀ 4 — F15 VoIP Telnyx/EHIWEB (8-12h)

- Setup SIP trunk Telnyx + numero italiano EHIWEB
- Prerequisito: latenza < 800ms P95 ✅ (F03 DONE)
- HW Note: Intel iMac potrebbe limitare — valutare Mac Mini M2

---

## ⚠️ TODO PRODUZIONE APERTI (non bloccanti)

1. `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` reali in `src-tauri/src/commands/settings.rs`
2. Groq API key in keychain macOS (post-tauri-plugin-stronghold stable)

---

## AZIONI INIZIO S50

```bash
# 1. Leggi license-ed25519.ts per vedere TierInfo attuale
cat src/types/license-ed25519.ts | head -60

# 2. Wire checkout URLs (30min) → commit
# 3. LicenseManager UX Enhancement (2h) → commit
# 4. npm run type-check → 0 errori → push → sync iMac

# Checkout URLs (da MEMORY — PERMANENTI):
# Base   €497:   https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-24c2-4214-a456-320c67056bd3
# Pro    €897:   https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702
# Clinic €1.497: https://fluxion.lemonsqueezy.com/checkout/buy/e3864cc0-937b-486d-b412-a1bebcfe0023
```
