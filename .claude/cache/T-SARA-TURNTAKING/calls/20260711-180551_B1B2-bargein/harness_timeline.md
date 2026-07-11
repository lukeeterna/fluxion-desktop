# Harness timeline (UAC) — GATE A3

- echo_db: 0.0 (0=OFF) · inject_at_ms: 2500 · rx_rms_max: 4640 · rx_frames: 800
- rx.wav = audio ricevuto da Sara (TX di Sara) · tx.wav = audio inviato dall'harness (eco+inject) · mix.wav = stereo L=rx R=tx

| t(s) | rx_rms | injecting |
|------|--------|-----------|
|   1.0 |     0 | false |
|   2.0 |     0 | false |
|   3.0 |  1850 | true |
|   4.0 |  4640 | true |
|   5.0 |  3110 | true |
|   6.0 |   363 | false |
|   7.0 |  3023 | false |
|   8.0 |  3056 | false |
|   9.0 |  2191 | false |
|  10.0 |  3268 | false |
|  11.0 |  1678 | false |
|  12.0 |     0 | false |
|  13.0 |     0 | false |
|  14.0 |     0 | false |
|  15.0 |     0 | false |
