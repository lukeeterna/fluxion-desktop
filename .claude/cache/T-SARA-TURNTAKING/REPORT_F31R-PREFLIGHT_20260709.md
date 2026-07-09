# REPORT T-SARA-TURNTAKING — F3.1-R PREFLIGHT + defer mutazione (context ceiling)

Data: 2026-07-09 · Gate label (#1c): **IDLE/preflight** · Verdetto: 🟢 **FASE 0 VERDE** (baseline verificata, discordanze loggate, restore stampato, uac.go allineato) · 🟡 **FASE 1-R NON avviata** (ceiling context mutante) · Mutazioni codice: **ZERO** (solo cleanup git-index + gitignore)

> Questo report copre anche il **C1 mancato della F3.1** (sessione df3fda5 non lo produsse).

## 1. FASE 0 — apertura (eseguita, read-only)
- **A1**: letti HANDOFF.md (1-40) + REPORT_FASE3.0 §5 + REPORT_FASE1 §5/6. Spec A3 e refactor uac.go acquisite, nessuna contraddizione col mandato.
- **A2 context**: partenza reale ≈ **52-54%** (NON ~38%). Il boot di questa sessione è genuinamente pesante (CLAUDE.md globale+progetto ~550 righe, 6 rules, MEMORY.md ~180 righe, liste agenti/skill molto lunghe). Applicata REGOLA #27 con tracking onesto: l'inflazione RAW qui è minima perché il boot ha davvero consumato ~100k. → sopra il ceiling mutante ~45-50%.
- **A3 baseline (prova live, ssh imac)**:
  - PID **82763** `main.py --port 3002` (unico), cwd `/Volumes/MacSSD - Dati/FLUXION/voice-agent`, `VOICE_ENGINE` non settato → default pjsua2.
  - `/health` ok v2.1.0; `/voip/status` → `registered:true, reg_status:200, engine:"pjsua2", rtp_active:false`.
  - **3003 DOWN** (no response); **zero orfani** engine_darwin/gospike; `calls/` vuota senza flag (default-OFF).

## 2. RESTORE COMMAND (da ps/cwd reali, stampato prima di ogni atto)
```
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && env -u VOICE_ENGINE nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 &'
```
Non consumato: 82763 vivo, mai toccato. FASE 1-2 previste su istanza SEPARATA 3003 (VOICE_ENGINE=go, SIP dummy 127.0.0.1) → 3002/trunk mai toccati.

## 3. DISCORDANZE (premessa | fatto | correzione)
- **D#1 working dir** | `/Volumes/MacSSD - Dati/FLUXION` | sul MacBook (sessione) esiste solo `/Volumes/MontereyT7/FLUXION`; `MacSSD - Dati` è path **iMac** | il repo git vive su MacBook, harness/Sara/3003 su iMac via ssh. Nessun blocco.
- **D#2 path uac.go** | `tools/gospike/uac.go` | reale = `voice-agent/tools/gospike/uac.go` | uso path reale.
- **D#3 case FLUXION/fluxion** | mandato «MAIUSCOLO» vs report FASE1 «fluxion» | APFS case-insensitive: stessa dir | nessuna azione.

## 4. Allineamento harness (prova)
- uac.go MacBook == iMac: md5 `850d32a904ee1fbc6c85eb3c2021fc2e`, 10861 B (entrambi). Baseline pulita per il refactor.
- `.gitignore` gospike: `gospike_darwin_amd64`, `gospike_windows_amd64.exe`, `*.wav` (+ aggiunto `*.bak-*` questa sessione).

## 5. Cleanup C3 (non-mutante, git-reversibile)
- `git rm --cached voice-agent/tools/gospike/uac.go.bak-PRE-F31-20260709-170519` (finito in df3fda5) → file su disco INTATTO (3889 B).
- Aggiunto `*.bak-*` a `.gitignore` gospike per non ri-tracciare i backup #1d.

## 6. Perché la FASE 1-R è rinviata (decisione CTO, non diplomatica #9)
FASE 1-R è mutante sostanziosa (rewrite Go RX-goroutine + TX-ticker, build darwin **e** cross windows/amd64 CGO_ENABLED=0, smoke 30s su 3003, verifica WAV, con iterazione su errori). Avviarla a ~54% reale → rischio stop a ~60% **a metà mutazione** = uac.go sporco su 2 macchine, harness (veicolo del test A3) corrotto. Asimmetria netta (#1b/#6/#7): mutazione sporca ≫ rinvio pulito. La FASE 3 del mandato impone già chiusura >50%. Chiudo a confine di fase pulito, non stato PARTIAL a metà edit.

## 7. Refactor F3.1-R — spec pronta per sessione fresca (già in HANDOFF + REPORT_FASE3.0 §5 + FASE1 §5)
Premessa cieca (bug df3fda5): `runUAC` single-loop, `dec.Read()` blocca sul silenzio → `-dur` inefficace, mai CALL_END, `calls/` vuota. Refactor:
- **RX in goroutine**: aggiorna `echoBuf` sotto `sync.Mutex`; `cancelCall()` su read-error/EOF. Re-add import `sync`.
- **TX su `time.NewTicker(20ms)`**: ogni tick frame 320B = echo(ultimi 320B RX × gain da `-echo` dB) + inject(cursore `utterPCM`, attivo da `-injectat`); check `callCtx.Done()` per tick.
- **-dur scaduto** → BYE pulito → CALL_END → capture finalizzata.
- Build darwin OK + `GOOS=windows GOARCH=amd64 CGO_ENABLED=0` OK.
- Smoke D1 su 3003 (VOICE_ENGINE=go, VOIP_SIP_SERVER=127.0.0.1 dummy — trunk mai toccato), `SARA_TEST_CAPTURE=1`, `-dur 30`: harness termina solo, WAV prodotto in `.claude/cache/T-SARA-TURNTAKING/calls/`.

## 8. Stato lasciato
- Sara **default pjsua2 PID 82763** su 3002, health ok, `reg_status:200`, INVARIATA (zero edit codice/runtime). Restore point intatto.
- 3003 DOWN, zero orfani, `calls/` vuota (default-OFF).
- uac.go/main.go harness INTATTI (md5 invariato). Backup pre-F31 `.bak-PRE-F31-20260709-170519` su disco (untracked).
