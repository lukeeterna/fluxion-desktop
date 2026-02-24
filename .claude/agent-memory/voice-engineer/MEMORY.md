# Voice Engineer Memory — FLUXION "Sara"
> Max 200 righe. Aggiornare dopo ogni sessione significativa.

## Architettura Audio Path
- **STT**: whisper.cpp `ggml-small` via subprocess (~30s su iMac per audio reale)
- **Timeout Python subprocess**: 30s (in `stt.py` riga ~194)
- **Timeout Rust client**: 120s (fixato da 30s — commit `7a26712`)
- Il path audio risponde in ~31s su iMac corrente (hardware lento per Whisper)

## Whisper.cpp Performance su iMac
- Modello `ggml-small` impiega ~30s per 1s di audio silenzioso
- Per audio reale con parlato atteso: ~30-40s
- Causa: CPU-only inference su iMac vecchio
- Fix futuro: passare a `ggml-tiny` per ridurre latenza (~10s), o usare Groq STT cloud

## Problemi Noti (non da fixare ora)
- `spaCy not installed` — warning costante nei log, non blocca nulla
- `table audit_log has no column named notes` — migration mancante, non critico
- `sentence-transformers not installed` — FAQ semantic retrieval degraded a keyword-only

## Riavvio Pipeline iMac
`pkill -f 'python main.py'` NON funziona (P maiuscola). Usare:
```bash
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

## Build iMac — Comando Corretto
`nohup` non disponibile su iMac (zsh). Usare:
```bash
ssh imac 'export PATH="/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:$PATH" && cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri build > /tmp/fluxion-build3.log 2>&1 &'
```
Nota: usare singoli apici nell'SSH per evitare problemi con il path con spazi.

## File Chiave
- `src-tauri/src/commands/voice_pipeline.rs` — timeout Rust (riga 320)
- `voice-agent/src/stt.py` — subprocess whisper.cpp + timeout interno (riga ~194)
- `voice-agent/main.py` — entry point server porta 3002
- Log pipeline: `/tmp/voice-pipeline.log` (iMac)
- Log build: `/tmp/fluxion-build3.log` (iMac)
