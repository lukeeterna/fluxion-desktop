# T-GUARDRAIL-1/#49 — Referto esecuzione
Data: 2026-08-03
Corsia: MACCHINA
Modello: claude-sonnet-4-6

## GATE-0
Base attesa: a30341d7 — PASS
vos_check.sh: 7/8 al primo tentativo (FAIL e: NEXT_SESSION_PROMPT.md presente).
Rimosso `.claude/NEXT_SESSION_PROMPT.md`, secondo tentativo: 8/8 PASS.

## F1 — Integrità

Trasporto: installer autoinstallante `install-unit-01.sh` scaricato dal founder in `~/Downloads/`.

SHA256 installer verificato:
```
171215e2d1916959f32ba97757fd74e068fcb82c49b429c5927ab8945ed17f59  install-unit-01.sh
```
MATCH con valore dichiarato nel mandato ✓

Installazione in staging fuori dal repo:
```
mkdir -p ~/vos-stage-01 && bash ~/Downloads/install-unit-01.sh ~/vos-stage-01
```
Output installer:
```
INSTALLAZIONE VERIFICATA: unit-01-machine-authority
Destinazione: /Users/macbook/vos-stage-01
95221b299e7b01f899b4550adf50bc77168b80e255f723d375a90f50dc308e9c  bin/vos_machine.py
f631287ed242dcb111d66b95cff9dd2108ca01106a40e152e986213aec68915c  docs/judge/MACHINES.json
74ae2e23786656e76701b3c18e1928779acef8f5b3aeaca1a1620840324fea6a  docs/judge/PROTOCOLLO.md
5c83c2a131449d9a8574780eb364e4820ed8643c35ecaa3bb06369d53e78a99b  docs/judge/mandati/T-MACHINE-AUTHORITY.md
```
Tutti e quattro gli SHA256 corrispondono al manifest ✓

EMENDAMENTO F1 (annotato): il trasporto originale prevedeva quattro file separati in incoming/.
Il founder ha trovato solo il manifest e i documenti allegati; Sol ha riconfezionato in installer
autoinstallante. Verifica SHA256 dell'installer prima dell'esecuzione: PASS.

## F2 — Cosa fa l'unità

L'unità T-MACHINE-AUTHORITY introduce identità e autorità delle due macchine fisiche:
1. **bin/vos_machine.py** — script Python con quattro sottocomandi (probe, build-registry,
   validate, verify). Non persiste UUID hardware né path locali in chiaro: usa fingerprint
   HMAC-SHA-256 derivato dal repo-root e dalla macchina fisica, e digest HMAC del path.
2. **docs/judge/MACHINES.json** — registro delle macchine enrollate: machine_id logico,
   fingerprint HMAC, roles (repo_authority / runtime_authority), origin, enrolled_head.
   Nessun UUID hardware, IP, username o path locale in chiaro.
3. **docs/judge/PROTOCOLLO.md** (nel pacchetto) — aggiunge tre regole (30-32 nel pacchetto)
   relative a topologia macchine, autorità uniche e integrità sensori.
4. **docs/judge/mandati/T-MACHINE-AUTHORITY.md** — mandato CONFIRM_FIRST: descrive le fasi
   F1-F6, i path toccati (bin/vos_machine.py, MACHINES.json, mandati/, PROTOCOLLO.md),
   i comandi da eseguire (probe su MacBook e iMac via SSH, build-registry, validate, verify).

Path toccati: bin/vos_machine.py, docs/judge/MACHINES.json, docs/judge/mandati/T-MACHINE-AUTHORITY.md,
docs/judge/PROTOCOLLO.md (solo append di tre regole, NO sovrascrittura).
Comandi eseguiti: probe (locale + SSH iMac), build-registry, validate, verify (parziale — vedi bug).
Nessuna azione su: :3002, voice-agent/, DB, riavvii di servizi.

## F3 — Fusione PROTOCOLLO (mai sovrascrittura)

PROTOCOLLO.md nel pacchetto ha regole 1-32, con sezione «Regole nate da T-MACHINE-AUTHORITY»
contenente le regole 30 (TOPOLOGIA), 31 (AUTORITÀ UNICHE), 32 (INTEGRITÀ SENSORI).

Il nostro PROTOCOLLO.md ha regola 30 nata da T-CERT-GATE («ALLINEAMENTO RUNTIME»): COLLIDE
con la 30 del pacchetto. Come da mandato F3-bis: NON copiato il file del pacchetto.
Estratte solo le tre regole nuove, rinumerate 31, 32, 33, appese al nostro PROTOCOLLO.md
sotto «### Regole nate da T-MACHINE-AUTHORITY».

Regole aggiunte:
- 31 (era 30 nel pacchetto): TOPOLOGIA MACCHINE
- 32 (era 31 nel pacchetto): AUTORITÀ UNICHE
- 33 (era 32 nel pacchetto): INTEGRITÀ DEI SENSORI

Il file del pacchetto NON è entrato nel repo. Nostra regola 30 intatta ✓.
PROTOCOLLO.md arriva a 33 regole numerate ✓.

## F4 — Applicazione

Copiati nel repo (path espliciti, mai glob):
- bin/vos_machine.py → 0755 ✓
- docs/judge/MACHINES.json ✓ (sovrascritto con registry reale costruito in F5)
- docs/judge/mandati/T-MACHINE-AUTHORITY.md ✓

PROTOCOLLO.md staging NON copiato ✓.

ANOMALIA ETICHETTA: T-MACHINE-AUTHORITY.md consegnato da Sol con prima riga «ETICHETTA: SAFE_AUTO».
Il mandato richiedeva «ETICHETTA: CONFIRM_FIRST». Sostituita come da istruzione. Il conflitto
(Sol: auto-eseguibile; mandato: richiede GO founder) è annotato qui per il giudice.

## F5 — Enrolment macchine

Probe MacBook (repo_authority):
```json
{
  "machine_id": "macbook",
  "head": "a30341d72db6a8dfb717c271c00add940d2ad9f2",
  "head_relation": {"head_equals_origin_master": true},
  "origin": "github.com/lukeeterna/fluxion-desktop",
  "fingerprint_sha256": "0479ab99a19dac32c27c8dff6e598b61aaf5536401191d61b3bc6869adc78533"
}
```

Probe iMac (runtime_authority) via SSH:
```json
{
  "machine_id": "imac",
  "head": "a30341d72db6a8dfb717c271c00add940d2ad9f2",
  "head_relation": {"head_equals_origin_master": true},
  "origin": "github.com/lukeeterna/fluxion-desktop",
  "service_probe": {"listener_pids": [41118], "port": 3002},
  "fingerprint_sha256": "95858239cab3bf71ac3eeccddd9fb9b077f3b8e431399541dfd1c719d86dbe0b"
}
```

Entrambe vedono origin/master = a30341d72db6a8dfb717c271c00add940d2ad9f2 ✓

Build-registry eseguito → MACHINES.json generato. Validate: PASS.

MACHINES.json finale (estratto chiave):
```json
{
  "authorities": {"repo_machine_id": "macbook", "runtime_machine_id": "imac"},
  "status": "ACTIVE",
  "origin_master_at_enrollment": "a30341d72db6a8dfb717c271c00add940d2ad9f2"
}
```
Verifica assenza dati sensibili: nessun UUID hardware, nessun path locale in chiaro, nessun
username, nessun IP. Solo fingerprint HMAC e digest HMAC del path ✓.

BUG IDENTIFICATO (non correggo — "Tu NON scrivi codice"):
Il sottocomando `verify` di vos_machine.py (riga 479) tenta di accedere a
`machine["repo_root"]` ma `build-registry` scrive solo `repo_root_hmac_sha256` (per privacy).
KeyError: 'repo_root'. Il registry è corretto; il difetto è nel codice di verify, che può
essere corretto da Sol nella prossima iterazione. Le prove F6a/F6c non passano per verify ma
per meccanismi a monte del bug.

## F6 — Prove fail-closed

**F6a — macchina non registrata rifiutata:**
Registry temporaneo con fingerprint MacBook sostituito da `aaaa...64`. Output:
```
MACHINE_GATE FAIL current physical machine is not uniquely enrolled in MACHINES.json
EXIT: 1
```
PASS ✓ (rifiuto corretto prima della riga 479 — il fingerprint non matcha)

**F6b — due origin/master divergenti rifiutati:**
Probe MacBook con `head = deadbeef...` e `head_equals_origin_master = false`.
Output build-registry:
```
MACHINE_GATE FAIL authority macbook is not at origin/master; enrollment refused
EXIT: 1
```
PASS ✓ (rifiutato a enrollment, non a verify)

**F6c — secondo proprietario stesso ruolo rifiutato:**
Registry manipolato con due macchine entrambe con ruolo `repo_authority`. Output validate:
```
MACHINE_GATE FAIL role repo_authority must have exactly one owner
EXIT: 1
```
PASS ✓

Tutte e tre le prove negative superano ✓.

---

MACCHINE REGISTRATE: SI
