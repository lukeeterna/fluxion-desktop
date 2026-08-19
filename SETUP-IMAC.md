# 🖥️ Setup iMac per FLUXION

## 📍 Configurazione Completata su MacBook

✅ Repository GitHub creato: `lukeeterna/fluxion-desktop`
✅ `.gitignore` configurato
✅ Commit iniziale pushato
✅ Autenticazione GitHub configurata senza credenziali nel repository

---

## 🚀 Setup Veloce iMac

Apri il Terminale sull'iMac ed esegui:

```bash
# 1. Vai nella directory SSD locale
cd "/Volumes/MacSSD - Dati"

# 2. Se esiste già una copia vecchia, cancellala
rm -rf fluxion

# 3. Clona il repository usando le credenziali GitHub già configurate
# Preferito: `gh auth login` / credential manager. Mai inserire token nell'URL o nei file del repo.
git clone https://github.com/lukeeterna/fluxion-desktop.git fluxion

# 4. Entra nella directory
cd fluxion

# 5. Copia il file .env (IMPORTANTE!)
# Copia il file .env dal disco MontereyT7 se è collegato:
cp "/Volumes/MontereyT7/FLUXION/.env" .env
chmod 600 .env

# 6. Installa dipendenze Node
npm install

# 7. Avvia Tauri in development mode
npm run tauri dev
```

---

## 🔄 Workflow Quotidiano

### Su MacBook (sviluppo)
```bash
cd /Volumes/MontereyT7/FLUXION

# Lavori sul codice...
# Quando hai finito:
git add .
git commit -m "Descrizione modifiche"
git push
```

### Su iMac (test)
```bash
cd "/Volumes/MacSSD - Dati/fluxion"

git pull
npm run tauri dev
```

---

## ⚠️ Note Importanti

1. **File `.env`**: NON è su GitHub. Contiene credenziali e deve restare locale, con permessi restrittivi.
2. **Token/API key**: non inserirli mai in URL Git, documentazione, script o commit. Usa GitHub CLI/credential manager, secret store locali e GitHub Actions Secrets.
3. **`node_modules/`**: NON è su GitHub. Dopo ogni clone esegui `npm install`.
4. **`target/`**: la directory Rust viene rigenerata automaticamente al primo build.
5. **SSD locale**: lavora su SSD locale (`/Volumes/MacSSD - Dati/fluxion`), NON su disco esterno USB.

---

## 🆘 Problemi Comuni

### `npm install` fallisce
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### `git pull` chiede credenziali
Configura l'autenticazione fuori dal repository, ad esempio con GitHub CLI:

```bash
gh auth login
git remote set-url origin https://github.com/lukeeterna/fluxion-desktop.git
```

Non salvare token personali nel remote URL.

### Build Rust fallisce
```bash
cd src-tauri
cargo clean
cargo build
```

---

## 📊 Verifica Setup

```bash
cd "/Volumes/MacSSD - Dati/fluxion"
node --version
rustc --version
npm list --depth=0
npm run tauri dev
```

Se vedi la finestra dell'app aprirsi, il setup è completo.

---

*Generato il 2025-12-31; hardening credenziali aggiornato il 2026-08-19.*
