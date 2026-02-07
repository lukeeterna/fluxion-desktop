# PROMPT RIPARTENZA - Test Live Voice Agent v0.8.1

> **Data**: 2026-02-08 (Oggi)  
> **Obiettivo**: Completare Test Live Voice Agent "Sara" + Build Finale  
> **Stato**: Codice pronto, ambiente configurato, attesa test vocali

---

## 🎯 MISSIONE OGGI

Completare i **5 scenari test live vocali** con Sara sul Voice Agent, verificare i risultati e procedere con il **build di produzione v0.8.1**.

---

## 🧪 SCENARI TEST LIVE DA COMPLETARE

### Preparazione Database (già fatto su iMac)
```sql
-- Clienti test presenti su iMac:
test-gigio | Gigio Peruzzi | +39 333 123 4567 | 15/03/1985
test-maria | Maria Bianchi | +39 333 999 8877 | 22/07/1990
```

### SCENARIO 1: "Gino vs Gigio" 🎭
**Obiettivo**: Verificare disambiguazione fonetica

**Setup:** In database c'è "Gigio Peruzzi"

| # | Input Vocale | Attesa |
|---|--------------|--------|
| 1 | *"Sono Gino Peruzzi"* | Sara chiede: *"Forse intendeva 'Gigio'? Mi conferma la data di nascita?"* |
| 2 | *"Sì, sono nato il 15 marzo 1985"* | Match confermato → *"Bentornato Gigio!"* |

**✅ PASS**: Sara chiede conferma per similarità fonetica

---

### SCENARIO 2: "La Chiacchierona" 💬
**Obiettivo**: Verificare chiusura graceful + rimanere in linea

| # | Input Vocale | Attesa |
|---|--------------|--------|
| 1 | *"Vorrei prenotare un taglio"* | Sara chiede data/ora |
| 2 | *"Domani alle 15"* | Proposta conferma |
| 3 | *"Sì confermo"* | Sara chiede: *"Terminiamo la comunicazione...?"* |
| 4 | **NO** *"No aspetta, mi serve anche la piega"* | Sara: *"Va bene, rimaniamo in linea..."* |

**✅ PASS**: Sara rimane in linea e continua

---

### SCENARIO 3: "Flusso Perfetto" 📞
**Obiettivo**: Verificare intero flusso booking → WhatsApp → chiusura

| # | Input Vocale | Attesa |
|---|--------------|--------|
| 1 | *"Sono Marco Rossi, è la prima volta"* | Sara chiede telefono |
| 2 | *"+39 333 123 9999"* | Salvato |
| 3 | *"Vorrei un taglio domani alle 16"* | Proposta conferma |
| 4 | *"Sì, va bene"* | Sara chiede chiusura |
| 5 | *"Sì, grazie"* | Chiamata chiusa |

**Verifica post-test:**
```bash
# Su iMac:
sqlite3 fluxion.db "SELECT nome, cognome FROM clienti WHERE nome='Marco' AND cognome='Rossi';"
sqlite3 fluxion.db "SELECT c.nome, c.cognome, a.data, a.ora FROM appuntamenti a JOIN clienti c ON a.cliente_id = c.id WHERE c.cognome='Rossi';"
```

**✅ PASS**: Cliente + appuntamento creati, WhatsApp inviato

---

### SCENARIO 4: "STT Confuso - Generi" 🔀
**Obiettivo**: Verificare disambiguazione errori STT su genere

**Setup:** In database c'è "Maria Bianchi"

| # | Input Vocale | Attesa |
|---|--------------|--------|
| 1 | *"Sono Mario Bianchi"* | Sara chiede conferma, NON dice "bentornato" subito |

**✅ PASS**: Sara chiede conferma data di nascita

---

### SCENARIO 5: "Rifiuto Elegante" 🙅‍♂️
**Obiettivo**: Verificare rifiuto booking in CONFIRMING

| # | Input Vocale | Attesa |
|---|--------------|--------|
| 1 | *"Vorrei prenotare oggi alle 15"* | Riepilogo proposto |
| 2 | *"No, ho cambiato idea"* | Booking annullato |
| 3 | - | Sara: *"Posso aiutarla in altro modo?"* |

**✅ PASS**: Booking annullato + offerta aiuto alternativo

---

## 🚀 PROCEDURA AVVIO TEST

### Step 1: Avvio Fluxion su iMac (fisicamente)
```bash
# SULL'IMAC (non via SSH):
cd "/Volumes/MacSSD - Dati/fluxion"
export PATH="/usr/local/bin:$HOME/.cargo/bin:$PATH"
npm run tauri dev
```

### Step 2: Accesso Voice Agent
1. Attendi che Fluxion si avvii
2. Completa Setup Wizard se richiesto
3. Vai alla sezione "Voice Agent" o avvia test
4. **Inizia la chiamata con Sara**

### Step 3: Esecuzione Test
Per ogni scenario:
1. **Tu parli** con Sara (input vocale)
2. **Io verifico** i log via SSH
3. **Segno** il risultato (PASS/FAIL)
4. **Reset** stato per scenario successivo

---

## ✅ CHECKLIST TEST

- [ ] SCENARIO 1: Gino vs Gigio - Disambiguazione OK
- [ ] SCENARIO 2: Chiacchierona - Chiusura graceful OK  
- [ ] SCENARIO 3: Flusso Perfetto - WhatsApp inviato OK
- [ ] SCENARIO 4: STT Confuso - Mario/Maria OK
- [ ] SCENARIO 5: Rifiuto Elegante - Annullamento OK

**Se TUTTI passano:**
- [ ] Build v0.8.1
- [ ] Tag release
- [ ] Deploy

---

## 🔧 COMANDI UTILI

### Verifica stato Voice Agent (SSH)
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python3 -c 'from src.booking_state_machine import BookingStateMachine; print(\"OK\")'"
```

### Verifica database (SSH)
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && sqlite3 fluxion.db 'SELECT nome, cognome FROM clienti ORDER BY created_at DESC LIMIT 5;'"
```

### Verifica appuntamenti (SSH)
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && sqlite3 fluxion.db 'SELECT c.nome, c.cognome, a.data, a.ora FROM appuntamenti a JOIN clienti c ON a.cliente_id = c.id ORDER BY a.created_at DESC LIMIT 5;'"
```

---

## 📋 STATO IMPLEMENTAZIONI

| Feature | Stato | Note |
|---------|-------|------|
| WhatsApp post-booking | ✅ | Implementato e testato |
| Chiusura graceful | ✅ | Stato ASKING_CLOSE_CONFIRMATION attivo |
| Disambiguazione nomi | ✅ | Phonetic matching implementato |
| Voice Agent greeting | ✅ | API get_voice_agent_config pronta |
| Installazione remota | ✅ | Script remote-install.sh creato |
| Assistenza remota | ✅ | Comandi remote_assist.rs implementati |

---

## 🆘 TROUBLESHOOTING

### Se Voice Agent non risponde:
1. Verifica porta 3002: `lsof -i :3002`
2. Riavvia Voice Agent: `pkill -f "python3 main.py"`
3. Verifica log: `cat /tmp/voice-agent.log`

### Se Sara non riconosce nomi:
1. Verifica database: `SELECT * FROM clienti`
2. Controlla similarità: Verifica che Gino/Gigio siano >70%

### Se WhatsApp non invia:
1. Verifica numero telefono salvato
2. Controlla log: `grep -i "whatsapp" voice-agent/logs/*.log`

---

## 🎲 CRITERI SUCCESSO BUILD

Test considerati **SUPERATI** se:
- ✅ 5/5 scenari passano senza errori critici
- ✅ WhatsApp inviato (Scenario 3)
- ✅ Disambiguazione funziona (Scenari 1, 4)
- ✅ Chiusura graceful funziona (Scenario 2)
- ✅ Rifiuto gestito correttamente (Scenario 5)

**Se tutti passano → BUILD v0.8.1 e RELEASE** 🚀

---

## 📁 FILE CHIAVE

| File | Descrizione |
|------|-------------|
| `PROMPT-RIPARTENZA-2026-02-08-TEST-LIVE.md` | Questo file |
| `scripts/remote-install.sh` | Installazione remota |
| `src-tauri/src/commands/remote_assist.rs` | Assistenza remota |
| `voice-agent/src/booking_state_machine.py` | State machine |
| `voice-agent/src/disambiguation_handler.py` | Disambiguazione |

---

*Buona fortuna con i test live! 🎲*
*Ricorda: registra l'esito di ogni scenario per il report finale*
