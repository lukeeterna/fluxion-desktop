# FLUXION MCP Server - Remote Debugging Guide

**Agente responsabile**: mcp-engineer

## Overview

MCP (Model Context Protocol) permette a Claude Code e Cursor di controllare FLUXION da remoto per debugging visivo.

## Funzionalità Disponibili

| Tool | Descrizione |
|------|-------------|
| `take_screenshot` | Cattura screenshot dell'app (base64 PNG) |
| `get_window_info` | Info finestra (titolo, dimensioni, posizione) |
| `get_dom_content` | HTML DOM del webview |
| `execute_script` | Esegue JavaScript nel contesto app |
| `mouse_click(x, y)` | Simula click mouse |
| `type_text(text)` | Digita testo nel campo attivo |
| `get_local_storage` | Legge localStorage |
| `ping` | Test connettività |

## Setup

### 1. Avvia FLUXION con MCP

```bash
# Su iMac (macOS 12+)
cd /Volumes/MacSSD\ -\ Dati/fluxion
git pull
npm run dev:mcp
```

Output atteso:
```
🤖 MCP Server plugin enabled for remote debugging
   Socket path: /tmp/fluxion-mcp.sock
```

### 2. Configura Claude Code

Copia la configurazione in `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fluxion-mcp": {
      "command": "node",
      "args": ["/path/to/mcp-server/build/index.js"],
      "env": {
        "TAURI_MCP_IPC_PATH": "/tmp/fluxion-mcp.sock"
      }
    }
  }
}
```

### 3. Riavvia Claude Code

Dopo aver salvato la config, riavvia Claude Code per caricare il server MCP.

## Workflow Debug Tipico

```
1. Claude: "Mostrami lo stato dell'app"
   → take_screenshot() → Analisi visiva

2. Claude: "Il dropdown è nascosto dietro il contenuto"
   → get_dom_content() → Trova z-index CSS
   → execute_script('getComputedStyle(el).zIndex')

3. Claude: "Testa il form di login"
   → mouse_click(x, y) sul campo email
   → type_text("test@example.com")
   → take_screenshot() → Verifica risultato
```

## Sicurezza

- MCP è **SOLO** abilitato quando si usa `--features mcp`
- **MAI** abilitare in build di produzione
- Il socket `/tmp/fluxion-mcp.sock` è accessibile solo localmente
- Nessun dato viene inviato a server esterni

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| "Connection refused" | Verifica che FLUXION sia avviato con `dev:mcp` |
| "Socket not found" | Controlla path in config (`/tmp/fluxion-mcp.sock`) |
| MCP non appare in Claude | Riavvia Claude dopo aver salvato config |
| Screenshot vuoto | Aspetta che l'app sia completamente caricata |

## File Correlati

- `.claude/mcp_config.json` - Configurazione MCP
- `src-tauri/Cargo.toml` - Feature flag `mcp`
- `src-tauri/src/lib.rs` - Registrazione plugin
- `.claude/agents/mcp-engineer.md` - Agente specializzato
