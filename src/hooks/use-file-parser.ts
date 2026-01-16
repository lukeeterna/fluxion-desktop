// ═══════════════════════════════════════════════════════════════════
// FLUXION - File Parser Hook
// Parse Excel/Word files for product/price extraction
// ═══════════════════════════════════════════════════════════════════

import { useState, useCallback } from 'react';
import * as XLSX from 'xlsx';
import mammoth from 'mammoth';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

export interface ParsedProduct {
  sku?: string;
  descrizione: string;
  qty: number;
  price: number;
}

export interface FileParseResult {
  products: ParsedProduct[];
  rawData: Record<string, unknown>[];
  columns: string[];
  fileName: string;
  fileType: 'excel' | 'word' | 'pdf' | null;
  error: string | null;
  loading: boolean;
}

interface ColumnMapping {
  sku?: string;
  descrizione: string;
  qty?: string;
  price: string;
}

// ───────────────────────────────────────────────────────────────────
// Hook
// ───────────────────────────────────────────────────────────────────

export function useFileParser() {
  const [result, setResult] = useState<FileParseResult>({
    products: [],
    rawData: [],
    columns: [],
    fileName: '',
    fileType: null,
    error: null,
    loading: false,
  });

  // Reset state
  const reset = useCallback(() => {
    setResult({
      products: [],
      rawData: [],
      columns: [],
      fileName: '',
      fileType: null,
      error: null,
      loading: false,
    });
  }, []);

  // Parse Excel file
  const parseExcel = useCallback(async (file: globalThis.File): Promise<FileParseResult> => {
    setResult((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const arrayBuffer = await file.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: 'array' });

      // Get first sheet
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];

      // Parse to JSON
      const rawData = XLSX.utils.sheet_to_json<Record<string, unknown>>(worksheet, {
        defval: null,
        blankrows: false,
      });

      // Get column names from first row
      const columns = rawData.length > 0 ? Object.keys(rawData[0]) : [];

      const newResult: FileParseResult = {
        products: [],
        rawData,
        columns,
        fileName: file.name,
        fileType: 'excel',
        error: null,
        loading: false,
      };

      setResult(newResult);
      return newResult;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Errore parsing Excel';
      const errorResult: FileParseResult = {
        products: [],
        rawData: [],
        columns: [],
        fileName: file.name,
        fileType: 'excel',
        error,
        loading: false,
      };
      setResult(errorResult);
      return errorResult;
    }
  }, []);

  // Parse Word/DOCX file
  const parseWord = useCallback(async (file: globalThis.File): Promise<FileParseResult> => {
    setResult((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const arrayBuffer = await file.arrayBuffer();

      // Convert to HTML
      const htmlResult = await mammoth.convertToHtml({ arrayBuffer });
      const html = htmlResult.value;

      // Extract tables from HTML
      const tableRegex = /<table[^>]*>([\s\S]*?)<\/table>/gi;
      const tables = html.match(tableRegex) || [];

      if (tables.length === 0) {
        throw new Error('Nessuna tabella trovata nel documento Word');
      }

      // Parse first table
      const rawData = parseHtmlTable(tables[0]!);
      const columns = rawData.length > 0 ? Object.keys(rawData[0]) : [];

      const newResult: FileParseResult = {
        products: [],
        rawData,
        columns,
        fileName: file.name,
        fileType: 'word',
        error: null,
        loading: false,
      };

      setResult(newResult);
      return newResult;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Errore parsing Word';
      const errorResult: FileParseResult = {
        products: [],
        rawData: [],
        columns: [],
        fileName: file.name,
        fileType: 'word',
        error,
        loading: false,
      };
      setResult(errorResult);
      return errorResult;
    }
  }, []);

  // Map columns to products (accepts optional data to bypass async state)
  const mapToProducts = useCallback(
    (mapping: ColumnMapping, data?: Record<string, unknown>[]): ParsedProduct[] => {
      const products: ParsedProduct[] = [];
      const rawData = data ?? result.rawData;

      for (const row of rawData) {
        const descrizione = String(row[mapping.descrizione] || '').trim();
        if (!descrizione) continue;

        const priceRaw = row[mapping.price];
        const price = parsePrice(priceRaw);

        const qtyRaw = mapping.qty ? row[mapping.qty] : 1;
        const qty = parseNumber(qtyRaw) || 1;

        const sku = mapping.sku ? String(row[mapping.sku] || '').trim() : undefined;

        products.push({
          sku,
          descrizione,
          qty,
          price,
        });
      }

      setResult((prev) => ({ ...prev, products }));
      return products;
    },
    [result.rawData]
  );

  // Auto-detect column mapping (accepts optional columns to bypass async state)
  const autoDetectMapping = useCallback((cols?: string[]): ColumnMapping | null => {
    const columns = cols ?? result.columns;
    if (columns.length === 0) return null;

    // Find description column
    const descPatterns = ['descrizione', 'description', 'prodotto', 'product', 'nome', 'name', 'articolo'];
    const descCol = columns.find((c) =>
      descPatterns.some((p) => c.toLowerCase().includes(p))
    );

    // Find price column
    const pricePatterns = ['prezzo', 'price', 'costo', 'cost', 'importo', 'amount', 'euro', '€'];
    const priceCol = columns.find((c) =>
      pricePatterns.some((p) => c.toLowerCase().includes(p))
    );

    // Find quantity column
    const qtyPatterns = ['qty', 'quantit', 'quantity', 'qta', 'pezzi', 'units'];
    const qtyCol = columns.find((c) =>
      qtyPatterns.some((p) => c.toLowerCase().includes(p))
    );

    // Find SKU column
    const skuPatterns = ['sku', 'codice', 'code', 'cod', 'ref', 'articolo'];
    const skuCol = columns.find((c) =>
      skuPatterns.some((p) => c.toLowerCase().includes(p))
    );

    if (!descCol || !priceCol) return null;

    return {
      descrizione: descCol,
      price: priceCol,
      qty: qtyCol,
      sku: skuCol,
    };
  }, [result.columns]);

  // Parse any supported file
  const parseFile = useCallback(
    async (file: globalThis.File): Promise<FileParseResult> => {
      const ext = file.name.split('.').pop()?.toLowerCase();

      if (ext === 'xlsx' || ext === 'xls' || ext === 'csv') {
        return parseExcel(file);
      } else if (ext === 'docx') {
        return parseWord(file);
      } else {
        const errorResult: FileParseResult = {
          products: [],
          rawData: [],
          columns: [],
          fileName: file.name,
          fileType: null,
          error: `Formato non supportato: .${ext}. Usa Excel (.xlsx, .xls, .csv) o Word (.docx)`,
          loading: false,
        };
        setResult(errorResult);
        return errorResult;
      }
    },
    [parseExcel, parseWord]
  );

  return {
    ...result,
    parseFile,
    parseExcel,
    parseWord,
    mapToProducts,
    autoDetectMapping,
    reset,
  };
}

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

function parseHtmlTable(tableHtml: string): Record<string, unknown>[] {
  const rows: Record<string, unknown>[] = [];

  // Extract header row
  const headerMatch = tableHtml.match(/<tr[^>]*>([\s\S]*?)<\/tr>/i);
  if (!headerMatch) return rows;

  const headerCells = headerMatch[1].match(/<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/gi) || [];
  const headers = headerCells.map((cell) =>
    cell.replace(/<[^>]+>/g, '').trim()
  );

  // Extract data rows
  const rowMatches = tableHtml.match(/<tr[^>]*>([\s\S]*?)<\/tr>/gi) || [];

  for (let i = 1; i < rowMatches.length; i++) {
    const cells = rowMatches[i].match(/<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/gi) || [];
    const rowData: Record<string, unknown> = {};

    cells.forEach((cell, idx) => {
      const value = cell.replace(/<[^>]+>/g, '').trim();
      const key = headers[idx] || `col${idx}`;
      rowData[key] = value;
    });

    if (Object.keys(rowData).length > 0) {
      rows.push(rowData);
    }
  }

  return rows;
}

function parsePrice(value: unknown): number {
  if (typeof value === 'number') return value;
  if (!value) return 0;

  const str = String(value)
    .replace(/[€$£]/g, '')
    .replace(/\s/g, '')
    .replace(',', '.');

  const num = parseFloat(str);
  return isNaN(num) ? 0 : num;
}

function parseNumber(value: unknown): number {
  if (typeof value === 'number') return value;
  if (!value) return 0;

  const num = parseFloat(String(value).replace(',', '.'));
  return isNaN(num) ? 0 : num;
}
