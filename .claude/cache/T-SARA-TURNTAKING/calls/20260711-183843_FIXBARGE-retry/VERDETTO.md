# VERDETTO D1 — FIX BARGE-IN (retry post echo-floor decoupling) — 🟢 VERDE

> Chiamata identica a b1/b2: `-injectat 2500 -echo 0 -dur 16`, UAC loopback su 127.0.0.1:15090
> (trunk non toccato). `SARA_TEST_CAPTURE=1` su ENTRAMBI i lati (harness + main.py --port 3003).
> Fix sotto test: `voip_goengine.py` md5 `6c8c04c6481128b7d94cf062cfac6af3` (MacBook=iMac).

## D1 — BARGE-IN: 🟢 tutte e tre le sotto-condizioni soddisfatte

### (1) BARGE-IN log + clear_tx nella finestra t≈[2.5–5.5]s
```
18:38:46 [voip_goengine] BARGE-IN: rms=13943 thr=500 floor=0 (pre=17 frame)
```
Call start 18:38:43, inject a +2500ms → trigger 18:38:46 (≈+3s) dentro [2.5–5.5s].
`clear_tx()` invocato nel branch trigger (svuota TX + stop invio + fine grace).

### (2) Marker RX: `_echo_floor` NON insegue il beep (root-cause b2 curata)
`[RX-MARK]` (~1/s) nella finestra iniezione:
```
18:38:45 state=LISTENING rms=0     floor=0 thr=500 sustain=0   ← pre-inject
18:38:46 state=LISTENING rms=13943 floor=0 thr=500 sustain=0   ← inject: floor RESTA 0
18:38:47 state=LISTENING rms=13943 floor=0 thr=500 sustain=0
18:38:48 state=LISTENING rms=13943 floor=0 thr=500 sustain=0
```
Il loop VEDE rms=13943 (ROSSO-MARKER falsificato: nessun drop su rx_queue). Il floor resta **0**
(≲2× pre-inject=0) mentre rms≈14000 → `thr=max(500, 2.5·floor)` resta base **500** → SUSTAIN=13
raggiunto → BARGE-IN. In b1/b2 il floor inseguiva il beep (floor 0→6663 in 4 frame, thr>rms, reset).

### (3) TX di Sara si interrompe ≤1s dal trigger (derivato RMS lato-harness, wall-clock 1/s)
`rx.wav` harness = TX di Sara ricevuto dall'harness:
```
t(s)  rx_rms  injecting
 3.0   2468   true     ← trigger ~qui (18:38:46)
 4.0      0   true     ← Sara MUTA ≤1s dopo il trigger
 5.0      0   true
 ...
10.0   1605   false    ← Sara riprende: risposta al "parlato" (beep→STT)
```
b1/b2: Sara continuava per tutta la finestra (1876/2949/2538/2832). Ora si ferma a t=4.0s.

## D3 — Cattura ADDENDUM W su ENTRAMBI i lati (REGOLA #32)
- **Lato-Sara**: `call_20260711-183843_SARA-SIDE.wav` (stereo L=RX beep / R=TX Sara), rx_rms=6037
  tx_rms=3143, 16.0s @8k. RX_L beep presente 9859→13943 in finestra 2-5s (baseline 0 fuori) → prova
  che il beep raggiunge l'RX dell'adapter di Sara. (NB: assi RX/TX del WAV NON wall-clock-allineati —
  due stream concatenati+zero-pad; la prova temporale di (3) è il derivato harness, non il TX_R del WAV.)
- **Lato-harness**: `rx.wav`/`tx.wav`/`mix.wav` + `harness_timeline.md`.
- `sara3003_window.log`: finestra log adapter (RX-MARK + BARGE-IN + capture).

## ESITO
- b2 CURATO: il disaccoppiamento echo-floor (update solo se `rms<=thr` fuori warm-up) + warm-up ~180ms
  post-ingresso SPEAKING → il beep non avvelena più la propria soglia → barge scatta.
- Osservabilità RX (marker 1/s) chiude la sotto-distinzione "loop VAD vs drop rx_queue": il loop VAD
  VEDE i frame (rms=13943 a RX-MARK) → NON droppati su rx_queue.
