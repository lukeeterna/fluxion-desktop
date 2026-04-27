# S170 — Synthesis & Decision Matrix
**Data**: 2026-04-27 · **Owner**: Gianluca Di Stasi · **Stato**: Pronto per approvazione

## 1. Convergenze tra i 3 report

| Tema | Trend (01) | UX (02) | Storyboard (03) |
|------|-----------|---------|-----------------|
| Length ottimale 60-90s cold funnel | Wistia 52% engagement <1min | Mobile drop sopra 60s | 4 verticali oltre 75s = REPLACE |
| CTA fuori dal video, sticky landing | W4 pattern winning | P2 problem critico | (n/a — focus video) |
| Numeri/credibilità PRIMA del play | R3 raccomandazione | Quick win #2 copy sopra iframe | Hook alternativi con numeri 0-3s |
| Link verticale ≠ link generico | R5 raccomandazione | Quick win #5 link separato per WA preview | Coerenza hook→video per verticale |
| Trust signals zero in landing attuale | W3 testimonial = +46% | P3 garanzia sepolta | (n/a) |

**Conclusione**: tutti e 3 gli agenti convergono su 3 leve: **video più corti dove bloated**, **landing copy che precede il play**, **WA che mande link verticale + preview card**.

## 2. Decision Matrix per i 10 video YouTube

| Video | YT ID | Verdetto | Effort | Priorità | Motivo |
|-------|-------|----------|--------|----------|--------|
| Landing master | `22IQmealPrw` | KEEP | 0h | — | 2:29 ok per landing main |
| Parrucchiere | `FlNHHvxxfOE` | **REPLACE VO** | 1h | P1 | VO 40s → target 25s; hook "colore nel lavandino" mancante |
| Nail artist | `rau4yuR9NS4` | **REPLACE VO** | 1h | P1 | Concept forte sprecato da VO 42s |
| Dentista | `1sa4MN8bmGU` | **REPLACE VO** | 1h | P1 | VO 45s; confronto XDENT non emerge |
| Centro estetico | `hWs8wI6t3xU` | **REPLACE VO** | 1h | P1 | VO 47s; dato €22.500/anno non sfruttato |
| Officina | `pG9VKWSbYd4` | REWORK | 30min | P2 | Spostare "€13k/mese" nel hook 0-3s |
| Barbiere | `Dd9DgAzfUtk` | REWORK lieve | 20min | P3 | Già il migliore — togliere 1 screenshot |
| Palestra | `GzSbYJBCXAk` | REWORK lieve | 20min | P3 | Chiarire pain: retention vs certificato |
| Carrozzeria | `1HXQBBUmgp0` | KEEP | 0h | — | Struttura corretta |
| Fisioterapista | `y8YMK7GWKLU` | KEEP | 0h | — | VO perfetto, uso VAS credibile |

**Totale effort video**: ~5h30 (Edge-TTS + FFmpeg riassemblaggio, costo €0). **NO Veo 3 nuove clip** — solo VO replacement + remix.

## 3. Quick wins landing (<2h totali, file/righe in 02-funnel-ux-audit.md)

1. **`landing/index.html` ~r9** — meta `og:image` + `og:description` (link WA preview card)
2. **`landing/index.html` ~r261** — copy headline+teaser sopra iframe YT (play rate +18-24%)
3. **`landing/index.html` pre-r1749** — banner garanzia 30gg visibile (completion +15-25%)
4. **`tools/SalesAgentWA/templates.py`** — firme standard 2 varianti senza brand redundancy
5. **`tools/SalesAgentWA/templates.py` r225** — link su riga propria → attiva preview card WA

## 4. Quick wins WA agent

- **Sales agent invia link verticale**, non landing master (UTM `utm_content=parrucchiere` etc.)
  - Mapping da implementare: `category → YT video ID` o `category → /v/<vertical>` route landing
- Coerenza hook WA ↔ hook video (entrambi attaccano lo stesso pain primario)

## 5. Cosa NON fare (anti-pattern convergenti)

- ❌ Allungare video oltre 90s "per spiegare meglio"
- ❌ Autoplay con audio (privacy + UX)
- ❌ Countdown/scarcity falsi (rompe trust PMI italiane)
- ❌ Pop-up email gate prima del video
- ❌ Emoji nei template WA (Luca Ferretti rule già attiva)
- ❌ Mention "prova gratuita" — non esiste, compromette il modello
- ❌ Girare con attori reali — fuori scope, costo > €0

## 6. Conversion uplift atteso (stima)

| Step funnel | Baseline | Post-fix | Lift |
|-------------|---------|----------|------|
| WA click → landing | 4% reply, ~15% click stimato | Preview card + link verticale → ~25% | +60% |
| Landing → video play | ~30% (no copy sopra iframe) | +headline+teaser → ~50% | +66% |
| Video play → completion | ~38% (video 75s) | →62% (video 50-60s) | +63% |
| Completion → Stripe click | ~5% (no garanzia visibile) | +banner 30gg → ~10% | +100% |
| End-to-end stimato | **0.2-0.3%** | **0.6-1.2%** | **3-4x** |

Fonte: aggregazione benchmark Wistia 2025 + Wyzowl 2026 + First Page Sage Feb 2026 + Baymard Institute. Confidence: media (benchmark internazionali, gap dati Italia/PMI).

## 7. Roadmap operativa proposta (S170 → S171)

### Fase A — Quick wins landing + WA (1 sessione, <3h)
1. 5 edit `landing/index.html` + `templates.py`
2. Mapping `category → YT video ID` in sales agent
3. Deploy CF Pages production
4. Verifica WA preview card su numero test (3807769822)

### Fase B — Video REPLACE VO (4 verticali P1, 1 sessione ~5h)
1. Riscrivere copioni 25-27s per parrucchiere/nail/dentista/centro_estetico
2. Edge-TTS `it-IT-IsabellaNeural --rate -8% --pitch -5Hz`
3. `python3 assemble_all.py [verticale]` ognuno
4. Re-upload YouTube via `youtube_batch_upload.py --only X --replace`
5. Verifica ffprobe target 50-60s

### Fase C — Video REWORK (3 verticali P2-P3, 1 sessione ~70min)
1. Officina: ricolloca "€13k/mese" → hook 0-3s
2. Barbiere: rimuove 1 screenshot ridondante
3. Palestra: chiarisce pain primario nel VO
4. Re-upload YouTube

### Fase D — Promote → public (manuale fondatore)
- Review YT Studio i video aggiornati
- `--privacy public --only X,Y,Z` per quelli approvati

## 8. Open questions per il fondatore

1. **OK procedere con REPLACE VO sui 4 P1?** (zero costo, ~5h effort)
2. **OK ai 5 quick wins landing** (og tags, copy iframe, banner garanzia)?
3. **OK al mapping verticale → YT ID nel sales agent**? Richiede modifica `templates.py` per CTA per-verticale
4. **Garanzia 30gg "soddisfatti o rimborsati"**: confermi che esiste come policy commerciale? (banner inutile se non onorabile)
5. **Testimonial scritti** in landing — abbiamo case reali da citare (anche solo nome attività + città + 1 metrica)?

## 9. File di riferimento

- `01-competitor-benchmark.md` — 7 competitor, 17 benchmark numerici, 7 raccomandazioni
- `02-funnel-ux-audit.md` — 10 problemi prioritizzati, HTML esatto per 5 quick wins, mobile checklist 7 voci
- `03-storyboard-per-vertical.md` — 9 storyboard frame-by-frame, copioni compressi 25s, hook alternativi 3x9, standard template 2026
