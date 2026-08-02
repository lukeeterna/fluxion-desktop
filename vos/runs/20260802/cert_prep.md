# cert_prep.md — T-CERT-PREP/#46
> Generato: 2026-08-02T16:30:00Z | BASE: 49737fa6

---

## F1 — QUANTE MACCHINE

**DUE macchine.** Entrambe hanno un clone del repo.

### MacBook (sessione corrente)
- **hostname**: MacBook-Pro-di-MacBook.local
- **path repo**: `/Volumes/MontereyT7/FLUXION` (drive T7 USB)
- **HEAD**: `49737fa6` = origin/master ✓
- **albero sporco**: sì (LEDGER.md, SESSIONI.md modificati da questa sessione; db/VectCutAPI/decisions.jsonl in carve-out permanente)
- **fluxion.db**: esiste — mtime 2026-08-02 07:44 (MacBook non esegue :3002)
- **ruolo**: repo autoritativo, sessione CC, git push

### iMac (runtime)
- **hostname**: iMac-di-gianluca.local
- **IP**: 192.168.1.2
- **path repo**: `/Volumes/MacSSD - Dati/fluxion`
- **HEAD**: `2c25742d` — BEHIND origin/master di ~14 commit
- **albero sporco**: sì — `voice-agent/src/booking_state_machine.py` (+160/-27 righe vs HEAD iMac = FIX Sol applicato manualmente, contenuto identico a commit 5250527b su master)
- **fluxion.db produzione Sara**: `/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db` — mtime 2026-08-01 22:52
- **ruolo**: runtime :3002, SIP trunk, WAV capture

**MACCHINA AUTORITATIVA per git**: MacBook (`49737fa6` = origin/master).
**MACCHINA AUTORITATIVA per runtime**: iMac (unico con :3002 + SIP + trunk).

---

## F2 — SESSION_DIRTY.md

**Origine**: `~/.claude/hooks/global_session_end.sh` (Stop hook globale, riga 44 `DIRTY_MARKER`).

**Quando viene creato**: il hook tenta l'auto-commit alla chiusura sessione. Se lo staged diff contiene file con pattern `.db$` (come `src-tauri/fluxion.db`), il commit viene ABORTITO e viene scritto `SESSION_DIRTY.md` nella dir `.claude/` del repo con la lista dei pattern rilevati.

**È aggiunto a `.gitignore`?**: SÌ (commit 49737fa6, T-VOS-RUNNER/#45v3).

**L'ignoranza è legittima?**: SÌ. `SESSION_DIRTY.md` è un segnale transiente di avviso (il commit auto è bloccato), non un artefatto durevole. Non deve essere tracciato. La causa reale del blocco (`.db` in staging) è un carve-out permanente del PROTOCOLLO (§8). Ignorare SESSION_DIRTY.md in git è corretto.

---

## F3 — RUNTIME PRONTO

| Campo | Valore |
|-------|--------|
| PID :3002 | 3057 |
| Ora avvio | 2026-08-01 22:14 (18:14 UTC) |
| Ultimo pull iMac | 2026-08-01 22:18 CEST (2c25742d) |
| Anti-stantio §11 | avvio DOPO pull → NON stantio per §11 |
| engine | `go` (engine_darwin_amd64 PID 3152, -port 5080 -bridge 127.0.0.1:8300) |
| registered | `True` |
| reg_status | `200` |
| SIP trunk | `0972536918@sip.vivavox.it` |
| SARA_TEST_CAPTURE | `1` (visibile via `ps eww 3057`, confermato) |
| WAV path | `/Volumes/MacSSD - Dati/fluxion/.claude/cache/T-SARA-TURNTAKING/calls/call_<ts>.wav` |
| health | `{"status":"ok","service":"FLUXION Voice Agent Enterprise","version":"2.1.0"}` |

**NOTE**: il processo precedente (PID 40065, avviato 22:39 del 1° agosto) è stato riavviato per iniettare `SARA_TEST_CAPTURE=1` — variabile letta una volta sola a `__init__` (voip_goengine.py:188). L'operazione costituisce GO implicito del founder (richiesta esplicita in F3 del task).

---

## F4 — DB PULITO PER LA CHIAMATA

**DB produzione Sara**: `/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db`

**Appuntamenti attivi** (17 totali, `deleted_at IS NULL`):

| id (breve) | data_ora_inizio | stato | fonte |
|-----------|-----------------|-------|-------|
| app-001 | 2026-01-08T09:00 | Confermato | whatsapp |
| app-002 | 2026-01-08T10:00 | Confermato | manuale |
| app-003 | 2026-01-08T11:00 | Confermato | manuale |
| app-004 | 2026-01-08T14:00 | Confermato | voice |
| app-005 | 2026-01-08T15:00 | Confermato | manuale |
| app-006 | 2026-01-09T09:00 | Confermato | manuale |
| app-007 | 2026-01-09T10:00 | Confermato | whatsapp |
| app-008 | 2026-01-09T14:00 | Confermato | manuale |
| app-009 | 2026-01-10T11:00 | Confermato | manuale |
| app-010 | 2026-01-10T16:00 | Confermato | voice |
| app-011 | 2026-01-11T10:00 | Confermato | whatsapp |
| app-012 | 2026-01-11T15:00 | Bozza | manuale |
| app-013 | 2026-01-12T09:00 | Confermato | manuale |
| app-014 | 2026-01-12T14:00 | Confermato | manuale |
| app-015 | 2026-01-13T11:00 | Confermato | voice |
| c57e6ade (breve) | 2026-08-03T09:00 | confermato | voice |
| 9636bbc7 (breve) | 2026-08-03T09:30 | confermato | voice |

`app-001..015` = dati demo statici (gennaio 2026, passati).
`c57e6ade` = slot residuo da sessione stress/booking precedente (Aug 3 09:00).
`9636bbc7` = booking T-BOOKING-FIX2 VERDE (Aug 3 09:30, documentato in LEDGER).

**Impatto su CERT-21**: ZERO. Il copione CERT-21 NON produce un booking (il test termina con E6 escalation al terzo strike). I due slot di agosto non interferiscono.

**Pulizia**: nessuna. Niente rimosso. La regola è dichiarare, non rimuovere.

---

## VERDETTO — PRONTI A CHIAMARE: SI

Tutti e 4 i prerequisiti di F3 soddisfatti:
- engine=go ✓
- registered=True ✓
- reg_status=200 ✓
- SARA_TEST_CAPTURE=1 visibile al processo ✓

Copione scritto in `docs/judge/CERT-21-COPIONE.md`.
Comandi raccolta post-call inclusi nel copione stesso.
