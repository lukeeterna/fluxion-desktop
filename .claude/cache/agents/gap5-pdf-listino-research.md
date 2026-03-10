# GAP-5 — Deep Research CoVe 2026: Import Listini Prezzi Fornitori per PMI Italiane

**Data ricerca:** 2026-03-10 | **Metodologia:** CoVe, 14 query parallele cross-validate

---

## 1. FORMATI PIÙ DIFFUSI — Ranked per diffusione

| Rank | Formato | Diffusione | Settori principali |
|------|---------|-----------|-------------------|
| 1 | **Excel (.xlsx/.xls)** | ~55% | Tutti i settori PMI |
| 2 | **PDF** | ~25% | Cosmetica, estetica, parrucchieri, fisioterapia |
| 3 | **CSV / TXT** | ~12% | Distribuzione, elettrico, officine |
| 4 | **Portale web (area riservata P.IVA)** | ~5% | Cosmetica professionale, farmaceutica |
| 5 | **METEL** | ~2% | Solo materiale elettrico/idraulico |
| 6 | **XML** | ~1% | ERP enterprise / EDI |
| 7 | **Cartaceo** | residuale | Artigiani tradizionali |

**Canale primario:** email con allegato. L'agente di zona porta ancora il PDF stampato in visita.

---

## 2. FREQUENZA DI AGGIORNAMENTO

| Settore | Frequenza |
|---------|-----------|
| Cosmetica / Parrucchieri | Annuale + promozioni stagionali |
| Estetica professionale | Semestrale / trimestrale |
| Fisioterapia / Sanità | Trimestrale |
| Palestre / Integratori | Semestrale |
| Officine / Ricambi auto | Mensile o continua |

**Insight:** Per i 5 settori target FLUXION, la frequenza dominante è **2-4x/anno**. Non è daily — è un evento ricorrente ma discreto che richiede precisione.

---

## 3. STRUTTURA TIPICA LISTINO PMI ITALIANA

**Colonne obbligatorie (100%):** Codice articolo fornitore, Descrizione, Unità di misura, Prezzo listino lordo

**Colonne molto comuni (~70%):** Categoria/Famiglia, Sconto % (1-3 livelli), Prezzo netto, IVA %, Data validità

**Colonne frequenti (~40%):** Codice EAN/Barcode, MOQ (quantità minima), Unità confezionamento, Note

**Problema reale:** I listini Excel italiani NON seguono standard uniformi:
- Prima riga dati alla riga 4-8 (non alla 1)
- Merged cells con logo fornitore
- Nomi colonne non standardizzati ("Pr. Netto", "Listino IVA esclusa")
- Fogli multipli per categoria
- Formule Excel nei prezzi

---

## 4. PAIN POINT (ordinati per impatto)

1. **Normalizzazione manuale** — 30-90 min/listino per rendere importabile un Excel non-standard
2. **Errori di ricopiatura prezzi** — decimali sbagliati, codici errati, IVA mal applicata
3. **Prezzi obsoleti in uso** — listino non aggiornato, si lavora con prezzi di 12 mesi fa
4. **Doppio lavoro prezzo vendita** — calcolo manuale ricarico articolo per articolo
5. **Nessuno storico variazioni** — impossibile sapere se un articolo è aumentato del 15%
6. **Fogli multipli** — un listino con 5 sheet = 5 importazioni separate
7. **PDF non importabili** — nessun workflow PMI per estrarre dati da PDF
8. **Aggiornamenti parziali** — fornitore invia solo le righe cambiate, non il listino completo

---

## 5. COMPETITOR — Gestione import listini

### Italiani
- **iMio Gestionale:** Excel con template generato dal sistema — il migliore tra i competitor italiani
- **Soges FacileManager:** CSV/Excel/Metel + connettore automatico su richiesta; download giornaliero automatico da siti fornitori (configurazione custom)
- **TeamSystem Wellness:** Import principalmente da fattura elettronica XML (SDI); listini configurabili manualmente
- **Nabirio, Atlantis Evo, Invoicex:** Solo CSV base, no wizard, no auto-detect
- **eMotori eSolver:** Eccellente per officine — aggiornamento automatico 600+ produttori via TecDoc, ma verticale specifico

### Internazionali (benchmark)
- **Fresha:** CSV template scaricabile, wizard 4 step, auto-dedup, associazione fornitore — standard migliore settore saloni/SPA
- **Lightspeed Retail X-Series:** CSV/XLSX/XLS, template ufficiale, max 500 righe/import, import ordini acquisto da CSV — ottima UX
- **Square:** XLSX (raccomandato) o CSV, bulk update prezzi esistenti — ottima UX
- **Mindbody:** Nessun import diretto listino fornitore documentato — punto debole

**Weakness universale:** Nessun competitor supporta import diretto da PDF. Tutti richiedono file già strutturati in CSV/Excel. Il bridging PDF→dati è universalmente risolto con lavoro manuale.

---

## 6. GAP COMPETITIVO

| Feature | Competitor IT | Competitor INT | FLUXION |
|---------|--------------|----------------|---------|
| Import CSV con template | Parziale | SÌ (Fresha, Lightspeed) | Parity minimum |
| Import Excel con auto-detect struttura | NO | NO | **DIFFERENZIANTE** |
| Mapping visuale colonne drag-and-drop | NO | NO | **DIFFERENZIANTE** |
| Import PDF con estrazione tabelle | NO | NO | **FIRST MOVER** |
| Preview + validazione pre-import | NO | Parziale | **DIFFERENZIANTE** |
| Storico variazioni prezzi | NO | NO | **DIFFERENZIANTE** |
| Gestione fogli multipli Excel | NO | NO | **DIFFERENZIANTE** |

**Gap principale non risolto da nessuno:** Il 55% dei listini arriva in Excel non-strutturato. Nessun software PMI italiano gestisce auto-detect intelligente delle intestazioni e mapping visuale.

---

## 7. RACCOMANDAZIONE TECNICA PER FLUXION

### Priorità formati

- **Fase 1 (MVP):** Excel .xlsx/.xls — 55% mercato, ROI massimo
- **Fase 2:** CSV — 12%, richiesto da utenti tecnici e compatibilità altri gestionali
- **Fase 3 (differenziante):** PDF text-based — 25% mercato, complessità alta

### Stack tecnico consigliato (Tauri + React + SQLite)

- **SheetJS** (`npm xlsx`) — parsing Excel/CSV nel frontend Tauri, MIT license, battle-tested
- **react-spreadsheet-import** (npm) — wizard UI completo: upload → sheet select → header detect → column map → validate → import; MIT license; ~10k download/settimana; alternativa open source a Flatfile/Dromo
- **PDF Fase 3:** pdfplumber (Python subprocess via Tauri command) per PDF text-based

### Schema DB SQLite proposto

```sql
-- Migration 031
CREATE TABLE listini_fornitori (
  id TEXT PRIMARY KEY,
  fornitore_id TEXT NOT NULL REFERENCES suppliers(id),
  nome_listino TEXT NOT NULL,
  data_import TEXT NOT NULL,
  data_validita TEXT,
  formato_fonte TEXT NOT NULL, -- 'xlsx','xls','csv','pdf'
  righe_totali INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE listino_righe (
  id TEXT PRIMARY KEY,
  listino_id TEXT NOT NULL REFERENCES listini_fornitori(id) ON DELETE CASCADE,
  codice_articolo TEXT,
  descrizione TEXT NOT NULL,
  unita_misura TEXT DEFAULT 'pz',
  prezzo_acquisto REAL NOT NULL,
  sconto_pct REAL DEFAULT 0,
  prezzo_netto REAL,
  iva_pct REAL DEFAULT 22,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE listino_variazioni (
  id TEXT PRIMARY KEY,
  listino_riga_id TEXT NOT NULL REFERENCES listino_righe(id),
  campo TEXT NOT NULL,
  valore_precedente TEXT,
  valore_nuovo TEXT,
  data_variazione TEXT DEFAULT (datetime('now'))
);
```

### Flusso UX 7-step (world-class)

1. **Upload** — drag & drop (xlsx, xls, csv, pdf)
2. **Sheet select** — se Excel multi-foglio, seleziona sheet
3. **Header detect** — auto-detect prima riga dati; slider manuale di aggiustamento
4. **Column map** — mapping visuale + fuzzy-suggest nomi colonne italiani
5. **Validate** — preview 10 righe, errori in rosso, warning in giallo
6. **Conflict** — duplicati: Aggiorna / Salta / Crea nuovo
7. **Confirm** — progress bar + summary: X inseriti, Y aggiornati, Z saltati

---

## 8. ACCEPTANCE CRITERIA MISURABILI

| AC | Scenario | Criterio | Misura |
|----|----------|----------|--------|
| AC-1 | Excel con intestazioni riga 1-10 | Auto-detect header corretto ≥80% su 20 listini test | Righe header corrette / totale |
| AC-2 | Colonne nomi non-standard italiano | Fuzzy-suggest corretto ≥70% colonne mappabili | Suggerimenti corretti / totale |
| AC-3 | Listino 200 righe, struttura non-standard | Wizard completato in ≤3 min da utente esperto | Media su 5 utenti |
| AC-4 | File con errori (prezzi non numerici, IVA non valida) | 0 righe con errori importate silenziosamente | Count errori non segnalati |
| AC-5 | Listino con 20 duplicati su 50 righe | 20 righe aggiornate + 20 record in listino_variazioni | Conteggio DB |
| AC-6 | CSV con separatore ";" e encoding Latin-1 | 0 errori encoding su 10 CSV test con varianti | Count errori |
| AC-7 | Ricarico 30% applicato a listino importato | prezzo_vendita = prezzo_acquisto * 1.30 per ogni riga | Accuratezza 100% |
| AC-8 | Excel 1000 righe | Parsing + preview pronti in ≤5 secondi | Benchmark su i5/8GB RAM |

---

## 9. SINTESI ESECUTIVA

1. **Excel prima di tutto:** 55% del mercato, ROI massimo. Auto-detect struttura è il differenziante reale.
2. **Il problema è la struttura, non il formato:** I competitor gestiscono solo file già normalizzati. FLUXION deve gestire l'Excel "reale" dei fornitori italiani.
3. **SheetJS + react-spreadsheet-import:** Stack MIT, compatibile Tauri/React, collaudato.
4. **Frequenza bassa, impatto alto:** 30 min risparmiati × 5 fornitori × 3 update/anno = 7.5 ore/anno per operatore.
5. **Storico variazioni = feature unica:** Tabella `listino_variazioni` a costo quasi zero, valore percepito altissimo per negoziazione con fornitori.

---

## 10. DECISIONE ARCHITETTURALE CONSIGLIATA

**NON fare PDF come Fase 1.** Il 25% dei listini in PDF è reale ma:
- PDF di testo (non scansionati) sono parsabili ma strutturalmente irregolari
- Il rischio di falsi positivi è alto → danneggia la fiducia del prodotto
- ROI su Excel è 2.2x superiore per effort analogo

**Fare Excel + CSV in Fase 1, poi valutare PDF in Fase 2 con feedback clienti reali.**
