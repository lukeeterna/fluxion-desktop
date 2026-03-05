# FLUXION — Handoff Sessione 26 (2026-03-05) — Kaggle Mockup Generator

## STATO CORRENTE

**F05 LicenseManager UI** ✅ DONE — committato `74dfe7c`
**F04 Schede Mancanti** ✅ DONE (già in codebase, verificato sessione 25)
**Kaggle Mockup Generator** 🔄 IN PROGRESS — v4 pushato, in attesa run

---

## Kaggle Notebook — Stato

| Versione | Stato | Note |
|----------|-------|------|
| v1-v2 | ❌ | cloudflared FileNotFoundError |
| v3 | ❌ | diffusers==0.31.0 incompatibile con transformers su P100/Python3.12 |
| v4 | ⏳ running | diffusers>=0.33.0, transformers<4.48.0 |

**Kernel URL**: https://www.kaggle.com/code/fluxiongestionale/fluxion-ai-generator
**Output atteso**: 7 PNG mockup in /kaggle/working/

### Comando per scaricare output quando completato:
```bash
export KAGGLE_API_TOKEN=KGAT_46561d6a21824bef3b867a0d30986a38
kaggle kernels status fluxiongestionale/fluxion-ai-generator
kaggle kernels output fluxiongestionale/fluxion-ai-generator -p /tmp/kaggle-output
```

### Immagini che verranno generate:
1. `01-scheda-parrucchiere.png` — client card salone
2. `02-scheda-fitness.png` — profilo fitness con BMI gauge
3. `03-scheda-medica.png` — cartella medica + GDPR
4. `04-scheda-estetica.png` — scheda estetica + loyalty
5. `05-scheda-veicoli.png` — gestione veicoli officina
6. `06-dashboard-principale.png` — dashboard KPI
7. `07-calendario-prenotazioni.png` — calendario settimanale

### Dopo il download:
- Aprire le PNG come riferimento design
- Redesign React dei componenti scheda usando il visual language generato
- Tutti i componenti in `src/components/schede/`

---

## Prossimi Task (ROADMAP_REMAINING.md)

| Fase | Task | Status |
|------|------|--------|
| **Kaggle** | Mockup UI FLUX.1-schnell | 🔄 in corso |
| **F10** | CI/CD GitHub Actions | ⏳ |
| **F07** | LemonSqueezy payment | ⏳ |

---

## Stato Git
```
Branch: master | HEAD: 74dfe7c
type-check: ✅ 0 errori
Voice tests: ✅ 1263 PASS / 0 FAIL
Kaggle token: KGAT_46561d6a21824bef3b867a0d30986a38 (⚠️ rigenerare dopo uso)
```
