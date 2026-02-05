# AGENTS.md - Istruzioni per Agenti AI (FLUXION)

> **⚠️ REGOLA CRITICA**: Questo file viene caricato AUTOMATICAMENTE ad ogni sessione. Segui SEMPRE le procedure indicate.

---

## 🤖 Skills di Sistema (Auto-Attivazione)

Le seguenti skills sono attive e si attivano automaticamente quando necessario:

### 1. [Fluxion Build Verification](.claude/skills/fluxion-build-verification/SKILL.md)
**Trigger**: Quando l'utente chiede "build", "deploy", "produzione" o si fanno modifiche significative.

**Comportamento**: 
- ESEGUE AUTOMATICAMENTE `npm run type-check` e `cargo check --lib`
- Se errori → STOP, mostra errori, chiede se fixare
- Se OK → può suggerire build

**REGOLA**: MAI suggerire `npm run tauri build` senza verifica preliminare.

### 2. [Fluxion Git Workflow](.claude/skills/fluxion-git-workflow/SKILL.md)
**Trigger**: Dopo fix completati, implementazioni, o quando si dice "pusha".

**Comportamento**:
- Esegue automaticamente git add, commit, push
- Sincronizza anche l'iMac via SSH
- Non chiede conferma, agisce direttamente

---

## 🔄 Procedura di Verifica Pre-Build (Riepilogo)

```
Utente: "Fai il build"
   ↓
Agente: [AUTO] Esegue verifica
   ↓
┌────────────────────────────────────────────────────────┐
│ 1. npm run type-check                                  │
│    └─> Se errori: STOP, mostra errori                 │
│    └─> Se OK: prosegui                                │
├────────────────────────────────────────────────────────┤
│ 2. cargo check --lib                                   │
│    └─> Se errori: STOP, mostra errori                 │
│    └─> Se OK: prosegui                                │
├────────────────────────────────────────────────────────┤
│ 3. Report: "✅ Verifica OK. X errori, Y warning"       │
│    └─> Suggerisci build solo se 0 errori              │
└────────────────────────────────────────────────────────┘
```

---

## 📋 Comandi di Riferimento Rapido

### Verifica
```bash
# TypeScript
npm run type-check

# Rust
cd src-tauri && cargo check --lib

# Test Rust
cd src-tauri && cargo test --lib

# Su iMac (completo)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && npm run type-check && cd src-tauri && cargo check --lib"
```

### Build
```bash
# Dev (con hot reload)
npm run tauri dev

# Produzione (SOLO dopo verifica OK)
npm run tauri build
```

---

## 🚫 Anti-Pattern da EVITARE

### ❌ SBAGLIATO
```
Utente: "Ho modificato il codice, possiamo fare il build?"
Agente: "Sì, ecco il comando: npm run tauri build"
```

### ✅ CORRETTO
```
Utente: "Ho modificato il codice, possiamo fare il build?"
Agente: "Verifico automaticamente lo stato..."
       [esegue type-check e cargo check]
       "Trovati X errori. Li fixo prima?"
       [dopo fix]
       "✅ Verifica OK. Ecco il comando per il build..."
```

---

## 📝 Note Tecniche Progetto

| Aspetto | Dettaglio |
|---------|-----------|
| **Stack** | Tauri (Rust) + React + TypeScript + SQLx |
| **MacBook** | `/Volumes/MontereyT7/FLUXION` (no Rust) |
| **iMac** | `/Volumes/MacSSD - Dati/fluxion` (build) |
| **Repo** | `lukeeterna/fluxion-desktop` |
| **Node** | v18+ richiesto |
| **Rust** | Solo su iMac |

---

## 🆘 Errori Comuni & Soluzioni

### TypeScript
| Errore | Soluzione |
|--------|-----------|
| `Module not found` | Crea componente o installa pacchetto |
| `Type 'string' not assignable` | Aggiungi `as SpecificType` |
| `Cannot find name 'X'` | Importa componente/types |
| `is declared but never read` | Rimuovi import non usato |

### Rust
| Errore | Soluzione |
|--------|-----------|
| `borrow of partially moved` | Usa `.clone()` o `.unwrap_or_else()` |
| `missing field` | Aggiungi campo alla struct/init |
| `trait bound not satisfied` | Implementa trait o usa derive |

---

## 📚 Documentazione Collegata

- [Skill Build Verification](.claude/skills/fluxion-build-verification/SKILL.md)
- [Skill Git Workflow](.claude/skills/fluxion-git-workflow/SKILL.md)
- [Prompt Sessione SQLx Fix](PROMPT-FIX-SQLX-SESSIONE.md)
- [README Progetto](README.md)

---

## ⚙️ Convenzioni Codice

### Rust
- Formattazione: `cargo fmt`
- Lint: `cargo clippy`
- Preferire `unwrap_or_else()` a `unwrap_or()` per String

### TypeScript/React
- Strict mode abilitato
- No `any` impliciti
- Componenti: `PascalCase`
- Hooks: `camelCase` con prefisso `use`
- Types: `PascalCase` con suffisso `Type` o `Props`

---

*Ultimo aggiornamento: 2026-02-05*
*Skills aggiunte per automazione verifica e git workflow*
