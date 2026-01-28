# Fluxion Project Context

## Environment Configuration

| Machine | Host | Path | Usage |
|---------|------|------|-------|
| **MacBook** | localhost | `/Volumes/MontereyT7/FLUXION` | Development |
| **iMac** | 192.168.1.9 | `/Volumes/MacSSD - Dati/fluxion` | Live Testing |

> **NOTA**: Tauri 2.x NON funziona su macOS Big Sur. Dev su MacBook, test su iMac (Monterey 12.7.4).

---

## BMAD Task Execution Protocol

### Ogni Task DEVE seguire questo workflow:

```
1. Implementare il codice
2. Eseguire test locali (pytest, cargo test, npm run type-check)
3. Sync su iMac: scp file imac:/path/
4. Restart servizi se Python modificato: ssh imac "..."
5. TEST LIVE su iMac - verifica funzionalità REALE
6. Solo se LIVE OK → Commit e Push
```

### Test Locali (MacBook)

```bash
# TypeScript
npm run type-check && npm run lint

# Rust (se modificato)
cd src-tauri && cargo test && cd ..

# Python (se modificato)
cd voice-agent && pytest tests/ -v && cd ..
```

### Sync su iMac

```bash
# Sync singolo file
scp /Volumes/MontereyT7/FLUXION/path/to/file.py \
    "imac:/Volumes/MacSSD\ -\ Dati/fluxion/path/to/"

# Sync directory
scp -r /Volumes/MontereyT7/FLUXION/voice-agent/src/ \
    "imac:/Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/src/"
```

### Restart Servizi iMac

```bash
# Restart voice pipeline (se Python modificato)
ssh imac "lsof -ti :3002 | xargs kill -9 2>/dev/null; \
  cd /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent && \
  source venv/bin/activate && \
  nohup python main.py > /tmp/voice.log 2>&1 &"

# Verifica servizi attivi
ssh imac "curl -s http://localhost:3001/health && \
          curl -s http://localhost:3002/health"
```

### Test LIVE su iMac

```bash
# Test voice agent via HTTP
ssh imac "curl -X POST http://localhost:3002/api/voice/process \
  -H 'Content-Type: application/json' \
  -d '{\"session_id\": \"test\", \"text\": \"INPUT DA TESTARE\"}'"

# Verifica risposta contiene i valori attesi
# Es: intent corretto, layer corretto, response attesa
```

---

## Servizi Attivi

| Servizio | Porta | Descrizione |
|----------|-------|-------------|
| HTTP Bridge | 3001 | Rust/Tauri backend API |
| Voice Pipeline | 3002 | Python voice agent |

---

## Voice Agent Pipeline

### 4-Layer Architecture

```
L0: Special Commands (annulla, stop, aiuto) → Regex
L1: Intent Classification (PRENOTAZIONE, CANCELLAZIONE, etc.) → Patterns
L2: Slot Filling (Booking State Machine)
L3: FAQ Retrieval
L4: Groq LLM Fallback
```

### Intent Priority

1. **L1** handles CANCELLAZIONE/SPOSTAMENTO BEFORE L2 booking SM
2. PRENOTAZIONE goes to L2 for slot filling
3. FAQ/general queries go to L3/L4

---

## Commit Protocol

```bash
# Pre-commit checklist
1. npm run type-check  ✅
2. npm run lint        ✅
3. cargo test          ✅ (se Rust)
4. pytest tests/       ✅ (se Python)
5. LIVE test su iMac   ✅ (OBBLIGATORIO)

# Commit
git add <files>
git commit -m "type(scope): description"
git push origin <branch>
```

---

## Quality Gates

| Gate | Criterio | Tool |
|------|----------|------|
| Type Safety | 0 errori TypeScript | `npm run type-check` |
| Lint | 0 errori ESLint | `npm run lint` |
| Rust Tests | Tutti passati | `cargo test` |
| Python Tests | Tutti passati | `pytest` |
| **LIVE Test** | Funziona su iMac | Manual / curl |

---

*Aggiornato: 2026-01-28*
