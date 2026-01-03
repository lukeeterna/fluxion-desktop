// ═══════════════════════════════════════════════════════════════════
// FLUXION - ValidationAlert Component
// Display validation results (hard blocks / warnings / suggestions)
// Color-coded: red (hard block), orange (warning), blue (suggestion)
// ═══════════════════════════════════════════════════════════════════

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import {
  AlertCircle,
  AlertTriangle,
  Lightbulb,
  XCircle,
  CheckCircle2,
} from 'lucide-react';
import type {
  ValidationResultDto,
  SuggestionDto,
} from '@/types/appuntamento-ddd.types';

// ───────────────────────────────────────────────────────────────────
// Component Props
// ───────────────────────────────────────────────────────────────────

export interface ValidationAlertProps {
  validation: ValidationResultDto;
  /** Callback when user accepts suggestion */
  onAcceptSuggestion?: (suggestion: SuggestionDto) => void;
  /** Show compact version (only counts) */
  compact?: boolean;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export function ValidationAlert({
  validation,
  onAcceptSuggestion,
  compact = false,
}: ValidationAlertProps) {
  // Se tutto OK, mostra successo
  if (!validation.is_blocked && !validation.has_warnings && !validation.has_suggestions) {
    return (
      <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
        <CheckCircle2 className="h-4 w-4 text-green-600" />
        <AlertTitle className="text-green-900 dark:text-green-100">
          Validazione OK
        </AlertTitle>
        <AlertDescription className="text-green-800 dark:text-green-200">
          Nessun problema rilevato. Puoi procedere con la conferma.
        </AlertDescription>
      </Alert>
    );
  }

  // Mode compact: mostra solo counts
  if (compact) {
    return (
      <div className="flex gap-2">
        {validation.is_blocked && (
          <Badge variant="destructive" className="gap-1">
            <XCircle className="h-3 w-3" />
            {validation.hard_blocks.length} blocco
          </Badge>
        )}
        {validation.has_warnings && (
          <Badge variant="outline" className="gap-1 border-orange-500 text-orange-700">
            <AlertTriangle className="h-3 w-3" />
            {validation.warnings.length} avvisi
          </Badge>
        )}
        {validation.has_suggestions && (
          <Badge variant="outline" className="gap-1 border-blue-500 text-blue-700">
            <Lightbulb className="h-3 w-3" />
            {validation.suggestions.length} suggerimenti
          </Badge>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Hard Blocks (CRITICO) */}
      {validation.is_blocked && (
        <Alert variant="destructive" className="border-red-600 bg-red-50 dark:bg-red-950">
          <XCircle className="h-4 w-4" />
          <AlertTitle className="flex items-center gap-2">
            Errori bloccanti
            <Badge variant="destructive">{validation.hard_blocks.length}</Badge>
          </AlertTitle>
          <AlertDescription>
            <ul className="mt-2 space-y-1 list-disc list-inside">
              {validation.hard_blocks.map((error, idx) => (
                <li key={idx} className="text-sm text-red-800 dark:text-red-200">
                  {error}
                </li>
              ))}
            </ul>
            <p className="mt-2 text-xs text-red-700 dark:text-red-300 font-semibold">
              ❌ Impossibile procedere finché questi errori non sono risolti.
            </p>
          </AlertDescription>
        </Alert>
      )}

      {/* Warnings (continuabili con conferma) */}
      {validation.has_warnings && (
        <Alert className="border-orange-500 bg-orange-50 dark:bg-orange-950">
          <AlertTriangle className="h-4 w-4 text-orange-600" />
          <AlertTitle className="flex items-center gap-2 text-orange-900 dark:text-orange-100">
            Avvisi
            <Badge variant="outline" className="border-orange-500">
              {validation.warnings.length}
            </Badge>
          </AlertTitle>
          <AlertDescription className="text-orange-800 dark:text-orange-200">
            <ul className="mt-2 space-y-2">
              {validation.warnings.map((warning, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0 text-orange-600" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{warning.messaggio}</p>
                    <p className="text-xs text-orange-700 dark:text-orange-300 mt-0.5">
                      Tipo: {warning.tipo}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs text-orange-700 dark:text-orange-300 font-semibold">
              ⚠️ Puoi continuare confermando di aver preso visione degli avvisi (override).
            </p>
          </AlertDescription>
        </Alert>
      )}

      {/* Suggestions (proattivi, non bloccanti) */}
      {validation.has_suggestions && (
        <Alert className="border-blue-500 bg-blue-50 dark:bg-blue-950">
          <Lightbulb className="h-4 w-4 text-blue-600" />
          <AlertTitle className="flex items-center gap-2 text-blue-900 dark:text-blue-100">
            Suggerimenti
            <Badge variant="outline" className="border-blue-500">
              {validation.suggestions.length}
            </Badge>
          </AlertTitle>
          <AlertDescription className="text-blue-800 dark:text-blue-200">
            <ul className="mt-2 space-y-2">
              {validation.suggestions.map((suggestion, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <Lightbulb className="h-4 w-4 mt-0.5 flex-shrink-0 text-blue-600" />
                  <div className="flex-1">
                    <p className="text-sm">{suggestion.messaggio}</p>
                    {onAcceptSuggestion && (
                      <button
                        onClick={() => onAcceptSuggestion(suggestion)}
                        className="mt-1 text-xs text-blue-700 dark:text-blue-300 underline hover:no-underline"
                      >
                        Applica suggerimento
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs text-blue-700 dark:text-blue-300">
              💡 Suggerimenti opzionali per migliorare la pianificazione.
            </p>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

// ───────────────────────────────────────────────────────────────────
// Validation Summary (counts only)
// ───────────────────────────────────────────────────────────────────

export interface ValidationSummaryProps {
  validation: ValidationResultDto;
}

export function ValidationSummary({ validation }: ValidationSummaryProps) {
  return <ValidationAlert validation={validation} compact={true} />;
}
