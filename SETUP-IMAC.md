# 🖥️ Setup iMac per FLUXION

## 📍 Configurazione Completata su MacBook

✅ Repository GitHub creato: `lukeeterna/fluxion-desktop` (privato)
✅ .gitignore configurato
✅ Commit iniziale pushato
✅ Remote configurato con token

---

## 🚀 Setup Veloce iMac (copia e incolla tutto)

Apri il Terminale sull'iMac ed esegui:

```bash
# 1. Vai nella directory SSD locale
cd "/Volumes/MacSSD - Dati"

# 2. Se esiste già una copia vecchia, cancellala
rm -rf fluxion

# 3. Clona il repository da GitHub
git clone https://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@github.com/lukeeterna/fluxion-desktop.git fluxion

# 4. Entra nella directory
cd fluxion

# 5. Copia il file .env (IMPORTANTE!)
# Copia il file .env dal disco MontereyT7 se è collegato:
cp "/Volumes/MontereyT7/FLUXION/.env" .env

# 6. Installa dipendenze Node (ci vorrà qualche minuto)
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

# Sincronizza modifiche da GitHub
git pull

# Testa l'app
npm run tauri dev
```

---

## ⚠️ Note Importanti

1. **File .env**: NON è su GitHub (escluso da .gitignore). Devi copiarlo manualmente dal disco MontereyT7
2. **node_modules/**: NON è su GitHub. Dopo ogni clone devi eseguire `npm install`
3. **target/**: La directory Rust viene rigenerata automaticamente al primo build
4. **SSD locale**: Lavora SEMPRE su SSD locale (`/Volumes/MacSSD - Dati/fluxion`), NON su disco esterno USB

---

## 🆘 Problemi Comuni

### "npm install" fallisce
```bash
# Pulisci cache e riprova
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### "git pull" chiede credenziali
Il token è già nell'URL del remote. Se chiede password:
```bash
git remote set-url origin https://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@github.com/lukeeterna/fluxion-desktop.git
```

### Build Rust fallisce
```bash
cd src-tauri
cargo clean
cargo build
```

---

## 📊 Verifica Setup

Dopo il setup, verifica che tutto funzioni:

```bash
cd "/Volumes/MacSSD - Dati/fluxion"

# Controlla versione Node (deve essere >= 18)
node --version

# Controlla Rust
rustc --version

# Controlla dipendenze
npm list --depth=0

# Avvia app
npm run tauri dev
```

Se vedi la finestra dell'app aprirsi, il setup è completo! ✅

---

*Generato il 2025-12-31*
