// ═══════════════════════════════════════════════════════════════════
// FLUXION - Listino Utils (Gap #5)
// Fuzzy matching italiano + SheetJS parser + validazione righe
// ═══════════════════════════════════════════════════════════════════

import * as XLSX from 'xlsx';
import type {
  ParsedSheet,
  TargetColumn,
  ColumnMapping,
  ValidatedRow,
  RigaImportInput,
  FormatoFonte,
} from '@/types/listino';
import { COLUMN_ALIASES } from '@/types/listino';

// ─── Levenshtein distance (for fuzzy matching) ────────────────────

function levenshtein(a: string, b: string): number {
  const m = a.length;
  const n = b.length;
  const dp: number[][] = Array.from({ length: m + 1 }, (_, i) =>
    Array.from({ length: n + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0))
  );
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] =
        a[i - 1] === b[j - 1]
          ? dp[i - 1][j - 1]
          : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
    }
  }
  return dp[m][n];
}

/** Normalizza stringa per confronto (lowercase, trim, rimuovi punteggiatura) */
function normalize(s: string): string {
  return s
    .toLowerCase()
    .trim()
    .replace(/[.\-_/\\%()]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Suggerisce la colonna target per un header sorgente.
 * Utilizza confronto esatto sugli alias, poi distanza Levenshtein.
 * Soglia: score >= 0.70 per accettare il suggerimento.
 */
export function suggestTargetColumn(header: string): TargetColumn {
  const norm = normalize(header);

  // Confronto esatto/parziale sugli alias
  for (const [target, aliases] of Object.entries(COLUMN_ALIASES) as [TargetColumn, string[]][]) {
    if (target === '__skip__') continue;
    for (const alias of aliases) {
      if (normalize(alias) === norm || norm.includes(normalize(alias)) || normalize(alias).includes(norm)) {
        return target;
      }
    }
  }

  // Fuzzy Levenshtein su tutti gli alias
  let bestTarget: TargetColumn = '__skip__';
  let bestScore = 0;

  for (const [target, aliases] of Object.entries(COLUMN_ALIASES) as [TargetColumn, string[]][]) {
    if (target === '__skip__') continue;
    for (const alias of aliases) {
      const dist = levenshtein(norm, normalize(alias));
      const maxLen = Math.max(norm.length, alias.length);
      const score = maxLen === 0 ? 1 : 1 - dist / maxLen;
      if (score > bestScore) {
        bestScore = score;
        bestTarget = target;
      }
    }
  }

  return bestScore >= 0.70 ? bestTarget : '__skip__';
}

// ─── Excel/CSV parser ─────────────────────────────────────────────

export interface ParseResult {
  sheets: ParsedSheet[];
  formato: FormatoFonte;
}

/** Converte il workbook XLSX in array di ParsedSheet (raw string rows). */
export function parseWorkbook(buffer: ArrayBuffer, fileName: string): ParseResult {
  const ext = fileName.split('.').pop()?.toLowerCase() ?? '';
  const formato: FormatoFonte = ext === 'xls' ? 'xls' : ext === 'csv' ? 'csv' : 'xlsx';

  const wb = XLSX.read(buffer, { type: 'array', raw: false, cellDates: false });

  const sheets: ParsedSheet[] = wb.SheetNames.map((name) => {
    const ws = wb.Sheets[name];
    const aoa: (string | number | boolean | null | undefined)[][] = XLSX.utils.sheet_to_json(ws, {
      header: 1,
      defval: '',
      blankrows: false,
      raw: false,
    });
    // Normalizza tutto a stringa
    const rows: string[][] = aoa.map((row) =>
      row.map((cell) => (cell == null ? '' : String(cell).trim()))
    );
    return { name, rows };
  });

  return { sheets, formato };
}

// ─── Auto-detect header row ───────────────────────────────────────

/**
 * Cerca la prima riga che contiene almeno 2 colonne riconoscibili.
 * Scansiona le prime 10 righe. Ritorna 0-based index, default 0.
 */
export function autoDetectHeaderRow(rows: string[][]): number {
  for (let i = 0; i < Math.min(10, rows.length); i++) {
    const row = rows[i];
    if (row.length < 2) continue;
    let recognized = 0;
    for (const cell of row) {
      if (cell && suggestTargetColumn(cell) !== '__skip__') recognized++;
    }
    if (recognized >= 2) return i;
  }
  return 0;
}

// ─── Build column mappings ────────────────────────────────────────

export function buildColumnMappings(headerRow: string[]): ColumnMapping[] {
  return headerRow.map((header, i) => ({
    sourceIndex: i,
    sourceHeader: header,
    targetColumn: suggestTargetColumn(header),
  }));
}

// ─── Validate rows ────────────────────────────────────────────────

const IVA_VALIDE = new Set([0, 4, 5, 10, 22]);

export function validateRows(
  dataRows: string[][],
  mappings: ColumnMapping[],
  ricaricoPct: number
): ValidatedRow[] {
  const results: ValidatedRow[] = [];

  for (let ri = 0; ri < dataRows.length; ri++) {
    const row = dataRows[ri];
    const raw: Record<string, string> = {};
    const parsed: Partial<RigaImportInput> = {};
    const errors: string[] = [];
    const warnings: string[] = [];

    // Mappa colonne
    for (const m of mappings) {
      if (m.targetColumn === '__skip__') continue;
      const val = row[m.sourceIndex] ?? '';
      raw[m.targetColumn] = val;

      switch (m.targetColumn) {
        case 'descrizione':
          if (val.trim()) parsed.descrizione = val.trim();
          break;
        case 'codice_articolo':
          if (val.trim()) parsed.codice_articolo = val.trim();
          break;
        case 'unita_misura':
          if (val.trim()) parsed.unita_misura = val.trim();
          break;
        case 'categoria':
          if (val.trim()) parsed.categoria = val.trim();
          break;
        case 'ean':
          if (val.trim()) parsed.ean = val.trim();
          break;
        case 'note':
          if (val.trim()) parsed.note = val.trim();
          break;
        case 'prezzo_acquisto': {
          const n = parseItalianNumber(val);
          if (isNaN(n)) errors.push(`Prezzo acquisto non numerico: "${val}"`);
          else if (n <= 0) errors.push(`Prezzo acquisto deve essere > 0`);
          else parsed.prezzo_acquisto = n;
          break;
        }
        case 'sconto_pct': {
          if (val.trim()) {
            const n = parseItalianNumber(val.replace('%', ''));
            if (isNaN(n)) warnings.push(`Sconto non numerico: "${val}"`);
            else if (n < 0 || n > 100) warnings.push(`Sconto fuori range: ${n}%`);
            else parsed.sconto_pct = n;
          }
          break;
        }
        case 'prezzo_netto': {
          if (val.trim()) {
            const n = parseItalianNumber(val);
            if (!isNaN(n) && n > 0) parsed.prezzo_netto = n;
          }
          break;
        }
        case 'iva_pct': {
          if (val.trim()) {
            const n = parseItalianNumber(val.replace('%', ''));
            if (isNaN(n)) warnings.push(`IVA non numerica: "${val}"`);
            else if (!IVA_VALIDE.has(n)) warnings.push(`Aliquota IVA non standard: ${n}%`);
            else parsed.iva_pct = n;
          }
          break;
        }
      }
    }

    // Validazioni cross-field
    if (!parsed.descrizione) {
      errors.push('Descrizione obbligatoria');
    }
    if (parsed.prezzo_acquisto == null) {
      errors.push('Prezzo acquisto obbligatorio');
    }

    // Calcola prezzo_netto se mancante (AC-7: ricarico)
    if (parsed.prezzo_acquisto != null && parsed.prezzo_netto == null) {
      const sconto = parsed.sconto_pct ?? 0;
      parsed.prezzo_netto = parsed.prezzo_acquisto * (1 - sconto / 100);
    }

    // Applica ricarico per prezzo vendita suggerito (metadato, non salvato in DB)
    if (ricaricoPct > 0 && parsed.prezzo_acquisto != null) {
      raw['prezzo_vendita_suggerito'] = (parsed.prezzo_acquisto * (1 + ricaricoPct / 100)).toFixed(2);
    }

    // Salta righe completamente vuote
    const hasAnyData = Object.values(row).some((v) => v.trim() !== '');
    if (!hasAnyData) continue;

    results.push({ rowIndex: ri, raw, parsed, errors, warnings });
  }

  return results;
}

/** Parsifica numeri in formato italiano (1.234,56 → 1234.56) */
function parseItalianNumber(val: string): number {
  const cleaned = val
    .trim()
    .replace(/[€$\s]/g, '')
    .replace(/\.(?=\d{3})/g, '')   // rimuove separatore migliaia italiano
    .replace(',', '.');             // virgola decimale → punto
  return parseFloat(cleaned);
}

// ─── Convert validated rows to import input ───────────────────────

export function validatedRowsToImportInput(rows: ValidatedRow[]): RigaImportInput[] {
  return rows
    .filter((r) => r.errors.length === 0 && r.parsed.descrizione && r.parsed.prezzo_acquisto != null)
    .map((r) => r.parsed as RigaImportInput);
}
