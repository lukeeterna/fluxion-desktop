# S245 — PRODUCTION SPRINT START (PIVOT da VOIP debug)

**Generato**: 2026-05-15 fine sessione S244 (CLOSED ORANGE, founder esausto)
**Repo**: `/Volumes/MontereyT7/FLUXION` master `3348ecc`
**Pipeline iMac**: DOWN_OK (clean stop dopo T3 falsified)

## Contesto S244 chiusura — onestà CTO

**5 fix VOIP tentati oggi tutti falsificati** (T0 S240, T1/T1.5/T2 S243, T3 S244). Pattern strutturale confermato: refactor pjmedia op queue in pjsip 2.16-dev è rotto cross-thread anche single-thread (threadCnt=0).

**T3 smoking gun** (`.claude/cache/agents/s244/t3-extract.log`):
- `Add port 1 queued` su `_pjsua2_thread` ✅ (pjsua_0 eliminato OK)
- `Add port 2 (sara_bridge) queued` su `onCallMediaS` (Python thread)
- → cross-thread sul conf op queue → bridge wiring fail → Vodafone "telefono spento"

**Errore CTO oggi**: continuato a patchare 2.16-dev quando segnali "branch instabile" erano chiari dalla S237 (status=506784 non mappato + log `possibly re-registering existing thread` esplicito). Avrei dovuto proporre B1 downgrade 2.15.1 6 ore fa.

**Decisione**: VOIP via SIP NON è blocker lancio. Sara web/Tauri funziona. Rientra come tech debt.

## VOIP path futuro (NON in S245)

- **B1**: downgrade pjsip 2.15.1 LTS + rebuild SWIG bindings (~2h, mente fresca)
- **D**: fallback Asterisk ARI Docker zero-cost (~1-2 sessioni)
- NO altri patch SWIG su 2.16-dev — branch instabile dimostrato 5 volte.

## START S245 — Production Sprint P0

Founder priority shift S240 era già chiaro: dimentica VOIP, sblocca revenue.

### PRIMA di code: rispondere ai 5 dubbi founder residui

1. **Pricing migration**: drop €297 Base. Cosa fa migrazione clienti esistenti €497→€897 Pro?
2. **Ehiweb mechanic**: come si integra provider VOIP business italiano per produzione?
3. **Landing per verticale**: 9 landing distinte o 1 con tab? CF Pages costi €0?
4. **Video demo Sara**: senza VOIP attivo, registrare con Sara web Tauri (schermo + voce iMac)?
5. **Beta clienti scouting**: 6 clienti ITA, canali outreach? LinkedIn? Reddit r/PMI? Cold email?

### Plan P0-P7

- **P0** pricing 2-tier €497/€897 (drop €297) — Stripe + Worker + landing
- **P1** Ehiweb mechanic VOIP commerciale (sblocca produzione Sara via telefono FUTURO)
- **P2** Win MSI unsigned + pagina SmartScreen mitigation
- **P3** Sentry free tier verify post auto-downgrade (oggi 2026-05-15)
- **P4** Sara latency 1330ms → <800ms (streaming L4 Groq + TTS chunked)
- **P5** sales agent AMBRA-style su WA `3314928901` Erica Fluxion (riuso Baileys ARGOS)
- **P6** beta 6 clienti ITA scouting + onboarding
- **P7** public launch

## Comando ripartenza S245

```bash
cd /Volumes/MontereyT7/FLUXION
git log -1 --format="%h %s"            # 3348ecc T3 falsified
cat .claude/cache/agents/s244/t3-extract.log
# Poi: 5 dubbi founder → scegliere P0 prima task.
```

## Stato repo S244 finale

- Master `3348ecc` (T3 landed ma falsified, mantenuto in storia per dossier B1 futuro)
- MacBook + iMac sync
- Pipeline iMac DOWN_OK (clean kill PID 53120)
- Sentry account auto-downgrade verifica oggi 2026-05-15 (free tier confirm — calendar reminder)
- CF API token MacBook MISSING (verificare se serve in P0 Stripe deploy)
