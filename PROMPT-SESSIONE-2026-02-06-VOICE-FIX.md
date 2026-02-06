# PROMPT SESSIONE - FIX VOICE AGENT v0.8.1

## 🎯 OBIETTIVO
Fixare anomalie riscontrate nei test live del Voice Agent "Sara"

## 🐛 ANOMALIE RISCONTRATE (Test Live 2026-02-06)

### 1. 🔴 WhatsApp NON arriva
**Problema:** Dopo conferma appuntamento, il messaggio WhatsApp non viene inviato

**Comportamento attuale:**
- Appuntamento creato ✅
- WhatsApp NON inviato ❌

**Comportamento atteso:**
- Appuntamento creato ✅
- WhatsApp inviato automaticamente ✅

**File da controllare:**
- `voice-agent/src/orchestrator.py` - funzione `_send_wa_booking_confirmation()`
- `voice-agent/src/whatsapp.py` - implementazione WhatsApp client
- `src-tauri/src/commands/whatsapp.rs` - integrazione Tauri

---

### 2. 🔴 Chiamata NON chiusa correttamente
**Problema:** La chiamata non viene chiusa quando l'utente decide di terminare

**Flow corretto da implementare:**
```
1. Voice: "Appuntamento confermato! Terminiamo la comunicazione e le inviamo la conferma via WhatsApp?"
2. Utente: "Sì" / "Va bene" / "OK"
3. Voice: "Perfetto! A presto da Salone Super Bellezza. Buona giornata!"
4. [INVIO WHATSAPP]
5. [CHIUSURA CHIAMATA]
```

**Comportamento attuale:**
- Chiamata rimane aperta
- Nessuna richiesta di conferma chiusura

**Comportamento atteso:**
- Chiedere conferma chiusura
- Inviare WhatsApp
- Chiudere chiamata gracefully

**File da modificare:**
- `voice-agent/src/booking_state_machine.py` - stato CONFIRMED → CLOSING
- `voice-agent/src/orchestrator.py` - gestione intent CONFERMA post-booking
- `voice-agent/src/main.py` - chiusura sessione HTTP

---

### 3. 🔴 Miss-match riconoscimento nome (CRITICO)
**Problema:** "Gino Peruzzi" (nuovo) interpretato come "Gigio Peruzzi" (esistente)

**Caso:**
- Utente dice: "Sono Gino Peruzzi" (nuovo cliente)
- Voice capta: "Gigio Peruzzi" (cliente esistente simile)
- Voice risponde: "Bentornato Gigio!" ❌
- Utente confuso: non è il suo nome

**Soluzioni possibili:**
1. **Chiedere conferma nome:** "Mi conferma che si chiama Gigio Peruzzi?"
2. **Phonetic matching:** Usare Soundex/Metaphone per nomi simili
3. **Nuovo cliente detection:** Se match ambiguo, chiedere "È la prima volta?"
4. **Correzione:** Permettere all'utente di correggere: "No, mi chiamo Gino"

**File da modificare:**
- `voice-agent/src/disambiguation_handler.py` - aggiungere controllo fonetico
- `voice-agent/src/booking_state_machine.py` - stato REGISTERING_SURNAME
- `voice-agent/src/nlu/italian_nlu.py` - phonetic similarity

---

## 📋 TASK DA COMPLETARE

### Priority 1 (Bloccanti)
- [ ] Fix invio WhatsApp post-booking
- [ ] Implementare flow chiusura chiamata con conferma
- [ ] Fix miss-match nomi (disambiguation)

### Priority 2 (Miglioramenti)
- [ ] Aggiungere "È la prima volta?" per nuovi clienti
- [ ] Implementare correzione nome durante registrazione
- [ ] Test E2E con nomi simili (Gino/Gigio, Mario/Marino)

---

## 🔧 ARCHITETTURA FLUSSO CORRETTO

```
BOOKING_COMPLETED
        ↓
"Appuntamento confermato per [servizio] 
 il [data] alle [ora]."
        ↓
"Terminiamo la comunicazione e le 
 inviamo la conferma via WhatsApp?"
        ↓
    ┌──────────┴──────────┐
    ↓                     ↓
CONFERMA (sì)          RIFIUTO (no)
    ↓                     ↓
"Perfetto! A presto"   "Come preferisce"
    ↓                     ↓
[INVIA WHATSAPP]    [RIMANI IN LINEA]
    ↓
[CHIUDI CHIAMATA]
    ↓
Sessione terminata
```

---

## 📁 FILE CHIAVE

```
voice-agent/
├── src/
│   ├── orchestrator.py          ← Logica invio WhatsApp
│   ├── booking_state_machine.py ← Stati booking + chiusura
│   ├── disambiguation_handler.py ← Fix match nomi
│   ├── session_manager.py       ← Gestione sessione/chiusura
│   ├── nlu/
│   │   └── italian_nlu.py       ← Phonetic matching
│   └── whatsapp.py              ← Invio messaggi
└── main.py                      ← HTTP server + chiusura

src-tauri/src/
└── commands/
    └── whatsapp.rs              ← API WhatsApp Tauri
```

---

## ✅ TEST DA EFFETTUARE

### Test 1: Flow completo booking + WhatsApp
1. "Vorrei prenotare un taglio"
2. Fornire nome: "Test Nome"
3. Selezionare data/ora
4. Confermare appuntamento
5. Verificare: Chiede chiusura? → Invia WhatsApp? → Chiude?

### Test 2: Nuovo cliente vs Esistente
1. "Sono Gino Peruzzi" (nuovo)
2. Verificare: NON dice "bentornato"
3. Chiede "È la prima volta?"
4. Registra correttamente

### Test 3: Nomi simili
1. Cliente esistente: "Gigio Peruzzi"
2. Nuovo cliente: "Gino Peruzzi"
3. Verificare disambiguazione corretta

---

## 📝 NOTE IMPLEMENTAZIONE

### WhatsApp Integration
```python
# In orchestrator.py dopo booking_created:
await self._send_wa_booking_confirmation(booking_data)
# -> Chiama Tauri API prepare_whatsapp_message
# -> Genera link wa.me
# -> Salva in coda messaggi
```

### Chiusura Chiamata
```python
# Nuovo stato in booking_state_machine:
ASKING_CLOSE_CONFIRMATION → 
    if CONFERMA: SEND_WHATSAPP + CLOSE_SESSION
    if RIFIUTO: CONTINUE_SESSION
```

### Phonetic Matching
```python
# In disambiguation_handler:
from fuzzywuzzy import fuzz
# Se fuzz.ratio(nome_input, nome_esistente) > 80:
#    Chiedi conferma
```

---

## 🚀 CRITERI DI SUCCESSO

- [ ] WhatsApp inviato correttamente dopo ogni booking
- [ ] Chiamata chiusa con flow "Terminiamo e inviamo WhatsApp?"
- [ ] Nomi simili gestiti con disambiguazione
- [ ] Test passati con clienti test (Maria, Giuseppe, Anna)

---

*Sessione successiva: Fix Voice Agent v0.8.1*
