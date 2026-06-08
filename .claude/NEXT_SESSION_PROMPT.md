# Prompt ripartenza — S355 NDEBUG rebuild pjproject

**Generato**: `2026-06-08T11:55:00Z`
**Sessione chiusa per context budget 72% (CLOSING_ONLY)**
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)

## Contesto crash (confermato, non ri-derivare)
Sara crasha SIGABRT su `lock.c:279` ogni volta che monta la conference port.
Fix confermato giudice Claude AI: rebuild pjproject con `-DNDEBUG=1` → `pj_assert` diventa NO-OP.

## STEP 0 — COMPLETATO con scoperta critica

### Path verificati
- **PYMOD**: `/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/`
  - File chiave: `_pjsua2.cpython-39-darwin.so` + `pjsua2.py` + tutte le `.dylib`
  - NON installato in site-packages — lib bundled custom
  - Backup precedenti trovati: `pjsua2.backup-PRE-S337-20260604-125255/` e `pjsua2.backup-2.16dev-20260515/`
- **Interprete Python Sara**: `/usr/bin/python3` (shebang `#!/usr/bin/env python3`)
  - Import via `sys.path.insert(0, .../lib/pjsua2)` in `voip_pjsua2.py` righe 119-121

### PJPROJECT_ROOT — NON ESISTE PIU' SULL'IMAC
`find` su tutta la home e `/Volumes/MacSSD - Dati` non ha trovato `config.log` né `build.mak`.
Il nome backup `pjsua2.backup-2.16dev-20260515` conferma: era un clone temporaneo già eliminato.
`otool -L` sul .so mostra dipendenze da `/usr/local/opt/opus`, `/usr/local/opt/openssl@3` (Homebrew).

**CONCLUSIONE STEP 0**: serve riclonare pjproject, identificare la versione esatta, e fare un build fresh con `-DNDEBUG=1`.

## WORK ORDER per la prossima sessione

### STEP 0b — Identifica versione pjproject nel .so
```bash
ssh imac "strings '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/libpjsip.dylib' 2>/dev/null | grep -E 'pjsip-[0-9]|pjsua2-[0-9]|version [0-9]' | head -10"
```
Oppure:
```bash
ssh imac "strings '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/libpj.dylib' 2>/dev/null | grep -E '2\.[0-9]+\.' | head -10"
```

### STEP 1 — Backup .so esistente (reversibilità, vincolo #1d)
```bash
ts=$(date +%Y%m%d-%H%M%S)
ssh imac "cp '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so' /tmp/_pjsua2.so.bak-PRE-NDEBUG-${ts} && stat /tmp/_pjsua2.so.bak-PRE-NDEBUG-${ts}"
```
Incolla output stat (size>0 obbligatorio).

### STEP 2 — Clone pjproject
```bash
ssh imac "cd /tmp && git clone --depth=1 https://github.com/pjsip/pjproject.git pjproject-ndebug 2>&1 | tail -5"
```
Se il backup è `2.16dev-20260515`, probabilmente è HEAD del branch master di quel periodo.
Se la versione non coincide esattamente non è critico — il fix NDEBUG è indipendente dalla versione patch.

### STEP 3 — Recupera le configure options dal backup .so via nm/strings
```bash
ssh imac "nm '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/libpjmedia.dylib' 2>/dev/null | grep -i 'no_avx\|codec\|opus' | head -10"
```
Le opzioni configure originali erano probabilmente:
- `--disable-video` (iMac 2012, no video processing)
- `--with-opus` (opus linkato via Homebrew)
- Senza AVX2 (CPU iMac 2012)

### STEP 4 — Configure con NDEBUG
```bash
ssh imac "cd /tmp/pjproject-ndebug && ./configure \
  CFLAGS='-DNDEBUG=1 -O2' \
  --disable-video \
  --with-opus=/usr/local/opt/opus \
  2>&1 | tail -20"
```
Adatta le opzioni a quello che trovi nei STEP 0b/3.

### STEP 5 — Build
```bash
ssh imac "cd /tmp/pjproject-ndebug && make dep && make -j2 2>&1 | tail -30"
```
(Può richiedere 10-20 minuti su iMac 2012.)

### STEP 6 — Gate build
```bash
ssh imac "grep -- '-DNDEBUG' /tmp/pjproject-ndebug/build.mak | head -3"
```
Se vuoto → STOP, la flag non si è propagata.

### STEP 7 — Rebuild modulo Python pjsua2
```bash
ssh imac "cd /tmp/pjproject-ndebug/pjsip-apps/src/swig && make python 2>&1 | tail -20"
# Identifica il .so prodotto:
ssh imac "find /tmp/pjproject-ndebug -name '_pjsua2*.so' 2>/dev/null"
# Copia in posizione:
ssh imac "cp /tmp/pjproject-ndebug/pjsip-apps/src/swig/python/_pjsua2.cpython-39-darwin.so '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so'"
```

### STEP 8 — Gate 1: test runtime
```bash
# Riavvia pipeline
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && /usr/bin/python3 main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
sleep 5
ssh imac "curl -s http://127.0.0.1:3002/health"
ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"
# Lancia harness
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && /usr/bin/python3 scripts/sara_audio_harness.py 2>&1"
# Verifica ZERO crash report nuovi:
ssh imac "ls -lt ~/Library/Logs/DiagnosticReports/Python-*.ips 2>/dev/null | head -5"
```
ATTESO: zero SIGABRT, zero `lock.c:279`, nessun nuovo `.ips`.

### ROLLBACK se crash persiste
```bash
ssh imac "cp /tmp/_pjsua2.so.bak-PRE-NDEBUG-<ts> '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so'"
```

## VINCOLI ASSOLUTI
- NON toccare `voice-agent/src/voip_pjsua2.py` né il confinement S354
- PRESERVA tutte le `.dylib` esistenti in lib/pjsua2/ — sostituisci solo `_pjsua2.cpython-39-darwin.so`
- Se il nuovo .so ha dipendenze da path diversi → aggiorna anche le `.dylib` dal nuovo build
- TRUST-BUT-VERIFY: incolla output reale di ogni comando-chiave, mai dichiarare "fatto" senza prova

## Prompt ripartenza per Luke
"Sei il voice-engineer di FLUXION. Riprendi work order NDEBUG da `.claude/NEXT_SESSION_PROMPT.md`.
STEP 0 completato: PYMOD = `/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/`.
PJPROJECT_ROOT non esiste piu' sull'iMac (clone temporaneo rimosso).
Prima azione: identifica versione pjproject con `strings libpjsip.dylib | grep pjsip`, poi clone fresh + build con `-DNDEBUG=1`.
Backup .so PRIMA di sovrascrivere. TRUST-BUT-VERIFY su ogni step."
