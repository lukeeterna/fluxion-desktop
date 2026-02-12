# PROMPT RIPARTENZA - FLUXION Voice Agent Fix & Test Live

**Data**: 2026-02-12  
**Priorità**: CRITICA 🔴  
**Obiettivo**: Fixare Voice Agent timeout + Test Live CoVe su iMac

---

## 🚨 PROBLEMA CRITICO: Voice Agent Timeout

### Sintomo
```
operation timed out
error ending request for URL http://127.0.0.1:3002/api/voice/process
```

### Root Cause (NON ANCORA RISOLTO)
Il Voice Agent sull'iMac ascolta su **127.0.0.1** (localhost) invece che su **0.0.0.0** (tutte le interfacce).

**Verifica:**
```bash
ssh imac "lsof -i :3002"
# Dovrebbe mostrare: TCP *:3002 (LISTEN) 
# Invece mostra: TCP localhost:3002 (LISTEN)
```

### Fix Richiesto
1. Modificare `voice-agent/main.py` riga 105:
   ```python
   # DA:
   host: str = "127.0.0.1"
   # A:
   host: str = "0.0.0.0"
   ```

2. Riavviare Voice Agent sull'iMac

3. Verificare con test cross-machine:
   ```bash
   # Da MacBook:
   curl http://192.168.1.7:3002/health
   ```

---

## ✅ IMPLEMENTAZIONI CoVe COMPLETATE (da testare)

### 1. FluxionLatencyOptimizer
**File**: `voice-agent/src/latency_optimizer.py` (18,822 bytes)
- Streaming LLM tokens to TTS
- Connection pooling con keep-alive
- Model selection dinamico (mixtral/llama)

### 2. FluxionTurnTracker  
**File**: `voice-agent/src/turn_tracker.py` (23,518 bytes)
- Turn-level observability
- SQLite backend
- Latency breakdown per componente

### 3. Streaming LLM
**File**: `voice-agent/src/groq_client.py` (modificato)
- `generate_response_streaming()` - async generator
- Chunking su punteggiatura
- Parallel TTS-ready

### 4. Test Suite Completa
**File**: `voice-agent/tests/test_voice_agent_complete.py` (24,618 bytes)
- 12 classi di test
- 40+ test totali
- Coverage: intent, entity, state machine, performance

### 5. Smoke Tests
**File**: `voice-agent/scripts/smoke_test.py` (10,867 bytes)
- 14 test rapidi
- Test cross-machine

### 6. Test Cross-Machine
**File**: `voice-agent/scripts/test_cross_machine.py` (2,452 bytes)
- Verifica reale MacBook → iMac

---

## 🧪 TEST LIVE DA ESEGUIRE (CoVe Verified)

### Pre-requisiti
- [ ] Voice Agent ascolta su 0.0.0.0:3002 (NON 127.0.0.1)
- [ ] IP statico 192.168.1.7 configurato su router
- [ ] Test cross-machine: `python voice-agent/scripts/test_cross_machine.py`

### Test Scenari

#### 1. Disambiguazione Fonetica (Gino vs Gigio)
**Input**: "Sono Gino Peruzzi" (DB ha "Gigio Peruzzi")  
**Atteso**: "Mi scusi, ha detto Gino o Gigio?"

#### 2. Soprannome VIP (Gigi → Gigio)
**Input**: "Sono Gigi Peruzzi"  
**Atteso**: "Ciao Gigi! Bentornato Gigio!"

#### 3. Chiusura Graceful
**Input**: "Confermo chiusura"  
**Atteso**: WhatsApp inviato + "Grazie, arrivederci!"

#### 4. Flusso Perfetto
**Input**: Nuovo cliente completo  
**Atteso**: Registrazione + booking + WhatsApp + chiusura

#### 5. WAITLIST
**Input**: "Vorrei domani alle 15" (slot occupato) → "Mettetemi in lista"  
**Atteso**: Salvataggio waitlist + conferma WhatsApp

---

## 📁 FILE DA VERIFICARE

```
voice-agent/main.py                           ← MODIFICARE host: "0.0.0.0"
voice-agent/src/latency_optimizer.py          ← Verificare import
voice-agent/src/turn_tracker.py               ← Verificare DB init
voice-agent/src/groq_client.py                ← Verificare streaming
voice-agent/tests/test_voice_agent_complete.py ← Verificare pytest
voice-agent/scripts/smoke_test.py             ← Verificare esecuzione
voice-agent/scripts/test_cross_machine.py     ← Verificare cross-machine
NETWORK-CONFIG.md                             ← Documentazione IP
```

---

## 🔧 COMANDI RAPIDI

### Fix Voice Agent Host
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && sed -i '' 's/host: str = \"127.0.0.1\"/host: str = \"0.0.0.0\"/g' main.py && grep 'host: str' main.py"
```

### Riavvio Voice Agent
```bash
ssh imac "pkill -f 'python.*main.py'; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && export GROQ_API_KEY=... && python3 main.py --port 3002 &"
```

### Test Cross-Machine
```bash
# Da MacBook:
python3 voice-agent/scripts/test_cross_machine.py

# O curl:
curl http://192.168.1.7:3002/health
curl -X POST http://192.168.1.7:3002/api/voice/process -d '{"text":"Ciao"}'
```

### Test Suite
```bash
# Su iMac:
cd /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent
python3 scripts/smoke_test.py
python3 -m pytest tests/test_voice_agent_complete.py -v
```

---

## 📝 CONFIGURAZIONE NETWORK

### IP Statici (da configurare su router)
| Dispositivo | IP | Porta |
|-------------|----|-------|
| iMac (Voice Agent) | 192.168.1.7 | 3002 |
| iMac (Tauri Bridge) | 192.168.1.7 | 3001 |

### URL Corretti
```
Voice Agent API: http://192.168.1.7:3002/api/voice/process
HTTP Bridge:     http://192.168.1.7:3001
Health:          http://192.168.1.7:3002/health
```

---

## ⚠️ ERRORI PRECEDENTI (da evitare)

1. **Test falsi positivi**: I test smoke giravano in localhost sull'iMac, non verificavano reale connettività MacBook→iMac

2. **Host 127.0.0.1**: Il server ascoltava solo su localhost, inaccessibile dalla rete

3. **Mancanza IP statico**: L'IP 192.168.1.7 non era garantito dal router

---

## 🎯 CRITERI DI SUCCESSO

- [ ] `curl http://192.168.1.7:3002/health` da MacBook funziona
- [ ] `test_cross_machine.py` passa
- [ ] Scenari test live 1-5 completati con successo
- [ ] Latency < 2s per risposta
- [ ] Nessun timeout

---

## 🔄 WORKFLOW CoVe

1. **Verifica**: `lsof -i :3002` deve mostrare `*:3002` non `localhost:3002`
2. **Fix**: Modificare main.py host → "0.0.0.0"
3. **Test**: Eseguire test_cross_machine.py
4. **Push**: Commit e push su GitHub
5. **Sync**: Pull su iMac
6. **Live Test**: Eseguire 5 scenari test

---

*Prompt generato: 2026-02-12*  
*Stato: CRITICO - Voice Agent non accessibile da rete*  
*Prossimo step: Fix host + Test live*
