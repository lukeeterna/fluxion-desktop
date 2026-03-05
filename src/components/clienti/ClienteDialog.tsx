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
import { Badge } from '@/components/ui/badge';
import { User, Star, Package, Calendar, Loader2, ClipboardList } from 'lucide-react';
import { SchedaClienteDynamic } from '@/components/schede-cliente/SchedaClienteDynamic';
import { useAppuntamenti } from '@/hooks/use-appuntamenti';

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

// ───────────────────────────────────────────────────────────────────
// ClienteStorico — tab storico appuntamenti (A5 CoVe2026)
// ───────────────────────────────────────────────────────────────────

const STATO_COLORS: Record<string, string> = {
  completato: 'bg-green-500/20 text-green-400',
  confermato: 'bg-blue-500/20 text-blue-400',
  in_attesa: 'bg-yellow-500/20 text-yellow-400',
  cancellato: 'bg-red-500/20 text-red-400',
  no_show: 'bg-slate-500/20 text-slate-400',
};

function ClienteStorico({ clienteId }: { clienteId: string }) {
  // range ampio: ultimi 5 anni → prossimi 2 anni
  const start = new Date(); start.setFullYear(start.getFullYear() - 5);
  const end   = new Date(); end.setFullYear(end.getFullYear() + 2);
  const fmt = (d: Date) => d.toISOString().slice(0, 10);

  const { data: appuntamenti, isLoading } = useAppuntamenti({
    start_date: fmt(start),
    end_date: fmt(end),
    cliente_id: clienteId,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8 text-slate-400">
        <Loader2 className="h-5 w-5 animate-spin mr-2" />
        Caricamento storico...
      </div>
    );
  }

  if (!appuntamenti?.length) {
    return (
      <p className="text-center text-slate-400 py-8">Nessun appuntamento registrato.</p>
    );
  }

  const sorted = [...appuntamenti].sort(
    (a, b) => new Date(b.data_ora_inizio).getTime() - new Date(a.data_ora_inizio).getTime()
  );

  return (
    <div className="space-y-2 max-h-80 overflow-y-auto">
      {sorted.map((a) => {
        const data = new Date(a.data_ora_inizio);
        const statoKey = a.stato?.toLowerCase() ?? '';
        return (
          <div
            key={a.id}
            className="flex items-center justify-between rounded-lg bg-slate-900 px-4 py-3"
          >
            <div className="flex flex-col">
              <span className="text-sm font-medium text-white">{a.servizio_nome}</span>
              <span className="text-xs text-slate-400">
                {data.toLocaleDateString('it-IT', { day: '2-digit', month: 'short', year: 'numeric' })}
                {' — '}
                {data.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}
                {a.operatore_nome && ` · ${a.operatore_nome} ${a.operatore_cognome ?? ''}`}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-300">€{Number(a.prezzo_finale).toFixed(2)}</span>
              <Badge className={`text-xs ${STATO_COLORS[statoKey] ?? 'bg-slate-700 text-slate-300'}`}>
                {a.stato}
              </Badge>
            </div>
          </div>
        );
      })}
    </div>
  );
}

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
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-hidden flex flex-col bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white">
            {cliente.nome} {cliente.cognome}
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Gestisci dati, fedeltà e pacchetti del cliente
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto min-h-0">
        <Tabs defaultValue="dati" className="w-full">
          <TabsList className="grid w-full grid-cols-5 bg-slate-900">
            <TabsTrigger value="dati" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Dati
            </TabsTrigger>
            <TabsTrigger value="storico" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Storico
            </TabsTrigger>
            <TabsTrigger value="fedelta" className="flex items-center gap-2">
              <Star className="h-4 w-4" />
              Fedeltà
            </TabsTrigger>
            <TabsTrigger value="pacchetti" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              Pacchetti
            </TabsTrigger>
            <TabsTrigger value="scheda" className="flex items-center gap-2">
              <ClipboardList className="h-4 w-4" />
              Scheda
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

          {/* Tab: Storico Appuntamenti */}
          <TabsContent value="storico" className="mt-4">
            <ClienteStorico clienteId={cliente.id} />
          </TabsContent>

          {/* Tab: Fedeltà (Tessera Timbri) */}
          <TabsContent value="fedelta" className="mt-4">
            <LoyaltyProgress clienteId={cliente.id} showVipToggle />
          </TabsContent>

          {/* Tab: Pacchetti */}
          <TabsContent value="pacchetti" className="mt-4">
            <PacchettiList clienteId={cliente.id} />
          </TabsContent>

          {/* Tab: Scheda Cliente (verticale-specific) */}
          <TabsContent value="scheda" className="mt-4">
            <SchedaClienteDynamic clienteId={cliente.id} />
          </TabsContent>
        </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
};
