// ═══════════════════════════════════════════════════════════════════
// FLUXION - Servizi Page
// Manage services (pricing, duration, categories)
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { Scissors, Plus, Pencil, Trash2, Loader2 } from 'lucide-react';
import { useServizi, useDeleteServizio } from '@/hooks/use-servizi';
import { Button } from '@/components/ui/button';
import { ServizioDialog } from '@/components/servizi/ServizioDialog';
import type { Servizio, CreateServizioInput, UpdateServizioInput } from '@/types/servizio';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export const Servizi: FC = () => {
  const { data: servizi, isLoading, error } = useServizi(true); // active only
  const deleteServizio = useDeleteServizio();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingServizio, setEditingServizio] = useState<Servizio | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [servizioToDelete, setServizioToDelete] = useState<Servizio | null>(null);

  // Handlers
  const handleCreate = () => {
    setEditingServizio(undefined);
    setDialogOpen(true);
  };

  const handleEdit = (servizio: Servizio) => {
    setEditingServizio(servizio);
    setDialogOpen(true);
  };

  const handleDelete = (servizio: Servizio) => {
    setServizioToDelete(servizio);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (servizioToDelete) {
      deleteServizio.mutate(servizioToDelete.id);
      setDeleteDialogOpen(false);
      setServizioToDelete(null);
    }
  };

  const handleDialogSubmit = (_data: CreateServizioInput | UpdateServizioInput) => {
    setDialogOpen(false);
    setEditingServizio(undefined);
  };

  // Format currency
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(price);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Scissors className="w-8 h-8 text-cyan-500" />
          <div>
            <h1 className="text-3xl font-bold text-white">Servizi</h1>
            <p className="text-slate-400">
              {servizi?.length || 0} servizi attivi
            </p>
          </div>
        </div>

        <Button onClick={handleCreate} className="bg-cyan-500 hover:bg-cyan-600 text-white">
          <Plus className="w-4 h-4 mr-2" />
          Nuovo Servizio
        </Button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-red-500">
            Errore nel caricamento dei servizi: {(error as Error).message}
          </p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && servizi && servizi.length === 0 && (
        <div className="text-center py-12 bg-slate-900/50 rounded-lg border border-slate-800">
          <Scissors className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">Nessun servizio trovato</h3>
          <p className="text-slate-400 mb-6">Inizia aggiungendo il tuo primo servizio</p>
          <Button onClick={handleCreate} className="bg-cyan-500 hover:bg-cyan-600 text-white">
            <Plus className="w-4 h-4 mr-2" />
            Crea Servizio
          </Button>
        </div>
      )}

      {/* Services Table */}
      {!isLoading && !error && servizi && servizi.length > 0 && (
        <div className="bg-slate-900/50 rounded-lg border border-slate-800 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-800/50 border-b border-slate-700">
              <tr>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Servizio</th>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Categoria</th>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Prezzo</th>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Durata</th>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Colore</th>
                <th className="text-right p-4 text-sm font-medium text-slate-400">Azioni</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {servizi.map((servizio) => (
                <tr key={servizio.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4">
                    <div>
                      <div className="font-medium text-white">{servizio.nome}</div>
                      {servizio.descrizione && (
                        <div className="text-sm text-slate-400 truncate max-w-xs">
                          {servizio.descrizione}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="p-4">
                    {servizio.categoria ? (
                      <span className="px-2 py-1 rounded bg-slate-800 text-sm text-slate-300">
                        {servizio.categoria}
                      </span>
                    ) : (
                      <span className="text-slate-600">-</span>
                    )}
                  </td>
                  <td className="p-4">
                    <div>
                      <div className="font-medium text-white">{formatPrice(servizio.prezzo)}</div>
                      <div className="text-xs text-slate-400">IVA {servizio.iva_percentuale}%</div>
                    </div>
                  </td>
                  <td className="p-4 text-slate-300">
                    {servizio.durata_minuti} min
                    {servizio.buffer_minuti > 0 && (
                      <span className="text-xs text-slate-500"> (+{servizio.buffer_minuti})</span>
                    )}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-6 h-6 rounded border border-slate-700"
                        style={{ backgroundColor: servizio.colore }}
                      />
                      <span className="text-sm text-slate-400">{servizio.colore}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEdit(servizio)}
                        className="text-slate-400 hover:text-white hover:bg-slate-800"
                      >
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(servizio)}
                        className="text-slate-400 hover:text-red-400 hover:bg-red-500/10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Dialogs */}
      <ServizioDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        servizio={editingServizio}
        onSubmit={handleDialogSubmit}
      />

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-slate-950 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Elimina Servizio</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Sei sicuro di voler eliminare il servizio "{servizioToDelete?.nome}"?
              Questa azione disattiverà il servizio ma non eliminerà gli appuntamenti esistenti.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-slate-800 text-white border-slate-700 hover:bg-slate-700">
              Annulla
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-red-500 text-white hover:bg-red-600"
            >
              Elimina
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
