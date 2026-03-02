# D1 Landing Screenshots — CoVe 2026 Research
> Generato: 2026-03-02 | Aggiornato: 2026-03-02 (rebuild + WebSearch 2026) | VERIFIED

## Screenshot Attivi (7 file in `landing/assets/screenshots/`)

| File | Sezione | Ruolo | Size |
|------|---------|-------|------|
| `fx_calendario.png` | `#gestionale` HERO mac-frame | Screenshot principale full-width | 115 KB |
| `fx_fatture.png` | Grid 4 card, slot 1 | Fatture e FatturaPA | 154 KB |
| `fx_operatori.png` | Grid 4 card, slot 2 | Gestione operatori | 126 KB |
| `fx_scheda_cliente.png` | Grid 4 card, slot 3 | Scheda cliente | 69 KB |
| `fx_cassa.png` | Grid 4 card, slot 4 | Cassa giornaliera | 111 KB |
| `fx_dashboard.png` | Secondary row, sinistra | Dashboard KPI | 142 KB |
| `fx_servizi.png` | Secondary row, destra | Lista servizi | 167 KB |

## Screenshot Obsoleti (NON referenziati — da rimuovere)
`fx_fattura_detail.png`, `fx_fedelta.png`, `fluxion_01_main.png`, `fluxion_01_launch.png`,
`fluxion_02_focused.png`, `fluxion_03_activated.png`, `fluxion_04_window.png`

---

## DA AGGIORNARE per v0.9.2

| File | Motivo | Priorità |
|------|--------|---------|
| `fx_operatori.png` | Pre B2/B3/B4 — mancano tab KPI/Servizi/Orari/Assenze | 🔴 CRITICO |
| `fx_fatture.png` | Pre C1 — manca badge "Inviata SDI" + bottone "Invia SDI" | 🔴 CRITICO |

## NUOVI da catturare

| File | Contenuto | Priorità |
|------|-----------|---------|
| `fx_operatori_kpi.png` | Tab Statistiche con barchart 6 mesi | 🟡 ALTA |
| `fx_voice_agent.png` | Pagina Sara — voice agent in ascolto | 🔴 CRITICO (gap: Sara assente nella landing) |

---

## TOP 5 Priority Shots (per conversion)

1. **`fx_calendario.png`** — HERO full-width; mostrare 3+ operatori, 15+ appuntamenti reali
2. **`fx_operatori.png`** refresh → tab Statistiche KPI (differenziatore enterprise)
3. **`fx_fatture.png`** refresh → badge SDI verde visibile (prova integrazione italiana)
4. **`fx_voice_agent.png`** NUOVO → Sara è selling point #1, 0 screenshot attuali
5. **`fx_dashboard.png`** verifica → KPI plausibili (ricavo ~€2.400, 31 clienti)

---

## Specifiche Tecniche

- **Formato**: PNG obbligatorio, macOS dark mode
- **Hero** (`fx_calendario.png`): 1440×900 px, target ≤300 KB
- **Card** (tutto il resto): max 900px width, target ≤200 KB
- **Ottimizzazione**:
  ```bash
  sips -Z 1440 fx_calendario.png   # resize hero
  pngquant --quality=70-85 *.png   # compress tutti
  ```

---

## Workflow Cattura (su iMac)

```bash
# 1. Apri Fluxion.app dalla build v0.9.2
open '/Volumes/MacSSD - Dati/FLUXION/src-tauri/target/release/bundle/macos/Fluxion.app'

# 2. Cattura: Cmd+Shift+4 → trascina sulla finestra
# 3. Screenshot salvati in ~/Desktop

# 4. Ottimizza
cd ~/Desktop
sips -Z 1440 fx_calendario.png
pngquant --quality=70-85 --ext .png --force fx_*.png

# 5. Trasferisci a MacBook
scp ~/Desktop/fx_*.png macbook:/Volumes/MontereyT7/FLUXION/landing/assets/screenshots/
```

---

## Workflow D2 — Cloudflare Pages Redeploy

```bash
# Su MacBook dopo aggiornamento screenshots
cd /Volumes/MontereyT7/FLUXION
zip -r /tmp/fluxion-landing-$(date +%Y%m%d).zip landing/ -x "*/.DS_Store"
# Upload ZIP: dash.cloudflare.com → Workers & Pages → fluxion-landing → Upload assets
```

---

## Note Sezione HTML

La sezione `#gestionale` usa:
- `mac-frame` div con `<img src="assets/screenshots/fx_calendario.png">`
- Grid 4 card con `screenshots/fx_fatture.png`, `fx_operatori.png`, `fx_scheda_cliente.png`, `fx_cassa.png`
- Secondary row: `fx_dashboard.png` (sinistra) + `fx_servizi.png` (destra)
- **Sara non ha sezione screenshot** → aggiungere sezione voice dopo D1 (vedi sotto)

---

## Priority 2026 — TOP 8 Shots (Expanded, WebSearch 2026)

| Rank | File | Perché converte (2026 research) |
|------|------|--------------------------------|
| 1 | `fx_calendario.png` | HERO — first visual impression, real UI > mockup |
| 2 | `fx_voice_agent.png` | **Sara = primary selling point — ZERO screenshots oggi** |
| 3 | `fx_fatture.png` | SDI badge = Italian compliance proof |
| 4 | `fx_operatori.png` | KPI tab = enterprise differentiator |
| 5 | `fx_dashboard.png` | Social proof con numeri reali |
| 6 | `fx_scheda_cliente.png` | CRM integrato, non solo rubrica |
| 7 | `fx_cassa.png` | Sostituisce registro cartaceo |
| 8 | `fx_servizi.png` | Setup immediato visibile |

**Best practice 2026**: Real screenshots +23% trust vs mockups. B2B SaaS hero con value prop chiaro = +35-40% conversione.

---

## Setup Dati Pre-Cattura (iMac)

Prima di ogni screenshot, l'app deve mostrare **dati realistici**:
```
Operatori: 3+ (es. Giulia, Marco, Stefania)
Clienti: 15+ (nomi italiani, 2-3 VIP badge)
Appuntamenti: calendario pieno (6-8 slot visibili nella settimana)
Fatture: mix stati (bozza, inviata, SDI verde "Accettata", SDI giallo "In elaborazione")
Sara: sessione in corso con testo conversazione visibile
```

---

## Edge Cases

| Edge Case | Soluzione |
|-----------|-----------|
| Display Retina 2x (iMac) | `sips -Z 1440` dopo cattura (2880→1440px) |
| Dark Mode | Cattura in **Light Mode** (macOS Preferenze → Aspetto) per leggibilità |
| Sara UI non visibile nell'app | Screenshot schermata terminale con curl test styled o sezione HTML placeholder fino a UI |
| Dati placeholder vuoti | Inserisci dati reali pre-cattura (vedi Setup Dati) |
| File > 250KB | Riapplica `pngquant --quality=60-75` |

---

## Sezione Sara — HTML da Aggiungere (D1 consegnato)

Inserisci in `landing/index.html` tra `#come-funziona` e `#gestionale`:

```html
<section id="sara-voice" class="py-20 bg-gradient-to-br from-slate-900 to-slate-800">
  <div class="container mx-auto px-6">
    <div class="text-center mb-12">
      <span class="inline-block px-4 py-1 bg-teal-500/20 text-teal-400 rounded-full text-sm font-medium mb-4">
        Intelligenza Artificiale
      </span>
      <h2 class="text-4xl font-bold text-white mb-4">Sara risponde per te, 24/7</h2>
      <p class="text-slate-400 text-xl max-w-2xl mx-auto">
        L'assistente vocale AI che prenota, gestisce la lista d'attesa e manda conferme WhatsApp.
      </p>
    </div>
    <div class="max-w-3xl mx-auto rounded-2xl overflow-hidden shadow-2xl border border-slate-700">
      <img src="assets/screenshots/fx_voice_agent.png"
           alt="Sara — Voice Agent FLUXION"
           class="w-full" loading="lazy" decoding="async" width="1440" height="900">
    </div>
  </div>
</section>
```

---

## Formato Immagini 2026

**D1 (questa sessione)**: PNG + pngquant → ottimale per Cloudflare Pages (no Polish gratuito)
**D2+ (futuro)**: `<picture>` con WebP fallback → -26% size; AVIF encoding lento macOS → v1.1

---

*Research sources: SaaS Landing Page Trends 2026 (SaaSFrame), AVIF vs WebP 2026 (Elementor), B2B SaaS Conversion Benchmarks 2026 (SaasHero), Screenhance screenshots guide 2026*
