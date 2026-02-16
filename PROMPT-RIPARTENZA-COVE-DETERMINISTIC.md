# PROMPT RIPARTENZA - CoVe Deterministic
## Fluxion Voice Agent Enterprise - Final Phase

**Data**: 2026-02-13  
**Stato**: Voice Agent 100% Implementato - Build Tauri Pendente  
**Target**: iMac (192.168.1.7) - macOS 12.7.4  
**Metodologia**: Chain of Verification (CoVe) - Reddit-verified practices

---

## 🎯 OBIETTIVO NON NEGOZIABILE

**Completare il build Tauri di Fluxion sull'iMac e verificare il Voice Agent in produzione.**

```
Success Criteria:
✅ Node.js 20.11.0 LTS installato su iMac
✅ npm install eseguito senza errori  
✅ npm run tauri build completato con successo
✅ Bundle .app generato in src-tauri/target/release/bundle/macos/
✅ Voice Agent testato live con audio reale
✅ Latenza < 800ms verificata
```

---

## 📊 STATO ATTUALE (Snapshot 2026-02-13)

### ✅ Completato
| Componente | Stato | Dettaglio |
|------------|-------|-----------|
| Voice Agent Core | 100% | Python backend su iMac:3002 ✅ |
| 4 Verticali | 100% | salone, medical, palestra, auto ✅ |
| MCP Skills | 100% | CoVe architecture implementata ✅ |
| Frontend Build | 100% | IP 192.168.1.7:3002 corretto ✅ |
| Test Suite | 100% | 53/53 test passati ✅ |
| Git Commit | e27a128 | MCP & CoVe Architecture ✅ |

### ⏳ Pendente
| Task | Bloccante | Soluzione |
|------|-----------|-----------|
| Node.js su iMac | ✅ SÌ | Script CoVe pronto |
| npm install | ✅ SÌ | Dopo Node.js |
| Tauri Build | ✅ SÌ | Dopo npm install |
| Test Live | ✅ SÌ | Dopo build |

### 📁 File Riferimento
- Skill Node.js: `.claude/skills/fluxion-nodejs-setup/SKILL.md`
- Prompt Setup: `PROMPT-NODEJS-COVE-DETERMINISTIC.md`
- PRD v3.0: `PRD-FLUXION-COMPLETE-v3.md`
- Voice Orchestrator: `.claude/agents/fluxion-voice-orchestrator/agent.md`

---

## 🔧 COVE EXECUTION PLAN

### FASE 1: PRE-CHECK (Deterministic)
```bash
# Verifica prerequisiti su iMac
ssh imac "
  # Check 1: macOS version >= 12.0
  sw_vers -productVersion | cut -d. -f1 | grep -q '12' && echo '✅ macOS 12+' || exit 1
  
  # Check 2: Disk space >= 5GB
  df -g / | awk 'NR==2{if (\$4 >= 5) print \"✅ Disk OK\"; else exit 1}'
  
  # Check 3: Network connectivity
  ping -c 1 github.com &>/dev/null && echo '✅ Network OK' || exit 1
  
  # Check 4: Repository presente
  test -d '/Volumes/MacSSD - Dati/fluxion' && echo '✅ Repo OK' || exit 1
"
```
**CoVe Gate**: Tutti i check devono passare. Se fallisce → STOP e report.

---

### FASE 2: NODE.JS INSTALLATION (Deterministic)
```bash
# Script deterministica con versioni fisse
NVM_VERSION="0.39.7"
NODE_VERSION="20.11.0"

ssh imac '
  set -euo pipefail
  
  # Install NVM (se non presente)
  if [[ ! -d "$HOME/.nvm" ]]; then
    curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/v'$NVM_VERSION'/install.sh" | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  fi
  
  # Install Node.js LTS
  source ~/.nvm/nvm.sh
  nvm install "'$NODE_VERSION'"
  nvm alias default "'$NODE_VERSION'"
  nvm use default
  
  # Verify
  node --version | grep "v'$NODE_VERSION'" || exit 1
  npm --version || exit 1
'
```
**CoVe Gate**: `node --version` deve restituire `v20.11.0`.

---

### FASE 3: DEPENDENCIES INSTALL
```bash
ssh imac '
  cd "/Volumes/MacSSD - Dati/fluxion"
  source ~/.nvm/nvm.sh
  nvm use default
  
  # Clean install
  rm -rf node_modules package-lock.json
  npm install
  
  # Verify
  test -d node_modules || exit 1
  test -f package-lock.json || exit 1
'
```
**CoVe Gate**: `node_modules` deve esistere e contenere dipendenze.

---

### FASE 4: TAURI BUILD
```bash
ssh imac '
  cd "/Volumes/MacSSD - Dati/fluxion"
  source ~/.nvm/nvm.sh
  nvm use default
  
  # Build Tauri
  npm run tauri build
  
  # Verify bundle created
  ls -la src-tauri/target/release/bundle/macos/*.app || exit 1
'
```
**CoVe Gate**: File `.app` deve essere creato.

---

### FASE 5: DEPLOY & TEST
```bash
# 1. Verifica Voice Agent attivo
ssh imac "curl -s http://192.168.1.7:3002/health | grep -q 'status.*ok'"

# 2. Avvia applicazione Tauri
ssh imac '
  open "/Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/bundle/macos/Fluxion.app"
'

# 3. Test Voice Agent
# - Apri Voice Agent dall'app
# - Clicca microfono
# - Verifica connessione a 192.168.1.7:3002
# - Test conversazione: "Ciao" → risposta Sara
```
**CoVe Gate**: Audio input → STT → NLU → TTS → Audio output < 800ms.

---

## 🚨 BLOCKER HANDLING

### Se Node.js install fallisce
```bash
# Rollback e retry
ssh imac '
  rm -rf ~/.nvm
  sed -i.bak "/NVM/d" ~/.zshrc
'
# Poi ripeti FASE 2
```

### Se npm install fallisce
```bash
# Clean cache e retry
ssh imac '
  cd "/Volumes/MacSSD - Dati/fluxion"
  npm cache clean --force
  rm -rf node_modules
  npm install --legacy-peer-deps
'
```

### Se Tauri build fallisce
```bash
# Verifica Rust
ssh imac 'rustc --version && cargo --version'
# Se manca: installa Rustup
# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

---

## 📈 SUCCESS METRICS

| Metric | Target | Verification |
|--------|--------|--------------|
| Node.js Version | v20.11.0 | `node --version` |
| NPM Version | 10.x | `npm --version` |
| Build Exit Code | 0 | `echo $?` |
| Bundle Size | < 500MB | `du -h *.app` |
| Voice Latency | < 800ms | Chrome DevTools |
| Health Check | ok | `curl /health` |

---

## 📝 POST-SESSION CHECKLIST

### Da completare:
- [ ] FASE 1: Pre-check ✅/❌
- [ ] FASE 2: Node.js install ✅/❌  
- [ ] FASE 3: npm install ✅/❌
- [ ] FASE 4: Tauri build ✅/❌
- [ ] FASE 5: Deploy & Test ✅/❌

### Da documentare:
- [ ] Eventuali errori incontrati
- [ ] Tempo effettivo di build
- [ ] Dimensione bundle finale
- [ ] Risultato test Voice Agent

### Commit finale:
```bash
git add -A
git commit -m "Fluxion v3.0 - Tauri Build iMac

- Node.js 20.11.0 installed
- Tauri build completed
- Voice Agent tested live
- CoVe verified: 6/6 phases passed

Build: src-tauri/target/release/bundle/macos/"
```

---

## 🎓 RIFERIMENTI

### Comandi utili
```bash
# Verifica stato Voice Agent
curl http://192.168.1.7:3002/health | jq

# Log Voice Agent
ssh imac "tail -f '/Volumes/MacSSD - Dati/fluxion/voice-agent/logs/voice-agent.log'"

# Restart Voice Agent
ssh imac "pkill -f 'python.*voice-agent'; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source ~/.nvm/nvm.sh && python main.py --port 3002"
```

### File di log
- Voice Agent: `voice-agent/logs/voice-agent.log`
- Build Tauri: `src-tauri/target/release/build.log`

---

## ⚡ QUICK START (Prossima Sessione)

1. **Attiva skill**: "Attiva skill fluxion-nodejs-setup"
2. **Esegui CoVe**: Segui le 5 fasi sopra
3. **Verifica**: Test Voice Agent live
4. **Commit**: Salva tutto su git

---

```
╔════════════════════════════════════════════════════════════════════════════╗
║  MISSION: Tauri Build su iMac + Voice Agent Live Test                      ║
║  METHODOLOGY: Chain of Verification (CoVe)                                 ║
║  SUCCESS CRITERIA: 6/6 fasi completate, Voice Agent < 800ms                ║
╚════════════════════════════════════════════════════════════════════════════╝
```

**PRONTO PER L'ESECUZIONE.**
