# PROMPT RIPARTENZA — SESSIONE 190 FLUXION

## S189-B ✅ CHIUSA — Gate 3 P0 LIVE su Cloudflare

**F-3 + F-4 deployed**:
- Worker `fluxion-proxy.gianlucanewtech.workers.dev` version `6c21c822`
- Cron live: `0 9 * * *` (email daily) + `*/5 * * * *` (health 5min)
- Secrets settati: `DISCORD_HEALTH_WEBHOOK_URL` + `ADMIN_API_SECRET` (ruotato in `/tmp/fluxion_admin_secret.txt`)

**E2E verde**:
- F-3: 5 email step a `fluxion.gestionale@gmail.com` con resend_id confermati
- F-4: `state=healthy` (landing UP, resend UP, stripe UP)

**Bug fix S189-B**: rimosso self-probe `/health` da `fluxion-proxy/src/scheduled/health-monitor.ts`. CF Workers non instrada self-fetch durante scheduled invocation. Ridondante.

## Token CF (memoria aggiornata `reference_cloudflare_token.md`)
- WORKING: `[REDACTED-CF-TOKEN-WORKING-S192]` (iMac `.env`)
- DEAD: `[REDACTED-CF-TOKEN-DEAD-S192]` (scope vuoto, NON usare)
- Account: `22ddff3a4ef544511523a841b3dcadf8`

## Gate 3 status
- F-1 ✅ | F-2 ✅ | F-3 ✅ LIVE | F-4 ✅ LIVE
- D-1 SQLite EXPLAIN (MacBook) — OPEN P1
- D-2 IPC <100ms (MacBook Tauri) — OPEN P1
- D-3 Voice Piper P50/P95 (NEEDS iMac voice-pipeline) — OPEN P1

## S190 prossimi step
1. Founder verifica Gmail (5 email da `onboarding@resend.dev`) + Discord (alert RECOVERED)
2. D-1 + D-2 eseguibili MacBook senza iMac
3. D-3 → avviare voice-pipeline iMac

## Note
- Per future deploy CF: usa token iMac via `ssh imac "grep CLOUDFLARE_API_TOKEN '/Volumes/MacSSD - Dati/fluxion/.env'"` oppure direct CF API
- `.env` MacBook non scrivibile (permission denied verificato S189-B) — token non persistito locale
