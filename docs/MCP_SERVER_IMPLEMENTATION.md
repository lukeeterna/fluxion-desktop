# MCP Server Implementation - FLUXION

Complete MCP server setup for Claude Code integration with FLUXION voice pipeline.

---

## 1. Setup & Installation

```bash
# Create mcp-server directory
cd fluxion
mkdir -p mcp-server/src/{tools,resources}
cd mcp-server

# Initialize Node.js project
npm init -y
npm install @modelcontextprotocol/sdk dotenv sqlite3 axios

# Install dev dependencies
npm install -D typescript @types/node @types/@modelcontextprotocol/sdk ts-node nodemon

# Create TypeScript config
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
EOF

# Update package.json
cat > package.json << 'EOF'
{
  "name": "fluxion-mcp-server",
  "version": "1.0.0",
  "description": "MCP server for FLUXION automation system",
  "main": "dist/index.js",
  "type": "commonjs",
  "scripts": {
    "dev": "ts-node src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "dotenv": "^1.0.0",
    "sqlite3": "^5.1.6",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/@modelcontextprotocol/sdk": "^0.5.0",
    "typescript": "^5.3.0",
    "ts-node": "^10.9.0"
  }
}
EOF

npm install
```

---

## 2. Main MCP Server File

**File: `mcp-server/src/index.ts`**

```typescript
import { Server, StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Tool, TextContent } from "@modelcontextprotocol/sdk/types.js";
import Database from "better-sqlite3";
import * as path from "path";
import * as dotenv from "dotenv";

dotenv.config({ path: path.join(__dirname, "../.env") });

// Database connection
const dbPath = path.join(process.env.FLUXION_HOME || process.env.HOME, "Library/Application Support/fluxion/fluxion.db");
const db = new Database(dbPath);

// Initialize MCP Server
const server = new Server({
  name: "fluxion-mcp",
  version: "1.0.0",
});

// Tool definitions
const tools: Tool[] = [
  {
    name: "search_clienti",
    description: "Search for clients by phone number, email, or name",
    inputSchema: {
      type: "object" as const,
      properties: {
        query: {
          type: "string",
          description: "Search query (phone, email, or name)",
        },
        limit: {
          type: "number",
          description: "Max results (default: 10)",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "create_appuntamento",
    description: "Create a new appointment",
    inputSchema: {
      type: "object" as const,
      properties: {
        cliente_id: {
          type: "string",
          description: "Client ID",
        },
        servizio_id: {
          type: "string",
          description: "Service ID",
        },
        data: {
          type: "string",
          description: "Date (YYYY-MM-DD)",
        },
        ora_inizio: {
          type: "string",
          description: "Start time (HH:MM)",
        },
        nota: {
          type: "string",
          description: "Optional notes",
        },
      },
      required: ["cliente_id", "servizio_id", "data", "ora_inizio"],
    },
  },
  {
    name: "get_disponibilita",
    description: "Get available appointment slots for a service",
    inputSchema: {
      type: "object" as const,
      properties: {
        servizio_id: {
          type: "string",
          description: "Service ID",
        },
        data: {
          type: "string",
          description: "Date (YYYY-MM-DD)",
        },
      },
      required: ["servizio_id", "data"],
    },
  },
  {
    name: "get_faq",
    description: "Get FAQ entries for a vertical",
    inputSchema: {
      type: "object" as const,
      properties: {
        verticale: {
          type: "string",
          description: "Vertical (auto, bellezza, medico, ecommerce)",
        },
        categoria: {
          type: "string",
          description: "Optional FAQ category filter",
        },
        limit: {
          type: "number",
          description: "Max results (default: 20)",
        },
      },
      required: ["verticale"],
    },
  },
];

// Tool handlers
server.setRequestHandler("tools/list", async () => ({
  tools,
}));

server.setRequestHandler("tools/call", async (request: any) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "search_clienti":
        return await handleSearchClienti(args);
      case "create_appuntamento":
        return await handleCreateAppuntamento(args);
      case "get_disponibilita":
        return await handleGetDisponibilita(args);
      case "get_faq":
        return await handleGetFAQ(args);
      default:
        return {
          content: [
            {
              type: "text",
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Handler functions
async function handleSearchClienti(args: any) {
  const { query, limit = 10 } = args;

  try {
    const stmt = db.prepare(`
      SELECT id, nome, cognome, telefono, email, soprannome
      FROM clienti
      WHERE telefono LIKE ? OR email LIKE ? OR nome LIKE ? OR cognome LIKE ?
      LIMIT ?
    `);

    const results = stmt.all(
      `%${query}%`,
      `%${query}%`,
      `%${query}%`,
      `%${query}%`,
      limit
    );

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(results, null, 2),
        },
      ],
    };
  } catch (error: any) {
    throw new Error(`Failed to search clienti: ${error.message}`);
  }
}

async function handleCreateAppuntamento(args: any) {
  const { cliente_id, servizio_id, data, ora_inizio, nota } = args;

  try {
    // Calculate ora_fine based on servizio durata
    const servizio = db
      .prepare("SELECT durata FROM servizi WHERE id = ?")
      .get(servizio_id) as any;

    if (!servizio) {
      throw new Error(`Servizio ${servizio_id} not found`);
    }

    const [hours, minutes] = ora_inizio.split(":").map(Number);
    const endTime = new Date(0, 0, 0, hours, minutes + servizio.durata);
    const ora_fine = `${String(endTime.getHours()).padStart(2, "0")}:${String(
      endTime.getMinutes()
    ).padStart(2, "0")}`;

    const id = `app_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const stmt = db.prepare(`
      INSERT INTO appuntamenti 
      (id, cliente_id, servizio_id, data, ora_inizio, ora_fine, nota, stato, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, 'confermato', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    `);

    stmt.run(id, cliente_id, servizio_id, data, ora_inizio, ora_fine, nota || "");

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { success: true, id, message: "Appointment created" },
            null,
            2
          ),
        },
      ],
    };
  } catch (error: any) {
    throw new Error(`Failed to create appointment: ${error.message}`);
  }
}

async function handleGetDisponibilita(args: any) {
  const { servizio_id, data } = args;

  try {
    // Get all appointments for this service on this date
    const stmt = db.prepare(`
      SELECT ora_inizio, ora_fine
      FROM appuntamenti
      WHERE servizio_id = ? AND data = ? AND stato != 'cancellato'
      ORDER BY ora_inizio
    `);

    const occupied = stmt.all(servizio_id, data) as any[];

    // Generate available slots (9:00 - 18:00 in 30-min intervals)
    const slots = [];
    for (let h = 9; h < 18; h++) {
      for (let m of [0, 30]) {
        const time = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
        const isOccupied = occupied.some(
          (slot) => slot.ora_inizio === time
        );
        if (!isOccupied) {
          slots.push(time);
        }
      }
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { date: data, available_slots: slots },
            null,
            2
          ),
        },
      ],
    };
  } catch (error: any) {
    throw new Error(`Failed to get disponibilita: ${error.message}`);
  }
}

async function handleGetFAQ(args: any) {
  const { verticale, categoria, limit = 20 } = args;

  try {
    let query = `
      SELECT id, faq_id, domanda, risposta_template, categoria, keywords
      FROM faq_entries
      WHERE categoria_pmi = ?
    `;

    const params: any[] = [verticale];

    if (categoria) {
      query += ` AND categoria = ?`;
      params.push(categoria);
    }

    query += ` LIMIT ?`;
    params.push(limit);

    const stmt = db.prepare(query);
    const results = stmt.all(...params);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(results, null, 2),
        },
      ],
    };
  } catch (error: any) {
    throw new Error(`Failed to get FAQ: ${error.message}`);
  }
}

// Resource handlers (optional - for Claude to inspect state)
server.setRequestHandler("resources/list", async () => ({
  resources: [
    {
      uri: "fluxion://clienti",
      name: "All Clients",
      description: "List of all clients in the system",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://servizi",
      name: "All Services",
      description: "List of available services per vertical",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://faq",
      name: "FAQ Database",
      description: "FAQ entries for all verticals",
      mimeType: "application/json",
    },
  ],
}));

server.setRequestHandler("resources/read", async (request: any) => {
  const { uri } = request.params;

  if (uri === "fluxion://clienti") {
    const stmt = db.prepare(
      "SELECT id, nome, cognome, telefono, email FROM clienti LIMIT 100"
    );
    const clients = stmt.all();
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(clients, null, 2),
        },
      ],
    };
  }

  if (uri === "fluxion://servizi") {
    const stmt = db.prepare(
      "SELECT id, nome, prezzo, durata, verticale_pmi FROM servizi"
    );
    const services = stmt.all();
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(services, null, 2),
        },
      ],
    };
  }

  if (uri === "fluxion://faq") {
    const stmt = db.prepare(
      "SELECT faq_id, categoria_pmi, domanda, categoria FROM faq_entries LIMIT 100"
    );
    const faqs = stmt.all();
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(faqs, null, 2),
        },
      ],
    };
  }

  return {
    contents: [
      {
        uri,
        mimeType: "text/plain",
        text: `Unknown resource: ${uri}`,
      },
    ],
  };
});

// Start server
const transport = new StdioServerTransport();
server.connect(transport).then(() => {
  console.error("MCP Server started successfully");
});
```

---

## 3. Environment Configuration

**File: `mcp-server/.env`**

```env
# FLUXION MCP Server Configuration
FLUXION_HOME=~/Library/Application Support/fluxion

# SQLite Database Path
DB_PATH=${FLUXION_HOME}/fluxion.db

# MCP Server Settings
MCP_PORT=3003
MCP_BIND=127.0.0.1

# Claude Code Configuration
CLAUDE_CODE_ENABLED=true
```

---

## 4. Claude Code Integration

**Add to `.vscode/settings.json`:**

```json
{
  "claude": {
    "mcpServers": {
      "fluxion": {
        "command": "node",
        "args": ["${workspaceFolder}/mcp-server/dist/index.js"],
        "env": {
          "FLUXION_HOME": "${workspaceFolder}"
        }
      }
    }
  }
}
```

---

## 5. Build & Run

```bash
cd mcp-server

# Development
npm run dev

# Production build
npm run build

# Run production
npm start
```

---

## 6. Usage in Claude Code

```typescript
// In Claude Code editor, use MCP tools directly:

// Search for client
await tools.search_clienti({
  query: "3459876543"  // Phone number
});

// Create appointment
await tools.create_appuntamento({
  cliente_id: "cli_123",
  servizio_id: "srv_tagliando",
  data: "2026-01-20",
  ora_inizio: "10:30",
  nota: "Tagliando + controllo freni"
});

// Get available slots
await tools.get_disponibilita({
  servizio_id: "srv_tagliando",
  data: "2026-01-22"
});

// Get FAQs
await tools.get_faq({
  verticale: "auto",
  categoria: "pricing",
  limit: 10
});

// Access resources
await resources.read("fluxion://clienti");
await resources.read("fluxion://servizi");
await resources.read("fluxion://faq");
```

---

## 7. Next Steps

- [ ] Test MCP server with `npm run dev`
- [ ] Verify SQLite connection
- [ ] Integrate with Claude Code in Windsurf/Cursor
- [ ] Run end-to-end tests with voice pipeline
- [ ] Monitor latency (<100ms target for each tool call)

---

**Status**: 🟢 MCP Server Ready for Implementation  
**Maintainer**: Automated by Claude Code  
**Last Updated**: 15 Gennaio 2026
