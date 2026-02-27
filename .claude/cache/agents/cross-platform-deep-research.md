# Cross-Platform Deep Research — FLUXION CoVe 2026

**Data ricerca:** 2026-02-27
**Metodo:** Analisi statica codebase + WebSearch verificata
**Scope:** macOS + Windows (Linux secondario)

---

## Executive Summary

La codebase FLUXION ha **6 problemi residui** di compatibilità cross-platform dopo i fix P1-P6 già implementati.

| Severita | Numero | Area |
|----------|--------|------|
| CRITICA | 2 | Rust/Tauri (path hardcoded macOS), log su /tmp/ |
| ALTA | 3 | Python: piper-tts archiviato, chatterbox-tts su Windows, vad_debug /tmp/ |
| MEDIA | 2 | CI voice-agent.yml Linux-only, PyInstaller separator Windows |
| BASSA | 1 | requirements.txt dipendenze opzionali non separate |

**Verdetto:** Non pronto per Windows con la configurazione attuale. I 2 problemi CRITICI bloccano l'avvio su Windows client. Gli altri degradano gracefully ma impattano TTS e CI.

---

## 1. Python voice-agent — Problemi macOS-only non ancora fixati

### P7 — CRITICO: VADConfig.dump_path hardcoded /tmp/
**File:** `voice-agent/src/vad/ten_vad_integration.py`, riga 85
**Codice attuale:**
```python
dump_path: str = "/tmp/vad_debug"
```
**Problema:** `/tmp/` non esiste su Windows. Su Windows il percorso temp equivalente è `%TEMP%` o `C:\Users\<user>\AppData\Local\Temp`.
**Fix:**
```python
import tempfile, os
dump_path: str = os.path.join(tempfile.gettempdir(), "vad_debug")
```
**Impatto:** Il campo è usato solo se `dump_audio=True` (debug mode), quindi non causa crash in produzione — ma rompe il debug cross-platform. **Severità ALTA** se il debug viene attivato su Windows.

---

### P8 — ALTA: piper-tts repository ARCHIVIATO (ottobre 2025)
**File:** `voice-agent/requirements.txt`, riga 48: `piper-tts>=1.2.0`
**Problema:** Il repository rhasspy/piper è stato **archiviato il 6 ottobre 2025** ed è read-only. Su Windows, `piper-tts` dipende da `piper-phonemize` che non ha wheel pre-compilate per Windows (richiede compilazione da sorgente con cmake).
**Situazione concreta:**
- PyPI package piper-tts 1.4.1 esiste ancora (ultimo aggiornamento febbraio 2026)
- Ma piper-phonemize su Windows richiede Visual C++ Build Tools
- Il binary `piper.exe` cercato da PiperTTS._find_binary() ha fallback Windows (tts.py righe 211-217) ma il PATH Windows è diverso
**Fix a breve termine:** Usare piper binary standalone pre-compilato (rilasciato su GitHub releases) invece del pip package. Oppure documentare che Piper TTS è opzionale su Windows e Chatterbox/System TTS sono i path principali.
**Fix strutturale:** Rimuovere `piper-tts` da requirements.txt e usarlo solo come optional extra.

---

### P9 — ALTA: chatterbox-tts richiede PyTorch — problematico su Windows headless
**File:** `voice-agent/requirements.txt`, righe 44-46:
```
chatterbox-tts>=0.1.0
torchaudio>=2.1.0
scipy>=1.11.0
```
**Problema specifico Windows:**
- chatterbox-tts richiede PyTorch come dipendenza obbligatoria
- Su Windows il download di torch è ~2.5GB (versione CPU) vs ~700MB su macOS
- PyInstaller con torch su Windows genera executable di 3-4GB
- Il fallback del factory `get_tts()` funziona (Piper → System TTS) ma il BLOCCO sta nell'installazione: se `pip install chatterbox-tts` fallisce per problemi di torch, tutta l'installazione fallisce
**Fix:** Separare torch in extras opzionali:
```
# requirements.txt
# TTS - Primary (requires PyTorch ~2.5GB)
# chatterbox-tts>=0.1.0  # OPTIONAL - comentare se non serve primary TTS
# Fallback automatico a Piper o System TTS
```
**Workaround confermato:** Il codice tts.py già gestisce il caso `ImportError` di torch con fallback a Piper — il problema è solo nell'installazione, non a runtime.

---

### P10 — MEDIA: stt.py cerca whisper.cpp in /usr/local/bin (macOS/Linux only)
**File:** `voice-agent/src/stt.py`, righe 127-128:
```python
Path("/usr/local/bin/whisper-cli"),
Path("/usr/local/bin/whisper"),
```
**Problema:** Questi path non esistono su Windows. Tuttavia `WhisperOfflineSTT` è la terza priorità (dopo FasterWhisper e GroqSTT) e il codice gestisce `FileNotFoundError` con fallback, quindi non causa crash.
**Impatto reale:** BASSO — il fallback Groq funziona. Ma se qualcuno installa whisper.cpp su Windows, non verrà trovato automaticamente.
**Fix semplice:** Aggiungere path Windows nella lista:
```python
Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "whisper.cpp/whisper-cli.exe",
Path.home() / "whisper.cpp/build/bin/Release/whisper-cli.exe",
```

---

### P11 — BASSA: analytics.py path DB usa Path.home() — OK su entrambi i sistemi
**File:** `voice-agent/src/session_manager.py`, righe 35-36:
```python
_FLUXION_DIR = Path.home() / ".fluxion"
DEFAULT_SESSIONS_DB = str(_FLUXION_DIR / "voice_sessions.db")
```
**Verdetto:** `Path.home()` funziona su Windows (restituisce `C:\Users\<username>`). Nessun problema. Confermato OK.

---

### P12 — BASSA: tts.py commento obsoleto "macOS say command"
**File:** `voice-agent/src/tts.py`, riga 11: `3. System TTS - macOS say command (last resort)`
**Problema:** Il codice `SystemTTS` gestisce già entrambi i sistemi (righe 319-396), ma il commento nel docstring è fuorviante. Non è un bug funzionale. **Fix:** Aggiornare il docstring.

---

## 2. Rust/Tauri — Problemi OS-specific

### R1 — CRITICO: Path hardcoded macOS in voice_pipeline.rs
**File:** `src-tauri/src/commands/voice_pipeline.rs`, righe 467-472:
```rust
// 4. Known development paths (macOS specific)
candidates.push(std::path::PathBuf::from(
    "/Volumes/MacSSD - Dati/fluxion/voice-agent",
));
candidates.push(std::path::PathBuf::from(
    "/Volumes/MontereyT7/FLUXION/voice-agent",
));
```
**Problema:** Questi path hardcoded esistono SOLO sul Mac di sviluppo. Su qualsiasi altra macchina (incluso Windows cliente) falliscono. Il codice poi fa fallback ad altri candidati (resource_dir, cwd, exe_path), ma questi path hardcoded sono indice che l'app non è stata testata con `find_voice_agent_dir` su un sistema pulito.
**Rischio reale:** Se i candidati precedenti (resource_dir, cwd, exe_path) non trovano voice-agent, il fallback hardcoded fallisce su Windows → il pannello voice non si avvia.
**Fix:** Rimuovere i path hardcoded macOS di sviluppo. Aggiungere invece path Windows:
```rust
// Windows: AppData path
if let Ok(appdata) = std::env::var("APPDATA") {
    candidates.push(std::path::PathBuf::from(appdata).join("FLUXION").join("voice-agent"));
}
```

---

### R2 — CRITICO: Log su /tmp/fluxion-voice.log in voice_pipeline.rs
**File:** `src-tauri/src/commands/voice_pipeline.rs`, riga 18:
```rust
.open("/tmp/fluxion-voice.log")
```
**Problema:** `/tmp/` non esiste su Windows. Il codice usa `if let Ok(...)` quindi non crasha, ma il logging è silenziosamente disabilitato su Windows. Per il debug di produzione su Windows questo è un gap critico.
**Fix:**
```rust
fn get_log_path() -> std::path::PathBuf {
    #[cfg(target_os = "windows")]
    {
        std::env::var("TEMP")
            .map(|t| std::path::PathBuf::from(t).join("fluxion-voice.log"))
            .unwrap_or_else(|_| std::path::PathBuf::from("C:/Temp/fluxion-voice.log"))
    }
    #[cfg(not(target_os = "windows"))]
    {
        std::path::PathBuf::from("/tmp/fluxion-voice.log")
    }
}
```

---

### R3 — MEDIA: find_python() cerca solo path macOS/Linux dopo venv
**File:** `src-tauri/src/commands/voice_pipeline.rs`, righe 519-527:
```rust
let full_paths = [
    "/usr/bin/python3",
    "/usr/local/bin/python3",
    "/opt/homebrew/bin/python3",
    "/Library/Frameworks/Python.framework/Versions/Current/bin/python3",
];
```
**Problema:** Questi path esistono solo su macOS/Linux. Su Windows `python3` viene trovato via PATH lookup (righe 540-556) che funziona, MA solo se Python è nel PATH di Windows.
**Impatto reale:** MEDIO — `python3` spesso non è nel PATH di default su Windows (solo `python`). La funzione controlla `python` come secondo fallback (riga 549), quindi funziona ma dipende dalla configurazione utente.
**Fix consigliato:** Aggiungere path Windows comuni:
```rust
#[cfg(target_os = "windows")]
let win_paths = [
    r"C:\Python311\python.exe",
    r"C:\Program Files\Python311\python.exe",
    // ... etc
];
```

---

## 3. Frontend React — Nessun problema OS-specific

**Ricerca effettuata:** grep su `src/` per `platform`, `process.platform`, `os.type`, `navigator.platform`.
**Risultato:** Nessuna occorrenza trovata. Il frontend React è puro TypeScript/HTML e non contiene logica OS-specific. **CONFERMATO OK.**

---

## 4. CI/CD — Gap nel workflow Windows

### CI-1 — CRITICA: voice-agent.yml gira SOLO su ubuntu-latest
**File:** `.github/workflows/voice-agent.yml`
Tutti i 9 job (lint, unit-tests, e2e-tests, complete-tests, smoke-tests, performance, security, build, summary) girano esclusivamente su `ubuntu-latest`. **Nessun test su Windows o macOS.**
**Conseguenza:** I problemi P7-P12 e R1-R3 elencati sopra non vengono rilevati in CI.
**Fix necessario:** Aggiungere matrix per smoke-tests almeno:
```yaml
runs-on: ${{ matrix.os }}
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
```

### CI-2 — MEDIA: release-full.yml voice-agent PyInstaller con separatore path errato
**File:** `.github/workflows/release-full.yml`, riga 123:
```yaml
pyinstaller --onefile --name voice-agent \
  --add-data "models:models" \   # Separatore : → Linux/macOS
  --add-data "config:config" \
```
**Problema:** PyInstaller usa separatore `:` su Linux/macOS ma `;` su Windows.
**Fix:** Usare la sintassi portabile di PyInstaller:
```yaml
# Su Windows runner
--add-data "models;models"   # Windows
# Su macOS/Linux runner
--add-data "models:models"   # Unix
```
Oppure usare `${{ runner.os == 'Windows' && ';' || ':' }}` in step condizionale.

### CI-3 — BASSA: voice-agent.yml job "build" genera start.sh (solo Unix)
**File:** `.github/workflows/voice-agent.yml`, righe 461-469:
```yaml
cat > dist/fluxion-voice-agent/start.sh << 'EOF'
#!/bin/bash
...
EOF
chmod +x dist/fluxion-voice-agent/start.sh
```
**Problema:** Genera solo `start.sh` (bash), nessun `start.bat` per Windows.
**Impatto:** Questo job gira su ubuntu-latest, quindi non è un errore CI ma manca il corrispondente Windows.

---

## 5. Dipendenze — Problemi noti Windows 2025-2026

### DEP-1: piper-tts — Repository archiviato (ottobre 2025)
- **Status:** Archiviato il 06/10/2025, read-only
- **piper-tts 1.4.1** su PyPI ancora disponibile (aggiornato feb 2026)
- **Windows:** piper-phonemize richiede compilazione da sorgente con cmake + Visual C++ Build Tools
- **Consiglio:** Usare binary standalone da GitHub releases se il pip package fallisce

### DEP-2: chatterbox-tts — Dipendenza da PyTorch su Windows
- **Status:** Richiede PyTorch, anche per CPU. Su Windows, wheel PyTorch CPU = ~2.5GB
- **Python 3.11 raccomandato** per massima compatibilità wheel
- **PyInstaller:** Executable finale 3-4GB — troppo grande per distribuzione normale
- **Soluzione pratica:** Su Windows, usare Piper binary + System TTS (pyttsx3) senza chatterbox

### DEP-3: faster-whisper + CTranslate2 — Compatibilità CUDA Windows
- **Status CPU:** Funziona correttamente su Windows (CPUExecutionProvider)
- **Status GPU:** CTranslate2 >= 4.5.0 richiede CUDA >= 12.3 + cuDNN v9 → conflitti frequenti
- **Per FLUXION (CPU-only):** Nessun problema. `compute_type="int8"` funziona su CPU Windows.
- **Raccomandazione:** Specificare `ctranslate2<4.5.0` in requirements se si vuole evitare problemi CUDA su sistemi con GPU NVIDIA.

### DEP-4: onnxruntime — OK su Windows
- **Status:** onnxruntime (CPU) funziona perfettamente su Windows
- `CPUExecutionProvider` è il default e non richiede CUDA
- Silero VAD (usato in FluxionVAD) funziona su Windows senza modifiche
- **Unico rischio:** Python 3.14 (wheels non ancora disponibili) — ma FLUXION usa 3.9-3.12

### DEP-5: sentence-transformers + faiss-cpu — OK su Windows
- Entrambi hanno wheel pre-compilate per Windows x64
- `faiss-cpu` su Windows richiede numpy<2.0 (potenziale conflitto con numpy>=2.0 richiesto da altre librerie)
- **Raccomandare:** `numpy>=1.24.0,<2.0` in requirements.txt

### DEP-6: pipecat-ai + aiortc — Situazione Windows complessa
**File:** `requirements.txt`, righe 26-29:
```
pipecat-ai>=0.0.30
aiortc>=1.6.0
aioice>=0.9.0
av>=12.0.0
```
- `aiortc` dipende da `libopus` e `libvpx` — su Windows richiede binari pre-compilati
- `av` (PyAV) dipende da FFmpeg — su Windows il wheel include FFmpeg ma può avere problemi con versioni specifiche
- **Impatto:** Queste dipendenze sono per VoIP/SIP (futuro) — non usate nel core path attuale

---

## 6. Piano Fix Completo (Priorità + Effort)

### SPRINT 1 — Fix Critici (1-2 ore, blocca Windows)

| ID | File | Fix | Effort |
|----|------|-----|--------|
| R1 | `src-tauri/src/commands/voice_pipeline.rs` | Rimuovere path hardcoded `/Volumes/...`, aggiungere `std::env::current_dir()` fallback | 20 min |
| R2 | `src-tauri/src/commands/voice_pipeline.rs` | Sostituire `/tmp/fluxion-voice.log` con `tempfile`/env cross-platform | 15 min |
| P7 | `voice-agent/src/vad/ten_vad_integration.py` | Sostituire `/tmp/vad_debug` con `tempfile.gettempdir()` | 5 min |

**Codice R2 pronto:**
```rust
fn get_log_path() -> std::path::PathBuf {
    #[cfg(windows)]
    return std::env::var("TEMP")
        .map(|t| std::path::PathBuf::from(t).join("fluxion-voice.log"))
        .unwrap_or_else(|_| std::path::PathBuf::from(r"C:\Temp\fluxion-voice.log"));
    #[cfg(not(windows))]
    return std::path::PathBuf::from("/tmp/fluxion-voice.log");
}
```

**Codice P7 pronto:**
```python
import tempfile
import os

@dataclass
class VADConfig:
    dump_path: str = field(default_factory=lambda: os.path.join(tempfile.gettempdir(), "vad_debug"))
```

---

### SPRINT 2 — Fix Alti (2-4 ore, migliora stabilità Windows)

| ID | File | Fix | Effort |
|----|------|-----|--------|
| P8 | `requirements.txt` | Rendere piper-tts opzionale (extra), documentare binary standalone | 30 min |
| P9 | `requirements.txt` | Separare chatterbox-tts + torch in requirements-tts-primary.txt opzionale | 30 min |
| R3 | `voice_pipeline.rs` | Aggiungere path Python Windows nel full_paths array | 20 min |
| CI-2 | `release-full.yml` | Fix PyInstaller separator `--add-data` per Windows vs Unix | 15 min |

**Struttura requirements consigliata:**
```
# requirements.txt (core — sempre installato)
faster-whisper>=1.0.0
groq>=0.4.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
python-Levenshtein>=0.21.0
dateparser>=1.2.0
sentence-transformers>=2.2.2
faiss-cpu>=1.7.4
numpy>=1.24.0,<2.0
onnxruntime>=1.16.0
sounddevice>=0.4.6
soundfile>=0.12.1

# requirements-tts-primary.txt (opzionale, ~2.5GB su Windows)
chatterbox-tts>=0.1.0
torch>=2.1.0
torchaudio>=2.1.0
scipy>=1.11.0

# requirements-tts-piper.txt (opzionale, solo se binary disponibile)
piper-tts>=1.2.0  # Usare binary standalone su Windows

# requirements-voip.txt (futuro, non usato in v1.0)
pipecat-ai>=0.0.30
aiortc>=1.6.0
```

---

### SPRINT 3 — CI/CD (2-3 ore, rileva problemi automaticamente)

| ID | File | Fix | Effort |
|----|------|-----|--------|
| CI-1 | `voice-agent.yml` | Aggiungere matrix Windows per smoke-tests | 1h |
| CI-3 | `voice-agent.yml` | Aggiungere start.bat per Windows | 30 min |

**Snippet CI-1:**
```yaml
smoke-tests:
  runs-on: ${{ matrix.os }}
  strategy:
    matrix:
      os: [ubuntu-latest, windows-latest]
  steps:
    - name: Install deps (Windows audio)
      if: runner.os == 'Windows'
      run: pip install sounddevice soundfile pyaudio
```

---

## Fonti

- Analisi statica: tutti i file .py e .rs elencati sopra (HIGH confidence)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper) — CTranslate2 4.5.0+ CUDA issues (MEDIUM)
- [piper-tts PyPI](https://pypi.org/project/piper-tts/) — status repository (HIGH, verificato 2026-02-27)
- [rhasspy/piper archived](https://github.com/rhasspy/piper/discussions/577) — repo read-only ottobre 2025 (HIGH)
- [Tauri 2 Windows docs](https://v2.tauri.app/distribute/windows-installer/) — WebView2 bundling (HIGH)
- [chatterbox Windows install](https://emanueleferonato.com/2026/01/07/text-to-speech-on-your-pc-running-chatterbox-turbo-locally-on-windows-clean-setup-known-pitfalls/) — pitfalls noti (MEDIUM)

---

## Riepilogo Finale — Matrice Severità

| # | Problema | File | Severità | Impatto Windows | Fix Effort |
|---|----------|------|----------|-----------------|------------|
| R1 | Path hardcoded /Volumes/ | voice_pipeline.rs:467 | CRITICA | Voice agent non si avvia | 20 min |
| R2 | Log su /tmp/ (Rust) | voice_pipeline.rs:18 | CRITICA | Debug impossibile su Windows | 15 min |
| P7 | /tmp/vad_debug hardcoded | ten_vad_integration.py:85 | ALTA | VAD debug mode crasherebbe | 5 min |
| P8 | piper-tts archiviato | requirements.txt:48 | ALTA | Installazione fallisce su Windows | 30 min |
| P9 | chatterbox-tts + torch | requirements.txt:44-46 | ALTA | Install 2.5GB + possibili errori | 30 min |
| CI-1 | voice-agent.yml solo Linux | .github/workflows/ | MEDIA | Problemi non rilevati in CI | 1h |
| CI-2 | PyInstaller separator : vs ; | release-full.yml:123 | MEDIA | Build exe Windows fallisce | 15 min |
| R3 | Python path macOS-only | voice_pipeline.rs:519 | MEDIA | Python non trovato se non in PATH | 20 min |
| P10 | whisper /usr/local/bin | stt.py:127-128 | BASSA | Solo WhisperOfflineSTT, fallback OK | 10 min |
| P12 | Docstring obsoleto | tts.py:11 | BASSA | Solo documentazione | 2 min |

**Totale effort stimato:** 3h40min per tutti i fix
**Effort solo critici (SPRINT 1):** 40 minuti
