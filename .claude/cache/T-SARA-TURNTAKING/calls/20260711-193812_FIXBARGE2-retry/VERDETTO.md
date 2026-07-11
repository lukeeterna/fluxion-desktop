# VERDETTO D1 — FIX-BARGEIN-2 (soglia TX-referenced) — 🟢 VERDE

> Chiamata `-injectat 2500 -echo 0 -dur 16`, UAC loopback `127.0.0.1:15090` (trunk NON toccato).
> `SARA_TEST_CAPTURE=1` su ENTRAMBI i lati (harness + sara3003 su :3003, VOICE_ENGINE=go).
> Fix sotto test: `voip_goengine.py` md5 `c1fac303a4467eefd79ec35970127edf` (MacBook = iMac).
> Call answer 19:38:37.128 · inject +2500ms (~19:38:39.6) · trigger sustain 13f (~260ms).

## D1 — BARGE-IN: 🟢 tutte le sotto-condizioni

### (1) BARGE-IN + clear_tx nella finestra t≈[2.5–5.5]s
```
19:38:39 [voip_goengine] BARGE-IN: rms=13943 thr=2439 floor=12257 (pre=17 frame)
```
Trigger 19:38:39 = ~t+2.8s dopo answer → dentro [2.5–5.5s]. `clear_tx()` invocato nel branch trigger.

### (2) thr DERIVATA DA tx_ref (NON dal floor) — root-cause b2 curata in modo rinforzato
`[RX-MARK]` (~1/s), finestra iniezione:
```
19:38:39 rms=0     tx_ref=0    thr=500  floor=0     stato=LISTENING sustain=0  ← pre-beep nel secondo
19:38:40 rms=13943 tx_ref=6098 thr=2439 floor=12257 stato=LISTENING sustain=0  ← thr=0.4·6098=2439
19:38:41 rms=13943 tx_ref=0    thr=500  floor=12257 stato=LISTENING sustain=0  ← finestra TX drenata
19:38:42 rms=13943 tx_ref=0    thr=500  floor=12257 stato=LISTENING sustain=0
```
**Prova che il fix è load-bearing**: `floor=12257` (l'echo-floor EMA HA inseguito il beep). Con la
vecchia formula `thr=max(500, 2.5·floor)=30642 > rms=13943` → barge NON sarebbe scattato. La nuova
`thr=max(500, 0.4·tx_ref)=2439 < 13943` → barge scatta. Il floor resta SOLO nel marker diagnostico.
Il loop VEDE `rms=13943` (nessun drop su rx_queue).

### (3) TX di Sara si interrompe ≤1s dal trigger (derivato RMS lato-harness)
`rx.wav` harness = TX di Sara ricevuto dall'harness (`harness_timeline.md`):
```
t(s)  rx_rms  injecting
 2.0      0   false
 3.0   1609   true     ← coda greeting (SystemTTS fallback, TX debole rms_max=1609)
 4.0      0   true     ← Sara MUTA
 5.0      0   true
```
Trigger ~19:38:39.9 (t≈2.8s); TX Sara → 0 entro t=4.0s. NB: EdgeTTS ha fallito (afconvert rc=1) →
fallback SystemTTS → greeting a bassa energia (tx_rms lato-Sara 2683). Il barge è comunque scattato:
tx_ref=6098 (picco su finestra 400ms) > soglia base → thr 2439 > eco/silenzio, < beep 13943.

## D5 — Cattura ADDENDUM W su ENTRAMBI i lati (REGOLA #32)
- **Lato-Sara**: `call_20260711-193837_SARA-SIDE.wav` (stereo L=RX / R=TX, rx_rms=6037 tx_rms=2683, 16s @8k).
- **Lato-harness**: `rx.wav` / `tx.wav` / `mix.wav` + `harness_timeline.md`.
- `sara3003_window.log`: finestra adapter (RX-MARK + BARGE-IN + CALL_END).

## ESITO
Opzione (b) emendata RATIFICATA e VERIFICATA: la soglia barge àncora al TX di Sara (`tx_ref = max`
deque 20× `_current_tx_rms` ≈400ms), il floor RX esce dalla formula. Barge scatta anche quando il
floor è avvelenato dal beep (12257) — condizione che nel run precedente (floor=0) non discriminava.
