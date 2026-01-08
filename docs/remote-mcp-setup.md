# 🔧 Setup Completo: Claude Code → iMac Remote Testing

**Guida Passo-Passo per Connessione Remota**  
*Risolve SSH fallito + MCP non configurato*

---

## 🎯 Obiettivo Finale

```
MacBook (Claude Code) → SSH → iMac (Tauri App + MCP Server)
                            ↓
                   Interact remotely via MCP
```

---

## FASE 1: Fix SSH Connection (iMac Server)

### Step 1.1: Setup SSH Server su iMac

```bash
# Su iMac, apri Terminal

# 1. Abilita SSH (Remote Login)
# System Settings → General → Sharing → Remote Login [ON]

# 2. Oppure via CLI:
sudo systemsetup -setremotelogin on

# 3. Verifica porta SSH
sudo lsof -i :22

# Output atteso:
# sshd    12345 root    4u  IPv6 0xc0a83e00      0t0  TCP *:ssh (LISTEN)
```

### Step 1.2: Ottieni IP iMac

```bash
# Su iMac in Terminal:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Output esempio:
# inet 192.168.1.100 netmask 0xffffff00 broadcast 192.168.1.255

# SALVA: 192.168.1.100 (questo è l'IP iMac)
```

### Step 1.3: Configura SSH con Chiave (No Password)

```bash
# Su MacBook (client):

# 1. Genera SSH key se non hai
ssh-keygen -t ed25519 -f ~/.ssh/imac_key -N ""

# Output:
# Your identification has been saved in /Users/you/.ssh/imac_key
# Your public key has been saved in /Users/you/.ssh/imac_key.pub

# 2. Copia chiave pubblica su iMac
ssh-copy-id -i ~/.ssh/imac_key.pub -p 22 YOUR_IMAC_USERNAME@192.168.1.100

# Sostituisci:
# YOUR_IMAC_USERNAME = username iMac (es: marco)
# 192.168.1.100 = IP iMac

# Ti chiede password iMac: inserisci

# 3. Testa SSH
ssh -i ~/.ssh/imac_key YOUR_IMAC_USERNAME@192.168.1.100

# Atteso: accedi a iMac senza password
# Se funziona: premi Ctrl+D per uscire
```

### Step 1.4: Configura ~/.ssh/config

```bash
# Su MacBook:
nano ~/.ssh/config

# Aggiungi:
Host imac
    HostName 192.168.1.100
    User YOUR_IMAC_USERNAME
    IdentityFile ~/.ssh/imac_key
    Port 22
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# Salva: Ctrl+O → Enter → Ctrl+X

# Ora puoi fare:
ssh imac
# (senza digitare tutto il comando)
```

### Step 1.5: Test SSH Finale

```bash
# MacBook
ssh imac "whoami"

# Atteso output: YOUR_IMAC_USERNAME

# Se funziona: SSH è OK ✓
```

---

## FASE 2: Setup Tauri + MCP su iMac

### Step 2.1: Clona Progetto su iMac

```bash
# Su iMac:
ssh imac

# Dentro iMac:
cd ~
git clone https://github.com/yourusername/your-tauri-project.git
cd your-tauri-project

# Installa dipendenze
npm install
cd src-tauri && cargo build --release
cd ..
```

### Step 2.2: Configura MCP Server su iMac

```bash
# Su iMac nella cartella progetto:
cd mcp-server-ts
pnpm install
pnpm build

# Verifica output
ls -la build/index.js
# Deve esistere
```

### Step 2.3: Crea Script di Startup su iMac

```bash
# Su iMac:
nano ~/start-tauri-mcp.sh

# Copia dentro:
#!/bin/bash

# Cambia directory al progetto
cd ~/your-tauri-project

# Porta del dev server
export VITE_PORT=1420

# Porta MCP socket over TCP (per network)
export TAURI_MCP_PORT=5000

# Avvia in background
npm run dev &
TAURI_PID=$!

# Aspetta che l'app sia avviata
sleep 5

# Avvia MCP server TCP (ascolta su 0.0.0.0:5000)
node mcp-server-ts/build/index.js --port 5000 &
MCP_PID=$!

echo "✓ Tauri PID: $TAURI_PID"
echo "✓ MCP Server PID: $MCP_PID"
echo "✓ MCP listening on 0.0.0.0:5000"

# Mantieni in background
wait

# Salva: Ctrl+O → Enter → Ctrl+X

# Rendi eseguibile
chmod +x ~/start-tauri-mcp.sh
```

### Step 2.4: Configura MCP Server per Network

Il file `mcp-server-ts/src/index.ts` deve accettare TCP su rete:

```typescript
// mcp-server-ts/src/index.ts

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import * as net from "net";

const port = parseInt(process.env.TAURI_MCP_PORT || "5000");
const host = "0.0.0.0"; // Ascolta su tutte le interfacce di rete

const server = new Server({
  name: "tauri-mcp",
  version: "1.0.0",
});

// Create TCP server
const tcpServer = net.createServer((socket) => {
  console.log(`[MCP] Client connected from ${socket.remoteAddress}`);

  // Setup stdio transport
  server.connect(socket);

  socket.on("error", (err) => {
    console.error("[MCP] Socket error:", err);
  });

  socket.on("close", () => {
    console.log("[MCP] Client disconnected");
  });
});

tcpServer.listen(port, host, () => {
  console.log(`🔌 MCP Server listening on ${host}:${port}`);
});

// Handle server startup errors
tcpServer.on("error", (err) => {
  console.error("[MCP] Server error:", err);
  process.exit(1);
});
```

### Step 2.5: Avvia Tauri + MCP su iMac

```bash
# Su iMac:
~/start-tauri-mcp.sh

# Atteso output:
# ✓ Tauri PID: 12345
# ✓ MCP Server PID: 12346
# ✓ MCP listening on 0.0.0.0:5000
```

### Step 2.6: Verifica Accessibilità da MacBook

```bash
# Su MacBook:
ssh imac "lsof -i :5000"

# Atteso:
# node    12346 marco    5u  IPv6 0x12345      0t0  TCP *:5000 (LISTEN)

# Test connessione TCP
nc -zv 192.168.1.100 5000

# Atteso:
# Connection to 192.168.1.100 port 5000 [tcp/*] succeeded!
```

---

## FASE 3: Configura Claude Code / Cursor su MacBook

### Step 3.1: Crea Port Forward (Opzionale ma Consigliato)

```bash
# Su MacBook (Terminal):
ssh -i ~/.ssh/imac_key -N -L 5000:localhost:5000 YOUR_IMAC_USERNAME@192.168.1.100 &

# Questo mappa:
# MacBook localhost:5000 → iMac localhost:5000 (via SSH tunnel)

# Verifica
lsof -i :5000

# Atteso:
# ssh   12345 you    7u  IPv6 0x...  0t0  TCP localhost:5000 (LISTEN)
```

### Step 3.2: Configura MCP in Claude Code / Cursor

**Opzione A: Connessione Diretta (Senza SSH Tunnel)**

```json
// ~/.config/Claude/claude_desktop_config.json
// (oppure ~/Library/Application Support/Claude/claude_desktop_config.json su macOS)

{
  "mcpServers": {
    "tauri-mcp": {
      "command": "nc",
      "args": ["192.168.1.100", "5000"],
      "env": {
        "TAURI_MCP_HOST": "192.168.1.100",
        "TAURI_MCP_PORT": "5000"
      }
    }
  }
}
```

**Opzione B: Via SSH Tunnel (Più Sicuro)**

```json
// ~/.config/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "tauri-mcp": {
      "command": "nc",
      "args": ["localhost", "5000"],
      "env": {
        "TAURI_MCP_HOST": "localhost",
        "TAURI_MCP_PORT": "5000"
      }
    }
  }
}
```

### Step 3.3: Restart Claude Code / Cursor

```bash
# Chiudi e riapri Claude Code / Cursor

# Verifica che MCP sia connesso:
# In Claude Code, apri chat e chiedi:
# "Take a screenshot of the Tauri app"

# Se funziona: Claude mostra la screenshot della iMac
```

---

## FASE 4: Test Connessione Completa

### Test 1: SSH Tunnel Funzionante

```bash
# MacBook Terminal
ssh imac "curl -s http://localhost:1420" | head -5

# Atteso: HTML della pagina React
```

### Test 2: MCP Raggiungibile

```bash
# MacBook Terminal (se hai SSH tunnel attivo):
echo '{"jsonrpc":"2.0","id":1}' | nc localhost 5000

# Oppure diretto:
echo '{"jsonrpc":"2.0","id":1}' | nc 192.168.1.100 5000

# Atteso: risposta MCP (JSON)
```

### Test 3: Claude Code Può Testare App

**In Claude Code Chat:**

```
User: "Take a screenshot of the app running on my iMac"

Claude Response:
📸 Taking screenshot...
✓ Screenshot captured: [shows image from iMac]
```

---

## TROUBLESHOOTING

### ❌ SSH Connection Refused

```bash
# Diagnostica
ssh -vvv imac

# Controlla:
# 1. iMac ha SSH enabled? (System Settings → Sharing → Remote Login)
# 2. IP è corretto? (ssh imac mostra quale IP usa)
# 3. Firewall iMac blocca port 22? (sudo lsof -i :22)

# Fix: Riabilita SSH
ssh -i ~/.ssh/imac_key marco@192.168.1.100 "sudo systemsetup -setremotelogin on"
```

### ❌ MCP Port 5000 Non Raggiungibile

```bash
# Su iMac
ssh imac

# Verifica processo
lsof -i :5000

# Se non vedi output, MCP non è in ascolto:
ps aux | grep node

# Se non vedi MCP, riavvia:
~/start-tauri-mcp.sh

# Verifica logs
tail -f ~/.tauri-mcp-logs.txt  # se hai setup logging
```

### ❌ Claude Code Non Vede MCP

```bash
# 1. Verifica config JSON sintassi
cat ~/.config/Claude/claude_desktop_config.json | jq .

# 2. Se errore JSON, fix e restart Claude

# 3. Verifica che MCP server sia in ascolto
netstat -an | grep 5000

# 4. Test connessione manuale
nc -zv 192.168.1.100 5000
```

### ❌ SSH Tunnel Lento/Disconnessione

```bash
# Aggiungi keepalive nel SSH config
# ~/.ssh/config

Host imac
    HostName 192.168.1.100
    User YOUR_IMAC_USERNAME
    IdentityFile ~/.ssh/imac_key
    Port 22
    StrictHostKeyChecking no
    ServerAliveInterval 60        # Keepalive ogni 60 sec
    ServerAliveCountMax 3         # Riprova 3 volte
    TCPKeepAlive yes
```

---

## SETUP FINALE: Checklist

- [ ] **SSH Working**: `ssh imac "whoami"` ritorna username
- [ ] **Tauri Running**: `ssh imac "lsof -i :1420"` mostra processo
- [ ] **MCP Running**: `ssh imac "lsof -i :5000"` mostra node process
- [ ] **Network Accessible**: `nc -zv 192.168.1.100 5000` succeeds
- [ ] **MCP Config**: `~/.config/Claude/claude_desktop_config.json` valido
- [ ] **Claude Code Connesso**: Chat → "Take screenshot" → vede app iMac
- [ ] **Test Interaction**: Claude clicca bottone → vede risultato

---

## QUICK START (Versione Rapida)

```bash
# MacBook Terminal - Una volta sola:

# 1. Setup SSH
ssh-keygen -t ed25519 -f ~/.ssh/imac_key -N ""
ssh-copy-id -i ~/.ssh/imac_key.pub -p 22 marco@192.168.1.100

# 2. Configura SSH config
cat >> ~/.ssh/config << 'EOF'
Host imac
    HostName 192.168.1.100
    User marco
    IdentityFile ~/.ssh/imac_key
EOF

# 3. Test
ssh imac "whoami"

# Successivamente, ogni volta che vuoi testare:

# 4. iMac: Avvia app
ssh imac "~/start-tauri-mcp.sh &"

# 5. MacBook: SSH tunnel
ssh -N -L 5000:localhost:5000 imac &

# 6. Claude Code: Testa
# Chat: "Test the app on iMac"
```

---

## Variante: Se iMac Non Ha SSH Accesso (Rete Locale Diretta)

Se SSH non è un'opzione, puoi usare accesso diretto:

```json
// ~/.config/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "tauri-mcp": {
      "command": "node",
      "args": ["/path/to/mcp-server-ts/build/index.js"],
      "env": {
        "TAURI_MCP_IPC_PATH": "tcp://192.168.1.100:5000"
      }
    }
  }
}
```

Ma SSH tunnel è **più sicuro** per rete locale condivisa.

---

## RISULTATO FINALE

Dopo setup:

```
MacBook Claude Code
    ↓ (MCP SSH Tunnel)
iMac MCP Server (port 5000)
    ↓ (IPC)
iMac Tauri App (port 1420)
    
Claude Code chiede: "Test login flow"
Claude interagisce con app reale su iMac
Documenta errori automaticamente
```

**Tutto funziona via SSH da MacBook!** 🎉