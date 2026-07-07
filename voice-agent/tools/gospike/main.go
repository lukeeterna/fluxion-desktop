// T-SARA-GOSPIKE — motore SIP/media esterno in Go (spike GO/NO-GO).
// Falsifica: REGISTER + inbound + audio DUPLEX (echo) sul trunk EHIWEB dietro NAT.
// Stack: emiago/diago v0.29.0 + emiago/sipgo v1.4.3. Codec PCMU/PCMA. Zero-cost.
//
// Credenziali SOLO da env VOIP_SIP_USER / VOIP_SIP_PASS / VOIP_SIP_SERVER (mai in argv).
// Uso:
//   VOIP_SIP_USER=.. VOIP_SIP_PASS=.. VOIP_SIP_SERVER=sip.vivavox.it \
//     ./gospike -port 5080 [-external <IP_PUBBLICO>] -wav /tmp/gospike_rx.wav -dur 120
package main

import (
	"bytes"
	"context"
	"encoding/binary"
	"errors"
	"flag"
	"io"
	"log/slog"
	"math"
	"net"
	"os"
	"os/signal"
	"time"

	"github.com/emiago/diago"
	"github.com/emiago/diago/audio"
	"github.com/emiago/sipgo"
	"github.com/emiago/sipgo/sip"
)

var (
	fPort     = flag.Int("port", 5080, "porta SIP di bind")
	fBind     = flag.String("bind", "0.0.0.0", "host IPv4 di bind listener SIP (evita dual-stack [::] self-collision)")
	fRTPMin   = flag.Int("rtpmin", 20000, "RTP port range min (dichiarato)")
	fRTPMax   = flag.Int("rtpmax", 20100, "RTP port range max (dichiarato)")
	fExternal = flag.String("external", "", "IP pubblico per SDP/media (NAT Piano B)")
	fWav      = flag.String("wav", "/tmp/gospike_rx.wav", "path cattura RX WAV")
	fDur      = flag.Int("dur", 120, "durata massima chiamata (secondi)")
)

func main() {
	flag.Parse()
	slog.SetDefault(slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelInfo})))

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	user := os.Getenv("VOIP_SIP_USER")
	pass := os.Getenv("VOIP_SIP_PASS")
	server := os.Getenv("VOIP_SIP_SERVER")
	if user == "" || pass == "" || server == "" {
		slog.Error("env mancanti: servono VOIP_SIP_USER, VOIP_SIP_PASS, VOIP_SIP_SERVER")
		os.Exit(2)
	}

	if err := run(ctx, user, pass, server); err != nil && !errors.Is(err, context.Canceled) {
		slog.Error("gospike terminato con errore", "error", err)
		os.Exit(1)
	}
	slog.Info("gospike uscita pulita")
}

func run(ctx context.Context, user, pass, server string) error {
	ua, err := sipgo.NewUA(sipgo.WithUserAgent(user))
	if err != nil {
		return err
	}
	defer ua.Close()

	tr := diago.Transport{
		Transport: "udp",
		BindHost:  *fBind,
		BindPort:  *fPort,
	}
	if *fExternal != "" {
		tr.ExternalHost = *fExternal
		if ip := net.ParseIP(*fExternal); ip != nil {
			tr.MediaExternalIP = ip
		}
	}
	tu := diago.NewDiago(ua, diago.WithTransport(tr))

	// Handler chiamate in ingresso.
	go func() {
		serveErr := tu.Serve(ctx, func(inDialog *diago.DialogServerSession) {
			slog.Info("INBOUND INVITE", "from", inDialog.InviteRequest.Source(), "callid", inDialog.InviteRequest.CallID().Value())
			if err := handle(ctx, inDialog); err != nil && !errors.Is(err, io.EOF) {
				slog.Error("errore handler chiamata", "error", err)
			}
		})
		if serveErr != nil && !errors.Is(serveErr, context.Canceled) {
			slog.Error("Serve terminato", "error", serveErr)
		}
	}()

	// REGISTER con keepalive (expiry 120s, re-register anticipato via RetryInterval 25s).
	regURI := sip.Uri{}
	if err := sip.ParseUri("sip:"+user+"@"+server, &regURI); err != nil {
		return err
	}
	slog.Info("REGISTER avvio", "uri", "sip:"+user+"@"+server, "port", *fPort,
		"external", *fExternal, "rtp_range", []int{*fRTPMin, *fRTPMax})
	return tu.Register(ctx, regURI, diago.RegisterOptions{
		Username:      user,
		Password:      pass,
		Expiry:        120 * time.Second,
		RetryInterval: 25 * time.Second,
	})
}

func handle(ctx context.Context, d *diago.DialogServerSession) error {
	d.Trying()
	d.Ringing()
	if err := d.Answer(); err != nil {
		return err
	}
	slog.Info("ANSWERED — chiamata risposta")

	// 1) BEEP 2s 440Hz (playback gestisce encoding+pacing verso il codec negoziato).
	beep := makeBeepWav(440.0, 2*time.Second)
	if pb, err := d.PlaybackCreate(); err == nil {
		if _, err := pb.Play(bytes.NewReader(beep), "audio/wav"); err != nil {
			slog.Warn("beep playback errore", "error", err)
		}
	} else {
		slog.Warn("PlaybackCreate errore", "error", err)
	}
	slog.Info("BEEP inviato — entro in ECHO")

	// 2) ECHO + strumentazione (RMS/WAV su RX).
	mp := diago.MediaProps{}
	audioReader, err := d.AudioReader(diago.WithAudioReaderMediaProps(&mp))
	if err != nil {
		return err
	}
	audioWriter, err := d.AudioWriter(diago.WithAudioWriterMediaProps(&mp))
	if err != nil {
		return err
	}
	pt := mp.Codec.PayloadType
	slog.Info("MEDIA negoziato", "payloadType", pt, "codec", mp.Codec.Name)

	dec, err := audio.NewPCMDecoderReader(pt, audioReader)
	if err != nil {
		return err
	}
	enc, err := audio.NewPCMEncoderWriter(pt, audioWriter)
	if err != nil {
		return err
	}

	// Hangup pulito a fine durata.
	callCtx, cancelCall := context.WithCancel(ctx)
	defer cancelCall()
	go func() {
		select {
		case <-time.After(time.Duration(*fDur) * time.Second):
			slog.Info("durata massima raggiunta — hangup")
			_ = d.Hangup(context.Background())
		case <-callCtx.Done():
		}
	}()

	var wavBuf bytes.Buffer // PCM int16 LE accumulato (RX)
	buf := make([]byte, 4096)
	var totFrames, totBytes int64
	var secFrames, secBytes, secSamples int64
	var secSumSq float64
	var maxRMS float64
	lastLog := time.Now()

	for {
		n, rerr := dec.Read(buf)
		if n > 0 {
			totFrames++
			totBytes += int64(n)
			secFrames++
			secBytes += int64(n)
			for i := 0; i+1 < n; i += 2 {
				s := int16(binary.LittleEndian.Uint16(buf[i : i+2]))
				secSumSq += float64(s) * float64(s)
				secSamples++
			}
			wavBuf.Write(buf[:n])
			if _, werr := enc.Write(buf[:n]); werr != nil {
				slog.Warn("echo write errore", "error", werr)
			}
		}
		if time.Since(lastLog) >= time.Second {
			rms := 0.0
			if secSamples > 0 {
				rms = math.Sqrt(secSumSq / float64(secSamples))
			}
			if rms > maxRMS {
				maxRMS = rms
			}
			slog.Info("RX", "frames", secFrames, "bytes", secBytes, "rms", int(rms))
			lastLog = time.Now()
			secFrames, secBytes, secSamples, secSumSq = 0, 0, 0, 0
		}
		if rerr != nil {
			if !errors.Is(rerr, io.EOF) {
				slog.Info("read RX terminato", "reason", rerr.Error())
			}
			break
		}
	}

	if err := writeWav(*fWav, wavBuf.Bytes()); err != nil {
		slog.Error("scrittura WAV fallita", "error", err)
	}
	slog.Info("CALL END", "tot_frames_rx", totFrames, "tot_bytes_rx", totBytes,
		"rms_max", int(maxRMS), "wav", *fWav, "wav_pcm_bytes", wavBuf.Len())
	return nil
}

// makeBeepWav genera un WAV PCM 8kHz mono 16-bit con un tono sinusoidale.
func makeBeepWav(freq float64, dur time.Duration) []byte {
	const sr = 8000
	nSamples := int(float64(sr) * dur.Seconds())
	data := make([]byte, nSamples*2)
	amp := 0.6 * 32767.0
	for i := 0; i < nSamples; i++ {
		v := int16(amp * math.Sin(2*math.Pi*freq*float64(i)/float64(sr)))
		binary.LittleEndian.PutUint16(data[i*2:], uint16(v))
	}
	return wavBytes(sr, data)
}

// writeWav scrive un WAV PCM 8kHz mono 16-bit su path.
func writeWav(path string, pcm []byte) error {
	if len(pcm) == 0 {
		// Garantisce comunque un file non-nullo minimo (header) — ma logghiamo.
		slog.Warn("PCM RX vuoto: WAV conterrà solo header")
	}
	return os.WriteFile(path, wavBytes(8000, pcm), 0644)
}

// wavBytes costruisce un container WAV canonico (PCM mono 16-bit).
func wavBytes(sampleRate int, pcm []byte) []byte {
	var b bytes.Buffer
	dataLen := len(pcm)
	byteRate := sampleRate * 2
	b.WriteString("RIFF")
	binary.Write(&b, binary.LittleEndian, uint32(36+dataLen))
	b.WriteString("WAVE")
	b.WriteString("fmt ")
	binary.Write(&b, binary.LittleEndian, uint32(16))
	binary.Write(&b, binary.LittleEndian, uint16(1))  // PCM
	binary.Write(&b, binary.LittleEndian, uint16(1))  // mono
	binary.Write(&b, binary.LittleEndian, uint32(sampleRate))
	binary.Write(&b, binary.LittleEndian, uint32(byteRate))
	binary.Write(&b, binary.LittleEndian, uint16(2))  // block align
	binary.Write(&b, binary.LittleEndian, uint16(16)) // bits/sample
	b.WriteString("data")
	binary.Write(&b, binary.LittleEndian, uint32(dataLen))
	b.Write(pcm)
	return b.Bytes()
}
