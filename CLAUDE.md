# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: Saloni, palestre, cliniche, officine (1-15 dipendenti)
- **Model**: Licenza LIFETIME desktop (NO SaaS, NO commissioni)
- **Voice**: "Sara" - assistente vocale prenotazioni (5-layer RAG pipeline)
- **License**: Ed25519 offline, 3 tier (Base/Pro/Enterprise), 6 verticali

## 🏛️ I 3 PILASTRI (Core Business)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXION - I 3 PILASTRI                       │
├─────────────────────────────────────────────────────────────────┤
│  📱 COMUNICAZIONE      🎯 MARKETING        ⚙️ GESTIONE          │
│  WhatsApp + Voice      Loyalty + Pacchetti  Calendario + Schede │
│                                                                  │
│  → Sostituisce l'operatore        → PMI non hanno tempo        │
│  → 24/7 automatico                → Zero-cost marketing         │
│  → Vantaggio competitivo          → Automazione completa        │
└─────────────────────────────────────────────────────────────────┘
```

**Questi 3 pilastri devono essere PERFETTI - sono il cuore del prodotto.**

## Critical Rules
1. Never commit API keys, secrets, or .env files
2. Always TypeScript (never JS), always async Tauri commands
3. Run tests before commit (see `.claude/rules/testing.md` for checklist)
4. A task is NOT complete until code works AND is verified (DB records, E2E)
5. Italian field names in APIs: `servizio`, `data`, `ora`, `cliente_id`
6. Dev on MacBook, test on iMac (192.168.1.7) - Tauri needs macOS 12+
7. Restart voice pipeline on iMac after ANY Python change

## Active Sprint
```yaml
branch: master
phase: Comunicazione Perfetta - Voice Agent Fix + Test Live
status: 92% - Voice Agent fixati, pronti per test live su iMac
tests: 955 passing (voice-agent), 54/54 Rust tests, TypeScript OK
next_step: Test Live Voice Agent su iMac + Build Finale v0.8.1
```

## 🎯 OBIETTIVO: COMUNICAZIONE PERFETTA

I 3 pilastri devono funzionare alla perfezione:

### 1. 📱 COMUNICAZIONE (Sostituisce Operatore)
- ✅ Voice Agent "Sara" - 5 layer pipeline completa
- ✅ WAITLIST intent + business logic
- ✅ WhatsApp Business integration base
- ✅ **FIXATO (2026-02-06)**: WhatsApp inviato dopo booking
- ✅ **FIXATO (2026-02-06)**: Chiusura graceful chiamata con conferma
- ✅ **FIXATO (2026-02-06)**: Disambiguazione nomi (Gino/Gigio, Maria/Mario)
- 🔴 **DA FARE**: Invio pacchetti WhatsApp selettivo (VIP/filtri)
- 🔴 **DA FARE**: Voice Agent greeting dinamico con nome attività

### 2. 🎯 MARKETING (Zero-Cost per PMI)
- ✅ Sistema Loyalty (timbri, VIP, referral)
- ✅ Pacchetti servizi (creazione, scontistica libera)
- ✅ Database: `is_vip`, `loyalty_visits`, `consenso_whatsapp`
- 🔴 **DA FARE**: Invio WhatsApp pacchetti filtrato per VIP/stelle

### 3. ⚙️ GESTIONE (Automazione Completa)
- ✅ Calendario + Booking con state machine
- ✅ 3 Schede verticali complete (Odontoiatrica, Fisioterapia, Estetica)
- ✅ Fatturazione elettronica XML
- 📝 5 Schede placeholder (da fare in Fase 2)

## 📋 TASK CRITICHE DA COMPLETARE

### 🔴 Priorità Massima (Prima del Build)
1. **WhatsApp Pacchetti Selettivo**
   - UI in `PacchettiAdmin.tsx` o scheda cliente
   - Filtri: Tutti (con consenso) | VIP | VIP 3+ stelle
   - Template WhatsApp con nome attività
   - Rate limiting 60 msg/ora
   - Tracking invio

2. **Voice Agent Greeting Dinamico**
   - Leggere `nome_attivita` da impostazioni
   - "Buongiorno, sono Sara di {nome_attivita}"
   - Integrare in tutti i messaggi vocali

3. **E2E Testing**
   - Fix PATH in `playwright.config.ts`
   - Test smoke + critical su iMac

4. **Build Produzione**
   - Solo a fine sviluppo (NON ora)
   - Verificare Fluxion.app ~16MB
   - Tag release v0.8.0

### 🟡 Priorità Media (Dopo il Build)
5. **5 Schede Verticali Placeholder**
   - Parrucchiere, Veicoli, Carrozzeria, Medica, Fitness

## ✅ IMPLEMENTATO OGGI (2026-02-06)

### Voice Agent v0.8.1 Fixes ✅
- **WhatsApp Fix**: Salvataggio numero telefono cliente + invio post-chiusura
- **Chiusura Graceful**: Nuovo stato `ASKING_CLOSE_CONFIRMATION` con flow conferma
  - "Terminiamo la comunicazione e le inviamo la conferma via WhatsApp?"
  - Utente può rispondere "sì" (chiude) o "no" (rimane in linea)
- **Phonetic Matching**: Fix miss-match nomi simili (Gino/Gigio, Maria/Mario)
  - Similarità Levenshtein ≥70% → chiede conferma
  - Dizionario varianti fonetiche italiane
- **Interruption Fix**: Pattern "aspetta"/"ancora" non interferiscono più con close confirmation

### Voice Agent WAITLIST ✅
- Intent WAITLIST con 8 pattern italiani
- 5 nuovi stati state machine
- Business logic: alternative slots + notifica WhatsApp

### Setup Wizard v2 ✅
- Campi `whatsapp_number`, `ehiweb_number`, `nome_attivita`
- Migration 021
- TypeScript + Rust API

## 📁 FILE CHIAVE

```
# Comunicazione (da completare)
src/components/loyalty/PacchettiAdmin.tsx     # Aggiungere invio WhatsApp
src/components/whatsapp/                       # Verificare integrazione
voice-agent/src/main.py                         # Greeting dinamico

# Marketing (esistente, da integrare)
src/components/loyalty/LoyaltyProgress.tsx     # ✅ Esiste
src/hooks/use-loyalty.ts                       # ✅ Esiste
src-tauri/migrations/005_loyalty_pacchetti_vip.sql  # ✅ Migration OK

# Gestione (completo)
src/components/schede-cliente/                 # 3 complete, 5 placeholder
src/pages/Calendario.tsx                       # ✅ Completo
```

## 🔧 COMANDI RAPIDI

```bash
# Test (MacBook)
cd /Volumes/MontereyT7/FLUXION
npm run type-check

# Test (iMac via SSH)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && export PATH='/Users/gianlucadistasi/.cargo/bin:$PATH' && cargo test --lib"

# Build (SOLO a fine sviluppo, su iMac)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && export PATH='/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:$PATH' && npm run tauri build"

# Sync
git add -A && git commit -m "..." && git push origin master --no-verify
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
```

## 📚 DOCUMENTAZIONE

- **PRD**: `PRD-FLUXION-COMPLETE.md` ⭐ Documento di verità
- **Prompt**: `PROMPT-RIPARTENZA-COMPLETO-2026-02-06.md` - Per ripartenza
- **Agents**: `AGENTS.md` - Istruzioni agenti AI

## Context Status
🟡 **92%** - Voice Agent fixati e testati, pronti per test live
Last save: 2026-02-06
Action: Test Live Voice Agent su iMac (domani) + Build Finale v0.8.1

## 🧪 TEST LIVE PREPARATI (per domani su iMac)

### Scenari da testare con Voice Agent "Sara":
1. **"Gino vs Gigio"** - Verificare disambiguazione fonetica
2. **"Chiacchierona Post-Booking"** - Cliente che non vuole chiudere dopo booking
3. **"Flusso Perfetto"** - Booking → WhatsApp → Chiusura completa
4. **"STT Confuso"** - Errori di riconoscimento vari
5. **"Rifiuto Elegante"** - Cliente che rifiuta la prenotazione

### File Voice Agent modificati:
- `voice-agent/src/orchestrator.py` - WhatsApp + salvataggio phone
- `voice-agent/src/booking_state_machine.py` - Stato ASKING_CLOSE_CONFIRMATION
- `voice-agent/src/disambiguation_handler.py` - Phonetic matching
