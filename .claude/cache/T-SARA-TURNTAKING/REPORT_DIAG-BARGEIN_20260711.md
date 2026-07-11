# REPORT DIAGNOSI BARGE-IN — T-SARA-TURNTAKING (2026-07-11, READ-ONLY)

> Mandato: discriminare **(a) l'iniezione non atterra su RTP verso Sara** vs
> **(b) il beep arriva ma l'engine/adapter non reagisce (barge-in non cablato/non attivo)**.
> Sessione read-only: zero mutazioni runtime/codice, solo artefatti committati (39bcc29a/ca59cde)
> + sorgente in lettura. Ogni claim con fonte (file:riga / misura WAV / riga di log).

## VERDETTO: (b) — IL BEEP ESCE SU RTP, LA REAZIONE MANCA LATO SARA

L'ipotesi (a) è **falsificata**: il tono 300Hz è provatamente scritto sull'encoder RTP verso Sara.
La reazione barge-in **non scatta**, e la logica di reazione avrebbe dovuto scattare se i frame
fossero arrivati al VAD Python → il guasto è **a valle dell'iniezione, sul path RX di Sara**
(Go-engine RTP-RX → bridge `FRAME_AUDIO_RX` → `rx_queue`), NON sull'harness.

Sotto-localizzazione b1 (Go-engine non inoltra RX) vs b2 (inoltra ma VAD non trigger) **NON
decidibile dagli artefatti committati**: l'unico strumento che la deciderebbe — il WAV lato-Sara
`call_<ts>.wav` (REGOLA #32) — **non è mai stato prodotto** per questa chiamata (vedi §4).

---

## FASE 1 — CONTROLLO STRUMENTO: lo strumento è MUTO sul RX

Il RED di -f conclude "barge-in non wired" da `grep = 0` dei marker RX-side. Quel grep NON prova nulla:

1. **Il log engine committato non copre nemmeno la finestra del barge-in.**
   `rig/sara3003.log` va da `22:45:56` (riga 1) a `23:13:29` (ultima riga) — è la finestra del
   **D3-soak** (report D3 `2026-07-10T20:56Z` UTC = ~22:56 locale). La chiamata barge-in è alle
   **23:26:33** (`calls/20260710-232633_A3-bargein/harness.log:1`), **13 min DOPO** la fine del log.
   Il "grep=0 nella finestra 23:26:33–50" è stato fatto contro un log che quella finestra non la contiene.

2. **Il vocabolario del log è quasi solo TX.** Su 1705 righe: `[GATE2R-PY-TX]`=1558, `[GATE2R-GO-TX]`=9.
   Marker RX-side (`GATE2R-PY-RX`, `echo_floor`, `barge`, `turn`, `clear_tx`, `rms`) = **0**.
   Gli unici `vad/VAD` sono il banner di startup (`sara3003.log:1`). `caller` compare 2 volte
   (`CALL_START caller=192.168.1.2:15080` @22:50:25, l'invite-probe D3).

3. **Il loop RX non emette marker per-frame BY DESIGN.** In `voip_goengine.py:663-751` il loop VAD/barge
   aggiorna `_echo_floor` in silenzio (`:697-699`, nessun log) e logga **solo** quando il barge-in
   scatta (`:706`) o a fine-turno (`:751,765`). Con RX che scorre ma sotto soglia → **zero righe**.

4. **Prova incrociata**: l'invite-probe D3 (22:50:25) ha avuto RX con energia reale (report RIG-A3:26
   "RX rms 1667-3291") eppure ha prodotto **zero marker RX/VAD** in `sara3003.log`. Lo strumento è muto
   anche quando l'RX c'è davvero.

**Conclusione FASE 1**: strumento MUTO su ogni path → il "zero marker" del RED **non è evidenza di
non-wiring**. Si decide coi WAV (FASE 2).

---

## FASE 2 — I WAV: il beep ESCE, Sara non si ferma

Fonte: `calls/20260710-232633_A3-bargein/{tx,rx}.wav` (PCM16 8kHz mono, 16.0s). RMS per secondo
(python stdlib `wave`+`array`; `audioop` assente su 3.13):

```
t(s)   tx_rms   rx_rms      note
 1        0     3258        Sara greeting; harness TX muto (-echo 0, no inject)
 2        0     3866
 3     9829     2993   ◄─── beep in TX (inject t=2.5–5.5) │ Sara CONTINUA
 4    13901     1878   ◄─── beep pieno                    │ Sara CONTINUA
 5    13901     2850   ◄─── beep pieno                    │ Sara CONTINUA
 6     9829     3353   ◄─── coda beep                     │ Sara CONTINUA
 7        0      539
 8        0     3557
 9        0     1028
10-16     0        0        fine greeting
```

- **tx.wav (harness → Sara)**: il beep è presente con energia forte (rms **9829→13901**) SOLO nella
  finestra di iniezione, zero fuori. Frequenza verificata = **~300Hz** (sign-changes=1199 su 2.0s →
  300Hz), = `beepPCM(300.0, 3s)` di `uac.go:98,286-296`. **Il tono è realmente stato emesso.**
- **rx.wav (greeting di Sara)**: rms ~2000–3500 **continuo attraverso la finestra** (t=3,4,5,6) →
  Sara non ha smesso di parlare → **barge-in NON scattato** (conferma il RED, ma sul dato harness).
- `harness.log:7-11` mostra `injecting=true` a t=3,4,5 (cursore dentro la finestra) mentre `rx_rms`
  (di Sara) resta 2993/1708/2925 → Sara ignora il tono.

**tx.wav = i byte scritti su `enc.Write`.** In `uac.go:236` `enc.Write(txFrame)` va all'encoder RTP;
`uac.go:240` `txBuf.Write(txFrame)` accumula gli **stessi** byte in tx.wav. Quindi tx.wav È la prova
di ciò che è stato consegnato all'RTP. **RTP bidirezionale su loopback provato attivo**: rx.wav
(Sara→harness) porta audio rms 3000+, cioè lo stesso socket-pair recapita nei due sensi → il beep
harness→Sara raggiunge il socket RTP di Sara con probabilità ~certa.

→ **(a) falsificata**: il beep atterra su RTP.

---

## FASE 3 — SORGENTE (conferma del meccanismo, non fix)

### uac.go — `-echo 0` azzera SOLO l'echo, NON l'inject
Invocazione RED (`VERDETTO.md:5`): `-echo 0 -injectat 2500`. In `uac.go`:
- `:102-105` `echoGain` resta **0.0** quando `-echo == 0`.
- Frame-builder `:221-234`: la componente echo è sommata **solo se** `echoGain > 0` (`:216,223`);
  l'inject (`:227-232`, `acc += utterPCM`) è **indipendente** dal gain.
- Risultato atteso: tx = 0 (silenzio) + beep nella finestra. **Coincide esattamente col tx.wav** (0 fuori,
  ~14000 dentro). L'invocazione RED non ha auto-annullato il beep. `injecting=true` a log (`:208`)
  deriva dal cursore `txSample`, ma i byte del beep **sono comunque** passati a `enc.Write` (`:236`).

### voip_goengine.py — il path RX→VAD→barge esiste, è attivo, ed è gated correttamente
- `rx_queue` è alimentata **solo** da `FRAME_AUDIO_RX` dal bridge Go→Python: `:344-348`
  (`_dispatch` → `rx_queue.put_nowait(payload)`).
- Loop VAD/barge avviato in `start()`: `:226` thread `goengine-audio` → `_audio_processing_loop`.
- Barge gated su `_is_sara_speaking()` (`:692-694`), che è **True mentre la coda TX è piena** (`:606-608`)
  → durante la greeting il barge **è** valutato.
- Con `-echo 0` l'harness manda silenzio fuori dal beep → `_echo_floor` (`:697-699`, init 0 a `:148`)
  resta ~0 → soglia `thr = max(500, 1.8·floor) ≈ 500` (`:702`). Un beep rms ~14000 sostenuto 3s
  supererebbe 500 per ben oltre `BARGE_IN_SUSTAIN` → `clear_tx()` **avrebbe dovuto** scattare (`:703-710`).
- Non è scattato ⇒ i `FRAME_AUDIO_RX` col beep **non hanno raggiunto `rx_queue`** con rms utile.
  Anello sospetto = **Go-engine RTP-RX → `FRAME_AUDIO_RX`** (a monte di `_dispatch:344`), lato Sara.

---

## FASE 4 — CATENA DI PROVA, CAVEAT, RACCOMANDAZIONE

### Catena di prova
1. Beep emesso su RTP: tx.wav rms 9829→13901 @~300Hz in finestra (uac.go:236,240) — **provato**.
2. RTP bidirezionale su loopback attivo: rx.wav (Sara→harness) rms 3000+ — **provato**.
3. ⇒ beep recapitato al socket RTP di Sara — **inferenza ~certa** (stesso socket-pair, verso opposto recapita).
4. Barge-logic attiva, gated bene, soglia 500 con echo_floor~0 (voip_goengine.py:226,606-608,702) — **provato in codice**.
5. Barge non scattato (rx.wav Sara continua; nessun `clear_tx`) — **provato**.
6. 4∧5 ⇒ i frame beep non sono arrivati al VAD Python ⇒ guasto sul path RX di Sara — **inferenza forte**.

### CAVEAT (onestà #10/#1b)
- **Nessuna evidenza engine-side committata per la chiamata 23:26:33**: `sara3003.log` finisce alle 23:13:29.
- Il punto 3 è inferenza (nessun capture RTP-RX di Sara), non misura diretta.
- b1 (Go-engine non inoltra RX) vs b2 (inoltra ma VAD non trigger) resta **aperto**: manca il WAV lato-Sara.

### Perché manca lo strumento decisivo (root del blocco)
`voip_goengine.py:183` abilita il capture lato-Sara con `SARA_TEST_CAPTURE=="1"`; su `CALL_END`
scrive `calls/call_<ts>.wav` (`:403-405,888-922`) con **rx=linea chiamante** (il beep) + tx=voce Sara.
Ma lo script di rilancio del rig (`REPORT_RIG-A3_2026-07-10-f.md:59-62`) esporta `SARA_TEST_CAPTURE=1`
**solo all'harness gospike**, NON al processo Python `sara3003`. Quindi il WAV-giudice lato-Sara
**non è mai stato prodotto** — confermato: `git ls-files | grep call_*.wav` = 0, `find` su disco = 0.
La REGOLA #32 esiste nel codice ma non è stata attivata sul processo giusto per questa chiamata.

### RACCOMANDAZIONE (progettata, NON implementata — fix = mandato separato)
1. **Riabilitare lo strumento**: ri-lanciare A3 barge-in esportando `SARA_TEST_CAPTURE=1` **anche** sul
   `main.py --port 3003` (non solo sull'harness). Su `CALL_END` si ottiene `calls/call_<ts>.wav`.
   Poi misurare l'rms del canale rx in t=2.5–5.5s:
   - rx con beep → i `FRAME_AUDIO_RX` arrivano → guasto in VAD/soglia/timing `_is_sara_speaking` = **b2**;
   - rx muto → il Go-engine non inoltra l'RTP-RX al bridge = **b1** → strumentare la lettura RTP del Go-engine.
2. **Rendere osservabile il RX** (causa del mis-read del RED): aggiungere in `_audio_processing_loop`
   un marker INFO ~1/s con `rms`, `_echo_floor`, `sara_speaking` (oggi il loop è muto sotto-soglia).
   Senza questo, "zero marker" continuerà a essere confuso con "non wired".

### Correzione del VERDETTO.md di -f (RED mal attribuito)
`calls/20260710-232633_A3-bargein/VERDETTO.md:13-15` usa "ZERO marker RX-side (grep=0)" come prova di
"path caller-audio→VAD non processa". **Inferenza invalida**: (i) il loop RX non logga per-frame by
design (`voip_goengine.py:697-699`), (ii) il `sara3003.log` committato non copre la finestra della
chiamata. Il fatto osservato corretto ("barge-in non scattato") regge dal **rx.wav** (Sara non si ferma),
NON dai marker. La root-cause "gap RX-side" era **non provata**; questo report la ri-qualifica come
**(b) confermato, sotto-localizzazione b1/b2 pendente su `call_<ts>.wav`**.

---

## C4 — REPORT GIUDICE (schema fisso)

- **DOMANDA**: barge-in RED (calls/20260710-232633_A3-bargein) = (a) iniezione non atterra o (b) non cablato?
- **VERDETTO**: **(b)** — il beep 300Hz esce su RTP (provato); la reazione barge-in manca sul path RX di Sara.
- **PROVE CHIAVE**:
  - tx.wav rms 9829→13901 @~300Hz in finestra 2.5–5.5s (beep emesso, uac.go:236,240).
  - rx.wav Sara rms 3000+ continuo → RTP loopback bidirezionale attivo + Sara non si ferma.
  - Barge-logic attiva/gated/soglia≈500 con echo_floor~0 (voip_goengine.py:226,606-608,702) → avrebbe dovuto scattare.
  - `-echo 0` non annulla l'inject (uac.go:216-232) → il beep NON è auto-soppresso dal test.
- **STRUMENTO**: MUTO — sara3003.log copre 22:45–23:13 (D3-soak), non la call 23:26; loop RX no log per-frame.
- **CAVEAT**: nessun capture engine-side per la call; b1 vs b2 non decidibile senza `call_<ts>.wav` lato-Sara.
- **AZIONE MINIMA PER CHIUDERE**: ri-run con `SARA_TEST_CAPTURE=1` sul processo `sara3003` → leggere rx di `call_<ts>.wav`.
- **STATO 3002 pjsua2**: NON toccato (sessione read-only). VectCutAPI intatto.

## FONTI CITATE
- Artefatti: `calls/20260710-232633_A3-bargein/{harness.log,tx.wav,rx.wav,harness_timeline.md,VERDETTO.md}`,
  `rig/sara3003.log`, `REPORT_RIG-A3_2026-07-10-f.md`.
- Sorgente (lettura): `voice-agent/tools/gospike/uac.go`, `voice-agent/src/voip_goengine.py`.
- Misure WAV: python stdlib `wave`+`array` (RMS/secondo, sign-change freq), read-only.
