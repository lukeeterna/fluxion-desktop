# Windows Compatibility Research — FLUXION

**Researched:** 2026-02-27
**Domain:** Cross-platform desktop (Tauri 2.x + Python voice agent)
**Overall Confidence:** HIGH (Tauri/SQLite) + MEDIUM (Python stack)

---

## Executive Summary

FLUXION ha una base Tauri 2.x solida per Windows: il framework e SQLite sono intrinsecamente cross-platform e il Rust compila nativamente su Windows tramite GitHub Actions. Le criticità reali sono concentrate nel voice agent Python, che contiene **5 blocchi bloccanti** per Windows:

1. **SystemTTS usa `say` + `afconvert` (macOS-only)** — non esiste su Windows, rompe il TTS fallback
2. **Path hardcoded macOS** in `booking_state_machine.py` e `voice_pipeline.rs` — `/Volumes/MacSSD/`, `/Library/Frameworks/Python/`
3. **`main.py` carica SQLite da `~/Library/Application Support/`** — non esiste su Windows (deve usare `%APPDATA%`)
4. **Piper binary path cerca `/usr/local/bin/piper`** — non valido su Windows
5. **Python packaging**: `requirements.txt` include `torch`, `chatterbox-tts`, `pipecat-ai` — packaging complesso su Windows senza piano

Effort totale stimato: **~9 giorni** per Windows compatibility completa.

**Priorità assoluta:** I punti 1, 2, 3 bloccano qualsiasi avvio del voice agent su Windows.

---

## 1. Tauri 2.x su Windows

### Compatibilità

**Stato: OTTIMO** (HIGH confidence — fonte: v2.tauri.app ufficiale)

Tauri 2.x supporta Windows nativamente:
- **WebView2**: Microsoft Edge WebView2 (pre-installato su Windows 10 1803+ e Windows 11)
- **Installer**: NSIS (`.exe`) e MSI (`.msi`) — entrambi supportati
- **Auto-update**: `tauri-plugin-updater` funziona su Windows con NSIS e MSI
- **Windows minimo**: Windows 10 (con WebView2)

Il codice `main.rs` ha già il flag corretto:
```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
```

### Gap identificati

**GAP 1 — `tauri.conf.json` manca configurazione Windows:**
Attualmente solo `"macOS": { ... }` nel bundle. Non è un blocco (defaults ragionevoli), ma per produzione serve firmare il binario.

**GAP 2 — WebView2 install mode non configurato:**
Senza `webviewInstallMode`, il default è `downloadBootstrapper` (richiede internet durante install). Per PMI offline-first consigliato `embedBootstrapper` (+1.8MB).

**GAP 3 — No code signing Windows (Authenticode):**
Senza firma digitale, Windows SmartScreen blocca l'installer con avviso "Publisher unknown". Per vendita a PMI è un problema serio.

### Remediation

```json
// tauri.conf.json — aggiungere in bundle:
"windows": {
  "webviewInstallMode": { "type": "embedBootstrapper" },
  "nsis": { "installMode": "perMachine" }
}
```

---

## 2. Voice Agent Python su Windows

### FasterWhisperSTT — COMPATIBILE ✅

`faster-whisper` usa CTranslate2 che ha wheel precompilate per Windows x64 su PyPI. Usa `WhisperModel(model_size, device="cpu", compute_type="int8")` — funziona su Windows senza modifiche.

### Piper TTS — RICHIEDE FIX ⚠️

Piper ha binary Windows AMD64 disponibili. Il problema è che il codice cerca solo path Unix:

```python
# src/tts.py — PROBLEMA:
Path.home() / ".local" / "bin" / "piper",    # Linux/macOS only
Path("/usr/local/bin/piper"),                  # macOS/Linux only
Path("/usr/bin/piper"),                        # Linux only
```

**Fix consigliato**: usare `piper-onnx` Python package (cross-platform, no binary separato):
```bash
pip install piper-onnx
```

### Silero ONNX / VAD — COMPATIBILE ✅

`onnxruntime` ha wheel per Windows x64. `silero_vad.onnx` è cross-platform. `webrtcvad` richiede `webrtcvad-wheels` su Windows.

### SystemTTS — BLOCCANTE ❌ (CRITICO)

```python
# src/tts.py — COMPLETAMENTE ROTTO SU WINDOWS:
class SystemTTS:
    """Fallback TTS using macOS say command."""
    async def synthesize(self, text: str) -> bytes:
        process = await asyncio.create_subprocess_exec(
            "say",       # Non esiste su Windows
            "-v", self.voice, "-o", output_path, ...
        )
        # poi usa "afconvert" — macOS-only
```

**Fix richiesto**:
```python
import sys

class SystemTTS:
    async def synthesize(self, text: str) -> bytes:
        if sys.platform == "win32":
            return await self._synthesize_windows(text)
        else:
            return await self._synthesize_macos(text)

    async def _synthesize_windows(self, text: str) -> bytes:
        import pyttsx3, tempfile, os
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        with open(output_path, "rb") as f:
            data = f.read()
        os.unlink(output_path)
        return data
```

Aggiungere a `requirements.txt`: `pyttsx3>=2.90`

### Chatterbox TTS — PACKAGING PROBLEMATICO ⚠️

Funziona su Windows CPU ma richiede PyTorch (~2.5GB). Troppo grande per bundle PyInstaller. **Escludere dal bundle Windows**, usare Piper come primary TTS su Windows.

### Riepilogo Voice Agent

| Componente | Windows OK? | Fix richiesto |
|-----------|------------|---------------|
| FasterWhisperSTT | ✅ SÌ | Nessuno |
| GroqSTT | ✅ SÌ | Nessuno |
| Silero VAD (ONNX) | ✅ SÌ | Nessuno |
| webrtcvad | ✅ SÌ (con wheels) | `pip install webrtcvad-wheels` |
| Chatterbox TTS | ⚠️ SÌ (lento CPU) | Escludi da bundle Windows |
| Piper TTS | ⚠️ Parziale | Migra a `piper-onnx` package |
| SystemTTS | ❌ NO — BLOCCA | Implementare con pyttsx3 |

---

## 3. Path Hardcoded macOS

### Occorrenze trovate

| File | Pattern macOS | Severità |
|------|---------------|----------|
| `voice-agent/main.py` | `~/Library/Application Support/com.fluxion.desktop/...` | **CRITICO** |
| `voice-agent/src/booking_state_machine.py` | `/Volumes/MacSSD - Dati/...`, `/Volumes/MontereyT7/...` | **CRITICO** |
| `voice-agent/src/tts.py` | `say`, `afconvert`, `.aiff`, voce "Alice" | **CRITICO** |
| `voice-agent/src/tts.py` | `/usr/local/bin/piper`, `/usr/bin/piper` | **ALTO** |
| `voice-agent/src/stt.py` | `/usr/local/bin/whisper-cli` | MEDIO (già in fallback) |
| `src-tauri/src/commands/voice_pipeline.rs` | `/Volumes/MacSSD...` | MEDIO (dev-only) |
| `src-tauri/src/commands/voice_pipeline.rs` | `/Library/Frameworks/Python...` | BASSO (cade su PATH) |

### Fix richiesti

**Fix 1 — `main.py` SQLite path:**
```python
import sys
home = Path.home()
if sys.platform == "win32":
    appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    candidates = [
        appdata / "com.fluxion.desktop" / "fluxion.db",
        appdata / "fluxion" / "fluxion.db",
    ]
else:
    candidates = [
        home / "Library" / "Application Support" / "com.fluxion.desktop" / "fluxion.db",
        home / "Library" / "Application Support" / "fluxion" / "fluxion.db",
    ]
```

**Fix 2 — `booking_state_machine.py`:**
Rimuovere le righe con path `/Volumes/`. Lasciare solo path relativi e `FLUXION_DB_PATH` env var.

---

## 4. SQLite / Database

**Stato: OTTIMO** (HIGH confidence)

SQLx con SQLite funziona perfettamente su Windows. Il codice Rust usa `app.path().app_data_dir()` che su Windows restituisce `C:\Users\{user}\AppData\Roaming\com.fluxion.desktop\`. Rust `PathBuf` gestisce automaticamente `\` vs `/`.

Il DB Windows sarà in:
```
C:\Users\{username}\AppData\Roaming\com.fluxion.desktop\fluxion.db
```

Il Python voice agent però non sa dove sta il DB Windows — questo è il gap da fixare (sezione 3, Fix 1).

---

## 5. Packaging Strategy Windows

### Raccomandazione: PyInstaller + esclusione Chatterbox

```
Windows bundle strategy:
- TTS primary: Piper (via piper-onnx Python package) — modello 60MB
- TTS fallback: pyttsx3 + Windows SAPI5 (zero download)
- STT primary: Groq cloud (già configurato)
- STT fallback: FasterWhisper base (~145MB download al primo avvio)
- VAD: Silero ONNX (~2MB — includere nel bundle)

PyInstaller exe finale: ~400-500MB (accettabile)
Installer NSIS totale: ~600-700MB con WebView2 bootstrap
```

**Creare `voice-agent/requirements-windows.txt`** che esclude:
- `chatterbox-tts` (2.5GB PyTorch)
- `torchaudio`
- `pipecat-ai` (SIP/VoIP non critico per v1.0)
- `aiortc`, `aioice`, `av`

**Tauri Sidecar**:
```json
// tauri.conf.json:
"bundle": { "externalBin": ["binaries/voice-agent"] }
```

In `voice_pipeline.rs`, usare `tauri::api::process::Command::new_sidecar("voice-agent")`.

**Attenzione antivirus**: PyInstaller exe vengono spesso flaggati da Windows Defender. EV code signing certificate riduce drasticamente i false positive.

---

## 6. CI/CD Windows Build

Il workflow `.github/workflows/release.yml` ha già la struttura Windows corretta con `windows-latest` runner. Gap: non builda il voice agent PyInstaller exe.

**Step da aggiungere nel workflow:**
```yaml
- name: Build Voice Agent Windows
  if: matrix.platform == 'windows-latest'
  shell: pwsh
  run: |
    cd voice-agent
    pip install pyinstaller -r requirements-windows.txt
    pyinstaller --onefile --name=voice-agent --add-data "models;models" main.py
    cp dist/voice-agent.exe ../src-tauri/binaries/voice-agent-x86_64-pc-windows-msvc.exe
```

**Code Signing Windows (Authenticode):**
- OV Certificate: ~$100-200/anno
- **EV Certificate: ~$300-500/anno — rimuove SmartScreen completamente (RACCOMANDATO)**

---

## 7. Piano di Remediation

### Priorità ALTA — Bloccanti (1.5 gg)

| # | Task | File | Effort |
|---|------|------|--------|
| P1 | SystemTTS Windows fallback con pyttsx3 | `src/tts.py` | 0.5 gg |
| P2 | SQLite path Windows in `main.py` | `main.py` | 0.25 gg |
| P3 | Piper binary discovery Windows / migra a piper-onnx | `src/tts.py` | 0.5 gg |
| P4 | Rimuovere path `/Volumes/` hardcoded | `src/booking_state_machine.py` | 0.25 gg |

### Priorità MEDIA (5.5 gg)

| # | Task | Effort |
|---|------|--------|
| P5 | `requirements-windows.txt` (senza chatterbox/torch) | 0.25 gg |
| P6 | `tauri.conf.json` Windows bundle config | 0.25 gg |
| P7 | `voice_pipeline.rs` — Windows venv path | test only |
| P8 | PyInstaller spec file + test su Windows CI | 1.5 gg |
| P9 | GitHub Actions Windows job aggiornato con sidecar | 1.0 gg |
| P10 | EV Code signing setup | 0.5 gg |
| Testing Windows VM manuale | 2.0 gg |

### Effort totale

| Area | Giorni |
|------|--------|
| P1-P4 (bloccanti) | 1.5 |
| P5-P7 (configurazione) | 0.75 |
| P8-P9 (PyInstaller + CI) | 2.5 |
| P10 (signing) | 0.5 |
| Testing Windows VM | 2.0 |
| Buffer/debugging | 1.5 |
| **TOTALE** | **~9 giorni** |

---

## 8. Rischi

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|------------|---------|-------------|
| Antivirus flagga voice-agent.exe (PyInstaller) | ALTA | ALTO | EV code signing certificate |
| WebView2 non pre-installato | BASSA | MEDIO | `embedBootstrapper` nella config Tauri |
| Voci italiane Windows SAPI5 non installate | MEDIA | MEDIO | Piper TTS come primary (include voice IT) |
| FasterWhisper 145MB download al primo avvio | CERTA | MEDIO | Pre-bundlare in PyInstaller exe |
| Chatterbox TTS incompatibile con Windows packaging | ALTA | MEDIO | Su Windows usare Piper come primary TTS |
| pipecat-ai / aiortc falliscono build Windows | MEDIA | BASSO | Escluderli da requirements-windows.txt |

---

## Sources

- Tauri 2.x Windows Installer docs — WebView2 modes, NSIS config (HIGH)
- Tauri 2.x Windows Code Signing docs — Authenticode setup (HIGH)
- Tauri 2.x GitHub Actions Pipeline docs — CI setup (HIGH)
- faster-whisper PyPI — Windows wheel disponibili (HIGH)
- piper-onnx PyPI — alternativa cross-platform a piper binary (MEDIUM)
- Analisi diretta codebase FLUXION — path hardcoded, struttura voice agent (HIGH)
