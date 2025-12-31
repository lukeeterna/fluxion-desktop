// ═══════════════════════════════════════════════════════════════════
// FLUXION - Cliente Dialog
// Dialog for creating and editing clienti
// ═══════════════════════════════════════════════════════════════════

import { type FC } from 'react';
import type { Cliente, CreateClienteInput, UpdateClienteInput } from '@/types/cliente';
import { ClienteForm } from './ClienteForm';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface ClienteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  cliente?: Cliente; // If provided, dialog is in edit mode
  onSubmit: (data: CreateClienteInput | UpdateClienteInput) => void;
  isSubmitting?: boolean;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const ClienteDialog: FC<ClienteDialogProps> = ({
  open,
  onOpenChange,
  cliente,
  onSubmit,
  isSubmitting = false,
}) => {
  const isEditMode = !!cliente;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white">
            {isEditMode ? 'Modifica Cliente' : 'Nuovo Cliente'}
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            {isEditMode
              ? 'Modifica i dati del cliente. I campi contrassegnati con * sono obbligatori.'
              : 'Inserisci i dati del nuovo cliente. I campi contrassegnati con * sono obbligatori.'}
          </DialogDescription>
        </DialogHeader>

        <ClienteForm
          cliente={cliente}
          onSubmit={onSubmit}
          onCancel={() => onOpenChange(false)}
          isSubmitting={isSubmitting}
        />
      </DialogContent>
    </Dialog>
  );
};
