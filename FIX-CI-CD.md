# 🔧 FIX CI/CD ERRORS - ISTRUZIONI PER iMAC

**Data**: 2026-01-03
**Commit**: ca9b619
**Workflow**: https://github.com/lukeeterna/fluxion-desktop/actions/runs/20677085870

---

## ❌ ERRORI RILEVATI

### 1. Code Quality - Rust Formatting Failed
```
cargo fmt --check
```
**Causa**: Codice Rust non formattato secondo rustfmt

### 2. Backend Tests - Domain Layer Tests Failed
```
cargo test --lib -- domain::
```
**Causa**: Test di dominio falliscono (probabilmente errori compilazione)

### 3. Build Tauri - Debug Build Failed
```
npm run tauri build -- --debug
```
**Causa**: App non compila (dipende da errori Rust)

---

## ✅ SOLUZIONE (ESEGUIRE SU iMAC)

### Step 1: Sync Repository
```bash
cd /Volumes/MacSSD\ -\ Dati/FLUXION
git pull origin master
```

### Step 2: Format Rust Code
```bash
cd src-tauri
cargo fmt
cd ..
```

### Step 3: Check TypeScript (già OK)
```bash
npm run type-check
```
**Expected**: ✅ Dovrebbe passare (frontend tests passed su CI)

### Step 4: Run Tests Locally
```bash
cd src-tauri
cargo test --lib -- domain::
```

**Se fallisce**: Leggi errori e risolvi

### Step 5: Verify Build
```bash
npm run tauri build -- --debug
```

**Expected**: ✅ Dovrebbe compilare senza errori

### Step 6: Commit Fixed Code
```bash
git add src-tauri/
git commit -m "fix: format Rust code with cargo fmt

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push origin master
```

### Step 7: Verify CI Passes
Vai su: https://github.com/lukeeterna/fluxion-desktop/actions

Attendi ~8 minuti per workflow completion.

**Expected result**: Tutti i job ✅ verdi

---

## 🚨 SE TESTS FALLISCONO

### Scenario A: Errori Compilazione Rust

```bash
cd src-tauri
cargo build
```

Leggi errori output e fixa.

Possibili cause:
- Import mancanti
- Syntax errors
- Type mismatches

### Scenario B: Tests Falliscono

```bash
cargo test --lib -- domain:: --nocapture
```

Leggi quale test fallisce e perché.

Possibili cause:
- Logic errors in domain layer
- Assertion failures
- Panic in test

### Scenario C: Build Tauri Fallisce

```bash
npm run tauri build -- --debug 2>&1 | tee build-errors.txt
```

Analizza `build-errors.txt` per errori specifici.

---

## 📋 CHECKLIST PRE-PUSH

- [ ] `cargo fmt` eseguito
- [ ] `cargo test --lib` passa ✅
- [ ] `cargo build` passa ✅
- [ ] `npm run type-check` passa ✅
- [ ] `npm run tauri build -- --debug` passa ✅

Se tutti ✅, puoi fare `git push` con confidenza.

---

## 🔄 WORKFLOW COMPLETO (COPIA-INCOLLA)

```bash
# 1. Sync
cd /Volumes/MacSSD\ -\ Dati/FLUXION
git pull origin master

# 2. Format + Test
cd src-tauri
cargo fmt
cargo test --lib
cargo build
cd ..

# 3. Verify frontend
npm run type-check

# 4. Build Tauri
npm run tauri build -- --debug

# 5. Se tutto OK, commit
git add .
git commit -m "fix: format Rust code and verify all tests pass"
git push origin master

# 6. Verifica CI
# https://github.com/lukeeterna/fluxion-desktop/actions
```

---

## 📞 SUPPORTO

Se hai bisogno di aiuto, dimmi:
1. Quale step fallisce
2. L'errore completo (copia output)
3. Screenshot se necessario

Claude Code ti aiuterà a risolvere! 🚀
