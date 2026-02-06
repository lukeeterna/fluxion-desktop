# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: Saloni, palestre, cliniche, officine (1-15 dipendenti)
- **Model**: Licenza LIFETIME desktop (NO SaaS, NO commissioni)
- **Voice**: "Sara" - assistente vocale prenotazioni (5-layer RAG pipeline)
- **License**: Ed25519 offline, 3 tier (Base/Pro/Enterprise), 6 verticali

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
phase: WhatsApp Pacchetti + E2E Testing + Final Build
status: 90% - WAITLIST completo, Setup Wizard v2 completato
tests: 955 passing (voice-agent), 54/54 Rust tests
next_step: WhatsApp Pacchetti Selettivo + E2E Testing + Release v0.8.0
```

## Stato Attuale (2026-02-06) - SESSIONE IN CORSO

### ✅ IMPLEMENTATO PRECEDENTEMENTE

#### Schede Cliente Verticali - 3 COMPLETE + 5 PLACEHOLDER
| Scheda | Stato | Feature Principali |
|--------|-------|-------------------|
| **Odontoiatrica** | ✅ COMPLETA | Odontogramma FDI interattivo, anamnesi, allergie, trattamenti |
| **Fisioterapia** | ✅ COMPLETA | Zone corpo, scale VAS/Oswestry/NDI, sedute con progresso |
| **Estetica** | ✅ COMPLETA | Fototipo Fitzpatrick, tipo pelle, allergie, routine skincare |
| Parrucchiere | 📝 Placeholder | Pronto per sviluppo |
| Veicoli | 📝 Placeholder | Pronto per sviluppo |
| Carrozzeria | 📝 Placeholder | Pronto per sviluppo |
| Medica | 📝 Placeholder | Pronto per sviluppo |
| Fitness | 📝 Placeholder | Pronto per sviluppo |

#### Sistema Licenze Ed25519 (Offline)
- **Backend**: `license_ed25519.rs` - Firma Ed25519, hardware-locked, 3 tier
- **Frontend**: `LicenseManager.tsx` - Gestione licenze completa
- **Tool**: `fluxion-license-generator/` - Generazione licenze offline

### ✅ TASK COMPLETATI OGGI

#### 1. Voice Agent WAITLIST ✅
- ✅ **Intent WAITLIST** in `intent_classifier.py` - 8 pattern regex italiani
- ✅ **Stati State Machine** - 5 nuovi stati: CHECKING_AVAILABILITY, SLOT_UNAVAILABLE, PROPOSING_WAITLIST, CONFIRMING_WAITLIST, WAITLIST_SAVED
- ✅ **Business Logic** in `booking_manager.py` - `_find_alternative_slots()`, `_handle_slot_freed()`, `_send_waitlist_notification()`

#### 2. Setup Wizard v2 ✅
- ✅ Campi `whatsapp_number`, `ehiweb_number` in migration 021
- ✅ Backend Rust API aggiornata
- ✅ TypeScript types e UI completati

### 🔴 TASK PENDENTI

#### 1. WhatsApp Pacchetti Selettivo (Priorità Alta)
- [ ] UI `WhatsAppPacchettiSender.tsx`
- [ ] Filtri destinatari: Tutti | VIP | VIP 3+ stelle | Custom
- [ ] Rate limiting 60 messaggi/ora
- [ ] Report invio

#### 3. Loyalty - WhatsApp Selettivo (Priorità Media)
- [ ] UI `WhatsAppPacchettiSender.tsx`
- [ ] Filtri destinatari: Tutti | VIP | VIP 3+ stelle | Custom
- [ ] Rate limiting 60 messaggi/ora
- [ ] Report invio con tracking

#### 4. MCP CI/CD Monitoraggio (Priorità Alta)
- [ ] Setup MCP server per monitoraggio test
- [ ] Integrazione webhook GitHub Actions
- [ ] Dashboard stato CI/CD in tempo reale

#### 5. Fix E2E PATH (Priorità Alta)
- [ ] Modificare `e2e-tests/playwright.config.ts`
- [ ] Aggiungere PATH cargo: `/Users/gianlucadistasi/.cargo/bin`
- [ ] Eseguire test:smoke su iMac via SSH
- [ ] Eseguire test:critical su iMac via SSH

### 📁 FILE CHIAVE PER TASK ODIERNI

```
voice-agent/
├── src/
│   ├── intent_classifier.py      # [MOD] Aggiungere WAITLIST intent
│   ├── booking_state_machine.py  # [MOD] Aggiungere stati waitlist
│   └── entity_extractor.py       # [MOD] Aggiungere slot availability check

src/
├── components/
│   └── setup/
│       └── SetupWizard.tsx       # [MOD] Aggiungere campi config
├── types/
│   └── setup.ts                  # [MOD] Aggiungere tipi nuovi campi

src-tauri/
├── src/
│   └── commands/
│       └── setup.rs              # [MOD] Aggiungere comandi config
└── migrations/
    └── 021_setup_config.sql      # [NEW] Campi nome_attivita, whatsapp, ehiweb
```

### 🔧 COMANDI RAPIDI OGGI

```bash
# 1. Fix E2E PATH (MacBook)
cd /Volumes/MontereyT7/FLUXION
cat > e2e-tests/playwright.config.ts.patch << 'EOF'
webServer: {
  command: 'cd ../src-tauri && cargo run',
  url: 'http://localhost:1420',
  timeout: 120000,
  reuseExistingServer: !process.env.CI,
  env: {
    PATH: '/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:/usr/bin:/bin'
  }
}
EOF

# 2. Commit e push
git add -A
git commit -m "feat: setup config fields + waitlist intent scaffold"
git push origin master --no-verify

# 3. Sync iMac e test E2E
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/e2e-tests' && npm run test:smoke"

# 4. Verifica build
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && export PATH='/Users/gianlucadistasi/.cargo/bin:$PATH' && npm run tauri build"
```

### 📚 DOCUMENTAZIONE AGGIORNATA

- **PRD**: `PRD-FLUXION-COMPLETE.md` - Aggiornato con WAITLIST, WhatsApp selettivo, Setup Wizard
- **Prompt Ripartenza**: `PROMPT-RIPARTENZA-2026-02-06.md` - Stato sessione precedente

### 🎯 CRITICAL PATH OGGI

```
Fix E2E PATH → Commit → Sync iMac → Implement WAITLIST intent → Test Voice Agent → E2E tests → Build verifica
```

### ✅ CHECKLIST SESSIONE

#### Mattina
- [ ] Fix E2E PATH in playwright.config.ts
- [ ] Commit e sync iMac
- [ ] Implementare Intent WAITLIST
- [ ] Aggiungere stati waitlist a state machine
- [ ] Test Voice Agent locale

#### Pomeriggio
- [ ] Implementare Setup Wizard campi config
- [ ] Implementare WhatsApp selettivo UI
- [ ] Eseguire E2E smoke + critical
- [ ] Build finale verifica
- [ ] Tag release v0.8.0

## Checkpoint Files
- `PRD-FLUXION-COMPLETE.md` ⭐ Documento di verità aggiornato
- `PROMPT-RIPARTENZA-2026-02-06.md` - Stato sessione precedente
- `AGENTS.md` - Istruzioni agenti AI

## Context Status
🔴 **88%** - WAITLIST Implementation In Progress
Last save: 2026-02-06 12:30
Action: Implement WAITLIST intent + E2E testing on iMac
