# Ricetta build pjsua2 NDEBUG — Sara FLUXION

## Perché

pjproject include asserzioni di debug (`pj_assert`) nel conference bridge. In build DEBUG
queste asserzioni terminano il processo con SIGABRT quando operazioni sul conf port avvengono
fuori dal thread owner del group lock (race pjmedia 2.16-dev, confermata S354).

Compilare con `-DNDEBUG=1` disabilita tutte le `pj_assert` a compile-time, eliminando il crash
senza modificare la logica (le asserzioni non proteggono invarianti runtime critici per Sara —
sono guardrail di sviluppo). Cfr. Asterisk docs su NDEBUG: https://docs.asterisk.org/Development/Debugging/

Il `.so` risultante (8.6MB, link statico pjsip; link dinamico opus/openssl/system) è stato
validato con:
- Gate 1: 30 chiamate SIP sequenziali — zero crash
- Gate 2: 3 chiamate SIP concorrenti — zero crash
- `reg_status:200` stabile dopo riavvio pipeline

## Commit pjproject pinnato

- URL: https://github.com/pjsip/pjproject.git
- Commit: `d0cbf57aca90f4722194c4e0d94ef0b236bb2489`
- Branch al momento del clone: `master` (2.17-dev, nessun tag)
- Data build: 2026-06-08

**IMPORTANTE**: fare sempre checkout del commit pinnato, non di `master` (si muove).

## Dipendenze host iMac (già installate)

```bash
brew install opus openssl@3 swig
# swig: /usr/local/bin/swig — versione 4.4.1
# opus: /usr/local/opt/opus
# openssl: /usr/local/opt/openssl@3
```

Python target: `/usr/bin/python3` (CPython 3.9, usato dalla pipeline Sara).

## Step 1 — Clone e checkout al commit pinnato

```bash
cd /tmp
git clone https://github.com/pjsip/pjproject.git pjproject-ndebug
cd pjproject-ndebug
git checkout d0cbf57aca90f4722194c4e0d94ef0b236bb2489
```

## Step 2 — Configure con NDEBUG=1

Comando esatto usato (da `config.log`, voce "Invocation command line"):

```bash
./aconfigure 'CFLAGS=-DNDEBUG=1 -O2' \
    --disable-video \
    --with-opus=/usr/local/opt/opus \
    --with-ssl=/usr/local/opt/openssl@3
```

Verifica che `build.mak` contenga `-DNDEBUG=1`:

```bash
grep -- '-DNDEBUG' build.mak
# output atteso: -DNDEBUG=1 -O2 -DPJ_IS_BIG_ENDIAN=0 ...
```

## Step 3 — Build pjproject

```bash
make dep && make
```

Tempo stimato iMac 2012 (CPU-only): ~15-20 minuti.

## Step 4 — Build SWIG Python binding

Il Makefile SWIG usa `setup.py build` via `python3`. Non servono comandi g++ manuali
se `setup.py` trova le flags via `helper.mak`.

```bash
cd pjsip-apps/src/swig
make python
```

Questo produce:
- `python/_pjsua2.so` (o `_pjsua2.cpython-39-darwin.so` dopo rename automatico)
- `python/pjsua2.py` (wrapper SWIG, 14676 righe — DIVERSO da quello in produzione 7506 righe)

**Nota wrapper**: la pipeline Sara funziona con il `pjsua2.py` esistente in
`voice-agent/lib/pjsua2/pjsua2.py` (Jun 4, 7506 righe). NON sostituire automaticamente
il wrapper senza verificare compatibilità. Il wrapper della build NDEBUG è archiviato in
`voice-agent/lib/pjsua2/prebuilt/pjsua2.py.ndebug-build` come riferimento.

**DA VERIFICARE se si usa `make python` su un Mac futuro**: il build directory del `.so`
sarà in `python/build/lib.macosx-*/`, rinominarlo con il suffisso cpython corretto.

## Step 5 — Deploy del .so

```bash
# Backup preventivo
cp voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so \
   voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so.bak

# Deploy nuovo .so (trovarlo in build/lib.macosx-*/cpython-39/)
BUILT_SO=$(find /tmp/pjproject-ndebug/pjsip-apps/src/swig/python/build -name '_pjsua2*.so' | head -1)
cp "$BUILT_SO" voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so
```

## Artefatti prebuilt nel repo

`voice-agent/lib/pjsua2/prebuilt/` contiene gli artefatti del build S355 (2026-06-08):

| File | Descrizione |
|------|-------------|
| `_pjsua2.cpython-39-darwin.so.ndebug` | .so NDEBUG live, MD5 `c8b51f209c6bfb64c0619af62c566b04` |
| `_pjsua2.cpython-39-darwin.so.PRE-NDEBUG-bak` | .so DEBUG originale (rollback) |
| `pjsua2.py.ndebug-build` | wrapper SWIG dalla build NDEBUG (14676 righe, non in uso) |

Per rollback rapido (senza rebuild):
```bash
cp voice-agent/lib/pjsua2/prebuilt/_pjsua2.cpython-39-darwin.so.ndebug \
   voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so
```

## Note sul LC_ID_DYLIB

`otool -L` mostra come primo entry `/tmp/_pjsua2-ndebug.cpython-39-darwin.so` — questo è
il `install_name` (self-ID del dylib, LC_ID_DYLIB), non una dipendenza runtime su un file
in `/tmp`. Il caricamento NON fallisce al reboot (verificato: `import pjsua2` OK dopo
copia in `lib/pjsua2/`). Le dipendenze reali (opus, openssl, system frameworks) sono tutte
in percorsi permanenti (Homebrew + system).

Per correggere il self-ID esteticamente (non necessario per funzionare):
```bash
install_name_tool -id @rpath/_pjsua2.cpython-39-darwin.so \
    voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so
```

## Smoke test post-deploy

```bash
python3 -c "import sys; sys.path.insert(0, 'voice-agent/lib'); import pjsua2; print('OK')"
curl -s http://127.0.0.1:3002/health
curl -s http://127.0.0.1:3002/api/voice/voip/status | python3 -m json.tool | grep reg_status
```
