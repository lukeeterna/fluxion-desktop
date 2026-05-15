# S244 — FLUXION Resume Prompt

**Generato**: 2026-05-15 fine S243
**Status S243**: ORANGE — patch T1+T1.5+T2 applicata e FALSIFICATA live test, delega Claude.ai per diagnosi externa
**Repo**: `/Volumes/MontereyT7/FLUXION` master `161ecef`
**iMac**: sync `161ecef`, pipeline DEAD (PID 37288 abortita da SIGABRT)

## S243 outcome (cosa è successo)

1. **Patch Claude.ai applicata**: 8 modifiche surgicali via Edit tool (hunk counts patch malformati, fallback a Edit manuale). Commit `161ecef`.
   - T1: `_PendingBridge` dataclass + defer startTransmit nel main loop `_pjsua2_thread.drain_pending_bridges()`
   - T1.5: rimosso sleep loop bloccante 25×20ms dentro `onCallMediaState`
   - T2: `SaraAccount.active_calls/_released_calls`, deferred next-tick release pattern
2. **Test live 18:40:31**: founder chiama 0972536918 da 3281536308 → "Vodafone telefono spento". Pipeline `_pjsua2_thread` SIGABRT su `grp_lock_unset_owner_thread lock.c:279`.
3. **Patch FALSIFICATA con timing diverso da S242**:
   - S242 (T0 solo): crash DOPO `startTransmit` ("Audio bridge established 0ms")
   - S243 (T0+T1+T1.5+T2): crash PRIMA di drain_pending_bridges, subito dopo `S243 T1: bridge wiring enqueued`
4. **Insight S243**: il bug NON dipende da `startTransmit` né dal callback context. Il colpevole è ANCHE PIÙ A MONTE — probabilmente C-thread pjmedia spawnato lazy da `ensure_port()` o `getAudioMedia()` che non è pjlib-registered.

## Smoking gun S243

Log file: `.claude/cache/agents/s243/live-test-log-s243.txt` (16559 bytes, 131 righe, scp'd da iMac /tmp/sara-live-s243.log)

Sequence chiave:
```
18:40:31 Incoming call from: <sip:3281536308@79.98.45.133>
18:40:31 S236 DIAG H1: call_audio=AudioMedia mro=...  (ensure_port + getAudioMedia OK)
18:40:31 S236 DIAG H2: audio_port refcount=2 _port_created=True
18:40:31 S236 DIAG H3: call.format=sara.format (8kHz mono L16 match perfetto)
18:40:31 S243 T1: bridge wiring enqueued (media_idx=0, queue_depth=1)
Assertion failed: (glock->owner == pj_thread_this()), function grp_lock_unset_owner_thread, file lock.c, line 279.
Fatal Python error: Aborted

Thread 0x0000700015b85000 (most recent call first):
  pjsua2.py:13767 in libHandleEvents
  voip_pjsua2.py:793 in _pjsua2_thread
```

Solo `_pjsua2_thread` visibile aborting → thread offender è C-only invisible (pattern S239 N1 hypothesis).

## Stato delega Claude.ai

**File prompt diagnostico**: `.claude/cache/agents/s243/claude-ai-prompt.md`

Founder ha incollato (o sta incollando) questo prompt su Claude.ai per analisi esterna fresca. Richieste:
1. Decode line `pjsua2.py:13767 libHandleEvents` → quale C function nel sorgente pjsip 2.16-dev
2. Ranking hypothesis N1-N5 con motivazione
3. Se N1 (pjmedia clock C-thread): workaround Python-side via ctypes possibile?
4. Se N4 (regressione 2.16-dev): runbook downgrade 2.15.1 LTS testato macOS 11
5. Se N5 (Asterisk ARI): skeleton Python aiohttp WebSocket+REST equivalente

## S244 — Primo task: leggere output Claude.ai

**Workflow attesa**:
1. Founder incolla output Claude.ai (ranking + patch/runbook)
2. Save in `.claude/cache/agents/s244/claude-ai-response.md`
3. **Decisione CTO autonoma** basata su ranking:
   - **Se N1 con workaround Python**: applica patch surgicalmente (verifica hunk counts!), commit, test live
   - **Se N4 dominante**: procedi B1 downgrade pjsip 2.15.1 (runbook in plan S243 — vedi sotto sezione B1)
   - **Se N5 dominante**: discuti effort 1-2 sessioni con founder PRIMA di iniziare, non start automatico fine sessione
   - **Se Claude.ai indeciso/raccomanda diagnostica aggiuntiva**: applica diagnostica, NON pivotare a B2

## B1 runbook (downgrade pjsip 2.15.1) — se Claude.ai conferma N4

Plan completo fornito founder S243 (vedi git log per dettagli). Steps:

```bash
# Step 1: pre-flight toolchain iMac
ssh imac "xcode-select -p && clang --version && which libtoolize && which autoconf && which automake"
# Se manca: ssh imac "brew install libtool autoconf automake pkg-config"

# Step 2: backup bundle 2.16-dev
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && cp -r lib/pjsua2 lib/pjsua2.backup-2.16dev-$(date +%Y%m%d)"

# Step 3: clone + checkout 2.15.1
ssh imac "mkdir -p ~/build && cd ~/build && rm -rf pjproject && git clone https://github.com/pjsip/pjproject.git && cd pjproject && git checkout 2.15.1"

# Step 4: configure (flag minimizzati Big Sur)
ssh imac "cd ~/build/pjproject && \
  echo '#define PJ_HAS_SSL_SOCK 0' > pjlib/include/pj/config_site.h && \
  echo '#define PJMEDIA_HAS_VIDEO 0' >> pjlib/include/pj/config_site.h && \
  ./configure --prefix=\$HOME/build/pjproject-install --enable-shared --disable-video --disable-opencore-amr --disable-libwebrtc --disable-libyuv --disable-ssl"

# Step 5: build (~30-45 min)
ssh imac "cd ~/build/pjproject && make dep && make"

# Step 6: SWIG bindings
ssh imac "which swig || brew install swig"
ssh imac "cd ~/build/pjproject/pjsip-apps/src/swig && make && cd python && make"

# Step 7: integrate
ssh imac "cp ~/build/pjproject/pjsip-apps/src/swig/python/pjsua2.py '/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2/pjsua2.py'"
ssh imac "cp ~/build/pjproject/pjsip-apps/src/swig/python/_pjsua2.so '/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2/_pjsua2.so'"

# Step 8: smoke test
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && ./venv/bin/python -c 'import sys, os; sys.path.insert(0, \"lib/pjsua2\"); os.environ[\"DYLD_LIBRARY_PATH\"]=os.path.abspath(\"lib/pjsua2\"); import pjsua2 as pj; ep=pj.Endpoint(); ep.libCreate(); print(\"version:\", ep.libVersion().full); ep.libDestroy(); print(\"OK\")'"

# Step 9: test live S244-B1
ssh imac "lsof -ti:6080 | xargs -r kill -9; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && VOIP_LOCAL_PORT=6080 nohup ./venv/bin/python main.py > /tmp/sara-live-s244-b1.log 2>&1 & echo PID=\$!"
sleep 15
ssh imac "grep 'SIP REGISTERED\|pjsua version' /tmp/sara-live-s244-b1.log"
# Founder chiama 0972536918
ssh imac "tail -100 /tmp/sara-live-s244-b1.log | grep -E 'Incoming|S243|bridge|Assertion|greeting|Aborted'"
```

**Esiti B1**:
- B1-A (VERDE): no assertion, Sara parla → commit + push + chiudi VERDE
- B1-B (SIGABRT identico): bug NON è regressione 2.16-dev → strutturale pjsua2 SWIG director macOS → chiudi GIALLA con plan B2 in S245
- B1-C (errore nuovo): incolla log, diagnostica caso-per-caso
- B1-FAIL toolchain: STOP, NON forzare B2 fine sessione esausta (anti-pattern S159), chiudi GIALLA handoff dettagliato

## Discriminate criteria S244 test live

| Outcome | Verdetto | Next |
|---------|----------|------|
| Sara audible <3s + dialog | Fix Claude.ai OK / B1 OK → VERDE | S245 sprint produzione |
| SIGABRT grp_lock identico | Fix falsificato → analizza ranking | B1 (se non già fatto) o B2 |
| Errore nuovo | Patch ha rotto altro | Revert + diagnose |
| Build toolchain fail (B1) | Sessione GIALLA | Handoff S245 con stato esatto build |

## Vincoli mantenuti

- Zero-cost (#5): no servizi paid, no nuovi acquisti hardware
- Italiano per founder, tecnica in EN
- D-01 VOS DECISIONS.md: 2-tier €497/€897, FLUXION = gestionale + Voice Agent Sara
- D-02 VOS: WA 3314928901 condiviso, persona "Erica Fluxion" solo in body messaggi
- Context budget: `/context` monitor, sopra 50% NO edit schema/migration/CLAUDE.md/HELPDESK.md
- CTO ownership (memoria `feedback_cto_decide_no_review.md`): decido io P0/P1/P2, founder collabora
- Anti-pattern S159: NO B2 switch architetturale fine sessione esausta
- Lezione S236: MAI `f"{exc}"` su `pj.Error` — usare `exc.info(True)` o helper `_pj_error_info()`
- Lezione S243: hunk counts patch Claude.ai possono essere malformati → preferire output sezioni discrete con context unambiguous, fallback Edit manuale

## Stato repo fine S243

- MacBook: `161ecef` master (`fix(S243): defer startTransmit out of onCallMediaState (T1+T1.5+T2)`)
- iMac: sync `161ecef` master
- Pipeline iMac voice-agent: DOWN (PID 37288 abortita da SIGABRT, non killed manualmente)
- Log smoking gun: `.claude/cache/agents/s243/live-test-log-s243.txt`
- Prompt Claude.ai: `.claude/cache/agents/s243/claude-ai-prompt.md`

## Open Q founder pendenti

1. **Tariffa Ehiweb €/mese cliente** (D-03 Open Q #3): TBD, non blocker S244 (deferred a P4 post-Sara-verde)
2. **Output Claude.ai S243 prompt**: founder deve incollare quando pronto all'inizio S244
3. **Backup pjsua2.16-dev**: NON ancora fatto. **Da fare PRIMA di B1**: `ssh imac "cp -r '/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2' '/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2.backup-2.16dev-20260515'"`

## Roadmap aggiornata

**S244 — Sara VoIP fix** (gating hard, ancora):
- Leggi output Claude.ai → decide tra patch surgical / B1 / B2 / diagnostica aggiuntiva
- Test live, verdetto, commit

**S245+ — Sprint produzione** (SOLO post-Sara verde):
- P0 Win MSI unsigned (mercato Italia ~80% Win)
- P1 Sentry free tier verify (2026-05-15 auto-downgrade)
- P2 Sara latency 1330→<800ms (streaming L4_groq→TTS chunked)
- P3 Beta clienti scouting (5-20 manuali, NO automation)
- P4 Ehiweb wizard onboarding

**DEFERRED indefinito** (post-first-paying-customer €497):
- WA outbox SQLite refactor
- Switch Twilio dedicated number
- Landing per-verticale 9 settori
- Video demo Sara per verticale

## Anti-pattern da evitare S244 (lezioni S232-S243)

- MAI `f"{exc}"` su `pj.Error` — usare `exc.info(True)` (lezione S236 permanente)
- MAI assumere thread Python visibile = unico thread coinvolto (S239+S243 hanno mostrato C-thread invisible)
- MAI sovradimensionare architettura pre-product
- MAI lanciare beta su pipeline non validata live
- MAI switch architetturale (B2) fine sessione esausta — handoff dettagliato e ripartire fresco
- MAI applicare patch senza syntax check Python (`python3 -m py_compile`) prima di commit
- MAI commit pre-flight skip — pre-commit hook FLUXION fa type-check + lint
- LEZIONE S243: hunk counts patch Claude.ai possono essere `@@ -343,6 +343,28 @@` mentre il content è 350 righe. Sempre `git apply --check --recount` PRIMA di apply; se fallisce, fallback Edit surgicale.
