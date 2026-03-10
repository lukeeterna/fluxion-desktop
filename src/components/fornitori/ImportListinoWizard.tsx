// ═══════════════════════════════════════════════════════════════════
// FLUXION - Import Listino Wizard (Gap #5)
// Wizard 6-step: Upload → Sheet → Header → Map → Validate → Confirm
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useCallback, useRef } from 'react';
import { Upload, ChevronRight, ChevronLeft, Check, AlertTriangle, Info, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import type { WizardState, TargetColumn, ColumnMapping, ValidatedRow } from '@/types/listino';
import {
  parseWorkbook,
  autoDetectHeaderRow,
  buildColumnMappings,
  validateRows,
  validatedRowsToImportInput,
} from '@/lib/listino-utils';
import { useImportListino } from '@/hooks/use-listini';

// ─── Constants ────────────────────────────────────────────────────

const TARGET_COLUMN_LABELS: Record<TargetColumn, string> = {
  codice_articolo: 'Codice Articolo',
  descrizione: 'Descrizione',
  unita_misura: 'Unità Misura',
  prezzo_acquisto: 'Prezzo Acquisto',
  sconto_pct: 'Sconto %',
  prezzo_netto: 'Prezzo Netto',
  iva_pct: 'IVA %',
  categoria: 'Categoria',
  ean: 'EAN / Barcode',
  note: 'Note',
  __skip__: '— Ignora —',
};

const ALL_TARGETS = Object.keys(TARGET_COLUMN_LABELS) as TargetColumn[];

const INITIAL_STATE: WizardState = {
  step: 1,
  file: null,
  formato: null,
  sheets: [],
  selectedSheetIndex: 0,
  headerRowIndex: 0,
  columnMappings: [],
  validatedRows: [],
  ricaricoPct: 0,
  nomeListino: '',
  dataValidita: '',
};

// ─── Props ────────────────────────────────────────────────────────

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fornitoreId: string;
  fornitoreNome: string;
}

// ═══════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════

export const ImportListinoWizard: FC<Props> = ({ open, onOpenChange, fornitoreId, fornitoreNome }) => {
  const [state, setState] = useState<WizardState>(INITIAL_STATE);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const importMutation = useImportListino();

  const reset = useCallback(() => setState(INITIAL_STATE), []);

  const handleClose = () => {
    reset();
    onOpenChange(false);
  };

  // ─── Step 1: Upload ──────────────────────────────────────────────

  const handleFileSelect = useCallback(async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase() ?? '';
    if (!['xlsx', 'xls', 'csv'].includes(ext)) {
      toast.error('Formato non supportato', { description: 'Usa .xlsx, .xls o .csv' });
      return;
    }

    const buffer = await file.arrayBuffer();
    const { sheets, formato } = parseWorkbook(buffer, file.name);

    if (sheets.length === 0 || sheets[0].rows.length === 0) {
      toast.error('File vuoto o non leggibile');
      return;
    }

    const defaultName = file.name.replace(/\.[^.]+$/, '');
    const headerIdx = autoDetectHeaderRow(sheets[0].rows);
    const headerRow = sheets[0].rows[headerIdx] ?? [];
    const mappings = buildColumnMappings(headerRow);

    setState((s) => ({
      ...s,
      file,
      formato,
      sheets,
      selectedSheetIndex: 0,
      headerRowIndex: headerIdx,
      columnMappings: mappings,
      nomeListino: defaultName,
      step: sheets.length > 1 ? 2 : 3, // skip step 2 se single-sheet
    }));
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) void handleFileSelect(file);
    },
    [handleFileSelect]
  );

  // ─── Step 2: Sheet select ─────────────────────────────────────────

  const handleSheetSelect = (idx: number) => {
    const sheet = state.sheets[idx];
    const headerIdx = autoDetectHeaderRow(sheet.rows);
    const headerRow = sheet.rows[headerIdx] ?? [];
    const mappings = buildColumnMappings(headerRow);
    setState((s) => ({
      ...s,
      selectedSheetIndex: idx,
      headerRowIndex: headerIdx,
      columnMappings: mappings,
      step: 3,
    }));
  };

  // ─── Step 3: Header detect / slider ──────────────────────────────

  const handleHeaderRowChange = (rowIdx: number) => {
    const sheet = state.sheets[state.selectedSheetIndex];
    const headerRow = sheet?.rows[rowIdx] ?? [];
    const mappings = buildColumnMappings(headerRow);
    setState((s) => ({ ...s, headerRowIndex: rowIdx, columnMappings: mappings }));
  };

  const goToStep4 = () => setState((s) => ({ ...s, step: 4 }));

  // ─── Step 4: Column mapping ───────────────────────────────────────

  const updateMapping = (sourceIndex: number, targetColumn: TargetColumn) => {
    setState((s) => ({
      ...s,
      columnMappings: s.columnMappings.map((m) =>
        m.sourceIndex === sourceIndex ? { ...m, targetColumn } : m
      ),
    }));
  };

  const goToStep5 = () => {
    const sheet = state.sheets[state.selectedSheetIndex];
    const dataRows = sheet.rows.slice(state.headerRowIndex + 1);
    const validated = validateRows(dataRows, state.columnMappings, state.ricaricoPct);
    setState((s) => ({ ...s, validatedRows: validated, step: 5 }));
  };

  // ─── Step 6: Import ───────────────────────────────────────────────

  const handleImport = async () => {
    const righe = validatedRowsToImportInput(state.validatedRows);
    if (righe.length === 0) {
      toast.error('Nessuna riga valida da importare');
      return;
    }

    setState((s) => ({ ...s, step: 6 }));

    try {
      const result = await importMutation.mutateAsync({
        fornitore_id: fornitoreId,
        nome_listino: state.nomeListino || `Listino ${new Date().toLocaleDateString('it-IT')}`,
        data_validita: state.dataValidita || undefined,
        formato_fonte: state.formato ?? 'xlsx',
        righe,
      });

      toast.success('Listino importato', {
        description: `${result.righe_inserite} inseriti · ${result.righe_aggiornate} aggiornati · ${result.variazioni_registrate} variazioni registrate`,
      });
      handleClose();
    } catch (err) {
      toast.error('Errore importazione', { description: String(err) });
      setState((s) => ({ ...s, step: 5 }));
    }
  };

  // ─── Current sheet data ───────────────────────────────────────────

  const currentSheet = state.sheets[state.selectedSheetIndex];
  const previewRows = currentSheet?.rows.slice(
    state.headerRowIndex,
    state.headerRowIndex + 11
  ) ?? [];
  const errorCount = state.validatedRows.filter((r) => r.errors.length > 0).length;
  const validCount = state.validatedRows.filter((r) => r.errors.length === 0).length;
  const warnCount = state.validatedRows.filter((r) => r.warnings.length > 0 && r.errors.length === 0).length;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="bg-slate-950 border-slate-800 max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Upload className="w-5 h-5 text-cyan-500" />
            Import Listino — {fornitoreNome}
          </DialogTitle>
        </DialogHeader>

        {/* Step indicator */}
        <StepIndicator step={state.step} />

        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-[55vh] pr-2">
            {/* STEP 1 — Upload */}
            {state.step === 1 && (
              <Step1Upload
                onFileSelect={handleFileSelect}
                onDrop={handleDrop}
                fileInputRef={fileInputRef}
              />
            )}

            {/* STEP 2 — Sheet select */}
            {state.step === 2 && (
              <Step2SheetSelect
                sheets={state.sheets}
                selectedIndex={state.selectedSheetIndex}
                onSelect={handleSheetSelect}
              />
            )}

            {/* STEP 3 — Header detect */}
            {state.step === 3 && (
              <Step3HeaderDetect
                rows={currentSheet?.rows ?? []}
                headerRowIndex={state.headerRowIndex}
                onChange={handleHeaderRowChange}
                nomeListino={state.nomeListino}
                dataValidita={state.dataValidita}
                onNomeChange={(v) => setState((s) => ({ ...s, nomeListino: v }))}
                onDataValiditaChange={(v) => setState((s) => ({ ...s, dataValidita: v }))}
              />
            )}

            {/* STEP 4 — Column mapping */}
            {state.step === 4 && (
              <Step4ColumnMap
                mappings={state.columnMappings}
                previewRows={previewRows}
                onUpdateMapping={updateMapping}
              />
            )}

            {/* STEP 5 — Validate */}
            {state.step === 5 && (
              <Step5Validate
                rows={state.validatedRows}
                validCount={validCount}
                errorCount={errorCount}
                warnCount={warnCount}
                ricaricoPct={state.ricaricoPct}
                onRicaricoChange={(v) => setState((s) => ({ ...s, ricaricoPct: v }))}
              />
            )}

            {/* STEP 6 — Confirm / Progress */}
            {state.step === 6 && (
              <Step6Confirm isPending={importMutation.isPending} />
            )}
          </ScrollArea>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <Button
            variant="outline"
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
            onClick={() => {
              if (state.step === 1) handleClose();
              else if (state.step === 3 && state.sheets.length > 1) setState((s) => ({ ...s, step: 2 }));
              else setState((s) => ({ ...s, step: (s.step - 1) as WizardState['step'] }));
            }}
            disabled={state.step === 6}
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            {state.step === 1 ? 'Annulla' : 'Indietro'}
          </Button>

          {state.step < 5 && state.step !== 1 && (
            <Button
              className="bg-cyan-500 hover:bg-cyan-600 text-white"
              onClick={() => {
                if (state.step === 3) goToStep4();
                else if (state.step === 4) goToStep5();
              }}
            >
              Avanti
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          )}

          {state.step === 5 && (
            <Button
              className="bg-green-600 hover:bg-green-700 text-white"
              onClick={() => void handleImport()}
              disabled={validCount === 0}
            >
              <Check className="w-4 h-4 mr-2" />
              Importa {validCount} righe
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ═══════════════════════════════════════════════════════════════════
// SUB-COMPONENTS
// ═══════════════════════════════════════════════════════════════════

// ─── Step indicator ───────────────────────────────────────────────

const STEPS = ['Upload', 'Foglio', 'Intestazione', 'Colonne', 'Valida', 'Importa'];

const StepIndicator: FC<{ step: number }> = ({ step }) => (
  <div className="flex items-center gap-1 mb-4">
    {STEPS.map((label, i) => {
      const n = i + 1;
      const active = n === step;
      const done = n < step;
      return (
        <div key={label} className="flex items-center gap-1 flex-1">
          <div
            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0
              ${done ? 'bg-green-600 text-white' : active ? 'bg-cyan-500 text-white' : 'bg-slate-800 text-slate-500'}`}
          >
            {done ? <Check className="w-3 h-3" /> : n}
          </div>
          <span className={`text-xs hidden sm:block ${active ? 'text-white' : 'text-slate-500'}`}>
            {label}
          </span>
          {i < STEPS.length - 1 && (
            <div className={`flex-1 h-px mx-1 ${done ? 'bg-green-600' : 'bg-slate-800'}`} />
          )}
        </div>
      );
    })}
  </div>
);

// ─── Step 1 ───────────────────────────────────────────────────────

const Step1Upload: FC<{
  onFileSelect: (f: File) => void;
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
}> = ({ onFileSelect, onDrop, fileInputRef }) => (
  <div className="space-y-6">
    <div
      className="border-2 border-dashed border-slate-700 rounded-xl p-12 text-center cursor-pointer hover:border-cyan-500 transition-colors"
      onDrop={onDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={() => fileInputRef.current?.click()}
    >
      <Upload className="w-12 h-12 text-cyan-500 mx-auto mb-4" />
      <p className="text-white font-medium text-lg">Trascina il listino qui</p>
      <p className="text-slate-400 mt-2">oppure clicca per selezionare il file</p>
      <div className="flex justify-center gap-2 mt-4">
        {['XLSX', 'XLS', 'CSV'].map((ext) => (
          <Badge key={ext} variant="outline" className="border-slate-600 text-slate-400">
            .{ext.toLowerCase()}
          </Badge>
        ))}
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xls,.csv"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) void onFileSelect(f);
        }}
      />
    </div>
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
      <p className="text-slate-400 text-sm flex items-start gap-2">
        <Info className="w-4 h-4 text-cyan-500 shrink-0 mt-0.5" />
        FLUXION rileva automaticamente le intestazioni e suggerisce il mapping delle colonne.
        Funziona anche con listini non-standard (logo in cima, righe vuote, merged cells).
      </p>
    </div>
  </div>
);

// ─── Step 2 ───────────────────────────────────────────────────────

const Step2SheetSelect: FC<{
  sheets: { name: string; rows: string[][] }[];
  selectedIndex: number;
  onSelect: (idx: number) => void;
}> = ({ sheets, selectedIndex, onSelect }) => (
  <div className="space-y-3">
    <p className="text-slate-400 text-sm">Il file contiene più fogli. Seleziona quello con il listino prezzi:</p>
    {sheets.map((s, i) => (
      <button
        key={i}
        onClick={() => onSelect(i)}
        className={`w-full text-left p-4 rounded-lg border transition-colors
          ${selectedIndex === i ? 'border-cyan-500 bg-cyan-500/10' : 'border-slate-700 hover:border-slate-600'}`}
      >
        <p className="text-white font-medium">{s.name}</p>
        <p className="text-slate-400 text-sm">{s.rows.length} righe</p>
      </button>
    ))}
  </div>
);

// ─── Step 3 ───────────────────────────────────────────────────────

const Step3HeaderDetect: FC<{
  rows: string[][];
  headerRowIndex: number;
  onChange: (idx: number) => void;
  nomeListino: string;
  dataValidita: string;
  onNomeChange: (v: string) => void;
  onDataValiditaChange: (v: string) => void;
}> = ({ rows, headerRowIndex, onChange, nomeListino, dataValidita, onNomeChange, onDataValiditaChange }) => {
  const maxRows = Math.min(rows.length - 1, 12);
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <Label className="text-slate-300">Nome listino</Label>
          <Input
            value={nomeListino}
            onChange={(e) => onNomeChange(e.target.value)}
            className="bg-slate-900 border-slate-700 text-white"
            placeholder="Es. Listino Primavera 2026"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-slate-300">Validità (opzionale)</Label>
          <Input
            type="date"
            value={dataValidita}
            onChange={(e) => onDataValiditaChange(e.target.value)}
            className="bg-slate-900 border-slate-700 text-white"
          />
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label className="text-slate-300">Riga intestazione (riga {headerRowIndex + 1})</Label>
          <span className="text-cyan-400 text-sm font-mono">Riga {headerRowIndex + 1} / {rows.length}</span>
        </div>
        <Slider
          min={0}
          max={maxRows}
          step={1}
          value={[headerRowIndex]}
          onValueChange={([v]) => onChange(v)}
          className="w-full"
        />
        {/* Preview prime 3 righe intorno all'intestazione selezionata */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <tbody>
                {rows.slice(Math.max(0, headerRowIndex - 1), headerRowIndex + 3).map((row, ri) => {
                  const absRow = Math.max(0, headerRowIndex - 1) + ri;
                  const isHeader = absRow === headerRowIndex;
                  return (
                    <tr key={ri} className={isHeader ? 'bg-cyan-500/20' : ''}>
                      <td className="px-2 py-1.5 text-slate-500 border-r border-slate-800 w-8">
                        {absRow + 1}
                      </td>
                      {row.slice(0, 6).map((cell, ci) => (
                        <td
                          key={ci}
                          className={`px-3 py-1.5 border-r border-slate-800 truncate max-w-[120px]
                            ${isHeader ? 'text-cyan-400 font-semibold' : 'text-slate-300'}`}
                        >
                          {cell || <span className="text-slate-600">—</span>}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Step 4 ───────────────────────────────────────────────────────

const Step4ColumnMap: FC<{
  mappings: ColumnMapping[];
  previewRows: string[][];
  onUpdateMapping: (srcIdx: number, target: TargetColumn) => void;
}> = ({ mappings, previewRows, onUpdateMapping }) => {
  const usedTargets = new Set(mappings.filter((m) => m.targetColumn !== '__skip__').map((m) => m.targetColumn));

  return (
    <div className="space-y-3">
      <p className="text-slate-400 text-sm">
        FLUXION ha suggerito il mapping automatico. Verifica e correggi se necessario.
      </p>
      <div className="space-y-2">
        {mappings.map((m) => {
          const previewVals = previewRows.slice(1, 4).map((r) => r[m.sourceIndex] ?? '').filter(Boolean);
          return (
            <div key={m.sourceIndex} className="flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-lg p-3">
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">{m.sourceHeader || `Colonna ${m.sourceIndex + 1}`}</p>
                <p className="text-slate-500 text-xs truncate">{previewVals.join(' · ') || '—'}</p>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-600 shrink-0" />
              <div className="w-44 shrink-0">
                <Select
                  value={m.targetColumn}
                  onValueChange={(v) => onUpdateMapping(m.sourceIndex, v as TargetColumn)}
                >
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white text-xs h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-700">
                    {ALL_TARGETS.map((t) => (
                      <SelectItem
                        key={t}
                        value={t}
                        className="text-white text-xs"
                        disabled={t !== '__skip__' && t !== m.targetColumn && usedTargets.has(t)}
                      >
                        {TARGET_COLUMN_LABELS[t]}
                        {t !== '__skip__' && t !== m.targetColumn && usedTargets.has(t) && ' ✓'}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ─── Step 5 ───────────────────────────────────────────────────────

const Step5Validate: FC<{
  rows: ValidatedRow[];
  validCount: number;
  errorCount: number;
  warnCount: number;
  ricaricoPct: number;
  onRicaricoChange: (v: number) => void;
}> = ({ rows, validCount, errorCount, warnCount, ricaricoPct, onRicaricoChange }) => {
  const preview = rows.slice(0, 10);

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-green-900/20 border border-green-800 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-green-400">{validCount}</p>
          <p className="text-green-300 text-xs">Righe valide</p>
        </div>
        <div className={`border rounded-lg p-3 text-center ${warnCount > 0 ? 'bg-yellow-900/20 border-yellow-800' : 'bg-slate-900 border-slate-800'}`}>
          <p className={`text-2xl font-bold ${warnCount > 0 ? 'text-yellow-400' : 'text-slate-500'}`}>{warnCount}</p>
          <p className={`text-xs ${warnCount > 0 ? 'text-yellow-300' : 'text-slate-500'}`}>Con avvisi</p>
        </div>
        <div className={`border rounded-lg p-3 text-center ${errorCount > 0 ? 'bg-red-900/20 border-red-800' : 'bg-slate-900 border-slate-800'}`}>
          <p className={`text-2xl font-bold ${errorCount > 0 ? 'text-red-400' : 'text-slate-500'}`}>{errorCount}</p>
          <p className={`text-xs ${errorCount > 0 ? 'text-red-300' : 'text-slate-500'}`}>Con errori (escluse)</p>
        </div>
      </div>

      {/* Ricarico */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-slate-300 text-sm">Ricarico suggerito per prezzo vendita</Label>
          <span className="text-cyan-400 font-mono text-sm">{ricaricoPct}%</span>
        </div>
        <Slider
          min={0}
          max={200}
          step={5}
          value={[ricaricoPct]}
          onValueChange={([v]) => onRicaricoChange(v)}
        />
        <p className="text-slate-500 text-xs">
          Il ricarico non modifica il prezzo_acquisto salvato, ma viene mostrato nella colonna "P. Vendita" come riferimento.
        </p>
      </div>

      {/* Preview table */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="px-3 py-2 text-left text-slate-400">Codice</th>
                <th className="px-3 py-2 text-left text-slate-400">Descrizione</th>
                <th className="px-3 py-2 text-right text-slate-400">P. Acquisto</th>
                {ricaricoPct > 0 && <th className="px-3 py-2 text-right text-slate-400">P. Vendita</th>}
                <th className="px-3 py-2 text-center text-slate-400">IVA</th>
                <th className="px-3 py-2 text-center text-slate-400">Stato</th>
              </tr>
            </thead>
            <tbody>
              {preview.map((row) => (
                <tr key={row.rowIndex} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="px-3 py-2 text-slate-400 font-mono">{row.parsed.codice_articolo ?? '—'}</td>
                  <td className="px-3 py-2 text-white truncate max-w-[180px]">{row.parsed.descrizione ?? '—'}</td>
                  <td className="px-3 py-2 text-right text-white">
                    {row.parsed.prezzo_acquisto != null ? `€${row.parsed.prezzo_acquisto.toFixed(2)}` : '—'}
                  </td>
                  {ricaricoPct > 0 && (
                    <td className="px-3 py-2 text-right text-cyan-400">
                      {row.parsed.prezzo_acquisto != null
                        ? `€${(row.parsed.prezzo_acquisto * (1 + ricaricoPct / 100)).toFixed(2)}`
                        : '—'}
                    </td>
                  )}
                  <td className="px-3 py-2 text-center text-slate-400">
                    {row.parsed.iva_pct != null ? `${row.parsed.iva_pct}%` : '22%'}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {row.errors.length > 0 ? (
                      <span title={row.errors.join(', ')}>
                        <X className="w-4 h-4 text-red-400 mx-auto" />
                      </span>
                    ) : row.warnings.length > 0 ? (
                      <span title={row.warnings.join(', ')}>
                        <AlertTriangle className="w-4 h-4 text-yellow-400 mx-auto" />
                      </span>
                    ) : (
                      <Check className="w-4 h-4 text-green-400 mx-auto" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {rows.length > 10 && (
          <p className="text-slate-500 text-xs px-3 py-2 border-t border-slate-800">
            + {rows.length - 10} altre righe non mostrate
          </p>
        )}
      </div>
    </div>
  );
};

// ─── Step 6 ───────────────────────────────────────────────────────

const Step6Confirm: FC<{ isPending: boolean }> = ({ isPending }) => (
  <div className="flex flex-col items-center justify-center py-16 space-y-6">
    {isPending ? (
      <>
        <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-white text-lg font-medium">Importazione in corso...</p>
        <Progress value={undefined} className="w-64" />
      </>
    ) : (
      <>
        <Check className="w-16 h-16 text-green-400" />
        <p className="text-white text-lg font-medium">Completato</p>
      </>
    )}
  </div>
);
