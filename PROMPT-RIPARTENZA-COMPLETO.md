# PROMPT RIPARTENZA - FLUXION Voice Agent & Schede Verticali

**Usa questo prompt all'inizio di una nuova sessione con Kimi/Claude per ricostruire il contesto completo.**

---

## 🎯 CONTESTO PROGETTO

Sto sviluppando **FLUXION**, un sistema di gestione appuntamenti per PMI italiane con **Voice Agent integrato** e **schede cliente verticali** specifiche per settore.

### Architettura Stack
- **Backend Voice Agent**: Python (Layer 0 Regex, State Machine, Booking Manager)
- **Frontend**: React + TypeScript + Tauri (Rust)
- **Database**: SQLite (migrations in `src-tauri/migrations/`)
- **Comunicazione**: WhatsApp Business API

---

## 📁 FILE ESISTENTI (Già Creati)

### Voice Agent (Python)
```
voice-agent/src/
├── italian_regex.py           # ✅ Layer 0 - Pattern italiani
├── intent_classifier.py       # ✅ Layer 1 - Classificazione intent
├── entity_extractor.py        # ✅ Layer 2 - Estrazione entità
├── booking_state_machine.py   # ✅ Layer 2 - Macchina stati
├── vertical_schemas.py        # ✅ Schede cliente (dataclass)
├── booking_manager.py         # ✅ CRUD + VIP + Waitlist
├── service_resolver.py        # ✅ Fuzzy matching DB
├── booking_orchestrator.py    # ✅ Orchestratore completo
├── groq_nlu.py                # ✅ Layer 4 - Fallback LLM
├── whatsapp.py                # ✅ Integrazione WhatsApp
└── tests/
    └── test_booking_e2e_complete.py  # ✅ Test E2E
```

### Database (SQL)
```
src-tauri/migrations/
├── 001_init.sql               # ✅ Tabelle base (clienti, appuntamenti, operatori)
├── 011_voice_agent.sql        # ✅ Config Voice Agent
├── 012_operatori_voice_agent.sql  # ✅ Operatori + specializzazioni
├── 013_waitlist.sql           # ✅ Lista d'attesa VIP
└── 019_schede_clienti_verticali.sql  # ✅ NUOVO - Schede verticali
```

### Frontend (TypeScript)
```
src/types/
├── setup.ts                   # ✅ Setup esistente (categoria_attivita)
├── cliente.ts                 # ✅ Tipo Cliente esistente
└── setup-verticals.ts         # ✅ NUOVO - Macro/Micro categorie
```

### Documentazione
```
docs/
├── MOCKUP-SCHEDE-CLIENTE.md   # ✅ Mockup UI complete
└── VERTICALS-FINAL-6.md       # ✅ Ricerca settori

voice-agent/
└── IMPLEMENTATION_SUMMARY.md  # ✅ Riepilogo implementazione

SESSION-CONTEXT-SAVE.md        # ✅ Checkpoint sessione
```

---

## 🏗️ OBIETTIVO PRINCIPALE

Implementare **schede cliente dinamiche** che si attivano in base alla **micro-categoria** selezionata nel setup:

```
Flusso:
1. Utente installa app
2. Setup Wizard → seleziona "odontoiatra" 
3. App si configura con servizi dentali
4. Scheda cliente mostra ODONTOGRAMMA, trattamenti, etc.

vs

2. Setup Wizard → seleziona "fisioterapia"
3. App si configura con servizi riabilitativi  
4. Scheda cliente mostra VAS, scale valutazione, sedute
```

---

## 📊 SETTORI VERTICALI SUPPORTATI

### Medico
| Macro | Micro | Scheda DB | Componente React |
|-------|-------|-----------|------------------|
| medico | odontoiatra | schede_odontoiatriche | SchedaOdontoiatrica |
| medico | fisioterapia | schede_fisioterapia | SchedaFisioterapia |
| medico | osteopata | schede_fisioterapia | SchedaFisioterapia |
| medico | podologo | schede_fisioterapia | SchedaFisioterapia |
| medico | psicologo | - (base) | SchedaBase |
| medico | nutrizionista | - (base) | SchedaBase |

### Beauty
| Macro | Micro | Scheda DB | Componente React |
|-------|-------|-----------|------------------|
| beauty | estetista_viso | schede_estetica | SchedaEstetica |
| beauty | estetista_corpo | schede_estetica | SchedaEstetica |
| beauty | nail_specialist | schede_estetica | SchedaEstetica |
| beauty | epilazione_laser | schede_estetica | SchedaEstetica |
| beauty | spa | schede_estetica | SchedaEstetica |

### Hair
| Macro | Micro | Scheda DB | Componente React |
|-------|-------|-----------|------------------|
| hair | salone_donna | schede_parrucchiere | SchedaParrucchiere |
| hair | barbiere | schede_parrucchiere | SchedaParrucchiere |
| hair | salone_unisex | schede_parrucchiere | SchedaParrucchiere |
| hair | extension_specialist | schede_parrucchiere | SchedaParrucchiere |
| hair | tricologo | schede_parrucchiere | SchedaParrucchiere |

### Auto
| Macro | Micro | Scheda DB | Componente React |
|-------|-------|-----------|------------------|
| auto | officina_meccanica | schede_veicoli | SchedaVeicoli |
| auto | carrozzeria | schede_carrozzeria | SchedaCarrozzeria |
| auto | elettrauto | schede_veicoli | SchedaVeicoli |
| auto | gommista | schede_veicoli | SchedaVeicoli |

---

## 🔧 STRUTTURA DATABASE (Migration 019)

### Tabelle Schede

```sql
-- Odontoiatrica
schede_odontoiatriche {
  id, cliente_id,
  odontogramma TEXT,           -- JSON: {"11": {"stato": "sano"}, ...}
  prima_visita, ultima_visita,
  spazzolino, filo_interdentale, collutorio,
  allergia_lattice, allergia_anestesia,
  otturazioni, estrazioni, devitalizzazioni, corone, impianti,  -- JSON arrays
  ortodonzia_in_corso, tipo_apparecchio,
  note_cliniche
}

-- Fisioterapia
schede_fisioterapia {
  id, cliente_id,
  motivo_primo_accesso,
  data_inizio_terapia, data_fine_terapia,
  diagnosi_medica, diagnosi_fisioterapica,
  zona_principale, zone_secondarie,
  valutazione_iniziale, scale_valutazione,  -- JSON
  numero_sedute_prescritte, frequenza_settimanale,
  sedute_effettuate,  -- JSON array
  esito_trattamento,
  controindicazioni
}

-- Estetica
schede_estetica {
  id, cliente_id,
  fototipo (1-6), tipo_pelle,
  allergie_prodotti, allergie_profumi, allergie_henne,
  trattamenti_precedenti,  -- JSON
  ultima_depilazione, metodo_depilazione,
  unghie_naturali, problematiche_unghie,
  problematiche_viso, routine_skincare,
  peso_attuale, obiettivo,
  gravidanza, allattamento, patologie_attive
}

-- Parrucchiere
schede_parrucchiere {
  id, cliente_id,
  tipo_capello, porosita, lunghezza_attuale,
  base_naturale, colore_attuale,
  colorazioni_precedenti, decolorazioni, permanente, stirature_chimiche,
  allergia_tinta, allergia_ammoniaca, test_pelle_eseguito, data_test_pelle,
  servizi_abituali, frequenza_taglio, frequenza_colore,
  prodotti_casa, preferenze_colore, non_vuole
}

-- Veicoli
schede_veicoli {
  id, cliente_id,
  targa, marca, modello, anno, alimentazione, cilindrata, kw, telaio,
  ultima_revisione, scadenza_revisione,
  km_attuali, km_ultimo_tagliando,
  misura_gomme, tipo_gomme,
  preferenza_ricambi, note_veicolo,
  interventi,  -- JSON
  is_default
}

-- Carrozzeria
schede_carrozzeria {
  id, cliente_id, veicolo_id,
  tipo_danno, posizione_danno, entita_danno, descrizione_danno,
  foto_pre, foto_post,  -- JSON arrays URL
  preventivo_numero, importo_preventivo, approvato,
  data_ingresso, data_consegna_prevista, data_consegna_effettiva,
  lavorazioni, verniciatura, codice_colore,
  sinistro_assicurativo, compagnia, numero_sinistro,
  stato
}
```

---

## 🎨 MOCKUP UI (da docs/MOCKUP-SCHEE-CLIENTE.md)

### Scheda Odontoiatrica
- Header: Nome cliente + telefono + icona 🏥
- Sezione ODONTOGRAMMA: Griglia denti 18-11 | 21-28, 48-41 | 31-38
- Legenda: 🟢 Sano 🟡 Otturazione 🔴 Dente mancante
- Sezione STORIA CLINICA: Prima/ultima visita, abitudini igiene
- Sezione ALLERGIE: Check lattice, anestesia
- Tabella TRATTAMENTI: Data, tipo, dente

### Scheda Fisioterapia
- Header: Nome cliente + icona 🏥
- Sezione MOTIVO: Dolore lombare, data inizio/fine
- Sezione ZONE: 🔴 Zona principale, 🟡 Zone secondarie
- Tabella VALUTAZIONI: Scala | Iniziale | Attuale | Obiettivo
- Tabella SEDUTE: Data | Trattamento | Note
- Progress bar: Sedute effettuate / Totali

### Scheda Veicoli
- Header: Nome cliente + icona 🚗
- Card VEICOLO PRINCIPALE: Targa, marca, modello, anno, km
- Sezione TAGLIANDI: Ultimo, prossimo, revisione
- Sezione GOMME: Misura, tipo, ultimo cambio
- Tabella STORICO: Data | Intervento | KM | Prezzo

---

## 🧩 COMPONENTI DA IMPLEMENTARE

### 1. Setup Wizard (Modifica)
**File**: `src/components/setup/SetupWizard.tsx`

Aggiungere Step 2.5:
```
Seleziona Macro Categoria:
[ ] 🏥 Sanitario/Medico
[ ] 💅 Bellezza/Estetica  
[ ] 💇 Parrucchiere/Barbiere
[ ] 🚗 Automotive
...

Se selezionato "Sanitario", mostra:
Seleziona Specializzazione:
[ ] Odontoiatra
[ ] Fisioterapia
[ ] Osteopata
...
```

Salvare in impostazioni:
```typescript
await saveConfig({
  ...baseConfig,
  macro_categoria: 'medico',
  micro_categoria: 'odontoiatra'
});
```

### 2. Componenti Schede Cliente (Nuovi)

**Cartella**: `src/components/schede-cliente/`

```typescript
// SchedaOdontoiatrica.tsx
interface Props {
  clienteId: string;
}

export function SchedaOdontoiatrica({ clienteId }: Props) {
  const { data: scheda } = useSchedaOdontoiatrica(clienteId);
  
  return (
    <div className="scheda-odontoiatrica">
      <Odontogramma data={scheda?.odontogramma} />
      <StoriaClinica 
        primaVisita={scheda?.prima_visita}
        ultimeVisita={scheda?.ultima_visita}
      />
      <TabellaTrattamenti trattamenti={scheda?.otturazioni} />
    </div>
  );
}
```

### 3. Componente Wrapper (Switcher)

**File**: `src/components/schede-cliente/SchedaClienteDynamic.tsx`

```typescript
export function SchedaClienteDynamic({ clienteId }: { clienteId: string }) {
  const { data: config } = useSetupConfig();
  
  const schedaComponent = {
    'odontoiatra': SchedaOdontoiatrica,
    'fisioterapia': SchedaFisioterapia,
    'estetista_viso': SchedaEstetica,
    'salone_donna': SchedaParrucchiere,
    'officina_meccanica': SchedaVeicoli,
    'carrozzeria': SchedaCarrozzeria,
  }[config?.micro_categoria];
  
  if (!schedaComponent) return <SchedaBase clienteId={clienteId} />;
  
  const Component = schedaComponent;
  return <Component clienteId={clienteId} />;
}
```

### 4. API Rust (Tauri)

**File**: `src-tauri/src/commands/schede_cliente.rs`

```rust
#[tauri::command]
async fn get_scheda_odontoiatrica(
    cliente_id: String,
    pool: State<'_, SqlitePool>
) -> Result<Option<SchedaOdontoiatrica>, String> {
    sqlx::query_as::<_, SchedaOdontoiatrica>(
        "SELECT * FROM schede_odontoiatriche WHERE cliente_id = ?"
    )
    .bind(&cliente_id)
    .fetch_optional(&*pool)
    .await
    .map_err(|e| e.to_string())
}

#[tauri::command]
async fn upsert_scheda_odontoiatrica(
    scheda: SchedaOdontoiatricaInput,
    pool: State<'_, SqlitePool>
) -> Result<String, String> {
    // INSERT OR REPLACE
}
```

---

## 🔄 FLUSSO DATI COMPLETO

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   SETUP WIZARD  │────▶│  Impostazioni    │────▶│  Voice Agent    │
│                 │     │  DB (SQLite)     │     │  Configurazione │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Macro/Micro    │     │  Pagina Cliente  │◀────│  Prenotazione   │
│  Categoria      │────▶│                  │     │  Voice/WhatsApp │
│  selezionata    │     │  SchedaDynamic   │────▶│                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                    ┌─────────┴─────────┐
                    ▼                   ▼
           ┌──────────────┐    ┌──────────────┐
           │ SchedaOdonto │    │ SchedaFisio  │
           │   (odontoiatra)   │ (fisioterapia)   │
           └──────────────┘    └──────────────┘
```

---

## ✅ CHECKLIST IMPLEMENTAZIONE

### Fase 1: Setup
- [ ] Modificare `SetupWizard.tsx` aggiungendo step macro/micro
- [ ] Creare componente `MacroCategoriaSelect.tsx`
- [ ] Creare componente `MicroCategoriaSelect.tsx` (dipendente dalla macro)
- [ ] Salvare macro_categoria e micro_categoria in impostazioni
- [ ] Aggiornare hook `useSetupConfig()` per includere nuovi campi

### Fase 2: Schede Cliente (scegli 1 per iniziare)
- [ ] Creare struttura cartella `src/components/schede-cliente/`
- [ ] Implementare **SchedaOdontoiatrica.tsx** (consigliata per iniziare)
- [ ] Sottocomponenti: Odontogramma, StoriaClinica, TabellaTrattamenti
- [ ] Creare hook `useSchedaOdontoiatrica(clienteId)`
- [ ] Testare visualizzazione dati mock

### Fase 3: API Rust
- [ ] Creare `src-tauri/src/commands/schede_cliente.rs`
- [ ] Comandi: get, create, update per scheda odontoiatrica
- [ ] Aggiungere comandi in `lib.rs`
- [ ] Testare con `cargo tauri dev`

### Fase 4: Integrazione
- [ ] Creare `SchedaClienteDynamic.tsx` (switcher)
- [ ] Modificare pagina cliente esistente per usare SchedaClienteDynamic
- [ ] Verificare che cambi scheda in base a impostazioni

### Fase 5: Altri Settori
- [ ] SchedaFisioterapia
- [ ] SchedaEstetica
- [ ] SchedaParrucchiere
- [ ] SchedaVeicoli
- [ ] SchedaCarrozzeria

### Fase 6: Voice Agent
- [ ] Verificare che `vertical_schemas.py` sia compatibile
- [ ] Testare flusso prenotazione con nuove schede
- [ ] Integrare lista d'attesa VIP con frontend

---

## 🎨 DESIGN SYSTEM

### Colori per Settore
```css
--medico-primary: #ef4444;      /* Rosso */
--medico-secondary: #fee2e2;

--beauty-primary: #ec4899;      /* Rosa */
--beauty-secondary: #fce7f3;

--hair-primary: #8b5cf6;        /* Viola */
--hair-secondary: #ede9fe;

--auto-primary: #3b82f6;        /* Blu */
--auto-secondary: #dbeafe;

--wellness-primary: #10b981;    /* Verde */
--wellness-secondary: #d1fae5;
```

### Icone
- Medico: `Stethoscope`, `Heart`, `Activity`
- Beauty: `Sparkles`, `Face`, `Hand`
- Hair: `Scissors`, `Brush`, `Sparkles`
- Auto: `Car`, `Wrench`, `Gauge`

---

## 🧪 TEST

### Test Setup
```typescript
// Verifica che macro/micro vengano salvate
describe('Setup Wizard', () => {
  it('dovrebbe salvare macro e micro categoria', async () => {
    await fillSetupForm({
      nome_attivita: 'Studio Dentistico Rossi',
      macro_categoria: 'medico',
      micro_categoria: 'odontoiatra'
    });
    
    const config = await getSetupConfig();
    expect(config.micro_categoria).toBe('odontoiatra');
  });
});
```

### Test Schede
```typescript
describe('SchedaOdontoiatrica', () => {
  it('dovrebbe mostrare odontogramma', () => {
    render(<SchedaOdontoiatrica clienteId="123" />);
    expect(screen.getByText('Odontogramma')).toBeInTheDocument();
  });
});
```

---

## 📚 REFERENZE

### File da Leggere
1. `docs/MOCKUP-SCHEDE-CLIENTE.md` - Visione UI
2. `src-tauri/migrations/019_schede_clienti_verticali.sql` - Schema DB
3. `src/types/setup-verticals.ts` - Tipi categorie
4. `voice-agent/src/vertical_schemas.py` - Dataclass Python

### Comandi Utili
```bash
# Test sintassi Python
cd voice-agent && python -m py_compile src/*.py

# Test TypeScript
cd /Volumes/MontereyT7/FLUXION && npm run type-check

# Dev Tauri
cd src-tauri && cargo tauri dev

# Test E2E
cd voice-agent && python -m pytest tests/ -v
```

---

## 💡 NOTE CRITICHE

1. **NON modificare** tabelle esistenti (`clienti`, `appuntamenti`)
2. **SOLO aggiungere** nuove tabelle schede_*
3. **Mantenere** compatibilità con setup esistente
4. **Usare** `categoria_attivita` come fallback se `micro_categoria` non settata
5. **Priorità**: Implementare 1 scheda completa (odontoiatra) prima delle altre

---

## ❓ DOMANDE DA RISOLVERE

1. Qual è il primo settore da implementare? (Consiglio: odontoiatra)
2. Sull'iMac hai già fatto `git pull`?
3. Preferisci iniziare dal Setup Wizard o dalle Schede?
4. Hai bisogno dei comandi Rust subito o possiamo usare mock API?

---

**INIZIA LA SESSIONE CON: "Sono pronto, iniziamo con [odontoiatra/setup/...]"**
