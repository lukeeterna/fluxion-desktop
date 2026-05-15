# S245 — PRE-LAUNCH AUDIT 6 CATEGORIE ENTERPRISE

**Generato**: 2026-05-15 fine S244 (CLOSED ORANGE — VOIP T3 falsified + scope violation corretto)
**Repo**: `/Volumes/MontereyT7/FLUXION` master `7f800bf`
**Pipeline iMac**: DOWN_OK (clean stop)
**Mandato founder esplicito S244**: "se devo partire deve essere tutto pronto e pienamente funzionante"

## Vincolo non negoziabile (memoria S181 — feedback_cto_full_production_responsibility.md)

> "Completamente a pieno regime" = NO compromessi feature, NO lancio parziale.
> CTO responsibility: enumerare TUTTI i pre-launch gate enterprise senza chiedere.

**NON proporre MVP. NON proporre "1 verticale per validare". NON proporre "lancio parziale".**
Si shippa SOLO con tutti P0 verdi su 6 categorie.

## Primo task S245 (PRIMA del codice, prima di tutto)

Audit completo 6 categorie pre-launch. Output strutturato:

`.claude/cache/agents/s245/PRE-LAUNCH-AUDIT.md`

Per ciascuna categoria:
- **Stato attuale verificato** (filesystem + grep + ssh iMac + curl reali, no claim a memoria)
- **Gap precisi** (cosa manca file-by-file, feature-by-feature)
- **Dipendenze** (cosa blocca cosa)
- **P0 BLOCKING / P1 quality / P2 marketing-readiness** (decido io, no review founder)

### 6 categorie (ordine audit)

1. **Build / Distribution**
   - macOS PKG + DMG ad-hoc signed + Gatekeeper mitigation page
   - Windows MSI unsigned + SmartScreen mitigation page
   - Universal Binary (Intel + arm64)
   - Auto-updater GitHub Releases configurato e testato
   - Python voice agent sidecar bundled (PyInstaller ~520MB)
   - Version checking client-side
   - Distribuzione zero-cost (CF Pages + GitHub Releases)

2. **Functional E2E** — ogni hero feature, test reale
   - Gestionale: calendario (CRUD appuntamenti + drag&drop), clienti (CRUD + import CSV + scheda verticale), servizi/operatori, cassa, fatture elettroniche SDI (export XML)
   - WhatsApp Business: API integrata, template approvati, reminder appuntamenti, campagne, review request
   - Voice Sara: telefono (path B1 downgrade pjsip 2.15.1 OR D Asterisk ARI) + web/Tauri funzionante
   - Marketing: loyalty (punti, premi), pacchetti, scadenze
   - 9 verticali con schede personalizzate (saloni, palestre, medical, auto, odonto, vet, servizi, immobiliare, assicurazioni)
   - Setup wizard zero-friction

3. **Security**
   - OWASP ASVS Level 2 audit
   - Ed25519 license signing + tamper-proof verification
   - Zero secret hardcoded (grep audit)
   - IPC boundaries Tauri (allowlist commands)
   - SQLite consideration (at-rest encryption opzionale?)
   - Audit log GDPR (chi accede a cosa, quando)
   - Rate limiting CF Worker proxy

4. **Performance**
   - SLO definiti e misurati per ogni flusso:
     - Startup <3s
     - IPC <100ms (P95)
     - Query SQLite <50ms (P95)
     - Voice Sara P95 <800ms (attuale 1330ms → gap concreto)
     - UI responsiveness (no jank, FPS >50)
   - Profiling reale, non claim

5. **Compliance**
   - GDPR completa: cookie banner, privacy policy, data export, right to erasure, registro trattamenti, DPO contact, breach notification flow
   - D.Lgs 206/2005: recesso 14gg, termini e condizioni, garanzia legale
   - Fatturazione elettronica SDI: XML FatturaPA conforme, codice destinatario, PEC SDI test

6. **Customer Success**
   - Onboarding wizard zero-friction (Setup Wizard prima apertura)
   - Video tutorial per ogni hero feature (gestionale, WhatsApp, Sara, marketing) — registrati e hostati
   - Help center (FAQ, troubleshooting, install guides per OS)
   - Email support automatizzato (fluxion.gestionale@gmail.com)
   - Self-healing diagnostics (health check 30s, auto-restart 3 fail)
   - Monitoring Sentry free tier verify
   - Aggiornamento auto trasparente

## Vincoli di esecuzione audit (verifiche reali)

- **Filesystem reali**: `ls`, `wc -l`, `grep` su path concreti — no claim a memoria
- **Test reali**: `npm run type-check`, `cargo check`, `pytest`, `curl http://192.168.1.2:3002/health`
- **Browser/UI**: se serve verifica visuale → screenshot via skill `fluxion-screenshot-capture`
- **No subagent paralleli inutili**: audit sequenziale, una categoria alla volta, fonte verificata

## Output atteso audit

Tabella riassuntiva per ogni categoria:
```
| Feature/Aspetto | Stato | Evidence (file:line OR comando) | P0/P1/P2 | Effort stimato |
|-----------------|-------|----------------------------------|----------|----------------|
```

## VOIP path futuro (NON in S245)

Quando si tornerà al VOIP: B1 downgrade pjsip 2.15.1 LTS (~2h mente fresca) OR D Asterisk ARI Docker zero-cost (~1-2 sessioni). NO altri patch SWIG 2.16-dev.

## Stato repo S244 finale

- Master `7f800bf` (chiusura S244)
- T3 patch landed in `3348ecc` (falsified ma mantenuto per dossier B1)
- MacBook + iMac sync
- Pipeline iMac DOWN_OK
- Sentry verifica auto-downgrade oggi 2026-05-15 (rientra in P3 customer-success audit S245)

## Comando ripartenza S245

```bash
cd /Volumes/MontereyT7/FLUXION
git log -1 --format="%h %s"
cat .claude/NEXT_SESSION_PROMPT.manual.md
# Poi: avviare audit categoria 1 (Build/Distribution). Scrivere output in .claude/cache/agents/s245/PRE-LAUNCH-AUDIT.md
# NESSUN commit di codice S245 finché audit 6/6 categorie non chiuso e P0 enumerato.
```
