# PLAYBOOK — FLUXION

**Ultimo aggiornamento**: 2026-04-24 (S167)
**Stato**: Instabile — aggiornare ad OGNI cambio procedura. Niente riassunti in altri file.

> Questo è l'unico posto dove vivono le procedure correnti.
> Quando cambia pricing, messaggistica, deploy, runbook → si aggiorna QUI.
> Non toccare NORTH_STAR.md per cambi di procedura.

---

## Pricing (2026-04-24)
| Tier | Prezzo | Include | Durata |
|------|--------|---------|--------|
| Base | €497 | Gestionale + WhatsApp + Sara trial 30gg | Lifetime |
| Pro | €897 | Gestionale + WhatsApp + Sara per sempre + 1 nicchia configurata | Lifetime |
| Clinic | nascosto | TBD tier enterprise cliniche/dentisti (non ancora in vendita) | — |

Commissione Stripe: 1.5%. Nessun altro costo.

## Messaggistica sales corrente
- **Landing pubblica**: https://fluxion-landing.pages.dev (deploy branch=main)
- **Template WA primo contatto**: Sales Agent WA Blueprint → `tools/SalesAgentWA/SALES-AGENT-BLUEPRINT.md`
- **Mittente WA outreach**: 3314928901 (vedi `memory/reference_wa_sales_numbers.md`)
- **Numero test**: 3807769822
- **Email post-vendita**: fluxion.gestionale@gmail.com via Resend API
- **Regola copy**: €497 (mai €297), "Segretaria AI" (mai "Voice AI"), "FLUXION" maiuscolo sempre.
- **Regola WA outreach**: max 5 righe, zero emoji, zero formalismi (Luca Ferretti rule).

## Sequenza Sales Agent WA
- **LaunchAgent**: `~/Library/LaunchAgents/com.fluxion.wa-monitor.plist`
- **Frequenza**: ogni 15 min nelle fasce 9–12 e 14–17 (evita sveglia clienti)
- **Batch giornaliero**: 5 msg (limite soft anti-ban)
- **Log monitor**: `ssh imac "tail -f /tmp/wa_monitor_cron.log"`
- **Invio manuale**: `ssh imac "nohup python3 agent.py send --limit 5 > /tmp/wa_send.log 2>&1 &"`
- **Comandi sales agent**: `scrape`, `send --limit N`, `monitor [--loop]`, `stats`, `dashboard`

## Procedure deploy

### Landing (CF Pages)
```bash
CLOUDFLARE_API_TOKEN=<token> wrangler pages deploy ./landing \
  --project-name=fluxion-landing --branch=main --commit-dirty=true
```
⚠️ Usare `--branch=main` NON `--branch=production` per aggiornare il dominio live.

### Proxy API (CF Worker)
```bash
cd fluxion-proxy && CLOUDFLARE_API_TOKEN=<token> wrangler deploy
```

### Voice Pipeline Sara (iMac 192.168.1.2)
```bash
ssh imac "kill \$(lsof -ti:3002); kill \$(lsof -ti:5080); sleep 2; \
  cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  DYLD_LIBRARY_PATH=lib/pjsua2 PYTHONUNBUFFERED=1 \
  nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python \
  main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```
⚠️ **Riavviare dopo OGNI modifica codice Python voice-agent.**

### App Tauri (build cross-platform)
- Build: solo su iMac (MacBook è dev-only, no Rust toolchain).
- macOS: PKG/DMG Universal Binary + ad-hoc signing.
- Windows: MSI unsigned (SmartScreen mitigation pagina).
- Release: GitHub Releases con auto-update Tauri.

## Runbook incident

### Voice pipeline down (porta 3002)
```bash
curl http://192.168.1.2:3002/health                   # check
ssh imac "tail -50 /tmp/voice-pipeline.log"           # diagnosi
# Restart con comando sopra
```

### WA monitor bloccato
```bash
ssh imac "tail -100 /tmp/wa_monitor_cron.log"
ssh imac "launchctl unload ~/Library/LaunchAgents/com.fluxion.wa-monitor.plist"
ssh imac "launchctl load ~/Library/LaunchAgents/com.fluxion.wa-monitor.plist"
```

### Landing 500 / down
1. Verifica CF dashboard status
2. Redeploy con comando sopra (ultima versione stabile)
3. Se regressione: `git log` → `git revert <sha>` → redeploy

### Stripe webhook fail
- Log: Stripe dashboard → Developers → Webhooks → attempts
- CF Worker log: `wrangler tail` in `fluxion-proxy/`
- Ritenta manualmente da dashboard Stripe dopo fix

## Sessioni Claude Code

### Start sessione
1. Leggi `HANDOFF.md` → fase corrente
2. Leggi `.claude/NORTH_STAR.md` → verifica allineamento task
3. Leggi `ROADMAP_REMAINING.md` → prima fase pending
4. `/gsd:plan-phase <FASE>` se manca PLAN.md
5. `/gsd:execute-phase` per implementare

### Fine sessione
1. Aggiorna `ROADMAP_REMAINING.md` (fase completata → archiviata)
2. Aggiorna `HANDOFF.md` (stato + prossimo step)
3. Aggiorna `~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md` (max 200 righe)
4. Fornisci SEMPRE il prompt di ripartenza per sessione successiva

## Convenzioni codice (enforcement)
- TypeScript: strict mode, zero `any`, zero `@ts-ignore` senza justification.
- Rust: Tauri commands sempre `async`, `Result<T, E>` tipizzato.
- Python voice-agent: no venv (Python 3.9 system iMac), import assoluti.
- Field names API: italiani (`servizio`, `data`, `ora`, `cliente_id`).
- Commit: conventional (`feat:`, `fix:`, `docs:`, `chore:`), MAI `--no-verify`.
- Branch: lavoro diretto su `master` (fondatore solista), rebase quando sync iMac.

## Storico cambi
- **2026-04-24 (S167)** — Creato PLAYBOOK (consolidamento procedure sparse).
- **2026-04-24 (S167)** — Fix video freeze: `pad_video_to_audio()` ora usa `-stream_loop -1` invece di `tpad=clone`.
