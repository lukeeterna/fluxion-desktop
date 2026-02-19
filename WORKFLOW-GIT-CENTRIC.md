# 🔄 Fluxion Git-Centric Workflow

> Workflow ottimizzato per sviluppo cross-device MacBook ↔ iMac dato l'impossibilità di usare SSH stabile.

---

## 📋 Panoramica

```
┌─────────────────┐    git push     ┌─────────────────┐    git pull     ┌─────────────────┐
│                 │ ───────────────>│                 │<────────────────│                 │
│   MacBook Dev   │                 │   GitHub Repo   │                 │   iMac Build    │
│  (Node/TypeScript)│               │ (lukeeterna/    │                 │  (Rust/Tauri)   │
│                 │ <───────────────│  fluxion-desktop)│───────────────>│                 │
└─────────────────┘    git status   └─────────────────┘    build        └─────────────────┘
```

---

## 🚀 Quick Start

### MacBook (Sviluppo)

```bash
# 1. Modifica il codice normalmente
# 2. Committa le modifiche
git add -A
git commit -m "feat: nuova feature"

# 3. Sync con iMac (push + istruzioni)
./scripts/sync-to-imac.sh
```

### iMac (Build)

```bash
# 1. Entra nella directory
cd "/Volumes/MacSSD - Dati/fluxion"

# 2. Pull cambiamenti
git pull origin master

# 3. Installa dipendenze se necessario
npm install

# 4. Build
./build-fluxion.sh
# oppure manualmente:
npm run type-check
cd src-tauri && cargo check --lib
npm run tauri build
```

---

## 📁 Script Disponibili

### MacBook

| Script | Descrizione | Uso |
|--------|-------------|-----|
| `scripts/sync-to-imac.sh` | Push codice + istruzioni | `./scripts/sync-to-imac.sh` |
| `scripts/build-on-imac.sh` | Tenta build remoto o istruzioni | `./scripts/build-on-imac.sh` |

### iMac

| Script | Descrizione | Uso |
|--------|-------------|-----|
| `scripts/setup-imac-build.sh` | Setup iniziale iMac | `./scripts/setup-imac-build.sh` |
| `build-fluxion.sh` | Build completo | `./build-fluxion.sh` |

---

## 🔧 Setup Iniziale

### 1. MacBook (già configurato)

Il MacBook è già configurato con:
- Node.js v22
- Git con credenziali GitHub
- Repository clonato

### 2. iMac (prima configurazione)

Copia ed esegui lo script setup:

```bash
# Sul MacBook, copia lo script
cat scripts/setup-imac-build.sh | pbcopy

# Sull'iMac, incolla e salva come setup.sh, poi esegui
chmod +x setup.sh && ./setup.sh
```

Oppure manualmente:

```bash
# 1. Clona repo
cd "/Volumes/MacSSD - Dati/fluxion"
git clone https://github.com/lukeeterna/fluxion-desktop.git .

# 2. Installa dipendenze
npm install

# 3. Verifica Rust
cargo --version
rustc --version
```

---

## 📝 Workflow Dettagliato

### Scenario 1: Sviluppo Feature

```bash
# MacBook
# =======
git checkout -b feature/nuova-feature
# ... modifica codice ...
./scripts/sync-to-imac.sh

# iMac
# ====
git pull
git checkout feature/nuova-feature
./build-fluxion.sh
```

### Scenario 2: Hotfix

```bash
# MacBook
# =======
git checkout master
git pull origin master
# ... fix urgente ...
git add -A
git commit -m "hotfix: correzione bug"
git push origin master

# iMac
# ====
git checkout master
git pull origin master
./build-fluxion.sh
```

### Scenario 3: Build di Release

```bash
# MacBook - aggiorna versione
npm version patch  # o minor/major
git push origin master --tags

# iMac
# ====
git pull origin master
git fetch --tags
./build-fluxion.sh
# Il bundle avrà la nuova versione
```

---

## ⚠️ Troubleshooting

### SSH non disponibile

**Problema**: `ssh: connect to host 192.168.1.7 port 22: Connection refused`

**Soluzione**: Usare il workflow Git-Centric (questo documento). SSH non è necessario.

Per abilitare SSH futuro:
1. iMac: Preferenze di Sistema > Condivisione
2. Attiva "Accesso remoto"
3. MacBook: `ssh 192.168.1.7` per verificare

### Conflitti di Merge

```bash
# iMac
# ====
git pull origin master
# Se ci sono conflitti:
# 1. Risolvi i file segnati
# 2. git add <file>
# 3. git commit -m "merge: risolti conflitti"
```

### Type-check fallito

```bash
# MacBook - correggi errori
npm run type-check
# Correggi errori TypeScript
./scripts/sync-to-imac.sh
```

---

## 🔐 Sicurezza

### Git Credentials

Usa Git Credential Manager o token:

```bash
# Configura credential helper
git config --global credential.helper osxkeychain

# O usa token nel remote (già configurato)
git remote set-url origin https://<token>@github.com/lukeeterna/fluxion-desktop.git
```

### SSH Key (opzionale)

Per Git via SSH (più sicuro):

```bash
# Genera key
ssh-keygen -t ed25519 -C "email@example.com"

# Copia pubblica su GitHub
cat ~/.ssh/id_ed25519.pub | pbcopy
# → GitHub > Settings > SSH Keys > Add

# Cambia remote
git remote set-url origin git@github.com:lukeeterna/fluxion-desktop.git
```

---

## 📊 Confronto Workflow

| Aspetto | SSHFS | GitHub Actions | Docker Remote | **Git-Centric** |
|---------|-------|----------------|---------------|-----------------|
| Setup | Complesso | Complesso | Molto complesso | **Semplice** |
| Dipende da SSH | Sì | Parzialmente | Sì | **No** |
| Stabilità | Bassa | Media | Media | **Alta** |
| Costo | Gratis | API Key | Setup | **Gratis** |
| Velocità | Lenta | Media | Media | **Veloce** |
| Rollback | Difficile | Sì | Sì | **Sì** |
| Offline work | No | No | No | **Sì (parzialmente)** |

---

## 🎯 Best Practices

1. **Committa spesso**: Piccoli commit frequenti riducono conflitti
2. **Branch per feature**: Isola lo sviluppo
3. **Test type-check**: Prima del push, esegui `npm run type-check`
4. **Tag per release**: Usa `git tag -a v1.0.0 -m "Version 1.0.0"`
5. **Documenta**: Aggiorna questo workflow se cambi processo

---

## 📚 Documentazione Collegata

- [AGENTS.md](AGENTS.md) - Istruzioni per agenti AI
- [INTEGRATION-TAURI-AUTOMATION.md](INTEGRATION-TAURI-AUTOMATION.md) - E2E testing
- [PROMPT-SESSIONE-PROSSIMA-CoVe.md](PROMPT-SESSIONE-PROSSIMA-CoVe.md) - Sessione CoVe originale

---

## 🔬 Research & Fonti

Questo workflow è basato su research da Reddit e StackOverflow:

### SSHFS - Problemi di Stabilità

> "SSHFS has a tendency to crap out occasionally under heavy load. NFS is a little more stable, IMO, but SSHFS can be easier to configure."
> — [r/linuxquestions](https://www.reddit.com/r/linuxquestions/comments/6ub4yw/)

> "SSHFS does not handle concurrency very well, especially when dealing with large files."
> — [r/linuxquestions](https://www.reddit.com/r/linuxquestions/comments/1224qvg/)

### GitHub Actions Self-Hosted - Problemi macOS

> "Github Actions self hosted runner on macOS tries to checkout repository forever"
> — [StackOverflow](https://stackoverflow.com/questions/79881327/)

### Git Workflow Best Practices

> "A better option would be NFS mounts. SSHFS has some issues when the remote connection goes offline or into sleep mode."
> — [r/linux](https://www.reddit.com/r/linux/comments/12lf8g/)

---

*Ultimo aggiornamento: 2026-02-19*
*Workflow: Git-Centric v1.0*
*Research sources: Reddit r/linux, r/linuxquestions, StackOverflow*
