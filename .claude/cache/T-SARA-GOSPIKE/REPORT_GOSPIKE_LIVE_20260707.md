# REPORT LIVE — T-SARA-GOSPIKE (FASE 2, 2026-07-07)

## VERDETTO
**🟢 VERDE-BASE** — TEST 1/3 (porta 5080) e TEST 2/3 (porta 5062 NON forwardata) VERDI su
REGISTER+keepalive+symmetric-RTP PURI (`external=""`, nessun IP pubblico, nessun port-forward).
TEST 3/3 (CGNAT 4G) **non eseguito** (gate context reale >50%, rimandato a sessione fresca).
Piano B (SDP IP pubblico) **mai usato** → il verde è product-clean, non NAT-truccato.

## PROVA GREZZA (per-test)

### TEST 1/3 — trunk base, porta 5080 (iMac)
- REGISTER ok su `sip:0972536918@sip.vivavox.it`, listener `192.168.1.2:5080` (IPv4), 0 ERROR.
- `INBOUND INVITE from=79.98.45.133:5060` (gateway EHIWEB) → `ANSWERED`.
- `MEDIA negoziato payloadType=8 codec=PCMA` (G.711 A-law).
- RX: baseline rms~8 (silenzio) → picchi **2471/2678/3044/2837/2265/1947** sul parlato.
- `CALL END tot_frames_rx=4924 tot_bytes_rx=1575680 rms_max=3044`.
- WAV: `rx_20260707_224141.wav` = **1.575.724 B** (non-nullo, committato).
- **Founder (orecchio): "beep + eco pulita"** → duplex confermato soggettivamente.

### TEST 2/3 — porta NON forwardata 5062 (iMac)
- REGISTER ok, listener `192.168.1.2:5062`, 0 ERROR.
- `INBOUND INVITE from=79.98.45.133:5060` **arrivato su 5062** (porta arbitraria mai
  forwardata) → l'INVITE è entrato SOLO dal pinhole aperto da REGISTER/keepalive =
  **niente-port-forward VALIDATO sulla segnalazione**.
- `MEDIA negoziato PCMA`, RX rms_max=**3082**, 4305 frame, `CALL END tot_bytes_rx=1377600`.
- WAV: `rx5062_20260707_224902.wav` = **1.377.644 B** (non-nullo, committato).
- **Founder (orecchio): "no beep, eco perfetto"** → duplex audio confermato su porta
  non forwardata.

## DISCORDANZE
- **#1 (bug spike, corretto in-sessione)**: primo avvio su 5080 → `bind: address already in
  use` **contro sé stesso**: il listener prendeva `[::]:5080` (IPv6 dual-stack, che su macOS
  copre anche IPv4) e la transaction REGISTER collideva su `192.168.1.2:5080`. FIX: aggiunto
  flag `-bind` (default `0.0.0.0`) → forzato listener IPv4 `192.168.1.2:5080`, self-collision
  risolta. Porta 5080 era realmente libera (Sara killata, `PORT_FREE_OK`). main.go aggiornato
  + rebuild su iMac (BUILD_OK).
- **#2 (beep 2/3, cosmetica, non-bloccante)**: su 5062 il founder NON ha sentito il beep ma
  eco perfetto. Causa probabile: su 5062 `MEDIA negoziato` è loggato ~2s dopo `ANSWERED`
  (INVITE arrivato al tick 34), il beep parte subito dopo `Answer()` e cade nel media non
  ancora ACTIVE. Fix da fare in fase mediaswap: emettere beep/greeting SOLO dopo media ACTIVE.
- **#3 (premessa cwd restore)**: report S704 indicava `.../fluxion/voice-agent` (minuscolo);
  cwd reale del PID 73256 = `.../FLUXION/voice-agent` (maiuscolo). Restore corretto e usato.

## STATO LASCIATO / RESTORE
- **Sara RIPRISTINATA e VERIFICATA**: PID 4130, `/health` 200, `registered:true reg_status:200`
  (`0972536918`@sip.vivavox.it), engine pjsua2, `rtp_active:false`. DB non toccato (0 turni Sara
  durante la finestra: gospike è un processo separato, Sara era down).
- gospike de-registrato pulito (SIGINT) → porte 5080/5062 libere. Binario resta su iMac
  (gitignorato). Toolchain Go `~/sdk` invariata.
- Restore usato (verificato per cwd/interprete reali):
  `ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && nohup python3 main.py --port 3002 > /tmp/sara_restart.log 2>&1 &'`

## PROSSIMO PASSO
- **TEST 3/3 (CGNAT 4G via hotspot, MacBook)** — sessione fresca, gate context ≤50% + founder
  disponibile: git pull gospike, verifica se il binario darwin-amd64 gira sul MacBook (macOS 11
  Big Sur vs Go 1.26.4 — premessa cieca, eventuale rebuild user-space), aggancio hotspot 4G,
  REGISTER + chiamata. Duplex ok = VERDE-PIENO-PRODOTTO.
- **Se si salta 3/3**: VERDE-BASE è sufficiente per avviare **T-SARA-MEDIASWAP-GO** (motore Go +
  adapter socket sulle code rx/tts, greeting con disclosure AI art.50, fix beep-dopo-media #2).
