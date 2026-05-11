# Prompt ripartenza S198 — Generato S197 chiusura ordinata

**Generato**: 2026-05-11 (S197 chiusa context 62%)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Ultimo commit S197**: vedi `git log --oneline | head -5`

## S197 ✅ CHIUSA — Deploy F-3+F-4 LIVE

- PRE-LAUNCH-AUDIT.md NEW 242 righe (commit `65dfc97`)
- Cleanup orphan `scripts/setup-piper.js` (commit `65dfc97`)
- Deploy CF `fluxion-proxy` version `008dd86c-46c1-4a55-8943-32814dac1019` LIVE
- Cron triggers attivi: `0 9 * * *` (F-3) + `*/5 * * * *` (F-4)
- Gate 3 ✅ COMPLETO BLINDATO (F-1..F-4 + D-1..D-3 P95 sotto SLO)

## S198 START

```
PRIORITY 1 (~5 min): E2E admin endpoints auth fix.
  ssh imac "grep '^ADMIN_API_SECRET=' '/Volumes/MacSSD - Dati/fluxion/.env'" | head -c 60
  Confronta con CF Worker secret. Se diverso → re-set via wrangler secret put
  (pattern reference_cloudflare_token.md S192-procedure).
  Verifica:
    SECRET=$(ssh imac "grep '^ADMIN_API_SECRET=' '/Volumes/MacSSD - Dati/fluxion/.env'" | cut -d= -f2)
    curl -s -X POST https://fluxion-proxy.gianlucanewtech.workers.dev/admin/health/run-now -H "Authorization: Bearer $SECRET"
    curl -s -X POST https://fluxion-proxy.gianlucanewtech.workers.dev/admin/email-sequence/preview -H "Authorization: Bearer $SECRET" -H "Content-Type: application/json" -d '{"email":"fluxion.gestionale@gmail.com","tier":"BASE","step":1}'
    unset SECRET

PRIORITY 2 (~30 min): privacy policy + ToS via agent legal-compliance-checker
  → pubblicare landing CF Pages (P0 GDPR pre-launch).

PRIORITY 3 (~60 min): test live audio Sara iMac — 5 scenari (voice-agent-details.md):
  Gino/Gigio, VIP, chiusura graceful, flusso perfetto, waitlist.

PRIORITY 4 (founder schedule TBD): build Win MSI cross-compile
  (P0 ~80% mercato IT — rule architecture-distribution.md).

PRIORITY 5 (P1 deferred): FAQ pubblica via documentation-writer.
```

## Vincolo S197 acquired (vincolo #11 strutturale)

**MAI proporre "founder action CF rotate/deploy" senza prima**:
1. Leggere `reference_cloudflare_token.md` (procedura SSH stateless)
2. `ssh imac "grep '^CLOUDFLARE_API_TOKEN=' '/Volumes/MacSSD - Dati/fluxion/.env'" | head -c 30` (verifica esiste)
3. Verifica scope via API `curl /accounts/{ID}/workers/scripts`

Pattern deploy autonomo:
```
TOKEN=$(ssh imac "grep '^CLOUDFLARE_API_TOKEN=' '/Volumes/MacSSD - Dati/fluxion/.env'" | cut -d= -f2)
CLOUDFLARE_API_TOKEN=$TOKEN CLOUDFLARE_ACCOUNT_ID=22ddff3a4ef544511523a841b3dcadf8 npx wrangler deploy
unset TOKEN
```

## Riferimenti

- Audit: `docs/launch/PRE-LAUNCH-AUDIT.md`
- Perf Gate 3: `docs/perf/D{1,2,3}-*.md`
- CF token procedure: `~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/reference_cloudflare_token.md`
- HANDOFF dettagli S197: `HANDOFF.md` sezione 197
