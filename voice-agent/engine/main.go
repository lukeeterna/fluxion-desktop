// T-SARA-MEDIASWAP — motore telefonico Go per Sara (sostituto di pjsua2).
//
// Fa SIP (REGISTER+digest+keepalive) + RTP simmetrico + codec G.711 (PCMA/PCMU),
// riusando il gospike validato LIVE (commit 768e476, diago v0.29.0). Il "cervello"
// (STT+NLU+TTS+FSM) resta in Python; questo processo scambia audio PCM16/8k con
// l'adapter Python (voip_goengine.py) via un ponte TCP locale FRAMED.
//
// Credenziali SOLO da env VOIP_SIP_USER / VOIP_SIP_PASS / VOIP_SIP_SERVER (mai in argv).
//
// PROTOCOLLO PONTE TCP (framed): frame = tipo(1B) + len(2B big-endian) + payload(len B).
//
//	L'engine è CLIENT, si connette a -bridge (default 127.0.0.1:8300).
//	Engine → Python:
//	  0x01 STATUS     payload = JSON stato SIP (registered, reg_status, ...)
//	  0x02 CALL_START payload = caller id (stringa UTF-8); emesso SOLO a media ATTIVO
//	  0x03 AUDIO_RX   payload = 320 byte = 20ms PCM16/8000Hz/mono (little-endian)
//	  0x04 CALL_END   payload = vuoto
//	Python → Engine:
//	  0x10 AUDIO_TX   payload = 320 byte PCM16/8000Hz/mono (little-endian)
//	  0x11 HANGUP     payload = vuoto
//
// PACING & BARGE-IN: la riproduzione RTP verso il chiamante è cadenzata dall'engine
// (clock RTP proprio, 20ms). Python invia AUDIO_TX appena ha audio, senza pacing.
// Il buffer TX interno è cappato a 200ms: se supera, si scartano i frame più vecchi
// (barge-in dal lato Python svuota comunque la sua coda e smette di inviare).
package main

import (
	"bytes"
	"context"
	"encoding/binary"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"log/slog"
	"math"
	"net"
	"os"
	"os/signal"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/emiago/diago"
	"github.com/emiago/diago/audio"
	"github.com/emiago/sipgo"
	"github.com/emiago/sipgo/sip"
)

// Tipi di frame del ponte TCP.
const (
	frameSTATUS         byte = 0x01
	frameCALLSTART      byte = 0x02
	frameAUDIORX        byte = 0x03
	frameCALLEND        byte = 0x04
	frameTRANSFERSTATUS byte = 0x05
	frameAUDIOTX        byte = 0x10
	frameHANGUP         byte = 0x11
	frameTRANSFER       byte = 0x12
)

const (
	frameBytes  = 320 // 20ms PCM16 @ 8kHz mono
	frameMillis = 20
	txCapFrames = 10 // 200ms / 20ms — cap barge-in del buffer TX
)

var (
	fPort     = flag.Int("port", 5080, "porta SIP di bind")
	fBind     = flag.String("bind", "", "host IPv4 di bind (vuoto = auto-detect IPv4 locale; MAI [::]/0.0.0.0)")
	fRTPMin   = flag.Int("rtpmin", 20000, "RTP port range min (dichiarato)")
	fRTPMax   = flag.Int("rtpmax", 20100, "RTP port range max (dichiarato)")
	fExternal = flag.String("external", "", "IP pubblico per SDP/media (NAT Piano B; default vuoto = CGNAT-safe)")
	fBridge   = flag.String("bridge", "127.0.0.1:8300", "host:port adapter Python (engine = client TCP)")
	fSelftest = flag.Bool("selftest", false, "modalità selftest: nessun SIP, echo del ponte TCP per il test locale")
)

func main() {
	flag.Parse()
	slog.SetDefault(slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelInfo})))

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	if *fSelftest {
		if err := runSelftest(ctx); err != nil && !errors.Is(err, context.Canceled) {
			slog.Error("selftest terminato con errore", "error", err)
			os.Exit(1)
		}
		slog.Info("selftest uscita pulita")
		return
	}

	user := os.Getenv("VOIP_SIP_USER")
	pass := os.Getenv("VOIP_SIP_PASS")
	server := os.Getenv("VOIP_SIP_SERVER")
	if user == "" || pass == "" || server == "" {
		slog.Error("env mancanti: servono VOIP_SIP_USER, VOIP_SIP_PASS, VOIP_SIP_SERVER")
		os.Exit(2)
	}

	if err := run(ctx, user, pass, server); err != nil && !errors.Is(err, context.Canceled) {
		slog.Error("engine terminato con errore", "error", err)
		os.Exit(1)
	}
	slog.Info("engine uscita pulita")
}

// autoBindIP apre una dial UDP verso il server SIP e legge il LocalAddr per
// ricavare l'IPv4 locale corretto. Fix #1: MAI [::] né 0.0.0.0 (su Big Sur il
// dual-stack [::] ruba l'IPv4 → "address already in use").
func autoBindIP(server string) (string, error) {
	// Prova risoluzione + dial UDP:5060 verso il server SIP.
	addr := server
	if _, _, err := net.SplitHostPort(server); err != nil {
		addr = net.JoinHostPort(server, "5060")
	}
	conn, err := net.Dial("udp4", addr)
	if err != nil {
		return "", fmt.Errorf("auto-bind dial %s: %w", addr, err)
	}
	defer conn.Close()
	host, _, err := net.SplitHostPort(conn.LocalAddr().String())
	if err != nil {
		return "", err
	}
	if ip := net.ParseIP(host); ip == nil || ip.To4() == nil {
		return "", fmt.Errorf("auto-bind IP non IPv4: %q", host)
	}
	return host, nil
}

func run(ctx context.Context, user, pass, server string) error {
	bind := *fBind
	if bind == "" {
		ip, err := autoBindIP(server)
		if err != nil {
			return fmt.Errorf("fix#1 auto-bind IPv4 fallito: %w", err)
		}
		bind = ip
		slog.Info("fix#1 auto-bind IPv4 rilevato", "bind", bind)
	}
	if bind == "0.0.0.0" || bind == "::" || bind == "[::]" {
		return fmt.Errorf("fix#1 violato: bind %q vietato (dual-stack self-collision Big Sur)", bind)
	}

	// Ponte TCP verso l'adapter Python (engine = client, con retry).
	br := newBridge(*fBridge)
	go br.connectLoop(ctx)

	ua, err := sipgo.NewUA(sipgo.WithUserAgent(user))
	if err != nil {
		return err
	}
	defer ua.Close()

	tr := diago.Transport{
		Transport: "udp",
		BindHost:  bind,
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
			caller := inDialog.InviteRequest.Source()
			slog.Info("INBOUND INVITE", "from", caller, "callid", inDialog.InviteRequest.CallID().Value())
			if err := handleCall(ctx, inDialog, caller, br, tu, server, user, pass); err != nil && !errors.Is(err, io.EOF) {
				slog.Error("errore handler chiamata", "error", err)
			}
		})
		if serveErr != nil && !errors.Is(serveErr, context.Canceled) {
			slog.Error("Serve terminato", "error", serveErr)
		}
	}()

	// REGISTER con keepalive.
	regURI := sip.Uri{}
	if err := sip.ParseUri("sip:"+user+"@"+server, &regURI); err != nil {
		return err
	}
	slog.Info("REGISTER avvio", "uri", "sip:"+user+"@"+server, "port", *fPort, "bind", bind, "external", *fExternal)

	// Nota: emettiamo STATUS(registered) verso Python appena REGISTER ritorna 200.
	// diago.Register blocca fino a errore/ctx done; il 200 iniziale è implicito nel
	// non-errore dei primi cicli → segnaliamo ottimisticamente e correggiamo su errore.
	go func() {
		time.Sleep(1500 * time.Millisecond)
		br.sendStatus(statusJSON(true, 200, user, server))
	}()

	err = tu.Register(ctx, regURI, diago.RegisterOptions{
		Username:      user,
		Password:      pass,
		Expiry:        120 * time.Second,
		RetryInterval: 25 * time.Second,
	})
	if err != nil && !errors.Is(err, context.Canceled) {
		br.sendStatus(statusJSON(false, 0, user, server))
	}
	return err
}

func statusJSON(reg bool, code int, user, server string) []byte {
	b, _ := json.Marshal(map[string]any{
		"registered": reg,
		"reg_status": code,
		"username":   user,
		"server":     server,
	})
	return b
}

// handleCall gestisce una chiamata: answer, negozia media, poi FA IL PONTE audio
// tra RTP (G.711) e il ponte TCP (PCM16/8k). fix #2: CALL_START verso Python SOLO
// quando il media è ATTIVO (dopo che AudioReader/Writer sono pronti).
func handleCall(ctx context.Context, d *diago.DialogServerSession, caller string, br *bridge, dg *diago.Diago, sipServer, sipUser, sipPass string) error {
	d.Trying()
	d.Ringing()
	if err := d.Answer(); err != nil {
		return err
	}
	slog.Info("ANSWERED — negozio media")

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
	remoteAddr := mp.Raddr
	if remoteAddr == "" {
		remoteAddr = caller
	}
	slog.Info("MEDIA negoziato", "payloadType", pt, "codec", mp.Codec.Name, "remote", remoteAddr)

	// Decoder/encoder G.711 ↔ PCM16 (puro-Go, niente CGO/opus).
	dec, err := audio.NewPCMDecoderReader(pt, audioReader)
	if err != nil {
		return err
	}
	enc, err := audio.NewPCMEncoderWriter(pt, audioWriter)
	if err != nil {
		return err
	}

	callCtx, cancelCall := context.WithCancel(ctx)
	defer cancelCall()
	mediaCtx, cancelMedia := context.WithCancel(callCtx)

	var wg sync.WaitGroup
	wg.Add(2)

	// Registra questa chiamata come attiva sul ponte. cancelMedia ferma soltanto Sara RTP;
	// cancelCall termina l'intera chiamata. Il transfer B2BUA usa questa separazione per
	// cedere il media all'operatore senza abbattere la gamba del chiamante.
	call := br.attachCall(cancelCall, cancelMedia, wg.Wait, d, dg, sipServer, sipUser, sipPass)
	defer br.detachCall()

	// fix #2: media ATTIVO → emetti CALL_START.
	br.sendFrame(frameCALLSTART, []byte(caller))
	slog.Info("CALL_START emesso (media attivo)", "caller", caller)

	// RX: RTP(G.711)→PCM16 → ponte TCP AUDIO_RX (in frame da 320B).
	go func() {
		defer wg.Done()
		buf := make([]byte, 4096)
		var carry []byte
		for {
			select {
			case <-mediaCtx.Done():
				return
			default:
			}
			n, rerr := dec.Read(buf)
			if n > 0 {
				carry = append(carry, buf[:n]...)
				for len(carry) >= frameBytes {
					br.sendFrame(frameAUDIORX, carry[:frameBytes])
					carry = carry[frameBytes:]
				}
			}
			if rerr != nil {
				if !errors.Is(rerr, io.EOF) {
					slog.Info("read RX terminato", "reason", rerr.Error())
				}
				cancelCall()
				return
			}
		}
	}()

	// TX: pacing RTP proprio (clock 20ms). Drena il buffer TX (cappato 200ms) e
	// scrive frame PCM16 all'encoder G.711. Silenzio se non c'è audio.
	go func() {
		defer wg.Done()
		ticker := time.NewTicker(frameMillis * time.Millisecond)
		defer ticker.Stop()
		silence := make([]byte, frameBytes)
		lastLog := time.Now()
		for {
			select {
			case <-mediaCtx.Done():
				return
			case <-ticker.C:
				frame := call.popTX()
				if frame == nil {
					frame = silence
					atomic.AddInt64(&call.mRtpSil, 1)
				} else {
					atomic.AddInt64(&call.mRtpVoice, 1)
				}
				if _, werr := enc.Write(frame); werr != nil {
					slog.Warn("TX write errore", "error", werr)
				}
				if time.Since(lastLog) >= time.Second {
					slog.Info("[GATE2R-GO-TX]",
						"rx_audiotx", atomic.LoadInt64(&call.mRxTx),
						"push_acc", atomic.LoadInt64(&call.mPushAcc),
						"push_drop", atomic.LoadInt64(&call.mPushDrop),
						"rtp_voice", atomic.LoadInt64(&call.mRtpVoice),
						"rtp_silence", atomic.LoadInt64(&call.mRtpSil),
						"payloadType", pt,
						"remote", remoteAddr)
					lastLog = time.Now()
				}
			}
		}
	}()

	<-callCtx.Done()
	cancelMedia()
	wg.Wait()
	_ = d.Hangup(context.Background())
	br.sendFrame(frameCALLEND, nil)
	slog.Info("CALL_END emesso")
	return nil
}

// ---------------------------------------------------------------------------
// Ponte TCP
// ---------------------------------------------------------------------------

type activeCall struct {
	mu          sync.Mutex
	txBuf       [][]byte // buffer TX, cappato a txCapFrames (barge-in scarta i più vecchi)
	cancel      context.CancelFunc
	cancelMedia context.CancelFunc
	waitMedia   func()
	dialog      *diago.DialogServerSession
	dg          *diago.Diago
	sipServer   string
	sipUser     string
	sipPass     string

	transferMu   sync.Mutex
	transferring bool
	// GATE2R metriche (atomiche): AUDIO_TX ricevuti da socket, pushTX accettati/scartati.
	mRxTx     int64 // AUDIO_TX ricevuti dal ponte
	mPushAcc  int64 // pushTX accettati (entrati nel buffer)
	mPushDrop int64 // pushTX scartati dal cap txCapFrames
	mRtpVoice int64 // frame RTP scritti NON-silenzio
	mRtpSil   int64 // frame RTP scritti silenzio
}

func (c *activeCall) pushTX(frame []byte) {
	atomic.AddInt64(&c.mRxTx, 1)
	c.mu.Lock()
	defer c.mu.Unlock()
	if len(c.txBuf) >= txCapFrames {
		// Barge-in: scarta i frame più vecchi (mantieni gli ultimi txCapFrames-1).
		dropped := int64(len(c.txBuf) - (txCapFrames - 1))
		atomic.AddInt64(&c.mPushDrop, dropped)
		c.txBuf = c.txBuf[len(c.txBuf)-(txCapFrames-1):]
	}
	f := make([]byte, len(frame))
	copy(f, frame)
	c.txBuf = append(c.txBuf, f)
	atomic.AddInt64(&c.mPushAcc, 1)
}

func (c *activeCall) popTX() []byte {
	c.mu.Lock()
	defer c.mu.Unlock()
	if len(c.txBuf) == 0 {
		return nil
	}
	f := c.txBuf[0]
	c.txBuf = c.txBuf[1:]
	return f
}

func (c *activeCall) clearTX() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.txBuf = nil
}

type bridge struct {
	addr string
	mu   sync.Mutex
	conn net.Conn
	call *activeCall
}

func newBridge(addr string) *bridge { return &bridge{addr: addr} }

func (b *bridge) attachCall(cancel context.CancelFunc, cancelMedia context.CancelFunc, waitMedia func(), dialog *diago.DialogServerSession, dg *diago.Diago, sipServer, sipUser, sipPass string) *activeCall {
	c := &activeCall{
		cancel: cancel, cancelMedia: cancelMedia, waitMedia: waitMedia, dialog: dialog, dg: dg,
		sipServer: sipServer, sipUser: sipUser, sipPass: sipPass,
	}
	b.mu.Lock()
	b.call = c
	b.mu.Unlock()
	return c
}

func (b *bridge) detachCall() {
	b.mu.Lock()
	b.call = nil
	b.mu.Unlock()
}

// connectLoop mantiene la connessione al ponte con retry/backoff e legge i frame
// Python→Engine (AUDIO_TX, HANGUP).
func (b *bridge) connectLoop(ctx context.Context) {
	backoff := 200 * time.Millisecond
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}
		conn, err := net.Dial("tcp", b.addr)
		if err != nil {
			slog.Warn("ponte connect fallito, retry", "addr", b.addr, "error", err, "backoff", backoff)
			select {
			case <-ctx.Done():
				return
			case <-time.After(backoff):
			}
			if backoff < 3*time.Second {
				backoff *= 2
			}
			continue
		}
		slog.Info("ponte connesso", "addr", b.addr)
		backoff = 200 * time.Millisecond
		b.mu.Lock()
		b.conn = conn
		b.mu.Unlock()
		b.readFrames(ctx, conn)
		b.mu.Lock()
		if b.conn == conn {
			b.conn = nil
		}
		b.mu.Unlock()
		conn.Close()
		slog.Warn("ponte disconnesso, riconnetto")
	}
}

func (b *bridge) readFrames(ctx context.Context, conn net.Conn) {
	header := make([]byte, 3)
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}
		if _, err := io.ReadFull(conn, header); err != nil {
			return
		}
		typ := header[0]
		n := binary.BigEndian.Uint16(header[1:3])
		payload := make([]byte, n)
		if n > 0 {
			if _, err := io.ReadFull(conn, payload); err != nil {
				return
			}
		}
		switch typ {
		case frameAUDIOTX:
			b.mu.Lock()
			c := b.call
			b.mu.Unlock()
			if c != nil && len(payload) == frameBytes {
				c.pushTX(payload)
			}
		case frameHANGUP:
			slog.Info("HANGUP ricevuto da Python")
			b.mu.Lock()
			c := b.call
			b.mu.Unlock()
			if c != nil {
				c.clearTX()
				if c.cancel != nil {
					c.cancel()
				}
			}
		case frameTRANSFER:
			b.mu.Lock()
			c := b.call
			b.mu.Unlock()
			if c == nil {
				b.sendTransferStatus("no_route", 0, "no active call")
				continue
			}
			// REFER can wait for NOTIFY: never block the bridge reader.
			go c.beginTransfer(string(payload), b)
		default:
			slog.Warn("frame Python ignoto", "type", typ, "len", n)
		}
	}
}

type transferStatus struct {
	Status string `json:"status"`
	Code   int    `json:"code,omitempty"`
	Detail string `json:"detail,omitempty"`
}

func (b *bridge) sendTransferStatus(status string, code int, detail string) {
	payload, _ := json.Marshal(transferStatus{Status: status, Code: code, Detail: detail})
	b.sendFrame(frameTRANSFERSTATUS, payload)
}

// normalizeTransferDestination accepts phone-like values loaded from trusted FLUXION
// configuration only. SIP URIs, domains, headers and arbitrary caller-controlled text
// are rejected. The SIP domain is always supplied separately by VOIP_SIP_SERVER.
func normalizeTransferDestination(raw string) (string, error) {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return "", errors.New("empty transfer destination")
	}
	var digits strings.Builder
	for _, r := range raw {
		switch {
		case r >= '0' && r <= '9':
			digits.WriteRune(r)
		case r == '+' || r == ' ' || r == '-' || r == '(' || r == ')' || r == '.' || r == '/':
			// Formatting characters only.
		default:
			return "", fmt.Errorf("invalid transfer destination character %q", r)
		}
	}
	out := digits.String()
	if len(out) < 6 || len(out) > 15 {
		return "", fmt.Errorf("invalid transfer destination length: %d", len(out))
	}
	return out, nil
}

func mapTransferStatus(code int) string {
	switch {
	case code >= 100 && code < 200:
		return "progress"
	case code >= 200 && code < 300:
		return "answered"
	case code == 486:
		return "busy"
	case code == 408 || code == 480:
		return "no_answer"
	case code == 404 || code == 484:
		return "no_route"
	default:
		return "failed"
	}
}

func (c *activeCall) beginTransfer(raw string, b *bridge) {
	c.transferMu.Lock()
	if c.transferring {
		c.transferMu.Unlock()
		b.sendTransferStatus("failed", 409, "transfer already in progress")
		return
	}
	c.transferring = true
	c.transferMu.Unlock()
	defer func() {
		c.transferMu.Lock()
		c.transferring = false
		c.transferMu.Unlock()
	}()

	destination, err := normalizeTransferDestination(raw)
	if err != nil {
		slog.Warn("TRANSFER destinazione rifiutata", "error", err)
		b.sendTransferStatus("invalid", 0, "invalid trusted destination")
		return
	}
	if c.dialog == nil || strings.TrimSpace(c.sipServer) == "" {
		b.sendTransferStatus("no_route", 0, "missing active SIP dialog or server")
		return
	}

	if c.dg == nil {
		b.sendTransferStatus("no_route", 0, "missing SIP engine")
		return
	}

	var recipient sip.Uri
	if err := sip.ParseUri("sip:"+destination+"@"+c.sipServer, &recipient); err != nil {
		b.sendTransferStatus("invalid", 0, "cannot build trusted SIP destination")
		return
	}

	// A two-leg B2BUA bridge is authoritative for live transfer. Unlike REFER,
	// InviteBridge returns only after the outbound operator leg has answered.
	callBridge := diago.NewBridge()
	callBridge.WaitDialogsNum = 3 // prevent automatic proxy until Sara has released RTP
	if err := callBridge.AddDialogSession(c.dialog); err != nil {
		b.sendTransferStatus("failed", 0, "cannot attach caller leg")
		return
	}

	inviteCtx, cancelInvite := context.WithTimeout(context.Background(), 25*time.Second)
	defer cancelInvite()
	lastCode := 0
	b.sendTransferStatus("trying", 0, "")
	slog.Info("TRANSFER B2BUA outbound INVITE", "destination_digits", len(destination))

	outDialog, err := c.dg.InviteBridge(inviteCtx, recipient, &callBridge, diago.InviteOptions{
		Originator: c.dialog,
		Username:   c.sipUser,
		Password:   c.sipPass,
		OnResponse: func(res *sip.Response) error {
			if res == nil {
				return nil
			}
			lastCode = res.StatusCode
			status := mapTransferStatus(lastCode)
			if status == "progress" || status == "answered" {
				b.sendTransferStatus(status, lastCode, "")
			}
			return nil
		},
	})
	if err != nil {
		status := mapTransferStatus(lastCode)
		if inviteCtx.Err() != nil {
			status, lastCode = "no_answer", 408
		} else if status == "progress" || status == "answered" {
			status = "failed"
		}
		b.sendTransferStatus(status, lastCode, "outbound operator leg not connected")
		slog.Warn("TRANSFER B2BUA INVITE fallito", "status", status, "sip_status", lastCode, "error", err)
		return
	}
	defer func() {
		_ = outDialog.Hangup(context.Background())
		_ = outDialog.Close()
	}()

	// Operator answered. Stop Sara media before proxying the same inbound dialog.
	// StopRTP unblocks any reader/writer currently owned by Sara; waitMedia closes
	// the handoff race before Bridge.ProxyMedia takes ownership of both RTP streams.
	c.clearTX()
	if c.cancelMedia != nil {
		c.cancelMedia()
	}
	_ = c.dialog.Media().StopRTP(2, 0)
	if c.waitMedia != nil {
		c.waitMedia()
	}

	b.sendTransferStatus("connected", 200, "operator leg answered; media bridge active")
	slog.Info("TRANSFER CONNECTED — B2BUA media proxy")
	if err := callBridge.ProxyMedia(); err != nil && !errors.Is(err, io.EOF) {
		slog.Warn("TRANSFER media proxy terminato", "error", err)
	}
	if c.cancel != nil {
		c.cancel()
	}
}

func (b *bridge) sendFrame(typ byte, payload []byte) {
	b.mu.Lock()
	conn := b.conn
	b.mu.Unlock()
	if conn == nil {
		return
	}
	var hdr [3]byte
	hdr[0] = typ
	binary.BigEndian.PutUint16(hdr[1:3], uint16(len(payload)))
	var frame bytes.Buffer
	frame.Write(hdr[:])
	frame.Write(payload)
	if _, err := conn.Write(frame.Bytes()); err != nil {
		slog.Warn("ponte write errore", "type", typ, "error", err)
	}
}

func (b *bridge) sendStatus(payload []byte) { b.sendFrame(frameSTATUS, payload) }

// ---------------------------------------------------------------------------
// Selftest engine-side: nessun SIP. Si connette al ponte, emette CALL_START +
// un tono come sequenza di AUDIO_RX, e ri-riproduce (echo) gli AUDIO_TX ricevuti
// verso stderr come conteggio. Serve a validare il ponte TCP end-to-end quando
// l'adapter Python gira il proprio selftest. (Il selftest PRIMARIO è lato Python.)
// ---------------------------------------------------------------------------

func runSelftest(ctx context.Context) error {
	slog.Info("SELFTEST engine: connessione al ponte", "addr", *fBridge)
	conn, err := net.Dial("tcp", *fBridge)
	if err != nil {
		return fmt.Errorf("selftest: ponte non raggiungibile su %s: %w", *fBridge, err)
	}
	defer conn.Close()

	// Emetti CALL_START.
	writeFrame(conn, frameCALLSTART, []byte("selftest-engine"))

	// Emetti 1s di tono 440Hz come 50 frame AUDIO_RX da 320B, cadenzati 20ms.
	tone := makeTone(440.0, 50)
	go func() {
		ticker := time.NewTicker(frameMillis * time.Millisecond)
		defer ticker.Stop()
		for _, f := range tone {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				writeFrame(conn, frameAUDIORX, f)
			}
		}
		time.Sleep(500 * time.Millisecond)
		writeFrame(conn, frameCALLEND, nil)
	}()

	// Conta gli AUDIO_TX di ritorno.
	header := make([]byte, 3)
	var txCount int
	deadline := time.Now().Add(10 * time.Second)
	conn.SetReadDeadline(deadline)
	for {
		if _, err := io.ReadFull(conn, header); err != nil {
			break
		}
		n := binary.BigEndian.Uint16(header[1:3])
		payload := make([]byte, n)
		if n > 0 {
			if _, err := io.ReadFull(conn, payload); err != nil {
				break
			}
		}
		if header[0] == frameAUDIOTX {
			txCount++
		}
	}
	slog.Info("SELFTEST engine done", "audio_tx_ricevuti", txCount)
	return nil
}

func writeFrame(conn net.Conn, typ byte, payload []byte) {
	var hdr [3]byte
	hdr[0] = typ
	binary.BigEndian.PutUint16(hdr[1:3], uint16(len(payload)))
	conn.Write(hdr[:])
	if len(payload) > 0 {
		conn.Write(payload)
	}
}

func makeTone(freq float64, nFrames int) [][]byte {
	const sr = 8000
	samplesPerFrame := frameBytes / 2
	frames := make([][]byte, 0, nFrames)
	amp := 0.6 * 32767.0
	idx := 0
	for f := 0; f < nFrames; f++ {
		frame := make([]byte, frameBytes)
		for i := 0; i < samplesPerFrame; i++ {
			v := int16(amp * math.Sin(2*math.Pi*freq*float64(idx)/float64(sr)))
			binary.LittleEndian.PutUint16(frame[i*2:], uint16(v))
			idx++
		}
		frames = append(frames, frame)
	}
	return frames
}
