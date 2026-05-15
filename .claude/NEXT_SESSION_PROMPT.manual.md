# S240 — Prompt ripartenza (handoff S239 -> S240)

**Generato**: 2026-05-15 ~16:40 CEST (chiusura S239 ORANGE — F3 falsified, dossier delegato a Claude.ai)
**Branch**: master @ `4da1352` (MacBook + iMac sync)
**Pipeline iMac**: STOPPED clean (DOWN_OK)
**Dossier delega**: `/Volumes/MontereyT7/FLUXION/DOSSIER-SARA-VOIP-BUG.md` (603 righe, 32KB)

## TL;DR S239 outcome

- ✅ **F3 fix landed** (commit `4da1352`): `_install_pjlib_aware_default_executor` sostituisce asyncio default executor con TPE che ha `initializer=_pjlib_thread_initializer`. Audit copre tutti i `run_in_executor(None, ...)` + `asyncio.to_thread(...)` in voice-agent/src.
- ❌ **F3 hypothesis FALSIFICATA** dal test live 16:25:23: SIGABRT identico, `Audio bridge established after 0ms` -> immediato `grp_lock_unset_owner_thread` assertion lock.c:279.
- 🎯 **Smoking gun S239**: faulthandler dump mostra solo 2 thread Python (`_pjsua2_thread` + main asyncio loop). I 2 `_worker` TPE visibili in S238 sono spariti -> non erano il colpevole.
- 🚨 **Implicazione**: vero colpevole è thread **C-only** non visibile dal faulthandler Python. Hypothesis dominante S240: **pjmedia clock master thread** spawnato internamente da pjmedia conference bridge, non controllato da `threadCnt=0`.

## Delega Claude.ai (workflow founder S240)

Founder ha aperto dossier `DOSSIER-SARA-VOIP-BUG.md` in Claude.ai web/desktop per sessione fresca knowledge pjsip internals.

Dossier self-contained: stack, cronologia 9 fix, smoking gun, codice rilevante, 5 hypothesis ordinate (N1 pjmedia clock master TOP, N2 SWIG GC refcount, N3 Endpoint.instance, N4 downgrade 2.15, N5-d Asterisk ARI), comandi riproducibili.

## Plan S240 in Claude Code (se prosegui qui)

### Path A — Claude.ai output disponibile
1. Leggere risposta Claude.ai
2. Applicare patch a `voice-agent/src/voip_pjsua2.py`
3. Sync iMac, restart pipeline, test live founder
4. Se OK -> commit, push, chiudi VERDE

### Path B — Claude.ai non risponde, fix N1 autonomo
Leggere `.claude/cache/agents/s238/pjsua2-clock-master-pattern.md` (388 righe research voice-engineer S238). Implementare master port custom o serialize `conf_connect` via `_pjsua2_thread` pending queue.

### Path C — Fallback architetturale Asterisk ARI Docker
Setup zero-cost iMac: `docker-compose` Asterisk 18 + ARI endpoint + Sara client HTTP/WS. Bypass pjsua2 completo. Cost ~1-2 sessioni.

### Path D — Downgrade pjsip 2.15 stable
Rebuild SWIG bindings su iMac con LTS. Cost ~2h.

## Stato repo

- MacBook: master `4da1352`. Untracked: `DOSSIER-SARA-VOIP-BUG.md`, `.claude/cache/agents/s239/`
- iMac: master `4da1352` synced
- Pipeline: STOPPED clean entrambi

## File modificati S239 (committed `4da1352`)

- `voice-agent/src/voip_pjsua2.py`:
  - L13-26 import `concurrent.futures`
  - L60-118 helper `_pjlib_thread_initializer` + `_install_pjlib_aware_default_executor`
  - L634-641 chiamata `_install_pjlib_aware_default_executor(self._main_loop)` in `VoIPManager.start()`

## Comando one-liner ripartenza S240 (Claude Code locale)

```
Sessione S240 FLUXION. Leggi DOSSIER-SARA-VOIP-BUG.md sez 6 hypothesis N1
(pjmedia clock master thread) + .claude/cache/agents/s238/pjsua2-clock-master-pattern.md
(388 righe research voice-engineer S238). Se founder ha output da Claude.ai
(check chat history o file .claude/cache/claude-ai-response-s240.md) applicare
quel fix. Altrimenti Plan: (a) verifica pjsip upstream GitHub
pjmedia/src/pjmedia/conference.c se conf_bridge spawna clock thread interno
su connect_port. (b) se confermato: implementare master port custom o serialize
conf_connect via _pjsua2_thread pending queue. (c) test live discriminate. (d)
se A non risolve in 1 sessione: valutare N5-d Asterisk ARI Docker zero-cost.
Mantieni F1+F1-bis+F2+F3+faulthandler. NON revert.
```

## Cronologia bug onesta (aggiornata S239)

| Sessione | Fix tentato | Esito | Insight |
|----------|-------------|-------|---------|
| S232 | Test text-based 147/0/0 | Offline OK | Bug solo in SIP live |
| S233-S236 | startTransmit fail diagnostico | status=506784 isolato | Core Audio blocker |
| S237 F1 | `setNullDev()` post `libStart` | startTransmit SUCCESS 0ms | Nuovo blocker grp_lock assertion |
| S237 F1-bis | register audio cb threads | Crash persiste | audio cb non erano colpevoli |
| S238 F2 | register on_connected daemon threads + faulthandler | Crash persiste, dump rivela TPE workers | F2 falsified |
| S239 F3 | asyncio default executor pjlib-aware | Crash persiste, dump pulito 2 thread | **F3 falsified, colpevole C-only** |
| S240 | Delega Claude.ai N1 pjmedia clock master | TBD | In attesa output esterno |
