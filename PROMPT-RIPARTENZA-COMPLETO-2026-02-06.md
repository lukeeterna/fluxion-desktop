# PROMPT RIPARTENZA - FLUXION Sessione 2026-02-06 (POMERIGGIO)

> **Data**: 2026-02-06 (Sessione Pomeridiana)
> **Stato**: 90% - WAITLIST Implementato, Setup Wizard v2 Completo
> **Branch**: `master`
> **Commit**: `ae6c3a6`

---

## 📚 FILE DI SISTEMA (Riferimento Obbligatorio)

| File | Scopo | Stato |
|------|-------|-------|
| `CLAUDE.md` | Master orchestrator, sprint attivo, checklist | Aggiornato |
| `PRD-FLUXION-COMPLETE.md` | Documento di verità funzionalità | Aggiornato v1.0 |

**⚠️ REGOLA**: Leggere sempre `CLAUDE.md` prima di iniziare. Verificare `PRD-FLUXION-COMPLETE.md` sezione 7.1 per roadmap.

---

## ✅ TASK COMPLETATE OGGI (Flag)

### Voice Agent WAITLIST
- ✅ [x] **Intent WAITLIST** in `intent_classifier.py` - 8 pattern regex italiani
- ✅ [x] **Stati State Machine**: `CHECKING_AVAILABILITY`, `SLOT_UNAVAILABLE`, `PROPOSING_WAITLIST`, `CONFIRMING_WAITLIST`, `WAITLIST_SAVED`
- ✅ [x] **Business Logic** in `booking_manager.py`:
  - `_find_alternative_slots()` - Trova 3+ slot alternativi
  - `_build_alternatives_message()` - Messaggio voice-friendly
  - `_handle_slot_freed()` - Notifica waitlist su cancellazione
  - `_send_waitlist_notification()` - WhatsApp con 2h timeout
- ✅ [x] Campi context `BookingContext`: `waitlist_id`, `proposed_waitlist`, `alternative_slots`

### Setup Wizard v2 - Configurazione
- ✅ [x] **Migration 021** `setup_config.sql` - Campi `whatsapp_number`, `ehiweb_number`
- ✅ [x] **Backend Rust** `setup.rs` - Aggiunti campi a `SetupConfig`, save/get
- ✅ [x] **TypeScript** `setup.ts` - Zod schemas, types, default values
- ✅ [x] **UI** `SetupWizard.tsx` Step 6 - Campi WhatsApp Business e EhiWeb

### Testing & Quality
- ✅ [x] **Rust Tests**: 54/54 PASSED su iMac
- ✅ [x] **TypeScript**: Clean compile (0 errori)
- ✅ [x] **Voice Agent Import**: Test OK su iMac
- ✅ [x] **Commit + Push**: `ae6c3a6` su master

---

## 🔴 TASK PENDENTI (Da Completare)

### Priorità Alta
- [ ] **WhatsApp Pacchetti Selettivo**
  - UI `WhatsAppPacchettiSender.tsx`
  - Filtri: Tutti | VIP (`is_vip=1`) | VIP 3+ stelle (`loyalty_visits>=3`) | Custom
  - Rate limiting 60 msg/ora
  - Report invio

- [ ] **E2E Testing**
  - Fix PATH in `e2e-tests/playwright.config.ts`
  - Test smoke su iMac
  - Test critical su iMac

- [ ] **Build Produzione Finale**
  - Verificare build completata su iMac
  - Tag release v0.8.0

### Priorità Media
- [ ] **MCP CI/CD Monitoraggio** (opzionale)
  - Setup MCP server
  - Dashboard stato test

### Priorità Bassa (Fase 2)
- [ ] **5 Schede Verticali Placeholder**:
  - Parrucchiere (colorazioni, formulazioni)
  - Veicoli (storico, tagliandi)
  - Carrozzeria (danni, foto)
  - Medica (cartella clinica)
  - Fitness (schede, misurazioni)

---

## 🎯 OBIETTIVI PROSSIMA SESSIONE

### Scenario A: Completa WhatsApp (Consigliato)
```
WhatsApp Pacchetti Selettivo → E2E Testing → Build → Release v0.8.0
Tempo stimato: 2-3 ore
```

### Scenario B: Completa Schede Verticali
```
Scheda Parrucchiere → Scheda Veicoli → Test → Build
Tempo stimato: 3-4 giorni
```

---

## 📁 FILE CHIAVE MODIFICATI (Oggi)

```
voice-agent/
├── src/
│   ├── intent_classifier.py      ✅ IntentCategory.WAITLIST + 8 patterns
│   ├── booking_state_machine.py  ✅ 5 nuovi stati waitlist
│   └── booking_manager.py        ✅ Business logic completa (+193 righe)

src/
├── components/
│   └── setup/
│       └── SetupWizard.tsx       ✅ Step 6 con campi WhatsApp/EhiWeb
├── types/
│   └── setup.ts                  ✅ Nuovi campi config

src-tauri/
├── src/
│   └── commands/
│       └── setup.rs              ✅ API nuovi campi
└── migrations/
    └── 021_setup_config.sql      ✅ Migration nuovi campi
```

---

## 🔧 COMANDI RAPIDO RIPARTENZA

```bash
# 1. Verifica stato (MacBook)
cd /Volumes/MontereyT7/FLUXION
git status
npm run type-check

# 2. Sync iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"

# 3. Test Rust
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && export PATH='/Users/gianlucadistasi/.cargo/bin:$PATH' && cargo test --lib"

# 4. Build (se necessario)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && export PATH='/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:$PATH' && npm run tauri build"
```

---

## 📊 STATO PROGETTO

```
Completamento: ~90%
├── Core System: 100% ✅
├── CRM + 3 Schede: 100% ✅
├── Calendario + Booking: 100% ✅
├── Fatturazione: 100% ✅
├── Loyalty: 100% ✅
├── Voice Agent Base: 95% ✅
├── Voice Agent WAITLIST: 90% ✅ (intent + logic)
├── Setup Wizard v2: 100% ✅
├── Licenze Ed25519: 100% ✅
├── 5 Schede Verticali: 0% 📝 (placeholder)
└── WhatsApp Pacchetti: 0% 🔴 (da fare)
```

---

## 💬 PROMPT PER RIPARTENZA

Copia e incolla questo prompt:

```
Ciao, sono il CTO di FLUXION. Proseguiamo lo sviluppo.

STATO ATTUALE (2026-02-06 pomeriggio):
- WAITLIST: ✅ Intent + State Machine + Business Logic implementati
- Setup Wizard v2: ✅ Campi WhatsApp, EhiWeb, Nome Attività aggiunti
- Rust Tests: ✅ 54/54 PASSED
- TypeScript: ✅ Clean
- Commit: ae6c3a6 su master

DA COMPLETARE:
1. WhatsApp Pacchetti Selettivo (UI + filtri VIP/stelle)
2. E2E Testing (fix PATH playwright)
3. Build produzione finale + tag v0.8.0

FILE RIFERIMENTO:
- CLAUDE.md (master orchestrator)
- PRD-FLUXION-COMPLETE.md (documento verità)
- PROMPT-RIPARTENZA-COMPLETO-2026-02-06.md (questo file)

AMBIENTE:
- MacBook: /Volumes/MontereyT7/FLUXION (dev)
- iMac: /Volumes/MacSSD - Dati/fluxion (build)
- Repo: lukeeterna/fluxion-desktop

Procedi con WhatsApp Pacchetti Selettivo o E2E Testing.
```

---

## 🏁 CHECKLIST CHIUSURA SESSIONE

### Prima di chiudere:
- [ ] Verificare `CLAUDE.md` aggiornato
- [ ] Verificare `PRD-FLUXION-COMPLETE.md` aggiornato
- [ ] Commit e push modifiche
- [ ] Sync iMac
- [ ] Test passano
- [ ] Build OK

### Prossima sessione:
- [ ] Leggere questo prompt
- [ ] Leggere `CLAUDE.md`
- [ ] Scegliere task da `🔴 TASK PENDENTI`
- [ ] Eseguire `🔧 COMANDI RAPIDO RIPARTENZA`

---

*Prompt generato: 2026-02-06*
*Versione: 1.0*
*Stato: Pronto per ripartenza*
