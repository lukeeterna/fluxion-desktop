---
name: sales_agent_blueprint
description: Blueprint implementativo completo Sales Agent WA — path file, status, dipendenze chiave, roadmap
type: project
---

Blueprint completo creato il 2026-04-14. Pronto per implementazione, nessuna dipendenza a pagamento.

**Path blueprint:** `tools/SalesAgentWA/SALES-AGENT-BLUEPRINT.md`
**Path iMac:** `/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA/`

**Moduli implementati nel blueprint:**
- `config.py` — costanti, warm-up schedule, orari business
- `utm.py` — UTM builder + normalizzazione numeri italiani
- `templates.py` — 6 categorie × 3+ varianti, render con variazione Jaccard
- `scraper.py` — Google Places API + PagineBianche + OSM Overpass
- `sender.py` — Playwright WA Web, session persist, anti-ban delay gaussiano
- `dashboard.py` — Flask SPA con funnel AARRR, auto-refresh 30s
- `agent.py` — CLI argparse: init|scrape|send|dashboard|stats|pause|resume|next-week
- `com.fluxion.salesagent.plist` — LaunchAgent iMac, esecuzione 9:30 lun-ven

**Dipendenze Python (pip install):**
requests==2.31.0, beautifulsoup4==4.12.3, lxml==5.1.0, playwright==1.44.0, flask==3.0.3, schedule==1.2.1

**Warm-up schedule implementato:**
Sett 1-2: 5/g | Sett 3-4: 10/g | Sett 5: 20/g | Sett 6+: 25/g

**Funnel tracciato:** Scraped → Contattati → Delivered → Read → Replied → (Acquisto su Stripe)

**Conversione attesa cold outreach:** ~1% end-to-end (WA → YouTube → Landing → Stripe)
20 msg/giorno × 30 gg = 600 msg → ~6 acquisti/mese = €3k-5.4k MRR equivalente lifetime

**Why:** Sprint 5 roadmap lancio FLUXION. Primary acquisition channel (60% cold outreach).

**How to apply:** Prima di modificare il blueprint, verificare che la struttura file sia
ancora allineata con la directory `tools/SalesAgentWA/`. La prima implementazione
richiede 2h setup + 2 settimane warm-up manuale da fondatore prima di automatizzare.
