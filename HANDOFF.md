# FLUXION — Handoff Sessione 39 → 40 (2026-03-10)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: 98fd8f4
Working tree: DIRTY — Gap #8 implementato, NON ancora committato
type-check: 0 errori ✅
iMac: sincronizzato, pipeline UP porta 3002, Cloudflare Tunnel LaunchAgent attivo
```

---

## ✅ COMPLETATO SESSIONE 39

### Gap #8 — Fattura 1-click da appuntamento
**Impatto PMI**: risparmio ~5h/mese in creazione fatture manuali (€3.000/anno/cliente)
**File modificati** (NON committati):
- `src/components/fatture/FatturaDialog.tsx` — prop `prefill?` + `useEffect` sync
- `src/components/calendario/AppuntamentoDialog.tsx` — bottone "Genera Fattura" + `FatturaDialog` embedded

**Come funziona:**
1. Utente clicca su appuntamento con `stato === 'completato'` nel Calendario
2. `AppuntamentoDialog` mostra bottone verde "Genera Fattura" in footer
3. Click apre `FatturaDialog` pre-compilato con:
   - `cliente_id` → dall'appuntamento
   - `importoRapido` → `prezzo_finale` appuntamento
   - `causale` → `servizio_nome` appuntamento

**Acceptance Criteria verificati**: AC1-AC5 ✅ | type-check 0 errori ✅

---

## 🚀 PROSSIMO: Gap #5 — Excel import listino fornitori

### STEP 0 — Commit Gap #8 (OBBLIGATORIO prima di partire)
```bash
cd /Volumes/MontereyT7/FLUXION
git add src/components/fatture/FatturaDialog.tsx src/components/calendario/AppuntamentoDialog.tsx
git commit -m "feat(gap8): fattura 1-click da appuntamento completato

Bottone 'Genera Fattura' in AppuntamentoDialog (stato=completato).
FatturaDialog pre-compilato con cliente, importo e causale dall'appuntamento.
AC1-AC5 verificati, type-check 0 errori."
```

### Gap #5 — Research già pronta
`.claude/cache/agents/gap5-pdf-listino-research.md` ✅ — leggi e procedi al PLAN

### Gap #5 — Stack approvato
| Libreria | Uso | Licenza |
|---------|-----|---------|
| **SheetJS** (`xlsx`) | Parse Excel .xlsx/.xls | MIT |
| **react-spreadsheet-import** | UI mapping colonne | MIT |

### Gap #5 — Migration DB
File: `src-tauri/migrations/031_listini_fornitori.sql` (da creare):
```sql
listini_fornitori  -- fornitore + metadati listino (nome, data, valido_dal/al)
listino_righe      -- righe prodotto (codice, descrizione, prezzo_lordo, sconto)
listino_variazioni -- storico versioni precedenti
```

### Gap #5 — Acceptance Criteria (da verificare)
- AC1: Upload .xlsx/.xls accettato, parsing OK (merged cells, header non in riga 1)
- AC2: UI mapping colonne (Codice, Descrizione, Prezzo lordo, Sconto %)
- AC3: Righe salvate in DB con fornitore_id
- AC4: Lista listini visualizzabile per fornitore
- AC5: type-check 0 errori

---

## PRIORITÀ BACKLOG

| # | Gap | Revenue | Effort | Status |
|---|-----|---------|--------|--------|
| **5** | Excel listino fornitori | €1.800/anno/cliente | L | **NEXT** |
| 9 | Analytics + report PDF mensile | decisioni migliori | L | ⏳ |
| 10 | WhatsApp bulk anti-churn | retention €500-1K/mese | L | ⏳ |

---

## INFRA ATTIVA

### Cloudflare Tunnel (LaunchAgent permanente)
```bash
launchctl list | grep cloudflare
grep TUNNEL_URL '/Volumes/MontereyT7/FLUXION/config.env'
```

### iMac (192.168.1.12)
```bash
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### License Server (F07 — ngrok free, URL cambia al riavvio)
```bash
ssh imac "curl -s http://localhost:3010/health"
# Se URL ngrok cambiato: aggiornare webhook LS + ACTIVATE_URL_BASE in config.env iMac
```
