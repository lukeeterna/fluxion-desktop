# FLUXION MCP Server

Model Context Protocol server for Claude Code integration with FLUXION.

## Features

### Tools (8)

| Tool | Description |
|------|-------------|
| `search_clienti` | Search clients by phone/name/email |
| `create_appuntamento` | Create new appointment |
| `get_disponibilita` | Get available time slots |
| `get_faq` | Get FAQ by vertical |
| `list_servizi` | List services |
| `list_operatori` | List operators |
| `get_cliente` | Get client details |
| `get_appuntamenti_cliente` | Get client appointments |

### Resources (9)

| URI | Description |
|-----|-------------|
| `fluxion://clienti` | All clients |
| `fluxion://servizi` | All services |
| `fluxion://operatori` | All operators |
| `fluxion://appuntamenti/oggi` | Today's appointments |
| `fluxion://faq/salone` | Salon FAQ |
| `fluxion://faq/wellness` | Wellness FAQ |
| `fluxion://faq/medical` | Medical FAQ |
| `fluxion://faq/auto` | Auto FAQ |
| `fluxion://stats` | System statistics |

## Installation

```bash
cd mcp-server
npm install
```

## Usage

### Development
```bash
npm run dev
```

### Production
```bash
npm run build
npm start
```

## Claude Code Configuration

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fluxion": {
      "command": "node",
      "args": ["/Volumes/MontereyT7/FLUXION/mcp-server/dist/index.js"],
      "env": {
        "FLUXION_DB_PATH": "~/Library/Application Support/fluxion/fluxion.db"
      }
    }
  }
}
```

## Example Tool Usage

```typescript
// Search client
await tools.search_clienti({ query: "Mario", limit: 5 });

// Create appointment
await tools.create_appuntamento({
  cliente_id: "cli_123",
  servizio_id: "srv_taglio",
  data: "2026-01-20",
  ora_inizio: "10:30"
});

// Get availability
await tools.get_disponibilita({
  data: "2026-01-20",
  servizio_id: "srv_taglio"
});

// Get FAQ
await tools.get_faq({
  verticale: "salone",
  categoria: "pricing"
});
```

## Example Resource Access

```typescript
// Read all clients
await resources.read("fluxion://clienti");

// Read today's appointments
await resources.read("fluxion://appuntamenti/oggi");

// Read FAQ
await resources.read("fluxion://faq/salone");

// Read stats
await resources.read("fluxion://stats");
```
