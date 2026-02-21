# PROMPT - FIX VOICE AGENT "LOAD FAILED"

## 🚨 PROBLEMA

Voice Agent su iMac mostra **"Load Failed"** quando si clicca sul microfono.

### Stato Attuale
- ✅ Fluxion App (Tauri) avviata su iMac
- ✅ Voice Agent backend (Python) avviato su porta 3002
- ✅ HTTP Bridge su porta 3001
- ✅ Comunicazione tra frontend e backend funzionante
- ❌ **Microfono: "Load Failed"**

### Root Cause Identificati

#### 1. **VAD (Voice Activity Detection) Mancante**
```
ModuleNotFoundError: No module named 'onnxruntime'
```
- Voice Agent richiede `onnxruntime` per Silero VAD
- Python 3.13 su iMac non ha supporto onnxruntime
- Fallback a webrtcvad parzialmente implementato ma con errori

#### 2. **Permessi Microfono Tauri v2**
- In dev mode (`tauri dev`) i permessi macOS non funzionano correttamente
- `Info.plist` ha `NSMicrophoneUsageDescription` ma non viene riconosciuto
- App Tauri nativa non richiede permesso microfono all'utente

#### 3. **Configurazione Browser vs Tauri**
- Browser (Chrome/Safari) richiede esplicitamente permessi e funziona meglio
- App Tauri nativa ha problemi in development mode

---

## 🎯 OBIETTIVO

**Far funzionare il microfono in Voice Agent** con una delle seguenti soluzioni:

### Opzione A: Fix VAD con webrtcvad (Consigliata)
- Rimuovere dipendenza onnxruntime/Silero VAD
- Implementare completamente webrtcvad come VAD alternativo
- Testare funzionamento microfono

### Opzione B: Build Tauri Produzione
- Creare build di produzione (`npm run tauri build`)
- Firmare app con permessi microfono corretti
- Installare e testare app .dmg

### Opzione C: Voice Agent via Browser
- Configurare ambiente per test via browser
- Risolvere CORS/security per comunicazione browser ↔ Voice Agent
- Testare flusso completo in Chrome/Safari

---

## 📋 TASK DA COMPLETARE

### Pre-requisiti Verifica
- [ ] Verificare SSH attivo verso iMac (192.168.1.2)
- [ ] Verificare stato Voice Agent (`curl http://127.0.0.1:3002/health`)
- [ ] Verificare stato Fluxion (`pgrep -f 'Fluxion'`)
- [ ] Verificare porte in uso (3001, 3002, 1420/5173)

### Fix VAD (Opzione A)
- [ ] Analizzare file `voice-agent/src/vad_http_handler.py`
- [ ] Rimuovere/rinominare file che importa silero/onnxruntime
- [ ] Implementare VAD wrapper con webrtcvad completamente funzionante
- [ ] Modificare `voice-agent/main.py` per usare VAD semplificato
- [ ] Installare `webrtcvad-wheels` su iMac (già fatto, verificare)
- [ ] Testare avvio Voice Agent senza errori
- [ ] Testare endpoint VAD (`/api/voice/vad/start`)

### Fix Permessi Microfono Tauri (Opzione B)
- [ ] Verificare `src-tauri/Info.plist` contiene `NSMicrophoneUsageDescription`
- [ ] Verificare `src-tauri/tauri.conf.json` ha capabilities corrette
- [ ] Aggiungere entitlements per microfono in macOS
- [ ] Eseguire build produzione (`npm run tauri build`)
- [ ] Verificare .dmg generato in `src-tauri/target/release/bundle/`
- [ ] Installare app e testare permessi microfono

### Configurazione Browser (Opzione C)
- [ ] Avviare Vite standalone (`npm run dev`)
- [ ] Verificare CORS per comunicazione con Voice Agent
- [ ] Configurare security headers in Voice Agent per accettare richieste da localhost
- [ ] Testare in Chrome/Safari su http://localhost:1420

### Test Finale
- [ ] Cliccare microfono in Voice Agent
- [ ] Verificare nessun "Load Failed"
- [ ] Verificare VAD rileva parola (indicatore visivo)
- [ ] Verificare STT (Speech-to-Text) funziona
- [ ] Verificare risposta TTS (Text-to-Speech) arriva

---

## 🔧 COMANDI RIFERIMENTO

### SSH iMac
```bash
ssh imac  # configurato in ~/.ssh/config
# o
ssh gianlucadistasi@192.168.1.2
```

### Verifica Stato
```bash
# Voice Agent
curl http://127.0.0.1:3002/health

# Processi
pgrep -f 'Fluxion'
pgrep -f 'python.*main.py'

# Porte
lsof -i :3001  # HTTP Bridge
lsof -i :3002  # Voice Agent
lsof -i :1420  # Vite
```

### Avvio Servizi
```bash
# Voice Agent
cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
python3 main.py --port 3002

# Fluxion Dev (Vite)
cd "/Volumes/MacSSD - Dati/fluxion"
npm run dev

# Fluxion Tauri Dev
cd "/Volumes/MacSSD - Dati/fluxion"
npm run tauri dev
```

### Build Produzione
```bash
cd "/Volumes/MacSSD - Dati/fluxion"
npm run tauri build
# DMG in: src-tauri/target/release/bundle/dmg/
```

---

## 📁 FILES CRITICI

| File | Path | Note |
|------|------|------|
| VAD Handler | `voice-agent/src/vad_http_handler.py` | Da modificare per webrtcvad |
| Main Voice | `voice-agent/main.py` | Avvio server, gestione VAD |
| Tauri Config | `src-tauri/tauri.conf.json` | Permessi, capabilities |
| Info.plist | `src-tauri/Info.plist` | Permessi macOS |
| Cargo.toml | `src-tauri/Cargo.toml` | Features, plugins |

---

## ✅ CRITERI DI SUCCESSO

1. **Microfono si attiva** senza "Load Failed"
2. **VAD rileva parola** (indicatore visivo attivo)
3. **STT funziona** (trascrizione audio → testo)
4. **Risposta arriva** (TTS o azione)
5. **Nessun errore** in console browser o log Python

---

## 🚫 ANTI-PATTERN DA EVITARE

- ❌ Non installare onnxruntime (non compatibile Python 3.13)
- ❌ Non modificare Cargo.toml features senza verificare compatibilità
- ❌ Non usare `sudo pip3` (rompe sistema)
- ❌ Non modificare codice senza backup

---

## 📞 COMUNICAZIONE

Durante la sessione, comunicare:
- ✅ "Step X completato" quando un task è fatto
- ❌ "Errore: [messaggio]" se c'è un problema
- ❓ "Domanda: [chiarimento]" se serve spiegazione

---

## 🎉 OUTPUT ATTESO

Al termine della sessione:
1. Microfono funzionante in Voice Agent
2. Documentazione modifiche effettuate
3. Backup files modificati
4. Istruzioni per sessioni future

---

*Prompt creato: 2026-02-19*  
*Problema: Voice Agent "Load Failed"*  
*Priorità: Alta*
