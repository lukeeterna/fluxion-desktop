# T-SARA-GOSPIKE — TEST 3/3 CGNAT — REPORT 2026-07-07

## VERDETTO: 🟢 VERDE-PIENO-PRODOTTO

Il motore Go (diago v0.29.0 + sipgo v1.4.3) regge l'inbound audio DUPLEX reale sul
trunk EHIWEB **dietro CGNAT mobile (doppio NAT: hotspot 4G + CGNAT carrier)**, con
`external=""` — zero port-forward, zero IP pubblico, Piano B mai usato (impossibile su
CGNAT per definizione). Chiude il verdetto di prodotto: VERDE-BASE → VERDE-PIENO.

## RETE DI TEST (CGNAT, caso peggiore reale)
- Macchina: **MacBook** (macOS 11 Big Sur), non l'iMac.
- Rete: hotspot 4G founder. IP locale MacBook `10.45.26.173` (range hotspot, NON casa
  192.168.1.x). IP pubblico `151.45.151.20` (mobile TIM). → dietro NAT hotspot + CGNAT carrier.
- 2 telefoni: uno hotspot, uno per la chiamata (test pulito, no sospensione-dati).

## PROVA GREZZA (log gospike, /tmp/gospike_cgnat.log verbatim nel WAV-companion)
```
23:23:23 Listening on transport addr=10.45.26.173:5062 protocol=udp
23:23:23 REGISTER avvio uri=sip:0972536918@sip.vivavox.it port=5062 external="" rtp_range=[20000 20100]
   [REGISTER+keepalive STABILE ≥30s, zero errori, processo vivo]
23:25:52 INBOUND INVITE from=79.98.45.133:5060 callid=29b32ecd...@79.98.45.133:5060
23:25:52 ANSWERED — chiamata risposta
23:25:54 BEEP inviato — entro in ECHO
23:25:54 MEDIA negoziato payloadType=8 codec=PCMA
   [RX duplex: picchi voce rms 595/1823/2008/3302/4183/3869/3577... alternati a silenzio rms=8]
23:26:32 CALL END tot_frames_rx=1862 tot_bytes_rx=595840 rms_max=4183 wav_pcm_bytes=595840
```
- WAV committato: `.claude/cache/T-SARA-GOSPIKE/gospike_rx_cgnat_20260707.wav` = **595.884 B** non-nullo.
- Founder orecchio: **ECO udita = SÌ** (beep: presente nel log "BEEP inviato").

## DONE-CONDITION (tutte VERDI)
1. ✅ founder sente l'ECO della propria voce (sì confermato).
2. ✅ rms RX>0 loggato (rms_max 4183, 1862 frame RX).
3. ✅ WAV committato non-nullo (595.884 B).

## DISCORDANZE
- **#A (mandato FASE A.2 falsificata, correzione applicata)**: premessa = "se diago
  richiede Go >1.23 → MacBook fuori, installa Go 1.23 user-space". Fatto = diago v0.29.0
  e sipgo v1.4.3 richiedono `go 1.23.0` (floor, da proxy ufficiale); il MacBook ha **già**
  Go 1.24.1 funzionante su Big Sur (> floor). Il `go 1.26.4` del nostro go.mod è
  sovra-specificato (scritto dall'iMac). Correzione: build sul MacBook col Go 1.24.1 locale
  (`GOTOOLCHAIN=local CGO_ENABLED=0`), da copia usa-e-getta del go.mod con direttiva
  abbassata a `go 1.24` (go.mod committato NON toccato, vincolo #1d). FASE B evitata.
- **#1 (bug self-collision dual-stack — NON risolto dal flag su Big Sur)**: con
  `-bind 0.0.0.0` diago apriva comunque il listener su `[::]:5062` e la transazione REGISTER
  tentava un secondo socket su `10.45.26.173:5062` → `bind: address already in use` (morte in
  50ms). Sull'iMac Monterey lo stesso codice gira; su Big Sur il binding dual-stack ruba la
  porta IPv4. **Fix (unica iterazione tecnica)**: `-bind <IPv4-locale-specifico>` (es.
  `10.45.26.173`) → listener su IPv4 puro `10.45.26.173:5062`, nessuna collisione. Da
  incorporare in T-SARA-MEDIASWAP-GO: default `-bind` a IPv4-specifico o disabilitare dual-stack.
- **#2 (beep)**: non rilevante qui — log conferma "BEEP inviato"; fix beep-dopo-media resta
  in mediaswap.

## STATO LASCIATO (restore verificato per proprietà esterna)
- Sara RIPRISTINATA su iMac: PID **9257**, health 200, `reg_status:200`, DB non toccato.
  Comando restore = command-line reale del PID pre-esistente (`ps -p 4130`), CWD
  `/Volumes/MacSSD - Dati/FLUXION/voice-agent`.
- gospike FERMATO (SIGINT, de-register pulito), porte libere.
- Binario `voice-agent/tools/gospike/gospike_darwin_amd64` (gitignorato, solo build locale).
  go.mod committato invariato (`go 1.26.4`).

## PROSSIMO PASSO
**T-SARA-MEDIASWAP-GO** (su qualunque esito non-rosso → qui VERDE-PIENO), incorporando:
- fix #1: `-bind` a IPv4-specifico di default (o forza IPv4 single-stack, no `[::]`);
- fix #2: beep dopo media ACTIVE.
