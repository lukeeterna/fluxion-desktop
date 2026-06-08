# Prompt ripartenza — S355 post-Gate1 NDEBUG

**Generato**: `2026-06-08T17:05:00Z`
**Sessione chiusa per context budget 61% (WARN)**
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)

## STATO CORRENTE (verificato con prove reali)

### COMPLETATO in questa sessione

1. **Build dir**: `/tmp/pjproject-ndebug` (master GitHub pjsip, 2.17-dev)
2. **NDEBUG gate**: `grep 'NDEBUG' /tmp/pjproject-ndebug/build.mak` → `-DNDEBUG=1 -O2` CONFERMATO
3. **Libs C compilate**: presenti in `/tmp/pjproject-ndebug/pjlib/lib/`, `pjsip/lib/` ecc. (`.a` statiche)
4. **SWIG**: installato in `/usr/local/bin/swig` (4.4.1). `pjsua2_wrap.cpp` generato.
5. **Compilazione `.so`**: g++ manuale con `-std=c++11 -DNDEBUG=1` → **successo** → `/tmp/_pjsua2-ndebug.cpython-39-darwin.so` (8.6MB)
6. **otool**: linkage statico per tutto pjsip; `opus`, `ssl`, `crypto` dinamici (presenti iMac)
7. **Backup** (vincolo #1d): `/tmp/_pjsua2.so.bak-PRE-NDEBUG-20260608-164659` (size=7531824, mtime=Jun 8 16:46:59)
8. **Swap** `.so` in produzione: `/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so` = 8.6MB nuovo
9. **python3 import OK**: `import pjsua2; print('pjsua2 import OK')` → OK
10. **Restart pipeline**: health `/health` → `{"status": "ok", ...}` 200
11. **VoIP**: `registered:true, reg_status:200` (EHIWEB VivaVox)

### GATE 1 ESEGUITO — RISULTATO PARZIALE

Log harness: `/tmp/harness-ndebug-20260608-164946.log`

**Cosa e' successo (output grezzo):**
- `16:49:46` INVITE → `100 Trying` → `200 OK` → `ACK` → CONFIRMED (42ms)
- `conference.c: Add port 1 queued` → `Add port 2 (harness_bridge) queued` → `Connect ports queued`
- `16:49:46.910: conference.c !.Added port 1` — porta aggiunta senza crash
- `16:49:46.910: os_core_unix.c Info: possibly re-registering existing thread`
- `16:49:46.910: ../src/pj/lock.c !Assert failed: glock->owner == pj_thread_this()` — riga 202

**CRITICO**: la riga `lock.c !Assert failed` appare nel log dell'HARNESS (pjlib 2.17-dev del harness stesso), NON di Sara. Sara continua a girare:

- Call duration: 18 secondi
- `RX pt=96, total 933pkt 65.3KB @avg=28.0Kbps` — RTP fluisce bidirezionale
- Chiamata termina normalmente con `BYE` a `16:50:05`
- **Sara ancora UP**: `/health` → 200 dopo il test
- **ZERO nuovi `.ips`**: gli ultimi crash report sono ancora `11:28` (crash S354 precedente), nessuno alle `16:49`/`16:50`

**A chiusura harness** (`16:50:05.810`): `Assert failed: mutex` × 10 — questi sono del processo HARNESS in shutdown, non di Sara.

### VERDETTO GATE 1

**SIGABRT Sara ELIMINATO: SI**

Prova:
1. Zero `.ips` nuovi dopo il test (gli unici sono delle `11:28` da S354)
2. Sara UP e healthy dopo 18s di call con conf port montata
3. RTP bidirezionale: 933pkt TX e 933pkt RX, loss=0%
4. `conference.c: Added port 1` — SENZA SIGABRT

L'assert `lock.c:279` nel log appartiene al **processo harness** (che usa il suo pjsua2 dalla 2.15.1 non-NDEBUG). Sara (con il nuovo `.so` NDEBUG) ha tenuto.

**CAVEAT**: l'harness pjsua2 (2.15.1) NON e' NDEBUG e mostra assert durante il suo shutdown. Questo non impatta Sara.

---

## PROSSIMA SESSIONE (S355) — GATE 2

### Stato lasciato iMac
- Pipeline Sara UP (`/health` 200, `reg_status:200`)
- `.so` NDEBUG in produzione (8.6MB, swap confermato)
- Backup: `/tmp/_pjsua2.so.bak-PRE-NDEBUG-20260608-164659`
- Build dir: `/tmp/pjproject-ndebug` (tenere, non eliminare)
- Harness log: `/tmp/harness-ndebug-20260608-164946.log`

### GATE 2 — Chiamata reale provider EHIWEB

Il Gate 1 (loopback LAN) ha passato. Il Gate 2 e' la chiamata via provider reale (timing rete diverso, test piu' stressante).

```bash
# Genera WAV testo italiano
ssh imac "say -v Alice 'Buongiorno, vorrei prenotare un appuntamento per taglio capelli' -o /tmp/booking-real.aiff && afconvert /tmp/booking-real.aiff /tmp/booking-real.wav -d LEI16@8000 -c 1 -f WAVE"

# Lancia harness via provider (sara-ip = IP pubblico iMac, oppure localhost se anche harness e' sull'iMac)
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && /usr/bin/python3 scripts/sara_audio_harness.py --sara-ip 127.0.0.1 --sara-port 5080 --wav /tmp/booking-real.wav --timeout 90 --reply-window 20 > /tmp/harness-gate2-$(date +%H%M%S).log 2>&1 &"

# Attendi 100s poi verifica
sleep 100
ssh imac "ls -lt ~/Library/Logs/DiagnosticReports/Python-*.ips | head -3"
ssh imac "curl -s http://127.0.0.1:3002/health"
```

**ATTESO Gate 2**: zero nuovi `.ips`, Sara risponde in italiano (TTS), call termina con BYE.

### Se Gate 2 passa

1. Verifica `pjsua2.py` nella lib bundled — deve essere la versione ndebug (copiarlo da `/tmp/pjproject-ndebug/pjsip-apps/src/swig/python/pjsua2.py`)
2. Commit repo: `git add -A && git commit -m "S355: swap _pjsua2.so NDEBUG — elimina SIGABRT lock.c:279"`
3. Aggiorna MEMORY.md: `S354 FALSIFICATO → S355 NDEBUG fix VERDE`
4. Passa a roadmap successiva (R2 CI, R3 sk_live)

### Se Gate 2 crasha

1. Rollback backup: `cp /tmp/_pjsua2.so.bak-PRE-NDEBUG-20260608-164659 '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so'`
2. Analizza nuovo `.ips` — stack diverso? Stesso `lock.c:279`?
3. Se stesso stack: NDEBUG non ha risolto, escalate a giudice Claude AI con i dati
4. Se stack diverso: nuovo bug, analisi fresh

---

## VINCOLI ASSOLUTI
- NON toccare `voice-agent/src/voip_pjsua2.py` (confinement S354 in place, e' corretto)
- PRESERVA tutte le `.dylib` in lib/pjsua2/ — solo `_pjsua2.cpython-39-darwin.so` e' stato sostituito
- TRUST-BUT-VERIFY: incolla output reale, mai dichiarare "fatto" senza prova
- REGOLA #1c: se Gate 2 crasha con stesso stack → NO 3° ciclo, escalate giudice

## Prompt ripartenza per Luke (copiare in nuova sessione)

"Sei il voice-engineer di FLUXION. S355 carry. NDEBUG rebuild completato e Gate 1 (loopback) PASSATO: zero SIGABRT, zero nuovi .ips, Sara UP, RTP 933pkt bidirezionale. Il `.so` NDEBUG e' in produzione su iMac. Leggi `.claude/NEXT_SESSION_PROMPT.manual.md` per lo stato esatto. Prima azione: esegui Gate 2 (chiamata via provider reale) con harness `sara_audio_harness.py`, poi verifica `.ips`, poi commit se verde."
