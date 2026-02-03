# 🤖 FLUXION Agent Hierarchy

Sistema di orchestrazione gerarchica per sviluppo FLUXION basato su **Kimi Code CLI Task API**.

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────────────┐
│                     MASTER ORCHESTRATOR (L0)                     │
│                     Top-level coordinator                        │
└─────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ GSD Planner (L1)│  │GSD Executor (L1)│  │GSD Verifier (L1)│
│                 │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│Voice Orchestrator│ │Backend Orchestrator│ │Frontend Orchestrator│
│    (L1)       │    │    (L1)       │    │    (L1)       │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
   ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
   ▼    ▼    ▼          ▼    ▼    ▼          ▼    ▼    ▼
 NLU  TTS  Pipeline   Rust SQLite API     React UI  State
(L2)  (L2)   (L2)     (L2)  (L2)  (L2)    (L2) (L2)  (L2)
```

## 📁 Struttura

```
.kimi/
├── README.md                    # Questo file
├── AGENT-HIERARCHY.md           # Documentazione completa
├── config.json                  # Configurazione agenti
│
├── orchestrators/               # Livello 1
│   ├── master-orchestrator.md   # Entry point
│   ├── gsd-planner.md           # Pianificazione
│   ├── gsd-executor.md          # Esecuzione
│   ├── gsd-verifier.md          # Verifica
│   ├── voice-orchestrator.md    # Dominio Voice
│   ├── backend-orchestrator.md  # Dominio Backend
│   ├── frontend-orchestrator.md # Dominio Frontend
│   └── ...
│
├── specialists/                 # Livello 2
│   ├── voice/
│   │   ├── nlu-specialist.md
│   │   ├── tts-specialist.md
│   │   └── pipeline-specialist.md
│   ├── backend/
│   │   ├── rust-specialist.md
│   │   └── sqlite-specialist.md
│   └── frontend/
│       ├── react-specialist.md
│       └── ui-specialist.md
│
├── workers/                     # Livello 3
│   └── (atomici, creati on-demand)
│
└── protocols/                   # Protocolli
    └── agent-message.json       # Schema messaggi
```

## 🚀 Quick Start

### Come Utente

```bash
# Kimi usa automaticamente la gerarchia quando necessario
kimi "Implementa voice booking nel calendario"
```

### Come Sviluppatore

```bash
# Crea nuovo orchestrator
cp templates/orchestrator.md orchestrators/mio-orchestrator.md

# Crea nuovo specialist
cp templates/specialist.md specialists/mio-dominio/mio-specialist.md

# Aggiorna config.json
vim config.json
```

## 🔄 Workflow Esempio

### Richiesta Utente
```
"Aggiungi supporto per 'modifica orario' nel voice agent"
```

### Esecuzione Gerarchica

```
1. MASTER ORCHESTRATOR
   └─ Decomposizione:
      - NLU: Nuovo intent "modifica_orario"
      - Conversation: Flow modifica
      - Backend: API per modifica
      
2. Spawn Parallelo
   ├─▶ Voice Orchestrator
   │   ├─▶ NLU Specialist (L2)
   │   │   └─ Modifica italian_regex.py, intent_classifier.py
   │   └─▶ Conversation Specialist (L2)
   │       └─ Modifica booking_state_machine.py
   │
   └─▶ Backend Orchestrator
       └─▶ Rust Specialist (L2)
           └─ Nuovo command modifica_appuntamento
           
3. Verifica
   └─▶ GSD Verifier
       └─ Test integrazione end-to-end
       
4. Report
   └─ Master aggrega risultati
```

## 📊 Confronto Infrastrutture

| Caratteristica | Kimi Task API | GitHub Actions | MCP |
|---------------|---------------|----------------|-----|
| Gerarchia | ✅ Illimitata | ❌ Max 4 | ✅ Illimitata |
| Contesto isolato | ✅ Automatico | ❌ Condiviso | ⚠️ Manuale |
| Parallelo | ✅ Nativo | ✅ Jobs | ❌ No |
| Overhead | ✅ Zero | ❌ Runners | ⚠️ Server |
| Costo | ✅ Gratuito | ❌ Azioni | ⚠️ Hosting |
| **Scelta FLUXION** | ✅ **Questa** | | |

## 🎯 Vantaggi

1. **Contesto Isolato**: Ogni sub-agente ha contesto pulito, no degradation
2. **Parallelo Nativo**: `Promise.all([Task(), Task(), Task()])`
3. **Zero Config**: Usa tool `Task` già disponibile in Kimi
4. **Gerarchia Illimitata**: L0 → L1 → L2 → L3 → ...
5. **Scalabile**: Aggiungi agenti senza modificare infrastruttura

## 📋 Protocollo

### Messaggio Standard

```typescript
{
  from: "master-orchestrator",
  to: "voice-orchestrator",
  level: 0,
  type: "task",
  taskId: "uuid",
  payload: {
    description: "Implement voice booking",
    context: ["file1.py", "file2.rs"],
    acceptanceCriteria: ["..."]
  }
}
```

## 🔧 Configurazione

Modifica `config.json` per aggiungere/rimuovere agenti:

```json
{
  "agents": {
    "level1": {
      "mio-orchestrator": {
        "id": "mio-orchestrator",
        "file": "orchestrators/mio-orchestrator.md",
        "triggers": ["keyword1", "keyword2"]
      }
    }
  }
}
```

## 📝 Convenzioni

### Naming
- Orchestrator: `{domain}-orchestrator.md`
- Specialist: `{focus}-specialist.md`
- Worker: `{task}-worker.md`

### Frontmatter
```yaml
---
id: unique-id
name: Display Name
level: 1
domain: voice
tools: [Task, Read, Write, ...]
---
```

### Contesto Budget
```
L0 (Master):        0-20%   (coordinazione)
L1 (Orchestrator): 20-50%   (pianificazione)
L2 (Specialist):   50-80%   (implementazione)
L3 (Worker):       80-100%  (task atomici)
```

## 🧪 Test

```bash
# Validazione config
npx ajv validate -s protocols/agent-message.json -d config.json

# Test orchestrator (simulato)
kimi --test-orchestrator orchestrators/voice-orchestrator.md
```

## 📚 Documentazione

- [Architettura Completa](AGENT-HIERARCHY.md)
- [Configurazione](config.json)
- [Protocollo Messaggi](protocols/agent-message.json)

## 🏭 Stato Integrazione

| Componente | Stato |
|-----------|-------|
| Master Orchestrator | ✅ Pronto |
| Voice Orchestrator | ✅ Pronto |
| Backend Orchestrator | ✅ Pronto |
| Frontend Orchestrator | ✅ Pronto |
| GSD Planner | 🔄 Da migrare |
| GSD Executor | 🔄 Da migrare |
| GSD Verifier | 🔄 Da migrare |

## 🔄 Migration da .claude/agents

Il sistema esistente in `.claude/agents/` viene gradualmente migrato:

| Esistente | Nuova Posizione | Livello |
|-----------|-----------------|---------|
| `gsd-*.md` | `orchestrators/gsd-*.md` | L1 |
| `voice-engineer.md` | `orchestrators/voice-orchestrator.md` | L1 |
| `rust-backend.md` | `specialists/backend/rust-specialist.md` | L2 |
| `react-frontend.md` | `specialists/frontend/react-specialist.md` | L2 |

---

*Version: 1.0*  
*Created: 2026-02-03*  
*Stack: Kimi Code CLI + FLUXION*
