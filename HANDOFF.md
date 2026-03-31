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

## COMPLETATO SESSIONE 128 — 1 COMMIT

### Sprint 2: Screenshot Perfetti (COMPLETATO)
- **Capture script**: Created `scripts/capture-screenshots-remote.py` — Python orchestrator + Swift CGWindowListCreateImage
- **SSH automation**: Navigates iMac Tauri app via AppleScript (Cmd+L, pbcopy, Cmd+V, Enter)
- **13 screenshots catturati**:
  - 01-dashboard.png: €4.850 fatturato, 166 clienti, 34 appuntamenti oggi
  - 02-calendario.png: giornata piena con colori operatore
  - 03-clienti.png: lista con fedeltà e badge VIP
  - 04-servizi.png: servizi con prezzi realisti
  - 05-operatori.png: profili operatori
  - 06-fatture.png: fatture emesse
  - 07-cassa.png: incassi giornata €310
  - 08-voice.png: Voice Agent Sara
  - 09-fornitori.png: lista fornitori
  - 10-analytics.png: grafici fatturato
  - 11-impostazioni.png: sidebar completamente configurato (NO warning)
  - 12-pacchetti.png: 3 pacchetti attivi (Festa Papà, Estate, Natale)
  - 13-fedelta.png: programma fedeltà con VIP points
- **Risoluzione**: 1621×1023 PNG (full Tauri window capture)
- **Data quality**: 100% realistic Italian PMI data (nomi, importi, date)
- **Old schede backedup**: Moved old 12-23 screenshots to `landing/screenshots/backup-old/`

### Acceptance Criteria S128 ✅
- ✅ 13+ screenshot catturati (target 18 con schedes verticali opzionali)
- ✅ Dati realistici (166 clienti, €4.850 fatturato, 34 apt oggi, mix pagamenti)
- ✅ Zero warning "non configurato" visibile
- ⏳ Schede verticali a schermo pieno (2.2 — opzionale per video)

---

## STATO GIT
```
Branch: master | HEAD: bd35ac9
Commits S128:
  bd35ac9 feat(S128): capture 13 fresh screenshots with demo data
  74fe9e7 feat(S127): add demo seed for screenshots — €4.850 fatturato, 48 clients
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       ✅ FAQ + SEED + ALIAS + DISAMBIG + WELCOME-BACK + NEW-VERTICALS (S123-S126)
Phase 10e: Sara Bug Fixes       ✅ FAQ vars + intent routing (S127)
Sprint 1:  Product Ready        ✅ Prezzi OK + Phone-home OK + Demo seed loaded (S127)
Sprint 2:  Screenshot Perfetti  ⏳ NEXT — catturare da iMac con dati demo belli
Sprint 3:  Video che Spacca     ⏳
Sprint 4:  Landing Definitiva   ⏳
Sprint 5:  Sales Agent WA       ⏳
```

---

## PROSSIMA SESSIONE 129 — PRIORITÀ

### A. Sprint 3: Video che Spacca (NUOVO SCREENSHOT CONTENT)
- **Disponibile**: 13 screenshot perfetti con dati realisti in `landing/screenshots/`
- Aggiornare voiceover copy per includere:
  - Sezione PACCHETTI & MARKETING (Festa Papà, Estate, Natale)
  - Sezione FEDELTÀ (VIP points, timbri, premi)
  - Copy competitore aggiornato: "€120+ al mese vs FLUXION lifetime €897"
  - Insight: "Con Sara lavori in maniera ordinata"
- Rigenerare storyboard JSON con screenshot nuovi (12-pacchetti, 13-fedelta)
- Generare voiceover Edge-TTS
- Assemblare Video V6 con footage nuovo
- Upload YouTube con metadata SEO (capitoli, tags italiani, SRT)

### B. Remaining voice bugs (lower priority)
- [ ] Two-digit phone words (trentatre, ventuno)
- [ ] Spostamento appuntamenti non trova appuntamenti esistenti

### C. Landing Page Update (Sprint 4 prep)
- [ ] Embed video YouTube nella landing
- [ ] Aggiornare hero section screenshot (01-dashboard.png)
- [ ] Aggiornare feature grid con nuovi screenshot

---

## FILE CHIAVE SESSIONE 128
- `scripts/capture-screenshots-remote.py` — Python SSH orchestrator + Swift capture
- `landing/screenshots/01-13/*.png` — 13 screenshot perfetti, 1621×1023, dati reali
- `landing/screenshots/backup-old/` — Old schede screenshots (S126+earlier)

---

## NOTE TECNICHE

### Pipeline riavvio (SEMPRE CON PYTHONUNBUFFERED)
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && DYLD_LIBRARY_PATH=lib/pjsua2 PYTHONUNBUFFERED=1 nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Demo DB su iMac
```
Seed: scripts/seed-demo-screenshot.sql
Path: /Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db
Vertical: salone | Nome: Salone Elegance di Giulia
Clienti: 48 (5 VIP) | Fatturato: €4.850 | Oggi: 9 apt | Settimana: 25 apt
Top servizio: Taglio + Barba (25x)
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 129.
PRIORITÀ:
1. Sprint 3: Video che spacca con contenuti pacchetti + fedeltà
2. Sprint 4: Landing page aggiornata con video
3. Sprint 5: Sales Agent WhatsApp (il cuore del business)

Note:
- Screenshot pronti e belli: landing/screenshots/
- Script di capture salvato: scripts/capture-screenshots-remote.py
- Prossimo: rinnovare video voiceover + aggiungere sezioni mancanti
```
