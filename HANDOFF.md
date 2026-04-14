# FLUXION — Handoff Sessione 159 → 160 (2026-04-14)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline porta 3002 (127.0.0.1 only) | SIP: 0972536918

---

## SESSIONE 159 — COMPLETATA (2026-04-14)

### Risultati
1. **Sales Agent WA implementato** — 8 file Python creati in `tools/SalesAgentWA/`:
   - `agent.py` — CLI principale (init/scrape/send/dashboard/stats/pause/resume/next-week)
   - `scraper.py` — 3 sorgenti (Google Places / PagineBianche / OSM Overpass)
   - `sender.py` — Playwright WA Web automation con anti-ban
   - `templates.py` — 6 categorie, 3+ varianti per sezione
   - `dashboard.py` — Flask dashboard con funnel AARRR
   - `utm.py` — UTM link builder + phone normalizer
   - `config.py` — Costanti e configurazione
   - `com.fluxion.salesagent.plist` — LaunchAgent iMac

2. **Scraping testato su iMac**: 18 lead reali scrappati da PagineBianche
   - 8 parrucchieri Milano
   - 10 officine Milano
   - Google Places: skip (GCP credits esauriti, key non configurata)
   - OSM: 0 risultati (pochi dati con telefono in OSM per Italia)

3. **PagineBianche CSS selectors fixati**: il sito usa `div.list-element__content` come container listing, non i selettori standard del blueprint

4. **Dry-run testato**: 5 messaggi generati con personalizzazione corretta (nome, attivita, citta, UTM)

5. **Dashboard API testata**: /api/stats e /api/categories funzionanti

### Test Results S159
```
Scraping:    18 lead reali (PagineBianche Milano)
Dry-run:     5/5 messaggi generati correttamente
Dashboard:   API stats + categories OK
TypeScript:  0 errors (pre-commit passed)
```

### File creati/modificati
- `tools/SalesAgentWA/agent.py` — nuovo
- `tools/SalesAgentWA/config.py` — nuovo
- `tools/SalesAgentWA/utm.py` — nuovo
- `tools/SalesAgentWA/templates.py` — nuovo
- `tools/SalesAgentWA/scraper.py` — nuovo + fix selettori PagineBianche
- `tools/SalesAgentWA/sender.py` — nuovo + lazy playwright import + dry-run fix
- `tools/SalesAgentWA/dashboard.py` — nuovo
- `tools/SalesAgentWA/com.fluxion.salesagent.plist` — nuovo

---

## STATO BLOCKER (invariato da S157)
Tutti 7 BLOCKERS chiusi. Prodotto tecnicamente pronto.

---

## PROSSIME SESSIONI

### SESSIONE 160 — SALES AGENT: PLAYWRIGHT + PRIMO INVIO
```
STEP 1: Installare Playwright su iMac: pip3 install playwright && python3 -m playwright install chromium
STEP 2: Login WA Web (QR code — fondatore deve scansionare fisicamente)
STEP 3: Primo invio REALE: python3 agent.py send --limit 3
STEP 4: Aggiornare YOUTUBE_LINKS in config.py con URL reali
STEP 5: Scraping multi-citta: roma, napoli, torino
STEP 6: Avviare dashboard: python3 agent.py dashboard
STEP 7: (Opzionale) Installare LaunchAgent per background execution
```

### Prompt di ripartenza S160
```
Leggi HANDOFF.md. Sessione 160.
S159: Sales Agent WA implementato. 8 file Python. 18 lead reali scrappati.
Dry-run OK. Dashboard API OK.
TASK: Installare Playwright su iMac, fare login WA Web (fondatore),
primo invio REALE, aggiornare YOUTUBE_LINKS con URL reali.
```

---

## STATO GIT
```
Branch: master | Commit: a3cd893 fix(S159): dry-run skips business hours wait
```
