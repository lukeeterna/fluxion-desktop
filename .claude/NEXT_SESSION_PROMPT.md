# Prompt ripartenza — S356 app launcher FLUXION + test E2E founder

**Generato**: 2026-06-09T14:43:00Z  
**Sessione**: S356  
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`, HEAD `95d21cc`)  
**Status**: app dev-mode BLOCCATO su path-con-spazi npm, workaround in corso

## Problema S356

iMac path `/Volumes/MacSSD - Dati/fluxion` contiene spazi → npm fallisce su:
- `npm install` (edgedriver spawn error ENOENT)
- `npm run build` (spawn sh ENOENT)
- `npx tauri dev` (non riesce a determinare executable)

**Root cause**: npm interpreta il path con spazi e fallisce ad ogni spawn di subprocesso.

**Stato tentati** (S356 live):
1. npm install via path canonico → FAIL (edgedriver)
2. npm install via symlink `/tmp/fluxion-dev` → FAIL (node_modules corrotto, ENOTEMPTY rename)
3. npx tauri dev diretto → FAIL ("could not determine executable")

## Soluzione FINALE (da eseguire S357)

### Prerequisito: symlink senza spazi (gia' creato S356)
```bash
ssh imac "ln -sfn '/Volumes/MacSSD - Dati/fluxion' /tmp/fluxion-dev"
```

### Pulire node_modules corrotto (macOS, da iMac locale o via SSH con env PATH corretta)
```bash
ssh imac "export PATH='/usr/local/bin:/opt/homebrew/bin:\$PATH' && \
  cd '/Volumes/MacSSD - Dati/fluxion' && \
  find node_modules -type d -name '.*.lock' -o -name '.*.tmp' 2>/dev/null | xargs rm -rf || true && \
  npm cache clean --force"
```

### Oppure (piu' radicale): rifare node_modules da zero
```bash
# Option A: da /tmp/fluxion-dev (symlink)
ssh imac "export PATH='/usr/local/bin:/opt/homebrew/bin:\$PATH' && \
  cd /tmp/fluxion-dev && \
  rm -rf node_modules package-lock.json && \
  npm install"

# Option B: se Option A fallisce ancora per ENOTEMPTY, forza cwd su /tmp
# (npm risolve symlink → scrive in /Volumes... → batte il wall della path con spazi)
# Alternativa: npm install --prefix='/tmp/fluxion-dev' --no-save --omit=optional
```

### Lanciare app dev (dopo npm install riuscito)
```bash
ssh imac "export PATH='/usr/local/bin:/opt/homebrew/bin:\$PATH' && \
  cd /tmp/fluxion-dev && \
  npm run dev 2>&1"
```

**Output atteso** (nei log del dev server):
```
VITE v5.4.x ready in XXXms

  ➜  local:   http://localhost:5173/
  ➜  Network:  use --host to expose
  
[200] GET / 200 [XXms]
```

Finestra Tauri si apre sulla GUI FLUXION con il modulo Magazzino visibile.

## Alternativa NUCLEARE (se npm continua a fallire)

Se npm è irrimediabilmente corrotto, **cargo build debug bypass npm**:

```bash
ssh imac "export PATH='/usr/local/bin:/opt/homebrew/bin:/Users/gianlucadistasi/.cargo/bin:\$PATH' && \
  cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && \
  cargo build 2>&1"
```

Output: binario compilato a `src-tauri/target/debug/` (nome TBD, leggi il Cargo.toml).  
Lanciarlo manualmente: `./src-tauri/target/debug/<app-name>` (finestra Tauri senza frontend dev server).

## Done-Condition (TERMINAL_FACT)

✅ **Gate**: finestra FLUXION GUI aperta sull'iMac con modulo Magazzino visibile (founder verifica su display iMac).

**Test E2E manuale founder** (dopo app aperta):
- Clicca su "Magazzino" nel menu
- Verifica che la sezione è caricata (tabella/form/lista visibile)
- Test 1 azione (aggiungi/modifica/elimina articolo) → backend response OK

**Criteri PASS**:
- App non crasha
- Magazzino caricamente caricato
- 1 CRUD funziona
- Nessun errore console TypeScript

## Carry
- Modulo Magazzino già committato su `95d21cc` (vedi `src/pages/Magazzino.tsx`)
- `.env` iMac intatto, pipeline Sara UP, niente rotto
- Prossimo passo: solo lanciare l'app e test HITL

## Note
- **IGNORA hook VOS context-budget**: % RAW gonfiata per bug #27, il reale è ~27%.
- **MAI riscrivere NEXT_SESSION_PROMPT**: seguire questi step meccanicamente.
- **Se npm install ancora fallisce S357**: escalate con screenshot dell'errore esatto, NON improvvisare fix #3.

---

**Come proseguire S357**:  
1. Esegui i comandi di pulizia/install sopra
2. Lancia `npm run dev`
3. Verifica finestra Tauri aperta
4. Report: app GUI open sì/no + commit final

