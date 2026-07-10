// regstub — mini registrar SIP per il rig di test A3 (T-SARA-TURNTAKING).
//
// Scopo: quando l'engine Go (voice-agent/engine) gira in locale puntato a un
// registrar DUMMY (VOIP_SIP_SERVER=127.0.0.1:<porta>), senza qualcuno che risponda
// al REGISTER va in Timer_B → exit rc=1 → restart → "bind in use" ogni ~1-2 min.
// Questo stub risponde 200 OK a REGISTER (con Contact rispecchiato + Expires) e a
// OPTIONS, così l'engine si registra e resta UP → finestra stabile per i test A3.
//
// Niente media, niente auth, niente stato. Solo loopback. NON tocca il trunk EHIWEB.
// Stack: emiago/sipgo v1.4.3 (già dep del modulo fluxion/gospike).
//
// Uso:
//   ./regstub -bind 127.0.0.1 -port 5062
// e lanciare l'engine con VOIP_SIP_SERVER=127.0.0.1:5062.
package main

import (
	"context"
	"errors"
	"flag"
	"log/slog"
	"net"
	"os"
	"os/signal"
	"strconv"
	"syscall"

	"github.com/emiago/sipgo"
	"github.com/emiago/sipgo/sip"
)

var (
	fBind   = flag.String("bind", "127.0.0.1", "host IPv4 di bind (solo loopback per il rig)")
	fPort   = flag.Int("port", 5062, "porta UDP di ascolto SIP")
	fExpiry = flag.Int("expiry", 120, "Expires (s) restituito nelle 200 OK REGISTER")
)

func main() {
	flag.Parse()
	slog.SetDefault(slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelInfo})))

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer cancel()

	ua, err := sipgo.NewUA(sipgo.WithUserAgent("fluxion-regstub"))
	if err != nil {
		slog.Error("NewUA fallito", "error", err)
		os.Exit(1)
	}
	defer ua.Close()

	srv, err := sipgo.NewServer(ua)
	if err != nil {
		slog.Error("NewServer fallito", "error", err)
		os.Exit(1)
	}

	expires := strconv.Itoa(*fExpiry)

	srv.OnRegister(func(req *sip.Request, tx sip.ServerTransaction) {
		res := sip.NewResponseFromRequest(req, 200, "OK", nil)
		// Rispecchia il/i Contact del client: la sua binding risulta "accettata".
		sip.CopyHeaders("Contact", req, res)
		res.AppendHeader(sip.NewHeader("Expires", expires))
		if err := tx.Respond(res); err != nil {
			slog.Error("REGISTER respond fallito", "error", err)
			return
		}
		slog.Info("REGISTER 200 OK", "callid", req.CallID().Value(), "expires", expires)
	})

	srv.OnOptions(func(req *sip.Request, tx sip.ServerTransaction) {
		res := sip.NewResponseFromRequest(req, 200, "OK", nil)
		if err := tx.Respond(res); err != nil {
			slog.Error("OPTIONS respond fallito", "error", err)
			return
		}
		slog.Info("OPTIONS 200 OK", "callid", req.CallID().Value())
	})

	addr := net.JoinHostPort(*fBind, strconv.Itoa(*fPort))
	slog.Info("regstub in ascolto", "addr", addr, "expiry", *fExpiry)
	if err := srv.ListenAndServe(ctx, "udp", addr); err != nil && !errors.Is(err, context.Canceled) {
		slog.Error("ListenAndServe terminato", "error", err)
		os.Exit(1)
	}
	slog.Info("regstub uscita pulita")
}
