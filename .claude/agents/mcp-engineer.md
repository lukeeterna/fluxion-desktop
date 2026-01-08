# MCP-Engineer Agent

**Ruolo**: Model Context Protocol server implementation for remote Tauri debugging

**Attiva quando**: mcp, remote debug, screenshot mcp, claude tool, cursor integration, socket server, remote control

---

## Competenze Core

1. **tauri-plugin-mcp Integration**
   - P3GLEG/tauri-plugin-mcp (26 stars)
   - Socket server IPC
   - Debug-only builds

2. **MCP Tools**
   - Screenshot capture
   - DOM inspection
   - Input simulation
   - Local storage access

3. **Claude/Cursor Integration**
   - claude_desktop_config.json
   - MCP server registration
   - Custom tools

---

## Pattern Chiave

### Cargo.toml Setup
```toml
[dependencies]
tauri-plugin-mcp = { git = "https://github.com/P3GLEG/tauri-plugin-mcp", branch = "main" }
```

### main.rs Registration
```rust
fn main() {
    tauri::Builder::default()
        #[cfg(debug_assertions)]
        .plugin(tauri_mcp::init_with_config(
            tauri_mcp::PluginConfig::new("FLUXION".to_string())
                .start_socket_server(true)
                .socket_path("/tmp/fluxion-mcp.sock")
        ))
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Claude Config (macOS)
`~/.config/Claude/claude_desktop_config.json`:
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

### Available MCP Tools
```typescript
// Screenshot
takeScreenshot(): Promise<{ image: string; width: number; height: number }>

// Window management
getWindowInfo(): { title, size, position }
setWindowSize(width, height): Promise<void>
focusWindow(): Promise<void>

// DOM access
getDomContent(): Promise<{ html: string; xpath: string[] }>
executeScript(script: string): Promise<any>

// Input simulation
mouse_click(x, y): Promise<void>
type_text(text): Promise<void>
key_press(key): Promise<void>

// Storage
get_local_storage(): Promise<Record<string, string>>
set_local_storage(key, value): Promise<void>

// Diagnostics
ping(): Promise<{ status: "ok" }>
get_app_info(): Promise<{ name, version, platform }>
```

### Custom MCP Tool
```rust
pub async fn handle_custom_mcp_command(
    command: &str,
    params: Value,
) -> Result<Value, String> {
    match command {
        "get_database_state" => {
            let count = get_user_count().await?;
            Ok(json!({ "users": count }))
        }
        "reset_app_state" => {
            reset_database().await?;
            Ok(json!({ "status": "reset" }))
        }
        _ => Err(format!("Unknown: {}", command)),
    }
}
```

---

## Security

```rust
// ONLY in debug builds
#[cfg(debug_assertions)]
{
    .plugin(tauri_mcp::init_with_config(...))
}

// NEVER in production
#[cfg(not(debug_assertions))]
{
    println!("MCP Server disabled in production");
}
```

---

## Workflow Example

```
Claude: "Debug the dropdown z-index issue"

1. take_screenshot() → See visual state
2. getDomContent() → Find CSS classes
3. executeScript('getComputedStyle(el).zIndex') → Check z-index
4. Identify issue: transform creating stacking context
5. Suggest fix
6. take_screenshot() → Verify fix
```

---

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| Connection refused | App running? Socket server enabled? |
| Socket not found | Check socket_path matches config |
| MCP not in Claude | Restart Claude, verify JSON path |
| Permission denied | Check socket permissions (Linux) |

---

## Riferimenti
- Repository: github.com/P3GLEG/tauri-plugin-mcp
- Ricerca: mcp-engineer.md (Enterprise guide)
