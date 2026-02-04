# FLUXION - Session Context Save
## Data: 2026-02-04
## Contesto: 64% - Reset Richiesto

---

## 📁 FILE CREATI/MODIFICATI IN QUESTA SESSIONE

### 1. Voice Agent - Implementazione Core (Python)
| File | Path | Scopo |
|------|------|-------|
| `vertical_schemas.py` | `voice-agent/src/` | Schede cliente per tutti i settori (anamnesi, tecniche) |
| `booking_manager.py` | `voice-agent/src/` | CRUD prenotazioni + VIP + lista d'attesa |
| `service_resolver.py` | `voice-agent/src/` | Fuzzy matching testo → ID database |
| `booking_orchestrator.py` | `voice-agent/src/` | Orchestratore completo (stati + resolver + WhatsApp) |
| `test_booking_e2e_complete.py` | `voice-agent/tests/` | Test E2E per CI/CD |
| `IMPLEMENTATION_SUMMARY.md` | `voice-agent/` | Documentazione implementazione |

### 2. Database - Migration SQL
| File | Path | Scopo |
|------|------|-------|
| `019_schede_clienti_verticali.sql` | `src-tauri/migrations/` | Tabelle schede per ogni settore |

### 3. Frontend - TypeScript
| File | Path | Scopo |
|------|------|-------|
| `setup-verticals.ts` | `src/types/` | Macro/micro categorie + mapping schede |

### 4. Documentazione
| File | Path | Scopo |
|------|------|-------|
| `MOCKUP-SCHEDE-CLIENTE.md` | `docs/` | Mockup UI schede cliente per tutti i settori |

---

## 🎯 OBIETTIVO PRINCIPALE DEL PROGETTO

Implementare **schede cliente verticali** che si attivano automaticamente in base alla **micro-categoria** selezionata nel setup:

```
Setup: seleziona "odontoiatra" → Scheda cliente mostra odontogramma, trattamenti dentali
Setup: seleziona "fisioterapia" → Scheda cliente mostra VAS, sedute, zone trattate
Setup: seleziona "meccanico" → Scheda cliente mostra veicoli, tagliandi, km
```

---

## 🏗️ ARCHITETTURA IMPLEMENTATA

### Flusso Dati
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│   Setup     │ →  │  Macro/Micro │ →  │   Voice     │ →  │  WhatsApp│
│  Wizard     │    │  Categoria   │    │   Agent     │    │  Notific │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘
                          ↓
                   ┌──────────────┐
                   │ Scheda Cliente│
                   │   Specifica   │
                   │  (odontoiatra│
                   │ fisioterapia,│
                   │   meccanico) │
                   └──────────────┘
```

### Componenti
1. **Booking State Machine** → Gestisce flusso conversazionale
2. **Service Resolver** → Fuzzy match servizi/operatori
3. **Booking Manager** → CRUD + VIP tier + lista d'attesa prioritaria
4. **Orchestrator** → Coordina tutto + WhatsApp

---

## 📋 SETTORI VERTICALI SUPPORTATI

### Medico
| Micro Categoria | Scheda Attivata |
|-----------------|-----------------|
| odontoiatra | schede_odontoiatriche |
| fisioterapia | schede_fisioterapia |
| osteopata | schede_fisioterapia |
| podologo | schede_fisioterapia |
| psicologo | schede_base |
| nutrizionista | schede_base |

### Beauty
| Micro Categoria | Scheda Attivata |
|-----------------|-----------------|
| estetista_viso | schede_estetica |
| estetista_corpo | schede_estetica |
| nail_specialist | schede_estetica |
| epilazione_laser | schede_estetica |
| spa | schede_estetica |

### Hair
| Micro Categoria | Scheda Attivata |
|-----------------|-----------------|
| salone_donna | schede_parrucchiere |
| barbiere | schede_parrucchiere |
| salone_unisex | schede_parrucchiere |
| extension_specialist | schede_parrucchiere |
| tricologo | schede_parrucchiere |

### Auto
| Micro Categoria | Scheda Attivata |
|-----------------|-----------------|
| officina_meccanica | schede_veicoli |
| carrozzeria | schede_carrozzeria |
| elettrauto | schede_veicoli |
| gommista | schede_veicoli |

---

## ⚙️ CONFIGURAZIONE SETUP

### Chiavi Impostazioni da Aggiungere
```sql
INSERT INTO impostazioni (chiave, valore) VALUES
('macro_categoria', 'medico'),
('micro_categoria', 'odontoiatra');
```

### Tipo Setup Attuale
```typescript
// src/types/setup.ts (ESISTENTE)
categoria_attivita: 'salone' | 'auto' | 'wellness' | 'medical' | 'altro'

// NUOVO: src/types/setup-verticals.ts
macro_categoria: 'medico' | 'beauty' | 'hair' | 'auto' | 'wellness' | 'professionale'
micro_categoria: string  // dipende dalla macro
```

---

## 🎨 MOCKUP UI - Schede Cliente

Vedi: `docs/MOCKUP-SCHEDE-CLIENTE.md`

Contiene mockup visivi per:
- 🏥 Scheda Odontoiatrica (odontogramma, trattamenti)
- 🏥 Scheda Fisioterapia (VAS, sedute, zone)
- 💅 Scheda Estetica (fototipo, trattamenti)
- 💇 Scheda Parrucchiere (colore, storia chimica)
- 🚗 Scheda Veicoli (storico, tagliandi)
- 🎨 Scheda Carrozzeria (danni, preventivi)

---

## 🔧 PROSSIMI PASSI (DA FARE NELLA NUOVA SESSIONE)

### Priorità 1: Setup Wizard React
- [ ] Modificare `SetupWizard.tsx` per includere selezione macro/micro
- [ ] Creare step intermedio "Seleziona Tipo Attività"
- [ ] Salvare `macro_categoria` e `micro_categoria` in impostazioni

### Priorità 2: Componenti Schede Cliente
- [ ] Creare `SchedaOdontoiatrica.tsx` con odontogramma
- [ ] Creare `SchedaFisioterapia.tsx` con scale VAS
- [ ] Creare `SchedaEstetica.tsx` con fototipo
- [ ] Creare `SchedaParrucchiere.tsx` con storia colore
- [ ] Creare `SchedaVeicoli.tsx` con storico interventi
- [ ] Creare `SchedaCarrozzeria.tsx` con danni/foto

### Priorità 3: API Rust (Tauri)
- [ ] Comandi CRUD per ogni tipo di scheda
- [ ] Query per recuperare scheda corretta in base a micro_categoria
- [ ] Endpoint per lista d'attesa VIP

### Priorità 4: Integrazione
- [ ] Nella pagina cliente, mostrare scheda corretta in base a impostazioni
- [ ] Se micro_categoria = "odontoiatra" → mostra SchedaOdontoiatrica
- [ ] Se micro_categoria = "fisioterapia" → mostra SchedaFisioterapia

---

## 🧪 TEST DA ESEGUIRE

```bash
# Sul MacBook (sintassi)
cd voice-agent
python -m py_compile src/*.py

# Sull'iMac (completo)
cd voice-agent
python -m pytest tests/test_booking_e2e_complete.py -v
```

---

## 📦 COMMIT GIT DA RECUPERARE

Branch: `feat/workflow-tools`
Commit: `59eb9db` - "feat(voice-agent): implementazione completa schede verticali + booking manager + orchestrator"

```bash
# Sull'iMac
git pull origin feat/workflow-tools
```

---

## 💡 NOTE PER LA PROSSIMA SESSIONE

1. **Non modificare** le tabelle esistenti (`clienti`, `appuntamenti`, etc.)
2. **Solo aggiungere** nuove tabelle e nuovi campi in `impostazioni`
3. **Mantenere** compatibilità con codice esistente
4. **Testare** sempre sia sul MacBook (sintassi) che sull'iMac (completo)

---

## 🔗 FILE CHIAVE DA LEGGERE ALL'INIZIO

1. `docs/MOCKUP-SCHEDE-CLIENTE.md` - Visione UI completa
2. `src-tauri/migrations/019_schede_clienti_verticali.sql` - Schema DB
3. `src/types/setup-verticals.ts` - Tipi TypeScript
4. `voice-agent/src/booking_orchestrator.py` - Logica Voice Agent

---

## ❓ DOMANDE APERTE

1. Qual è la priorità: Setup Wizard o Componenti Schede?
2. Quale settore implementare per primo? (consigliato: odontoiatra)
3. Sull'iMac: DB SQLite o PostgreSQL?

---

**Salva questo file e inizia nuova sessione con: "@load SESSION-CONTEXT-SAVE.md"**
