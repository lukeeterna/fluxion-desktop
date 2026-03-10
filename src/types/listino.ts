// ═══════════════════════════════════════════════════════════════════
// FLUXION - Listini Fornitori Types (Gap #5)
// ═══════════════════════════════════════════════════════════════════

export type FormatoFonte = 'xlsx' | 'xls' | 'csv';

export interface ListinoFornitore {
  id: string;
  fornitore_id: string;
  nome_listino: string;
  data_import: string;
  data_validita: string | null;
  formato_fonte: FormatoFonte;
  righe_totali: number;
  righe_inserite: number;
  righe_aggiornate: number;
  note: string | null;
  created_at: string;
}

export interface ListinoRiga {
  id: string;
  listino_id: string;
  codice_articolo: string | null;
  descrizione: string;
  unita_misura: string;
  prezzo_acquisto: number;
  sconto_pct: number;
  prezzo_netto: number | null;
  iva_pct: number;
  categoria: string | null;
  ean: string | null;
  note: string | null;
  created_at: string;
}

export interface ListinoVariazione {
  id: string;
  listino_riga_id: string;
  campo: string;
  valore_precedente: string | null;
  valore_nuovo: string;
  data_variazione: string;
}

export interface RigaImportInput {
  codice_articolo?: string;
  descrizione: string;
  unita_misura?: string;
  prezzo_acquisto: number;
  sconto_pct?: number;
  prezzo_netto?: number;
  iva_pct?: number;
  categoria?: string;
  ean?: string;
  note?: string;
}

export interface ImportListinoRequest {
  fornitore_id: string;
  nome_listino: string;
  data_validita?: string;
  formato_fonte: FormatoFonte;
  righe: RigaImportInput[];
}

export interface ImportListinoResult {
  listino_id: string;
  righe_inserite: number;
  righe_aggiornate: number;
  righe_totali: number;
  variazioni_registrate: number;
}

// ─── Wizard State ─────────────────────────────────────────────────

export type WizardStep = 1 | 2 | 3 | 4 | 5 | 6;

export interface ParsedSheet {
  name: string;
  rows: string[][];  // raw rows including headers
}

/** Colonne target canoniche del dominio FLUXION */
export type TargetColumn =
  | 'codice_articolo'
  | 'descrizione'
  | 'unita_misura'
  | 'prezzo_acquisto'
  | 'sconto_pct'
  | 'prezzo_netto'
  | 'iva_pct'
  | 'categoria'
  | 'ean'
  | 'note'
  | '__skip__';

export interface ColumnMapping {
  sourceIndex: number;
  sourceHeader: string;
  targetColumn: TargetColumn;
}

export interface ValidatedRow {
  rowIndex: number;
  raw: Record<string, string>;
  parsed: Partial<RigaImportInput>;
  errors: string[];
  warnings: string[];
}

export interface WizardState {
  step: WizardStep;
  file: File | null;
  formato: FormatoFonte | null;
  sheets: ParsedSheet[];
  selectedSheetIndex: number;
  headerRowIndex: number;       // 0-based index della riga intestazione
  columnMappings: ColumnMapping[];
  validatedRows: ValidatedRow[];
  ricaricoPct: number;          // % ricarico suggerito → prezzo_vendita (AC-7)
  nomeListino: string;
  dataValidita: string;
}

// ─── Fuzzy mapping helpers ─────────────────────────────────────────

/** Alias italiani per fuzzy-suggest */
export const COLUMN_ALIASES: Record<TargetColumn, string[]> = {
  codice_articolo: ['codice', 'cod', 'cod.', 'sku', 'art', 'cod articolo', 'codice art', 'ref', 'riferimento'],
  descrizione: ['descrizione', 'desc', 'prodotto', 'articolo', 'nome', 'denominazione', 'voce'],
  unita_misura: ['um', 'unita', 'unità', 'u.m.', 'conf', 'confezione', 'pz', 'kg'],
  prezzo_acquisto: ['prezzo', 'listino', 'pr. listino', 'prezzo listino', 'pr listino', 'costo', 'importo', 'listino lordo', 'pr. lordo'],
  sconto_pct: ['sconto', 'sc', 'sc%', 'sconto%', '% sconto', 'sconto %', 'ribasso'],
  prezzo_netto: ['prezzo netto', 'pr. netto', 'pr netto', 'netto', 'costo netto', 'importo netto'],
  iva_pct: ['iva', 'aliquota', 'aliquota iva', 'iva%', '% iva', 'iva %', 'aliq'],
  categoria: ['categoria', 'cat', 'famiglia', 'linea', 'gruppo', 'settore', 'reparto'],
  ean: ['ean', 'barcode', 'codice a barre', 'ean13', 'upc', 'gtin'],
  note: ['note', 'note', 'descrizione aggiuntiva', 'info', 'annotazioni'],
  __skip__: [],
};
