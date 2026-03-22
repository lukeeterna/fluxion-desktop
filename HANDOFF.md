# FLUXION — Handoff Sessione 108 → 109 (2026-03-21)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni. MAI presentare problemi senza soluzioni. MAI fare il compitino."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev ATTIVO porta 3001 | **sshd ha Screen Recording + Accessibility**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0 (NO drawtext/subtitles), Edge-TTS, Pillow, wrangler 3.22

---

## STATO GIT
```
Branch: master | HEAD: 51a0123
type-check: 0 errori
iMac: sincronizzato, Tauri dev attivo
```

---

## COMPLETATO SESSIONE 108

### 1. Seed Dati Video Demo
- `scripts/seed-video-demo.sql` — 47 appuntamenti (17-22 marzo), 5 schede verticali compilate, 5 incassi
- Applicato al DB iMac: `/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db`
- Clienti con schede: Sara Colombo (parrucchiere), Marco Ricci (veicoli), Elena Moretti (odontoiatrica), Francesca Russo (estetica), Luca Pellegrini (fitness)

### 2. Screenshot REALI da App Live (iMac)
Catturati via SSH + Swift CGWindowListCreateImage + AppleScript accessibility:
```
landing/screenshots/
  01-dashboard.png       — 9 appuntamenti, 61 clienti, KPI reali
  03-clienti.png         — Lista 61 clienti
  04-servizi.png         — Listino con prezzi
  05-operatori.png       — 4 operatori
  07-cassa.png           — €222 totale, 5 transazioni, contanti+carta+satispay
  08-voice.png           — Sara Voice Agent
  12-scheda-selector.png — Selezione 8 verticali (WOW per video)
  13-scheda-parrucchiere.png — Passaporto Capello, tipo/porosità/lunghezza
  14-scheda-veicoli.png  — 3 veicoli con targhe, Volkswagen principale
  15-scheda-odontoiatrica.png — Odontogramma 32 denti colorati!
  16-scheda-estetica.png — Fototipo Fitzpatrick 6 livelli, tipo pelle
  17-scheda-fitness.png  — Profilo, misurazioni, scheda allenamento
```

### 3. Tecnica Screenshot iMac via SSH (FUNZIONANTE)
- **Screen Recording**: abilitato per `sshd-keygen-wrapper` + `Terminal.app`
- **Accessibility**: abilitato per `sshd-keygen-wrapper`
- **Cattura window**: Swift CGWindowListCreateImage (cap1.swift su iMac)
- **Navigazione**: AppleScript click at {x,y} + accessibility API per trovare elementi
- **Sidebar coords**: Dashboard(153), Calendario(197), Clienti(241), Servizi(285), Operatori(329), Fatture(373), Cassa(417), Fornitori(461), Analytics(505?), Voice(549), Impostazioni(593)

### 4. Video Script V3 (create-demo-video.py)
- Scritto ma NON eseguito (priorità cambiata a UI audit)
- Struttura: Hook → Dashboard → Calendario → Clienti → Verticali (problema→soluzione) → Sara → Prezzo → CTA

---

## DA FARE S109 — UI POLISH CON SKILL ENTERPRISE (PRIORITA' FONDATORE)

### PROBLEMA IDENTIFICATO
Il fondatore ha visto gli screenshot delle schede verticali e ha detto:
- "Non mi piace l'estetica"
- "Pochi effetti, deve essere attrattivo"
- "Inutile fare il video ora" (l'UI non è pronta)
- "Devi usare SOLO Claude Code SKILL di livello enterprise grade"

### AUDIT UI COMPLETATO (S108)
Risultato audit completo — 3 CRITICAL, 6 HIGH, 8 MEDIUM, 5 LOW:
- **C1**: 5 schede mancano glassmorphism header (solo Parrucchiere ce l'ha)
- **C2**: Nessuna scheda ha stat chips tranne Parrucchiere
- **C3**: Loading states inconsistenti
- **H1**: Tab styling incoerente tra schede
- **H2**: Badge count mancanti sui tab
- **H3**: Outer container diverso (Card vs rounded-2xl shadow-2xl)
- **H4**: Colori accent caotici tra schede
- **H5**: SchedaEstetica usa document.getElementById (anti-pattern)
- **H6**: Empty state inconsistenti
- **M1-M8**: Section cards mancanti, no "Passaporto" strip, Dashboard piatta, Calendario "oggi" invisibile, etc.
- Gold standard interno: `SchedaParrucchiere.tsx` (glassmorphism, stat chips, color timeline, ambient blur)

### IMPLEMENTAZIONE S108 — DA RIFARE CON SKILL
⚠️ **L'implementazione fatta in S108 è stata eseguita con agent `react-frontend` SENZA skill enterprise.**
Il fondatore richiede che OGNI implementazione usi SOLO Claude Code skills enterprise-grade.

**Cosa è stato fatto (da VERIFICARE e potenzialmente rifare con skill):**
- Creato `SchedaWrapper.tsx` + `SchedaTabs.tsx` (componenti condivisi)
- Refactored 5 schede (Veicoli, Odontoiatrica, Estetica, Fitness, Carrozzeria)
- Fix SchedaEstetica: document.getElementById → state, checkbox → pill toggles, 6 colori fototipo
- type-check: 0 errori

**DA FARE IN S109:**
1. **Creare skill `fluxion-ui-polish`** per task UI/UX (design system, componenti, animazioni)
2. **Verificare visivamente** le modifiche S108 (sync iMac → screenshot → confronto before/after)
3. Se qualità insufficiente → **rifare con skill enterprise**
4. Aggiungere: micro-animazioni tab, Dashboard glassmorphism, Calendario "oggi" highlight
5. **Riscattare screenshot** dopo verifica
6. **POI video** con screenshot aggiornati

### FEEDBACK FONDATORE VIDEO (da integrare quando si fa)
- Ristoranti NO — tolti dal video
- Sara: video REALE telefonata cliente↔Sara con prenotazione live
- Mostrare marketing: pacchetti VIP, loyalty, come si comunica con i clienti
- QR code per clienti: non implementato, da fare
- Spiegazione video di ogni feature
- "Gianluca Distasi" eliminato dai dati demo → rinominato "Luca Pellegrini"

---

## STRIPE INFO
```
Account: LIVE
Base Payment Link: https://buy.stripe.com/bJe7sM19ZdWegU727E24000
Pro Payment Link: https://buy.stripe.com/00w28sdWL8BU0V9fYu24001
```

---

## DIRETTIVE FONDATORE (NON NEGOZIABILI)
1-16: vedi S107 HANDOFF (invariate)

---

## BUILD COMMANDS
```bash
# Cattura screenshot iMac (SSH)
ssh imac "swift /tmp/cap1.swift /tmp/screenshot.png"
scp imac:/tmp/screenshot.png ./landing/screenshots/XX-name.png

# Click sidebar via AppleScript
ssh imac "osascript -e 'tell application \"System Events\" to tell process \"tauri-app\" to click at {90, Y}'"

# Screenshot Playwright (mock, MacBook only)
cd e2e-tests && npx playwright test tests/screenshots.spec.ts --project=firefox
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 109. CTO MODE FULL.
S108: 13 screenshot REALI + audit UI completato + implementazione SchedaWrapper (DA VERIFICARE).
FONDATORE: "SOLO Claude Code skills enterprise-grade per OGNI implementazione."
FOCUS S109:
1. DEEP RESEARCH CoVe 2026: UI best practice gestionali/CRM PMI 2026 (Fresha, Notion, Linear, HubSpot, Monday)
2. CREARE skill `fluxion-ui-polish` (design system, bento box, micro-animazioni, colori semantici)
3. Verificare visivamente le modifiche S108 (sync iMac → screenshot before/after)
4. Se qualità insufficiente → RIFARE con la nuova skill usando i risultati della research
5. Pattern da implementare: Bento Box layout, micro-animazioni stato, colori semantici (semaforo), meno linee + più spazio bianco + icone
6. Riscattare screenshot → poi video
REGOLA: FASE 0 CoVe 2026 = identificare/creare skill PRIMA di implementare. MAI agent raw.
REGOLA: Deep research PRIMA di implementare qualsiasi UI change.
```
