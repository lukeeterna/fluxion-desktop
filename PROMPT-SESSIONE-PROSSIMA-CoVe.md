# PROMPT SESSIONE CoVe DETERMINISTICA - Gestione Sviluppo Distribuito

**Data:** 2026-02-19  
**Obiettivo:** Ottimizzare workflow sviluppo MacBook (dev) → iMac (build)  
**Metodologia:** Chain of Verification (CoVe) - Reddit-verified practices  

---

## 🚨 PROBLEMATICHE EMERSE SESSIONE PRECEDENTE

### 1. SSH Instabilità
- Connessione SSH a iMac (192.168.1.2) cade dopo timeout lunghi
- Build su iMac richiede 20-30 minuti, supera timeout shell
- Processo background su iMac non sempre tracciabile

### 2. Version Mismatch Ambiente
| Componente | MacBook | iMac | Stato |
|------------|---------|------|-------|
| macOS | 11.7.10 | 12.7.4 | ❌ Incompatibile Tauri 2.x |
| Node.js | 22.14.0 | 20.11.0 | ⚠️ Diversi |
| Tauri | Non builda | 2.10.2 | ✅ Solo iMac |
| Rust | Installato | 1.92.0 | ✅ OK |

### 3. Crash MacBook con Tauri 2.x
- Errore: `WKUIDelegate webView:requestMediaCapturePermissionForOrigin` non trovato
- macOS 11 non supporta API richieste da Tauri 2.x
- Downgrade a Tauri 1.x richiede 4-6 ore di refactoring

### 4. Sync Codice
- File modificati su MacBook devono essere pushati su GitHub
- iMac deve fare pull prima del build
- Rischi di conflitti se non sincronizzato

---

## 🎯 OBIETTIVO SESSIONE

**Definire e implementare workflow ottimale per:**
1. Sviluppo frontend (React/TS) su MacBook
2. Build Tauri (Rust) su iMac 
3. Testing Voice Agent su entrambi
4. Zero downtime, zero conflitti

---

## 🔧 FASE 1: DEEP RESEARCH CoVe (OBBLIGATORIA)

### Research Topics (verificare su Reddit/StackOverflow/GitHub):

**1. Remote Development Workflows**
```
- "develop on macbook build on remote mac ssh"
- "tauri remote build ssh github actions"
- "macos development distributed build farm"
```

**2. SSH Persistence Solutions**
```
- "tmux vs screen vs nohup long running builds"
- "ssh keep alive build process detached"
- "remote build notification when complete"
```

**3. Git Sync Strategies**
```
- "git workflow multiple development machines"
- "pre-commit hooks cross platform macbook imac"
- "git auto sync between two computers"
```

**4. Tauri Cross-Compilation**
```
- "tauri build on different machine than development"
- "tauri ci cd github actions self hosted runner"
- "tauri remote compilation macos"
```

---

## 📋 FASE 2: LETTURA FILE CONTESTO (OBBLIGATORIA)

**Prima di qualsiasi azione, leggi:**

1. **AGENTS.md** - Convenzioni progetto
2. **README.md** - Setup e architettura
3. **src-tauri/Cargo.toml** - Dipendenze Rust
4. **package.json** - Dipendenze Node
5. **.github/workflows/release-full.yml** - Pipeline CI/CD
6. **voice-agent/main.py** - Configurazione Voice Agent
7. **PROMPT-SESSIONE-2026-02-11.md** - Contesto sessione precedente

---

## 🔬 FASE 3: ANALISI STATO ATTUALE

### Verifiche deterministiche da eseguire:

```bash
# 1. Stato Git su MacBook
git status
git log --oneline -5

# 2. Stato Git su iMac (via SSH)
ssh gianlucadistasi@192.168.1.2 "cd '/Volumes/MacSSD - Dati/fluxion' && git status && git log --oneline -3"

# 3. Processi attivi su iMac
ssh gianlucadistasi@192.168.1.2 "pgrep -f 'tauri|cargo|voice' | head -10"

# 4. Voice Agent status
curl -s http://192.168.1.2:3002/health | jq .

# 5. Spazio disco iMac
ssh gianlucadistasi@192.168.1.2 "df -h / | tail -1"
```

---

## 🛠️ FASE 4: IMPLEMENTAZIONE WORKFLOW OTTIMALE

### Opzioni da valutare (basate su research):

**OPZIONE A: Git-Centric Workflow**
```
MacBook:        GitHub:         iMac:
  dev ──push──►  repo  ◄──pull── build
  test ◄──────── web ─────────► deploy
```

**OPZIONE B: Shared Folder (NFS/SSHFS)**
```
MacBook monta /Volumes/MacSSD-Imac/ via SSHFS
Sviluppo locale, build remoto sullo stesso filesystem
```

**OPZIONE C: GitHub Actions Self-Hosted**
```
iMac come runner GitHub Actions
Build automatico su push da MacBook
```

**OPZIONE D: Docker Remote (se supportato)**
```
Container Rust su iMac
MacBook controlla via docker context
```

---

## ✅ CRITERI DI SUCCESSO (CoVe Gates)

| # | Gate | Verifica | Stato |
|---|------|----------|-------|
| 1 | Research completata | Almeno 3 fonti Reddit/StackOverflow | ⬜ |
| 2 | File contesto letti | Tutti i 7 file elencati | ⬜ |
| 3 | Stato attuale verificato | SSH, Git, processi OK | ⬜ |
| 4 | Workflow scelto | Decisione documentata | ⬜ |
| 5 | Implementazione testata | Build funzionante su iMac | ⬜ |
| 6 | Sync testato | Modifica MacBook → build iMac | ⬜ |

---

## 📝 PROCEDURA ESECUZIONE

### Step 1: Research (15 min)
- Cerca su Reddit i workflow elencati sopra
- Documenta soluzioni trovate
- Identifica best practices

### Step 2: Analisi (10 min)
- Leggi tutti i file contesto
- Verifica stato attuale su entrambi i Mac
- Identifica blocker

### Step 3: Decisione (5 min)
- Scegli workflow ottimale
- Documenta pro/contro
- Ottieni conferma utente

### Step 4: Implementazione (30-60 min)
- Configura workflow scelto
- Testa sincronizzazione
- Verifica build funzionante

### Step 5: CoVe Verification (10 min)
- Tutti i 6 gate devono essere ✅
- Documenta risultati
- Crea checklist per sessioni future

---

## ⚠️ BLOCKER NOTE

**Se si verificano:**
- SSH non risponde → Verifica `sudo systemsetup -setremotelogin on` su iMac
- Git conflitti → Usa `git stash` / `git reset --hard origin/master`
- Build fallisce → Verifica spazio disco: `df -h`
- Voice Agent down → Riavvia: `cd voice-agent && python main.py --port 3002`

---

## 🎯 OUTPUT ATTESO

1. **Report Research:** Riassunto fonti Reddit con link
2. **Decisione Documentata:** Workflow scelto con motivazione
3. **Configurazione Implementata:** Script/comandi per il workflow
4. **Test Passed:** Build completata con successo su iMac
5. **Guida Futura:** Istruzioni step-by-step per prossime sessioni

---

```
╔═══════════════════════════════════════════════════════════════╗
║  MISSION: Workflow Ottimale MacBook → iMac                   ║
║  METHODOLOGY: CoVe Deterministic                              ║
║  SUCCESS CRITERIA: 6/6 gates passati                         ║
╚═══════════════════════════════════════════════════════════════╝
```

**PRONTO PER ESECUZIONE CoVe.**
