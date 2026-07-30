# sip_diag — T-SIP-DIAG / #34v — 2026-07-30

## F1 — Motivo lato engine (go engine, porta 15090)

**Errore verbatim** (2 occorrenze identiche, run 20:24:25 e 20:24:40):

```
time=2026-07-30T20:24:25.568+02:00 level=ERROR msg="errore handler chiamata" error="more than 1 media line for type \"audio\""
time=2026-07-30T20:24:40.186+02:00 level=INFO  msg="INBOUND INVITE" from=127.0.0.1:15082 callid=D9347555-4C92-4E34-A4AE-D0790B512C18
time=2026-07-30T20:24:40.187+02:00 level=ERROR msg="errore handler chiamata" error="more than 1 media line for type \"audio\""
```

**Causa**: la go engine analizza l'SDP offerto dal driver pjsua2 e trova più di una m-line
di tipo `audio`. Il parser SDP del go engine è scritto per SDP con una singola m=audio;
due m-line (es. RTP + RTCP mux, o dual-audio) causano il rifiuto dell'handler con questo
errore. La sessione non viene creata, il BYE/480 arriva al driver.

Il log NON mostra nessun'altra causa (nessun errore di registrazione, nessun codec mismatch
precedente all'errore). Il rifiuto è attribuibile interamente alla validazione SDP.

---

## F2 — A/B con scenario giugno

**Nessuno scenario harness archiviato in `.claude/cache/T-SARA-TURNTAKING/` è eseguibile
tal quale con SIP INVITE.**

- I report di luglio 2026 (B1/B2, BARGE-IN, FASE1-3, B3_LIVE) sono documenti narrativi, non script.
- L'unico driver Python pre-30/7 eseguibile è `vos/runs/20260718/5-SUITE11/f3_driver.py`:
  usa **endpoint HTTP REST** (`/api/voice/reset`, `/api/voice/process`) — non emette INVITE SIP,
  non produce un CONFIRMED SIP. Non è confrontabile con il driver v2 su questo asse.
- Mancanza: nessuno script `.py` eseguibile con INVITE SIP è archivato in `.claude/cache/T-SARA-TURNTAKING/`.

Il confronto A/B SIP non è eseguibile con i materiali archiviati.

---

## Conclusione

Il go engine rifiuta ogni INVITE pjsua2 perché l'SDP contiene più di una m-line audio;
il driver HTTP REST di giugno (unico script eseguibile archiviato) non usa SIP — il confronto A/B SIP non è eseguibile.

---

## Stato rig alla chiusura

- sara3003 (pid 6620): KILLED
- regstub (pid 6618): KILLED
- Porte high-port 3003/15062/15090/8399: tutte FREE
- :3002 baseline: non attivo (era offline pre-rig, invariato)
