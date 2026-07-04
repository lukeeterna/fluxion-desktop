# REPORT — T-SARA-GOSPIKE (2026-07-04)

## VERDETTO
**VERDE-TOOLCHAIN+BUILD (FASE 0+1 chiuse), LIVE-TEST PENDING (FASE 2 non eseguita — chiusura per gate context #7).**
Non è un ROSSO né un VERDE-PIENO: la falsificazione live (done-condition 1-3) NON è stata girata.
Done-condition **#4 (cross-compile Windows) RAGGIUNTA**. Nessuna gamba di capacità mancante (ROSSO-CAPACITÀ EVITATO).

## PROVA GREZZA
- **Toolchain**: Go assente su iMac → installato user-space `~/sdk/go` (tarball ufficiale darwin-amd64, no sudo/brew). `go version go1.26.4 darwin/amd64`.
- **Fetch pinnato**: `github.com/emiago/sipgo v1.4.3`, `github.com/emiago/diago v0.29.0`. Codec G.711 = `github.com/zaf/g711 v1.4.0` (PURO GO → abilita build statico). Digest auth = `github.com/icholy/digest v1.1.0`. opus = `gopkg.in/hraban/opus.v2` (CGO, dietro build-tag, NON trascinato quando inutilizzato).
- **VETTING 6/6 gambe (read-only su module cache)**:
  - (a) REGISTER+digest → `tu.Register(ctx,uri,RegisterOptions{Username,Password})` + `digest_auth.go` (esempio `examples/register`).
  - (b) inbound Serve+Answer → `tu.Serve(ctx, func(*DialogServerSession))` + `inDialog.Answer()`.
  - (c) PCMU/PCMA → `media/codec.go:19-20` `CodecAudioUlaw{pt:0}` / `CodecAudioAlaw{pt:8}`.
  - (d) read+write raw → `AudioReader()` + `AudioWriter() io.Writer` (`dialog_media.go:438`); echo esempio `wav_record` via `media.Copy(reader,writer)`.
  - (e) symmetric-RTP/NAT → `media/rtp_session.go:40 RTPSourceLock bool` (source-lock ≥v0.23) + `diago.go:65 ExternalHost` / `:69 MediaExternalIP net.IP` (SDP con IP pubblico = Piano B).
  - (f) keepalive/re-register → `RegisterOptions.Expiry` + `RetryInterval` (`register_transaction.go:33-43`).
- **BUILD (esiti reali, `go build`)**:
  - `CGO_ENABLED=1 go build` darwin-amd64 → `gospike_darwin_amd64` **11.617.984 B** OK.
  - `CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build` → `gospike_windows_amd64.exe` **11.455.488 B** OK ⇒ **DONE-CONDITION #4**.

## VERSIONI PINNATE
Go **1.26.4** | diago **v0.29.0** | sipgo **v1.4.3** | g711 **v1.4.0** | icholy/digest **v1.1.0** | pion/rtp v1.8.18, pion/srtp/v3 v3.0.6.

## DISCORDANZE
- **#1 (premessa mandato)**: «iMac = macOS 11 Big Sur, Go 1.23.x ultima linea». **Fatto disco**: iMac = **macOS 12.7.4 Monterey x86_64** (`sw_vers`). **Correzione**: vincolo Big Sur sull'host cade → usata ultima linea stabile Go 1.26.4. Portabilità reale = target Windows (cross-compile, OS-host-indipendente): non intaccata.

## STATO LASCIATO
- **Sara MAI toccata**: PID 73256 UP, `/health` 200, SIP `reg_status:200` (`0972536918`@sip.vivavox.it), `rtp_active:false`, engine pjsua2. Nessuno stop/riavvio (FASE 1.3 interruzione servizio NON avviata → nessun yes/no founder consumato). DB non toccato.
- **gospike MAI avviato** (nessun REGISTER concorrente → nessun rischio kick su Sara). Binari solo su iMac (gitignorati). Sorgente+go.mod+go.sum committati su MacBook.
- Toolchain Go resta in `~/sdk` su iMac (user-space, riusabile).

## RESTORE
Sara non richiede restore (mai stoppata). Comando di riavvio annotato per completezza:
`ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion/voice-agent" && nohup python3 main.py --port 3002 > /tmp/sara_restart.log 2>&1 &'`

## PROSSIMO PASSO (FASE 2 — sessione fresca, resume one-shot)
1. `ssh imac` export `PATH=~/sdk/go/bin:$PATH GOPATH=~/sdk/gopath GOCACHE=~/sdk/gocache`; binario già compilabile in `voice-agent/tools/gospike/`.
2. Carica creds da env: `set -a; source "/Volumes/MacSSD - Dati/fluxion/voice-agent/.env"; set +a` → export `VOIP_SIP_USER=$VOIP_SIP_USER` ecc. (mai in argv/chiaro). NB verificare i nomi reali delle var nel `.env` iMac.
3. **yes/no NATIVO founder** (FASE 1.3): stop Sara PID 73256 per liberare account+porta 5080. Restore = comando sopra.
4. Avvia `./gospike_darwin_amd64 -port 5080 -wav .claude/cache/T-SARA-GOSPIKE/rx_$(date +%s).wav -dur 120`, attendi log `REGISTER` ok.
5. «PRONTO — chiama 0972536918, ascolta beep, parla ~20s verificando l'ECO, riaggancia».
6. Valuta done-condition 1-3: log `INBOUND INVITE from=`, `RX rms>0`, WAV committata non-nulla. Se RX=0 ma INVITE arrivato → Piano B: riavvia con `-external <IP_PUBBLICO>` (SDP IP pubblico + source-lock), UNA iterazione. Se INVITE mai arrivato = NAT.
7. Su verde: FASE 2-BIS porta 5062 non-forwardata (prova NAT-cliente). Poi verdetto VERDE-PIENO/VERDE-CON-RISERVA-NAT/ROSSO-*.
