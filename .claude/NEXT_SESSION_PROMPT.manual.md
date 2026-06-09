# Prompt ripartenza — FASE 6 E2E Magazzino (HITL Luke@iMac)

**Aggiornato**: 2026-06-09 sessione S360  
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`, HEAD `93cc1db`)  
**Status**: ✅ PREREQUISITO FASE 6 COMPLETO — app Magazzino LIVE su iMac.
**⏸️ E2E Magazzino S1-S7 = PENDING** (2026-06-09): iMac INACCESSIBILE (tastiera rotta) → l'E2E HITL GUI non eseguibile finché iMac non torna usabile. Riprendere quando iMac accessibile. Codice/migration GIÀ verificati live (tabelle create, `✓ [042] ready`).
**▶️ TASK ATTIVO = STAZIONE 2: build installer Windows via CI GitHub** (da origin/master, NON locale, NON iMac).

## ⭐ DA FARSI (prossima sessione)

**1. L'app è già accesa sull'iMac. Per RILANCIARLA se serve:**
```
ssh imac
cd '/Volumes/MacSSD - Dati/fluxion' && cargo tauri dev
```
(login shell zsh per PATH node/cargo. NON usare `npm run tauri`: lo script non risolve `.bin`. Log: `/tmp/fluxion-dev.log`.)

**2. E2E FASE 6 S1-S7 — Luke clicca nella GUI, CC osserva DB read-only:**
- S1 Magazzino → crea articolo (giacenza 10, soglia 5) → atteso alert = 0
- S2 badge sidebar = 0 (sopra soglia)
- S3 scarico 6 unità → giacenza 4 → atteso alert count = 1
- S4 il badge sale SENZA aprire la pagina
- S5 la pagina evidenzia l'articolo sottoscorta
- S6 2° scarico non ri-emette alert (anti-spam); carico sopra soglia → alert = 0
- S7 con licenza Base → upsell (se manca licenza Base = PENDING, non FAIL)
- 🚀 se S1-S6 PASS (S7 PASS o PENDING).

**Osservazione DB (CC):** `DB="/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db"` → `sqlite3 "$DB" "SELECT id,nome,giacenza,soglia_minima,alert_notificato FROM articoli;"` + `"SELECT * FROM movimenti_magazzino;"`. (Magazzino è solo Tauri IPC, NON su HTTP bridge → serve la GUI, non pilotabile via curl.)

**3. Poi → Windows R2 → Sara** (ordine founder).

## Cosa è stato fatto S360 (contesto)
- Reset iMac `40fcb80d`→`93cc1db` (97 commit dietro). De-risk validato, `.so` NDEBUG 8.6MB intatto, stash `PRE-FASE6-safety-20260609`.
- BUG #1 fixato: node_modules corrotto (symlink dangling `.bin/vite`) → `npm ci`. (NON era il path-con-spazi.)
- BUG #2 fixato (commit `93cc1db`): migration `042_magazzino.sql` mai cablata in `lib.rs` → tabelle magazzino mai create sul DB. REGOLA #24 (unit-test 4/4 verdi ma comportamento live rotto). Ora `✓ [042] ready`.
- App live: `🚀 Application ready` + `🌉 HTTP Bridge 3001`, tabelle `articoli`/`movimenti_magazzino` confermate.

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

