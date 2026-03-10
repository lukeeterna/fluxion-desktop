# FLUXION — Handoff Sessione 40 → 41 (2026-03-10)

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
Branch: master | HEAD: 5d61b1c
Working tree: CLEAN ✅
type-check: 0 errori ✅
cargo check: 0 errori ✅ (verificato su iMac)
iMac: sincronizzato ✅ | pipeline UP porta 3002 | Cloudflare Tunnel LaunchAgent attivo
```

---

## ✅ COMPLETATO SESSIONE 40

### Gap #8 — Fattura 1-click (commit ed18320)
- `FatturaDialog.tsx` prop `prefill?` + useEffect sync
- `AppuntamentoDialog.tsx` bottone verde su stato=completato + FatturaDialog embedded
- AC1-AC5 ✅ | type-check 0 errori ✅

### Gap #5 — Import Listino Fornitori Excel/CSV (commit 5d61b1c)
**Impatto**: 7.5h/anno risparmiate · 0 errori ricopiatura · storico variazioni unico vs competitor
- Migration 031: `listini_fornitori` + `listino_righe` + `listino_variazioni`
- 5 comandi Tauri: `import_listino`, `get_listini_fornitore`, `get_listino_righe`, `delete_listino`, `get_listino_variazioni`
- `src/lib/listino-utils.ts`: SheetJS parser + Levenshtein fuzzy-match + validateRows + autoDetect header
- `ImportListinoWizard.tsx`: wizard 6-step completo
- `ListiniTable.tsx` + `ListiniTab.tsx`: tab "Listini Prezzi" in Fornitori.tsx
- AC1-AC8 implementati ✅ | type-check 0 errori ✅

---

## 🚀 PROSSIMO: Gap #4 — WhatsApp Interactive Confirm/Cancel

### Obiettivo
Quando Sara prenota (o operatore crea appuntamento), invia WA con 3 bottoni interattivi:
- **✅ Confermo** → stato appuntamento → `confirmed`
- **❌ Cancello** → stato → `cancelled` + slot libero + notifica operatore
- **📅 Sposto** → Sara riapre FSM in `PROPOSING_DATETIME`

### Revenue
+5-10% confirmation rate → meno no-show → +€200-400/mese per PMI tipica

### File chiave da leggere prima di implementare
- `scripts/whatsapp-service.cjs` — bot WhatsApp locale (porta 3001)
- `voice-agent/src/whatsapp.py` — integrazione WA lato Python
- `voice-agent/src/booking_state_machine.py` — FSM 23 stati

### Research necessaria
`.claude/cache/agents/gap4-wa-interactive-research.md` — da creare se non esiste

---

## INFRA ATTIVA

### iMac (192.168.1.12)
```bash
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Cloudflare Tunnel
```bash
launchctl list | grep cloudflare
grep TUNNEL_URL '/Volumes/MontereyT7/FLUXION/config.env'
```

### License Server
```bash
ssh imac "curl -s http://localhost:3010/health"
```
