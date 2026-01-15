# PROMPT PER GENERAZIONE SERVIZI DEFAULT PER VERTICALE

> **ISTRUZIONI**: Copia questo prompt in Perplexity/Claude per generare i seed SQL dei servizi.
> **OUTPUT RICHIESTO**: SQL INSERT statements per popolare la tabella `servizi` in base al verticale.

---

## CONTESTO

FLUXION usa una tabella `servizi` universale. Al primo avvio, in base alla **chiave verticale** scelta dall'utente, vengono inseriti servizi default realistici.

### Schema Tabella Servizi

```sql
CREATE TABLE servizi (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    descrizione TEXT,
    prezzo REAL NOT NULL,
    durata INTEGER NOT NULL,      -- minuti
    categoria TEXT,
    colore TEXT DEFAULT '#6366f1', -- per calendario
    attivo INTEGER DEFAULT 1
);
```

---

## RICHIESTA GENERAZIONE

Per **OGNI verticale**, genera gli INSERT SQL con servizi realistici italiani.

### Requisiti:
- **Prezzi**: realistici per il mercato italiano 2025-2026
- **Durate**: in minuti, arrotondate (15, 30, 45, 60, 90, 120)
- **Categorie**: raggruppamento logico
- **ID**: formato `srv_[verticale]_[numero]`

---

## OUTPUT RICHIESTO PER VERTICALE

### 1. SALONE PARRUCCHIERE (`seed_salone.sql`)

```sql
-- Servizi default per SALONE PARRUCCHIERE
-- FLUXION seed data - Verticale: salone

INSERT INTO servizi (id, nome, descrizione, prezzo, durata, categoria, colore) VALUES
('srv_sal_001', 'Taglio Donna', 'Taglio, shampoo e asciugatura', 35.00, 60, 'taglio', '#ec4899'),
('srv_sal_002', 'Taglio Uomo', 'Taglio classico maschile', 18.00, 30, 'taglio', '#3b82f6'),
('srv_sal_003', 'Piega', 'Messa in piega professionale', 20.00, 30, 'styling', '#8b5cf6'),
('srv_sal_004', 'Colore', 'Colorazione completa', 55.00, 90, 'colore', '#f59e0b'),
('srv_sal_005', 'Meches', 'Meches o colpi di sole', 65.00, 120, 'colore', '#f59e0b'),
('srv_sal_006', 'Balayage', 'Tecnica schiarente naturale', 85.00, 150, 'colore', '#f59e0b'),
('srv_sal_007', 'Trattamento Cheratina', 'Trattamento lisciante ristrutturante', 80.00, 120, 'trattamenti', '#10b981'),
('srv_sal_008', 'Barba', 'Taglio e rifinitura barba', 12.00, 20, 'uomo', '#3b82f6'),
('srv_sal_009', 'Taglio + Barba', 'Combo taglio e barba uomo', 28.00, 45, 'uomo', '#3b82f6'),
('srv_sal_010', 'Shampoo + Piega', 'Lavaggio e asciugatura', 25.00, 30, 'styling', '#8b5cf6'),
('srv_sal_011', 'Tinta Ricrescita', 'Ritocco radici', 40.00, 60, 'colore', '#f59e0b'),
('srv_sal_012', 'Permanente', 'Ondulazione permanente', 60.00, 120, 'trattamenti', '#10b981'),
('srv_sal_013', 'Extension', 'Applicazione extension capelli', 150.00, 180, 'speciali', '#ef4444'),
('srv_sal_014', 'Sposa', 'Acconciatura sposa (prova inclusa)', 120.00, 120, 'speciali', '#ef4444'),
('srv_sal_015', 'Taglio Bambino', 'Taglio bambino sotto 12 anni', 12.00, 20, 'taglio', '#ec4899');
```

Genera anche per:

### 2. PALESTRA/WELLNESS (`seed_wellness.sql`)

Servizi tipici:
- Abbonamento mensile (€45, 0 min - è un "servizio" ma senza durata)
- Abbonamento annuale (€400)
- Ingresso singolo (€10)
- Personal Training (€50, 60 min)
- Corsi: Yoga, Pilates, Spinning, CrossFit, Zumba (€10 ciascuno, 60 min)
- Valutazione fitness iniziale (€30, 45 min)
- Massaggio sportivo (€50, 60 min)

### 3. STUDIO MEDICO (`seed_medical.sql`)

Servizi tipici:
- Visita generale (€80, 30 min)
- Visita specialistica (€120, 45 min)
- Ecografia addominale (€70, 30 min)
- Ecografia tiroidea (€60, 20 min)
- Analisi sangue (€35, 15 min)
- ECG (€50, 20 min)
- Certificato medico (€30, 15 min)
- Certificato sportivo (€50, 30 min)
- Visita + ECG (€120, 45 min)
- Vaccino (€30, 15 min)

### 4. OFFICINA/AUTO (`seed_auto.sql`)

Servizi tipici:
- Tagliando base (€120, 120 min) - prezzo indicativo, varia per auto
- Revisione (€66.88, 60 min) - prezzo fisso nazionale
- Cambio gomme 4 (€40, 60 min)
- Equilibratura 4 gomme (€20, 30 min)
- Diagnosi computerizzata (€35, 30 min)
- Cambio olio (€50, 45 min)
- Cambio pastiglie freni (€80, 90 min)
- Sostituzione batteria (€30 manodopera, 30 min)
- Ricarica clima (€60, 45 min)
- Controllo pre-vacanze (€25, 30 min)

---

## FORMATO OUTPUT

Per ogni verticale, genera un file `.sql` con:

```sql
-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Servizi Default
-- Verticale: [NOME_VERTICALE]
-- Generato: [DATA]
-- ═══════════════════════════════════════════════════════════════════

-- Pulisci servizi esistenti (opzionale, per reset)
-- DELETE FROM servizi;

INSERT INTO servizi (id, nome, descrizione, prezzo, durata, categoria, colore) VALUES
-- [LISTA INSERT]
;

-- Verifica
-- SELECT COUNT(*) FROM servizi;
```

---

## DOPO LA GENERAZIONE

1. Salva i file in `src-tauri/migrations/seeds/`
2. Claude Code li integra nel setup wizard
3. Al primo avvio, FLUXION popola i servizi in base al verticale scelto

---

*FLUXION - Setup Wizard - Gennaio 2026*
