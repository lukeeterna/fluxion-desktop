# REPORT — T-SARA-PYRTP-SPIKE (2026-07-04)

## VERDETTO: 🔴 ROSSO-LIBRERIA
**pyVoIP 1.6.8 NON regge l'inbound sul trunk EHIWEB su questa piattaforma.** La chiamata non
raggiunge MAI la fase media/answer: il founder sente **"linea occupata"** in entrambi i tentativi.
Done-condition esterna (eco confermata + rms RX>0 + WAV non-nullo) **NON raggiunta**. Nessuna
iterazione oltre le due eseguite (timebox #1c rispettato: reproduction ottenuta, verdetto chiuso).

## DOVE SI ROMPE (prova grezza verbatim)
REGISTER **sempre OK** (200 REGISTERED, <0.4s). Il collo è a valle, sulla **segnalazione SIP inbound**.

### try1 (WAV `capture_rx_20260704.wav` — mai creato, `handle_call` mai invocato)
INVITE raggiunge pyVoIP → **crash della thread SIP di ricezione**, poi provider timeout → busy:
```
[spike 20:07:49.267] REGISTER ok -> status=PhoneStatus.REGISTERED
Exception in thread SIP Recieve:
Traceback (most recent call last):
  File ".venv-spike/lib/python3.9/site-packages/pyVoIP/util.py", line 17, in acquired_lock_and_unblocked_socket
    socket.setblocking(False)
OSError: [Errno 9] Bad file descriptor
During handling of the above exception, another exception occurred:
  File ".venv-spike/lib/python3.9/site-packages/pyVoIP/SIP.py", line 853, in recv_loop
    with acquired_lock_and_unblocked_socket(self.recvLock, self.s):
  File ".venv-spike/lib/python3.9/site-packages/pyVoIP/util.py", line 20, in acquired_lock_and_unblocked_socket
    socket.setblocking(True)
OSError: [Errno 9] Bad file descriptor
TODO: Add 500 Error on Receiving SIP Response
---SPIKE-RESULT--- rms_max=0 total_rx=0
```
Segnale chiave: `TODO: Add 500 Error on Receiving SIP Response` = pyVoIP ha ricevuto una
**risposta SIP che non sa gestire**, il socket di segnalazione viene chiuso da un'altra thread
→ `self.s` diventa fd invalido → `recv_loop` muore → nessun 200 OK all'INVITE → busy.

### try2 (WAV `capture_rx_20260704_try2.wav` — mai creato)
`REGISTER ok` + `PRONTO`, poi **nessun log `INBOUND INVITE`, processo idle, nessun crash**:
l'INVITE **non è stato instradato affatto** allo spike → busy a monte lato provider.
Cioè: due sotto-firme dello stesso fallimento (crash-su-INVITE / non-routing), stessa UX = "occupato".

## AMBIENTE (per riproduzione dal giudice)
- **Host**: iMac 2012, macOS 11 Big Sur (no AVX2), Python **3.9.6** (CommandLineTools di sistema).
- **Rete**: iMac LAN `192.168.1.2` (en0) dietro router domestico, **IP pubblico `151.45.159.109`, NESSUN port-forward**.
- **Provider**: EHIWEB **VivaVox Free** (trial 30gg/100min), `sip.vivavox.it:5060/UDP`, codec **G729.A**
  annunciato dal provider, **UN SOLO account = il DID `0972536918`** (no 2° account per test A/B).
- **Libreria**: `pyVoIP==1.6.8` (ultima STABILE PyPI, 17-gen-2024; 2.x solo alpha), wheel `py3-none-any`,
  **zero dipendenze binarie**, puro Python (verificato — requisito portabilità Windows on-premise).
- **Spike**: `voice-agent/tools/pyrtp_spike.py` (committato). `sipPort=5080`, `rtp=4000-4020`,
  `myIP=192.168.1.2`, Piano-A beep-first latching (2s 440Hz), echo loop `write_audio(read_audio())`.
- **Formato audio verificato dal disco** (`RTP.py parse_pcmu`/`encode_pcmu`): **8-bit UNSIGNED PCM
  mono 8kHz**, silenzio `0x80` (NON PCM16 come da premessa mandato — vedi DISCORDANZE).

## DISCORDANZE (contratto)
- **§1.2 formato beep**: premessa "PCM16 8k mono" | disco: pyVoIP usa **8-bit unsigned** (PCM16
  romperebbe μ-law encode). Correzione applicata: beep 8-bit unsigned, RMS su segnale de-biasato.
- **cwd Sara**: HANDOFF cita `MacSSD - Dati/fluxion` | disco (lsof): `.../FLUXION` maiuscolo
  (FS case-insensitive, non bloccante).

## STORICO — pattern strutturale (per il giudice)
Ogni stack SIP+media **in-process** provato su QUESTA combinazione (iMac Big Sur / Python 3.9 /
EHIWEB / NAT senza forward) fallisce sull'**inbound reale**, ma in punti diversi:
- **pjsua2** (S244 / S351 / S354 / T-SARA-WIRING / T-SARA-TRUNK-CALL1): la chiamata **si connette**
  (TX udibile), ma la **RX è morta** — il media clock-thread crasha/non pompa. Firme:
  `lock.c:279 Assert glock->owner`, `grp_lock_release`, `os_core_unix.c "possibly re-registering
  existing thread"`. `latency count=0`, zero `Speech turn detected RMS=`. Decisione già presa →
  **Asterisk ARI** (Sara = solo brain). CALL-1 (2026-07-04) ha **falsificato S244** anche sul trunk.
- **pyVoIP 1.6.8** (QUESTA sessione): la chiamata **non si connette nemmeno** — la thread SIP di
  ricezione crasha (`OSError Bad file descriptor`) o l'INVITE non viene instradato → "linea occupata".
Filo comune: **il modello "layer SIP/media puro-Python in-process, inbound diretto dal provider,
dietro NAT senza forward" non è robusto su questo terreno.** Il punto di rottura si sposta
(media in pjsua2, segnalazione in pyVoIP) ma l'inbound reale non chiude mai il duplex.

## DOMANDA AL GIUDICE (soluzione definitiva richiesta dal founder)
Dato che **due** stack in-process (pjsua2 e pyVoIP) falliscono l'inbound su questo terreno, e che
per pjsua2 era già stato deciso il pivot ad **Asterisk ARI**:
1. Il pattern "linea occupata / inbound non chiude" è la **stessa root-cause** del pivot Asterisk ARI
   già deciso, e quindi il verdetto è: **abbandonare il layer SIP puro-Python e mettere Asterisk
   (o alternativa gestita) davanti, con Sara solo come brain sull'audio via ARI/AudioSocket**? OPPURE
2. Esiste un fix specifico e verificabile per pyVoIP 1.6.8 su questo `OSError Bad file descriptor`
   (es. gestione della risposta SIP non gestita `TODO: Add 500 Error`, patch al `recv_loop`, o
   versione/branch che regge EHIWEB) che renderebbe il layer puro-Python viabile e portabile su
   Windows on-premise?
3. Confondente da chiudere: quanto pesa il **NAT senza port-forward** vs. il bug libreria? try2
   (INVITE non instradato) suggerisce una componente provider/NAT; try1 (crash su INVITE) è
   puramente libreria. Serve un 2° account SIP EHIWEB o un test in rete pubblica per separarli?

Fornire una **soluzione singola implementabile** (non lista A/B/C/D operativa) con i comandi/patch
esatti da eseguire.

## STATO LASCIATO (verificato)
- **Sara UP**: PID **73256**, `/health` 200, SIP `registered:true, reg_status:200`
  (`0972536918`@sip.vivavox.it), `rtp_active:false`, engine pjsua2. Restore eseguito col comando A3.
- **DB non toccato**: nessuna call ha raggiunto la fase media → 0 turni → 0 booking/cliente.
- **venv** `voice-agent/.venv-spike` resta sull'iMac (gitignorato, pyVoIP 1.6.8 installato) per ritest.
- **File toccati/creati**: `voice-agent/tools/pyrtp_spike.py` (nuovo, committato),
  questo report. Log grezzi iMac `/tmp/pyrtp_spike*.log` (EFFIMERI — verbatim catturati qui).
- **Nessun edit** a Sara / `voip_pjsua2.py` / repo produzione oltre lo spike tool + venv.
