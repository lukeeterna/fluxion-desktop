# CARRY S356 — FIX SARA SIGABRT = REBUILD pjproject NDEBUG. Diagnosi CHIUSA e VERIFICATA. Resta solo esecuzione build.

> **SVOLTA S355**: il FORK A(downgrade 2.15.1)-vs-B(Asterisk ARI) era un FALSO BINARIO. Il crash `lock.c:279` NON è una race strutturale: è un **`pj_assert` del build di DEFAULT di pjproject** che diventa NO-OP sotto `NDEBUG`. Fix = rebuild del pjproject **ATTUALE (2.16-dev)** con `CFLAGS="-DNDEBUG=1"`. Nessun downgrade, nessun PBX.

## ⚠️ PRIMA AZIONE S356
1. Pre-flight SIP: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → atteso `reg_status:200` (era 200 a S355). Se 403 → BLOCKED-ON EHIWEB, non re-diagnosticare.
2. **DELEGA il build a `voice-engineer` FOREGROUND** (REGOLA #27: background = no Bash). Vedi WORK ORDER sotto.
3. **META-CRITICO (REGOLA #27 / S351)**: l'hook VOS context-budget inietta nel subagent la % RAW gonfiata del MAIN → l'agente si auto-aborta ("76%"/"80%") pur avendo finestra fresca (a S355 l'agente aveva ~29% reale). Mitigazione: (a) spawna l'agente build SUBITO con main a basso contesto; (b) istruisci esplicitamente l'agente a IGNORARE quel numero (evidenza misurata = sua finestra è fresca); (c) se serve, `CLAUDE_BYPASS_CTX_GATE=1` per la sessione build.

## DIAGNOSI VERIFICATA (NON ri-derivare, NON riaprire il FORK)
- Crash signature thread `clock`: `clock_callback → get_frame → grp_lock_release → __assert_rtn (lock.c:279)`. Crashano sia Sara sia l'harness, stack identico (evidenza `.ips` S354).
- `pj_assert(expr)` → `assert(expr)` → **no-op sotto `NDEBUG`**. Fonte AUTOREVOLE (Asterisk docs, verificata via WebSearch S355): *"The default configuration of pjproject enables 'assert' functions which can cause Asterisk to crash unexpectedly. To disable the asserts, set NDEBUG to 1"* via `./configure CFLAGS="-DNDEBUG=1"` o `config_site.h` (`#define NDEBUG 1`). Asterisk (l'opzione B) builda pjproject ESATTAMENTE così per non crashare su questa classe di assert.
- 2.15.1 NON risolve (premessa falsificata 2x dal giudice: conf op già async + stesso group lock). 2.15.1 = MORTO, non riaprire.
- Il confinement S354 è CORRETTO e va TENUTO (`voip_pjsua2.py`): non è stato inutile, ha spostato il crash sull'unico residuo C-side, rendendo leggibile che era un assert. NON toccarlo.

## FATTI SCOPERTI S355 (STEP 0 dell'agente, già verificati — riparti da qui)
- Modulo Python da sostituire: **`/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so`**
- Interprete pipeline: **`/usr/bin/python3`** (cpython 3.9)
- **PJPROJECT_ROOT NON ESISTE PIÙ** sull'iMac (source tree rimossa post-build). Indizio versione dal backup `pjsua2.backup-2.16dev-20260515` → **2.16-dev**. → serve `git clone` fresh.

## WORK ORDER S356 (consegna a voice-engineer foreground)
Obiettivo: ricostruire pjproject 2.16-dev + binding SWIG pjsua2 con `-DNDEBUG=1` e sostituire SOLO il `.so`. Ogni claim = output grezzo incollato (trust-but-verify, lezione S354).

0. **Identità ABI del `.so` attuale**: `ssh imac "otool -L '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so'"` → vedere se linka STATICAMENTE (allora basta swap del `.so`) o DINAMICAMENTE `libpjsip.dylib`/`libpjmedia.dylib` ecc. (allora vanno ricostruiti/sostituiti anche quelli). `strings` sul `.so`/dylib per confermare versione esatta pjproject.
1. **Backup (REGOLA #1d)**: `cp` del `_pjsua2.cpython-39-darwin.so` attuale in `/tmp/_pjsua2.so.bak-PRE-NDEBUG-<ts>` + `stat` (size>0). Rollback = ricopiare il backup.
2. **Clone**: `git clone https://github.com/pjsip/pjproject` (o `asterisk/pjproject`), `git checkout` al tag/commit 2.16-dev corrispondente (verifica con la versione da STEP 0).
3. **Configure NDEBUG + Big Sur no-AVX2**: `./configure CFLAGS="-DNDEBUG=1 <flag no-AVX2/no-video coerenti col build originale>"`. (Source originale persa → ricostruisci config minimale: tipicamente `--disable-video`, disabilitazioni codec pesanti; deduci le dipendenze dinamiche da `otool -L` STEP 0). In alternativa più robusta: `#define NDEBUG 1` in `pjlib/include/pj/config_site.h` PRIMA di configure.
4. `make dep && make`.
5. **GATE BUILD**: `grep -- '-DNDEBUG' build.mak` → DEVE comparire. Se vuoto → STOP.
6. **SWIG python**: `cd pjsip-apps/src/swig && make python`. Trova il nuovo `_pjsua2*.so` prodotto.
7. **Swap**: sostituisci il `.so` in `voice-agent/lib/pjsua2/` col nuovo (+ eventuali dylib se linkaggio dinamico da STEP 0). Backup-first già fatto STEP 1.
8. **Restart pipeline**: kill processo + `main.py --port 3002`, verifica `/health` 200 + `reg_status:200`.
9. **GATE 1 (loopback = timing peggiore)**: `voice-agent/scripts/sara_audio_harness.py` (WAV PCM16 8kHz mono `/tmp/book.wav`). ATTESO: INVITE→200 OK→CONFIRMED→RTP>0 byte, `S243 T1: Audio bridge established`, **ZERO SIGABRT**, zero `lock.c:279`. VERIFICA: `ls -lt ~/Library/Logs/DiagnosticReports/Python-*.ips | head` → NESSUN nuovo crash con ts del run. Incolla output harness + check .ips.
10. ROLLBACK se Gate 1 crasha: ricopia `/tmp/_pjsua2.so.bak-PRE-NDEBUG-<ts>`, riavvia.

## GATE 2 (DOPO Gate 1 verde — falsifica "assert spurio", REGOLA #1b)
NDEBUG spegne TUTTI gli assert, anche quelli che catturano bug veri. L'assert qui è quasi certamente spurio (pattern async legittimo, mutex pthread sotto regge — per questo Asterisk lo disabilita di default), MA va dimostrato sotto carico:
- 2° account VivaVox autenticato (€0, già raccomandato) → chiamate inbound back-to-back/sovrapposte.
- Atteso: nessun crash random / double-free (cfr pjproject issue #2527 su `pj_grp_lock_release` sotto carico). Se sotto stress spunta corruzione → race VERA → SOLO allora escala a stable tag (MAI 2.15.1) o Asterisk. Altrimenti: gate Sara CHIUSO a €0, zero rework.

## STATO CODICE / FILE
- `voip_pjsua2.py` iMac: confinement S354 IN PLACE = TIENILO. Backup `voip_pjsua2.py.bak-PRE-S354-20260608-111954` (58322B).
- `sara_audio_harness.py` iMac: patchato confinement S354. Backup `.bak-PRE-S354-20260608-112257` (17749B).
- Repo MacBook divergente da iMac (S352-guard) → allinea/committa DOPO Gate 1 verde.
- Pre-flight S355: `reg_status:200`, account `0972536918`@`sip.vivavox.it`, EHIWEB UP.

## CONTESTO PRODOTTO
EHIWEB/VivaVox = carrier su cui ogni cliente FLUXION ospiterà Sara. Path inbound-answer+media DEVE essere crash-proof. Gate vendita REGOLA #21.

## Carry residui (dopo gate Sara)
- **R2**: CI `release-full.yml` ROTTO. Prima azione: `gh run view 25328286560 --log-failed`.
- **R3**: E-3 sk_live (Stripe live key).
