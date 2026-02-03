# 🤖 FLUXION Agent Hierarchy - Orchestration Infrastructure

## Overview

Sistema di orchestrazione gerarchica per FLUXION basato su **Kimi Code CLI Task API**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MASTER ORCHESTRATOR                            │
│                         (Kimi - User Interaction)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
           ┌────────────┐   ┌────────────┐   ┌────────────┐
           │  PLANNER   │   │  EXECUTOR  │   │  VERIFIER  │
           │   (GSD)    │   │   (GSD)    │   │   (GSD)    │
           └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
                 │                │                │
       ┌─────────┼─────────┐      │       ┌────────┼────────┐
       │         │         │      │       │        │        │
       ▼         ▼         ▼      ▼       ▼        ▼        ▼
   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
   │Domain│ │Domain│ │Domain│ │Task  │ │Test  │ │Review│ │Report│
   │Expert│ │Expert│ │Expert│ │Runner│ │Agent │ │Agent │ │Agent │
   └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
       │         │         │      │       │        │        │
       ▼         ▼         ▼      ▼       ▼        ▼        ▼
   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
   │Sub-  │ │Sub-  │ │Sub-  │ │Sub-  │ │Sub-  │ │Sub-  │ │Sub-  │
   │Agent │ │Agent │ │Agent │ │Agent │ │Agent │ │Agent │ │Agent │
   └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
```

## Livelli Gerarchici

### Level 0: Master Orchestrator
**Riferimento**: `AGENT-HIERARCHY.md` (questo file)

**Responsabilità**:
- Ricevere richieste utente
- Decomposizione iniziale
- Selezione agenti di primo livello
- Coordinamento globale
- Gestione stato progetto

**Decisioni**:
- Quale agente spawnare
- Quando parallelizzare vs sequenzializzare
- Quando fermarsi per verifica umana

---

### Level 1: Domain Orchestrators

#### 1.1 GSD Planner (`orchestrators/gsd-planner.agent.md`)
**Trigger**: Pianificazione nuove feature
**Output**: PLAN.md files

**Sub-agenti**:
- Research Sub-Agent (analisi tecnologie)
- Architecture Sub-Agent (decisioni strutturali)
- Task Breakdown Sub-Agent (decomposizione)

#### 1.2 GSD Executor (`orchestrators/gsd-executor.agent.md`)
**Trigger**: Esecuzione PLAN.md
**Output**: Codice + SUMMARY.md

**Sub-agenti**:
- Code Sub-Agent (implementazione)
- Test Sub-Agent (unit test)
- Fix Sub-Agent (bug fixing)

#### 1.3 GSD Verifier (`orchestrators/gsd-verifier.agent.md`)
**Trigger**: Verifica completamento
**Output**: VERIFICATION.md

**Sub-agenti**:
- Static Analysis Sub-Agent
- Integration Test Sub-Agent
- Coverage Sub-Agent

#### 1.4 Domain Expert Orchestrator
**Trigger**: Task specifici per dominio

| Dominio | Agent | Sub-agenti |
|---------|-------|------------|
| Voice | `voice-orchestrator.agent.md` | NLU, TTS, STT, Pipeline |
| Backend | `backend-orchestrator.agent.md` | Rust, DB, API, Auth |
| Frontend | `frontend-orchestrator.agent.md` | React, UI, State, Forms |
| DevOps | `devops-orchestrator.agent.md` | CI/CD, Deploy, Monitor |
| Data | `data-orchestrator.agent.md` | Migration, Seed, Analytics |

---

### Level 2: Specialist Agents

Ogni Domain Orchestrator può spawnare specialisti:

#### Voice Domain Specialists
```
voice-orchestrator/
├── nlu-specialist.md         # Intent classification, entity extraction
├── tts-specialist.md         # Piper TTS, voice config
├── stt-specialist.md         # Groq Whisper integration
├── pipeline-specialist.md    # Pipecat orchestration
└── conversation-specialist.md # Dialog flow, state machine
```

#### Backend Domain Specialists
```
backend-orchestrator/
├── rust-specialist.md        # Rust code, Tauri commands
├── sqlite-specialist.md      # Schema, migrations, queries
├── api-specialist.md         # REST endpoints, validation
└── auth-specialist.md        # Authentication, authorization
```

#### Frontend Domain Specialists
```
frontend-orchestrator/
├── react-specialist.md       # Components, hooks
├── ui-specialist.md          # shadcn/ui, Tailwind
├── state-specialist.md       # Zustand, TanStack Query
└── form-specialist.md        # React Hook Form, Zod
```

---

### Level 3: Atomic Workers

Specialisti che eseguono task specifici con contesto minimale:

- **Code Generator**: Genera codice da specifiche
- **Code Reviewer**: Analizza codice esistente
- **Test Generator**: Crea test automatici
- **Doc Generator**: Genera documentazione
- **Refactoring Agent**: Applica pattern di refactoring
- **Debug Agent**: Analisi e fix errori

---

## Protocolli di Comunicazione

### Messaggio Standard Tra Livelli

```typescript
interface AgentMessage {
  // Metadati
  from: string;           // ID agent mittente
  to: string;             // ID agent destinatario
  level: number;          // Livello gerarchico
  timestamp: string;      // ISO 8601
  
  // Contenuto
  type: 'task' | 'result' | 'error' | 'question' | 'report';
  taskId: string;         // ID univoco task
  parentTaskId?: string;  // Riferimento task parent
  
  // Payload
  payload: {
    // Per type='task'
    description?: string;
    context?: string[];   // File di riferimento
    acceptanceCriteria?: string[];
    constraints?: string[];
    
    // Per type='result'
    status?: 'success' | 'partial' | 'failure';
    artifacts?: string[]; // File prodotti
    summary?: string;
    nextActions?: string[];
    
    // Per type='error'
    error?: string;
    stackTrace?: string;
    recoverySuggestion?: string;
  };
  
  // Stato
  contextUsage: number;   // % contesto utilizzato
  estimatedProgress: number; // % completamento stimato
}
```

### Esempio: Chain of Spawning

```
User: "Aggiungi voice booking al calendario"
  │
  ▼
Master Orchestrator
  │─ Decomposizione: voice + calendar + integration
  │
  ├─▶ Domain Orchestrator: Voice
  │   │─ Task: Integrazione voice con calendar API
  │   │
  │   ├─▶ Specialist: Pipeline
  │   │   │─ Task: Aggiungere evento calendar in booking_state_machine.py
  │   │   │─ Result: ✅ Codice aggiornato
  │   │
  │   └─▶ Specialist: TTS
  │       │─ Task: Nuovi messaggi per conferma calendar
  │       │─ Result: ✅ Template TTS creati
  │
  ├─▶ Domain Orchestrator: Frontend (Calendar)
  │   │─ Task: Visualizzazione booking voice
  │   │
  │   ├─▶ Specialist: React
  │   │   │─ Task: Componente VoiceBookingIndicator
  │   │   │─ Result: ✅ Componente creato
  │   │
  │   └─▶ Specialist: State
  │       │─ Task: Zustand store per voice events
  │       │─ Result: ✅ Store aggiornato
  │
  └─▶ Domain Orchestrator: Backend
      │─ Task: API calendar integration
      │
      ├─▶ Specialist: Rust
      │   │─ Task: Command Tauri per calendar sync
      │   │─ Result: ✅ Commands implementati
      │
      └─▶ Specialist: SQLite
          │─ Task: Migration per voice_bookings
          │─ Result: ✅ Migration creata

  ▼
Master Orchestrator
  │─ Verifica finale
  │─ Report all'utente
```

---

## Implementazione Kimi Code CLI

### Task API Usage Pattern

```typescript
// Esempio: Master Orchestrator spawns Domain Orchestrators

// Task 1: Voice Domain (parallelo)
const voiceTask = await Task({
  subagent_name: 'voice-orchestrator',
  description: 'Voice calendar integration',
  prompt: `
    PROJECT: FLUXION Voice Agent
    TASK: Integrate voice booking with calendar
    
    CONTEXT:
    - booking_state_machine.py gestisce il flow
    - Voice agent usa Pipecat + Groq
    - Calendar usa React Big Calendar
    
    SUB-TASKS TO DELEGATE:
    1. Pipeline specialist: Aggiornare state machine
    2. TTS specialist: Messaggi conferma calendar
    3. Conversation specialist: Flow calendar query
    
    RETURN FORMAT:
    - Status: success | partial | failure
    - Files modified
    - Integration points
  `
});

// Task 2: Frontend Domain (parallelo)
const frontendTask = await Task({
  subagent_name: 'frontend-orchestrator',
  description: 'Calendar voice UI',
  prompt: `
    PROJECT: FLUXION Frontend
    TASK: UI for voice bookings in calendar
    
    CONTEXT:
    - Calendar component in src/pages/Calendario.tsx
    - Zustand store per state
    - shadcn/ui components
    
    SUB-TASKS TO DELEGATE:
    1. React specialist: Voice booking indicator
    2. State specialist: Store per voice events
    
    RETURN FORMAT:
    - Status
    - Components created
    - State changes
  `
});

// Attende entrambi
const [voiceResult, frontendResult] = await Promise.all([
  voiceTask, 
  frontendTask
]);

// Verifica risultati e integra
if (voiceResult.status === 'success' && frontendResult.status === 'success') {
  // Spawn verifier
  await Task({
    subagent_name: 'gsd-verifier',
    description: 'Verify integration',
    prompt: `
      Verify voice-calendar integration:
      - Files: ${voiceResult.artifacts.join(', ')}
      - UI: ${frontendResult.artifacts.join(', ')}
      Check key links and create VERIFICATION.md
    `
  });
}
```

---

## Configuration

### .kimi/config.json

```json
{
  "orchestration": {
    "maxLevels": 4,
    "parallelMax": 5,
    "contextThreshold": 70,
    "checkpointInterval": 3,
    "agents": {
      "level0": ["master-orchestrator"],
      "level1": [
        "gsd-planner",
        "gsd-executor",
        "gsd-verifier",
        "voice-orchestrator",
        "backend-orchestrator",
        "frontend-orchestrator",
        "devops-orchestrator",
        "data-orchestrator"
      ],
      "level2": {
        "voice": ["nlu-specialist", "tts-specialist", "stt-specialist", "pipeline-specialist"],
        "backend": ["rust-specialist", "sqlite-specialist", "api-specialist", "auth-specialist"],
        "frontend": ["react-specialist", "ui-specialist", "state-specialist", "form-specialist"]
      }
    }
  }
}
```

---

## Workflow Patterns

### Pattern 1: Fan-Out / Fan-In

```
Master
  │─ Spawn 3 specialisti (parallelo)
  │    ├─ Specialist A
  │    ├─ Specialist B
  │    └─ Specialist C
  │
  └─ Aggrega risultati
       └─ Verifier
```

### Pattern 2: Pipeline Sequenziale

```
Master
  └─ Planner (output: PLAN.md)
       └─ Executor (output: code + SUMMARY.md)
            └─ Verifier (output: VERIFICATION.md)
```

### Pattern 3: Branch & Merge

```
Master
  ├─ Branch A (indipendente)
  │    ├─ Task A1
  │    └─ Task A2
  │
  ├─ Branch B (indipendente)
  │    ├─ Task B1
  │    └─ Task B2
  │
  └─ Merge Point (dipende da A e B)
       └─ Integration Task
```

---

## Best Practices

### 1. Context Budget Management

```
Livello 0 (Master):        0-20% context
Livello 1 (Orchestrator): 20-50% context
Livello 2 (Specialist):   50-80% context
Livello 3 (Worker):       80-100% context (fresh)
```

### 2. Checkpoint Strategy

```
Ogni 3 task completati → Checkpoint umano
Context > 70% → Forza checkpoint
Architettural decision → Checkpoint
```

### 3. Error Handling

```
Worker fail → Retry 1x con hint
Specialist fail → Escalate a Orchestrator
Orchestrator fail → Escalate a Master
Master fail → Human intervention
```

---

## File Structure

```
.kimi/
├── AGENT-HIERARCHY.md          # Questo file
├── config.json                 # Configurazione orchestrazione
│
├── orchestrators/              # Livello 1
│   ├── master-orchestrator.md
│   ├── gsd-planner.md
│   ├── gsd-executor.md
│   ├── gsd-verifier.md
│   ├── voice-orchestrator.md
│   ├── backend-orchestrator.md
│   ├── frontend-orchestrator.md
│   └── devops-orchestrator.md
│
├── specialists/                # Livello 2
│   ├── voice/
│   │   ├── nlu-specialist.md
│   │   ├── tts-specialist.md
│   │   ├── stt-specialist.md
│   │   └── pipeline-specialist.md
│   ├── backend/
│   │   ├── rust-specialist.md
│   │   ├── sqlite-specialist.md
│   │   └── api-specialist.md
│   └── frontend/
│       ├── react-specialist.md
│       ├── ui-specialist.md
│       └── state-specialist.md
│
└── workers/                    # Livello 3
    ├── code-generator.md
    ├── code-reviewer.md
    ├── test-generator.md
    └── doc-generator.md
```

---

## Migration da Sistema Esistente

Il sistema GSD esistente (.claude/agents/gsd-*) viene integrato:

| Esistente | Nuova Posizione | Livello |
|-----------|-----------------|---------|
| gsd-planner.md | orchestrators/gsd-planner.md | 1 |
| gsd-executor.md | orchestrators/gsd-executor.md | 1 |
| gsd-verifier.md | orchestrators/gsd-verifier.md | 1 |
| voice-engineer.md | orchestrators/voice-orchestrator.md | 1 |
| rust-backend.md | specialists/backend/rust-specialist.md | 2 |
| react-frontend.md | specialists/frontend/react-specialist.md | 2 |

---

## Quick Start

### Per Utenti

```bash
# Attiva orchestrazione gerarchica
kimi --use-agent-hierarchy

# Richiesta con orchestrazione automatica
"Implementa voice booking nel calendario"
```

### Per Sviluppatori Agenti

```bash
# Crea nuovo orchestrator
cp templates/orchestrator.md orchestrators/my-orchestrator.md

# Crea nuovo specialist
cp templates/specialist.md specialists/domain/my-specialist.md
```

---

*Version: 1.0*
*Created: 2026-02-03*
*Stack: Kimi Code CLI + FLUXION*
