# 📚 FLUXION - Indice Documentazione

> Mappa di navigazione per Claude Code. Leggi solo ciò che serve.

---

## 🗂️ STRUTTURA CONTESTO

```
docs/context/
├── CLAUDE-INDEX.md          ← SEI QUI
├── CLAUDE-BACKEND.md        ← Rust + Tauri + SQLite + API
├── CLAUDE-FRONTEND.md       ← React + TypeScript + Hooks
├── CLAUDE-DESIGN-SYSTEM.md  ← Design tokens + Componenti UI
├── CLAUDE-INTEGRATIONS.md   ← WhatsApp + API esterne
├── CLAUDE-VOICE.md          ← Voice Agent (Groq + Piper)
├── CLAUDE-FATTURE.md        ← Fatturazione elettronica XML
└── CLAUDE-DEPLOYMENT.md     ← Build + Release + Licenze
```

---

## 🎯 GUIDA RAPIDA: QUALE FILE LEGGERE?

### Per Task Backend

| Task | File |
|------|------|
| Schema database SQLite | CLAUDE-BACKEND.md |
| Tauri commands (Rust) | CLAUDE-BACKEND.md |
| API REST interne | CLAUDE-BACKEND.md |
| Migrations database | CLAUDE-BACKEND.md |
| Plugin Tauri | CLAUDE-BACKEND.md |

### Per Task Frontend

| Task | File |
|------|------|
| Componenti React | CLAUDE-FRONTEND.md |
| Custom hooks | CLAUDE-FRONTEND.md |
| State management | CLAUDE-FRONTEND.md |
| Routing | CLAUDE-FRONTEND.md |
| TypeScript types | CLAUDE-FRONTEND.md |

### Per Task Design/UI

| Task | File |
|------|------|
| Colori e palette | CLAUDE-DESIGN-SYSTEM.md |
| Typography | CLAUDE-DESIGN-SYSTEM.md |
| Spacing e layout | CLAUDE-DESIGN-SYSTEM.md |
| Componenti shadcn/ui | CLAUDE-DESIGN-SYSTEM.md |
| Animazioni | CLAUDE-DESIGN-SYSTEM.md |
| Mockup completo | FLUXION-DESIGN-BIBLE.md |

### Per Task Integrazioni

| Task | File |
|------|------|
| WhatsApp bridge | CLAUDE-INTEGRATIONS.md |
| Template messaggi | CLAUDE-INTEGRATIONS.md |
| Rate limiting | CLAUDE-INTEGRATIONS.md |

### Per Task Voice Agent

| Task | File |
|------|------|
| Architettura voice | CLAUDE-VOICE.md |
| Groq + Whisper | CLAUDE-VOICE.md |
| Piper TTS | CLAUDE-VOICE.md |
| VoIP Ehiweb | CLAUDE-VOICE.md |
| Pipecat pipeline | CLAUDE-VOICE.md |

### Per Task Fatturazione

| Task | File |
|------|------|
| XML FatturaPA | CLAUDE-FATTURE.md |
| Validazione CF/PIVA | CLAUDE-FATTURE.md |
| Schema XML | CLAUDE-FATTURE.md |
| Invio SDI | CLAUDE-FATTURE.md |

### Per Task DevOps

| Task | File |
|------|------|
| Build Tauri | CLAUDE-DEPLOYMENT.md |
| Code signing | CLAUDE-DEPLOYMENT.md |
| Auto-update | CLAUDE-DEPLOYMENT.md |
| CI/CD GitHub Actions | CLAUDE-DEPLOYMENT.md |
| Sistema licenze | CLAUDE-DEPLOYMENT.md |

---

## 📊 DIPENDENZE TRA FILE

```
CLAUDE.md (Orchestrator)
    │
    ├── CLAUDE-INDEX.md (Navigazione)
    │
    ├── CLAUDE-BACKEND.md
    │       └── Schema DB usato da tutti
    │
    ├── CLAUDE-FRONTEND.md
    │       └── Dipende da DESIGN-SYSTEM
    │
    ├── CLAUDE-DESIGN-SYSTEM.md
    │       └── Usato da FRONTEND
    │
    ├── CLAUDE-INTEGRATIONS.md
    │       └── Dipende da BACKEND (API)
    │
    ├── CLAUDE-VOICE.md
    │       └── Dipende da BACKEND + INTEGRATIONS
    │
    ├── CLAUDE-FATTURE.md
    │       └── Dipende da BACKEND (clienti, servizi)
    │
    └── CLAUDE-DEPLOYMENT.md
            └── Dipende da tutto (build finale)
```

---

## 🔢 ORDINE LETTURA CONSIGLIATO

### Prima Volta (Setup)
1. CLAUDE.md
2. CLAUDE-INDEX.md (questo)
3. CLAUDE-BACKEND.md (schema DB)
4. CLAUDE-DESIGN-SYSTEM.md (tokens)
5. CLAUDE-FRONTEND.md (componenti)

### Sviluppo Quotidiano
1. CLAUDE.md (stato corrente)
2. File specifico per il task

### Debug/Review
1. CLAUDE.md
2. Tutti i file rilevanti al bug

---

## 📝 CONVENZIONI DOCUMENTAZIONE

### Struttura Standard File CLAUDE-*.md

```markdown
# 🏷️ TITOLO

> Descrizione breve (1 riga)

---

## 📋 Indice
- Sezione 1
- Sezione 2
- ...

---

## Sezione 1
Contenuto...

---

## Sezione 2
Contenuto...

---

## 🔗 File Correlati
- Link ad altri file

---

*Ultimo aggiornamento: YYYY-MM-DDTHH:MM:SS*
```

### Codice nei File

- **TypeScript/React**: Blocchi ```tsx
- **Rust**: Blocchi ```rust
- **SQL**: Blocchi ```sql
- **Bash**: Blocchi ```bash
- **JSON**: Blocchi ```json

---

## 🚀 QUICK LINKS

| Risorsa | Path Relativo |
|---------|---------------|
| Master Prompt | `../../CLAUDE.md` |
| Variabili Env | `../../.env` |
| Design Bible | `../FLUXION-DESIGN-BIBLE.md` |
| Agenti | `../../.claude/agents/` |
| Sessioni | `../sessions/` |

---

*Ultimo aggiornamento: 2025-12-28T18:00:00*
