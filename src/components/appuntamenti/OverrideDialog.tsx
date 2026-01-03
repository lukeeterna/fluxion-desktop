// ═══════════════════════════════════════════════════════════════════
// FLUXION - OverrideDialog Component
// Dialog per conferma override warnings
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Shield } from 'lucide-react';
import type {
  ValidationResultDto,
  WarningDto,
  ConfermaConOverrideDto,
} from '@/types/appuntamento-ddd.types';

// ───────────────────────────────────────────────────────────────────
// Component Props
// ───────────────────────────────────────────────────────────────────

export interface OverrideDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Appuntamento ID da confermare */
  appuntamentoId: string;
  /** Operatore ID che esegue override */
  operatoreId: string;
  /** Validation result con warnings */
  validation: ValidationResultDto;
  /** Callback quando utente conferma override */
  onConfirm: (dto: ConfermaConOverrideDto) => void;
  /** Loading state */
  isLoading?: boolean;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export function OverrideDialog({
  open,
  onOpenChange,
  appuntamentoId,
  operatoreId,
  validation,
  onConfirm,
  isLoading = false,
}: OverrideDialogProps) {
  const [motivazione, setMotivazione] = useState('');
  const [confermato, setConfermato] = useState(false);

  const handleConfirm = () => {
    if (!confermato) return;

    const warningsIgnorati = validation.warnings.map((w) => w.tipo);

    onConfirm({
      appuntamento_id: appuntamentoId,
      operatore_id: operatoreId,
      motivazione: motivazione.trim() || undefined,
      warnings_ignorati: warningsIgnorati,
    });

    // Reset state
    setMotivazione('');
    setConfermato(false);
  };

  const handleCancel = () => {
    setMotivazione('');
    setConfermato(false);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-orange-600" />
            Conferma con Override
          </DialogTitle>
          <DialogDescription>
            Stai per confermare un appuntamento ignorando {validation.warnings.length} avvisi.
            Questa azione sarà tracciata per audit.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Lista warnings da ignorare */}
          <div>
            <Label className="text-sm font-semibold">Avvisi che verranno ignorati:</Label>
            <div className="mt-2 space-y-2 bg-orange-50 dark:bg-orange-950 p-3 rounded-md border border-orange-200">
              {validation.warnings.map((warning: WarningDto, idx: number) => (
                <div key={idx} className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 mt-0.5 text-orange-600 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-orange-900 dark:text-orange-100">
                      {warning.messaggio}
                    </p>
                    <Badge
                      variant="outline"
                      className="mt-1 text-xs border-orange-500 text-orange-700"
                    >
                      {warning.tipo}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Campo motivazione (opzionale ma consigliato) */}
          <div>
            <Label htmlFor="motivazione" className="text-sm font-semibold">
              Motivazione (consigliato per audit):
            </Label>
            <Textarea
              id="motivazione"
              placeholder="Es: Cliente urgente, emergenza, richiesta speciale..."
              value={motivazione}
              onChange={(e) => setMotivazione(e.target.value)}
              rows={3}
              className="mt-1"
              disabled={isLoading}
            />
            <p className="mt-1 text-xs text-muted-foreground">
              La motivazione aiuta a giustificare l'override in caso di review.
            </p>
          </div>

          {/* Checkbox conferma */}
          <div className="flex items-start gap-3 bg-yellow-50 dark:bg-yellow-950 p-3 rounded-md border border-yellow-200">
            <Checkbox
              id="conferma-override"
              checked={confermato}
              onCheckedChange={(checked) => setConfermato(checked === true)}
              disabled={isLoading}
            />
            <div className="flex-1">
              <Label
                htmlFor="conferma-override"
                className="text-sm font-semibold text-yellow-900 dark:text-yellow-100 cursor-pointer"
              >
                Confermo di voler procedere con l'override
              </Label>
              <p className="text-xs text-yellow-800 dark:text-yellow-200 mt-1">
                Ho preso visione degli avvisi e assumo la responsabilità di questa conferma.
                L'override sarà registrato con timestamp, ID operatore e motivazione.
              </p>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleCancel} disabled={isLoading}>
            Annulla
          </Button>
          <Button
            variant="default"
            onClick={handleConfirm}
            disabled={!confermato || isLoading}
            className="bg-orange-600 hover:bg-orange-700"
          >
            {isLoading ? 'Confermando...' : 'Conferma Override'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ───────────────────────────────────────────────────────────────────
// Helper Hook
// ───────────────────────────────────────────────────────────────────

/**
 * Hook per gestire dialog override
 *
 * @example
 * const override = useOverrideDialog();
 *
 * // Mostra dialog
 * override.open({
 *   appuntamentoId: "...",
 *   operatoreId: "...",
 *   validation: validationResult,
 *   onConfirm: (dto) => mutate(dto)
 * });
 *
 * // Render
 * <OverrideDialog {...override.props} />
 */
export function useOverrideDialog() {
  const [isOpen, setIsOpen] = useState(false);
  const [props, setProps] = useState<Omit<OverrideDialogProps, 'open' | 'onOpenChange'> | null>(
    null
  );

  const open = (
    config: Omit<OverrideDialogProps, 'open' | 'onOpenChange'>
  ) => {
    setProps(config);
    setIsOpen(true);
  };

  const close = () => {
    setIsOpen(false);
    setTimeout(() => setProps(null), 200); // Delay per animazione
  };

  return {
    open,
    close,
    props: props
      ? {
          ...props,
          open: isOpen,
          onOpenChange: setIsOpen,
        }
      : null,
  };
}
