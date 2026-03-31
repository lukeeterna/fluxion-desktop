# FLUXION — Handoff Sessione 128 → 129 (2026-03-31)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 128 — 4 COMMIT

### 1. Sprint 2: Screenshot Perfetti (PARZIALE)
- **22 screenshot totali** in `landing/screenshots/`
- 9 pagine principali catturate FRESCHE con dati demo reali:
  - 01-dashboard: 5.639 fatturato, 34 apt oggi, 152 clienti, NO warning banner
  - 02-calendario: Marzo 2026 pieno di appuntamenti
  - 03-clienti: 152 clienti con fedelta/VIP (Giulia 30/10, Valeria 14/10)
  - 04-servizi, 05-operatori, 06-fatture (65 fatture, 6.312)
  - 07-cassa: 310 giornata (ha Invalid Date nel campo Ora)
  - 08-voice: Sara Voice Agent (stato inattivo)
  - 09-fornitori
- 2 pagine restaurate da sessioni precedenti:
  - 10-analytics: mostra layout ma con 0.00 fatturato (dati vecchi)
  - 11-impostazioni: pagina Email configurazione
- 2 pagine marketing restaurate:
  - 22-pacchetti: 3 pacchetti (Festa Papa, Natale, Estate)
  - 23-fedelta: Anna Ferrari 8/10 visite, badge VIP
- 9 schede verticali restaurate da S126

### 2. Bug fix: Cassa Invalid Date
- Root cause: new Date con spazio invece di T separator
- Fix in src/pages/Cassa.tsx:280 - aggiunto .replace(' ', 'T')
- Non verificato su iMac (app crashata)

### 3. Bug fix: DiagnosticsPanel crash guard
- Root cause: backup.path con backup potenzialmente undefined
- Fix in src/components/impostazioni/DiagnosticsPanel.tsx:327
- Non verificato (stessa ragione)

### 4. Screenshot capture script
- scripts/capture-screenshots-remote.py
- Approccio: CGEvent sidebar click + Swift CGWindowListCreateImage
- Prerequisito: display iMac sveglio (caffeinate -d -t 600)

---

## STATO GIT
```
Branch: master | HEAD: 4329707
Commits S128:
  79eb324 fix(S128): Cassa Invalid Date + Impostazioni crash guard
  bd35ac9 feat(S128): capture 13 fresh screenshots with demo data
  4329707 fix(S128): restore schede screenshots + clean up agent duplicates
```

---

## BUG CRITICO: F.path.split su iMac

### Sintomi
- Errore undefined is not an object (evaluating F.path.split) su TUTTE le pagine
- App era funzionante nella prima parte della sessione (screenshots 01-09 OK)
- Si e' rotto dopo navigazione su Impostazioni + cancellazione Vite cache

### Come risolvere
1. Dall'iMac fisicamente: aprire app, se errore -> Cmd+R per ricaricare
2. Se non funziona: cd /Volumes/MacSSD\ -\ Dati/fluxion && rm -rf node_modules && npm install && npm run tauri dev
3. Alternativa: npm run build per rigenerare dist/ con codice corretto
4. Il dist/ e' stato restaurato (era stato rinominato durante debug)

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       DONE (S123-S126)
Phase 10e: Sara Bug Fixes       DONE FAQ vars + intent routing (S127)
Sprint 1:  Product Ready        DONE Prezzi + Phone-home + Demo seed (S127)
Sprint 2:  Screenshot Perfetti  IN PROGRESS - 22 catturati, 3 da ricatturare
Sprint 3:  Video che Spacca     NEXT
Sprint 4:  Landing Definitiva   PENDING
Sprint 5:  Sales Agent WA       PENDING
```

---

## PROSSIMA SESSIONE 129

### A. Fix iMac app crash (BLOCKER)
- npm install + npm run tauri dev su iMac (full reinstall)
- Verificare Cassa mostra orari (non Invalid Date)
- Verificare Impostazioni funziona senza crash

### B. Re-catturare screenshot mancanti
- 07-cassa: dopo fix Invalid Date
- 10-analytics: con dati demo aggiornati
- 11-impostazioni: se funziona
- 22-pacchetti e 23-fedelta: dalla pagina Impostazioni

### C. Sprint 3: Video V6
- Con screenshot aggiornati, procedere al video
- Aggiungere sezioni Pacchetti + Fedelta
- Edge-TTS voiceover aggiornato

---

## NOTE TECNICHE

### Sidebar positions (window 1158: X=360, Y=72, W=1200, H=800)
```
SIDEBAR_X = 440
Dashboard:    Y=200
Calendario:   Y=244
Clienti:      Y=288
Servizi:      Y=332
Operatori:    Y=376
Fatture:      Y=420
Cassa:        Y=464
Fornitori:    Y=508
Voice Agent:  Y=552
Impostazioni: Y=596
```
NO Analytics in sidebar (10 items, not 11).

### Pipeline riavvio
```bash
ssh imac "kill $(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && DYLD_LIBRARY_PATH=lib/pjsua2 PYTHONUNBUFFERED=1 nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 129.
PRIORITA:
1. Fix iMac app crash (F.path.split -- npm install + rebuild)
2. Re-catturare 07-cassa, 10-analytics, 11-impostazioni
3. Sprint 3: Video V6 con nuovi screenshot
```
