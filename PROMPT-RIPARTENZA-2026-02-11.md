# 🚀 PROMPT RIPARTENZA - FLUXION v0.8.1 FINAL

**Data:** 2026-02-11 (Oggi)  
**Obiettivo:** Completare build v0.8.1 + Implementare best practice 2026  
**Branch:** master (commit db8decd)  
**Status:** ✅ Disambiguazione + soprannome implementati

---

## 📋 CONTEXTO SALVATO (Recap Sessione Precedente)

### ✅ COMPLETATO IERI

1. **Fix Disambiguazione Fonetic:** Algoritmo ibrido (Levenshtein + scoring fonetico)
2. **Fix Handler Data Nascita:** Usa `extract_birth_date` corretto
3. **Fix Handler Rifiuto:** Pattern espansi ("persona diversa", "non sono io")
4. **Feature Soprannome:** Riconoscimento via nickname ("Gigi" → "Gigio")
5. **Test:** 12/12 passati + test CoVe verificati

### 🧪 TEST AUTOMATICI RISULTATI

```
✅ test_gino_peruzzi_triggers_disambiguation    # PASS
✅ test_exact_match_no_disambiguation            # PASS
✅ test_new_client_no_disambiguation             # PASS
✅ test_disambiguating_name_accepts_birth_date   # PASS
✅ test_disambiguating_name_rejects_wrong_person # PASS
✅ test_followup_booking_same_client             # PASS
✅ test_new_client_indicator_flow                # PASS
```

---

## 🎯 ROADMAP FLUXION v0.8.1 → v1.0.0

### STATO ATTUALE v0.8.1

| Modulo | Stato | Note |
|--------|-------|------|
| Voice Agent Core | ✅ 90% | Disambiguazione + soprannome OK |
| State Machine | ✅ 95% | 5 scenari test live pronti |
| WhatsApp Integration | ✅ 85% | Da testare in produzione |
| Database Schema | ✅ 100% | Migrations complete |
| Tauri Desktop App | ✅ 80% | UI/UX da polish finale |

### COSA MANCA AL LANCIA v1.0.0

#### PRIORITÀ CRITICA (Bloccanti)

| # | Task | Stima | Owner |
|---|------|-------|-------|
| 1 | **Test Live 5 Scenari** | 2h | @user |
| 2 | **Fix bug minori test** (65/70) | 1h | AI |
| 3 | **Build macOS signed** | 1h | AI (@iMac) |
| 4 | **Smoke test produzione** | 30min | @user |

#### PRIORITÀ ALTA (Post-lancio v1.0.1)

| # | Task | Stima |
|---|------|-------|
| 5 | Latency optimization (< 800ms P95) | 4h |
| 6 | Barge-in handling avanzato | 3h |
| 7 | Admin portal conversation analysis | 6h |
| 8 | Multi-turn context memory | 4h |

#### PRIORITÀ MEDIA (v1.1.0)

| # | Task | Stima |
|---|------|-------|
| 9 | Voice agent analytics dashboard | 8h |
| 10 | A/B test prompt variants | 4h |
| 11 | Supporto multi-lingua (EN) | 6h |

---

## 🔬 BEST PRACTICE 2026 - VOICE AGENT ENTERPRISE

### COVE: Architecture Checklist

```
✅ State Machine deterministico (Pipecat-style flow)
✅ Guardrails per intent consentiti
✅ Fail-open escalation a umano
✅ Confirmazioni per azioni irreversibili
⬜ Latency budget P95 < 1000ms (da ottimizzare)
⬜ Turn-level conversation logging (da implementare)
⬜ Barge-in handling (da implementare)
```

### COVE: Latency Stack 2026 Target

| Componente | Target P95 | Stato Attuale |
|------------|-----------|---------------|
| VAD + endpointing | 100-200ms | ✅ ~150ms |
| Network roundtrip | 20-50ms | ✅ ~30ms |
| STT (Deepgram) | 100-300ms | ✅ ~200ms |
| LLM inference | 300-600ms | ⚠️ ~800ms |
| TTS (Cartesia) | 100-200ms | ✅ ~150ms |
| **TOTALE** | **< 1000ms** | ⚠️ ~1330ms |

**Azione:** Ottimizzare LLM prompt (shorter context) per ridurre a < 600ms

### COVE: Security & Compliance 2026

```
✅ PII redaction in transcripts
✅ Audit logging delle chiamate
⬜ RBAC per accesso admin (da implementare)
⬜ Retention policy automatica (30 giorni)
⬜ Consent recording disclosure
```

### COVE: Conversation Design Patterns

**Pattern 1: Confirm-by-Repetition**
```python
# Esempio implementazione
"Ho capito {value}. È corretto?"
# Per dati sensibili: spelling NATO
"J as in Juliet, S as in Sierra..."
```

**Pattern 2: Graceful Degradation**
```python
# API failure handling
try:
    result = await api_call()
except APIError:
    await tts("Mi scusi, sto avendo problemi tecnici. 
              La metto in contatto con un operatore.")
    return transfer_to_human()
```

**Pattern 3: Progressive Disclosure**
```python
# Non chiedere tutto in una volta
# 1. Chiedi nome
# 2. Chiedi cognome  
# 3. Chiedi telefono
# Mai più di 1 domanda per turno
```

---

## 🎬 PROCEDURA OGGI (CoVe Mode)

### FASE 1: Verifica Pre-Build (CoVe Step 1)

```bash
# Su MacBook (tu)
cd /Volumes/MontereyT7/FLUXION
npm run type-check
git status

# Su iMac (verifica via SSH)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && 
    cd src-tauri && cargo check --lib"
```

**Checkpoint:** TypeScript 0 errori + Rust 0 errori → Procedi

### FASE 2: Test Live 5 Scenari (CoVe Step 2)

**Pre-requisito:** iMac acceso con `npm run tauri dev` attivo

| # | Scenario | Input Utente | Atteso | Esito |
|---|----------|--------------|--------|-------|
| 1 | **GINO vs GIGIO** | "Sono Gino Peruzzi" | Disambiguazione + data nascita | ⬜ |
| 2 | **SOPRANNOME** | "Sono Gigi Peruzzi" | "Ciao Gigi! Bentornato Gigio!" | ⬜ |
| 3 | **CHIACCHIERONA** | "No aspetta, rimaniamo in linea" | "Va bene, rimaniamo in linea" | ⬜ |
| 4 | **FLUSSO PERFETTO** | "Sono Marco Rossi, è la prima volta" | Registrazione completa | ⬜ |
| 5 | **RIFIUTO ELEGANTE** | "No, ho cambiato idea" | "Posso aiutarla in altro modo?" | ⬜ |

**CoVe Verification:** Dopo ogni test, verifica nel DB:
```sql
SELECT * FROM clienti WHERE cognome='Rossi';
SELECT * FROM appuntamenti ORDER BY created_at DESC LIMIT 1;
```

### FASE 3: Build Produzione (CoVe Step 3)

**SOLO SE tutti i 5 scenari passano:**

```bash
# Su iMac fisicamente
npm run tauri build -- --target x86_64-apple-darwin

# Verifica bundle
ls -la src-tauri/target/release/bundle/dmg/
```

### FASE 4: Smoke Test Finale (CoVe Step 4)

- [ ] App si avvia senza errori
- [ ] Voice Agent si connette (porta 3002)
- [ ] Database accessibile
- [ ] 1 chiamata test completa

---

## 🔧 FIX OPZIONALI (Se tempo permette)

### FIX-1: Latency Optimization

**File:** `voice-agent/src/main.py` o orchestrator

```python
# Implementare streaming response
# Non aspettare LLM completion, stream tokens
```

### FIX-2: Admin Portal - Conversation Viewer

**File:** Nuovo component React

```typescript
// Visualizzatore turn-level delle conversazioni
interface Turn {
  timestamp: number;
  userText: string;
  botText: string;
  latency: number;
  state: BookingState;
}
```

### FIX-3: Barge-in Handling

**File:** `voice-agent/src/audio_handler.py`

```python
# Interruzione durante TTS
# Se utente parla durante risposta bot, stop TTS e ascolta
```

---

## 📝 NOTE TECNICHE

### Comandi Utili

```bash
# Verifica Voice Agent su iMac
ssh imac "lsof -i :3002 | grep LISTEN"

# Reset conversazione
ssh imac "curl -X POST http://localhost:3002/api/reset"

# Log in tempo reale
ssh imac "tail -f /tmp/voice-agent.log"

# Verifica DB
ssh imac "sqlite3 '/Volumes/MacSSD - Dati/fluxion/fluxion.db' 'SELECT COUNT(*) FROM clienti;'"
```

### Files Critici

| File | Descrizione | Ultima Modifica |
|------|-------------|-----------------|
| `voice-agent/src/booking_state_machine.py` | Core FSM | db8decd |
| `voice-agent/src/disambiguation_handler.py` | Disambiguazione | db8decd |
| `src-tauri/src/http_bridge.rs` | Bridge Rust/Python | - |

---

## 🆘 EMERGENZE

### Se Voice Agent non risponde:

```bash
ssh imac "pkill -f 'python.*voice-agent'; sleep 2; 
    cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && 
    source venv/bin/activate && 
    python -m src.main --port 3002 &"
```

### Se build fallisce:

```bash
# Su iMac
cd '/Volumes/MacSSD - Dati/fluxion'
rm -rf src-tauri/target
npm run tauri build
```

---

## ✅ DEFINIZIONE DI "FATTO"

**Build v0.8.1 è pronta quando:**

- [ ] 5 scenari test live passano
- [ ] TypeScript 0 errori
- [ ] Rust 0 errori
- [ ] Build macOS completata
- [ ] Smoke test finale OK

**Success Criteria:**
- Latenza media < 2 secondi
- Disambiguazione funziona in < 3 turni
- Zero crash durante i test

---

## 🤖 ISTRUZIONI PER AI (Prossima Sessione)

1. **Leggi questo file all'avvio** - Contiene stato completo progetto
2. **Verifica CoVe prima di ogni azione** - Type-check + cargo check
3. **Test-driven development** - Scrivere test prima del fix
4. **Git workflow** - Commit atomici, push frequente
5. **Documentazione** - Aggiornare questo file dopo ogni modifica

**Prompt iniziale prossima sessione:**
```
"Leggi PROMPT-RIPARTENZA-2026-02-11.md e procedi con 
FASE 1: Verifica Pre-Build"
```

---

*Ultimo aggiornamento: 2026-02-10*  
*Versione prompt: 1.0*  
*CoVe Validation: PENDING*
