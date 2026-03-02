# Operatori Features — CoVe 2026 Research
> Generato: 2026-03-02 | Agente background

## Schema DB Esistente (CONFERMATO)
- `operatori` — id, nome, cognome, email, telefono, ruolo, colore, avatar_url, attivo
- `operatori_servizi` — operatore_id, servizio_id (**many-to-many ESISTE GIA**)
- `orari_lavoro` — giorno, ora_inizio, ora_fine, tipo, `operatore_id` (**supporto per-operatore ESISTE GIA**)
- Migration 012 aggiunge: `specializzazioni TEXT`, `descrizione_positiva TEXT`, `anni_esperienza INTEGER`

**Gap critici:** nessuna UI per `operatori_servizi`, OperatoriPage.tsx è placeholder, zero KPI, zero assenze, zero commissioni.

## Priorità per PMI Italiane (impatto − complessità)

| # | Feature | Impatto | Complessità | Score | Effort |
|---|---------|---------|-------------|-------|--------|
| 1 | Servizi abilitati (UI) | 5 | 1 | **+4** | 6h |
| 2 | Turni/Orari operatore (UI) | 5 | 2 | **+3** | 10h |
| 3 | KPI statistiche (VIEW) | 5 | 2 | **+3** | 8h |
| 4 | Assenze/Ferie | 4 | 2 | **+2** | 10h |
| 5 | Commissioni | 4 | 3 | **+1** | 11h |
| — | Target mensili bonus | 3 | 1 | **+2** | 3h |
| — | Permessi granulari | 3 | 4 | **-1** | 15h (v1.1) |

**Ordine ottimale v1.0**: 1 → 2 → 3 → Target → 4 → 5

## FEATURE 1: Servizi Abilitati (UI su tabella esistente)
- `operatori_servizi` esiste — serve solo UI con checkbox per servizio + toggle "Specializzato"
- Migration 024: `ALTER TABLE operatori_servizi ADD COLUMN priorita INTEGER DEFAULT 0;`
- Commands: `get_operatore_servizi(id)`, `update_operatore_servizi(id, servizi[])`
- UI: `OperatoreServiziSection.tsx` — checkbox raggruppati per categoria, star = specializzato

## FEATURE 2: Turni/Orari (UI su tabella esistente)
- `orari_lavoro` con `operatore_id` ESISTE — serve solo UI griglia 7 giorni
- **ZERO migration needed**
- Commands: `get_orari_operatore(id)`, `update_orari_operatore(id, orari[])`
- UI: griglia lun-dom con time picker, toggle "chiuso", supporto pausa pranzo

## FEATURE 3: KPI Statistiche (solo VIEW)
```sql
-- Migration 024:
CREATE VIEW v_kpi_operatori AS
SELECT o.id, o.nome || ' ' || o.cognome AS nome_completo,
    strftime('%Y-%m', a.data_ora_inizio) AS mese,
    COUNT(CASE WHEN a.stato = 'completato' THEN 1 END) AS appuntamenti_completati,
    COUNT(CASE WHEN a.stato = 'no_show' THEN 1 END) AS no_show,
    COUNT(DISTINCT a.cliente_id) AS clienti_unici,
    COALESCE(SUM(CASE WHEN a.stato = 'completato' THEN a.prezzo_finale END), 0) AS fatturato_generato,
    ROUND(AVG(CASE WHEN a.stato = 'completato' THEN a.prezzo_finale END), 2) AS ticket_medio
FROM operatori o
LEFT JOIN appuntamenti a ON a.operatore_id = o.id
WHERE o.attivo = 1
GROUP BY o.id, strftime('%Y-%m', a.data_ora_inizio);
```

## FEATURE 4: Assenze/Ferie (nuova tabella)
```sql
CREATE TABLE operatori_assenze (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    operatore_id TEXT NOT NULL,
    data_inizio TEXT NOT NULL,  -- YYYY-MM-DD
    data_fine TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('ferie','malattia','permesso','formazione','maternita','altro')),
    note TEXT, approvata INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE
);
-- View per Sara e dashboard:
CREATE VIEW v_operatori_assenti_oggi AS
SELECT o.id, o.nome, o.cognome, a.tipo, a.data_inizio, a.data_fine
FROM operatori_assenze a JOIN operatori o ON o.id = a.operatore_id
WHERE date('now') BETWEEN a.data_inizio AND a.data_fine AND a.approvata = 1;
```

## FEATURE 5: Commissioni (nuova tabella)
```sql
CREATE TABLE operatori_commissioni (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    operatore_id TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('percentuale_servizio','percentuale_prodotti','fisso_mensile','soglia_bonus')),
    percentuale REAL, importo_fisso REAL,
    soglia_fatturato REAL, bonus_importo REAL,
    valida_dal TEXT NOT NULL, valida_al TEXT,
    servizio_id TEXT, note TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE
);
```

## Architettura UI Consigliata
Pagina dettaglio `/operatori/:id` con tab:
```
[Anagrafica] [Servizi & Orari] [Statistiche] [Assenze] [Commissioni]
```

Nuovi file:
```
src/components/operatori/
├── OperatoriPage.tsx (FULL - attualmente placeholder)
├── OperatoreDettaglio.tsx (nuova pagina tab)
├── OperatoreServiziSection.tsx
├── OperatoreOrariSection.tsx
├── OperatoreKpiCard.tsx
├── OperatoriRankingTable.tsx
├── OperatoreAssenzeSection.tsx
└── OperatoreCommissioniSection.tsx

src/hooks/
├── use-operatori-servizi.ts
├── use-operatori-kpi.ts
└── use-operatori-assenze.ts
```
