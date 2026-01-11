# Sessione: Voice Agent DB Integration Complete

**Data**: 2026-01-11T14:00:00
**Fase**: 7 (Voice Agent + WhatsApp)
**Agenti**: rust-backend, voice-engineer

---

## Obiettivo
Implementare integrazione completa Voice Agent con database per:
- Preferenza operatore con disponibilità
- Proposta alternative con "doti positive"
- Registrazione nuovo cliente via conversazione
- Lista d'attesa con priorità VIP
- Disambiguazione cliente con data_nascita

---

## Implementazioni Completate

### 1. Migrations (Rust/SQLite)

#### Migration 012: Operatori Voice Agent Enhancement
```sql
ALTER TABLE operatori ADD COLUMN specializzazioni TEXT DEFAULT '[]';
ALTER TABLE operatori ADD COLUMN descrizione_positiva TEXT;
ALTER TABLE operatori ADD COLUMN anni_esperienza INTEGER DEFAULT 0;
```

#### Migration 013: Waitlist con Priorità VIP
```sql
CREATE TABLE waitlist (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL,
    servizio TEXT NOT NULL,
    data_preferita TEXT,
    ora_preferita TEXT,
    operatore_preferito TEXT,
    priorita TEXT DEFAULT 'normale', -- 'normale', 'vip', 'urgente'
    priorita_valore INTEGER DEFAULT 10, -- 10=normale, 50=vip, 100=urgente
    ...
);
```

### 2. HTTP Bridge Endpoints (Rust/Axum)

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/operatori/list` | GET | Lista operatori con specializzazioni e descrizioni positive |
| `/api/operatori/disponibilita` | POST | Verifica disponibilità operatore + alternative |
| `/api/clienti/create` | POST | Crea nuovo cliente da Voice/WA |
| `/api/waitlist/add` | POST | Aggiungi a waitlist con priorità VIP |

**Miglioramenti endpoint esistenti:**
- `/api/clienti/search` - Ora supporta `data_nascita` per disambiguazione
- `/api/appuntamenti/create` - Ora supporta `operatore_id` preference

### 3. Voice Agent Pipeline (Python)

**Nuovi metodi:**
- `get_operatori()` - Lista operatori con specializzazioni
- `check_operatore_disponibilita()` - Disponibilità + alternative
- `create_client()` - Registrazione nuovo cliente
- `add_to_waitlist()` - Waitlist con priorità

**Flow aggiornato:**
1. Estrae preferenza operatore dal testo ("con Maria", "preferisco Laura")
2. Valida operatore contro DB
3. Verifica disponibilità operatore per data/ora
4. Se non disponibile, prepara alternative con descrizioni positive
5. LLM riceve context notes per suggerire alternative
6. Crea appuntamento con operatore_id

---

## Commits Pushati

| Hash | Descrizione |
|------|-------------|
| `38f2e0c` | feat(voice): add operator voice agent fields (migration 012) |
| `ba0f624` | feat(voice): add Voice Agent DB integration endpoints |
| `03036a9` | feat(voice): integrate DB endpoints in Voice Agent pipeline |

---

## File Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| src-tauri/migrations/012_operatori_voice_agent.sql | Nuovo | Campi operatori |
| src-tauri/migrations/013_waitlist.sql | Nuovo | Tabella waitlist |
| src-tauri/src/lib.rs | Mod | Migration runners |
| src-tauri/src/http_bridge.rs | Mod | 6 nuovi endpoints |
| voice-agent/src/pipeline.py | Mod | Integrazione completa DB |

---

## Test da Eseguire su iMac

```bash
# 1. Pull e rebuild
cd /Volumes/MacSSD\ -\ Dati/fluxion
git pull
npm run tauri dev

# 2. Test operatori list
curl http://127.0.0.1:3001/api/operatori/list

# 3. Test disponibilità operatore
curl -X POST http://127.0.0.1:3001/api/operatori/disponibilita \
  -H "Content-Type: application/json" \
  -d '{"operatore_id": "op-paola", "data": "2026-01-13"}'

# 4. Test Voice Agent con preferenza operatore
# Dire: "Vorrei prenotare un taglio con Paola per martedì"
# Voice Agent dovrebbe verificare disponibilità e proporre alternative se necessario
```

---

## API Response Examples

### GET /api/operatori/list
```json
[
  {
    "id": "op-paola",
    "nome": "Paola",
    "cognome": "Verdi",
    "specializzazioni": ["taglio", "colore", "piega"],
    "descrizione_positiva": "La titolare! Esperta in ogni tipo di trattamento",
    "anni_esperienza": 20
  }
]
```

### POST /api/operatori/disponibilita (non disponibile)
```json
{
  "operatore_id": "op-paola",
  "data": "2026-01-13",
  "disponibile": false,
  "slots": [],
  "alternative_operators": [
    {
      "id": "op-giulia",
      "nome": "Giulia",
      "descrizione_positiva": "Artista del colore e delle extension",
      "anni_esperienza": 5,
      "slots_disponibili": ["09:00", "10:00", "14:00"]
    }
  ]
}
```

---

## Prossimi Passi

1. Test su iMac con rebuild Tauri
2. Test conversazione Voice Agent con preferenza operatore
3. Test registrazione nuovo cliente via voce
4. Aggiornare UI per mostrare operatori con specializzazioni

