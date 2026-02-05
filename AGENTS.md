# AGENTS.md - Istruzioni per Agenti AI

> **⚠️ REGOLA FONDAMENTALE**: Questo file DEVE essere consultato prima di qualsiasi azione significativa sul progetto.

---

## 🔄 Prassi di Verifica Post-Modifica (CRITICA)

### **REGOLA D'ORO**
> **DOPO ogni modifica o implementazione, MAI suggerire comandi di build o deploy senza prima completare la fase di verifica.**

### Flusso Obbligatorio

```
┌─────────────────────────────────────────────────────────────────┐
│  1. IMPLEMENTAZIONE                                              │
│     └─> Modifiche al codice (Rust, TypeScript, ecc.)            │
├─────────────────────────────────────────────────────────────────┤
│  2. VERIFICA LOCALE (MUST HAVE)                                  │
│     ├─> TypeScript: npm run type-check                          │
│     ├─> Rust: cargo check --lib && cargo test --lib             │
│     ├─> Lint: npm run lint                                      │
│     └─> Formattazione: cargo fmt --check                        │
├─────────────────────────────────────────────────────────────────┤
│  3. TEST E2E/INTEGRAZIONE                                        │
│     ├─> npm run test:e2e (se disponibile)                       │
│     └─> Verifica manuale dei flussi critici                     │
├─────────────────────────────────────────────────────────────────┤
│  4. SOLO DOPO VERIFICA OK                                        │
│     └─> Puoi suggerire build produzione / deploy                │
└─────────────────────────────────────────────────────────────────┘
```

### Checklist Pre-Build

**Prima di suggerire `npm run tauri build` o `cargo build --release`:**

- [ ] `npm run type-check` passa senza errori
- [ ] `cargo check --lib` passa senza errori  
- [ ] Tutti i test Rust passano (`cargo test --lib`)
- [ ] Nessun errore di lint critico
- [ ] File modificati sono stati formattati

**Se la checklist NON è completa:**
1. NON suggerire comandi di build
2. Elenca i problemi trovati
3. Proponi fix per i problemi
4. Solo dopo il fix, procedi alla build

---

## 📋 Comandi di Verifica Rapida

### Stack Tauri (FLUXION)

```bash
# 1. TypeScript type check
npm run type-check

# 2. Rust check
pushd src-tauri && cargo check --lib && popd

# 3. Test Rust
pushd src-tauri && cargo test --lib && popd

# 4. Lint
npm run lint

# 5. Build DEV (con hot reload)
npm run tauri dev

# 6. Build PRODUZIONE (SOLO dopo verifica OK)
npm run tauri build
```

---

## 🚫 Anti-Pattern da EVITARE

### ❌ SBAGLIATO
```
Utente: "Ho modificato il codice"
Agente: "Ecco il comando per buildare: npm run tauri build"
```

### ✅ CORRETTO
```
Utente: "Ho modificato il codice"
Agente: "Prima verifichiamo che tutto sia OK..."
       [esegue type-check, cargo check, test]
       "Ci sono 34 errori TypeScript da risolvere prima del build"
```

---

## 🔍 Esempio Pratico

### Scenario: Fix SQLx Migration

```bash
# 1. Fix applicati al codice
# 2. VERIFICA immediata:
ssh imac "cd project && cargo check --lib"
# Output: error[E0382]: borrow of partially moved value...

# 3. FIX iterativi finché non passa
# 4. SOLO quando: "Finished dev profile..."
# 5. Allora e solo allora: "Build pronta per produzione? Ecco i comandi..."
```

---

## 📝 Note per il Progetto FLUXION

### Stato Attuale CI/CD
- Build Rust: ✅ Funzionante
- TypeScript: ❌ 34+ errori (bloccanti)
- E2E Tests: ⚠️ Da verificare

### Priorità Pre-Produzione
1. Fix errori TypeScript (34 errori)
2. Creare componenti UI mancanti (slider, radio-group)
3. Allineare tipi TypeScript/Rust
4. Setup certificati Apple (per notarizzazione)

---

## ⚙️ Convenzioni Codice

### Rust
- Usare `cargo fmt` per formattazione
- `#![warn(clippy::all)]` abilitato
- Errori di borrow checker: usare `.clone()` o `.unwrap_or_else()`

### TypeScript/React
- Strict mode abilitato
- No `any` impliciti
- Componenti in `src/components/`
- Hooks in `src/hooks/`
- Types in `src/types/`

---

## 🔗 Risorse

- Documentazione Tauri: https://tauri.app/
- Rust Book: https://doc.rust-lang.org/book/
- TypeScript Handbook: https://www.typescriptlang.org/docs/

---

*Ultimo aggiornamento: 2026-02-05*
*Regola Verifica Post-Modifica aggiunta dopo incidente build*
