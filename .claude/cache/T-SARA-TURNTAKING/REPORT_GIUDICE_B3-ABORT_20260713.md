ca# REPORT GIUDICE — T-SARA-TURNTAKING / GATE-B3-LIVE (2026-07-13)

## VERDETTO
🟡 **GATE-B3-LIVE NON AVVIATO** — STOP per vincolo TAGLIA S #34 al primo checkpoint.
Non è un fallimento del test vocale: è una **non-apertura per budget di context**. Produzione intatta, chiusura pulita.

## PERCHÉ NON APERTO
- Il mandato impone: «A qualunque checkpoint ≥40% context reale → salto a FASE RESTORE+CHIUSURA» + «PRINCIPIO: la finestra termina SEMPRE con pjsua2 ripristinato».
- Context reale al **primo** checkpoint (FASE 0) = **52%** (ctx `8cc2ea9b`, used_pct=52).
- A 52% non è garantibile completare l'intera finestra live (switch pjsua2→Sara-go → chiamata founder → pull WAV → commit → **restore**) senza esaurire il context a metà. Morire a metà finestra lascerebbe **Sara-go (build di test) sul trunk reale** (DID 0972536918) a rispondere a chiamanti veri = scenario peggiore. TAGLIA S esiste per prevenirlo. Quindi GATE-1 non presentato.

## STATO PROVATO (FASE 0, read-only)
- HEAD = `0474dde4` (atteso ✓) — A3 5/5 sigillata resta valida.
- git status = solo effimero `tools/VectCutAPI` (m); unpushed = 0.
- Nessun capitolato/rituale B3 ratificato in `.claude/cache/` → vale il rituale del mandato.

## RESTORE / PRODUZIONE (B4) — verificato, no-op (nessuno switch fatto)
- `ssh imac curl 127.0.0.1:3002/api/voice/voip/status` →
  `{"running":true,"sip":{"registered":true,"reg_status":200,"username":"0972536918","server":"sip.vivavox.it"},"rtp_active":false,"engine":"pjsua2"}`
- `ps` iMac → **ZERO ORFANI TEST** (no regstub/gospike/engine_darwin/main.py --port 3003/VOICE_ENGINE=go).
- Traccar 5062/5090 e trunk non toccati.

## SCORECARD RITUALE (M1-M5)
Non applicabile — il rituale founder (5 mosse) non è stato eseguito perché la finestra non è stata aperta.

## COMMIT
- `2b621118` docs(handoff/B3): NON aperto — STOP TAGLIA S boot 52%, prod pjsua2 intatta.
- Push → origin/master OK, unpushed 0. File nel commit: `HANDOFF.md` + `vos-out/decisions.jsonl` (append-only audit, auto-staging hook noto). Zero file codice/config toccati. Backup #1d `HANDOFF.md.bak-PRE-B3ABORT-20260713-181641` (locale).

## CONTEXT
52% a FASE 0.

## BLOCCO STRUTTURALE (root cause)
Il boot di sessione parte già a ~52% per **overhead**: `HANDOFF.md` ~43k token + CLAUDE.md globale/progetto + 6 rules + inject VOS + MEMORY.md. Nessuna sessione può aprire una finestra live pesante partendo da lì.

## PROSSIMO PASSO (raccomandazione CTO)
1. **Micro-sessione dedicata SOLO al trim-head di HANDOFF.md** (lossless, REGOLA #26: backup #1d → testa ≤40 righe + ultime ~10 entry, corpo storico integrale → `.claude/cache/HANDOFF_ARCHIVE_20260713.md`). È la FASE 4 già differita dalla sessione -d. Obiettivo: boot < 40%.
2. **Poi GATE-B3-LIVE** in sessione fresca con budget sufficiente per finestra + restore. Rituale invariato: 1 chiamata (max 2) al DID 0972536918, 5 mosse (greeting+disclosure / barge-in / prenotazione / silenzio-reprompt / congedo), evidenza WAV Sara-side, restore pjsua2 sempre.

## SERVE DAL FOUNDER
Decisione (yes/no): autorizzo la micro-sessione di trim-head HANDOFF come **precondizione** a B3?
(È l'unico modo per avere il budget di context che il rituale live esige. In alternativa esplicita: forzare B3 ora — ma contraddirebbe TAGLIA S scritto nel mandato stesso.)
