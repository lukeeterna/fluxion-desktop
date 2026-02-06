# PROMPT RIPARTENZA - FLUXION Sessione 2026-02-06 (POMERIGGIO)

> **Data**: 2026-02-06 (Sessione Pomeridiana)
> **Stato**: 90% - Comunicazione da perfezionare
> **Branch**: `master`
> **Commit**: `902bd81`

---

## 🏛️ VISIONE: I 3 PILASTRI (Da Leggere Prima)

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

**REGOLA**: I 3 pilastri devono essere PERFETTI. Questo è il cuore del prodotto.

---

## 📚 FILE DI SISTEMA (Riferimento Obbligatorio)

| File | Scopo | Stato |
|------|-------|-------|
| `CLAUDE.md` | I 3 pilastri, task, comandi | ✅ Aggiornato |
| `PRD-FLUXION-COMPLETE.md` | Funzionalità dettagliate | ✅ Aggiornato v1.0 |

**⚠️ LEGGERE SEMPRE `CLAUDE.md` PRIMA** - Contiene la visione dei 3 pilastri.

---

## ✅ COSA C'È GIÀ (Non rifare)

### 📱 Comunicazione (Parziale)
- ✅ Voice Agent "Sara" - 5 layer pipeline
- ✅ WAITLIST intent + business logic completa
- ✅ WhatsApp Business base integration
- ✅ Setup Wizard con `nome_attivita`, `whatsapp_number`

### 🎯 Marketing (Base OK)
- ✅ Database Loyalty: `is_vip`, `loyalty_visits`, `consenso_whatsapp`
- ✅ UI Pacchetti: `PacchettiAdmin.tsx` (creazione pacchetti)
- ✅ UI Loyalty: `LoyaltyProgress.tsx` (tessera timbri)
- ✅ Hooks: `use-loyalty.ts` (API complete)

### ⚙️ Gestione (Completa)
- ✅ Calendario + Booking state machine
- ✅ 3 Schede verticali complete (Odontoiatrica, Fisioterapia, Estetica)
- ✅ Fatturazione XML

---

## 🔴 COSA MANCA (Task Prioritarie)

### 1. WhatsApp Pacchetti Selettivo (CRITICO)
**Dove**: Integrare in `PacchettiAdmin.tsx` o nuovo componente

**Flusso Operatore:**
1. Crea pacchetto personalizzato (servizi + sconto % libero) ✅ GIÀ FATTO
2. **NUOVO**: Seleziona filtro destinatari:
   - Tutti i clienti (con `consenso_whatsapp = true`)
   - Solo VIP (`is_vip = 1`)
   - Solo VIP 3+ stelle (`is_vip = 1 AND loyalty_visits >= 3`)
3. **NUOVO**: Invio WhatsApp con template
4. **NUOVO**: Rate limiting 60 msg/ora + tracking

**Template WhatsApp:**
```
Ciao {nome}! 🎁

Abbiamo pensato a te: {nome_pacchetto}
✨ {servizi_inclusi} servizi
💰 Solo €{prezzo_scontato} invece di €{prezzo_originale}
⏰ Valido per {validita_giorni} giorni

Prenota ora rispondendo a questo messaggio!
{nome_attivita}
```

### 2. Voice Agent Greeting Dinamico
- Leggere `nome_attivita` da impostazioni DB
- Modificare greeting: "Buongiorno, sono Sara di {nome_attivita}"
- File: `voice-agent/src/main.py` o config

### 3. E2E Testing
- Fix PATH `e2e-tests/playwright.config.ts`
- Test smoke + critical su iMac

### 4. Build Produzione (SOLO a fine sviluppo)
- Verificare su iMac
- Tag v0.8.0

---

## 🎯 SCENARI PROSSIMA SESSIONE

### Scenario A: Completa Comunicazione (Consigliato - 2-3 ore)
```
WhatsApp Pacchetti UI → Voice Greeting → E2E → Build → v0.8.0
```
**Risultato**: I 3 pilastri sono PERFETTI. Pronto per vendita.

### Scenario B: Scheda Parrucchiere (3-4 giorni)
```
Scheda Parrucchiere completa → Test → Build
```
**Risultato**: +1 verticale completo. Pilastri già OK.

---

## 📁 FILE CHIAVE DA MODIFICARE

```
# DA MODIFICARE (Task 1 - WhatsApp Pacchetti)
src/components/loyalty/PacchettiAdmin.tsx
  └── Aggiungere: sezione "Invia via WhatsApp"
  └── Aggiungere: select filtri (Tutti/VIP/VIP 3+)
  └── Aggiungere: preview template
  └── Aggiungere: bottone invio con rate limiting

src/hooks/use-loyalty.ts o nuovo use-whatsapp-marketing.ts
  └── Aggiungere: hook per invio WhatsApp selettivo

src-tauri/src/commands/
  └── Aggiungere: comando Tauri per invio WhatsApp pacchetti

# DA MODIFICARE (Task 2 - Voice Greeting)
voice-agent/src/main.py o config.py
  └── Modificare: caricare nome_attivita da DB all'avvio
  └── Modificare: usare nome_attivita in tutti i greeting
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

# 3. Test Rust (iMac)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && export PATH='/Users/gianlucadistasi/.cargo/bin:$PATH' && cargo test --lib"

# 4. Build FINALE (SOLO a fine sviluppo, iMac)
# ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && export PATH='/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:$PATH' && npm run tauri build"
```

---

## 💬 PROMPT PER RIPARTENZA

Copia e incolla questo prompt:

```
Ciao, sono il CTO di FLUXION. Proseguiamo lo sviluppo.

VISIONE (leggere CLAUDE.md sezione "I 3 PILASTRI"):
I 3 pilastri (Comunicazione, Marketing, Gestione) devono essere PERFETTI.
Sono il cuore del prodotto e il vantaggio competitivo per le PMI.

STATO ATTUALE:
- Comunicazione: 90% (Voice OK, WhatsApp base OK, manca invio pacchetti)
- Marketing: 80% (Loyalty OK, pacchetti OK, manca invio WhatsApp selettivo)
- Gestione: 95% (3 schede complete, 5 placeholder)

DA COMPLETARE PRIORITARIO:
1. WhatsApp Pacchetti Selettivo (da integrare in PacchettiAdmin.tsx)
   - Filtri: Tutti/VIP/VIP 3+ stelle
   - Template con nome_attivita
   - Rate limiting 60 msg/ora

2. Voice Agent Greeting Dinamico (usare nome_attivita da DB)

3. E2E Testing → Build Finale v0.8.0

FILE RIFERIMENTO:
- CLAUDE.md (I 3 pilastri, visione prodotto)
- PRD-FLUXION-COMPLETE.md (Sezione 3.6 Loyalty)

AMBIENTE:
- MacBook: /Volumes/MontereyT7/FLUXION (dev)
- iMac: /Volumes/MacSSD - Dati/fluxion (build, solo a fine)
- Repo: lukeeterna/fluxion-desktop

Procedi con WhatsApp Pacchetti Selettivo.
```

---

## ✅ CHECKLIST CHIUSURA SESSIONE

### Prima di chiudere:
- [ ] I 3 pilastri funzionano correttamente?
- [ ] WhatsApp Pacchetti invia con filtri corretti?
- [ ] Voice Agent usa nome attività?
- [ ] Test passano (54/54 Rust, TypeScript clean)?
- [ ] Commit e push

### Build Finale (solo quando tutto OK):
- [ ] E2E tests passano
- [ ] Build su iMac OK
- [ ] Tag v0.8.0
- [ ] Test su macOS e Windows

---

*Prompt generato: 2026-02-06*
*Versione: 2.0 (Allineato con Visione 3 Pilastri)*
*Stato: Pronto per ripartenza*
