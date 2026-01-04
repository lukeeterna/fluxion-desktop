// ═══════════════════════════════════════════════════════════════════
// FLUXION - Cliente Dialog
// Dialog for creating and editing clienti (with Loyalty - Fase 5)
// ═══════════════════════════════════════════════════════════════════

import { type FC } from 'react';
import type { Cliente, CreateClienteInput, UpdateClienteInput } from '@/types/cliente';
import { ClienteForm } from './ClienteForm';
import { LoyaltyProgress } from '@/components/loyalty/LoyaltyProgress';
import { PacchettiList } from '@/components/loyalty/PacchettiList';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User, Star, Package } from 'lucide-react';

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

  // In create mode, show simple form
  if (!isEditMode) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-950 border-slate-800">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-white">
              Nuovo Cliente
            </DialogTitle>
            <DialogDescription className="text-slate-400">
              Inserisci i dati del nuovo cliente. I campi contrassegnati con * sono obbligatori.
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
  }

  // In edit mode, show tabs with Dati, Fedeltà, Pacchetti
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white">
            {cliente.nome} {cliente.cognome}
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Gestisci dati, fedeltà e pacchetti del cliente
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="dati" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-slate-900">
            <TabsTrigger value="dati" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Dati
            </TabsTrigger>
            <TabsTrigger value="fedelta" className="flex items-center gap-2">
              <Star className="h-4 w-4" />
              Fedeltà
            </TabsTrigger>
            <TabsTrigger value="pacchetti" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              Pacchetti
            </TabsTrigger>
          </TabsList>

          {/* Tab: Dati Cliente */}
          <TabsContent value="dati" className="mt-4">
            <ClienteForm
              cliente={cliente}
              onSubmit={onSubmit}
              onCancel={() => onOpenChange(false)}
              isSubmitting={isSubmitting}
            />
          </TabsContent>

          {/* Tab: Fedeltà (Tessera Timbri) */}
          <TabsContent value="fedelta" className="mt-4">
            <LoyaltyProgress clienteId={cliente.id} showVipToggle />
          </TabsContent>

          {/* Tab: Pacchetti */}
          <TabsContent value="pacchetti" className="mt-4">
            <PacchettiList clienteId={cliente.id} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
