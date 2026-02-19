# 🎯 Piano di Esecuzione Deterministica

> Ogni step ha: **Input** → **Azione** → **Verifica** → **Fallback**

---

## FASE 1: Pre-condizioni MacBook (Da fare ora)

### Step 1.1: Verifica Git Status
```bash
# INPUT: Directory /Volumes/MontereyT7/FLUXION
cd /Volumes/MontereyT7/FLUXION
git status --short

# CRITERIO DI SUCCESSO: Output vuoto o solo PROMPT-SESSIONE-PROSSIMA-CoVe.md
# FALLBACK: Se ci sono modifiche non committate:
#   git add -A
#   git commit -m "sync: Pre-workflow-setup"
```

### Step 1.2: Verifica Type-Check
```bash
# AZIONE
npm run type-check

# CRITERIO DI SUCCESSO: 0 errori o errori già noti (non nuovi)
# FALLBACK: Se nuovi errori:
#   - Correggere errori TypeScript
#   - Ripetere type-check
```

### Step 1.3: Test Script Sync
```bash
# AZIONE
./scripts/sync-to-imac.sh --help

# CRITERIO DI SUCCESSO: Visualizza help dello script
# FALLBACK: Se permesso negato:
#   chmod +x scripts/sync-to-imac.sh
```

**CHECKPOINT 1**: ✅ MacBook pronto per push

---

## FASE 2: Setup iMac (Da fare sull'iMac)

### Step 2.1: Accesso Fisico iMac
```bash
# INPUT: Login all'iMac come gianlucadistasi
# AZIONE: Apri Terminal.app

# VERIFICA: whoami restituisce "gianlucadistasi"
# FALLBACK: Se utente diverso, switch user o adatta path
```

### Step 2.2: Verifica Rust Installato
```bash
# AZIONE
cargo --version
rustc --version

# CRITERIO DI SUCCESSO: Entrambi i comandi restituiscono versione
# OUTPUT ATTESO: cargo 1.x.x, rustc 1.x.x

# FALLBACK: Se non trovato:
#   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
#   source $HOME/.cargo/env
```

### Step 2.3: Verifica Node.js
```bash
# AZIONE
node --version
npm --version

# CRITERIO DI SUCCESSO: node v18+ o v20+
# FALLBACK: Se non trovato:
#   brew install node
#   oppure scarica da nodejs.org
```

### Step 2.4: Clone Repository
```bash
# AZIONE
cd "/Volumes/MacSSD - Dati"
git clone https://github.com/lukeeterna/fluxion-desktop.git fluxion

# CRITERIO DI SUCCESSO: Directory fluxion creata con contenuto .git
# VERIFICA: ls -la fluxion/.git

# FALLBACK: Se directory esiste già:
#   cd fluxion
#   git status
```

### Step 2.5: Installazione Dipendenze
```bash
# AZIONE
cd "/Volumes/MacSSD - Dati/fluxion"
npm install

# CRITERIO DI SUCCESSO: node_modules/ creato
# VERIFICA: ls node_modules | head -5

# FALLBACK: Se errori:
#   rm -rf node_modules package-lock.json
#   npm install
```

### Step 2.6: Setup Script Build
```bash
# AZIONE
cp scripts/setup-imac-build.sh .
./setup-imac-build.sh

# CRITERIO DI SUCCESSO: Script build-fluxion.sh creato ed eseguibile
# VERIFICA: ls -la build-fluxion.sh
```

**CHECKPOINT 2**: ✅ iMac configurato per build

---

## FASE 3: Primo Build di Test (iMac)

### Step 3.1: Type-Check
```bash
# AZIONE
cd "/Volumes/MacSSD - Dati/fluxion"
npm run type-check

# CRITERIO DI SUCCESSO: Passa senza errori (come su MacBook)
# FALLBACK: Se errori diversi dal MacBook:
#   - Verificare versione Node (devono coincidere)
#   - npm install per allineare dipendenze
```

### Step 3.2: Cargo Check
```bash
# AZIONE
cd src-tauri
cargo check --lib

# CRITERIO DI SUCCESSO: Compila senza errori
# TEMPO ATTESO: 30-120 secondi (prima volta)
# FALLBACK: Se errori:
#   cargo clean
#   cargo check --lib
```

### Step 3.3: Build Tauri
```bash
# AZIONE
cd "/Volumes/MacSSD - Dati/fluxion"
npm run tauri build

# CRITERIO DI SUCCESSO: Bundle creato in src-tauri/target/release/bundle/
# TEMPO ATTESO: 5-15 minuti (prima volta, include compilazione Rust)
# OUTPUT ATTESO: 
#   - src-tauri/target/release/bundle/dmg/*.dmg
#   - src-tauri/target/release/bundle/macos/*.app

# FALLBACK: Se fallisce:
#   1. Leggi errore specifico
#   2. cargo clean && npm run tauri build
#   3. Se persiste: verifica Xcode Command Line Tools
```

**CHECKPOINT 3**: ✅ Build Tauri funzionante

---

## FASE 4: Workflow di Sviluppo Quotidiano

### Ciclo Standard

```bash
# MACBOOK
# =======
# 1. Modifica codice
# 2. Commit
git add -A
git commit -m "feat: descrizione"

# 3. Push
./scripts/sync-to-imac.sh

# IMAC (fisico o istruzioni)
# ==========================
# 1. Pull
git pull origin master

# 2. Build
./build-fluxion.sh

# 3. Test bundle
open src-tauri/target/release/bundle/macos/Fluxion.app
```

---

## FASE 5: Verifiche Post-Implementazione

### Test 1: Git Sync
```bash
# MacBook: modifica test
echo "// Test $(date)" >> src/test.txt
git add -A
git commit -m "test: sync verification"
git push origin master

# iMac: verifica ricezione
git pull origin master
cat src/test.txt

# CRITERIO: File ricevuto correttamente
# CLEANUP: git revert HEAD && git push
```

### Test 2: Build Idempotente
```bash
# iMac: esegui build 2 volte
./build-fluxion.sh
./build-fluxion.sh

# CRITERIO: Seconda build riusa cache, completa più velocemente
```

### Test 3: Rollback
```bash
# MacBook: crea commit test
git add -A && git commit -m "test: rollback" && git push

# iMac: pull e verifica
git pull

# Rollback
git revert HEAD
./build-fluxion.sh

# CRITERIO: Build funziona dopo revert
```

**CHECKPOINT FINALE**: ✅ Workflow deterministico verificato

---

## 📋 Matrice di Decisione

| Condizione | Azione Deterministica |
|------------|----------------------|
| Type-check fallito | STOP → Correggi errori → Ripeti |
| Git push fallito | STOP → Verifica remote → Riprova |
| Cargo check fallito | `cargo clean` → Riprova |
| Build Tauri fallito | Leggi errore → Fix specifico → Riprova |
| iMac offline | Attendi → Retry o build manuale successiva |
| Node version mismatch | Allinea versioni (preferibilmente v20 LTS) |

---

## ⏱️ Timeline Stimata

| Fase | Tempo | Dipendenze |
|------|-------|------------|
| 1: Pre-condizioni MacBook | 5 min | - |
| 2: Setup iMac | 15-30 min | Accesso fisico iMac |
| 3: Primo build | 10-20 min | Fase 2 completata |
| 4: Test workflow | 10 min | Fase 3 completata |
| **TOTALE** | **40-65 min** | **Accesso fisico iMac** |

---

## 🚨 Condizioni di Abort

Abortire e richiedere assistenza se:
1. ❌ iMac non ha Rust installato E installazione fallisce
2. ❌ Errore di permessi su "/Volumes/MacSSD - Dati" non risolvibile
3. ❌ Build Tauri fallisce dopo 3 tentativi con `cargo clean`
4. ❌ Errori di linking macOS (richiedono Xcode)

---

*Piano deterministico - ogni step è reversibile e verificabile*
