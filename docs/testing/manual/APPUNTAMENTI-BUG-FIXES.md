# TEST MANUALI GUIDATI - Bug Fix Appuntamenti

**Data creazione**: 2026-01-02
**Ambiente**: macOS Monterey (iMac)
**Obiettivo**: Verificare fix per 3 bug critici appuntamenti

---

## 🔴 BUG #1: Date Shift (+1 giorno)

### Descrizione Bug
Gli appuntamenti vengono salvati con data **+1 giorno** rispetto alla data selezionata.

### Riproduzione
1. Aprire Calendario
2. Click "Nuovo Appuntamento"
3. Selezionare data: **02/01/2026** ore **10:00**
4. Compilare cliente, servizio, operatore
5. Click "Crea Appuntamento"
6. Verificare nel calendario

### Risultato Atteso
✅ Appuntamento appare il **02/01/2026** (giovedì)

### Risultato Errato (PRIMA DEL FIX)
❌ Appuntamento appare il **03/01/2026** (venerdì)

### Test di Verifica Post-Fix
- [ ] Test 1: Creare appuntamento 02/01/2026 → verifica appare 02/01
- [ ] Test 2: Creare appuntamento 15/01/2026 → verifica appare 15/01
- [ ] Test 3: Creare appuntamento ultimo giorno mese (31/01) → verifica appare 31/01
- [ ] Test 4: Modificare appuntamento da 02/01 a 05/01 → verifica appare 05/01

---

## 🔴 BUG #2: Eliminazione Non Funziona

### Descrizione Bug
Impossibile eliminare appuntamenti dall'interfaccia.

### Riproduzione
1. Aprire Calendario
2. Click su un appuntamento esistente
3. Cercare pulsante "Elimina" o opzione eliminazione
4. Provare a eliminare

### Risultato Atteso
✅ Appuntamento viene eliminato e NON appare più nel calendario

### Risultato Errato (PRIMA DEL FIX)
❌ Nessun pulsante "Elimina" visibile, oppure elimina non funziona

### Test di Verifica Post-Fix
- [ ] Test 1: Creare appuntamento → eliminarlo → verificare sparisce
- [ ] Test 2: Eliminare appuntamento passato → verificare sparisce
- [ ] Test 3: Eliminare appuntamento futuro → verificare sparisce
- [ ] Test 4: Provare a eliminare e annullare → verificare rimane
- [ ] Test 5: Soft delete funziona (deleted_at non NULL in DB)

---

## 🔴 BUG #3: Vista Giorno Incompleta

### Descrizione Bug
Non è possibile visualizzare TUTTI gli appuntamenti di un giorno specifico.

### Riproduzione
1. Creare 5+ appuntamenti nello stesso giorno (es. 10/01/2026)
2. Click sul giorno nel calendario
3. Verificare quanti appuntamenti vengono mostrati

### Risultato Atteso
✅ Vengono mostrati TUTTI i 5+ appuntamenti creati

### Risultato Errato (PRIMA DEL FIX)
❌ Vengono mostrati solo alcuni appuntamenti (es. primi 3)

### Test di Verifica Post-Fix
- [ ] Test 1: Creare 5 appuntamenti stesso giorno → verificare tutti visibili
- [ ] Test 2: Creare 10 appuntamenti stesso giorno → verificare tutti visibili
- [ ] Test 3: Click "+N altri" (se presente) → verificare mostra tutti
- [ ] Test 4: Scroll funziona se lista lunga
- [ ] Test 5: Tutti appuntamenti clickabili per edit

---

## Checklist Generale Regressione

### Funzionalità Base (NON DEVONO ROMPERSI)
- [ ] Creazione appuntamento funziona
- [ ] Modifica appuntamento funziona
- [ ] Conflict detection funziona (stesso operatore, stessa ora)
- [ ] Auto-fill prezzo/durata da servizio funziona
- [ ] Filtro per operatore funziona
- [ ] Navigazione mesi funziona
- [ ] Vista calendario responsive

---

## Annotazioni Tester

**Data test**: ___________
**Tester**: ___________
**Build version**: ___________

**Note aggiuntive**:
___________________________________________________________
___________________________________________________________
___________________________________________________________

