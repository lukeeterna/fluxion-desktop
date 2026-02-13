# Fluxion MCP Core Skill

## Description
Model Context Protocol (MCP) Core Integration for Fluxion Voice Agent.
Provides deterministic tool execution and context management for AI agents.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUXION MCP ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     MCP Protocol     ┌─────────────────────────┐  │
│  │  Claude Desktop │ ◄───────────────────►│   MCP Server (Node.js)  │  │
│  │  / Web Client   │   stdio/sse          │   - Tool Registry       │  │
│  └────────┬────────┘                      │   - Context Management  │  │
│           │                               │   - Resource Provider   │  │
│           │                               └───────────┬─────────────┘  │
│           │                                           │                 │
│           │           ┌───────────────────────────────┼─────────┐       │
│           │           │                               │         │       │
│           ▼           ▼                               ▼         ▼       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    FLUXION AGENT ORCHESTRATOR                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │  Voice   │  │ Booking  │  │  FAQ     │  │ Analytics│        │   │
│  │  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │        │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │   │
│  │       └─────────────┴─────────────┴─────────────┘                │   │
│  │                         │                                        │   │
│  │                         ▼                                        │   │
│  │              ┌─────────────────────┐                             │   │
│  │              │   Shared Context    │                             │   │
│  │              │   - Session State   │                             │   │
│  │              │   - Client Data     │                             │   │
│  │              │   - Conversation    │                             │   │
│  │              └─────────────────────┘                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## MCP Tools Registry

### Voice Tools
- `voice/process_text` - Process text through NLU pipeline
- `voice/process_audio` - Process audio (STT → NLU → TTS)
- `voice/start_vad_session` - Start Voice Activity Detection
- `voice/send_vad_chunk` - Send audio chunk to VAD
- `voice/stop_vad_session` - Stop VAD session

### Booking Tools
- `booking/create` - Create new booking
- `booking/cancel` - Cancel existing booking
- `booking/reschedule` - Reschedule booking
- `booking/check_availability` - Check slot availability
- `booking/get_client_bookings` - Get client booking history

### Context Tools
- `context/get_session` - Get session state
- `context/update_slots` - Update slot values
- `context/reset` - Reset conversation

### FAQ Tools
- `faq/search` - Search FAQs by query
- `faq/get_by_category` - Get FAQs by category

## Deterministic Execution (CoVe)

```python
class MCPDeterministicExecutor:
    """
    Chain of Verification executor for deterministic AI operations.
    
    Every AI operation must pass verification before execution:
    1. PRE_CHECK: Validate inputs against schema
    2. EXECUTE: Run the operation
    3. POST_VERIFY: Verify outputs match expected format
    4. COMMIT: Save state if all checks pass
    """
    
    async def execute(self, tool_name: str, params: dict) -> dict:
        # 1. Pre-check
        validation = await self.validate_inputs(tool_name, params)
        if not validation.valid:
            return {"error": validation.errors}
        
        # 2. Execute
        result = await self.tools[tool_name](params)
        
        # 3. Post-verify
        verification = await self.verify_outputs(tool_name, result)
        if not verification.valid:
            return {"error": verification.errors}
        
        # 4. Commit
        await self.commit_state(tool_name, params, result)
        return {"success": True, "data": result}
```

## Resources

### Session Resource
```json
{
  "uri": "fluxion://session/{session_id}",
  "mimeType": "application/json",
  "data": {
    "session_id": "string",
    "vertical": "salone|medical|palestra|auto",
    "state": "IDLE|COLLECTING|CONFIRMING|CLOSED",
    "slots": {"servizio": "string", "data": "string", "ora": "string"},
    "fallback_count": "number",
    "client_id": "string|null"
  }
}
```

### Client Resource
```json
{
  "uri": "fluxion://client/{client_id}",
  "mimeType": "application/json",
  "data": {
    "id": "string",
    "nome": "string",
    "telefono": "string",
    "email": "string",
    "storico_prenotazioni": "array"
  }
}
```

## Prompts

### Voice Agent Prompt
```
Sei Sara, l'assistente vocale AI di {business_name}.

CONTEXTO ATTUALE:
- Stato: {session_state}
- Slot raccolti: {filled_slots}
- Slot mancanti: {missing_slots}
- Fallback count: {fallback_count}

ISTRUZIONI:
1. Se stato == IDLE: Dai il saluto e propni le opzioni disponibili
2. Se stato == COLLECTING: Chiedi lo slot mancante con opzioni numerate
3. Se stato == CONFIRMING: Riepiloga e chiedi conferma
4. Se fallback_count >= 2: Passa a GUIDED MODE (opzioni numerate)
5. Se fallback_count >= 3: Offri escalation a operatore umano

RISPOSTA (JSON):
{
  "response": "Testo da pronunciare",
  "options": ["Opzione 1", "Opzione 2"] // Se guided mode
}
```

## Implementation

### Server Setup
```typescript
// mcp-server/src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({
  name: 'fluxion-mcp-server',
  version: '2.0.0',
}, {
  capabilities: {
    tools: {},
    resources: {},
    prompts: {},
  },
});

// Tool handlers
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  return await executeTool(request.params.name, request.params.arguments);
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Rules
1. ALWAYS use deterministic execution with CoVe verification
2. ALWAYS validate inputs against JSON schema before execution
3. ALWAYS maintain session state consistency
4. NEVER expose sensitive data in MCP resources
5. ALWAYS log MCP operations for analytics
6. ALWAYS handle tool execution errors gracefully

## Files
- `mcp-server/src/index.ts` - MCP server entry point
- `mcp-server/src/tools/` - Tool implementations
- `mcp-server/src/resources/` - Resource providers
- `mcp-server/src/prompts/` - Prompt templates
