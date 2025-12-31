# 🧪 TEST FASE 2 - CRM Clienti

**Data**: 2025-12-30
**Ambiente**: iMac macOS Monterey (senza Claude Code)

---

## ✅ Pre-requisiti Setup

- [x] Componenti shadcn installati (form, alert-dialog)
- [x] TypeScript compila senza errori
- [x] TanStack Query configurato
- [x] Rust commands registrati

---

## 📋 Piano Test CRUD

### 1. Avvio Applicazione

```bash
cd /Volumes/MontereyT7/FLUXION
npm run tauri dev
```

**Verifica**:
- [ ] App si avvia senza crash
- [ ] Database inizializzato (vedi console: "✅ Database initialized")
- [ ] Migrations eseguite (vedi console: "✅ Migrations completed")
- [ ] Sidebar visibile
- [ ] Navigazione a "Clienti" funziona

---

### 2. Test CREATE Cliente

**Click**: Bottone "Nuovo Cliente" (in alto a destra)

**Compilare form**:
```
Nome: Mario
Cognome: Rossi
Telefono: +39 333 1234567
Email: mario.rossi@example.com
Data Nascita: 1985-03-15
Indirizzo: Via Roma 123
CAP: 20100
Città: Milano
Provincia: MI
Consenso marketing: ✓
Consenso WhatsApp: ✓
```

**Click**: "Crea Cliente"

**Verifica**:
- [ ] Dialog si chiude
- [ ] Cliente appare nella tabella
- [ ] Nome completo: "Mario Rossi"
- [ ] Telefono formattato correttamente
- [ ] Email visibile
- [ ] Città: Milano
- [ ] Counter header: "1 cliente totale"

**Log atteso (console browser F12)**:
```
✅ Cliente creato con successo
```

**Log atteso (console Rust - terminal)**:
```
📁 Database path: /Users/.../fluxion.db
✅ Database initialized
✅ Migrations completed
```

---

### 3. Test READ Lista

**Verifica tabella**:
- [ ] Header colonne: Nome | Telefono | Email | Città | Azioni
- [ ] Riga cliente con dati corretti
- [ ] Icone Phone e Mail visibili
- [ ] Bottoni Edit (matita) e Delete (cestino) presenti

**Se lista vuota** (non dovrebbe):
- [ ] Messaggio: "Nessun cliente trovato"
- [ ] Sotto-testo: "Inizia aggiungendo il tuo primo cliente"

---

### 4. Test UPDATE Cliente

**Click**: Bottone Edit (matita) su "Mario Rossi"

**Modificare**:
```
Telefono: +39 333 9999999  (cambiare numero)
Email: mario.rossi.new@example.com
Note: Cliente VIP - Prenotazioni prioritarie
```

**Click**: "Aggiorna Cliente"

**Verifica**:
- [ ] Dialog si chiude
- [ ] Telefono aggiornato nella tabella
- [ ] Email aggiornata
- [ ] Note salvate (non visibili in tabella, ma salvate nel DB)

**Log browser**:
```
✅ Cliente aggiornato
```

---

### 5. Test DELETE Cliente (Soft Delete)

**Click**: Bottone Delete (cestino) su "Mario Rossi"

**Verifica Alert Dialog**:
- [ ] Titolo: "Elimina Cliente"
- [ ] Messaggio: "Sei sicuro di voler eliminare Mario Rossi?"
- [ ] Bottoni: "Annulla" + "Elimina" (rosso)

**Click**: "Elimina"

**Verifica**:
- [ ] Dialog si chiude
- [ ] Cliente SCOMPARE dalla tabella
- [ ] Counter header: "0 clienti totali"
- [ ] Messaggio empty state: "Nessun cliente trovato"

**Log browser**:
```
✅ Cliente eliminato
```

**Verifica Database** (opzionale - avanzato):
```bash
sqlite3 ~/Library/Application\ Support/com.tauri-app.tauri-app/fluxion.db \
  "SELECT nome, cognome, deleted_at FROM clienti;"
```
**Atteso**: Mario Rossi con `deleted_at` popolato (non NULL)

---

### 6. Test Validazione Form

**Click**: "Nuovo Cliente"

**Lasciare vuoti** i campi obbligatori

**Click**: "Crea Cliente"

**Verifica errori**:
- [ ] Nome: "Nome richiesto (min 2 caratteri)"
- [ ] Cognome: "Cognome richiesto (min 2 caratteri)"
- [ ] Telefono: "Telefono richiesto (min 10 cifre)"
- [ ] Form NON si invia
- [ ] Dialog rimane aperto

**Inserire email invalida**: `mario@invalid`

**Verifica**:
- [ ] Email: "Email non valida"

---

### 7. Test Stati Loading

**Durante creazione cliente**, osservare:
- [ ] Bottone cambia: "Crea Cliente" → "Salvataggio..."
- [ ] Bottone disabilitato durante submit
- [ ] Dopo successo: bottone torna normale

**Durante fetch lista**:
- [ ] Spinner cyan visibile al primo caricamento
- [ ] Spinner: `<Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />`

---

### 8. Test Error Handling

**Simulare errore** (opzionale - avanzato):
- Fermare app con Ctrl+C
- Riaviare app
- Database corrotto? → Messaggio errore rosso

**Verifica error state**:
- [ ] Background rosso (#ef4444 con opacity)
- [ ] Messaggio: "Errore nel caricamento dei clienti: ..."

---

## 📸 Screenshot da Catturare

1. **Lista vuota** (primo avvio)
2. **Form nuovo cliente** (compilato)
3. **Tabella con 1 cliente**
4. **Dialog edit** (form pre-popolato)
5. **Alert delete** (conferma eliminazione)
6. **Lista dopo delete** (empty state)

---

## 🐛 Bug da Segnalare

Se trovi problemi, annotare:

```
### Bug #X: [Titolo breve]

**Step per riprodurre**:
1. ...
2. ...

**Comportamento atteso**: ...

**Comportamento attuale**: ...

**Screenshot**: (se applicabile)

**Log console browser**:
```
[inserire log]
```

**Log console Rust**:
```
[inserire log]
```
```

---

## ✅ Checklist Finale

Al termine dei test:

- [ ] Tutti i 7 test passati
- [ ] Nessun crash applicazione
- [ ] Nessun errore TypeScript in console browser
- [ ] Nessun errore Rust in terminal
- [ ] Performance fluida (no lag)
- [ ] UI responsive (resize window funziona)
- [ ] Dark theme corretto (Navy/Cyan/Teal)

---

**Al termine**: Riporta risultati a Claude Code su MacBook Big Sur (copy/paste questo file con checkbox compilate + eventuali log errori)
