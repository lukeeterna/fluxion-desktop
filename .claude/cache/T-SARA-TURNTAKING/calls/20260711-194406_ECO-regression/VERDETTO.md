# VERDETTO D2 — ECO REGRESSION (-echo -15dB, no inject) — 🟢 VERDE

> Chiamata `-echo -15 -injectat 999999 (=no inject) -dur 16`, UAC loopback `127.0.0.1:15090`
> (trunk NON toccato). `SARA_TEST_CAPTURE=1` entrambi i lati. Fix md5 `c1fac303…` (MacBook=iMac).
> Call answer ~19:44:06. rms_max eco lato-harness = 3842; SARA-side rx_rms=363.

## D2 — 🟢 ZERO trigger barge E ZERO trascrizione STT dall'eco

### (1) ZERO barge nella finestra ECO
`grep BARGE-IN` sul log copre SOLO il vecchio D1 (19:38:39). Nessun BARGE-IN in 19:44:06–22.
`sustain` resta **0** per tutta la finestra SPEAKING (`sara3003_window.log`).

### (2) Perché non scatta — thr ancorata al TX rigetta l'eco (∝ TX)
`[RX-MARK]` durante SPEAKING (eco -15dB della greeting, no inject):
```
t         rms   tx_ref  thr    floor  stato     sustain
19:44:07  1642  9217    3687   787    SPEAKING  0
19:44:08     0  4053    1621   119    SPEAKING  0
19:44:10   517  7272    2909   699    SPEAKING  0
19:44:11   104  4827    1931   346    SPEAKING  0
19:44:13  1349  7575    3030   237    SPEAKING  0
19:44:14   245  4035    1614   345    SPEAKING  0
```
I picchi eco (max 1642) sono SEMPRE < `thr = 0.4·tx_ref` (1614–3687). Nel run ROSSO precedente
l'eco -15dB (picchi 577–964) superava la soglia base 500 perché il floor non poteva tracciarli;
ora la soglia àncora al TX di Sara (tx_ref 4000–9200) → thr 1600–3700 >> eco → sustain mai incrementa.
`floor` (787/119/699/237) è basso ma IRRILEVANTE (fuori formula).

### (3) ZERO trascrizione STT
Nessuna riga `input=` / `intent` / STT nella finestra: senza barge, il branch SPEAKING fa `continue`,
l'RX non entra mai in STT (nessun forward del ring). Nel run rosso l'eco produceva `input='Salute!'`
intent=CORTESIA (via falso barge → forward). Qui: nessun falso barge → nessun forward → nessun turno NLU.

## D5 — Cattura ADDENDUM W (REGOLA #32)
- **Lato-Sara**: `call_20260711-194406_SARA-SIDE.wav` (rx_rms=363 = eco basso, tx_rms=2843, ~16s).
- **Lato-harness**: `rx.wav` / `tx.wav` / `mix.wav` + `harness_timeline.md`.
- `sara3003_window.log`: finestra adapter (RX-MARK SPEAKING con eco rigettato).

## ESITO
La tensione di design del run rosso (eco > soglia base fissa 500, floor bloccato) è RISOLTA: la soglia
TX-referenced separa l'eco-di-linea (∝ energia TX, rigettato) dal barge reale (D1 beep 13943, accettato).
Nessun ROLLBACK. Fix confermato su ENTRAMBE le done-condition D1 + D2.
