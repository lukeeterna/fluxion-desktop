# S246 — CONTINUA PRE-LAUNCH AUDIT (CAT 3-6) + DECIDE PATH SARA + WA STACK

**Generato**: 2026-05-15 fine S245 (CLOSED GREEN — audit Cat 1+2 completo, 15 P0 enumerati)
**Repo**: master (commit S245 chiusura)
**Pipeline iMac**: DOWN_OK
**Mandato S244 ancora attivo**: "se devo partire deve essere tutto pronto e pienamente funzionante" — NO MVP, NO lancio parziale.

## Audit S245 — stato

File: `.claude/cache/agents/s245/PRE-LAUNCH-AUDIT.md`

- **Cat 1 Build/Distribution**: 8 P0 BLOCKING (~12-16h) — v1.0.1 zero assets, latest.json 404, signing key disabled, sidecar placeholder, UB mancante, MSI mancante, version mismatch Cargo/Tauri, createUpdaterArtifacts=false
- **Cat 2 Functional E2E**: 7 P0 BLOCKING (~30-50h) — Calendario drag&drop assente, Operatori.tsx stub 4 righe, WhatsApp-web.js viola ToS, Sara VoIP broken, Sara web E2E non testato, FatturaPA XSD validator CI assente, E2E suite stato run ignoto
- **Cat 3 Security**: PENDING
- **Cat 4 Performance**: PENDING
- **Cat 5 Compliance**: PENDING
- **Cat 6 Customer Success**: PENDING

**Totale P0 attuali (Cat 1+2)**: 15 — effort ~42-66h.

## Primo task S246

1. **Continuare audit Cat 3 Security** — OWASP ASVS L2 check, grep secrets hardcoded, Ed25519 verify, IPC allowlist Tauri capabilities, GDPR audit log, rate limit CF Worker proxy.
2. **Cat 4 Performance** — verificare SLO definiti per startup/IPC/query/Sara/UI. Profiling reale dove possibile (cargo bench, queries plan EXPLAIN).
3. **Cat 5 Compliance** — GDPR completa (cookie banner, privacy, export, erasure, registro trattamenti), D.Lgs 206/2005 recesso 14gg, FatturaPA conformità SDI XSD.
4. **Cat 6 Customer Success** — Setup Wizard UX, video tutorial presenza, help center, self-healing, Sentry free tier verify, auto-update trasparente.

Vincoli S245 confermati:
- Verifiche reali (`ls`, `grep`, `curl`, `npm`, `cargo`)
- Sequenziale, una categoria alla volta
- Decido io P0/P1/P2 — no review founder
- A 65% context chiudo pulito anche se non finito

## Decisioni founder ricorrenti da prendere PRIMA del codice S246+

Queste decisioni founder bloccano implementation. Va deciso PRIMA di partire con fix.

### D1 — Sara VoIP path (post-S244 falsified T3)
- **B1**: downgrade pjsip 2.15.1 LTS rebuild SWIG (~2-4h, rischio bug bypass ma stesso stack)
- **D**: Asterisk ARI Docker zero-cost (~8-16h, stack diverso, robusto enterprise)

Raccomandazione CTO post-audit: **D Asterisk ARI**. Motivo: 9 fix falsificati su pjsua2 SWIG indicano bug strutturale del binding. Asterisk ARI è enterprise-grade, documentato, testato globalmente. Effort maggiore ma definitivo. B1 = workaround temporaneo che potrebbe ri-rompere su Mac Big Sur.

### D2 — WhatsApp stack
- **A**: WA Business API ufficiale via Meta Developer (richiede account Meta Business, costo $0.05-0.15/template, template approval 24h, NO ban rischio)
- **B**: Baileys con consenso esplicito ToS al cliente (zero costo, stesso rischio whatsapp-web.js ma più resiliente)
- **C**: mantenere whatsapp-web.js e rischiare (RIFIUTO CTO — viola guardrail enterprise)

Raccomandazione CTO: **A Meta Business API** per Pro €897, **B Baileys** opzionale per Base €497 con disclaimer. Motivo: clienti enterprise non possono permettersi ban WA su numero business.

### D3 — Verticali macro count
- 8 macro vs 9 docs. Aggiungere `assicurazioni` come macro proprio O aggiornare docs a 8 macro/17 micro (immobiliare/assicurazioni dentro professionale).

Raccomandazione CTO: **aggiornare docs a 8 macro**. Motivo: assicurazioni/immobiliare già dentro `professionale` come micro, no schede cliente verticali specifiche → ristrutturare confonderebbe.

## Comando ripartenza S246

```bash
cd /Volumes/MontereyT7/FLUXION
git log -1 --format="%h %s"
cat .claude/NEXT_SESSION_PROMPT.manual.md
cat .claude/cache/agents/s245/PRE-LAUNCH-AUDIT.md | head -80
# Poi: continuare audit Cat 3 Security. Append a PRE-LAUNCH-AUDIT.md.
# NESSUN commit di codice S246 finché audit 6/6 categorie non chiuso e decisioni founder D1/D2/D3 prese.
```

## Stato repo fine S245

- Audit Cat 1+2 committato
- Pipeline iMac DOWN_OK
- 15 P0 enumerati, founder ha letto Cat 1+2
- Tech debt minore: `tools/VectCutAPI` dirty submodule (ignorato)
