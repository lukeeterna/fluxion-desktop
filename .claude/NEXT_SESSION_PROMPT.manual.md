# S247 — DECIDE D1/D2/D3 (FOUNDER) + START FIX SEQUENCE PRE-LAUNCH

**Generato**: 2026-05-15 fine S246 (CLOSED GREEN — audit 6/6 completo, 31 P0 enumerati)
**Repo**: master (commit S246 chiusura)
**Pipeline iMac**: DOWN_OK
**Mandato S244**: "se devo partire deve essere tutto pronto e pienamente funzionante" — NO MVP, NO lancio parziale.

## Audit S245+S246 — STATO FINALE

File: `.claude/cache/agents/s245/PRE-LAUNCH-AUDIT.md` (376 righe, 6/6 categorie)

| Cat | Nome | P0 | Effort range |
|-----|------|-----|--------------|
| 1 | Build/Distribution | 8 | 12-16h |
| 2 | Functional E2E | 7 | 30-50h |
| 3 | Security | 5 | 8-12h |
| 4 | Performance | 1 | 1h |
| 5 | Compliance | 5 | 14-20h |
| 6 | Customer Success | 5 | 12-17h |
| **TOT** | | **31 P0** | **77-116h** |

Range realistico pre-launch: **~85-100h sequential** (≈60-75h wall-clock se 2 stream paralleli).

## DECISIONI FOUNDER pending (CTO recommendations)

**D1 — Sara VoIP path** → raccomandazione **D Asterisk ARI Docker**
- B1 downgrade pjsip 2.15.1 = workaround temporaneo (2-4h, rischio re-rottura macOS Big Sur)
- D Asterisk ARI Docker = enterprise-robust definitivo (8-16h, stack separato HTTP+WS)
- Motivo: 9 fix S232-S239 falsificati su pjsua2 SWIG indicano bug strutturale binding

**D2 — WhatsApp stack** → raccomandazione **A Meta Business API (Pro) + B Baileys+consenso (Base)**
- A Meta Business API: NO ban, $0.05-0.15/template, account Meta Business required
- B Baileys: zero-cost, consenso esplicito ToS al cliente
- **RIFIUTO** mantenere whatsapp-web.js (viola ToS, ban rischio = causa civile)

**D3 — Verticali count 8 vs 9** → raccomandazione **aggiornare docs a 8 macro/17 micro**
- Codice `src/types/setup.ts:80-127` ha 8 macro (assicurazioni/immobiliare dentro `professionale`)
- Refactor a 9 macro = 8-12h + migration; doc update = 5min

## Sequenza fix consigliata (4 fasi)

### FASE A — Founder actions (parallel, ~1d)
- D1/D2/D3 decisioni
- **Sentry trial Business 14gg con NUOVO account email** (founder request S246):
  - Account originale `fluxion.gestionale@gmail.com` Trial Business scaduto 2026-05-15 (oggi)
  - Creare nuovo account Sentry con email alternativa (es. `fluxion.dev@gmail.com` o variant founder) → attivare Trial Business 14gg fresh
  - Sfruttare APPIENO features Business in finestra trial: Performance Monitoring (tracesSampleRate>0), Session Replay, Profiling, Advanced Alerting, Issue Owners, Custom Dashboards
  - Pattern: ciclo trial multipli con email rotation pre-revenue (vincolo zero-cost #5)
  - Update DSN in `src-tauri/src/lib.rs` + `src/main.tsx` + GH secrets `SENTRY_DSN`/`SENTRY_AUTH_TOKEN`
  - Calendar reminder: nuovo downgrade ~14gg da activation (~2026-05-29)
- Rigenerare Tauri signing key + GH secrets (1h)
- Aprire account Meta Business API (D2 path A)
- Aprire account Ehiweb commerciale (Cat 2 P1)

### FASE B — Security + Performance + Compliance fondamenta (~25-35h)
- Cat 3: encryption salt random per-installation + CSP Tauri + cargo audit CI + HTTP Bridge auth
- Cat 4: ipc_bench live run + report
- Cat 5: FatturaPA XSD validator + GDPR export/erasure IPC + cookie banner + DPA template

### FASE C — Build + Functional core (~40-60h)
- Cat 1: bump Cargo 1.0.1 → createUpdaterArtifacts true → sidecar build → MSI/UB targets → release pipeline → latest.json
- Cat 2: Operatori CRUD UI + Calendario d&d + WA stack migration (post D2) + Sara VoIP fix (post D1) + Sara web E2E + E2E suite verde
- Cat 6: help center in-app + backup/restore DB + video tutorial Sara

### FASE D — Pre-launch validation (~8-12h)
- Smoke test installers cross-OS (macOS arm64+x64, Win10/11)
- VirusTotal submission
- E2E suite 10 spec verde su CI
- FatturaPA sandbox SDI invio reale
- Refund flow E2E TEST MODE
- Sentry capture test → email founder

## Primo task S247

1. **Founder conferma/dissenso D1, D2, D3** (le 3 decisioni sopra)
2. **Sentry nuovo trial Business 14gg** (founder request S246):
   - Founder crea account Sentry con email alternativa (NON `fluxion.gestionale@gmail.com` — già trial-burned)
   - Attiva Trial Business 14gg → fornisce nuovo DSN + auth token a CTO
   - CTO aggiorna `src-tauri/src/lib.rs` (Rust DSN env var) + `src/main.tsx` (Frontend DSN env var) + GH secrets
   - CTO abilita features Business per finestra trial: `tracesSampleRate: 0.1` (Performance), `replaysSessionSampleRate: 0.1` (Session Replay), `profilesSampleRate: 0.1` (Profiling)
   - CTO setup Custom Dashboards Sentry per pre-launch monitoring (error trends, slow IPC, voice pipeline failures)
   - Salvare reminder calendar: downgrade ~2026-05-29 → revert sample rates a 0.0 prima scadenza
3. **Start FASE B** se decisioni confermate — Cat 3 encryption salt fix per primo (root cause sicurezza più critica + isolato)

Vincoli mantenuti:
- Verifiche reali, no claim a memoria
- Sequential, atomic commits per ogni P0 risolto
- CTO decide P0/P1/P2 — no review
- A 65% context chiudi pulito
- Test E2E obbligatorio per ogni fix
- Zero costi mantenuto

## Comando ripartenza S247

```bash
cd /Volumes/MontereyT7/FLUXION
git log -1 --format="%h %s"
cat .claude/NEXT_SESSION_PROMPT.manual.md
cat .claude/cache/agents/s245/PRE-LAUNCH-AUDIT.md | tail -100  # sintesi finale + sequence
# Poi: presentare di nuovo D1/D2/D3 al founder se non ha già confermato
# Poi: avviare FASE B Cat 3 P0 #1 encryption salt random per-installation
```

## Stato repo fine S246

- Audit 6/6 completato committato (S246 doc-only)
- Pipeline iMac DOWN_OK
- 31 P0 enumerati con effort e dipendenze
- Decisioni founder D1/D2/D3 in attesa
- Tech debt minore: `tools/VectCutAPI` dirty submodule (ignorato)
- NESSUN codice modificato S246 (audit only)
