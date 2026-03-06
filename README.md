# 🌊 FLUXION

[![CI](https://github.com/lukeeterna/fluxion-desktop/actions/workflows/ci.yml/badge.svg)](https://github.com/lukeeterna/fluxion-desktop/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/lukeeterna/fluxion-desktop)](https://github.com/lukeeterna/fluxion-desktop/releases)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

> **Gestionale Desktop Enterprise per PMI Italiane**
> CRM + Booking + Fatturazione + WhatsApp + Voice Agent

**Features**:
- ✅ State Machine per workflow appuntamenti
- ✅ Validazione 3-layer (Hard Block + Warning + Suggerimento)
- ✅ Domain-Driven Design architecture
- ✅ Multi-platform (Windows, macOS, Linux)

---

## 📊 Stack Tecnologico

- **Backend**: Rust + Tauri 2.x
- **Frontend**: React 19 + TypeScript 5.x
- **Database**: SQLite + SQLx (async)
- **UI**: Tailwind CSS 3.4 + shadcn/ui + Lucide Icons
- **Routing**: React Router v7

---

## 💻 Requisiti di Sistema

### ⚠️ IMPORTANTE - Sistema Operativo

**Tauri 2.x richiede versioni moderne di macOS/Windows:**

| OS | Versione Minima | Supportato |
|---|---|---|
| **macOS** | 12 Monterey (2021+) | ✅ |
| **Windows** | 10 build 1809+ | ✅ |
| **Windows** | 11 | ✅ |
| **macOS** | 11 Big Sur | ❌ **NON supportato** |

**Motivo**: Tauri 2.x usa WebKit/WebView2 API moderne disponibili solo da macOS 12+.

**Copertura mercato**: ~85% dei Mac attivi (hardware 2017+ con aggiornamenti).

### Software per Sviluppo

| Richiesto | Versione |
|---|---|
| Node.js | 20.x+ |
| Rust | 1.75+ |
| npm | 10.x+ |

---

## 🚀 Quick Start

### 1. Clone e Setup

```bash
cd /path/to/FLUXION
npm install
```

### 2. Avvia Sviluppo

```bash
# IMPORTANTE: Richiede macOS 12+ o Windows 10 1809+
npm run tauri dev
```

### 3. Build Produzione

```bash
npm run tauri build
```

---

## 📁 Struttura Progetto

```
FLUXION/
├── CLAUDE.md                    # 🎯 Master orchestrator (leggi sempre primo)
├── QUICKSTART.md                # 🚀 Guida setup dettagliata
├── README.md                    # 📖 Questo file
│
├── docs/
│   ├── context/                 # Documentazione per agenti AI
│   ├── sessions/                # Log sessioni di sviluppo
│   └── FLUXION-DESIGN-BIBLE.md  # 🎨 Design system completo
│
├── .claude/agents/              # Agenti specializzati per sviluppo
│
├── src/                         # Frontend React + TypeScript
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── types/
│
└── src-tauri/                   # Backend Rust + Tauri
    ├── src/
    │   ├── lib.rs               # Main entry point
    │   └── commands/            # Tauri commands
    └── migrations/              # Database migrations
```

---

## 🎯 Roadmap

| Fase | Status | Descrizione |
|---|---|---|
| 0 - Setup | ✅ | Tauri + React + Database |
| 1 - Layout | ✅ | Sidebar + Header + Navigation |
| 2 - CRM | 🟡 | Gestione clienti CRUD |
| 3 - Calendario | ⚪ | Booking appuntamenti |
| 4 - Servizi | ⚪ | Listino servizi + operatori |
| 5 - Fatture | ⚪ | Fatturazione elettronica XML |
| 6 - WhatsApp | ⚪ | Notifiche + reminder |
| 7 - Voice | ⚪ | Assistente vocale AI |
| 8 - Deploy | ⚪ | Build + licenze + update |

**Status corrente**: Fase 1 completata ✅

---

## 📚 Documentazione

| Risorsa | Path |
|---|---|
| 🎯 Master Orchestrator | [`CLAUDE.md`](CLAUDE.md) |
| 🚀 Setup Rapido | [`QUICKSTART.md`](QUICKSTART.md) |
| 🎨 Design Bible | [`docs/FLUXION-DESIGN-BIBLE.md`](docs/FLUXION-DESIGN-BIBLE.md) |
| 🔧 Backend (Rust) | [`docs/context/CLAUDE-BACKEND.md`](docs/context/CLAUDE-BACKEND.md) |
| ⚛️ Frontend (React) | [`docs/context/CLAUDE-FRONTEND.md`](docs/context/CLAUDE-FRONTEND.md) |
| 🎨 Design System | [`docs/context/CLAUDE-DESIGN-SYSTEM.md`](docs/context/CLAUDE-DESIGN-SYSTEM.md) |

---

## 🎨 Design System

**Palette FLUXION** (Navy + Cyan + Teal):

- **Primary**: Cyan `#22D3EE` - Azioni principali
- **Secondary**: Teal `#0891B2` - Azioni secondarie
- **Accent**: Purple `#C084FC` - Highlights
- **Background**: Navy `#1E293B` / `#0F172A` - Dark theme

**Font**: Inter con fallback system fonts

---

## 🏢 Target Market

**PMI Italiane** (1-15 dipendenti):
- Saloni di bellezza
- Palestre e centri fitness
- Cliniche mediche/dentistiche
- Ristoranti e bar
- Centri estetici
- Studi professionali

**Modello Business**: Licenza annuale desktop (NO SaaS, NO commissioni).

---

## 🔐 Licenza

Proprietario - Automation Business
P.IVA 02159940762

---

## 🐛 Troubleshooting

### L'app non si avvia su macOS

**Errore**: `failed overriding protocol method -[WKUIDelegate webView:...]`

**Causa**: macOS Big Sur (11.x) non è supportato da Tauri 2.x

**Soluzione**: Aggiorna a macOS 12 Monterey o superiore

### Build fallito su Windows

**Causa**: WebView2 runtime mancante

**Soluzione**:
```powershell
# Installa WebView2 Runtime
winget install Microsoft.EdgeWebView2Runtime
```

---

*Ultimo aggiornamento: 2025-12-30*
