# FLUXION — Handoff Sessione 152 → 153 (2026-04-14)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline porta 3002 | SIP: 0972536918

---

## COMPLETATO SESSIONE 152

### 1. Sales Agent CTO Validation (3 agenti comparati)
- Agent 1 (ARGOS): A- (92/100) — battle-tested, 122MB DB
- Agent 2 (New): C+ (72/100) — codice pulito ma design debole
- Agent 3 (Enterprise): B+ (85/100 post-fix) — migliore design, S.A.C.P., tutte 6 Passe
- Fondatore ha completato Sales Agent Enterprise (Passe 1-6), bug fixati

### 2. Fix gommista service mismatch (b8b30cf)
- "cambio" regex negative lookahead + synonym cross-contamination filter
- E2E: "vorrei un cambio gomme" → "Cambio gomme stagionale, per quale giorno?" PASS

### 3. F1-3b Adaptive Silence VAD hookup (a923b84)
- FluxionVAD.update_silence_ms() dynamic (300-1200ms)
- Orchestrator → VAD sessions wired bidirezionalmente

### 4. VoIP Traccar conflict fix
- Traccar GPS (Java) occupava TCP:5080 → LaunchAgent disabilitato permanentemente
- plist rinominato .DISABLED

### 5. macOS DMG Build SUCCESS
- Fluxion_1.0.0_x64.dmg (69MB) compilato su iMac
- Universal Binary: non fattibile (sidecar ARM64 manca), x86_64 funziona via Rosetta 2

### 6. Sprint 6 — Pagina installazione
- `landing/come-installare.html` gia' completa (490 righe, macOS + Windows)

---

## BUG CRITICO APERTO — SARA VOIP NON RISPONDE

### Problema
pjsua2 `reinv_timer_cb()` causa deadlock mutex su OGNI chiamata in ingresso.
Il telefono squilla, Sara risponde 200 OK, ma il deadlock impedisce il media setup.
La chiamata cade e va alla segreteria Vodafone.

### Tentativi S152 (tutti falliti)
1. **Risposta immediata 200 OK** da onIncomingCall → deadlock dopo 2s
2. **Thread separato + 1s delay** → deadlock identico
3. **Session timer INACTIVE** → deadlock persiste (timer interno non disattivabile)
4. **timerSessExpiresSec=0** → assertion crash `sess_expires >= min_se`
5. **150ms delay** → deadlock ancora presente

### Root Cause
`reinv_timer_cb()` e' un timer interno di pjsua2 che scatta durante il processing
del 200 OK e compete per il mutex. NON e' controllabile via config.
E' un bug noto di pjsua2 2.16-dev su macOS x86_64.

### Approcci da provare in S153
1. **Aggiornare pjsua2** — verificare se versioni piu' recenti fixano il deadlock
2. **Compilare pjsip con `--disable-session-timer`** — disabilita a livello C
3. **Usare pjsua (CLI) invece di pjsua2 (Python binding)** — approccio diverso
4. **SIP proxy** — Asterisk/FreeSWITCH locale che fa da intermediario
5. **Aumentare mutex timeout** di pjsua2 (`PJ_MUTEX_LOCK_TIMEOUT`)

### Log chiave
```
Incoming call from: <sip:3281536308@79.98.45.133>
Answering call with 200 OK
Timed-out trying to acquire PJSUA mutex (possibly system has deadlocked) in reinv_timer_cb()
```

---

## STATO GIT
```
Branch: master | HEAD: 7728a88
Commits S152:
  b8b30cf fix(S152): gommista service mismatch
  a923b84 feat(S152): F1-3b adaptive silence VAD
  218baa0 fix(S152): VoIP deadlock — onCallState separate thread (non risolve)
  185176c fix(S152): VoIP answer immediately (non risolve)
  2291c6d fix(S152): disable SIP session timers (assertion crash)
  3b50e83 fix(S152): valid min_se/expires values
  7728a88 fix(S152): 150ms delayed 200 OK (deadlock persiste)
  61a1ab4 docs(S152): HANDOFF + MEMORY
```

---

## PROSSIMA SESSIONE (153) — FRAMEWORK

### PRIORITA' 1: FIX VOIP SARA (BLOCCANTE)
```
STEP 1: /gsd:debug → Investigazione sistematica deadlock pjsua2
STEP 2: Deep research pjsua2 reinv_timer_cb fix 2026
STEP 3: Implementa fix (o alternativa: Asterisk local proxy)
STEP 4: Test chiamata live 0972536918
```

### PRIORITA' 2: Sprint 6 restante
- Windows MSI build (cross-compile o VM)
- Content repurposing (6.1)

### PRIORITA' 3: Sales Agent deploy
- Fondatore gestisce, supporto tecnico se richiesto

### Suite da caricare
```
SKILLS:     /fluxion-voice-agent, /fluxion-service-rules, /deep-research
AGENTS:     voice/sara-fsm-architect, engineering/voice-engineer, engineering/debugger
MCP:        context7 (docs pjsua2), WebSearch (bug reports pjsua2)
```

### Prompt di ripartenza S153
```
Leggi HANDOFF.md. Sessione 153.
PRIORITA' 1: Fix VoIP Sara — pjsua2 reinv_timer_cb deadlock.
Il telefono squilla, Sara risponde 200 OK, ma il mutex deadlock
impedisce il media setup. 5 tentativi in S152 tutti falliti.
Serve deep research su pjsua2 mutex deadlock + soluzione alternativa.
Usa /gsd:debug per investigazione sistematica.
```
