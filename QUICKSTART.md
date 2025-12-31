# 🚀 FLUXION - Guida Avvio Rapido

> Da zero a progetto funzionante in 15 minuti.

---

## 📋 Prerequisiti

### 💻 Sistema Operativo Richiesto

**IMPORTANTE**: Tauri 2.x ha requisiti specifici di sistema operativo.

| OS | Versione Minima | Note |
|---|---|---|
| **macOS** | 12 Monterey (2021+) | ❌ Big Sur 11.x NON supportato |
| **Windows** | 10 build 1809+ | Oppure Windows 11 |
| **Linux** | Ubuntu 20.04+ | Debian 11+, Fedora 36+ |

**Perché?** Tauri 2.x richiede WebKit/WebView2 API moderne disponibili solo da macOS 12+.

**Copertura**: ~85% dei Mac attivi (hardware 2017+ con aggiornamenti).

### Software Richiesto

| Software | Versione | Verifica |
|----------|----------|----------|
| **Node.js** | 20.x+ | `node --version` |
| **npm** | 10.x+ | `npm --version` |
| **Rust** | 1.75+ | `rustc --version` |
| **Git** | 2.x+ | `git --version` |

### Installazione Rust (se mancante)

```bash
# macOS/Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Riavvia terminale, poi:
rustup update
```

### Dipendenze macOS

```bash
# Xcode Command Line Tools
xcode-select --install
```

---

## 🏁 Setup Progetto

### 1. Copia su Disco Esterno

```bash
# Il progetto deve essere in:
/Volumes/MONTEREYT7/FLUXION/

# Verifica
ls /Volumes/MONTEREYT7/FLUXION/
# Dovresti vedere: CLAUDE.md, .env, docs/, .claude/, ecc.
```

### 2. Inizializza Progetto Tauri

```bash
cd /Volumes/MONTEREYT7/FLUXION

# Crea progetto Tauri + React
npm create tauri-app@latest . -- --template react-ts

# Se chiede di sovrascrivere, scegli NO per i file esistenti
```

### 3. Installa Dipendenze

```bash
# Dipendenze Node
npm install

# Dipendenze aggiuntive
npm install @tanstack/react-query zustand lucide-react date-fns
npm install react-hook-form @hookform/resolvers zod
npm install clsx tailwind-merge class-variance-authority

# Dev dependencies
npm install -D @types/node
```

### 4. Configura shadcn/ui

```bash
# Inizializza shadcn
npx shadcn@latest init

# Rispondi:
# - Style: New York
# - Base color: Slate
# - CSS variables: Yes

# Installa componenti base
npx shadcn@latest add button card input table dialog
npx shadcn@latest add dropdown-menu tabs toast
```

### 5. Configura Tailwind

Sostituisci `tailwind.config.js` con il contenuto da `docs/FLUXION-DESIGN-BIBLE.md`.

### 6. Copia Design Tokens

Copia il CSS da `docs/FLUXION-DESIGN-BIBLE.md` (sezione globals.css) in `src/index.css`.

### 7. Plugin Tauri

```bash
# Aggiungi plugin Tauri necessari
cd src-tauri
cargo add tauri-plugin-sql --features sqlite
cargo add tauri-plugin-fs
cargo add tauri-plugin-dialog
cargo add tauri-plugin-store

# SQLx per queries tipizzate
cargo add sqlx --features runtime-tokio,sqlite
cargo add tokio --features full
```

### 8. Primo Avvio

```bash
cd /Volumes/MONTEREYT7/FLUXION

# Development mode
npm run tauri dev
```

Se tutto funziona, vedrai la finestra Tauri con React!

---

## 📁 Struttura Post-Setup

```
FLUXION/
├── CLAUDE.md                 ← Master orchestrator
├── .env                      ← Variabili (già configurate)
├── package.json              ← Dipendenze Node
├── tailwind.config.js        ← Config Tailwind
├── vite.config.ts            ← Config Vite
│
├── src/                      ← Frontend React
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css             ← Design tokens
│   └── components/
│       └── ui/               ← shadcn/ui
│
├── src-tauri/                ← Backend Rust
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── src/
│       └── main.rs
│
├── docs/                     ← Documentazione
│   ├── context/              ← Contesto agenti
│   └── FLUXION-DESIGN-BIBLE.md
│
└── .claude/
    └── agents/               ← Definizioni agenti
```

---

## 🔧 Comandi Utili

| Comando | Descrizione |
|---------|-------------|
| `npm run tauri dev` | Avvia in development |
| `npm run tauri build` | Build production |
| `npm run dev` | Solo frontend (browser) |
| `cargo check` | Verifica Rust |
| `cargo test` | Test Rust |

---

## ❓ Troubleshooting

### Errore: "Rust not found"

```bash
source $HOME/.cargo/env
# oppure riavvia terminale
```

### Errore: "SQLite not found"

```bash
# macOS
brew install sqlite3

# Linux
sudo apt install libsqlite3-dev
```

### Errore: "Permission denied" su disco esterno

```bash
# Verifica permessi
ls -la /Volumes/MONTEREYT7/

# Se necessario
chmod -R 755 /Volumes/MONTEREYT7/FLUXION/
```

### Errore: "Port already in use"

```bash
# Trova processo su porta 1420
lsof -i :1420

# Termina processo
kill -9 <PID>
```

---

## 🎯 Prossimi Passi

Dopo il setup, leggi:

1. **CLAUDE.md** - Per capire come lavorare con gli agenti
2. **docs/context/CLAUDE-BACKEND.md** - Per implementare il database
3. **docs/FLUXION-DESIGN-BIBLE.md** - Per i componenti UI

---

## 📞 Supporto

Se hai problemi:

1. Verifica i prerequisiti
2. Controlla i log in terminale
3. Consulta la documentazione in `docs/`

---

*Ultimo aggiornamento: 2025-12-28*
