package main

import (
	"bytes"
	"context"
	"encoding/binary"
	"errors"
	"io"
	"log/slog"
	"math"
	"net"
	"os"
	"time"

	"github.com/emiago/diago"
	"github.com/emiago/diago/audio"
	"github.com/emiago/sipgo"
	"github.com/emiago/sipgo/sip"
)

// runUAC — modalita harness GATE2R: INVITE diretto a target (no REGISTER); all'answer
// inietta un WAV utterance verso il chiamato (Sara) e REGISTRA l'audio RX su -wav.
// Il comportamento UAS di default (run) resta intatto: attivo solo con -call.
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
	pt := mp.Codec.PayloadType
	slog.Info("UAC MEDIA negoziato", "payloadType", pt, "codec", mp.Codec.Name)

	// Utterance (WAV) da iniettare: playback gestisce encode+pacing verso il codec.
	var utter []byte
	if *fInjectWav != "" {
		utter, err = os.ReadFile(*fInjectWav)
		if err != nil {
			slog.Warn("UAC injectwav read fallito, uso tono di test", "error", err)
			utter = makeBeepWav(300.0, 3*time.Second)
		}
	} else {
		utter = makeBeepWav(300.0, 3*time.Second)
	}
	go func() {
		time.Sleep(500 * time.Millisecond) // lascia partire il greeting di Sara
		if pb, perr := d.PlaybackCreate(); perr == nil {
			if _, werr := pb.Play(bytes.NewReader(utter), "audio/wav"); werr != nil {
				slog.Warn("UAC inject playback errore", "error", werr)
			} else {
				slog.Info("UAC utterance iniettata", "bytes", len(utter))
			}
		} else {
			slog.Warn("UAC PlaybackCreate errore", "error", perr)
		}
	}()

	dec, err := audio.NewPCMDecoderReader(pt, audioReader)
	if err != nil {
		return err
	}
	go func() {
		select {
		case <-time.After(time.Duration(*fDur) * time.Second):
			slog.Info("UAC durata max — hangup")
			cancelCall()
		case <-callCtx.Done():
		}
	}()

	var wavBuf bytes.Buffer
	buf := make([]byte, 4096)
	var totFrames, totBytes int64
	var secSamples int64
	var secSumSq, maxRMS float64
	lastLog := time.Now()
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
			wavBuf.Write(buf[:n])
		}
		if time.Since(lastLog) >= time.Second {
			rms := 0.0
			if secSamples > 0 {
				rms = math.Sqrt(secSumSq / float64(secSamples))
			}
			if rms > maxRMS {
				maxRMS = rms
			}
			slog.Info("UAC RX", "rms", int(rms), "tot_bytes", totBytes)
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
	if werr := writeWav(*fWav, wavBuf.Bytes()); werr != nil {
		slog.Error("UAC scrittura WAV fallita", "error", werr)
	}
	slog.Info("UAC CALL END", "tot_frames_rx", totFrames, "tot_bytes_rx", totBytes,
		"rms_max", int(maxRMS), "wav", *fWav, "wav_pcm_bytes", wavBuf.Len())
	return nil
}
