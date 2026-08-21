package main

import "testing"

func TestNormalizeTransferDestination(t *testing.T) {
	cases := []struct {
		in, want string
		ok       bool
	}{
		{"+39 333-123-4567", "393331234567", true},
		{"06 1234 5678", "0612345678", true},
		{"sip:3331234567@evil.example", "", false},
		{"3331234567;transport=tcp", "", false},
		{"123", "", false},
	}
	for _, tc := range cases {
		got, err := normalizeTransferDestination(tc.in)
		if tc.ok && (err != nil || got != tc.want) {
			t.Fatalf("%q => %q, %v", tc.in, got, err)
		}
		if !tc.ok && err == nil {
			t.Fatalf("%q unexpectedly accepted as %q", tc.in, got)
		}
	}
}

func TestMapTransferStatus(t *testing.T) {
	cases := map[int]string{
		100: "progress", 180: "progress", 200: "answered", 202: "answered",
		408: "no_answer", 480: "no_answer", 486: "busy",
		404: "no_route", 484: "no_route", 500: "failed",
	}
	for code, want := range cases {
		if got := mapTransferStatus(code); got != want {
			t.Fatalf("%d => %s, want %s", code, got, want)
		}
	}
}
