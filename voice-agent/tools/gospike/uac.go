package main

import (
	"bytes"
	"context"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"math"
	"net"
	"os"
	"path/filepath"
	"time"

	"github.com/emiago/diago"
	"github.com/emiago/diago/audio"
	"github.com/emiago/sipgo"
	"github.com/emiago/sipgo/sip"
)

// runUAC — modalita harness GATE A3 (T-SARA-TURNTAKING): INVITE diretto a target
// (no REGISTER); all'answer inietta un WAV utterance verso il chiamato (Sara), OPZIONALMENTE
// rimixa nel proprio TX il RX ricevuto attenuato (eco di linea simulata, -echo), e cattura
// dual-stream rx/tx/mix.wav + timeline SOLO sotto SARA_TEST_CAPTURE=1 (default OFF).
// Il comportamento UAS di default (run) resta intatto: attivo solo con -call.
//
// Differenza chiave vs GATE 2R: la TX non è più delegata a PlaybackCreate ma gestita
// direttamente (AudioWriter+encoder) così da poter MIXARE eco + inject temporizzato,
// mantenendo il pacing 1:1 col RX (stesso pattern provato dell'engine: 1 frame TX per
// ogni frame RX letto → timing RTP corretto senza clock separato).
func runUAC(ctx context.Context, user, target string) error {
	ua, err := sipgo.NewUA(sipgo.WithUserAgent(user))
	if err != nil {
		return err
	}
	defer ua.Close()

	tr := diago.Transport{Transport: "udp", BindHost: *fBind, BindPort: *fPort}
	if *fExternal != "" {
		tr.ExternalHost = *fExternal
		if ip := net.ParseIP(*fExternal); ip != nil {
			tr.MediaExternalIP = ip
		}
	}
	tu := diago.NewDiago(ua, diago.WithTransport(tr))

	recipient := sip.Uri{}
	if err := sip.ParseUri(target, &recipient); err != nil {
		return err
	}
	slog.Info("UAC INVITE", "target", target, "bind", *fBind, "port", *fPort)

	callCtx, cancelCall := context.WithCancel(ctx)
	defer cancelCall()

	d, err := tu.Invite(callCtx, recipient, diago.InviteOptions{Headers: []sip.Header{}})
	if err != nil {
		return err
	}
	defer d.Hangup(context.Background())
	slog.Info("UAC ANSWERED — media attivo")

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
	slog.Info("UAC MEDIA negoziato", "payloadType", pt, "codec", mp.Codec.Name)

	dec, err := audio.NewPCMDecoderReader(pt, audioReader)
	if err != nil {
		return err
	}
	enc, err := audio.NewPCMEncoderWriter(pt, audioWriter)
	if err != nil {
		return err
	}

	// Utterance (WAV → PCM16 8k mono) da iniettare SOPRA il parlato di Sara.
	var utterPCM []byte
	if *fInjectWav != "" {
		raw, rerr := os.ReadFile(*fInjectWav)
		if rerr != nil {
			slog.Warn("UAC injectwav read fallito, uso tono di test", "error", rerr)
			utterPCM = beepPCM(300.0, 3*time.Second)
		} else {
			utterPCM = wavToPCM(raw)
		}
	} else {
		utterPCM = beepPCM(300.0, 3*time.Second)
	}

	// Parametri echo-sim + inject.
	echoGain := 0.0
	if *fEchoDB != 0 {
		echoGain = math.Pow(10, *fEchoDB/20.0) // es. -15dB → 0.178
	}
	injectStartSample := int64(*fInjectAt) * 8 // ms → campioni @8kHz
	utterSamples := int64(len(utterPCM) / 2)
	slog.Info("UAC harness config", "echo_db", *fEchoDB, "echo_gain", fmt.Sprintf("%.3f", echoGain),
		"inject_at_ms", *fInjectAt, "utter_samples", utterSamples)

	// Capture dual-stream (SOLO sotto SARA_TEST_CAPTURE=1).
	capture := os.Getenv("SARA_TEST_CAPTURE") == "1"
	var rxBuf, txBuf bytes.Buffer // PCM16 LE accumulato
	var timeline []string
	if capture {
		slog.Info("UAC capture ATTIVO (SARA_TEST_CAPTURE=1)", "dir", *fCaptureDir)
	}

	// Hangup pulito a fine durata.
	go func() {
		select {
		case <-time.After(time.Duration(*fDur) * time.Second):
			slog.Info("UAC durata max — hangup")
			cancelCall()
		case <-callCtx.Done():
		}
	}()

	buf := make([]byte, 4096)
	txFrame := make([]byte, 0, 4096)
	var totFrames, totBytes int64
	var txSample int64 // campioni TX emessi (per schedulare l'inject)
	var secSamples int64
	var secSumSq, maxRMS float64
	lastLog := time.Now()
	start := time.Now()
	for {
		select {
		case <-callCtx.Done():
			goto done
		default:
		}
		n, rerr := dec.Read(buf)
		if n > 0 {
			totFrames++
			totBytes += int64(n)
			for i := 0; i+1 < n; i += 2 {
				sm := int16(binary.LittleEndian.Uint16(buf[i : i+2]))
				secSumSq += float64(sm) * float64(sm)
				secSamples++
			}
			if capture {
				rxBuf.Write(buf[:n])
			}

			// Costruisci il frame TX: eco(rx*gain) + inject(utterance schedulata).
			// Stessa lunghezza n del RX → pacing 1:1 col clock RTP (pattern engine).
			if cap(txFrame) < n {
				txFrame = make([]byte, n)
			}
			txFrame = txFrame[:n]
			for i := 0; i+1 < n; i += 2 {
				var acc float64
				if echoGain > 0 {
					rxs := int16(binary.LittleEndian.Uint16(buf[i : i+2]))
					acc += float64(rxs) * echoGain
				}
				si := txSample + int64(i/2)
				if si >= injectStartSample && si < injectStartSample+utterSamples {
					off := (si - injectStartSample) * 2
					us := int16(binary.LittleEndian.Uint16(utterPCM[off : off+2]))
					acc += float64(us)
				}
				binary.LittleEndian.PutUint16(txFrame[i:i+2], uint16(clip16(acc)))
			}
			txSample += int64(n / 2)
			if _, werr := enc.Write(txFrame); werr != nil {
				slog.Warn("UAC TX write errore", "error", werr)
			}
			if capture {
				txBuf.Write(txFrame)
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
			el := time.Since(start).Seconds()
			injecting := txSample >= injectStartSample && txSample < injectStartSample+utterSamples
			slog.Info("UAC RX", "t", fmt.Sprintf("%.1fs", el), "rms", int(rms), "tot_bytes", totBytes, "injecting", injecting)
			if capture {
				timeline = append(timeline, fmt.Sprintf("| %5.1f | %5d | %v |", el, int(rms), injecting))
			}
			lastLog = time.Now()
			secSamples, secSumSq = 0, 0
		}
		if rerr != nil {
			if !errors.Is(rerr, io.EOF) {
				slog.Info("UAC read RX terminato", "reason", rerr.Error())
			}
			goto done
		}
	}
done:
	// -wav (RX): compat GATE 2R.
	if werr := writeWav(*fWav, rxBuf.Bytes()); werr != nil {
		slog.Error("UAC scrittura WAV RX fallita", "error", werr)
	}
	if capture {
		writeCaptureArtifacts(*fCaptureDir, rxBuf.Bytes(), txBuf.Bytes(), timeline,
			*fEchoDB, *fInjectAt, int(maxRMS), totFrames)
	}
	slog.Info("UAC CALL END", "tot_frames_rx", totFrames, "tot_bytes_rx", totBytes,
		"rms_max", int(maxRMS), "wav", *fWav, "capture", capture)
	return nil
}

// clip16 satura un float su int16.
func clip16(v float64) uint16 {
	if v > 32767 {
		v = 32767
	} else if v < -32768 {
		v = -32768
	}
	return uint16(int16(v))
}

// beepPCM genera PCM16 8k mono (senza header) — tono sinusoidale.
func beepPCM(freq float64, dur time.Duration) []byte {
	const sr = 8000
	nSamples := int(float64(sr) * dur.Seconds())
	data := make([]byte, nSamples*2)
	amp := 0.6 * 32767.0
	for i := 0; i < nSamples; i++ {
		v := int16(amp * math.Sin(2*math.Pi*freq*float64(i)/float64(sr)))
		binary.LittleEndian.PutUint16(data[i*2:], uint16(v))
	}
	return data
}

// wavToPCM estrae il payload PCM16 dal chunk "data" di un WAV canonico.
// Robusto a chunk extra: scandisce fino a trovare "data". Fallback: salta 44B header.
func wavToPCM(raw []byte) []byte {
	if len(raw) < 44 || !bytes.HasPrefix(raw, []byte("RIFF")) {
		return raw
	}
	// Cerca il chunk "data".
	i := 12 // dopo "RIFF"+size(4)+"WAVE"
	for i+8 <= len(raw) {
		id := string(raw[i : i+4])
		sz := int(binary.LittleEndian.Uint32(raw[i+4 : i+8]))
		body := i + 8
		if id == "data" {
			end := body + sz
			if end > len(raw) || sz <= 0 {
				end = len(raw)
			}
			return raw[body:end]
		}
		i = body + sz
		if sz%2 == 1 {
			i++ // padding chunk dispari
		}
	}
	if len(raw) > 44 {
		return raw[44:]
	}
	return nil
}

// writeCaptureArtifacts scrive rx.wav / tx.wav / mix.wav (stereo L=rx R=tx) + harness_timeline.md.
func writeCaptureArtifacts(dir string, rxPCM, txPCM []byte, timeline []string, echoDB float64, injectAt, maxRMS int, frames int64) {
	if dir == "" {
		dir = "."
	}
	if err := os.MkdirAll(dir, 0755); err != nil {
		slog.Error("UAC capture mkdir fallito", "error", err, "dir", dir)
		return
	}
	rxPath := filepath.Join(dir, "rx.wav")
	txPath := filepath.Join(dir, "tx.wav")
	mixPath := filepath.Join(dir, "mix.wav")
	if err := os.WriteFile(rxPath, wavBytes(8000, rxPCM), 0644); err != nil {
		slog.Error("UAC rx.wav fallito", "error", err)
	}
	if err := os.WriteFile(txPath, wavBytes(8000, txPCM), 0644); err != nil {
		slog.Error("UAC tx.wav fallito", "error", err)
	}
	if err := os.WriteFile(mixPath, wavBytesStereo(8000, rxPCM, txPCM), 0644); err != nil {
		slog.Error("UAC mix.wav fallito", "error", err)
	}
	// Timeline markdown (RMS + injecting per secondo).
	var b bytes.Buffer
	fmt.Fprintf(&b, "# Harness timeline (UAC) — GATE A3\n\n")
	fmt.Fprintf(&b, "- echo_db: %.1f (0=OFF) · inject_at_ms: %d · rx_rms_max: %d · rx_frames: %d\n", echoDB, injectAt, maxRMS, frames)
	fmt.Fprintf(&b, "- rx.wav = audio ricevuto da Sara (TX di Sara) · tx.wav = audio inviato dall'harness (eco+inject) · mix.wav = stereo L=rx R=tx\n\n")
	fmt.Fprintf(&b, "| t(s) | rx_rms | injecting |\n|------|--------|-----------|\n")
	for _, row := range timeline {
		b.WriteString(row)
		b.WriteByte('\n')
	}
	if err := os.WriteFile(filepath.Join(dir, "harness_timeline.md"), b.Bytes(), 0644); err != nil {
		slog.Error("UAC harness_timeline.md fallito", "error", err)
	}
	slog.Info("UAC capture scritta", "rx", rxPath, "tx", txPath, "mix", mixPath)
}

// wavBytesStereo costruisce un WAV PCM 16-bit STEREO da due tracce mono (L, R).
// Le tracce vengono allineate alla lunghezza maggiore (zero-pad).
func wavBytesStereo(sampleRate int, left, right []byte) []byte {
	nL := len(left) / 2
	nR := len(right) / 2
	n := nL
	if nR > n {
		n = nR
	}
	inter := make([]byte, n*4)
	for i := 0; i < n; i++ {
		var l, r uint16
		if i < nL {
			l = binary.LittleEndian.Uint16(left[i*2 : i*2+2])
		}
		if i < nR {
			r = binary.LittleEndian.Uint16(right[i*2 : i*2+2])
		}
		binary.LittleEndian.PutUint16(inter[i*4:], l)
		binary.LittleEndian.PutUint16(inter[i*4+2:], r)
	}
	var b bytes.Buffer
	dataLen := len(inter)
	byteRate := sampleRate * 2 * 2 // 2 canali * 2 byte
	b.WriteString("RIFF")
	binary.Write(&b, binary.LittleEndian, uint32(36+dataLen))
	b.WriteString("WAVE")
	b.WriteString("fmt ")
	binary.Write(&b, binary.LittleEndian, uint32(16))
	binary.Write(&b, binary.LittleEndian, uint16(1))  // PCM
	binary.Write(&b, binary.LittleEndian, uint16(2))  // stereo
	binary.Write(&b, binary.LittleEndian, uint32(sampleRate))
	binary.Write(&b, binary.LittleEndian, uint32(byteRate))
	binary.Write(&b, binary.LittleEndian, uint16(4))  // block align (2ch*2B)
	binary.Write(&b, binary.LittleEndian, uint16(16)) // bits/sample
	b.WriteString("data")
	binary.Write(&b, binary.LittleEndian, uint32(dataLen))
	b.Write(inter)
	return b.Bytes()
}
