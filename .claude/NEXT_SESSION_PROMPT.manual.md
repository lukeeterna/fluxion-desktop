# S243 — FLUXION Resume Prompt

**Generato**: 2026-05-15 fine S242
**Status S242**: ORANGE — T0 falsificato live test, plan T0+T1+T2 patch atomica per S243
**Repo**: `/Volumes/MontereyT7/FLUXION` master
**Last commit**: `63539b7 chore(S241): close session GREEN — P0 €297 cleanup done + P2 WA pipeline audit landed`

## S242 Outcome (cosa è successo)

1. **Pivot da WA outbox a Sara VoIP**: founder ha contestato (giustamente) la raccomandazione di fixare P0 WA outbox in fase pre-product. Sara non funziona ancora → blocker hard prima di qualsiasi outreach. WA outbox refactor deferred a post-first-paying-customer.
2. **Test live Sara T0** (commit `4df32f1` S240): pipeline UP `VOIP_LOCAL_PORT=6080`, SIP REGISTER 200 OK. Founder ha chiamato da 3281536308 → "Vodafone telefono spento".
3. **T0 FALSIFICATO definitivamente**: smoking gun log `/tmp/sara-live-s242-t0.log` linea 115:
   ```
   18:10:28 Audio bridge established: call(slot=1) ↔ Sara(slot=2) after 0ms
   18:10:28 Assertion failed: (glock->owner == pj_thread_this()),
            function grp_lock_unset_owner_thread, file lock.c, line 279.
   Fatal Python error: Aborted
   ```
   Faulthandler: solo `_pjsua2_thread` + main asyncio visibili. Il thread che aborta è **C-only invisible** (pjmedia clock master non pjlib-registered al release `grp_lock`). T0 (revert `mainThreadOnly=False`+`threadCnt=1`) non tocca C-thread spawning interno pjmedia.
4. **Founder ha delegato a Claude.ai** per generare patch T0+T1+T2 atomica. File `voip_pjsua2.py` (54KB, 1.5K righe) aperto in TextEdit MacBook per copia-incolla.

## S243 — Primo task: applicare patch unificata

**Path A (preferito)** — Patch fornita da Claude.ai esterna:
1. Founder incolla `voip_pjsua2.py` su Claude.ai con dossier `/Volumes/MontereyT7/FLUXION/DOSSIER-SARA-VOIP-BUG.md` (603 righe)
2. Claude.ai genera patch git apply-ready T0+T1+T2
3. Applico patch su MacBook: `cd /Volumes/MontereyT7/FLUXION && git apply <patch>`
4. Sync iMac: `git push && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull"`
5. Riavvio pipeline iMac: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && VOIP_LOCAL_PORT=6080 nohup ./venv/bin/python main.py > /tmp/sara-live-s243.log 2>&1 & echo PID=\$!"`
6. Test live founder chiama 0972536918 da 3281536308
7. Verdetto discriminate (vedi sotto)

**Path B (fallback se A fallisce)** — Downgrade pjsip 2.15 LTS:
1. Hypothesis: bug `grp_lock_unset_owner_thread` è regressione 2.16-dev
2. Effort: ~2h rebuild SWIG su iMac (download tarball + `./configure && make && make install` + rebuild Python bindings)
3. Rischio: SWIG compatibility macOS 11 Big Sur, può rompersi

**Path C (fallback finale)** — Asterisk ARI Docker:
1. Eliminare pjsua2 completamente, sostituirlo con container Asterisk
2. Python parla REST/WebSocket con Asterisk via ARI
3. Effort: 1-2 sessioni dedicate, refactor pesante
4. Vantaggio: battle-tested, elimina C-thread invisible hell

## Discriminate criteria S243 test live

| Outcome | Verdetto | Next |
|---------|----------|------|
| Sara audible <3s + dialog coerente | T0+T1+T2 ✅ chiudi VERDE | S244 sprint produzione |
| Vodafone "spento" + SIGABRT grp_lock | Patch falsificata | Path B downgrade 2.15 |
| Sara audio rotto / silenzio | Discrimina T1 lock inversion vs T2 refcount | Issue-specific patch |
| SIGSEGV / nuova crash | Patch ha rotto altro | Revert + analizza |

## Roadmap aggiornata S243+

**S243 — Sara VoIP fix** (gating hard):
- Apply patch T0+T1+T2 → test live → verdetto
- Se KO: B1 → B2 fino a Sara funzionante

**S244+ — Sprint produzione** (SOLO post-Sara verde):
- P0 Win MSI unsigned (mercato Italia ~80% Win)
- P1 Sentry free tier (verifica downgrade Developer 2026-05-15)
- P2 Sara latency 1330→<800ms (streaming L4_groq→TTS chunked)
- P3 Beta clienti scouting (5-20 contatti manuali, NO automation, NO WA blast)
- P4 Ehiweb wizard onboarding (quando tariffa €/mese arriva — Open Q D-03)

**DEFERRED indefinito** (rivalutare a primo cliente pagante):
- WA outbox SQLite refactor (`.claude/cache/agents/s241/wa-pipeline-audit-P2.md` resta valido come riferimento)
- Switch Twilio dedicated number (D-02 trigger: 1° bonifico €497)
- Landing per-verticale 9 settori (D-01 trigger: post P0+P1 working)
- Video demo Sara per verticale (D-01 trigger: post P5 outreach iniziato)

## Vincoli mantenuti

- Zero-cost (#5): no servizi paid, no nuovi acquisti hardware
- Italiano per founder, tecnica in EN
- D-01 VOS DECISIONS.md: 2-tier €497/€897, FLUXION = gestionale + Voice Agent Sara
- D-02 VOS: WA 3314928901 condiviso, persona "Erica Fluxion" solo in body messaggi
- Context budget: `/context` monitor, sopra 50% NO edit schema/migration/CLAUDE.md/HELPDESK.md
- CTO ownership (memoria `feedback_cto_decide_no_review.md`): decido io P0/P1/P2, founder collabora

## Stato repo fine S242

- MacBook: `63539b7` master
- iMac: TODO sync (se diverge dopo S241 commit chiusura)
- Pipeline iMac voice-agent: DOWN (PID 33282 killed in test S242)
- WA daemon: NOT running (deferred fix)

## Open Q founder pendenti

1. **Tariffa Ehiweb €/mese cliente** (D-03 Open Q #3): TBD, non blocker S243 (deferred a P4 S244+)
2. **Claude.ai patch T0+T1+T2 pronta?**: founder deve confermare quando ha la patch in mano da incollare

## Anti-pattern da evitare S243 (lezioni S232-S242)

- MAI `f"{exc}"` su `pj.Error` — usare `exc.info(True)` (lezione S236 permanente)
- MAI assumere thread Python visibile = unico thread coinvolto (S239 ha mostrato C-thread invisible)
- MAI sovradimensionare architettura pre-product (lezione S242 WA outbox)
- MAI lanciare beta su pipeline non validata live (lezione: 3+ ipotesi falsificate solo con test reale chiamata Vodafone)
