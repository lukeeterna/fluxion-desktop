# Sessione: Voice Agent DB Integration

**Data**: 2026-01-11T01:30:00
**Fase**: 7 (Voice Agent + WhatsApp + FLUXION IA)
**Agenti**: rust-backend, voice-engineer

---

## Obiettivo Sessione
Collegare Voice Agent al database per identificazione clienti e creazione appuntamenti reali.

---

## Modifiche Effettuate

### 1. Voice Agent Pipeline Rewrite (`voice-agent/src/pipeline.py`)
- Integrato caricamento FAQ da `data/faq_salone.md`
- FAQ incluso nel system prompt di Groq LLM
- Aggiunto HTTP Bridge client per comunicazione con Tauri backend
- Implementata estrazione info prenotazione dal testo utente
- Implementata identificazione cliente da pattern "sono X" / "mi chiamo X"
- Test diretto: risponde con prezzi corretti (es. "taglio uomo €18, donna €35")

### 2. Python Virtual Environment
- Creato `voice-agent/venv/` su iMac
- Dipendenze installate: aiohttp, python-dotenv, groq
- Risolto errore "externally-managed-environment" di macOS

### 3. Rust: Priorità venv Python (`voice_pipeline.rs`)
- Funzione `find_python()` ora accetta `voice_agent_dir` parameter
- Prima cerca `venv/bin/python3` (Unix) o `venv/Scripts/python.exe` (Windows)
- Fallback a Python di sistema se venv non esiste

### 4. HTTP Bridge Voice API (`http_bridge.rs`)
Aggiunti 3 nuovi endpoints per Voice Agent:

```rust
// Cerca clienti
GET /api/clienti/search?q=Mario
// Response: [{"id": "...", "nome": "Mario", "cognome": "Rossi", ...}]

// Slot disponibili
POST /api/appuntamenti/disponibilita
// Body: {"data": "2026-01-12", "servizio": "Taglio"}
// Response: {"slots": ["09:00", "10:00", ...]}

// Crea appuntamento
POST /api/appuntamenti/create
// Body: {"cliente_id": "...", "servizio": "Taglio", "data": "2026-01-12", "ora": "10:00"}
// Response: {"success": true, "id": "..."}
```

### 5. UI Bug Fixes
- Cambiato nome assistente da "Sara" a "Paola" in VoiceAgent.tsx
- Cambiato "Groq Llama 3.3 70B" a "FLUXION AI"
- Header: icone notifiche e menu ora funzionali con dropdown
- Sidebar: profilo utente collegato a /impostazioni
- RagChat: rimossi badge confidenza e modello

---

## Commits

| Hash | Descrizione |
|------|-------------|
| `c6940d5` | feat(voice): prioritize Python venv for voice-agent |
| `d633ade` | feat(http-bridge): add Voice Agent API endpoints |

---

## Test Effettuati

### Voice Agent (test diretto Python)
```bash
cd /Volumes/MacSSD\ -\ Dati/FLUXION/voice-agent
source venv/bin/activate
python3 -c "... test pipeline ..."
```
**Risultato**:
- FAQ caricato: 2312 chars
- Intent detection: OK
- Risposta: "Il costo di un taglio dipende dal tipo: uomo €18, donna €35..."

### Voice Agent HTTP Server
```bash
curl -X POST http://127.0.0.1:3002/api/voice/process \
  -H 'Content-Type: application/json' \
  -d '{"text": "Vorrei prenotare un taglio per domani"}'
```
**Risultato**:
- success: true
- intent: "prenotazione"
- response: Conferma prenotazione in italiano

---

## Stato Finale

### Funzionante
- Voice Agent risponde in italiano con persona "Paola"
- FAQ caricato e usato per risposte sui prezzi
- Intent detection (prenotazione, cancellazione, informazioni, etc.)
- TTS funzionante (macOS say)

### Da Testare (domani)
- Client identification via HTTP Bridge `/api/clienti/search`
- Booking creation via HTTP Bridge `/api/appuntamenti/create`
- Richiede rebuild Tauri per includere nuovi endpoints

### Bloccato
- WhatsApp: in attesa scansione QR da parte dell'utente

---

## Prossimi Passi

1. **Rebuild Tauri su iMac**
   ```bash
   cd /Volumes/MacSSD\ -\ Dati/FLUXION
   git pull
   npm run tauri dev
   ```

2. **Test Client Identification**
   ```bash
   curl 'http://127.0.0.1:3001/api/clienti/search?q=Mario'
   ```

3. **Test Full Booking Flow**
   - Dire "Sono Mario, vorrei prenotare un taglio per domani"
   - Verificare che trovi Mario nel DB
   - Verificare che crei l'appuntamento

4. **WhatsApp**: Ricordare all'utente di scansionare QR

---

## File Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `voice-agent/src/pipeline.py` | Rewrite | RAG + HTTP Bridge integration |
| `src-tauri/src/commands/voice_pipeline.rs` | Edit | venv Python priority |
| `src-tauri/src/http_bridge.rs` | Edit | +3 Voice API endpoints |
| `src/pages/VoiceAgent.tsx` | Edit | Sara→Paola, Groq→FLUXION AI |
| `src/components/rag/RagChat.tsx` | Edit | Rimossi badge |
| `src/components/layout/Header.tsx` | Edit | Dropdown funzionali |
| `src/components/layout/Sidebar.tsx` | Edit | Profile link |
