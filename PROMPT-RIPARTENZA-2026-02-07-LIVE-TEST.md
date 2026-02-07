# PROMPT RIPARTENZA - Test Live Voice Agent v0.8.1

> **Data**: 2026-02-07 (Domani)  
> **Obiettivo**: Test Live Voice Agent "Sara" su iMac  
> **Stato**: Fix implementati, codice su iMac, pronti per test

---

## 🎯 MISSIONE OGGI

Testare in **LIVE** il Voice Agent "Sara" con scenari realistici per verificare i fix implementati ieri.

### Fix da Verificare:
1. ✅ **WhatsApp inviato dopo booking** - `_send_wa_booking_confirmation()`
2. ✅ **Chiusura graceful con conferma** - Stato `ASKING_CLOSE_CONFIRMATION`
3. ✅ **Disambiguazione nomi** - Phonetic matching (Gino/Gigio)

---

## 🖥️ AMBIENTE TEST

### MacBook (Dev)
- Path: `/Volumes/MontereyT7/FLUXION`
- Uso: Modifiche code, documentazione

### iMac (Test Live)
- IP: `192.168.1.7`
- Path: `/Volumes/MacSSD - Dati/fluxion`
- Codice: Già aggiornato (pull di ieri sera)
- Database: `fluxion.db` (con dati test)

---

## 🧪 SCENARI TEST LIVE

### SCENARIO 1: "Gino vs Gigio" 🎭
**Obiettivo**: Verificare disambiguazione fonetica

**Setup iMac:**
```sql
-- Inserisci cliente esistente "Gigio Peruzzi"
INSERT INTO clienti (id, nome, cognome, telefono, created_at) 
VALUES ('test-gigio', 'Gigio', 'Peruzzi', '+393331234567', datetime('now'));
```

**Test:**
1. Avvia Voice Agent su iMac
2. Simula chiamata: "Sono Gino Peruzzi" (STT lo capta male)
3. **Verifica**: Sara deve chiedere "Forse intendeva 'Gigio'? Mi conferma la data di nascita?"
4. Se risponde data corretta → match corretto
5. Se risponde "no, sono Gino" → registra nuovo cliente

**Comandi:**
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python3 -m src.main"
```

---

### SCENARIO 2: "La Chiacchierona Post-Booking" 💬
**Obiettivo**: Verificare chiusura graceful + rimanere in linea

**Setup:**
- Cliente esistente: Maria Bianchi (con telefono)

**Test:**
1. "Vorrei prenotare un taglio"
2. "Per lunedì alle 15"
3. "Sì confermo"
4. **Verifica**: Sara chiede "Terminiamo la comunicazione e le inviamo la conferma via WhatsApp?"
5. Rispondi: "No aspetta, mi serve anche la piega"
6. **Verifica**: Sara risponde "Va bene, rimaniamo in linea. Posso aiutarla con altro?"
7. Continua con nuovo booking piega
8. Alla fine conferma chiusura
9. **Verifica**: WhatsApp inviato con entrambi gli appuntamenti

---

### SCENARIO 3: "Flusso Perfetto Completo" 📞
**Obiettivo**: Verificare intero flusso booking → WhatsApp → chiusura

**Test:**
1. Nuovo cliente: "Sono Marco Rossi, è la prima volta"
2. Fornisci telefono: "+393331234567"
3. Scegli servizio, data, ora
4. Conferma: "Sì"
5. Alla domanda chiusura: "Sì, va bene"
6. **Verifica finale**:
   - Chiamata chiusa
   - Cliente "Marco Rossi" creato in DB
   - Appuntamento creato
   - WhatsApp inviato a +393331234567

---

### SCENARIO 4: "STT Confuso - Generi" 🔀
**Obiettivo**: Verificare disambiguazione errori STT su genere

**Setup:**
```sql
INSERT INTO clienti (id, nome, cognome, telefono) 
VALUES ('test-maria', 'Maria', 'Bianchi', '+393339998877');
```

**Test:**
1. "Sono Mario Bianchi" (STT sbaglia genere)
2. **Verifica**: Sara deve chiedere conferma, non dare "bentornato"
3. Se data di nascita matcha con Maria → "Ah, quindi è Maria!"
4. Se non matcha → "Nuovo cliente Mario Bianchi"

---

### SCENARIO 5: "Rifiuto Elegante" 🙅‍♂️
**Obiettivo**: Verificare rifiuto booking in CONFIRMING

**Test:**
1. Proponi booking completo
2. Utente: "No, ho cambiato idea"
3. **Verifica**: Booking annullato, sessione continua
4. Chiede: "Posso aiutarla con altro?"

---

## 🔧 COMANDI UTILi

### Su iMac (via SSH):

```bash
# Entra su iMac
ssh imac

# Vai al progetto
cd '/Volumes/MacSSD - Dati/fluxion'

# Test Voice Agent Python
python3 -c "
from voice-agent.src.booking_state_machine import BookingStateMachine
sm = BookingStateMachine()
print('✅ Voice Agent carica correttamente')
"

# Controlla database
cd '/Volumes/MacSSD - Dati/fluxion'
sqlite3 fluxion.db "SELECT nome, cognome, telefono FROM clienti WHERE cognome='Peruzzi';"

# Restart Voice Agent (se necessario)
pkill -f "voice-agent"
cd voice-agent && python3 -m src.main
```

### Su MacBook:

```bash
# Sync codice
cd /Volumes/MontereyT7/FLUXION
git pull origin master

# Test rapido
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent/src' && python3 -c 'from booking_state_machine import BookingStateMachine; print(\"OK\")'"
```

---

## 📋 CHECKLIST TEST LIVE

### Pre-Test:
- [ ] iMac acceso e accessibile via SSH
- [ ] Codice aggiornato su iMac (git pull già fatto)
- [ ] Database pronto con dati test
- [ ] Voice Agent si avvia senza errori

### Durante Test:
- [ ] SCENARIO 1: Gino vs Gigio - OK
- [ ] SCENARIO 2: Chiacchierona - OK
- [ ] SCENARIO 3: Flusso Perfetto - OK
- [ ] SCENARIO 4: STT Confuso - OK
- [ ] SCENARIO 5: Rifiuto Elegante - OK

### Post-Test:
- [ ] Verifica WhatsApp inviati (controlla log)
- [ ] Verifica clienti creati in DB
- [ ] Verifica appuntamenti creati
- [ ] Se tutto OK → Build v0.8.1

---

## 🐛 TROUBLESHOOTING

### Se Voice Agent non parte:
```bash
# Check dipendenze Python
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && pip3 install -r requirements.txt"
```

### Se test falliscono:
1. Controlla log errori: `tail -f voice-agent/logs/error.log`
2. Verifica stato DB: `sqlite3 fluxion.db ".tables"`
3. Riavvia Voice Agent: `pkill -f voice-agent && python3 -m src.main`

### Se WhatsApp non invia:
1. Verifica numero telefono cliente salvato
2. Controlla log: `grep -i "whatsapp" voice-agent/logs/*.log`
3. Verifica `whatsapp.py` configurato correttamente

---

## 🎯 CRITERI SUCCESSO

Test considerati **SUPERATI** se:
- ✅ Tutti e 5 gli scenari passano senza errori
- ✅ WhatsApp inviato correttamente dopo ogni booking
- ✅ Disambiguazione nomi funziona (chiede conferma per simili)
- ✅ Chiusura graceful funziona (chiede conferma, gestisce "no")
- ✅ Nessun crash o errore critico

Se tutti i criteri passano → **Build Produzione v0.8.1** 🚀

---

## 📁 FILE MODIFICATI (da ieri)

```
voice-agent/src/orchestrator.py          +20 righe (WhatsApp + phone)
voice-agent/src/booking_state_machine.py   +91 righe (ASKING_CLOSE_CONFIRMATION)
voice-agent/src/disambiguation_handler.py  +144 righe (Phonetic matching)
```

---

*Buona fortuna per i test live! 🎲*
*Ricorda: il CTO vuole un'esperienza gradevole, non solo test passati*
