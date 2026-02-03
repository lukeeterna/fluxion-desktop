# 🚀 Esempi di Utilizzo - Agent Hierarchy

Esempi pratici di utilizzo del sistema di orchestrazione gerarchica.

---

## Esempio 1: Voice Booking Calendar Integration

### Richiesta Utente
```
"Aggiungi voice booking al calendario"
```

### Implementazione Master Orchestrator

```typescript
// Level 0: Master Orchestrator

async function handleVoiceCalendarIntegration() {
  // Pre-flight check
  const projectState = await readFile('CLAUDE.md');
  const currentSprint = extractSprint(projectState);
  
  console.log(`Current Sprint: ${currentSprint}`);
  
  // Decomposizione in task paralleli
  const tasks = [
    {
      agent: 'voice-orchestrator',
      description: 'Integrate voice booking with calendar events',
      context: {
        files: [
          'voice-agent/src/booking_state_machine.py',
          'voice-agent/src/orchestrator.py'
        ],
        requirement: 'Emit calendar event on booking confirmation'
      }
    },
    {
      agent: 'backend-orchestrator',
      description: 'Create calendar sync API',
      context: {
        files: ['src-tauri/src/commands/appuntamenti.rs'],
        requirement: 'New endpoint for voice booking sync'
      }
    },
    {
      agent: 'frontend-orchestrator',
      description: 'Add voice booking indicator in calendar',
      context: {
        files: ['src/pages/Calendario.tsx', 'src/components/appuntamenti/'],
        requirement: 'Visual indicator for voice bookings'
      }
    }
  ];
  
  // Esecuzione parallela (Fan-Out)
  console.log('Spawning domain orchestrators in parallel...');
  
  const results = await Promise.all(
    tasks.map(t => Task({
      subagent_name: t.agent,
      description: t.description,
      prompt: formatPrompt(t)
    }))
  );
  
  // Analisi risultati
  const allSuccess = results.every(r => r.status === 'success');
  const anyPartial = results.some(r => r.status === 'partial');
  
  if (allSuccess) {
    // Verifica finale
    const verification = await Task({
      subagent_name: 'gsd-verifier',
      description: 'Verify voice-calendar integration',
      prompt: `
        Verify integration between:
        - Voice: ${results[0].artifacts.join(', ')}
        - Backend: ${results[1].artifacts.join(', ')}
        - Frontend: ${results[2].artifacts.join(', ')}
        
        Check key links and create VERIFICATION.md
      `
    });
    
    return {
      status: 'success',
      components: results,
      verification: verification,
      summary: 'Voice booking calendar integration complete'
    };
  } else if (anyPartial) {
    // Checkpoint umano
    return createCheckpoint({
      type: 'human-verify',
      reason: 'Some components completed partially',
      completedWork: results,
      resumeSignal: 'Type "continue" to proceed or "retry" to restart'
    });
  } else {
    // Errore
    return {
      status: 'failure',
      errors: results.filter(r => r.status === 'failure'),
      recommendation: 'Review error logs and retry'
    };
  }
}

function formatPrompt(task) {
  return `
    PROJECT: FLUXION
    TASK: ${task.description}
    
    CONTEXT:
    ${task.context.files.map(f => `- ${f}`).join('\n')}
    
    REQUIREMENT:
    ${task.context.requirement}
    
    ACCEPTANCE CRITERIA:
    - Code follows project patterns
    - Tests pass
    - No breaking changes
    
    RETURN FORMAT:
    \`\`\`json
    {
      "status": "success | partial | failure",
      "artifacts": ["file1", "file2"],
      "summary": "...",
      "restartRequired": false
    }
    \`\`\`
  `;
}
```

---

## Esempio 2: Voice Orchestrator - Conversation Flow

### Richiesta
```
"Aggiungi supporto per 'modifica orario'"
```

### Implementazione Voice Orchestrator

```typescript
// Level 1: Voice Orchestrator

async function handleModificaOrario() {
  // Analisi requisito
  const subTasks = [
    {
      specialist: 'nlu-specialist',
      task: 'intent_classification',
      description: 'Add "modifica_orario" intent',
      details: {
        patterns: ['cambia orario', 'sposta alle', 'modifica l\'ora'],
        confidence: 0.7
      }
    },
    {
      specialist: 'conversation-specialist',
      task: 'state_machine',
      description: 'Add conversation flow for modifica_orario',
      details: {
        newStates: ['MODIFICA_ORARIO', 'NEW_TIME', 'CONFIRM_CHANGE'],
        transitions: [
          'CONFIRMED → MODIFICA_ORARIO',
          'MODIFICA_ORARIO → NEW_TIME',
          'NEW_TIME → CONFIRM_CHANGE',
          'CONFIRM_CHANGE → COMPLETED'
        ]
      }
    },
    {
      specialist: 'tts-specialist',
      task: 'templates',
      description: 'Add TTS templates for modifica flow',
      details: {
        templates: [
          'A che ora preferisci spostare?',
          'Confermo: sposto alle {nuova_ora}?',
          'Appuntamento spostato con successo'
        ]
      }
    }
  ];
  
  // Sequenziale: NLU prima, poi conversation, poi TTS
  console.log('Step 1: NLU Specialist');
  const nluResult = await Task({
    subagent_name: 'nlu-specialist',
    description: subTasks[0].description,
    prompt: formatNluPrompt(subTasks[0])
  });
  
  if (nluResult.status !== 'success') {
    return escalateToMaster(nluResult);
  }
  
  console.log('Step 2: Conversation Specialist');
  const convResult = await Task({
    subagent_name: 'conversation-specialist',
    description: subTasks[1].description,
    prompt: formatConversationPrompt(subTasks[1])
  });
  
  if (convResult.status !== 'success') {
    return escalateToMaster(convResult);
  }
  
  console.log('Step 3: TTS Specialist');
  const ttsResult = await Task({
    subagent_name: 'tts-specialist',
    description: subTasks[2].description,
    prompt: formatTtsPrompt(subTasks[2])
  });
  
  // Test integrazione
  console.log('Step 4: Integration Test');
  const testResult = await Task({
    subagent_name: 'test-specialist',
    description: 'Test modifica_orario flow',
    prompt: `
      Test the complete flow:
      1. Input: "Vorrei cambiare orario"
         Expected: intent=modifica_orario, state=MODIFICA_ORARIO
      
      2. Input: "Spostiamo alle 15:00"
         Expected: new_time=15:00, state=CONFIRM_CHANGE
      
      3. Input: "Sì, confermo"
         Expected: booking updated, state=COMPLETED
      
      Run tests and verify.
    `
  });
  
  return {
    status: testResult.status === 'success' ? 'success' : 'partial',
    nlu: nluResult,
    conversation: convResult,
    tts: ttsResult,
    tests: testResult,
    restartRequired: true
  };
}
```

---

## Esempio 3: Backend Orchestrator - New Entity

### Richiesta
```
"Aggiungi entità Promemoria con CRUD"
```

### Implementazione Backend Orchestrator

```typescript
// Level 1: Backend Orchestrator

async function handleNewEntityPromemoria() {
  // Parallel: DB + Rust (indipendenti)
  console.log('Creating Promemoria entity...');
  
  const [dbResult, rustResult] = await Promise.all([
    // Database specialist
    Task({
      subagent_name: 'sqlite-specialist',
      description: 'Create promemoria table and migration',
      prompt: `
        Create SQLite table "promemoria":
        - id TEXT PRIMARY KEY (UUID)
        - cliente_id TEXT NOT NULL (FK)
        - messaggio TEXT NOT NULL
        - data_ora TEXT NOT NULL (ISO 8601)
        - inviato INTEGER DEFAULT 0
        - created_at TEXT DEFAULT CURRENT_TIMESTAMP
        
        Files:
        - migrations/000X_promemoria.sql
        
        Requirements:
        - Foreign key to clienti(id)
        - Index on data_ora
        - Index on cliente_id
      `
    }),
    
    // Rust specialist
    Task({
      subagent_name: 'rust-specialist',
      description: 'Create Promemoria domain and commands',
      prompt: `
        Create Promemoria CRUD:
        
        1. Domain (domain/promemoria.rs):
           struct Promemoria { ... }
           struct NuovoPromemoria { ... }
        
        2. Commands (commands/promemoria.rs):
           - get_promemoria
           - get_promemori_cliente
           - crea_promemoria
           - aggiorna_promemoria
           - elimina_promemoria
           - segna_inviato
        
        3. Register in:
           - commands/mod.rs
           - main.rs invoke_handler
        
        Patterns:
        - Use sqlx::query_as!
        - Return Result<T, String>
        - Async commands with State<'_, AppState>
      `
    })
  ]);
  
  // Verifica integrazione
  if (dbResult.status === 'success' && rustResult.status === 'success') {
    const verifyResult = await Task({
      subagent_name: 'rust-specialist',
      description: 'Verify Promemoria integration',
      prompt: `
        Verify:
        1. cargo build (no errors)
        2. cargo test (all passing)
        3. sqlx migrate run (success)
        
        Files to check:
        - Domain model matches migration
        - Commands use correct table/columns
        - All types properly defined
      `
    });
    
    return {
      status: verifyResult.status,
      database: dbResult,
      rust: rustResult,
      verification: verifyResult
    };
  }
  
  // Gestione errori
  return {
    status: 'failure',
    database: dbResult,
    rust: rustResult,
    errors: [
      ...(dbResult.status !== 'success' ? ['Database failed'] : []),
      ...(rustResult.status !== 'success' ? ['Rust failed'] : [])
    ]
  };
}
```

---

## Esempio 4: Frontend Orchestrator - Feature Page

### Richiesta
```
"Crea pagina statistiche vendite"
```

### Implementazione Frontend Orchestrator

```typescript
// Level 1: Frontend Orchestrator

async function handleStatsPage() {
  // Parallel: UI, State, Chart Component
  const [uiResult, stateResult, chartResult] = await Promise.all([
    // UI specialist
    Task({
      subagent_name: 'ui-specialist',
      description: 'Create Statistics page layout',
      prompt: `
        Create pages/Statistiche.tsx:
        - Header with title "Statistiche Vendite"
        - Date range selector (from/to)
        - Grid layout for KPI cards
        - Section for charts
        - Use shadcn/ui: Card, DatePicker
        - Tailwind classes for responsive layout
      `
    }),
    
    // State specialist
    Task({
      subagent_name: 'state-specialist',
      description: 'Create statistics store and hooks',
      prompt: `
        Create:
        1. stores/statsStore.ts:
           - Zustand store for date range
           - Actions: setDateRange, reset
        
        2. hooks/useStatistiche.ts:
           - useStatsVendite(dateRange)
           - useKPIs(dateRange)
           - TanStack Query with caching
        
        Types: src/types/statistiche.ts
      `
    }),
    
    // React specialist
    Task({
      subagent_name: 'react-specialist',
      description: 'Create chart components',
      prompt: `
        Create components/dashboard/:
        - VenditeChart.tsx (line chart)
        - KPIGrid.tsx (4 KPI cards)
        - TopServiziChart.tsx (bar chart)
        
        Use recharts library.
        Props typed with TypeScript.
      `
    })
  ]);
  
  // Integration (dipende da tutti)
  if ([uiResult, stateResult, chartResult].every(r => r.status === 'success')) {
    const integrationResult = await Task({
      subagent_name: 'react-specialist',
      description: 'Wire up statistics page',
      prompt: `
        Integrate Statistiche page:
        1. Wire components to hooks
        2. Connect date range to store
        3. Add to App.tsx router
        4. Add to Sidebar navigation
        
        Verify:
        - npm run build passes
        - No TypeScript errors
        - Responsive layout works
      `
    });
    
    return {
      status: 'success',
      ui: uiResult,
      state: stateResult,
      charts: chartResult,
      integration: integrationResult
    };
  }
  
  return {
    status: 'partial',
    ui: uiResult,
    state: stateResult,
    charts: chartResult
  };
}
```

---

## Esempio 5: Error Recovery

### Scenario
```
Specialist fallisce, escalation automatica
```

### Implementazione

```typescript
// Error handling nel workflow

async function executeWithRetry(task, maxRetries = 1) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const result = await Task({
      subagent_name: task.agent,
      description: task.description,
      prompt: task.prompt + (attempt > 0 ? '\n\n[RETRY ATTEMPT]' : '')
    });
    
    if (result.status === 'success') {
      return result;
    }
    
    if (attempt === maxRetries) {
      // Escalation
      return await escalate(task, result);
    }
  }
}

async function escalate(failedTask, error) {
  // Determina livello di escalation
  const agentLevel = getAgentLevel(failedTask.agent);
  
  if (agentLevel === 2) {
    // L2 failed → Escalate to L1 (Orchestrator)
    console.log(`Escalating ${failedTask.agent} to Domain Orchestrator`);
    
    return await Task({
      subagent_name: getParentOrchestrator(failedTask.agent),
      description: `Handle failed task: ${failedTask.description}`,
      prompt: `
        The following task failed:
        Agent: ${failedTask.agent}
        Task: ${failedTask.description}
        Error: ${error.error}
        
        Please:
        1. Analyze the error
        2. Determine if it's architectural
        3. Either fix it or escalate to Master
      `
    });
  } else if (agentLevel === 1) {
    // L1 failed → Escalate to L0 (Master)
    console.log(`Escalating to Master Orchestrator`);
    
    return createCheckpoint({
      type: 'human-verify',
      reason: 'Domain orchestrator failed',
      error: error,
      resumeSignal: 'Type "retry" or "abort"'
    });
  }
}
```

---

## Pattern Ricorrenti

### Fan-Out / Fan-In
```typescript
// Parallel execution
const results = await Promise.all(tasks.map(t => Task({...})));
const merged = mergeResults(results);
```

### Pipeline Sequenziale
```typescript
// Sequential execution
const step1 = await Task({ subagent_name: 'planner', ... });
const step2 = await Task({ subagent_name: 'executor', ... });
const step3 = await Task({ subagent_name: 'verifier', ... });
```

### Branch & Merge
```typescript
// Independent branches
const [branchA, branchB] = await Promise.all([
  Task({ subagent_name: 'backend', ... }),
  Task({ subagent_name: 'frontend', ... })
]);

// Merge point
const integration = await Task({
  subagent_name: 'integration',
  prompt: `Merge: ${branchA.artifacts} + ${branchB.artifacts}`
});
```

---

*Esempi aggiornati al sistema v1.0*
