# REPORT SBLOCCO-A3 — T-SARA-TURNTAKING (sessione 2026-07-10-e)

> Rito di chiusura C1. Verdetto + prove grezze + discordanze + file/backup + restore.
> Stato verificato ALLA FONTE dopo compaction (disco vince sulla sintesi).

## VERDETTO

- **FASE 1 (SBLOCCO BUILD) 🟢 VERDE** — blocco di 2 sessioni ROTTO via **PROVA A0** (build in-place su iMac).
- **D1 (smoke live 3003) 🟢 VERDE** — harness termina da solo a `-dur`, capture WAV non vuoti, CALL_END pulito.
- **FASE 2 GATE A3: 1/5 🟢 (ECO)**, 4/5 🔴 **BLOCKED-ON rig-stability** (barge-in/filler/no-hangup/silenzio).
- **FASE 4 (B3 founder) — NON eseguita** (checkpoint context + rig instabile).

## PROVE GREZZE

### FASE 1 — PROVA A0 (build in-place iMac, go.mod INTATTO)
- iMac Monterey 12.7.4: `~/sdk/go/bin/go version` → **`go version go1.26.4 darwin/amd64`** (user-space, non di sistema).
- Build con `GOTOOLCHAIN=local CGO_ENABLED=0`, **go.mod NON toccato** (`go 1.26.4` committato resta).
- Binari prodotti su iMac (`tools/gospike/`):
  - `gospike_darwin_amd64` → **11759568 B** (EXIT=0)
  - `gospike_windows_amd64.exe` → **11606016 B** (cross-compile EXIT=0)
- **PROVA A (fallback)** = abbassare go.mod a `go 1.24` sul MacBook: NON necessaria (A0 ha funzionato). Resta documentata come fallback.

### D1 — smoke port 3003
- Dir: `.claude/cache/T-SARA-TURNTAKING/calls/20260710-215045_D1-smoke/`
  - `rx.wav` 208364 B · `tx.wav` 480044 B · `mix.wav` 960044 B · `harness_timeline.md` 1087 B
- Harness termina da solo esattamente a `-dur` (bug "non termina" fixato nel refactor uac.go della sessione -c). CALL_END pulito, capture non vuoto.

### FASE 2 A3 — ECO 🟢 (1/5)
- Dir: `20260710-215842_A3-eco/` (rx 466604 B) + re-run `20260710-220352_A3-eco/` (rx 225964 B).
- Scenario: `-echo -15` SENZA inject (`-injectat 9999000` per evitare la contaminazione del beep di default a uac.go:97-99).
- Esito: Sara **NON trascrive** l'eco a -15 dB della propria greeting → zero STT/intent spurii sul path Go. **VERDE.**

### FASE 2 A3 — BARGE-IN 🔴 inconcludente
- Dir: `20260710-220618_A3-bargein/` (rx 400044 B, tx 400044 B).
- Confound: l'engine Go crasha sul registrar dummy → esito non isolabile. **NON conta come pass.**

## BLOCCO STRUTTURALE (root cause del 4/5 mancante)
- Il go-engine (`engine_darwin_amd64`, spawnato da `voip_goengine.py`) su registrar **dummy** `127.0.0.1` va in `REGISTER ... Timer_B timed out` → `exit rc=1` → restart → `bind: address already in use` su 5090, ciclo ~ogni 1–2 min.
- NON fixabile senza (a) modificare l'engine (VIETATO), o (b) aggiungere un registrar SIP locale al rig di test.
- Finestra utile stimata ~90 s tra un crash e l'altro → insufficiente per 4 scenari stabili back-to-back.
- Trunk EHIWEB **MAI toccato** (vincolo). A3 gira solo su 3003 localhost.

## DISCORDANZE / CONTRADDIZIONI APERTE
1. Handoff -c diceva "PROVA A = abbassare go.mod a 1.24 sul MacBook". **Superata**: A0 (build su iMac, go.mod intatto) è preferibile — zero mutazione go.mod, zero rischio feature-loss diago/sipgo. A resta fallback solo se iMac indisponibile.
2. Open-question -c "engine Go child prebuilt separato dal harness?" → **CONFERMATO**: `engine_darwin_amd64` (con flag `-bridge`) è separato dal harness gospike (UAC test client). Due binari distinti.
3. 4/5 A3 non completati: NON è un fallimento di Sara, è instabilità del **rig di test** (dummy registrar). Da distinguere nel prossimo giro.

## FILE / BACKUP
- iMac backup pre-sync: `tools/gospike/uac.go.bak-PRE-A0SYNC-20260710-213819` (10861 B, md5 850d32a9…).
- Capture durevoli (MacBook, committati): `.claude/cache/T-SARA-TURNTAKING/calls/{20260710-215045_D1-smoke, 20260710-215842_A3-eco, 20260710-220352_A3-eco, 20260710-220618_A3-bargein}/`.
- `tools/VectCutAPI` = modifica pre-esistente NON correlata, NON toccata in questa sessione.

## STATO FINALE VERIFICATO (post-teardown)
- **3002 DEFAULT INTATTO**: `curl 127.0.0.1:3002/api/voice/voip/status` → `running:true, registered:true, reg_status:200, username:0972536918, server:sip.vivavox.it, engine:"pjsua2"`. PID **82763** unico.
- **3003 DOWN** · **zero orfani** `engine_darwin_amd64 -port 5090`.

## RESTORE (se 3002 dovesse cadere)
```
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &"
```

## PROSSIMO PASSO (boot fresco)
1. Stabilizzare il rig A3: registrar SIP locale (es. `sipp -sn uas` o mini-UAS) su 127.0.0.1 così l'engine registra senza Timer_B → finestra stabile per i 4 scenari residui.
2. Completare A3 5/5 (barge-in, filler ZERO-bank, no-hangup [BLOCKED-ON se non riproducibile in harness], silenzio con `-dur ≥50s` per superare il timer idle Sara 40s).
3. Solo dopo 5/5 con prove → FASE 4 GATE B3 (chiamata reale DID 0972536918, finestra founder, context ≤50%).
