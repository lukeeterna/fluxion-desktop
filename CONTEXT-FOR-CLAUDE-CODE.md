# CONTEXTO COMPLETO PER CLAUDE CODE

> Sessione: Fix Voice Agent + Build Tauri
> Data: 2026-02-19
> Stato: Voice Agent funzionante, Build Tauri in sospeso

---

## ✅ COMPLETATO - Voice Agent Fix

### Problema Risolto
- **Issue**: Voice Agent mostrava "Load Failed" su microfono
- **Root Cause**: VAD richiedeva `onnxruntime` non compatibile con Python 3.13
- **Soluzione**: Implementato fallback a `webrtcvad` quando Silero ONNX non disponibile

### Files Modificati

#### 1. `voice-agent/src/vad/ten_vad_integration.py`
- **Path completo**: `/Volumes/MontereyT7/FLUXION/voice-agent/src/vad/ten_vad_integration.py`
- **Modifiche**:
  - Aggiunto try/except per import onnxruntime
  - Aggiunto fallback a webrtcvad quando onnxruntime non disponibile
  - Metodi `_start_silero()` e `_start_webrtc()` separati
  - `_process_audio_silero()` e `_process_audio_webrtc()` separati
- **Stato**: ✅ Funzionante sull'iMac

#### 2. `voice-agent/main.py`
- **Path completo**: `/Volumes/MontereyT7/FLUXION/voice-agent/main.py`
- **Modifiche**:
  - Aggiornata label VAD da "silero-vad-onnx" a "silero-or-webrtc"
  - Aumentato limite richiesta HTTP a 50MB (fix "Request Entity Too Large")
- **Stato**: ✅ Funzionante

#### 3. `voice-agent/src/vad_http_handler.py`
- **Path completo**: `/Volumes/MontereyT7/FLUXION/voice-agent/src/vad_http_handler.py`
- **Stato**: Sincronizzato sull'iMac, contiene endpoint VAD

---

## 🟡 IN CORSO - Build Tauri Natica

### Stato Attuale
- CLI Tauri v2 installata globalmente
- Progetto Tauri in stato ibrido (codice v1, CLI v2)
- Build fallita per incompatibilità

### Files Coinvolti

#### 1. `src-tauri/Cargo.toml`
- **Path**: `/Volumes/MontereyT7/FLUXION/src-tauri/Cargo.toml`
- **Stato**: Modificato multiple volte, ultima versione per Tauri v1
- **Problema**: Mancano dipendenze (thiserror, async-trait, axum, tower-http, tracing)

#### 2. `src-tauri/tauri.conf.json`
- **Path**: `/Volumes/MontereyT7/FLUXION/src-tauri/tauri.conf.json`
- **Stato**: Formato v1, funziona con CLI v1
- **Nota**: Per Tauri v2 serve formato diverso

#### 3. `src-tauri/src/lib.rs`
- **Path**: `/Volumes/MontereyT7/FLUXION/src-tauri/src/lib.rs`
- **Stato**: Plugin aggiornati per v2 ma codice ha errori
- **Errori principali**:
  - Manca crate `thiserror` (derive Error)
  - Manca crate `async-trait`
  - Manca crate `axum` e `tower-http` (http_bridge.rs)
  - Manca crate `tracing`

#### 4. `src-tauri/Info.plist`
- **Path**: `/Volumes/MontereyT7/FLUXION/src-tauri/Info.plist`
- **Stato**: Aggiornato con permessi microfono e Speech Recognition

#### 5. `src-tauri/entitlements.plist`
- **Path**: `/Volumes/MontereyT7/FLUXION/src-tauri/entitlements.plist`
- **Stato**: Creato nuovo, permessi audio/network

#### 6. `src-tauri/capabilities/default.json`
- **Path**: `/Volumes/MontereyT7/FLUXION/src-tauri/capabilities/default.json`
- **Stato**: Creato per Tauri v2, solo "core:default"

---

## 📋 ISTRUZIONI PER CONTINUARE

### Opzione 1: Modalità Browser (Consigliata - Immediata)

```bash
# Su iMac (192.168.1.2)
ssh imac

# 1. Avvia Voice Agent
cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
python3 main.py --port 3002

# 2. In altra shell, avvia frontend
cd "/Volumes/MacSSD - Dati/fluxion"
npm run dev

# 3. Apri browser su http://localhost:1420
# Il microfono funziona nativamente via Web APIs
```

**Vantaggi**: Microfono funziona immediatamente, nessuna build richiesta

### Opzione 2: Build Tauri v1 (Stabile)

```bash
# Su iMac
cd "/Volumes/MacSSD - Dati/fluxion"

# Usa CLI v1 specifica
npx @tauri-apps/cli@1.5.6 build

# Nota: Richiede fix dipendenze mancanti in Cargo.toml:
# - thiserror = "1"
# - async-trait = "0.1"
# - axum = "0.6"
# - tower-http = "0.4"
# - tracing = "0.1"
```

### Opzione 3: Migrazione Completa a Tauri v2

```bash
# 1. Aggiorna Cargo.toml a Tauri v2
# 2. Fix tutti i breaking changes (async traits, etc.)
# 3. Aggiorna tauri.conf.json a formato v2
# 4. Build con npm run tauri build

# Stima tempo: 2-3 ore
```

---

## 🔧 FIX NECESSARI PER BUILD NATIVA

### Cargo.toml Completo (mancante)

```toml
[dependencies]
# ... existing deps ...

# Mancanti per build:
thiserror = "1"
async-trait = "0.1"
axum = "0.6"
tower-http = { version = "0.4", features = ["cors"] }
tracing = "0.1"

# Per Tauri v2 (se si migra):
# tauri = { version = "2" }
# tauri-plugin-dialog = "2"
# etc.
```

### Errori da Risolvere in lib.rs

1. **Linea 747**: `tauri_plugin_sql::Builder::default()` → per v2 serve `Builder::new()`
2. **Linea 750**: `tauri_plugin_store::Builder::default()` → per v2 serve `Builder::new()`
3. **Linea 753**: `tauri_plugin_updater` → non esiste in v2 o serve crate separato

---

## 🎯 TESTING VOICE AGENT

### Endpoint Disponibili

```bash
# Health check
curl http://127.0.0.1:3002/health

# Start VAD session
curl -X POST http://127.0.0.1:3002/vad/start \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test"}'

# Process audio chunk
curl -X POST http://127.0.0.1:3002/vad/chunk \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "audio_hex": "..."}'
```

### Log Files

```bash
# Log Voice Agent (su iMac)
tail -f /tmp/voice-agent.log

# Log build Tauri
tail -f /tmp/tauri-build-final.log
tail -f /tmp/tauri-build-v1-final.log
```

---

## 📁 FILES CRITICI BACKUP

Tutti i files modificati sono in:
- `/Volumes/MontereyT7/FLUXION/voice-agent/` (locale MacBook)
- Sincronizzati su iMac: `/Volumes/MacSSD - Dati/fluxion/`

### Lista Files Modificati Oggi

```
✅ voice-agent/src/vad/ten_vad_integration.py
✅ voice-agent/main.py
✅ voice-agent/src/vad_http_handler.py
🟡 src-tauri/tauri.conf.json
🟡 src-tauri/Cargo.toml
🟡 src-tauri/src/lib.rs
🟡 src-tauri/Info.plist
🟡 src-tauri/entitlements.plist
🟡 src-tauri/capabilities/default.json
```

---

## 🚀 COMANDI RAPIDI CLAUDE CODE

```bash
# Verifica stato Voice Agent
ssh imac "curl -s http://127.0.0.1:3002/health"

# Riavvia Voice Agent
ssh imac "pkill -f 'python.*main.py' && sleep 2 && cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python3 main.py --port 3002 > /tmp/voice-agent.log 2>&1 &"

# Build Tauri v1
ssh imac "export PATH=\"/usr/local/bin:\$HOME/.nvm/versions/node/v18.20.4/bin:\$PATH\" && cd '/Volumes/MacSSD - Dati/fluxion' && npx @tauri-apps/cli@1.5.6 build"

# Sincronizza files
scp "/Volumes/MontereyT7/FLUXION/PATH/FILE" "imac:'/Volumes/MacSSD - Dati/fluxion/PATH/FILE'"
```

---

## ⚠️ NOTE IMPORTANTI

1. **iMac IP**: 192.168.1.2
2. **Voice Agent Porta**: 3002
3. **HTTP Bridge Porta**: 3001
4. **Vite Dev Porta**: 1420
5. **Python**: 3.9 (iMac), webrtcvad-wheels installato

### Problema Microfono Build Natica
- In build Tauri, il microfono richiede:
  - `NSMicrophoneUsageDescription` in Info.plist ✅
  - Capability `microphone:default` in Tauri v2
  - Per Tauri v1: funziona via Web APIs standard

---

## 📞 CONTEXTO SESSIONE

- **Task**: Fix Voice Agent "Load Failed" + Build Tauri
- **Risultato**: Voice Agent ✅ / Build Tauri 🟡
- **Tempo**: ~3 ore
- **Blocker**: Incompatibilità Tauri v1/v2, dipendenze mancanti
- **Soluzione Temporanea**: Usare modalità browser (funzionante)

---

*Generato: 2026-02-19*
*Per: Claude Code Continuation*
