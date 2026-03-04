# FLUXION — Roadmap Rimanente per v1.0 Launch
> Aggiornato: 2026-03-04 | CTO review sessione 16
> **Strategia**: Prima vendita > Feature completeness

---

## 🔴 BLOCKERS PRIMA VENDITA

| Fase | Feature | Effort | Status |
|------|---------|--------|--------|
| **F01** | Click-to-sign contratto nel SetupWizard | 2h | 🔄 IN PROGRESS |
| **F02** | Vertical system Sara (guardrails + entity extractor) | 3h | ⏳ |

---

## 🟡 PRODUCT QUALITY (dopo prima vendita)

| Fase | Feature | Effort | Status |
|------|---------|--------|--------|
| **F03** | Latency optimizer Sara P95 <800ms | 4-6h | ⏳ |
| **F04** | Schede mancanti: Parrucchiere, Fitness, Medica | 4h | ⏳ |
| **F05** | LicenseManager integrato in tab Impostazioni | 1h | ⏳ |
| **F06** | Clinic tier €1.497 (add to license system) | 2h | ⏳ |

---

## 🟢 BUSINESS (dopo video Vimeo + P.IVA)

| Fase | Feature | Effort | Status |
|------|---------|--------|--------|
| **F07** | LemonSqueezy payment integration | 2h | ⏳ |
| **F08** | Test live audio Sara T1-T5 (iMac) | 1h | ⏳ |
| **F09** | Multi-sede (SKIP — senza P.IVA) | — | 🚫 |

---

## ✅ COMPLETATO (v1.0 base)

| Feature | Commit |
|---------|--------|
| CRM + Calendario + Servizi + Operatori | — |
| Fatturazione SDI + XML FatturaPA multi-provider | c1ece40 |
| Voice Agent Sara 1160 test PASS | 679e3c4 |
| WhatsApp webhook B2 | 47ba161 |
| License system Ed25519 offline | — |
| Feature gate Voice Agent (Base tier) | 391ddbf |
| Pricing corretto €497/€897/€1.497 | 391ddbf |
| B4 Exception handling narrowed | 499f9da |
| P1 Voice prod fixes (5 fix) | 2b72aaf |
| Landing page live | — |

---

## 📐 Architettura Pricing Definitiva

| Tier | Nome | Prezzo | Features chiave |
|------|------|--------|----------------|
| Trial | Trial 30gg | €0 | Tutto incluso |
| Base | FLUXION Base | €497 | 1 verticale, no Voice |
| Pro | FLUXION Pro | €897 | 3 verticali + Voice + WhatsApp AI |
| Clinic | FLUXION Clinic | €1.497 | Verticali illimitate + API + onboarding |

---

## 🛠️ Workflow CTO — Claude Code 2026

```
Ogni sessione:
1. Leggi HANDOFF.md + ROADMAP_REMAINING.md
2. Prendi la prima fase NON completata
3. CoVe 2026: Research → Plan → Implement → Verify → Deploy
4. Aggiorna status in questo file
5. Aggiorna HANDOFF.md + MEMORY.md

Subagenti in parallelo dove possibile:
- Research in background mentre leggi file
- Type-check sempre prima del commit
```

---

## ⚖️ Note Legali

- **Venditore**: Privato senza P.IVA → Prestazione Occasionale max €5.000/anno
- **Documento vendita**: Ricevuta P.O. con ritenuta d'acconto 20%
- **Contratto**: Concessione Licenza Software (FES click-to-sign in-app)
- **GDPR**: Dati locali, no cloud, conservazione 10 anni in localStorage + export PDF
- **P.IVA**: Aprire regime forfettario prima dei €5.000 (tassa effettiva ~12%)
- **Multi-sede**: Rimandato a dopo apertura P.IVA
