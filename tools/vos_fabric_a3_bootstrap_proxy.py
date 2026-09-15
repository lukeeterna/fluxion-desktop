#!/usr/bin/env python3
"""Ephemeral VOS A3 bootstrap CONNECT relay.

Source-IP restricted, CONNECT:443 only.  Uses blocking sockets with select-driven
backpressure so large signed package downloads cannot be truncated by nonblocking
sendall semantics.  This is transport only; it is not an authorization boundary.
"""
import os
import select
import socket
import socketserver

BIND = ("192.168.64.1", int(os.environ["VOS_PROXY_PORT"]))
ALLOWED_SOURCE = os.environ["VOS_GUEST_IP"]


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        if self.client_address[0] != ALLOWED_SOURCE:
            return
        self.connection.settimeout(30)
        line = self.rfile.readline(8192).decode("ascii", "replace").strip().split()
        if len(line) != 3 or line[0].upper() != "CONNECT" or ":" not in line[1]:
            return
        host, port_text = line[1].rsplit(":", 1)
        try:
            port = int(port_text)
        except ValueError:
            return
        if port != 443:
            self.wfile.write(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            return
        print("CONNECT_HOST=%s:443" % host, flush=True)
        while True:
            header = self.rfile.readline(8192)
            if header in (b"\r\n", b"\n", b""):
                break
        try:
            upstream = socket.create_connection((host, 443), timeout=30)
        except OSError as exc:
            print("UPSTREAM_ERROR=%s" % type(exc).__name__, flush=True)
            self.wfile.write(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            return
        with upstream:
            # After CONNECT succeeds both sockets stay blocking. select() gates reads;
            # sendall() then supplies normal TCP backpressure instead of spuriously
            # closing a tunnel on BlockingIOError during large binary transfers.
            self.connection.settimeout(None)
            upstream.settimeout(None)
            self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            sockets = [self.connection, upstream]
            while True:
                readable, _, exceptional = select.select(sockets, [], sockets, 180)
                if exceptional or not readable:
                    return
                for source in readable:
                    destination = upstream if source is self.connection else self.connection
                    try:
                        payload = source.recv(65536)
                    except OSError:
                        return
                    if not payload:
                        return
                    try:
                        destination.sendall(payload)
                    except OSError:
                        return


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Server(BIND, Handler) as server:
        print("READY=%s:%d source=%s" % (BIND[0], BIND[1], ALLOWED_SOURCE), flush=True)
        server.serve_forever()
